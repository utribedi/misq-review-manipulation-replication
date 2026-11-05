"""
Replicate the table structure of Nie, Zheng & Sarkar (2022, MISQ) on a hotel-quarter panel.
Usage: python3 05_estimate.py <panel.csv> <label> <outdir>
Specification (eq. 1 of the paper):
  Y_it = b1 log(Airbnb_{i,t-1}) + b2 log(CompHotels_{i,t-1}) + b3 log(ReviewCount_{i,t-1}) + b4 log(Airbnb_{i,t-1}) x LowEnd_i
         + ReviewRatios_{i,t-1} (2,3,4,5-star shares on TA) + hotel FE + year-quarter FE + city x season FE + e_it
  2SLS: log(Airbnb) instrumented by log(Cmp_Airbnb) (Airbnb listings near the focal hotel's competitors, excl. its own);
        the interaction is instrumented by log(Cmp_Airbnb) x LowEnd.  SEs clustered by hotel.
Tables: 1 (summary), 2 (self-promotion), 3 (demoting others), 8 (being demoted), 5 (IV validity), first stage, OLS-FE counterpart.
"""
import sys, os, numpy as np, pandas as pd
from linearmodels.iv import IV2SLS
from linearmodels.panel import PanelOLS
panel, label, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(outdir, exist_ok=True)
p = pd.read_csv(panel)
p["q"] = pd.PeriodIndex(p.yq, freq="Q"); p = p.sort_values(["hotel_id","q"]).reset_index(drop=True)
p["season"] = p.q.dt.quarter; p["city_season"] = p.city.astype(str) + "_" + p.season.astype(str)
# lagged review controls (previous quarter on TripAdvisor)
g = p.groupby("hotel_id")
for c in ["n_ta","ta2","ta3","ta4","ta5"]:
    p[f"{c}_lag"] = g[c].shift(1)
prevq_ok = (g.q.shift(1) == p.q - 1)
p.loc[~prevq_ok, [f"{c}_lag" for c in ["n_ta","ta2","ta3","ta4","ta5"]]] = np.nan
p["n_ta_lag"] = p.n_ta_lag.fillna(0)
for s in [2,3,4,5]: p[f"ratio{s}_lag"] = np.where(p.n_ta_lag > 0, p[f"ta{s}_lag"] / p.n_ta_lag, 0.0)
p["log_reviews_lag"] = np.log(p.n_ta_lag + 1)
p["log_airbnb_x_low"] = p.log_airbnb * p.lowend; p["log_iv_x_low"] = p.log_iv * p.lowend
RATIOS = [f"ratio{s}_lag" for s in [2,3,4,5]]
lines = []
def out(s=""): print(s); lines.append(s)

# ---------- Table 1 ----------
has_both = p.selfpromo.notna()
t1 = p[has_both]
rows = {"Number of TripAdvisor reviews per quarter": t1.n_ta}
for s in range(1,6): rows[f"Number of TripAdvisor {s}-star reviews per quarter"] = t1[f"ta{s}"]
if "n_bk" in p: 
    rows["Number of Booking.com reviews per quarter"] = t1.n_bk
    for k, nm in [("bk_top9","9-10"),("bk_top8","8-10"),("bk_bot5","<=5"),("bk_bot4","<=4")]: rows[f"Number of Booking.com {nm} reviews per quarter"] = t1[k]
rows["Number of competing Airbnb listings per quarter"] = t1.airbnb_lag
rows["Number of competing hotels per quarter"] = t1.comphotels
tab1 = pd.DataFrame({k: [v.mean(), v.std(), v.min(), v.max()] for k, v in rows.items()}, index=["Mean","SD","Min","Max"]).T.round(2)
out(f"# {label}: replication tables\n\n## Table 1. Summary statistics at the hotel-quarter level\n")
out(tab1.to_markdown()); out(f"\nTotal hotels: {t1.hotel_id.nunique():,} | hotel-quarter observations: {len(t1):,} | low-end hotels: {t1.drop_duplicates('hotel_id').lowend.sum()}\n")

# ---------- helpers ----------
def within(df, cols):
    """Demean by hotel (absorbs hotel FE); time FE and city x season FE enter as dummies, also demeaned."""
    dq = pd.get_dummies(df.yq.astype(str), prefix="yq", drop_first=True, dtype=float)
    dcs = pd.get_dummies(df.city_season.astype(str), prefix="cs", dtype=float)
    ref_city = sorted(df.city.astype(str).unique())[0]
    dcs = dcs[[c for c in dcs.columns if not c.startswith(f"cs_{ref_city}_") and not c.endswith("_1")]]   # avoid collinearity with quarter FE
    X = pd.concat([df[cols], dq, dcs], axis=1)
    return X - X.groupby(df.hotel_id).transform("mean")
def stars(pv): return "***" if pv < 0.001 else "**" if pv < 0.01 else "*" if pv < 0.05 else ""
def fmt(b, se, pv): return f"{b:.3f}{stars(pv)} ({se:.3f})"

