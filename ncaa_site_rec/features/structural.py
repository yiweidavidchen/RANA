
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


def compute_functional_site_distances(*args, **kwargs):
    """Compute minimum distances to user-defined catalytic/binding residues."""
    raise NotImplementedError


def compute_local_packing(*args, **kwargs):
    """Compute a simple local packing / crowding descriptor."""
    raise NotImplementedError


def compute_pazf_steric_proxy(*args, **kwargs):
    """Estimate pAzF steric compatibility using a Phe-derived rotamer proxy."""
    raise NotImplementedError
