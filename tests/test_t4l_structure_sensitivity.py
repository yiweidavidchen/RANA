"""Sensitivity-study identities, ties and source-preserving preparation."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "docs/structure_sensitivity/t4l"


@pytest.fixture
def modules(monkeypatch):
    monkeypatch.syspath_prepend(str(SCRIPTS))
    result = {}
    for name in ["structure_audit", "run_scans", "analyze"]:
        spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        monkeypatch.setitem(sys.modules, name, module)
        result[name] = module
    return result


@pytest.mark.parametrize("ascending", [True, False])
def test_top10_boundary_retains_all_ties(modules, ascending):
    values = pd.Series([*range(1, 10), 10, 10, 10, 11], index=range(13), dtype=float)
    if not ascending:
        values = -values
    members = modules["analyze"].inclusive_top(values, ascending)
    assert members == set(range(12))  # include three tied tenth-place entries


def test_constant_rank_correlation_is_missing_and_ties_retained(modules):
    analysis = modules["analyze"]
    assert analysis.spearman(pd.Series([1, 1]), pd.Series([2, 3])) is None
    assert analysis.spearman(pd.Series([1, 1, 2, 3]), pd.Series([3, 3, 2, 1])) == pytest.approx(-1)
    with pytest.raises(ValueError):
        analysis.inclusive_top(pd.Series([np.nan]), True)


@pytest.mark.parametrize("unscored", ["failed", "skipped"])
def test_common_set_preserves_missing_failed_parent_mismatch_diagnostics(modules, tmp_path, unscored):
    analysis = modules["analyze"]
    mapping = pd.DataFrame([
        dict(pdb_id=p, chain="A", author_residue_number=n, insertion_code="", modeled=True,
             entity_parent="A", reference_parent="A") for p in ["one", "two"] for n in range(1, 5)
    ])
    mapping.loc[(mapping.pdb_id == "two") & (mapping.author_residue_number == 4), "modeled"] = False
    frame = pd.DataFrame([dict(chain="A", residue_number=n, insertion_code="", residue_name="ALA",
                              status="scored", reason="", rsa=.2, ca_neighbors_8a=3, min_steric_score=1,
                              low_clash_fraction=.5, candidate_tier="geometry_favorable", n_rotamers=12,
                              rsa_rank=n, steric_rank=n, rotamer_robustness_rank=n) for n in range(1, 5)])
    other = frame.iloc[:3].copy()
    other.loc[1, ["status", "reason"]] = [unscored, "missing_backbone"]
    other.loc[2, "residue_name"] = "GLY"
    frames = {"one": frame, "two": other}
    for pdb, data in frames.items():
        (tmp_path / pdb).mkdir()
        data.to_csv(tmp_path / pdb / "ranked.csv", index=False)
        (tmp_path / pdb / "protein_A.pdb").write_text("synthetic")
    long, ledger = analysis.common_tables(frames, mapping, tmp_path)
    assert len(ledger) == 8 and len(long) == 2
    assert set(long.residue_number) == {1}
    assert ledger.query("pdb_id == 'two' and residue_number == 2").iloc[0].exclusion_or_missing_reason == "missing_backbone"
    assert ledger.query("pdb_id == 'two' and residue_number == 2").iloc[0].status == unscored
    assert ledger.query("pdb_id == 'two' and residue_number == 3").iloc[0].exclusion_or_missing_reason == "Parent/mapping mismatch"
    assert ledger.query("pdb_id == 'two' and residue_number == 4").iloc[0].status == "absent_from_input"
    assert ledger.query("pdb_id == 'one' and residue_number == 4").iloc[0].status == "scored"
    mapping.loc[(mapping.pdb_id == "two") & (mapping.author_residue_number == 4), "modeled"] = True
    with pytest.raises(ValueError, match="Missing scan row for modeled coordinate"):
        analysis.common_tables(frames, mapping, tmp_path)
    with pytest.raises(ValueError, match="Duplicate"):
        analysis.common_tables({"one": pd.concat([frame, frame.iloc[:1]])}, mapping, tmp_path)


def test_common_ranks_recomputed_original_ranks_unchanged(modules):
    rows = []
    for pdb in ["one", "two"]:
        for n, value in enumerate([.9, .9, .2], 1):
            rows.append(dict(pdb_id=pdb, chain="A", residue_number=n, insertion_code="", residue_name="ALA",
                             site_label=f"A{n}", rsa=value, ca_neighbors_8a=n, min_steric_score=n,
                             low_clash_fraction=.5, candidate_tier="geometry_favorable", original_full_rsa_rank=42))
    long, ranges, correlations, top, transitions = modules["analyze"].calculate(pd.DataFrame(rows))
    assert long.rsa_common_rank_min.tolist() == [1, 1, 3, 1, 1, 3]
    assert long.original_full_rsa_rank.eq(42).all()
    assert ranges.tier_stable.all()
    assert transitions["count"].sum() == 3
    assert correlations.loc[correlations.metric.eq("low_clash_fraction"), "spearman_rho"].isna().all()
    assert top["jaccard"].eq(1).all()


def test_preparation_preserves_altlocs_and_refuses_overwrite(modules, tmp_path):
    source = tmp_path / "source.pdb"
    source.write_text(
        "ATOM      1  CA AALA A   1       1.000   2.000   3.000  0.50 10.00           C  \n"
        "ATOM      2  CA BALA A   1       2.000   2.000   3.000  0.50 11.00           C  \n"
        "ATOM      3  CA  ALA B   1       9.000   2.000   3.000  1.00 10.00           C  \n"
        "HETATM    4  O   HOH A 201       8.000   8.000   8.000  1.00 10.00           O  \nEND\n"
    )
    output = tmp_path / "prepared.pdb"
    result = modules["run_scans"].prepare(source, output)
    assert result["retained_chains"] == ["A"]
    assert result["heavy_atom_records_including_altlocs"] == 2
    assert result["max_abs_coordinate_change_A"] == 0
    assert "CA AALA" in output.read_text() and "CA BALA" in output.read_text()
    assert "HOH" not in output.read_text()
    before = output.read_bytes()
    with pytest.raises(FileExistsError):
        modules["run_scans"].prepare(source, output)
    assert output.read_bytes() == before


@pytest.mark.parametrize("change", ["none", "content", "extra", "missing"])
def test_frozen_scientific_source_guard(modules, tmp_path, monkeypatch, change):
    runner = modules["run_scans"]
    package = tmp_path / "ncaa_site_rec"
    package.mkdir()
    path = package / "a.py"
    path.write_bytes(b"frozen = 1\r\n" if change != "content" else b"changed = 2\n")
    if change == "extra":
        (package / "extra.py").write_text("extra")
    if change == "missing":
        path.unlink()
    def git_output(command, **kwargs):
        return b"ncaa_site_rec/a.py\n" if "ls-tree" in command else b"frozen = 1\n"
    monkeypatch.setattr(runner.subprocess, "check_output", git_output)
    if change == "none":
        runner.verify_scientific_source(tmp_path, package, "base")
    else:
        with pytest.raises(ValueError, match="Scientific source"):
            runner.verify_scientific_source(tmp_path, package, "base")


@pytest.fixture
def recorded_analysis_inputs(modules, tmp_path, monkeypatch):
    """Synthetic provenance chain; no historical files or structure downloads."""
    analysis = modules["analyze"]
    profile, run = tmp_path / "profile", tmp_path / "run"
    profile.mkdir()
    (profile / "audit").mkdir()
    (run / "one").mkdir(parents=True)
    plan = {"structures": [{"pdb_id": "one"}]}
    for name, field in [("analysis_plan.md", "analysis_plan_sha256"),
                        ("audit/structure_audit.json", "audit_sha256"),
                        ("audit/site_mapping.csv", "mapping_sha256"),
                        ("source_manifest.json", "source_manifest_sha256")]:
        path = profile / name
        path.write_text("synthetic frozen dependency\n")
        plan[field] = analysis.sha(path)
    (profile / "frozen_plan.json").write_text(json.dumps(plan))
    for name in ["ranked.csv", "ranked.metadata.json", "protein_A.pdb"]:
        (run / "one" / name).write_text("synthetic recorded input\n")
    record = {"status": "scans_completed", "plan_sha256": analysis.sha(profile / "frozen_plan.json"),
              "structures": {"one": {"output_validation": {
                  "csv_sha256": analysis.sha(run / "one/ranked.csv"),
                  "metadata_sha256": analysis.sha(run / "one/ranked.metadata.json")},
                  "preparation": {"prepared_sha256": analysis.sha(run / "one/protein_A.pdb")}}}}
    (run / "run.json").write_text(json.dumps(record))
    monkeypatch.setattr(analysis, "HERE", profile)
    return profile, run


def test_recorded_inputs_pass_without_csv_parsing(modules, recorded_analysis_inputs, monkeypatch):
    analysis = modules["analyze"]
    profile, run = recorded_analysis_inputs
    monkeypatch.setattr(analysis.pd, "read_csv", lambda *a, **k: pytest.fail("Premature CSV parsing"))
    plan, record = analysis.verified_run_inputs(run)
    assert record["status"] == "scans_completed" and plan["structures"] == [{"pdb_id": "one"}]


@pytest.mark.parametrize("filename", ["frozen_plan.json", "analysis_plan.md", "audit/structure_audit.json",
                                     "audit/site_mapping.csv", "source_manifest.json", "one/ranked.csv",
                                     "one/ranked.metadata.json", "one/protein_A.pdb"])
def test_changed_input_fails_before_csv_parsing(modules, recorded_analysis_inputs, monkeypatch, tmp_path, filename):
    analysis = modules["analyze"]
    profile, run = recorded_analysis_inputs
    path = (run if filename.startswith("one/") else profile) / filename
    path.write_bytes(path.read_bytes() + b"\n")
    record_before = (run / "run.json").read_bytes()
    monkeypatch.setattr(analysis.pd, "read_csv", lambda *a, **k: pytest.fail("Premature CSV parsing"))
    output = tmp_path / "must_not_exist"
    with pytest.raises(ValueError, match="Input SHA-256 mismatch"):
        analysis.analyze(run, None, output)
    assert not output.exists() and (run / "run.json").read_bytes() == record_before


def test_incomplete_run_and_missing_input_rejected(modules, recorded_analysis_inputs):
    analysis = modules["analyze"]
    profile, run = recorded_analysis_inputs
    record_path = run / "run.json"
    record = json.loads(record_path.read_text())
    record["status"] = "failed"
    record_path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="Run incomplete"):
        analysis.verified_run_inputs(run)
    record["status"] = "scans_completed"
    record_path.write_text(json.dumps(record))
    (run / "one/ranked.csv").unlink()
    with pytest.raises(FileNotFoundError):
        analysis.verified_run_inputs(run)


def tier_fixture():
    return pd.DataFrame([dict(pdb_id=pdb, chain="A", residue_number=n, insertion_code="", residue_name="ALA",
                             site_label=f"A{n}", rsa=n/10, ca_neighbors_8a=n, min_steric_score=n,
                             low_clash_fraction=.5, candidate_tier="geometry_favorable")
                         for pdb in ["one", "two", "three"] for n in [1, 2]])


@pytest.mark.parametrize("tier", ["bad_tier", "", None])
def test_invalid_tier_rejected(modules, tier):
    frame = tier_fixture()
    frame.loc[0, "candidate_tier"] = tier
    with pytest.raises(ValueError, match="Invalid candidate_tier"):
        modules["analyze"].calculate(frame)


@pytest.mark.parametrize("damage", ["total", "missing_pair", "duplicate_cell", "stable", "identity"])
def test_tier_count_guards(modules, damage):
    analysis = modules["analyze"]
    long, ranges, _, _, transitions = analysis.calculate(tier_fixture())
    analysis.validate_tier_counts(long, ranges, transitions)
    if damage == "total":
        transitions.loc[0, "count"] += 1
    elif damage == "missing_pair":
        transitions = transitions[~((transitions.structure_a == "one") & (transitions.structure_b == "two"))]
    elif damage == "duplicate_cell":
        transitions = pd.concat([transitions, transitions.iloc[:1]])
    elif damage == "stable":
        ranges.loc[0, "tier_stable"] = False
    else:
        ranges.loc[0, "residue_number"] = 99
    with pytest.raises(ValueError, match="[Tt]ier"):
        analysis.validate_tier_counts(long, ranges, transitions)


@pytest.mark.parametrize("optimize", [False, True])
@pytest.mark.parametrize("damage", ["hash", "tier", "counts", "missing_row"])
def test_runtime_guards_fail_nonzero_under_python_optimization(modules, recorded_analysis_inputs, tmp_path, optimize, damage):
    profile, run = recorded_analysis_inputs
    prefix = f"import sys; from pathlib import Path; sys.path.insert(0, {str(SCRIPTS)!r}); import analyze; "
    if damage == "hash":
        path = run / "one/ranked.csv"
        path.write_bytes(path.read_bytes() + b"\n")
        code = prefix + f"analyze.HERE=Path({str(profile)!r}); analyze.analyze(Path({str(run)!r}), None, Path({str(tmp_path/'out')!r}))"
        message = "Input SHA-256 mismatch"
    elif damage == "tier":
        code = prefix + "import pandas as pd; analyze.calculate(pd.DataFrame({'candidate_tier':['invalid']}))"
        message = "Invalid candidate_tier"
    elif damage == "counts":
        # Import the pure synthetic fixture, not pytest execution or real data.
        code = prefix + f"sys.path.insert(0, {str(Path(__file__).parent)!r}); from test_t4l_structure_sensitivity import tier_fixture; "
        code += "x,r,p,t,c=analyze.calculate(tier_fixture()); c.loc[0,'count']+=1; analyze.validate_tier_counts(x,r,c)"
        message = "Tier transition total/coverage invalid"
    else:
        code = prefix + "import pandas as pd; m=pd.DataFrame([dict(pdb_id='one',chain='A',author_residue_number=1,insertion_code='',modeled=True,entity_parent='A',reference_parent='A')]); "
        code += "f=pd.DataFrame(columns=['chain','residue_number','insertion_code','status','candidate_tier']); analyze.common_tables({'one':f},m,Path('.'))"
        message = "Missing scan row for modeled coordinate"
    result = subprocess.run([sys.executable, *(["-O"] if optimize else []), "-B", "-c", code], capture_output=True, text=True)
    assert result.returncode != 0 and message in result.stderr
    assert not (tmp_path / "out").exists()


def test_svg_normalization_is_whitespace_only_and_idempotent(modules, tmp_path):
    path = tmp_path / "plot.svg"
    old = '<svg>  \n<path d="M 0 1 \nL 2 3 " />\t\n</svg>\n'
    path.write_text(old)
    modules["analyze"].normalize_svg(path)
    expected = "\n".join(line.rstrip() for line in old.splitlines()) + "\n"
    assert path.read_text() == expected
    first = path.read_bytes()
    modules["analyze"].normalize_svg(path)
    assert path.read_bytes() == first
