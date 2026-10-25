"""Synthetic reliability checks; never download structures or execute scans."""
import ast
import csv
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from Bio.SeqUtils import seq3

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "docs/reproducibility"


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def driver():
    return load_script("reproduce_2fg8")


@pytest.fixture
def profile():
    return json.loads((ROOT / "configs/2fg8_assembly1.json").read_text(encoding="utf-8"))


def rows_for(driver, profile):
    rows = []
    for number, aa in enumerate(profile["sequence"], start=profile["author_residue_start"]):
        row = dict.fromkeys(driver.NUMERIC_FIELDS, "1.0")
        row.update(chain="A", residue_number=str(number), insertion_code="",
                   residue_name=seq3(aa).upper(), has_ca="True", status="scored",
                   n_rotamers="12", rotamer_scores=repr([1.0] * 12), reason="",
                   special_residue_flag="", candidate_tier="geometry_favorable",
                   ranking_reason="Synthetic fixture; no scientific calculation")
        rows.append(row)
    return rows


def mutate(rows, case):
    if case == "missing_row":
        rows.pop()
    elif case == "duplicate":
        rows[1] = rows[0].copy()
    elif case in {"failed", "skipped"}:
        rows[0]["status"] = case
    else:
        changes = {
            "wrong_chain": ("chain", "B"), "wrong_number": ("residue_number", "179"),
            "wrong_parent": ("residue_name", "ALA"), "insertion": ("insertion_code", "A"),
            "diagnostic": ("reason", "Unexpected scoring diagnostic"),
            "rotamer_count": ("n_rotamers", "11"),
            "rotamer_length": ("rotamer_scores", repr([1.0] * 11)),
            "rotamer_nan": ("rotamer_scores", "[NaN," + ",".join(["1.0"] * 11) + "]"),
            "rotamer_inf": ("rotamer_scores", "[1e309," + ",".join(["1.0"] * 11) + "]"),
            "scalar_nan": ("rsa", "NaN"), "scalar_inf": ("min_steric_score", "Inf"),
            "missing_numeric": ("sasa_abs", ""), "missing_ca": ("has_ca", "False"),
            "missing_tier": ("candidate_tier", ""), "missing_explanation": ("ranking_reason", ""),
        }
        field, value = changes[case]
        rows[0][field] = value


def write_scan(driver, profile, path, pdb, rows=None):
    if rows is None:
        rows = rows_for(driver, profile)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(driver.TEXT_FIELDS + driver.NUMERIC_FIELDS))
        writer.writeheader()
        writer.writerows(rows)
    config = {k: v for k, v in profile["scan"].items() if k not in {"chain", "n_rotamers"}}
    metadata = {"schema_version": "1.0", "tool": "RANA",
                "input": {"chain": "A", "pdb_sha256": driver.sha(pdb)},
                "configuration": config, "sampling": {"n_rotamers_observed": [12]},
                "results": {"n_residues": 174, "status_counts": {"scored": 174},
                            "tier_counts": {"geometry_favorable": 174}},
                "output": {"csv_sha256": driver.sha(path)}}
    path.with_suffix(".metadata.json").write_text(json.dumps(metadata), encoding="utf-8")


BAD_ROWS = ["missing_row", "duplicate", "wrong_chain", "wrong_number", "wrong_parent",
            "insertion", "failed", "skipped", "diagnostic", "rotamer_count", "rotamer_length",
            "rotamer_nan", "rotamer_inf", "scalar_nan", "scalar_inf", "missing_numeric",
            "missing_ca", "missing_tier", "missing_explanation"]


@pytest.mark.parametrize("case", BAD_ROWS)
def test_output_validator_rejects_bad_rows(driver, profile, tmp_path, case):
    pdb = tmp_path / "input.pdb"
    pdb.write_text("synthetic input", encoding="utf-8")
    rows = rows_for(driver, profile)
    mutate(rows, case)
    path = tmp_path / "scan.csv"
    write_scan(driver, profile, path, pdb, rows)
    with pytest.raises((ValueError, SyntaxError)):
        driver.validate_scan_output(path, profile, pdb)


@pytest.mark.parametrize("case", ["missing_csv", "missing_metadata", "bad_json", "metadata_hash",
                                  "metadata_counts", "metadata_config", "missing_field",
                                  "duplicate_header", "extra_cell", "truncated_cell"])
