
import subprocess
import sys

import pandas as pd


def test_inspect_command(tmp_path):
    """Test the complete RANA inspect CLI workflow."""

    pdb_content = (
        "ATOM      1  CA  ALA A   1      10.000  11.000  12.000  1.00 20.00           C\n"
        "ATOM      2  CA  GLY A   2      13.000  14.000  15.000  1.00 20.00           C\n"
        "TER\n"
        "END\n"
    )

    pdb_path = tmp_path / "input.pdb"
    output_path = tmp_path / "results" / "residues.csv"

    pdb_path.write_text(pdb_content)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ncaa_site_rec.cli",
            "inspect",
            "--pdb",
            str(pdb_path),
            "--output",
            str(output_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert output_path.is_file()

    df = pd.read_csv(output_path)

    assert len(df) == 2
    assert df["residue_name"].tolist() == ["ALA", "GLY"]
    assert df["residue_number"].tolist() == [1, 2]
    assert df["ca_x"].tolist() == [10.0, 13.0]
