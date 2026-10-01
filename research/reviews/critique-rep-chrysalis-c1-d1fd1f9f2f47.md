# Adversarial critique

Payload SHA-256: d1fd1f9f2f472edfae367c411b0acc4d6eea7f83e55328b30b2d7dfcd56fe6c6

The numbers in the evidence match specification.json: point estimates, all four arms' intervals, convergence counts and iteration medians. The core finding is well supported, because alpha=0.34 lies about 0.5 bootstrap SE from the point estimate, inside every tightened interval. The weaknesses are in the argument and the labelling. First, the reasons offered for trusting the tightened arm are partly invalid. The independent implementation validates only the shared point estimate, not any arm's intervals. Second, both 'starting schemes' are anchored at the full-data optimum, so their agreement is weak evidence of global convergence. The bootstrap refits also do not use the init grid the paper implies. Third, the bare 'refuted' outcome overstates the disagreement, given that every other component of C1 is confirmed. Smaller issues are a cross-cutoff maximum quoted as the full-data agreement figure, no sensitivity check on unconverged refits, quality checks run on a different subset, and an unpinned artefact.

**major** (evidence (justification for preferring the tightened arm)): One reason given for treating the tightened arm as correct is that 'its point estimate agrees with an independent least-squares implementation'. In specification.py all four arms bootstrap around the same full-data point estimate, p0 = grid_fit(...). The independent check (max difference 2.6e-8 on the full data) therefore validates the point fit only. It says nothing about which bootstrap arm gives correct intervals, so it cannot tell the arms apart.
Suggested fix: Drop this argument. Alternatively, validate the intervals directly. Options: compare each arm's bootstrap refits against least_squares refits of the same resamples, or report the objective gap between each arm's refits and a full grid refit on a subset of resamples.

**major** (evidence / code (specification.py boot, JIT)): Neither 'starting scheme' is independent of the full-data optimum. The 'five starts' are small fixed jitters around p0: ±0.5 or ±1 in log A and log B, and ±0.05 or less in log E, alpha and beta. The 'single' scheme is p0 itself. Agreement between two schemes anchored at the same point is weak evidence that the refits reach the resample's global optimum. The paper says it used the 'same grid of initialisations', but that holds only for the point fit, not the bootstrap refits.
Suggested fix: Re-run at least a subsample of resamples (e.g. 50–100) with the full or coarse grid_fit. Report whether the alpha interval changes. State explicitly that the bootstrap refits used local starts, not the grid.

**major** (outcome): The outcome is labelled 'refuted', yet the evidence states that the point estimates and the beta and E exclusions all replicate. Only the alpha conjunct fails. A conjunctive claim with one false component is technically false. Still, a bare 'refuted' label on the record misrepresents how much of C1 holds, and readers or aggregators may read it as the refit failing.
Suggested fix: Use a partial or mixed outcome if the protocol allows one. Otherwise state in the first sentence that C1 is refuted solely because alpha=0.34 falls inside the interval, while every other part of C1 is confirmed.

**minor** (evidence ('agrees to within 8e-8')): 7.6e-8 is the maximum independent-implementation difference across all six compute cutoffs, taken from the 1e20 cutoff. For the 245-point fit actually under replication, the difference is 2.6e-8. The figure quoted is not the one for the stated dataset.
Suggested fix: Quote the full-data difference (2.6e-8), or say the 8e-8 is a maximum across cutoffs.

**minor** (evidence (convergence)): Unconverged refits are kept in the intervals: 9 of 400 under one scheme and 4 of 400 under the other. No sensitivity analysis excluding them is reported. The impact is probably small, but it is asserted rather than shown.
Suggested fix: Report the alpha, beta and E intervals with unconverged refits excluded.

**minor** (evidence / quality checks): quality.json (parameter recovery, independent check, extraction noise) was run on the trimmed 240-point dataset, not the 245-point dataset C1 concerns. No extraction-noise robustness is reported for the alpha-inside, beta-outside or E-outside conclusions on the full data.
Suggested fix: Run the extraction-noise and recovery checks on the full 245-point data for alpha, beta and E. Otherwise state that they were not done for this replication.

**minor** (evidence (parent explanation)): The paper speculates that the parent used a default-tolerance bootstrap started at the optimum. That arm gives a nearly degenerate E interval of [1.882, 1.901] and an alpha width of about 0.002. The paper does not check whether the parent's stated results are quantitatively consistent with such an arm, beyond the exclusion pattern.
Suggested fix: Keep the hedge. Also note that this explanation is one of several, for example a different resampling scheme or interval method.

**minor** (artefacts): The artefact link is a repository URL with no commit hash or tag, so the cited code may change after publication.
Suggested fix: Pin a commit hash.
