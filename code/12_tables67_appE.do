*==============================================================================
* Table 6 (look-ahead PSM), Table 7 (synthetic control) and Appendix E (kernel competition) of
* Nie, Zheng & Sarkar (2022), Texas panel. Stata estimation.
* Inputs (built by code/12_appE_table6_inputs.py): data_extract/panel_tx_appE.csv, data_extract/hotels_tx_lapsm.csv, data_extract/panel_tx.csv
* Outputs: results/stata/tx_tableE1.txt, tx_table6.txt, tx_table6_balance.txt, tx_table7.txt
* Run from the project folder:  do "code/12_tables67_appE.do"
* Requires: reghdfe ivreghdfe ftools ivreg2 ranktest estout psmatch2 sdid
*==============================================================================
clear all
set more off
capture mkdir "results/stata"
set scheme s1mono
set seed 2022

local STAR  star(* 0.05 ** 0.01 *** 0.001)
local FMT   b(3) se(3) nonotes nogaps compress varwidth(30) modelwidth(16)
local IVST  stats(N widstat, fmt(%9.0fc %9.1f) labels("Observations" "Kleibergen-Paap F"))

program define prep_basic
    * ids, time, lagged review controls (no Airbnb variables assumed)
    encode hotel_id, gen(hid)
    gen qdate = quarterly(yq, "YQ")
    format qdate %tq
    capture drop season
    capture drop city_season
    gen season = quarter(dofq(qdate))
    encode city, gen(cityid)
    egen city_season = group(cityid season)
    xtset hid qdate
    foreach v in n_ta ta2 ta3 ta4 ta5 {
        capture drop `v'_lag
        gen `v'_lag = L.`v'
        replace `v'_lag = 0 if missing(`v'_lag)
    }
    forvalues s = 2/5 {
        capture drop ratio`s'_lag
        gen ratio`s'_lag = cond(n_ta_lag > 0, ta`s'_lag / n_ta_lag, 0)
    }
    capture drop log_reviews_lag
    gen log_reviews_lag = log(n_ta_lag + 1)
    label var log_reviews_lag "Log(ReviewCount)"
end

program define three_models
    args y pre haslow
    eststo `pre'_m1: ivreghdfe `y' log_comphotels (log_airbnb = log_iv), absorb(hid qdate city_season) cluster(hid)
    eststo `pre'_m2: ivreghdfe `y' log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag ///
        (log_airbnb = log_iv), absorb(hid qdate city_season) cluster(hid)
    if `haslow' {
        eststo `pre'_m3: ivreghdfe `y' log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag ///
            (log_airbnb log_airbnb_x_low = log_iv log_iv_x_low), absorb(hid qdate city_season) cluster(hid)
    }
end

*==============================================================================
* Appendix E: Gaussian-kernel competition intensity, bandwidths 1 km and 0.5 km (Table E1)
*==============================================================================
import delimited "data_extract/panel_tx_appE.csv", clear varnames(1) encoding(utf8)
prep_basic
eststo clear
foreach k in k1 k05 {
    capture drop log_airbnb log_comphotels log_iv log_airbnb_x_low log_iv_x_low demoting_others
    gen log_airbnb       = log_airbnb_`k'
    gen log_comphotels   = log_comphotels_`k'
    gen log_iv           = log_iv_`k'
    gen demoting_others  = demoting_others_`k'
    gen log_airbnb_x_low = log_airbnb * lowend
    gen log_iv_x_low     = log_iv * lowend
    label var log_airbnb        "log(Airbnb, kernel)"
    label var log_comphotels    "log(CompetingHotels, kernel)"
    label var log_airbnb_x_low  "log(Airbnb) x Low-end"
    three_models selfpromo       e`k'p 1
    three_models demoting_others e`k'd 1
}
esttab ek1p_* ek1d_* using "results/stata/tx_tableE1.txt", replace `FMT' `STAR' label `IVST' ///
    mtitles("Promote 1" "Promote 2" "Promote 3" "Demote 1" "Demote 2" "Demote 3") ///
    keep(log_airbnb log_comphotels log_reviews_lag log_airbnb_x_low) ///
    title("Table E1 (Texas). Gaussian kernel, bandwidth 1 km, 2SLS")
esttab ek05p_* ek05d_* using "results/stata/tx_tableE1_05km.txt", replace `FMT' `STAR' label `IVST' ///
    mtitles("Promote 1" "Promote 2" "Promote 3" "Demote 1" "Demote 2" "Demote 3") ///
    keep(log_airbnb log_comphotels log_reviews_lag log_airbnb_x_low) ///
    title("Table E1 (Texas). Gaussian kernel, bandwidth 0.5 km, 2SLS")

