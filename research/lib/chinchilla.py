"""Shared model, objective and fitting routines for the Chinchilla refit."""
import hashlib, itertools, sys
import numpy as np
import pandas as pd
from scipy.optimize import minimize

DATA = "research/data/svg_extracted_data.csv"
EXPECTED_SHA = "193478df4e90f040016431996c45682659306840ecdadf83cfb9cd5ca0aa1b30"
HOFFMANN = dict(A=406.4, B=410.7, E=1.69, alpha=0.34, beta=0.28)  # reported, Approach 3
TIGHT = dict(maxiter=20000, ftol=1e-15, gtol=1e-12)
KEYS = ["A", "B", "E", "alpha", "beta", "a_opt"]

def load():
    raw = open(DATA, "rb").read()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != EXPECTED_SHA:
        sys.exit(f"data file hash {sha} does not match the pinned extraction; refusing to fit")
    df = pd.read_csv(DATA)[["Model Size", "Training FLOP", "loss"]].dropna()
    N = df["Model Size"].to_numpy(); C = df["Training FLOP"].to_numpy(); L = df["loss"].to_numpy()
    return N, C / (6.0 * N), L, sha

def pred(p, N, D):
    a, b, e, al, be = p
    return np.logaddexp(np.logaddexp(a - al * np.log(N), b - be * np.log(D)), e)

def huber(r, d):
    ar = np.abs(r)
    return np.where(ar <= d, 0.5 * r * r, d * (ar - 0.5 * d))

def obj(p, N, D, L, d=1e-3):
    return float(np.sum(huber(np.log(L) - pred(p, N, D), d)))

def jac(p, N, D, L, d=1e-3):
    a, b, e, al, be = p
    lN, lD = np.log(N), np.log(D)
    u1, u2 = a - al * lN, b - be * lD
    m = np.maximum(np.maximum(u1, u2), e)
    t1, t2, t3 = np.exp(u1 - m), np.exp(u2 - m), np.exp(e - m)
    S = t1 + t2 + t3
    r = np.log(L) - (m + np.log(S))
    w = -np.where(np.abs(r) <= d, r, d * np.sign(r)) / S
    return np.array([np.sum(w * t1), np.sum(w * t2), np.sum(w * t3),
                     np.sum(-w * lN * t1), np.sum(-w * lD * t2)])

def fit_from(p0, N, D, L, d=1e-3, opts=None):
    return minimize(obj, p0, args=(N, D, L, d), jac=jac, method="L-BFGS-B",
                    options=TIGHT if opts is None else opts)

def grid_fit(N, D, L, d=1e-3, coarse=False):
    """Hoffmann-style grid of initialisations; coarse=True for repeated use."""
    g = (dict(al=[0, 0.5, 1], be=[0, 0.5, 1], e=[-1, 0, 1], a=[0, 10, 20], b=[0, 10, 20]) if coarse else
         dict(al=np.arange(0, 2.5, 0.5), be=np.arange(0, 2.5, 0.5), e=np.arange(-1, 1.5, 0.5),
              a=np.arange(0, 30, 5), b=np.arange(0, 30, 5)))
    best = None
    for al, be, e, a, b in itertools.product(g["al"], g["be"], g["e"], g["a"], g["b"]):
        r = fit_from([a, b, e, al, be], N, D, L, d)
        if np.all(np.isfinite(r.x)) and (best is None or r.fun < best.fun):
            best = r
    return best

def natural(p):
    a, b, e, al, be = p
    return dict(A=float(np.exp(a)), B=float(np.exp(b)), E=float(np.exp(e)),
                alpha=float(al), beta=float(be), a_opt=float(be / (al + be)))

def to_log(h):
    return [np.log(h["A"]), np.log(h["B"]), np.log(h["E"]), h["alpha"], h["beta"]]

def hoffmann_a_opt():
    return HOFFMANN["beta"] / (HOFFMANN["alpha"] + HOFFMANN["beta"])

def bootstrap(N, D, L, start, n, seed, d=1e-3, opts=None):
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        i = rng.integers(0, len(N), len(N))
        out.append(list(natural(fit_from(start, N[i], D[i], L[i], d, opts).x).values()))
    return np.array(out)

def ci95(samples):
    return {k: [float(np.percentile(samples[:, j], 2.5)), float(np.percentile(samples[:, j], 97.5))]
            for j, k in enumerate(KEYS)}
