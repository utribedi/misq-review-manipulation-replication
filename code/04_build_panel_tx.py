"""
Build the Texas hotel-quarter panel (Austin, Dallas, Fort Worth), 2011Q1-2019Q2.
Inputs : data_extract/reviews_TX.csv (TripAdvisor, HotelRec), data_extract/tx_hotel_geo.csv (geocoded hotels),
         airbnb/{austin,dallas,fort-worth}_listings_*.csv.gz
Output : data_extract/panel_tx.csv, data_extract/panel_tx_hotels.csv
No verified-review benchmark exists for Texas in public data, so manipulation is proxied by reviews from one-time reviewers
(Luca & Zervas 2016; Mayzlin et al. 2014 use the same logic for suspicious reviewers):
  SelfPromotion_proxy = share of TA reviews that are 5-star (4-5 for low-end) AND written by a one-time reviewer
  Demotion_proxy      = share of TA reviews that are 1-2-star (1 for low-end) AND written by a one-time reviewer
  DemotingOthers      = as in the paper, using Demotion_proxy x n_ta spread over competitors
Airbnb_{t-1}, CompHotels_{t-1}, IV: identical construction to the EU panel (1 km radius, host start date from host tenure).
"""
import os, sys, numpy as np, pandas as pd, glob
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DX, AB = os.path.join(ROOT, "data_extract"), os.path.join(ROOT, "airbnb")
WORK = sys.argv[1] if len(sys.argv) > 1 else DX
OUTD = sys.argv[2] if len(sys.argv) > 2 else DX   # optional output dir
Q0, Q1 = pd.Period("2011Q1"), pd.Period("2019Q2")
RADIUS_KM = 1.0

geo = pd.read_csv(os.path.join(WORK, "tx_hotel_geo.csv")).dropna(subset=["lat","lng"])
BUDGET = r"(motel 6|studio 6|super 8|super 7|days inn|econo lodge|rodeway|red roof|knights inn|americas best value|america s best value|budget|scottish inn|extended stay america|intown|hometowne|woodspring|microtel|travelodge|howard johnson|relax inn|motel|hostel|rv park|rv resort|koa|executive inn|royal inn|galaxy inn|tropicana|apple inn|dalworth|stay express|express studios|sunstone|motor lodge|magnuson)"   # STR economy-class brands = low-end
geo["lowend"] = geo.name.str.lower().str.contains(BUDGET.replace("(", "(?:"), regex=True).astype(int)
hot = geo.drop_duplicates("hotel_id").reset_index(drop=True)
hot["first_q"] = pd.to_datetime(hot.first_review).dt.to_period("Q"); hot["last_q"] = pd.to_datetime(hot.last_review).dt.to_period("Q")
OPEN = {r.hotel_id: (r.first_q, r.last_q) for r in hot.itertuples()}
active = lambda c, q: OPEN[c][0] <= q <= OPEN[c][1]
print("geocoded hotels:", len(hot), "| low-end:", hot.lowend.sum(), f"({hot.lowend.mean():.0%})")

ta = pd.read_csv(os.path.join(WORK, "reviews_TX.csv"), usecols=["hotel_id","author","date","rating"], dtype={"author":str})
ac = ta.groupby("author").size(); ta["onetime"] = ta.author.map(ac).eq(1)   # one-time = single review in all of Texas
ta = ta[ta.hotel_id.isin(hot.hotel_id)].copy()
ta["q"] = pd.to_datetime(ta.date, errors="coerce").dt.to_period("Q")
ta = ta[(ta.q >= Q0) & (ta.q <= Q1)]
g = ta.groupby(["hotel_id","q"])
taq = pd.DataFrame({"n_ta": g.size()})
for s in range(1, 6): taq[f"ta{s}"] = g.rating.apply(lambda r, s=s: (r == s).sum())
taq["ta5_onetime"]  = g.apply(lambda d: (d.onetime & (d.rating == 5)).sum(), include_groups=False)
taq["ta45_onetime"] = g.apply(lambda d: (d.onetime & (d.rating >= 4)).sum(), include_groups=False)
taq["ta12_onetime"] = g.apply(lambda d: (d.onetime & (d.rating <= 2)).sum(), include_groups=False)
taq["ta1_onetime"]  = g.apply(lambda d: (d.onetime & (d.rating == 1)).sum(), include_groups=False)
taq["n_onetime"]    = g.onetime.sum()
taq = taq.reset_index()

CITYFILE = {"Austin":"austin","Dallas":"dallas","Fort Worth":"fort-worth"}
ab = []
for city, slug in CITYFILE.items():
    f = glob.glob(os.path.join(AB, f"{slug}_listings_*.csv.gz"))[0]
    d = pd.read_csv(f, usecols=["id","latitude","longitude","last_scraped","hosts_time_as_host_years","hosts_time_as_host_months"], low_memory=False)
    months = d.hosts_time_as_host_years.fillna(0)*12 + d.hosts_time_as_host_months.fillna(0)
    d["host_start"] = pd.to_datetime(d.last_scraped) - pd.to_timedelta(months*30.44, unit="D")
    d["city"] = city; ab.append(d[["id","city","latitude","longitude","host_start"]])
