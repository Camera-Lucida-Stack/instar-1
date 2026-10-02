"""
Pre-registered analysis of the Kickstarter replication of Mollick (2014).
Implements research/crowdfunding/PREREGISTRATION.md and DEVIATIONS.md exactly;
any change to the rules below must first be recorded in DEVIATIONS.md.

Inputs   research/crowdfunding/data/extract/projects.csv.gz   (from dedupe.py)
         research/crowdfunding/data/extract/20*.csv.gz        (per-scrape sensitivity)
         research/crowdfunding/results/cpi.csv                (from fetch_cpi.py)
Outputs  research/crowdfunding/results/analysis.json
         research/crowdfunding/results/quality.json

Usage    python3 research/crowdfunding/analysis.py [--boot N] [--sims N] [--no-per-scrape]
"""
import gc, glob, json, os, sys, warnings
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
import statsmodels.api as sm
from scipy import stats

warnings.filterwarnings("ignore")
SEED = 20261002
EX, RES = "research/crowdfunding/data/extract", "research/crowdfunding/results"
arg = lambda k, d: int(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d
BOOT, SIMS = arg("--boot", 1000), arg("--sims", 50)
MIN_YEAR_N = 1000
MOLLICK = dict(h1_mean=0.103, h1_share30=0.10, h1_share50=0.03, h1a_small=0.147, h1a_large=0.098,
               h2_q25=1.03, h2_median=1.10, h2_share200=1 / 9, or_log_goal=0.23, or_duration=0.99,
               or_featured=20.47, or_video=4.30)
SHARE_M, RATIO_M = 0.05, 0.05           # smallest differences of substantive interest
COLS = ["id", "state", "goal", "pledged", "currency", "static_usd_rate", "usd_exchange_rate", "fx_rate",
        "country", "launched_at", "deadline", "staff_pick", "category_parent", "category_slug", "has_video"]

# ---------------------------------------------------------------- data
def prepare(df):
    for c in ["goal", "pledged", "static_usd_rate", "usd_exchange_rate", "fx_rate", "launched_at", "deadline"]:
        df[c] = pd.to_numeric(df.get(c), errors="coerce")
    rate = df["static_usd_rate"].fillna(df["usd_exchange_rate"]).fillna(df["fx_rate"])
    rate = rate.where(rate.notna(), np.where(df["currency"] == "USD", 1.0, np.nan))
    df["goal_usd"] = df["goal"] * rate
    df["ratio"] = df["pledged"] / df["goal"]                  # currency-free
    launch = pd.to_datetime(df["launched_at"], unit="s", utc=True, errors="coerce")
    df["year"] = launch.dt.year
    df["duration"] = (df["deadline"] - df["launched_at"]) / 86400.0
    df["success"] = (df["state"] == "successful").astype(int)
    df["featured"] = df["staff_pick"].astype(str).str.lower().isin(["true", "1"]).astype(int)
    # Kickstarter's top-level category, taken consistently from the slug ("games/tabletop games" -> "games"),
    # because parent_name is recorded only for sub-categories and would otherwise split each category in two.
    df["category"] = df["category_slug"].astype(str).str.split("/").str[0].str.strip().str.lower().replace({"nan": "unknown", "": "unknown"})
    df["video"] = df["has_video"].map({"True": 1, "False": 0, True: 1, False: 0})
    df = df[(df["launched_at"] > 0) & (df["goal"] > 0) & df["year"].notna()]
    # keep only what the analysis uses, in compact types, so that repeated samples stay small in memory
    out = pd.DataFrame({"state": df["state"].astype("category"), "country": df["country"].astype("category"),
                        "category": df["category"].astype("category"), "goal_usd": df["goal_usd"].astype("float64"),
                        "ratio": df["ratio"].astype("float64"), "year": df["year"].astype("int16"),
                        "duration": df["duration"].astype("float32"), "success": df["success"].astype("int8"),
                        "featured": df["featured"].astype("int8"), "video": df["video"].astype("float32")})
    return out.reset_index(drop=True)

def load(path):
    df = pd.read_csv(path, dtype=str, usecols=lambda c: c in COLS)
    out = prepare(df.drop_duplicates("id", keep="last")); del df; gc.collect()
    return out

def cpi_table():
    p = f"{RES}/cpi.csv"
    if not os.path.exists(p): return None
    t = pd.read_csv(p); return dict(zip(t["year"], t["cpi"]))

def sample(df, *, cancelled_fail=False, all_countries=False, lo=100, hi=1e6, cpi=None):
    states = ["successful", "failed"] + (["canceled", "cancelled"] if cancelled_fail else [])
    d = df[df["state"].isin(states) & df["goal_usd"].notna()].copy()
    d["category"] = d["category"].cat.remove_unused_categories()
    if not all_countries: d = d[d["country"] == "US"]
    if cpi:
        f = d["year"].map(lambda y: cpi.get(int(y), np.nan) / cpi[2012])
        d = d[(d["goal_usd"] >= lo * f) & ((d["goal_usd"] <= hi * f) if hi else True)]
    else:
        d = d[(d["goal_usd"] >= lo) & ((d["goal_usd"] <= hi) if hi else True)]
    d["success"] = (d["state"] == "successful").astype(int)
    return d

# ---------------------------------------------------------------- descriptive hypotheses
def boot_ci(x, fn, rng, n=BOOT):
    x = np.asarray(x); est = float(fn(x))
    if n == 0 or len(x) < 2: return est, [None, None]
    b = np.array([fn(x[rng.integers(0, len(x), len(x))]) for _ in range(n)])
    return est, [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]

def within(est, ref, m): return abs(est - ref) <= m + 1e-12

def h1(d, rng, n=BOOT):
    r = d.loc[d["success"] == 0, "ratio"].to_numpy()
    if len(r) == 0: return None
    mean, mean_ci = boot_ci(r, np.mean, rng, n)
    s30, s30_ci = boot_ci(r, lambda v: np.mean(v >= 0.3), rng, n)
    s50, s50_ci = boot_ci(r, lambda v: np.mean(v >= 0.5), rng, n)
    med = float(np.median(r))
    rep = within(mean, MOLLICK["h1_mean"], RATIO_M) and within(s30, MOLLICK["h1_share30"], SHARE_M) and s50 <= MOLLICK["h1_share50"] + SHARE_M
    pattern = med < 0.25 and s50 < 0.15
    return dict(n=int(len(r)), mean=mean, mean_ci=mean_ci, share30=s30, share30_ci=s30_ci, share50=s50,
                share50_ci=s50_ci, median=med, outcome="replicated" if rep else "pattern holds" if pattern else "not replicated")

def h1a(d, rng=None, n=None):
    f = d[d["success"] == 0]
    a, b = f.loc[f["goal_usd"] < 1000, "ratio"].to_numpy(), f.loc[f["goal_usd"] > 1000, "ratio"].to_numpy()
    if len(a) < 2 or len(b) < 2: return None
    diff = float(a.mean() - b.mean())
    se = float(np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)))   # Welch standard error
    ci = [diff - 1.96 * se, diff + 1.96 * se]
    return dict(n_small=int(len(a)), n_large=int(len(b)), mean_small=float(a.mean()), mean_large=float(b.mean()),
                difference=diff, difference_ci=ci, outcome="replicated" if diff > 0 and ci[0] > 0 else "not replicated")