*==============================================================================
* Table 6: look-ahead PSM. Treated = Group A (Airbnb competitor in Period 1); controls drawn from Groups B and C
* (not yet treated in Period 1). Matching on observable pre-period covariates (STR price, rooms, chain and
* location type are not available), nearest neighbour without replacement, caliper 0.1 on the propensity score.
*==============================================================================
import delimited "data_extract/hotels_tx_lapsm.csv", clear varnames(1) encoding(utf8)
encode city, gen(cityid)
logit treated lowend pre_reviews pre_rating pre_share5 pre_share12 n_comp_same opened_before_2011 i.cityid
predict ps, pr
psmatch2 treated, pscore(ps) neighbor(1) noreplacement caliper(0.1) common
quietly count if treated == 1 & _weight != .
local n_tr = r(N)
quietly count if treated == 0 & _weight != .
local n_co = r(N)
display "Table 6 matched sample: " `n_tr' " treated hotels and " `n_co' " matched controls"
* balance of the matched sample
pstest lowend pre_reviews pre_rating pre_share5 pre_share12 n_comp_same opened_before_2011, both
capture log close balance
log using "results/stata/tx_table6_balance.txt", replace text name(balance)
display "Table 6 (Texas). Covariate balance before and after look-ahead PSM: " `n_tr' " treated, " `n_co' " controls"
pstest lowend pre_reviews pre_rating pre_share5 pre_share12 n_comp_same opened_before_2011, both
log close balance
keep if _weight != .
keep hotel_id _weight
tempfile matched
save `matched'

import delimited "data_extract/panel_tx.csv", clear varnames(1) encoding(utf8)
merge m:1 hotel_id using `matched', keep(match) nogenerate
prep_basic
gen log_airbnb_x_low = log_airbnb * lowend
gen log_iv_x_low     = log_iv * lowend
label var log_airbnb        "log(Airbnb)"
label var log_comphotels    "log(CompetingHotels)"
label var log_airbnb_x_low  "log(Airbnb) x Low-end"
eststo clear
three_models selfpromo       t6p 1
three_models demoting_others t6d 1
esttab t6p_* t6d_* using "results/stata/tx_table6.txt", replace `FMT' `STAR' label `IVST' ///
    mtitles("Promote 1" "Promote 2" "Promote 3" "Demote 1" "Demote 2" "Demote 3") ///
    keep(log_airbnb log_comphotels log_reviews_lag log_airbnb_x_low) ///
    title("Table 6 (Texas). LA-PSM-matched hotels, 2SLS")

*==============================================================================
* Table 7: synthetic control with staggered adoption (sdid, Arkhangelsky et al. 2021), the Stata counterpart of
* the paper's generalized synthetic control. Binary treatment = any competing Airbnb listing within 1 km (lagged),
* absorbing. Balanced panel 2012Q1-2019Q2 of hotels with the outcome observed every quarter and not yet treated
* at the start of the window. Covariates projected out: log(CompetingHotels), Log(ReviewCount).
*==============================================================================
import delimited "data_extract/panel_tx.csv", clear varnames(1) encoding(utf8)
prep_basic
gen treat = airbnb_lag > 0
keep if qdate >= tq(2012q1)
quietly sum qdate
local nq = r(max) - r(min) + 1
matrix T7 = J(5, 6, .)
matrix rownames T7 = "Airbnb treatment (ATT)" "Standard error" "Treated hotels" "Control hotels" "Quarters"
matrix colnames T7 = "Promote all" "Promote high" "Promote low" "Demote all" "Demote high" "Demote low"
local col = 0
foreach y in selfpromo demoting_others {
    foreach s in all high low {
        local col = `col' + 1
        preserve
        if "`s'" == "high" keep if lowend == 0
        if "`s'" == "low"  keep if lowend == 1
        bysort hid: egen nobs = count(`y')
        bysort hid: egen treat0 = max(cond(qdate == tq(2012q1), treat, 0))
        keep if nobs == `nq' & treat0 == 0
        bysort hid: egen ever = max(treat)
        quietly tab hid if ever == 1
        local ntr = r(r)
        quietly tab hid if ever == 0
        local nco = r(r)
        display "Table 7, `y' `s': treated hotels = `ntr', control hotels = `nco'"
        capture noisily sdid `y' hid qdate treat, vce(bootstrap) reps(50) seed(2022) covariates(log_comphotels log_reviews_lag, projected)
        if _rc == 0 {
            matrix T7[1, `col'] = e(ATT)
            matrix T7[2, `col'] = e(se)
        }
        matrix T7[3, `col'] = `ntr'
        matrix T7[4, `col'] = `nco'
        matrix T7[5, `col'] = `nq'
        restore
    }
}
matrix list T7
esttab matrix(T7, fmt(3 3 0 0 0)) using "results/stata/tx_table7.txt", replace nonotes compress varwidth(26) modelwidth(13) ///
    title("Table 7 (Texas). Synthetic difference-in-differences (sdid), balanced panel 2012Q1-2019Q2")

display "Done. results/stata/tx_tableE1.txt, tx_tableE1_05km.txt, tx_table6.txt, tx_table6_balance.txt, tx_table7.txt"
