# Appendices B, C, F, H (Texas)

## Table B1. Relative-time model

Hotels ever treated (Airbnb within 1 km): 351; never treated: 98. Treatment quarter = first quarter with a lagged competing listing. Dummies at exactly j = -2..+3 quarters from treatment (Autor 2003), OLS, hotel + quarter + city x season FE, SEs clustered by hotel.

|                         | Self-promotion M1   | Self-promotion M2   | Demoting others M1   | Demoting others M2   |
|:------------------------|:--------------------|:--------------------|:---------------------|:---------------------|
| Airbnb_Binary treat(-2) | -0.007 (0.017)      | -0.005 (0.017)      | 0.060 (0.095)        | 0.058 (0.096)        |
| Airbnb_Binary treat(-1) | 0.007 (0.018)       | 0.011 (0.018)       | 0.039 (0.042)        | 0.037 (0.041)        |
| Airbnb_Binary treat(0)  | 0.009 (0.016)       | 0.011 (0.016)       | 0.026 (0.034)        | 0.026 (0.034)        |
| Airbnb_Binary treat(+1) | 0.040* (0.016)      | 0.039* (0.016)      | -0.002 (0.042)       | -0.003 (0.042)       |
| Airbnb_Binary treat(+2) | 0.007 (0.015)       | 0.004 (0.015)       | 0.012 (0.044)        | 0.015 (0.045)        |
| Airbnb_Binary treat(+3) | 0.004 (0.015)       | 0.003 (0.015)       | 0.097 (0.092)        | 0.097 (0.091)        |
| log_comphotels          | 0.026 (0.023)       | 0.020 (0.022)       | -0.239** (0.084)     | -0.240** (0.085)     |
| log_reviews_lag         |                     | 0.027*** (0.005)    |                      | 0.013 (0.022)        |
| ReviewRatios            | NO                  | YES                 | NO                   | YES                  |
| Observations            | 10,068              | 10,068              | 7,487                | 7,487                |

## Table F1. Alternative operationalisation (same thresholds for all hotels)


## Table F1

|                            | Self-promotion Model 1   | Self-promotion Model 2   | Self-promotion Model 3   | Demoting others Model 1   | Demoting others Model 2   | Demoting others Model 3   |
|:---------------------------|:-------------------------|:-------------------------|:-------------------------|:--------------------------|:--------------------------|:--------------------------|
| log(Airbnb)                | 0.024 (0.016)            | 0.020 (0.015)            | 0.019 (0.015)            | -0.161 (0.097)            | -0.165 (0.098)            | -0.162 (0.097)            |
| log(CompetingHotels)       | 0.008 (0.024)            | 0.004 (0.023)            | 0.006 (0.023)            | -0.162 (0.102)            | -0.159 (0.102)            | -0.164 (0.106)            |
| Log(ReviewCount)           |                          | 0.026*** (0.005)         | 0.026*** (0.005)         |                           | 0.006 (0.025)             | 0.005 (0.025)             |
| log(Airbnb) x Low-end      |                          |                          | 0.005 (0.019)            |                           |                           | -0.015 (0.076)            |
| ReviewRatios               | NO                       | YES                      | YES                      | NO                        | YES                       | YES                       |
| Observations               | 10,068                   | 10,068                   | 10,068                   | 7,487                     | 7,487                     | 7,487                     |
| First-stage F (log Airbnb) | 86.3                     | 86.6                     | 89.5                     | 70.3                      | 70.6                      | 70.7                      |

*p<0.05, **p<0.01, ***p<0.001; robust SEs clustered in parentheses.

## Table H1. All neighbouring hotels as competitors (regardless of tier)


## Table H1

|                            | Self-promotion Model 1   | Self-promotion Model 2   | Self-promotion Model 3   | Demoting others Model 1   | Demoting others Model 2   | Demoting others Model 3   |
|:---------------------------|:-------------------------|:-------------------------|:-------------------------|:--------------------------|:--------------------------|:--------------------------|
| log(Airbnb)                | 0.011 (0.016)            | 0.010 (0.014)            | 0.014 (0.014)            | -0.076 (0.054)            | -0.076 (0.053)            | -0.076 (0.055)            |
| log(CompetingHotels)       | 0.009 (0.027)            | 0.003 (0.026)            | -0.001 (0.026)           | -0.207** (0.075)          | -0.208** (0.076)          | -0.208** (0.077)          |
| Log(ReviewCount)           |                          | 0.028*** (0.005)         | 0.028*** (0.005)         |                           | 0.006 (0.014)             | 0.006 (0.014)             |
| log(Airbnb) x Low-end      |                          |                          | -0.019 (0.018)           |                           |                           | 0.001 (0.040)             |
| ReviewRatios               | NO                       | YES                      | YES                      | NO                        | YES                       | YES                       |
| Observations               | 10,068                   | 10,068                   | 10,068                   | 8,271                     | 8,271                     | 8,271                     |
| First-stage F (log Airbnb) | 106.9                    | 107.2                    | 107.0                    | 92.1                      | 92.5                      | 91.9                      |

*p<0.05, **p<0.01, ***p<0.001; robust SEs clustered in parentheses.

## Table C1. Mutual demotion within hotel triplets

Triplets: 2,403; triplet-quarters: 25,087; low-end triplets: 136


## Table C1 (2SLS, triplet FE + quarter FE + city x season, SEs clustered by triplet)

|                            | Model 1           | Model 2           | Model 3          |
|:---------------------------|:------------------|:------------------|:-----------------|
| log(Airbnb)                | -0.423*** (0.108) | -0.386*** (0.101) | -0.347** (0.108) |
| log(CompetingHotels)       | 0.246*** (0.074)  | 0.164* (0.071)    | 0.136 (0.073)    |
| Log(ReviewCount)           |                   | 0.178*** (0.021)  | 0.177*** (0.020) |
| log(Airbnb) x Low-end      |                   |                   | -0.127** (0.043) |
| ReviewRatios               | NO                | YES               | YES              |
| Observations               | 25,087            | 25,087            | 25,087           |
| First-stage F (log Airbnb) | 127.6             | 126.8             | 194.8            |

*p<0.05, **p<0.01, ***p<0.001; robust SEs clustered in parentheses.
