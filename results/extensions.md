# Extensions and appendix analyses


## Table I1 (TX) and extension: 2SLS by sub-period (paper's inflection point 2011Q4; added break at 2015Q4, the paper's end of sample)

|                            | Self-promotion: <=2011Q4   | Self-promotion: 2012Q1-2015Q4   | Self-promotion: >=2016Q1   | Demoting others: <=2011Q4   | Demoting others: 2012Q1-2015Q4   | Demoting others: >=2016Q1   |
|:---------------------------|:---------------------------|:--------------------------------|:---------------------------|:----------------------------|:---------------------------------|:----------------------------|
| log(Airbnb)                | -0.061 (0.079)             | 0.107* (0.045)                  | 0.040 (0.114)              | 0.042 (0.055)               | 0.002 (0.280)                    | -0.418 (0.582)              |
| log(CompetingHotels)       | 0.245 (0.152)              | 0.006 (0.054)                   | -0.034 (0.039)             | 0.125 (0.066)               | -0.184 (0.341)                   | 0.177 (0.109)               |
| Log(ReviewCount)           | -0.004 (0.024)             | 0.020** (0.007)                 | 0.028*** (0.008)           | 0.008 (0.015)               | 0.003 (0.030)                    | 0.001 (0.025)               |
| ReviewRatios               | YES                        | YES                             | YES                        | YES                         | YES                              | YES                         |
| Observations               | 809                        | 4,480                           | 4,779                      | 572                         | 3,253                            | 3,662                       |
| First-stage F (log Airbnb) | 43.3                       | 19.7                            | 10.1                       | 32.1                        | 11.7                             | 12.9                        |

*p<0.05, **p<0.01, ***p<0.001; SEs clustered by hotel. Hotel FE, quarter FE, city x season FE; Model 2 controls (lagged review count and ratios).


## Appendix G (TX): Airbnb price per person — 24th percentile cutoff = $34 (paper: $25); 91% of listings have a price


## Table G1 (TX): same-segment Airbnb competitors (low-end hotels vs low-price listings, high-end vs the rest), 2SLS

|                            | Self-promotion: Model 1   | Self-promotion: Model 2   | Self-promotion: Model 3   | Demoting others: Model 1   | Demoting others: Model 2   | Demoting others: Model 3   |
|:---------------------------|:--------------------------|:--------------------------|:--------------------------|:---------------------------|:---------------------------|:---------------------------|
| log(Airbnb)                | 0.026 (0.016)             | 0.021 (0.014)             | 0.022 (0.014)             | -0.126 (0.079)             | -0.128 (0.080)             | -0.118 (0.078)             |
| log(CompetingHotels)       | 0.012 (0.024)             | 0.008 (0.023)             | 0.006 (0.023)             | -0.166 (0.101)             | -0.166 (0.102)             | -0.200 (0.105)             |
| Log(ReviewCount)           |                           | 0.028*** (0.005)          | 0.028*** (0.005)          |                            | 0.011 (0.023)              | 0.008 (0.023)              |
| log(Airbnb) x Low-end      |                           |                           | -0.008 (0.036)            |                            |                            | -0.167 (0.100)             |
| ReviewRatios               | NO                        | YES                       | YES                       | NO                         | YES                        | YES                        |
| Observations               | 10,068                    | 10,068                    | 10,068                    | 7,487                      | 7,487                      | 7,487                      |
| First-stage F (log Airbnb) | 96.9                      | 97.4                      | 98.0                      | 70.7                       | 70.6                       | 71.1                       |

*p<0.05, **p<0.01, ***p<0.001; SEs clustered by hotel. Hotel FE, quarter FE, city x season FE; Models as in Table 2 (lagged review count and ratios).


## Extension (EU): one-time-reviewer excess, TripAdvisor minus verified Booking.com, same hotel-quarter

- Share of reviews by one-time reviewers: TripAdvisor 46.9% (5-star or 1-2-star only); Booking.com 27.1% (all scores)
- Mean excess (top): 0.242; (bottom): 0.055; correlation with Mayzlin-style selfpromo: 0.69

## Extension table (EU): one-time-reviewer excess on Airbnb supply

|                            | Excess one-time 5-star (promotion): 2SLS   | Excess one-time 5-star (promotion): OLS-FE   | Excess one-time 1-2-star (demotion): 2SLS   | Excess one-time 1-2-star (demotion): OLS-FE   |
|:---------------------------|:-------------------------------------------|:---------------------------------------------|:--------------------------------------------|:----------------------------------------------|
| log(Airbnb)                | -0.102 (0.062)                             | -0.027 (0.016)                               | 0.018 (0.040)                               | 0.001 (0.015)                                 |
| log(CompetingHotels)       | -0.032 (0.050)                             | -0.042 (0.043)                               | 0.011 (0.026)                               | 0.013 (0.024)                                 |
| Log(ReviewCount)           | 0.004 (0.005)                              | 0.003 (0.005)                                | -0.002 (0.003)                              | -0.002 (0.004)                                |
| ReviewRatios               | YES                                        | YES                                          | YES                                         | YES                                           |
| Observations               | 7,118                                      | 7,118                                        | 7,118                                       | 7,118                                         |
| First-stage F (log Airbnb) | 2.9                                        |                                              | 2.9                                         |                                               |

*p<0.05, **p<0.01, ***p<0.001; SEs clustered by hotel. Hotel FE, quarter FE, city x season FE; Model 2 controls (lagged review count and ratios).
