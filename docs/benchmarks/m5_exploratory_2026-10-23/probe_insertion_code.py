"""Read-only diagnostic, not a fix. Run with the existing RANA environment.

Print JSON evidence to stdout. Optional --pdb adds a real-geometry label-only
probe. Source tables are copied in memory; neither input nor code is written.
"""

import argparse
import hashlib
import json
import platform
import subprocess
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
from ncaa_site_rec.features import pazf
from ncaa_site_rec.io.structure import pdb_to_atom_table


def run(pdb):
    environment = pd.DataFrame({"chain": ["A"] * 4, "residue_number": [31] * 4,
                                "insertion_code": ["A", "A", "", ""],
                                "atom_name": ["N", "C", "N", "C"]})
    overlaps = np.array([[1., 2., 3., 4.]])
    omitted = pazf.exclude_bonded_neighbor_overlaps(overlaps, [2], environment, "A", 31)
    explicit = pazf.exclude_bonded_neighbor_overlaps(overlaps, [2], environment, "A", 31, insertion_code="A")
    assert omitted.tolist() == [[1., 2., 0., 0.]]
    assert explicit.tolist() == [[0., 0., 3., 4.]]
    record = {"python": platform.python_version(),
              "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "synthetic_environment": environment.to_dict(orient="records"),
              "input_overlap": overlaps.tolist(), "omitted_argument": omitted.tolist(),
              "explicit_nonblank_argument": explicit.tolist(),
              "interpretation": "For target A:31:A omission leaves its CB/N,C self contacts and wrongly excludes blank-code A:31 contacts."}
    if pdb:
        atoms = pdb_to_atom_table(pdb)
        original = pazf.exclude_bonded_neighbor_overlaps
        calls = []

        def traced(*args, **kwargs):
            calls.append({"chain": kwargs.get("chain"), "residue_number": kwargs.get("residue_number"),
                          "insertion_code_keyword_present": "insertion_code" in kwargs,
                          "n_positional_arguments": len(args)})
            return original(*args, **kwargs)

        blank = pazf.score_pazf_site(atoms, chain="A", residue_number=31, insertion_code="", seed=42)
        altered = atoms.copy()
        target = (altered.chain == "A") & (altered.residue_number == 31) & (altered.insertion_code == "")
        altered.loc[target, "insertion_code"] = "A"
        with patch.object(pazf, "exclude_bonded_neighbor_overlaps", traced):
            nonblank = pazf.score_pazf_site(altered, chain="A", residue_number=31, insertion_code="A", seed=42)
        assert len(calls) == 12 and all(not c["insertion_code_keyword_present"] and c["n_positional_arguments"] == 3 for c in calls)
        assert blank["min_steric_score"] != nonblank["min_steric_score"]
        record["label_only_real_geometry_probe"] = {
            "source": str(pdb), "source_sha256": hashlib.sha256(pdb.read_bytes()).hexdigest(),
            "target": "1L63 A:31 blank versus identical geometry relabeled A:31:A in memory",
            "blank_min_steric_score": blank["min_steric_score"],
            "nonblank_min_steric_score": nonblank["min_steric_score"],
            "blank_low_clash_count": sum(r["steric_score"] <= 10 for r in blank["rotamers"]),
            "nonblank_low_clash_count": sum(r["steric_score"] <= 10 for r in nonblank["rotamers"]),
            "forwarding_calls": calls,
            "scope": "Diagnostic relabeling only, not a new frozen scan or experimental variant."}
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdb", type=Path)
    run(parser.parse_args().pdb)
