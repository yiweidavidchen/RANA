"""Fetch pinned public coordinates or run the frozen T4L sensitivity inputs."""
import argparse
import ast
import json
import platform
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

import numpy as np
import pandas as pd
from Bio.PDB import PDBParser
from Bio.PDB.Polypeptide import is_aa

import ncaa_site_rec
from structure_audit import protein_atoms, sha

HERE = Path(__file__).resolve().parent


def verify_scientific_source(root, package, base):
    """Allow documentation-only descendants; require the entire frozen source."""
    expected = {p for p in subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", base, "--", "ncaa_site_rec"], cwd=root,
    ).decode().splitlines() if p.endswith(".py")}
    actual = {p.relative_to(root).as_posix() for p in package.rglob("*.py")}
    if not expected or expected != actual:
        raise ValueError("Scientific source file set differs from frozen base")
    for relative in sorted(actual):
        reference = subprocess.check_output(["git", "show", f"{base}:{relative}"], cwd=root)
        if (root / relative).read_bytes().replace(b"\r\n", b"\n") != reference.replace(b"\r\n", b"\n"):
            raise ValueError(f"Scientific source differs from frozen base: {relative}")


def fetch(output, all_audit_files=False):
    manifest = json.loads((HERE / "source_manifest.json").read_text())
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    output.mkdir(parents=True, exist_ok=False)
    records = {}
    try:
        for name, source in manifest["files"].items():
            if not all_audit_files and name not in {f"{p}.{ext}" for p in ["1L63", "1LW9", "219L"] for ext in ["pdb", "cif"]}:
                continue
            with urllib.request.urlopen(source["url"], timeout=60) as response:
                payload, final_url = response.read(), response.geturl()
            path = output / name
            path.write_bytes(payload)
            records[name] = {"url": source["url"], "final_url": final_url,
                             "retrieved_utc": datetime.now(timezone.utc).isoformat(), "sha256": sha(path)}
            if records[name]["sha256"] != source["sha256"]:
                raise ValueError(f"Public source changed: {name}; review required")
    finally:
        (output / "retrieval.json").write_text(json.dumps(records, indent=2) + "\n")


def prepare(source, output, chain="A"):
    """Copy original T4L ATOM records, not the 2FG8 assembly converter."""
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("source", source)
    if len(structure) != 1 or chain not in structure[0]:
        raise ValueError("A single model containing the target chain is required")
    model = structure[0]
    expected = {k: a for k, a in protein_atoms(model).items() if k[0] == chain}
    lines = [line for line in source.read_text().splitlines()
             if line.startswith("ATOM  ") and line[21] == chain
             and line[17:20] in {r.resname for r in model[chain] if is_aa(r, standard=True)}
             and line[76:78].strip() not in {"H", "D"}]
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write("MODEL        1\n" + "\n".join(lines) + "\nENDMDL\nEND   \n")
    prepared = parser.get_structure("prepared", output)[0]
    actual = protein_atoms(prepared)
    if expected.keys() != actual.keys():
        raise ValueError("Prepared atom identities do not match retained source atoms")
    for key in expected:
        a, b = expected[key], actual[key]
        if not np.array_equal(a.coord, b.coord) or a.occupancy != b.occupancy or a.bfactor != b.bfactor:
            raise ValueError(f"Copied atom changed: {key}")
    # Alternate records retain source order, including the tie-selected atom.
    for old_residue, new_residue in zip([r for r in model[chain] if is_aa(r, standard=True)], prepared[chain]):
        for old_atom in old_residue:
            if old_atom.element in {"H", "D"}:
                continue
            new_atom = new_residue[old_atom.name]
            if old_atom.altloc != new_atom.altloc or not np.array_equal(old_atom.coord, new_atom.coord):
                raise ValueError("Selected alternate conformer changed")
    return {"source_sha256": sha(source), "prepared_sha256": sha(output),
            "retained_chains": [c.id for c in prepared], "modeled_sites": len(prepared[chain]),
            "heavy_atom_records_including_altlocs": len(actual), "max_abs_coordinate_change_A": 0,
            "selected_altlocs_preserved": True}


def validate_scan(path, expected):
    frame = pd.read_csv(path, keep_default_na=False)
    keys = ["chain", "residue_number", "insertion_code", "residue_name"]
    if frame.duplicated(keys[:3]).any() or set(map(tuple, frame[keys].itertuples(index=False, name=None))) != expected:
        raise ValueError("Scan identity set differs from prepared residues")
    if not frame.status.isin(["scored", "failed", "skipped"]).all():
        raise ValueError("Unexpected scan status")
    for row in frame.itertuples():
        if row.status == "scored":
            scores = np.array(ast.literal_eval(row.rotamer_scores), dtype=float)
            values = np.array([row.rsa, row.ca_neighbors_8a, row.min_steric_score, row.low_clash_fraction], dtype=float)
            if scores.shape != (12,) or row.n_rotamers != 12 or not np.isfinite(scores).all() or not np.isfinite(values).all():
                raise ValueError("Scored row lacks finite metrics/12 rotamers")
        elif not row.reason:
            raise ValueError("Unscored row lacks a diagnostic")
    metadata = json.loads(path.with_suffix(".metadata.json").read_text())
    if metadata["output"]["csv_sha256"] != sha(path) or metadata["results"]["n_residues"] != len(frame):
        raise ValueError("Scan sidecar does not match CSV")
    return {"rows": len(frame), "status_counts": frame.status.value_counts().to_dict(),
            "csv_sha256": sha(path), "metadata_sha256": sha(path.with_suffix(".metadata.json"))}


