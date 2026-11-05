"""
Appendices B, C, F and H of Nie, Zheng & Sarkar (2022) on the Texas panel.
  B1  Relative-time model (Autor 2003): Airbnb dichotomised (any competing listing within 1 km, lagged), event dummies
      for j in {-2,-1,0,+1,+2,+3} around the first treated quarter, OLS with hotel, quarter and city x season FE.
  C1  Mutual demotion within hotel triplets (three same-tier hotels all within 1 km of each other), 2SLS as in Table 4.
  F1  Alternative operationalisation: the same thresholds for all hotels (5-star = promotion, 1-2-star = demotion).
  H1  Competitors regardless of tier: competitor count, demoting-others and the instrument rebuilt over all hotels within 1 km.
Usage: python3 11_appendix_robustness.py <workdir with panel_tx.csv> <airbnb dir> <outdir>
Writes: panel_tx_appB.csv, panel_tx_appFH.csv, panel_triplets_TX.csv (for the Stata do-file) and appendix_BCFH_TX.md
"""
import sys, os, glob, itertools, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from replib import haversine, prep, within, fit, models, table_md, fmt, RATIOS
from linearmodels.iv import IV2SLS
WORK, AB, OUT = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(OUT, exist_ok=True)

p = pd.read_csv(os.path.join(WORK, "panel_tx.csv")); p["q"] = pd.PeriodIndex(p.yq, freq="Q")
p = p.sort_values(["hotel_id", "q"]).reset_index(drop=True)
hot = p.drop_duplicates("hotel_id")[["hotel_id", "city", "lat", "lng", "lowend"]].reset_index(drop=True)
Q0, Q1 = p.q.min(), p.q.max(); quarters = pd.period_range(Q0 - 1, Q1, freq="Q")

# ---- rebuild the geography (same code as 04_build_panel_tx.py) ----
ab = []
for slug in ["austin", "dallas", "fort-worth"]:
    d = pd.read_csv(glob.glob(os.path.join(AB, f"{slug}_listings_*.csv.gz"))[0], usecols=["id", "latitude", "longitude", "last_scraped", "hosts_time_as_host_years", "hosts_time_as_host_months"], low_memory=False)
    months = d.hosts_time_as_host_years.fillna(0) * 12 + d.hosts_time_as_host_months.fillna(0)
    d["start_q"] = (pd.to_datetime(d.last_scraped) - pd.to_timedelta(months * 30.44, unit="D")).dt.to_period("Q"); ab.append(d)
ab = pd.concat(ab)
rows_ab, comp_same, comp_all = {}, {}, {}
for _, h in hot.iterrows():
    near = ab[haversine(h.lat, h.lng, ab.latitude.values, ab.longitude.values) <= 1.0]
    rows_ab[h.hotel_id] = {q: set(near.id[near.start_q <= q]) for q in quarters}
    hh = hot[hot.hotel_id != h.hotel_id]; dh = haversine(h.lat, h.lng, hh.lat.values, hh.lng.values)
    comp_same[h.hotel_id] = set(hh.hotel_id[(dh <= 1.0) & (hh.lowend.values == h.lowend)])
    comp_all[h.hotel_id] = set(hh.hotel_id[dh <= 1.0])
# operating window = first to last quarter with a TripAdvisor review (as in 04, from the hotel file)
hf = pd.read_csv(os.path.join(WORK, "panel_tx_hotels.csv")) if os.path.exists(os.path.join(WORK, "panel_tx_hotels.csv")) else None
if hf is not None:
    OPEN = {r.hotel_id: (pd.Period(r.first_q), pd.Period(r.last_q)) for r in hf.itertuples()}
else:
    g = p[p.n_ta.fillna(0) > 0].groupby("hotel_id").q
    OPEN = {h: (a, b) for h, a, b in zip(g.min().index, g.min(), g.max())}
active = lambda c, q: c in OPEN and OPEN[c][0] <= q <= OPEN[c][1]
# sanity check against the delivered panel
chk = [sum(active(c, q - 1) for c in comp_same[h]) for h, q in zip(p.hotel_id, p.q)]
print("competitor-count mismatches vs panel_tx.csv:", int((np.array(chk) != p.comphotels.values).sum()))

px = p.set_index(["hotel_id", "q"])
lines = []
def out(s=""): print(s); lines.append(s)
out("# Appendices B, C, F, H (Texas)\n")

