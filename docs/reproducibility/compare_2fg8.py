"""Compare completed new scans to explicit historical references, never generate.

Requires the new run to have completed before any historical file is opened.
Tolerances come from the configuration saved before either new scan ran.
"""

import argparse
import ast
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from Bio.PDB import PDBParser
from ncaa_site_rec.io.prepare_structure import atom_records, coordinate_difference


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_close(a, b, *, rtol, atol, label):
    """Compare finite arrays with explicit checks, including under python -O."""
    if a.shape != b.shape or not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError(f"{label}: shape mismatch or non-finite values")
    if not np.allclose(a, b, rtol=rtol, atol=atol, equal_nan=False):
        raise ValueError(f"{label}: values differ beyond the declared tolerance")


def structure_comparison(generated, reference, coordinate_tolerance):
    parser = PDBParser(QUIET=True)
    new = parser.get_structure("new", generated)
    old = parser.get_structure("old", reference)
    if len(new) != 1 or len(old) != 1:
        raise ValueError("Comparison requires one model in both inputs")
    new_model, old_model = new[0], old[0]
    new_atoms, old_atoms = atom_records(new_model), atom_records(old_model)
    delta = coordinate_difference(old_atoms, new_atoms)
    if not np.isfinite(delta) or delta > coordinate_tolerance:
        raise ValueError(f"{generated}: coordinate difference {delta} exceeds tolerance")
    for key in old_atoms:
        require_close(np.asarray(new_atoms[key].coord), np.asarray(old_atoms[key].coord),
                      rtol=0, atol=coordinate_tolerance, label=f"coordinates {key}")
        if old_atoms[key].occupancy != new_atoms[key].occupancy:
            raise ValueError(f"Occupancy differs for {key}")
        if old_atoms[key].bfactor != new_atoms[key].bfactor:
            raise ValueError(f"B factor differs for {key}")
    new_lines = generated.read_text().splitlines()
    old_lines = reference.read_text().splitlines()
    without_model_records = lambda lines: [s for s in lines if not s.startswith(("MODEL ", "ENDMDL"))]
    serialization_only = without_model_records(new_lines) == without_model_records(old_lines)
    if sha(generated) != sha(reference) and not serialization_only:
        raise ValueError("Byte difference is not explained solely by model records/newline serialization")
    return {"generated_sha256": sha(generated), "reference_sha256": sha(reference),
            "byte_identical": sha(generated) == sha(reference), "atom_identities_equal": True,
            "chains": len(new_model), "residues": sum(len(c) for c in new_model),
            "atoms_including_altlocs": len(new_atoms), "max_abs_coordinate_difference_A": delta,
            "occupancy_and_bfactor_equal": True,
            "serialization_difference": "none" if sha(generated) == sha(reference) else "explicit MODEL 1/ENDMDL records (and possible line-ending serialization) only; all other text records equal"}


