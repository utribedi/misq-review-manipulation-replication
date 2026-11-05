# Text-based manipulation measure (TX)

- Reviews scored: 906,644; share flagged deceptive (p>0.5): 21.8%; among 5-star 28.2%; among 1-2-star 23.0%
- Hotel-quarter correlation of share_fake5 with the panel's self-promotion measure: 0.46; with one-time 5-star share: 0.46

## Share of reviews that are 5-star and flagged deceptive on Airbnb supply (TX)

|                            | Model 1 2SLS   | Model 1 OLS    | Model 2 2SLS     | Model 2 OLS      | Model 3 2SLS     | Model 3 OLS      |
|:---------------------------|:---------------|:---------------|:-----------------|:-----------------|:-----------------|:-----------------|
| log(Airbnb)                | 0.023* (0.010) | 0.006 (0.004)  | 0.022* (0.010)   | 0.006 (0.004)    | 0.022* (0.010)   | 0.006 (0.004)    |
| log(CompetingHotels)       | 0.017 (0.013)  | 0.026* (0.013) | 0.015 (0.013)    | 0.024 (0.013)    | 0.014 (0.013)    | 0.024 (0.013)    |
| Log(ReviewCount)           |                |                | 0.012*** (0.003) | 0.011*** (0.003) | 0.012*** (0.003) | 0.011*** (0.003) |
| log(Airbnb) x Low-end      |                |                |                  |                  | -0.003 (0.008)   | 0.001 (0.006)    |
| ReviewRatios               | NO             | NO             | YES              | YES              | YES              | YES              |
| Observations               | 10,068         | 10,068         | 10,068           | 10,068           | 10,068           | 10,068           |
| First-stage F (log Airbnb) | 86.3           |                | 86.6             |                  | 89.5             |                  |

*p<0.05, **p<0.01, ***p<0.001; SEs clustered by hotel. Hotel FE, quarter FE, city x season FE.


## Share of reviews that are 1-2-star and flagged deceptive on Airbnb supply (TX)

|                            | Model 1 2SLS   | Model 1 OLS    | Model 2 2SLS   | Model 2 OLS    | Model 3 2SLS   | Model 3 OLS    |
|:---------------------------|:---------------|:---------------|:---------------|:---------------|:---------------|:---------------|
| log(Airbnb)                | -0.007 (0.007) | -0.000 (0.003) | -0.007 (0.007) | -0.000 (0.003) | -0.006 (0.006) | -0.001 (0.003) |
| log(CompetingHotels)       | 0.007 (0.013)  | 0.004 (0.011)  | 0.008 (0.012)  | 0.004 (0.011)  | 0.005 (0.012)  | 0.006 (0.011)  |
| Log(ReviewCount)           |                |                | 0.002 (0.002)  | 0.002 (0.002)  | 0.002 (0.002)  | 0.002 (0.002)  |
| log(Airbnb) x Low-end      |                |                |                |                | -0.007 (0.009) | 0.005 (0.007)  |
| ReviewRatios               | NO             | NO             | YES            | YES            | YES            | YES            |
| Observations               | 10,068         | 10,068         | 10,068         | 10,068         | 10,068         | 10,068         |
| First-stage F (log Airbnb) | 86.3           |                | 86.6           |                | 89.5           |                |

*p<0.05, **p<0.01, ***p<0.001; SEs clustered by hotel. Hotel FE, quarter FE, city x season FE.


## Mean deceptive probability on Airbnb supply (TX)

|                            | Model 1 2SLS   | Model 1 OLS    | Model 2 2SLS     | Model 2 OLS      | Model 3 2SLS     | Model 3 OLS      |
|:---------------------------|:---------------|:---------------|:-----------------|:-----------------|:-----------------|:-----------------|
| log(Airbnb)                | 0.007 (0.005)  | 0.001 (0.002)  | 0.006 (0.005)    | 0.001 (0.002)    | 0.006 (0.005)    | 0.001 (0.002)    |
| log(CompetingHotels)       | 0.015 (0.008)  | 0.019* (0.007) | 0.014 (0.007)    | 0.017* (0.007)   | 0.014 (0.008)    | 0.016* (0.007)   |
| Log(ReviewCount)           |                |                | 0.011*** (0.002) | 0.011*** (0.002) | 0.011*** (0.002) | 0.011*** (0.002) |
| log(Airbnb) x Low-end      |                |                |                  |                  | 0.002 (0.006)    | -0.001 (0.004)   |
| ReviewRatios               | NO             | NO             | YES              | YES              | YES              | YES              |
| Observations               | 10,068         | 10,068         | 10,068           | 10,068           | 10,068           | 10,068           |
| First-stage F (log Airbnb) | 86.3           |                | 86.6             |                  | 89.5             |                  |

*p<0.05, **p<0.01, ***p<0.001; SEs clustered by hotel. Hotel FE, quarter FE, city x season FE.
