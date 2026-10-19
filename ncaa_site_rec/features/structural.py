
from pathlib import Path

import pandas as pd
from Bio.PDB import PDBParser, ShrakeRupley
from Bio.PDB.Polypeptide import is_aa


def compute_sasa(
    pdb_path: str | Path,
    n_points: int = 500,
) -> pd.DataFrame:
    """Compute residue-level absolute SASA in square angstroms."""

    pdb_path = Path(pdb_path)

    if not pdb_path.is_file():
        raise FileNotFoundError(f"PDB file not found: {pdb_path}")

    parser = PDBParser(QUIET=True)
    structure = parser.get_structure(pdb_path.stem, str(pdb_path))

    # Use the first model and protein atoms only.
    model = next(structure.get_models())

    for chain in list(model):
        for residue in list(chain):
            if not is_aa(residue, standard=True):
                chain.detach_child(residue.id)

    sr = ShrakeRupley(n_points=n_points)
    sr.compute(model, level="R")

    rows = []

    for chain in model:
        for residue in chain:
            _, residue_number, insertion_code = residue.id

            rows.append({
                "chain": chain.id,
                "residue_number": residue_number,
                "insertion_code": insertion_code.strip(),
                "residue_name": residue.resname,
                "sasa_abs": float(residue.sasa),
            })

    return pd.DataFrame(rows)


def compute_relative_sasa(
    sasa_df: pd.DataFrame,
    max_asa: dict[str, float],
) -> pd.DataFrame:
    """Normalize absolute SASA by residue-specific maximum ASA."""

    df = sasa_df.copy()

    df["sasa_max"] = df["residue_name"].map(max_asa)

    if df["sasa_max"].isna().any():
        missing = sorted(
            df.loc[df["sasa_max"].isna(), "residue_name"].unique()
        )
        raise ValueError(
            f"Missing maximum ASA reference for: {missing}"
        )

    if (df["sasa_max"] <= 0).any():
        raise ValueError("Maximum ASA values must be positive.")

    df["rsa"] = df["sasa_abs"] / df["sasa_max"]

    return df



def compute_local_packing(
    residue_df: pd.DataFrame,
) -> pd.DataFrame:
    """Count neighboring C-alpha atoms within a specified radius."""

    import numpy as np

    radius = 8.0

    if radius <= 0:
        raise ValueError("Radius must be positive.")

    df = residue_df.copy()

    coords = df[["ca_x", "ca_y", "ca_z"]].to_numpy(dtype=float)
    valid = df["has_ca"].to_numpy(dtype=bool)

    neighbor_counts = np.full(len(df), np.nan)

    for i in range(len(df)):
        if not valid[i]:
            continue

        distances = np.linalg.norm(coords[valid] - coords[i], axis=1)

        # Exclude the residue itself.
        neighbor_counts[i] = int(np.sum(distances < radius)) - 1

    df["ca_neighbors_8a"] = neighbor_counts

    return df






def compute_pazf_steric_proxy(*args, **kwargs):
    """Estimate pAzF steric compatibility using a Phe-derived rotamer proxy."""
    raise NotImplementedError
