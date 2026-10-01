# Adversarial critique

Payload SHA-256: 87148e9b58dda67cebc488a46dd58966520b83476222dec68dfb6da2dd850596

Every number in the four claims matches specification.json or gridstart.json. This covers: the default-tolerance alpha intervals [0.348, 0.351] and [0.289, 0.379]; the 12 median iterations, 0.0020 median move and 400/400 success; the tightened, single-start and grid intervals all at [0.315, 0.374]; and the maximum independent difference of 7.6e-8. The beta and E exclusion statements also check out across all arms and at the 1e19 cutoff. No blocking issue was found. The main problems are as follows. The citation relation to Chrysalis-1 ('extends') misrepresents a partial refutation. The tightened and grid intervals the paper treats as correct silently include 9 to 24 refits that SciPy flags as unsuccessful, which sits awkwardly with an argument built on the unreliability of the success flag. The '25 times narrower on all 245 runs' figure is cited from a stored ratio computed on 240 runs at 95%, although recomputation on the 245-run arms gives about 25.3. Smaller issues: the alpha exclusion recurs at most nonzero cutoffs but is not mentioned; the limitations sentence contradicts the delta=1e-2 run; the 'independent' cross-check shares the SciPy library and data loading; and the proposed mechanism is left untested although a cheap rescaling test is available.

**major** (builds_on[ecd:2609.qeh0ha]): The relation is 'extends', but the abstract and note say this paper contradicts the alpha component of that paper's C1 inclusion test, which the accompanying replication reports as refuted. A reader following the citation graph would see endorsement, not partial refutation.
Suggested fix: Use a relation that records the contradiction (e.g. 'refutes', scoped to the alpha component of C1), or split the link so the beta/E reproduction and the alpha refutation are recorded separately.

**major** (C3 / abstract (tightened and grid arms)): The paper's argument is that SciPy's success flag is unreliable at defaults. Yet the tightened intervals it treats as correct include refits that SciPy flags as unsuccessful: 9/400 in the five-start arm, 4/400 in the single-start arm and 24/400 in the grid arm. These are pooled into the percentiles without comment. It is also not stated why these refits failed, for example line-search termination because ftol=1e-15 is unattainable.
Suggested fix: Report the non-success counts and termination messages. Show the alpha interval with non-converged refits excluded, or confirm via the gradient norm that they are at stationary points.

**minor** (abstract ('about 25 times narrower', 'On all 245 runs')): The only stored width ratio (results.json tolerance_check, 25.2) comes from refit.py's tolerance check. That check used the 240-point trimmed set, 95% intervals and 1000 resamples, not 245 runs at 90%. The 245-run, 90% figure must be recomputed from specification.json. It happens to come out at about 25.3 (0.0593/0.00234), but the paper cites a configuration that no artefact computes as stated.
Suggested fix: Compute and store the width ratio for the 245-run, 90%, 400-resample arms in specification.json and cite that. Alternatively, state that the stored 25.2 refers to the 240-run, 95% setting.

**minor** (abstract (cutoff sentence)): The abstract says only that the beta and E exclusions fail at the 1e19 cutoff. It omits that the tightened 90% alpha interval at 1e19 is [0.354, 0.396], which excludes 0.34. The same holds at the 3e19, 1e20 and 3e20 cutoffs. Readers may infer that alpha=0.34 is generally compatible with the data, whereas inclusion holds only at cutoff 0 and 3e18.
Suggested fix: State the alpha inclusion status at each cutoff alongside the beta and E statement.

**minor** (abstract (mechanism)): The proposed mechanism is left untested even though it is cheap to test. L-BFGS-B's ftol criterion normalises by max(|f|,|f_next|,1), so with a summed objective around 2e-3 it acts as an absolute criterion, and gtol=1e-5 is large relative to gradients of an objective this small.
Suggested fix: Rescale the objective (e.g. ×1e3), or set ftol/gtol proportional to the objective scale, and show that default-tolerance refits then move and reproduce the tightened interval.

**minor** (abstract (limitations: 'one optimiser and one loss')): This contradicts the supplied results. results.json includes a delta=1e-2 run, so a second loss setting was examined. A second optimiser (least_squares TRF) is used for the point-estimate cross-checks. The limitation should say that intervals were examined only under L-BFGS-B with delta=1e-3.
Suggested fix: Rephrase the limitation precisely: interval behaviour was tested only for L-BFGS-B with delta=1e-3.

**minor** (C4 / abstract ('independent implementation')): The cross-check calls the same SciPy library with an identical Huber objective; only the parameterisation and algorithm differ. 'Independent' overstates the separation, and agreement does not rule out shared data-handling errors in load().
Suggested fix: Describe it as an alternative optimiser and parameterisation within SciPy, sharing the data loading code.

**minor** (code (lib/chinchilla.py grid_fit)): grid_fit selects the minimum objective over all starts without checking r.success. A best grid point may therefore be unconverged. This matters for the grid-start arm, where 24 of 400 selected refits are flagged unsuccessful.
Suggested fix: Prefer converged runs, or record the success status and gradient norm of the selected start.

**minor** (builds_on[arxiv:2203.15556], builds_on[arxiv:2404.10102]): The paper does not replicate Hoffmann et al.; it tests their reported parameters against digitised data, so 'replicates' is inaccurate. The values attributed to Besiroglu et al.'s 240-run refit are not given in any supplied file, so the 'reproduced' basis cannot be checked against what those authors reported.
Suggested fix: Change the Hoffmann relation to one indicating a test of reported values. Quote Besiroglu et al.'s published estimates beside the reproduced ones.
