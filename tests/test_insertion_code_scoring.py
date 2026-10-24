"""Regression coverage for residue identity in pAzF steric exclusions."""

import numpy as np
import pandas as pd
import pytest

from ncaa_site_rec.features.pazf import (
    exclude_bonded_neighbor_overlaps,
    score_pazf_site,
)
from ncaa_site_rec.features.site_scan import scan_pazf_sites


def backbone(chain, number, code, offset=(0.0, 0.0, 0.0)):
    """Minimal noncollinear backbone, independent of downloaded PDB fixtures."""
    coordinates = {
        "N": (0.0, 1.46, 0.0), "CA": (0.0, 0.0, 0.0),
        "C": (1.52, 0.0, 0.0), "O": (2.1, -1.0, 0.0),
    }
    return pd.DataFrame([
        {"chain": chain, "residue_number": number, "insertion_code": code,
         "residue_name": "ALA", "atom_name": name, "element": name[0],
         **dict(zip(("x", "y", "z"), np.array(position) + offset))}
        for name, position in coordinates.items()
    ])


@pytest.mark.parametrize("code", ["A", "B"])
def test_exclusion_keeps_same_number_other_code_and_chain_contacts(code):
    """Only the target's CB/N,C contacts are bonded, not nearby identities."""
    environment = pd.DataFrame({
        "chain": ["A"] * 6 + ["B"] * 2 + ["A"] * 2,
        "residue_number": [20] * 8 + [21] * 2,
        "insertion_code": [code] * 4 + [""] * 2 + [code] * 4,
        "atom_name": [
            "N", "C", "CA", "O", "N", "C", "N", "C", "N", "C",
        ],
    })
    overlaps = np.arange(1.0, 21.0).reshape(2, 10)
    expected = overlaps.copy()
    expected[0, :2] = 0.0
    actual = exclude_bonded_neighbor_overlaps(
        overlaps, [2, 3], environment, "A", 20, insertion_code=code,
    )
    np.testing.assert_array_equal(actual, expected)
    np.testing.assert_array_equal(overlaps, np.arange(1.0, 21.0).reshape(2, 10))


@pytest.mark.parametrize(
    "identity", [("A", 20, "A"), ("A", 20, "B"), ("Z", 47, "B")],
)
def test_label_only_change_preserves_all_rotamer_scores(identity):
    """Without an identity collision, labels must not change fixed geometry."""
    atoms = pd.concat([
        backbone("A", 20, ""), backbone("B", 21, "", (3.0, 2.0, 1.0)),
    ], ignore_index=True)
    original_atoms = atoms.copy(deep=True)
    original = score_pazf_site(atoms, chain="A", residue_number=20, seed=42)
    relabeled = atoms.copy()
    target = (relabeled.chain == "A") & (relabeled.residue_number == 20)
    for column, value in zip(
        ("chain", "residue_number", "insertion_code"), identity,
    ):
        relabeled.loc[target, column] = value
    actual = score_pazf_site(
        relabeled, chain=identity[0], residue_number=identity[1],
        insertion_code=identity[2], seed=42,
    )
    assert (
        actual["chain"], actual["residue_number"], actual["insertion_code"],
    ) == identity
    assert len(actual["rotamers"]) == len(original["rotamers"]) == 12
    np.testing.assert_allclose(
        [r["steric_score"] for r in actual["rotamers"]],
        [r["steric_score"] for r in original["rotamers"]], rtol=0, atol=1e-12,
    )
    assert actual["min_steric_score"] == pytest.approx(
        original["min_steric_score"], abs=1e-12,
    )
    assert actual["best_rotamer"] == original["best_rotamer"]
    pd.testing.assert_frame_equal(atoms, original_atoms)


def test_scan_preserves_colliding_residue_identities_and_scores():
    """Exercise scan -> score -> exclusion with blank/A/B and another chain."""
    atoms = pd.concat([
        backbone("A", 20, ""), backbone("A", 20, "A", (4.0, 2.0, 1.0)),
        backbone("A", 20, "B", (1.0, 5.0, 2.0)),
        backbone("B", 20, "A", (-2.0, 1.0, 3.0)),
    ], ignore_index=True)
    actual = scan_pazf_sites(
        atoms, chain="A", candidate_residues=[20], seed=42,
    )
    assert actual[["chain", "residue_number", "insertion_code"]].values.tolist() == [
        ["A", 20, ""], ["A", 20, "A"], ["A", 20, "B"],
    ]
    assert actual["status"].tolist() == ["scored"] * 3
    assert actual["reason"].tolist() == [""] * 3
    for row in actual.itertuples(index=False):
        # A unique blank-code identity provides a reference through the working
        # default-code path, retaining every other residue as steric environment.
        reference_atoms = atoms.copy()
        target = (
            (reference_atoms.chain == "A")
            & (reference_atoms.residue_number == 20)
            & (reference_atoms.insertion_code == row.insertion_code)
        )
        reference_atoms.loc[target, "chain"] = "Z"
        reference_atoms.loc[target, "residue_number"] = 999
        reference_atoms.loc[target, "insertion_code"] = ""
        reference = score_pazf_site(
            reference_atoms, chain="Z", residue_number=999, seed=42,
        )
        scores = np.array([r["steric_score"] for r in reference["rotamers"]])
        np.testing.assert_allclose(row.rotamer_scores, scores, rtol=0, atol=1e-12)
        assert row.n_rotamers == 12
        assert row.min_steric_score == pytest.approx(scores.min(), abs=1e-12)
        assert row.low_clash_fraction == np.mean(scores <= 10.0)
