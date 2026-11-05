"""Shared helpers: panel preparation and the paper's 2SLS / OLS specification (used by 08-10)."""
import numpy as np, pandas as pd
from linearmodels.iv import IV2SLS
RATIOS = [f"ratio{s}_lag" for s in [2, 3, 4, 5]]

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    a = np.sin((lat2-lat1)/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin((lon2-lon1)/2)**2
    return 6371.0 * 2 * np.arcsin(np.sqrt(a))

def prep(p, unit="hotel_id"):
    """Add quarter objects, season, city x season, lagged review controls and interaction terms."""
    p = p.copy(); p["q"] = pd.PeriodIndex(p.yq, freq="Q"); p = p.sort_values([unit, "q"]).reset_index(drop=True)
    p["season"] = p.q.dt.quarter; p["city_season"] = p.city.astype(str) + "_" + p.season.astype(str)
    g = p.groupby(unit)
    for c in ["n_ta","ta2","ta3","ta4","ta5"]: p[f"{c}_lag"] = g[c].shift(1)
    ok = (g.q.shift(1) == p.q - 1); p.loc[~ok, [f"{c}_lag" for c in ["n_ta","ta2","ta3","ta4","ta5"]]] = np.nan
    p["n_ta_lag"] = p.n_ta_lag.fillna(0)
    for s in [2,3,4,5]: p[f"ratio{s}_lag"] = np.where(p.n_ta_lag > 0, p[f"ta{s}_lag"].fillna(0) / p.n_ta_lag, 0.0)
    p["log_reviews_lag"] = np.log(p.n_ta_lag + 1)
    if "lowend" in p: p["log_airbnb_x_low"] = p.log_airbnb * p.lowend; p["log_iv_x_low"] = p.log_iv * p.lowend
    return p

def within(df, cols, unit):
    dq = pd.get_dummies(df.yq.astype(str), prefix="yq", drop_first=True, dtype=float)
    dcs = pd.get_dummies(df.city_season.astype(str), prefix="cs", dtype=float)
    ref = sorted(df.city.astype(str).unique())[0]
    dcs = dcs[[c for c in dcs.columns if not c.startswith(f"cs_{ref}_") and not c.endswith("_1")]]
    X = pd.concat([df[cols], dq, dcs], axis=1)
    return X - X.groupby(df[unit]).transform("mean")

def stars(pv): return "***" if pv < 0.001 else "**" if pv < 0.01 else "*" if pv < 0.05 else ""
def fmt(b, se, pv): return f"{b:.3f}{stars(pv)} ({se:.3f})"
LABELS = [("log_airbnb","log(Airbnb)"),("log_comphotels","log(CompetingHotels)"),("log_reviews_lag","Log(ReviewCount)"),("log_airbnb_x_low","log(Airbnb) x Low-end")]

def fit(d, y, extra, unit="hotel_id", iv=True, endog_base="log_airbnb", instr_base="log_iv"):
    """One column: y on log_airbnb (+ interaction) with the paper's controls; returns (results obj, dict of formatted cells)."""
    d = d.dropna(subset=[y]).copy()
    endog = [endog_base] + (["log_airbnb_x_low"] if "log_airbnb_x_low" in extra else [])
    exog = [c for c in ["log_comphotels"] + extra if c not in endog]
    instr = [instr_base] + (["log_iv_x_low"] if "log_airbnb_x_low" in endog else [])
    yv = d[y] - d.groupby(unit)[y].transform("mean")
    Xw = within(d, exog + endog + instr, unit); Xw = Xw.loc[:, Xw.abs().sum() > 1e-10]
    dum = Xw[[c for c in Xw.columns if c not in exog + endog + instr]]
    X_ex = pd.concat([Xw[[c for c in exog if c in Xw]], dum], axis=1)
    if iv: m = IV2SLS(yv, X_ex, Xw[endog], Xw[instr]).fit(cov_type="clustered", clusters=d[unit])
    else:  m = IV2SLS(yv, pd.concat([X_ex, Xw[endog]], axis=1), None, None).fit(cov_type="clustered", clusters=d[unit])
    col = {lab: fmt(m.params[v], m.std_errors[v], m.pvalues[v]) for v, lab in LABELS if v in m.params}
    col["ReviewRatios"] = "YES" if "ratio2_lag" in extra else "NO"; col["Observations"] = f"{int(m.nobs):,}"
    if iv:
        try: col["First-stage F (log Airbnb)"] = f"{m.first_stage.diagnostics.loc[endog_base, 'f.stat']:.1f}"
        except Exception: pass
    return m, col

def models(has_low):
    M = [("Model 1", []), ("Model 2", ["log_reviews_lag"] + RATIOS), ("Model 3", ["log_reviews_lag"] + RATIOS + ["log_airbnb_x_low"])]
    return M if has_low else M[:2]

def table_md(title, res, note="*p<0.05, **p<0.01, ***p<0.001; robust SEs clustered in parentheses."):
    rows = [l for _, l in LABELS] + ["ReviewRatios","Observations","First-stage F (log Airbnb)"]
    df = pd.DataFrame({k: {r: v.get(r, "") for r in rows} for k, v in res.items()})
    df = df.loc[[r for r in rows if (df.loc[r] != "").any()]]
    return f"\n## {title}\n\n" + df.to_markdown() + f"\n\n{note}\n"
