"""Curate the accepted single-input BglB case without rescoring or fitting."""
import argparse
import itertools
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from Bio.SeqUtils import seq1

from run_case import (HERE, KEYS, REVISION, TEXT_HASH_ALGORITHM, approved_plan,
                      check_hash, identities, protein_lines, read_json, require, sha,
                      text_sha, validate_output, verify_execution_sources)

RANKS = {"steric_rank": ("min_steric_score", True), "rsa_rank": ("rsa", False),
         "rotamer_robustness_rank": ("low_clash_fraction", False)}


def inclusive_members(values, ascending, k=10):
    require(len(values) > 0 and np.isfinite(values.to_numpy(dtype=float)).all(), "Invalid top-list values")
    boundary = float(values.sort_values(ascending=ascending).iloc[min(k, len(values)) - 1])
    return values.index[values.le(boundary) if ascending else values.ge(boundary)].tolist(), boundary


def verified_inputs(run_dir):
    record = read_json(run_dir / "run.json")
    require(record["status"] in {"scan_completed", "scan_completed_with_diagnostics"}, "Run not complete")
    plan, approval = approved_plan()
    verify_execution_sources(run_dir, record, plan, approval)
    for name, digest in [("ranked.csv", record["output_validation"]["csv_sha256"]),
                         ("ranked.metadata.json", record["output_validation"]["metadata_sha256"]),
                         ("protein_A.pdb", record["preparation"]["prepared_sha256"]),
                         ("2O9P_original.pdb", plan["source_sha256"]),
                         ("executed_sources/run_case.py", record["wrapper_sha256"]),
                         ("executed_sources/execution_plan_2026-10-25.json", record["execution_plan_sha256"])]:
        check_hash(run_dir / name, digest)
    audit = read_json(HERE / "candidate_audit.json")
    authority = {(r["chain"], r["residue_number"], r["insertion_code"]): r["residue_name"]
                 for r in audit["structures"]["2O9P"]["observed_residue_identities"]}
    require(protein_lines(run_dir / "protein_A.pdb") == protein_lines(run_dir / "2O9P_original.pdb"), "Prepared coordinate/atom records differ from source")
    require(identities(protein_lines(run_dir / "protein_A.pdb"))[1] == authority, "Prepared identity set differs from audit")
    validation = validate_output(run_dir / "ranked.csv", authority, plan["cli_configuration"], record["preparation"]["prepared_sha256"], record["git_commit"])
    require(validation == record["output_validation"], "Run validation differs from recorded results")
    return record, plan, audit