def run(sources, output):
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    plan = json.loads((HERE / "frozen_plan.json").read_text())
    for name, field in [("analysis_plan.md", "analysis_plan_sha256"), ("audit/structure_audit.json", "audit_sha256"),
                        ("audit/site_mapping.csv", "mapping_sha256"), ("source_manifest.json", "source_manifest_sha256")]:
        if sha(HERE / name) != plan[field]:
            raise ValueError(f"Frozen dependency changed: {name}")
    root = HERE.parents[2]
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    package = Path(ncaa_site_rec.__file__).resolve().parent
    if package != root / "ncaa_site_rec":
        raise ValueError("Use the scientific package from this checkout")
    verify_scientific_source(root, package, plan["base_git_commit"])
    subprocess.run(["git", "diff", "--exit-code", "HEAD", "--", "ncaa_site_rec"], cwd=root, check=True)
    output.mkdir(parents=True, exist_ok=False)
    record = {"started_utc": datetime.now(timezone.utc).isoformat(), "status": "started", "stage": "preparation",
              "git_commit": head, "plan_sha256": sha(HERE / "frozen_plan.json"),
              "script_sha256": {p.name: sha(p) for p in [Path(__file__), HERE / "structure_audit.py"]},
              "scientific_package_sha256": {p.relative_to(root).as_posix(): sha(p) for p in package.rglob("*.py")},
              "environment": {"python": platform.python_version(), "executable": sys.executable,
                  "platform": platform.platform(), "packages": {p: version(p) for p in ["numpy", "pandas", "biopython", "rdkit"]}},
              "structures": {}}
    def save():
        (output / "run.json").write_text(json.dumps(record, indent=2) + "\n")
    save()
    try:
        for entry in plan["structures"]:
            pdb = entry["pdb_id"]
            record["stage"] = f"{pdb}_preparation"
            save()
            for ext in ["pdb", "cif"]:
                if sha(sources / f"{pdb}.{ext}") != entry[f"{ext}_sha256"]:
                    raise ValueError(f"Source hash mismatch: {pdb}.{ext}")
            case = output / pdb
            case.mkdir()
            prepared = case / "protein_A.pdb"
            preparation = prepare(sources / f"{pdb}.pdb", prepared)
            model = PDBParser(QUIET=True).get_structure(pdb, prepared)[0]
            expected = {(c.id, r.id[1], r.id[2].strip(), r.resname) for c in model for r in c}
            if len(expected) != entry["modeled_sites"]:
                raise ValueError("Prepared residue count differs from audit")
            csv_path = case / "ranked.csv"
            config = plan["scan"]
            command = [sys.executable, "-I", "-B", "-m", "ncaa_site_rec.cli", "rank", "--pdb", str(prepared),
                       "--chain", entry["chain"], "--ncaa", config["ncaa"], "--seed", str(config["seed"]),
                       "--low-clash-threshold", str(config["low_clash_threshold"]),
                       "--favorable-fraction", str(config["favorable_fraction"]), "--output", str(csv_path)]
            record["stage"] = f"{pdb}_scan"
            info = {"preparation": preparation, "command": command, "started_utc": datetime.now(timezone.utc).isoformat()}
            record["structures"][pdb] = info
            save()
            print(f"Frozen scan {pdb}: {len(expected)} modeled sites", flush=True)
            completed = subprocess.run(command, cwd=root, capture_output=True, text=True)
            (case / "stdout.txt").write_text(completed.stdout)
            (case / "stderr.txt").write_text(completed.stderr)
            info.update(returncode=completed.returncode, finished_utc=datetime.now(timezone.utc).isoformat())
            save()
            info["output_validation"] = validate_scan(csv_path, expected)
            completed.check_returncode()
            save()
        record.update(status="scans_completed", stage="complete", finished_utc=datetime.now(timezone.utc).isoformat())
        save()
    except Exception as error:
        record.update(status="failed", error=f"{type(error).__name__}: {error}")
        save()
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["fetch", "run"])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sources", type=Path)
    parser.add_argument("--all-audit-files", action="store_true")
    args = parser.parse_args()
    if args.action == "fetch":
        fetch(args.output.resolve(), args.all_audit_files)
    else:
        if not args.sources:
            parser.error("run requires --sources")
        run(args.sources.resolve(), args.output.resolve())
