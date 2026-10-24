"""pAzF side-chain template and rotamer geometry utilities."""

import numpy as np

from rdkit import Chem
from rdkit.Chem import AllChem
from ncaa_site_rec.features.geometry import (
    build_backbone_frame,
    local_to_global,
    align_sidechain_to_cb,
    build_cb_from_angles,
)
from rdkit.Chem import rdMolTransforms


PAZF_SMILES = "N[C@@H](Cc1ccc(N=[N+]=[N-])cc1)C(=O)O"


def build_pazf_molecule() -> Chem.Mol:
    """Build a pAzF molecule from its SMILES representation."""

    mol = Chem.MolFromSmiles(PAZF_SMILES)

    if mol is None:
        raise ValueError("Failed to parse pAzF SMILES.")

    return mol

def generate_pazf_conformer(seed: int = 42) -> Chem.Mol:
    """Generate an initial 3D conformer of L-pAzF."""

    mol = Chem.AddHs(build_pazf_molecule())

    params = AllChem.ETKDGv3()
    params.randomSeed = seed

    result = AllChem.EmbedMolecule(mol, params)

    if result != 0:
        raise RuntimeError("Failed to generate pAzF conformer.")

    return mol

def get_pazf_local_coordinates(mol: Chem.Mol) -> np.ndarray:
    """Express pAzF atom coordinates in its backbone-local frame."""

    coords = np.asarray(mol.GetConformer().GetPositions(), dtype=float)

    n = coords[0]
    ca = coords[1]
    c = coords[12]

    frame = build_backbone_frame(n, ca, c)

    return (coords - ca) @ frame

def place_pazf_on_backbone(
    mol: Chem.Mol,
    n: np.ndarray,
    ca: np.ndarray,
    c: np.ndarray,
) -> np.ndarray:
    """Place a pAzF conformer onto a target backbone."""

    local_coords = get_pazf_local_coordinates(mol)

    target_frame = build_backbone_frame(n, ca, c)

    return local_to_global(local_coords, ca, target_frame)

def set_pazf_rotamer(
    mol: Chem.Mol,
    chi1: float,
    chi2: float,
) -> Chem.Mol:
    """Return a pAzF conformer with specified side-chain dihedrals."""

    mol = Chem.Mol(mol)
    conf = mol.GetConformer()

    # Chi1: N-CA-CB-CG
    rdMolTransforms.SetDihedralDeg(
        conf, 0, 1, 2, 3, float(chi1)
    )

    # Chi2: CA-CB-CG-CD1
    rdMolTransforms.SetDihedralDeg(
        conf, 1, 2, 3, 4, float(chi2)
    )

    return mol

def generate_rotamer_grid() -> list[tuple[float, float]]:
    """Generate an initial grid of pAzF chi1/chi2 angles."""

    chi1_values = [-60.0, 60.0, 180.0]
    chi2_values = [-90.0, 0.0, 90.0, 180.0]

    return [
        (chi1, chi2)
        for chi1 in chi1_values
        for chi2 in chi2_values
    ]

def generate_pazf_rotamers(
    mol: Chem.Mol,
) -> list[tuple[float, float, Chem.Mol]]:
    """Generate pAzF conformers for each rotamer grid point."""

    rotamers = []

    for chi1, chi2 in generate_rotamer_grid():
        rotamer = set_pazf_rotamer(
            mol,
            chi1=chi1,
            chi2=chi2,
        )

        rotamers.append((chi1, chi2, rotamer))

    return rotamers

def get_environment_atoms(
    atom_df,
    chain: str,
    residue_number: int,
    insertion_code: str = "",
):
    """Keep protein environment while removing the target sidechain."""

    is_target = (
        (atom_df["chain"] == chain)
        & (atom_df["residue_number"] == residue_number)
        & (atom_df["insertion_code"].fillna("") == insertion_code)
    )

    backbone_atoms = {"N", "C", "O", "OXT"}

    is_target_backbone = (
        is_target
        & atom_df["atom_name"].isin(backbone_atoms)
    )

    keep_atoms = ~is_target | is_target_backbone

    return atom_df.loc[keep_atoms].copy()

