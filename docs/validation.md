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
