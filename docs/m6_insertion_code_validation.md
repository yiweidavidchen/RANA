# M6 insertion-code repair: validation summary

Validation date: **2026-10-24**. Branch: `codex/m6-insertion-code-fix`.
Base: M5 PR #3 merge, `312b504722bac84003e61cc0fcb14e20f4cae561`.
This summary records completed software checks before the subsequent
documentation-only follow-up; those tests were not rerun for prose changes.

## Repair scope and regression evidence

[`score_pazf_site`](../ncaa_site_rec/features/pazf.py) now forwards
`insertion_code` to `exclude_bonded_neighbor_overlaps`. This makes the
CB-to-N/C bonded-neighbor exclusion use the intended full residue identity.
Thresholds, seed, sampling, scoring rules and rotamer library are unchanged.

The six new [regression cases](../tests/test_insertion_code_scoring.py) cover
nonblank insertion codes, same-chain/same-number blank and nonblank residues,
different-chain/same-number contacts, and label-only score invariance without
identity collisions. Before repair, **4 failed and 2 passed**, reproducing
the forwarding defect. After repair:

- Targeted scoring, scan, feature and ranking tests: **51 passed**.
- Full `tests/` suite: **91 passed**, no failures, errors or warnings.
- The first targeted attempt had two temporary-directory permission setup
  errors; the successful rerun used a new independent temporary directory.

Environment: Python 3.13.12; pytest 9.1.1; NumPy 2.5.4; pandas 3.0.6;
Biopython 1.88; RDKit 2026.09.1. Exact test commands are in the local record below.

## Existing blank-insertion-code cases

Before/after replay covered T4 lysozyme 1L63 (162 sites), RNase A 7RSA
(124), and the existing ferritin assembly and monomer inputs (174 each).
All **634 sites and 7,608 rotamer scores** were exactly equal before and
after repair, including minimum/mean/median scores, low-clash fractions,
tiers and all three independent ranks. Replays also matched archived numeric
outputs within an absolute tolerance of 1e-10.

Only steric scoring was rerun. Unchanged archived structural fields supplied
RSA/packing for rank verification; SASA was not recalculated. No new reference
structure or structure-sensitivity analysis was introduced. Inputs, archived
CSVs and M5 frozen records were preserved; new outputs used a separate directory.

## Detailed local records and interpretation

The [detailed validation record](../data/processed/m6_insertion_code_fix_2026-10-24/validation_summary.json)
is stored at repository-relative
`data/processed/m6_insertion_code_fix_2026-10-24/validation_summary.json`.
It records commands, environment, file hashes and comparison results; adjacent
`before/verification.json` and `after/verification.json` retain case provenance.
This directory is Git-ignored, so the detailed link works only where those local
outputs exist and is not expected in a fresh checkout. This document preserves
the concise reviewable evidence without publishing generated runs.

The README's **85-test** statement remains historical smoke-validation evidence;
the **91-test** result here belongs to this repair. These are software regression
checks, not experimental prediction-performance validation. They do not establish
accuracy or generalization of the [M5 retrospective pilots](benchmarks/README.md).
