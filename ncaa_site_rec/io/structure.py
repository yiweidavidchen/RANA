
from pathlib import Path

import pandas as pd
from Bio.PDB import PDBParser
from Bio.PDB.Polypeptide import is_aa


def pdb_to_residue_table(pdb_path: str | Path) -> pd.DataFrame:
    """Convert a PDB structure into a residue-level table."""

    pdb_path = Path(pdb_path)

    if not pdb_path.is_file():
        raise FileNotFoundError(f"PDB file not found: {pdb_path}")

    parser = PDBParser(QUIET=True)
    structure = parser.get_structure(pdb_path.stem, str(pdb_path))

    rows = []

    # M1 uses the first structural model.
    model = next(structure.get_models())

    for chain in model:
        for residue in chain:

            if not is_aa(residue, standard=True):
                continue

            hetflag, residue_number, insertion_code = residue.id

            # Some residues may have missing coordinates.
            has_ca = "CA" in residue

            row = {
                "chain": chain.id,
                "residue_number": residue_number,
                "insertion_code": insertion_code.strip(),
                "residue_name": residue.resname,
                "has_ca": has_ca,
                "ca_x": None,
                "ca_y": None,
                "ca_z": None,
            }

            if has_ca:
                ca = residue["CA"]
                row["ca_x"] = float(ca.coord[0])
                row["ca_y"] = float(ca.coord[1])
                row["ca_z"] = float(ca.coord[2])

            rows.append(row)

    if not rows:
        raise ValueError("No standard amino-acid residues found in PDB.")

    return pd.DataFrame(rows)

def pdb_to_atom_table(pdb_path: str | Path) -> pd.DataFrame:
    """Convert standard amino-acid atoms into an atom-level table."""

    pdb_path = Path(pdb_path)

    if not pdb_path.is_file():
        raise FileNotFoundError(f"PDB file not found: {pdb_path}")

    parser = PDBParser(QUIET=True)
    structure = parser.get_structure(pdb_path.stem, str(pdb_path))

    model = next(structure.get_models())
    rows = []

    for chain in model:
        for residue in chain:
            if not is_aa(residue, standard=True):
                continue

            _, residue_number, insertion_code = residue.id

            for atom in residue.get_atoms():
                rows.append({
                    "chain": chain.id,
                    "residue_number": residue_number,
                    "insertion_code": insertion_code.strip(),
                    "residue_name": residue.resname,
                    "atom_name": atom.get_name(),
                    "element": atom.element,
                    "x": float(atom.coord[0]),
                    "y": float(atom.coord[1]),
                    "z": float(atom.coord[2]),
                })

    if not rows:
        raise ValueError("No standard amino-acid atoms found in PDB.")

    return pd.DataFrame(rows)