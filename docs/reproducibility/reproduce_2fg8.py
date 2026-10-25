"""Run preparation and two frozen scans in a NEW directory, without old outputs.

Use an installed RANA environment. Supply --input for local public mmCIF(.gz),
or omit it to download the one explicit RCSB source pinned in --profile.
"""

import argparse
import ast
import csv
import hashlib
import json
import math
import platform
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

import ncaa_site_rec
from Bio.SeqUtils import seq3
from ncaa_site_rec.io.prepare_structure import prepare_expanded_assembly

PUBLIC_URL = "https://files.rcsb.org/download/2FG8-assembly1.cif.gz"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


NUMERIC_FIELDS = (
    "ca_x", "ca_y", "ca_z", "ca_neighbors_8a", "sasa_abs", "sasa_max", "rsa",
    "min_steric_score", "mean_steric_score", "median_steric_score",
    "low_clash_fraction", "best_chi1", "best_chi2", "n_rotamers",
    "steric_rank", "rsa_rank", "rotamer_robustness_rank",
)
TEXT_FIELDS = (
    "chain", "residue_number", "insertion_code", "residue_name", "has_ca",
    "status", "rotamer_scores", "reason", "special_residue_flag",
    "candidate_tier", "ranking_reason",
)


def validate_scan_output(csv_path: Path, profile: dict, pdb_path: Path) -> dict:
    """Require a complete finite 2FG8 scan; this is not historical validation."""
    chain = profile["scan"]["chain"]
    numbers = list(range(profile["author_residue_start"], profile["author_residue_end"] + 1))
    sequence = profile["sequence"]
    if len(numbers) != 174 or len(sequence) != 174 or profile["residues_per_chain"] != 174:
        raise ValueError("This verified profile requires exactly 174 residues")
    expected = {(chain, n, ""): seq3(aa).upper() for n, aa in zip(numbers, sequence)}
    if not csv_path.is_file():
        raise ValueError(f"Missing scan CSV: {csv_path}")
    with csv_path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, strict=True)
        fields = reader.fieldnames
        if not fields or len(set(fields)) != len(fields):
            raise ValueError("Missing or duplicate CSV header fields")
        missing = set(NUMERIC_FIELDS + TEXT_FIELDS) - set(fields)
        if missing:
            raise ValueError(f"Missing required CSV fields: {sorted(missing)}")
        rows = list(reader)
    if len(rows) != len(expected):
        raise ValueError(f"Expected 174 site rows, received {len(rows)}")
    seen = set()
    tiers = {}
    for index, row in enumerate(rows, start=2):
        if None in row or any(value is None for value in row.values()):
            raise ValueError(f"CSV row {index}: field count does not match header")
        identity = (row["chain"], int(row["residue_number"]), row["insertion_code"])
        if identity in seen or identity not in expected:
            raise ValueError(f"CSV row {index}: duplicate or unexpected site {identity}")
        seen.add(identity)
        if row["residue_name"] != expected[identity]:
            raise ValueError(f"CSV row {index}: parent residue does not match profile")
        if row["status"] != "scored" or row["reason"].strip():
            raise ValueError(f"CSV row {index}: non-scored status or diagnostic: {row['status']} {row['reason']}")
        if row["has_ca"] != "True":
            raise ValueError(f"CSV row {index}: missing CA")
        for field in NUMERIC_FIELDS:
            if not row[field].strip() or not math.isfinite(float(row[field])):
                raise ValueError(f"CSV row {index}: missing or non-finite {field}")
        scores = ast.literal_eval(row["rotamer_scores"])
        if (float(row["n_rotamers"]) != 12 or not isinstance(scores, list)
                or len(scores) != 12
                or any(type(value) not in (int, float) or not math.isfinite(value) for value in scores)):
            raise ValueError(f"CSV row {index}: expected 12 finite numeric rotamer scores")
        tier = row["candidate_tier"]
        if tier not in {"geometry_favorable", "geometry_limited", "geometry_unfavorable"} or not row["ranking_reason"].strip():
            raise ValueError(f"CSV row {index}: missing/invalid tier or ranking explanation")
        tiers[tier] = tiers.get(tier, 0) + 1
    if seen != set(expected):
        raise ValueError("Site identity set does not match profile")
    metadata_path = csv_path.with_suffix(".metadata.json")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata["schema_version"] != "1.0" or metadata["tool"] != "RANA":
        raise ValueError("Invalid scan metadata schema/tool")
    if metadata["input"]["chain"] != chain or metadata["input"]["pdb_sha256"] != sha(pdb_path):
        raise ValueError("Metadata input identity/hash does not match prepared input")
    configuration = {k: v for k, v in profile["scan"].items() if k not in {"chain", "n_rotamers"}}
    if metadata["configuration"] != configuration:
        raise ValueError("Metadata configuration does not match frozen profile")
    results = metadata["results"]
    if (results["n_residues"] != 174 or results["status_counts"] != {"scored": 174}
            or results["tier_counts"] != tiers
            or metadata["sampling"]["n_rotamers_observed"] != [12]
            or metadata["output"]["csv_sha256"] != sha(csv_path)):
        raise ValueError("Metadata counts, sampling or CSV hash disagree with validated output")
    return {"sites": len(rows), "rotamer_scores": len(rows) * 12,
            "status": "complete_scored_output", "csv_sha256": sha(csv_path),
            "metadata_sha256": sha(metadata_path)}


