# M6.3 T4L reference-structure sensitivity

This is a **same-background computational input-sensitivity study**, not a new
independent experimental benchmark. It uses the merged PR #5 scientific code and
frozen pAzF settings. No experimental outcomes select structures or tune scores.
The M5 1L63 records remain unchanged.

Start with the [results and limits](results_report.md),
[frozen analysis plan](analysis_plan.md), [machine-readable plan](frozen_plan.json)
and [original execution/verification summary](execution_summary.json).
The [analysis revision and verification](analysis_revision_2026-10-24.md)
([JSON](analysis_revision_2026-10-24.json)) records the subsequent input-integrity,
eligibility, tier-count and SVG-format fixes. The original execution summary is
preserved as a historical snapshot; its script hashes/test counts refer to that
snapshot, not the revised analysis. No structure was downloaded or re-scanned
for this revision.

## Structure selection and mapping

The [selection CSV](audit/structure_selection.csv),
[full local audit](audit/structure_audit.json),
[mapping CSV](audit/site_mapping.csv) and
[official source manifest](source_manifest.json) record complete entity sequences,
mutations, numbering, chains, missing residues/heavy atoms, altlocs, method,
resolution, components and assembly operators. Source files themselves remain
ignored. The author-number mapping is direct, not an assumed sequence offset.

