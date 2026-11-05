*==============================================================================
* Every table and figure in the deck, produced by Stata.
* Tables  -> results\stata\<name>.txt  (esttab plain text, pasted into the slides as Stata output)
* Figures -> results\stata\<name>.png  (Stata graphs, Times New Roman, monochrome)
* Run from the project folder:  do "code\07_stata_outputs.do"
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

*------------------------------------------------------------------------------
program define prep_panel
    * ids, time, lagged review controls, interaction terms (same as 06_tables.do)
    encode hotel_id, gen(hid)
    gen qdate = quarterly(yq, "YQ")
    format qdate %tq
    gen season = quarter(dofq(qdate))
    encode city, gen(cityid)
    egen city_season = group(cityid season)
    xtset hid qdate
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
    label var log_iv            "log(Cmp_Airbnb)"
end

program define three_models
    * args: y  prefix  haslow
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
* TEXAS: Tables 1, 2, 3, 8, 5, Appendix I and the 2015Q4 break
*==============================================================================
import delimited "data_extract/panel_tx.csv", clear varnames(1) encoding(utf8)
prep_panel

* Table 1
preserve
keep if !missing(selfpromo)
estpost tabstat n_ta ta1 ta2 ta3 ta4 ta5 airbnb_lag comphotels, stat(mean sd min max) col(stat)
esttab using "results/stata/tx_table1.txt", replace varwidth(34) cells("mean(fmt(2)) sd(fmt(2)) min(fmt(0)) max(fmt(0))") ///
    noobs nonumber nomtitle label title("Table 1 (Texas). Summary statistics at the hotel-quarter level") ///
    coeflabels(n_ta "TripAdvisor reviews per quarter" ta1 "1-star reviews" ta2 "2-star reviews" ta3 "3-star reviews" ///
    ta4 "4-star reviews" ta5 "5-star reviews" airbnb_lag "Competing Airbnb listings" comphotels "Competing hotels")
quietly tab hid
display "Texas: hotels = " r(r) ", hotel-quarters = " _N
restore

eststo clear
three_models selfpromo tx2 1
three_models demoting_others tx3 1
three_models demotion tx8 1
esttab tx2_* using "results/stata/tx_table2.txt", replace `FMT' `STAR' label `IVST' mtitles("Model 1" "Model 2" "Model 3") ///
    keep(log_airbnb log_comphotels log_reviews_lag log_airbnb_x_low) title("Table 2 (Texas). Self-promotion, 2SLS")
esttab tx3_* using "results/stata/tx_table3.txt", replace `FMT' `STAR' label `IVST' mtitles("Model 1" "Model 2" "Model 3") ///
    keep(log_airbnb log_comphotels log_reviews_lag log_airbnb_x_low) title("Table 3 (Texas). Demoting others, 2SLS")
esttab tx8_* using "results/stata/tx_table8.txt", replace `FMT' `STAR' label `IVST' mtitles("Model 1" "Model 2" "Model 3") ///
    keep(log_airbnb log_comphotels log_reviews_lag log_airbnb_x_low) title("Table 8 (Texas). Being demoted, 2SLS")

* Table 5: IV validity
bysort hid: egen ever_airbnb = max(airbnb_lag)
eststo clear
eststo t5_1: reghdfe selfpromo       log_iv log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag if ever_airbnb == 0, absorb(hid qdate city_season) cluster(hid)
eststo t5_2: reghdfe demoting_others log_iv log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag if ever_airbnb == 0, absorb(hid qdate city_season) cluster(hid)
eststo t5_3: reghdfe selfpromo       log_iv log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag if ever_airbnb >  0, absorb(hid qdate city_season) cluster(hid)
eststo t5_4: reghdfe demoting_others log_iv log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag if ever_airbnb >  0, absorb(hid qdate city_season) cluster(hid)
esttab t5_* using "results/stata/tx_table5.txt", replace `FMT' `STAR' label `OLST' modelwidth(18) ///
    mtitles("Unexposed promote" "Unexposed demote" "Exposed promote" "Exposed demote") ///
    keep(log_iv log_comphotels log_reviews_lag) title("Table 5 (Texas). IV validity: direct effect of the instrument")

