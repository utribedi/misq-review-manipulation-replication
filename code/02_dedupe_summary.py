"""Remove exact-duplicate rows left by an interrupted filter pass, then print coverage summaries."""
import os, hashlib, pandas as pd
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data_extract")
def dedupe(fn):
    p = os.path.join(OUT, fn); tmp = p + ".tmp"; seen = set(); n = k = 0
    with open(p, "rb") as f, open(tmp, "wb") as g:
        for line in f:
            n += 1; h = hashlib.blake2b(line, digest_size=12).digest()
            if h in seen: continue
            seen.add(h); g.write(line); k += 1
    os.replace(tmp, p); print(f"{fn}: {n:,} -> {k:,} rows (removed {n-k:,})")
for fn in ["reviews_TX.csv", "reviews_EU6.csv", "reviews_TX.jsonl", "reviews_EU6.jsonl"]: dedupe(fn)
for r in ("TX", "EU6"):
    df = pd.read_csv(os.path.join(OUT, f"reviews_{r}.csv"), usecols=["hotel_id","loc_slug","author","date","rating"])
    df["year"] = df["date"].str[:4]
    print(f"\n=== {r}: {len(df):,} reviews, {df.hotel_id.nunique():,} hotels, {df.author.nunique():,} authors ===")
    print("reviews by year:"); print(df.year.value_counts().sort_index().to_string())
    print("rating dist:"); print(df.rating.value_counts(normalize=True).sort_index().round(3).to_string())
    top = df.groupby("loc_slug").agg(hotels=("hotel_id","nunique"), reviews=("hotel_id","size")).sort_values("hotels", ascending=False)
    print("top locations:"); print(top.head(25).to_string())
    # rebuild hotels file after dedupe
    h = df.groupby("hotel_id").agg(loc_slug=("loc_slug","first"), n_reviews=("rating","size"), first_review=("date","min"), last_review=("date","max"))
    h.to_csv(os.path.join(OUT, f"hotels_{r}.csv"))
