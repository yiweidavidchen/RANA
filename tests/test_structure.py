
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
