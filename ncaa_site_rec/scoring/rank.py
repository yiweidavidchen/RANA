from ncaa_site_rec.models import CandidateSite

DEFAULT_FUNCTIONAL_ZONE_A = 6.0

def apply_functional_gate(site: CandidateSite, threshold_a: float = DEFAULT_FUNCTIONAL_ZONE_A) -> bool:
    distances = [site.features.dist_to_catalytic_site, site.features.dist_to_binding_site]
    finite = [d for d in distances if d is not None]
    return any(d < threshold_a for d in finite)

def score_site(site: CandidateSite) -> CandidateSite:
    if apply_functional_gate(site):
        site.composite_score = None
        site.recommendation_tier = "avoid"
        site.reason = "Inside the user-defined catalytic/binding safety zone."
        return site
    site.composite_score = 0.0
    site.recommendation_tier = "conditional"
    site.reason = "Eligible site; v0.1 scoring weights not yet implemented."
    return site
