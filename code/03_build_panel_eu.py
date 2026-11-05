"""
Build the EU hotel-quarter panel (London, Paris, Amsterdam, Barcelona, Milan, Vienna), 2015Q3-2017Q3.
Inputs : data_extract/reviews_EU6.csv (TripAdvisor, HotelRec), data_extract/booking515k.csv, data_extract/booking_ta_match.csv,
         airbnb/<city>_listings_*.csv.gz (Inside Airbnb)
Output : data_extract/panel_eu.csv  (one row per hotel x year-quarter) + data_extract/panel_eu_hotels.csv
Measures follow Nie, Zheng & Sarkar (2022) with Booking.com (verified stays) replacing Expedia:
  SelfPromotion = share5_TA - shareTop_BK      (Top = Booking score >= 9; low-end hotels: TA 4-5 star vs Booking >= 8)
  Demotion      = share12_TA - shareBottom_BK  (Bottom = Booking score <= 5; low-end: TA 1-star vs Booking <= 4)
  DemotingOthers = avg over same-type competitors within 1 km of (their demoting reviews / their n competitors)
  Airbnb_{t-1}   = # Airbnb listings within 1 km whose host started on/before end of quarter t-1
  CompHotels_{t-1} = # same-type matched hotels within 1 km
  IV = distinct Airbnb listings within 1 km of the focal hotel's competing hotels, excluding the focal hotel's own competing listings
"""
import os, sys, re, numpy as np, pandas as pd, glob
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DX, AB = os.path.join(ROOT, "data_extract"), os.path.join(ROOT, "airbnb")
WORK = sys.argv[1] if len(sys.argv) > 1 else DX
OUTD = sys.argv[2] if len(sys.argv) > 2 else DX   # optional output dir   # optional fast local dir holding copies of the inputs
Q0, Q1 = pd.Period("2015Q3"), pd.Period("2017Q3")
MATCH_MIN = 90
RADIUS_KM = 1.0

# ---------- hotels: crosswalk + coordinates ----------
m = pd.read_csv(os.path.join(WORK, "booking_ta_match.csv")); m = m[m.score >= MATCH_MIN]
bk = pd.read_csv(os.path.join(WORK, "booking515k.csv"), low_memory=False)
bk["Review_Date"] = pd.to_datetime(bk.Review_Date, errors="coerce"); bk["q"] = bk.Review_Date.dt.to_period("Q")
bk["lat"] = pd.to_numeric(bk.lat, errors="coerce"); bk["lng"] = pd.to_numeric(bk.lng, errors="coerce")
hot = bk.groupby("Hotel_Name").agg(lat=("lat","first"), lng=("lng","first"), bk_avg=("Average_Score","first")).reset_index()
hot = hot.merge(m[["city","booking_name","hotel_id","ta_slug"]], left_on="Hotel_Name", right_on="booking_name")
hot = hot.dropna(subset=["lat","lng"]).drop_duplicates("hotel_id")
hw = pd.read_csv(os.path.join(WORK, "hotels_EU6.csv"))[["hotel_id","first_review","last_review"]]
hot = hot.merge(hw, on="hotel_id", how="left")
hot["first_q"] = pd.to_datetime(hot.first_review).dt.to_period("Q"); hot["last_q"] = pd.to_datetime(hot.last_review).dt.to_period("Q")
OPEN = {r.hotel_id: (r.first_q, r.last_q) for r in hot.itertuples()}   # operating window (proxy for tax-filing period)
# hotel tier: budget-brand / hostel keywords -> low-end (substitute for STR price tier)
BUDGET = r"(ibis budget|ibis styles|premier inn|travelodge|easyhotel|hostel|motel|b&b hotel|b b hotel|hotel f1|formule 1|generator|yha|meininger|a&o|a o hotel|wombat|safestay|st christopher|tune hotel|point a hotel|hub by premier|budget)"
hot["lowend"] = hot.Hotel_Name.str.lower().str.contains(BUDGET.replace("(", "(?:"), regex=True).astype(int)
print("hotels in panel:", len(hot), "| low-end (keyword):", hot.lowend.sum())

