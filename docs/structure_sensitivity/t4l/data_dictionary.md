# Data fields and provenance

All positions refer to author chain/number/insertion code, verified against the
164-residue entity sequence. The blank insertion code is retained as an empty
CSV field. No PDB number offset was applied. Files are UTF-8 CSV with a header;
blank correlation values mean constant/insufficient rank vectors, accompanied by
`missing_reason`. No other experimental missing values are imputed.

## Source fields and comparison ranks

`results/metrics_long.csv` includes only the intersection of mapped same-parent
successfully scored sites. Each row has `pdb_id`, chain, residue number, insertion
code and three-letter parent; `site_label` is an author-number convenience label.

- `rsa`: original CLI relative SASA, normalized by the existing residue-specific
  reference area; dimensionless. `ca_neighbors_8a`: original Cα neighbor count
  within 8 Å, excluding self. `min_steric_score`: original minimum sampled steric
  overlap score, Å². `low_clash_fraction`: original fraction of 12 sampled
  rotamers with score ≤10.0 Å². No new geometric feature is computed here.
- `candidate_tier`, `n_rotamers`: copied CLI fields. Every common row is `scored`;
  complete statuses/reasons are in the eligibility ledger and original full scans.
  Existing glycine/proline caution flags and ranking explanations remain in the
  full raw CSVs; a tier is not evidence of experimental acceptability.
- `original_full_rsa_rank`, `original_full_steric_rank`,
  `original_full_rotamer_robustness_rank`: copied from the same-named CLI rank
  without the `original_full_` prefix. Denominators are 162/164/164 scored sites,
  so these are not the common-set comparison ranks.
- Each `*_common_rank_min`: re-computed minimum/competition rank among 162 common
  sites. RSA/fraction descend, packing/minimum steric ascend. The packing rank is
  comparison-only; it is not an additional native CLI rank or combined score.
- `source_scan`: path relative to local
  `data/processed/m6_t4l_structure_sensitivity_2026-10-24/`; these full scans are
  deliberately ignored, not broken public-download links. `source_scan_sha256`
  identifies exact bytes, `source_scan_row_1based` counts the header as row 1,
  and `source_prepared_sha256` identifies the input. Original metric/rank field
  names are preserved so joins back to the full CSV are explicit.

## Derived files

In the eligibility ledger, `absent_from_input` means the frozen coordinate audit
marks the position unmodeled. A modeled position missing its scan row is an
integrity error and stops analysis; it never silently reduces the common set.
Original `failed`/`skipped` statuses and diagnostics remain distinct from
parent/mapping mismatches. Only the three existing geometric tier labels are
accepted for scored rows; transition tables must account for every common site.

`site_ranges.csv` reports the min/max/range of each scalar and common competition
rank across all three structures. Tier columns are copied labels; `tier_stable`
means label equality across all inputs, not experimental correctness.
`m5_six_sites.csv` is the K16/H31/S44/N53/L91/K135 subset of the long table, with
all fields preserved. H31 is the Wilkerson pilot label; the other five are
Wilding labels. No experimental values, errors or correlations enter this study.

`pairwise_metrics.csv` reports all three pairs × four fields. Spearman rho is the
Pearson correlation of average ranks, preserving ties, with no p-values.
`top10_overlap.csv` takes every site at least as good as the 10th order statistic,
reports both actual set sizes, intersection/union, Jaccard and site IDs. Packing
has its comparison-only role explicitly labeled. Do not divide overlap by ten
when a boundary tie expands a set.

`tier_transitions.csv` includes every existing tier × tier combination for every
pair, including zero counts. Each pair sums to 162; off-diagonal counts are
input-dependent label changes. `site_eligibility.csv` has 492 potential positions
(164 × 3), including the two absent 1L63 terminal residues. Four scored terminal
rows from the complete structures remain in the raw scans but outside the common
comparison. Missing/unscored/excluded sites are not experimental negatives.

The audit selection and mapping CSVs provide full sequences, missing atom/residue
diagnostics and coordinate mapping provenance. Heavy-atom completeness uses
standard backbone/sidechain names; terminal OXT/hydrogens are optional, not
reconstructed. Atom-level audit uses PDB/mmCIF serialization tolerance 0.0006 Å;
the copied prepared inputs require zero coordinate difference to their source
PDBs. Raw coordinate files and complete scans/sidecars remain in the new ignored
directory; the public source manifest pins URLs, retrieval times and hashes.