- [1L63](https://www.rcsb.org/structure/1L63): historical C54T/C97A reference,
  1.75 Å X-ray; chain A has 162 coordinate residues, missing N163/L164.
- [1LW9](https://www.rcsb.org/structure/1LW9): identical full 164-residue entity
  sequence, 1.45 Å X-ray, complete chain A; selected protein altlocs at
  T54, N55, G56 and R137 are recorded explicitly.
- [219L](https://www.rcsb.org/structure/219L): identical full entity sequence,
  1.66 Å X-ray, complete chain A. The mutant-series title does not imply an
  insertion/deletion in this audited entry.
- [2LZM](https://www.rcsb.org/structure/2LZM): excluded because C54/C97 differ
  from the cysteine-free reference. [1L97](https://www.rcsb.org/structure/1L97)
  is also excluded: I3P on native C54/C97 background, with two ASU protein chains.
  Neither was scanned or pooled into the main comparison.

All selected assemblies are monomeric with identity operator 1; chain A is the
entire retained protein environment. All available standard-protein heavy ATOM
records are copied, including original altloc order; nonprotein components and
H/D are excluded. No H/D occurs in these selected inputs. No symmetry, relaxation,
rebuilding or atom-coordinate transformation is performed. Atom identities,
coordinates, occupancy/B factors and selected altlocs were unchanged on copying.
SASA, packing and steric screening receive the same prepared input. Crystal
neighbors are not included. The ferritin 2FG8 profile is not used.

The sequence screen is bounded, not exhaustive: first 100 of 124 RCSB sequence
search hits, with full-sequence equality subsequently checked locally. Five
candidates received complete coordinate/metadata audits. Selection preferred
same-background complete ordinary X-ray references, not correlation with ΔTm.
Different pressure, noble-gas, deuterated/neutron and ligand-soaked cases were
not needed for this three-input scope. Reference sequences do not establish
exact equivalence to the full tagged experimental constructs in the M5 papers.

## Reproduce from public coordinates

Use a full clone containing the frozen scientific base commit
`bc63d0a74036e702c698d349862c976059707ea3`. The current runner verifies the entire
scientific Python source against that base (allowing line-ending serialization
and later documentation-only commits), and refuses modified scientific source.
Use an editable install from this checkout:

```text
python -m venv .venv-t4l
```

Activate the venv for your shell, then from the repository root:

```text
python -m pip install -r docs/structure_sensitivity/t4l/requirements-analysis.txt
python -m pip install --no-deps -e .
python -B docs/structure_sensitivity/t4l/run_scans.py fetch --output data/processed/t4l_sensitivity_repro/sources
python -B docs/structure_sensitivity/t4l/run_scans.py run --sources data/processed/t4l_sensitivity_repro/sources --output data/processed/t4l_sensitivity_repro/run
python -B docs/structure_sensitivity/t4l/analyze.py --run-dir data/processed/t4l_sensitivity_repro/run --output data/processed/t4l_sensitivity_repro/analysis
```

The fetch command downloads only the three selected official PDB/mmCIF pairs,
checks pinned hashes and records new retrieval times. Local files with those
hashes may instead be supplied through `--sources`; no download is needed then.
For all five candidates' full audit inputs, use `fetch --all-audit-files` with a
different new output directory, then:

```text
python -B docs/structure_sensitivity/t4l/structure_audit.py --sources NEW_ALL_AUDIT_SOURCES --output NEW_AUDIT_DIRECTORY
```

Official file or API revisions may change hashes and are rejected for explicit
review; do not silently update the frozen profile. No paper PDF, local historical
structure, scan table or fixed operating-system path generates these inputs.
All output directories must be new; errors preserve partial diagnostic files.
The exact frozen scan command pattern is:

```text
python -I -B -m ncaa_site_rec.cli rank --pdb PREPARED_PROTEIN_A_PDB --chain A --ncaa pazf --seed 42 --low-clash-threshold 10.0 --favorable-fraction 0.5 --output NEW_RANKED_CSV
```

Actual execution used the existing Windows CPython 3.13.12 development venv;
this study did not validate a fresh environment or another platform. Exact
commands/times and raw sidecars are local at
`data/processed/m6_t4l_structure_sensitivity_2026-10-24/run/run.json`.
The three scans used the original wrapper snapshot saved under that run's
`executed_sources/`; its hashes remain in the run record. The current runner
subsequently gained the content-based scientific-source guard so a future
documentation-only HEAD does not prevent reproduction. That guard was checked
separately against the real checkout and synthetic negative fixtures. The
execution summary distinguishes original/current runner hashes; it does not
claim the current guard revision performed another real scan. Scientific code,
prepared atom policy and exact CLI parameters did not change.

## Reproduce the comparisons from the public small tables

```text
python -B docs/structure_sensitivity/t4l/analyze.py --curated docs/structure_sensitivity/t4l/results/metrics_long.csv --output data/processed/t4l_sensitivity_curated_repro
```

This requires no structures or ignored scans. It reproduces six common-site
comparison CSVs and all six PNG/SVG plot files byte-for-byte in the tested
environment. The analysis metadata intentionally records the new input mode/time.
SVG exports now remove trailing whitespace deterministically. The revision
changed only SVG whitespace and analysis provenance, not scientific results.
This level does not reconstruct the full mapping/eligibility ledger from the
already-filtered common table; those are separately provided and can be rebuilt
from source audits and full scans. See the [data dictionary](data_dictionary.md).

Before parsing scan CSVs, run-mode analysis verifies the plan against the run
record, the plan's audit/mapping/other frozen dependencies, and each recorded
scan, sidecar and prepared-input hash. A mismatch fails without updating any
expected hash. Missing scan rows for modeled coordinates are integrity errors;
only audited unmodeled coordinates receive `absent_from_input`. Invalid tiers or
incomplete transition/stability counts fail explicitly.

The [targeted tests](../../../tests/test_t4l_structure_sensitivity.py) cover tie
handling, rank re-computation, missing/failed/skipped/mismatched mappings,
coordinate and altloc preservation, overwrite refusal, source/input guards,
tier-count checks and whitespace normalization. Negative runtime checks also
run under `python -O`:

```text
python -B -m pytest tests/test_t4l_structure_sensitivity.py -q
```

## Results files

- [Common-site long table](results/metrics_long.csv): 486 rows, with raw field
  provenance, original full-input ranks and separate common-set ranks.
- [Per-site ranges](results/site_ranges.csv), [eligibility ledger](results/site_eligibility.csv).
- [Pairwise rank consistency](results/pairwise_metrics.csv),
  [inclusive top-10 overlap](results/top10_overlap.csv),
  [tier transitions](results/tier_transitions.csv).
- [Six M5 sites](results/m5_six_sites.csv), with no experimental values added.
- [Pairwise metric scatter](results/pairwise_metrics.svg),
  [rank ranges](results/rank_ranges.svg), [six-site figure](results/m5_six_sites.svg).
- [Analysis hashes/metadata](results/analysis_metadata.json) and
  [public file manifest](file_manifest.json).

This checks reference-input dependence within a restricted same-sequence crystal
sample. It does not calibrate incorporation, expression, stability, function or
labeling, and low-clash fraction remains a sampled geometric fraction, not an
experimental success probability. No M5 frozen file, exploratory script or
scientific scoring code was modified. No BglB, MD, ML or additional ncAA work.
