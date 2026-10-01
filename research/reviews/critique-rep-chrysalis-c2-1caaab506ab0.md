# Adversarial critique

Payload SHA-256: 1caaab506ab06daa779fcbf1860d80d263a5f937d259a814f2576544cf8b1069

The cutoff numbers quoted match specification.json, and the 1.9× figure is correctly taken from it. However, labelling the outcome 'replicated' overstates agreement. The replicator's own tightened-tolerance analysis shows the parent's 'specification-dominated / dramatically understate' framing is largely an artefact of loose optimiser tolerances: the beta spread is only 1.22× the sampling width, and that figure is omitted. The specification-spread metric itself is methodologically weak. It compares point estimates on shrinking subsets (down to n=63, with a poorly identified fit) against the sampling width of the full set, without per-cutoff intervals. The cutoff fits use a coarser initialisation grid that none of the quality checks validate, yet the abrupt a_opt jump suggests local-optimum switching. The bootstrap uses single-start refits without convergence checks. The result supports a partial replication of the direction of C2, not its magnitude.

**major** (outcome / evidence): The outcome is 'replicated', but the replicator's own tightened-tolerance result weakens the target claim's central qualifier. The parent claim says the fit is 'specification-dominated', and its abstract says sampling intervals 'dramatically understate' uncertainty. Under tightened tolerances the spread across cutoffs is only 1.93× the 90% sampling width for a_opt and 1.22× for beta (specification.json spread_to_width). For beta, specification spread and sampling width are of the same order, which does not show the fit is specification-dominated. The parent's dramatic understatement appears to rest on default-tolerance intervals, which are about 25× too narrow (tolerance_check width_ratio 25.2). The a_opt default 90% width is about 0.003, versus 0.108 tightened.
Suggested fix: Change the outcome to partially replicated. State that the direction (spread exceeds sampling width) holds, but the magnitude and the 'specification-dominated' characterisation do not. Name default-tolerance intervals as the likely cause.

**major** (evidence (beta ratio omitted)): Only the a_opt ratio (1.9×) is reported. The beta ratio of 1.22×, which is less favourable to the parent claim, is computed but omitted. This is selective reporting.
Suggested fix: Report both ratios: beta 1.22× and a_opt 1.93×.

**major** (code (specification.py)): The 'specification spread' is the range of point estimates across nested subsets that shrink to n=63. Those subsets have much larger sampling variance than the full 245-point fit whose interval forms the denominator. The spread therefore mixes subsample sampling noise with specification effects, which biases the ratio upward. At the 3e20 cutoff, A=3.3e5 and alpha=0.68 indicate a poorly identified fit. No bootstrap intervals are computed at each cutoff, so specification and sampling uncertainty are not actually separated.
Suggested fix: Bootstrap each cutoff fit. Compare the between-cutoff variation with the within-cutoff sampling intervals, or report spread excluding small, poorly identified subsets.

**major** (code (specification.py grid_fit coarse=True)): Cutoff fits use a coarse 3^5 initialisation grid, while the full-data fit and the sampling intervals use the fine grid. a_opt jumps abruptly from 0.563 (n=240) to 0.412 (n=192). This is consistent with switching between local optima, which a coarse grid may resolve inconsistently. None of the quality checks (recovery, reimplementation) validate the cutoff fits. The C>=1e19 numbers that the claim 'matches' are therefore unverified as global optima.
Suggested fix: Refit each cutoff with the fine grid and with the independent least_squares implementation. Report the agreement, and report the objective landscape near the 3e18–1e19 transition.

**minor** (code (lib bootstrap)): Each bootstrap refit starts from a single initialisation (the full-data optimum) with no grid search and no convergence check. Resamples can therefore stay near the start point, understating sampling width. The 25× tolerance sensitivity shows this mechanism operating. Even the tightened interval may be underdispersed, which would inflate the spread-to-width ratio.
Suggested fix: Use multi-start fits per resample, or at least check r.success. Report the share of non-converged resamples.

**minor** (evidence): The phrase 'consistent with the claimed 0.35 to 0.56' is loose. The observed minimum is 0.356, which rounds to 0.36, so the parent's lower bound of 0.35 is not reproduced exactly.
Suggested fix: Say the range is reproduced to within 0.01 at the lower end, or report three decimals (0.356–0.565).

**minor** (evidence): The clause 'by less than default-tolerance intervals would suggest' rests on a default-tolerance a_opt ratio that is not stated anywhere. It can only be derived from the specification.json default interval.
Suggested fix: State the default-tolerance spread-to-width ratio explicitly (about 75× for a_opt).

**minor** (evidence (limitations)): No limitations are stated. Omitted are digitisation error in the SVG-extracted data (the extraction-noise check found a_opt-related conclusions non-robust in 1 of 100 perturbations), the choice of cutoff set, and the 400-resample interval precision.
Suggested fix: Add a limitations sentence covering these points.
