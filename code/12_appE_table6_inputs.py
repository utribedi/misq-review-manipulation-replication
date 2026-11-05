"""
Inputs for Appendix E (Gaussian-kernel competition intensity) and Table 6 (look-ahead PSM) of Nie, Zheng & Sarkar (2022), Texas panel.
Appendix E. Competition intensity w_ij = exp(-0.5 (d_ij / h)^2), h = 1 km and 0.5 km (weights below 3h are dropped, < 0.011):
  Airbnb^w_i   = sum over listings l of w_il 1{l listed by q-1}
  CompHotels^w_i = sum over same-tier hotels j of w_ij 1{j operating in q-1}
  DemotingOthers^w_i = weighted mean over competitors j of (demoting reviews of j / W_j) with weights w_ij, W_j = sum_k w_jk
  IV^w_i       = weighted mean over competitors j of Airbnb^w_j computed over listings farther than h from i
Table 6. Hotel-level file with Figure 1 groups (A: Airbnb competitor in Period 1, B: only in Period 2, C: never) and pre-period covariates
  for propensity-score matching in Stata (psmatch2).
Usage: python3 12_appE_table6_inputs.py <workdir with panel_tx.csv + panel_tx_hotels.csv> <airbnb dir> <outdir>
Writes: panel_tx_appE.csv, hotels_tx_lapsm.csv
"""
import sys, os, glob, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from replib import haversine, prep, fit, models, table_md
WORK, AB, OUT = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(OUT, exist_ok=True)
p = pd.read_csv(os.path.join(WORK, "panel_tx.csv")); p["q"] = pd.PeriodIndex(p.yq, freq="Q")
p = p.sort_values(["hotel_id", "q"]).reset_index(drop=True)
hot = p.drop_duplicates("hotel_id")[["hotel_id", "city", "lat", "lng", "lowend"]].reset_index(drop=True)
Q0, Q1 = p.q.min(), p.q.max(); QS = pd.period_range(Q0, Q1, freq="Q")
hf = pd.read_csv(os.path.join(WORK, "panel_tx_hotels.csv"))
OPEN = {r.hotel_id: (pd.Period(r.first_q), pd.Period(r.last_q)) for r in hf.itertuples()}
active = lambda c, q: OPEN[c][0] <= q <= OPEN[c][1]
ab = []
for slug in ["austin", "dallas", "fort-worth"]:
    d = pd.read_csv(glob.glob(os.path.join(AB, f"{slug}_listings_*.csv.gz"))[0], usecols=["id", "latitude", "longitude", "last_scraped", "hosts_time_as_host_years", "hosts_time_as_host_months"], low_memory=False)
    months = d.hosts_time_as_host_years.fillna(0) * 12 + d.hosts_time_as_host_months.fillna(0)
    d["start_q"] = (pd.to_datetime(d.last_scraped) - pd.to_timedelta(months * 30.44, unit="D")).dt.to_period("Q"); ab.append(d)
ab = pd.concat(ab).reset_index(drop=True)
ab["start_i"] = (ab.start_q - Q0).apply(lambda x: x.n)          # quarter index relative to Q0 (can be negative)
qi = {q: i for i, q in enumerate(QS)}
px = p.set_index(["hotel_id", "q"])
dem = (px.demotion * px.n_ta)                                    # demoting reviews written by each hotel in each quarter

out = p[["hotel_id", "yq", "city", "lowend", "n_ta", "ta1", "ta2", "ta3", "ta4", "ta5", "selfpromo", "demotion"]].copy()
for h, tag in [(1.0, "k1"), (0.5, "k05")]:
    R = 3 * h
    near, W, compw = {}, {}, {}
    for _, hh in hot.iterrows():
        d = haversine(hh.lat, hh.lng, ab.latitude.values, ab.longitude.values); m = d <= R
        near[hh.hotel_id] = (ab.id.values[m], np.exp(-0.5 * (d[m] / h) ** 2), ab.start_i.values[m], d[m])
        o = hot[hot.hotel_id != hh.hotel_id]; dh = haversine(hh.lat, hh.lng, o.lat.values, o.lng.values)
        mm = (dh <= R) & (o.lowend.values == hh.lowend)
        compw[hh.hotel_id] = dict(zip(o.hotel_id.values[mm], np.exp(-0.5 * (dh[mm] / h) ** 2)))
    W = {i: sum(compw[i].values()) for i in compw}
    # kernel Airbnb supply by quarter index (supply at index t counts listings with start_i <= t)
    def supply(i, t, exclude=None):
        ids, w, s, d = near[i]
        m = s <= t
        if exclude is not None: m &= ~np.isin(ids, exclude)
        return w[m].sum()
    own = {i: near[i][0][near[i][3] <= h] for i in near}       # listings within h of the focal hotel, excluded from the IV
    A, C, DO, IV = [], [], [], []
    for i, q in zip(out.hotel_id, pd.PeriodIndex(out.yq, freq="Q")):
        t = qi[q] - 1                                               # lagged
        A.append(supply(i, t))
        comps = [(j, w) for j, w in compw[i].items() if active(j, q - 1)]
        C.append(sum(w for _, w in comps))
        if comps:
            IV.append(sum(w * supply(j, t, own[i]) for j, w in comps) / sum(w for _, w in comps))
        else: IV.append(0.0)
        vals = [(w, dem.get((j, q), np.nan) / W[j]) for j, w in compw[i].items() if pd.notna(dem.get((j, q), np.nan)) and W[j] > 0]
        DO.append(sum(w * v for w, v in vals) / sum(w for w, _ in vals) if vals else np.nan)
    out[f"airbnb_{tag}"] = A; out[f"comphotels_{tag}"] = C; out[f"demoting_others_{tag}"] = DO; out[f"iv_{tag}"] = IV
    out.loc[out.n_ta.fillna(0) == 0, f"demoting_others_{tag}"] = np.nan
    for c in ["airbnb", "comphotels", "iv"]: out[f"log_{c}_{tag}"] = np.log(out[f"{c}_{tag}"] + 1)
    print(f"h = {h} km: mean kernel Airbnb {out[f'airbnb_{tag}'][out.n_ta.fillna(0) > 0].mean():.2f}, competing hotels {out[f'comphotels_{tag}'][out.n_ta.fillna(0) > 0].mean():.2f}")