def scan_comparison(generated, reference, policy):
    new = pd.read_csv(generated, keep_default_na=False, float_precision="round_trip")
    old = pd.read_csv(reference, keep_default_na=False, float_precision="round_trip")
    if new.columns.tolist() != old.columns.tolist():
        raise ValueError("Scan column schemas differ")
    if len(new) != 174 or len(old) != 174:
        raise ValueError("Both scans must contain 174 sites")
    exact = ["chain", "residue_number", "insertion_code", "residue_name", "status", "reason",
             "ca_neighbors_8a", "n_rotamers", "low_clash_fraction", "candidate_tier",
             "steric_rank", "rsa_rank", "rotamer_robustness_rank", "ranking_reason", "special_residue_flag"]
    for column in exact:
        if column not in new or new[column].tolist() != old[column].tolist():
            raise ValueError(f"Exact scan column differs or is missing: {column}")
    for frame in (new, old):
        if not frame.status.eq("scored").all() or not frame.n_rotamers.eq(12).all():
            raise ValueError("Every site must be scored with 12 rotamers")
        if frame.duplicated(["chain", "residue_number", "insertion_code"]).any():
            raise ValueError("Duplicate scan site identity")
        if not frame.reason.eq("").all():
            raise ValueError("Unexpected scoring diagnostic")
    deltas = {}
    tolerances = {"sasa_abs": policy["SASA_abs_tolerance_A2"], "rsa": policy["RSA_abs_tolerance"],
                  **{c: policy["steric_scores_abs_tolerance_A2"] for c in ["min_steric_score", "mean_steric_score", "median_steric_score"]},
                  "sasa_max": 0.0, "best_chi1": 0.0, "best_chi2": 0.0,
                  "ca_x": 0.0, "ca_y": 0.0, "ca_z": 0.0,
                  **{c: 0.0 for c in ["ca_neighbors_8a", "low_clash_fraction",
                                      "steric_rank", "rsa_rank", "rotamer_robustness_rank"]}}
    for column, tolerance in tolerances.items():
        if column not in new:
            raise ValueError(f"Missing numeric scan field: {column}")
        a, b = new[column].to_numpy(dtype=float), old[column].to_numpy(dtype=float)
        require_close(a, b, rtol=policy["relative_tolerance"], atol=tolerance, label=column)
        deltas[column] = float(np.max(np.abs(a-b)))
    arrays = [np.array([ast.literal_eval(row) for row in frame.rotamer_scores]) for frame in [new, old]]
    if any(a.shape != (174, 12) for a in arrays):
        raise ValueError("Rotamer score arrays must have shape (174, 12)")
    require_close(*arrays, rtol=0, atol=policy["steric_scores_abs_tolerance_A2"], label="rotamer_scores")
    deltas["rotamer_scores"] = float(np.max(np.abs(arrays[0]-arrays[1])))
    known = set(exact) | set(tolerances) | {"rotamer_scores"}
    for column in new.columns:
        if column not in known:
            if new[column].tolist() != old[column].tolist():
                raise ValueError(f"Remaining scan column differs: {column}")
    return {"sites": len(new), "rotamer_scores": arrays[0].size,
            "generated_sha256": sha(generated), "reference_sha256": sha(reference),
            "exact_columns_equal": exact, "max_abs_differences": deltas,
            "all_remaining_columns_equal": True, "status": "pass"}


def compare(args):
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError("Preserve previous comparisons; choose a new report path")
    run = json.loads((args.run_dir / "run.json").read_text(encoding="utf-8"))
    if run["status"] != "scans_completed_pending_separate_comparison":
        raise ValueError("Generation has not completed successfully")
    profile = json.loads(args.profile.read_text(encoding="utf-8"))
    if run["profile_sha256"] != sha(args.profile):
        raise ValueError("Profile hash does not match the generation record")
    policy = profile["comparison_policy_declared_before_execution"]
    result = {"policy": policy, "generation_completed_before_historical_reads": True,
              "comparison_script_sha256": sha(Path(__file__)), "run_record_sha256": sha(args.run_dir / "run.json"),
              "structures": {}, "scans": {}}
    for case, filename, structure, scan in [
        ("assembly", "assembly1_protein.pdb", args.reference_assembly, args.reference_assembly_scan),
        ("monomer", "target_monomer.pdb", args.reference_monomer, args.reference_monomer_scan),
    ]:
        result["structures"][case] = structure_comparison(
            args.run_dir / "prepared" / filename, structure, policy["historical_prepared_max_abs_coordinate_A"],
        )
        result["scans"][case] = scan_comparison(args.run_dir / "scans" / f"{case}.csv", scan, policy)
    result["status"] = "pass"
    # Exclusive creation also refuses a report created while comparisons ran.
    with args.output.open("x", encoding="utf-8") as output:
        output.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for option in ["run-dir", "profile", "reference-assembly", "reference-monomer",
                   "reference-assembly-scan", "reference-monomer-scan", "output"]:
        parser.add_argument("--" + option, type=Path, required=True)
    compare(parser.parse_args())