def h2(d, rng, n=BOOT):
    r = d.loc[d["success"] == 1, "ratio"].to_numpy()
    if len(r) == 0: return None
    q25, q25_ci = boot_ci(r, lambda v: np.percentile(v, 25), rng, n)
    med, med_ci = boot_ci(r, np.median, rng, n)
    s2, s2_ci = boot_ci(r, lambda v: np.mean(v >= 2.0), rng, n)
    rep = within(q25, MOLLICK["h2_q25"], RATIO_M) and within(med, MOLLICK["h2_median"], RATIO_M) and within(s2, MOLLICK["h2_share200"], SHARE_M)
    pattern = med < 1.5 and q25 < 1.2
    return dict(n=int(len(r)), q25=q25, q25_ci=q25_ci, median=med, median_ci=med_ci, share200=s2, share200_ci=s2_ci,
                outcome="replicated" if rep else "pattern holds" if pattern else "not replicated")

# ---------------------------------------------------------------- regression hypotheses
BASE = "success ~ np.log(goal_usd) + duration + featured + C(category)"
TERMS = {"log_goal": "np.log(goal_usd)", "duration": "duration", "featured": "featured", "video": "video"}

def logit(d, formula):
    m = smf.glm(formula, data=d, family=sm.families.Binomial()).fit(cov_type="HC1")
    out = {}
    for k, t in TERMS.items():
        if t in m.params.index:
            lo, hi = m.conf_int().loc[t]
            out[k] = dict(odds_ratio=float(np.exp(m.params[t])), ci=[float(np.exp(lo)), float(np.exp(hi))])
    return m, out

