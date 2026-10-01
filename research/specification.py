"""
Specification sensitivity and the replication of Chrysalis-1 (ecd:2609.qeh0ha).
Writes research/results/specification.json. Deterministic given the seed.

Every fit here meets the same standard as the main refit:
- full grid of initialisations at every compute cutoff, cross-checked against an
  independent implementation (scipy least_squares, natural-space parameters);
- bootstrap refits from several starts per resample, keeping the best, with
  convergence status and iteration counts recorded;
- 90% bootstrap intervals within each cutoff, so specification effects can be
  compared with sampling uncertainty cutoff by cutoff.
"""
import json, sys
import numpy as np
from scipy.optimize import least_squares
sys.path.insert(0, "research/lib")
from chinchilla import *

SEED = 20261001
MIN_N = 100                      # below this a cutoff subset is reported as poorly identified
N_all, D_all, L_all, sha = load(); C_all = 6 * N_all * D_all
JIT = np.array([[0, 0, 0, 0, 0], [0.5, 0.5, 0, 0.03, 0.03], [-0.5, -0.5, 0, -0.03, -0.03],
                [1.0, -1.0, 0.05, 0.05, -0.05], [-1.0, 1.0, -0.05, -0.05, 0.05]])

def independent(N, D, L):
    def r(q):
        A, B, E, al, be = q
        return np.log(L) - np.log(E + A / N**al + B / D**be)
    best = None
    for x0 in ([400, 400, 1.7, 0.3, 0.3], [1000, 5000, 1.8, 0.4, 0.4], [200, 1000, 1.5, 0.3, 0.35], [5e4, 500, 1.8, 0.6, 0.35]):
        s = least_squares(r, x0, loss="huber", f_scale=1e-3, method="trf",
                          bounds=([1e-6, 1e-6, 1e-6, 0, 0], [1e8, 1e9, 10, 3, 3]),
                          x_scale="jac", xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=20000)
        if best is None or s.cost < best.cost: best = s
    A, B, E, al, be = best.x
    return dict(alpha=float(al), beta=float(be), E=float(E), a_opt=float(be / (al + be)))

def boot(N, D, L, p0, n, seed, opts=None, multistart=True):
    rng = np.random.default_rng(seed)
    est, conv, nit, moved = [], 0, [], []
    starts = JIT if multistart else JIT[:1]
    for _ in range(n):
        i = rng.integers(0, len(N), len(N))
        rs = [fit_from(p0 + j, N[i], D[i], L[i], opts=opts) for j in starts]
        r = min(rs, key=lambda r: r.fun)
        est.append(list(natural(r.x).values())); conv += int(r.success); nit.append(int(r.nit))
        moved.append(float(np.max(np.abs(r.x - p0))))
    return np.array(est), dict(converged=conv, resamples=n, median_iterations=float(np.median(nit)),
                               median_max_parameter_move=float(np.median(moved)))

def ci90(s, j): return [float(np.percentile(s[:, j], 5)), float(np.percentile(s[:, j], 95))]

cutoffs = []
for c in [0, 3e18, 1e19, 3e19, 1e20, 3e20]:
    m = C_all >= c
    N, D, L = N_all[m], D_all[m], L_all[m]
    g = grid_fit(N, D, L)
    f = natural(g.x); ind = independent(N, D, L)
    s, diag = boot(N, D, L, g.x, 200, SEED)
    cutoffs.append(dict(cutoff=c, n=int(m.sum()), well_identified=bool(m.sum() >= MIN_N), **f,
                        independent=ind, max_abs_difference=max(abs(ind[k] - f[k]) for k in ind),
                        ci90={k: ci90(s, j) for j, k in enumerate(KEYS)}, bootstrap=diag))
    print(f"C>={c:.0e} n={m.sum()} beta={f['beta']:.3f} a={f['a_opt']:.3f} indep diff={cutoffs[-1]['max_abs_difference']:.1e} beta90={cutoffs[-1]['ci90']['beta']}", flush=True)

# Chrysalis-1 C1: all points, 400 resamples, 90% intervals
p0 = grid_fit(N_all, D_all, L_all).x
arms = {
    "tightened": boot(N_all, D_all, L_all, p0, 400, SEED),                                   # tightened, five starts
    "tightened_single": boot(N_all, D_all, L_all, p0, 400, SEED, multistart=False),          # tightened, start at optimum
    "scipy_default": boot(N_all, D_all, L_all, p0, 400, SEED, opts={}),                      # defaults, five starts
    "scipy_default_single": boot(N_all, D_all, L_all, p0, 400, SEED, opts={}, multistart=False),  # defaults, start at optimum
}
chrys = {}
for label, (s, d) in arms.items():
    chrys[label] = {k: ci90(s, j) for j, k in enumerate(KEYS)}
    chrys[label]["diagnostics"] = d
    chrys[label]["hoffmann_outside"] = {k: not (chrys[label][k][0] <= HOFFMANN[k] <= chrys[label][k][1]) for k in ("alpha", "beta", "E")}

def spread(rows, k): return [min(r[k] for r in rows), max(r[k] for r in rows)]
well = [r for r in cutoffs if r["well_identified"]]
full = cutoffs[0]; c19 = next(r for r in cutoffs if r["cutoff"] == 1e19)
w = lambda r, k: r["ci90"][k][1] - r["ci90"][k][0]
out = dict(data_sha256=sha, seed=SEED, min_n_well_identified=MIN_N, cutoffs=cutoffs, fit_all=natural(p0),
           chrysalis_c1=dict(resamples=400, level=0.90, **chrys),
           spread_all=spread(cutoffs, "a_opt"), spread_well={k: spread(well, k) for k in ("beta", "a_opt")},
           ratio_well={k: (spread(well, k)[1] - spread(well, k)[0]) / w(full, k) for k in ("beta", "a_opt")},
           beta_ci_overlap_full_vs_1e19=bool(not (full["ci90"]["beta"][1] < c19["ci90"]["beta"][0] or c19["ci90"]["beta"][1] < full["ci90"]["beta"][0])),
           a_ci_overlap_full_vs_1e19=bool(not (full["ci90"]["a_opt"][1] < c19["ci90"]["a_opt"][0] or c19["ci90"]["a_opt"][1] < full["ci90"]["a_opt"][0])),
           max_independent_difference=max(r["max_abs_difference"] for r in cutoffs))
json.dump(out, open("research/results/specification.json", "w"), indent=2)
print(json.dumps({k: out[k] for k in ("spread_all", "spread_well", "ratio_well", "beta_ci_overlap_full_vs_1e19", "a_ci_overlap_full_vs_1e19", "max_independent_difference")}))
for k in chrys: print(k, {x: chrys[k][x] for x in ("alpha", "beta", "E", "hoffmann_outside", "diagnostics")})
