"""
Deviation 4: the live-capture test. Projects first seen in a scrape taken before
their campaign ended were collected before their outcome was known, so their
inclusion cannot depend on success. Re-estimating the findings on them tests
whether the overfunding trend reflects which projects remain visible.
Also records each project's staff-pick status at first sight (Deviation 4b).
Writes research/crowdfunding/results/live.json.
"""
import glob, importlib.util, json, sys
import numpy as np, pandas as pd

spec = importlib.util.spec_from_file_location("A", "research/crowdfunding/analysis.py")
argv = sys.argv; sys.argv = [argv[0]]; A = importlib.util.module_from_spec(spec); spec.loader.exec_module(A); sys.argv = argv
EX, RES = A.EX, A.RES
rng = np.random.default_rng(A.SEED + 4)
BOOT = int(sys.argv[sys.argv.index("--boot") + 1]) if "--boot" in sys.argv else 1000

raw = pd.read_csv(f"{EX}/projects.csv.gz", dtype=str, usecols=lambda c: c in A.COLS + ["first_seen"]).drop_duplicates("id", keep="last")
first_pick = {}
for f in sorted(glob.glob(f"{EX}/20*.csv.gz")):                      # oldest first: keep the first status seen
    x = pd.read_csv(f, dtype=str, usecols=["id", "staff_pick"]).drop_duplicates("id")
    new = x[~x["id"].isin(first_pick.keys())]
    first_pick.update(zip(new["id"], new["staff_pick"]))
raw["first_pick"] = raw["id"].map(first_pick)
d0 = raw.copy(); out = A.prepare(d0)
mask = (d0["launched_at"] > 0) & (d0["goal"] > 0) & d0["year"].notna()
seen = (pd.to_datetime(d0.loc[mask, "first_seen"], utc=True, errors="coerce") - pd.Timestamp(0, tz="UTC")) // pd.Timedelta(seconds=1)   # seconds since 1970, independent of the datetime unit
out["live"] = (seen.to_numpy() < d0.loc[mask, "deadline"].to_numpy()).astype(int)
out["featured_first"] = d0.loc[mask, "first_pick"].astype(str).str.lower().isin(["true", "1"]).astype("int8").to_numpy()

full = A.sample(out); live = full[full["live"] == 1]
assert full.loc[full["year"] <= 2013, "live"].sum() == 0, "no project launched before scraping began can have been captured live"
def h2s(g): r = g.loc[g["success"] == 1, "ratio"].to_numpy(); return (float(np.median(r)), float(np.mean(r >= 2))) if len(r) else (None, None)
def h1s(g): r = g.loc[g["success"] == 0, "ratio"].to_numpy(); return (float(np.mean(r)), float(np.mean(r >= 0.5))) if len(r) else (None, None)
years = {}
for y, g in full.groupby("year"):
    l = g[g["live"] == 1]
    years[int(y)] = dict(projects=int(len(g)), live=int(len(l)), live_share=float(len(l) / len(g)),
                         success_share_all=float(g["success"].mean()), success_share_live=(float(l["success"].mean()) if len(l) else None),
                         h2_median_all=h2s(g)[0], h2_share200_all=h2s(g)[1], h2_median_live=h2s(l)[0], h2_share200_live=h2s(l)[1],
                         h1_mean_live=h1s(l)[0], h1_share50_live=h1s(l)[1])

def period(lo, hi): s = live[(live["year"] >= lo) & (live["year"] <= hi) & (live["success"] == 1)]["ratio"].to_numpy(); return s
a, b = period(2014, 2016), period(2024, 2026)
def diff_ci(fn):
    est = fn(b) - fn(a)
    bs = [fn(b[rng.integers(0, len(b), len(b))]) - fn(a[rng.integers(0, len(a), len(a))]) for _ in range(BOOT)]
    return dict(estimate=float(est), ci=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))])
trend = dict(n_2014_2016=int(len(a)), n_2024_2026=int(len(b)),
             median_2014_2016=float(np.median(a)), median_2024_2026=float(np.median(b)),
             share200_2014_2016=float(np.mean(a >= 2)), share200_2024_2026=float(np.mean(b >= 2)),
             median_difference=diff_ci(np.median), share200_difference=diff_ci(lambda v: np.mean(v >= 2)))
md, sd = trend["median_difference"], trend["share200_difference"]
trend["supported"] = bool(md["estimate"] >= 0.05 and md["ci"][0] > 0 and sd["estimate"] >= 0.05 and sd["ci"][0] > 0)

regs = {}
for label, frame, feat in [("live_latest_pick", live, "featured"), ("live_first_pick", live, "featured_first"), ("all_first_pick", full, "featured_first")]:
    f = frame.copy(); f["featured"] = f[feat]
    regs[label] = A.regressions(f)
res = dict(rule="supported if, among live-captured successful projects, the median funding ratio and the share at 2x or more each rise by at least 0.05 from 2014-2016 to 2024-2026, with 95% bootstrap intervals excluding zero",
           live_projects=int(len(live)), trend=trend, by_year=years, regressions=regs)
json.dump(res, open(f"{RES}/live.json", "w"), indent=2, default=str)
print("LIVE-DONE", json.dumps(dict(trend=trend), default=str)[:900], flush=True)
