# code/ — pipeline, in run order

Python builds the datasets; Stata produces every table and figure shown in the presentation (course rule); R is used once, for the paper's generalized synthetic control estimator, which has no Stata implementation. All scripts are run from the repository root unless stated otherwise.

## Stage 0 — raw data reduction (needs the 50 GB HotelRec file; outputs are already shipped)

| File | What it does | Writes |
|---|---|---|
| `01_filter_hotelrec.py` | Resumable streaming pass over `Full_HotelRec/HotelRec.txt` (50,264,531 TripAdvisor reviews). Keeps every Texas hotel (`TX`) and the hotels of London, Paris, Amsterdam, Barcelona, Milan, Vienna (`EU6`). Runs in time-boxed chunks (`python 01_filter_hotelrec.py 140`) and checkpoints to `state.json`. | `data_extract/reviews_TX.csv`, `reviews_EU6.csv` (no text, Stata-ready), `reviews_*.jsonl` (with title + text, used only by the classifier), `hotels_TX.csv`, `hotels_EU6.csv` |
| `02_dedupe_summary.py` | Removes exact duplicate rows left by an interrupted pass of step 01 and prints coverage summaries (2,539,029 reviews kept = filter's own count). | in-place |

## Stage 1 — panel construction (Python)

| File | What it does | Writes |
|---|---|---|
| `04_build_panel_tx.py` | **Texas hotel-quarter panel**, Austin / Dallas / Fort Worth, 2011Q1–2019Q2. Manipulation proxies: `selfpromo` = share of TripAdvisor reviews that are 5-star (4–5 for low-end) *and* written by a one-time reviewer; `demotion` = 1–2-star (1 for low-end) by a one-time reviewer. `demoting_others` as in the paper. Airbnb supply within 1 km, lagged, from Inside Airbnb host tenure; competing hotels = same-tier hotels within 1 km; instrument = Airbnb listings near the focal hotel's competitors excluding its own. Low-end flag from the STR economy-brand list. | `data_extract/panel_tx.csv`, `panel_tx_hotels.csv` |
| `03_build_panel_eu.py` | **European hotel-quarter panel**, six cities, 2015Q3–2017Q3 (the Booking.com 515K window). Mayzlin-style measures: `selfpromo` = share of 5-star TripAdvisor reviews − share of ≥9 Booking.com scores; `demotion` = share of 1–2-star TA − share of ≤5 Booking. Otherwise identical construction to Texas. Uses `booking_ta_match.csv` (fuzzy name crosswalk, 1,125 of 1,492 Booking hotels at ≥90 score). | `data_extract/panel_eu.csv`, `panel_eu_hotels.csv` (`*_v2` copies are identical re-runs written while the original was open in Excel) |
| `11_appendix_robustness.py` | Inputs for Appendices B, C, F, H (Texas): relative-time dummies `ev_m2…ev_p3` around first Airbnb exposure (B1); hotel triplets all within 1 km of each other (C1); uniform thresholds for all hotels (F1); competitors regardless of tier (H1). Also estimates them in Python as a check. | `data_extract/panel_tx_appB.csv`, `panel_tx_appFH.csv`, `panel_triplets_TX.csv`, `results/appendix_BCFH_TX.md` |
| `12_appE_table6_inputs.py` | Inputs for Appendix E (Gaussian-kernel competition intensity, bandwidth 1 km and 0.5 km) and Table 6 (hotel-level file with Figure 1 groups A/B/C and pre-period covariates for look-ahead propensity-score matching). | `data_extract/panel_tx_appE.csv`, `hotels_tx_lapsm.csv`, `results/appendix_E_TX_check.md` |
| `replib.py` | Shared helpers: haversine distance, panel prep (quarters, seasons, lags, interactions), the paper's 2SLS/OLS specification via `linearmodels`, Markdown table writer. Imported by 08–11. | — |

## Stage 2 — estimation (Stata; this is what the slides show)

Requires `reghdfe ivreghdfe ftools ivreg2 ranktest estout psmatch2 sdid` (`ssc install …`). Run from the repository root: `do "code/07_stata_outputs.do"`.

| File | What it does | Writes (all in `results/stata/`) |
|---|---|---|
| `06_tables.do` | First Stata version of Tables 1, 2, 3, 5, 8 and the OLS-FE reference for one panel (`do code/06_tables.do panel_tx`). Superseded by 07 but kept as the minimal spec file. | RTF tables in `results/` |
| `07_stata_outputs.do` | **Every main table and figure in the deck, both panels.** Tables 1–5 and 8, Table I1 before/after breaks, Table G1 segmented Airbnb, text-measure 2SLS, EU extension; Figures A1, A2 (Stata graphs, Times New Roman, monochrome), D1. | `tx_table1…5.txt`, `tx_table8.txt`, `tx_tableG1.txt`, `tx_tableI1_breaks.txt`, `tx_text_measure.txt`, `eu_table2/3/4/8.txt`, `eu_summary.txt`, `eu_extension3.txt`, `figA1_TX.png`, `figA2_TX.png`, `figD1_EU.png`, `07_stata_outputs.dta` |
| `11_appendix_robustness.do` | Appendix B1 (relative-time model + event-study figure), C1 (triplets, 2SLS), F1 (uniform thresholds), H1 (all neighbouring hotels). | `tx_tableB1.txt`, `tx_tableC1.txt`, `tx_tableF1.txt`, `tx_tableH1.txt`, `figB1_TX.png` |
| `12_tables67_appE.do` | Table E1 (kernel competition, 1 km and 0.5 km), Table 6 (look-ahead PSM with `psmatch2` + balance table), Table 7 Stata stand-in (`sdid` synthetic DiD on a balanced 2012Q1–2019Q2 sub-panel). | `tx_tableE1.txt`, `tx_tableE1_05km.txt`, `tx_table6.txt`, `tx_table6_balance.txt`, `tx_table7.txt` |

## Stage 2b — Table 7 with the paper's estimator (R)

| File | What it does | Writes |
|---|---|---|
| `13_table7_gsynth.R` | Generalized synthetic control (Xu 2017) via `fect(method = "ife")` on the full Texas panel with binary absorbing Airbnb treatment, 200 bootstraps; `gsynth` on the balanced panel as a cross-check. Install `fect`/`gsynth` from CRAN (`cloud.r-project.org` mirror). | `results/table7_gsynth_R.csv`, `table7_gsynth_R.txt`, `results/stata/fig_table7_gsynth.png` |

## Stage 3 — Python estimation counterparts and extensions

These reproduce the Stata results independently (`linearmodels` IV2SLS, clustered by hotel) and run the extensions.

| File | What it does | Writes |
|---|---|---|
| `05_estimate.py` | Tables 1, 2, 3, 5, 8, first stage and OLS-FE counterpart for one panel: `python code/05_estimate.py data_extract/panel_tx.csv TX results`. | `results/tables_tx.md`, `tables_eu.md` |
| `07_appendix_figs_stats.py` | Model-free figures (1, A1, A2), Appendix D (trip-type shares, Friedman/ANOVA, KPSS), Appendix G (Airbnb rating distribution), in-text statistics (effect size, share of hotels with Airbnb competitors, mean ratings by tier). | `results/intext_stats.md`, `results/figures/*.png`, `data_extract/figD1_data_EU.csv` |
| `08_table4_pairs.py` | Table 4: mutual demotion at the hotel-pair level, pair FE, clustered by pair. | `data_extract/panel_pairs_*.csv`, `results/table4_TX.md`, `table4_EU.md` |
| `09_extensions.py` | Table I1 replicated and extended with a 2015Q4 break (era dependence); Appendix G segmented Airbnb competitors by price per person; Booking.com reviewer-history excess (EU). | `data_extract/panel_tx_segG.csv`, `panel_eu_extension.csv`, `results/extensions.md` |
| `10_text_classifier.py` | Text-based manipulation measure: TF-IDF (1–2-grams) + logistic regression trained on the Ott et al. deceptive-opinion corpus (5-fold CV accuracy 0.88), scores all 2.5M reviews in resumable chunks, aggregates to hotel-quarter, estimates the paper's 2SLS with the text outcomes. Modes: `train`, `score <TX|EU>`, `panel <TX|EU>`. | `data_extract/fake_review_model.joblib`, `classifier_cv.txt`, `scores_*.csv`, `panel_*_text.csv`, `results/text_measure_*.md` |

## Notes

* All Python scripts take explicit directory arguments (see each docstring) so they can run on a fast local disk and copy results back; the OneDrive project folder was too slow for line-by-line I/O.
* Stata do-files must be run from the repository root (they use `data_extract/...` and `results/stata/...` relative paths).
* `__pycache__`, `.RData` and `.Rhistory` are git-ignored.
