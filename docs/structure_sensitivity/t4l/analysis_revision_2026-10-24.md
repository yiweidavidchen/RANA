# M6.3 analysis revision: 2026-10-24

This revision fixes pre-commit review findings R1–R4 without changing geometric
scoring, thresholds, sampling, structures or scientific comparisons. The
[machine-readable validation record](analysis_revision_2026-10-24.json) gives
source hashes, commands, environment, output hashes and exact SVG differences.

## Changes

- Before CSV parsing, verify the actual plan against the completed run, all
  frozen dependencies (including the coordinate audit and mapping), and the
  three scan CSVs, sidecars and prepared inputs against their recorded hashes.
  Mismatches fail; expected hashes are never updated automatically.
- Use the coordinate audit's modeled flag to distinguish absent coordinates
  from missing scan output. A missing row for a modeled site fails rather than
  reducing the common set. Keep failed/skipped and parent/mapping diagnostics.
- Reject tiers outside the existing three labels. Check complete pairwise
  transition totals and stable/change identities and counts at runtime.
- Normalize SVG trailing whitespace at export; no figure tokens, numbers,
  labels or scientific meaning change. Repeated export remains deterministic.

All production checks use explicit exceptions, not assertions. Negative tests
exercise normal Python and `python -O`, including nonzero process exits.

## Actual validation

**38 targeted tests passed**, with no failures, skips or reported warnings.
The full unrelated suite was not repeated. Existing Windows Python 3.13.12 and
the recorded pinned analysis packages were used; no fresh environment was tested.

Analysis was regenerated from the original three real scans in a new directory,
then independently regenerated from the public common-site table. No structure
was downloaded and no scoring scan was repeated. All **seven CSVs** are
byte-identical to the pre-fix versions: scientific fields, original/common ranks,
eligibility reasons, common set, tier counts, correlations and top-list results.
There remain **162 common sites, 143 tier-stable and 19 changing sites**; the six
M5 sites remain tier-stable. All three PNGs are byte-identical. Each new SVG is
exactly its old bytes after line-trailing whitespace removal, with updated hashes.
The curated reproduction matches six CSVs plus six figure files byte-for-byte.
New analysis metadata records the revised script and execution time.

## Commands and provenance

Run from the repository root with the documented analysis environment:

```text
python -B -m pytest tests/test_t4l_structure_sensitivity.py -q -o cache_dir=data/processed/m6_t4l_structure_sensitivity_2026-10-24/analysis_revision_2026-10-24/pytest_cache --basetemp=data/processed/m6_t4l_structure_sensitivity_2026-10-24/analysis_revision_2026-10-24/pytest_tmp --junitxml=data/processed/m6_t4l_structure_sensitivity_2026-10-24/analysis_revision_2026-10-24/tests.xml
python -B docs/structure_sensitivity/t4l/analyze.py --run-dir data/processed/m6_t4l_structure_sensitivity_2026-10-24/run --output data/processed/m6_t4l_structure_sensitivity_2026-10-24/analysis_revision_2026-10-24/from_scans
python -B docs/structure_sensitivity/t4l/analyze.py --curated docs/structure_sensitivity/t4l/results/metrics_long.csv --output data/processed/m6_t4l_structure_sensitivity_2026-10-24/analysis_revision_2026-10-24/from_curated
```

These actual output directories already exist and are intentionally refused on
another run; choose new directories for reproduction. The detailed local
revision directory is `data/processed/m6_t4l_structure_sensitivity_2026-10-24/analysis_revision_2026-10-24/`, including `tests.xml`, `verify_revision.py`,
`from_scans/`, `from_curated/` and the pre-fix snapshot `before/`.

Scientific package Git source remains
`bc63d0a74036e702c698d349862c976059707ea3`. The original run record and all 18
scan/execution files, including the original wrapper snapshots, remain unchanged.
[execution_summary.json](execution_summary.json) remains the historical initial
execution/analysis summary; its original script/test hashes were not backfilled.
Current analysis source SHA-256 is `ddde046a59f2616231e128ab76a709faa3acdca0c63c8dce43345a6ec1ffe35a`; the previous
source SHA-256 is `6d4b09f28d70d03ff629df81892073e56156a0d0fe180753a83d36b040c58081`. Both are recorded separately.
This is software/data-integrity verification of a restricted computational
input-sensitivity study, not experimental predictive validation.
