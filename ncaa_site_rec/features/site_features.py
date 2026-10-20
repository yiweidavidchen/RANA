
from pathlib import Path

import pandas as pd

from ncaa_site_rec.io.structure import (
    pdb_to_atom_table,
    pdb_to_residue_table,
)
from ncaa_site_rec.features.asa_reference import TIEN_2013_MAX_ASA
from ncaa_site_rec.features.structural import (
    compute_sasa,
    compute_relative_sasa,
    compute_local_packing,
    compute_functional_site_distances,
)
from ncaa_site_rec.features.site_scan import scan_pazf_sites


RESIDUE_KEYS = [
    "chain",
    "residue_number",
    "insertion_code",
    "residue_name",
]


def build_pazf_feature_table(
    pdb_path: str | Path,
    chain: str = "A",
    functional_residues: list[tuple[str, int, str]] | None = None,
    seed: int = 42,
    low_clash_threshold: float = 10.0,
) -> pd.DataFrame:
    """Combine M2 structural features and M4.1 pAzF steric scores."""

    # M1: Read the original protein structure.
    residues = pdb_to_residue_table(pdb_path)
    atoms = pdb_to_atom_table(pdb_path)

    # Calculate packing using all protein chains.
    residues = compute_local_packing(residues)

    # Return features only for the requested chain.
    residues = residues.loc[
        residues["chain"] == chain
    ].copy()

    if residues.empty:
        raise ValueError(f"No standard residues found in chain {chain!r}.")

    # M2: Compute SASA and RSA from the complete structure.
    sasa = compute_relative_sasa(
        compute_sasa(pdb_path),
        TIEN_2013_MAX_ASA,
    )

    structural = residues.merge(
        sasa,
        on=RESIDUE_KEYS,
        how="left",
        validate="one_to_one",
        indicator=True,
    )

    if not (structural["_merge"] == "both").all():
        raise ValueError("SASA merge failed: unmatched residues.")

    structural = structural.drop(columns="_merge")

    if functional_residues is not None:
        structural = compute_functional_site_distances(
            structural,
            functional_residues=functional_residues,
        )

    # M4.1: Evaluate pAzF rotamers in the complete atom environment.
    steric = scan_pazf_sites(
        atoms,
        chain=chain,
        seed=seed,
        low_clash_threshold=low_clash_threshold,
    )

    # M4.2: Join structural and steric features by PDB identity.
    combined = structural.merge(
        steric,
        on=RESIDUE_KEYS,
        how="left",
        validate="one_to_one",
        indicator=True,
    )

    if not (combined["_merge"] == "both").all():
        raise ValueError("Steric merge failed: unmatched residues.")

    combined = combined.drop(columns="_merge")

    return combined.sort_values(
        ["chain", "residue_number", "insertion_code"]
    ).reset_index(drop=True)
