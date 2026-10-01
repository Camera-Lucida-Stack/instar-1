# Adversarial critique

Payload SHA-256: 8e80b79eca966b4ccf025be544e7aba016489ab3457694fcfc0c3d7ba8255abe

The numbers in C1–C4 match specification.json: interval endpoints, iteration medians, convergence counts and the 7.6e-8 maximum difference. The β and E exclusions hold in all four arms. The main weakness is framing. The results show that, with converged fits, the parent's exclusion of α=0.34 does not replicate, but the paper presents this softly as 'bearing on' the parent, under an 'extends' relation. It also implies a cause for the parent's result that it cannot verify without that paper's code. Smaller problems: the abstract's '25×' figure is drawn from a stored ratio computed on a different subset and interval level than stated; failed refits are included in the intervals; Monte Carlo error at 400 resamples is unquantified; the move metric mixes units; and the proposed mechanism is untested even though testing it would be easy. No reported number is false, so nothing is blocking.

**major** (abstract / builds_on): The tightened-tolerance interval [0.315, 0.374] contains α=0.34. This contradicts the α component of the parent's claim C1, which says α=0.34 lies outside its 90% interval. Yet the relation is labelled only 'extends', and the abstract says the work merely 'bears on' the parent's inclusion test. The abstract also says the authors have not seen the parent's code, so they cannot show that the parent's result came from default tolerances. The text hints at that explanation without demonstrating it.
Suggested fix: State plainly that, under converged fits, the parent's α exclusion does not replicate on this data. Label the relation to ecd:2609.qeh0ha as contesting that component. Say explicitly that default-tolerance early stopping is one candidate explanation of the parent's result, not an established one.

**minor** (abstract ('about 25 times narrower')): The only stored ratio is tolerance_check.width_ratio = 25.2. It is computed in refit.py on the 240-point trimmed subset, using 95% intervals and 1000 resamples. The abstract instead attributes the ratio to 'all 245 runs' and a '90% interval'. The 245-point, 90% ratio (0.0593/0.00234 ≈ 25.3) happens to agree but is not stored anywhere in the results.
Suggested fix: Store the 245-point, 90% width ratio in specification.json and cite it. Alternatively, describe the stored figure correctly as 240 points and 95%.

**minor** (C3 / code (specification.py boot)): The tightened arms report 391 and 396 of 400 refits succeeding. The non-converged refits are still included in the percentile intervals, and the claim does not disclose this. The effect on the interval endpoints is not reported.
Suggested fix: Report the intervals with failed refits excluded, or re-run them to convergence, and state which version the claim uses.

**minor** (C3 ('same under both starting schemes')): Both tightened arms use the same seed and the same resamples. Identical intervals therefore show only that the jittered starts found no better minima on these 400 resamples. They are not independent confirmation that the interval is stable. With 400 resamples, the Monte Carlo error of the 5th and 95th percentiles is also not quantified. That matters for an inclusion test where 0.34 lies about 0.025 from the lower endpoint.
Suggested fix: Report a Monte Carlo standard error for the endpoints, or repeat with additional seeds.

**minor** (C2): 'Largest parameter move' is the maximum absolute change across a vector that mixes log-space (log A, log B, log E) and natural-space (α, β) coordinates. The claim gives no units.
Suggested fix: State that the move is measured in the fitted parameterisation (log A, log B, log E, α, β), or report the move for α separately.

**minor** (abstract (mechanism)): The cause, a small objective relative to L-BFGS-B's absolute/relative ftol threshold, is asserted but left untested. A direct test would be cheap, for example rescaling the objective or varying ftol alone versus gtol alone.
Suggested fix: Run the ftol-only and gtol-only ablation or a rescaled-objective test, or remove the attribution.

**minor** (limitations / generality): The paper presents a general 'pitfall for interval estimation in these fits' but tests only one dataset, one seed, one δ (the default-tolerance arms use δ=1e-3 only) and five fixed jitter offsets. The extraction-noise checks in quality.json are run on the trimmed subset for β and a_opt, not on the tolerance finding.
Suggested fix: Narrow the generality statement, or add the δ=1e-2 and extraction-noise checks to the tolerance comparison.

**minor** (C4): The 'independent' implementation shares the data loader and the D=C/6N construction with the main fit. Its starting values and bounds are hand-chosen near the known solution. Agreement therefore confirms the optimiser, not the pipeline. The 3e20 cutoff is flagged as not well identified, yet it is included without comment.
Suggested fix: Describe the cross-check as an optimiser cross-check, and note that the 3e20 cutoff is poorly identified.
