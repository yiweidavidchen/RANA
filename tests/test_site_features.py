
import numpy as np
import pytest
import pandas as pd

from ncaa_site_rec.features.site_features import (
    build_pazf_feature_table,
    build_ranked_pazf_table,
)


PDB_PATH = "data/raw/1L63.pdb"


@pytest.fixture(scope="module")
def t4l_features():
    # Reuse one full-protein scan across tests.
    return build_pazf_feature_table(PDB_PATH, chain="A")


def test_feature_table_has_expected_rows(t4l_features):
    assert len(t4l_features) == 162
    assert t4l_features["status"].eq("scored").all()


def test_residue_keys_are_unique(t4l_features):
    keys = [
        "chain",
        "residue_number",
        "insertion_code",
        "residue_name",
    ]

    assert not t4l_features.duplicated(subset=keys).any()


def test_structural_features_are_present(t4l_features):
    expected = [
        "sasa_abs",
        "rsa",
        "ca_neighbors_8a",
        "min_steric_score",
        "mean_steric_score",
        "low_clash_fraction",
    ]

    assert t4l_features[expected].notna().all().all()


def test_site20_steric_regression(t4l_features):
    site20 = t4l_features.loc[
        t4l_features["residue_number"] == 20
    ].iloc[0]

    assert site20["residue_name"] == "ASP"
    assert np.isclose(
        site20["min_steric_score"],
        2.655490,
        atol=1e-5,
    )


def test_missing_chain_is_rejected():
    with pytest.raises(ValueError, match="No standard residues"):
        build_pazf_feature_table(PDB_PATH, chain="Z")


def test_functional_distance_integration():
    df = build_pazf_feature_table(
        PDB_PATH,
        chain="A",
        functional_residues=[("A", 20, "")],
    )

    assert "distance_to_functional_site_ca" in df.columns

    site20 = df.loc[
        df["residue_number"] == 20
    ].iloc[0]

    assert np.isclose(
        site20["distance_to_functional_site_ca"],
        0.0,
        atol=1e-8,
    )

    distances = df["distance_to_functional_site_ca"]

    assert distances.notna().all()
    assert (distances >= 0).all()


def test_missing_functional_residue_is_rejected():
    with pytest.raises(ValueError, match="Missing functional residue"):
        build_pazf_feature_table(
            PDB_PATH,
            chain="A",
            functional_residues=[("A", 9999, "")],
        )


def test_incomplete_backbone_is_preserved(tmp_path):
    original = tmp_path / "original.pdb"
    modified = tmp_path / "missing_ca.pdb"

    from pathlib import Path

    original.write_bytes(Path(PDB_PATH).read_bytes())

    lines = original.read_text().splitlines(keepends=True)

    filtered_lines = []

    for line in lines:
        is_target_ca = (
            line.startswith(("ATOM  ", "HETATM"))
            and line[12:16].strip() == "CA"
            and line[21:22] == "A"
            and line[22:26].strip() == "20"
            and line[26:27].strip() == ""
        )

        if not is_target_ca:
            filtered_lines.append(line)

    modified.write_text("".join(filtered_lines))

    df = build_pazf_feature_table(
        modified,
        chain="A",
    )

    assert len(df) == 162

    site20 = df.loc[
        df["residue_number"] == 20
    ].iloc[0]

    assert not bool(site20["has_ca"])
    assert np.isnan(site20["ca_neighbors_8a"])
    assert site20["status"] == "skipped"
    assert site20["reason"] == "incomplete_backbone"
    assert np.isnan(site20["min_steric_score"])


def test_packing_includes_other_chains(tmp_path):
    from pathlib import Path

    original_lines = Path(PDB_PATH).read_text().splitlines()

    # Find the CA atom of residue A:20.
    ca_line = next(
        line for line in original_lines
        if line.startswith("ATOM  ")
        and line[12:16].strip() == "CA"
        and line[21] == "A"
        and line[22:26].strip() == "20"
        and line[26].strip() == ""
    )

    # Copy the atom to a new chain B, residue 1.
    new_line = (
        ca_line[:6]
        + f"{99999:5d}"
        + ca_line[11:21]
        + "B"
        + f"{1:4d}"
        + ca_line[26:]
    )

    # Insert chain B immediately after the last ATOM record.
    last_atom_index = max(
        i for i, line in enumerate(original_lines)
        if line.startswith("ATOM  ")
    )

    pdb_lines = original_lines.copy()

    pdb_lines.insert(
        last_atom_index + 1,
        new_line,
    )

    modified_pdb = tmp_path / "two_chains.pdb"
    modified_pdb.write_text("\n".join(pdb_lines) + "\n")

    from ncaa_site_rec.io.structure import pdb_to_residue_table

    residue_table = pdb_to_residue_table(modified_pdb)
    assert set(residue_table["chain"]) == {"A", "B"}

    df = build_pazf_feature_table(
        modified_pdb,
        chain="A",
    )

    site20 = df.loc[
        df["residue_number"] == 20
    ].iloc[0]

    # Original T4L A:20 has 9 CA neighbors within 8 Å.
    # The additional chain B CA must be counted.
    assert site20["ca_neighbors_8a"] == 10

def test_ranked_pipeline_matches_manual_ranking():
    from ncaa_site_rec.features.site_ranking import rank_pazf_sites

    pdb_path = "data/raw/1L63.pdb"

    features = build_pazf_feature_table(
        pdb_path,
        chain="A",
        seed=42,
        low_clash_threshold=5.0,
    )

    expected = rank_pazf_sites(
        features,
        low_clash_threshold=5.0,
        favorable_fraction=0.75,
    )

    actual = build_ranked_pazf_table(
        pdb_path,
        chain="A",
        seed=42,
        low_clash_threshold=5.0,
        favorable_fraction=0.75,
    )

    pd.testing.assert_frame_equal(actual, expected)

    assert len(actual) == 162
    assert actual["candidate_tier"].notna().all()