def get_target_backbone(
    atom_df,
    chain: str,
    residue_number: int,
    insertion_code: str = "",
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Extract N, CA, and C coordinates of a target residue."""

    target = atom_df.loc[
        (atom_df["chain"] == chain)
        & (atom_df["residue_number"] == residue_number)
        & (atom_df["insertion_code"].fillna("") == insertion_code)
    ]

    coordinates = {}

    for atom_name in ("N", "CA", "C"):
        atoms = target.loc[target["atom_name"] == atom_name]

        if len(atoms) != 1:
            raise ValueError(
                f"Expected exactly one {atom_name} atom "
                f"at {chain}:{residue_number}{insertion_code}"
            )

        coordinates[atom_name] = atoms.iloc[0][
            ["x", "y", "z"]
        ].to_numpy(dtype=float)

    return coordinates["N"], coordinates["CA"], coordinates["C"]

def get_pazf_sidechain_coordinates(
    mol: Chem.Mol,
    coordinates: np.ndarray,
) -> np.ndarray:
    """Extract pAzF side-chain heavy-atom coordinates."""

    sidechain_indices = [
        atom.GetIdx()
        for atom in mol.GetAtoms()
        if atom.GetSymbol() != "H"
        and atom.GetIdx() not in {0, 1, 12, 13, 14}
    ]

    return coordinates[sidechain_indices]

def compute_atom_distance_matrix(
    sidechain_coords: np.ndarray,
    environment_coords: np.ndarray,
) -> np.ndarray:
    """Compute distances between side-chain and environment atoms."""

    sidechain_coords = np.asarray(sidechain_coords, dtype=float)
    environment_coords = np.asarray(environment_coords, dtype=float)

    differences = (
        sidechain_coords[:, None, :]
        - environment_coords[None, :, :]
    )

    return np.linalg.norm(differences, axis=2)

def compute_vdw_overlap_matrix(
    distances: np.ndarray,
    sidechain_elements: list[str],
    environment_elements: list[str],
) -> np.ndarray:
    """Compute element-specific van der Waals overlaps."""

    vdw_radii = {
        "C": 1.70,
        "N": 1.55,
        "O": 1.52,
        "S": 1.80,
    }

    sidechain_radii = np.array([
        vdw_radii[element.upper()]
        for element in sidechain_elements
    ])

    environment_radii = np.array([
        vdw_radii[element.upper()]
        for element in environment_elements
    ])

    radius_sums = (
        sidechain_radii[:, None]
        + environment_radii[None, :]
    )

    return np.maximum(0.0, radius_sums - distances)

def exclude_bonded_neighbor_overlaps(
    overlaps: np.ndarray,
    sidechain_atom_indices: list[int],
    environment,
    chain: str,
    residue_number: int,
    insertion_code: str = "",
) -> np.ndarray:
    """Exclude CB-to-backbone 1-3 contacts from overlap scoring."""

    corrected = overlaps.copy()

    is_target = (
        (environment["chain"] == chain)
        & (environment["residue_number"] == residue_number)
        & (
            environment["insertion_code"].fillna("")
            == insertion_code
        )
    )

    is_bonded_neighbor = (
        is_target
        & environment["atom_name"].isin(["N", "C"])
    )

    cb_atom_index = 2

    cb_row = sidechain_atom_indices.index(cb_atom_index)

    corrected[
        cb_row,
        is_bonded_neighbor.to_numpy(),
    ] = 0.0

    return corrected

def compute_steric_score(overlaps: np.ndarray) -> float:
    """Compute a squared van der Waals overlap penalty."""

    overlaps = np.asarray(overlaps, dtype=float)

    if np.any(overlaps < 0):
        raise ValueError("Overlap values must be non-negative.")

    return float(np.sum(overlaps ** 2))

def place_pazf_sidechain_on_backbone(
    mol,
    n,
    ca,
    c,
):
    """
    Place a pAzF sidechain using PDB backbone geometry.

    Returns coordinates for the full RDKit molecule, with
    N, CA, and C replaced by the supplied PDB coordinates.

    The returned coordinates are intended for sidechain
    steric evaluation, not as a fully refined residue.
    """

    n = np.asarray(n, dtype=float)
    ca = np.asarray(ca, dtype=float)
    c = np.asarray(c, dtype=float)

    original = np.asarray(
        mol.GetConformer().GetPositions(),
        dtype=float,
    )

    old_n = original[0]
    old_ca = original[1]
    old_cb = original[2]

    # Measure the original RDKit sidechain geometry.
    ca_cb_length = np.linalg.norm(old_cb - old_ca)

    def bond_angle(a, center, b):
        u = a - center
        v = b - center

        cosine = np.dot(u, v) / (
            np.linalg.norm(u) * np.linalg.norm(v)
        )

        return np.degrees(
            np.arccos(np.clip(cosine, -1.0, 1.0))
        )

    n_ca_cb_angle = bond_angle(
        original[0], old_ca, old_cb
    )

    c_ca_cb_angle = bond_angle(
        original[12], old_ca, old_cb
    )

    # Construct a new CB from the actual PDB backbone.
    new_cb = build_cb_from_angles(
        n=n,
        ca=ca,
        c=c,
        ca_cb_length=ca_cb_length,
        n_ca_cb_angle=n_ca_cb_angle,
        c_ca_cb_angle=c_ca_cb_angle,
    )

    # Move the complete sidechain rigidly.
    aligned = align_sidechain_to_cb(
        coordinates=original,
        old_ca=old_ca,
        old_cb=old_cb,
        new_ca=ca,
        new_cb=new_cb,
        old_n=old_n,
        new_n=n,
    )

    # Use the real PDB backbone coordinates.
    aligned[0] = n
    aligned[1] = ca
    aligned[12] = c

    return aligned

def score_pazf_site(
    atom_df,
    chain="A",
    residue_number=20,
    insertion_code="",
    seed=42,
):
    """
    Score 12 pAzF rotamers at one protein residue.

    Lower steric scores indicate less van der Waals overlap.

    Returns a dictionary containing all rotamer scores,
    the best rotamer, and the minimum steric score.
    """

    # 1. Extract target backbone and environment.
    n, ca, c = get_target_backbone(
        atom_df,
        chain,
        residue_number,
        insertion_code,
    )

    environment = get_environment_atoms(
        atom_df,
        chain,
        residue_number,
        insertion_code,
    )

    # RANA v0.1 uses heavy-atom-only steric scoring.
    # PDB structures may contain explicit hydrogen/deuterium atoms.
    environment = environment.loc[
        ~environment["element"].astype(str).str.strip().str.upper().isin(
            {"H", "D"}
        )
    ].copy()

    environment_coords = environment[
        ["x", "y", "z"]
    ].to_numpy(dtype=float)

    environment_elements = environment["element"].tolist()

    # 2. Generate pAzF conformer and rotamers.
    mol = generate_pazf_conformer(seed=seed)
    rotamers = generate_pazf_rotamers(mol)

    results = []

    # 3. Evaluate each rotamer.
    for chi1, chi2, rotamer in rotamers:

        coords = place_pazf_sidechain_on_backbone(
            rotamer,
            n,
            ca,
            c,
        )

        sidechain_indices = [
            atom.GetIdx()
            for atom in rotamer.GetAtoms()
            if atom.GetSymbol() != "H"
            and atom.GetIdx() not in {0, 1, 12, 13, 14}
        ]

        sidechain_elements = [
            rotamer.GetAtomWithIdx(i).GetSymbol()
            for i in sidechain_indices
        ]

        sidechain_coords = coords[sidechain_indices]

        distances = compute_atom_distance_matrix(
            sidechain_coords,
            environment_coords,
        )

        overlaps = compute_vdw_overlap_matrix(
            distances,
            sidechain_elements,
            environment_elements,
        )

        overlaps = exclude_bonded_neighbor_overlaps(
            overlaps,
            sidechain_indices,
            environment,
            chain=chain,
            residue_number=residue_number,
            insertion_code=insertion_code,
        )

        score = compute_steric_score(overlaps)

        results.append({
            "chi1": float(chi1),
            "chi2": float(chi2),
            "steric_score": float(score),
        })

    # 4. Identify the lowest-scoring rotamer.
    best = min(
        results,
        key=lambda item: item["steric_score"],
    )

    return {
        "chain": chain,
        "residue_number": residue_number,
        "insertion_code": insertion_code,
        "rotamers": results,
        "best_rotamer": best,
        "min_steric_score": best["steric_score"],
    }
