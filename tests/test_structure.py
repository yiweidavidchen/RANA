
from ncaa_site_rec.io.structure import pdb_to_residue_table


def test_pdb_to_residue_table(tmp_path):
    """Check that RANA extracts residue IDs and CA coordinates."""

    pdb_content = (
        "ATOM      1  CA  ALA A   1      10.000  11.000  12.000  1.00 20.00           C\n"
        "ATOM      2  CA  GLY A   2      13.000  14.000  15.000  1.00 20.00           C\n"
        "TER\n"
        "END\n"
    )

    pdb_path = tmp_path / "test.pdb"
    pdb_path.write_text(pdb_content)

    df = pdb_to_residue_table(pdb_path)

    assert len(df) == 2
    assert df["chain"].tolist() == ["A", "A"]
    assert df["residue_number"].tolist() == [1, 2]
    assert df["residue_name"].tolist() == ["ALA", "GLY"]
    assert df["has_ca"].tolist() == [True, True]

    assert df.loc[0, "ca_x"] == 10.0
    assert df.loc[1, "ca_z"] == 15.0

def test_compute_local_packing():
    """Check 8 Å C-alpha neighbor counts."""

    import pandas as pd
    from ncaa_site_rec.features.structural import compute_local_packing

    residues = pd.DataFrame({
        "residue_number": [1, 2, 3, 4],
        "has_ca": [True, True, True, False],
        "ca_x": [0.0, 3.0, 20.0, float("nan")],
        "ca_y": [0.0, 0.0, 0.0, float("nan")],
        "ca_z": [0.0, 0.0, 0.0, float("nan")],
    })

    result = compute_local_packing(residues)

    assert result.loc[0, "ca_neighbors_8a"] == 1
    assert result.loc[1, "ca_neighbors_8a"] == 1
    assert result.loc[2, "ca_neighbors_8a"] == 0
    assert pd.isna(result.loc[3, "ca_neighbors_8a"])

def test_local_packing_mini_pdb():
    """Check neighbor counts using a known PDB geometry."""
    from pathlib import Path

    from ncaa_site_rec.io.structure import pdb_to_residue_table
    from ncaa_site_rec.features.structural import compute_local_packing

    pdb_path = (
        Path(__file__).parent
        / "fixtures"
        / "mini_protein.pdb"
    )

    residues = pdb_to_residue_table(pdb_path)
    result = compute_local_packing(residues)

    assert len(result) == 4

    assert result["ca_neighbors_8a"].tolist() == [
        1.0,
        2.0,
        1.0,
        0.0,
    ]