"""Composite scoring and tiering for candidate sites.

v1 logic (see docs/design.md):
- catalytic/binding-site distance -> binary gate (exclude if within threshold),
  NOT a weighted continuous term
- load_bearing_flag=True -> automatic "avoid", regardless of other scores
- otherwise: combine SASA, ddg_estimate, cavity_volume_available into a
  composite score and assign a tier

Threshold values (distance cutoff, ddG cutoff) are placeholders — need to be
set from literature precedent or empirically once validation (docs/validation.md)
is run, not guessed.
"""
from rana.models import CandidateSite

CATALYTIC_DISTANCE_CUTOFF_ANGSTROM = 8.0  # placeholder, needs validation
DDG_AVOID_THRESHOLD = 2.0                  # placeholder, Rosetta energy units


def score_site(site: CandidateSite) -> CandidateSite:
    """Mutates and returns `site` with composite_score and recommendation_tier set."""
    f = site.features

    if f.get("load_bearing_flag"):
        site.recommendation_tier = "avoid"
        site.composite_score = 0.0
        return site

    dist = min(f.get("dist_to_catalytic_site", float("inf")),
               f.get("dist_to_binding_site", float("inf")))
    if dist < CATALYTIC_DISTANCE_CUTOFF_ANGSTROM:
        site.recommendation_tier = "avoid"
        site.composite_score = 0.0
        return site

    raise NotImplementedError("composite score combination not yet implemented")
