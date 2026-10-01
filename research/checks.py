"""
Standard quality checks, run after refit.py. Writes research/results/quality.json.
The composer refuses to build a paper unless every check passes.

1. Parameter recovery: synthetic data from the fitted parameters, with the fit's
   own residuals resampled as noise; the full method must recover the truth.
2. Independent re-implementation: a different optimiser and parameterisation
   (scipy least_squares, natural-space parameters) must agree with the main fit.
3. Extraction-noise sensitivity: perturb N, C and loss by assumed digitisation
   error, and record per claim whether each conclusion survives every
   perturbation. Claims that do not survive are weakened by the composer.
"""
import json, sys
import numpy as np
from scipy.optimize import least_squares
sys.path.insert(0, "research/lib")
from chinchilla import *

SEED = 7
R = json.load(open("research/results/results.json"))
N_all, D_all, L_all, sha = load()
assert sha == R["data_sha256"], "results were computed on different data"
trim = L_all < np.sort(L_all)[-5]
N, D, L = N_all[trim], D_all[trim], L_all[trim]
main = next(r for r in R["runs"] if r["label"].startswith("excluding"))
p_true = np.array(main["fit_log"])
rng = np.random.default_rng(SEED)
checks = {}

# 1. Parameter recovery
resid = np.log(L) - pred(p_true, N, D)
est = []
for _ in range(50):
    Ls = np.exp(pred(p_true, N, D) + rng.choice(resid, len(resid), replace=True))
    est.append(list(natural(grid_fit(N, D, Ls, coarse=True).x).values()))
est = np.array(est); truth = natural(p_true)
rec = {}
for j, k in enumerate(KEYS):
    if k in ("alpha", "beta", "a_opt"):
        lo, hi = np.percentile(est[:, j], [2.5, 97.5])
        rec[k] = dict(truth=truth[k], mean=float(est[:, j].mean()), bias=float(est[:, j].mean() - truth[k]),
                      central95=[float(lo), float(hi)], truth_inside=bool(lo <= truth[k] <= hi))
checks["parameter_recovery"] = dict(
    datasets=50, detail=rec,
    passed=all(v["truth_inside"] and abs(v["bias"]) < 0.01 for v in rec.values()))

# 2. Independent re-implementation
def resid_nat(q):
    A, Bc, E, al, be = q
    return np.log(L) - np.log(E + A / N**al + Bc / D**be)
best = None
for x0 in ([400, 400, 1.7, 0.3, 0.3], [1000, 5000, 1.8, 0.4, 0.4], [200, 1000, 1.5, 0.3, 0.35]):
    r = least_squares(resid_nat, x0, loss="huber", f_scale=1e-3, method="trf",
                      bounds=([1e-6, 1e-6, 1e-6, 0, 0], [1e7, 1e8, 10, 3, 3]),
                      x_scale="jac", xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=20000)
    if best is None or r.cost < best.cost:
        best = r
A, Bc, E, al, be = best.x
alt = dict(alpha=float(al), beta=float(be), a_opt=float(be / (al + be)), E=float(E))
diff = {k: abs(alt[k] - main["fit"][k]) for k in alt}
checks["independent_reimplementation"] = dict(
    method="scipy least_squares (trust-region reflective), Huber f_scale=1e-3, natural-space parameters",
    estimates=alt, abs_difference=diff, tolerance=0.005, passed=all(v < 0.005 for v in diff.values()))

# 3. Extraction-noise sensitivity (assumed digitisation error, stated in the paper)
SIG = dict(log_N=0.02, log_C=0.02, rel_loss=0.005)
ha = hoffmann_a_opt(); hb = HOFFMANN["beta"]
se_b, se_a = main["bootstrap_se"]["beta"], main["bootstrap_se"]["a_opt"]
pert = []
for _ in range(100):
    Np = N * np.exp(rng.normal(0, SIG["log_N"], len(N)))
    Cp = (6 * N * D) * np.exp(rng.normal(0, SIG["log_C"], len(N)))
    Lp = L * (1 + rng.normal(0, SIG["rel_loss"], len(N)))
    Dp = Cp / (6 * Np)
    r = min((fit_from(p0, Np, Dp, Lp) for p0 in (p_true, p_true + [0.5, 0.5, 0, 0.03, 0.03],
             p_true - [0.5, 0.5, 0, 0.03, 0.03])), key=lambda r: r.fun)
    pert.append(natural(r.x))
b = np.array([p["beta"] for p in pert]); a = np.array([p["a_opt"] for p in pert])
hold_b = int((b - 1.96 * se_b > hb).sum()); hold_a = int((a - 1.96 * se_a > ha).sum())
checks["extraction_noise"] = dict(
    assumed_error=SIG, perturbations=len(pert),
    rule="a conclusion is robust if, in every perturbation, estimate minus 1.96 bootstrap SE exceeds the reported value",
    per_claim={
        "beta_exceeds_reported": dict(reported=hb, range=[float(b.min()), float(b.max())],
                                      holds_in=hold_b, robust=hold_b == len(pert)),
        "a_opt_exceeds_reported": dict(reported=ha, range=[float(a.min()), float(a.max())],
                                       holds_in=hold_a, robust=hold_a == len(pert)),
    },
    # Robustness is reported per claim; the composer weakens any claim that is
    # not robust. The check itself fails only if it could not be run.
    passed=True)

out = dict(data_sha256=sha, results_seed=R["seed"], seed=SEED, checks=checks,
           all_passed=all(c["passed"] for c in checks.values()))
json.dump(out, open("research/results/quality.json", "w"), indent=2)
print(json.dumps({k: v["passed"] for k, v in checks.items()}), "ALL PASSED" if out["all_passed"] else "FAILED")
