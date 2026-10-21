# RANA contributor guidance (proposed at M4.6)

## Scientific scope

- RANA `0.1.0.dev0` screens fixed-structure geometric accommodation of pAzF
  with 12 discrete rotamers. Ranks and tiers are heuristic, not calibrated
  predictions of incorporation, expression, stability, function, or labeling.
- Treat active code and tests as current behavior. Separate historical design
  proposals, inactive scaffolding, and future plans in documentation.
- Preserve residue chain, number, and insertion code in joins and outputs.
  Keep failed/skipped rows and explain diagnostics; never silently drop them.

## Coding conventions

- Use Python >=3.10, four-space indentation, snake_case functions/modules, and
  type hints/docstrings consistent with nearby code. Use pathlib for paths.
- Keep changes small; reuse existing NumPy/pandas/Biopython/RDKit code.
  Add dependencies only with a concrete need and an explicit explanation.
- Do not change scientific constants, sampling, scores, or tier rules as part
  of documentation cleanup. Scientific changes need a stated rationale and
  regression evidence; avoid implying validation from execution alone.

## Validation and reproducibility

- Follow `docs/examples.md` from the repository root: install `.[dev]`, fetch
  public `data/raw/1L63.pdb`, and run `python -m pytest tests/ -q`.
- Validate affected CLI examples and inspect CSV statuses and metadata, not
  exit code alone. Record input hashes, parameters, versions, and actual results.
- Add focused tests for behavior changes. Keep geometric checks separate from
  experimental validation; do not fit expectations merely to make tests pass.
- Preserve `.gitignore` rules for `data/raw/` and `data/processed/`. Keep large
  inputs, generated runs, and unpublished laboratory data out of Git.
- Review local exploratory scripts before proposing promotion to tests or
  utilities. Do not delete or commit them without maintainer approval.

## Development priorities

- During M4.6, limit changes to documentation accuracy and reproducible public
  examples. This scope restriction applies to this milestone only.
- Future maintainer-authorized work may implement M5 retrospective benchmarking
  with tested-site labels, baselines, metrics, and uncertainty; additional ncAAs;
  and ML-based methods. M4.6 restrictions do not permanently prohibit these
  scientific or development directions.
- Future work may also address functional constraints, handle accessibility,
  and experimental validation within a maintainer-approved scope. Scientific
  rationale, validation, reproducibility, testing, and approval requirements
  continue to apply. Stable release criteria remain undecided.
- Work on a separate branch. Do not commit, push, open a PR, or create a
  release tag without explicit user approval.
