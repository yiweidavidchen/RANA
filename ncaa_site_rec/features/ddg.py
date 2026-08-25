from ncaa_site_rec.models import StabilityEstimate

def estimate_stability(*args, **kwargs) -> StabilityEstimate:
    """Optional stability-estimate hook; do not claim pAzF-specific ddG unless validated."""
    return StabilityEstimate(value=None, method="not_run", substitution=None, is_proxy=True)
