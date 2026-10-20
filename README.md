# RANA

**RANA** is a structure-guided screening tool for prioritizing protein sites for non-canonical amino acid (ncAA) incorporation.

> **Core question:** Where can we introduce new chemical functionality into an existing protein structure?

RANA v0.1 focuses on **p-azido-L-phenylalanine (pAzF / AzF; PDB CCD `4II`)**, an aromatic ncAA containing a bioorthogonal azide handle.

The current implementation evaluates fixed-structure geometric accommodation. It does **not** predict experimental incorporation success, protein stability, retained activity, or labeling efficiency.

## Current capabilities

Given a protein PDB structure, RANA can:

- Enumerate residues in a selected protein chain.
- Compute solvent-accessible surface area (SASA) and relative SASA (RSA).
- Estimate local packing using neighboring Cα atoms.
- Optionally calculate distances to user-specified functional residues.
- Generate and evaluate 12 discrete pAzF side-chain rotamers per site.
- Calculate heuristic van der Waals overlap scores using heavy atoms.
- Report minimum steric score and low-clash rotamer fraction.
- Provide independent steric, accessibility, and rotamer-robustness ranks.
- Assign interpretable geometric screening tiers.
- Export a residue-level CSV and JSON reproducibility metadata.

The current scoring uses a fixed protein backbone and discrete side-chain sampling. It does not explicitly model protein relaxation or energetic consequences of substitution.

## Installation

RANA requires Python 3.10 or later.

```bash
git clone https://github.com/yiweidavidchen/RANA.git
cd rana
pip install -e .
```

The pAzF conformer-generation workflow also requires RDKit. Its installation requirements should be verified against the project's dependency configuration before distribution.

For development and testing:

```bash
pip install -e ".[dev]"
python -m pytest tests/ -q
```

## Quick start

Download a test protein structure from the RCSB Protein Data Bank:

```bash
mkdir -p data/raw
curl -L https://files.rcsb.org/download/1L63.pdb -o data/raw/1L63.pdb
```

Run the pAzF geometric screening:

```bash
rana rank \
  --pdb data/raw/1L63.pdb \
  --chain A \
  --ncaa pazf \
  --seed 42 \
  --output data/processed/t4l_pazf_ranked.csv
```

Optionally provide functional residues:

```bash
rana rank \
  --pdb data/raw/1L63.pdb \
  --chain A \
  --ncaa pazf \
  --functional-residues A:11,A:20 \
  --output data/processed/t4l_pazf_ranked.csv
```

The functional-residue IDs above are syntax examples, not validated catalytic-site annotations for this structure.

**Important:** Functional-residue annotations currently provide distance features. They do not automatically exclude residues from geometric screening.

## Output

A successful ranking run produces two files:

```text
data/processed/t4l_pazf_ranked.csv
data/processed/t4l_pazf_ranked.metadata.json
```

The CSV contains residue identities, structural features, steric scores, rotamer statistics, ranking information, screening tiers, and diagnostic status fields.

The metadata records input structure identity and SHA-256 hash, selected parameters, output hash, available Git revision information, and run summary statistics.

### Screening tiers

| Tier | Interpretation |
|---|---|
| `geometry_favorable` | Low minimum steric overlap and sufficiently many low-clash rotamers |
| `geometry_limited` | At least one low-clash rotamer, but limited rotamer robustness |
| `geometry_unfavorable` | No rotamer meets the minimum-overlap threshold |
| `not_evaluated` | Geometric screening was skipped or failed |

Default thresholds:

- Low-clash steric score: ≤ 10.0
- Favorable low-clash rotamer fraction: ≥ 0.5

These thresholds are engineering heuristics, **not experimentally calibrated success probabilities**.

## Computational smoke validation

The current pipeline has been tested on two experimental protein structures:

| Protein | PDB | Residues scored | Rotamers per site |
|---|---|---:|---:|
| T4 lysozyme | 1L63 | 162/162 | 12 |
| Bovine pancreatic RNase A | 7RSA | 124/124 | 12 |
| **Total** | | **286/286** | |

The test suite currently contains **85 passing tests**.

These results demonstrate successful execution on two different protein structures. They do not establish predictive accuracy for ncAA incorporation or experimental protein function.

See [Validation](docs/validation.md) for the scientific benchmarking plan and limitations.

## Important limitations

- Only pAzF is currently supported.
- Protein structures are treated as fixed during site scoring.
- Steric overlap is a geometric heuristic, not a substitution free energy.
- Explicit hydrogen and deuterium atoms are excluded from steric scoring.
- The 12 sampled rotamers do not exhaust all possible side-chain conformations.
- The azide handle's chemical accessibility is not independently evaluated.
- Functional-site distances do not establish functional tolerance.
- Disulfide bonds and other structural constraints are not automatically incorporated into the recommendation tiers.
- Incorporation efficiency depends on the expression system, orthogonal translation machinery, and experimental conditions.
- The current thresholds have not been calibrated against experimental outcomes.

## Roadmap

| Stage | Scope |
|---|---|
| v0.1 development | pAzF structural features, geometric scanning, interpretable ranking, CLI, metadata |
| M4.4 | Cross-protein computational smoke validation |
| M5 | Literature-based retrospective benchmark and baseline comparisons |
| v1.0 | Improved scoring validation, independent experimental datasets, and robust packaging |
| Future | Additional ncAAs, functional-group accessibility, stronger structural and energetic models |

## Status

**Research software under active development.**

RANA currently prioritizes sites based on geometric accommodation, not experimentally validated incorporation success. Interfaces, ranking heuristics, and scientific scope may evolve as additional evidence becomes available.