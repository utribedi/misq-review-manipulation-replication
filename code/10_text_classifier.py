"""
Extension: text-based manipulation measure.
  train : TF-IDF (word 1-2 grams) + logistic regression on the Ott et al. (2011/2013) deceptive-opinion corpus (1,600 labelled hotel reviews);
          5-fold CV accuracy reported. Model saved with joblib.
  score : stream reviews_<region>.jsonl, write hotel_id, date, rating, p_fake per review (resumable in chunks; call repeatedly until done)
  panel : aggregate to hotel-quarter (share of 5-star reviews flagged deceptive, share of 1-2-star flagged), merge into panel_<region>.csv,
          and estimate the paper's 2SLS specification with the text-based outcomes.
Usage: python3 10_text_classifier.py train <workdir> | score <region TX|EU> <workdir> [max_chunks] | panel <region> <workdir> <outdir>
"""
import sys, os, json, time, numpy as np, pandas as pd, joblib
mode, args = sys.argv[1], sys.argv[2:]
CHUNK = 50_000
if mode == "train":
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.model_selection import cross_val_score, StratifiedKFold
    WORK = args[0]
    d = pd.read_csv(os.path.join(WORK, "ott_deceptive_opinion.csv"))
    # Kaggle copy has mangled label columns; the design is encoded in `source`: MTurk = deceptive (800), TripAdvisor/Web = truthful (800)
    y = (d.source.astype(str).str.strip().eq("MTurk")).astype(int).values
    # drop corpus-specific place / brand tokens so the classifier learns style, not Chicago
    LEAK = ["chicago","michigan","illinois","hilton","hyatt","sheraton","omni","amalfi","talbott","conrad","fairmont","intercontinental","james","knickerbocker","monaco","palmer","allegro","affinia","ambassador","hardrock","hard","rock","homewood","sofitel","swissotel","millennium","navy","pier","magnificent","mile","loop"]
    pipe = make_pipeline(TfidfVectorizer(ngram_range=(1,2), min_df=2, sublinear_tf=True, max_features=200_000, stop_words=LEAK), LogisticRegression(C=3.0, max_iter=2000))
    cv = cross_val_score(pipe, d.text, y, cv=StratifiedKFold(5, shuffle=True, random_state=1), scoring="accuracy")
    print(f"Ott corpus: {len(d)} reviews, {y.mean():.0%} deceptive; 5-fold CV accuracy {cv.mean():.3f} (sd {cv.std():.3f}); paper benchmark (Ott et al. 2011): ~0.89")
    pipe.fit(d.text, y); joblib.dump(pipe, os.path.join(WORK, "fake_review_model.joblib"))
    coef = pipe.named_steps["logisticregression"].coef_[0]; vocab = np.array(pipe.named_steps["tfidfvectorizer"].get_feature_names_out())
    top = np.argsort(coef); print("most deceptive n-grams:", ", ".join(vocab[top[-15:]][::-1])); print("most truthful n-grams:", ", ".join(vocab[top[:15]]))
    open(os.path.join(WORK, "classifier_cv.txt"), "w").write(f"5-fold CV accuracy {cv.mean():.3f} (sd {cv.std():.3f}); n={len(d)}\n")
