# T4L stability: six nonduplicate reference-mapped observations

This table is the compact view of [the master CSV](t4l_stability_master.csv); [frozen JSON](frozen_records.json) retains exact source rows and provenance. Every row is a conditional inclusion in the descriptive reference pilot, not a verified full-construct match or a calibrated stability prediction.

Means and error lengths are **digitized estimates**, not exact published numerical measurements. Wilding values come only from the five blue unconjugated bars in Figure 3A (PDF p4, printed p513). H31 comes only from Wilkerson Figure 2 (PDF p4, p5120). Exact per-site values were not found in the main/SI text or tables. The [digitization record](digitization_method.md) documents source digests, native-image coordinates, calibration and uncertainty.

| Site | Original study | delta_Tm (degC) | Error (degC; type) | N | RSA | Packing | Minimum score (Å²) | Low-clash count / 12 | Fraction | Tier |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| K16 | Wilding2018 | -5.4 | 0.8; SD | N >= 3 | 0.4104 | 9 | 0.3464 | 10 / 12 | 0.8333 | `geometry_favorable` |
| S44 | Wilding2018 | -2.1 | 0.3; SD | N >= 3 | 0.4599 | 8 | 0.2398 | 8 / 12 | 0.6667 | `geometry_favorable` |
| N53 | Wilding2018 | -2.9 | 0.2; SD | N >= 3 | 0.6628 | 5 | 0.2194 | 12 / 12 | 1.0000 | `geometry_favorable` |
| L91 | Wilding2018 | -9.6 | 0.7; SD | N >= 3 | 0.0371 | 9 | 12.6748 | 0 / 12 | 0.0000 | `geometry_unfavorable` |
| K135 | Wilding2018 | -4.8 | 1.3; SD | N >= 3 | 0.6401 | 8 | 0.4698 | 8 / 12 | 0.6667 | `geometry_favorable` |
| H31 | Wilkerson2020 | -7.2 | 0.5; SEM | N >= 3 | 0.1458 | 10 | 0.7073 | 4 / 12 | 0.3333 | `geometry_limited` |

Wilding's image-reading bound is +/-0.2 degC for each mean and error length; H31's is +/-0.1 degC. These conservative reading bounds are **separate** from the plotted experimental SD/SEM and are not statistical confidence intervals. Numerical digitization coordinates and intermediate values carry additional digits solely for audit/reproduction. Published N >= 3 is never replaced by N = 3; exact N remains blank. SD and SEM are not converted or pooled.

## Reference geometry, original independent ranks and provenance

All geometric fields are taken from one existing `data/processed/t4l_pazf_ranked.csv`, with chain A, author number and insertion code as the join key. RSA/score/fraction in the display are rounded to four decimals; CSV retains the source precision and JSON retains the original strings. Packing is `ca_neighbors_8a`, other C-alpha atoms strictly within 8 Å. Minimum score is `min_steric_score`, squared heavy-atom overlap penalty in Å². Low-clash count is the count of the same row's `rotamer_scores <= 10.0`, out of 12 sampled rotamers; it is not experimental acceptability or success probability. Tier is copied, never assigned from delta_Tm.

| Site | Steric rank | RSA rank | Rotamer robustness rank | Scan CSV line |
| --- | --- | --- | --- | --- |
| K16 | 42 | 41 | 12 | 17 |
| S44 | 25 | 29 | 18 | 45 |
| N53 | 21 | 7 | 1 | 54 |
| L91 | 128 | 134 | 124 | 92 |
| K135 | 60 | 8 | 18 | 136 |
| H31 | 67 | 104 | 67 | 32 |

Ranks remain over all 162 scored reference sites, with minimum score ascending and RSA/fraction descending (`method="min"`). No overall rank exists; its CSV field is blank. Frozen parameters are pAzF, seed 42, threshold 10.0 Å², favorable fraction 0.5, no functional-residue annotations. No scan was rerun.

The scan/input hashes match `docs/examples/reference-results.json`. Its reference run records commit `0f938eca19a8f5dd0eed06986b2d7cda29d1f78f` and tracked modifications at execution. The legacy **local sidecar has no software block**; therefore its actual execution commit/environment remain unknown and blank. The reference run's commit is kept as a distinct field, not substituted for that missing provenance. Current curation HEAD is recorded separately in the frozen JSON.

## Construct and assay limits

Wilding reports cysteine-free pY71 T4L with a C-terminal Strep-tag, CFPS, unconjugated controls matched to reaction incubation, and derivative thermal-shift analysis (Methods 3.2-3.3 and 3.5/3.7.1). The reported no-PEG WT control is at pH 7.4. Wilkerson reports the same expression/vector/tag class and says H31 used the identical previous procedure. This is not proof that the batches, full coding sequences or control values are identical. Delta_Tm is a within-study variant-minus-corresponding-control contrast; no 2018 absolute control Tm is assigned to H31.

1L63 is the fixed reference: SEQADV C54T/C97A, 162 coordinate residues, no modeled terminal reconstruction or Strep-tag. Full experimental sequences and tag/junction sequences are unconfirmed. Local site parents and numbering are verified for all six. These uncertainties are exposed in every master row; none is claimed fully sequence-matched.

## Descriptive comparison, including disagreements

K16 and K135 retain `geometry_favorable` despite measured melting-temperature decreases near -5.4 and -4.8 degC. Their 10/12 and 8/12 low-clash samples are not evidence of preserved thermal stability. S44 and N53 are also geometrically favorable and have negative delta_Tm. These observations are retained, not removed as inconvenient cases. H31 has only 4/12 low-clash samples with a decrease near -7.2 degC. L91 has no low-clash sampled rotamer and a decrease near -9.6 degC. These are descriptive associations across different physical quantities, not a fitted ranking, statistical relationship or proof of predictive correctness.

No effect significance, cross-paper pooled correlation, binary failed-site label, calibrated error rate or generalization claim is calculated. All sites are from one protein scaffold; source overlap reduces nine figure presentations to six observations.

The count of six refers to nonduplicate underlying site/condition records, not six statistically independent biological experiments. Within-study controls, scaffold and measurement procedures are shared.
