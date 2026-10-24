# RANA M5: Wilkerson 2020 four-site stability pilot

This pilot pairs published stability records for H31, S44, N53, and L91 → pAzF with results from a single existing RANA scan. The data are in [wilkerson2020_stability_pilot.csv](wilkerson2020_stability_pilot.csv). No new scan was run, no scoring rules were changed, and no parameters were tuned against experimental outcomes. Figure 2 has not been formally digitized, so ΔTm and SEM are blank. A blank does not mean zero.

## Sources and locations

- **P (main article)**: `E:\Papers for RANA\The Effects of pAzF incorporation on Protein Structure and Stability.pdf`. Wilkerson et al., *J. Chem. Inf. Model.* 2020, DOI [10.1021/acs.jcim.0c00725](https://doi.org/10.1021/acs.jcim.0c00725). PDF page 2 (journal page 5118), Methods / Proteins and Figure 1, identifies the structure and sites. PDF page 3 (5119), Experimental Techniques, distinguishes newly measured data from reused data. PDF page 4 (5120), Experimental Data and Figure 2, defines ΔTm, SEM, and N≥3. Reference 13 on PDF page 7 (5123) provides the Wilding 2018 citation.
- **S (supporting information)**: `E:\Papers for RANA\Supp_Wilkerson_2020.pdf`, 5 pages. The six/nine replicates in Simulation Length on page 1, and the nine replicates in Figure S2 on page 3, are MD simulations. Figure S4 on page 5 reports RMSF and its uncertainty, not a thermal-shift ΔTm data table. No directly transcribable table of four-site ΔTm or SEM values was found in the supplied PDFs.
- **C (sole source of computational values)**: `data/processed/t4l_pazf_ranked.csv`. All structural features, steric statistics, tiers, and existing ranks for a site come from the same row in this file. No other scan files were mixed in. Below, C:field denotes an original field in this CSV.
- **M (local metadata sidecar)**: `data/processed/t4l_pazf_ranked.metadata.json`. The input, parameters, and scan population were checked using `input.pdb_sha256`, `input.chain`, `configuration`, and `results`.
- **I (input structure)**: `data/raw/1L63.pdb`. ATOM residues in the first MODEL were checked using the mapping key `chainID + resSeq + iCode + resName`.
- **R (reference run record)**: `docs/examples/reference-results.json`, `runs.t4l_pazf_ranked`. Its input and output SHA-256 hashes match I and C. Local M has no `software` block or output hash fields, so `scan_actual_git_commit` remains blank in the pilot CSV. The reference run commit in R is not presented as execution provenance recorded by the local sidecar. Matching file contents alone do not establish when the local files were generated or which execution environment produced them.

## Structure mapping

| Published site | I:chainID | I:resSeq | I:iCode | I:resName | C:residue_name | Physical line in C (header is line 1) | Result |
|---|---|---:|---|---|---|---:|---|
| H31 | A | 31 | Blank | HIS | HIS | 32 | Parent and identity match |
| S44 | A | 44 | Blank | SER | SER | 45 | Parent and identity match |
| N53 | A | 53 | Blank | ASN | ASN | 54 | Parent and identity match |
| L91 | A | 91 | Blank | LEU | LEU | 92 | Parent and identity match |

All four sites have N, CA, and C atoms, and C:status is `scored` for each. A blank insertion code is a verified blank PDB code, not an unknown mapping. Sites were matched directly by PDB residue identity, without an offset or automatic renumbering.

The input parent structure is 1L63 (I), whose PDB SEQADV records identify a C54T/C97A background. SEQRES lists 164 residues, whereas the available coordinates and C contain only 162 standard residues. The Methods section in P (PDF pages 2–3, 5118–5119) describes the experimental control as cysteine-free T4L and states that CHARMM-GUI added the last two residues to the simulation model. The experimental expression construct also carries a C-terminal strep-tag. RANA uses the existing coordinates in the original I; it did not add terminal residues or a tag, or reproduce the article's MD preparation. This pilot verifies only the chain, residue number, and parent residue at the four sites. It does not establish that the input structure, full experimental construct, and published MD model are identical.

## Computational comparison from one scan

Continuous values below are displayed to 6 decimal places for readability; the CSV retains the full source precision. Headers identify the original C fields. Within the table below, `n_acceptable_rotamers` is the only derived count.

| Site | C:rsa | C:ca_neighbors_8a | Number of low-clash rotamers (`n_acceptable_rotamers`) | C:n_rotamers | C:low_clash_fraction | C:min_steric_score (Å²) | C:mean_steric_score (Å²) | C:median_steric_score (Å²) | C:candidate_tier |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| H31 | 0.145802 | 10 | 4 | 12 | 0.333333 | 0.707324 | 39.598138 | 50.646349 | geometry_limited |
| S44 | 0.459877 | 8 | 8 | 12 | 0.666667 | 0.239751 | 13.413712 | 1.933707 | geometry_favorable |
| N53 | 0.662753 | 5 | 12 | 12 | 1.000000 | 0.219412 | 0.908098 | 0.806950 | geometry_favorable |
| L91 | 0.037061 | 9 | 0 | 12 | 0.000000 | 12.674815 | 50.613006 | 55.197769 | geometry_unfavorable |

| Site | C:steric_rank | C:rsa_rank | C:rotamer_robustness_rank | overall_rank |
|---|---:|---:|---:|---|
| H31 | 67 | 104 | 67 | |
| S44 | 25 | 29 | 18 | |
| N53 | 21 | 7 | 1 | |
| L91 | 128 | 134 | 124 | |

These are the existing independent ranks among all 162 `scored` sites in C, not ranks within this four-site subset. No composite / overall rank is defined, so that column remains blank.

### Field definitions and numerical sources

- `rsa`: copied directly from C:rsa; dimensionless. `structural.compute_relative_sasa` defines it as C:sasa_abs / C:sasa_max. Both source columns are retained in the CSV (units: Å²). This is parent-structure residue RSA, not exposure of the substituted pAzF or its azide handle.
- `ca_neighbors_8a`: copied from the same-named field in C. `structural.compute_local_packing` counts other Cα atoms at distances strictly `<8 Å` across all retained protein chains, excluding the target itself. This is a raw neighbor count, not an energy or calibrated packing tolerance. The radius comes from `radius = 8.0` in `ncaa_site_rec/features/structural.py`.
- `n_acceptable_rotamers`: the number of sampled conformations with steric score ≤10.0 Å², counted from **the same row's C:rotamer_scores** using `score <= M:configuration.low_clash_threshold`. It is not C:n_rotamers. This count does not represent experimentally validated acceptability, a success probability, or a fraction of the complete conformational space. For each row, count / C:n_rotamers was checked against C:low_clash_fraction. See `ncaa_site_rec/features/site_scan.py::scan_pazf_sites` for the implemented definition.
- `n_rotamers`: copied directly from C:n_rotamers; the number of rotamers actually scored. Each row has 12. This is neither an experimental replicate count nor exhaustive conformational sampling.
- `min_steric_score`, `mean_steric_score`, `median_steric_score`, `low_clash_fraction`, and `rotamer_scores`: retained directly from the same-named C fields. `pazf.compute_steric_score` sums squared overlaps over included atom pairs, in Å². It is not an energy or ΔΔG. The rotamer library was not changed, and rotamer scores were not recalculated.
- `candidate_tier`: retained directly from C. `site_ranking.rank_pazf_sites` uses the minimum steric score and low-clash fraction, with thresholds in M of 10.0 and 0.5, respectively. RSA, packing, and published experimental outcomes do not determine the tier. This pilot only checked that the existing fields agree with the existing rules.
- The three ranks: retained directly from the same-named C fields. For sites with `status == scored`, `site_ranking.rank_pazf_sites` ranks min_steric_score in ascending order, rsa in descending order, and low_clash_fraction in descending order. Ties use `method='min'`. No composite score, percentile, or new ranking was produced. `rank_population_n_scored` is the count of C:status values equal to scored, giving 162, consistent with M:results.status_counts.scored.
- `low_clash_threshold_A2` and `favorable_fraction_threshold`: transcribed from M:configuration.low_clash_threshold and M:configuration.favorable_fraction, respectively. The seed is M:configuration.seed = 42. No parameters were tuned.
- `residue_number`, `parent_residue`, `chain`, and `insertion_code`: extracted from the corresponding identity fields in C and independently checked against ATOM resSeq, resName, chainID, and iCode in I. `scan_source_csv_line` is the physical line number in C, including the header.

## Experimental fields and deduplication

| Site | ΔTm (°C) | SEM (°C) | Exact experimental N | Replicates reported in P | original_data_source | Source pages / figure | extraction_method |
|---|---|---|---|---|---|---|---|
| H31 | | | | N≥3 | Wilkerson 2020, newly measured | P PDF 3/4; journal pages 5119/5120; Figure 2 | Text and caption transcription; not digitized |
| S44 | | | | N≥3 | Wilding 2018, reused by Wilkerson 2020 | P PDF 3/4; journal pages 5119/5120; Figure 2; ref. 13 | Text and caption transcription; not digitized |
| N53 | | | | N≥3 | Wilding 2018, reused by Wilkerson 2020 | P PDF 3/4; journal pages 5119/5120; Figure 2; ref. 13 | Text and caption transcription; not digitized |
| L91 | | | | N≥3 | Wilding 2018, reused by Wilkerson 2020 | P PDF 3/4; journal pages 5119/5120; Figure 2; ref. 13 | Text and caption transcription; not digitized |

- **ΔTm definition**: Experimental Data and Figure 2 on P PDF page 4 define `Tm,treatment - Tm,control`, with the article's cysteine-free T4L as the control. This is not the effect of a PEGylated conjugate.
- **Why ΔTm is blank**: Figure 2 bar heights have not been formally digitized, and neither supplied PDF provides a directly transcribable numerical table. No previous or current visual estimates are used.
- **Why SEM is blank**: The Figure 2 caption and main text identify the error bars as standard error (SEM), but their values have not been formally digitized. `uncertainty_type=SEM` records the uncertainty type, not an available numerical value.
- **Why exact N is blank**: P reports at least three independent replicates, without exact per-variant thermal-stability experimental counts. The CSV values `experimental_n_reported=N>=3` and `experimental_n_minimum=3` come from the main text and Figure 2 caption on P PDF page 4. The lower bound 3 is not treated as an exact N.
- **MD replicates are excluded from experimental N**: S PDF page 1 reports nine runs for H31 and six for the other systems; these are simulation replicates. Figure S2 on S page 3 also describes the nine short simulations. These counts are not entered in `experimental_n_exact`. The RMSF uncertainty on S page 5 is not entered as the SEM of ΔTm.
- **Original data source**: Experimental Techniques on P PDF page 3 and the Figure 2 caption on page 4 explicitly identify the sources. The original Wilding article was not supplied, so source verification is limited to Wilkerson's explicit attribution, as recorded in `original_source_access`. Reference 13 on P PDF page 7 is Wilding et al., *The locational impact of site-specific PEGylation: streamlined screening with cell-free protein expression and coarse-grain simulation*, *ACS Synth. Biol.* 2018, 7, 510–521, DOI [10.1021/acssynbio.7b00316](https://doi.org/10.1021/acssynbio.7b00316).
- **Deduplication rule**: The CSV contains one row per site. `deduplication_key` combines the original publication, cysteine-free T4L, substitution site, unconjugated state, and thermal-shift endpoint. If S44/N53/L91 are later combined with a Wilding 2018 dataset, retain their original source identity rather than counting them again as independent measurements newly made in 2020. The key is a manually assigned provenance identifier for this pilot, not an author-provided sample ID. Raw measurement files and sample-level data are not available. Shared controls and sites in the same protein do not automatically constitute statistically independent observations.
- `incorporation`, `soluble_expression`, `activity`, and `conjugation` remain blank, with reasons in the CSV. These endpoints are not inferred from stability, the article's discussion of surrogate measures, or RANA geometric features. `original_data_source` identifies the original reporting publication, not an experimental raw-data file that was not supplied.

## File hashes and verification

The following SHA-256 hashes were computed directly from the original bytes of each file to identify the inputs to this extraction. They are not additional experimental values.

| File | SHA-256 |
|---|---|
| C | `84e0e69451dd06d2f443d23921b0936f6025fe9300af4ffe20cc179adb3a0d15` |
| I | `dbc42255d5f5670725b4f93c00bc58b9996d32437172949081aa0a493caf0825` |
| M | `53cd65ab834522ab2ff66f2c30d6e23fb162b1eb79f5c7185c0ddf940bdbd100` |
| P | `ce06cf47c48c00e8e4e81808e814c2928f71414f0c3fc734f6fb41e6788d6f16` |
| S | `a438681a0cdb820f0b7b09101542fc37fbc85ef51ce5c2d3fb9251c40282f709` |
| R | `1e4aab86718c1bc49355be0280066580f1d3332586dccfcd0586a2b74387da55` |

Each CSV row includes the path, SHA-256, and line number for C; the path and SHA-256 for I; the experimental PDF path and page/figure locations; and reasons for missing values. Direct numerical sources retain their original field names. The derivations of `n_acceptable_rotamers` and `rank_population_n_scored` are described above.

Verification covered unique identity matches for all four sites; agreement of the input hash with M and R; agreement of the C hash with R; consistency of RSA arithmetic, packing counts, rotamer counts, and fractions; and agreement of the existing tiers and three full-scan ranks with the current code rules. These are extraction-consistency checks. No new scan or significance test was run.

## Limitations

This is a provenance and feature pilot for four published sites in one protein, not a complete M5 benchmark. It supports no conclusions about performance, significance, correlation, calibration, or generalization. Quantitative comparison is pending Figure 2 digitization. Exact per-site experimental replicate counts were not reported; the available information is N ≥ 3.

RANA's fixed-parent-structure geometric scores are not thermal-stability predictions. They do not model relaxation, salt-bridge loss, folding free energy, or changes in experimental conditions. Low clash does not imply ΔTm near zero. All four rows are retained; no site is removed because of its tier or experimental trend. The known insertion-code forwarding omission remains unfixed. All four sites here have blank insertion codes, so this pilot cannot validate behavior for nonblank insertion codes.

Scientific code, scoring constants, thresholds, the rotamer library, original inputs, scan results, and the seven exploratory scripts were not changed. No parameters were tuned against experimental outcomes, and no commit, push, or PR was created for this pilot.
