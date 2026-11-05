# tx: replication tables

## Table 1. Summary statistics at the hotel-quarter level

|                                                  |   Mean |    SD |   Min |   Max |
|:-------------------------------------------------|-------:|------:|------:|------:|
| Number of TripAdvisor reviews per quarter        |  12.39 | 19.55 |     1 |   418 |
| Number of TripAdvisor 1-star reviews per quarter |   0.89 |  1.76 |     0 |    31 |
| Number of TripAdvisor 2-star reviews per quarter |   0.84 |  1.6  |     0 |    24 |
| Number of TripAdvisor 3-star reviews per quarter |   1.49 |  2.34 |     0 |    34 |
| Number of TripAdvisor 4-star reviews per quarter |   3.02 |  4.63 |     0 |    79 |
| Number of TripAdvisor 5-star reviews per quarter |   6.15 | 13.2  |     0 |   318 |
| Number of competing Airbnb listings per quarter  |  11.84 | 33.89 |     0 |   282 |
| Number of competing hotels per quarter           |   3.27 |  3.42 |     0 |    22 |

Total hotels: 448 | hotel-quarter observations: 10,068 | low-end hotels: 115


## Table 2. Self-Promotion with 2SLS

|                                    | Model 1         | Model 2          | Model 3          |
|:-----------------------------------|:----------------|:-----------------|:-----------------|
| log(Airbnb)                        | 0.022 (0.017)   | 0.018 (0.016)    | 0.022 (0.015)    |
| log(CompetingHotels)               | 0.013 (0.024)   | 0.009 (0.023)    | 0.001 (0.024)    |
| Log(ReviewCount)                   |                 | 0.028*** (0.005) | 0.028*** (0.005) |
| log(Airbnb) x Low-end              |                 |                  | -0.023 (0.023)   |
| ReviewRatios                       | NO              | YES              | YES              |
| Hotel FE / Time FE / City x Season | YES / YES / YES | YES / YES / YES  | YES / YES / YES  |
| Observations                       | 10,068          | 10,068           | 10,068           |
| First-stage F (log Airbnb)         | 86.3            | 86.6             | 89.5             |

*p<0.05, **p<0.01, ***p<0.001; robust SEs clustered at the hotel level in parentheses.


## Table 2. Self-Promotion — OLS two-way FE (reference)

|                                    | Model 1         | Model 2          | Model 3          |
|:-----------------------------------|:----------------|:-----------------|:-----------------|
| log(Airbnb)                        | 0.007 (0.007)   | 0.007 (0.006)    | 0.010 (0.006)    |
| log(CompetingHotels)               | 0.021 (0.023)   | 0.015 (0.022)    | 0.009 (0.023)    |
| Log(ReviewCount)                   |                 | 0.028*** (0.005) | 0.028*** (0.005) |
| log(Airbnb) x Low-end              |                 |                  | -0.015 (0.012)   |
| ReviewRatios                       | NO              | YES              | YES              |
| Hotel FE / Time FE / City x Season | YES / YES / YES | YES / YES / YES  | YES / YES / YES  |
| Observations                       | 10,068          | 10,068           | 10,068           |

*p<0.05, **p<0.01, ***p<0.001; robust SEs clustered at the hotel level in parentheses.


## Table 3. Demotion Behavior (DemotingOthers) with 2SLS

|                                    | Model 1         | Model 2         | Model 3         |
|:-----------------------------------|:----------------|:----------------|:----------------|
| log(Airbnb)                        | -0.128 (0.090)  | -0.130 (0.091)  | -0.128 (0.090)  |
| log(CompetingHotels)               | -0.157 (0.099)  | -0.156 (0.099)  | -0.160 (0.103)  |
| Log(ReviewCount)                   |                 | 0.010 (0.023)   | 0.009 (0.023)   |
| log(Airbnb) x Low-end              |                 |                 | -0.013 (0.067)  |
| ReviewRatios                       | NO              | YES             | YES             |
| Hotel FE / Time FE / City x Season | YES / YES / YES | YES / YES / YES | YES / YES / YES |
| Observations                       | 7,487           | 7,487           | 7,487           |
| First-stage F (log Airbnb)         | 70.3            | 70.6            | 70.7            |

