"""
Model-free figures and in-text statistics of Nie et al. (2022), reproduced on both panels.
  Figure 1  : treatment groups A/B/C (Airbnb exposure in first two-thirds vs last third of the horizon)
  Figure A1 : average TripAdvisor (and Booking) rating by quarter vs mean Airbnb supply
  Figure A2 : share of positive / negative TripAdvisor ratings by quarter, low-end vs high-end
  Appendix D: trip-type shares by quarter (Booking.com tags, EU only) + one-way repeated-measures ANOVA + KPSS
  Appendix G: distribution of Airbnb listing ratings (Inside Airbnb review_scores_rating)
  In-text   : effect-size calculation, share of hotels with Airbnb competitors, mean ratings by tier
Usage: python3 07_appendix_figs_stats.py <workdir with panel_tx.csv, panel_eu.csv, booking515k.csv> <outdir>
"""
import sys, os, re, glob, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy import stats
plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"], "font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
WORK, OUT = sys.argv[1], sys.argv[2]; FIG = os.path.join(OUT, "figures"); os.makedirs(FIG, exist_ok=True)
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."); AB = os.path.join(ROOT, "airbnb")
L = []
def out(s=""): print(s); L.append(s)
out("# In-text statistics and model-free figures\n")
for label, fn in [("TX", "panel_tx.csv"), ("EU", "panel_eu.csv")]:
    p = pd.read_csv(os.path.join(WORK, fn)); p["q"] = pd.PeriodIndex(p.yq, freq="Q")
    ok = p[p.n_ta.fillna(0) > 0].copy()
    out(f"## {label} panel\n")
    # --- hotels with >=1 Airbnb competitor (paper: 48%)
    ever = ok.groupby("hotel_id").airbnb_lag.max()
    out(f"- Hotels with at least one competing Airbnb listing at some point: {(ever>0).mean():.1%} (paper: 48%)")
    # --- Figure 1 groups (first two-thirds vs last third of quarters)
    qs = sorted(p.q.unique()); cut = qs[int(len(qs)*2/3) - 1]
    g1 = p[p.q <= cut].groupby("hotel_id").airbnb_lag.max() > 0; g2 = p[p.q > cut].groupby("hotel_id").airbnb_lag.max() > 0
    A, B, C = (g1 & g2).sum(), (~g1 & g2).sum(), (~g1 & ~g2).sum()
    out(f"- Figure 1 groups (Period 1 = through {cut}, Period 2 after): A (Airbnb in both) = {A}, B (only in Period 2) = {B}, C (never) = {C}")
    # --- effect size as in the paper: log(mean Airbnb last / first) x beta
    byq = ok.groupby("q").airbnb_lag.mean()
    beta = 0.022 if label == "TX" else -0.155
    windows = [("2011Q4","2015Q4"), ("2011Q4","2019Q2")] if label == "TX" else [(str(byq.index[0]), str(byq.index[-1]))]
    for a, b in windows:
        fa_, la_ = byq.get(pd.Period(a), np.nan), byq.get(pd.Period(b), np.nan)
        out(f"- Mean competing Airbnb listings: {fa_:.2f} in {a} -> {la_:.2f} in {b}; implied effect log({la_:.2f}/{fa_:.2f}) x {beta} = {np.log(la_/fa_)*beta*100:.1f} pp (paper: 0.554 in 2011Q1 -> 9.187 in 2015Q4, log ratio x 0.021 = 5.6 pp)")
    # --- mean ratings by tier (paper: TA 3.0 low / 4.0 high; Expedia 3.1 / 4.1)
    ok["mean_ta"] = (ok.ta1*1+ok.ta2*2+ok.ta3*3+ok.ta4*4+ok.ta5*5)/ok.n_ta
    m = ok.groupby("lowend").apply(lambda d: np.average(d.mean_ta, weights=d.n_ta), include_groups=False)
    out(f"- Mean TripAdvisor rating: low-end {m.get(1, float('nan')):.2f}, high-end {m.get(0, float('nan')):.2f} (paper: 3.0 / 4.0)")
    if "n_bk" in ok:
        bk = pd.read_csv(os.path.join(WORK, "booking515k.csv"), usecols=["Hotel_Name","Reviewer_Score"], low_memory=False)
        tier = ok.drop_duplicates("hotel_id").set_index("Hotel_Name").lowend
        bk["lowend"] = bk.Hotel_Name.map(tier); bk["Reviewer_Score"] = pd.to_numeric(bk.Reviewer_Score, errors="coerce")
        mb = bk.dropna(subset=["lowend"]).groupby("lowend").Reviewer_Score.mean()
        out(f"- Mean Booking.com score (0-10): low-end {mb.get(1, float('nan')):.2f}, high-end {mb.get(0, float('nan')):.2f} (paper Expedia: 3.1 / 4.1 on 5-point scale)")
    # --- Figure A1: average rating by quarter vs Airbnb supply
    fa = ok.groupby("q").apply(lambda d: pd.Series({"ta": np.average(d.mean_ta, weights=d.n_ta), "airbnb": d.airbnb_lag.mean(),
                               "bk": (np.average((d.bk_top9/d.n_bk).fillna(0), weights=d.n_bk) if "n_bk" in d else np.nan)}), include_groups=False)
    fig, ax = plt.subplots(figsize=(6.5, 3.6)); x = fa.index.to_timestamp()
    ax.plot(x, fa.ta, color="black", lw=1.6, label="TripAdvisor mean rating (1-5)")
    ax.set_ylabel("Mean TripAdvisor rating"); ax2 = ax.twinx(); ax2.spines["top"].set_visible(False)
    ax2.plot(x, fa.airbnb, color="grey", lw=1.2, ls="--", label="Mean competing Airbnb listings"); ax2.set_ylabel("Competing Airbnb listings (mean)")
    if "n_bk" in ok:
        ax3 = ax.twinx(); ax3.spines["right"].set_position(("axes", 1.18)); ax3.plot(x, fa.bk, color="black", lw=1.2, ls=":", label="Booking share of 9-10 scores"); ax3.set_ylabel("Booking.com share 9-10")
    ax.set_title(f"Figure A1 ({label}). Average ratings and Airbnb supply by quarter", loc="left", fontsize=11)
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels(); ax.legend(h1+h2, l1+l2, frameon=False, fontsize=9, loc="upper left")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, f"figA1_{label}.png"), dpi=200); plt.close(fig)
    # --- Figure A2: positive / negative shares by tier
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.4), sharey=True)
    for ax, (lo, name) in zip(axes, [(1, "Low-end hotels"), (0, "High-end hotels")]):
        d = ok[ok.lowend == lo]
        if len(d) == 0: ax.set_title(name + " (none)"); continue
        s = d.groupby("q").apply(lambda g: pd.Series({"pos": g.share5_ta.mul(g.n_ta).sum()/g.n_ta.sum(), "neg": g.share12_ta.mul(g.n_ta).sum()/g.n_ta.sum()}), include_groups=False)
        ax.plot(s.index.to_timestamp(), s.pos, color="black", lw=1.6, label="Positive share"); ax.plot(s.index.to_timestamp(), s.neg, color="grey", lw=1.6, label="Negative share")
        ax.set_title(name, fontsize=11); ax.legend(frameon=False, fontsize=9)
    fig.suptitle(f"Figure A2 ({label}). Proportions of positive and negative TripAdvisor ratings", x=0.01, ha="left", fontsize=11)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, f"figA2_{label}.png"), dpi=200); plt.close(fig)
    out(f"- Figures saved: figA1_{label}.png, figA2_{label}.png")
    out("")

