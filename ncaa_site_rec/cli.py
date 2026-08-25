from __future__ import annotations
import argparse
from pathlib import Path

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rana", description="RANA: structure-aware ncAA incorporation-site recommender")
    subparsers = parser.add_subparsers(dest="command", required=True)
    rank = subparsers.add_parser("rank", help="Rank candidate incorporation sites")
    rank.add_argument("--pdb", required=True, type=Path)
    rank.add_argument("--ncaa", required=True)
    rank.add_argument("--catalytic-residues", nargs="*", type=int, default=[])
    rank.add_argument("--binding-site-residues", nargs="*", type=int, default=[])
    rank.add_argument("--output", required=True, type=Path)
    return parser

def run_rank(args: argparse.Namespace) -> int:
    if args.ncaa.lower() not in {"pazf", "azf", "4ii"}:
        raise SystemExit("v0.1 currently supports pAzF / AzF / CCD 4II only.")
    raise NotImplementedError("End-to-end ranking is not implemented yet. See docs/design.md for the v0.1 pipeline.")

def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "rank":
        return run_rank(args)
    parser.error("Unknown command")
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
