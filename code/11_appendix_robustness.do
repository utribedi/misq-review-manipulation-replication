*==============================================================================
* Appendices B, C, F and H of Nie, Zheng & Sarkar (2022), Texas panel. Stata estimation.
* Inputs (built by code/11_appendix_robustness.py):
*   data_extract/panel_tx_appB.csv      hotel-quarter panel with relative-time dummies ev_m2 ... ev_p3
*   data_extract/panel_tx_appFH.csv     hotel-quarter panel with the uniform-threshold measures (F) and all-tier competitor measures (H)
*   data_extract/panel_triplets_TX.csv  hotel-triplet panel (C)
* Outputs: results/stata/tx_tableB1.txt, tx_tableF1.txt, tx_tableH1.txt, tx_tableC1.txt, figB1_TX.png
* Run from the project folder:  do "code/11_appendix_robustness.do"
* Requires: reghdfe ivreghdfe ftools ivreg2 ranktest estout
*==============================================================================
clear all
set more off
capture mkdir "results/stata"
graph set window fontface "Times New Roman"
set scheme s1mono

local STAR  star(* 0.05 ** 0.01 *** 0.001)
local FMT   b(3) se(3) nonotes nogaps compress varwidth(30) modelwidth(16)
local IVST  stats(N widstat, fmt(%9.0fc %9.1f) labels("Observations" "Kleibergen-Paap F"))
local OLST  stats(N, fmt(%9.0fc) labels("Observations"))

program define prep_panel
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
    capture drop log_airbnb_x_low
    capture drop log_iv_x_low
    gen log_airbnb_x_low = log_airbnb * lowend
    gen log_iv_x_low     = log_iv * lowend
    label var log_airbnb        "log(Airbnb)"
    label var log_comphotels    "log(CompetingHotels)"
    label var log_reviews_lag   "Log(ReviewCount)"
    label var log_airbnb_x_low  "log(Airbnb) x Low-end"
end

*==============================================================================
* Appendix B: relative-time model (Table B1) and an event-study figure
*==============================================================================
import delimited "data_extract/panel_tx_appB.csv", clear varnames(1) encoding(utf8)
prep_panel
label var ev_m2 "Airbnb_Binary treat(-2)"
label var ev_m1 "Airbnb_Binary treat(-1)"
label var ev_0  "Airbnb_Binary treat(0)"
label var ev_p1 "Airbnb_Binary treat(+1)"
label var ev_p2 "Airbnb_Binary treat(+2)"
label var ev_p3 "Airbnb_Binary treat(+3)"
eststo clear
eststo b1: reghdfe selfpromo       ev_m2 ev_m1 ev_0 ev_p1 ev_p2 ev_p3 log_comphotels, absorb(hid qdate city_season) cluster(hid)
eststo b2: reghdfe selfpromo       ev_m2 ev_m1 ev_0 ev_p1 ev_p2 ev_p3 log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag, absorb(hid qdate city_season) cluster(hid)
eststo b3: reghdfe demoting_others ev_m2 ev_m1 ev_0 ev_p1 ev_p2 ev_p3 log_comphotels, absorb(hid qdate city_season) cluster(hid)
eststo b4: reghdfe demoting_others ev_m2 ev_m1 ev_0 ev_p1 ev_p2 ev_p3 log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag, absorb(hid qdate city_season) cluster(hid)
esttab b1 b2 b3 b4 using "results/stata/tx_tableB1.txt", replace `FMT' `STAR' label `OLST' ///
    mtitles("Promote 1" "Promote 2" "Demote 1" "Demote 2") ///
    keep(ev_m2 ev_m1 ev_0 ev_p1 ev_p2 ev_p3 log_comphotels log_reviews_lag) ///
    title("Table B1 (Texas). Relative-time model, OLS with hotel, quarter and city x season FE")

* Event-study figure from models b2 and b4
foreach m in b2 b4 {
    estimates restore `m'
    matrix B_`m' = e(b)
    matrix V_`m' = e(V)
}
preserve
clear
set obs 6
gen j = _n - 3
gen b_promote = .
gen se_promote = .
gen b_demote = .
gen se_demote = .
local k = 1
foreach v in ev_m2 ev_m1 ev_0 ev_p1 ev_p2 ev_p3 {
    replace b_promote  = B_b2[1, colnumb(B_b2, "`v'")] in `k'
    replace se_promote = sqrt(V_b2[colnumb(V_b2, "`v'"), colnumb(V_b2, "`v'")]) in `k'
    replace b_demote   = B_b4[1, colnumb(B_b4, "`v'")] in `k'
    replace se_demote  = sqrt(V_b4[colnumb(V_b4, "`v'"), colnumb(V_b4, "`v'")]) in `k'
    local k = `k' + 1
}
foreach y in promote demote {
    gen lo_`y' = b_`y' - 1.96 * se_`y'
    gen hi_`y' = b_`y' + 1.96 * se_`y'
}
twoway (rcap lo_promote hi_promote j, lcolor(black)) (scatter b_promote j, mcolor(black) msymbol(O)) ///
       (rcap lo_demote hi_demote j, lcolor(gs8)) (scatter b_demote j, mcolor(gs8) msymbol(D)), ///
    yline(0, lcolor(gs10)) xline(-0.5, lpattern(dash) lcolor(gs10)) ///
    xlabel(-2 "-2" -1 "-1" 0 "0" 1 "+1" 2 "+2" 3 "+3") xtitle("Quarters relative to first Airbnb competitor") ytitle("Coefficient, 95% CI") ///
    legend(order(2 "Self-promotion" 4 "Demoting others") rows(1) position(6)) ///
    title("Figure B1 (Texas). Relative-time model, Model 2 coefficients", size(medium) position(11))
