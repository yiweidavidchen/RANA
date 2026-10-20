import pytest
import json

from ncaa_site_rec.cli import build_parser, main


def test_rank_parser_defaults():
    parser = build_parser()

    args = parser.parse_args([
        "rank",
        "--pdb", "example.pdb",
        "--ncaa", "pazf",
        "--output", "results.csv",
    ])

    assert args.command == "rank"
    assert args.chain == "A"
    assert args.seed == 42
    assert args.low_clash_threshold == 10.0
    assert args.favorable_fraction == 0.5


def test_rank_rejects_unsupported_ncaa(tmp_path):
    pdb = tmp_path / "example.pdb"
    pdb.write_text("")

    with pytest.raises(SystemExit, match="currently supports"):
        main([
            "rank",
            "--pdb", str(pdb),
            "--ncaa", "unknown",
            "--output", str(tmp_path / "out.csv"),
        ])


@pytest.mark.parametrize(
    "threshold",
    ["-1", "nan", "inf"],
)
def test_rank_rejects_invalid_threshold(tmp_path, threshold):
    pdb = tmp_path / "example.pdb"
    pdb.write_text("")

    with pytest.raises(SystemExit, match="low-clash-threshold"):
        main([
            "rank",
            "--pdb", str(pdb),
            "--ncaa", "pazf",
            "--low-clash-threshold", threshold,
            "--output", str(tmp_path / "out.csv"),
        ])


@pytest.mark.parametrize(
    "fraction",
    ["0", "1.5", "nan"],
)
def test_rank_rejects_invalid_fraction(tmp_path, fraction):
    pdb = tmp_path / "example.pdb"
    pdb.write_text("")

    with pytest.raises(SystemExit, match="favorable-fraction"):
        main([
            "rank",
            "--pdb", str(pdb),
            "--ncaa", "pazf",
            "--favorable-fraction", fraction,
            "--output", str(tmp_path / "out.csv"),
        ])


def test_rank_rejects_legacy_site_arguments(tmp_path):
    pdb = tmp_path / "example.pdb"
    pdb.write_text("")

    with pytest.raises(SystemExit, match="legacy placeholders"):
        main([
            "rank",
            "--pdb", str(pdb),
            "--ncaa", "pazf",
            "--catalytic-residues", "11",
            "--output", str(tmp_path / "out.csv"),
        ])


def test_rank_rejects_invalid_functional_residue(tmp_path):
    pdb = tmp_path / "example.pdb"
    pdb.write_text("")

    with pytest.raises(SystemExit, match="Invalid functional residue"):
        main([
            "rank",
            "--pdb", str(pdb),
            "--ncaa", "pazf",
            "--functional-residues", "11",
            "--output", str(tmp_path / "out.csv"),
        ])

import pandas as pd


def test_rank_writes_complete_csv(tmp_path, monkeypatch):
    import ncaa_site_rec.cli as cli

    fake_result = pd.DataFrame({
        "chain": ["A", "A"],
        "residue_number": [10, 11],
        "residue_name": ["ALA", "GLY"],
        "status": ["scored", "scored"],
        "min_steric_score": [0.5, 12.0],
        "n_rotamers": [12, 12],
        "candidate_tier": [
            "geometry_favorable",
            "geometry_unfavorable",
        ],
        "special_residue_flag": [
            "",
            "glycine_backbone_caution",
        ],
    })

    captured = {}

    def fake_pipeline(**kwargs):
        captured.update(kwargs)
        return fake_result.copy()

    monkeypatch.setattr(
        cli,
        "build_ranked_pazf_table",
        fake_pipeline,
    )

    pdb = tmp_path / "example.pdb"
    pdb.write_text("TEST PDB")

    output = tmp_path / "nested" / "results.csv"

    exit_code = cli.main([
        "rank",
        "--pdb", str(pdb),
        "--ncaa", "pazf",
        "--chain", "A",
        "--seed", "123",
        "--low-clash-threshold", "5.0",
        "--favorable-fraction", "0.75",
        "--output", str(output),
    ])

    assert exit_code == 0
    assert output.is_file()

    exported = pd.read_csv(output, keep_default_na=False)

    assert len(exported) == 2
    assert exported["residue_number"].tolist() == [10, 11]
    assert exported["candidate_tier"].tolist() == [
        "geometry_favorable",
        "geometry_unfavorable",
    ]

    assert captured["chain"] == "A"
    assert captured["seed"] == 123
    assert captured["low_clash_threshold"] == 5.0
    assert captured["favorable_fraction"] == 0.75

    metadata_path = output.with_suffix(".metadata.json")

    assert metadata_path.is_file()

    metadata = json.loads(
        metadata_path.read_text(encoding="utf-8")
    )

    assert metadata["tool"] == "RANA"
    assert metadata["input"]["chain"] == "A"
    assert metadata["configuration"]["seed"] == 123
    assert metadata["configuration"]["low_clash_threshold"] == 5.0
    assert metadata["configuration"]["favorable_fraction"] == 0.75
    assert metadata["configuration"]["functional_residues"] is None
    assert metadata["results"]["n_residues"] == 2

    from ncaa_site_rec.io.run_metadata import sha256_file

    assert metadata["output"]["csv_sha256"] == sha256_file(output)
    assert metadata["output"]["csv_path"] == str(output)

    assert "software" in metadata
    assert "git_commit" in metadata["software"]
    assert "tracked_worktree_modified" in metadata["software"]