# Design notes

## Data sources

| Data | Source | Notes |
|---|---|---|
| ncAA rotamer / structural params | SwissSidechain | primary source for v1 (azA confirmed present) |
| ncAA structural cross-ref | PDB Chemical Component Dictionary | fallback / validation for ncAAs not in SwissSidechain (e.g. azF) |
| ddG-ready residue params | Rosetta noncanonical residue_type_sets | plugs into existing cartesian_ddG pipeline |
| Physicochemical descriptors | computed via RDKit from SMILES | not tabulated anywhere off-the-shelf for ncAAs; this is the gap this project partly fills |
| Suppression/incorporation efficiency (aaRS/tRNA pairs) | NOT modeled in v1 | user asserts a working orthogonal pair; future linked repo covers this properly |

Verify current availability/URLs for SwissSidechain and CCD endpoints before
building hard dependencies — not confirmed live as of scaffolding.

## Required user inputs

- Structure: PDB file (or sequence + fold via existing Boltz pipeline)
- Target ncAA: SMILES or resolvable name (SwissSidechain / CCD ID)
- Catalytic residue list (required — not inferred)
- Binding-site residue list (required — not inferred)
- Oligomer interface residues (optional)

## Data schema

```
NCAA
├── id                    # e.g. "azA"
├── name
├── smiles
├── source                # "swiss-sidechain" | "pdb-ccd" | "manual"
├── parent_canonical_aa   # e.g. "ALA"
├── properties            # RDKit-computed, same axes as amino-acid property explorer
│   ├── hydropathy
│   ├── volume
│   ├── charge_ph7
│   ├── aromaticity
│   ├── rotatable_bonds
│   └── hbond_donors_acceptors
├── reactive_handle       # "azide" | "alkyne" | "photocage" | "none"
└── rotamer_params_path

Structure
├── id
├── pdb_path
├── source                # "user_upload" | "boltz_predicted" | "alphafold"
├── catalytic_residues    # list[int], user-provided
├── binding_site_residues # list[int], user-provided
└── oligomer_interfaces   # list[int], optional

CandidateSite
├── structure_id
├── residue_number
├── wt_residue
├── target_ncaa_id
├── features
│   ├── sasa
│   ├── cavity_volume_available
│   ├── dist_to_catalytic_site      # v1: used as binary safety gate, not continuous score
│   ├── dist_to_binding_site        # same
│   ├── ddg_predicted               # canonical->ncAA if params exist, else nearest-canonical-analog proxy (flag as approximation)
│   └── load_bearing_flag           # from ROSELIA-derived classifier
├── composite_score
└── recommendation_tier   # "recommended" | "conditional" | "avoid"
```

## v1 feature set (5, deliberately reduced from full schema)

1. SASA (solvent accessibility)
2. Distance to catalytic/binding site — binary gate: exclude if below threshold,
   not a weighted continuous term
3. ddG destabilization estimate (cartesian_ddG, canonical-analog proxy if no
   ncAA-specific params)
4. Basic steric/cavity check
5. Load-bearing flag (ROSELIA positioning-network classifier)

Deferred to later versions: RDKit property vector, suppression-context
features, oligomer-interface handling beyond a simple exclusion.

## Scope note: catalytic-zone sites

Sites inside the catalytic/binding zone are excluded from the "good
incorporation site" ranking, not scored low. Installing an ncAA there is a
different use case (mechanistic rescue, crosslinking/trapping probes,
deliberate loss-of-function) with different design criteria than standard
conjugation/labeling incorporation. v1 does not attempt to rank this category.
