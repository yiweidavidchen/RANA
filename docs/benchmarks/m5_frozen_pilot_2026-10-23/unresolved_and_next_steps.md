# Unresolved questions and next evaluation steps

## Missing fields retained

- **All six T4L records:** exact experimental N, full experimental coding sequence, precise Strep-tag/junction sequence, and independent confirmation of complete experimental/reference background equivalence remain missing. The published N >= 3 is retained. Missing sequence is not a failed site.
- **Six T4L scan associations:** the legacy local sidecar lacks actual execution commit/environment. Its input/output hashes match an archived reference run whose commit and dirty state are recorded separately. Do not upgrade hash equality to direct local execution provenance. No new scan was run to conceal this historical gap.
- **All master records:** incorporation, expression, activity and conjugation outcomes remain blank because they are not inferred from stability. Overall rank is blank because no composite rank exists.
- **Three reused presentations:** 2018 reports SD, 2020 reports SEM. Raw data or author clarification is needed to resolve the later error construction. There is one shared observation ID per site, not one independent observation per error label.
- **Eight ferritin records:** TLC replicate count, error definition/numerical error, author-used PDB accession and full fusion/junction/tag equivalence remain unresolved. Quantitative assembled fraction is not available. Percent fluorophore conjugated remains its original endpoint.
- **Excluded/separate variants:** insertion, double modification and PEG-state values are not missing failed single substitutions. They are outside this digitization scope and retained in the separate-condition registry. Schinn pPa remains outside the pAzF core.

## Recommended next steps

1. Obtain construct sequences/plasmid identifiers and exact background/tag/junction information for both T4L studies; establish which cohorts truly share the same background. Retain separate study/control identifiers until then. Resolve Schinn's declared-site/primer discrepancies before any future pPa mapping.
2. Ask a second reader to check the saved native/cropped/annotated figures and cap selections. Seek author-provided exact thermal-shift means, SD/SEM and per-site N; append a versioned superseding record rather than overwrite this digitized snapshot.
3. Resolve the reused-point SD/SEM issue from raw replicates or author methods. Do not back-calculate N from the two published error-bar sizes, and do not pool SD and SEM.
4. Preserve the documented geometric/experimental disagreements. Define a future endpoint-specific evaluation protocol, eligibility criteria, baselines, metrics and uncertainty analysis before evaluating a larger independent set; group/resample at protein/construct/study level where appropriate. Six sites in one scaffold do not support a generalization claim. This snapshot is not blinded or held out.
5. For ferritin, confirm author-used structure/construct and characterize assembly/environment assumptions. Keep assembly primary and monomer a sensitivity result; do not choose the environment retrospectively by the larger apparent agreement. The single-site substitution in a parent cage is not simultaneous mutation of all 24 subunits.
6. Continue López/Reddington construct- and condition-specific extraction separately. Do not turn unselected or absent variants into negatives. Endpoint-specific measured adverse outcomes may be retained without assigning a universal failed-incorporation class.
7. Track the known insertion-code forwarding omission in a separate regression test/issue before expanding to structures with nonblank insertion codes. All current joined sites are blank-code cases and do not validate that behavior.

## Validation boundary

This round checks hashes, source locators, figure calibration, table consistency, shared IDs and reference parent mappings. Those are data/software integrity checks. The previous 85-test result is historical software verification, not a new experimental validation result; the full suite is not repeated for these data/documentation additions. No RANA scientific implementation, threshold or rotamer library is changed. No correlation, significance test, binary performance statistic or literature-driven parameter tuning is performed.