# ---------- TripAdvisor hotel-quarter counts ----------
ta = pd.read_csv(os.path.join(WORK, "reviews_EU6.csv"), usecols=["hotel_id","author","date","rating"], dtype={"author":str})
ta = ta[ta.hotel_id.isin(hot.hotel_id)]
ta["q"] = pd.to_datetime(ta.date, errors="coerce").dt.to_period("Q")
ac = ta.groupby("author").size(); ta["onetime"] = ta.author.map(ac).eq(1)
ta = ta[(ta.q >= Q0) & (ta.q <= Q1)]
g = ta.groupby(["hotel_id","q"])
taq = pd.DataFrame({"n_ta": g.size()})
for s in range(1, 6): taq[f"ta{s}"] = g.rating.apply(lambda r, s=s: (r == s).sum())
taq["ta5_onetime"] = g.apply(lambda d: (d.onetime & (d.rating == 5)).sum(), include_groups=False)
taq["ta12_onetime"] = g.apply(lambda d: (d.onetime & (d.rating <= 2)).sum(), include_groups=False)
taq = taq.reset_index()

# ---------- Booking hotel-quarter counts ----------
b = bk[bk.Hotel_Name.isin(hot.Hotel_Name) & (bk.q >= Q0) & (bk.q <= Q1)].merge(hot[["Hotel_Name","hotel_id"]], on="Hotel_Name")
b["Reviewer_Score"] = pd.to_numeric(b.Reviewer_Score, errors="coerce")
gb = b.groupby(["hotel_id","q"])
bkq = pd.DataFrame({"n_bk": gb.size(),
                    "bk_top9": gb.Reviewer_Score.apply(lambda r: (r >= 9).sum()),
                    "bk_top8": gb.Reviewer_Score.apply(lambda r: (r >= 8).sum()),
                    "bk_bot5": gb.Reviewer_Score.apply(lambda r: (r <= 5).sum()),
                    "bk_bot4": gb.Reviewer_Score.apply(lambda r: (r <= 4).sum())}).reset_index()

# ---------- Airbnb: listings with host start date ----------
CITYFILE = {"London":"london","Paris":"paris","Amsterdam":"amsterdam","Barcelona":"barcelona","Milan":"milan","Vienna":"vienna"}
ab = []
for city, slug in CITYFILE.items():
    f = glob.glob(os.path.join(AB, f"{slug}_listings_*.csv.gz"))[0]
    d = pd.read_csv(f, usecols=["id","host_id","latitude","longitude","last_scraped","hosts_time_as_host_years","hosts_time_as_host_months"], low_memory=False)
    months = d.hosts_time_as_host_years.fillna(0)*12 + d.hosts_time_as_host_months.fillna(0)
    d["host_start"] = pd.to_datetime(d.last_scraped) - pd.to_timedelta(months*30.44, unit="D")
    d["city"] = city; ab.append(d[["id","city","latitude","longitude","host_start"]])
ab = pd.concat(ab); ab["start_q"] = ab.host_start.dt.to_period("Q")
print("airbnb listings:", len(ab))

