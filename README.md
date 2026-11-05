# Replication of Nie, Zheng & Sarkar (2022, *MIS Quarterly*)

**Paper.** Nie, L., Zheng, Z. (E.), & Sarkar, S. (2022). *Competing with the Sharing Economy: Incumbents' Reaction on Review Manipulation.* MIS Quarterly, 46(3). The paper shows that when Airbnb supply grows near a hotel, the hotel posts more self-promoting (fake positive) reviews on TripAdvisor and fewer reviews that demote nearby competing hotels. Manipulation is measured Mayzlin-style: the gap between a hotel's rating distribution on an unverified site (TripAdvisor) and a verified-stay site (Expedia).

**This repository** contains a full, from-scratch replication built for the Empirical MIS research seminar at Iowa State University (Fall 2026, Week 10 presentation, 5 November 2026) by Uttaran Tribedi. The paper's data and code are not public, so every dataset was re-collected from public sources and every table, figure, appendix result and in-text statistic was re-estimated, followed by three extension analyses.

---

## Headline results

| | Paper (Texas, 64 cities, 2008–2015) | Replication: Texas (Austin / Dallas / Fort Worth, 2011–2019) | Replication: Europe (6 cities, 2015Q3–2017Q3) |
|---|---|---|---|
| Table 2 — self-promotion ← log(Airbnb) | 0.021*** | **0.022** (0.017), same sign, n.s. | −0.155 (0.089) |
| Table 3 — demoting others ← log(Airbnb) | −0.035*** | −0.128 (0.090), same sign, n.s. | −0.565 (0.501) |
| Table 4 — mutual demotion (pairs) | −0.107*** | **−0.191\*** | not identified |
| Table 7 — self-promotion, generalized synthetic control | 0.029* | **0.033\*** (fect/gsynth in R) | — |
| Appendix C — triplets | −0.259*** | **−0.423\*\*\*** | — |
| First-stage strength (KP F) | 796.5 | 70–90 | 3–5 (weak) |
| Text-based manipulation measure (extension) | — | **0.023\*** | null (weak IV) |

Reading: on the Texas panel every main coefficient reproduces the paper's sign, the instrument is strong, and the IV-validity pattern (Table 5), the pair/triplet results (Table 4, C1), the generalized synthetic control (Table 7) and the text-based extension reproduce in sign *and* significance. Main-table point estimates match in magnitude (0.022 vs 0.021) but not in significance, because the panel is a third of the paper's size and the manipulation measure is a one-time-reviewer proxy (no verified-review benchmark exists in public data for Texas). The European panel has the paper's own Mayzlin-style measure (TripAdvisor minus verified Booking.com) but the design does not identify there: every hotel is treated and the instrument has no independent variation — a boundary condition of the paper's identification strategy rather than a failed replication. The full table-by-table comparison is in [`results/comparison_with_paper.md`](results/comparison_with_paper.md).

---

## Repository layout

```
.
├── code/           Python (data construction), Stata (all estimation in the deck), R (Table 7 GSC)   -> code/README.md
├── data_extract/   Everything derived from the raw sources: filtered reviews, crosswalks, panels, scores -> data_extract/README.md
├── airbnb/         Inside Airbnb listings snapshots for the 9 cities (inputs)                           -> airbnb/README.md
├── results/        Tables, figures, in-text statistics, comparison with the paper                       -> results/README.md
├── slides/         Presentation deck (.pptx) and presenter notes                                        -> slides/README.md
└── paper/          Reference to the original article (DOI; the PDF itself is not redistributed)
```

Each folder's README documents every file in it.

## Data sources and what replaced what

| Paper's source | Role in the paper | What this replication uses | Status |
|---|---|---|---|
| TripAdvisor reviews (own crawler) | unverified reviews, manipulation numerator | **HotelRec** corpus (Antognini & Faltings 2020), 50.3M TripAdvisor reviews, filtered to Texas and six European cities | public |
| Expedia reviews (own crawler) | verified-stay benchmark | Texas: none public → **one-time-reviewer proxy** (Luca & Zervas 2016). Europe: **Booking.com 515K** reviews (Kaggle/OpenML), verified stays | substitute |
| Airbnb listings + AirDNA | Airbnb supply within 1 km, entry date | **Inside Airbnb** latest snapshot per city; entry date from host tenure (`host_since` is no longer published) | public (survivorship caveat) |
| STR census | hotel tier, address, PSM covariates | STR economy-brand list for the low-end flag; TripAdvisor hotel pages for coordinates | commercial / unobtainable |
| Texas Comptroller hotel-tax data | operating period | first-to-last review window | public but not needed |
| Ott et al. deceptive-opinion corpus | — (extension) | 1,600 labelled hotel reviews, trains the text classifier | public |

The only raw input not in this repository is `HotelRec.txt` (50 GB). It is public (https://github.com/Diego999/HotelRec); `code/01_filter_hotelrec.py` reduces it to the two review files shipped here as `data_extract/reviews_TX.csv.gz` and `reviews_EU6.csv.gz`, so the entire pipeline from step 02 onward runs from this repository alone.

## Reproducing

```bash
pip install -r requirements.txt          # pandas, numpy, linearmodels, scikit-learn, joblib, matplotlib, statsmodels
cd data_extract && gunzip -k reviews_TX.csv.gz reviews_EU6.csv.gz booking515k.csv.gz && cd ..

# 1. Panels (Python)
python code/04_build_panel_tx.py                       # -> data_extract/panel_tx.csv
python code/03_build_panel_eu.py                       # -> data_extract/panel_eu.csv
python code/11_appendix_robustness.py data_extract airbnb results
python code/12_appE_table6_inputs.py  data_extract airbnb data_extract

# 2. All tables and figures in the deck (Stata 17+, run from the repo root)
#    ssc install reghdfe ivreghdfe ftools ivreg2 ranktest estout psmatch2 sdid
do code/07_stata_outputs.do
do code/11_appendix_robustness.do
do code/12_tables67_appE.do

# 3. Table 7 with the paper's own estimator (R: fect, gsynth)
Rscript code/13_table7_gsynth.R

# Python counterparts / extensions (optional)
python code/05_estimate.py data_extract/panel_tx.csv TX results
python code/08_table4_pairs.py TX data_extract results
python code/09_extensions.py data_extract results
python code/10_text_classifier.py train data_extract      # then: score TX data_extract ; panel TX data_extract results
```

Outputs land in `results/` (Markdown tables from Python) and `results/stata/` (plain-text `esttab` tables and PNG figures from Stata), already committed here so nothing has to be re-run to inspect them.

## Course requirements covered

1. **Data collected** — explained in `data_extract/README.md` and slides 3–6.
2. **Every table and figure of the paper, including appendices** — Tables 1–8, Figures 1, A1, A2, Appendices B–I; mapping in `results/README.md`.
3. **Comparison with the paper, what could and could not be replicated** — `results/comparison_with_paper.md`.
4. **Extensions** — era dependence (2012–2015 vs post-2016), a text-based manipulation measure (Ott-corpus classifier), and a verified-platform reviewer-history validation of the one-time-reviewer proxy; `results/extensions.md`, `results/text_measure_*.md`.

## Licences and attribution

Code in `code/` is released under the MIT licence (see `LICENSE`). Data files keep their original terms: Inside Airbnb is CC BY 4.0; HotelRec is released by Antognini & Faltings (2020) for research use; the Booking.com 515K file is the Kaggle/OpenML public dataset (Jiashen Liu); the Ott et al. corpus is distributed by its authors for research. The article itself is not redistributed; `paper/README.md` gives the DOI.
