"""Prepare and scan only the reviewed protein-only 2O9P A-chain profile."""
import argparse
import json
import math
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

import numpy as np
import pandas as pd
from Bio.Data.PDBData import protein_letters_3to1

import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
KEYS = ["chain", "residue_number", "insertion_code"]
TIERS = {"geometry_favorable", "geometry_limited", "geometry_unfavorable"}
FIELDS = ["sasa_abs", "rsa", "ca_neighbors_8a", "min_steric_score", "mean_steric_score",
          "median_steric_score", "low_clash_fraction", "rsa_rank", "steric_rank", "rotamer_robustness_rank",
          "best_chi1", "best_chi2"]
REVISION = "documentation-compatibility-2026-10-27"
APPROVAL_FILE = "tool_revision_2026-10-27.json"
FROZEN_MAPPING_FILE = "site_mapping_frozen_2026-10-25.md"
TEXT_HASH_ALGORITHM = "sha256-utf8-crlf-to-lf-v1"
FRACTION_ATOL = 1e-12
SCORE_ATOL = 1e-10


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_hash(path, expected):
    require(sha(path) == expected, f"SHA-256 mismatch: {path}")


def lf_bytes(data):
    """Validate UTF-8 and replace CRLF only; preserve all other bytes."""
    data.decode("utf-8")
    return data.replace(b"\r\n", b"\n")


def text_sha(path):
    return hashlib.sha256(lf_bytes(path.read_bytes())).hexdigest()


def check_text_hash(path, expected):
    require(text_sha(path) == expected, f"LF-content SHA-256 mismatch: {path}")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def approved_tools():
    """Accidental-change checks, not a tamper-resistant trust mechanism."""
    approval = read_json(HERE / APPROVAL_FILE)
    require(approval["revision"] == REVISION and approval["text_hash_algorithm"] == TEXT_HASH_ALGORITHM,
            "Unsupported tool revision/hash policy")
    require(set(approval["current_tools_lf_sha256"]) == {"run_case.py", "curate_case.py"}, "Incomplete tool approval")
    for name, digest in approval["current_tools_lf_sha256"].items():
        check_text_hash(HERE / name, digest)
    check_text_hash(HERE / "execution_plan_2026-10-25.json", approval["historical_plan_lf_sha256"])
    return approval


def approved_plan():
    approval = approved_tools()
    plan = read_json(HERE / "execution_plan_2026-10-25.json")
    require(plan["scientific_base_commit"] == approval["scientific_base_commit"], "Scientific base differs from approval")
    for name, digest in plan["dependencies_sha256"].items():
        if name != "run_case.py":
            # Markdown is provenance only; verify the exact approved document
            # separately from the maintained explanation. JSON checks stay intact.
            dependency = FROZEN_MAPPING_FILE if name == "site_mapping.md" else name
            check_text_hash(HERE / dependency, digest)
    return plan, approval


def approved_science(plan, approval):
    """Obtain approved source bytes from the pre-scan Git version, not HEAD."""
    base = plan["scientific_base_commit"]
    paths = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", base, "--", "ncaa_site_rec"], cwd=ROOT, text=True).splitlines()
    sources = {p: lf_bytes(subprocess.check_output(["git", "show", f"{base}:{p}"], cwd=ROOT))
               for p in paths if p.endswith(".py")}
    require(bool(sources), "Missing approved scientific source")
    require({p: hashlib.sha256(b).hexdigest() for p, b in sources.items()} == approval["scientific_source_lf_sha256"],
            "Approved Git content differs from revision source inventory")
    return sources


