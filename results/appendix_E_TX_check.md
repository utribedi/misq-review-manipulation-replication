# Appendix E (Texas), Python check


## Table E1, Gaussian kernel, bandwidth 1.0 km

|                            | Promote Model 1   | Promote Model 2   | Promote Model 3   | Demote Model 1   | Demote Model 2   | Demote Model 3   |
|:---------------------------|:------------------|:------------------|:------------------|:-----------------|:-----------------|:-----------------|
| log(Airbnb)                | 0.015 (0.010)     | 0.013 (0.009)     | 0.017 (0.009)     | 0.051 (0.095)    | 0.050 (0.096)    | -0.028 (0.065)   |
| log(CompetingHotels)       | -0.005 (0.032)    | -0.010 (0.030)    | -0.020 (0.031)    | -0.798* (0.380)  | -0.797* (0.379)  | -0.563* (0.249)  |
| Log(ReviewCount)           |                   | 0.028*** (0.005)  | 0.027*** (0.005)  |                  | 0.080 (0.081)    | 0.089 (0.080)    |
| log(Airbnb) x Low-end      |                   |                   | -0.016 (0.011)    |                  |                  | 0.406 (0.307)    |
| ReviewRatios               | NO                | YES               | YES               | NO               | YES              | YES              |
| Observations               | 10,068            | 10,068            | 10,068            | 9,100            | 9,100            | 9,100            |
| First-stage F (log Airbnb) | 593.7             | 595.9             | 636.3             | 552.0            | 553.0            | 595.2            |

*p<0.05, **p<0.01, ***p<0.001; robust SEs clustered in parentheses.


## Table E1, Gaussian kernel, bandwidth 0.5 km

|                            | Promote Model 1   | Promote Model 2   | Promote Model 3   | Demote Model 1   | Demote Model 2   | Demote Model 3   |
|:---------------------------|:------------------|:------------------|:------------------|:-----------------|:-----------------|:-----------------|
| log(Airbnb)                | 0.013 (0.011)     | 0.012 (0.010)     | 0.015 (0.010)     | -0.264 (0.193)   | -0.266 (0.193)   | -0.229 (0.193)   |
| log(CompetingHotels)       | 0.012 (0.029)     | 0.005 (0.027)     | -0.001 (0.028)    | -0.587* (0.238)  | -0.603* (0.239)  | -0.698** (0.264) |
| Log(ReviewCount)           |                   | 0.028*** (0.005)  | 0.028*** (0.005)  |                  | 0.009 (0.067)    | 0.004 (0.067)    |
| log(Airbnb) x Low-end      |                   |                   | -0.017 (0.020)    |                  |                  | -0.320 (0.196)   |
| ReviewRatios               | NO                | YES               | YES               | NO               | YES              | YES              |
| Observations               | 10,068            | 10,068            | 10,068            | 8,151            | 8,151            | 8,151            |
| First-stage F (log Airbnb) | 237.9             | 239.8             | 430.9             | 429.8            | 429.2            | 459.3            |

*p<0.05, **p<0.01, ***p<0.001; robust SEs clustered in parentheses.
