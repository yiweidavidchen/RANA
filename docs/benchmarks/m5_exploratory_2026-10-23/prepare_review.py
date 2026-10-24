"""Check frozen digitization and generate a pending human checklist.

Use the separate digitization Python environment (numpy, Pillow, pypdf,
pdfplumber). Run from any directory; output must be new. No PDF images are
copied to the documentation directory. No human approval is inferred.
"""

import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FROZEN = HERE.parent / "m5_frozen_pilot_2026-10-23"
IMAGE_DIR = ROOT / "data/processed/m5_frozen_pilot_2026-10-23/digitization_final"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(output):
    assert not output.exists(), "Preserve previous review records; choose a new output directory."
    calibration = json.loads((FROZEN / "digitization_calibration.json").read_text(encoding="utf-8"))
    assert sha(FROZEN / "digitize_stability.py") == calibration["script_sha256"]
    assert sha(FROZEN / "digitization_calibration.json") == sha(IMAGE_DIR / "calibration.json")
    spec = importlib.util.spec_from_file_location("frozen_digitization", FROZEN / "digitize_stability.py")
    digitization = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(digitization)
    with (FROZEN / "t4l_stability_master.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == len(calibration["measurements"]) == 6
    figures = {f["study_id"]: f for f in calibration["figures"]}
    hashes = {}
    lines = ["# Human digitization review checklist", "", "Status: **pending for all six rows**. Reviewer: ______. Review date: ______.", "",
             "Automated integrity checks and repeated checks by the same agent are not a second independent reader. A human must compare the original PDF, unannotated crop and overlay, verify identities and cap choices, and record any disagreement in a new revision record. Frozen means and errors are unchanged.", "",
             "Coordinates below are native pixels with top-left origin. Means/cap coordinates are rounded here to 0.01 pixel solely for navigation, not experimental precision; full coordinates and ROIs are in the frozen calibration JSON. Each marker location is (bar-center x, y). Upper cap means smaller y, not larger negative magnitude.", "",
             "| Site / study | Bar identity | x extent; center x | Mean edge y / method | Upper cap y | Lower cap y | Frozen ΔTm ± error (°C) | Human status |",
             "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    checks = []
    for measurement, row in zip(calibration["measurements"], rows):
        study, site = measurement["study_id"], measurement["literature_site"]
        assert (row["study_id"], row["literature_site"]) == (study, site)
        figure = figures[study]
        config = digitization.CONFIG[study]
        assert figure["source_sha256"] == config["sha256"] == row["source_sha256"]
        assert figure["crop_box_native_pixels_xyxy"] == config["crop_box_xyxy"]
        assert site in config["sites"] and int(row["source_pdf_page"]) == figure["pdf_page_1_based"]
        for field in ["value", "uncertainty_value"]:
            assert float(row[field]) == measurement[field]
        assert row["uncertainty_type"] == measurement["uncertainty_type"]
        assert row["n_reported"] == measurement["n_reported"] == "N >= 3" and row["n_exact"] == ""
        mean = figure["slope"] * measurement["mean_y_pixel"] + figure["intercept"]
        error = abs(figure["slope"]) * (measurement["error_lower_y_pixel"] - measurement["error_upper_y_pixel"]) / 2
        assert round(mean, 1) == float(row["value"])
        assert round(error, 1) == float(row["uncertainty_value"])
        for field in ["digitization_mean_reading_bound_degC", "digitization_error_reading_bound_degC"]:
            assert float(row[field]) == measurement["digitization_reading_bound_degC"]
        identity = "Figure 3A blue Unconjugated" if study == "Wilding2018" else "Figure 2 blue H31 only (reused sites excluded)"
        lines.append(f"| {site} / {study} | {identity} | {measurement['bar_x_extent_pixel']}; {measurement['bar_center_x_pixel']:.2f} | {measurement['mean_y_pixel']:.2f} / {measurement['mean_edge_method']} | {measurement['error_upper_y_pixel']:.2f} | {measurement['error_lower_y_pixel']:.2f} | {row['value']} ± {row['uncertainty_value']} {row['uncertainty_type']} | pending |")
        checks.append({"study_id": study, "literature_site": site, "automatic_check": "pass", "human_review": "pending"})
    for study, figure in figures.items():
        source = Path(figure["source_file"])
        assert sha(source) == figure["source_sha256"]
        hashes[str(source)] = sha(source)
        for filename, expected in figure["files"].items():
            assert sha(IMAGE_DIR / filename) == expected
            hashes[(IMAGE_DIR / filename).relative_to(ROOT).as_posix()] = expected
        lines += ["", f"## {study}: source and calibration", "",
                  f"PDF physical page {figure['pdf_page_1_based']}, printed page {figure['printed_page']}, Figure {figure['figure']} / {figure['panel']}. Source SHA-256 `{figure['source_sha256']}`. Crop box `{figure['crop_box_native_pixels_xyxy']}`.", "",
                  f"Conversion: ΔTm = ({figure['slope']:.12f}) × native y + ({figure['intercept']:.12f}) °C.", "",
                  "| Calibration tick ΔTm (°C) | Native y | Search ROI (x0,y0,x1,y1) |",
                  "| --- | --- | --- |"]
        lines += [f"| {t['value_degC']} | {t['y_pixel']} | `{t['roi_xyxy']}` |" for t in figure["ticks"]]
        base = "../../../../data/processed/m5_frozen_pilot_2026-10-23/digitization_final/"
        # This document is generated in a review/ subdirectory of HERE.
        lines += ["", f"[Native image]({base}{study}_native.png) · [Unannotated crop]({base}{study}_crop.png) · [Annotated means, caps and calibration]({base}{study}_annotated.png)", "",
                  "For each site in the table above, check its bar label/color, mean-edge rule, upper/lower cap center and search ROI, and all calibration ticks against these images. Wilding uses the integrated blue edge; H31 uses the black outline center. Confirm no PEG/Ins163/double/reused observation was substituted."]
    lines += ["", "## Sign-off requirements", "", "- [ ] Verify six identities, mean edges, both caps and calibration ticks against the source PDFs.",
              "- [ ] Retain Wilding SD, H31 SEM, N >= 3 and separate reading bounds; do not infer exact N.",
              "- [ ] Record reader identity/date and a per-site decision, including disagreements.",
              "- [ ] If a clear error is found, preserve this snapshot and append old/new values, reason and replacement provenance before any revised analysis.",
              "", "All boxes remain pending. Images are local review materials in ignored data/processed, not proposed publisher-image redistribution. Fresh-clone users must supply matching PDFs and regenerate them; see the benchmark reproduction guide."]
    output.mkdir(parents=True)
    (output / "human_review_checklist.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (output / "automatic_digitization_checks.json").write_text(json.dumps({
        "status": "automatic_integrity_checks_passed_not_independent_human_review",
        "script_sha256": sha(Path(__file__)), "frozen_calibration_sha256": sha(FROZEN / "digitization_calibration.json"),
        "digitization_script_sha256": calibration["script_sha256"],
        "verified_source_and_image_sha256": hashes, "rows": checks,
        "numeric_changes": False, "human_review_status": "pending"}, indent=2) + "\n", encoding="utf-8")
    print("Six records, source PDFs, script, calibration and six images verified; human review pending.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    prepare(parser.parse_args().output.resolve())
