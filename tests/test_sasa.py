
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


def test_compute_relative_sasa():
    """Check residue-specific SASA normalization."""

    import pandas as pd
    from ncaa_site_rec.features.structural import compute_relative_sasa

    sasa_df = pd.DataFrame({
        "residue_name": ["ALA", "GLY", "ALA"],
        "sasa_abs": [50.0, 20.0, 0.0],
    })

    max_asa = {
        "ALA": 100.0,
        "GLY": 80.0,
    }

    result = compute_relative_sasa(sasa_df, max_asa)

    assert result["rsa"].tolist() == pytest.approx([
        0.50,
        0.25,
        0.00,
    ])

    assert result["sasa_max"].tolist() == [
        100.0,
        80.0,
        100.0,
    ]

    # The original input must remain unchanged.
    assert "rsa" not in sasa_df.columns


def test_compute_relative_sasa_missing_reference():
    """Reject residues without a maximum ASA reference."""

    import pandas as pd
    from ncaa_site_rec.features.structural import compute_relative_sasa

    sasa_df = pd.DataFrame({
        "residue_name": ["ALA", "TRP"],
        "sasa_abs": [50.0, 80.0],
    })

    max_asa = {
        "ALA": 100.0,
    }

    with pytest.raises(ValueError, match="Missing maximum ASA reference"):
        compute_relative_sasa(sasa_df, max_asa)
