# RANA — Residue Assessment for Noncanonical Amino acids

Given a protein structure and a target non-canonical amino acid (ncAA), recommend
which residue positions are safe to mutate for ncAA incorporation — and flag
positions to avoid because they're structurally load-bearing or catalytically
important.

Builds on feature-extraction and load-bearing-residue classification methodology
from the ROSELIA project (BglB catalytic positioning network).

## Status: v1 (in progress)

v1 scope is intentionally narrow — one ncAA, one test protein, CLI only:

| | v1 | Later |
|---|---|---|
| ncAA | azido-alanine (azA) | azF, BCN-Lys, pAcF, photocaged residues |
| Interface | CLI | Streamlit / web front end |
| ncAA database | manual, single-entry | full SwissSidechain + PDB CCD integration |
| Orthogonal pair compatibility | not modeled (user asserts) | separate linked repo |
| Catalytic-zone sites | excluded from ranking entirely | separate "mechanistic probe candidate" mode |

See `docs/design.md` for the full feature schema and scoring rationale, and
`docs/validation.md` for the literature-comparison validation plan.

## Quick start (planned interface)

```bash
rana \
  --pdb structure.pdb \
  --target-ncaa azA \
  --catalytic-residues 164,353,406 \
  --binding-site-residues 19,295 \
  --out candidate_sites.csv
```

## Why this exists

Most protein engineering tooling (PyRosetta, FoldX, ESM-based predictors) treats
the 20 canonical residues as the alphabet and bolts ncAAs on as an afterthought.
Site selection for ncAA incorporation is currently mostly ad hoc — structural
intuition plus trial and error. This tool reframes the question as a ranking
problem over structural + chemical features, reusing methodology originally
built for classifying catalytically load-bearing residues.
