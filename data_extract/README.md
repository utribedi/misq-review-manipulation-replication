# data_extract/ — all derived data

Everything in this folder is produced by the scripts in `code/` from four public raw sources (HotelRec, Inside Airbnb, Booking.com 515K, Ott et al. corpus). Nothing here was hand-edited. Files ending in `.csv.gz` are gzip-compressed to stay under GitHub's file-size limit — `gunzip -k` them before running the scripts, which expect the plain `.csv` names.

## 1. Filtered raw reviews (from HotelRec, via `code/01_filter_hotelrec.py`)

HotelRec (Antognini & Faltings 2020, https://github.com/Diego999/HotelRec) is 50.4 GB of JSON lines with 50,264,531 TripAdvisor hotel reviews. One streaming pass kept the hotels of interest; the 50 GB source is **not** in this repository.

| File | Rows | Content |
|---|---|---|
| `reviews_TX.csv.gz` | 906,644 reviews, 4,784 hotels | **all Texas hotels**. Columns: `hotel_id` (TripAdvisor d-number), `geo_id` (g-number), `hotel_slug`, `loc_slug` (city), `region`, `author`, `date`, `rating`, six sub-ratings (`sr_service`, `sr_cleanliness`, `sr_value`, `sr_location`, `sr_sleep_quality`, `sr_rooms`). No review text, so it loads straight into Stata. |
| `reviews_EU6.csv.gz` | 1,632,385 reviews, 5,948 hotels | same layout for **London, Paris, Amsterdam, Barcelona, Milan, Vienna** (the six cities covered by the Booking.com 515K file). |
| `hotels_TX.csv`, `hotels_EU6.csv` | one row per hotel | `hotel_id, geo_id, hotel_slug, loc_slug, n_reviews, mean_rating, first_review, last_review`. |

Not shipped (regenerable with `01_filter_hotelrec.py`, only needed by `10_text_classifier.py score`): `reviews_TX.jsonl` (614 MB) and `reviews_EU6.jsonl` (1.3 GB) — the same reviews with title and text. The TripAdvisor page of any hotel is `https://www.tripadvisor.com/Hotel_Review-<geo_id>-<hotel_id>-Reviews-<hotel_slug>-<loc_slug>.html`. HotelRec dates are month-level (`YYYY-MM-01`), hence year-quarter aggregation as in the paper. About 83 % of authors appear exactly once, which is what makes the one-time-reviewer proxy usable.

## 2. Verified-stay benchmark (Europe only)

| File | Rows | Content |
|---|---|---|
| `booking515k.csv.gz` | 515,738 reviews, 1,492 hotels | the **Booking.com 515K Europe hotel reviews** dataset (Jiashen Liu, Kaggle / OpenML), Aug 2015 – Aug 2017, converted from ARFF. Columns include `Hotel_Name`, `Hotel_Address`, `Review_Date`, `Reviewer_Score` (0–10), `Total_Number_of_Reviews_Reviewer_Has_Given`, `Tags` (trip type), `lat`, `lng`, plus an added `city` column. Booking.com only accepts reviews from verified stays, so it plays Expedia's role in the paper. |
| `booking_ta_match.csv` | 1,492 | fuzzy-name crosswalk **Booking hotel → TripAdvisor hotel** within city: `city, booking_name, ta_slug, hotel_id, score`. 1,125 hotels match at score ≥ 90 and enter the EU panel. |

## 3. Hotel geography and tier (Texas)

| File | Rows | Content |
|---|---|---|
| `tx_hotel_geo.csv` | 449 hotels | the Austin / Dallas / Fort Worth hotels in the panel with coordinates read from their TripAdvisor pages (`geo_source` = tripadvisor for all 449), plus `price`, `hclass` (TA star class), `price_tier`, `lowend_price`, `addr`, review counts and operating window (`first_review`–`last_review`). |
| `tx_hotel_geo_ta.json`, `tx_hotel_geo_osm.json` | — | raw geocoding caches: TripAdvisor page scrape and the OpenStreetMap (Nominatim / Photon) fallback that was tried first. |

The low-end flag used everywhere (`lowend`) follows the STR "economy" chain-scale brand list (26 % of Texas hotels; paper: 24 %). The paper's STR census itself is commercial and was not obtainable.

## 4. Estimation panels (one row = hotel × year-quarter unless stated)

| File | Rows | Built by | Used for |
|---|---|---|---|
| `panel_tx.csv` | 15,266 (448 hotels × 2011Q1–2019Q2; 10,068 estimable) | `04_build_panel_tx.py` | **Main Texas panel**: Tables 1–3, 5, 8, I1, G1, Figures 1/A1/A2. Key columns: `selfpromo`, `demotion`, `demoting_others` (one-time-reviewer proxies), `airbnb_lag`, `comphotels`, `iv_airbnb_lag` and their logs, `lowend`, `n_ta`, `ta1…ta5`, `yq`, `city`, `lat`, `lng`. |
| `panel_tx_hotels.csv` | 448 | same | hotel-level attributes for the Texas panel. |
| `panel_eu.csv` / `panel_eu_v2.csv` | 8,451 (939 hotels × 2015Q3–2017Q3) | `03_build_panel_eu.py` | **Main European panel** with Mayzlin-style measures (`share5_ta − sharetop_bk`, etc.) and Booking columns `n_bk, bk_top9, bk_top8, bk_bot5, bk_bot4, bk_avg`. `_v2` is a byte-identical re-run made while the original was locked by Excel. |
| `panel_eu_hotels.csv` / `_v2` | 939 | same | hotel-level attributes for the EU panel. |
| `panel_pairs_TX.csv`, `panel_pairs_EU.csv` | 15,531 / ~110k pair-quarters | `08_table4_pairs.py` | **Table 4** mutual demotion at the hotel-pair level (`pair`, `mutual`, pair-level Airbnb, competitors and instrument). |
| `panel_triplets_TX.csv` | 25,087 triplet-quarters (2,403 triplets) | `11_appendix_robustness.py` | **Appendix C1** mutual demotion within hotel triplets. |
| `panel_tx_appB.csv` | 15,266 | `11_appendix_robustness.py` | **Appendix B1** relative-time model: `treated`, `T` (first treated quarter) and event dummies `ev_m2 … ev_p3`; also the input to `13_table7_gsynth.R` (Table 7). |
| `panel_tx_appFH.csv` | 15,266 | same | **Appendix F1** uniform-threshold measures (`selfpromo_F`, `demotion_F`, `demoting_others_F`) and **Appendix H1** all-tier competitor measures (`comphotels_all`, `demoting_others_all`, `iv_airbnb_lag_all`). |
| `panel_tx_appE.csv` | 15,266 | `12_appE_table6_inputs.py` | **Appendix E1** Gaussian-kernel competition intensity at bandwidth 1 km (`*_k1`) and 0.5 km (`*_k05`). |
| `hotels_tx_lapsm.csv` | 449 hotels | same | **Table 6** look-ahead PSM input: Figure 1 `group` (A/B/C), `treated`, `first_q`, pre-period covariates (`pre_reviews, pre_rating, pre_share5, pre_share12, pre_selfpromo, n_comp_same, opened_before_2011`). |
| `panel_tx_segG.csv` | 15,266 | `09_extensions.py` | **Appendix G** Airbnb competitors segmented by price per person (24th-percentile cutoff = $34). |
| `panel_eu_extension.csv` | 8,451 | same | EU extension: one-time-reviewer shares on TripAdvisor vs Booking.com (`share5_onetime`, `share12_onetime`) — the reviewer-history excess that validates the Texas proxy. |
| `panel_TX_text.csv`, `panel_EU_text.csv` | 15,266 / 8,451 | `10_text_classifier.py panel` | main panels plus the **text-based manipulation measure**: `fake5`, `fake12`, `pfake_mean`, `share_fake5`, `share_fake12`. |
| `figD1_data_EU.csv` | 9 quarters | `07_appendix_figs_stats.py` | **Appendix D** trip-type shares by quarter from Booking.com tags (leisure, business, couple, solo, family, group). |

## 5. Text classifier (extension)

| File | Content |
|---|---|
| `ott_deceptive_opinion.csv` | the Ott, Choi, Cardie & Hancock (2011, 2013) **Deceptive Opinion Spam Corpus**: 1,600 Chicago hotel reviews, half truthful and half crowd-sourced fakes, balanced by polarity (`deceptive, hotel, polarity, source, text`). Training set. |
| `fake_review_model.joblib` | fitted scikit-learn pipeline (TF-IDF word 1–2-grams → logistic regression). |
| `classifier_cv.txt` | 5-fold cross-validation accuracy: 0.882 (sd 0.021), n = 1,600; the published benchmark is ≈ 0.89. |
| `scores_TX.csv` (906k rows), `scores_EU.csv` (1.63M rows) | one row per review: `hotel_id, date, rating, p_fake` = the classifier's deceptive probability. Aggregated into `panel_*_text.csv`. |

## Not in the repository

| File | Size | Why | How to get it back |
|---|---|---|---|
| `Full_HotelRec/HotelRec.txt` | 50.4 GB | far above any Git limit | download from the HotelRec GitHub page, run `code/01_filter_hotelrec.py` |
| `reviews_TX.jsonl`, `reviews_EU6.jsonl` | 0.6 + 1.3 GB | text versions of the shipped CSVs | same script |
| `booking.com 2` (ARFF) | 251 MB | raw OpenML download, already converted to `booking515k.csv.gz` | OpenML / Kaggle "515K Hotel Reviews Data in Europe" |
| `state.json`, `*.log`, `reviews_TX.csv.tmp` | — | checkpoint / empty leftovers of the filter | not needed |
