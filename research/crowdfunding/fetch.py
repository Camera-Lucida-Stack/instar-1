"""
Download, fingerprint and extract the Web Robots Kickstarter scrapes
(webrobots.io/kickstarter-datasets), as the pre-registration requires.

Each scrape is streamed to a temporary file, fingerprinted (SHA-256), reduced
to project-level fields, and deleted. Creator fields, names, blurbs, images and
URLs are never written to disk in extracted form. The run is resumable: scrapes
already listed in the manifest are skipped.

Outputs
  research/crowdfunding/data/MANIFEST.csv     scrape date, URL, bytes, SHA-256 (committed)
  research/crowdfunding/data/extract/*.csv.gz project-level rows per scrape (not committed)

Usage
  python3 research/crowdfunding/fetch.py --inspect      first record's field names only
  python3 research/crowdfunding/fetch.py [--limit N]    process scrapes, oldest first
"""
import csv, gzip, hashlib, io, json, os, re, sys, tempfile, time, urllib.request, zipfile

PAGE = "https://webrobots.io/kickstarter-datasets/"
OUT = "research/crowdfunding/data"
EXTRACT = f"{OUT}/extract"
MANIFEST = f"{OUT}/MANIFEST.csv"
KEEP = ["id", "state", "goal", "pledged", "usd_pledged", "converted_pledged_amount", "currency",
        "static_usd_rate", "usd_exchange_rate", "fx_rate", "country", "launched_at", "deadline",
        "created_at", "state_changed_at", "staff_pick", "spotlight", "backers_count",
        "category_id", "category_slug", "category_parent", "location_country", "location_state", "has_video"]

def get(url, tries=4):
    for k in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Instar-1 research (ecdysis.me)"}), timeout=120)
        except Exception as e:
            if k == tries - 1: raise
            time.sleep(10 * (k + 1))

def scrape_list():
    html = get(PAGE).read().decode("utf-8", "replace")
    urls = sorted(set(re.findall(r'https://s3\.amazonaws\.com/weruns/forfun/Kickstarter/Kickstarter_[^"\]\s]+?\.json\.(?:gz|zip)', html)))
    def date(u): return re.search(r"Kickstarter_(\d{4}-\d{2}-\d{2})", u).group(1)
    return sorted(((date(u), u) for u in urls), key=lambda x: x[0])

def records(path, url):
    """Yield project dicts from a scrape, in either of Web Robots' formats."""
    if url.endswith(".zip"):
        z = zipfile.ZipFile(path); raw = io.TextIOWrapper(z.open(z.namelist()[0]), encoding="utf-8")
    else:
        raw = io.TextIOWrapper(gzip.open(path), encoding="utf-8")
    first = raw.read(1); raw_rest = raw
    if first == "[":   # older scrapes: one JSON array of pages
        data = json.loads("[" + raw_rest.read())
        for item in data:
            for p in (item.get("projects") or item.get("data", {}).get("projects") or [item.get("data", item)]):
                if isinstance(p, dict): yield p
    else:              # from December 2015: one JSON object per line
        line = first + raw_rest.readline()
        while line:
            line = line.strip()
            if line:
                o = json.loads(line); p = o.get("data", o)
                if isinstance(p, dict): yield p
            line = raw_rest.readline()

def flatten(p):
    cat = p.get("category") or {}; loc = p.get("location") or {}
    row = {k: p.get(k) for k in KEEP if k in p}
    row.update(category_id=cat.get("id"), category_slug=cat.get("slug"),
               category_parent=(cat.get("parent_name") or (cat.get("slug") or "").split("/")[0] or None),
               location_country=loc.get("country"), location_state=loc.get("state"),
               has_video=(None if "video" not in p else bool(p.get("video"))))  # presence only; video URLs are not kept
    return row

def main():
    os.makedirs(EXTRACT, exist_ok=True)
    scrapes = scrape_list()
    print(f"{len(scrapes)} scrapes listed, {scrapes[0][0]} to {scrapes[-1][0]}", flush=True)
    if "--inspect" in sys.argv:
        date, url = scrapes[-1]
        with tempfile.NamedTemporaryFile(suffix=os.path.basename(url)) as tmp:
            r = get(url)
            while (b := r.read(1 << 20)): tmp.write(b)
            tmp.flush()
            p = next(records(tmp.name, url))
            print("top-level fields:", sorted(p.keys()))
            print("category fields:", sorted((p.get("category") or {}).keys()))
            print("location fields:", sorted((p.get("location") or {}).keys()))
        return
    done = set()
    if os.path.exists(MANIFEST):
        done = {r["date"] for r in csv.DictReader(open(MANIFEST))}
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    todo = [s for s in scrapes if s[0] not in done][:limit]
    new = not os.path.exists(MANIFEST)
    with open(MANIFEST, "a", newline="") as mf:
        w = csv.writer(mf)
        if new: w.writerow(["date", "url", "bytes", "sha256", "records"])
        for date, url in todo:
            t0 = time.time()
            with tempfile.NamedTemporaryFile(suffix=os.path.basename(url)) as tmp:
                h, n, r = hashlib.sha256(), 0, get(url)
                while (b := r.read(1 << 20)): tmp.write(b); h.update(b); n += len(b)
                tmp.flush()
                count = 0
                with gzip.open(f"{EXTRACT}/{date}.csv.gz", "wt", newline="") as out:
                    ww = csv.DictWriter(out, fieldnames=KEEP, extrasaction="ignore"); ww.writeheader()
                    for p in records(tmp.name, url):
                        ww.writerow(flatten(p)); count += 1
            w.writerow([date, url, n, h.hexdigest(), count]); mf.flush()
            print(f"{date}: {n/1e6:.0f} MB, {count} records, {time.time()-t0:.0f}s", flush=True)
    print("FETCH-DONE", flush=True)

if __name__ == "__main__":
    main()