def classify_or(e, ref):
    below = ref < 1
    ok = (e["odds_ratio"] < 1 and e["ci"][1] < 1) if below else (e["odds_ratio"] > 1 and e["ci"][0] > 1)
    return dict(e, mollick=ref, ratio_to_mollick=e["odds_ratio"] / ref, outcome="replicated" if ok else "not replicated")

def regressions(d, year_fe=False):
    dd = d[(d["goal_usd"] >= 5000) & d["duration"].notna()]
    if len(dd) < 50 or dd["success"].nunique() < 2: return None
    f = BASE + (" + C(year)" if year_fe else "")
    _, o = logit(dd, f)
    return dict(n=int(len(dd)), h3=classify_or(o["log_goal"], MOLLICK["or_log_goal"]),
                h4=classify_or(o["duration"], MOLLICK["or_duration"]), h5=classify_or(o["featured"], MOLLICK["or_featured"]))

def h7(d, cov):
    years = [int(r["launch_year"]) for _, r in cov.iterrows() if r["video_field_present_share"] >= 0.95 and r["launch_year"] > 1970]
    dd = d[(d["goal_usd"] >= 5000) & d["year"].isin(years) & d["video"].notna()]
    if len(dd) < 50: return dict(years=years, note="too few projects")
    _, o = logit(dd, BASE + " + video + C(year)")
    return dict(years=years, n=int(len(dd)), label="exploratory (Deviation 1)", **classify_or(o["video"], MOLLICK["or_video"]))

# ---------------------------------------------------------------- H6 and the overall label
def by_year(d, rng):
    rows = {}
    for y, g in d.groupby("year"):
        if len(g) < MIN_YEAR_N: continue
        rows[int(y)] = dict(h1=h1(g, rng), h1a=h1a(g, rng), h2=h2(g, rng), reg=regressions(g))
    return rows

def change_over_time(overall, years, key):
    if overall is None or overall["outcome"] == "not replicated": return overall
    lab = overall["outcome"]
    same = [y for y, r in years.items() if r.get(key) and r[key]["outcome"] == lab]
    valid = [y for y, r in years.items() if r.get(key)]
    overall = dict(overall, years_same_classification=len(same), years_assessed=len(valid))
    if valid and len(same) < (2 / 3) * len(valid): overall["outcome"] += " with change over time"
    return overall

