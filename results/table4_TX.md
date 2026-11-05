# Table 4 (TX): Mutual demotion, hotel-pair level

Pairs: 991; pair-quarters: 15,531

## Table 4. Mutual Demotion Behavior with 2SLS

|                            | Model 1         | Model 2          | Model 3          |
|:---------------------------|:----------------|:-----------------|:-----------------|
| log(Airbnb)                | -0.191* (0.079) | -0.177* (0.072)  | -0.164* (0.072)  |
| log(CompetingHotels)       | -0.077 (0.057)  | -0.100 (0.054)   | -0.112* (0.057)  |
| Log(ReviewCount)           |                 | 0.179*** (0.028) | 0.178*** (0.028) |
| log(Airbnb) x Low-end      |                 |                  | -0.072 (0.052)   |
| ReviewRatios               | NO              | YES              | YES              |
| Observations               | 15,531          | 15,531           | 15,531           |
| First-stage F (log Airbnb) | 106.6           | 105.9            | 114.9            |

*p<0.05, **p<0.01, ***p<0.001; SEs clustered by hotel pair. Pair FE, quarter FE, city x season FE.

## Table 4 — OLS two-way FE (reference)

|                       | Model 1         | Model 2          | Model 3          |
|:----------------------|:----------------|:-----------------|:-----------------|
| log(Airbnb)           | -0.033 (0.042)  | -0.020 (0.040)   | -0.023 (0.041)   |
| log(CompetingHotels)  | -0.170* (0.068) | -0.193** (0.066) | -0.190** (0.067) |
| Log(ReviewCount)      |                 | 0.186*** (0.029) | 0.186*** (0.029) |
| log(Airbnb) x Low-end |                 |                  | 0.033 (0.063)    |
| ReviewRatios          | NO              | YES              | YES              |
| Observations          | 15,531          | 15,531           | 15,531           |

*p<0.05, **p<0.01, ***p<0.001; SEs clustered by hotel pair.
