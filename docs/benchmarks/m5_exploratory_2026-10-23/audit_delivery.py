"""Audit local/fresh-clone dependencies and propose an explicit public file list.

This does not stage files or change ignore rules. Run from any directory:
python -B <this-script> --baseline <optional protection JSON>
Outputs are public_manifest.json and delivery_checks.json in this directory.
These are current audit reports, not replacements for frozen evidence.
"""

import argparse
import ast
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BENCH = HERE.parent
FROZEN = BENCH / "m5_frozen_pilot_2026-10-23"
EXPLORATORY = ["inspect_site_clashes.py", "inspect_t4l_scan.py", "inspect_topology_sensitivity.py",
               "run_t4l_scan.py", "test_rotamer_distances.py", "test_site_scan.py", "test_site_scoring.py"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def ignored(path):
    return subprocess.run(["git", "check-ignore", "-q", str(path)], cwd=ROOT).returncode == 0


def csv_rows(filename):
    with (FROZEN / filename).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def run(baseline):
    protected = {}
    if baseline:
        protected = json.loads(baseline.read_text(encoding="utf-8"))
        changed = [name for name, digest in protected.items() if not (ROOT / name).is_file() or sha(ROOT / name) != digest]
        assert not changed, f"Pre-existing files changed: {changed}"
    scripts = [{"file": name, "sha256": sha(ROOT / name),
                "status": git("status", "--short", "--", name)} for name in EXPLORATORY]
    assert all(r["status"].startswith("?? ") for r in scripts)
    assert git("diff", "--name-only") == "" and git("diff", "--cached", "--name-only") == ""
    assert git("branch", "--show-current") == "codex/m5-khoshnejad-hftl-computational-case"
    t4l, ferritin = csv_rows("t4l_stability_master.csv"), csv_rows("ferritin_conjugation_comparison.csv")
    presentations = csv_rows("observation_presentations.csv")
    assert len(t4l) == len({r["observation_id"] for r in t4l}) == 6
    assert len(presentations) == 9 and len({r["observation_id"] for r in presentations}) == 6
    assert len(ferritin) == 8
    assert all(r["insertion_code"] == "" for r in t4l + ferritin)
    assert all(r["n_exact"] == "" and r["n_reported"] == "N >= 3" for r in t4l)
    # Field-level scan/input dependencies remain locally verifiable and ignored.
    dependencies = {}
    for rows, prefixes in [(t4l, [""]), (ferritin, ["assembly_", "monomer_"])]:
        for row in rows:
            for prefix in prefixes:
                fields = [(prefix + "scan_source_file", prefix + ("scan_source_sha256" if not prefix else "scan_sha256")),
                          (prefix + ("structure_source_file" if not prefix else "structure_file"), prefix + ("structure_source_sha256" if not prefix else "structure_sha256")),
                          (prefix + ("scan_metadata_file" if not prefix else "metadata_file"), prefix + ("scan_metadata_sha256" if not prefix else "metadata_sha256"))]
                for path_field, hash_field in fields:
                    name, digest = row[path_field], row[hash_field]
                    assert sha(ROOT / name) == digest
                    dependencies[name] = {"sha256": digest, "ignored": ignored(ROOT / name),
                                          "fresh_clone": "absent; analysis uses curated CSV, rescan needs reconstruction"}
    structures = {}
    for name in dependencies:
        if name.endswith(".pdb"):
            codes = sorted({line[26:27].strip() for line in (ROOT / name).read_text().splitlines() if line.startswith(("ATOM  ", "HETATM"))})
            structures[name] = {"insertion_codes": codes}
            assert codes == [""]
    results = json.loads((HERE / "results/results.json").read_text(encoding="utf-8"))
    assert results["script_sha256"] == sha(HERE / "analyze.py")
    for name, digest in results["input_sha256"].items():
        assert sha(ROOT / name) == digest
    for name, digest in results["output_sha256"].items():
        assert sha(HERE / "results" / name) == digest
    assert len(results["t4l_results"]) == 8
    assert sum(len(r["leave_one_out"]) for r in results["t4l_results"]) == 44
    # Compare displayed coefficient cells to machine-readable full precision.
    display = [line for line in (HERE / "results/results.md").read_text(encoding="utf-8").splitlines() if line.startswith(("| Wilding_primary", "| six_site_"))]
    for line, record in zip(display, results["t4l_results"]):
        cells = [v.strip() for v in line.split("|")[1:-1]]
        assert cells[:3] == [record["cohort"], "`" + record["field"] + "`", str(record["n_sites"])]
        assert cells[3:5] == [f"{record[k]:.3f}" for k in ["spearman_rho", "kendall_tau_b"]]
        for cell, key in zip(cells[5:], ["spearman_rho", "kendall_tau_b"]):
            limits = record["leave_one_out_ranges"][key]
            assert cell == f"{limits['minimum']:.3f} to {limits['maximum']:.3f}"
    assert len(display) == 8
    review_path = HERE / "review/human_review_2026-10-24.json"
    human_review = json.loads(review_path.read_text(encoding="utf-8"))
    assert human_review["reviewer"] == "Yiwei Chen" and human_review["review_date"] == "2026-10-24"
    assert [(r["study_id"], r["literature_site"], r["observation_id"]) for r in human_review["decisions"]] == [
        (r["study_id"], r["literature_site"], r["observation_id"]) for r in t4l]
    assert all(r["decision"] == "pass" for r in human_review["decisions"])
    for name, digest in human_review["reviewed_snapshot_sha256"].items():
        assert sha(review_path.parent / name) == digest
    replay_path = HERE / "curated_reproduction_check_2026-10-24.json"
    replay = json.loads(replay_path.read_text(encoding="utf-8"))
    assert replay["status"] == "pass" and replay["denied_input_access_attempts"] == []
    assert replay["cohort_metric_results_equal"] == 8 and replay["leave_one_out_results_equal"] == 44
    assert replay["analysis_script_sha256"] == sha(HERE / "analyze.py")
    assert replay["verifier_sha256"] == sha(HERE / "verify_curated_reproduction.py")
    assert replay["original_results_sha256"] == sha(HERE / "results/results.json")
    syntax_files = sorted(HERE.glob("*.py"))
    for path in syntax_files:
        ast.parse(path.read_text(encoding="utf-8"))
    text_files = list(BENCH.glob("*.md")) + [p for p in HERE.rglob("*") if p.suffix in {".py", ".md", ".txt"}]
    whitespace = [(p.relative_to(ROOT).as_posix(), i) for p in text_files
                  for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1)
                  if line.rstrip() != line]
    assert not whitespace, whitespace
    git("diff", "--check")
    render_path = HERE / "render_checks.json"
    render = json.loads(render_path.read_text(encoding="utf-8")) if render_path.exists() else None
    if render:
        for record in render["documents"]:
            assert sha(ROOT / record["file"]) == record["sha256"]
    manifest_path = HERE / "public_manifest.json"
    checks_path = HERE / "delivery_checks.json"
    exclude = {manifest_path, checks_path, FROZEN / "PAUSE_AND_RESUME.md"}
    allowed_images = {HERE / "results/t4l_scatter.png", HERE / "results/ferritin_scatter.png"}
    proposed = []
    for path in sorted(BENCH.rglob("*")):
        if not path.is_file() or path in exclude or "__pycache__" in path.parts:
            continue
        assert path.suffix.lower() in {".md", ".csv", ".json", ".py", ".mjs", ".txt"} or path in allowed_images, path
        assert not ignored(path), path
        proposed.append({"file": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size,
                         "sha256": sha(path), "git_status": git("status", "--short", "--", str(path)),
                         "purpose": "original analysis scatter plot" if path in allowed_images else "curated data, provenance, documentation or reproducible helper"})
    (HERE / "public_manifest.json").write_text(json.dumps({
        "status": "proposed_only_not_staged_not_published", "files": proposed,
        "audit_reports_to_include_after_review": [p.relative_to(ROOT).as_posix() for p in [manifest_path, checks_path]],
        "excluded": ["paper PDFs and DOCX", "publisher native/crop/annotated rasters", "data/raw/**", "data/processed/**", "seven root exploratory scripts", "historical local pause handoff"],
        "self_hash_policy": "Manifest and changing audit report omitted from content hash list to avoid circular hashes."}, indent=2) + "\n", encoding="utf-8")
    links = []
    proposed_names = {r["file"] for r in proposed} | {p.relative_to(ROOT).as_posix() for p in [manifest_path, checks_path]}
    for path in sorted(BENCH.rglob("*.md")):
        for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if target.startswith(("https://", "http://", "#")):
                continue
            actual = (path.parent / unquote(target.split("#")[0]).strip("<>")).resolve()
            try:
                name = actual.relative_to(ROOT).as_posix()
            except ValueError:
                name = str(actual)
            # This report is created after the checks below; its own incoming
            # link is part of the atomic report being prepared, not a missing input.
            available = actual.is_file() or actual == checks_path
            is_ignored = ignored(actual) if available else False
            classification = ("local_only_ignored_regenerate_from_supplied_PDF" if is_ignored else
                              "proposed_benchmark_file" if name in proposed_names else
                              "existing_repository_file" if available else "missing")
            links.append({"document": path.relative_to(ROOT).as_posix(), "href": target,
                          "target": name, "exists_locally": available, "fresh_clone_classification": classification})
    missing = [r for r in links if not r["exists_locally"]]
    assert not missing, missing
    checks = {"git_head": git("rev-parse", "HEAD"), "branch": git("branch", "--show-current"),
              "tracked_diff_empty": True, "index_empty": True,
              "preexisting_files_checked": len(protected), "preexisting_files_changed": 0,
              "protected_exploratory_scripts": scripts,
              "rows": {"T4L": 6, "presentations": 9, "deduplicated_T4L_ids": 6, "ferritin": 8},
              "scan_and_structure_dependencies": dependencies, "structure_insertion_code_check": structures,
              "analysis_pairs_checked": 52, "coefficient_MD_JSON_consistency": "pass",
              "new_python_syntax_files_checked": len(syntax_files), "new_text_trailing_whitespace": "pass",
              "git_diff_check": "pass; new untracked text checked separately",
              "render_checks": {"report": "render_checks.json", "documents": len(render["documents"]),
                                "tables": sum(len(d["tables"]) for d in render["documents"])} if render else "not run",
              "local_links": links, "broken_local_links": missing,
              "fresh_clone_local_only_link_count": sum(r["fresh_clone_classification"].startswith("local_only") for r in links),
              "manifest_file_count": len(proposed), "publisher_images_or_full_papers_in_manifest": 0,
              "human_review_status": "all_six_pass_reported_by_maintainer_2026-10-24",
              "human_review_record": {"file": review_path.relative_to(ROOT).as_posix(),
                                      "sha256": sha(review_path), "reviewer": human_review["reviewer"],
                                      "date": human_review["review_date"],
                                      "scope": "maintainer image check of agent digitization; not blinded, second independent digitization or prediction-performance validation"},
              "curated_replay_record": {"file": replay_path.relative_to(ROOT).as_posix(), "sha256": sha(replay_path),
                                        "status": "pass; same-environment curated-table replay only"},
              "scientific_validation": "not established by human image review or these automatic checks",
              "full_pytest": "not rerun; no scientific implementation changes",
              "script_sha256": sha(Path(__file__))}
    checks_path.write_text(json.dumps(checks, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: checks[k] for k in ["preexisting_files_checked", "preexisting_files_changed", "manifest_file_count", "fresh_clone_local_only_link_count", "analysis_pairs_checked"]}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path)
    run(parser.parse_args().baseline)
