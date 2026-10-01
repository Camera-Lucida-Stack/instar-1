# Adversarial critique

Payload SHA-256: a45a2db84e215b44b775b341dd78522a1b467e6b1918b3de644cb302a571c5e8

The numbers in C1–C4 match specification.json after rounding. The core finding is adequately supported for this dataset and seed: default-tolerance L-BFGS-B bootstraps started at the optimum barely move, while tightened bootstraps give [0.315, 0.374], which includes α=0.34. Several faults remain. C1 misdescribes the multistart scheme as five jittered starts when one is the optimum, contradicting the abstract. The result hinges on 'SciPy defaults', yet no SciPy version or actual tolerance values are recorded. The abstract leans on an uncited, unsupplied 'accompanying replication' while admitting the parent's code is unseen, so any implied cause of the parent's α exclusion is unsupported. The only stored 25x ratio comes from a different analysis (240 points, 95% intervals), even though the 245-point figure happens to agree. Lesser issues are the inclusion of unconverged tightened refits without saying so, a C4 wording that implies a continuous cutoff range, an over-broad robustness statement for E, and inaccurate builds_on relations. None of these puts a false headline number on the record, so none is blocking, but the claim text and provenance need correction.

**major** (C1): The claim says the second default-tolerance interval [0.289, 0.379] comes 'from five jittered starts'. In specification.py, JIT[0] is the zero offset, so one of the five starts is the full-data optimum and only four are jittered. The abstract states this correctly, so the claim text is wrong and contradicts the abstract.
Suggested fix: Reword to 'best of five starts per refit (the optimum plus four jittered starts)', matching the abstract.

**major** (C1, C2, C3, abstract): The central result depends on what 'SciPy's default L-BFGS-B tolerances' are, but no SciPy version is recorded anywhere. L-BFGS-B defaults and termination behaviour have changed across SciPy releases. A reader cannot tell whether the 12-iteration stop, 400/400 success and 25x narrowing will reproduce.
Suggested fix: Record the SciPy (and NumPy) versions in the results files and the paper. State the actual default values in force (ftol, gtol, maxiter, maxls) and the tightened values (ftol=1e-15, gtol=1e-12, maxiter=20000).

**major** (abstract): The abstract says the α inclusion test of ecd:2609.qeh0ha is reported as refuted 'by an accompanying replication'. That replication is not cited in builds_on, not given an identifier, and not among the supplied files, so the statement cannot be verified. The paper also admits it has not seen the parent's code. It therefore cannot show that the parent's exclusion of α arose from default-tolerance, optimum-started bootstraps. Juxtaposing the pitfall with the parent's result implies a cause the evidence does not establish.
Suggested fix: Cite the accompanying replication by ID or remove the reference. State explicitly that the mechanism behind the parent's α exclusion is unknown. Say that this paper shows only that a tightened bootstrap on the same data includes 0.34.

**minor** (abstract): The '25 times narrower' figure is supported for 245 points and 90% intervals by specification.json: 0.0593/0.00234 ≈ 25.3. However, the only stored ratio, tolerance_check.width_ratio = 25.2 in results.json, comes from a different analysis: 240 trimmed points, 95% intervals and 1000 resamples. The match is coincidental, and a reader checking the stored number will find it attached to a different dataset and level.
Suggested fix: Store the 245-point, 90% width ratio explicitly in specification.json and cite it. Alternatively, label tolerance_check as the 240-point, 95% analysis.

**minor** (C3): Nine (multistart) and four (single-start) tightened refits report failure, yet they are kept in the percentile intervals. The claim reports the success counts but not the fact that unconverged fits are included. It also gives no termination messages for these fits, such as ABNORMAL_TERMINATION_IN_LNSRCH at ftol=1e-15.
Suggested fix: State that unconverged refits are included, give their termination messages, and show the interval with them excluded.

**minor** (C4): 'Every compute cutoff from none to C≥3e20' reads as a continuous range, but only six discrete cutoffs were tested. The C≥3e20 subset (n=63) is flagged as not well identified. The 'independent' implementation also shares the model, loss and data, and its added start [5e4, 500, 1.8, 0.6, 0.35] appears tuned to the high-cutoff solution. Agreement therefore checks optimiser convergence, not correctness.
Suggested fix: Say 'at each of six cutoffs (0, 3e18, 1e19, 3e19, 1e20, 3e20 FLOP)'. Note that 3e20 is poorly identified. Describe the check as an optimiser cross-check with shared model and loss.

**minor** (abstract (limitations)): The limitations say 'one optimiser and one loss', yet results.json includes a δ=1e-2 Huber run and the cross-check uses a second optimiser. The tolerance pitfall itself was tested only at δ=1e-3 and only for L-BFGS-B, which is the limitation that actually matters.
Suggested fix: State that the default-versus-tightened comparison was run only for L-BFGS-B at δ=1e-3.

**minor** (abstract): The claim that the β and E exclusions 'hold under every setting we tested' is broader than the evidence for E. E was not part of the extraction-noise perturbation check, which covered only β and a_opt on 240 points. The a_opt robustness failure (99/100) is also not mentioned.
Suggested fix: Enumerate the settings tested: four bootstrap arms on 245 points, plus 95% intervals for trimmed data and δ=1e-2. Note that E was not perturbation-tested.

**minor** (builds_on): ecd:2609.qeh0ha is tagged 'extends', but the paper contradicts one component of its C1. arxiv:2203.15556 is tagged 'replicates', but the paper tests reported parameters rather than replicating the study.
Suggested fix: Use a relation reflecting partial contradiction for the Chrysalis paper and 'tests' (or similar) for Hoffmann et al.

**minor** (abstract): Only seed 20261001 is listed. The quality checks use seed 7, and no Monte Carlo uncertainty is given for interval endpoints estimated from 400 resamples.
Suggested fix: List all seeds and give the bootstrap standard errors of the endpoints, or state that they were not computed.
