# Reproduce the 2FG8 ferritin reference inputs and scans

This M6.2 workflow starts from the official, already-expanded **2FG8 assembly 1**
mmCIF. It needs no paper PDF, web cache, UniProt download, historical prepared PDB,
old scan table or fixed operating-system path. The old
[M5 preparation script](../benchmarks/khoshnejad2018_hftl_prepare.py) and case
records remain historical evidence and are not called by this workflow.

The [profile](../../configs/2fg8_assembly1.json) pins the public source's
decompressed SHA-256, protein chain order, sequence, author numbering, frozen
scan configuration and **comparison tolerances declared before execution**.
This is the previously authorized computational reference, not confirmation of
the exact PDB or full fusion used by the experimental authors.
Only this pinned **2FG8 assembly-1 profile and original target A** have been
verified. Custom profiles and conversion of arbitrary structures are not verified
capabilities; this profile requires residues 5–178 with blank insertion codes.

## Install in a fresh environment

From a checkout containing this implementation, create and activate a new venv:

```text
python -m venv .venv-repro
```

Activate with `.venv-repro/Scripts/Activate.ps1` in PowerShell or
`source .venv-repro/bin/activate` in a POSIX shell. Then:

```text
python -m pip install --no-cache-dir -r docs/reproducibility/requirements-2fg8.txt
python -m pip install --no-cache-dir --no-deps .
python -m pip check
```

The [direct dependency file](requirements-2fg8.txt) records versions used in the
independent verification. The [observed full runtime snapshot](requirements-2fg8-lock.txt)
also pins transitive packages and can be used in its place. The snapshot was
exported after the successful installation, not used as a pre-existing lock.
Python 3.13.12 on Windows was actually tested; other supported Python/OS
combinations are not claimed tested. Installing the local package may download
the build dependencies declared in pyproject.toml.

## Download, prepare and scan without historical inputs

```text
python -I docs/reproducibility/reproduce_2fg8.py --profile configs/2fg8_assembly1.json --work-dir data/processed/2fg8_reproduction_new
```

The work directory must be new. The driver downloads only
`https://files.rcsb.org/download/2FG8-assembly1.cif.gz`, recording requested/final
URL, actual UTC retrieval time, byte length and SHA-256. It checks decompressed
content against the profile before conversion. A later source revision with a
different digest is rejected for review, never silently accepted.

To avoid downloading, append `--input PATH_TO_PUBLIC_ASSEMBLY_CIF_OR_GZ`.
Local input is copied and hashed; a retrieval time is not fabricated.

Outputs are:

- `sources/`: supplied/downloaded structure and, when downloaded, retrieval JSON.
- `prepared/assembly1_protein.pdb`, `prepared/target_monomer.pdb`,
  `prepared/preparation.json`: two prepared inputs and atom/chain provenance.
- `scans/assembly.csv`, `scans/monomer.csv`, CLI metadata and stdout/stderr logs.
- `run.json`: installed source hashes, environment, source record, exact CLI
  commands/times, per-output completeness checks and generated-file hashes.
  The driver reads no historical scans.

A zero CLI exit is insufficient. For each CSV the driver requires the profile's
174 unique chain/number/insertion-code identities and parent residues, all
`scored`, empty scoring diagnostics, 12 finite numeric rotamer scores per site,
and finite required scores, ranks and structural features. It also checks the
metadata schema, input/CSV hashes, configuration, status/tier counts and sampling.
Missing or malformed outputs fail the run. Logs and partial files are retained;
`run.json` records `failed_stage` and the exception where writing remains possible.
An unhandled validation exception produces a nonzero process exit.

Only after both output checks pass is status set to
`scans_completed_pending_separate_comparison`. This establishes output
completeness, not agreement with historical results or scientific validation.

Both commands use target chain A, pAzF, seed 42, cutoff 10.0 Å² and favorable
fraction 0.5; the library still samples 12 rotamers. No algorithm, threshold or
library is changed. Assembly remains the primary environment; monomer is the
existing environment comparison, not a newly selected reference structure.

## Prepare a local structure separately

```text
python -m ncaa_site_rec.io.prepare_structure --input PATH_TO_PUBLIC_ASSEMBLY_CIF_OR_GZ --profile configs/2fg8_assembly1.json --output-dir data/processed/2fg8_prepared_new
```

