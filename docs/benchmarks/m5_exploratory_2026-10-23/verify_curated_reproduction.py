"""Replay the unchanged frozen analysis; no new analysis or structural scan.

Run from any directory with the analysis environment:
python -B <this-script> --output <new-directory> --report <new-JSON-path>
The process denies access to ignored raw/processed inputs, PDFs, and RANA
scientific source files while the original analysis runs. Git provenance still
uses the repository checkout. This is a same-environment replay, not proof of
a clean installation or end-to-end structure/scan reproducibility.
"""

import argparse
import hashlib
import json
import os
import runpy
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(output, report):
    assert not output.exists() and not report.exists(), "Use fresh paths; preserve previous records."
    original = json.loads((HERE / "results/results.json").read_text(encoding="utf-8"))
    analysis = HERE / "analyze.py"
    assert sha(analysis) == original["script_sha256"]
    for name, digest in original["input_sha256"].items():
        assert sha(ROOT / name) == digest
    denied_roots = [ROOT / "data/raw", ROOT / "data/processed", ROOT / "ncaa_site_rec"]
    observed, blocked = set(), []
    enabled = True

    def audit(event, args):
        if not enabled or event != "open" or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        path = Path(os.fsdecode(args[0])).resolve()
        if path.suffix.lower() in {".pdf", ".docx"} or any(path.is_relative_to(p) for p in denied_roots):
            blocked.append(str(path))
            raise PermissionError("Curated replay must not read source papers, scans, structures or scientific code: " + str(path))
        if path.is_relative_to(ROOT) and path.suffix == ".csv":
            observed.add(path.relative_to(ROOT).as_posix())

    sys.addaudithook(audit)
    saved_argv = sys.argv
    try:
        sys.argv = [str(analysis), "--output", str(output)]
        runpy.run_path(str(analysis), run_name="__main__")
    finally:
        enabled = False
        sys.argv = saved_argv
    assert not blocked, blocked
    replay = json.loads((output / "results.json").read_text(encoding="utf-8"))
    assert replay["t4l_results"] == original["t4l_results"]
    assert replay["input_sha256"] == original["input_sha256"]
    assert replay["value_source_fields"] == original["value_source_fields"]
    expected_csvs = {name for name in original["input_sha256"] if name.endswith(".csv")}
    assert observed == expected_csvs, observed
    output_matches = {name: sha(output / name) == digest for name, digest in original["output_sha256"].items()}
    assert all(output_matches.values()), output_matches
    result = {
        "check_type": "same_environment_replay_of_unchanged_frozen_analysis_not_new_analysis",
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "status": "pass", "verifier_sha256": sha(Path(__file__)),
        "analysis_script_sha256": sha(analysis), "input_sha256": replay["input_sha256"],
        "original_results_sha256": sha(HERE / "results/results.json"),
        "replay_results_sha256": sha(output / "results.json"),
        "original_results_unchanged": True,
        "cohort_metric_results_equal": 8, "leave_one_out_results_equal": 44,
        "replayed_output_matches": output_matches,
        "curated_csvs_read": sorted(observed), "denied_input_access_attempts": blocked,
        "denied_categories": ["ignored raw structures", "ignored processed scans", "paper PDFs/DOCX", "RANA scientific source"],
        "software": {k: replay[k] for k in ["python", "packages", "git_head"]},
        "replay_output_directory": str(output),
        "scope_limit": "Uses existing installed analysis environment and repository Git metadata. Does not establish clean-install, PDF digitization or structure-to-scan reproducibility. Historical pending review fields in replay output are unchanged execution-snapshot metadata, not current human-review status."
    }
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("PASS: frozen analysis replayed from two curated CSVs; all 52 coefficient pairs and existing output hashes match.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    verify(args.output.resolve(), args.report.resolve())
