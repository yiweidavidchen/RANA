# RANA Design Notes

## 1. Core question

RANA is a structure-aware recommender for non-canonical amino acid (ncAA) incorporation sites.

Its core question is:

> **Where can I install this ncAA in this protein, for this engineering objective, without introducing unacceptable structural or functional risk?**

Conceptually:

```text
Recommendation =
    f(protein structural environment, ncAA chemistry, engineering objective)
```

v0.1 implements a restricted version:

```text
protein structure + pAzF + safe-incorporation objective
                         ↓
                 ranked candidate sites
```

The first benchmark system is T4 lysozyme.

## 2. Design principles

### 2.1 Exhaustive site enumeration, staged evaluation

RANA evaluates the entire protein rather than requiring pre-selected mutation sites.

```text
all protein residues
        ↓
functional / structural hard gates
        ↓
cheap structural features for all eligible sites
        ↓
ncAA-specific conformer / steric evaluation
        ↓
compatibility ranking
        ↓
optional expensive refinement
```

Cheap calculations should run exhaustively. Expensive calculations such as Rosetta stability estimates should be restricted to shortlisted candidates when possible.

### 2.2 Separate generic protein features from ncAA-specific features

```text
RANA core
├── structure parsing
├── residue enumeration
├── SASA / accessibility
├── local packing
├── functional-site annotations
├── generic structural-risk features
├── ranking / tiering infrastructure
└── output / explanation

ncAA-specific model
├── chemical identity
├── parent canonical amino acid
├── geometry
├── conformer / rotamer model
├── steric envelope
├── reactive-handle representation
└── application-specific features
```

Future ncAAs should reuse the RANA core while supplying their own chemical and conformational models.

### 2.3 Separate structural compatibility from engineering objective

Long-term:

```text
Structural Compatibility Score
            +
Application / Objective Score
            ↓
Recommendation
```

Safe labeling generally favors exposed, non-functional sites; photocrosslinking may require proximity to an interaction partner; photocaging may deliberately target a functional residue; metal-binding ncAAs may require specific coordination geometry.

v0.1 implements only the structural-compatibility / safe-incorporation problem.

## 3. v0.1 target ncAA: pAzF

The first supported ncAA is **p-azido-L-phenylalanine (pAzF / AzF)**.

- PDB CCD ID: `4II`
- parent canonical amino acid: `PHE`
- reactive handle: azide

RANA should retain authoritative identifiers wherever possible:

```text
display_name
aliases
PDB_CCD_ID
SMILES
InChIKey
parent_canonical_aa
identity_source
```

## 4. Data sources

No single ncAA database is assumed to contain every required resource.

| Data | Preferred source | RANA use |
|---|---|---|
| ncAA chemical identity | PDB Chemical Component Dictionary | canonical residue identity |
| SMILES / InChI cross-check | PubChem or equivalent authoritative source | chemistry validation and descriptors |
| experimental ncAA geometry | PDB structures containing the ncAA | geometry reference / validation |
| parent canonical rotamers | established canonical rotamer library | v0.1 conformational proxy |
| ncAA-specific rotamers | validated literature or RANA-generated resource | future higher-accuracy modeling |
| Rosetta ncAA parameters | verified existing resource or documented RANA-generated parameters | optional energetic refinement |
| physicochemical descriptors | computed with documented methods | ncAA characterization |
| experimental site outcomes | primary literature | retrospective validation |
| suppression / aaRS efficiency | not modeled in v0.1 | future separate layer |

SwissSidechain may be used when a target ncAA is available there, but it is optional rather than mandatory.

## 5. Required user inputs

### v0.1

Required:
- protein structure (`PDB`)
- target ncAA (`pAzF`)
- catalytic residue list
- binding-site residue list

Optional:
- oligomer-interface annotations
- user-defined exclusion sites

Catalytic and binding residues are user-supplied in v0.1 and are not inferred automatically.

## 6. Data schema

```text
NCAA
├── id
├── display_name
├── aliases
├── smiles
├── inchikey
├── pdb_ccd_id
├── parent_canonical_aa
├── identity_source
├── geometry_source
├── rotamer_source
├── parameter_source
├── reactive_handle
└── properties
```

```text
Structure
├── id
├── pdb_path
├── source
├── catalytic_residues
├── binding_site_residues
└── oligomer_interfaces
```

```text
CandidateSite
├── structure_id
├── chain
├── residue_number
├── wt_residue
├── target_ncaa_id
├── features
│   ├── wt_sasa
│   ├── relative_sasa
│   ├── dist_to_catalytic_site
│   ├── dist_to_binding_site
│   ├── local_packing
│   ├── steric_proxy
│   ├── viable_rotamers
│   ├── total_rotamers
│   ├── stability_estimate
│   │   ├── value
│   │   ├── method
│   │   ├── substitution
│   │   └── is_proxy
│   └── load_bearing_risk
├── compatibility_score
├── recommendation_tier
├── confidence
└── reason
```

## 7. v0.1 feature set

### 7.1 Relative solvent accessibility

Use relative solvent accessibility where possible:

```text
relative_SASA = observed_residue_SASA / reference_maximum_SASA
```

Future versions should distinguish WT residue SASA, mutant ncAA SASA, and reactive-handle SASA.

### 7.2 Functional-site distance

Distance to catalytic and binding-site residues is primarily a **safety gate**, not a continuous weighted reward. Prefer minimum heavy-atom distances over C-alpha distance alone.

### 7.3 Local packing

Possible implementations include neighboring heavy-atom density, side-chain contact density, buried-contact fraction, or local coordination number. Normalize to a packing-tolerance measure where high values indicate a permissive environment.

### 7.4 pAzF conformer / rotamer compatibility

For v0.1:

