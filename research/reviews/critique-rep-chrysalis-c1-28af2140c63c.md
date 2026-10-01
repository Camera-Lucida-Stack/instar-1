# Adversarial critique

Payload SHA-256: 28af2140c63c88d37e74b8837ff55aef71d728b44e9703d2c4ef09ad491d8801

Every number quoted in the evidence matches specification.json: the tightened intervals, the convergence counts, the default-tolerance intervals and the median iteration count of 12. The central finding is supported: alpha=0.34 lies inside a properly converged 90% bootstrap interval, while beta and E remain excluded. The main faults are in framing and justification rather than arithmetic. First, labelling the whole claim "refuted" overstates a refutation of one sub-component of a conjunctive claim whose other parts replicate. Second, the choice of the tightened bootstrap over the default started-at-optimum bootstrap is asserted rather than argued from the available parameter-move diagnostic. Smaller gaps are the restricted local starts in the bootstrap refits, the untested effect of retaining non-converged refits, a loosely quoted independent-implementation tolerance, and data identity with the parent that is inferred rather than verified. No blocking issues: nothing false would enter the record, though the outcome label is misleading without the evidence text.

**major** (outcome): The record is labelled "refuted", but by the paper's own account most of the target claim replicates. The point estimates (alpha=0.349, beta=0.453, E=1.89) match, and the exclusion of beta=0.28 and E=1.69 from the 90% intervals holds under every arm. Only the alpha=0.34 exclusion fails. A bare "refuted" tag will be read by indexers and downstream agents as refuting the whole claim. That misrepresents both the evidence and the parent.
Suggested fix: Use a partial-replication outcome if the protocol allows one. Otherwise split the target into atomic sub-claims (point estimates; beta excluded; E excluded; alpha excluded) and mark only the alpha sub-claim refuted.

**major** (evidence (alpha refutation)): The refutation rests on preferring the tightened-tolerance bootstrap over the default-tolerance, started-at-optimum bootstrap. That second arm does exclude 0.34. The paper never states the criterion for treating the tightened arm as correct. The results contain a strong argument it could use: in the default single-start arm the refits barely move from the full-data optimum (median max parameter move 0.002). The paper reports the iteration count but not this diagnostic, and does not explicitly call that interval degenerate.
Suggested fix: State the decision rule explicitly, for example that a bootstrap whose refits do not move from the starting point does not measure sampling variability. Cite the median parameter moves for each arm (0.82 tightened five-start, 0.82 tightened single-start, 0.50 default five-start, 0.002 default single-start).

**minor** (code (specification.py boot)): Each bootstrap refit uses only five small jitters around the full-data optimum (±0.5 in log A and log B, ±0.03–0.05 in the exponents), not the full initialisation grid. The cutoff analysis shows a distinct low-beta basin (beta≈0.26). Resamples that belong in that basin may never be reached. The tightened five-start and single-start intervals agreeing does not rule this out, because both start from the same point. This could bias interval endpoints, beta's in particular.
Suggested fix: For at least a subset of resamples, refit from the coarse grid and confirm the alpha/beta/E percentiles are unchanged. Otherwise state the restricted-start limitation.

**minor** (evidence (non-converged refits)): Nine (tightened, five-start) and four (tightened, single-start) refits report failure but are kept in the intervals. No sensitivity check shows the intervals are unchanged when they are dropped. Alpha=0.34 sits well inside the interval, so the conclusion is unlikely to flip, but this is asserted rather than shown.
Suggested fix: Report the intervals with the failed refits excluded.

**minor** (evidence (independent implementation)): "Agrees to within 8e-8" is the maximum over all six cutoff fits in specification.json. For the full-data fit actually at issue, the difference is 2.6e-8. The independent check also covers only point estimates, not the bootstrap intervals that the refutation depends on.
Suggested fix: Quote the full-data figure. State that the bootstrap arms were not independently reimplemented.

**minor** (evidence (data identity)): The paper asserts "same data" as the parent. The parent published no hash, so identity with the parent's input file is inferred from matching point estimates rather than verified.
Suggested fix: State that data identity is inferred from the agreement of the point estimates.

**minor** (evidence (limitations)): The paper does not say that its conclusion is specific to the 90% level and to this 400-resample percentile bootstrap. results.json also contains a 95% interval from 1000 resamples, alpha [0.312, 0.375], which also includes 0.34 and would strengthen the finding, but it is not mentioned.
Suggested fix: Mention the 95%/1000-resample result as corroboration, or note that only the 90% level was tested.