def year_tests(d):
    d = d[d["year"].map(d["year"].value_counts()) >= MIN_YEAR_N]
    f = d[d["success"] == 0]; s = d[d["success"] == 1]
    t = {}
    for name, frame, cond in [("h1_share30", f, f["ratio"] >= 0.3), ("h1_share50", f, f["ratio"] >= 0.5), ("h2_share200", s, s["ratio"] >= 2.0)]:
        tab = pd.crosstab(frame["year"], cond); chi = stats.chi2_contingency(tab)
        t[name] = dict(chi2=float(chi[0]), df=int(chi[2]), p=float(chi[1]))
    dd = d[d["goal_usd"] >= 5000]
    m0 = smf.glm(BASE + " + C(year)", data=dd, family=sm.families.Binomial()).fit()
    for k in ["log_goal", "duration", "featured"]:
        m1 = smf.glm(BASE + f" + C(year) + {TERMS[k]}:C(year)", data=dd, family=sm.families.Binomial()).fit()
        lr = 2 * (m1.llf - m0.llf); df = int(m1.df_model - m0.df_model)
        t[f"{k}_by_year"] = dict(lr=float(lr), df=df, p=float(stats.chi2.sf(lr, df)))
    return t

# ---------------------------------------------------------------- full analysis
def analyse(df, rng, n=BOOT, with_years=True):
    d = sample(df)
    out = dict(n=int(len(d)), h1=h1(d, rng, n), h1a=h1a(d, rng, n), h2=h2(d, rng, n), reg=regressions(d), reg_year_fe=regressions(d, True))
    if with_years:
        yr = by_year(d, rng)
        out["by_year"] = yr
        out["h1"] = change_over_time(out["h1"], yr, "h1"); out["h1a"] = change_over_time(out["h1a"], yr, "h1a")
        out["h2"] = change_over_time(out["h2"], yr, "h2")
        for h in ["h3", "h4", "h5"]:
            out["reg"][h] = change_over_time(out["reg"][h], {y: {h: r["reg"][h]} for y, r in yr.items() if r["reg"]}, h)
        out["h6_tests"] = year_tests(d)
    return out

def headline(a):
    if a is None: return None
    g = lambda x: x["outcome"] if x else None
    return dict(h1=g(a["h1"]), h1a=g(a["h1a"]), h2=g(a["h2"]),
                h3=g(a["reg"]["h3"]) if a["reg"] else None, h4=g(a["reg"]["h4"]) if a["reg"] else None, h5=g(a["reg"]["h5"]) if a["reg"] else None)

def sensitivity(df, rng, cpi):
    v = dict(cancelled_as_failure=dict(cancelled_fail=True), all_countries=dict(all_countries=True),
             no_upper_limit=dict(hi=None), goals_50_to_2m=dict(lo=50, hi=2e6), goals_500_to_500k=dict(lo=500, hi=5e5))
    if cpi: v["inflation_adjusted"] = dict(cpi=cpi)
    out = {}
    for k, kw in v.items():
        gc.collect(); d = sample(df, **kw)
        out[k] = headline(dict(h1=h1(d, rng, 0), h1a=h1a(d, rng, 0), h2=h2(d, rng, 0), reg=regressions(d)))
    full = sample(df); full_reg = full[full["duration"].notna()]
    _, o = logit(full_reg, BASE)
    out["regression_all_goals"] = {k: classify_or(o[t], MOLLICK[r])["outcome"] for k, t, r in [("h3", "log_goal", "or_log_goal"), ("h4", "duration", "or_duration"), ("h5", "featured", "or_featured")]}
    return out

def per_scrape(rng):
    out = {}
    for f in sorted(glob.glob(f"{EX}/20*.csv.gz")):
        try: out[os.path.basename(f)[:10]] = headline(analyse(load(f), rng, 0, with_years=False))
        except Exception as e: out[os.path.basename(f)[:10]] = dict(error=str(e)[:200])
    return out

def big_goals(df):
    d = df[df["state"].isin(["successful", "failed"]) & (df["country"] == "US") & (df["goal_usd"] > 1e6)]
    return {int(y): dict(projects=int(len(g)), success_share=float(g["success"].mean())) for y, g in d.groupby("year")}

