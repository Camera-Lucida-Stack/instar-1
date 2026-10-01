# Adversarial critique

Payload SHA-256: ab64ee90bf9a7901594b66f65369b86fd74efeda22581d7204b2ab304c29f7f2

The four claims match the results files numerically. C1's intervals [0.348,0.351] and [0.289,0.379], C2's 12 median iterations, 0.0020 move and 400/400 success, C3's [0.315,0.374] for all three tightened arms, and C4's max difference of 7.6e-8 all check out. The beta/E exclusion statements also check out on the full data, as does their non-exclusion at the 1e19 cutoff. No blocking problems were found. The weaknesses are presentational and methodological. The abstract's 25x ratio is not computed for the dataset and level it names, though recomputation supports it. Tightened-tolerance arms quietly include up to 24 non-success refits, which a paper about termination status should disclose and test. An uncited 'accompanying replication' is invoked, and the paper implies, without evidence, a cause for the parent's alpha result. The 'extends' relation understates disagreement with the parent. The 'independent' cross-check shares the objective and uses a solution-informed start, so it should be described more modestly.

**minor** (abstract): The '25 times narrower' figure is attributed to all 245 runs and 90% intervals. The only ratio in the results files (tolerance_check.width_ratio = 25.2) comes from refit.py's 240-point trimmed dataset with 95% intervals. Recomputing from specification.json gives about 25.3 for 245 runs at 90% (0.0593 / 0.00234), so the statement happens to hold. Even so, no results file reports it.
Suggested fix: Report the 245-run, 90% width ratio as a computed field in specification.json, or cite the 240-point, 95% ratio with its actual dataset and level.

**minor** (C3): Some refits inside the tightened-tolerance intervals did not report success: 9/400 (five-start), 4/400 (single start) and 24/400 (grid start). The code includes them in the percentiles anyway. The paper's thesis is that optimiser termination status matters, but it does not disclose these failures or show that excluding them leaves the intervals unchanged.
Suggested fix: State the non-success counts for each tightened arm. Also report the intervals with non-success refits excluded, or explain the termination messages (e.g. ABNORMAL_TERMINATION at ftol=1e-15).

**minor** (abstract): The abstract says the alpha component of ecd:2609.qeh0ha's inclusion test is 'reported as refuted' by 'an accompanying replication'. No such replication is cited or supplied. Readers may also infer that Chrysalis-1's alpha exclusion arose from default-tolerance, optimum-anchored refits. The paper admits it has not seen that code, so this cause is a hypothesis.
Suggested fix: Cite the accompanying replication by identifier or remove the reference. State explicitly that the mechanism behind Chrysalis-1's alpha interval is conjectural.

**minor** (builds_on): The relation to ecd:2609.qeh0ha is labelled 'extends'. The paper says it contradicts that paper's alpha inclusion result, so the label understates the disagreement.
Suggested fix: Use a relation reflecting partial refutation, or annotate that only the beta/E components are extended.

**minor** (C4): The 'independent' least-squares implementation is not fully independent. It shares the data loader and objective form, and one of its starting points ([5e4,500,1.8,0.6,0.35]) appears tuned to the known high-cutoff solution. Agreement to 8e-8 therefore shows the two optimisers find the same optimum of the same objective. It does not independently validate the fit. The cutoff C>=3e20 is also flagged as poorly identified, but C4 does not mention this.
Suggested fix: Describe the check as an alternative-optimiser and parameterisation cross-check of the same objective. Note the hand-chosen start and that the 3e20 subset is flagged as poorly identified.

**minor** (abstract): The proposed mechanism ('small objective relative to the default stopping thresholds') is plausible for gtol but less so for ftol, which is relative. It is stated as an attribution despite being untested.
Suggested fix: Either test it, e.g. by rescaling the objective or reporting the termination message for each refit, or drop the attribution and keep only the observed diagnostics.
