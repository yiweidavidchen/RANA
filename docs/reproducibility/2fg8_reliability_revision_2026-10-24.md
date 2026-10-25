# M6.2 wrapper reliability revision — 2026-10-24

This revision addresses the two submission-review reliability findings for the
**pinned 2FG8 assembly-1 profile and original target A**. It adds no scientific
algorithm, threshold, seed, rotamer library or structure-sensitivity change.
Arbitrary structures, custom profiles and cross-platform operation are not
verified capabilities.

## Runtime checks

The [comparison script](compare_2fg8.py) uses explicit exceptions rather than
runtime assertions. Overwrite refusal, run-status/profile guards, finite-array
checks and structure/scan comparisons remain active under `python -O`. Report
creation is exclusive, including if a report appears after the initial check.

The [generation driver](reproduce_2fg8.py) checks each CSV after a zero CLI exit.
It requires the profile's complete 174-site identity set (chain, author number,
blank insertion code and parent residue), no duplicates, all statuses `scored`,
empty scoring diagnostics, a CA, 12 finite numeric rotamer scores, and finite
required scores, ranks and structural features. Missing/malformed files and
fields are rejected. Metadata must agree on input/CSV hashes, frozen
configuration, status/tier counts and sampling.

`run.json` records each successful output check. Errors retain partial artifacts
and record their stage and reason where disk access permits; unhandled errors
exit nonzero. Code-source preflight errors now also receive a failure journal.
Only after both checks pass does status become
`scans_completed_pending_separate_comparison`. **Output completeness is not a
passing historical comparison or scientific validation.**

## Targeted verification

Executed from the repository root in the existing development venv:

```text
.venv/Scripts/python.exe -B -m pytest tests/test_prepare_structure.py tests/test_2fg8_reproduction_scripts.py -q --basetemp=data/processed/m6_portable_2fg8_2026-10-24/revision_tests_final -o cache_dir=data/processed/m6_portable_2fg8_2026-10-24/revision_cache_final --junitxml=data/processed/m6_portable_2fg8_2026-10-24/revision_tests_final.xml
```

Result: **92 passed, 0 failed/errors/skipped, 0 warnings reported**, 124.11 s.
This consists of 14 unchanged conversion cases and 78 new wrapper cases.
There are 26 actual interpreter subprocess cases, including 13 under `-O`;
their data and scanner responses are synthetic. No real scoring CLI was invoked.
Tests cover overwrite/run/profile guards; structure and score/tier/rank/rotamer
differences; missing, duplicate or incorrect sites; failed/skipped diagnostics;
NaN/Inf and missing fields; metadata mismatches; valid outputs; and nonzero
interpreter exits when a fake zero-exit scanner produces invalid output.

Environment: Windows x86_64, CPython 3.13.12,
pytest 9.1.1, NumPy 2.5.4, pandas 3.0.6,
Biopython 1.88, RDKit 2026.9.1.
No dependencies were downloaded or installed. The full unrelated suite,
structure download, actual preparation and complete real scans were not rerun.
The JUnit record is local and ignored at `data/processed/m6_portable_2fg8_2026-10-24/revision_tests_final.xml`; its hash and the
current script/test hashes are in the [JSON record](2fg8_reliability_revision_2026-10-24.json).

The revised output validator was also applied read-only to both previously
generated M6.2 CSVs and their metadata/prepared inputs. Each passed with 174
scored sites and 2,088 finite rotamer scores. These checks read existing outputs;
they did not run preparation/scanning again or alter the original execution
provenance. CSV/metadata hashes are recorded separately in the revision JSON.

## Preserve the original execution record

The earlier [real-run summary](2fg8_validation.md) and
[original JSON](2fg8_validation.json) are unchanged. They describe the original
fresh-environment preparation, real assembly/monomer scans and historical
comparison, **using the original script versions**. Current revised script
hashes must not be substituted into those historical records.

Original driver SHA-256:
`32d650d7c1580cdcf6e0ddaefda3c2b7e06ab04af3fe5e594989478ab3d97401`.
Current driver SHA-256:
`e530d2776024cb3c4acedbcc3b64ecb772efacd27a3fe245284dbc8c9bbf2b34`.

Original comparator SHA-256:
`fb6f84089f46c1412df2a289d49806f9ed705ebbb10ab7a571bf845b742d3298`.
Current comparator SHA-256:
`13065e4116d83a6acb2353943d9a0a92a2bea914bbc4b2102cf85a48cdc88a3a`.

All 173 protected pre-existing files, M5 frozen records and seven untracked
exploratory scripts remain unchanged. Current checks establish wrapper
reliability on synthetic cases; they do not establish new real-run,
cross-platform or experimental validation. Experimental PDB/construct identity
uncertainty is retained. See the [guide](README.md) and
[submission manifest](submission_manifest.json) for delivery boundaries.
