# RANA M5 benchmark evidence and exploratory pilots

This is an endpoint-specific, retrospective evidence collection for RANA v0.1.
It does not validate incorporation, expression, stability, activity or labeling
from geometric accommodation alone. Scientific code, sampling, thresholds and
the pAzF rotamer library remain frozen. Documents below are local working-tree
deliverables; no publication or release is implied. Current M5 closeout status
and remaining boundaries are recorded in the [2026-10-24 closeout](m5_closeout_2026-10-24.md).

## Evidence and cases

- [Literature inventory, verified publications and attachment hashes](literature_m5_2026-10-23/README.md)
  and [data availability matrix](literature_m5_2026-10-23/data_availability.md).
- [Frozen evidence scope and inclusion/exclusion decisions](m5_frozen_pilot_2026-10-23/evidence_scope.md).
  Schinn uses pPa and remains outside the pAzF core. Untested, unreported or
  unselected sites are not negatives. Endpoint classes remain separate.
- [T4L stability table](m5_frozen_pilot_2026-10-23/t4l_stability_comparison.md),
  [six-row master CSV](m5_frozen_pilot_2026-10-23/t4l_stability_master.csv), and
  [presentation/reuse registry](m5_frozen_pilot_2026-10-23/observation_presentations.csv).
  Five Wilding sites plus new Wilkerson H31; S44/N53/L91 republications share IDs.
- [Ferritin eight-site conjugation table](m5_frozen_pilot_2026-10-23/ferritin_conjugation_comparison.md)
  and [CSV](m5_frozen_pilot_2026-10-23/ferritin_conjugation_comparison.csv).
  [Structure preparation and computational case](khoshnejad2018_hftl_computational_case.md)
  retain uncertainty about the authors' actual structure and experimental fusion.
  Assembly is primary; monomer is sensitivity only.

## Review and exploratory evaluation

- **Human image review completed:** Yiwei Chen checked K16, S44, N53, L91,
  K135 and H31 on **2026-10-24**, reporting all six as pass. See the
  [human review record](m5_exploratory_2026-10-23/review/human_review_2026-10-24.md)
  and [JSON](m5_exploratory_2026-10-23/review/human_review_2026-10-24.json).
  This is the maintainer's human check of agent-digitized results, not blinded
  review, a second independent digitization, or experimental prediction-performance
  validation. The [original pending checklist](m5_exploratory_2026-10-23/review/human_review_checklist.md)
  and [automatic checks](m5_exploratory_2026-10-23/review/automatic_digitization_checks.json)
  are preserved as historical snapshots.
- [Evaluation plan written before this analysis](m5_exploratory_2026-10-23/evaluation_plan.md)
  and [exploratory results, plots and all coefficient ranges](m5_exploratory_2026-10-23/results/results.md).
  Results were already seen during curation: this is not preregistration or an
  independent test set. All four fields and both cohorts are reported.
- [Confirmed insertion-code call-chain defect and separate repair proposal](m5_exploratory_2026-10-23/insertion_code_review.md).
  Current joined sites have blank insertion codes and are unaffected by this
  particular omission. No scientific fix is included here.
- [Frozen limitations and unresolved fields](m5_frozen_pilot_2026-10-23/unresolved_and_next_steps.md)
  and [public reproduction instructions and remaining conditions](m5_exploratory_2026-10-23/public_delivery.md).

Historical snapshots are retained, including the earlier four-site
[Wilkerson pilot](wilkerson2020_stability_pilot.md). Its blank experimental values
are historical and are supplemented, not overwritten, by the dated freeze.
Likewise earlier stages saying no correlations were performed describe those
stages; the later explicitly authorized exploratory evaluation is linked above.
Pending-review statements in the frozen plan, checklist and original results
describe their earlier execution dates; the dated human review above supplies
the current status without rewriting those records or their hashes.

## Reproducibility boundary

Small curated tables, scripts, calibration records, configuration and our own
scatter plots have a [proposed public file manifest](m5_exploratory_2026-10-23/public_manifest.json).
No files were staged. Original paper PDFs, publisher rasters, full structures and
full scan runs are excluded from that manifest. The existing raw/processed ignore
rules remain unchanged. Some historical/local-review image links require the
reader to supply the original PDFs and regenerate review materials; these are
explicitly classified by the delivery audit.

The [curated-table replay check](m5_exploratory_2026-10-23/curated_reproduction_check_2026-10-24.json)
checks the unchanged analysis using the two curated CSVs while denying access
to papers, ignored structures/scans and RANA scientific source. This establishes
same-environment curated-table analysis replay, not a fresh-install test or
complete end-to-end scan reproduction. See the [M6 plan](m6_plan.md) for deferred
structure reliability, sensitivity, computational cases and preparation portability;
no M6 implementation is included in this closeout.

Data/hash/table checks are software and curation verification. The historical
85-test result is not a new test run or experimental validation. This small,
selected, single-scaffold stability analysis cannot establish generalization,
calibrated ΔTm prediction, superiority over RSA, or experimental success
probabilities. The human image check is complete; construct clarification and
a larger independent endpoint-specific evaluation remain unresolved scientific
limitations. No pooled cross-protein or
cross-endpoint performance claim is made.
