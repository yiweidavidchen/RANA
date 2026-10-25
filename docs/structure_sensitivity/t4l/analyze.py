"""Frozen descriptive T4L sensitivity analysis; no experimental outcomes or fitting."""
import argparse
import itertools
import json
import os
import tempfile
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

import numpy as np
import pandas as pd
from Bio.SeqUtils import seq1

from structure_audit import sha

HERE = Path(__file__).resolve().parent
KEYS = ["chain", "residue_number", "insertion_code"]
METRICS = {"rsa": False, "ca_neighbors_8a": True, "min_steric_score": True, "low_clash_fraction": False}
M5 = {16: "K16", 31: "H31", 44: "S44", 53: "N53", 91: "L91", 135: "K135"}
NATIVE_RANKS = {"rsa": "rsa_rank", "min_steric_score": "steric_rank", "low_clash_fraction": "rotamer_robustness_rank"}
TIERS = ("geometry_favorable", "geometry_limited", "geometry_unfavorable")


def require_hash(path, expected):
    """Reject changed/missing inputs without changing the expected provenance."""
    if not isinstance(expected, str) or len(expected) != 64 or sha(path) != expected:
        raise ValueError(f"Input SHA-256 mismatch: {path.name}")


def verified_run_inputs(run_dir):
    """Check the recorded provenance chain before parsing any scan CSV."""
    run = json.loads((run_dir / "run.json").read_text())
    if run["status"] != "scans_completed":
        raise ValueError("Run incomplete")
    plan_path = HERE / "frozen_plan.json"
    require_hash(plan_path, run["plan_sha256"])
    plan = json.loads(plan_path.read_text())
    for name, field in [("analysis_plan.md", "analysis_plan_sha256"),
                        ("audit/structure_audit.json", "audit_sha256"),
                        ("audit/site_mapping.csv", "mapping_sha256"),
                        ("source_manifest.json", "source_manifest_sha256")]:
        require_hash(HERE / name, plan[field])
    for structure in plan["structures"]:
        pdb = structure["pdb_id"]
        record = run["structures"][pdb]
        for name, expected in [
            ("ranked.csv", record["output_validation"]["csv_sha256"]),
            ("ranked.metadata.json", record["output_validation"]["metadata_sha256"]),
            ("protein_A.pdb", record["preparation"]["prepared_sha256"]),
        ]:
            require_hash(run_dir / pdb / name, expected)
    return plan, run


def validate_tiers(values):
    if not values.isin(TIERS).all():
        invalid = values[~values.isin(TIERS)].astype(str).unique().tolist()
        raise ValueError(f"Invalid candidate_tier: {invalid}")


def inclusive_top(values, ascending, k=10):
    """Use the kth order statistic; include every boundary tie."""
    if len(values) == 0 or not np.isfinite(values.to_numpy(dtype=float)).all():
        raise ValueError("Top-list input must be nonempty and finite")
    cutoff = values.sort_values(ascending=ascending).iloc[min(k, len(values)) - 1]
    return set(values.index[values.le(cutoff) if ascending else values.ge(cutoff)])