# ---------- distances ----------
def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    a = np.sin((lat2-lat1)/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin((lon2-lon1)/2)**2
    return 6371.0 * 2 * np.arcsin(np.sqrt(a))

quarters = pd.period_range(Q0 - 1, Q1, freq="Q")   # include Q0-1 for the lag
rows_ab, comp = {}, {}
for _, h in hot.iterrows():
    a = ab[ab.city == h.city]
    dist = haversine(h.lat, h.lng, a.latitude.values, a.longitude.values)
    near = a[dist <= RADIUS_KM]
    rows_ab[h.hotel_id] = {q: set(near.id[near.start_q <= q]) for q in quarters}
    hh = hot[(hot.city == h.city) & (hot.hotel_id != h.hotel_id)]
    dh = haversine(h.lat, h.lng, hh.lat.values, hh.lng.values)
    comp[h.hotel_id] = {"same": list(hh.hotel_id[(dh <= RADIUS_KM) & (hh.lowend.values == h.lowend)]),
                        "all":  list(hh.hotel_id[dh <= RADIUS_KM])}

# ---------- assemble panel ----------
idx = pd.MultiIndex.from_product([hot.hotel_id, pd.period_range(Q0, Q1, freq="Q")], names=["hotel_id","q"])
p = pd.DataFrame(index=idx).reset_index().merge(taq, how="left").merge(bkq, how="left")
p = p.merge(hot[["hotel_id","city","Hotel_Name","ta_slug","lat","lng","lowend","bk_avg"]], on="hotel_id")
p["airbnb_lag"] = [len(rows_ab[h][q - 1]) for h, q in zip(p.hotel_id, p.q)]
p["airbnb_cur"] = [len(rows_ab[h][q]) for h, q in zip(p.hotel_id, p.q)]
active = lambda c, q: OPEN[c][0] <= q <= OPEN[c][1]
p["comphotels"] = [sum(active(c, q - 1) for c in comp[h]["same"]) for h, q in zip(p.hotel_id, p.q)]
p["comphotels_all"] = [sum(active(c, q - 1) for c in comp[h]["all"]) for h, q in zip(p.hotel_id, p.q)]
# IV: Airbnb listings near the focal hotel's competitors, excluding the focal's own nearby listings
def iv(h, q):
    own = rows_ab[h][q - 1]; s = set()
    for c in comp[h]["same"]:
        if active(c, q - 1): s |= rows_ab[c][q - 1]
    return len(s - own)
p["iv_airbnb_lag"] = [iv(h, q) for h, q in zip(p.hotel_id, p.q)]

# manipulation measures (require reviews on both sites in the quarter, as in the paper)
both = p.n_ta.fillna(0).gt(0) & p.n_bk.fillna(0).gt(0)
hi = p.lowend.eq(0)
p["share5_ta"]  = np.where(hi, p.ta5/p.n_ta, (p.ta4+p.ta5)/p.n_ta)
p["share12_ta"] = np.where(hi, (p.ta1+p.ta2)/p.n_ta, p.ta1/p.n_ta)
p["sharetop_bk"] = np.where(hi, p.bk_top9/p.n_bk, p.bk_top8/p.n_bk)
p["sharebot_bk"] = np.where(hi, p.bk_bot5/p.n_bk, p.bk_bot4/p.n_bk)
p["selfpromo"] = p.share5_ta - p.sharetop_bk
p["demotion"]  = p.share12_ta - p.sharebot_bk
# alternative, benchmark-free proxies (Luca & Zervas style)
p["share5_onetime"]  = p.ta5_onetime / p.n_ta
p["share12_onetime"] = p.ta12_onetime / p.n_ta
# DemotingOthers: competitor's demoting reviews (demotion x n_ta) spread evenly over its competitors, averaged over focal's competitors
dem = p.set_index(["hotel_id","q"]).demotion * p.set_index(["hotel_id","q"]).n_ta
ncomp = {h: len(comp[h]["same"]) for h in hot.hotel_id}
def demoting_others(h, q):
    vals = []
    for c in comp[h]["same"]:
        v = dem.get((c, q), np.nan)
        if pd.notna(v) and ncomp[c] > 0: vals.append(v / ncomp[c])
    return np.mean(vals) if vals else np.nan
p["demoting_others"] = [demoting_others(h, q) for h, q in zip(p.hotel_id, p.q)]
p.loc[~both, ["selfpromo","demotion","demoting_others"]] = np.nan
p["log_airbnb"] = np.log(p.airbnb_lag + 1); p["log_comphotels"] = np.log(p.comphotels + 1); p["log_iv"] = np.log(p.iv_airbnb_lag + 1)
p["yq"] = p.q.astype(str); p = p.drop(columns="q")
p.to_csv(os.path.join(OUTD, "panel_eu.csv"), index=False)
hot.assign(n_comp_same=hot.hotel_id.map(ncomp)).to_csv(os.path.join(OUTD, "panel_eu_hotels.csv"), index=False)
ok = p[both]
print(f"panel rows: {len(p):,}  with reviews on both sites: {len(ok):,}  hotels: {ok.hotel_id.nunique():,}")
print(ok[["n_ta","n_bk","airbnb_lag","comphotels","iv_airbnb_lag","selfpromo","demotion","demoting_others","share5_onetime"]].describe().T[["mean","std","min","max"]].round(3).to_string())
print("hotels with >=1 Airbnb competitor:", (ok.groupby("hotel_id").airbnb_lag.max() > 0).mean().round(3))
