# Deviations from the pre-registration

## 1. An exploratory test of videos (2 October 2026)

**What changed.** An exploratory hypothesis, H7, is added: that projects with a video are more likely to succeed, as Mollick (2014) found. It is estimated by adding an indicator for the presence of a video to the regression for H3 to H5, on the same sample.

**When and why.** The pre-registration listed videos among the findings that the data could not test. After it was committed, a check of the field names in a single record of the most recent scrape showed that the records include a field named "video". No values of any outcome, and no other records, had been examined. Because the decision follows data access, H7 is reported as exploratory and is not counted among the pre-registered tests.

**Definition and limits.** A project is coded as having a video if its "video" field is present and non-empty; only this indicator is retained, and no video content or address is stored. Before H7 is estimated, the share of projects with a video will be reported by launch year, so that readers can judge whether the field is populated consistently. If the field is absent from older scrapes, H7 is estimated only on the years in which it is present, and the paper will say so. H7 is assessed with the same directional rule as H3 to H5, and Mollick's reported odds ratio of 4.30 is given for comparison.

## 2. Scrapes that cannot be downloaded (2 October 2026)

**What changed.** The pre-registration committed to using every scrape listed by Web Robots. At least one listed file, the scrape of 12 June 2015, returns an access-denied error (HTTP 403) from its host. Any such file is recorded in MANIFEST.csv as unavailable, with the error code, and the analysis proceeds with the remaining scrapes.

**Why this is unlikely to matter.** Projects are deduplicated across scrapes, keeping each project's latest record, so a missing scrape removes a project only if it appears in no other scrape. The coverage table by launch year will show whether any gap results.
