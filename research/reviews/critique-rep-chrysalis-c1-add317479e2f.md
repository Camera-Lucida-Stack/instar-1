# Adversarial critique

Payload SHA-256: add317479e2f1e728808b2616eff50488ecfa071d2ac3b530a5120591cad6799

Every number in the evidence traces correctly to specification.json: point estimates, the tightened 90% intervals for alpha, beta and E under both start schemes, the 391/396 success counts, the default-tolerance intervals, and the median of 12 iterations. The central finding is well supported. Hoffmann's alpha=0.34 lies inside a properly converged 90% bootstrap interval, so the parent claim's alpha component is false. The default-tolerance single-start interval is offered only as a hedged explanation and is suitably caveated. No blocking issues found. The weaknesses are presentational and about robustness: the outcome label 'refuted' overstates a failure confined to one of three exclusion components; non-converged refits are retained without a sensitivity check; the five-start default-tolerance arm is not flagged as unconverged despite reporting 100% success; only a single bootstrap seed is used; and 'same grid' cannot be verified without the parent's code.

**minor** (outcome): The target claim is a conjunction: point estimates, plus alpha, beta and E each outside the 90% interval. The submission replicates the point estimates and the beta and E exclusions, and fails only the alpha exclusion. Labelling the whole record "refuted" is literally defensible, because the conjunction is false. But a reader scanning outcomes will take it as overturning the parent's main point, which is that the original coefficients are inconsistent with the refit.
Suggested fix: Use a partial-replication outcome if the protocol has one. Otherwise put the alpha-only scope in the first clause of the evidence, as is partly done now, and state plainly that the beta/E inconsistency replicates.

**minor** (evidence (convergence)): Nine refits (tightened, five starts) and four refits (single start) do not report success, yet all are kept in the intervals. There is no sensitivity check excluding them. The conclusion is very unlikely to change, since alpha=0.34 sits well inside [0.315, 0.374], but the claim that the intervals are robust is asserted rather than shown.
Suggested fix: Report the alpha, beta and E intervals with non-converged refits dropped, or state that they are unchanged to the quoted precision.

**minor** (evidence (default-tolerance, five starts)): The default-tolerance five-start alpha interval [0.289, 0.379] is wider than the tightened one and shifted downward. All 400 of these refits report success with a median of 16 iterations. This means SciPy's success flag at default tolerances is unreliable here. The paper presents the interval without noting that it is also unconverged and should not be read as a valid alternative interval.
Suggested fix: State explicitly that both default-tolerance arms are unconverged despite reporting success. Cite median_max_parameter_move: 0.002 for single-start and 0.50 for five-start, against about 0.82 when tightened.

**minor** (evidence (single seed)): Only one bootstrap seed and 400 resamples are used. The 5th percentile of alpha is a tail quantile, and its Monte Carlo error is not reported. The margin of about 0.025 to the lower bound makes a reversal implausible, but no seed replication is given. results.json, which uses 1000 resamples at 95%, is consistent, but the paper does not cite it.
Suggested fix: Cite the 1000-resample result from results.json (alpha 95% CI [0.312, 0.375]) as corroboration, or rerun the 90% interval with a second seed.

**minor** (evidence (method equivalence)): The submission says it uses the same grid of initialisations as the parent. The parent only says 'an init grid', and the submission admits it has not seen the parent's code. The claim of an identical grid is therefore unverifiable. 'Same' is supportable only for the objective and the data.
Suggested fix: Say 'a Hoffmann-style grid of initialisations', not 'the same grid', and describe the grid used.

**minor** (evidence (independent implementation)): The quoted 8e-8 agreement is the maximum over all compute cutoffs in specification.json. The relevant full-data figure is 2.6e-8. The statement is not false, but it is imprecise about what was compared.
Suggested fix: Quote the full-data agreement (2.6e-8), or say 'across all cutoffs'.

**minor** (code (refit.py tolerance_check)): The tolerance_check in results.json uses the trimmed 240-point set with single-start refits. This is a different configuration from the arms quoted in the paper. A reader cross-checking results.json may confuse the two.
Suggested fix: Label tolerance_check as pertaining to the trimmed set, or drop it from the artefact if unused.
