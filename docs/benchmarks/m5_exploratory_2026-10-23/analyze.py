"""Analyze frozen curated CSVs, never rescore structures or edit inputs.

Run from any directory with Python + numpy + pandas + matplotlib:
  python docs/benchmarks/m5_exploratory_2026-10-23/analyze.py --output <new-dir>
The output directory must not exist. No PDFs or ignored scans are needed.
"""

import argparse
import csv
import hashlib
import itertools
import json
import math
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FROZEN = HERE.parent / "m5_frozen_pilot_2026-10-23"
METRICS = {
    "rsa": "Parent-structure residue RSA",
    "ca_neighbors_8a": "Local packing (Cα neighbors <8 Å)",
    "min_steric_score": "Minimum steric score (Å²)",
    "low_clash_fraction": "Low-clash fraction (12 sampled rotamers)",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def average_ranks(values):
    return [1 + sum(w < v for w in values) +
            (sum(w == v for w in values) - 1) / 2 for v in values]


def coefficients(x, y):
    """Average-rank Spearman and pair-count tau-b; no p-values calculated."""
    assert len(x) == len(y) and len(x) >= 2
    assert all(math.isfinite(v) for v in x + y)
    rx, ry = average_ranks(x), average_ranks(y)
    dx = [v - sum(rx) / len(rx) for v in rx]
    dy = [v - sum(ry) / len(ry) for v in ry]
    denom = math.sqrt(sum(v*v for v in dx) * sum(v*v for v in dy))
    rho = sum(a*b for a, b in zip(dx, dy)) / denom if denom else None
    concordant = discordant = tied_x_only = tied_y_only = 0
    for i, j in itertools.combinations(range(len(x)), 2):
        a, b = x[i] - x[j], y[i] - y[j]
        if a == 0 and b == 0:
            continue
        if a == 0:
            tied_x_only += 1
        elif b == 0:
            tied_y_only += 1
        elif a*b > 0:
            concordant += 1
        else:
            discordant += 1
    denominator = math.sqrt((concordant + discordant + tied_x_only) *
                            (concordant + discordant + tied_y_only))
    tau = (concordant - discordant) / denominator if denominator else None
    # Independent vectorized checks: pandas average ranks / NumPy sign matrix.
    px, py = pd.Series(x).rank().to_numpy(), pd.Series(y).rank().to_numpy()
    if rho is not None:
        assert np.isclose(rho, np.corrcoef(px, py)[0, 1], atol=1e-12)
    a, b = np.asarray(x), np.asarray(y)
    upper = np.triu_indices(len(x), 1)
    sx = np.sign(a[:, None] - a[None, :])[upper]
    sy = np.sign(b[:, None] - b[None, :])[upper]
    d = math.sqrt(int(np.count_nonzero(sx)) * int(np.count_nonzero(sy)))
    if tau is not None:
        assert np.isclose(tau, np.sum(sx*sy) / d, atol=1e-12)
    return {"spearman_rho": rho, "kendall_tau_b": tau,
            "missing_reason": "constant variable" if denom == 0 else "",
            "concordant_pairs": concordant, "discordant_pairs": discordant,
            "tied_x_only_pairs": tied_x_only, "tied_y_only_pairs": tied_y_only}


def self_check():
    assert coefficients([1, 2, 3], [1, 2, 3])["spearman_rho"] == 1
    assert coefficients([1, 2, 3], [3, 2, 1])["kendall_tau_b"] == -1
    tied = coefficients([1, 1, 2], [1, 2, 3])
    assert np.isclose(tied["spearman_rho"], math.sqrt(3) / 2)
    assert np.isclose(tied["kendall_tau_b"], math.sqrt(2 / 3))
    assert coefficients([1, 1, 1], [1, 2, 3])["kendall_tau_b"] is None


def scatter_t4l(rows, output):
    fig, axes = plt.subplots(2, 2, figsize=(13, 10), layout="constrained")
    for ax, (field, label) in zip(axes.flat, METRICS.items()):
        for row in rows:
            wilding = row["study_id"] == "Wilding2018"
            color = "#1763a6" if wilding else "#b34400"
            x, y = float(row[field]), float(row["value"])
            ax.errorbar(x, y, yerr=float(row["uncertainty_value"]),
                        fmt="o" if wilding else "s", color=color,
                        capsize=4, elinewidth=1.4, markersize=6, zorder=3)
            # Gray broad caps show image-reading bound separately, not added to SD/SEM.
            bound = float(row["digitization_mean_reading_bound_degC"])
            ax.errorbar(x, y, yerr=bound, fmt="none", ecolor="#555555",
                        capsize=8, elinewidth=0.7, zorder=4)
            offset = {"K16": (5, -17), "S44": (5, 8), "N53": (5, -17),
                      "L91": (5, 8), "K135": (5, 8), "H31": (5, -17)}
            ax.annotate(row["literature_site"], (x, y),
                        xytext=offset[row["literature_site"]], textcoords="offset points")
        ax.set(xlabel=label, ylabel="Unconjugated ΔTm (°C)")
        ax.grid(alpha=0.2)
        ax.margins(x=0.18, y=0.17)
    fig.suptitle("T4L retrospective exploratory pilot: 1L63 reference geometry\n"
                 "Blue circles: Wilding 2018 (SD); orange square: Wilkerson 2020 H31 (SEM)", fontsize=13)
    fig.supxlabel("N ≥ 3 (exact N unreported). Wide gray caps: image reading ±0.2 °C (Wilding), ±0.1 °C (H31), not CI.\n"
                  "Primary analysis: five Wilding sites; six-site analysis: cross-study sensitivity. No fitted lines.", fontsize=10)
    fig.savefig(output / "t4l_scatter.png", dpi=170)
    plt.close(fig)


def scatter_ferritin(rows, output):
    fields = ["rsa", "min_steric_score", "low_clash_fraction"]
    fig, axes = plt.subplots(2, 3, figsize=(17, 10), layout="constrained")
    for line, environment in enumerate(["assembly", "monomer"]):
        for ax, field in zip(axes[line], fields):
            for row in rows:
                x, y = float(row[environment + "_" + field]), float(row["value"])
                color = "#a63832" if row["literature_site"] in {"I5", "L155"} else "#1763a6"
                ax.scatter(x, y, color=color, s=35)
                offset = {"F79": (4, -15), "L112": (4, 5), "K83": (4, -15),
                          "L155": (4, 6)}.get(row["literature_site"], (4, 6))
                if environment == "assembly" and field == "rsa":
                    offset = {"Y9": (-14, -18), "F79": (-25, 10), "L112": (10, 5)}.get(row["literature_site"], offset)
                if environment == "assembly" and field == "min_steric_score":
                    offset = {"K83": (-12, -20), "F79": (12, 10),
                              "L112": (24, -4), "Y9": (5, -18)}.get(row["literature_site"], offset)
                if environment == "monomer" and field == "min_steric_score":
                    offset = {"K105": (-24, 20), "L155": (18, 8), "L112": (22, 0),
                              "K83": (-20, -18), "F79": (10, -28)}.get(row["literature_site"], offset)
                if environment == "monomer" and field == "low_clash_fraction":
                    offset = {"K105": (10, 14), "L155": (-24, -18)}.get(row["literature_site"], offset)
                ax.annotate(row["literature_site"], (x, y), xytext=offset,
                            textcoords="offset points",
                            arrowprops={"arrowstyle": "-", "color": "#888888", "lw": 0.6})
            ax.set(xlabel=METRICS[field], ylabel="Reported fluorophore conjugated (%)",
                   title="Assembly primary (24 subunits)" if line == 0 else "Monomer sensitivity only")
            ax.grid(alpha=0.2)
            ax.margins(x=0.2, y=0.18)
    fig.suptitle("Khoshnejad 2018 hFTL: separate descriptive conjugation case (2FG8 reference)\n"
                 "All eight sites retained; red: I5 / L155 disagreements. No fitted lines or invented error bars.", fontsize=13)
    fig.supxlabel("Quantitative TLC: conjugated versus free fluorophore; reported cage:fluorophore 1:24.\n"
                  "Not incorporation efficiency or labeled fraction per subunit. Exact author-used structure / construct unresolved.", fontsize=11)
    fig.savefig(output / "ferritin_scatter.png", dpi=170)
    plt.close(fig)


def fmt(value):
    return "missing" if value is None else f"{value:.3f}"


def run(output):
    assert not output.exists(), "Use a new output directory; preserve earlier results."
    self_check()
    t4l = read_csv(FROZEN / "t4l_stability_master.csv")
    ferritin = read_csv(FROZEN / "ferritin_conjugation_comparison.csv")
    assert len(t4l) == len({r["observation_id"] for r in t4l}) == 6
    assert len(ferritin) == len({r["observation_id"] for r in ferritin}) == 8
    results = []
    for cohort, rows in [("Wilding_primary", [r for r in t4l if r["study_id"] == "Wilding2018"]),
                         ("six_site_cross_study_sensitivity", t4l)]:
        for field in METRICS:
            def evaluate(subset):
                return coefficients([float(r[field]) for r in subset], [float(r["value"]) for r in subset])
            full = evaluate(rows)
            loo = [{"omitted_site": row["literature_site"], "omitted_observation_id": row["observation_id"],
                    **evaluate(rows[:i] + rows[i+1:])} for i, row in enumerate(rows)]
            ranges = {}
            for key in ["spearman_rho", "kendall_tau_b"]:
                valid = [r[key] for r in loo if r[key] is not None]
                ranges[key] = {"minimum": min(valid) if valid else None,
                               "maximum": max(valid) if valid else None,
                               "n_defined": len(valid)}
            results.append({"cohort": cohort, "field": field, "n_sites": len(rows),
                            "observation_ids": [r["observation_id"] for r in rows],
                            **full, "leave_one_out": loo, "leave_one_out_ranges": ranges})
    output.mkdir(parents=True)
    inputs = [FROZEN / "t4l_stability_master.csv", FROZEN / "ferritin_conjugation_comparison.csv", HERE / "evaluation_plan.md"]
    record = {"analysis_type": "already_seen_retrospective_exploratory_not_preregistered",
              "human_digitization_review_status": "pending",
              "executed_utc": datetime.now(timezone.utc).isoformat(),
              "executable": sys.executable, "argv": sys.argv, "working_directory": str(Path.cwd()),
              "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "git_status_at_execution": subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True),
              "python": platform.python_version(), "packages": {"numpy": np.__version__, "pandas": pd.__version__, "matplotlib": matplotlib.__version__},
              "script_sha256": sha(Path(__file__)),
              "input_sha256": {p.relative_to(ROOT).as_posix(): sha(p) for p in inputs},
              "t4l_results": results,
              "value_source_fields": {"t4l_x": list(METRICS), "t4l_y": "value", "experimental_error": "uncertainty_value; uncertainty_type",
                                      "reading_bounds": "digitization_mean_reading_bound_degC; digitization_error_reading_bound_degC",
                                      "ferritin_x": [e + "_" + f for e in ["assembly", "monomer"] for f in ["rsa", "min_steric_score", "low_clash_fraction"]], "ferritin_y": "value"},
              "ferritin_correlations": "not calculated; separate descriptive case"}
    scatter_t4l(t4l, output)
    scatter_ferritin(ferritin, output)
    text = ["# Exploratory pilot results", "", "Executed after the [evaluation plan](../evaluation_plan.md) was saved. Already-seen retrospective data; independent human digitization review **pending**. No scientific scoring changes.", "",
            "## T4L: all four fields and both cohorts", "", "Coefficients retain raw field direction. Direction hypotheses: positive RSA/fraction; negative packing/steric. No p-values or significance conclusions. Leave-one-out ranges use every possible omitted site and do not justify deleting any site.", "",
            "| Cohort | Field | Sites | Spearman rho | Kendall tau-b | LOO rho range | LOO tau-b range |", "| --- | --- | ---: | ---: | ---: | --- | --- |"]
    for r in results:
        rr, tr = r["leave_one_out_ranges"]["spearman_rho"], r["leave_one_out_ranges"]["kendall_tau_b"]
        text.append(f"| {r['cohort']} | `{r['field']}` | {r['n_sites']} | {fmt(r['spearman_rho'])} | {fmt(r['kendall_tau_b'])} | {fmt(rr['minimum'])} to {fmt(rr['maximum'])} | {fmt(tr['minimum'])} to {fmt(tr['maximum'])} |")
    text += ["", "All individual deletions, observation IDs, pair/tie counts, input hashes, versions and execution provenance are in [results.json](results.json). Spearman uses average ranks; tau-b retains ties. Rankings were not recomputed or combined.", "", "![T4L scatter plots](t4l_scatter.png)", "", "Values and errors: frozen `t4l_stability_master.csv` fields `value`, `uncertainty_value`, `uncertainty_type`; exact row source locators and original PDF hashes remain there. Experimental SD (five Wilding sites) and SEM (H31) are distinct. Gray caps show operational reading bounds separately; they are not confidence intervals and are not added to SD/SEM. Bounds on extracted error lengths also remain in the frozen CSV. N >= 3 remains a lower bound.", "",
             "The frozen means are K16 −5.4, S44 −2.1, N53 −2.9, L91 −9.6, K135 −4.8 and H31 −7.2 °C. These are digitized estimates, not exact published text values. No current strict sequence-matched eligibility is established. The shared scaffold, selected sites, study/control differences and unresolved full construct/tag/background equivalence limit interpretation. The reference is 1L63, with SEQADV C54T/C97A.", "",
             "## Ferritin remains separate", "", "![Ferritin scatter plots](ferritin_scatter.png)", "", "Sources: frozen `ferritin_conjugation_comparison.csv`, `value` and `assembly_rsa`, `assembly_min_steric_score`, `assembly_low_clash_fraction` (primary); corresponding `monomer_` fields (sensitivity). Published S2/I5/Y9/F79/K83/K105/L112/L155 values are 30/57/10/14/16/18/14/18 percent fluorophore conjugated by TLC. Source: Khoshnejad main PDF p3 (printed 1211); condition definition p7 (1215). No N/error bars were fabricated.", "", "I5 retains 57% conjugation despite assembly low-clash fraction 0 and an unfavorable tier; L155 retains 18% despite assembly fraction 0 and an unfavorable tier. Monomer scores differ, but do not replace assembly as the primary environment. The frozen model substitutes only the target subunit in a parent cage; it does not model 24 simultaneously mutated subunits. Reference 2FG8 is approved for this computational case; the exact PDB used by the authors and complete fusion sequence remain unconfirmed.", "",
             "## What this supports", "", "This describes within-cohort rank associations and environment sensitivity. It does not establish generalization, causal stability mechanisms, calibrated ΔTm prediction, or superiority over RSA. Leave-one-out ranges expose small-cohort leverage and are not confidence intervals. Experimental uncertainty and digitization uncertainty were not propagated into correlation distributions. Human review and larger endpoint-specific independent cohorts remain necessary. No pooled T4L/ferritin correlation, fitting, significance testing, binary evaluation, tuning or new composite score was performed."]
    (output / "results.md").write_text("\n".join(text) + "\n", encoding="utf-8")
    record["output_sha256"] = {p.name: sha(p) for p in sorted(output.iterdir())}
    (output / "results.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "cohort_metric_pairs": len(results), "leave_one_out_pairs": sum(len(r["leave_one_out"]) for r in results)}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    run(parser.parse_args().output.resolve())
