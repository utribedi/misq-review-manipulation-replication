"""
Resumable streaming filter over HotelRec.txt (~50 GB JSON lines of TripAdvisor reviews).
Keeps reviews for  (a) all Texas hotels -> region TX   (b) London/Paris/Amsterdam/Barcelona/Milan/Vienna -> region EU6
Outputs in data_extract/:  reviews_<region>.csv (no text, Stata-ready), reviews_<region>.jsonl (with text), hotels_<region>.csv
Usage: python3 01_filter_hotelrec.py [seconds_budget]   -- re-run until state.json says done=true
"""
import json, re, csv, sys, time, os
HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(HERE, "..", "Full_HotelRec", "HotelRec.txt")
OUT  = os.path.join(HERE, "..", "data_extract"); os.makedirs(OUT, exist_ok=True)
STATE = os.path.join(OUT, "state.json")
BUDGET = float(sys.argv[1]) if len(sys.argv) > 1 else 140

EU6_GEO = {b"g186338", b"g187147", b"g188590", b"g187497", b"g187849", b"g190454"}
EU6_LOC = re.compile(rb"^(London_England|Paris_Ile_de_France|Amsterdam_North_Holland|Barcelona_Catalonia|Milan_Lombardy|Vienna)")
url_re  = re.compile(rb'"hotel_url": "Hotel_Review-(g\d+)-(d\d+)-Reviews-(.+?)-([^-"]+)\.html"')
quick   = re.compile(rb'_Texas\.html"|g186338-|g187147-|g188590-|g187497-|g187849-|g190454-')
SUB = ["service", "cleanliness", "value", "location", "sleep quality", "rooms"]
cols = ["hotel_id","geo_id","hotel_slug","loc_slug","region","author","date","rating"] + ["sr_"+s.replace(" ","_") for s in SUB]

st = json.load(open(STATE)) if os.path.exists(STATE) else {"offset": 0, "lines": 0, "kept": 0, "hotels": {}, "done": False, "calls": 0}
if st["done"]: print("already done"); sys.exit()
fresh = st["offset"] == 0
# if a previous call was interrupted after appending rows but before saving state, roll outputs back
for fn, sz in st.get("sizes", {}).items():
    fp = os.path.join(OUT, fn)
    if os.path.exists(fp) and os.path.getsize(fp) > sz:
        with open(fp, "r+b") as tf: tf.truncate(sz)
fh, jh, cw = {}, {}, {}
for r in ("TX", "EU6"):
    fh[r] = open(os.path.join(OUT, f"reviews_{r}.csv"), "w" if fresh else "a", newline="", encoding="utf-8")
    cw[r] = csv.writer(fh[r])
    if fresh: cw[r].writerow(cols)
    jh[r] = open(os.path.join(OUT, f"reviews_{r}.jsonl"), "w" if fresh else "a", encoding="utf-8")
hotels = st["hotels"]; t0 = time.time(); n = 0
size = os.path.getsize(SRC)
with open(SRC, "rb") as f:
    f.seek(st["offset"])
    while True:
        line = f.readline()
        if not line: st["done"] = True; break
        n += 1
        if n % 20000 == 0 and time.time() - t0 > BUDGET: break
        if not quick.search(line[:400]): continue
        m = url_re.search(line[:400])
        if not m: continue
        geo, hid, hslug, loc = m.groups()
        region = "TX" if loc.endswith(b"_Texas") else ("EU6" if (geo in EU6_GEO or EU6_LOC.match(loc)) else None)
        if region is None: continue
        try: d = json.loads(line)
        except Exception: continue
        pdict = d.get("property_dict") or {}
        hid_s, geo_s, hslug_s, loc_s = hid.decode(), geo.decode(), hslug.decode("utf-8","replace"), loc.decode("utf-8","replace")
        dt = (d.get("date") or "")[:10]
        cw[region].writerow([hid_s, geo_s, hslug_s, loc_s, region, d.get("author"), dt, d.get("rating")] + [pdict.get(k) for k in SUB])
        jh[region].write(json.dumps({"hotel_id": hid_s, "region": region, "author": d.get("author"), "date": dt,
                                     "rating": d.get("rating"), "title": d.get("title"), "text": d.get("text")}, ensure_ascii=False) + "\n")
        key = region + "|" + hid_s
        h = hotels.get(key)
        if h is None: h = hotels[key] = {"geo": geo_s, "slug": hslug_s, "loc": loc_s, "n": 0, "first": "9999", "last": "0000"}
        h["n"] += 1
        if dt: h["first"] = min(h["first"], dt); h["last"] = max(h["last"], dt)
        st["kept"] += 1
    st["offset"] = f.tell()
for r in ("TX", "EU6"): fh[r].close(); jh[r].close()
st["lines"] += n; st["calls"] += 1
st["sizes"] = {fn: os.path.getsize(os.path.join(OUT, fn)) for fn in ["reviews_TX.csv","reviews_TX.jsonl","reviews_EU6.csv","reviews_EU6.jsonl"]}
if st["done"]:
    for r in ("TX", "EU6"):
        with open(os.path.join(OUT, f"hotels_{r}.csv"), "w", newline="", encoding="utf-8") as hf:
            w = csv.writer(hf); w.writerow(["hotel_id","geo_id","hotel_slug","loc_slug","n_reviews","first_review","last_review"])
            for key, h in sorted(hotels.items()):
                if key.startswith(r + "|"): w.writerow([key.split("|")[1], h["geo"], h["slug"], h["loc"], h["n"], h["first"], h["last"]])
json.dump(st, open(STATE, "w"))
print(f"call {st['calls']}: +{n:,} lines in {time.time()-t0:.0f}s | total {st['lines']:,} lines, {st['offset']/1e9:.2f}/{size/1e9:.1f} GB ({100*st['offset']/size:.1f}%), kept {st['kept']:,} reviews, {len(hotels):,} hotels, done={st['done']}")
