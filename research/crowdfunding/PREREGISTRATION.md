# Pre-registration: a replication of Mollick (2014) on Kickstarter success

This document sets out, before any data have been downloaded or inspected, the hypotheses, data rules, analyses and decision criteria for Instar-1's replication of Mollick, E. (2014), "The dynamics of crowdfunding: An exploratory study", *Journal of Business Venturing*, 29(1), 1–16 (doi:10.1016/j.jbusvent.2013.06.005). Its date is established by the commit that adds it to the repository, and any later change to it is visible in the repository's history.

## Purpose

Mollick's study, based on Kickstarter projects from 2009 to 2012, reported that projects tend to succeed by narrow margins or fail by large ones, and that larger goals and longer campaigns are associated with a lower chance of success. This study asks whether those findings hold for the much larger body of projects launched in the decade since, and whether they have changed over time. It is a replication of the findings that publicly available data allow us to test, and it makes no claim about those that they do not.

## Findings tested and findings out of scope

The study tests Mollick's findings on the distribution of funding relative to goal, and on the associations of goal size, campaign duration and featuring by Kickstarter with success. It does not test his findings on quality signals (video, spelling errors and updates), founders' social networks, geography at the level of cities, or delivery delays, because the data contain no measures of them. The resulting paper will state this limitation in its abstract.

## Data

The data are the monthly scrapes of Kickstarter projects published by Web Robots at webrobots.io/kickstarter-datasets. Every scrape from the earliest available to the most recent at the time of first download will be used, and the list of files, with their SHA-256 fingerprints, will be recorded in the repository before analysis begins. The files will be downloaded from their source and will not be redistributed, because no licence for redistribution is stated.

Because a project can appear in several scrapes and, from December 2015, in several sub-categories of one scrape, records will be deduplicated by Kickstarter's project identifier, keeping the record from the latest scrape in which the project appears. Because Kickstarter has limited the number of historical projects visible in each category since April 2015, the number of projects per launch year will be compared across scrapes and reported, so that readers can judge how complete each year's coverage is.

Fields identifying creators, including names, profile links and images, will be discarded when the data are loaded. All analysis will use project-level fields only, and no individual project or creator will be identified in any output.

## Sample

The analysis sample comprises projects whose final state is "successful" or "failed". Projects that are live, cancelled or suspended are excluded from the main analysis. Mollick used the universe of Kickstarter projects from 2009 to July 2012, excluding goals below US$100 and above US$1,000,000 as non-serious efforts, and excluding projects located outside the United States. The main analysis follows the same rules, retaining projects located in the United States with goals from US$100 to US$1,000,000 inclusive.

Because prices have risen since 2012 and larger professional campaigns may have become more common, three further analyses of these thresholds are pre-specified. Every hypothesis is re-estimated with the thresholds adjusted for inflation, using annual averages of the United States consumer price index for all urban consumers (CPI-U) published by the Bureau of Labor Statistics, with 2012 as the base year and each project's launch year as the comparison year. Every hypothesis is also re-estimated with no upper limit on goals. Finally, the number of projects with goals above US$1,000,000 in each launch year, and the share of them that succeed, are reported descriptively, so that readers can judge whether the exclusion still removes only non-serious efforts.

Mollick estimated his regression of success only on projects with goals of US$5,000 or more, reasoning that small and large projects are likely to follow different models. The regression for H3 to H5 below is therefore estimated on that subsample, while the descriptive analyses for H1 and H2 use the full analysis sample, as his did.

Goals and amounts pledged in other currencies are converted to US dollars using the conversion rate recorded in each project's own record.

## Definitions

Success is a final state of "successful". The funding ratio is the amount pledged divided by the goal. Duration is the number of days between launch and deadline. Featuring is the "staff pick" field, which we take as the nearest available counterpart of Mollick's measure of featuring on Kickstarter's home page; the paper will note that the two may not be identical. Category is Kickstarter's top-level category, and launch year is the calendar year of launch in Coordinated Universal Time.

## Hypotheses and decision rules

Because the study examines whether Mollick's findings generalise to a decade of later projects, and because both his estimates and ours rest on tens of thousands of projects, statistical consistency with his figures would be an unduly strict test: almost any difference would be statistically significant. The descriptive hypotheses are instead judged against a smallest difference of substantive interest, fixed in advance, in the manner of equivalence testing (Lakens, 2017). That difference is 5 percentage points for shares and 0.05 for funding ratios, on the reasoning that a smaller difference would not change how a scholar or a founder would interpret the finding. The outcome vocabulary follows the spirit of the replication taxonomy proposed by LeBel and colleagues (2018).

For each descriptive hypothesis, a finding is **replicated** if every estimate named in its criterion lies within the margin of Mollick's figure; **pattern holds** if one or more estimates lie outside the margin but the qualitative pattern stated for that hypothesis is present; and **not replicated** otherwise. For each regression hypothesis, a finding is **replicated** if the odds ratio lies on the same side of one as Mollick's with a 95% confidence interval that excludes one, and **not replicated** otherwise; the ratio of our odds ratio to his is also reported. Each hypothesis is assessed for the full analysis sample, or the subsample stated for it, and separately for each launch year with 1,000 or more projects. Where the overall classification is replicated or pattern holds, but the same classification is reached in fewer than two-thirds of those years, the finding is reported as holding **with change over time**.

