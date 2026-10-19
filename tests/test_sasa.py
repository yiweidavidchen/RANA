
import pytest

from ncaa_site_rec.features.structural import compute_sasa


def test_compute_sasa_single_residue(tmp_path):
    """Check SASA calculation for an isolated amino-acid residue."""

    pdb_content = (
        "ATOM      1  CA  ALA A   1      10.000  11.000  12.000  1.00 20.00           C\n"
        "TER\n"
        "END\n"
    )

    pdb_path = tmp_path / "single_residue.pdb"
    pdb_path.write_text(pdb_content)

    df = compute_sasa(pdb_path, n_points=100)

    assert len(df) == 1
    assert df.loc[0, "chain"] == "A"
    assert df.loc[0, "residue_number"] == 1
    assert df.loc[0, "residue_name"] == "ALA"
    assert df.loc[0, "sasa_abs"] > 0


def test_compute_sasa_missing_file(tmp_path):
    """Check that a missing PDB produces a clear error."""

    missing_path = tmp_path / "missing.pdb"

    with pytest.raises(FileNotFoundError):
        compute_sasa(missing_path)