def verify_execution_sources(run_dir, record, plan, approval):
    """Bind raw historical evidence to approved content; never rewrite it."""
    require(all(k in record for k in ["scientific_package_sha256", "git_commit", "wrapper_sha256", "execution_plan_sha256",
                                      "source_sha256", "configuration", "source_provenance"]), "Missing execution provenance fields")
    require(record["source_sha256"] == plan["source_sha256"] and record["configuration"] == plan["cli_configuration"]
            and record["source_provenance"] == plan["source_provenance"], "Execution provenance differs from frozen plan")
    sources = approved_science(plan, approval)
    recorded = record.get("scientific_package_sha256")
    require(isinstance(recorded, dict) and set(recorded) == set(sources), "Missing/incomplete scientific source record")
    for name, data in sources.items():
        allowed = {hashlib.sha256(data).hexdigest(), hashlib.sha256(data.replace(b"\n", b"\r\n")).hexdigest()}
        require(recorded[name] in allowed, f"Unapproved recorded scientific source: {name}")
    # HEAD may include later documentation commits, but its scientific content must agree.
    commit = record["git_commit"]
    recorded_paths = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", commit, "--", "ncaa_site_rec"], cwd=ROOT, text=True).splitlines()
    require({p for p in recorded_paths if p.endswith(".py")} == set(sources), "Recorded commit source set mismatch")
    for name, data in sources.items():
        require(lf_bytes(subprocess.check_output(["git", "show", f"{commit}:{name}"], cwd=ROOT)) == data,
                f"Recorded commit scientific content mismatch: {name}")
    archived = run_dir / "executed_sources/run_case.py"
    check_hash(archived, record["wrapper_sha256"])
    if "tool_revision" not in record:
        require(record["wrapper_sha256"] == plan["dependencies_sha256"]["run_case.py"], "Historical runner differs from frozen approval")
    else:
        require(all(k in record for k in ["text_hash_algorithm", "wrapper_lf_sha256", "scientific_package_lf_sha256"]),
                "Missing revised execution provenance fields")
        if record["tool_revision"] == REVISION:
            executed_approval = approval
        else:
            previous = approval.get("previous_tool_approvals", {}).get(record["tool_revision"])
            require(previous is not None, "Unknown executed tool revision")
            check_text_hash(HERE / previous["file"], previous["lf_sha256"])
            executed_approval = read_json(HERE / previous["file"])
            require(executed_approval["revision"] == record["tool_revision"]
                    and executed_approval["scientific_base_commit"] == plan["scientific_base_commit"]
                    and executed_approval["scientific_source_lf_sha256"] == approval["scientific_source_lf_sha256"],
                    "Previous executed approval mismatch")
        require(record["text_hash_algorithm"] == TEXT_HASH_ALGORITHM, "Executed hash policy mismatch")
        require(record["wrapper_lf_sha256"] == executed_approval["current_tools_lf_sha256"]["run_case.py"], "Unapproved revised runner")
        check_text_hash(archived, record["wrapper_lf_sha256"])
        require(record["scientific_package_lf_sha256"] == approval["scientific_source_lf_sha256"], "Scientific LF-content record mismatch")
    archived_plan = run_dir / "executed_sources/execution_plan_2026-10-25.json"
    check_hash(archived_plan, record["execution_plan_sha256"])
    check_text_hash(archived_plan, approval["historical_plan_lf_sha256"])


def protein_lines(path):
    """Select the explicit heavy-atom profile without rewriting ATOM records."""
    lines = path.read_text(encoding="ascii").splitlines()
    require(sum(line.startswith("MODEL ") for line in lines) <= 1, "Multiple source models")
    return [line for line in lines if line.startswith("ATOM  ") and line[21] == "A"
            and line[17:20] in protein_letters_3to1 and line[76:78].strip().upper() not in {"H", "D"}]


def identities(lines):
    atoms, residues = set(), {}
    for line in lines:
        key = (line[21], int(line[22:26]), line[26].strip())
        atom = (*key, line[17:20], line[12:16].strip(), line[16].strip(), line[76:78].strip())
        require(atom not in atoms, f"Duplicate atom identity: {atom}")
        require(np.isfinite([float(line[30:38]), float(line[38:46]), float(line[46:54])]).all(), "Nonfinite input coordinates")
        require(key not in residues or residues[key] == line[17:20], "Conflicting input parents")
        atoms.add(atom)
        residues[key] = line[17:20]
    require(bool(atoms), "No target protein atoms")
    return atoms, residues


def prepare(source, output):
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    lines = protein_lines(source)
    atoms, residues = identities(lines)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="ascii", newline="\n") as handle:
        handle.write("MODEL        1\n" + "\n".join(lines) + "\nTER\nENDMDL\nEND\n")
    copied = protein_lines(output)
    require(copied == lines and identities(copied) == (atoms, residues), "Prepared atom records changed")
    return {"prepared_sha256": sha(output), "protein_heavy_atoms": len(atoms), "residue_count": len(residues),
            "coordinate_change_A": 0.0, "policy": "Exact original A-chain heavy ATOM records; one MODEL; no HETATM or H/D; no renumbering"}, residues


