"""
Extensions and remaining appendix analyses.
  (1) Appendix I replicated + extended: 2SLS before/after 2011Q4 and before/after 2015Q4 (Texas)
  (2) Appendix G: Airbnb competitors segmented by price per person (24th percentile cutoff); hotels matched to same-segment listings (Texas)
  (3) Extension: Booking.com reviewer-history excess (EU) — TripAdvisor one-time-reviewer top/bottom share minus the same share on verified Booking.com
Usage: python3 09_extensions.py <workdir> <outdir>
"""
import sys, os, glob, numpy as np, pandas as pd
from replib import haversine, prep, fit, models, table_md, RATIOS
WORK, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."); AB = os.path.join(ROOT, "airbnb")
md = ["# Extensions and appendix analyses\n"]
NOTE = "*p<0.05, **p<0.01, ***p<0.001; SEs clustered by hotel. Hotel FE, quarter FE, city x season FE; Model 2 controls (lagged review count and ratios)."

# ---------- (1) Appendix I and the 2015Q4 break (Texas) ----------
tx = prep(pd.read_csv(os.path.join(WORK, "panel_tx.csv")))
res = {}
for y, lab in [("selfpromo","Self-promotion"), ("demoting_others","Demoting others")]:
    for name, mask in [("<=2011Q4", tx.q <= "2011Q4"), ("2012Q1-2015Q4", (tx.q > "2011Q4") & (tx.q <= "2015Q4")), (">=2016Q1", tx.q > "2015Q4")]:
        try: res[f"{lab}: {name}"] = fit(tx[mask], y, ["log_reviews_lag"] + RATIOS, iv=True)[1]
        except Exception as e: res[f"{lab}: {name}"] = {"Observations": f"failed: {e}"}
md.append(table_md("Table I1 (TX) and extension: 2SLS by sub-period (paper's inflection point 2011Q4; added break at 2015Q4, the paper's end of sample)", res, NOTE))

# ---------- (2) Appendix G: segmented Airbnb competitors (Texas) ----------
hot = tx.drop_duplicates("hotel_id")[["hotel_id","city","lat","lng","lowend"]].reset_index(drop=True)
ab = []
for slug in ["austin","dallas","fort-worth"]:
    d = pd.read_csv(glob.glob(os.path.join(AB, f"{slug}_listings_*.csv.gz"))[0], usecols=["id","latitude","longitude","last_scraped","hosts_time_as_host_years","hosts_time_as_host_months","price","accommodates"], low_memory=False)
    months = d.hosts_time_as_host_years.fillna(0)*12 + d.hosts_time_as_host_months.fillna(0)
    d["start_q"] = (pd.to_datetime(d.last_scraped) - pd.to_timedelta(months*30.44, unit="D")).dt.to_period("Q"); ab.append(d)
ab = pd.concat(ab)
ab["price_num"] = pd.to_numeric(ab.price.astype(str).str.replace(r"[$,]", "", regex=True), errors="coerce")
ab["price_pp"] = ab.price_num / ab.accommodates.replace(0, np.nan)
cut = ab.price_pp.quantile(0.24); ab["low_seg"] = (ab.price_pp <= cut).astype(int)
md.append(f"\n## Appendix G (TX): Airbnb price per person — 24th percentile cutoff = ${cut:.0f} (paper: $25); {ab.price_pp.notna().mean():.0%} of listings have a price\n")
quarters = pd.period_range(tx.q.min() - 1, tx.q.max(), freq="Q")
seg_sets, comp = {}, {}
abp = ab[ab.price_pp.notna()]
for _, h in hot.iterrows():
    near = abp[haversine(h.lat, h.lng, abp.latitude.values, abp.longitude.values) <= 1.0]
    same = near[near.low_seg == h.lowend]
    seg_sets[h.hotel_id] = {q: set(same.id[same.start_q <= q]) for q in quarters}
    hh = hot[hot.hotel_id != h.hotel_id]; dh = haversine(h.lat, h.lng, hh.lat.values, hh.lng.values)
    comp[h.hotel_id] = list(hh.hotel_id[(dh <= 1.0) & (hh.lowend.values == h.lowend)])
tx["airbnb_seg_lag"] = [len(seg_sets[h][q-1]) for h, q in zip(tx.hotel_id, tx.q)]
def iv_seg(h, q):
    own = seg_sets[h][q-1]; s = set()
    for c in comp[h]: s |= seg_sets[c][q-1]
    return len(s - own)