def test_output_validator_rejects_missing_or_malformed_files(driver, profile, tmp_path, case):
    pdb = tmp_path / "input.pdb"
    pdb.write_text("synthetic input", encoding="utf-8")
    path = tmp_path / "scan.csv"
    write_scan(driver, profile, path, pdb)
    sidecar = path.with_suffix(".metadata.json")
    if case == "missing_csv":
        path.unlink()
    elif case == "missing_metadata":
        sidecar.unlink()
    elif case == "bad_json":
        sidecar.write_text("not JSON", encoding="utf-8")
    elif case.startswith("metadata_"):
        data = json.loads(sidecar.read_text(encoding="utf-8"))
        if case == "metadata_hash":
            data["output"]["csv_sha256"] = "incorrect"
        elif case == "metadata_counts":
            data["results"]["status_counts"] = {"scored": 173, "failed": 1}
        else:
            data["configuration"]["seed"] = 0
        sidecar.write_text(json.dumps(data), encoding="utf-8")
    else:
        lines = path.read_text(encoding="utf-8").splitlines()
        if case == "missing_field":
            lines[0] = lines[0].replace("rsa,", "absent_rsa,")
        elif case == "duplicate_header":
            lines[0] = lines[0].replace("rsa,", "sasa_abs,")
        elif case == "extra_cell":
            lines[1] += ",extra"
        else:
            lines[1] = lines[1].rsplit(",", 1)[0]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises((ValueError, FileNotFoundError, csv.Error)):
        driver.validate_scan_output(path, profile, pdb)


@pytest.mark.parametrize("case", ["ok", "missing_csv", *BAD_ROWS])
def test_zero_exit_scan_is_not_enough(driver, profile, tmp_path, monkeypatch, case):
    profile_path = tmp_path / "profile.json"
    profile_path.write_text(json.dumps(profile), encoding="utf-8")
    source = tmp_path / "input.cif"
    source.write_text("synthetic; never parsed", encoding="utf-8")

    def prepare(source, output, *args, **kwargs):
        output.mkdir()
        for filename in ["preparation.json", "assembly1_protein.pdb", "target_monomer.pdb"]:
            (output / filename).write_text("synthetic", encoding="utf-8")
        return {"target_output_chain": "A"}

    def scan(command, **kwargs):
        output = Path(command[command.index("--output") + 1])
        pdb = Path(command[command.index("--pdb") + 1])
        rows = rows_for(driver, profile)
        if case not in {"ok", "missing_csv"}:
            mutate(rows, case)
        if case != "missing_csv":
            write_scan(driver, profile, output, pdb, rows)
        return subprocess.CompletedProcess(command, 0, "synthetic stdout", "")

    monkeypatch.setattr(driver, "prepare_expanded_assembly", prepare)
    monkeypatch.setattr(driver.subprocess, "run", scan)
    work = tmp_path / "run"
    if case == "ok":
        driver.run(profile_path, work, local_input=source)
    else:
        with pytest.raises((ValueError, SyntaxError)):
            driver.run(profile_path, work, local_input=source)
    record = json.loads((work / "run.json").read_text(encoding="utf-8"))
    if case == "ok":
        assert record["status"] == "scans_completed_pending_separate_comparison"
        assert set(record["scan_output_validation"]) == {"assembly", "monomer"}
    else:
        assert record["status"] == "failed"
        assert record["failed_stage"] == "assembly_output_validation"
        assert record["error"]
        assert record["commands"][0]["returncode"] == 0
        assert (work / "scans/assembly.stdout.txt").is_file()


def test_code_preflight_failure_has_journal(driver, profile, tmp_path):
    profile_path = tmp_path / "profile.json"
    profile_path.write_text(json.dumps(profile), encoding="utf-8")
    bad_code = tmp_path / "bad_code.json"
    bad_code.write_text('{"package_file_sha256":{}}', encoding="utf-8")
    with pytest.raises(ValueError, match="code snapshot"):
        driver.run(profile_path, tmp_path / "run", code_record=bad_code)
    record = json.loads((tmp_path / "run/run.json").read_text(encoding="utf-8"))
    assert record["failed_stage"] == "code_validation"


@pytest.mark.parametrize("optimized", [False, True], ids=["normal", "python-O"])
@pytest.mark.parametrize("case", ["ok", "existing_report", "status", "profile", "coordinates",
                                  "atom_identity", "occupancy", "scan_score", "tier", "rank",
                                  "rotamer", "both_nonfinite"])
