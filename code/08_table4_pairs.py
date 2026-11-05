"""
Table 4 of Nie et al. (2022): mutual demotion at the hotel-pair level.
For each pair (A,B) of same-tier competitors within 1 km:  MutualDemoting_t = Demoting(A->B)_t + Demoting(B->A)_t,
where Demoting(B->A) = B's demoting reviews in t (Demotion_B x n_ta_B) attributed evenly over B's competitors.
Pair-level Airbnb = |Airbnb(A) ∩ Airbnb(B)| (lagged); pair-level competing hotels = |Comp(A) ∩ Comp(B)|;
IV = Airbnb listings near the pair's shared competitors, excluding the pair's own. Pair FE + quarter FE + city x season; SEs clustered by pair.
Usage: python3 08_table4_pairs.py <label TX|EU> <workdir> <outdir>
"""
import sys, os, glob, itertools, numpy as np, pandas as pd
from replib import haversine, prep, fit, models, table_md
label, WORK, OUT = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(OUT, exist_ok=True)
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."); AB = os.path.join(ROOT, "airbnb")
p = pd.read_csv(os.path.join(WORK, "panel_tx.csv" if label == "TX" else "panel_eu.csv")); p["q"] = pd.PeriodIndex(p.yq, freq="Q")
hot = p.drop_duplicates("hotel_id")[["hotel_id","city","lat","lng","lowend"]].reset_index(drop=True)
Q0, Q1 = p.q.min(), p.q.max()
CITY = {"TX": {"Austin":"austin","Dallas":"dallas","Fort Worth":"fort-worth"}, "EU": {"London":"london","Paris":"paris","Amsterdam":"amsterdam","Barcelona":"barcelona","Milan":"milan","Vienna":"vienna"}}[label]
ab = []
for city, slug in CITY.items():
    d = pd.read_csv(glob.glob(os.path.join(AB, f"{slug}_listings_*.csv.gz"))[0], usecols=["id","latitude","longitude","last_scraped","hosts_time_as_host_years","hosts_time_as_host_months"], low_memory=False)
    months = d.hosts_time_as_host_years.fillna(0)*12 + d.hosts_time_as_host_months.fillna(0)
    d["start_q"] = (pd.to_datetime(d.last_scraped) - pd.to_timedelta(months*30.44, unit="D")).dt.to_period("Q"); d["city"] = city; ab.append(d)
ab = pd.concat(ab)
quarters = pd.period_range(Q0 - 1, Q1, freq="Q")
rows_ab, comp = {}, {}
for _, h in hot.iterrows():
    a = ab if label == "TX" else ab[ab.city == h.city]
    near = a[haversine(h.lat, h.lng, a.latitude.values, a.longitude.values) <= 1.0]
    rows_ab[h.hotel_id] = {q: set(near.id[near.start_q <= q]) for q in quarters}
    hh = hot[hot.hotel_id != h.hotel_id]; dh = haversine(h.lat, h.lng, hh.lat.values, hh.lng.values)
    comp[h.hotel_id] = set(hh.hotel_id[(dh <= 1.0) & (hh.lowend.values == h.lowend)])
# per-hotel-quarter demoting reviews attributed to each competitor
px = p.set_index(["hotel_id","q"])
ncomp = pd.Series({h: max(len(comp[h]), 1) for h in comp})
dem_per_comp = ((px.demotion * px.n_ta) / px.index.get_level_values(0).map(ncomp).values).to_dict()
first = px.groupby(level=0).apply(lambda d: d[d.n_ta.fillna(0) > 0].index.get_level_values(1).min() if (d.n_ta.fillna(0) > 0).any() else None)
last  = px.groupby(level=0).apply(lambda d: d[d.n_ta.fillna(0) > 0].index.get_level_values(1).max() if (d.n_ta.fillna(0) > 0).any() else None)
active = lambda c, q: first.get(c) is not None and first[c] <= q <= last[c]
pairs = sorted({tuple(sorted((a, b))) for a in comp for b in comp[a]})
print(f"{label}: {len(pairs):,} same-tier competing pairs")
rows = []
for a, b in pairs:
    shared = comp[a] & comp[b]
    for q in pd.period_range(Q0, Q1, freq="Q"):
        da, db = dem_per_comp.get((a, q), np.nan), dem_per_comp.get((b, q), np.nan)
        if pd.isna(da) or pd.isna(db): continue
        own = rows_ab[a][q-1] | rows_ab[b][q-1]
        iv = set()
        for c in shared:
            if active(c, q-1): iv |= rows_ab[c][q-1]
        ra, rb = px.loc[(a, q)], px.loc[(b, q)]
        rows.append(dict(pair=f"{a}|{b}", yq=str(q), city=ra.city, lowend=int(ra.lowend), mutual=da + db,
                         airbnb_lag=len(rows_ab[a][q-1] & rows_ab[b][q-1]), comphotels=sum(active(c, q-1) for c in shared), iv_airbnb_lag=len(iv - own),
                         n_ta=ra.n_ta + rb.n_ta, ta2=ra.ta2+rb.ta2, ta3=ra.ta3+rb.ta3, ta4=ra.ta4+rb.ta4, ta5=ra.ta5+rb.ta5))
pp = pd.DataFrame(rows)
for c, src in [("log_airbnb","airbnb_lag"),("log_comphotels","comphotels"),("log_iv","iv_airbnb_lag")]: pp[c] = np.log(pp[src] + 1)
pp = prep(pp, unit="pair"); pp.to_csv(os.path.join(OUT, f"panel_pairs_{label}.csv"), index=False)
print(f"pair-quarter rows: {len(pp):,}; mean mutual demotion {pp.mutual.mean():.3f}; mean shared Airbnb {pp.airbnb_lag.mean():.1f}")
has_low = pp.drop_duplicates("pair").lowend.sum() >= 5
res_iv, res_ols = {}, {}
for name, extra in models(has_low):
    try: res_iv[name] = fit(pp, "mutual", extra, unit="pair", iv=True)[1]
    except Exception as e: res_iv[name] = {"Observations": f"failed: {e}"}
    try: res_ols[name] = fit(pp, "mutual", extra, unit="pair", iv=False)[1]
    except Exception as e: res_ols[name] = {"Observations": f"failed: {e}"}
md = f"# Table 4 ({label}): Mutual demotion, hotel-pair level\n\nPairs: {pp.pair.nunique():,}; pair-quarters: {len(pp):,}\n"
md += table_md("Table 4. Mutual Demotion Behavior with 2SLS", res_iv, "*p<0.05, **p<0.01, ***p<0.001; SEs clustered by hotel pair. Pair FE, quarter FE, city x season FE.")
md += table_md("Table 4 — OLS two-way FE (reference)", res_ols, "*p<0.05, **p<0.01, ***p<0.001; SEs clustered by hotel pair.")
open(os.path.join(OUT, f"table4_{label}.md"), "w").write(md); print(md)
