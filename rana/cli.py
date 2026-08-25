"""CLI entrypoint.

Planned usage (see README):

    rana \\
      --pdb structure.pdb \\
      --target-ncaa azA \\
      --catalytic-residues 164,353,406 \\
      --binding-site-residues 19,295 \\
      --out candidate_sites.csv
"""
import argparse


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Rank candidate ncAA incorporation sites.")
    p.add_argument("--pdb", required=True, help="Path to input PDB file")
    p.add_argument("--target-ncaa", required=True, help="ncAA id, e.g. azA")
    p.add_argument("--catalytic-residues", required=True,
                    help="Comma-separated residue numbers")
    p.add_argument("--binding-site-residues", required=True,
                    help="Comma-separated residue numbers")
    p.add_argument("--out", required=True, help="Output CSV path")
    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    raise NotImplementedError("pipeline wiring not yet implemented")


if __name__ == "__main__":
    main()
