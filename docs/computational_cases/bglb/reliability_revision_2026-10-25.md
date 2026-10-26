# BglB post-review reliability revision (2026-10-25)

This revision fixes case tooling only. It does not change scientific scoring,
sampling, thresholds, tiers, rotamers, input coordinates or candidate selection.
It detects accidental provenance/content inconsistencies; it is not a
tamper-resistant security mechanism. No real scan or download was repeated.

## Version and evidence boundaries

The original scan remains governed by the pre-scan
[execution plan](execution_plan_2026-10-25.json) and
[execution summary](execution_summary.json). Its archived runner raw SHA-256 is
`2c97e23b9e1dd406d812fd933a658bb5dfb988f630147de4738347ce8156b373`.
The original [curation record](curation_metadata.json), 25-test record and local
verification record remain unchanged. They do not describe the revised tools.

[Tool approval](tool_revision_2026-10-25.json) identifies the current runner and
curator separately and binds scientific Python source content to the original
approved Git version `2c690edaae77d4160134c6382abf00901d88d529`. Missing source
records, changed source content, an unapproved archived runner, and an edited
archived plan fail even when their self-reported hashes are updated. Recorded
execution commits must contain the same scientific source set and content.
Later documentation commits are allowed without changing scientific approval.
New runs explicitly record the revised tool version; the original run is never
relabeled as having used it.

## Numeric, text and checkout rules

Scored rows require finite numeric values, including `best_chi1` and `best_chi2`,
integer residue numbers/counts/ranks, expected identities/parents, legal statuses
and tiers, and exactly 12 finite rotamer scores. The existing minimum, mean,
median and low-clash consistency checks remain. Missing rows, required fields,
diagnostics or invalid values fail before public curation. Diagnosed failed or
skipped rows remain explicit rather than being dropped.

JSON is read/written explicitly as UTF-8; generated reports/CSVs also declare
their encoding. The protein name's β is preserved. Source PDB parsing remains
explicit ASCII, as required by the profile.

The named algorithm `sha256-utf8-crlf-to-lf-v1` validates UTF-8, replaces only
CRLF bytes with LF, and hashes the resulting bytes. It applies only to current
tool Python files, declared public plan/dependency text, and scientific Python
source inventories. It does not trim spaces, tabs or other content. Necessary
paths are covered by local `.gitattributes`; no global Git setting or historical
file was normalized. Curated CSVs have `-text` to preserve their byte hashes.

Original structures, scan CSVs, sidecars, historical run records and archived
sources retain raw byte hashes. A historical scientific-source digest must
match the approved Git content's exact LF or CRLF serialization; no changed
code content is accepted. Raw archived runner/plan hashes are checked as well
as their approval, not replaced by normalized hashes or current-tool hashes.

## Validation and re-curation

**58 targeted tests passed**, zero failures/errors/skips/reported warnings.
Tests cover missing/incomplete source records, source and archived-script
replacement, self-reported hash updates, missing/nonfinite/nonnumeric angles,
normal and optimized Python, LF/CRLF public-text exports, content-edit rejection
and explicit UTF-8 reading under non-UTF-8 default mode. The fixture runs are
simulated validation, not additional scientific scans.

From the repository root (new output directory required):

```text
python -B -m pytest tests/test_bglb_case.py -q
python -B docs/computational_cases/bglb/curate_case.py --run-dir data/processed/m6_bglb_pazf_case_2026-10-25/run --output-dir data/processed/m6_bglb_pazf_case_2026-10-25/reliability_revision_2026-10-25/curation_final
```

These local directories already exist. Use a different output name when
repeating; overwrite remains refused. New readers need their own complete raw
run for re-curation; public curated tables alone do not supply it. See
[reproduction instructions](reproduction.md) for obtaining public input and
generating a new run. No paper PDF or private coordinate path is required.

Re-curation of the existing raw scan produced **nine byte-identical data/report
artifacts**: six CSVs, top-list JSON and two Markdown reports. All 445 identities,
parents, scientific fields, original ranks and functional annotations are
unchanged. Inclusive top-list sizes remain **10 / 10 / 20**, with **31** sites in
the union; tiers remain **112 favorable / 175 limited / 158 unfavorable**.
Only new curation provenance has new tool hashes/timestamps. It is published as
[curation_revision_2026-10-25.json](curation_revision_2026-10-25.json), leaving the
original curation metadata intact.

The [validation summary](reliability_validation_2026-10-25.json) records commands,
environment, comparison hashes and preservation counts. Detailed local evidence,
tests XML, before-revision snapshots and generated outputs are under
`data/processed/m6_bglb_pazf_case_2026-10-25/reliability_revision_2026-10-25/`.
Original scan and validation records remain in their previous directories.

This is software/provenance and data-integrity validation. It is neither a
fresh-environment full-scan verification nor experimental predictive validation.
The single engineered apo reference, protein-only environment, 12 sampled
rotamers and heuristic tiers retain all previously stated scientific limits.