**H1. Failures fail by large margins.** Mollick reported that the mean funding ratio of failed projects was 0.103, that 10% of failed projects raised at least 30% of their goal, and that 3% raised at least half of it. The estimates are the mean funding ratio of failed projects (margin 0.053 to 0.153), the share of failed projects with a ratio of at least 0.3 (margin 0.05 to 0.15), and the share with a ratio of at least 0.5 (margin 0 to 0.08). The qualitative pattern is that the median funding ratio of failed projects is below 0.25 and fewer than 15% of failed projects raise at least half their goal.

**H1a. Smaller failures fail by smaller margins.** Mollick reported that failed projects with goals under US$1,000 raised a larger share of their goal on average (mean 0.147) than those with goals over US$1,000 (mean 0.098), and used this to argue that self-funding does not explain the pattern in H1. This is a directional hypothesis: it is replicated if the mean funding ratio of failed projects with goals under US$1,000 exceeds that of failed projects with goals over US$1,000, with a 95% confidence interval for the difference that excludes zero, and not replicated otherwise.

**H2. Successes succeed by narrow margins.** Mollick reported that a quarter of funded projects were 3% or less over their goal, that half were about 10% over or less, and that about one project in nine received at least twice its goal. The estimates are the lower quartile of the funding ratio of successful projects (margin 0.98 to 1.08), its median (margin 1.05 to 1.15), and the share of successful projects with a ratio of at least 2.0 (margin 0.061 to 0.161). The qualitative pattern is that the median funding ratio of successful projects is below 1.5 and its lower quartile is below 1.2.

**H3. Larger goals reduce the chance of success.** Mollick's logistic regression of success on the logarithm of the goal, duration in days, featuring and category, estimated on projects with goals of US$5,000 or more, gave an odds ratio of 0.23 for the logarithm of the goal. The criterion is that, in the same regression, the odds ratio for the logarithm of the goal is below one and its 95% confidence interval excludes one.

**H4. Longer campaigns reduce the chance of success.** Mollick reported an odds ratio of 0.99 per day of duration. The criterion is that, in the same regression, the odds ratio for duration is below one and its 95% confidence interval excludes one.

**H5. Featuring is associated with success.** Mollick used featuring as a control, so this is a secondary hypothesis; he reported an odds ratio of 20.47. The criterion is that, in the same regression, the odds ratio for featuring is above one and its 95% confidence interval excludes one.

**H6. Change over time.** This is exploratory and carries no directional prediction. For each of H1 to H5, the estimate for each launch year with 1,000 or more projects is reported with its confidence interval, together with a test of whether the estimates differ across years.

## Analysis

Shares and quantiles in H1 and H2 are reported with 95% confidence intervals from 1,000 bootstrap resamples of projects. The regression for H3 to H5 reproduces Mollick's specification, with category entered as fixed effects, and reports odds ratios with standard errors robust to heteroscedasticity. A second specification adds launch-year fixed effects, which his single-period sample did not need. The random seed is fixed in the code.

## Quality checks

In line with Instar-1's charter, every analysis is subject to the following checks before any paper is composed.

1. **Parameter recovery.** The regression is fitted to synthetic data generated from known coefficients, and must recover them.
2. **Independent implementation.** The regression is estimated with two independent implementations, which must agree.
3. **Specification sensitivity.** Every hypothesis is re-estimated with cancelled projects counted as failures, with all countries included, with the goal thresholds varied, and on each scrape separately, and the regression is also estimated on the full range of goals. A claim that holds only under the main specification will say so.

## Deviations

Any departure from this plan after data have been accessed will be recorded in a file named DEVIATIONS.md, with the reason and the date, and results will be reported under both the original and the revised plan. No hypothesis, threshold or criterion above will be changed in this document after data have been accessed.

## Ethics and data handling

This is independent research, conducted under the ethical standards set out in Instar-1's charter. The data are publicly available records of crowdfunding projects. Fields identifying creators are discarded on loading, no attempt is made to identify or contact any creator, only aggregate results are reported, and the data are not redistributed.

## Limitations stated in advance

The data are scraped from a website, not supplied by Kickstarter, and their coverage of older projects is incomplete. The "staff pick" field may not correspond exactly to Mollick's measure of featuring. Associations in observational data are not causal, and the study does not claim that they are.

## References

Lakens, D. (2017). Equivalence tests: A practical primer for t tests, correlations, and meta-analyses. *Social Psychological and Personality Science*, 8(4), 355–362.

LeBel, E. P., McCarthy, R. J., Earp, B. D., Elson, M., & Vanpaemel, W. (2018). A unified framework to quantify the credibility of scientific findings. *Advances in Methods and Practices in Psychological Science*, 1(3), 389–402.

Mollick, E. (2014). The dynamics of crowdfunding: An exploratory study. *Journal of Business Venturing*, 29(1), 1–16.
