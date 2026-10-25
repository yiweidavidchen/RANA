# T4L same-background structure-sensitivity results

These are descriptive results from three reference inputs with identical full
C54T/C97A entity sequences. They evaluate input dependence, not independent
experimental prediction. [Selection/mapping](README.md#structure-selection-and-mapping)
and the [pre-scan frozen plan](analysis_plan.md) define the scope.

## Inputs and completeness

1L63, 1LW9 and 219L retain only chain-A protein heavy atoms with original
coordinates and alternate records. All selected biological assemblies are
identity-operation monomers, so there are no omitted protein assembly partners.
Waters/ions/other components are excluded consistently. The 2FG8-specific
preparation profile was not used. Retained all-altloc atom counts are
1,292 / 1,328 / 1,308; the extra alternative records in 1LW9 are not extra
simultaneously scored conformers. Existing parser-selected atoms are used.

All **490 modeled sites** scored successfully with 12 rotamers: 162 in 1L63,
164 in each complete structure. There are no failed/skipped rows. The common set
contains **162 sites**, or 486 structure-site records. N163/L164 are absent from
1L63; their four successful rows in the complete structures are retained outside
the main comparison. The [492-row ledger](results/site_eligibility.csv) explicitly
records these absences/exclusions. No other parent mismatch or missing heavy
atom was found among modeled residues.

The newly scanned 1L63 CSV is byte-identical to the historical M5 CSV (SHA-256
`84e0e69451dd06d2f443d23921b0936f6025fe9300af4ffe20cc179adb3a0d15`).
The freshly downloaded original PDB also matches the historical input bytes.
This is new directly recorded execution evidence; it does not backfill the
historical sidecar's missing execution provenance or overwrite any M5 file.

## Broad rank ordering and top-list sensitivity

Across the three predeclared pairs, common-set Spearman rho ranges are:

- RSA: **0.9866–0.9930**.
- Packing: **0.9696–0.9808**, explicitly a comparison-only feature ranking.
- Minimum steric score: **0.9419–0.9693**.
- Low-clash fraction: **0.9637–0.9788**.

These describe fairly consistent broad ordering within this restricted sample;
they do not show invariant recommendations. [All pairwise coefficients](results/pairwise_metrics.csv)
are reported, including ties, without significance tests or picking a best pair.
The three native rank metrics and the comparison-only packing rank remain
separate; no combined rank was introduced.

Inclusive top-10 results illustrate the difference. RSA shares 8–9 of ten sites.
Minimum-steric-score lists share only **6–8 of ten**, with Jaccard **0.429–0.667**.
Low-clash boundary ties produce sets of **10 / 12 / 11** sites and pairwise
Jaccard **0.692–0.769**. Packing ties produce sets of **24 / 21 / 23** sites,
with Jaccard **0.800–0.880**. Site lists and actual denominators are in the
[top-list CSV](results/top10_overlap.csv); tie-expanded lists are not percentages
of a fixed ten. All comparisons use re-computed common-set ranks, while original
full-structure CLI ranks remain separately labeled in the long table.

## Per-site changes and tiers

**143/162 sites retain the same tier; 19 change tier** across the three inputs.
Pairwise off-diagonal transition counts are 14 (1L63/1LW9), 10 (1L63/219L), and
14 (1LW9/219L). The complete-input pair still has 14 changes on the same common
set, so differences cannot all be attributed to 1L63's missing tail. This does
not isolate the contributions of individual modeling/crystal differences.

Across-structure per-site range medians/maxima, read directly from
[site_ranges.csv](results/site_ranges.csv), are:

- RSA: median **0.01714**, maximum **0.34395**.
- Packing: median **0**, maximum **4** neighbors.
- Minimum steric score: median **0.68581 Å²**, maximum **35.82140 Å²**.
- Low-clash fraction: median **0**, maximum **1/3** of the 12 sampled rotamers.

The largest minimum-score range occurs at **N81**, from approximately 5.65 to
41.47 Å², with a limited/unfavorable tier change. Maximum common competition-rank
ranges are 47 (RSA), 80 (packing), 102 (minimum score) and 55 (fraction). These
site-specific changes remain visible rather than being removed as inconvenient
outliers. No post hoc "stable-score" cutoff was fitted.

Tier-stable only means these inputs produce the same heuristic label. Large
numerical changes can occur within a tier, while small changes near a threshold
can change the label. The [transition table](results/tier_transitions.csv) and
[rank-range plot](results/rank_ranges.svg) expose both limitations.

## Six M5 pilot sites

All six retain their tiers, with all values and both rank definitions in the
[18-row table](results/m5_six_sites.csv) and [figure](results/m5_six_sites.svg):

- K16, S44, N53 and K135 remain `geometry_favorable`.
- H31 remains `geometry_limited`; fraction remains 4/12.
- L91 remains `geometry_unfavorable`; fraction remains zero. Its minimum score
  ranges from approximately **11.89 to 13.63 Å²**, and packing changes from 9 to 10.
- K16 illustrates numerical dependence despite tier stability: RSA ranges
  **0.359–0.526**, fraction **10/12–11/12**, and minimum score **0.297–0.585 Å²**.

No experimental ΔTm values or experimental-performance correlations were used.
Tier stability for this retrospectively selected six-site subset does not make
it an independent validation set or prove accurate stability prediction.

## Evidence and limits

Input selection and plan hashing preceded scanning. Copied atom coordinates and
identities were unchanged; scientific package hashes and all parameters are
recorded. The original execution summary records ten targeted tests; the
[analysis revision](analysis_revision_2026-10-24.md) records 38 passing targeted
tests after the review fixes. From the public common-site table, six
comparison CSVs and all six plot files were reproduced byte-for-byte in the
current environment; the full eligibility ledger is separately provided.
Re-analysis from the unchanged original scans preserved all seven comparison
CSVs byte-for-byte, including eligibility reasons and all scientific results.
Only SVG trailing whitespace and analysis provenance changed; original scan
execution records and the prior analysis were retained.
The full unrelated pytest suite was not repeated. Actual runs used the existing
Windows development venv, not a new environment/cross-platform validation.

Same deposited sequence removes background substitutions from the main
comparison, but not missing-terminal, altloc, resolution/refinement, crystal
condition or representation differences. No different-background result was
pooled or interpreted as pure conformation. All three share a narrow crystal
setting; no solution ensemble, crystal-neighbor or multi-structure completeness
claim follows. The old exact-experimental-construct uncertainty is unchanged.
No structure was re-selected for agreement with experiment; no thresholds,
rotamers or algorithms were tuned. Cross-structure consistency is not
experimental success probability, accuracy or generalization evidence.

See [execution_summary.json](execution_summary.json) for source/code/environment
hashes and [data_dictionary.md](data_dictionary.md) for exact fields and formulas.
