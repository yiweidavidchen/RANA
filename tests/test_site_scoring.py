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

def test_explicit_hydrogens_do_not_change_steric_scores():
    """Heavy-atom scoring must be invariant to explicit H/D records."""
    atom_df = pdb_to_atom_table("data/raw/1L63.pdb")

    # Use the same heavy-atom coordinates in both inputs.
    # Synthetic H/D records test the atom-selection policy
    # without requiring another PDB fixture.
    extra_atoms = atom_df.iloc[:2].copy()
    extra_atoms.loc[extra_atoms.index[0], "element"] = "H"
    extra_atoms.loc[extra_atoms.index[1], "element"] = "D"

    import pandas as pd

    atom_df_with_hydrogens = pd.concat(
        [atom_df, extra_atoms],
        ignore_index=True,
    )

    baseline = score_pazf_site(
        atom_df,
        chain="A",
        residue_number=20,
        seed=42,
    )

    with_hydrogens = score_pazf_site(
        atom_df_with_hydrogens,
        chain="A",
        residue_number=20,
        seed=42,
    )

    assert len(baseline["rotamers"]) == 12
    assert len(with_hydrogens["rotamers"]) == 12

    for original, modified in zip(
        baseline["rotamers"],
        with_hydrogens["rotamers"],
    ):
        assert original["chi1"] == modified["chi1"]
        assert original["chi2"] == modified["chi2"]

        assert modified["steric_score"] == pytest.approx(
            original["steric_score"],
            abs=1e-10,
        )

    assert with_hydrogens["min_steric_score"] == pytest.approx(
        baseline["min_steric_score"],
        abs=1e-10,
    )