```text
Phe-like chi1 / chi2 states
        +
pAzF heavy-atom geometry
        ↓
site-specific steric evaluation
```

Initial metric:

```text
rotamer_compatibility =
    number_of_viable_pAzF_rotamers / number_of_tested_pAzF_rotamers
```

This must be labeled as a canonical-parent proxy, not a validated pAzF energetic rotamer library.

### 7.5 Load-bearing risk

v0.1 may use a simple structural heuristic, ROSELIA-inspired structural features, or no load-bearing contribution to the composite score. Do not describe it as a validated classifier unless one has actually been trained and benchmarked.

### 7.6 Stability estimate

Stability is optional in v0.1. Canonical-analog calculations must be explicitly marked as proxies:

```text
stability_estimate
├── value
├── method
├── substitution
└── is_proxy
```

## 8. Recommendation architecture

```text
functional hard gates
        ↓
structural vetoes
        ↓
normalized sub-scores
        ↓
compatibility score
        ↓
warning / confidence logic
        ↓
recommendation tier
```

### 8.1 Hard gates

For safe incorporation, sites closer than a configurable threshold to catalytic or binding residues are excluded. An initial default around 6 Å may be used as a modeling choice, not a biological constant.

### 8.2 Structural vetoes

Examples include extreme burial, severe steric clash, and near-zero viable rotamer fraction.

### 8.3 Normalized sub-scores

```text
A = accessibility
R = ncAA rotamer compatibility
P = local packing tolerance
L = load-bearing risk
```

### 8.4 Compatibility score

A weighted geometric mean is preferred:

```text
Compatibility =
    100 × A^wA × R^wR × P^wP × (1-L)^wL
```

with weights summing to 1.

One initial pAzF hypothesis is:

```text
wA = 0.30
wR = 0.35
wP = 0.25
wL = 0.10
```

Initial weights are hypotheses, not fitted truths, and should be frozen before an unbiased retrospective comparison.

### 8.5 Recommendation tier

Possible outputs:

```text
recommended
conditional
avoid
```

Compatibility score is not identical to recommendation tier. Warnings, missing annotations, proxy calculations, or applicability-domain concerns may downgrade a tier.

### 8.6 Explanation

Every recommendation should expose its reasoning, e.g.:

```text
Recommended:
high solvent accessibility; outside the functional zone;
7/9 pAzF conformers are sterically viable; low local packing.
```

## 9. Validation philosophy

RANA is a ranking system. A published successful incorporation site is a known positive, but untested sites are not automatically negatives.

Retrospective outputs should include raw rank, percentile rank, recommendation tier, feature values, and experimental outcome.

Keep experimental outcomes separate where possible:

```text
incorporation success
labeling / conjugation efficiency
protein stability
residual activity / function
```

## 10. v0.1 benchmark

The first benchmark is T4 lysozyme with pAzF. RANA should scan the complete protein.

Compare at least:

```text
Model 0: accessibility only
Model 1: accessibility + pAzF steric compatibility
Model 2: accessibility + sterics + packing
Model 3: full v0.1 RANA
```

### Avoiding validation leakage

```text
define scoring rules
        ↓
freeze initial v0.1 configuration
        ↓
run complete T4L scan
        ↓
save ranking
        ↓
overlay literature outcomes
```

If T4L outcomes are used to tune weights or thresholds, T4L becomes a development dataset. v1.0 should evaluate a frozen model on an independent protein or dataset.

## 11. Computational modes

### Fast / local mode

Normal workstation:
- structure parsing
- residue enumeration
- SASA
- functional-site distances
- packing
- ncAA conformer sterics
- ranking
- explanation

### Optional high-accuracy mode

May use workstation or HPC resources for:
- Rosetta relaxation
- ncAA-specific stability calculations
- larger conformer ensembles
- structure ensembles
- other expensive refinement

RANA should remain portable and should not depend specifically on UC Davis Hive.

## 12. Future ncAA extension model

Conceptually:

```python
class NCAAModel:
    def generate_conformers(self, site):
        ...

    def steric_score(self, site):
        ...

    def handle_accessibility(self, site):
        ...

    def application_score(self, site, objective):
        ...
```

pAzF is the first implementation.

Future chemical regimes may include bulky rigid aromatic ncAAs, long flexible bioorthogonal handles, photocaged residues, and metal-binding ncAAs. These are architectural examples, not release commitments.

New ncAAs should not merely change numerical weights: different chemistries and applications may introduce genuinely new structural requirements.

## 13. What RANA v0.1 does not claim

v0.1 does not claim to predict:
- aaRS/tRNA compatibility
- amber suppression efficiency
- cellular ncAA uptake
- expression yield
- universal ncAA mutation tolerance
- active-site ncAA engineering
- photocrosslinking efficiency
- photocaging effectiveness
- metal coordination
- general protein stability
- all ncAA chemistries

Its deliberately narrow claim is:

> **RANA v0.1 provides an interpretable, structure-aware ranking of candidate pAzF incorporation sites for a safe-incorporation use case.**

## 14. v0.1 stopping rule

Tag `v0.1.0` when:

1. RANA accepts a T4 lysozyme PDB structure.
2. RANA accepts pAzF as the target ncAA.
3. Catalytic and binding-site annotations can be supplied by the user.
4. All protein residues are enumerated automatically.
5. Functional-zone gates are applied.
6. Accessibility, packing, and pAzF steric features run end-to-end.
7. Every eligible site receives a compatibility score.
8. Every site receives a recommendation tier and explanation.
9. RANA produces a complete ranked CSV.
10. Published T4L pAzF sites can be overlaid for the first retrospective sanity check.
11. Approximations and limitations are explicitly documented.

Anything beyond these requirements belongs to v1.0 or later.
