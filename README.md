# RANA

**RANA** is a structure-aware recommender for selecting protein sites for non-canonical amino acid (ncAA) incorporation.

> **Core question:** Where can I install this ncAA without breaking the protein?

RANA v0.1 focuses on **p-azido-L-phenylalanine (pAzF / AzF; PDB CCD `4II`)** and a first benchmark on **T4 lysozyme**.

## What v0.1 does

Given a protein structure (`.pdb`), a target ncAA (`pAzF` in v0.1), and user-supplied catalytic/binding-site residues, RANA enumerates the whole protein, excludes functional-zone positions, computes inexpensive structural features, estimates pAzF steric compatibility using a Phe-like rotamer proxy, assigns recommendation tiers, and returns an interpretable ranked table.

### v0.1 feature set

- solvent-accessible surface area (SASA)
- distance to catalytic residues
- distance to binding-site residues
- local packing / steric crowding
- pAzF rotamer-clash proxy using Phe-like chi states
- optional load-bearing heuristic hook

### Deliberately deferred to v1.0

- validated pAzF-specific Rosetta polymer parameterization
- ncAA-specific Cartesian ddG as a required feature
- independent-protein validation
- multi-ncAA support
- suppression / aaRS / tRNA efficiency modeling
- automatic active-site inference
- sequence-to-structure prediction

## Scientific scope

RANA predicts **structural site compatibility**, not genetic incorporation efficiency. Catalytic- and binding-zone positions are excluded from the normal safe-incorporation ranking.

## v0.1 benchmark

The first benchmark target is **T4 lysozyme** because it is small enough for exhaustive scanning and has published site-specific pAzF data with experimentally measured consequences for conjugation, stability, and activity.

The intended v0.1 stopping rule is:

> **Given a T4 lysozyme structure, RANA automatically produces a complete pAzF site-ranking CSV and overlays published test sites without using those labels to tune the initial scoring rules.**

## Quick start

```bash
pip install -e .
```

```bash
rana rank \
  --pdb data/raw/1L63.pdb \
  --ncaa pAzF \
  --catalytic-residues 11 20 \
  --binding-site-residues 11 20 26 \
  --output data/processed/t4l_pazf_ranking.csv
```

The residue lists above are examples only. Use literature-supported annotations for the actual benchmark.

## Output

Planned columns:

```text
rank
chain
residue_number
wt_residue
target_ncaa
sasa
dist_to_catalytic_site
dist_to_binding_site
local_packing
steric_proxy
load_bearing_flag
composite_score
recommendation_tier
reason
```

## Version roadmap

| Version | Scope |
|---|---|
| v0.1 | pAzF + T4 lysozyme + exhaustive structural scan + interpretable ranking + first literature sanity check |
| v1.0 | frozen scoring + quantitative retrospective benchmark + independent validation + robust packaging |
| v1.x | additional ncAAs and stronger ncAA-specific parameterization |
| v2.0 | general ncAA-specific recommendation framework with cross-ncAA validation |

## Status

Early research software. Interfaces and scoring rules may change before v1.0.
