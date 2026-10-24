# Human digitization review checklist

Status: **pending for all six rows**. Reviewer: ______. Review date: ______.

Automated integrity checks and repeated checks by the same agent are not a second independent reader. A human must compare the original PDF, unannotated crop and overlay, verify identities and cap choices, and record any disagreement in a new revision record. Frozen means and errors are unchanged.

Coordinates below are native pixels with top-left origin. Means/cap coordinates are rounded here to 0.01 pixel solely for navigation, not experimental precision; full coordinates and ROIs are in the frozen calibration JSON. Each marker location is (bar-center x, y). Upper cap means smaller y, not larger negative magnitude.

| Site / study | Bar identity | x extent; center x | Mean edge y / method | Upper cap y | Lower cap y | Frozen ΔTm ± error (°C) | Human status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| K16 / Wilding2018 | Figure 3A blue Unconjugated | [131, 150]; 140.50 | 221.29 / blue_chroma_fractional_edge | 208.50 | 235.00 | -5.4 ± 0.8 SD | pending |
| S44 / Wilding2018 | Figure 3A blue Unconjugated | [253, 272]; 262.50 | 164.98 / blue_chroma_fractional_edge | 159.50 | 171.50 | -2.1 ± 0.3 SD | pending |
| N53 / Wilding2018 | Figure 3A blue Unconjugated | [374, 393]; 383.50 | 179.18 / blue_chroma_fractional_edge | 176.00 | 183.00 | -2.9 ± 0.2 SD | pending |
| L91 / Wilding2018 | Figure 3A blue Unconjugated | [496, 515]; 505.50 | 295.18 / blue_chroma_fractional_edge | 283.50 | 307.00 | -9.6 ± 0.7 SD | pending |
| K135 / Wilding2018 | Figure 3A blue Unconjugated | [617, 636]; 626.50 | 211.36 / blue_chroma_fractional_edge | 189.00 | 235.00 | -4.8 ± 1.3 SD | pending |
| H31 / Wilkerson2020 | Figure 2 blue H31 only (reused sites excluded) | [166, 284]; 225.00 | 455.50 / black_bar_outline_centerline | 428.00 | 482.50 | -7.2 ± 0.5 SEM | pending |

## Wilding2018: source and calibration

PDF physical page 4, printed page 513, Figure 3 / A. Source SHA-256 `c9042894c0b0080686f3be8debbe6ab73d611ec4911231ad766fc490d26e6f15`. Crop box `[0, 0, 969, 555]`.

Conversion: ΔTm = (-0.057689220016) × native y + (7.398544309346) °C.

| Calibration tick ΔTm (°C) | Native y | Search ROI (x0,y0,x1,y1) |
| --- | --- | --- |
| 0 | 128.0 | `[103, 126, 113, 133]` |
| -2 | 163.0 | `[103, 160, 113, 167]` |
| -4 | 197.5 | `[103, 195, 113, 202]` |
| -6 | 232.5 | `[103, 229, 113, 236]` |
| -8 | 267.0 | `[103, 264, 113, 271]` |
| -10 | 302.0 | `[103, 299, 113, 306]` |
| -12 | 335.5 | `[103, 334, 113, 341]` |
| -14 | 371.0 | `[103, 368, 113, 375]` |
| -16 | 406.0 | `[103, 403, 113, 410]` |
| -18 | 440.5 | `[103, 438, 113, 445]` |
| -20 | 474.5 | `[103, 472, 113, 479]` |

[Native image](../../../../data/processed/m5_frozen_pilot_2026-10-23/digitization_final/Wilding2018_native.png) · [Unannotated crop](../../../../data/processed/m5_frozen_pilot_2026-10-23/digitization_final/Wilding2018_crop.png) · [Annotated means, caps and calibration](../../../../data/processed/m5_frozen_pilot_2026-10-23/digitization_final/Wilding2018_annotated.png)

For each site in the table above, check its bar label/color, mean-edge rule, upper/lower cap center and search ROI, and all calibration ticks against these images. Wilding uses the integrated blue edge; H31 uses the black outline center. Confirm no PEG/Ins163/double/reused observation was substituted.

## Wilkerson2020: source and calibration

PDF physical page 4, printed page 5120, Figure 2 / whole figure. Source SHA-256 `ce06cf47c48c00e8e4e81808e814c2928f71414f0c3fc734f6fb41e6788d6f16`. Crop box `[0, 0, 1000, 722]`.

Conversion: ΔTm = (-0.016528925620) × native y + (0.330578512397) °C.

| Calibration tick ΔTm (°C) | Native y | Search ROI (x0,y0,x1,y1) |
| --- | --- | --- |
| 0 | 20.0 | `[130, 17, 141, 24]` |
| -2 | 141.0 | `[130, 138, 141, 145]` |
| -4 | 262.0 | `[130, 259, 141, 266]` |
| -6 | 383.0 | `[130, 380, 141, 387]` |
| -8 | 504.0 | `[130, 501, 141, 508]` |
| -10 | 625.0 | `[130, 622, 141, 629]` |

[Native image](../../../../data/processed/m5_frozen_pilot_2026-10-23/digitization_final/Wilkerson2020_native.png) · [Unannotated crop](../../../../data/processed/m5_frozen_pilot_2026-10-23/digitization_final/Wilkerson2020_crop.png) · [Annotated means, caps and calibration](../../../../data/processed/m5_frozen_pilot_2026-10-23/digitization_final/Wilkerson2020_annotated.png)

For each site in the table above, check its bar label/color, mean-edge rule, upper/lower cap center and search ROI, and all calibration ticks against these images. Wilding uses the integrated blue edge; H31 uses the black outline center. Confirm no PEG/Ins163/double/reused observation was substituted.

## Sign-off requirements

- [ ] Verify six identities, mean edges, both caps and calibration ticks against the source PDFs.
- [ ] Retain Wilding SD, H31 SEM, N >= 3 and separate reading bounds; do not infer exact N.
- [ ] Record reader identity/date and a per-site decision, including disagreements.
- [ ] If a clear error is found, preserve this snapshot and append old/new values, reason and replacement provenance before any revised analysis.

All boxes remain pending. Images are local review materials in ignored data/processed, not proposed publisher-image redistribution. Fresh-clone users must supply matching PDFs and regenerate them; see the benchmark reproduction guide.
