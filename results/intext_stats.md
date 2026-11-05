# In-text statistics and model-free figures

## TX panel

- Hotels with at least one competing Airbnb listing at some point: 76.3% (paper: 48%)
- Figure 1 groups (Period 1 = through 2016Q2, Period 2 after): A (Airbnb in both) = 296, B (only in Period 2) = 55, C (never) = 98
- Mean competing Airbnb listings: 0.79 in 2011Q4 -> 9.29 in 2015Q4; implied effect log(9.29/0.79) x 0.022 = 5.4 pp (paper: 0.554 in 2011Q1 -> 9.187 in 2015Q4, log ratio x 0.021 = 5.6 pp)
- Mean competing Airbnb listings: 0.79 in 2011Q4 -> 33.67 in 2019Q2; implied effect log(33.67/0.79) x 0.022 = 8.3 pp (paper: 0.554 in 2011Q1 -> 9.187 in 2015Q4, log ratio x 0.021 = 5.6 pp)
- Mean TripAdvisor rating: low-end 3.23, high-end 4.13 (paper: 3.0 / 4.0)
- Figures saved: figA1_TX.png, figA2_TX.png

## EU panel

- Hotels with at least one competing Airbnb listing at some point: 100.0% (paper: 48%)
- Figure 1 groups (Period 1 = through 2016Q4, Period 2 after): A (Airbnb in both) = 937, B (only in Period 2) = 2, C (never) = 0
- Mean competing Airbnb listings: 362.15 in 2015Q3 -> 665.43 in 2017Q3; implied effect log(665.43/362.15) x -0.155 = -9.4 pp (paper: 0.554 in 2011Q1 -> 9.187 in 2015Q4, log ratio x 0.021 = 5.6 pp)
- Mean TripAdvisor rating: low-end 2.77, high-end 4.30 (paper: 3.0 / 4.0)
- Mean Booking.com score (0-10): low-end 6.98, high-end 8.36 (paper Expedia: 3.1 / 4.1 on 5-point scale)
- Figures saved: figA1_EU.png, figA2_EU.png

## Appendix D (EU): trip-type shares by quarter (Booking.com tags)

| q      |   leisure |   business |   couple |   solo |   family |   group/friends |
|:-------|----------:|-----------:|---------:|-------:|---------:|----------------:|
| 2015Q3 |     0.846 |      0.126 |    0.492 |  0.186 |    0.214 |           0.111 |
| 2015Q4 |     0.772 |      0.201 |    0.514 |  0.241 |    0.125 |           0.124 |
| 2016Q1 |     0.789 |      0.184 |    0.536 |  0.223 |    0.13  |           0.114 |
| 2016Q2 |     0.809 |      0.164 |    0.516 |  0.212 |    0.144 |           0.128 |
| 2016Q3 |     0.855 |      0.116 |    0.483 |  0.183 |    0.217 |           0.116 |
| 2016Q4 |     0.793 |      0.178 |    0.49  |  0.217 |    0.172 |           0.121 |
| 2017Q1 |     0.787 |      0.179 |    0.455 |  0.246 |    0.177 |           0.12  |
| 2017Q2 |     0.813 |      0.156 |    0.452 |  0.193 |    0.193 |           0.157 |
| 2017Q3 |     0.843 |      0.127 |    0.452 |  0.176 |    0.203 |           0.161 |

- Friedman test (non-parametric repeated-measures ANOVA) that shares change across quarters: chi2=0.53, p=1.000 (paper: p close to 1)
- KPSS p-values (H0: stationary): leisure 0.10, business 0.10, couple 0.07, solo 0.10, family 0.10, group/friends 0.08  (paper: all stationary)

## Appendix G: Airbnb listing ratings (Inside Airbnb review_scores_rating)

- TX: 16,623 rated listings; share >= 4.5: 92.2%; share < 3.5: 1.6%; mean 4.80, sd 0.41
- EU: 187,249 rated listings; share >= 4.5: 84.5%; share < 3.5: 1.8%; mean 4.71, sd 0.43