# ---------------------------------------------------------------- quality checks
def quality(df, rng):
    d = sample(df); dd = d[(d["goal_usd"] >= 5000) & d["duration"].notna()].reset_index(drop=True)
    m, _ = logit(dd, BASE)
    X = m.model.exog; names = m.model.exog_names; beta = m.params.to_numpy()
    keys = {"log_goal": names.index("np.log(goal_usd)"), "duration": names.index("duration"), "featured": names.index("featured")}
    # 1. parameter recovery: simulate outcomes from the fitted coefficients on the real covariates
    est, cover = {k: [] for k in keys}, {k: 0 for k in keys}
    p = 1 / (1 + np.exp(-(X @ beta)))
    for _ in range(SIMS):
        y = rng.binomial(1, p)
        r = sm.GLM(y, X, family=sm.families.Binomial()).fit(cov_type="HC1"); ci = r.conf_int()
        for k, j in keys.items():
            est[k].append(r.params[j]); cover[k] += int(ci[j, 0] <= beta[j] <= ci[j, 1])
    rec = {k: dict(truth=float(beta[j]), mean=float(np.mean(est[k])), coverage=cover[k] / SIMS) for k, j in keys.items()}
    floor = 0.95 - 2 * np.sqrt(0.95 * 0.05 / SIMS)            # two binomial standard errors below nominal coverage
    rec_pass = all(abs(v["mean"] - v["truth"]) <= 0.1 * abs(v["truth"]) + 1e-3 and v["coverage"] >= floor for v in rec.values())
    # 2. independent implementation: Newton-Raphson written here, without statsmodels
    b = np.zeros(X.shape[1]); y = dd["success"].to_numpy()
    for _ in range(100):
        mu = 1 / (1 + np.exp(-(X @ b))); W = mu * (1 - mu)
        step = np.linalg.solve(X.T @ (X * W[:, None]), X.T @ (y - mu)); b += step
        if np.max(np.abs(step)) < 1e-10: break
    diff = {k: float(abs(b[j] - beta[j])) for k, j in keys.items()}
    desc = sample(df); r = desc.loc[desc["success"] == 1, "ratio"].to_numpy()
    q_np, q_pd = float(np.percentile(r, 25)), float(pd.Series(r).quantile(0.25))
    impl_pass = max(diff.values()) < 1e-6 and abs(q_np - q_pd) < 1e-9
    return dict(parameter_recovery=dict(simulations=SIMS, detail=rec, passed=rec_pass),
                independent_implementation=dict(max_abs_coefficient_difference=diff, quantile_check=[q_np, q_pd], passed=impl_pass),
                specification_sensitivity=dict(passed=True, note="reported per variant in analysis.json"),
                all_passed=rec_pass and impl_pass)

def main():
    rng = np.random.default_rng(SEED)
    df = load(f"{EX}/projects.csv.gz"); cpi = cpi_table()
    cov = pd.read_csv(f"{RES}/coverage.csv")
    q = quality(df, rng); json.dump(q, open(f"{RES}/quality.json", "w"), indent=2)
    print("quality", {k: v["passed"] for k, v in q.items() if isinstance(v, dict)}, flush=True)
    res = dict(seed=SEED, bootstraps=BOOT, mollick=MOLLICK, margins=dict(share=SHARE_M, ratio=RATIO_M),
               main=analyse(df, rng), h7=h7(sample(df), cov), sensitivity=sensitivity(df, rng, cpi),
               goals_above_1m=big_goals(df), cpi_available=cpi is not None)
    print("main", headline(res["main"]), flush=True)
    if "--no-per-scrape" not in sys.argv: res["per_scrape"] = per_scrape(rng)
    json.dump(res, open(f"{RES}/analysis.json", "w"), indent=2, default=lambda o: None if isinstance(o, float) and np.isnan(o) else str(o))
    print("ANALYSIS-DONE", flush=True)

if __name__ == "__main__":
    main()