def build_tables(raw, plan, audit, scan_sha, prepared_sha):
    """Copy scientific fields and add separate annotations/display membership."""
    scored = raw.status.eq("scored")
    for rank, (metric, ascending) in RANKS.items():
        expected = raw.loc[scored, metric].rank(method="min", ascending=ascending)
        require(np.array_equal(expected.to_numpy(), raw.loc[scored, rank].to_numpy()), f"Original rank inconsistent: {rank}")
    fields = [*KEYS, "residue_name", "status", "reason", "sasa_abs", "rsa", "ca_neighbors_8a",
              "n_rotamers", "min_steric_score", "mean_steric_score", "median_steric_score", "low_clash_fraction",
              "best_chi1", "best_chi2", "candidate_tier", *RANKS, "special_residue_flag", "ranking_reason"]
    table = raw[fields].copy()
    table["site_label"] = [f"{seq1(r.residue_name)}{r.residue_number}{r.insertion_code}" for r in table.itertuples()]
    counts = []
    for row in raw.itertuples():
        counts.append(sum(value <= plan["cli_configuration"]["low_clash_threshold"] for value in json.loads(row.rotamer_scores)) if row.status == "scored" else None)
    table["low_clash_rotamer_count"] = pd.array(counts, dtype="Int64")
    annotation = {tuple(r[k] for k in KEYS): r for r in plan["functional_annotations"]}
    require(len(annotation) == 11, "Functional annotation count/identity conflict")
    actual = {tuple(r[k] for k in KEYS): r["residue_name"] for r in table.to_dict("records")}
    for key, row in annotation.items():
        require(actual.get(key) == row["residue_name"], f"Functional annotation missing/parent mismatch: {key}")
    role_map = {}
    for item in audit["functional_mappings"][:11]:
        target = item["mappings"]["2O9P"]
        key = tuple(target[k] for k in KEYS)
        role_map[key] = ("; ".join(f["description"] for f in item["uniprot_features"]),
                         "; ".join(sorted({e["evidenceCode"] for f in item["uniprot_features"] for e in f.get("evidences", [])})))
    keys = [tuple(r[k] for k in KEYS) for r in table.to_dict("records")]
    table["maintainer_functional_flag"] = [key in annotation for key in keys]
    table["foldit_context_label"] = [annotation[key]["foldit_label"] if key in annotation else "" for key in keys]
    table["reference_role_annotation"] = [role_map.get(key, ("", ""))[0] for key in keys]
    table["reference_role_evidence"] = [role_map.get(key, ("", ""))[1] for key in keys]
    table["background_context"] = [{("A",376,""):"H376Q", ("A",377,""):"G377R"}.get(key, "") for key in keys]
    table["source_scan_sha256"] = scan_sha
    table["source_scan_row_1based"] = np.arange(2, len(raw) + 2)
    table["source_prepared_sha256"] = prepared_sha
    summary, memberships = {}, []
    selected = set()
    for rank, (metric, ascending) in RANKS.items():
        members, boundary = inclusive_members(raw.loc[scored, metric], ascending)
        selected.update(members)
        table["in_inclusive_top10_" + rank] = table.index.isin(members)
        identities_out = [table.loc[index, KEYS + ["site_label"]].to_dict() for index in members]
        # Convert NumPy integers for portable JSON without losing identity.
        for identity in identities_out:
            identity["residue_number"] = int(identity["residue_number"])
        summary[rank] = {"metric": metric, "ascending": ascending, "boundary": boundary,
                         "actual_size": len(members), "identities": identities_out}
        for index in members:
            row = table.loc[index]
            memberships.append({**{k: row[k] for k in KEYS + ["site_label"]}, "independent_rank": rank,
                                "rank": row[rank], "metric": metric, "metric_value": row[metric]})
    for a, b in itertools.combinations(RANKS, 2):
        # No additional metric or merged ordering; this is a membership count.
        summary[a]["overlap_with_" + b] = int((table["in_inclusive_top10_" + a] & table["in_inclusive_top10_" + b]).sum())
    overview = table.loc[sorted(selected)].sort_values(KEYS)
    functional = table[table.maintainer_functional_flag].sort_values(KEYS)
    background = table[table.background_context.ne("")].sort_values(KEYS)
    missing = pd.DataFrame([{"chain": r["auth_asym_id"], "residue_number": int(r["auth_seq_id"]),
                             "insertion_code": "" if r["PDB_ins_code"] in ["?", "."] else r["PDB_ins_code"],
                             "residue_name": r["auth_comp_id"], "coordinate_status": "declared_unobserved",
                             "reason": "Absent from deposited 2O9P coordinates; not an experimentally tested negative",
                             "source_field": "2O9P.cif _pdbx_unobs_or_zero_occ_residues"}
                            for r in audit["structures"]["2O9P"]["declared_unobserved_residues"]])
    return table, overview, functional, background, pd.DataFrame(memberships), missing, summary


