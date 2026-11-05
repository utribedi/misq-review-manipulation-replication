# eu: replication tables

## Table 1. Summary statistics at the hotel-quarter level

|                                                  |   Mean |     SD |   Min |   Max |
|:-------------------------------------------------|-------:|-------:|------:|------:|
| Number of TripAdvisor reviews per quarter        |  32.82 |  44.08 |     1 |   310 |
| Number of TripAdvisor 1-star reviews per quarter |   0.9  |   2.22 |     0 |    41 |
| Number of TripAdvisor 2-star reviews per quarter |   1.2  |   2.68 |     0 |    54 |
| Number of TripAdvisor 3-star reviews per quarter |   3.21 |   5.63 |     0 |    83 |
| Number of TripAdvisor 4-star reviews per quarter |   9.31 |  13.15 |     0 |   122 |
| Number of TripAdvisor 5-star reviews per quarter |  18.2  |  27.51 |     0 |   203 |
| Number of Booking.com reviews per quarter        |  37.55 |  52.14 |     1 |   711 |
| Number of Booking.com 9-10 reviews per quarter   |  17.72 |  24.35 |     0 |   302 |
| Number of Booking.com 8-10 reviews per quarter   |  24.24 |  32.09 |     0 |   374 |
| Number of Booking.com <=5 reviews per quarter    |   2.31 |   6.64 |     0 |   186 |
| Number of Booking.com <=4 reviews per quarter    |   0.82 |   2.84 |     0 |    89 |
| Number of competing Airbnb listings per quarter  | 526.24 | 461.19 |     0 |  3050 |
| Number of competing hotels per quarter           |  17.8  |  13.58 |     0 |    59 |

Total hotels: 903 | hotel-quarter observations: 7,118 | low-end hotels: 2

_Model 3 (low-end interaction) omitted: fewer than 5 low-end hotels in this panel._


## Table 2. Self-Promotion with 2SLS

|                                    | Model 1         | Model 2         |
|:-----------------------------------|:----------------|:----------------|
| log(Airbnb)                        | -0.155 (0.089)  | -0.162 (0.092)  |
| log(CompetingHotels)               | 0.023 (0.052)   | 0.028 (0.054)   |
| Log(ReviewCount)                   |                 | -0.001 (0.006)  |
| ReviewRatios                       | NO              | YES             |
| Hotel FE / Time FE / City x Season | YES / YES / YES | YES / YES / YES |
| Observations                       | 7,118           | 7,118           |
| First-stage F (log Airbnb)         | 2.9             | 2.9             |

*p<0.05, **p<0.01, ***p<0.001; robust SEs clustered at the hotel level in parentheses.


## Table 2. Self-Promotion — OLS two-way FE (reference)

|                                    | Model 1         | Model 2         |
|:-----------------------------------|:----------------|:----------------|
| log(Airbnb)                        | -0.018 (0.014)  | -0.018 (0.015)  |
| log(CompetingHotels)               | 0.006 (0.044)   | 0.009 (0.045)   |
| Log(ReviewCount)                   |                 | -0.002 (0.006)  |
| ReviewRatios                       | NO              | YES             |
| Hotel FE / Time FE / City x Season | YES / YES / YES | YES / YES / YES |
| Observations                       | 7,118           | 7,118           |

*p<0.05, **p<0.01, ***p<0.001; robust SEs clustered at the hotel level in parentheses.


## Table 3. Demotion Behavior (DemotingOthers) with 2SLS

|                                    | Model 1         | Model 2         |
|:-----------------------------------|:----------------|:----------------|
| log(Airbnb)                        | -0.565 (0.501)  | -0.563 (0.502)  |
| log(CompetingHotels)               | 0.070 (0.165)   | 0.069 (0.165)   |
| Log(ReviewCount)                   |                 | 0.002 (0.008)   |
| ReviewRatios                       | NO              | YES             |
| Hotel FE / Time FE / City x Season | YES / YES / YES | YES / YES / YES |
| Observations                       | 6,600           | 6,600           |
| First-stage F (log Airbnb)         | 5.0             | 5.0             |

*p<0.05, **p<0.01, ***p<0.001; robust SEs clustered at the hotel level in parentheses.


## Table 3. Demotion Behavior (DemotingOthers) — OLS two-way FE (reference)

|                                    | Model 1         | Model 2         |
|:-----------------------------------|:----------------|:----------------|
| log(Airbnb)                        | 0.058 (0.048)   | 0.057 (0.049)   |
| log(CompetingHotels)               | -0.038 (0.132)  | -0.040 (0.133)  |
| Log(ReviewCount)                   |                 | -0.005 (0.007)  |
| ReviewRatios                       | NO              | YES             |
| Hotel FE / Time FE / City x Season | YES / YES / YES | YES / YES / YES |
| Observations                       | 6,600           | 6,600           |

*p<0.05, **p<0.01, ***p<0.001; robust SEs clustered at the hotel level in parentheses.


## Table 8. Being Demoted with 2SLS

|                                    | Model 1         | Model 2         |
|:-----------------------------------|:----------------|:----------------|
| log(Airbnb)                        | -0.004 (0.056)  | -0.002 (0.059)  |
| log(CompetingHotels)               | 0.011 (0.033)   | 0.011 (0.034)   |
| Log(ReviewCount)                   |                 | -0.004 (0.004)  |
| ReviewRatios                       | NO              | YES             |
| Hotel FE / Time FE / City x Season | YES / YES / YES | YES / YES / YES |
| Observations                       | 7,118           | 7,118           |
| First-stage F (log Airbnb)         | 2.9             | 2.9             |

*p<0.05, **p<0.01, ***p<0.001; robust SEs clustered at the hotel level in parentheses.


## Table 8. Being Demoted — OLS two-way FE (reference)

|                                    | Model 1         | Model 2         |
|:-----------------------------------|:----------------|:----------------|
| log(Airbnb)                        | 0.004 (0.015)   | 0.002 (0.016)   |
| log(CompetingHotels)               | 0.010 (0.031)   | 0.010 (0.032)   |
| Log(ReviewCount)                   |                 | -0.004 (0.004)  |
| ReviewRatios                       | NO              | YES             |
| Hotel FE / Time FE / City x Season | YES / YES / YES | YES / YES / YES |
| Observations                       | 7,118           | 7,118           |

*p<0.05, **p<0.01, ***p<0.001; robust SEs clustered at the hotel level in parentheses.


## Table 5. IV validity: direct correlation between instrument and manipulation

|                      | w/o Airbnb ever: Promote   | w/o Airbnb ever: Demote   | w/ Airbnb: Promote   | w/ Airbnb: Demote   |
|:---------------------|:---------------------------|:--------------------------|:---------------------|:--------------------|
| Observations         | n/a (only 0 hotels)        | n/a (only 0 hotels)       | 7,118                | 6,600               |
| log(Cmp_Airbnb)      |                            |                           | -0.027* (0.011)      | -0.176 (0.114)      |
| log(CompetingHotels) |                            |                           | 0.051 (0.052)        | 0.118 (0.123)       |
| Log(ReviewCount)     |                            |                           | -0.002 (0.006)       | -0.003 (0.007)      |

*p<0.05, **p<0.01, ***p<0.001; robust SEs clustered at the hotel level in parentheses. ReviewRatios, hotel FE, time FE and city x season FE included.