graph export "results/stata/figB1_TX.png", width(2400) replace
restore

*==============================================================================
* Appendix F (uniform thresholds) and Appendix H (all neighbouring hotels as competitors)
*==============================================================================
import delimited "data_extract/panel_tx_appFH.csv", clear varnames(1) encoding(utf8)
prep_panel
gen log_iv_all_x_low = log_iv_all * lowend
label var log_comphotels_all "log(CompetingHotels)"
label var log_airbnb_x_low   "log(Airbnb) x Low-end"

* Table F1
eststo clear
foreach y in selfpromo_f demoting_others_f {
    eststo f_`y'_m1: ivreghdfe `y' log_comphotels (log_airbnb = log_iv), absorb(hid qdate city_season) cluster(hid)
    eststo f_`y'_m2: ivreghdfe `y' log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag (log_airbnb = log_iv), absorb(hid qdate city_season) cluster(hid)
    eststo f_`y'_m3: ivreghdfe `y' log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag ///
        (log_airbnb log_airbnb_x_low = log_iv log_iv_x_low), absorb(hid qdate city_season) cluster(hid)
}
esttab f_* using "results/stata/tx_tableF1.txt", replace `FMT' `STAR' label `IVST' ///
    mtitles("Promote 1" "Promote 2" "Promote 3" "Demote 1" "Demote 2" "Demote 3") ///
    keep(log_airbnb log_comphotels log_reviews_lag log_airbnb_x_low) ///
    title("Table F1 (Texas). Same thresholds for all hotels (5-star promotion, 1-2-star demotion), 2SLS")

* Table H1: competitor count, demoting-others and the instrument rebuilt over all hotels within 1 km
eststo clear
foreach y in selfpromo demoting_others_all {
    eststo h_`y'_m1: ivreghdfe `y' log_comphotels_all (log_airbnb = log_iv_all), absorb(hid qdate city_season) cluster(hid)
    eststo h_`y'_m2: ivreghdfe `y' log_comphotels_all log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag (log_airbnb = log_iv_all), absorb(hid qdate city_season) cluster(hid)
    eststo h_`y'_m3: ivreghdfe `y' log_comphotels_all log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag ///
        (log_airbnb log_airbnb_x_low = log_iv_all log_iv_all_x_low), absorb(hid qdate city_season) cluster(hid)
}
esttab h_* using "results/stata/tx_tableH1.txt", replace `FMT' `STAR' label `IVST' ///
    mtitles("Promote 1" "Promote 2" "Promote 3" "Demote 1" "Demote 2" "Demote 3") ///
    keep(log_airbnb log_comphotels_all log_reviews_lag log_airbnb_x_low) ///
    title("Table H1 (Texas). All neighbouring hotels as competitors, 2SLS")

*==============================================================================
* Appendix C: mutual demotion within hotel triplets (Table C1)
*==============================================================================
import delimited "data_extract/panel_triplets_TX.csv", clear varnames(1) encoding(utf8)
encode triplet, gen(tid)
gen qdate = quarterly(yq, "YQ")
encode city, gen(cityid)
capture drop city_season
capture drop season
gen season = quarter(dofq(qdate))
egen city_season = group(cityid season)
label var log_airbnb "log(Airbnb)"
label var log_comphotels "log(CompetingHotels)"
label var log_reviews_lag "Log(ReviewCount)"
label var log_airbnb_x_low "log(Airbnb) x Low-end"
eststo clear
eststo c1: ivreghdfe mutual log_comphotels (log_airbnb = log_iv), absorb(tid qdate city_season) cluster(tid)
eststo c2: ivreghdfe mutual log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag (log_airbnb = log_iv), absorb(tid qdate city_season) cluster(tid)
eststo c3: ivreghdfe mutual log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag (log_airbnb log_airbnb_x_low = log_iv log_iv_x_low), absorb(tid qdate city_season) cluster(tid)
esttab c1 c2 c3 using "results/stata/tx_tableC1.txt", replace `FMT' `STAR' label `IVST' mtitles("Model 1" "Model 2" "Model 3") ///
    keep(log_airbnb log_comphotels log_reviews_lag log_airbnb_x_low) ///
    title("Table C1 (Texas). Mutual demotion within hotel triplets, 2SLS")
quietly tab tid
display "Triplets = " r(r) ", triplet-quarters = " _N

display "Done. Tables in results/stata/tx_tableB1.txt, tx_tableF1.txt, tx_tableH1.txt, tx_tableC1.txt; figure results/stata/figB1_TX.png"
