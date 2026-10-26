# Execution, curation and reproduction

Protein: β-glucosidase B (BglB) from Paenibacillus polymyxa. Only the accepted
2O9P A-chain H376Q/G377R engineered apo reference was scanned, using PDB author
numbering. This does not identify the maintainer's experimental construct.

## Actual commands

From the repository root, using the existing development venv's Python:

```text
python -B docs/computational_cases/bglb/run_case.py --source-pdb data/processed/m6_bglb_structure_review_2026-10-25/sources/2O9P.pdb --output-dir data/processed/m6_bglb_pazf_case_2026-10-25/run
python -B docs/computational_cases/bglb/curate_case.py --run-dir data/processed/m6_bglb_pazf_case_2026-10-25/run --output-dir data/processed/m6_bglb_pazf_case_2026-10-25/curation_v1
python -B docs/computational_cases/bglb/curate_case.py --run-dir data/processed/m6_bglb_pazf_case_2026-10-25/run --output-dir data/processed/m6_bglb_pazf_case_2026-10-25/curation_reproduction
python -B -m pytest tests/test_bglb_case.py -q -o cache_dir=data/processed/m6_bglb_pazf_case_2026-10-25/pytest_cache --basetemp=data/processed/m6_bglb_pazf_case_2026-10-25/pytest_complete_tmp --junitxml=data/processed/m6_bglb_pazf_case_2026-10-25/tests.xml
```

The actual absolute interpreter/CLI arguments, timestamps, input hashes and raw
metadata remain in `data/processed/m6_bglb_pazf_case_2026-10-25/run/run.json`, not rewritten into a later execution.
Its public summary is [execution_summary.json](execution_summary.json). The
wrapper's archived source and execution plan are in `run/executed_sources/`;
curation sources are separately retained under each curation's `executed_sources/`.
All directories above already exist; wrappers reject overwrite. Reproduction
must use new output names. Only one real scan ran; the last curation command
reused the original scan and produced nine identical data/report artifacts.

**25 targeted tests passed**, no failures/skips/reported warnings. All 445 rows
were scored with 12 finite rotamer scores each (5340 total); raw/curated scientific
fields and ranks agree exactly. The 11 functional flags and two background sites
were joined only afterward. Input preparation preserved all 3626 heavy-atom
records and coordinates exactly, removing the 138 original waters. No organic
ligand was present in this deposited apo input. No structure download was needed
in this phase; the already-hashed public 2O9P cache was used.

Those commands and 25-test result describe the original archived tools, not the
revised tools now at these paths. The separate
[reliability revision](reliability_revision_2026-10-25.md) records the current
58-test result, new curation command and unchanged data comparison. It does not
backfill current hashes into the original execution or claim another real scan.

## New-reader inputs and dependencies

The only coordinate input needed for the scan is official
[2O9P.pdb](https://files.rcsb.org/download/2O9P.pdb), SHA-256
`94573091f10dd18ffc4d3bae84e90f3c151294d2590818133a3d5ee2c8de328d`. Obtain it from the provider into your own local cache.
No paper PDF, D2D coordinate file, private path or historical run is needed to
generate a new scan. Public audit/mapping/config files in this directory are
checked by hash before preparation; changed sources are rejected for review.

Include [tool_revision_2026-10-25.json](tool_revision_2026-10-25.json) with both
current scripts and the original frozen plan/dependencies. Current tool and
declared public-text dependency hashes use `sha256-utf8-crlf-to-lf-v1`: validate
UTF-8, replace CRLF with LF, then SHA-256; no other bytes or whitespace are
ignored. The local `.gitattributes` pins necessary public text to LF and leaves
curated CSVs byte-preserving. Both LF and CRLF text exports pass tool preflight;
actual edits fail. This is not a fresh-environment full-scan validation.

Original PDBs, raw scan CSV/sidecar, run records and archived execution sources
retain raw byte hashes. Historical runner approval comes from the original
pre-scan plan, while current tools have a separate post-review approval. The
scientific source inventory is checked against that plan's approved Git version,
including the recorded execution commit; do not use these checks as a security
or authenticity guarantee. Preserve raw run files byte-for-byte for re-curation.

Install the repository's development package and use the recorded direct
[dependency snapshot](requirements-case.txt) if reproducing this environment.
The commands were validated in the existing Windows Python 3.13.12
environment, not a fresh venv or another platform. The snapshot is not a complete
transitive dependency lock. The wrapper supports the reviewed **2O9P profile**,
not arbitrary proteins or generalized structural conversion.

For new paths, run the two scripts shown above with `--source-pdb YOUR_2O9P_PDB`
and new `--output-dir` names. Curation requires the complete new run directory,
including its hashed original/prepared inputs, CSV, sidecar and execution sources;
it verifies them before reading the CSV. The public curated tables allow result
inspection but are not a replacement for full raw provenance in re-curation.

## Interpretation boundaries

This is protein-only fixed-structure geometry. Ligands present in source files
are not automatically part of RANA sterics, and removing ligand from holo input
does not establish experimental apo geometry. 2JIE is context only; 2Z1S, 2O9R
and 2O9T remain uninvestigated future candidates in this phase. No experimental
pAzF validation, calibrated probability or claim about any laboratory's ncAA
experiments follows. No algorithm, threshold, seed or rotamer library changed.
