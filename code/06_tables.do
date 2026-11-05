*==============================================================================
* Replication of Nie, Zheng & Sarkar (2022, MISQ) table structure
* Run on data_extract/panel_eu.csv and data_extract/panel_tx.csv
* Requires: ssc install reghdfe ivreghdfe ftools ivreg2 ranktest estout
*==============================================================================
clear all
set more off
local panel "`1'"          // e.g. panel_eu  or panel_tx
if "`panel'" == "" local panel "panel_tx"
cd "`c(pwd)'"
import delimited "data_extract/`panel'.csv", clear varnames(1) encoding(utf8)

* ---- ids and time -----------------------------------------------------------
encode hotel_id, gen(hid)
gen qdate = quarterly(yq, "YQ")
format qdate %tq
gen season = quarter(dofq(qdate))
encode city, gen(cityid)
egen city_season = group(cityid season)
xtset hid qdate

* ---- lagged review controls (previous quarter on TripAdvisor) ---------------
foreach v in n_ta ta2 ta3 ta4 ta5 {
    gen `v'_lag = L.`v'
    replace `v'_lag = 0 if missing(`v'_lag)
}
forvalues s = 2/5 {
    gen ratio`s'_lag = cond(n_ta_lag > 0, ta`s'_lag / n_ta_lag, 0)
}
gen log_reviews_lag = log(n_ta_lag + 1)
gen log_airbnb_x_low = log_airbnb * lowend
gen log_iv_x_low     = log_iv * lowend
label var log_airbnb        "log(Airbnb)"
label var log_comphotels    "log(CompetingHotels)"
label var log_reviews_lag   "Log(ReviewCount)"
label var log_airbnb_x_low  "log(Airbnb) x Low-end"

* ---- Table 1 ----------------------------------------------------------------
preserve
keep if !missing(selfpromo)
tabstat n_ta ta1 ta2 ta3 ta4 ta5 airbnb_lag comphotels, stat(mean sd min max) col(stat) format(%9.2f)
capture tabstat n_bk bk_top9 bk_bot5, stat(mean sd min max) col(stat) format(%9.2f)
quietly tab hid
display "Total hotels: " r(r) "   hotel-quarter observations: " _N
restore

* ---- Tables 2, 3, 8: 2SLS with hotel FE, quarter FE, city x season FE --------
* Model 3 (low-end interaction) only when at least 5 low-end hotels exist
preserve
bysort hid: keep if _n == 1
quietly count if lowend == 1
local nlow = r(N)
restore
local haslow = (`nlow' >= 5)
display "low-end hotels: `nlow'  -> Model 3 " cond(`haslow', "included", "omitted")
local keepvars "log_airbnb log_comphotels log_reviews_lag"
if `haslow' local keepvars "`keepvars' log_airbnb_x_low"
eststo clear
foreach y in selfpromo demoting_others demotion {
    eststo `y'_m1: ivreghdfe `y' log_comphotels (log_airbnb = log_iv), ///
        absorb(hid qdate city_season) cluster(hid)
    eststo `y'_m2: ivreghdfe `y' log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag ///
        (log_airbnb = log_iv), absorb(hid qdate city_season) cluster(hid)
    if `haslow' {
        eststo `y'_m3: ivreghdfe `y' log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag ///
            (log_airbnb log_airbnb_x_low = log_iv log_iv_x_low), absorb(hid qdate city_season) cluster(hid)
    }
}
esttab selfpromo_* using "results/`panel'_table2_selfpromotion.rtf", replace label se star(* 0.05 ** 0.01 *** 0.001) ///
    keep(`keepvars') stats(N widstat, label("Observations" "KP F-stat")) ///
    title("Table 2. Self-Promotion with 2SLS")
esttab demoting_others_* using "results/`panel'_table3_demotingothers.rtf", replace label se star(* 0.05 ** 0.01 *** 0.001) ///
    keep(`keepvars') stats(N widstat, label("Observations" "KP F-stat")) ///
    title("Table 3. Demotion Behavior with 2SLS")
esttab demotion_* using "results/`panel'_table8_beingdemoted.rtf", replace label se star(* 0.05 ** 0.01 *** 0.001) ///
    keep(`keepvars') stats(N widstat, label("Observations" "KP F-stat")) ///
    title("Table 8. Being Demoted with 2SLS")

* ---- OLS two-way FE reference -----------------------------------------------
eststo clear
foreach y in selfpromo demoting_others demotion {
    eststo ols_`y': reghdfe `y' log_airbnb log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag, ///
        absorb(hid qdate city_season) cluster(hid)
}
esttab ols_* using "results/`panel'_ols_fe_reference.rtf", replace label se star(* 0.05 ** 0.01 *** 0.001) ///
    keep(log_airbnb log_comphotels log_reviews_lag) stats(N, label("Observations")) title("OLS two-way FE")

* ---- Table 5: IV validity (hotels never / ever exposed to Airbnb) -----------
bysort hid: egen ever_airbnb = max(airbnb_lag)
eststo clear
foreach y in selfpromo demoting_others {
    capture eststo v0_`y': reghdfe `y' log_iv log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag ///
        if ever_airbnb == 0, absorb(hid qdate city_season) cluster(hid)
    eststo v1_`y': reghdfe `y' log_iv log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag ///
        if ever_airbnb > 0, absorb(hid qdate city_season) cluster(hid)
}
esttab v* using "results/`panel'_table5_iv_validity.rtf", replace label se star(* 0.05 ** 0.01 *** 0.001) ///
    keep(log_iv log_comphotels log_reviews_lag) stats(N, label("Observations")) title("Table 5. IV validity check")

* ---- Appendix I: before/after the inflection point (2011Q4) -----------------
capture {
    eststo clear
    eststo pre:  ivreghdfe demoting_others log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag ///
        (log_airbnb = log_iv) if qdate <= tq(2011q4), absorb(hid qdate city_season) cluster(hid)
    eststo post: ivreghdfe demoting_others log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag ///
        (log_airbnb = log_iv) if qdate >  tq(2011q4), absorb(hid qdate city_season) cluster(hid)
    esttab pre post using "results/`panel'_tableI1_inflection.rtf", replace label se star(* 0.05 ** 0.01 *** 0.001) ///
        keep(log_airbnb log_comphotels) stats(N, label("Observations")) title("Table I1. Before/after 2011Q4")
}
display "done: `panel'"
