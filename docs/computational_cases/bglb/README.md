# M6.4 BglB pAzF computational application

Protein: **β-glucosidase B (BglB) from Paenibacillus polymyxa**.

**Status: one accepted protein-only 2O9P A-chain scan completed; 445 scored,
zero failed/skipped.** Geometric tiers: 112 favorable, 175 limited, 158 unfavorable.
Case selection originated from the maintainer's BglB research experience.
This is an independent RANA computational application. It does not establish
that the maintainer's BglB preprint, UC Davis Siegel Lab or D2D experimental
system has conducted ncAA experiments. None of these inputs is asserted to be
the maintainer's experimental construct. No private paths, HPC models or
unpublished experimental data were used.

The accepted and executed single main input is **2O9P chain A**, explicitly labeled as
the **H376Q/G377R engineered substrate-free (apo) reference**. It is not natural
WT, D2D standard or the maintainer's experimental construct. Input PDB author
numbering is retained. The supplied D2D file is a confirmed public **holo candidate**, with
unresolved preparation history; it is not treated as an experimental apo model
or an independent new experimental determination.

- [Three-input identity, provenance and coordinate review](structure_review.md).
- [Results, all functional-context sites and limitations](results_report.md).
- [All 445 curated sites](results/per_site.csv),
  [inclusive top-list union](candidate_overview.md), and
  [execution/source summary](execution_summary.json).
- [Reproduction and validation](reproduction.md) and
  [curation provenance](curation_metadata.json).
- [Post-review reliability revision](reliability_revision_2026-10-25.md),
  [current tool approval](tool_revision_2026-10-25.json), and
  [revised curation provenance](curation_revision_2026-10-25.json).
  The original execution/validation records remain unchanged; this revision
  checks accidental source/data changes and is not a tamper-resistant security mechanism.
- [Foldit/structure mapping and functional annotation sources](site_mapping.md).
- [Accepted scan/display plan](case_plan.md),
  [original pre-scan configuration record](case_plan.json), and
  [acceptance/frozen execution plan](execution_plan_2026-10-25.json).
- [Inspection methods and limitations](methods.md).
- [Full curated audit with complete sequences](candidate_audit.json),
  [complete position crosswalk](residue_crosswalk.json), and
  [source URLs, timestamps and SHA-256](source_manifest.json).
- [Public document manifest](file_manifest.json); raw inputs are excluded.

Main was safely fast-forwarded to `2c690edaae77d4160134c6382abf00901d88d529` (PR #6 merge), then branch
`codex/m6-bglb-computational-case` was created. All prior untracked files were
preserved. Raw source files and detailed inspection scripts/results are in the
new ignored directory `data/processed/m6_bglb_structure_review_2026-10-25/`.

The actual scan, source/prepared inputs, original output, logs, exact commands,
executed source snapshots and pre-scan documents are retained separately in
`data/processed/m6_bglb_pazf_case_2026-10-25/`. Scientific code and frozen parameters
were unchanged. Tests and reproduction verify software/data handling, not
experimental predictive performance or a fresh environment.

The scan is **protein-only**: source ligand presence does not imply RANA includes
ligand sterics. A ligand-removed holo model retains the holo conformation and
cannot be called an experimental apo structure. 2JIE remains a mechanism/ligand
reference without a new scan. 2Z1S, 2O9R and 2O9T are future candidates pending
review only; they were not downloaded, compared or analyzed in this phase.
