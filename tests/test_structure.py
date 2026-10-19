
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

def test_functional_site_distances_mini_pdb():
    """Check minimum C-alpha distances to functional residues."""
    from pathlib import Path

    import pytest

    from ncaa_site_rec.io.structure import pdb_to_residue_table
    from ncaa_site_rec.features.structural import (
        compute_functional_site_distances,
    )

    pdb_path = (
        Path(__file__).parent
        / "fixtures"
        / "mini_protein.pdb"
    )

    residues = pdb_to_residue_table(pdb_path)

    # Test one functional residue.
    single = compute_functional_site_distances(
        residues,
        functional_residues=[("A", 2, "")],
    )

    assert single["distance_to_functional_site_ca"].tolist() == pytest.approx(
        [3.0, 0.0, 5.0, 17.0]
    )

    # Test multiple functional residues.
    multiple = compute_functional_site_distances(
        residues,
        functional_residues=[
            ("A", 2, ""),
            ("A", 4, ""),
        ],
    )

    assert multiple["distance_to_functional_site_ca"].tolist() == pytest.approx(
        [3.0, 0.0, 5.0, 0.0]
    )

def test_functional_site_distances_invalid_input():
    """Reject empty or nonexistent functional residue selections."""
    from pathlib import Path

    import pytest

    from ncaa_site_rec.io.structure import pdb_to_residue_table
    from ncaa_site_rec.features.structural import (
        compute_functional_site_distances,
    )

    pdb_path = (
        Path(__file__).parent
        / "fixtures"
        / "mini_protein.pdb"
    )

    residues = pdb_to_residue_table(pdb_path)

    # No functional residues provided.
    with pytest.raises(ValueError, match="At least one"):
        compute_functional_site_distances(
            residues,
            functional_residues=[],
        )

    # Residue 999 does not exist in the structure.
    with pytest.raises(ValueError, match="Missing functional residue"):
        compute_functional_site_distances(
            residues,
            functional_residues=[("A", 999, "")],
        )

def test_functional_site_distances_chain_aware():
    """Distinguish identical residue numbers across chains."""
    import pandas as pd
    import pytest

    from ncaa_site_rec.features.structural import (
        compute_functional_site_distances,
    )

    residues = pd.DataFrame({
        "chain": ["A", "A", "B", "B"],
        "residue_number": [1, 2, 1, 2],
        "insertion_code": ["", "", "", ""],
        "has_ca": [True, True, True, True],
        "ca_x": [0.0, 3.0, 20.0, 23.0],
        "ca_y": [0.0, 0.0, 0.0, 0.0],
        "ca_z": [0.0, 0.0, 0.0, 0.0],
    })

    result = compute_functional_site_distances(
        residues,
        functional_residues=[("A", 2, "")],
    )

    assert result["distance_to_functional_site_ca"].tolist() == pytest.approx(
        [3.0, 0.0, 17.0, 20.0]
    )

def test_functional_site_distances_insertion_code():
    """Distinguish residues with different insertion codes."""
    import pandas as pd
    import pytest

    from ncaa_site_rec.features.structural import (
        compute_functional_site_distances,
    )

    residues = pd.DataFrame({
        "chain": ["A", "A", "A"],
        "residue_number": [10, 10, 10],
        "insertion_code": ["", "A", "B"],
        "has_ca": [True, True, True],
        "ca_x": [0.0, 4.0, 12.0],
        "ca_y": [0.0, 0.0, 0.0],
        "ca_z": [0.0, 0.0, 0.0],
    })

    result = compute_functional_site_distances(
        residues,
        functional_residues=[("A", 10, "A")],
    )

    assert result["distance_to_functional_site_ca"].tolist() == pytest.approx(
        [4.0, 0.0, 8.0]
    )

def test_functional_site_distances_missing_ca():
    """Keep missing C-alpha distances as NaN."""
    import pandas as pd
    import pytest

    from ncaa_site_rec.features.structural import (
        compute_functional_site_distances,
    )

    residues = pd.DataFrame({
        "chain": ["A", "A", "A"],
        "residue_number": [1, 2, 3],
        "insertion_code": ["", "", ""],
        "has_ca": [True, True, False],
        "ca_x": [0.0, 4.0, float("nan")],
        "ca_y": [0.0, 0.0, float("nan")],
        "ca_z": [0.0, 0.0, float("nan")],
    })

    result = compute_functional_site_distances(
        residues,
        functional_residues=[("A", 2, "")],
    )

    distances = result["distance_to_functional_site_ca"]

    assert distances.iloc[0] == pytest.approx(4.0)
    assert distances.iloc[1] == pytest.approx(0.0)
    assert pd.isna(distances.iloc[2])

def test_functional_site_missing_ca():
    """Reject functional residues without C-alpha coordinates."""
    import pandas as pd
    import pytest

    from ncaa_site_rec.features.structural import (
        compute_functional_site_distances,
    )

    residues = pd.DataFrame({
        "chain": ["A", "A", "A"],
        "residue_number": [1, 2, 3],
        "insertion_code": ["", "", ""],
        "has_ca": [True, False, True],
        "ca_x": [0.0, float("nan"), 10.0],
        "ca_y": [0.0, float("nan"), 0.0],
        "ca_z": [0.0, float("nan"), 0.0],
    })

    with pytest.raises(
        ValueError,
        match="No functional residues with C-alpha coordinates found",
    ):
        compute_functional_site_distances(
            residues,
            functional_residues=[("A", 2, "")],
        )

def test_functional_site_distances_partial_invalid():
    """Reject selections containing an invalid functional residue."""
    from pathlib import Path

    import pytest

    from ncaa_site_rec.io.structure import pdb_to_residue_table
    from ncaa_site_rec.features.structural import (
        compute_functional_site_distances,
    )

    pdb_path = (
        Path(__file__).parent
        / "fixtures"
        / "mini_protein.pdb"
    )

    residues = pdb_to_residue_table(pdb_path)

    with pytest.raises(ValueError, match="functional residue"):
        compute_functional_site_distances(
            residues,
            functional_residues=[
                ("A", 2, ""),
                ("A", 999, ""),
            ],
        )