def markdown_table(frame):
    columns = ["PDB author site", "RSA", "Packing", "Min steric (Å²)", "Low-clash count/12", "Geometric tier", "Steric/RSA/fraction ranks", "Functional flag"]
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in frame.itertuples():
        if row.status == "scored":
            values = [f"{row.chain}:{row.site_label}", f"{row.rsa:.3f}", str(int(row.ca_neighbors_8a)), f"{row.min_steric_score:.3f}",
                      f"{row.low_clash_rotamer_count}/12", row.candidate_tier,
                      f"{int(row.steric_rank)}/{int(row.rsa_rank)}/{int(row.rotamer_robustness_rank)}", str(row.maintainer_functional_flag)]
        else:
            values = [f"{row.chain}:{row.site_label}", "", "", "", "", row.status + ": " + row.reason, "", str(row.maintainer_functional_flag)]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def curate(run_dir, output):
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    record, plan, audit = verified_inputs(run_dir)
    raw = pd.read_csv(run_dir / "ranked.csv", keep_default_na=False, float_precision="round_trip", encoding="utf-8")
    table, overview, functional, background, memberships, missing, lists = build_tables(
        raw, plan, audit, record["output_validation"]["csv_sha256"], record["preparation"]["prepared_sha256"])
    output.mkdir(parents=True, exist_ok=False)
    results = output / "results"
    results.mkdir()
    for name, data in [("per_site", table), ("candidate_overview", overview), ("functional_context", functional),
                       ("background_context", background), ("top_list_memberships", memberships), ("coordinate_absences", missing)]:
        data.to_csv(results / f"{name}.csv", index=False, encoding="utf-8")
    (results / "top_lists.json").write_text(json.dumps(lists, indent=2) + "\n", encoding="utf-8")
    counts = record["output_validation"]["tier_counts"]
    report = f'''# BglB pAzF computational application: results

Protein: **β-glucosidase B (BglB) from Paenibacillus polymyxa**.
Input: **2O9P chain A, H376Q/G377R engineered apo reference**, not natural WT,
D2D standard or the maintainer's experimental construct. All output identities
use input PDB author chain, residue number and insertion code, not Foldit numbers.
Case selection originated from the maintainer's BglB research experience. This
is an independent RANA computation and does not imply that the preprint, any
laboratory or D2D has conducted ncAA experiments. There are no corresponding
pAzF experimental validation data in this case.

## Preparation and actual scan

Prepared only the 2O9P monomer's 3626 protein heavy atoms, preserving all source
ATOM records and coordinates, author positions A:4–448 and blank insertion codes.
Removed 138 waters; no organic ligand or ion was present in this deposited apo
input. No mutation, filling, relaxation or coordinate renumbering was performed.
SASA, packing and steric screening are **protein-only**. A ligand in an original
file does not imply RANA considered ligand sterics. Removing ligand from a holo
model retains the holo conformation and does not create an experimental apo.

One scan used RANA {record['git_commit']}, seed 42, the frozen 12-rotamer pAzF
library, 10.0 Å² cutoff and favorable fraction 0.5. Functional annotations were
joined afterward without modifying scores, tiers or independent ranks. The
[execution summary](execution_summary.json) preserves code, hashes, actual times,
environment and the detailed local run locator; it is software execution evidence,
not experimental predictive validation.

Status counts: {json.dumps(record['output_validation']['status_counts'], sort_keys=True)}.
Geometric tier counts: {json.dumps(counts, sort_keys=True)}.
The [complete curated table](results/per_site.csv) retains every attempted row.
The [nine coordinate absences](results/coordinate_absences.csv) are separate from
scoring failures and never treated as tested experimental negatives.

## Predefined independent displays

All cutoff ties are included at the tenth order statistic. Actual list sizes:
{'; '.join(f"{key}: {value['actual_size']}" for key,value in lists.items())}.
Their union contains **{len(overview)}** sites, displayed in structural identity
order in [candidate_overview.csv](results/candidate_overview.csv) and
[the full overview table](candidate_overview.md). This union is not a composite
ranking. Original ranks, individual memberships and boundaries remain in
[top_list_memberships.csv](results/top_list_memberships.csv) and
[top_lists.json](results/top_lists.json). No functional site was filtered out.

## All eleven functional-context sites

These are maintainer-provided flags with verified parent/number mapping, not a
model-derived exclusion set. UniProt reference annotations identify E167 as
proton donor and E356 as nucleophile (original ECO:0000255 evidence retained).
Other sites are not newly assigned specific experimentally proven roles here.
The [full context CSV](results/functional_context.csv) carries evidence sources.
Numbers below are rounded for display only; machine-readable files retain full
source precision. All scores/ranks come from the same run and same-named raw
fields, as located by source hash and source row in `per_site.csv`.

{markdown_table(functional)}

Functional annotations and original Gly/Pro cautions must remain visible even
where a geometric tier is favorable. Low-clash fraction is the fraction of 12
sampled conformers scoring <=10.0 Å²; it is neither experimental success
probability nor the fraction of all physical conformations. No interpretation
of activity, incorporation, expression, stability or conjugation follows.

## Engineered-background context

Both engineered sites are retained separately, not hidden by the functional list:

{markdown_table(background)}

Their structural background can affect the rest of the protein; this case does
not compare them with a natural sequence or perform mutational-effect inference.

## Scope and remaining limits

2JIE remains a mechanism/ligand reference, without a new scan. 2Z1S, 2O9R and
2O9T are future candidates pending review only: no download, comparison or new
analysis was performed for them. The D2D holo candidate was not rescored.
Single fixed reference, monomer-only environment, omitted ligand/water effects,
discrete rotamers and heuristic tiers limit interpretation. There is no fitted
model, experiment correlation, performance evaluation or experimental success claim.
No private paths, HPC models, unpublished experiments, MD, ML or second ncAA
were used. Source/preparation history limits from the [structure review](structure_review.md)
remain explicit. No fresh-environment or cross-platform validation is claimed.
'''
    (output / "results_report.md").write_text(report, encoding="utf-8", newline="\n")
    (output / "candidate_overview.md").write_text(
        "# Inclusive top-list union, in PDB structural identity order\n\n"
        "β-glucosidase B (BglB) from Paenibacillus polymyxa; 2O9P A H376Q/G377R engineered apo reference.\n\n"
        "Union of independent inclusive top-10 sets; every boundary tie retained. No combined rank.\n"
        "Functional flags do not change membership. Full precision, source hashes and membership columns: "
        "[candidate_overview.csv](results/candidate_overview.csv).\n\n" + markdown_table(overview) + "\n", encoding="utf-8", newline="\n")
    metadata = {"created_utc": datetime.now(timezone.utc).isoformat(), "curation_sha256": sha(Path(__file__)),
                "protein": plan["protein"],
                "tool_revision": REVISION, "text_hash_algorithm": TEXT_HASH_ALGORITHM,
                "current_tool_lf_sha256": {p.name: text_sha(p) for p in [Path(__file__), HERE / "run_case.py"]},
                "original_executed_wrapper_sha256": record["wrapper_sha256"],
                "original_execution_tool_revision": record.get("tool_revision", "original-pre-review-runner"),
                "run_record_sha256": sha(run_dir / "run.json"), "execution_plan_sha256": record["execution_plan_sha256"],
                "scan_sha256": record["output_validation"]["csv_sha256"], "rows": len(table), "functional_sites": len(functional),
                "background_sites": len(background), "coordinate_absences": len(missing), "overview_union_sites": len(overview),
                "top_list_sizes": {k:v["actual_size"] for k,v in lists.items()},
                "scientific_fields": "Copied same-named raw scan fields; ranks checked but not replaced. Only low_clash_rotamer_count derives from the existing 12 raw rotamer_scores <= frozen cutoff.",
                "annotation_fields": "Maintainer list / public D2D tooltip parent checks / UniProt reference roles and evidence; no scoring contribution.",
                "outputs_sha256": {p.relative_to(output).as_posix(): sha(p) for p in sorted(output.rglob("*")) if p.is_file()}}
    archive = output / "executed_sources"
    archive.mkdir()
    for source in [Path(__file__), HERE / "run_case.py"]:
        shutil.copy2(source, archive / source.name)
    metadata["executed_source_sha256"] = {p.name: sha(p) for p in archive.iterdir()}
    (output / "curation_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    curate(args.run_dir.resolve(), args.output_dir.resolve())