def validate_output(path, expected, configuration, prepared_sha256, git_commit):
    """An exit code alone is insufficient; retain diagnosed unscored rows."""
    frame = pd.read_csv(path, keep_default_na=False, float_precision="round_trip", encoding="utf-8")
    required = [*KEYS, "residue_name", "status", "reason", "n_rotamers", "rotamer_scores", "candidate_tier",
                "special_residue_flag", "ranking_reason", *FIELDS]
    require(set(required) <= set(frame.columns), "Missing scan columns")
    require(pd.api.types.is_integer_dtype(frame.residue_number), "Residue number must be an integer")
    require(not frame.duplicated(KEYS).any(), "Duplicate scan identity")
    actual = {tuple(row[k] for k in KEYS): row["residue_name"] for row in frame.to_dict("records")}
    require(actual == expected, "Scan identity/parent set differs from prepared profile")
    require(frame.status.isin(["scored", "failed", "skipped"]).all(), "Invalid scan status")
    for row in frame.to_dict("records"):
        if row["status"] != "scored":
            require(bool(str(row["reason"]).strip()), "Unscored row lacks diagnostic")
            require(row["candidate_tier"] == "not_evaluated", "Unscored row has evaluated tier")
            continue
        require(row["candidate_tier"] in TIERS, "Invalid scored tier")
        require(not row["reason"], "Scored row has abnormal diagnostic")
        require(all(isinstance(row[k], str) for k in ["chain", "insertion_code", "residue_name", "status", "reason", "special_residue_flag", "ranking_reason"]), "Invalid text field type")
        require(row["n_rotamers"] == 12 and not isinstance(row["n_rotamers"], bool)
                and all(isinstance(row[k], (float, int)) and not isinstance(row[k], bool) and math.isfinite(row[k]) for k in FIELDS),
                "Nonfinite/missing/nonnumeric scores or incorrect rotamer count")
        require(all(float(row[k]).is_integer() for k in ["ca_neighbors_8a", "rsa_rank", "steric_rank", "rotamer_robustness_rank"]), "Noninteger count/rank")
        scores = json.loads(row["rotamer_scores"])
        require(isinstance(scores, list) and len(scores) == 12 and all(isinstance(v, (float, int)) and not isinstance(v, bool) and math.isfinite(v) for v in scores), "Invalid rotamer scores")
        require(math.isclose(min(scores), row["min_steric_score"], rel_tol=1e-12, abs_tol=SCORE_ATOL), "Minimum score disagrees with rotamers")
        for field, value in [("mean_steric_score", np.mean(scores)), ("median_steric_score", np.median(scores))]:
            require(math.isclose(float(value), row[field], rel_tol=1e-12, abs_tol=SCORE_ATOL), f"{field} disagrees with rotamers")
        fraction = sum(v <= configuration["low_clash_threshold"] for v in scores) / 12
        require(math.isclose(fraction, row["low_clash_fraction"], rel_tol=0, abs_tol=FRACTION_ATOL), "Fraction disagrees with rotamers")
    metadata_path = path.with_suffix(".metadata.json")
    metadata = read_json(metadata_path)
    require(metadata["output"]["csv_sha256"] == sha(path), "Sidecar CSV hash mismatch")
    require(metadata["input"]["pdb_sha256"] == prepared_sha256 and metadata["input"]["chain"] == "A", "Sidecar input mismatch")
    require(metadata["configuration"] == configuration, "Sidecar configuration mismatch")
    require(metadata["software"]["git_commit"] == git_commit, "Sidecar code commit mismatch")
    counts = {str(k): int(v) for k, v in frame.status.value_counts().items()}
    require(metadata["results"]["n_residues"] == len(frame) and metadata["results"]["status_counts"] == counts, "Sidecar status counts mismatch")
    tiers = {str(k): int(v) for k, v in frame.candidate_tier.value_counts().items()}
    require(metadata["results"]["tier_counts"] == tiers, "Sidecar tier counts mismatch")
    return {"rows": len(frame), "status_counts": counts, "tier_counts": tiers, "csv_sha256": sha(path),
            "metadata_sha256": sha(metadata_path), "score_atol": SCORE_ATOL, "fraction_atol": FRACTION_ATOL}


def verify_source(base):
    """Verify the scientific Python source against the accepted merged code."""
    expected = set(subprocess.check_output(["git", "ls-tree", "-r", "--name-only", base, "--", "ncaa_site_rec"], cwd=ROOT, text=True).splitlines())
    expected = {p for p in expected if p.endswith(".py")}
    actual = {p.relative_to(ROOT).as_posix() for p in (ROOT / "ncaa_site_rec").rglob("*.py")}
    require(actual == expected and bool(actual), "Scientific source set changed")
    for name in sorted(actual):
        original = subprocess.check_output(["git", "show", f"{base}:{name}"], cwd=ROOT)
        require((ROOT / name).read_bytes().replace(b"\r\n", b"\n") == original.replace(b"\r\n", b"\n"), f"Scientific source changed: {name}")
    import ncaa_site_rec
    require(Path(ncaa_site_rec.__file__).resolve().parent == ROOT / "ncaa_site_rec", "Use scientific package from this checkout")
    return {p: sha(ROOT / p) for p in sorted(actual)}