def spearman(a, b):
    """Average-rank correlation, retaining ties; no significance calculation."""
    x, y = a.rank(method="average").to_numpy(), b.rank(method="average").to_numpy()
    if len(x) < 2 or np.ptp(x) == 0 or np.ptp(y) == 0:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def common_tables(frames, mapping, run_dir):
    """Keep an explicit eligibility ledger, then intersect mapped/scored sites."""
    ledger, eligible = [], {}
    indexed = {}
    for pdb, frame in frames.items():
        if frame.duplicated(KEYS).any():
            raise ValueError(f"Duplicate identities in {pdb}")
        if not frame.status.isin(["scored", "failed", "skipped"]).all():
            raise ValueError(f"Unexpected scan status in {pdb}")
        validate_tiers(frame.loc[frame.status.eq("scored"), "candidate_tier"])
        indexed[pdb] = frame.set_index(KEYS)
        eligible[pdb] = set()
        rows = mapping[(mapping.pdb_id == pdb) & (mapping.chain == "A")]
        expected_keys = {(r.chain, r.author_residue_number, r.insertion_code) for r in rows.itertuples()}
        if not set(indexed[pdb].index) <= expected_keys:
            raise ValueError("Unmapped scan identity")
        for row in rows.itertuples():
            key = (row.chain, row.author_residue_number, row.insertion_code)
            current = indexed[pdb].loc[key] if key in indexed[pdb].index else None
            if current is None and row.modeled:
                raise ValueError(f"Missing scan row for modeled coordinate: {pdb} {key}")
            reason = ""
            status = "absent_from_input" if current is None else current["status"]
            if current is None:
                reason = "No coordinate row; not an experimental failure"
            elif not row.modeled or seq1(current["residue_name"]) != row.entity_parent or row.entity_parent != row.reference_parent:
                reason = "Parent/mapping mismatch"
            elif status != "scored":
                reason = current["reason"] or status
            elif not np.isfinite(current[list(METRICS)].to_numpy(dtype=float)).all():
                reason = "Non-finite analysis metric"
            else:
                eligible[pdb].add(key)
            ledger.append({"pdb_id": pdb, "chain": key[0], "residue_number": key[1], "insertion_code": key[2],
                           "parent": row.entity_parent, "status": status, "eligible_individually": not reason,
                           "in_common_set": False, "exclusion_or_missing_reason": reason,
                           "source": "audit/site_mapping.csv and original ranked.csv status/reason"})
    common = set.intersection(*eligible.values())
    if not common:
        raise ValueError("No common eligible sites")
    for row in ledger:
        key = tuple(row[k] for k in KEYS)
        row["in_common_set"] = key in common
        if row["eligible_individually"] and key not in common:
            row["exclusion_or_missing_reason"] = "Not eligible/present in every selected structure; original scored row retained"
    rows = []
    for pdb, frame in indexed.items():
        path = run_dir / pdb / "ranked.csv"
        for key in sorted(common):
            r = frame.loc[key]
            row = {"pdb_id": pdb, "chain": key[0], "residue_number": key[1], "insertion_code": key[2],
                   "residue_name": r.residue_name, "site_label": f"{seq1(r.residue_name)}{key[1]}",
                   **{m: float(r[m]) for m in METRICS}, "candidate_tier": r.candidate_tier,
                   "n_rotamers": int(r.n_rotamers),
                   **{"original_full_" + rank: float(r[rank]) for rank in NATIVE_RANKS.values()},
                   "source_scan": f"{run_dir.name}/{pdb}/ranked.csv", "source_scan_sha256": sha(path),
                   "source_scan_row_1based": int(frames[pdb].index[frames[pdb][KEYS].apply(tuple, axis=1) == key][0]) + 2,
                   "source_prepared_sha256": sha(run_dir / pdb / "protein_A.pdb")}
            rows.append(row)
    return pd.DataFrame(rows), pd.DataFrame(ledger)


def calculate(long):
    validate_tiers(long.candidate_tier)
    if long.duplicated(["pdb_id", *KEYS]).any():
        raise ValueError("Duplicate curated identity")
    ids = long.pdb_id.drop_duplicates().tolist()
    if len(ids) < 2:
        raise ValueError("At least two nonempty structure groups are required")
    groups = {p: long[long.pdb_id == p].set_index(KEYS).sort_index() for p in ids}
    common_keys = groups[ids[0]].index
    if any(not common_keys.equals(g.index) for g in groups.values()):
        raise ValueError("Curated groups must have identical common identity sets")
    if any(not groups[ids[0]].residue_name.equals(g.residue_name) for g in groups.values()):
        raise ValueError("Common parents differ")
    for pdb, frame in groups.items():
        if not np.isfinite(frame[list(METRICS)].to_numpy(dtype=float)).all():
            raise ValueError("Non-finite curated metrics")
        for metric, ascending in METRICS.items():
            frame[metric + "_common_rank_min"] = frame[metric].rank(method="min", ascending=ascending)
    long = pd.concat([g.assign(pdb_id=p).reset_index() for p, g in groups.items()], ignore_index=True)
    pairs, tops, transitions = [], [], []
    for a, b in itertools.combinations(ids, 2):
        for metric, ascending in METRICS.items():
            rho = spearman(groups[a][metric], groups[b][metric])
            pairs.append({"structure_a": a, "structure_b": b, "metric": metric, "common_sites": len(common_keys),
                          "spearman_rho": rho, "missing_reason": "constant or insufficient ranks" if rho is None else "",
                          "rank_definition": "average ranks, all ties retained; no p-value"})
            ta, tb = inclusive_top(groups[a][metric], ascending), inclusive_top(groups[b][metric], ascending)
            joined = lambda keys: ";".join(f"{k[0]}:{k[1]}:{k[2]}" for k in sorted(keys))
            tops.append({"structure_a": a, "structure_b": b, "metric": metric,
                         "ranking_role": NATIVE_RANKS.get(metric, "comparison_only_packing_rank"),
                         "set_a_size": len(ta), "set_b_size": len(tb), "intersection": len(ta & tb),
                         "union": len(ta | tb), "jaccard": len(ta & tb) / len(ta | tb),
                         "sites_a": joined(ta), "sites_b": joined(tb), "shared_sites": joined(ta & tb),
                         "tie_policy": "inclusive 10th-order-statistic boundary; never break ties"})
        for before in TIERS:
            for after in TIERS:
                transitions.append({"structure_a": a, "structure_b": b, "tier_a": before, "tier_b": after,
                                    "count": int((groups[a].candidate_tier.eq(before) & groups[b].candidate_tier.eq(after)).sum())})
    ranges = []
    for key in common_keys:
        row = {**dict(zip(KEYS, key)), "residue_name": groups[ids[0]].loc[key, "residue_name"],
               "site_label": groups[ids[0]].loc[key, "site_label"],
               "tier_stable": len({groups[p].loc[key, "candidate_tier"] for p in ids}) == 1,
               **{p + "_tier": groups[p].loc[key, "candidate_tier"] for p in ids}}
        for metric in METRICS:
            for field in [metric, metric + "_common_rank_min"]:
                values = [float(groups[p].loc[key, field]) for p in ids]
                row.update({field + "_min": min(values), field + "_max": max(values), field + "_range": max(values) - min(values)})
        ranges.append(row)
    ranges, transitions = pd.DataFrame(ranges), pd.DataFrame(transitions)
    validate_tier_counts(long, ranges, transitions)
    return long, ranges, pd.DataFrame(pairs), pd.DataFrame(tops), transitions


