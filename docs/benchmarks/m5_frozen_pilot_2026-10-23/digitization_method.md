# Digitization protocol, calibration and verification images

## Exact-value search and source selection

The supplied full texts and supplements were inspected before selecting the quantitative source: Wilding main 12 pages/SI 10 pages; Wilkerson main 9 pages/SI 5 pages. No directly transcribable per-site mean/SD table for the five unconjugated substitutions or H31 mean/SEM table was found. Wilding's explicit absolute-control Tm values do not supply mutant delta_Tm; Wilkerson SI RMSF statistics and six/nine MD runs are not thermal-shift values/experimental N. The search finding and source digests are frozen in JSON. No previous visual estimates were used as numerical inputs.

Wilding Figure 3A supplies five blue **Unconjugated** bars: K16, S44, N53, L91, K135. Ins163, the double variant and PEG bars remain visible for context but are not measured into the primary table. Wilkerson Figure 2 supplies **H31 only**. Its S44/N53/L91 bars are explicitly reused data and generate no extra master rows. The original 2018 SD label and the 2020 SEM label are retained independently, without conversion.

## Image extraction and calibrated measurement

The script [digitize_stability.py](digitize_stability.py) uses pypdf to extract the original embedded raster image bytes, rather than rescaling a screenshot. Source-image and PDF hashes, PDF image bounding box, native pixel dimensions and crop bounds are recorded in [digitization_calibration.json](digitization_calibration.json). Cropping is for review only; all numerical coordinates refer to the full native raster, origin at top left. Pixel indices denote centers; fractional edge positions account for antialiasing.

1. Identify the printed major y-axis tick labels and record small tick search regions. Detect tick centers from dark-pixel runs in a fixed x strip (grayscale maximum <160). Fit an affine pixel-y to delta_Tm transform using all major ticks: Wilding 0 to -20 by 2; Wilkerson 0 to -10 by 2. No log scale or x-coordinate numerical conversion is used.
2. Identify contiguous blue bar x groups with fixed RGB criteria (blue >150, green >90, red <100, blue-red >90); the source group order and visible labels identify the five substitutions or H31. These image thresholds have no relationship to RANA scientific thresholds or experimental values.
3. Wilding mean endpoints use integrated blue chroma at the antialiased bottom edge, excluding the central error stem. Wilkerson has a black bar outline, so its outline centerline supplies the plotted mean endpoint. Neither endpoint is a number read from memory or a freehand approximate y value.
4. For each selected bar, use the recorded upper/lower error-cap search regions. Detect the horizontal dark cap centers (RGB maximum <120) within those small regions. Convert the upper/lower distances from the mean and record their asymmetry. The experimental error estimate is the half-distance between the two caps, multiplied by the calibrated y scale. All cap regions, center pixels and unrounded intermediate quantities are saved.
5. Verify calibration with endpoint-only versus all-tick fitting, and mean-edge sensitivity with red cutoffs 80 and 140. Check the cap midpoint agrees with the measured mean within 0.2 degC in the source raster. These checks assess extraction, not biology.

Major-tick seed coordinates and cap search regions were identified by inspecting the native figures, then measured by the deterministic script. This is a single-analyst digitization, not two independent human readings. A second analyst review remains desirable.

## Precision and uncertainty

Published/CSV means and experimental error estimates are rounded to **one decimal degC**. Native Wilding scale is about 17.3 pixels/degC; Wilkerson about 60.5 pixels/degC. A conservative reading bound of +/-0.2 degC (Wilding) and +/-0.1 degC (H31) is assigned to both mean and error-length estimates, allowing for pixel selection, stroke/antialiasing, calibration and rounding. These are operational image-reading bounds, not fitted confidence intervals or new experimental SD/SEM. Threshold/endpoint-fit sensitivity is smaller than the assigned bound and is logged per site.

Wilding Figure 3 caption states SD and n >= 3; stability Methods says assay reactions were in triplicate but does not enumerate pooled per-site exact N. Wilkerson Figure 2/Experimental Data states SEM and N >= 3. `n_exact` remains blank for all six. The narrow original SD/SEM labels are not reinterpreted, combined with reading bounds in quadrature, converted or used for significance tests. The unresolved SD/SEM labeling on three reused points is preserved in the presentation registry.

