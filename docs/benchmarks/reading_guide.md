# Reading the M5 retrospective pilots

## What M5 asks

M5 asks how RANA's fixed-structure pAzF geometric screening relates to selected
published experimental observations. It provides a small retrospective pilot
for researchers considering sites for ncAA substitution. The observations were
already known during curation; this is neither a preregistered study nor an
independent test set. This guide is a later interpretation of the preserved
evidence, not a replacement for it or a plan written before scanning.

The two cases address different endpoints. T4 lysozyme (T4L) measures changes
in melting temperature, whereas human ferritin light chain measures fluorophore
conjugation. Stability and conjugation involve processes beyond side-chain fit,
and their values have different units and denominators. They are analyzed
separately, without a pooled cross-protein correlation. The
[evidence scope](m5_frozen_pilot_2026-10-23/evidence_scope.md) also keeps
incorporation, expression, activity and these two endpoints distinct. Untested,
unreported or unselected sites are never assigned failure labels.

## T4L: six observations, two analysis sets

The [stability report](m5_frozen_pilot_2026-10-23/t4l_stability_comparison.md)
contains six nonduplicate site observations. The primary analysis uses Wilding
2018's five unconjugated single-site pAzF variants: K16, S44, N53, L91 and K135.
Adding Wilkerson 2020's newly measured H31 gives a six-site cross-study
sensitivity analysis. Wilkerson's S44, N53 and L91 observations reuse Wilding's
data and share observation IDs; they do not add independent measurements.
PEG-conjugated variants, insertion Ins163 and double substitutions remain
outside this stability cohort.

The digitized mean ΔTm values are −5.4, −2.1, −2.9, −9.6 and −4.8 °C for the
five Wilding sites, respectively, and −7.2 °C for H31. Each is a
variant-minus-corresponding-control contrast within its study. All six estimates
are negative. Four sites nevertheless have a favorable geometric tier,
including K16 and K135. Their ability to accommodate sampled pAzF conformations
does not establish preserved thermal stability. L91 has no low-clash sampled
rotamer and the largest melting-temperature decrease in this selected cohort.

The comparison uses four existing fields. Relative solvent accessibility (RSA)
describes exposure normalized by residue type. Packing counts other Cα atoms
within 8 Å. The minimum steric score is the lowest squared heavy-atom overlap
penalty, in Å², among 12 sampled rotamers. The low-clash fraction is the fraction
of those samples with scores ≤10.0 Å². It describes this discrete library in a
fixed environment, not experimental success probability or the fraction of all
possible conformations. RSA and packing provide simple structural baselines;
no composite score is introduced.

The [exploratory results](m5_exploratory_2026-10-23/results/results.md) report all
four fields, retaining ties in Spearman rho and Kendall tau-b. For the primary
five sites, Spearman rho is 0.700 for RSA, −0.791 for packing, −0.800 for minimum
steric score and 0.410 for low-clash fraction. The proposed directions were
higher RSA/fraction and lower packing/steric score with higher ΔTm. These
descriptive associations do not demonstrate superiority over RSA. Adding H31
changes the coefficients and introduces a study difference.

Leaving out each site in turn shows the limited stability of these summaries.
For the five-site analysis, low-clash fraction's Spearman rho ranges from
−0.211 to 0.800; RSA's ranges from 0.400 to 1.000. The complete ranges for both
coefficients and both cohorts are retained in the results. They expose
small-sample dependence, are not confidence intervals, and do not justify
deleting sites. No significance conclusion is drawn.

The means and error lengths were digitized from Wilding Figure 3A and Wilkerson
Figure 2 after exact per-site values were not found in the main text or SI.
Wilding's errors remain SD; H31's remains SEM. Separate image-reading bounds
are ±0.2 °C for Wilding and ±0.1 °C for H31, for both means and error lengths.
They are not added to the experimental errors. Exact per-site replicate counts
remain unreported; the available statement is N ≥ 3. Neither error types nor
replicate counts are converted to make the studies appear interchangeable.

The structural reference is 1L63, with C54T/C97A recorded in SEQADV. Local
numbering and parent residues match, but complete experimental sequence,
tag/junction and batch equivalence remain unconfirmed. The reference does not
model the experimental Strep-tag. These are conditionally included,
reference-mapped observations, not a fully sequence-matched benchmark.

## Ferritin: conjugation in an assembly environment

The [ferritin report](m5_frozen_pilot_2026-10-23/ferritin_conjugation_comparison.md)
retains eight reported percentages of fluorophore conjugated to protein,
measured by thin-layer chromatography (TLC): S2, I5, Y9, F79, K83, K105, L112
and L155. The denominator concerns fluorophore, not successfully incorporated
pAzF or labeled subunits. Conditions include final 1 µM hFTL-X, an
hFTL-X:DBCO-AlexaFluor488 ratio of 1:24, and overnight incubation at room
temperature. The original concentration/denominator convention is preserved
without conversion. Site-specific N and defined error values remain missing.

The primary environment is reference 2FG8 assembly 1: all 24 protein chains
surround target chain A. Cross-subunit contacts therefore contribute to exposure,
packing and steric screening. The isolated monomer is an environment-sensitivity
comparison. Only the target subunit is substituted in the calculation; the
other 23 retain their parent identities. Nonprotein species are omitted.

I5 has 57% reported conjugation despite zero low-clash assembly rotamers and an
unfavorable tier; L155 has 18% with the same geometric classification. These
disagreements remain visible. Monomer results do not replace assembly results
to improve agreement. Neither cage access by the conjugation reagent nor
reaction kinetics is predicted. The authors' exact PDB and complete fusion
construct remain unconfirmed; 2FG8 is a selected computational reference, not confirmed as the authors’ exact input.

## Reading order and strength of evidence

Start with the [literature inventory](literature_m5_2026-10-23/README.md) and
evidence scope, then the two case reports linked above. The
[T4L master CSV](m5_frozen_pilot_2026-10-23/t4l_stability_master.csv) and
[ferritin CSV](m5_frozen_pilot_2026-10-23/ferritin_conjugation_comparison.csv)
retain source locators, conditions, mappings and missing-field explanations.
Continue to the exploratory results for plots and all coefficient ranges.

For the extraction evidence, read the
[digitization method](m5_frozen_pilot_2026-10-23/digitization_method.md) and
[human review record](m5_exploratory_2026-10-23/review/human_review_2026-10-24.md).
Yiwei Chen checked all six sites against the original figures and review images
on 2026-10-24 and passed all six. This is a maintainer's human check of
agent-digitized results, not blinded review, a second independent digitization
or experimental prediction validation. Earlier pending statements are preserved
historical snapshots.

Finally, the [reproduction instructions](m5_exploratory_2026-10-23/public_delivery.md)
and [M5 closeout](m5_closeout_2026-10-24.md) define the verification boundary.
Software execution and checks establish specified program behavior; replay
establishes curated-table analysis reproducibility in the recorded environment.
Neither establishes a fresh-install, complete structure-to-scan M5 pipeline.
Descriptive associations summarize these selected observations. Predictive
accuracy and generalization require further independent, endpoint-specific
evidence. M5 does not validate incorporation, stability, function or conjugation
predictions from geometry alone.