def validate_tier_counts(long, ranges, transitions):
    """Require complete transition matrices and consistent stable/change totals."""
    ids = long.pdb_id.drop_duplicates().tolist()
    expected_stable = long.groupby(KEYS).candidate_tier.nunique().eq(1)
    n_common = len(expected_stable)
    if (len(ranges) != n_common or ranges.duplicated(KEYS).any()
            or not ranges.set_index(KEYS).index.sort_values().equals(expected_stable.index.sort_values())
            or not ranges.tier_stable.isin([True, False]).all()):
        raise ValueError("Invalid tier stable/changed identity set")
    stable = ranges.set_index(KEYS).tier_stable.reindex(expected_stable.index)
    if not stable.equals(expected_stable.rename("tier_stable")):
        raise ValueError("Tier stable/changed counts disagree with input tiers")
    if int(stable.sum()) + int((~stable).sum()) != n_common:
        raise ValueError("Tier stable/changed total differs from common-site count")
    expected_pairs = set(itertools.combinations(ids, 2))
    if set(zip(transitions.structure_a, transitions.structure_b)) != expected_pairs:
        raise ValueError("Incomplete tier transition structure pairs")
    for a, b in expected_pairs:
        table = transitions[(transitions.structure_a == a) & (transitions.structure_b == b)]
        if (len(table) != len(TIERS)**2 or table.duplicated(["tier_a", "tier_b"]).any()
                or not table.tier_a.isin(TIERS).all() or not table.tier_b.isin(TIERS).all()
                or not np.isfinite(table["count"]).all()
                or (table["count"] < 0).any() or (table["count"] % 1 != 0).any()
                or table["count"].sum() != n_common):
            raise ValueError(f"Tier transition total/coverage invalid: {a}/{b}")


def normalize_svg(path):
    """Remove export-only trailing whitespace without changing figure tokens."""
    path.write_text("\n".join(line.rstrip() for line in path.read_text(encoding="utf-8").splitlines()) + "\n",
                    encoding="utf-8", newline="\n")