elif mode == "score":
    region, WORK = args[0], args[1]; max_chunks = int(args[2]) if len(args) > 2 else 10**9
    pipe = joblib.load(os.path.join(WORK, "fake_review_model.joblib"))
    src, outf, stf = os.path.join(WORK, f"reviews_{region}.jsonl"), os.path.join(WORK, f"scores_{region}.csv"), os.path.join(WORK, f"scores_{region}.state")
    st = json.load(open(stf)) if os.path.exists(stf) else {"offset": 0, "n": 0, "done": False}
    if st["done"]: print("already done"); sys.exit()
    out = open(outf, "a" if st["offset"] > 0 else "w")
    if st["offset"] == 0: out.write("hotel_id,date,rating,p_fake\n")
    t0 = time.time(); chunks = 0
    with open(src, "rb") as f:
        f.seek(st["offset"])
        while chunks < max_chunks:
            rows = []
            for _ in range(CHUNK):
                line = f.readline()
                if not line: st["done"] = True; break
                d = json.loads(line); rows.append((d["hotel_id"], d["date"], d["rating"], ((d.get("title") or "") + ". " + (d.get("text") or ""))[:5000]))
            if rows:
                p = pipe.predict_proba([r[3] for r in rows])[:, 1]
                out.writelines(f"{r[0]},{r[1]},{r[2]},{pf:.4f}\n" for r, pf in zip(rows, p)); st["n"] += len(rows)
            st["offset"] = f.tell(); chunks += 1
            if st["done"] or time.time() - t0 > 140: break
    out.close(); json.dump(st, open(stf, "w"))
    print(f"{region}: scored {st['n']:,} reviews so far, done={st['done']}, {time.time()-t0:.0f}s")
elif mode == "panel":
    from replib import prep, fit, models, table_md, RATIOS
    region, WORK, OUT = args[0], args[1], args[2]
    s = pd.read_csv(os.path.join(WORK, f"scores_{region}.csv")); s["q"] = pd.to_datetime(s.date, errors="coerce").dt.to_period("Q").astype(str)
    s["fake"] = s.p_fake > 0.5
    g = s.groupby(["hotel_id","q"])
    agg = pd.DataFrame({"fake5": g.apply(lambda d: (d.fake & (d.rating == 5)).sum(), include_groups=False),
                        "fake12": g.apply(lambda d: (d.fake & (d.rating <= 2)).sum(), include_groups=False),
                        "pfake_mean": g.p_fake.mean()}).reset_index().rename(columns={"q": "yq"})
    p = pd.read_csv(os.path.join(WORK, "panel_tx.csv" if region == "TX" else "panel_eu.csv")).merge(agg, on=["hotel_id","yq"], how="left")
    has = p.n_ta.fillna(0) > 0
    p["share_fake5"] = np.where(has, p.fake5.fillna(0) / p.n_ta, np.nan); p["share_fake12"] = np.where(has, p.fake12.fillna(0) / p.n_ta, np.nan)
    p.loc[~has, "pfake_mean"] = np.nan
    p = prep(p); has = p.n_ta.fillna(0) > 0   # recompute the mask after prep() re-sorts rows
    p.to_csv(os.path.join(OUT, f"panel_{region}_text.csv"), index=False)
    md = [f"# Text-based manipulation measure ({region})\n", f"- Reviews scored: {len(s):,}; share flagged deceptive (p>0.5): {s.fake.mean():.1%}; among 5-star {s[s.rating==5].fake.mean():.1%}; among 1-2-star {s[s.rating<=2].fake.mean():.1%}",
          f"- Hotel-quarter correlation of share_fake5 with the panel's self-promotion measure: {p[has][['share_fake5','selfpromo']].corr().iloc[0,1]:.2f}; with one-time 5-star share: {p[has][['share_fake5', 'share5_onetime' if 'share5_onetime' in p else 'selfpromo']].corr().iloc[0,1]:.2f}"]
    has_low = p.drop_duplicates("hotel_id").lowend.sum() >= 5
    for y, lab in [("share_fake5","Share of reviews that are 5-star and flagged deceptive"), ("share_fake12","Share of reviews that are 1-2-star and flagged deceptive"), ("pfake_mean","Mean deceptive probability")]:
        res = {}
        for name, extra in models(has_low):
            for kind, iv in [("2SLS", True), ("OLS", False)]:
                try: res[f"{name} {kind}"] = fit(p[has], y, extra, iv=iv)[1]
                except Exception as e: res[f"{name} {kind}"] = {"Observations": f"failed: {e}"}
        md.append(table_md(f"{lab} on Airbnb supply ({region})", res, "*p<0.05, **p<0.01, ***p<0.001; SEs clustered by hotel. Hotel FE, quarter FE, city x season FE."))
    open(os.path.join(OUT, f"text_measure_{region}.md"), "w").write("\n".join(md)); print("\n".join(md))
