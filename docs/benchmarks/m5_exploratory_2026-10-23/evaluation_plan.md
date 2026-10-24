# Retrospective exploratory evaluation plan

Written before executing the analyses in this directory on 2026-10-23.
The site values and earlier descriptive comparisons have already been seen.
This is a retrospective exploratory pilot, not preregistration, a blinded
evaluation, or an independent test set. Independent human digitization review
remains pending. No algorithm, threshold, rotamer library or composite score
will be changed.

## Frozen inputs and analysis units

Use the six rows in
[`t4l_stability_master.csv`](../m5_frozen_pilot_2026-10-23/t4l_stability_master.csv)
and eight rows in
[`ferritin_conjugation_comparison.csv`](../m5_frozen_pilot_2026-10-23/ferritin_conjugation_comparison.csv).
Retain observation IDs and use each once. Wilding observations reproduced in
Wilkerson are not additional observations. Hash these files and this plan in
the execution record. No rescanning or numeric redigitization is planned.

T4L primary analysis: Wilding 2018 K16, S44, N53, L91 and K135 (n=5 sites).
Cross-study sensitivity: those five plus Wilkerson 2020 H31 (n=6 sites).
These are nonduplicate site observations in one scaffold, not independent
proteins or guaranteed independent assay controls. Full experimental construct
equivalence to reference 1L63 (SEQADV C54T/C97A) remains unresolved.
Insertion variants, double substitutions and PEGylated states remain excluded.

## T4L measures and calculations

Compare each of `rsa`, `ca_neighbors_8a` (local packing), `min_steric_score`
(Å²), and `low_clash_fraction` separately against `value` (ΔTm, °C).
Simplified directional hypotheses: higher RSA/fraction and lower packing/minimum
steric score may correspond to higher ΔTm. These assumptions are to be checked,
not established mechanistic relationships. Retain raw field direction in output
coefficients; do not sign-flip, combine, tune or select the best metric.

Report Spearman rho (Pearson correlation of average ranks) and Kendall tau-b
(tie-adjusted concordant-minus-discordant pairs) for all four fields in both
cohorts. Keep exact stored predictor ties, including repeated fractions and
packing counts. Use frozen rounded digitized means, without weighting SD and SEM
as interchangeable precision estimates. No p-values, significance declarations,
fitted models, prediction MAE/RMSE or binary evaluation.

For each cohort and metric, omit each site in turn and report every coefficient
and its min/max range. A constant remaining variable yields a missing coefficient
with a reason, not zero. Do not remove sites based on these sensitivities.
Scatter plots label every site and study. Experimental bars retain Wilding SD
and Wilkerson SEM. Separate reading bounds (Wilding ±0.2 °C, H31 ±0.1 °C,
operational image-reading bounds, not confidence intervals) are shown with a
different symbol and are not combined with experimental error. Exact N is
unreported; N >= 3 is not N = 3.

## Ferritin separate descriptive case

Plot all eight reported TLC percent-fluorophore-conjugated values against
assembly RSA, minimum steric score and low-clash fraction. Provide matching
monomer plots only as environment sensitivity; assembly remains primary.
No ferritin correlations are planned. Do not pool with T4L. Preserve I5 and L155
and all geometric/experimental disagreements. The original endpoint measures
conjugated versus free fluorophore by quantitative TLC under the reported
1:24 cage:fluorophore conditions; it is not incorporation efficiency, an
experimental success probability, or fraction labeled per subunit. N and error
definitions are missing; draw no invented error bars. The author-used PDB and
full experimental fusion remain unconfirmed; 2FG8 is an approved reference case.

## Interpretation and delivery

Report all coefficients and leave-one-out ranges, including results against the
directional hypotheses. Coefficient magnitude alone cannot establish that RANA
outperforms RSA. Tiny, selected, single-protein cohorts, shared study conditions,
construct uncertainty and unreviewed image digitization prevent claims of
generalization or calibrated stability prediction. Low-clash fraction counts
sampled conformers below the frozen cutoff; it is not experimental success
probability or coverage of the full conformational space.

Keep old data, scans and provenance unchanged. New analysis records must state
their actual software versions, Git HEAD, input hashes and script hash. Missing
historical scan execution provenance remains missing. A future independent
evaluation requires larger endpoint-specific cohorts and protein/construct/study
separation. Software and data-integrity checks are distinct from scientific
validation. Public delivery excludes paper PDFs and publisher figure rasters.