## Review materials

### Wilding2018

Source: `E:\Papers for RANA\Wilding_2018.pdf`; SHA-256 `c9042894c0b0080686f3be8debbe6ab73d611ec4911231ad766fc490d26e6f15`; PDF p4, printed p513, Figure 3, A.

Native image `Im4`: [969, 1669] pixels. Crop `(left, top, right, bottom)`: `[0, 0, 969, 555]`. PDF image bounding box (points, top-origin): `{'x0': 64.176, 'x1': 296.73, 'top': 69.16599999999994, 'bottom': 469.70099999999996}`.

Calibration: `delta_Tm = -0.057689220016 * y + 7.398544309346`. Maximum major-tick residual: 0.0438 degC. All calibration coordinates/residuals are in JSON; they are not extra significant figures for experimental outcomes.

[Native source image](../../../data/processed/m5_frozen_pilot_2026-10-23/digitization_final/Wilding2018_native.png) | [Unannotated crop](../../../data/processed/m5_frozen_pilot_2026-10-23/digitization_final/Wilding2018_crop.png) | [Annotated calibration/measurement image](../../../data/processed/m5_frozen_pilot_2026-10-23/digitization_final/Wilding2018_annotated.png)

### Wilkerson2020

Source: `E:\Papers for RANA\Wilkerson_2020.pdf`; SHA-256 `ce06cf47c48c00e8e4e81808e814c2928f71414f0c3fc734f6fb41e6788d6f16`; PDF p4, printed p5120, Figure 2, whole figure.

Native image `Im0`: [1000, 722] pixels. Crop `(left, top, right, bottom)`: `[0, 0, 1000, 722]`. PDF image bounding box (points, top-origin): `{'x0': 60.4910011, 'x1': 300.4720039, 'top': 335.1689915999999, 'bottom': 508.42199759999994}`.

Calibration: `delta_Tm = -0.016528925620 * y + 0.330578512397`. Maximum major-tick residual: 0.0000 degC. All calibration coordinates/residuals are in JSON; they are not extra significant figures for experimental outcomes.

[Native source image](../../../data/processed/m5_frozen_pilot_2026-10-23/digitization_final/Wilkerson2020_native.png) | [Unannotated crop](../../../data/processed/m5_frozen_pilot_2026-10-23/digitization_final/Wilkerson2020_crop.png) | [Annotated calibration/measurement image](../../../data/processed/m5_frozen_pilot_2026-10-23/digitization_final/Wilkerson2020_annotated.png)


The red marker is the measured mean endpoint; green markers/rectangles show error-cap centers/search regions; purple lines pass through the detected calibration ticks. Unannotated crops allow reviewers to see the source without overlays. Figure annotations do not modify native source bytes. Image hashes are in the calibration record. Generated images/runs are under ignored `data/processed/`, consistent with AGENTS.md; original PDFs remain in their supplied location. The small calibration JSON and script are retained with the documentation. A reader without local images needs the original source PDFs and can reproduce them.

## Reproduction

Run from the repository root with a separate analysis interpreter providing the recorded pypdf, pdfplumber, NumPy and Pillow versions (see calibration JSON). These are curation tools, not new RANA runtime dependencies. Example in this environment:

```powershell
& 'C:\Users\David\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B docs/benchmarks/m5_frozen_pilot_2026-10-23/digitize_stability.py --sources-dir 'E:\Papers for RANA' --output data/processed/m5_frozen_pilot_2026-10-23/reproduction_fresh
```

The output directory must be new and the input digests must match; existing archives are never overwritten. Font rendering of labels uses Arial on this Windows host. Font choice only affects annotations, not numerical detection. `digitization_final/` is the canonical reviewed run. Earlier partial/development directories in the same ignored namespace are not evidence sources. The CSVs are exported from the frozen JSON with the accompanying `export_tables.mjs` using the bundled artifact-tool runtime; no XLSX or scientific score file is produced.
