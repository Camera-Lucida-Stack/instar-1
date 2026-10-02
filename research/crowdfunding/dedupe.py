"""
Deduplicate the extracted scrapes and report coverage, as the pre-registration
requires, before any hypothesis is tested.

Each project is kept once, using its record from the latest scrape in which it
appears. Outputs:
  research/crowdfunding/data/extract/projects.csv.gz   one row per project (private)
  research/crowdfunding/results/coverage.csv           per launch year (committed)
  research/crowdfunding/results/coverage.json          summary (committed)

Coverage reports counts only. It deliberately excludes outcomes (success or
failure), which are first examined by the pre-registered analysis.
"""
import csv, glob, gzip, json, os, sys
from collections import defaultdict
from datetime import datetime, timezone

EX = "research/crowdfunding/data/extract"
RES = "research/crowdfunding/results"
csv.field_size_limit(sys.maxsize)
os.makedirs(RES, exist_ok=True)

files = sorted(glob.glob(f"{EX}/20*.csv.gz"))          # date-named, so oldest first
latest, first_seen, n_seen = {}, {}, defaultdict(int)
per_scrape_year = []                                    # (scrape date, {year: count})
fields = None
for k, f in enumerate(files):
    date = os.path.basename(f)[:10]
    counts = defaultdict(int)
    with gzip.open(f, "rt", newline="") as fh:
        r = csv.DictReader(fh); fields = fields or r.fieldnames
        seen_here = set()
        for row in r:
            pid = row.get("id")
            if not pid or pid in seen_here: continue    # duplicates within a scrape (sub-categories)
            seen_here.add(pid)
            latest[pid] = row; n_seen[pid] += 1; first_seen.setdefault(pid, date)
            try: counts[datetime.fromtimestamp(int(float(row["launched_at"])), timezone.utc).year] += 1
            except (KeyError, ValueError, TypeError): pass
    per_scrape_year.append((date, counts))
    print(f"{k+1}/{len(files)} {date}: {len(seen_here)} unique in scrape, {len(latest)} so far", flush=True)

out_fields = list(fields) + ["first_seen", "n_scrapes"]
year = defaultdict(lambda: dict(projects=0, terminal=0, video_field=0, video_yes=0, scrapes_mean=0.0))
with gzip.open(f"{EX}/projects.csv.gz", "wt", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=out_fields); w.writeheader()
    for pid, row in latest.items():
        row = dict(row, first_seen=first_seen[pid], n_scrapes=n_seen[pid]); w.writerow(row)
        try: y = datetime.fromtimestamp(int(float(row["launched_at"])), timezone.utc).year
        except (KeyError, ValueError, TypeError): continue
        Y = year[y]; Y["projects"] += 1; Y["scrapes_mean"] += n_seen[pid]
        if row.get("state") in ("successful", "failed"): Y["terminal"] += 1
        if row.get("has_video") not in (None, ""):
            Y["video_field"] += 1; Y["video_yes"] += row["has_video"] == "True"

best = defaultdict(int)                                 # largest count of a year's projects in any single scrape
for _, c in per_scrape_year:
    for y, n in c.items(): best[y] = max(best[y], n)
rows = []
for y in sorted(year):
    Y = year[y]; n = Y["projects"]
    rows.append(dict(launch_year=y, projects=n, terminal_projects=Y["terminal"],
                     mean_scrapes_per_project=round(Y["scrapes_mean"] / n, 2),
                     largest_single_scrape_share=round(best[y] / n, 3),
                     video_field_present_share=round(Y["video_field"] / n, 3),
                     video_yes_share_where_present=(round(Y["video_yes"] / Y["video_field"], 3) if Y["video_field"] else "")))
with open(f"{RES}/coverage.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
json.dump(dict(scrapes_processed=len(files), distinct_projects=len(latest),
               note="Counts only; outcomes are not examined here. largest_single_scrape_share is the largest number of a launch year's projects seen in any one scrape, divided by the distinct projects from that year found across all scrapes."),
          open(f"{RES}/coverage.json", "w"), indent=2)
print("DEDUPE-DONE", len(latest), flush=True)
for r in rows: print(r, flush=True)
