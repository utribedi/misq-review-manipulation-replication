# slides/ — Week 10 presentation (5 November 2026)

| File | Content |
|---|---|
| `replication_slides.pptx` | The 31-slide deck presented in the Empirical MIS research seminar (minimalist, Times New Roman; every table is pasted Stata output from `results/stata/`). |
| `presenter_notes.pdf` | Slide-by-slide presenter narrative: what to say, the numbers, why each choice was made, the link to the paper, and the question most likely to be asked. Opens with "the story in nine beats". |

## Deck outline

| # | Slide | Backing file |
|---|---|---|
| 1 | Title | — |
| 2 | Replication strategy with two independent setups (Texas proxy measure / Europe verified measure) | `README.md` |
| 3 | Data and what each source became | `data_extract/README.md` |
| 4 | Data pipeline | `code/README.md` |
| 5 | Measures | `code/03_build_panel_eu.py`, `04_build_panel_tx.py` docstrings |
| 6 | Table 1 summary statistics | `results/stata/tx_table1.txt` |
| 7–10 | Tables 2, 3, 4, 8 — self-promotion, demoting others, mutual demotion, being demoted (Texas, 2SLS) | `results/stata/tx_table2/3/4/8.txt` |
| 11 | Table 5 — validity of the instrument | `results/stata/tx_table5.txt` |
| 12 | Table 6 — look-ahead PSM | `results/stata/tx_table6.txt`, `tx_table6_balance.txt` |
| 13 | Table 7 — generalized synthetic control (R) with sdid cross-check | `results/table7_gsynth_R.txt`, `results/stata/fig_table7_gsynth.png` |
| 14 | Europe — the paper's measure, but no identification | `results/stata/eu_*.txt` |
| 15 | Figures A1 and A2 — model-free evidence | `results/stata/figA1_TX.png`, `figA2_TX.png` |
| 16 | Reproduction status, table by table | `results/comparison_with_paper.md` |
| 17 | Results reported in the text | `results/intext_stats.md` |
| 18–24 | Appendices G1, B1, F1, H1, C1, E1, D1 | `results/stata/tx_tableG1/B1/F1/H1/C1/E1.txt`, `figB1_TX.png`, `figD1_EU.png` |
| 25 | Obstacles | `results/comparison_with_paper.md` (data-source status) |
| 26 | Overall reproducibility | same |
| 27 | What the replication puts in question | — |
| 28 | Extension 1 — the effect belongs to Airbnb's growth phase (2012–2015: 0.107*) | `results/extensions.md`, `results/stata/tx_tableI1_breaks.txt` |
| 29 | Extension 2 — text-based manipulation measure (0.023*) | `results/text_measure_TX.md`, `results/stata/tx_text_measure.txt` |
| 30 | Extension 3 — validating the proxy on a verified platform (Europe) | `results/extensions.md`, `results/stata/eu_extension3.txt` |
| 31 | Conclusion | — |
