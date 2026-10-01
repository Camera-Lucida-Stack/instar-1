"""
Specification sensitivity and the replication of Chrysalis-1 (ecd:2609.qeh0ha).
Writes research/results/specification.json. Deterministic given the seed.

1. Compute cutoffs: refit on runs with C >= cutoff, for a fixed list of cutoffs.
2. Chrysalis-1 C1: 90% bootstrap intervals on all 245 points, 400 resamples, under
   (a) tightened and (b) SciPy default L-BFGS-B tolerances.
3. Specification spread versus sampling width for beta and a_opt.
"""
import json, sys
import numpy as np
sys.path.insert(0, "research/lib")
from chinchilla import *

SEED = 20261001
N, D, L, sha = load(); C = 6 * N * D
CUTOFFS = [0, 3e18, 1e19, 3e19, 1e20, 3e20]
spec = []
for c in CUTOFFS:
    m = C >= c
    if m.sum() < 30: continue
    f = natural(grid_fit(N[m], D[m], L[m], coarse=True).x)
    spec.append(dict(cutoff=c, n=int(m.sum()), **f))

def ci90(s, j): return [float(np.percentile(s[:, j], 5)), float(np.percentile(s[:, j], 95))]
p0 = grid_fit(N, D, L).x
chrys = {}
for label, opts in (("tightened", None), ("scipy_default", {})):
    s = bootstrap(N, D, L, p0, 400, SEED, opts=opts)
    chrys[label] = {k: ci90(s, j) for j, k in enumerate(KEYS)}
    chrys[label]["hoffmann_outside"] = {k: not (chrys[label][k][0] <= HOFFMANN[k] <= chrys[label][k][1])
                                        for k in ("alpha", "beta", "E")}
fit_all = natural(p0)
spread = {k: [min(r[k] for r in spec), max(r[k] for r in spec)] for k in ("alpha", "beta", "E", "a_opt")}
width = {k: chrys["tightened"][k][1] - chrys["tightened"][k][0] for k in ("beta", "a_opt")}
out = dict(data_sha256=sha, seed=SEED, cutoffs=spec, fit_all=fit_all,
           chrysalis_c1=dict(resamples=400, level=0.90, **chrys),
           spread=spread, sampling_width_90_tight=width,
           spread_to_width={k: (spread[k][1] - spread[k][0]) / width[k] for k in width})
json.dump(out, open("research/results/specification.json", "w"), indent=2)
print(json.dumps(dict(cutoffs=[(r["cutoff"], r["n"], round(r["alpha"],3), round(r["beta"],3), round(r["E"],2), round(r["a_opt"],3)) for r in spec],
      c1={k: {x: chrys[k][x] for x in ("alpha","beta","E","hoffmann_outside")} for k in chrys},
      spread=spread, width=width, ratio=out["spread_to_width"]), indent=1))
