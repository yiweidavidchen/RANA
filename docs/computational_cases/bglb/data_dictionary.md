# Curated result fields and source meanings

All results describe β-glucosidase B (BglB) from Paenibacillus polymyxa, 2O9P A
H376Q/G377R engineered apo reference, using input PDB author numbering. Blank
insertion codes remain empty fields. Files are UTF-8 CSV/JSON; empty role fields
mean no independently assigned role in this case, not proof of no function.

## per_site.csv

The complete 445-row table copies same-named fields directly from one raw
`ranked.csv`. Exact input/output hashes are in `execution_summary.json` and
`curation_metadata.json`; `source_scan_row_1based` includes the CSV header as row 1.
`source_scan_sha256` identifies the raw scan and `source_prepared_sha256` its
protein-only input. Full raw files remain in the documented ignored run directory.

- `chain`, `residue_number`, `insertion_code`, `residue_name`: original structural
  identity and parent. `site_label` joins the original parent letter and author
  number for display; it is not Foldit renumbering.
- `status`, `reason`: original CLI diagnostics, including failed/skipped if any.
  This run has 445 scored and zero failed/skipped. Coordinate absences are in a
  separate table, not silently missing scan rows or experimental negative labels.
- `sasa_abs`: original absolute residue SASA in Å²; `rsa`: existing reference-area
  normalized SASA, dimensionless; `ca_neighbors_8a`: existing packing count.
- `min_steric_score`, `mean_steric_score`, `median_steric_score`: original sampled
  overlap scores in Å², not energies or stability predictions. `best_chi1/2` are
  original sampled angles in degrees. `n_rotamers` is 12 for each scored row.
- `low_clash_fraction`: original fraction with steric score <=10.0 Å².
  `low_clash_rotamer_count` is the integer numerator recomputed only from the
  same raw `rotamer_scores` and cutoff, checked against the fraction. No score
  or threshold changes. Neither field means experimental acceptability or success
  probability, nor exhaustive conformational-space coverage.
- `candidate_tier`, `steric_rank`, `rsa_rank`, `rotamer_robustness_rank`,
  `special_residue_flag`, `ranking_reason`: unchanged CLI outputs, preserving
  minimum/competition ties and Gly/Pro cautions. Packing is displayed but no new
  packing rank or combined score is introduced.
- `maintainer_functional_flag`: membership in the maintainer's verified 11-site
  context list. False means unlisted, not functionally safe. `foldit_context_label`
  is a cross-reference only; the main output identity remains PDB author numbering.
  `reference_role_annotation/evidence` retain UniProt reference roles and original
  evidence codes where present. Original detailed role sources remain in
  `candidate_audit.json.functional_mappings` and `site_mapping.md`.
- `background_context`: H376Q or G377R at the two engineered reference positions.
- `in_inclusive_top10_*`: independent list membership using the tenth order
  statistic and all boundary ties. These Boolean displays do not alter scores,
  tiers, ranks or eligibility and do not create a combined recommendation.

## Subsets and absence ledger

`candidate_overview.csv` is the union of the three independent inclusive lists,
sorted by structural identity. `top_list_memberships.csv` retains each independent
rank/metric membership; `top_lists.json` records boundaries, actual sizes and all
identities. `functional_context.csv` contains all eleven annotated sites regardless
of geometry; `background_context.csv` retains Q376/R377. All subset values copy
the full table exactly.

`coordinate_absences.csv` retains all nine explicitly unobserved author positions
from 2O9P mmCIF `_pdbx_unobs_or_zero_occ_residues`: -5 through 3. Their absence
does not indicate an experimental failure. Source mmCIF URL/hash is in the
original `source_manifest.json`; no coordinate filling or renumbering was done.