ab = pd.concat(ab); ab["start_q"] = ab.host_start.dt.to_period("Q")

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    a = np.sin((lat2-lat1)/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin((lon2-lon1)/2)**2
    return 6371.0 * 2 * np.arcsin(np.sqrt(a))

quarters = pd.period_range(Q0 - 1, Q1, freq="Q")
rows_ab, comp = {}, {}
for _, h in hot.iterrows():
    a = ab   # Airbnb files overlap at the DFW seam; use all three cities' listings for every hotel
    dist = haversine(h.lat, h.lng, a.latitude.values, a.longitude.values)
    near = a[dist <= RADIUS_KM]
    rows_ab[h.hotel_id] = {q: set(near.id[near.start_q <= q]) for q in quarters}
    hh = hot[hot.hotel_id != h.hotel_id]
    dh = haversine(h.lat, h.lng, hh.lat.values, hh.lng.values)
    comp[h.hotel_id] = {"same": list(hh.hotel_id[(dh <= RADIUS_KM) & (hh.lowend.values == h.lowend)]), "all": list(hh.hotel_id[dh <= RADIUS_KM])}

idx = pd.MultiIndex.from_product([hot.hotel_id, pd.period_range(Q0, Q1, freq="Q")], names=["hotel_id","q"])
p = pd.DataFrame(index=idx).reset_index().merge(taq, how="left")
p = p.merge(hot[["hotel_id","name","city","lat","lng","lowend","geo_source"]], on="hotel_id")
p["airbnb_lag"] = [len(rows_ab[h][q - 1]) for h, q in zip(p.hotel_id, p.q)]
p["airbnb_cur"] = [len(rows_ab[h][q]) for h, q in zip(p.hotel_id, p.q)]
p["comphotels"] = [sum(active(c, q - 1) for c in comp[h]["same"]) for h, q in zip(p.hotel_id, p.q)]
p["comphotels_all"] = [sum(active(c, q - 1) for c in comp[h]["all"]) for h, q in zip(p.hotel_id, p.q)]
def iv(h, q):
    own = rows_ab[h][q - 1]; s = set()
    for c in comp[h]["same"]:
        if active(c, q - 1): s |= rows_ab[c][q - 1]
    return len(s - own)
p["iv_airbnb_lag"] = [iv(h, q) for h, q in zip(p.hotel_id, p.q)]

has = p.n_ta.fillna(0).gt(0); hi = p.lowend.eq(0)
p["share5_ta"]  = np.where(hi, p.ta5/p.n_ta, (p.ta4+p.ta5)/p.n_ta)
p["share12_ta"] = np.where(hi, (p.ta1+p.ta2)/p.n_ta, p.ta1/p.n_ta)
p["selfpromo"] = np.where(hi, p.ta5_onetime/p.n_ta, p.ta45_onetime/p.n_ta)      # one-time-reviewer proxy
p["demotion"]  = np.where(hi, p.ta12_onetime/p.n_ta, p.ta1_onetime/p.n_ta)
p["share_onetime"] = p.n_onetime / p.n_ta
dem = (p.set_index(["hotel_id","q"]).demotion * p.set_index(["hotel_id","q"]).n_ta)
ncomp = {h: len(comp[h]["same"]) for h in hot.hotel_id}
def demoting_others(h, q):
    vals = [dem.get((c, q), np.nan) / ncomp[c] for c in comp[h]["same"] if pd.notna(dem.get((c, q), np.nan)) and ncomp[c] > 0]
    return np.mean(vals) if vals else np.nan
p["demoting_others"] = [demoting_others(h, q) for h, q in zip(p.hotel_id, p.q)]
p.loc[~has, ["selfpromo","demotion","demoting_others","share5_ta","share12_ta","share_onetime"]] = np.nan
p["log_airbnb"] = np.log(p.airbnb_lag + 1); p["log_comphotels"] = np.log(p.comphotels + 1); p["log_iv"] = np.log(p.iv_airbnb_lag + 1)
p["yq"] = p.q.astype(str); p = p.drop(columns="q")
p.to_csv(os.path.join(OUTD, "panel_tx.csv"), index=False)
hot.assign(n_comp_same=hot.hotel_id.map(ncomp)).to_csv(os.path.join(OUTD, "panel_tx_hotels.csv"), index=False)
ok = p[has]
print(f"panel rows: {len(p):,}  with TA reviews: {len(ok):,}  hotels: {ok.hotel_id.nunique():,}")
print(ok[["n_ta","airbnb_lag","comphotels","iv_airbnb_lag","selfpromo","demotion","demoting_others","share_onetime"]].describe().T[["mean","std","min","max"]].round(3).to_string())
print("hotels with >=1 Airbnb competitor ever:", (ok.groupby("hotel_id").airbnb_lag.max() > 0).mean().round(3))
print("mean airbnb_lag by year:", ok.assign(y=ok.yq.str[:4]).groupby("y").airbnb_lag.mean().round(1).to_dict())
