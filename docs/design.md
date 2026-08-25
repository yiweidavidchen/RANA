# Design notes

## Design principle

RANA uses **exhaustive site enumeration with staged computational evaluation**. Cheap structural features are computed for every residue. Expensive calculations are reserved for plausible candidates rather than applied blindly to every position.

```text
all residues
    ↓
hard exclusions
    ↓
cheap structural features
    ↓
pAzF steric / rotamer compatibility
    ↓
shortlist
    ↓
optional expensive stability calculations
```

## v0.1 target ncAA

**p-azido-L-phenylalanine (pAzF / AzF)**

Canonical identity anchor:

- PDB CCD ID: `4II`
- parent canonical residue: `PHE`
- chemical identity should be verified from authoritative chemistry resources before hard-coding
- short aliases such as `AzF` are aliases, not the primary chemical identity

## Data sources

| Data | Primary source | Notes |
|---|---|---|
| ncAA chemical identity | PDB Chemical Component Dictionary | authoritative residue identity and polymer status |
| SMILES / InChI cross-check | PubChem or equivalent authoritative chemistry source | identity cross-check and descriptor input |
| experimentally observed ncAA geometry | PDB structures containing CCD `4II` | structural reference, not a universal rotamer library |
| canonical parent rotamers | Rosetta / Dunbrack-style Phe rotamers | v0.1 proxy for pAzF chi states |
| ncAA-specific rotamers | generated / literature | deferred unless a trustworthy source is established |
| Rosetta ncAA params | RANA-generated and documented, or verified existing source | not assumed to be official |
| physicochemical descriptors | RDKit where well-defined | method/provenance should be retained |
| experimental site labels | primary literature | used for retrospective validation |
| suppression/incorporation efficiency | not modeled in v0.1 | user is assumed to have a working orthogonal system |

SwissSidechain may be used opportunistically for ncAAs it contains, but it is **not** the mandatory primary source for RANA.

## Required user inputs

- Structure: PDB file
- Target ncAA: `pAzF` in v0.1
- Catalytic residue list: required, not inferred
- Binding-site residue list: required, not inferred
- Oligomer-interface residue list: optional

## Data schema

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

Structure
├── id
├── pdb_path
├── source
├── catalytic_residues
├── binding_site_residues
└── oligomer_interfaces

CandidateSite
├── structure_id
├── chain
├── residue_number
├── wt_residue
├── target_ncaa_id
├── features
│   ├── wt_sasa
│   ├── dist_to_catalytic_site
│   ├── dist_to_binding_site
│   ├── local_packing
│   ├── steric_proxy
│   ├── stability_estimate
│   │   ├── value
│   │   ├── method
│   │   ├── substitution
│   │   └── is_proxy
│   └── load_bearing_flag
├── composite_score
├── recommendation_tier
└── reason
```

## Accessibility

v0.1 uses **WT residue SASA** as the inexpensive accessibility feature. Future versions should distinguish `wt_sasa`, `mutant_sasa`, and `reactive_handle_sasa`.

## Functional-zone handling

Distance to catalytic and binding-site residues is a **hard safety gate** in the normal site-ranking mode. Sites inside the threshold are excluded rather than merely receiving a low score.

## pAzF steric model in v0.1

pAzF is treated as a Phe-derived ncAA. v0.1 may use Phe-like chi1/chi2 rotamer states, pAzF heavy-atom geometry from an authoritative definition or experimental structure, and a clash/local-packing test. This must be labeled as a **canonical-parent rotamer proxy**, not a validated pAzF energetic model.

```yaml
rotamer_model:
  method: canonical_parent_proxy
  parent: PHE
  approximation: true
```

## Stability estimate

Do not expose a generic `ddg_predicted` field if the calculation is not truly pAzF-specific. Use a structured stability estimate with `value`, `method`, `substitution`, and `is_proxy`.

## Load-bearing feature

Use neutral wording such as `load_bearing_heuristic` or `ROSELIA-inspired structural features` unless a trained and benchmarked classifier actually exists.

## Scoring philosophy

1. hard exclusions first;
2. independent feature calculations;
3. few transparent weights or rules;
4. expose all component features;
5. generate a human-readable reason.

## What v0.1 is not

- an aaRS/tRNA compatibility predictor
- an ncAA incorporation-efficiency predictor
- an active-site ncAA design engine
- a universally validated stability predictor
- a general multi-ncAA framework
