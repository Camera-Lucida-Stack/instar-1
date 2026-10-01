# Adversarial critique

Payload SHA-256: 9606b1835f1c0b64e51b3ab39dbf79e6175a03c3540f20ccf3e37cc58b33d47d

Every number in C1–C5 matches the results files. The problems lie in attribution and inference rather than arithmetic. First, the paper implies that the parent's alpha exclusion came from premature L-BFGS-B termination, but nothing about the parent's settings is known. Second, the default-versus-tightened comparison confounds tolerance with the number of starts (one versus five), so the causal 'as a result' wording in C1 and C2 is not isolated. Third, the abstract's claim that the effect is 'more modest than unconverged intervals imply' has no supporting computation. Fourth, the validation checks were run on the 240-point trimmed set and target claims this paper does not make; one of them fails robustness. Fifth, C4's non-overlap argument ignores that the subsets are nested and rests on 200 resamples. Finally, C5's ratio of about 1 for beta sits uneasily with the abstract's 'more than sampling uncertainty'. These are mostly major wording and design gaps rather than false numbers. None is blocking if the parent attribution and the 'more modest' sentence are corrected.

**major** (abstract): The abstract says default-tolerance termination produces an interval 'enough to reverse an inclusion test reported in ecd:2609.qeh0ha'. Read with the title, this attributes the parent's result to premature termination. Nothing supplied shows that Chrysalis-1 used SciPy default tolerances, a single start, or started its bootstraps at the full-data optimum. The paper only shows that a default-tolerance procedure written here reproduces the parent's exclusion of alpha. Note also that, as specification.py runs it, the default arm differs from the tightened arm in both tolerances and number of starts.
Suggested fix: State that the parent's optimiser settings are unknown, and that a default-tolerance bootstrap reproduces its alpha exclusion. Do not assert that this was the cause unless the parent's code or settings are obtained.

**major** (C1): The comparison '12 iterations / 0.0020 against 68 and 0.82 with tightened tolerances' is confounded. The tightened arm uses five starts per resample (multistart=True); the default arm uses one (multistart=False). The differences cannot be credited to tolerances alone, yet the claim names only tolerances.
Suggested fix: Either rerun the default arm with the same five starts, or the tightened arm with one start, so that only tolerances differ. Otherwise state in the claim that the arms differ in both tolerance and number of starts.

**major** (C2): 'As a result' implies tolerances alone cause the change in the interval. The two intervals come from arms differing in both tolerance and start count (five starts versus one). The causal attribution is not isolated by the code.
Suggested fix: Report a tight-tolerance, single-start interval for alpha on the 245 runs at 90%, or reword to describe the joint change.

**major** (abstract): 'Finding the effect more modest than unconverged intervals imply' is not backed by any computation. Default-tolerance intervals were computed only on the full data, never per cutoff. No result compares a specification effect under unconverged intervals with one under converged intervals. C5 shows the beta spread is about one interval width (0.98), not a measured reduction from some unconverged baseline.
Suggested fix: Either compute default-tolerance per-cutoff intervals and report the comparison, or delete the sentence. Alternatively state concretely: the well-identified a_opt spread is 0.376–0.565 versus the parent's 0.35–0.56, and the beta spread is about one interval width.

**major** (abstract): The claim that 'the method is validated by parameter recovery ... and by sensitivity to assumed digitisation error' overreaches in three ways:
- Both checks in quality.json are run on the 240-point trimmed set, with a coarse grid for recovery, and test only point estimates.
- Neither check tests the per-cutoff bootstrap intervals or the non-overlap and spread claims (C4, C5) that the paper makes.
- The extraction-noise check targets 'beta exceeds reported' and 'a_opt exceeds reported', which are not claims of this paper; the a_opt version fails robustness (99/100).
Suggested fix: Restrict the validation statement to what was tested, report the a_opt non-robustness, and run the noise and recovery checks on the cutoff-subset intervals that underpin C4 and C5.

**major** (C4): Non-overlap of the two 90% percentile intervals is offered as showing that specification moves beta by more than sampling uncertainty. The two samples are nested: the 192 runs at C≥1e19 are a subset of the 245, so the bootstrap distributions are not independent and non-overlap is not a calibrated test. The change is also a change of data (dropping low-compute runs), not only of specification. Each interval rests on only 200 resamples, and those that did not converge (2–4 per cutoff) are retained.
Suggested fix: Use a paired bootstrap of the difference beta(full) − beta(C≥1e19) on common resamples and report its interval. Note the nesting, and state the 200-resample basis in the paper.

**minor** (C5): The ratio's numerator is a max−min spread across 5 nested subsets; its denominator is the width of a single 90% interval at one specification. The metric depends on how many cutoffs were chosen and on the grid spacing. Also, a beta ratio of 0.98 means the beta spread is comparable to sampling width. This sits uneasily with the abstract's statement that specification moves the estimates 'by more than sampling uncertainty'.
Suggested fix: State that the ratio depends on the chosen cutoff set. Qualify the abstract: for beta the cross-cutoff spread is about equal to the interval width; only a_opt exceeds it.

**minor** (C3): The claim of agreement is accurate (max 7.6e-8), but the abstract's 'All fits are cross-checked' overstates it. Only the grid point estimates are cross-checked; no bootstrap refit is. A and B are not compared at all.
Suggested fix: Say 'all point-estimate fits'. Optionally report A and B differences.

**minor** (abstract): The mechanism ('small gradients allow L-BFGS-B ... to stop almost at once') is asserted but not tested. No gradient norms or stopping messages are reported, and default tolerances are never run at delta=1e-2 to show the dependence on delta.
Suggested fix: Report the termination message and the projected-gradient norm at stopping. Show the default-tolerance behaviour at delta=1e-2.

**minor** (abstract): 'About 25 times too narrow' is ambiguous. results.json's width_ratio of 25.2 comes from the 240-point trimmed set with 95% intervals and 1000 resamples, single start in both arms. The C2 intervals are 245-point, 90%, 400 resamples, giving a ratio of about 25.3. The reader cannot tell which figure is meant.
Suggested fix: State which data set, interval level and resample count the factor of 25 refers to.

**minor** (code): The 'multi-start' consists of five small jitters (±0.5 in log A and log B, ±0.03 in exponents) around the full-data optimum p0. This is local exploration, not an independent multi-start. Bootstrap resamples with distant optima, especially at small cutoffs, may be under-explored, which could bias intervals narrow. The 'median_max_parameter_move' diagnostic is also measured from p0, not as a convergence criterion.
Suggested fix: Add widely separated starts (e.g. the coarse grid) for a subset of resamples and report whether the intervals change.

**minor** (builds_on): The relation to ecd:2609.qeh0ha is given as 'extends'. However, C2 contradicts that paper's C1 for alpha (alpha=0.34 inside versus outside the 90% interval). The 'replicates' relation to arxiv:2203.15556 is also loose, since the original runs are not refit.
Suggested fix: Mark the parent relation as partially refuting or contesting for C1. Reconsider the label for Hoffmann et al.

**minor** (limitations): The limitations omit three things: per-cutoff intervals rest on 200 resamples; nested subsets make between-cutoff comparisons dependent; and resamples that did not converge are included in the percentiles.
Suggested fix: Add these to the limitations.
