"""
Independent refit of the Chinchilla parametric loss law (Hoffmann et al. 2022,
arXiv:2203.15556, Approach 3): L(N, D) = E + A / N^alpha + B / D^beta, on the
points Besiroglu et al. 2024 (arXiv:2404.10102) extracted from Figure 4.
Writes research/results/results.json. Deterministic given the seed.
"""
import json, sys
import numpy as np
sys.path.insert(0, "research/lib")
from chinchilla import *

SEED = 20261001
B = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
N_all, D_all, L_all, sha = load()

def run(mask, label, d=1e-3, opts=None):
    N, D, L = N_all[mask], D_all[mask], L_all[mask]
    best = grid_fit(N, D, L, d)
    s = bootstrap(N, D, L, best.x, B, SEED, d, opts)
    ci = ci95(s)
    hres = np.log(L) - pred(to_log(HOFFMANN), N, D)
    ref = {**HOFFMANN, "a_opt": hoffmann_a_opt()}
    return dict(label=label, n_points=int(mask.sum()), huber_delta=d, bootstraps=B,
                fit=natural(best.x), fit_log=[float(x) for x in best.x], ci95=ci,
                bootstrap_se={k: float(np.std(s[:, j], ddof=1)) for j, k in enumerate(KEYS)},
                objective_refit=best.fun, objective_hoffmann=obj(to_log(HOFFMANN), N, D, L, d),
                mean_residual_hoffmann=float(hres.mean()),
                hoffmann_inside_ci={k: bool(ci[k][0] <= v <= ci[k][1]) for k, v in ref.items()},
                half_inside_ci_a_opt=bool(ci["a_opt"][0] <= 0.5 <= ci["a_opt"][1]))

all_mask = np.ones(len(L_all), bool)
trim_mask = L_all < np.sort(L_all)[-5]   # drop 5 highest-loss points, as Besiroglu et al.
runs = [run(all_mask, "all points"), run(trim_mask, "excluding 5 highest-loss points"),
        run(all_mask, "all points, delta=1e-2", d=1e-2)]
loose = run(trim_mask, "tolerance check (SciPy defaults)", opts={})
w = lambda r: r["ci95"]["alpha"][1] - r["ci95"]["alpha"][0]
out = dict(seed=SEED, bootstraps=B, data_file=DATA, data_sha256=sha, hoffmann_reported=HOFFMANN,
           runs=runs, tolerance_check=dict(alpha_width_tight=w(runs[1]), alpha_width_default=w(loose),
                                           width_ratio=w(runs[1]) / w(loose)))
json.dump(out, open("research/results/results.json", "w"), indent=2)
print("results written")
