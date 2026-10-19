
from __future__ import annotations

import argparse
from pathlib import Path

from ncaa_site_rec.io.structure import pdb_to_residue_table


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
    df = pdb_to_residue_table(args.pdb)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)

    print(f"Parsed residues: {len(df)}")
    print(f"Chains: {', '.join(df['chain'].unique())}")
    print(f"Missing CA: {(~df['has_ca']).sum()}")
    print(f"Output: {args.output}")

    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "rank":
        return run_rank(args)

    if args.command == "inspect":
        return run_inspect(args)

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
