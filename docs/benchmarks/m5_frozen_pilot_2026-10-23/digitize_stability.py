"""Digitize published raster bars without changing RANA or using its scores.

Run with an analysis interpreter providing pypdf, pdfplumber, NumPy and Pillow.
The published PDFs are not distributed with this script. Output must be a new
directory; archived digitization materials are never overwritten.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
from importlib.metadata import version

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pdfplumber
from pypdf import PdfReader


CONFIG = {
    "Wilding2018": {
        "pdf": "Wilding_2018.pdf",
        "sha256": "c9042894c0b0080686f3be8debbe6ab73d611ec4911231ad766fc490d26e6f15",
        "page": 4, "printed_page": 513, "figure": "3", "panel": "A",
        "image_name": "Im4", "native_size": [969, 1669],
        "crop_box_xyxy": [0, 0, 969, 555],
        "axis_x_strip": [103, 113],
        "tick_seeds_y": [129, 163, 198, 232, 267, 302, 337, 371, 406, 441, 475],
        "tick_values": [0, -2, -4, -6, -8, -10, -12, -14, -16, -18, -20],
        "bar_search_y": [132, 340],
        "sites": ["K16", "S44", "N53", "L91", "K135"],
        "cap_y_seeds": [[209, 234], [160, 171], [175, 182], [284, 307], [190, 235]],
        "uncertainty_type": "SD", "digitization_bound_degC": 0.2,
    },
    "Wilkerson2020": {
        "pdf": "Wilkerson_2020.pdf",
        "sha256": "ce06cf47c48c00e8e4e81808e814c2928f71414f0c3fc734f6fb41e6788d6f16",
        "page": 4, "printed_page": 5120, "figure": "2", "panel": "whole figure",
        "image_name": "Im0", "native_size": [1000, 722],
        "crop_box_xyxy": [0, 0, 1000, 722],
        "axis_x_strip": [130, 141],
        "tick_seeds_y": [20, 141, 262, 383, 504, 625],
        "tick_values": [0, -2, -4, -6, -8, -10],
        "bar_search_y": [25, 610], "sites": ["H31"],
        "cap_y_seeds": [[429, 483]],
        "uncertainty_type": "SEM", "digitization_bound_degC": 0.1,
    },
}
def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def blue_mask(a: np.ndarray, red_max: int = 100) -> np.ndarray:
    """Fixed image segmentation; independent of RANA fields and outcomes."""
    return ((a[:, :, 2] > 150) & (a[:, :, 1] > 90)
            & (a[:, :, 0] < red_max) & ((a[:, :, 2] - a[:, :, 0]) > 90))


def peak_center(scores: np.ndarray, origin: int) -> float:
    selected = np.flatnonzero(scores >= 0.8 * np.max(scores))
    if not len(selected) or np.max(scores) < 3:
        raise ValueError("No reliable axis tick/error cap within the recorded ROI")
    return float(origin + (selected[0] + selected[-1]) / 2)


def detect_cap(a: np.ndarray, x: float, seed: int) -> tuple[float, list[int]]:
    x0, x1 = round(x) - 7, round(x) + 8
    y0, y1 = seed - 3, seed + 4
    dark = np.max(a[y0:y1, x0:x1, :], axis=2) < 120
    center = peak_center(dark.sum(axis=1), y0)
    return center, [x0, y0, x1, y1]


def digitize(source_dir: Path, output_dir: Path) -> dict:
    if output_dir.exists():
        raise FileExistsError(f"Choose a new output directory: {output_dir}")
    output_dir.mkdir(parents=True)
    result = {"method": "calibrated_native_raster_bar_and_error_cap_digitization",
              "coordinate_convention": "Native raster coordinates, origin at top left; integer indices are pixel centers; crop boxes use Pillow left/top/right/bottom exclusive bounds.",
              "script_sha256": sha256(Path(__file__)),
              "environment": {"python": platform.python_version(), "packages": {p: version(p) for p in ["pypdf", "pdfplumber", "numpy", "Pillow"]}},
              "figures": [], "measurements": []}
    for study_id, cfg in CONFIG.items():
        path = source_dir / cfg["pdf"]
        if sha256(path) != cfg["sha256"]:
            raise ValueError(f"Source digest differs from frozen inventory: {path}")
        page = PdfReader(path).pages[cfg["page"] - 1]
        image_file = next(im for im in page.images if Path(im.name).stem == cfg["image_name"])
        native = output_dir / f"{study_id}_native.png"
        native.write_bytes(image_file.data)
        image = Image.open(native).convert("RGB")
        assert list(image.size) == cfg["native_size"]
        a = np.asarray(image).astype(int)
        with pdfplumber.open(path) as pdf:
            p = pdf.pages[cfg["page"] - 1]
            box = next(im for im in p.images if im["name"] == cfg["image_name"])
            page_box = {k: box[k] for k in ["x0", "x1", "top", "bottom"]}
            page_size = [p.width, p.height]

        ticks = []
        x0, x1 = cfg["axis_x_strip"]
        for seed, value in zip(cfg["tick_seeds_y"], cfg["tick_values"]):
            y0, y1 = seed - 3, seed + 4
            dark = np.max(a[y0:y1, x0:x1], axis=2) < 160
            center = peak_center(dark.sum(axis=1), y0)
            ticks.append({"y_pixel": center, "value_degC": value,
                          "roi_xyxy": [x0, y0, x1, y1]})
        ys = np.array([t["y_pixel"] for t in ticks])
        values = np.array(cfg["tick_values"])
        slope, intercept = np.polyfit(ys, values, 1)
        endpoint_slope = (values[-1] - values[0]) / (ys[-1] - ys[0])
        endpoint_intercept = values[0] - endpoint_slope * ys[0]
        residual = float(np.max(np.abs(slope * ys + intercept - values)))
        assert residual < 0.07

        mask = blue_mask(a)
        y0, y1 = cfg["bar_search_y"]
        xs = np.flatnonzero(mask[y0:y1].sum(axis=0) > 15)
        groups = [g for g in np.split(xs, np.flatnonzero(np.diff(xs) > 1) + 1) if len(g) > 5]
        assert len(groups) == (7 if study_id == "Wilding2018" else 4)
        annotated = image.crop(tuple(cfg["crop_box_xyxy"]))
        draw = ImageDraw.Draw(annotated)
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 13)
        for t in ticks:
            draw.line([(x1 + 3, t["y_pixel"]), (image.width - 10, t["y_pixel"])], fill="#8b62c4", width=1)
        for i, site in enumerate(cfg["sites"]):
            g = groups[i]
            left, right = int(g[0]), int(g[-1])
            x = (left + right) / 2
            rows = np.flatnonzero(mask[y0:y1, left:right + 1].sum(axis=1) >= 0.5 * len(g)) + y0
            last_solid = int(rows[-1])
            # Median blue chroma avoids the central error stem. Integrate the
            # antialiased terminal edge rather than selecting one pixel by eye.
            cols = [j for j in range(left + 2, right - 1) if abs(j - x) > 3]
            chroma = np.median(np.maximum(a[:, cols, 2] - a[:, cols, 0], 0), axis=1)
            full = float(np.median(chroma[y0 + 5:min(last_solid - 5, y0 + 20)]))
            lo = last_solid - 4
            mean_y = float(lo - 0.5 + np.clip(chroma[lo:lo + 10] / full, 0, 1).sum())
            edge_method = "blue_chroma_fractional_edge"
            if study_id == "Wilkerson2020":
                # This figure has an explicit black bar outline. Its centerline
                # is the plotted endpoint, rather than the interior blue edge.
                strip = np.max(a[last_solid - 1:last_solid + 6, cols, :], axis=2) < 120
                mean_y = peak_center(strip.sum(axis=1), last_solid - 1)
                edge_method = "black_bar_outline_centerline"
            upper, upper_roi = detect_cap(a, x, cfg["cap_y_seeds"][i][0])
            lower, lower_roi = detect_cap(a, x, cfg["cap_y_seeds"][i][1])
            assert upper < mean_y < lower
            mean = float(slope * mean_y + intercept)
            error_up = abs(float(slope * (mean_y - upper)))
            error_down = abs(float(slope * (lower - mean_y)))
            error = abs(float(slope * (lower - upper) / 2))
            assert abs(error_up - error_down) < 0.2
            alternatives = []
            for threshold in [80, 140]:
                m = blue_mask(a, threshold)
                rr = np.flatnonzero(m[y0:y1, left:right + 1].sum(axis=1) >= 0.5 * len(g)) + y0
                alternatives.append(float(slope * (rr[-1] + 0.5) + intercept))
            # Compare endpoint-only calibration and fill-edge thresholds as
            # image-reading sensitivity checks, not experimental validation.
            alternatives.append(float(endpoint_slope * mean_y + endpoint_intercept))
            max_change = max(abs(v - mean) for v in alternatives)
            assert max_change <= cfg["digitization_bound_degC"]
            record = {"study_id": study_id, "literature_site": site,
                      "mean_y_pixel": mean_y, "mean_edge_method": edge_method,
                      "bar_x_extent_pixel": [left, right], "bar_center_x_pixel": x,
                      "error_upper_y_pixel": upper, "error_lower_y_pixel": lower,
                      "error_upper_cap_roi_xyxy": upper_roi, "error_lower_cap_roi_xyxy": lower_roi,
                      "unrounded_mean_degC": mean, "unrounded_error_halfspan_degC": error,
                      "unrounded_error_up_degC": error_up, "unrounded_error_down_degC": error_down,
                      "value": round(mean, 1), "uncertainty_value": round(error, 1),
                      "uncertainty_type": cfg["uncertainty_type"], "n_reported": "N >= 3",
                      "n_exact": None, "digitization_reading_bound_degC": cfg["digitization_bound_degC"],
                      "reading_bound_interpretation": "Conservative image-reading bound on mean and error length; not a confidence interval, SD, SEM, or biological uncertainty.",
                      "image_method_sensitivity_max_degC": max_change,
                      "reported_precision_decimals": 1}
            result["measurements"].append(record)
            for yy, color in [(mean_y, "#d50000"), (upper, "#087b39"), (lower, "#087b39")]:
                draw.line([(x - 12, yy), (x + 12, yy)], fill=color, width=2)
                draw.ellipse((x - 3, yy - 3, x + 3, yy + 3), outline=color, width=1)
            for roi in [upper_roi, lower_roi]:
                draw.rectangle(roi, outline="#087b39", width=1)
        crop_path = output_dir / f"{study_id}_crop.png"
        image.crop(tuple(cfg["crop_box_xyxy"])).save(crop_path)
        # Add a key outside the unchanged source plot, without covering labels.
        canvas = Image.new("RGB", (annotated.width, annotated.height + 46), "white")
        canvas.paste(annotated)
        d = ImageDraw.Draw(canvas)
        d.text((10, annotated.height + 5), "Red: measured mean endpoint. Green: error-cap ROI/center. Purple: calibrated major tick.", font=font, fill="black")
        d.text((10, annotated.height + 24), "Original native pixels; annotated source plot, not a new experiment. Unrounded coordinates are in calibration.json.", font=font, fill="black")
        annotated_path = output_dir / f"{study_id}_annotated.png"
        canvas.save(annotated_path)
        result["figures"].append({"study_id": study_id, "source_file": str(path), "source_sha256": cfg["sha256"],
                                  "pdf_page_1_based": cfg["page"], "printed_page": cfg["printed_page"], "figure": cfg["figure"], "panel": cfg["panel"],
                                  "embedded_image_name": cfg["image_name"], "native_size_pixels": cfg["native_size"],
                                  "pdf_page_size_points": page_size, "pdf_image_bbox_points_top_origin": page_box,
                                  "crop_box_native_pixels_xyxy": cfg["crop_box_xyxy"], "ticks": ticks,
                                  "calibration_equation": "delta_Tm_degC = slope * native_y_pixel + intercept",
                                  "slope": float(slope), "intercept": float(intercept), "max_tick_residual_degC": residual,
                                  "endpoint_only_slope": float(endpoint_slope), "endpoint_only_intercept": float(endpoint_intercept),
                                  "files": {p.name: sha256(p) for p in [native, crop_path, annotated_path]}})
    (output_dir / "calibration.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = digitize(args.sources_dir, args.output)
    print(json.dumps([{k: r[k] for k in ["study_id", "literature_site", "value", "uncertainty_value", "uncertainty_type", "digitization_reading_bound_degC"]} for r in data["measurements"]], indent=2))
