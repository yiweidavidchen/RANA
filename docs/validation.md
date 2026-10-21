# Validation status and research plan

RANA `0.1.0.dev0` has computational smoke validation on two structures.
Experimental predictive validity has not been demonstrated for ncAA incorporation,
expression, stability, retained function, or labeling efficiency. Geometric
accommodation is the scope of the implemented screen.

## M4.6 reproducibility check

On 2026-10-20, the unchanged existing suite completed with **85 passed in
185.00 seconds**, exit 0, on Python 3.12.14. Independent public screens scored
162/162 residues for 1L63 and 124/124 for 7RSA, with 12 rotamers per site and no
failed or skipped sites. These reproduce the reported M4.4 tier counts.

See [public examples](examples.md) for commands, input hashes, dependency versions,
current run summaries, and the independently rerun automated test results.
The historical M4.4 results below remain a record of that phase, not a claim that
all environments reproduce identical numbers. Dependency ranges are not a lockfile.

## M5 retrospective benchmark — planned, not implemented

The earlier sections titled "v0.1 goal" and "v0.1 stopping rule" combined
software execution with an uncompleted experimental benchmark. The following
research belongs to M5; no literature outcomes or benchmark metrics are added
by M4.6, and no release tag is authorized.

- Curate primary literature with explicit experimentally tested sites, structure
  and sequence mapping, protocols, and separately recorded incorporation,
  expression, conjugation/labeling, stability, and retained-function outcomes.
- Keep untested sites unlabeled. Published positives do not establish that
  untested sites fail; use ranking/enrichment evaluation unless justified
  negative labels are available.
- Freeze the implemented configuration before comparing to outcomes. Any protein
  used to tune thresholds is a development set; use independent data for claims
  of generalization.
- Compare the independent RANA ranks to prespecified simple baselines, including
  RSA-only, steric-only, and rotamer-robustness-only rankings. Define any rule
  combining features before evaluation. The current pipeline has no full
  composite score or functional-zone exclusion baseline.
- Prespecify evaluation metrics, tie handling, missing/failed-site handling,
  uncertainty estimates, and sensitivity analyses. Account for limited tested
  sites and positive-unlabeled bias; do not report a success probability from
  geometric tiers.
- If a percentile is used, define the rank and denominator explicitly. The
  historical suggestion `1 - (rank - 1)/(N - 1)` needs an explicit policy for
  ties and N <= 1; no percentile is currently emitted by the CLI.

## Known scientific limitations

- Only pAzF is supported, using 12 discrete proxy conformers without energetic
  weighting, protein relaxation, or exhaustive conformational sampling.
- WT SASA is not mutant or reactive-handle SASA. Explicit H/D atoms are excluded
  from sterics but are retained by the SASA calculation.
- Optional annotations provide minimum C-alpha distances only. There are no
  active functional-site or disulfide-preservation gates in `rana rank`.
- Glycine/proline caution flags do not veto a site.
- A confirmed insertion-code forwarding omission in `score_pazf_site` makes
  the bonded-neighbor exclusion helper use a blank insertion code. At nonblank
  insertion-code sites, target CB-to-N/C penalties can remain and contacts to a
  blank-code residue with the same chain and number can be incorrectly excluded.
  Clash scores, steric and rotamer-robustness rankings, and geometric tiers may
  change. Neither public example covers this case. See [design](design.md) for
  details; a code fix and regression test are outside M4.6 scope.
- Input preparation, missing coordinates, alternate locations, chain selection,
  ligand omission, and software versions can affect results.
- Geometric accommodation does not establish functional tolerance, folding,
  translational incorporation efficiency, or suitability for a labeling experiment.

## Release criteria

M4.6 completion concerns documentation consistency and reproducible software
execution, with limitations and failures disclosed. The historical instruction
to tag `v0.1.0` after a T4L scan and literature overlay is superseded.
Stable-release scope, scientific evidence requirements, and packaging validation
need a separate maintainer decision. The current version remains `0.1.0.dev0`.

---

## M4.4 — Cross-protein computational smoke validation

