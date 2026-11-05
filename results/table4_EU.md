# Table 4 (EU): Mutual demotion, hotel-pair level

Pairs: 8,648; pair-quarters: 61,220

## Table 4. Mutual Demotion Behavior with 2SLS

|                            | Model 1        | Model 2        |
|:---------------------------|:---------------|:---------------|
| log(Airbnb)                | 9.049 (18.670) | 9.635 (20.408) |
| log(CompetingHotels)       | 0.238 (0.479)  | 0.226 (0.456)  |
| Log(ReviewCount)           |                | -0.103 (0.234) |
| ReviewRatios               | NO             | YES            |
| Observations               | 61,220         | 61,220         |
| First-stage F (log Airbnb) | 0.3            | 0.2            |

*p<0.05, **p<0.01, ***p<0.001; SEs clustered by hotel pair. Pair FE, quarter FE, city x season FE.

## Table 4 — OLS two-way FE (reference)

|                      | Model 1       | Model 2        |
|:---------------------|:--------------|:---------------|
| log(Airbnb)          | 0.030 (0.023) | 0.025 (0.023)  |
| log(CompetingHotels) | 0.004 (0.018) | 0.008 (0.018)  |
| Log(ReviewCount)     |               | 0.008* (0.003) |
| ReviewRatios         | NO            | YES            |
| Observations         | 61,220        | 61,220         |

*p<0.05, **p<0.01, ***p<0.001; SEs clustered by hotel pair.
