# Table 7 of Nie, Zheng & Sarkar (2022) with the generalized synthetic control (Xu 2017), Texas panel.
# fect::fect(method = "ife") is the GSC estimator (interactive fixed effects, factors chosen by CV) and allows
# missing outcomes, so the full panel is used. gsynth::gsynth is the original estimator on a balanced panel.
# Run from the project folder:  source("code/13_table7_gsynth.R")
# Outputs: results/table7_gsynth_R.csv, results/table7_gsynth_R.txt, results/stata/fig_table7_gsynth.png
library(fect); library(gsynth)
d <- read.csv("data_extract/panel_tx_appB.csv", stringsAsFactors = FALSE)
d$treat <- as.integer(d$airbnb_lag > 0)                         # binary, absorbing Airbnb treatment (paper's Table 7)
d$t <- as.integer(factor(d$yq, levels = sort(unique(d$yq))))
d <- d[order(d$hotel_id, d$t), ]

run_fect <- function(y, sub) {
  sub <- sub[!is.na(sub[[y]]), ]
  f <- as.formula(paste(y, "~ treat + log_comphotels + log_reviews_lag"))
  tryCatch(
    fect(f, data = sub, index = c("hotel_id", "t"), method = "ife", force = "two-way",
         CV = TRUE, r = c(0, 5), se = TRUE, nboots = 200, parallel = TRUE, cores = 4, seed = 2022),
    error = function(e) { message("fect failed: ", conditionMessage(e)); NULL })
}
balanced <- function(y, sub, t0 = 5) {                          # 2012Q1 = t 5; hotels observed every quarter, untreated at t0
  sub <- sub[sub$t >= t0, ]
  nq <- length(unique(sub$t))
  ok <- tapply(!is.na(sub[[y]]), sub$hotel_id, sum) == nq
  untreated0 <- tapply(sub$treat[sub$t == t0], sub$hotel_id[sub$t == t0], max) == 0
  keep <- names(ok)[ok & untreated0[names(ok)]]
  sub[sub$hotel_id %in% keep, ]
}
run_gsynth <- function(y, sub) {
  sub <- balanced(y, sub)
  f <- as.formula(paste(y, "~ treat + log_comphotels + log_reviews_lag"))
  tryCatch(
    gsynth(f, data = sub, index = c("hotel_id", "t"), force = "two-way", CV = TRUE, r = c(0, 5),
           se = TRUE, inference = "parametric", nboots = 200, parallel = TRUE, cores = 4, seed = 2022),
    error = function(e) { message("gsynth failed: ", conditionMessage(e)); NULL })
}
grab <- function(o, label) {
  if (is.null(o)) return(data.frame(model = label, ATT = NA, SE = NA, p = NA, r = NA, treated = NA, controls = NA))
  ea <- o$est.avg
  data.frame(model = label, ATT = o$att.avg, SE = ea[1, "S.E."], p = ea[1, "p.value"], r = o$r.cv,
             treated = o$Ntr, controls = o$Nco)
}
specs <- list(c("selfpromo", "all"), c("selfpromo", "high"), c("selfpromo", "low"),
              c("demoting_others", "all"), c("demoting_others", "high"), c("demoting_others", "low"))
rows <- list(); fits <- list()
for (s in specs) {
  y <- s[1]; sub <- if (s[2] == "all") d else if (s[2] == "high") d[d$lowend == 0, ] else d[d$lowend == 1, ]
  lab <- paste(ifelse(y == "selfpromo", "Promote", "Demote"), s[2])
  cat("\n==== ", lab, " ====\n")
  fi <- run_fect(y, sub); fits[[paste(lab, "fect")]] <- fi
  rows[[length(rows) + 1]] <- grab(fi, paste(lab, "| GSC (fect, full panel)"))
  gi <- run_gsynth(y, sub)
  rows[[length(rows) + 1]] <- grab(gi, paste(lab, "| gsynth (balanced 2012Q1 on)"))
}
t7 <- do.call(rbind, rows)
t7[, c("ATT", "SE", "p")] <- round(t7[, c("ATT", "SE", "p")], 3)
print(t7, row.names = FALSE)
write.csv(t7, "results/table7_gsynth_R.csv", row.names = FALSE)
sink("results/table7_gsynth_R.txt")
cat("Table 7 (Texas). Generalized synthetic control (Xu 2017), binary Airbnb treatment, 200 bootstraps\n")
print(t7, row.names = FALSE)
sink()
if (!is.null(fits[["Promote all fect"]])) {
  png("results/stata/fig_table7_gsynth.png", width = 2400, height = 1500, res = 300)
  print(plot(fits[["Promote all fect"]], main = "Self-promotion, treated vs counterfactual (GSC)"))
  dev.off()
}
cat("\nWritten: results/table7_gsynth_R.csv, results/table7_gsynth_R.txt, results/stata/fig_table7_gsynth.png\n")
