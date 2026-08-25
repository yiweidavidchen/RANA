"""Structural feature extraction.

v1 features, per docs/design.md:
- SASA
- distance to catalytic site (used downstream as a binary gate)
- distance to binding site (same)
- cavity/steric check

TODO: reuse ROSELIA feature-extraction code where possible instead of
reimplementing distance/SASA calculations from scratch.
"""
from rana.models import Structure


def compute_sasa(structure: Structure, residue_number: int) -> float:
    """Solvent accessible surface area for a given residue.

    Placeholder — wire up to freesasa or Rosetta's SASA calculator.
    """
    raise NotImplementedError


def distance_to_nearest(structure: Structure, residue_number: int, targets: list[int]) -> float:
    """Minimum distance (e.g. CA-CA or side-chain centroid) from residue_number
    to any residue in `targets` (catalytic or binding-site residues).
    """
    raise NotImplementedError


def cavity_volume_available(structure: Structure, residue_number: int) -> float:
    """Estimate of void space available at the site, to flag steric clash risk
    for bulkier ncAA side chains.

    Placeholder — candidate approaches: POVME, simple probe-sphere packing,
    or a Rosetta packing-based estimate.
    """
    raise NotImplementedError
