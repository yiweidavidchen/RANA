from ncaa_site_rec.models import CandidateSite, CandidateFeatures
from ncaa_site_rec.scoring.rank import apply_functional_gate, score_site

def test_functional_gate_excludes_close_site():
    site = CandidateSite(structure_id="test", chain="A", residue_number=10, wt_residue="ALA", target_ncaa_id="pAzF", features=CandidateFeatures(dist_to_catalytic_site=4.5, dist_to_binding_site=12.0))
    assert apply_functional_gate(site, threshold_a=6.0) is True
    assert score_site(site).recommendation_tier == "avoid"

def test_distant_site_is_not_hard_excluded():
    site = CandidateSite(structure_id="test", chain="A", residue_number=50, wt_residue="SER", target_ncaa_id="pAzF", features=CandidateFeatures(dist_to_catalytic_site=14.0, dist_to_binding_site=10.0))
    assert apply_functional_gate(site, threshold_a=6.0) is False
