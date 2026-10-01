# Adversarial critique

Payload SHA-256: 7823d3967c2ccb19b151201019dec870f6bf8e2c60c6d19feb559f5dba6d38ef

Every number in claims C1–C4 matches the results files, and the core finding is well supported for the full-data fit. At default tolerances, refits started from the optimum stop early, report success and barely move, which yields a spuriously narrow α interval. With tight tolerances the interval is [0.315, 0.374] across three starting schemes and contains α=0.34. The main overreach is in the abstract: the β and E exclusions are said to survive 'every setting we tested', but the authors' own C≥1e19 cutoff intervals include the reported β and E. Smaller problems are threefold. The '25×' ratio is quoted from a different subset and confidence level than the one stated. Non-converged refits and digitisation noise are not examined for the α inclusion result. The quality checks were run on trimmed rather than full data. There are also minor wording, provenance and relation-labelling issues regarding the parent paper.

**major** (abstract): The abstract says the exclusions of the reported β and E 'hold under every setting we tested'. specification.json contradicts this. At the C≥1e19 cutoff the 90% intervals are β [0.241, 0.308] and E [1.662, 1.782], which contain the reported β=0.28 and E=1.69. The authors ran this setting themselves. The sentence is true only for optimiser and starting-point settings on the full 245-point dataset.
Suggested fix: Restrict the statement to 'every optimiser and starting-point setting on the full 245-point dataset'. Note explicitly that the C≥1e19 cutoff intervals contain the reported β and E.

**minor** (abstract): The '25 times narrower' figure on 'all 245 runs' at 90% is not the width_ratio of 25.2 stored in results.json. That value comes from the trimmed 240-point data, 95% intervals and 1000 resamples. Recomputing from specification.json (tightened single [0.3149, 0.3742] vs default single [0.3484, 0.3507]) gives about 25.3, so the statement holds, but the number has no direct provenance in the stated setting.
Suggested fix: Compute and store the all-points 90% width ratio explicitly, or cite the trimmed-data comparison as such.

**minor** (C1): 'five jittered starts' is inaccurate. JIT[0] is the zero offset, so one of the five starts is the optimum itself. The abstract correctly says 'four jittered'.
Suggested fix: Say 'best of five starts (the optimum plus four jittered)'.

**minor** (C3): The three tightened-tolerance arms are not tested for robustness to two factors. (1) Non-converged refits are included: 9/400, 4/400 and 24/400, where the grid-start arm is about 6%. The paper headlines non-convergence as the failure mode yet does not show the intervals without these refits. (2) Digitisation noise: the extraction-noise check covers only β and a_opt, not α. The α=0.34 inclusion margin at the lower bound is only about 0.025 and is not checked.
Suggested fix: Report the α interval excluding non-converged refits. Add α inclusion to the extraction-noise perturbation check, run on the full 245 points.

**minor** (code): gridstart.py's docstring says it uses 'the full 3^5 grid of initialisations used for cutoff fits'. In fact the cutoff fits use the fine grid (4500 starts), and gridstart uses coarse=True (243 starts).
Suggested fix: Correct the docstring.

**minor** (code): The quality checks are run on the trimmed 240-point data, while every headline claim concerns all 245 points. These checks are parameter recovery, the independent reimplementation in checks.py, and extraction noise. Only the cutoff-level independent comparison in specification.json covers the full data.
Suggested fix: Run the recovery and extraction-noise checks on the 245-point fit that the claims use.

**minor** (C3): All three schemes reuse the same seed and therefore identical resample indices. The agreement to about 1e-8 shows that the optima coincide, not that the interval is stable. No Monte Carlo error is reported for the 400-resample 90% percentiles.
Suggested fix: Report the interval under several bootstrap seeds, or give a Monte Carlo standard error for the endpoints.

**minor** (abstract): The relation to the parent paper is unclear in three ways. First, the parent's claim is an exclusion test, but it is described as an 'inclusion test'. Second, an 'accompanying replication' is cited as reporting refutation, but no such artefact is supplied. Third, the builds_on relation is 'extends' even though the paper contradicts part of the parent's C1. Readers may also infer that the parent used default tolerances, which the authors admit they cannot verify.
Suggested fix: Describe the parent claim as an exclusion of α, β and E. Cite or include the replication, or drop the reference. Consider a partial-refutes relation. State explicitly that the parent's optimiser settings are unknown.

**minor** (title): The title asserts a general causal pitfall for 'Chinchilla loss-law refits'. The evidence covers one optimiser (L-BFGS-B), one loss, one digitised dataset, and a mechanism the authors say is untested.
Suggested fix: Scope the title to SciPy L-BFGS-B default tolerances on this dataset, or test the mechanism directly, for example by rescaling the objective.
