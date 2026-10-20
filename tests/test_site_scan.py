import pytest
import numpy as np

from ncaa_site_rec.io.structure import pdb_to_atom_table
from ncaa_site_rec.features.site_scan import scan_pazf_sites


@pytest.fixture(scope="module")
def pilot_results():
    atom_df = pdb_to_atom_table("data/raw/1L63.pdb")

    return scan_pazf_sites(
        atom_df,
        chain="A",
        seed=42,
        candidate_residues=[18, 19, 20, 21, 22],
    )


def test_pilot_site_count(pilot_results):
    assert len(pilot_results) == 5
    assert pilot_results["residue_number"].tolist() == [
        18, 19, 20, 21, 22
    ]


def test_all_pilot_sites_scored(pilot_results):
    assert (pilot_results["status"] == "scored").all()
    assert (pilot_results["n_rotamers"] == 12).all()


def test_full_environment_site20(pilot_results):
    site20 = pilot_results.loc[
        pilot_results["residue_number"] == 20
    ].iloc[0]

    assert site20["min_steric_score"] == pytest.approx(
        2.65549,
        abs=0.01,
    )
    assert site20["best_chi1"] == 180.0
    assert site20["best_chi2"] == 90.0


def test_rotamer_score_distribution(pilot_results):
    for _, site in pilot_results.iterrows():
        assert len(site["rotamer_scores"]) == 12
        assert site["low_clash_fraction"] >= 0.0
        assert site["low_clash_fraction"] <= 1.0


def test_negative_threshold_rejected():
    atom_df = pdb_to_atom_table("data/raw/1L63.pdb")

    with pytest.raises(ValueError):
        scan_pazf_sites(
            atom_df,
            chain="A",
            low_clash_threshold=-1.0,
            candidate_residues=[20],
        )

def test_empty_candidate_list_preserves_schema():
    atom_df = pdb_to_atom_table("data/raw/1L63.pdb")

    result = scan_pazf_sites(
        atom_df,
        chain="A",
        candidate_residues=[],
    )

    assert result.empty
    assert "status" in result.columns
    assert "residue_number" in result.columns
    assert "min_steric_score" in result.columns


def test_incomplete_backbone_is_skipped():
    atom_df = pdb_to_atom_table("data/raw/1L63.pdb")

    # Remove the CA atom from residue A:20.
    atom_df = atom_df.loc[
        ~(
            (atom_df["chain"] == "A")
            & (atom_df["residue_number"] == 20)
            & (atom_df["atom_name"] == "CA")
        )
    ].copy()

    result = scan_pazf_sites(
        atom_df,
        chain="A",
        candidate_residues=[20],
    )

    assert len(result) == 1

    site20 = result.iloc[0]

    assert site20["status"] == "skipped"
    assert site20["reason"] == "incomplete_backbone"
    assert site20["n_rotamers"] == 0
    assert np.isnan(site20["min_steric_score"])