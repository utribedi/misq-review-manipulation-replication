# results/ — every table, figure and statistic of the paper, reproduced

Two parallel sets of outputs exist: **`results/stata/`** holds the Stata `esttab` text tables and Stata graphs that appear verbatim in the slides (course rule: all presented numbers come from Stata), and the Markdown files in **`results/`** are the independent Python (`linearmodels`) estimates of the same specifications plus the extensions. The two agree to the third decimal wherever they overlap.

## Start here

| File | What it is |
|---|---|
| `comparison_with_paper.md` | **The reproducibility assessment.** Side-by-side coefficients (paper vs Texas vs Europe) for every table, data-source status (public / commercial / substitute / unobtainable), what reproduced and what did not, and the extensions. Updated through 4 Nov 2026. |
| `intext_stats.md` | In-text numbers the paper reports outside its tables: Figure 1 group sizes, share of hotels with an Airbnb competitor (76 % vs paper 48 %), effect-size calculation (5.4 pp vs 5.6 pp), mean ratings by tier, Appendix D/G statistics. |
| `extensions.md` | Table I1 by sub-period with the added 2015Q4 break (era dependence), Appendix G segmented Airbnb (price cutoff $34 vs $25), Booking.com reviewer-history excess (EU). |
| `text_measure_TX.md`, `text_measure_EU.md` | Extension 2: the Ott-classifier text measure (share of 5-star reviews flagged deceptive) regressed on Airbnb supply — 0.023* on Texas, null in Europe. |

## Mapping: paper → file

| Paper item | Stata output (in slides) | Python counterpart |
|---|---|---|
| Table 1 summary statistics | `stata/tx_table1.txt`, `stata/eu_summary.txt` | `tables_tx.md`, `tables_eu.md` §Table 1 |
| Table 2 self-promotion | `stata/tx_table2.txt`, `stata/eu_table2.txt` | `tables_*.md`, `panel_*_table2_selfpromotion.rtf` |
| Table 3 demoting others | `stata/tx_table3.txt`, `stata/eu_table3.txt` | `tables_*.md`, `panel_*_table3_demotingothers.rtf` |
| Table 4 mutual demotion (pairs) | `stata/tx_table4.txt`, `stata/eu_table4.txt` | `table4_TX.md`, `table4_EU.md` |
| Table 5 IV validity (hotels with / without Airbnb) | `stata/tx_table5.txt` | `tables_*.md`, `panel_*_table5_iv_validity.rtf` |
| Table 6 look-ahead PSM | `stata/tx_table6.txt` + `stata/tx_table6_balance.txt` (psmatch2 balance) | — |
| Table 7 synthetic control | `table7_gsynth_R.txt` / `.csv` (paper's GSC estimator, R) and `stata/tx_table7.txt` (sdid cross-check); figure `stata/fig_table7_gsynth.png` | — |
| Table 8 being demoted | `stata/tx_table8.txt`, `stata/eu_table8.txt` | `tables_*.md`, `panel_*_table8_beingdemoted.rtf` |
| OLS-FE reference (footnote comparison) | — | `panel_*_ols_fe_reference.rtf` |
| Figure 1 treatment groups A/B/C | counts in `intext_stats.md` | `intext_stats.md` |
| Figure A1 ratings vs Airbnb supply | `stata/figA1_TX.png` | `figures/figA1_TX.png`, `figures/figA1_EU.png` |
| Figure A2 positive / negative share by tier | `stata/figA2_TX.png` | `figures/figA2_TX.png`, `figures/figA2_EU.png` |
| Appendix B1 relative-time (event-study) model | `stata/tx_tableB1.txt`, `stata/figB1_TX.png` | `appendix_BCFH_TX.md` |
| Appendix C1 triplets | `stata/tx_tableC1.txt` | `appendix_BCFH_TX.md` |
| Appendix D trip-type stationarity | `stata/figD1_EU.png` | `figures/figD1_EU.png`, `intext_stats.md` |
| Appendix E1 Gaussian-kernel competition | `stata/tx_tableE1.txt` (1 km), `stata/tx_tableE1_05km.txt` (0.5 km) | `appendix_E_TX_check.md` |
| Appendix F1 uniform thresholds | `stata/tx_tableF1.txt` | `appendix_BCFH_TX.md` |
| Appendix G1 segmented Airbnb competitors | `stata/tx_tableG1.txt` | `extensions.md` |
| Appendix H1 all neighbouring hotels | `stata/tx_tableH1.txt` | `appendix_BCFH_TX.md` |
| Appendix I1 before/after inflection | `stata/tx_tableI1_breaks.txt` | `extensions.md`, `panel_tx_tableI1_inflection.rtf` |
| Extension: text measure | `stata/tx_text_measure.txt` | `text_measure_TX.md`, `text_measure_EU.md` |
| Extension: EU reviewer-history excess | `stata/eu_extension3.txt` | `extensions.md` |

## Other files in `results/stata/`

* `07_stata_outputs.dta` — the Texas panel as Stata saved it after `07_stata_outputs.do` (with generated FE and lag variables), handy for interactive follow-ups.
* `stata op2.dta` — working dataset saved during the final Table 6/7 session.

All Stata tables: 2SLS with `ivreghdfe`, hotel FE + year-quarter FE + city × season FE, standard errors clustered by hotel (by pair / triplet in Table 4 / C1), Kleibergen–Paap F reported. Significance: * p < 0.05, ** p < 0.01, *** p < 0.001, matching the paper's convention.
