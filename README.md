# RANA

**RANA** is a structure-guided screening tool for prioritizing protein sites for non-canonical amino acid (ncAA) incorporation.

> **Core question:** Where can we introduce new chemical functionality into an existing protein structure?

**Mission**: RANA aims to reduce the experimental search burden of ncAA incorporation through structure-guided site prioritization.

RANA `0.1.0.dev0` focuses on **p-azido-L-phenylalanine (pAzF / AzF; PDB CCD `4II`)**, an aromatic ncAA containing a bioorthogonal azide handle.

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
cd RANA
python -m pip install -e .
```

The declared runtime dependencies are NumPy, pandas, Biopython, and RDKit;
the installation command installs them. See [reproducible examples](docs/examples.md)
for an isolated environment, both public structures, and recorded run results.

For development and testing:

```bash
python -m pip install -e ".[dev]"
# Download data/raw/1L63.pdb as shown below before running the full suite.
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

The functional-residue IDs above are syntax examples, not validated catalytic-site annotations for this structure. These optional annotations must occur in the selected chain and have Cα coordinates. The legacy `--catalytic-residues` and `--binding-site-residues` options reject nonempty lists.

**Important:** Functional-residue annotations provide minimum Cα distance features only. They do not exclude residues or affect ranks or tiers.

## Output

A successful ranking run produces two files:

```text
data/processed/t4l_pazf_ranked.csv
data/processed/t4l_pazf_ranked.metadata.json
```

The CSV contains residue identities, structural features, steric scores, rotamer statistics, ranking information, screening tiers, and diagnostic status fields. Rows remain in residue order. The three independent ranks use minimum steric score (ascending), RSA (descending), and low-clash fraction (descending), with shared minimum ranks for ties. There is no composite score. SASA, packing, and functional distances do not determine the tiers.

The metadata records input structure identity and SHA-256 hash, selected parameters, output hash, available Git revision information, and run summary statistics. Run from the repository root for meaningful Git provenance; record dependency versions separately, since the CLI does not include them in its sidecar.

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

## Retrospective benchmark pilot (M5)

The M5 first delivery is complete; see the [benchmark evidence and pilot
index](docs/benchmarks/README.md) for curated T4 lysozyme stability and ferritin
conjugation records, human image review, exploratory comparisons and reproduction
instructions. These are small retrospective pilots. They do not establish
predictive accuracy or generalization; the current reproduction level is curated
tables to analysis, not a complete portable structure-to-scan pipeline.

## Computational smoke validation

The historical smoke runs exercised two experimental protein structures:

| Protein | PDB | Residues scored | Rotamers per site |
|---|---|---:|---:|
| T4 lysozyme | 1L63 | 162/162 | 12 |
| Bovine pancreatic RNase A | 7RSA | 124/124 | 12 |
| **Total** | | **286/286** | |

The earlier smoke-validation phase reported 85 passing tests. See
[Validation](docs/validation.md) for the independently rerun M4.6 results and
[examples](docs/examples.md) for reproducible commands and environment details.

These results demonstrate successful execution on two different protein structures. They do not establish predictive accuracy for ncAA incorporation or experimental protein function.

This section describes the historical computational smoke tests only. The
current literature-based retrospective pilot is documented in the
[M5 benchmark index](docs/benchmarks/README.md). Current insertion-code repair
checks are recorded separately in the [M6 validation summary](docs/m6_insertion_code_validation.md).

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
| M4.6 | Repository documentation and reproducibility cleanup |
| M5 | First delivery complete: small retrospective literature pilots and exploratory baseline comparisons |
| M6 | Insertion-code reliability work in progress; broader structure-sensitivity and application scope planned separately |
| Later release planning | Validation evidence, independent datasets, and packaging criteria to be agreed separately |
| Future | Additional ncAAs, functional-group accessibility, stronger structural and energetic models |

## Status

**Research software under active development.**

RANA currently prioritizes sites based on geometric accommodation, not experimentally validated incorporation success. Interfaces, ranking heuristics, and scientific scope may evolve as additional evidence becomes available.

See [Design and implementation status](docs/design.md) for active code paths,
historical proposals, input handling, and future research boundaries.
