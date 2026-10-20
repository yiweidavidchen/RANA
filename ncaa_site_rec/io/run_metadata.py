"""Reproducibility metadata for RANA screening runs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd
import subprocess

def sha256_file(path: str | Path) -> str:
    """Compute the SHA-256 digest of an input file."""
    digest = hashlib.sha256()

    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()

def get_git_revision() -> dict:
    """Identify the Git revision and whether tracked files are modified."""

    def git(*args: str) -> str:
        return subprocess.check_output(
            ["git", *args],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()

    try:
        revision = git("rev-parse", "HEAD")
        tracked_changes = git("status", "--porcelain", "--untracked-files=no")

        return {
            "git_commit": revision,
            "tracked_worktree_modified": bool(tracked_changes),
        }
    except (OSError, subprocess.CalledProcessError):
        return {
            "git_commit": None,
            "tracked_worktree_modified": None,
        }

def build_run_metadata(
    *,
    pdb_path: str | Path,
    chain: str,
    ncaa: str,
    seed: int,
    low_clash_threshold: float,
    favorable_fraction: float,
    result: pd.DataFrame,
) -> dict:
    """Describe the input and configuration of a screening run."""

    pdb_path = Path(pdb_path)

    return {
        "schema_version": "1.0",
        "tool": "RANA",
        "software": get_git_revision(),
        "analysis": "fixed_structure_pazf_geometric_screening",
        "input": {
            "pdb_path": str(pdb_path),
            "pdb_sha256": sha256_file(pdb_path),
            "chain": chain,
        },
        "configuration": {
            "ncaa": ncaa.lower(),
            "seed": seed,
            "low_clash_threshold": low_clash_threshold,
            "favorable_fraction": favorable_fraction,
        },
        "sampling": {
            "method": "discrete_chi1_chi2_rotamer_sampling",
            "n_rotamers_observed": sorted(
                int(x)
                for x in result["n_rotamers"].dropna().unique()
            ),
        },
        "results": {
            "n_residues": len(result),
            "status_counts": {
                str(k): int(v)
                for k, v in result["status"].value_counts().items()
            },
            "tier_counts": {
                str(k): int(v)
                for k, v in result["candidate_tier"].value_counts().items()
            },
        },
        "limitations": [
            "Fixed-structure steric screening, not a stability prediction.",
            "Rotamer sampling does not exhaust conformational space.",
            "Scores and tiers are heuristic and not experimentally calibrated.",
            "No prediction of ncAA incorporation efficiency.",
            "Chemical-handle accessibility is not explicitly evaluated.",
        ],
    }


def write_run_metadata(
    metadata: dict,
    output_path: str | Path,
) -> None:
    """Write run metadata as human-readable JSON."""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2, ensure_ascii=False)
        handle.write("\n")