The following results and debugging history were reported at M4.4. Current
independently rerun results are recorded in [examples.md](examples.md).

### Objective

Evaluate whether the RANA v0.1 pAzF geometric screening pipeline can execute consistently on different experimental protein structures, including PDB files with explicit hydrogen atoms.

This is a **software and computational workflow validation**, not an experimental benchmark of ncAA incorporation success.

### Test structures

| Protein | PDB ID | Experimental method | Resolution | Residues scored |
|---|---|---|---|---|
| T4 lysozyme | 1L63 | X-ray crystallography | 1.75 Å | 162/162 |
| Bovine pancreatic RNase A | 7RSA | X-ray crystallography | 1.26 Å | 124/124 |

Both structures were screened using 12 discrete pAzF rotamers per residue, with a fixed protein structure and heavy-atom steric scoring.

### Geometric screening results

| Metric | T4 lysozyme | RNase A |
|---|---:|---:|
| Residues evaluated | 162 | 124 |
| Successfully scored | 162 | 124 |
| Failed | 0 | 0 |
| Rotamers per site | 12 | 12 |
| Geometry favorable | 60 | 54 |
| Geometry limited | 63 | 40 |
| Geometry unfavorable | 39 | 30 |

The geometric tiers use default heuristic thresholds: minimum steric score ≤ 10.0 and low-clash rotamer fraction ≥ 0.5.

Similar tier distributions across the two proteins should not be interpreted as evidence of predictive calibration or comparable experimental incorporation probabilities.

### Explicit-hydrogen compatibility

The T4 lysozyme input contained no explicit hydrogen atoms, while the RNase A input contained 996 hydrogen ATOM records.

The initial RNase A screening failed at all 124 residues with `KeyError: 'H'`, because explicit hydrogen atoms were included in the steric environment but were absent from the van der Waals radius lookup.

The scoring implementation was updated to exclude hydrogen and deuterium atoms from the environment, consistent with the existing heavy-atom-only pAzF side-chain scoring.

After this correction, all 124 RNase A residues were successfully scored.

A regression test was added to verify that adding explicit H/D records does not change the 12 rotamer steric scores for an otherwise identical heavy-atom structure.

### CLI failure reporting

After completing feature generation and writing artifacts, the ranking CLI distinguishes between successful, partially failed, and unsuccessful screening runs. Input and earlier pipeline errors can stop before artifacts are written.

- Fully successful runs return exit code 0.
- Runs with at least one successfully scored residue but some failed sites return exit code 0 with a warning.
- Runs with no successfully scored residues return exit code 1.

Diagnostic CSV and metadata files are preserved even when no residues are successfully scored.

### RNase A disulfide-bond case study

RNase A contains four native disulfide bonds:

- C26–C84
- C40–C95
- C58–C110
- C65–C72

Six cysteine residues were classified as `geometry_unfavorable`, while C40 and C58 were classified as `geometry_limited`.

C40 and C58 illustrate an important limitation: a site may accommodate some pAzF rotamers geometrically while still being biologically unsuitable for substitution because it participates in an essential structural constraint.

The current geometric tiers do not explicitly encode disulfide-bond preservation.

### Automated tests

At the completion of this smoke-validation phase, the test suite contained **85 passing tests**, including regression tests for explicit hydrogen compatibility and CLI failure handling.

### Interpretation and remaining work

The two-protein smoke test demonstrates that the implemented workflow can process both tested structures and generate complete residue-level geometric screening outputs.

It does not establish:

- Experimental pAzF incorporation success.
- Retention of protein folding, stability, or catalytic activity.
- Chemical accessibility of the azide group.
- Quantitative agreement with published incorporation datasets.
- Generalization across a broad distribution of protein structures.

The next scientific milestone is a retrospective benchmark using published site-specific experimental outcomes, with comparison against simple structural baselines and careful handling of positive-unlabeled data.

**M4.4 conclusion:** Cross-protein computational smoke validation passed for the two tested structures. Experimental predictive validation remains outstanding.