* Appendix I and the 2015Q4 break (extension 1)
eststo clear
eststo i1: ivreghdfe selfpromo log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag (log_airbnb = log_iv) if qdate <= tq(2011q4), absorb(hid qdate city_season) cluster(hid)
eststo i2: ivreghdfe selfpromo log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag (log_airbnb = log_iv) if qdate >  tq(2011q4) & qdate <= tq(2015q4), absorb(hid qdate city_season) cluster(hid)
eststo i3: ivreghdfe selfpromo log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag (log_airbnb = log_iv) if qdate >  tq(2015q4), absorb(hid qdate city_season) cluster(hid)
eststo i4: ivreghdfe demoting_others log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag (log_airbnb = log_iv) if qdate <= tq(2011q4), absorb(hid qdate city_season) cluster(hid)
eststo i5: ivreghdfe demoting_others log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag (log_airbnb = log_iv) if qdate >  tq(2011q4) & qdate <= tq(2015q4), absorb(hid qdate city_season) cluster(hid)
eststo i6: ivreghdfe demoting_others log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag (log_airbnb = log_iv) if qdate >  tq(2015q4), absorb(hid qdate city_season) cluster(hid)
esttab i1 i2 i3 i4 i5 i6 using "results/stata/tx_tableI1_breaks.txt", replace `FMT' `STAR' label `IVST' ///
    mtitles("Promote <=2011q4" "Promote 2012-15" "Promote >=2016" "Demote <=2011q4" "Demote 2012-15" "Demote >=2016") ///
    keep(log_airbnb log_comphotels log_reviews_lag) title("Table I1 (Texas) and extension 1: 2SLS by sub-period")

* Figure A1 (Texas): mean TripAdvisor rating and mean competing Airbnb listings by quarter
preserve
keep if n_ta > 0
gen mean_ta = (ta1 + 2*ta2 + 3*ta3 + 4*ta4 + 5*ta5) / n_ta
collapse (mean) mean_ta airbnb_lag [aw = n_ta], by(qdate)
twoway (line mean_ta qdate, lcolor(black) lwidth(medthick) yaxis(1)) ///
       (line airbnb_lag qdate, lcolor(gs8) lpattern(dash) yaxis(2)), ///
    ytitle("Mean TripAdvisor rating", axis(1)) ytitle("Competing Airbnb listings (mean)", axis(2)) xtitle("") ///
    legend(order(1 "TripAdvisor mean rating" 2 "Competing Airbnb listings") rows(1) position(6)) ///
    title("Figure A1 (Texas). Average ratings and Airbnb supply by quarter", size(medium) position(11))
graph export "results/stata/figA1_TX.png", width(2400) replace
restore

* Figure A2 (Texas): positive and negative shares by tier
preserve
keep if n_ta > 0
gen pos = share5_ta * n_ta
gen neg = share12_ta * n_ta
collapse (sum) pos neg n_ta, by(qdate lowend)
gen pos_share = pos / n_ta
gen neg_share = neg / n_ta
label define tier 0 "High-end hotels" 1 "Low-end hotels"
label values lowend tier
twoway (line pos_share qdate, lcolor(black) lwidth(medthick)) (line neg_share qdate, lcolor(gs8) lwidth(medthick)), ///
    by(lowend, rows(1) note("") title("Figure A2 (Texas). Proportions of positive and negative TripAdvisor ratings", size(medium) position(11))) ///
    ytitle("Share of quarterly reviews") xtitle("") legend(order(1 "Positive share" 2 "Negative share") rows(1) position(6))
graph export "results/stata/figA2_TX.png", width(2400) replace
restore