def run_models(y, models, iv=True):
    """models: list of (name, controls) ; returns dict col -> {var: 'coef (se)'} plus N and first-stage F."""
    res = {}
    for name, extra in models:
        d = p.dropna(subset=[y]).copy()
        d = d[d.n_ta_lag.notna()]
        exog = ["log_comphotels"] + extra
        endog = ["log_airbnb"] + (["log_airbnb_x_low"] if "log_airbnb_x_low" in extra else [])
        exog = [c for c in exog if c not in endog]
        instr = ["log_iv"] + (["log_iv_x_low"] if "log_airbnb_x_low" in endog else [])
        yv = d[y] - d.groupby("hotel_id")[y].transform("mean")
        Xw = within(d, exog + endog + instr)
        # drop all-zero / collinear dummy columns
        Xw = Xw.loc[:, (Xw.abs().sum() > 1e-10)]
        exw, enw, inw = Xw[[c for c in exog if c in Xw]], Xw[endog], Xw[instr]
        dum = Xw[[c for c in Xw.columns if c not in exog + endog + instr]]
        X_ex = pd.concat([exw, dum], axis=1)
        try:
            if iv: m = IV2SLS(yv, X_ex, enw, inw).fit(cov_type="clustered", clusters=d.hotel_id)
            else:  m = IV2SLS(yv, pd.concat([X_ex, enw], axis=1), None, None).fit(cov_type="clustered", clusters=d.hotel_id)
        except Exception as e:
            out(f"_{name} for {y}: estimation failed — {e}_"); res[name] = {"Observations": "failed"}; continue
        col = {}
        for v, lab in [("log_airbnb","log(Airbnb)"),("log_comphotels","log(CompetingHotels)"),("log_reviews_lag","Log(ReviewCount)"),("log_airbnb_x_low","log(Airbnb) x Low-end")]:
            if v in m.params: col[lab] = fmt(m.params[v], m.std_errors[v], m.pvalues[v])
        col["ReviewRatios"] = "YES" if "ratio2_lag" in extra else "NO"
        col["Hotel FE / Time FE / City x Season"] = "YES / YES / YES"
        col["Observations"] = f"{int(m.nobs):,}"
        if iv:
            try:
                fs = m.first_stage.diagnostics
                col["First-stage F (log Airbnb)"] = f"{fs.loc['log_airbnb','f.stat']:.1f}"
            except Exception: pass
        res[name] = col
    return res

def table(title, res, note):
    out(f"\n## {title}\n")
    rows = ["log(Airbnb)","log(CompetingHotels)","Log(ReviewCount)","log(Airbnb) x Low-end","ReviewRatios","Hotel FE / Time FE / City x Season","Observations","First-stage F (log Airbnb)"]
    df = pd.DataFrame({k: {r: v.get(r, "") for r in rows} for k, v in res.items()})
    df = df.loc[[r for r in rows if (df.loc[r] != "").any()]]
    out(df.to_markdown()); out(f"\n{note}\n")

MODELS = [("Model 1", []), ("Model 2", ["log_reviews_lag"] + RATIOS), ("Model 3", ["log_reviews_lag"] + RATIOS + ["log_airbnb_x_low"])]
has_low = p.drop_duplicates("hotel_id").lowend.sum() >= 5
if not has_low: MODELS = MODELS[:2]; out("_Model 3 (low-end interaction) omitted: fewer than 5 low-end hotels in this panel._\n")
NOTE = "*p<0.05, **p<0.01, ***p<0.001; robust SEs clustered at the hotel level in parentheses."
for y, title in [("selfpromo","Table 2. Self-Promotion with 2SLS"), ("demoting_others","Table 3. Demotion Behavior (DemotingOthers) with 2SLS"), ("demotion","Table 8. Being Demoted with 2SLS")]:
    table(title, run_models(y, MODELS, iv=True), NOTE)
    table(title.replace("with 2SLS","— OLS two-way FE (reference)"), run_models(y, MODELS, iv=False), NOTE)

# ---------- Table 5: IV validity ----------
ever = p.groupby("hotel_id").airbnb_lag.transform("max")
res5 = {}
for samp, mask in [("w/o Airbnb ever", ever == 0), ("w/ Airbnb", ever > 0)]:
    for y, lab in [("selfpromo","Promote"),("demoting_others","Demote")]:
        d = p[mask].dropna(subset=[y]); d = d[d.n_ta_lag.notna()]
        if d.hotel_id.nunique() < 20: res5[f"{samp}: {lab}"] = {"Observations": f"n/a (only {d.hotel_id.nunique()} hotels)"}; continue
        cols = ["log_iv","log_comphotels","log_reviews_lag"] + RATIOS
        yv = d[y] - d.groupby("hotel_id")[y].transform("mean"); Xw = within(d, cols); Xw = Xw.loc[:, Xw.abs().sum() > 1e-10]
        m = IV2SLS(yv, Xw, None, None).fit(cov_type="clustered", clusters=d.hotel_id)
        res5[f"{samp}: {lab}"] = {"log(Cmp_Airbnb)": fmt(m.params["log_iv"], m.std_errors["log_iv"], m.pvalues["log_iv"]),
                                  "log(CompetingHotels)": fmt(m.params["log_comphotels"], m.std_errors["log_comphotels"], m.pvalues["log_comphotels"]),
                                  "Log(ReviewCount)": fmt(m.params["log_reviews_lag"], m.std_errors["log_reviews_lag"], m.pvalues["log_reviews_lag"]),
                                  "Observations": f"{int(m.nobs):,}"}
out("\n## Table 5. IV validity: direct correlation between instrument and manipulation\n")
out(pd.DataFrame(res5).fillna("").to_markdown()); out(f"\n{NOTE} ReviewRatios, hotel FE, time FE and city x season FE included.\n")
open(os.path.join(outdir, f"tables_{label}.md"), "w").write("\n".join(lines))
p.to_csv(os.path.join(outdir, f"panel_{label}_estimation.csv"), index=False)
print("\nwritten:", os.path.join(outdir, f"tables_{label}.md"))
