import numpy as np
import pandas as pd

from ncaa_site_rec.features.pazf import score_pazf_site


STANDARD_AMINO_ACIDS = {
    "ALA", "ARG", "ASN", "ASP", "CYS",
    "GLN", "GLU", "GLY", "HIS", "ILE",
    "LEU", "LYS", "MET", "PHE", "PRO",
    "SER", "THR", "TRP", "TYR", "VAL",
}

SCAN_RESULT_COLUMNS = [
    "chain",
    "residue_number",
    "insertion_code",
    "residue_name",
    "status",
    "min_steric_score",
    "mean_steric_score",
    "median_steric_score",
    "low_clash_fraction",
    "best_chi1",
    "best_chi2",
    "n_rotamers",
    "rotamer_scores",
    "reason",
]


def scan_pazf_sites(
    atom_df: pd.DataFrame,
    chain: str = "A",
    seed: int = 42,
    low_clash_threshold: float = 10.0,
    candidate_residues: list[int] | None = None,
) -> pd.DataFrame:
    """
    Scan standard amino-acid residues in a protein chain
    for pAzF sidechain steric compatibility.

    Returns one row per residue, including failed/skipped sites.
    """

    if low_clash_threshold < 0:
        raise ValueError("low_clash_threshold must be nonnegative")

    chain_atoms = atom_df.loc[
        atom_df["chain"] == chain
    ]

    residue_columns = [
        "chain",
        "residue_number",
        "insertion_code",
        "residue_name",
    ]

    residues = (
        chain_atoms[residue_columns]
        .drop_duplicates()
        .sort_values(
            ["residue_number", "insertion_code"]
        )
    )

    if candidate_residues is not None:
        residues = residues.loc[
            residues["residue_number"].isin(candidate_residues)
        ]

    results = []

    for residue in residues.itertuples(index=False):
        residue_name = str(residue.residue_name).upper()
        residue_number = int(residue.residue_number)
        insertion_code = str(residue.insertion_code).strip()

        row = {
            "chain": chain,
            "residue_number": residue_number,
            "insertion_code": insertion_code,
            "residue_name": residue_name,
            "status": "skipped",
            "min_steric_score": np.nan,
            "mean_steric_score": np.nan,
            "median_steric_score": np.nan,
            "low_clash_fraction": np.nan,
            "best_chi1": np.nan,
            "best_chi2": np.nan,
            "n_rotamers": 0,
            "rotamer_scores": None,
            "reason": "",
        }

        if residue_name not in STANDARD_AMINO_ACIDS:
            row["reason"] = "nonstandard_residue"
            results.append(row)
            continue

        residue_atoms = chain_atoms.loc[
            (chain_atoms["residue_number"] == residue_number)
            & (
                chain_atoms["insertion_code"].fillna("").str.strip()
                == insertion_code
            )
        ]

        atom_names = set(residue_atoms["atom_name"])

        if not {"N", "CA", "C"}.issubset(atom_names):
            row["reason"] = "incomplete_backbone"
            results.append(row)
            continue

        try:
            site = score_pazf_site(
                atom_df,
                chain=chain,
                residue_number=residue_number,
                insertion_code=insertion_code,
                seed=seed,
            )

            scores = np.array(
                [
                    rotamer["steric_score"]
                    for rotamer in site["rotamers"]
                ],
                dtype=float,
            )

            best = site["best_rotamer"]

            row.update({
                "status": "scored",
                "min_steric_score": float(np.min(scores)),
                "mean_steric_score": float(np.mean(scores)),
                "median_steric_score": float(np.median(scores)),
                "low_clash_fraction": float(
                    np.mean(scores <= low_clash_threshold)
                ),
                "best_chi1": best["chi1"],
                "best_chi2": best["chi2"],
                "n_rotamers": len(scores),
                "rotamer_scores": scores.tolist(),
                "reason": "",
            })

        except (ValueError, KeyError, IndexError) as exc:
            row["status"] = "failed"
            row["reason"] = f"{type(exc).__name__}: {exc}"

        results.append(row)

    return pd.DataFrame(
    results,
    columns=SCAN_RESULT_COLUMNS,
)