def run(source, output):
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    plan_path = HERE / "execution_plan_2026-10-25.json"
    plan, approval = approved_plan()
    approved_science(plan, approval)
    check_hash(source, plan["source_sha256"])
    package_hashes = verify_source(plan["scientific_base_commit"])
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    output.mkdir(parents=True, exist_ok=False)
    record = {"started_utc": datetime.now(timezone.utc).isoformat(), "status": "started", "stage": "source_copy",
              "git_commit": head, "execution_plan_sha256": sha(plan_path), "wrapper_sha256": sha(Path(__file__)),
              "tool_revision": REVISION, "text_hash_algorithm": TEXT_HASH_ALGORITHM,
              "wrapper_lf_sha256": text_sha(Path(__file__)),
              "scientific_package_lf_sha256": approval["scientific_source_lf_sha256"],
              "scientific_package_sha256": package_hashes, "source_sha256": sha(source),
              "source_provenance": plan["source_provenance"], "configuration": plan["cli_configuration"],
              "environment": {"python": platform.python_version(), "platform": platform.platform(), "executable": sys.executable,
                              "packages": {p: version(p) for p in ["numpy", "pandas", "biopython", "rdkit"]}}}
    def save():
        (output / "run.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    save()
    try:
        snapshot = output / "executed_sources"
        snapshot.mkdir()
        for p in [Path(__file__), plan_path]:
            shutil.copy2(p, snapshot / p.name)
        shutil.copy2(source, output / "2O9P_original.pdb")
        check_hash(output / "2O9P_original.pdb", record["source_sha256"])
        record["stage"] = "preparation"
        save()
        info, expected = prepare(output / "2O9P_original.pdb", output / "protein_A.pdb")
        authority = read_json(HERE / "candidate_audit.json")["structures"]["2O9P"]["observed_residue_identities"]
        require(expected == {(r["chain"], r["residue_number"], r["insertion_code"]): r["residue_name"] for r in authority}, "Prepared identities differ from audit")
        require(len(expected) == 445 and info["protein_heavy_atoms"] == 3626, "Prepared profile count mismatch")
        for annotation in plan["functional_annotations"]:
            require(expected[tuple(annotation[k] for k in KEYS)] == annotation["residue_name"], "Functional annotation parent mismatch")
        record["preparation"] = info
        cfg = plan["cli_configuration"]
        command = [sys.executable, "-I", "-B", "-m", "ncaa_site_rec.cli", "rank", "--pdb", str(output / "protein_A.pdb"),
                   "--chain", "A", "--ncaa", "pazf", "--seed", str(cfg["seed"]), "--low-clash-threshold", str(cfg["low_clash_threshold"]),
                   "--favorable-fraction", str(cfg["favorable_fraction"]), "--output", str(output / "ranked.csv")]
        record.update(stage="scanning", command=command, scan_started_utc=datetime.now(timezone.utc).isoformat())
        save()
        with (output / "stdout.log").open("x", encoding="utf-8") as stdout, (output / "stderr.log").open("x", encoding="utf-8") as stderr:
            result = subprocess.run(command, cwd=ROOT, stdout=stdout, stderr=stderr)
        record.update(returncode=result.returncode, scan_finished_utc=datetime.now(timezone.utc).isoformat(), stage="output_validation")
        save()
        require(result.returncode == 0, "CLI failed; diagnostic artifacts retained")
        record["output_validation"] = validate_output(output / "ranked.csv", expected, cfg, info["prepared_sha256"], head)
        check_hash(output / "protein_A.pdb", info["prepared_sha256"])
        check_hash(output / "2O9P_original.pdb", record["source_sha256"])
        require(sha(Path(__file__)) == record["wrapper_sha256"] and sha(plan_path) == record["execution_plan_sha256"], "Execution source changed during scan")
        require(verify_source(plan["scientific_base_commit"]) == package_hashes, "Scientific source changed during scan")
        verify_execution_sources(output, record, plan, approval)
        record.update(status="scan_completed" if record["output_validation"]["status_counts"] == {"scored":445} else "scan_completed_with_diagnostics",
                      stage="complete", finished_utc=datetime.now(timezone.utc).isoformat())
        save()
    except Exception as error:
        record.update(status="failed", error=f"{type(error).__name__}: {error}", finished_utc=datetime.now(timezone.utc).isoformat())
        save()
        raise
    print(json.dumps({k: record[k] for k in ["status", "git_commit", "preparation", "output_validation"]}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-pdb", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    run(args.source_pdb.resolve(), args.output_dir.resolve())