def plots(long, ranges, output):
    with tempfile.TemporaryDirectory() as config:
        os.environ["MPLCONFIGDIR"] = config
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        plt.rcParams["svg.hashsalt"] = "RANA-M6.3-frozen"
        ids = long.pdb_id.drop_duplicates().tolist()
        pairs = list(itertools.combinations(ids, 2))
        labels = {"rsa": "RSA", "ca_neighbors_8a": "Packing (Cα neighbors, 8 Å)",
                  "min_steric_score": "Minimum steric score (Å²)", "low_clash_fraction": "Low-clash fraction"}
        fig, axes = plt.subplots(4, 3, figsize=(13, 14), constrained_layout=True)
        fig.suptitle("Same-background T4L: all common sites; orange = six M5 sites", fontsize=13)
        for i, metric in enumerate(METRICS):
            for j, (a, b) in enumerate(pairs):
                x = long[long.pdb_id == a].set_index(KEYS).sort_index()
                y = long[long.pdb_id == b].set_index(KEYS).sort_index()
                ax = axes[i, j]
                ax.scatter(x[metric], y[metric], s=10, alpha=.5)
                pilot = [("A", n, "") for n in M5]
                ax.scatter(x.loc[pilot, metric], y.loc[pilot, metric], s=22, color="darkorange")
                ax.set(xlabel=f"{a}: {labels[metric]}", ylabel=f"{b}: {labels[metric]}")
        for ext in ["svg", "png"]:
            fig.savefig(output / f"pairwise_metrics.{ext}", dpi=140, metadata={"Date": None} if ext == "svg" else None)
        plt.close(fig)
        fig, axes = plt.subplots(2, 2, figsize=(11, 7), constrained_layout=True)
        for ax, metric in zip(axes.flat, METRICS):
            for offset, pdb in enumerate(ids):
                frame = long[long.pdb_id == pdb].set_index("residue_number")
                ax.plot(np.arange(6) + (offset - 1)*.12, [frame.loc[n, metric] for n in M5], "o", label=pdb)
            ax.set(xticks=np.arange(6), xticklabels=list(M5.values()), ylabel=labels[metric])
            ax.legend(fontsize=8)
        for ext in ["svg", "png"]:
            fig.savefig(output / f"m5_six_sites.{ext}", dpi=140, metadata={"Date": None} if ext == "svg" else None)
        plt.close(fig)
        fig, axes = plt.subplots(4, 1, figsize=(12, 9), constrained_layout=True)
        for ax, metric in zip(axes, METRICS):
            ax.scatter(ranges.residue_number, ranges[metric + "_common_rank_min_range"], s=8)
            ax.set(xlabel="Author residue number", ylabel=labels[metric] + "\ncommon-rank range")
        for ext in ["svg", "png"]:
            fig.savefig(output / f"rank_ranges.{ext}", dpi=140, metadata={"Date": None} if ext == "svg" else None)
        plt.close(fig)
        for path in output.glob("*.svg"):
            normalize_svg(path)


def analyze(run_dir, curated, output):
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    if curated:
        long = pd.read_csv(curated, keep_default_na=False, float_precision="round_trip")
        ledger = None
        source = {"curated": curated.name, "curated_sha256": sha(curated)}
    else:
        plan, run = verified_run_inputs(run_dir)
        frames = {s["pdb_id"]: pd.read_csv(run_dir / s["pdb_id"] / "ranked.csv", keep_default_na=False, float_precision="round_trip") for s in plan["structures"]}
        mapping = pd.read_csv(HERE / "audit/site_mapping.csv", keep_default_na=False)
        long, ledger = common_tables(frames, mapping, run_dir)
        source = {"run_record_sha256": sha(run_dir / "run.json"), "plan_sha256": run["plan_sha256"]}
    long, ranges, pairs, tops, transitions = calculate(long)
    output.mkdir(parents=True, exist_ok=False)
    for name, frame in [("metrics_long", long), ("site_ranges", ranges), ("pairwise_metrics", pairs),
                        ("top10_overlap", tops), ("tier_transitions", transitions),
                        ("m5_six_sites", long[long.residue_number.isin(M5)])]:
        frame.to_csv(output / f"{name}.csv", index=False)
    if ledger is not None:
        ledger.to_csv(output / "site_eligibility.csv", index=False)
    plots(long, ranges, output)
    metadata = {"created_utc": datetime.now(timezone.utc).isoformat(), "analysis_sha256": sha(Path(__file__)),
                "source": source, "environment": {p: version(p) for p in ["numpy", "pandas", "biopython", "matplotlib"]},
                "common_sites": len(ranges), "tier_stable": int(ranges.tier_stable.sum()),
                "tier_changed": int((~ranges.tier_stable).sum()),
                "outputs_sha256": {p.name: sha(p) for p in output.iterdir() if p.is_file()},
                "scope": "Same-background input sensitivity only; no experimental outcome, model fitting or performance claim."}
    (output / "analysis_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--run-dir", type=Path)
    inputs.add_argument("--curated", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    analyze(args.run_dir, args.curated, args.output)
