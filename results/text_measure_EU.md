# Text-based manipulation measure (EU)

- Reviews scored: 1,632,385; share flagged deceptive (p>0.5): 9.3%; among 5-star 13.9%; among 1-2-star 11.5%
- Hotel-quarter correlation of share_fake5 with the panel's self-promotion measure: 0.27; with one-time 5-star share: 0.41

## Share of reviews that are 5-star and flagged deceptive on Airbnb supply (EU)

|                            | Model 1 2SLS   | Model 1 OLS    | Model 2 2SLS   | Model 2 OLS    |
|:---------------------------|:---------------|:---------------|:---------------|:---------------|
| log(Airbnb)                | -0.054 (0.046) | -0.004 (0.006) | -0.053 (0.045) | -0.003 (0.006) |
| log(CompetingHotels)       | 0.001 (0.017)  | -0.005 (0.015) | 0.002 (0.017)  | -0.004 (0.015) |
| Log(ReviewCount)           |                |                | -0.003 (0.002) | -0.004 (0.002) |
| ReviewRatios               | NO             | NO             | YES            | YES            |
| Observations               | 7,246          | 7,246          | 7,246          | 7,246          |
| First-stage F (log Airbnb) | 2.9            |                | 2.9            |                |

*p<0.05, **p<0.01, ***p<0.001; SEs clustered by hotel. Hotel FE, quarter FE, city x season FE.


## Share of reviews that are 1-2-star and flagged deceptive on Airbnb supply (EU)

|                            | Model 1 2SLS   | Model 1 OLS   | Model 2 2SLS   | Model 2 OLS    |
|:---------------------------|:---------------|:--------------|:---------------|:---------------|
| log(Airbnb)                | 0.015 (0.017)  | 0.003 (0.005) | 0.015 (0.017)  | 0.003 (0.005)  |
| log(CompetingHotels)       | 0.016 (0.013)  | 0.018 (0.013) | 0.016 (0.013)  | 0.018 (0.013)  |
| Log(ReviewCount)           |                |               | -0.000 (0.001) | -0.000 (0.001) |
| ReviewRatios               | NO             | NO            | YES            | YES            |
| Observations               | 7,246          | 7,246         | 7,246          | 7,246          |
| First-stage F (log Airbnb) | 2.9            |               | 2.9            |                |

*p<0.05, **p<0.01, ***p<0.001; SEs clustered by hotel. Hotel FE, quarter FE, city x season FE.


## Mean deceptive probability on Airbnb supply (EU)

|                            | Model 1 2SLS   | Model 1 OLS   | Model 2 2SLS   | Model 2 OLS   |
|:---------------------------|:---------------|:--------------|:---------------|:--------------|
| log(Airbnb)                | -0.019 (0.023) | 0.001 (0.004) | -0.021 (0.024) | 0.001 (0.004) |
| log(CompetingHotels)       | 0.015 (0.012)  | 0.012 (0.011) | 0.015 (0.012)  | 0.012 (0.011) |
| Log(ReviewCount)           |                |               | 0.001 (0.001)  | 0.001 (0.001) |
| ReviewRatios               | NO             | NO            | YES            | YES           |
| Observations               | 7,246          | 7,246         | 7,246          | 7,246         |
| First-stage F (log Airbnb) | 2.9            |               | 2.9            |               |

*p<0.05, **p<0.01, ***p<0.001; SEs clustered by hotel. Hotel FE, quarter FE, city x season FE.
