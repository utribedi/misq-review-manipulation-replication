# Nie, Zheng & Sarkar (2022) vs. replication — coefficient comparison

Coefficient on log(Airbnb_{t-1}) (SE), Model 1 / Model 2 / Model 3. 2SLS, hotel FE + quarter FE + city x season, SEs clustered by hotel.

| Outcome | Paper (Texas, 64 cities, 2008-2015, N=32,122) | Replication: Texas (Austin/Dallas/Fort Worth, 2011-2019, N=10,068) | Replication: Europe (6 cities, 2015Q3-2017Q3, N=7,118) |
|---|---|---|---|
| Table 2 Self-promotion | 0.021*** (0.006) / 0.020** / 0.020*** ; x Low-end -0.054* | 0.022 (0.017) / 0.018 / 0.022 ; x Low-end -0.023 (0.023) | -0.155 (0.089) / -0.162 (0.092) ; Model 3 n/a |
| Table 3 Demoting others | -0.035*** (0.009) / -0.035*** / -0.035*** ; x Low-end -0.006 | -0.128 (0.090) / -0.130 / -0.128 ; x Low-end -0.013 | -0.565 (0.501) / -0.563 ; n/a |
| Table 8 Being demoted | 0.123* (0.048) / 0.137** / 0.139** ; x Low-end -0.161 | 0.022 (0.013) / 0.021 / 0.017 ; x Low-end 0.027 | -0.004 (0.056) / -0.002 ; n/a |
| log(CompetingHotels), Table 3 | -0.297*** (0.044) | -0.157 (0.099) [OLS-FE: -0.260** (0.097)] | 0.070 (0.165) |
| First-stage strength | KP F = 796.5 | F = 70-90 | F = 3-5 (weak) |
| Table 5 IV validity | IV insignificant for hotels w/o Airbnb; significant w/ Airbnb | same pattern (w/o: 0.005 / 0.286 n.s.; w/: promote 0.005 n.s., demote -0.097*) | no untreated hotels exist (all hotels have Airbnb within 1 km) |
| Table 1 key moments | 10.9 TA reviews/qtr; 3.3 Airbnb competitors (0.55 in 2011Q1 -> 9.2 in 2015Q4); 5.0 competing hotels; 48% hotels w/ Airbnb; 24% low-end | 12.4 TA reviews/qtr; 11.8 Airbnb competitors (0.5 in 2011 -> 7.8 in 2015 -> 32 in 2019); 3.3 competing hotels; 76% w/ Airbnb; 26% low-end | 32.8 TA + 37.5 Booking reviews/qtr; 526 Airbnb competitors; 17.8 competing hotels; 100% w/ Airbnb; <1% low-end |

## Reading
* Texas: every main coefficient has the paper's sign (self-promotion +, demoting others -, being demoted +, competing hotels -), the instrument is strong, and the IV-validity pattern of Table 5 reproduces. Point estimates are not statistically significant: the panel has a third of the paper's observations, three cities instead of 64, and the manipulation measures are one-time-reviewer proxies (no verified-review benchmark exists in public data for Texas). Self-promotion 0.022 vs 0.021 is numerically almost identical.
* Europe: the Mayzlin-style measure (TripAdvisor minus verified Booking.com) is available, but the design does not identify in dense European centres: Airbnb supply is 100x the Texas level, every hotel is treated, and after hotel and quarter fixed effects the competitors'-Airbnb instrument has almost no independent variation (first-stage F 3-5). Estimates are therefore imprecise and should be reported as a boundary condition of the paper's identification strategy, not as a failed replication.

## Data-source status (for the reproducibility assessment)
| Paper source | Role | Status in replication |
|---|---|---|
| TripAdvisor reviews (own crawler) | unverified reviews | Public: HotelRec corpus (Antognini & Faltings 2020) |
| Expedia reviews (own crawler) | verified benchmark | Not public for Texas (would need scraping). Europe substitute: Booking.com 515K (Kaggle/OpenML), verified stays |
| Airbnb listings + AirDNA | supply within 1 km, entry date | Public: Inside Airbnb latest snapshot; entry date from host tenure (host_since no longer published); AirDNA prices (Appendix G only) commercial/unobtainable |
| STR census | hotel tier (price), address | Commercial/unobtainable. Substitute: STR economy-class brand list (TX, 26% low-end); TripAdvisor price tier available but coarse |
| Texas Comptroller hotel tax | operating period, address | Public but not used; operating period proxied by first-to-last review window; coordinates taken from TripAdvisor pages |
| Hotel coordinates (Expedia) | distances | TripAdvisor hotel pages (TX, 449/449); Booking.com file (EU) |