# ================= B1: relative-time model =================
pb = p.copy()
pb["treated"] = (pb.airbnb_lag > 0).astype(int)
first_t = pb[pb.treated == 1].groupby("hotel_id").q.min()
pb["T"] = pb.hotel_id.map(first_t)
rel = (pb.q - pb["T"]).apply(lambda x: x.n if pd.notna(x) else np.nan)
EV = [("ev_m2", -2), ("ev_m1", -1), ("ev_0", 0), ("ev_p1", 1), ("ev_p2", 2), ("ev_p3", 3)]
for c, j in EV: pb[c] = (rel == j).astype(float)
pb = prep(pb)
n_treated = first_t.size; n_never = hot.hotel_id.nunique() - n_treated
out(f"## Table B1. Relative-time model\n\nHotels ever treated (Airbnb within 1 km): {n_treated}; never treated: {n_never}. "
    f"Treatment quarter = first quarter with a lagged competing listing. Dummies at exactly j = -2..+3 quarters from treatment (Autor 2003), OLS, hotel + quarter + city x season FE, SEs clustered by hotel.\n")
EVLAB = {"ev_m2": "Airbnb_Binary treat(-2)", "ev_m1": "Airbnb_Binary treat(-1)", "ev_0": "Airbnb_Binary treat(0)", "ev_p1": "Airbnb_Binary treat(+1)", "ev_p2": "Airbnb_Binary treat(+2)", "ev_p3": "Airbnb_Binary treat(+3)"}
def ols_fe(d, y, cols):
    d = d.dropna(subset=[y]).copy()
    yv = d[y] - d.groupby("hotel_id")[y].transform("mean")
    Xw = within(d, cols, "hotel_id"); Xw = Xw.loc[:, Xw.abs().sum() > 1e-10]
    m = IV2SLS(yv, Xw, None, None).fit(cov_type="clustered", clusters=d.hotel_id)
    col = {EVLAB.get(v, v): fmt(m.params[v], m.std_errors[v], m.pvalues[v]) for v in cols if v in m.params}
    col["ReviewRatios"] = "YES" if "ratio2_lag" in cols else "NO"; col["Observations"] = f"{int(m.nobs):,}"; return col
evc = [c for c, _ in EV]
resB = {}
for y, lab in [("selfpromo", "Self-promotion"), ("demoting_others", "Demoting others")]:
    resB[f"{lab} M1"] = ols_fe(pb, y, evc + ["log_comphotels"])
    resB[f"{lab} M2"] = ols_fe(pb, y, evc + ["log_comphotels", "log_reviews_lag"] + RATIOS)
rowsB = list(EVLAB.values()) + ["log_comphotels", "log_reviews_lag", "ReviewRatios", "Observations"]
dfB = pd.DataFrame({k: {r: v.get(r, "") for r in rowsB} for k, v in resB.items()}); out(dfB.to_markdown()); out()
pb.drop(columns=["q"]).to_csv(os.path.join(OUT, "panel_tx_appB.csv"), index=False)

# ================= F1 and H1 on the hotel-quarter panel =================
pf = p.copy()
has = pf.n_ta.fillna(0) > 0
pf["selfpromo_F"] = np.where(has, pf.ta5_onetime / pf.n_ta, np.nan)          # 5-star by one-time reviewer, all hotels
pf["demotion_F"] = np.where(has, pf.ta12_onetime / pf.n_ta, np.nan)          # 1-2-star by one-time reviewer, all hotels
def demoting_others(dem_series, comp, ncomp):
    d = dem_series.to_dict(); res = []
    for h, q in zip(pf.hotel_id, pf.q):
        vals = [d[(c, q)] / ncomp[c] for c in comp[h] if (c, q) in d and pd.notna(d[(c, q)]) and ncomp[c] > 0]
        res.append(np.mean(vals) if vals else np.nan)
    return np.array(res)
ns = {h: len(comp_same[h]) for h in comp_same}; na = {h: len(comp_all[h]) for h in comp_all}
pfx = pf.set_index(["hotel_id", "q"])
pf["demoting_others_F"] = demoting_others(pfx.demotion_F * pfx.n_ta, comp_same, ns)
pf["demoting_others_all"] = demoting_others(pfx.demotion * pfx.n_ta, comp_all, na)
def iv_count(h, q, comp):
    own = rows_ab[h][q - 1]; s = set()
    for c in comp[h]:
        if active(c, q - 1): s |= rows_ab[c][q - 1]
    return len(s - own)
