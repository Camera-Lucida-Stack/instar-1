# Adversarial critique

Payload SHA-256: 5e3f2c0cdea114bbf50847a937e1860b09a8536d84843b88608a45440a0adcde

Every number in C1–C4 matches specification.json: the intervals [0.348, 0.351], [0.289, 0.379] and [0.315, 0.374], the 12 iterations, the 0.0020 move, the 400/400, 391 and 396 success counts, and the maximum difference of 7.6e-8 < 8e-8. The statement that the β and E exclusions hold in all arms is also correct. The causal mechanism is explicitly marked as untested, and the paper does not overclaim about the parent's code. The main weakness is the abstract's general statement that refits 'stay close to wherever they start'. The stored diagnostics measure movement from the optimum rather than from each start, so this is shown only for the optimum-start arm. The jittered-arm interval also mixes selection over five starts with early stopping. The headline width ratio is quoted in a setting different from the one where it is stored. Further gaps are single-seed Monte Carlo error, non-converged refits retained in the reference interval, and parameter-move units left undefined. None of these puts a false claim on the record, but the abstract wording and diagnostics should be tightened.

**major** (abstract / code (specification.py boot)): The abstract says bootstrap refits 'stay close to wherever they start'. For the jittered arm, the recorded diagnostic `median_max_parameter_move` is measured from p0 (the full-data optimum), not from the jittered start that was selected. The default-jittered value of 0.4997 matches the 0.5 jitter magnitude, but no recorded quantity shows that refits stay near their own start. Only the optimum-start arm (move 0.0020) supports the statement directly. Separately, the jittered-arm estimate is the best of five fits, so its interval mixes start selection with early stopping. The paper does not separate these two effects.
Suggested fix: Record each refit's distance from its actual starting point, and which of the five starts won. Alternatively, restrict the 'stay close to where they start' wording to the optimum-start arm.

**minor** (abstract ("about 25 times narrower")): The only stored width ratio, `tolerance_check.width_ratio` = 25.2 in results.json, comes from a different setting: the 240-point trimmed data, 95% intervals and 1000 resamples. The abstract applies the figure to all 245 runs with 90% intervals. Computing it from specification.json gives 0.05929 / 0.00234 ≈ 25.3, so the figure is right, but the coincidence hides where it came from.
Suggested fix: Cite the ratio computed from `specification.json` `chrysalis_c1` (25.3) and store it explicitly, or state both settings.

**minor** (C1): 'Five jittered starts' is slightly misleading: the first JIT row is a zero offset, so one of the five starts is the optimum itself. The ±1.0 log-unit offsets apply only to log A and log B; E and the exponents are jittered by at most 0.05.
Suggested fix: Describe the scheme as 'the optimum plus four jittered starts' and give the offsets.

**minor** (C2): The 'largest parameter move' is a max-abs over the parameter vector, which mixes log A, log B and log E with raw α and β. The units are not stated. The cause of termination (the ftol vs gtol criterion) is also not recorded, although the abstract does concede the mechanism is untested.
Suggested fix: State that moves are in the (log A, log B, log E, α, β) parameterisation. Record the termination message for each refit.

**minor** (C3): Treating the tightened interval as the reference assumes that the 9 and 4 non-converged refits do not distort it. These refits are kept in the percentiles without comment, and no coverage study is run (this is acknowledged). Agreement between the two tightened arms is partly guaranteed by construction, because they use identical resample indices from the same seed.
Suggested fix: Report the intervals with non-converged refits excluded. Note that the two arms share the same resamples, so their agreement tests optimiser determinism, not sampling robustness.

**minor** (limitations): All interval endpoints and the 'reversal' come from a single bootstrap seed with 400 resamples. No Monte Carlo error is given for the endpoints or for the width ratio.
Suggested fix: Repeat with several seeds, or report bootstrap-of-bootstrap endpoint SEs.

**minor** (C4): The independent implementation is also SciPy and also uses a Huber objective with a handful of starts. Agreement at the point estimate does not validate the interval machinery that the paper is about. The 3e20 cutoff (n=63) is flagged as not well identified, yet it is included in 'every cutoff' without qualification.
Suggested fix: Note the shared-library limitation and the poorly identified cutoff in the claim or in the limitations.