Files: data_extract/panel_tx.csv, data_extract/panel_eu_v2.csv (same as panel_eu.csv once the open copy is closed), results/tables_tx.md, results/tables_eu.md.
Code: code/01-05 (Python, reproducible end-to-end), code/06_tables.do (Stata: reghdfe/ivreghdfe version of the same specifications).

## Added 2026-10-29: remaining tables, in-text results and extensions

| Item | Paper | Replication (Texas unless noted) | File |
|---|---|---|---|
| Table 4 Mutual demotion (pair level), log(Airbnb) | -0.107*** / -0.092*** / -0.092***; x Low-end +0.136*** | **-0.191\* / -0.177\* / -0.164\*** (F=106); x Low-end -0.072 n.s. EU: not identified (F=0.3) | table4_TX.md, table4_EU.md |
| Table I1 before/after 2011Q4 | insignificant before, significant after | <=2011Q4: -0.061 n.s.; 2012Q1-2015Q4 (paper's window): **0.107\* (0.045)**; >=2016Q1: 0.040 n.s. | extensions.md |
| Table G1 segmented Airbnb (price/person, 24th pct) | cutoff $25; 0.020**/0.019**/0.018** | cutoff $34; 0.026/0.021/0.022 (n.s.), same pattern | extensions.md |
| Figure 1 groups A/B/C | (counts not reported) | A=296, B=55, C=98 (Period 1 = through 2016Q2) | intext_stats.md |
| Figures A1/A2 | TA ratings rise with Airbnb; high-end positive share rises, low-end flat | reproduced (figA1_TX, figA2_TX; EU versions too) | results/figures |
| Appendix D trip types | repeated-measures ANOVA p ~ 1; KPSS all stationary | EU, Booking tags: Friedman p = 1.00; KPSS p = 0.07-0.10 (all stationary) | intext_stats.md, figD1_EU.png |
| Appendix G Airbnb ratings | 95.7% rated >= 4.5; mean 4.82 (sd 0.31) | TX 92.2%, mean 4.80 (sd 0.41); EU 84.5%, mean 4.71 | intext_stats.md |
| In-text: KP F | 796.51 | 85.7 (Stata ivreghdfe) | Stata log |
| In-text: effect size 2011-2015 | 0.554 -> 9.187 listings; 5.6 pp | 0.79 (2011Q4) -> 9.29 (2015Q4); 5.4 pp | intext_stats.md |
| In-text: hotels with Airbnb competitor | 48% | 76% (2011-2019 horizon) | intext_stats.md |
| In-text: mean TA rating low/high-end | 3.0 / 4.0 | 3.23 / 4.13 | intext_stats.md |
| In-text: management response rates 4.1% vs 6.8% | from Expedia | not obtainable | — |
| Tables 6-7 (LA-PSM, GSC) | — | not reproduced: matching covariates are STR (unobtainable); GSC feasible but not run | — |

### Extensions
1. **Era dependence.** The self-promotion response is concentrated in the paper's own era (2012-2015, 0.107*) and absent after 2016 as Airbnb becomes ubiquitous — the Texas and Europe findings are the same phenomenon at different stages of Airbnb penetration.
2. **Text-based manipulation measure.** TF-IDF + logistic classifier trained on the Ott et al. deceptive-opinion corpus (5-fold CV accuracy 0.88, benchmark 0.89), scored on all 2.5M reviews. Share of 5-star reviews flagged deceptive rises with Airbnb supply: **0.023\* (0.010) / 0.022\* / 0.022\*** (2SLS, F=86) — significant, and numerically the paper's 0.021; flagged negative reviews do not move (-0.007 n.s.), matching the paper's null on demotion. Correlates 0.46 with the one-time-reviewer measure at the hotel-quarter level. EU: null (weak IV). Files: text_measure_TX.md, text_measure_EU.md, data_extract/scores_*.csv, fake_review_model.joblib.
3. **Verified-platform reviewer-history excess (EU).** Share of TripAdvisor reviews from one-time reviewers (46.9% of 5-star/1-2-star) vs Booking.com one-time reviewers (27.1%); the hotel-quarter excess correlates 0.69 with the Mayzlin-style gap — external validation of the one-time-reviewer proxy used for Texas. Effect on Airbnb supply: null in EU (weak IV).

## Added 2026-11-04: Appendices B, C, F, H (Texas; code/11_appendix_robustness.py builds the panels, code/11_appendix_robustness.do estimates; Stata text in results/stata/tx_tableB1/C1/F1/H1.txt, figure figB1_TX.png)

| Item | Paper | Replication (Texas) |
|---|---|---|
| Table B1 relative-time model (Airbnb_Binary, j = -2..+3) | leads n.s.; treat(0) 0.060* promotion, -0.108* demoting others | leads n.s. (-0.007, 0.007 / 0.060, 0.039); promotion 0.040* at +1; demoting others n.s. throughout; 351 treated, 98 never treated |
| Table C1 triplets | -0.259*** / -0.185*** / -0.178***; x Low-end +1.667*; N = 437,695 | **-0.423*** / -0.386*** / -0.347**** (F = 127); x Low-end -0.127**; 2,403 triplets, N = 24,966 |
| Table F1 uniform thresholds | 0.027*** / 0.025*** / 0.026***; demoting -0.036*** | 0.024 / 0.020 / 0.019 (n.s.); demoting -0.16 (n.s.); unchanged from Tables 2-3, as in the paper |
| Table H1 all neighbouring hotels | 0.022*** / 0.020** / 0.021***; demoting -0.018* | 0.011 / 0.010 / 0.014 (n.s.); demoting -0.076 (n.s.); competing hotels -0.208**; F > 100 |
| Appendix E Gaussian kernel | consistent with main | not run (needs kernel-weighted competitor counts) |

## Added 2026-11-04: Tables 6, 7 and Appendix E (Texas; inputs from code/12_appE_table6_inputs.py, estimation in code/12_tables67_appE.do; Stata text in results/stata/tx_table6.txt, tx_table6_balance.txt, tx_table7.txt, tx_tableE1.txt, tx_tableE1_05km.txt)

| Item | Paper | Replication (Texas) |
|---|---|---|
| Table 6 LA-PSM | 0.034* / 0.031* / 0.030*; demoting -0.084** / -0.086** / -0.087**; N = 10,759 | matched on observable pre-period covariates (STR price/rooms/chain/location unavailable), 101 treated + 101 controls, mean bias 30% -> 12%: 0.050 / 0.035 / 0.010 (n.s.); demoting -0.515 / -0.527 (n.s.); N = 4,424 / 2,916; Model 3 first stage F 0.3 |
| Table 7 GSC | Airbnb treatment 0.029* (all), 0.033* (high), -0.003 (low); demoting -0.034, -0.037*, 0.192 | sdid (no Stata GSC), balanced panel 2012Q1-2019Q2, 88 hotels: ATT -0.028 (0.023) all, -0.025 (0.022) high; demoting 0.015 (0.083), 0.006 (0.094); low-end not estimable (4 treated, 1 control). Not reproduced |
| Table E1 Gaussian kernel | consistent with main results at h = 1 km and 0.5 km (not tabulated) | h = 1 km: 0.015 / 0.013 / 0.017 (n.s.), demoting 0.051 / 0.050 (n.s.), competing hotels -0.80*; h = 0.5 km: 0.013 / 0.012 / 0.015, demoting -0.26 (n.s.); first stage F 240-590 |

## Added 2026-11-04: Table 7 with the paper's estimator (R, code/13_table7_gsynth.R, fect method = ife, full panel, 200 bootstraps; results/table7_gsynth_R.csv/.txt, figure results/stata/fig_table7_gsynth.png)

| Column | Paper (GSC) | Replication (GSC, fect) |
|---|---|---|
| Self-promotion, all | 0.029* (0.013) | **0.033* (0.015)**, p = 0.027, 165 treated / 101 controls |
| Self-promotion, high-end | 0.033* (0.015) | **0.039* (0.017)**, p = 0.024 |
| Self-promotion, low-end | -0.003 (0.073) | 0.009 (0.042) |
| Demoting others, all | -0.034 (0.022) | 0.046 (0.066) |
| Demoting others, high-end | -0.037* (0.019) | 0.004 (0.069) |
| Demoting others, low-end | 0.192 (0.175) | 0.417 (0.381) |
Self-promotion reproduces with the paper's own estimator; demotion does not. The sdid rows above are a Stata cross-check on a balanced 88-hotel panel.