def test_comparator_guards_in_real_interpreter(driver, profile, tmp_path, optimized, case):
    run = tmp_path / "run"
    (run / "prepared").mkdir(parents=True)
    (run / "scans").mkdir()
    profile_path = tmp_path / "profile.json"
    profile_path.write_text(json.dumps(profile), encoding="utf-8")
    (run / "run.json").write_text(json.dumps({
        "status": "failed" if case == "status" else "scans_completed_pending_separate_comparison",
        "profile_sha256": "incorrect" if case == "profile" else driver.sha(profile_path),
    }), encoding="utf-8")
    reference = tmp_path / "reference.pdb"
    pdb_text = "ATOM      1  CA  SER A   5       1.000   2.000   3.000  1.00 10.00           C  \nEND   \n"
    reference.write_text(pdb_text, encoding="utf-8")
    for filename in ["assembly1_protein.pdb", "target_monomer.pdb"]:
        text = pdb_text
        if case == "coordinates":
            text = text.replace("1.000", "2.000", 1)
        elif case == "atom_identity":
            text = text.replace("SER A   5", "SER A   6")
        elif case == "occupancy":
            text = text.replace("1.00 10.00", "0.50 10.00")
        (run / "prepared" / filename).write_text(text, encoding="utf-8")
    old = tmp_path / "reference.csv"
    base_rows = rows_for(driver, profile)
    if case == "both_nonfinite":
        base_rows[0]["sasa_abs"] = "NaN"
    write_scan(driver, profile, old, reference, base_rows)
    rows = [row.copy() for row in base_rows]
    if case in {"scan_score", "tier", "rank", "rotamer"}:
        field, value = {"scan_score": ("min_steric_score", "2"),
                        "tier": ("candidate_tier", "geometry_limited"),
                        "rank": ("steric_rank", "2"),
                        "rotamer": ("rotamer_scores", repr([2.0] * 12))}[case]
        rows[0][field] = value
    for name in ["assembly", "monomer"]:
        write_scan(driver, profile, run / "scans" / f"{name}.csv", reference, rows)
    output = tmp_path / "comparison.json"
    if case == "existing_report":
        output.write_text("preserve original", encoding="utf-8")
    command = [sys.executable, "-B", *(["-O"] if optimized else []), str(SCRIPTS / "compare_2fg8.py"),
               "--run-dir", str(run), "--profile", str(profile_path),
               "--reference-assembly", str(reference), "--reference-monomer", str(reference),
               "--reference-assembly-scan", str(old), "--reference-monomer-scan", str(old),
               "--output", str(output)]
    completed = subprocess.run(command, capture_output=True, text=True,
                               env={**os.environ, "PYTHONPATH": str(ROOT)})
    if case == "ok":
        assert completed.returncode == 0, completed.stderr
        assert json.loads(output.read_text(encoding="utf-8"))["status"] == "pass"
    else:
        assert completed.returncode != 0, completed.stdout
        if case == "existing_report":
            assert output.read_text(encoding="utf-8") == "preserve original"
        else:
            assert not output.exists()


def test_runtime_scripts_do_not_use_assert():
    for name in ["compare_2fg8.py", "reproduce_2fg8.py"]:
        tree = ast.parse((SCRIPTS / name).read_text(encoding="utf-8"))
        assert not any(isinstance(node, ast.Assert) for node in ast.walk(tree))


@pytest.mark.parametrize("optimized", [False, True], ids=["normal", "python-O"])
def test_driver_invalid_zero_exit_output_propagates_nonzero(tmp_path, optimized):
    # A child interpreter exercises unhandled failure/exit behavior. The fake
    # scanner returns zero without writing a CSV; no scientific CLI is launched.
    code = '''
import json, runpy, subprocess, sys
from pathlib import Path
helpers = runpy.run_path(sys.argv[1])
driver = helpers["load_script"]("reproduce_2fg8")
root = Path(sys.argv[2])
def prepare(source, output, *args, **kwargs):
    output.mkdir()
    for filename in ["preparation.json", "assembly1_protein.pdb", "target_monomer.pdb"]:
        (output / filename).write_text("synthetic", encoding="utf-8")
    return {"target_output_chain": "A"}
driver.prepare_expanded_assembly = prepare
driver.subprocess.run = lambda command, **kwargs: subprocess.CompletedProcess(command, 0, "synthetic", "")
source = root / "input.cif"
source.write_text("synthetic; never parsed", encoding="utf-8")
driver.run(Path(sys.argv[3]), root / "run", local_input=source)
'''
    completed = subprocess.run(
        [sys.executable, "-B", *(["-O"] if optimized else []), "-c", code,
         str(Path(__file__)), str(tmp_path), str(ROOT / "configs/2fg8_assembly1.json")],
        capture_output=True, text=True, env={**os.environ, "PYTHONPATH": str(ROOT)},
    )
    assert completed.returncode != 0
    assert "Missing scan CSV" in completed.stderr
    record = json.loads((tmp_path / "run/run.json").read_text(encoding="utf-8"))
    assert record["failed_stage"] == "assembly_output_validation"
    assert record["commands"][0]["returncode"] == 0
