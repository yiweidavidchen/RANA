
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


def compute_functional_site_distances(
    residue_df: pd.DataFrame,
    functional_residues: list[tuple[str, int, str]],
) -> pd.DataFrame:
    """Compute minimum C-alpha distance to specified functional residues."""
    import numpy as np

    if not functional_residues:
        raise ValueError("At least one functional residue is required.")

    df = residue_df.copy()

    functional_ids = set(functional_residues)

    residue_ids = list(
        zip(
            df["chain"],
            df["residue_number"],
            df["insertion_code"],
        )
    )

    # Validate every requested functional residue.
    available_ids = set(residue_ids)

    missing_ids = functional_ids - available_ids

    if missing_ids:
        raise ValueError(
            f"Missing functional residue(s): {sorted(missing_ids)}"
        )

    residues_with_ca = set(
        residue_id
        for residue_id, has_ca in zip(residue_ids, df["has_ca"])
        if has_ca
    )

    missing_ca_ids = functional_ids - residues_with_ca

    if missing_ca_ids:
        raise ValueError(
            "No functional residues with C-alpha coordinates found "
            f"for: {sorted(missing_ca_ids)}"
        )

    functional_mask = pd.Series(
        [residue_id in functional_ids for residue_id in residue_ids],
        index=df.index,
    ) & df["has_ca"]

    if not functional_mask.any():
        raise ValueError("No functional residues with C-alpha coordinates found.")

    coords = df[["ca_x", "ca_y", "ca_z"]].to_numpy(dtype=float)
    functional_coords = coords[functional_mask.to_numpy()]

    min_distances = np.full(len(df), np.nan)

    for i in range(len(df)):
        if not df.iloc[i]["has_ca"]:
            continue

        distances = np.linalg.norm(
            functional_coords - coords[i],
            axis=1,
        )

        min_distances[i] = distances.min()

    df["distance_to_functional_site_ca"] = min_distances

    return df

def compute_pazf_steric_proxy(*args, **kwargs):
    """Estimate pAzF steric compatibility using a Phe-derived rotamer proxy."""
    raise NotImplementedError