# --- Appendix D (EU only): trip types from Booking tags
bk = pd.read_csv(os.path.join(WORK, "booking515k.csv"), usecols=["Review_Date","Tags"], low_memory=False)
bk["q"] = pd.to_datetime(bk.Review_Date, errors="coerce").dt.to_period("Q")
TYPES = {"Leisure trip":"leisure", "Business trip":"business", "Couple":"couple", "Solo traveler":"solo", "Family":"family", "Group":"group/friends"}
for k, v in TYPES.items(): bk[v] = bk.Tags.astype(str).str.contains(k, regex=False)
sh = bk.groupby("q")[list(TYPES.values())].mean(); sh = sh[(sh.index >= "2015Q3") & (sh.index <= "2017Q3")]
out("## Appendix D (EU): trip-type shares by quarter (Booking.com tags)\n"); out(sh.round(3).to_markdown())
sh.reset_index().assign(q=lambda d: d.q.astype(str)).to_csv(os.path.join(OUT, "figD1_data_EU.csv"), index=False)
# repeated-measures (within-quarter) ANOVA analogue: Friedman test across quarters; KPSS stationarity per series
fr = stats.friedmanchisquare(*[sh.loc[q].values for q in sh.index])   # quarters = repeated measures, trip types = subjects
out(f"\n- Friedman test (non-parametric repeated-measures ANOVA) that shares change across quarters: chi2={fr.statistic:.2f}, p={fr.pvalue:.3f} (paper: p close to 1)")
try:
    from statsmodels.tsa.stattools import kpss
    kp = {c: kpss(sh[c].values, regression="c", nlags=1)[1] for c in sh.columns}
    out("- KPSS p-values (H0: stationary): " + ", ".join(f"{k} {v:.2f}" for k, v in kp.items()) + "  (paper: all stationary)")
except Exception as e: out(f"- KPSS not run: {e}")
fig, ax = plt.subplots(figsize=(6.5, 3.4))
for c in sh.columns: ax.plot(sh.index.to_timestamp(), sh[c], lw=1.4, label=c)
ax.set_ylabel("Share of Booking.com reviews"); ax.legend(frameon=False, fontsize=8, ncol=3); ax.set_title("Figure D1 (EU). Trip-type shares by quarter", loc="left", fontsize=11)
fig.tight_layout(); fig.savefig(os.path.join(FIG, "figD1_EU.png"), dpi=200); plt.close(fig)

# --- Appendix G: Airbnb rating distribution (paper: 95.7% rated 4.5 or 5; mean 4.82, sd 0.31)
out("\n## Appendix G: Airbnb listing ratings (Inside Airbnb review_scores_rating)\n")
for label, cities in [("TX", ["austin","dallas","fort-worth"]), ("EU", ["london","paris","amsterdam","barcelona","milan","vienna"])]:
    r = pd.concat([pd.read_csv(glob.glob(os.path.join(AB, f"{c}_listings_*.csv.gz"))[0], usecols=["review_scores_rating"], low_memory=False) for c in cities]).review_scores_rating.dropna()
    out(f"- {label}: {len(r):,} rated listings; share >= 4.5: {(r>=4.5).mean():.1%}; share < 3.5: {(r<3.5).mean():.1%}; mean {r.mean():.2f}, sd {r.std():.2f}")
open(os.path.join(OUT, "intext_stats.md"), "w").write("\n".join(L)); print("\nwritten", os.path.join(OUT, "intext_stats.md"))