def run(profile_path, work_dir, local_input=None, code_record=None):
    if work_dir.exists() or work_dir.is_symlink():
        raise FileExistsError(f"Refusing existing work directory: {work_dir}")
    work_dir.mkdir(parents=True, exist_ok=False)
    record = {
        "started_utc": datetime.now(timezone.utc).isoformat(), "status": "started",
        "stage": "preflight", "driver_sha256": sha(Path(__file__)),
        "scan_output_validation": {},
        "commands": [], "policy": "No historical prepared inputs, scans, PDF or web-cache files are read by this generation driver.",
    }
    record_path = work_dir / "run.json"

    def save():
        record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    save()
    try:
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        record["profile_sha256"] = sha(profile_path)
        if profile["source_url"] != PUBLIC_URL:
            raise ValueError("This driver only supports the explicit 2FG8 RCSB assembly source")
        config = profile["scan"]
        if config != {"chain": "A", "ncaa": "pazf", "seed": 42, "low_clash_threshold": 10.0,
                      "favorable_fraction": 0.5, "functional_residues": None, "n_rotamers": 12}:
            raise ValueError("Refusing a non-frozen scan configuration")
        record["stage"] = "code_validation"
        package_root = Path(ncaa_site_rec.__file__).resolve().parent
        installed_hashes = {"ncaa_site_rec/" + p.relative_to(package_root).as_posix(): sha(p)
                            for p in sorted(package_root.rglob("*.py"))}
        code = json.loads(code_record.read_text(encoding="utf-8")) if code_record else None
        if code is not None and installed_hashes != code["package_file_sha256"]:
            raise ValueError("Installed package sources do not match the recorded code snapshot")
        record.update({"code_source": code, "installed_package_file_sha256": installed_hashes,
                       "environment": {"python": platform.python_version(), "executable": sys.executable,
                           "prefix": sys.prefix, "base_prefix": sys.base_prefix, "package_root": str(package_root),
                           "packages": {p: version(p) for p in ["rana-ncaa-site-recommender", "numpy", "pandas", "biopython", "rdkit"]}}})
        record["stage"] = "source_acquisition"
        save()
        sources = work_dir / "sources"
        sources.mkdir()
        if local_input:
            source = sources / local_input.name
            source.write_bytes(local_input.read_bytes())
            source_record = None
            record["local_input_copy"] = {"from": str(local_input), "sha256": sha(source)}
        else:
            source = sources / "2FG8-assembly1.cif.gz"
            # No credentials, hidden cache, alternate URL or symmetry service.
            with urllib.request.urlopen(PUBLIC_URL, timeout=120) as response:
                payload = response.read()
                final_url = response.geturl()
            source.write_bytes(payload)
            retrieval = {"url": PUBLIC_URL, "final_url": final_url,
                         "retrieved_utc": datetime.now(timezone.utc).isoformat(),
                         "sha256": sha(source), "bytes": len(payload)}
            source_record = sources / "retrieval.json"
            source_record.write_text(json.dumps(retrieval, indent=2) + "\n", encoding="utf-8")
            record["retrieval"] = retrieval
        prepared = work_dir / "prepared"
        record["stage"] = "preparation"
        save()
        manifest = prepare_expanded_assembly(source, prepared, profile_path,
                                             source_record_path=source_record)
        record["preparation_manifest_sha256"] = sha(prepared / "preparation.json")
        save()
        if manifest["target_output_chain"] != config["chain"]:
            raise ValueError("Prepared target chain does not match frozen scan configuration")
        scans = work_dir / "scans"
        scans.mkdir()
        for case, filename in [("assembly", "assembly1_protein.pdb"), ("monomer", "target_monomer.pdb")]:
            record["stage"] = f"{case}_scan_command"
            save()
            command = [sys.executable, "-I", "-B", "-m", "ncaa_site_rec.cli", "rank",
                       "--pdb", str(prepared / filename), "--chain", manifest["target_output_chain"],
                       "--ncaa", config["ncaa"], "--seed", str(config["seed"]),
                       "--low-clash-threshold", str(config["low_clash_threshold"]),
                       "--favorable-fraction", str(config["favorable_fraction"]),
                       "--output", str(scans / f"{case}.csv")]
            print(f"Scanning {case} with frozen configuration", flush=True)
            started = datetime.now(timezone.utc).isoformat()
            completed = subprocess.run(command, cwd=work_dir, capture_output=True, text=True)
            (scans / f"{case}.stdout.txt").write_text(completed.stdout, encoding="utf-8")
            (scans / f"{case}.stderr.txt").write_text(completed.stderr, encoding="utf-8")
            record["commands"].append({"case": case, "argv": command, "started_utc": started,
                                       "finished_utc": datetime.now(timezone.utc).isoformat(),
                                       "returncode": completed.returncode})
            save()
            completed.check_returncode()
            record["stage"] = f"{case}_output_validation"
            save()
            record["scan_output_validation"][case] = validate_scan_output(
                scans / f"{case}.csv", profile, prepared / filename,
            )
            save()
        record["generated_files_sha256"] = {p.relative_to(work_dir).as_posix(): sha(p)
                                             for p in work_dir.rglob("*") if p.is_file() and p != record_path}
        record["status"] = "scans_completed_pending_separate_comparison"
        record["stage"] = "complete"
        record["finished_utc"] = datetime.now(timezone.utc).isoformat()
        save()
        print("Both scan outputs passed completeness checks; historical comparison and scientific validation remain separate.", flush=True)
    except Exception as error:
        record["status"] = "failed"
        record["failed_stage"] = record["stage"]
        record["error"] = f"{type(error).__name__}: {error}"
        record["finished_utc"] = datetime.now(timezone.utc).isoformat()
        try:
            save()
        except OSError as save_error:
            print(f"Could not save failure record: {save_error}", file=sys.stderr)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True, type=Path)
    parser.add_argument("--work-dir", required=True, type=Path)
    parser.add_argument("--input", type=Path, help="Optional local public structure input; otherwise download the pinned RCSB file")
    parser.add_argument("--code-record", type=Path, help="Optional source snapshot/commit hash manifest for installed-code verification")
    args = parser.parse_args()
    run(args.profile.resolve(), args.work_dir.resolve(),
        args.input.resolve() if args.input else None,
        args.code_record.resolve() if args.code_record else None)