*==============================================================================
* TEXAS: Table G1 (segmented Airbnb), Table 4 (pairs), text-based measure (extension 2)
*==============================================================================
import delimited "data_extract/panel_tx_segG.csv", clear varnames(1) encoding(utf8)
encode hotel_id, gen(hid)
gen qdate = quarterly(yq, "YQ")
encode city, gen(cityid)
capture drop city_season
capture drop season
gen season = quarter(dofq(qdate))
egen city_season = group(cityid season)
label var log_airbnb_seg "log(Airbnb, same segment)"
label var log_comphotels "log(CompetingHotels)"
label var log_reviews_lag "Log(ReviewCount)"
label var log_airbnb_x_low_seg "log(Airbnb) x Low-end"
eststo clear
foreach y in selfpromo demoting_others {
    eststo g_`y'_m1: ivreghdfe `y' log_comphotels (log_airbnb_seg = log_iv_seg), absorb(hid qdate city_season) cluster(hid)
    eststo g_`y'_m2: ivreghdfe `y' log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag (log_airbnb_seg = log_iv_seg), absorb(hid qdate city_season) cluster(hid)
    eststo g_`y'_m3: ivreghdfe `y' log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag ///
        (log_airbnb_seg log_airbnb_x_low_seg = log_iv_seg log_iv_x_low_seg), absorb(hid qdate city_season) cluster(hid)
}
esttab g_* using "results/stata/tx_tableG1.txt", replace `FMT' `STAR' label `IVST' ///
    mtitles("Promote 1" "Promote 2" "Promote 3" "Demote 1" "Demote 2" "Demote 3") ///
    keep(log_airbnb_seg log_comphotels log_reviews_lag log_airbnb_x_low_seg) title("Table G1 (Texas). Same-segment Airbnb competitors, 2SLS")

import delimited "data_extract/panel_pairs_TX.csv", clear varnames(1) encoding(utf8)
encode pair, gen(pid)
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
eststo p1: ivreghdfe mutual log_comphotels (log_airbnb = log_iv), absorb(pid qdate city_season) cluster(pid)
eststo p2: ivreghdfe mutual log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag (log_airbnb = log_iv), absorb(pid qdate city_season) cluster(pid)
eststo p3: ivreghdfe mutual log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag (log_airbnb log_airbnb_x_low = log_iv log_iv_x_low), absorb(pid qdate city_season) cluster(pid)
esttab p1 p2 p3 using "results/stata/tx_table4.txt", replace `FMT' `STAR' label `IVST' mtitles("Model 1" "Model 2" "Model 3") ///
    keep(log_airbnb log_comphotels log_reviews_lag log_airbnb_x_low) title("Table 4 (Texas). Mutual demotion, hotel-pair level, 2SLS")

import delimited "data_extract/panel_TX_text.csv", clear varnames(1) encoding(utf8)
encode hotel_id, gen(hid)
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
foreach y in share_fake5 share_fake12 {
    eststo x_`y'_m1: ivreghdfe `y' log_comphotels (log_airbnb = log_iv) if n_ta > 0, absorb(hid qdate city_season) cluster(hid)
    eststo x_`y'_m2: ivreghdfe `y' log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag (log_airbnb = log_iv) if n_ta > 0, absorb(hid qdate city_season) cluster(hid)
    eststo x_`y'_m3: ivreghdfe `y' log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag (log_airbnb log_airbnb_x_low = log_iv log_iv_x_low) if n_ta > 0, absorb(hid qdate city_season) cluster(hid)
}
esttab x_* using "results/stata/tx_text_measure.txt", replace `FMT' `STAR' label `IVST' ///
    mtitles("Fake 5-star 1" "Fake 5-star 2" "Fake 5-star 3" "Fake 1-2-star 1" "Fake 1-2-star 2" "Fake 1-2-star 3") ///
    keep(log_airbnb log_comphotels log_reviews_lag log_airbnb_x_low) title("Extension 2 (Texas). Text-flagged deceptive reviews, 2SLS")

*==============================================================================
* EUROPE: Tables 2, 3, 8 (and Table 4), Figure D1, extension 3
*==============================================================================
import delimited "data_extract/panel_eu_v2.csv", clear varnames(1) encoding(utf8)
prep_panel
eststo clear
three_models selfpromo eu2 0
three_models demoting_others eu3 0
three_models demotion eu8 0
esttab eu2_* using "results/stata/eu_table2.txt", replace `FMT' `STAR' label `IVST' mtitles("Model 1" "Model 2") keep(log_airbnb log_comphotels log_reviews_lag) title("Table 2 (Europe). Self-promotion, 2SLS")
esttab eu3_* using "results/stata/eu_table3.txt", replace `FMT' `STAR' label `IVST' mtitles("Model 1" "Model 2") keep(log_airbnb log_comphotels log_reviews_lag) title("Table 3 (Europe). Demoting others, 2SLS")
esttab eu8_* using "results/stata/eu_table8.txt", replace `FMT' `STAR' label `IVST' mtitles("Model 1" "Model 2") keep(log_airbnb log_comphotels log_reviews_lag) title("Table 8 (Europe). Being demoted, 2SLS")
esttab eu2_m2 eu3_m2 eu8_m2 using "results/stata/eu_summary.txt", replace `FMT' `STAR' label `IVST' ///
    mtitles("Self-promotion" "Demoting others" "Being demoted") keep(log_airbnb log_comphotels) title("Europe. 2SLS, Model 2, all three outcomes")

