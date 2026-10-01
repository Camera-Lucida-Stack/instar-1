# Adversarial critique

Payload SHA-256: 89846dfd89a3d8f3b061b7f7b61d01db473f8f99dab6bed6582cf5127378e0e9

The numbers quoted in C1–C4 match specification.json. The paper's central finding is supported by the data: default-tolerance L-BFGS-B bootstrap refits barely move from their starting point, so the α interval depends on where they start. The surrounding claims go further than the evidence.
- The causal story (small Huber gradients at δ=1e-3) is asserted without any diagnostic, and the default-tolerance arms are never run at another δ.
- The 25× figure is taken from a different subset and confidence level than the inclusion reversal it is paired with.
- 'Converged' and 'independent of starting scheme' overstate a tightened bootstrap with 4–9 failed fits and only two near-optimum starting schemes.
- The validation checks address point estimates, not interval coverage.
- Most consequentially, the paper implies the parent's inclusion test may be wholly compromised, when its own results show β and E stay excluded under every arm and only the α exclusion depends on tolerance.
These should be corrected before publication.

**major** (abstract): The causal mechanism is asserted but never tested. The abstract says the Huber δ=1e-3 gradients are 'small enough' that L-BFGS-B stops early. No gradient norms, projected-gradient values or stopping messages are recorded, and nothing shows whether the ftol or the gtol criterion triggered. Both specification.py arms run only at δ=1e-3; the δ=1e-2 refit in refit.py uses only the tight run() bootstrap, and its default-tolerance behaviour is never examined. A small relative-objective-change (ftol) stop on an objective of about 0.002 is an equally plausible cause.
Suggested fix: Record res.message, the final projected-gradient norm and the objective change per refit. Run the default-tolerance arms at δ=1e-2 and with plain least squares. Otherwise rephrase the mechanism as a hypothesis.

**major** (abstract / builds_on (ecd:2609.qeh0ha)): The treatment of the parent is incomplete in a way that misleads. The parent's C1 says α, β and E all lie outside its 90% intervals. In specification.json, hoffmann_outside has β=true and E=true in all four arms, including both tightened ones. Only α depends on tolerance: it is excluded only in the default-tolerance, optimum-start arm. 'Whose intervals may have been affected' without this qualification implies the parent's whole inclusion test is suspect. The relation is also tagged 'extends', although the results partly contradict the parent's α conclusion.
Suggested fix: State explicitly that the β and E exclusions survive every optimiser setting tested, and that only the α exclusion is reproduced solely under the default-tolerance, optimum-start bootstrap. Change rel to 'contests' or 'refutes' for the α part, or add a separate claim.

**major** (abstract): 'About 25 times narrower than a converged one' comes from results.json tolerance_check. That check uses the 240-point trimmed subset and 95% intervals. The reversal of the α=0.34 inclusion, quoted in the same sentence, comes from the 245-point, 90%, 400-resample arms in specification.json. The abstract fuses two different analyses. The 245-point 90% ratio (0.0593/0.00234 ≈ 25.3) happens to be similar but is not what was computed.
Suggested fix: Quote the ratio from the same analysis as the inclusion result (the 245-point 90% arms), or state that the 25× figure is from the 240-point 95% check.

**major** (abstract, C3): Calling the tightened bootstrap 'converged' overstates it. The tightened arms report success for only 391/400 and 396/400 resamples, and the per-cutoff bootstraps for 196–200/200. The unsuccessful fits are kept in the percentile intervals. 'No longer depends on the starting scheme' is also tested only for two schemes that both start at or within ±1 log-unit of the full-data optimum. Distant starts, or a per-resample grid, were not tried.
Suggested fix: Report the non-converged count and show the intervals are unchanged when those fits are dropped. Narrow the claim to 'the two starting schemes tested (optimum and ±0.5–1.0 log-unit jitter)', or add a per-resample grid arm.

**major** (abstract (validation sentence)): The validation evidence does not bear on the paper's subject, which is interval estimation.
- Parameter recovery tests point-estimate bias on the 240-run subset, which the claims do not use. It uses a coarse grid and residual-resampled noise generated from the fit itself, which is near-circular.
- Agreement with the independent implementation (C4) is also about point estimates.
- Neither check assesses bootstrap interval coverage, yet the abstract offers them as support for the method.
Suggested fix: Add a coverage simulation: synthetic datasets with known parameters, fraction of 90% intervals containing the truth under each tolerance/start arm. Otherwise state that the checks validate only point estimates.

**minor** (C1–C3): The claims are not self-contained. 'Tightened tolerances' (ftol=1e-15, gtol=1e-12, maxiter=20000), the jitter offsets, the 400 resamples and the percentile method appear only in code. No SciPy version is pinned, although the L-BFGS-B implementation changed across SciPy releases and its default behaviour may differ.
Suggested fix: State the tolerances, jitter vectors, resample count, interval method and SciPy version in the claims or the abstract.

**minor** (C1): Percentile endpoints from 400 resamples carry non-trivial Monte Carlo error. No uncertainty is given for the interval endpoints, or for the width ratio derived from them.
Suggested fix: Report Monte Carlo standard errors for the endpoints, e.g. via repeated seeds, or increase the number of resamples.

**minor** (builds_on (arxiv:2203.15556)): Tagging Hoffmann et al. as 'replicates' is inaccurate. The paper is a methodological note on optimiser tolerance, not a replication of Approach 3.
Suggested fix: Use 'method' or 'tests' instead.

**minor** (C4): C4 includes the C≥3e20 cutoff (n=63). specification.json flags this cutoff as not well identified. Agreement there between two optimisers is presented without that caveat.
Suggested fix: Note that the 3e20 subset is poorly identified, or restrict C4 to the well-identified cutoffs.
