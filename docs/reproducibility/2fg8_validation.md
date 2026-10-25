# M6.2 2FG8 preparation and scan verification

Date: **2026-10-24**. Branch: `codex/m6-portable-structure-preparation`.
Local main was fast-forwarded to PR #4 merge
`94426a4b0bb262f73c189765ecadccc75de58689` before the branch was created.
No reset, clean, commit or push was used.

## Code, configuration and environment actually executed

A source snapshot exported from that merge contained the package, pyproject and
README, overlaid with the new `ncaa_site_rec/io/prepare_structure.py`. The new
module was **uncommitted**, not part of the base commit. Its SHA-256 and all 19
installed package-source hashes are recorded in [2fg8_validation.json](2fg8_validation.json).
A noneditable wheel was built/installed into a **new venv**, without system site
packages or reuse of the old development environment. Installed source hashes
matched the snapshot. The driver ran with isolated Python mode and a working
directory outside the repository, containing no old scans, structures or papers.

Tested: Windows 11 x86_64, CPython 3.13.12, NumPy 2.5.4, pandas 3.0.6,
Biopython 1.88, RDKit 2026.9.1, pytest 9.1.1. Dependencies were freshly downloaded
with `pip --no-cache-dir`; `pip check` reported no broken requirements. Direct
versions and the observed full runtime snapshot are trackable alongside this
document. Initial sandbox network access was denied; installation succeeded
after normal-account network access was authorized. No blocked installation is
being described as a successful run.

The [profile](../../configs/2fg8_assembly1.json) was saved before execution.
Frozen pAzF parameters remain seed 42, 12 library rotamers, score cutoff 10.0 Å²,
favorable fraction 0.5 and no functional annotations. Scientific algorithms,
thresholds, seed and rotamer library were not changed.

## Preparation results

The official expanded assembly was downloaded from the explicit RCSB URL on
2026-10-24 at 11:28:49 UTC. Its compressed SHA-256 is
`9bedf6e9e326d9504675eb88ffe1847b99b02850430be6ceaff11cc008f5fd66`;
decompressed content matches the pinned profile. Source chain order
A–H / A-2–H-2 / A-3–H-3 maps to output A–X, with source/output A the target.

- Assembly: one model, 24 protein chains, 4,176 residues, 33,648 atoms.
- Monomer: one model, chain A, 174 residues, 1,402 atoms.
- Every chain preserves author residues 5–178; atom identities, alternate IDs,
  occupancy and B factors match the historical prepared inputs.
- Source-to-output and historical-to-new maximum coordinate differences are
  both **0 Å**. No relaxation, reconstruction or symmetry application occurred.
- 30 CS and 441 HOH residues were excluded; no standard protein atoms were added
  or removed. Preparation records the nonprotein policy explicitly.

Prepared PDB byte hashes differ: the new writer emits explicit MODEL 1/ENDMDL
records. After stripping only those record types and normalizing text line
endings, every other record matches. Atom-level comparison independently confirms
no coordinate or identity difference; hash inequality was not treated as a
structural difference or used to dismiss actual coordinate changes.

## Scan comparison and tests

Only after both new CLI scans finished were historical inputs/outputs read by
the separate comparison script. Each new scan scored all 174 target sites with
12 rotamers. Across both scans, **348 site records and 4,176 rotamer scores**
match. Both CSVs are byte-identical to their corresponding historical outputs:

- Assembly SHA-256: `009b67525e68b3a8b4a657e386e3a3c48324e44ec37d20a62709a6ea7432aca9`.
- Monomer SHA-256: `64726abde3858410489759719d37633aa4e364449e24f344ccbd64e2d6b2bdf1`.

Predeclared absolute tolerances were 1e-8 Å² for steric scores, 1e-6 Å² for SASA,
1e-8 for RSA, zero for comparison to historical prepared coordinates, and zero
relative tolerance. Identity, status, packing, fraction, tier and all three ranks
required exact equality. All observed numeric differences were **zero**; no
tolerance, parameter or structure environment was changed to obtain agreement.

**14 targeted conversion tests passed** in the fresh installed environment
(0 failures, 0 warnings). They cover identity/coordinate retention, gzip input,
target-chain mapping, water/metal exclusion, overwrite refusal, source/profile
and retrieval-record mismatches, multiple-model rejection and alternate atoms.
An initial test-collection attempt hit a Windows ancestor-directory permission
issue; explicit rootdir/confcutdir and a new temporary directory resolved it.
The full unrelated suite was not repeated; actual preparation and both complete
CLI scans were additionally checked, including statuses and metadata.

## Reproduction commands and local details

The [reproduction guide](README.md) gives portable fresh-venv installation,
download/local-input preparation, scanning and optional historical-comparison
commands. The executed driver was equivalent to:

```text
python -I reproduce_2fg8.py --profile 2fg8_assembly1.json --work-dir NEW_INDEPENDENT_RUN --code-record code_source.json
```

`code_source.json` records the base commit, uncommitted overlay and source hashes;
it is an audit input, not a dependency on old scientific results. The generated
CLI sidecars correctly contain null Git provenance outside a checkout. Their
missing commit fields were not backfilled; the wrapper records actual installed
code provenance separately.

Complete generated records are archived in the **new ignored directory**
`data/processed/m6_portable_2fg8_2026-10-24/`: `run/` contains the fresh source
download, preparation, scans and exact command/timing log `run/run.json`;
`comparison.json` contains full comparisons; `independent/` retains the new venv,
source snapshot and `code_source.json`. Original execution paths in these logs
remain truthful after archival. They are local records, absent in a fresh clone;
the tracked JSON summary preserves the concise results and hashes.

All 173 protected pre-existing files were unchanged, including M5 records and
the seven exploratory scripts. No old input, preparation script, frozen result
or global data ignore rule was overwritten.

This establishes the pinned 2FG8 preparation-to-scan workflow on **one fresh
environment on the same Windows host**. It does not establish cross-platform
reproducibility, exact experimental construct/PDB identity, predictive performance,
multi-structure sensitivity, a BglB case or support for another ncAA. Source
revisions with changed content hashes require a new explicit audit.
