"""Load-bearing / catalytic positioning-network flag.

This is the one feature in the schema that isn't reconstructable from public
data sources — it comes from the ROSELIA classifier developed for the BglB
project (graph-theoretic structural features: articulation points, betweenness
centrality, H-bond bridging network membership).

v1: wraps/reuses that classifier directly rather than reimplementing it.
"""
from rana.models import Structure


def is_load_bearing(structure: Structure, residue_number: int) -> bool:
    """True if this residue is classified as part of the catalytic
    positioning/bridging network and should be excluded from incorporation
    site recommendations regardless of other feature scores.

    Placeholder — import and call the ROSELIA classifier here once that
    code is factored out into an importable module.
    """
    raise NotImplementedError
