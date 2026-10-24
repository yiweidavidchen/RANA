# Wilding 2018: original-source context and deduplication

This addendum records newly available original sources without overwriting the [historical Wilkerson pilot](../wilkerson2020_stability_pilot.md) or its CSV. The historical note that the original Wilding publication was not supplied describes the earlier curation state; it is superseded for current source access by this addendum. Public sources: [Wilding 2018](https://doi.org/10.1021/acssynbio.7b00316) and [Wilkerson 2020](https://doi.org/10.1021/acs.jcim.0c00725). See [inventory](literature_inventory.json) for local file paths/hashes, and [observation JSON](wilding2018_observations.json) for source locators, conditions, and null-value explanations.

## Construct and screened modifications

W-M PDF p7, printed p516, Methods 3.2 identifies a cysteine-free T4 lysozyme in pY71 with a C-terminal Strep-tag. Methods 3.3 uses E. coli-derived CFPS, 3 mM AzF for the single variants, and incubation at 30 °C overnight (~15 h in this work). W-M p2 lists five substitutions K16, S44, N53, L91, K135, an **insertion** between K162 and N163 (Ins163), and the double variant N53/Ins163. The production sentence on that page omits L91 from its enumeration, but the selected-site sentence, Figure 3, and the Methods site list document L91. An insertion is not an N163 substitution, and the double variant is not an independent single-site observation.

The Figure 1/SI S2 structural depiction uses 2LZM, whereas the preserved pilot uses 1L63. The existing pilot's 1L63 SEQADV C54T/C97A context and incomplete full-construct-equivalence check remain in force; this addendum does not remap or assert identity between complete experimental constructs and an arbitrary PDB. It records the paper's structure choice separately.

## Condition separation and endpoints

| Record condition | Protein/reagent conditions | Reference and source |
| --- | --- | --- |
| Unconjugated pAzF variant | No attached PEG; reaction-incubation controls are matched | No-PEG cysteine-free T4L control; W-M p8 (517), Methods 3.5/3.7.1 |
| 5 kDa PEG conjugate | 5 µM protein; 50 equivalents DBCO-mPEG; PBS; 37 °C, 280 rpm, 18 h | WT + 5 kDa PEG reaction; W-M p8 (517), Methods 3.5 |
| 20 kDa PEG conjugate | 5 µM protein; 20 equivalents DBCO-mPEG; PBS; 37 °C, 280 rpm, 18 h | WT + 20 kDa PEG reaction; W-M p8 (517), Methods 3.5 |

The double N53/Ins163 variant receives double those PEG equivalents (100 for 5 kDa, 40 for 20 kDa); it is outside the individual observations curated in this first batch. Unconjugated pAzF is distinct from the no-ncAA control protein.

| Endpoint | Source | Reported uncertainty / replication | Numerical availability |
| --- | --- | --- | --- |
| Full-length CFPS yield | W-M p2 (511), Figure 1B | SD; n ≥ 2 | Bars require digitization; text gives a yield range and one double-variant yield, not a per-site table |
| PEGylation efficiency | W-M p3 (512), Figure 2B; Methods 3.6 p8 | SD; n ≥ 2 | Bars require digitization; SDS-PAGE/autoradiogram densitometry measures shifted / total band intensity |
| ΔTm | W-M p4 (513), Figure 3A; Methods 3.7.1 p8 | SD; n ≥ 3; protocol reactions in triplicate | Per-site means and SD require digitization; do not turn the caption bound into exact pooled N |
| Relative activity | W-M p4 (513), Figure 3B; Methods 3.8 p9 | SD; n ≥ 3 | Bars require digitization; conjugate-specific activity is calculated from mixtures and conjugation fractions under the paper's additive-activity assumptions |

Thermal shift uses unpurified reaction aliquots and a derivative-based Tm. ΔTm is variant Tm minus the average Tm of its **condition-matched** WT reaction. ΔTm,conj is a different contrast: ΔTm,PEGylated − ΔTm,unconjugated (W-M p4, 513). Neither is a direct calibration target for fixed-structure geometry. Activity uses EnzChek at final 0.06 µM lysozyme, 37 °C, 2 h endpoint (W-M p9, 518); derived conjugate activity must be distinguished from the directly measured reaction-mixture activity.

W-M p3 (512), Section 1.1.3 explicitly gives control Tm at pH 7.4: 61.0 ± 0.10 °C (no PEG), 61.1 ± 0.81 °C (5 kDa PEG), 60.7 ± 0.39 °C (20 kDa PEG). These textual values are retained as control context in JSON. That sentence does not define its plus/minus type or each control's N; those fields remain null. These are not three site-specific pAzF observations.

## Three reused observations: count once

WK-M PDF p3 (5119), Experimental Techniques explicitly states that S44, N53, and L91 values come from Wilding; p4 (5120), Figure 2 confirms reuse and identifies H31 as newly measured in 2020. The original source for the three reused **unconjugated** stability observations is W-M Figure 3A, blue bars, not either PEG group. The existing keys are retained:

- `Wilding2018|cysteine_free_T4L|S44pAz|unconjugated|thermal_shift`
- `Wilding2018|cysteine_free_T4L|N53pAz|unconjugated|thermal_shift`
- `Wilding2018|cysteine_free_T4L|L91pAz|unconjugated|thermal_shift`

H31 remains a distinct Wilkerson 2020 observation. The new JSON has separate condition/endpoint records for these three Wilding sites, including PEG sizes and activity/efficiency; those are not relabeled as the reused no-PEG stability measurements. Replots in W-M Figures 2C/3C and W-S S3/S4 do not add observations. Coarse-grain simulation results in W-M Figure 4/W-S S5 are not experimental replicate counts.

**Source-specific error-label discrepancy:** W-M Figure 3 reports SD; WK-M Figure 2 reports SEM for its reused points. Both labels are retained as reported. No SD-to-SEM conversion, inferred exact N, or numerical reconciliation is performed. Raw data or author clarification would be needed to resolve how the later figure's errors were obtained. The preserved pilot's SEM field remains unchanged and must not silently be treated as the 2018 SD.

## Current numerical boundary

Quantitative comparison is pending formal figure digitization. Exact per-site experimental replicate counts are not enumerated; the stability/activity captions provide n ≥ 3. Missing exact N does not by itself preclude a descriptive quantitative comparison, but limits uncertainty analyses. No Figure 2/3 bar height or error was digitized or estimated in this round. The three control Tm values are explicit text, not substitutes for the missing mutant values.

The original four-site Wilkerson pilot remains one protein and four sites, with three reused stability observations. This intake adds provenance and conditions, without a claim of generalization, pooled cross-paper correlation, incorporation/expression prediction, or calibrated geometric performance.