tx["iv_seg_lag"] = [iv_seg(h, q) for h, q in zip(tx.hotel_id, tx.q)]
tx["log_airbnb_seg"] = np.log(tx.airbnb_seg_lag + 1); tx["log_iv_seg"] = np.log(tx.iv_seg_lag + 1)
tx["log_airbnb_x_low_seg"] = tx.log_airbnb_seg * tx.lowend; tx["log_iv_x_low_seg"] = tx.log_iv_seg * tx.lowend
tx.to_csv(os.path.join(OUT, "panel_tx_segG.csv"), index=False)   # for the Stata version of Table G1
res = {}
for y, lab in [("selfpromo","Self-promotion"), ("demoting_others","Demoting others")]:
    for name, extra in models(True):
        try:
            d = tx.copy()
            if "log_airbnb_x_low" in extra:   # swap in segmented interaction terms
                d["log_airbnb_x_low"], d["log_iv_x_low"] = d.log_airbnb_x_low_seg, d.log_iv_x_low_seg
            m, col = fit(d, y, extra, iv=True, endog_base="log_airbnb_seg", instr_base="log_iv_seg")
            col["log(Airbnb)"] = f"{m.params['log_airbnb_seg']:.3f}{'***' if m.pvalues['log_airbnb_seg']<0.001 else '**' if m.pvalues['log_airbnb_seg']<0.01 else '*' if m.pvalues['log_airbnb_seg']<0.05 else ''} ({m.std_errors['log_airbnb_seg']:.3f})"
            res[f"{lab}: {name}"] = col
        except Exception as e: res[f"{lab}: {name}"] = {"Observations": f"failed: {e}"}
md.append(table_md("Table G1 (TX): same-segment Airbnb competitors (low-end hotels vs low-price listings, high-end vs the rest), 2SLS", res, NOTE.replace("Model 2 controls", "Models as in Table 2")))

# ---------- (3) Booking reviewer-history excess (EU) ----------
eu = prep(pd.read_csv(os.path.join(WORK, "panel_eu.csv")))
bk = pd.read_csv(os.path.join(WORK, "booking515k.csv"), usecols=["Hotel_Name","Review_Date","Reviewer_Score","Total_Number_of_Reviews_Reviewer_Has_Given"], low_memory=False)
bk["q"] = pd.to_datetime(bk.Review_Date, errors="coerce").dt.to_period("Q"); bk["yq"] = bk.q.astype(str)
bk["score"] = pd.to_numeric(bk.Reviewer_Score, errors="coerce"); bk["one"] = pd.to_numeric(bk.Total_Number_of_Reviews_Reviewer_Has_Given, errors="coerce").eq(1)
g = bk.groupby(["Hotel_Name","yq"])
bq = pd.DataFrame({"bk_one_share": g.one.mean(), "bk_one_top": g.apply(lambda d: (d.one & (d.score >= 9)).sum() / len(d), include_groups=False),
                   "bk_one_bot": g.apply(lambda d: (d.one & (d.score <= 5)).sum() / len(d), include_groups=False)}).reset_index()
eu = eu.merge(bq, on=["Hotel_Name","yq"], how="left")
eu["onetime_excess_top"] = eu.share5_onetime - eu.bk_one_top      # TA one-time 5-star share minus Booking one-time 9-10 share
eu["onetime_excess_bot"] = eu.share12_onetime - eu.bk_one_bot
eu["onetime_excess_all"] = (eu.ta5_onetime + eu.ta12_onetime) / eu.n_ta - eu.bk_one_share
has = eu.selfpromo.notna()
md.append("\n## Extension (EU): one-time-reviewer excess, TripAdvisor minus verified Booking.com, same hotel-quarter\n")
md.append(f"- Share of reviews by one-time reviewers: TripAdvisor {((eu.ta5_onetime+eu.ta12_onetime)[has].sum()/eu.n_ta[has].sum()):.1%} (5-star or 1-2-star only); Booking.com {eu.bk_one_share[has].mean():.1%} (all scores)")
md.append(f"- Mean excess (top): {eu.onetime_excess_top[has].mean():.3f}; (bottom): {eu.onetime_excess_bot[has].mean():.3f}; correlation with Mayzlin-style selfpromo: {eu[has][['onetime_excess_top','selfpromo']].corr().iloc[0,1]:.2f}")
res = {}
for y, lab in [("onetime_excess_top","Excess one-time 5-star (promotion)"), ("onetime_excess_bot","Excess one-time 1-2-star (demotion)")]:
    for kind, iv in [("2SLS", True), ("OLS-FE", False)]:
        try: res[f"{lab}: {kind}"] = fit(eu[has], y, ["log_reviews_lag"] + RATIOS, iv=iv)[1]
        except Exception as e: res[f"{lab}: {kind}"] = {"Observations": f"failed: {e}"}
md.append(table_md("Extension table (EU): one-time-reviewer excess on Airbnb supply", res, NOTE))
eu.to_csv(os.path.join(OUT, "panel_eu_extension.csv"), index=False)
open(os.path.join(OUT, "extensions.md"), "w").write("\n".join(md)); print("\n".join(md))
