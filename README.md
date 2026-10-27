# RANA

RANA helps protein engineers and chemical biologists shortlist protein positions
for non-canonical amino acid (ncAA) substitution experiments. It screens how
well a proposed side chain fits a supplied protein structure and reports the
geometric evidence for each site.

RANA `0.1.0.dev0` currently supports **p-azido-L-phenylalanine (pAzF / AzF;
PDB CCD `4II`)** only. This aromatic ncAA carries a bioorthogonal azide handle.
The results describe accommodation in a fixed structure. They do not predict
incorporation efficiency, expression, stability, retained activity or labeling
efficiency.

## Input and screening

Provide a protein PDB file and the chain to screen. Residue identities retain
the input chain, author residue number and insertion code. The retained protein
chains define the surrounding structural environment, so an isolated chain and
a complete assembly can give different results. Input preparation must make that
choice explicit; the ranking command does not reconstruct missing residues or
a biological assembly automatically.

For each site, RANA:

- Computes solvent-accessible surface area (SASA), the area exposed to solvent,
  and relative SASA (RSA), normalized by a reference area for that residue type.
- Counts nearby Cα atoms as a measure of local packing.
- Samples 12 discrete side-chain conformations, or rotamers, for pAzF and scores
  heavy-atom van der Waals overlaps with the retained protein environment.
- Reports the minimum overlap score and the low-clash fraction: the fraction of
  sampled conformations that meet the overlap cutoff.
- Provides separate steric, accessibility and rotamer-robustness ranks, together
  with heuristic geometric tiers. Optional functional-residue annotations add
  distance features.

The protein backbone and surrounding coordinates remain fixed. The calculation
does not model structural relaxation or the energetic consequences of substitution.

## Examples and evidence

The M5 literature retrospective pilot and M6 are complete.
The [M6 summary](docs/m6_summary.md) connects the four deliveries and explains
their results, verification levels and remaining limits.

- [Quick start](#quick-start) and [reproducible examples](docs/examples.md):
  installation, public T4 lysozyme/RNase A inputs and example commands.
- [M5 benchmark evidence](docs/benchmarks/README.md): curated T4 lysozyme stability
  and ferritin conjugation observations, human image review and exploratory analysis.
- [2FG8 ferritin reproduction](docs/reproducibility/README.md): the verified
  profile for rebuilding assembly and monomer inputs from public coordinates.
- [T4 lysozyme structure sensitivity](docs/structure_sensitivity/t4l/README.md):
  how scores, tiers and rankings change across three references with the same sequence.
- [BglB pAzF computational case](docs/computational_cases/bglb/README.md):
  a single-reference application with functional annotations shown separately.

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

The CSV retains each attempted residue, its structural features, steric scores,
rotamer statistics, ranks, tier and diagnostic status. Rows follow chain,
author residue number and insertion-code order. Failed or skipped rows retain
their diagnostic reason.

Lower minimum steric scores indicate less overlap among the sampled conformations.
Higher RSA indicates greater relative solvent exposure; a higher low-clash fraction
means more of the sampled conformations meet the cutoff. The three independent
ranks use minimum steric score in ascending order and RSA and low-clash fraction
in descending order. Tied sites share the minimum rank. There is no composite
score, and SASA, packing and functional distances do not determine the tiers.

The JSON sidecar records the input structure identity and SHA-256 hash, parameters,
output hash, available Git revision and run summary. Run from the repository root
for meaningful Git provenance. Record dependency versions separately: the CLI
sidecar does not include them.

### Screening tiers

| Tier | Interpretation |
|---|---|
| `geometry_favorable` | Low minimum steric overlap and sufficiently many low-clash rotamers |
| `geometry_limited` | At least one low-clash rotamer, but limited rotamer robustness |
| `geometry_unfavorable` | No rotamer meets the minimum-overlap threshold |
| `not_evaluated` | Geometric screening was skipped or failed |

Default thresholds:

- Low-clash steric score: ≤ 10.0 Å²
- Favorable low-clash rotamer fraction: ≥ 0.5

These thresholds are engineering heuristics, **not experimentally calibrated success probabilities**.

## Retrospective benchmark pilot (M5)

The M5 first delivery is complete; see the [benchmark evidence and pilot
index](docs/benchmarks/README.md) for curated T4 lysozyme stability and ferritin
conjugation records, human image review, exploratory comparisons and reproduction
instructions. These are small retrospective pilots. They do not establish
predictive accuracy or generalization. The M5 delivery reproduces analysis from
curated tables. The later [2FG8 workflow](docs/reproducibility/README.md) separately
verifies a specific structure-preparation-to-scan path; it does not make the
entire M5 literature workflow reproducible from raw sources.

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
| M6 | Complete: insertion-code repair, pinned 2FG8 preparation/reproduction, same-background T4L sensitivity and the BglB computational case; see the [summary](docs/m6_summary.md) |
| M7 (planned) | Support for a second ncAA, with pBpA as a candidate; not implemented |
| Later release planning | Future release criteria remain to be defined: validation evidence, independent datasets and packaging |
| Future research | Functional-group accessibility and stronger structural or energetic models |

## Status

**Research software under active development.**

RANA currently prioritizes sites based on geometric accommodation, not experimentally validated incorporation success. Interfaces, ranking heuristics, and scientific scope may evolve as additional evidence becomes available.

See [Design and implementation status](docs/design.md) for active code paths,
historical proposals, input handling, and future research boundaries.
