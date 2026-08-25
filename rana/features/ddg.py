"""ddG destabilization estimate for a candidate mutation.

Reuses the cartesian_ddG pipeline already running on Hive for BglB/ROSELIA.
If the target ncAA has dedicated Rosetta params, run ddG directly against it.
Otherwise, fall back to the nearest canonical analog as a proxy and flag the
result as an approximation (see docs/validation.md, known limitations).
"""
from rana.models import NCAA, Structure


def estimate_ddg(structure: Structure, residue_number: int, ncaa: NCAA) -> tuple[float, bool]:
    """Returns (ddg_estimate, is_proxy).

    is_proxy=True means no ncAA-specific Rosetta params were available and
    the nearest canonical analog (ncaa.parent_canonical_aa) was used instead.
    Callers must propagate this flag — never present a proxy estimate as
    equivalent precision to a true ncAA-specific ddG.
    """
    raise NotImplementedError