pf["iv_airbnb_lag_all"] = [iv_count(h, q, comp_all) for h, q in zip(pf.hotel_id, pf.q)]
pf["log_comphotels_all"] = np.log(pf.comphotels_all + 1); pf["log_iv_all"] = np.log(pf.iv_airbnb_lag_all + 1)
pf.loc[~has, ["demoting_others_F", "demoting_others_all"]] = np.nan
pf.drop(columns=["q"]).to_csv(os.path.join(OUT, "panel_tx_appFH.csv"), index=False)

pfp = prep(pf)
out("## Table F1. Alternative operationalisation (same thresholds for all hotels)\n")
resF = {}
for y, lab in [("selfpromo_F", "Self-promotion"), ("demoting_others_F", "Demoting others")]:
    for name, extra in models(True): resF[f"{lab} {name}"] = fit(pfp, y, extra)[1]
out(table_md("Table F1", resF));

out("## Table H1. All neighbouring hotels as competitors (regardless of tier)\n")
ph = pf.copy()
ph["log_comphotels"] = ph.log_comphotels_all; ph["log_iv"] = ph.log_iv_all
php = prep(ph)
resH = {}
for y, lab in [("selfpromo", "Self-promotion"), ("demoting_others_all", "Demoting others")]:
    for name, extra in models(True): resH[f"{lab} {name}"] = fit(php, y, extra)[1]
out(table_md("Table H1", resH))

# ================= C1: hotel triplets =================
ncomp = pd.Series({h: max(len(comp_same[h]), 1) for h in comp_same})
dem_per_comp = ((px.demotion * px.n_ta) / px.index.get_level_values(0).map(ncomp).values).to_dict()
tri = set()
for a in comp_same:
    for b in comp_same[a]:
        if b <= a: continue
        for c in comp_same[a] & comp_same[b]:
            if c > b: tri.add((a, b, c))
tri = sorted(tri); print(f"triplets: {len(tri):,}")
cols = ["city", "lowend", "n_ta", "ta2", "ta3", "ta4", "ta5"]
info = {k: v for k, v in zip(px.index, px[cols].itertuples(index=False))}
rows = []
for a, b, c in tri:
    shared = comp_same[a] & comp_same[b] & comp_same[c]
    for q in pd.period_range(Q0, Q1, freq="Q"):
        ds = [dem_per_comp.get((h, q), np.nan) for h in (a, b, c)]
        if any(pd.isna(x) for x in ds): continue
        own = rows_ab[a][q - 1] | rows_ab[b][q - 1] | rows_ab[c][q - 1]
        iv = set()
        for s in shared:
            if active(s, q - 1): iv |= rows_ab[s][q - 1]
        ia, ib, ic = info[(a, q)], info[(b, q)], info[(c, q)]
        rows.append(dict(triplet=f"{a}|{b}|{c}", yq=str(q), city=ia.city, lowend=int(ia.lowend), mutual=2 * sum(ds),
                         airbnb_lag=len(rows_ab[a][q - 1] & rows_ab[b][q - 1] & rows_ab[c][q - 1]), comphotels=sum(active(s, q - 1) for s in shared),
                         iv_airbnb_lag=len(iv - own), n_ta=ia.n_ta + ib.n_ta + ic.n_ta, ta2=ia.ta2 + ib.ta2 + ic.ta2, ta3=ia.ta3 + ib.ta3 + ic.ta3,
                         ta4=ia.ta4 + ib.ta4 + ic.ta4, ta5=ia.ta5 + ib.ta5 + ic.ta5))
pt = pd.DataFrame(rows)
for c, src in [("log_airbnb", "airbnb_lag"), ("log_comphotels", "comphotels"), ("log_iv", "iv_airbnb_lag")]: pt[c] = np.log(pt[src] + 1)
pt = prep(pt, unit="triplet"); pt.to_csv(os.path.join(OUT, "panel_triplets_TX.csv"), index=False)
out(f"## Table C1. Mutual demotion within hotel triplets\n\nTriplets: {pt.triplet.nunique():,}; triplet-quarters: {len(pt):,}; low-end triplets: {int(pt.drop_duplicates('triplet').lowend.sum())}\n")
has_low = pt.drop_duplicates("triplet").lowend.sum() >= 5
resC = {}
for name, extra in models(has_low):
    try: resC[name] = fit(pt, "mutual", extra, unit="triplet", iv=True)[1]
    except Exception as e: resC[name] = {"Observations": f"failed: {e}"}
out(table_md("Table C1 (2SLS, triplet FE + quarter FE + city x season, SEs clustered by triplet)", resC))
open(os.path.join(OUT, "appendix_BCFH_TX.md"), "w").write("\n".join(lines))
