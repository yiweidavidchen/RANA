"""Core data structures for the ncAA site recommender.

Mirrors the schema in docs/design.md. Kept as plain dataclasses for v1 —
no ORM/DB layer until there's an actual need for persistence beyond a
single run.
"""
from dataclasses import dataclass, field


@dataclass
class NCAA:
    id: str                      # e.g. "azA"
    name: str
    smiles: str
    source: str                  # "swiss-sidechain" | "pdb-ccd" | "manual"
    parent_canonical_aa: str      # e.g. "ALA"
    reactive_handle: str          # "azide" | "alkyne" | "photocage" | "none"
    rotamer_params_path: str | None = None
    properties: dict = field(default_factory=dict)  # filled in by features/properties.py


@dataclass
class Structure:
    id: str
    pdb_path: str
    source: str                  # "user_upload" | "boltz_predicted" | "alphafold"
    catalytic_residues: list[int] = field(default_factory=list)
    binding_site_residues: list[int] = field(default_factory=list)
    oligomer_interfaces: list[int] = field(default_factory=list)


@dataclass
class CandidateSite:
    structure_id: str
    residue_number: int
    wt_residue: str
    target_ncaa_id: str
    features: dict = field(default_factory=dict)
    composite_score: float | None = None
    recommendation_tier: str | None = None  # "recommended" | "conditional" | "avoid"