`--target-source-chain` can select a retained source chain; the manifest records
its output ID. The frozen reproduction driver uses the profile's original A
target. An optional `--source-record` accepts a URL/time/hash retrieval record
that must agree with the local input. Existing output directories, including
partial earlier attempts, are refused. Use a new directory for every attempt.

## Coordinate and component policy

The input already contains the assembly coordinates. No symmetry matrices are
applied. Protein label chains A–H, A-2–H-2 and A-3–H-3 map in that order to
output A–X. Every source-to-output pair is recorded. Author residue IDs 5–178,
parent identities, insertion codes and alternate atom conformers are preserved.
The target monomer retains the selected assembly chain's coordinates and ID.
Both PDBs contain one explicit `MODEL 1` and `ENDMDL` pair.

All nonstandard/nonprotein residues are excluded, including water, metals and
ligands. For this source the omissions are 30 CS and 441 HOH residues. Standard
protein atom/altloc records are retained; no hydrogens are added or removed by
preparation. No relaxation, residue reconstruction, mutation or coordinate
transformation occurs. PDB formatting has three-decimal precision; an atom-level
round-trip check permits at most 0.0006 Å per Cartesian component. The actual
verified 2FG8 conversion has **zero coordinate change**.

The official expanded file identifies its entry as `XXXX` and lacks the original
assembly metadata category; identity is therefore supported by the pinned public
URL/content digest and explicit sequence/chain/number checks, not by pretending
that this placeholder is a verified accession. The asymmetric-unit mmCIF and
UniProt FASTA were needed for the original literature/sequence audit, not this
frozen coordinate reconstruction. Papers, SI and archived web pages are likewise
historical evidence only.

## Verification level and historical comparison

See the [verification summary](2fg8_validation.md) and
[machine-readable result](2fg8_validation.json) for the **original real execution**.
Those immutable records identify the original script hashes. The
[2026-10-24 reliability revision](2fg8_reliability_revision_2026-10-24.md) and its
[JSON record](2fg8_reliability_revision_2026-10-24.json) describe the revised
wrappers and targeted synthetic tests; dependencies and full real scans were
not rerun for this revision. Do not attribute the earlier execution to revised
script hashes. Actual original verification used a new
venv with freshly downloaded packages, a source snapshot of the PR #4 merge
plus the uncommitted new preparation module, an installed wheel, and a working
directory outside the repository. Installed package hashes were checked against
the snapshot. No old virtual environment or paper/cache files generated inputs.

Only **after** both scans finished did [compare_2fg8.py](compare_2fg8.py) read
historical inputs/outputs. It requires explicit reference paths and a fresh
report path:

```text
python -I docs/reproducibility/compare_2fg8.py --run-dir NEW_RUN_DIRECTORY --profile configs/2fg8_assembly1.json --reference-assembly HISTORICAL_ASSEMBLY_PDB --reference-monomer HISTORICAL_MONOMER_PDB --reference-assembly-scan HISTORICAL_ASSEMBLY_CSV --reference-monomer-scan HISTORICAL_MONOMER_CSV --output NEW_COMPARISON_JSON
```

Runtime guards and comparison checks use explicit exceptions and remain active
under `python -O`. Existing reports (including symbolic links) are refused;
exclusive file creation also prevents overwriting a report created during the
comparison. Invalid generation status, profile mismatch, non-finite data and
structure/scan differences are rejected, not recorded as a passing comparison.

Historical full scans are ignored and not shipped; new users do not need them
to generate their own results. The tracked verification summary records this
comparison. Prepared byte hashes differ because the new PDBs explicitly encode
MODEL/ENDMDL; atom identities, numbering, occupancy, B factors and coordinates
match, and both resulting scan CSVs are byte-identical to the historical scans.

CLI sidecars outside a Git checkout correctly report no Git commit. The wrapper's
`run.json` stores the separate actual code-source manifest and installed hashes
when `--code-record` is supplied, without backfilling the sidecar. For a developer
verification, record the base commit, local patch hashes and exported source
hashes when building a snapshot; do not describe uncommitted additions as part
of the base commit.

This verifies the computational 2FG8 preparation-to-scan path in one new local
environment. It is not cross-platform verification, experimental validation,
multi-structure sensitivity analysis, or proof of exact experimental construct
identity. No BglB or additional ncAA work is included. M5 frozen records and the
global data ignore rules remain unchanged.

The [submission manifest](submission_manifest.json) lists the proposed tracked
files and their hashes. Full generated inputs/scans, environments, papers and
local audit files remain outside that list.