import delimited "data_extract/panel_pairs_EU.csv", clear varnames(1) encoding(utf8)
encode pair, gen(pid)
gen qdate = quarterly(yq, "YQ")
encode city, gen(cityid)
capture drop city_season
capture drop season
gen season = quarter(dofq(qdate))
egen city_season = group(cityid season)
label var log_airbnb "log(Airbnb)"
label var log_comphotels "log(CompetingHotels)"
label var log_reviews_lag "Log(ReviewCount)"
eststo clear
eststo pe1: ivreghdfe mutual log_comphotels (log_airbnb = log_iv), absorb(pid qdate city_season) cluster(pid)
eststo pe2: ivreghdfe mutual log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag (log_airbnb = log_iv), absorb(pid qdate city_season) cluster(pid)
esttab pe1 pe2 using "results/stata/eu_table4.txt", replace `FMT' `STAR' label `IVST' mtitles("Model 1" "Model 2") keep(log_airbnb log_comphotels log_reviews_lag) title("Table 4 (Europe). Mutual demotion, hotel-pair level, 2SLS")

import delimited "data_extract/panel_eu_extension.csv", clear varnames(1) encoding(utf8)
encode hotel_id, gen(hid)
gen qdate = quarterly(yq, "YQ")
encode city, gen(cityid)
capture drop city_season
capture drop season
gen season = quarter(dofq(qdate))
egen city_season = group(cityid season)
label var log_airbnb "log(Airbnb)"
label var log_comphotels "log(CompetingHotels)"
label var log_reviews_lag "Log(ReviewCount)"
correlate onetime_excess_top selfpromo if !missing(selfpromo)
display "Correlation of the one-time-reviewer excess with the Mayzlin-style gap: " r(rho)
eststo clear
eststo e1: ivreghdfe onetime_excess_top log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag (log_airbnb = log_iv) if !missing(selfpromo), absorb(hid qdate city_season) cluster(hid)
eststo e2: reghdfe   onetime_excess_top log_airbnb log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag if !missing(selfpromo), absorb(hid qdate city_season) cluster(hid)
eststo e3: ivreghdfe onetime_excess_bot log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag (log_airbnb = log_iv) if !missing(selfpromo), absorb(hid qdate city_season) cluster(hid)
eststo e4: reghdfe   onetime_excess_bot log_airbnb log_comphotels log_reviews_lag ratio2_lag ratio3_lag ratio4_lag ratio5_lag if !missing(selfpromo), absorb(hid qdate city_season) cluster(hid)
esttab e1 e2 e3 e4 using "results/stata/eu_extension3.txt", replace `FMT' `STAR' label `OLST' ///
    mtitles("Excess top, 2SLS" "Excess top, OLS" "Excess bottom, 2SLS" "Excess bottom, OLS") keep(log_airbnb log_comphotels log_reviews_lag) ///
    title("Extension 3 (Europe). One-time-reviewer excess, TripAdvisor minus Booking.com")

* Figure D1 (Europe): trip-type shares by quarter
import delimited "data_extract/figD1_data_EU.csv", clear varnames(1) encoding(utf8)
gen qdate = quarterly(q, "YQ")
format qdate %tq
twoway (line leisure qdate, lcolor(black)) (line business qdate, lcolor(gs6)) (line couple qdate, lcolor(gs9)) ///
       (line solo qdate, lcolor(black) lpattern(dash)) (line family qdate, lcolor(gs6) lpattern(dash)) (line groupfriends qdate, lcolor(gs9) lpattern(dash)), ///
    ytitle("Share of Booking.com reviews") xtitle("") legend(order(1 "Leisure" 2 "Business" 3 "Couple" 4 "Solo" 5 "Family" 6 "Group/friends") rows(2) position(6)) ///
    title("Figure D1 (Europe). Trip-type shares by quarter", size(medium) position(11))
graph export "results/stata/figD1_EU.png", width(2400) replace

display "done: results/stata/"