*p<0.05, **p<0.01, ***p<0.001; robust SEs clustered at the hotel level in parentheses.


## Table 3. Demotion Behavior (DemotingOthers) — OLS two-way FE (reference)

|                                    | Model 1          | Model 2          | Model 3         |
|:-----------------------------------|:-----------------|:-----------------|:----------------|
| log(Airbnb)                        | 0.024 (0.034)    | 0.025 (0.034)    | 0.023 (0.036)   |
| log(CompetingHotels)               | -0.260** (0.097) | -0.261** (0.097) | -0.257* (0.101) |
| Log(ReviewCount)                   |                  | 0.015 (0.022)    | 0.015 (0.022)   |
| log(Airbnb) x Low-end              |                  |                  | 0.015 (0.075)   |
| ReviewRatios                       | NO               | YES              | YES             |
| Hotel FE / Time FE / City x Season | YES / YES / YES  | YES / YES / YES  | YES / YES / YES |
| Observations                       | 7,487            | 7,487            | 7,487           |

*p<0.05, **p<0.01, ***p<0.001; robust SEs clustered at the hotel level in parentheses.


## Table 8. Being Demoted with 2SLS

|                                    | Model 1         | Model 2         | Model 3         |
|:-----------------------------------|:----------------|:----------------|:----------------|
| log(Airbnb)                        | 0.022 (0.013)   | 0.021 (0.012)   | 0.017 (0.012)   |
| log(CompetingHotels)               | -0.005 (0.018)  | -0.003 (0.018)  | 0.006 (0.018)   |
| Log(ReviewCount)                   |                 | 0.001 (0.004)   | 0.001 (0.004)   |
| log(Airbnb) x Low-end              |                 |                 | 0.027 (0.020)   |
| ReviewRatios                       | NO              | YES             | YES             |
| Hotel FE / Time FE / City x Season | YES / YES / YES | YES / YES / YES | YES / YES / YES |
| Observations                       | 10,068          | 10,068          | 10,068          |
| First-stage F (log Airbnb)         | 86.3            | 86.6            | 89.5            |

*p<0.05, **p<0.01, ***p<0.001; robust SEs clustered at the hotel level in parentheses.


## Table 8. Being Demoted — OLS two-way FE (reference)

|                                    | Model 1         | Model 2         | Model 3         |
|:-----------------------------------|:----------------|:----------------|:----------------|
| log(Airbnb)                        | 0.007 (0.005)   | 0.008 (0.005)   | 0.005 (0.005)   |
| log(CompetingHotels)               | 0.003 (0.017)   | 0.004 (0.016)   | 0.009 (0.016)   |
| Log(ReviewCount)                   |                 | 0.001 (0.003)   | 0.001 (0.003)   |
| log(Airbnb) x Low-end              |                 |                 | 0.014 (0.011)   |
| ReviewRatios                       | NO              | YES             | YES             |
| Hotel FE / Time FE / City x Season | YES / YES / YES | YES / YES / YES | YES / YES / YES |
| Observations                       | 10,068          | 10,068          | 10,068          |

*p<0.05, **p<0.01, ***p<0.001; robust SEs clustered at the hotel level in parentheses.


## Table 5. IV validity: direct correlation between instrument and manipulation

|                      | w/o Airbnb ever: Promote   | w/o Airbnb ever: Demote   | w/ Airbnb: Promote   | w/ Airbnb: Demote   |
|:---------------------|:---------------------------|:--------------------------|:---------------------|:--------------------|
| log(Cmp_Airbnb)      | -0.021 (0.023)             | 0.286 (0.168)             | 0.005 (0.007)        | -0.097* (0.045)     |
| log(CompetingHotels) | -0.058 (0.067)             | 0.017 (0.183)             | 0.025 (0.023)        | -0.148 (0.094)      |
| Log(ReviewCount)     | 0.030* (0.013)             | -0.016 (0.041)            | 0.028*** (0.005)     | 0.017 (0.025)       |
| Observations         | 2,242                      | 1,454                     | 7,826                | 6,033               |

*p<0.05, **p<0.01, ***p<0.001; robust SEs clustered at the hotel level in parentheses. ReviewRatios, hotel FE, time FE and city x season FE included.
