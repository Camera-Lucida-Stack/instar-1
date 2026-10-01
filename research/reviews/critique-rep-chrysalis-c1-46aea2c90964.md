# Adversarial critique

Payload SHA-256: 46aea2c9096477ea3b4f98586f539e2ec49b11fdd7900b28a0a23ad8978655fc

Every number quoted in the paper matches specification.json: point estimates, tightened and default intervals, convergence counts, median iterations and parameter moves. The core finding, that alpha=0.34 lies inside a properly computed 90% bootstrap interval, is supported by the results, so the conjunctive claim C1 fails as stated. The main weakness is the diagnosis. The 'default tolerance' bootstrap is also single-start, which confounds tolerance with multistart, and the paper implies, without evidence, that the parent used such a procedure. Lesser problems: the bare 'refuted' label hides that most of C1 replicates, the handling of non-converged refits is undisclosed, the degeneracy metric is coarse, and limitations are missing. None of these makes the headline refutation false, so nothing is blocking.

**major** (evidence (tolerance comparison) / code: specification.py boot()): The 'SciPy default tolerances' bootstrap differs from the tightened one in two ways, not one. It uses default tolerances and also a single start (multistart=False), while the tightened run uses five jittered starts per resample. The paper says only that the bootstrap was repeated 'with SciPy's default tolerances'. It therefore attributes the collapse of the interval entirely to tolerances, but the comparison cannot separate tolerance from multistart.
Suggested fix: Add the missing arms: defaults with five starts, and tight tolerances with one start. Then either attribute the degeneracy correctly, or state plainly that both settings changed.

**major** (evidence ('reproduces the claim')): The paper implies that Chrysalis-1's intervals came from a degenerate default-tolerance bootstrap. No parent code or settings are cited to support this. Matching an excluded alpha is consistent with that mechanism but does not show it. The parent's own reported intervals are not compared either.
Suggested fix: Phrase this as a hypothesis ('a default-tolerance bootstrap would reproduce...'), or cite the parent's artefacts showing the settings it used.

**minor** (outcome): The target claim is a conjunction. The point estimates and the beta and E exclusions all replicate; only the alpha exclusion fails. Labelling the whole claim 'refuted' without qualification may lead readers to think the refit itself failed to replicate.
Suggested fix: State in the outcome summary that the point estimates and the beta and E conclusions replicate and only the alpha exclusion fails, or use a partial-replication label if the protocol allows one.

**minor** (evidence (convergence)): Nine of the 400 tightened refits did not report convergence. The code keeps them in the percentile intervals, and the paper does not say whether they were included or how they affect the endpoints.
Suggested fix: Report the intervals with the non-converged refits excluded, or state explicitly that they are included and show that the alpha conclusion does not change.

**minor** (evidence (degeneracy diagnostic)): The 'median max parameter move' is a maximum over log A, log B, log E, alpha and beta. It is likely dominated by log A and log B, so it says little directly about whether alpha moved. Each resample also starts at the full-data optimum, possibly with jitter, rather than from a fresh grid. Residual anchoring to that optimum could still narrow the intervals.
Suggested fix: Report per-parameter moves, especially for alpha, and check the tightened intervals against a coarse grid search per resample on a subset.

**minor** (evidence ('Same data', 'independent implementation')): The parent does not publish a data hash, so 'same data' is assumed rather than verified. The 8e-8 agreement applies to point fits across cutoffs; it does not validate the bootstrap intervals that the refutation rests on.
Suggested fix: Say that data identity is inferred from the description, and scope the independent-implementation statement to the point estimates.

**minor** (limitations): No limitations are stated. The 90% percentile endpoints from 400 resamples carry Monte Carlo error. The extraction-noise and parameter-recovery checks were run on the 240-point trimmed set, not the 245-point C1 setting.
Suggested fix: Add a limitations sentence covering endpoint Monte Carlo error and the scope of the quality checks. Note that alpha=0.34 sits about 0.025 inside the lower bound, so it is robust to that error.