out.to_csv(os.path.join(OUT, "panel_tx_appE.csv"), index=False)

# quick Python check of Table E1 (2SLS, same spec as Table 2/3)
lines = ["# Appendix E (Texas), Python check\n"]
for h, tag in [(1.0, "k1"), (0.5, "k05")]:
    d = out.copy()
    d["log_airbnb"] = d[f"log_airbnb_{tag}"]; d["log_comphotels"] = d[f"log_comphotels_{tag}"]; d["log_iv"] = d[f"log_iv_{tag}"]
    d["demoting_others"] = d[f"demoting_others_{tag}"]
    dp = prep(d); res = {}
    for y, lab in [("selfpromo", "Promote"), ("demoting_others", "Demote")]:
        for name, extra in models(True): res[f"{lab} {name}"] = fit(dp, y, extra)[1]
    lines.append(table_md(f"Table E1, Gaussian kernel, bandwidth {h} km", res))
open(os.path.join(OUT, "appendix_E_TX_check.md"), "w").write("\n".join(lines)); print("\n".join(lines))

# ---------------- Table 6 inputs: Figure 1 groups and pre-period covariates ----------------
ok = p[p.n_ta.fillna(0) > 0]
qs = sorted(ok.q.unique()); cut = qs[int(len(qs) * 2 / 3) - 1]
g1 = p[p.q <= cut].groupby("hotel_id").airbnb_lag.max() > 0; g2 = p[p.q > cut].groupby("hotel_id").airbnb_lag.max() > 0
grp = pd.Series(np.where(g1, "A", np.where(g2, "B", "C")), index=g1.index)
print(f"Figure 1 groups (Period 1 through {cut}): A = {(grp == 'A').sum()}, B = {(grp == 'B').sum()}, C = {(grp == 'C').sum()}")
hl = hot.set_index("hotel_id").copy(); hl["group"] = grp; hl["treated"] = (hl.group == "A").astype(int)
hl["first_q"] = hl.index.map(lambda h: str(OPEN[h][0])); hl["opened_before_2011"] = (hl.index.map(lambda h: OPEN[h][0]) < Q0).astype(int)
ncomp = {h: int(r) for h, r in zip(hf.hotel_id, hf.n_comp_same)}; hl["n_comp_same"] = hl.index.map(ncomp)
rows = {}
for h, d in ok.groupby("hotel_id"):
    pre = d[d.q <= pd.Period("2012Q4")]
    if len(pre) == 0: pre = d.head(8)                               # hotels first reviewed after 2012: first eight quarters with reviews
    rating = (pre.ta1 + 2 * pre.ta2 + 3 * pre.ta3 + 4 * pre.ta4 + 5 * pre.ta5).sum() / pre.n_ta.sum()
    rows[h] = dict(pre_reviews=pre.n_ta.mean(), pre_rating=rating, pre_share5=pre.ta5.sum() / pre.n_ta.sum(), pre_share12=(pre.ta1 + pre.ta2).sum() / pre.n_ta.sum(),
                   pre_quarters=len(pre), pre_selfpromo=pre.selfpromo.mean(), pre_period_used=int(len(d[d.q <= pd.Period("2012Q4")]) > 0))
hl = hl.join(pd.DataFrame(rows).T)
hl.reset_index().to_csv(os.path.join(OUT, "hotels_tx_lapsm.csv"), index=False)
print(hl.groupby("group")[["pre_reviews", "pre_rating", "pre_share5", "n_comp_same", "lowend"]].mean().round(2))
