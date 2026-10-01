"""
Grid-start bootstrap for Chrysalis-1 C1 (ecd:2609.qeh0ha#C1).
Every bootstrap refit starts from the full 3^5 grid of initialisations used for
cutoff fits, independent of the full-data optimum, with tightened tolerances,
and keeps the best. Writes research/results/gridstart.json.
"""
import json, sys
import numpy as np
sys.path.insert(0, "research/lib")
from chinchilla import *

SEED = 20261001
B = int(sys.argv[1]) if len(sys.argv) > 1 else 400
N, D, L, sha = load()
p_full = grid_fit(N, D, L).x
rng = np.random.default_rng(SEED)
est, conv, far = [], 0, 0
for k in range(B):
    i = rng.integers(0, len(N), len(N))
    r = grid_fit(N[i], D[i], L[i], coarse=True)
    est.append(list(natural(r.x).values())); conv += int(r.success)
    far += int(np.max(np.abs(r.x - p_full)) > 1.0)
    if (k + 1) % 50 == 0: print(f"{k+1}/{B}", flush=True)
s = np.array(est)
ci = {k: [float(np.percentile(s[:, j], 5)), float(np.percentile(s[:, j], 95))] for j, k in enumerate(KEYS)}
out = dict(data_sha256=sha, seed=SEED, resamples=B, starts_per_resample=243, level=0.90, ci90=ci,
           converged=conv, optima_far_from_full_data=far,
           hoffmann_outside={k: not (ci[k][0] <= HOFFMANN[k] <= ci[k][1]) for k in ("alpha", "beta", "E")})
json.dump(out, open("research/results/gridstart.json", "w"), indent=2)
print(json.dumps({k: out[k] for k in ("ci90", "converged", "optima_far_from_full_data", "hoffmann_outside")}))
