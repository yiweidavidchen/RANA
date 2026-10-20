import pytest

from ncaa_site_rec.io.structure import pdb_to_atom_table
from ncaa_site_rec.features.pazf import score_pazf_site


@pytest.fixture(scope="module")
def site_result():
    atom_df = pdb_to_atom_table("data/raw/1L63.pdb")

    return score_pazf_site(
        atom_df,
        chain="A",
        residue_number=20,
    )


def test_rotamer_count(site_result):
    assert len(site_result["rotamers"]) == 12


def test_best_rotamer(site_result):
    best = site_result["best_rotamer"]

    assert best["chi1"] == 180.0
    assert best["chi2"] == 90.0


def test_minimum_steric_score(site_result):
    assert site_result["min_steric_score"] == pytest.approx(
        2.655,
        abs=0.01,
    )


def test_scores_are_nonnegative(site_result):
    for rotamer in site_result["rotamers"]:
        assert rotamer["steric_score"] >= 0


def test_best_score_matches_minimum(site_result):
    scores = [
        rotamer["steric_score"]
        for rotamer in site_result["rotamers"]
    ]

    assert site_result["min_steric_score"] == min(scores)