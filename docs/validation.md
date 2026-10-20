# Validation plan

## v0.1 goal

Demonstrate that RANA can produce a complete, interpretable pAzF site ranking for a real protein and compare the ranking with published site-specific measurements. The first benchmark target is **T4 lysozyme**.

## Important distinction

Published incorporation sites are not automatically "the correct sites." A published site establishes that it was tested and may establish that it worked under a particular protocol. It does not prove that untested positions would fail.

Therefore RANA should be evaluated as a **ranking / enrichment** method rather than a binary classifier unless true negative labels are available.

## Development-vs-validation split

1. define the initial v0.1 feature set and scoring rules;
2. run the full T4 lysozyme scan;
3. save the ranking;
4. overlay published pAzF test sites;
5. inspect agreement and failure modes;
6. if T4L labels are used to tune thresholds or weights, treat T4L as a development set;
7. freeze v1.0 scoring;
8. evaluate on an independent protein/dataset.

## Primary v0.1 outputs

For each literature-tested site:

- raw rank
- percentile rank among eligible residues
- recommendation tier
- individual structural features
- reason
- experimental outcome(s), if available

Suggested percentile:

```text
percentile = 1 - (rank - 1) / (N_eligible - 1)
```

## Experimental outcomes should remain separate

Where available, keep these labels separate:

```text
incorporation_success
conjugation_or_labeling_efficiency
protein_stability
residual_function
```

RANA v0.1 primarily addresses structural accessibility and structural/functional tolerance, **not** translational incorporation efficiency.

## First benchmark: T4 lysozyme

Run RANA across the entire protein, not only the published test sites. Ask whether experimentally tolerated pAzF sites are enriched toward the top, disruptive sites rank lower, and the full method improves on a SASA-only baseline.

## Baselines

At minimum compare:

1. SASA-only ranking
2. SASA + functional-zone exclusion
3. full v0.1 RANA

## Known limitations

- v0.1 supports one ncAA: pAzF.
- pAzF rotamers may use a Phe-derived proxy rather than a validated pAzF-specific energetic library.
- WT SASA is not equivalent to reactive-handle SASA.
- structural site compatibility is not the same as aaRS/tRNA suppression efficiency.
- user-defined catalytic/binding annotations can be incomplete or subjective.
- retrospective literature datasets may contain positive-unlabeled bias.
- a small number of experimentally tested sites limits statistical power.
- catalytic-zone ncAA engineering is outside the normal ranking scope.

## v0.1 stopping rule

Tag `v0.1.0` when:

1. the CLI accepts a T4 lysozyme PDB, pAzF, and functional-site annotations;
2. all residues are enumerated;
3. the v0.1 feature set runs end-to-end;
4. a ranked CSV is produced;
5. each site receives a tier and explanation;
6. published T4L pAzF sites can be overlaid for a first retrospective sanity check;
7. approximations and limitations are documented.

---

## M4.4 — Cross-protein computational smoke validation

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

The ranking CLI now distinguishes between successful, partially failed, and unsuccessful screening runs.

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