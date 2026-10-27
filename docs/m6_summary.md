# M6 summary: reliable inputs and computational applications

The M6 milestone is complete as of 2026-10-27. RANA now preserves full residue
identities during steric scoring, provides a reproducible ferritin input
profile, documents sensitivity to T4 lysozyme reference structures, and includes
a BglB pAzF application. These deliveries build on the completed
[M5 retrospective pilot](benchmarks/README.md). They strengthen software and
computational evidence without establishing experimental prediction accuracy.

The [original M6 plan](benchmarks/m6_plan.md) remains a historical record from
the M5 closeout. Current status is recorded here and in the
[project roadmap](../README.md#roadmap).

## Insertion-code repair: preserve full residue identity

Residues with the same chain and number can differ by an insertion code.
The repair forwards that code when excluding bonded-neighbor overlaps, so the
calculation uses the intended residue rather than a conflicting identity.
Regression cases cover nonblank codes, blank/nonblank collisions, different
chains and label-only changes without identity conflicts.

Existing blank-code cases retained identical scores, low-clash fractions,
geometric tiers (heuristic fit categories) and ranks across 634 sites. The
repair's full test suite passed **91 tests on 2026-10-24**; this is software
regression evidence. Only steric scoring was replayed for that
comparison; archived RSA and packing fields were reused, not recalculated.
See the [repair validation summary](m6_insertion_code_validation.md).

## 2FG8: rebuild the ferritin environment from public coordinates

The pinned 2FG8 assembly-1 workflow removes dependence on old prepared files,
paper PDFs and fixed local paths. It retains 24 protein chains and prepares
the target-chain monomer separately. Atom identities and coordinates matched
the historical inputs, and both 174-site scans produced byte-identical CSVs.
Assembly is the primary environment; monomer results describe environment
sensitivity rather than an alternative selected for agreement with experiment.

The original preparation and scans ran in one fresh virtual environment on
the same Windows host, with **14 targeted conversion tests passing**. A later
wrapper-reliability revision passed **92 targeted conversion and wrapper tests**.
Its wrapper checks used synthetic scanner responses and did not repeat the real
scans. This verifies the stated
2FG8 profile, not arbitrary structure conversion, cross-platform reproduction
or exact identity with the literature's full experimental construct.
See the [reproduction guide](reproducibility/README.md),
[original execution evidence](reproducibility/2fg8_validation.md) and
[wrapper revision](reproducibility/2fg8_reliability_revision_2026-10-24.md).

## T4 lysozyme: reference choice can change a shortlist

Across 1L63, 1LW9 and 219L, 143 of 162 mapped common sites retained the same
geometric tier and 19 changed tier. Broad rank ordering was similar, but the
minimum-steric-score lists shared only 6-8 sites at their inclusive top-ten
boundaries. The six M5 pilot sites retained their tiers. Scores and ranks could
still vary within a tier, so a stable label does not imply an invariant result.

The three inputs share the same C54T/C97A background sequence. Missing terminal
residues, alternate atom positions and crystallographic conditions still differ;
the comparison does not isolate a pure conformational effect. Structure
selection preceded scanning and did not use agreement with experimental data.
The analysis revision passed **38 targeted tests** in the existing Windows
environment and reproduced the small-table comparisons. It did not establish
a fresh-environment scan or an independent experimental benchmark.
See the [study entry](structure_sensitivity/t4l/README.md),
[results](structure_sensitivity/t4l/results_report.md) and
[analysis revision](structure_sensitivity/t4l/analysis_revision_2026-10-24.md).

## BglB: a single-reference pAzF application

The case scored all 445 modeled sites in β-glucosidase B (BglB) from
Paenibacillus polymyxa. Its 31-site overview is the union of three independent
ranking lists, with cutoff ties retained. Functional annotations remain visible
as separate context and do not change scores, ranks or list membership.

The input is 2O9P chain A, an H376Q/G377R engineered apo reference. It is not
natural WT, D2D standard or the maintainer's experimental construct. Screening
is protein-only, and no corresponding pAzF experimental validation is available.
The original scan used the existing development environment, not a fresh one.
The later documentation-dependency compatibility revision passed **66 targeted
tests on 2026-10-27**. Re-curation preserved scientific tables and candidate
sets; the human-edited report intentionally differs from the historical template.
See the [case entry](computational_cases/bglb/README.md),
[results and limits](computational_cases/bglb/results_report.md) and
[reproduction/version boundaries](computational_cases/bglb/reproduction.md).

## What completion means

The test counts above belong to different stages and scopes. They must not be
added into a full-suite total or presented as a new test run for this closeout.
Software tests check behavior; computational reproduction checks agreement for
specified inputs and environments; structure sensitivity describes dependence
on the chosen reference. None calibrates incorporation, stability, function or
conjugation predictions. Geometric tiers are heuristic categories, and the
low-clash fraction counts sampled conformations, not experimental successes.

pAzF remains the only supported ncAA. A second ncAA, such as pBpA, belongs to
the planned M7 scope and has not been implemented. M6 introduced no MD, ML,
literature-driven parameter tuning or composite score. Broader modeling and release-validation work remains outside M6.
