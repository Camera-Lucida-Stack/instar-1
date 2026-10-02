"""
Fetch US consumer price index for all urban consumers (CPI-U, series CUUR0000SA0,
not seasonally adjusted) from the Bureau of Labor Statistics public API, and
write annual averages to research/crowdfunding/results/cpi.csv, as the
pre-registration requires for the inflation-adjusted thresholds.

The annual average is the mean of the year's monthly values, which is how BLS
computes its published annual average. A year with fewer than 12 months
available is marked partial.
"""
import csv, json, urllib.request
from datetime import date

def fetch(a, b):
    req = urllib.request.Request("https://api.bls.gov/publicAPI/v1/timeseries/data/",
        data=json.dumps({"seriesid": ["CUUR0000SA0"], "startyear": str(a), "endyear": str(b)}).encode(),
        headers={"Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=60))
    if r.get("status") != "REQUEST_SUCCEEDED": raise SystemExit(f"BLS request failed: {r.get('message')}")
    return r["Results"]["series"][0]["data"]

rows = fetch(2009, 2018) + fetch(2019, 2026)
by_year = {}
for x in rows:
    if x["period"].startswith("M") and x["period"] != "M13" and x["value"] not in ("-", ""):  # BLS marks months not collected with a dash
        by_year.setdefault(int(x["year"]), []).append(float(x["value"]))
with open("research/crowdfunding/results/cpi.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["year", "cpi", "months", "partial", "source", "retrieved"])
    for y in sorted(by_year):
        v = by_year[y]
        w.writerow([y, round(sum(v) / len(v), 3), len(v), len(v) < 12, "BLS CUUR0000SA0", date.today().isoformat()])
print("CPI-OK", {y: len(v) for y, v in sorted(by_year.items())})
