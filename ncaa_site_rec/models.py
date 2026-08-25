from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

@dataclass
class NCAA:
    id: str
    display_name: str
    aliases: list[str]
    parent_canonical_aa: str
    pdb_ccd_id: str | None = None
    smiles: str | None = None
    inchikey: str | None = None
    reactive_handle: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class Structure:
    id: str
    pdb_path: Path
    source: str = "user_upload"
    catalytic_residues: list[int] = field(default_factory=list)
    binding_site_residues: list[int] = field(default_factory=list)
    oligomer_interfaces: list[int] = field(default_factory=list)

@dataclass
class StabilityEstimate:
    value: float | None = None
    method: str | None = None
    substitution: str | None = None
    is_proxy: bool = True

@dataclass
class CandidateFeatures:
    wt_sasa: float | None = None
    dist_to_catalytic_site: float | None = None
    dist_to_binding_site: float | None = None
    local_packing: float | None = None
    steric_proxy: float | None = None
    stability_estimate: StabilityEstimate = field(default_factory=StabilityEstimate)
    load_bearing_flag: bool | None = None

@dataclass
class CandidateSite:
    structure_id: str
    chain: str
    residue_number: int
    wt_residue: str
    target_ncaa_id: str
    features: CandidateFeatures = field(default_factory=CandidateFeatures)
    composite_score: float | None = None
    recommendation_tier: str | None = None
    reason: str | None = None
