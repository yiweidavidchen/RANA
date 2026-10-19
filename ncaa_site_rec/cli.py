
from __future__ import annotations

import argparse
from pathlib import Path

import re

from ncaa_site_rec.io.structure import pdb_to_residue_table
from ncaa_site_rec.features.structural import (
    compute_sasa,
    compute_relative_sasa,
    compute_local_packing,
    compute_functional_site_distances,
)
from ncaa_site_rec.features.asa_reference import TIEN_2013_MAX_ASA

def parse_functional_residues(
    value: str,
) -> list[tuple[str, int, str]]:
    """Parse residue IDs such as A:11,A:20,A:10B."""
    result = []

    for item in value.split(","):
        item = item.strip()

        match = re.fullmatch(
            r"([^:\s,]):(-?\d+)([A-Za-z]?)",
            item,
        )

        if match is None:
            raise ValueError(
                f"Invalid functional residue ID: {item!r}. "
                "Expected format such as A:11 or A:10B."
            )

        chain, number, insertion_code = match.groups()

        result.append(
            (chain, int(number), insertion_code)
        )

    return result

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rana",
        description="RANA: structure-aware ncAA incorporation-site recommender",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    # Existing ranking command
    rank = subparsers.add_parser(
        "rank",
        help="Rank candidate incorporation sites",
    )
    rank.add_argument("--pdb", required=True, type=Path)
    rank.add_argument("--ncaa", required=True)
    rank.add_argument("--catalytic-residues", nargs="*", type=int, default=[])
    rank.add_argument("--binding-site-residues", nargs="*", type=int, default=[])
    rank.add_argument("--output", required=True, type=Path)

    # New structure inspection command
    inspect = subparsers.add_parser(
        "inspect",
        help="Parse a PDB structure into a residue table",
    )
    inspect.add_argument("--pdb", required=True, type=Path)
    inspect.add_argument("--output", required=True, type=Path)

    inspect.add_argument(
        "--functional-residues",
        type=str,
        default=None,
        help=(
            "Comma-separated functional residue IDs, "
            "e.g. A:11,A:20"
        ),
    )  

    return parser


def run_rank(args: argparse.Namespace) -> int:
    if args.ncaa.lower() not in {"pazf", "azf", "4ii"}:
        raise SystemExit(
            "v0.1 currently supports pAzF / AzF / CCD 4II only."
        )

    raise NotImplementedError(
        "End-to-end ranking is not implemented yet. "
        "See docs/design.md for the v0.1 pipeline."
    )



def run_inspect(args: argparse.Namespace) -> int:
    # M1: Parse residue identities and coordinates.
    residues = pdb_to_residue_table(args.pdb)

    # M2: Compute protein-only absolute SASA.
    sasa = compute_relative_sasa(
        compute_sasa(args.pdb),
        TIEN_2013_MAX_ASA,
    )

    # Match features using original PDB residue identities.
    keys = [
        "chain",
        "residue_number",
        "insertion_code",
        "residue_name",
    ]

    df = residues.merge(
        sasa,
        on=keys,
        how="left",
        validate="one_to_one",
        indicator=True,
    )

    # Stop if any residue failed to match.
    if not (df["_merge"] == "both").all():
        raise ValueError(
            "SASA merge failed: some residues were not matched."
        )

    df = df.drop(columns=["_merge"])
    df = compute_local_packing(df)

    # M2.4: Optional distance to functional residues.
    if args.functional_residues is not None:
        functional_residues = parse_functional_residues(
            args.functional_residues
        )

        df = compute_functional_site_distances(
            df,
            functional_residues=functional_residues,
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)

    print(f"Parsed residues: {len(df)}")
    print(f"Chains: {', '.join(df['chain'].unique())}")
    print(f"Missing CA: {(~df['has_ca']).sum()}")
    print(f"Missing SASA: {df['sasa_abs'].isna().sum()}")
    print(f"Total SASA (A^2): {df['sasa_abs'].sum():.2f}")
    print(f"Output: {args.output}")

    return 0



def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "rank":
        return run_rank(args)

    if args.command == "inspect":
        return run_inspect(args)

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
