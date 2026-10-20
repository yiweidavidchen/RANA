import json

import pandas as pd

from ncaa_site_rec.io.run_metadata import (
    build_run_metadata,
    sha256_file,
    write_run_metadata,
)


def test_sha256_file_is_deterministic(tmp_path):
    pdb = tmp_path / "example.pdb"
    pdb.write_bytes(b"TEST STRUCTURE\n")

    first = sha256_file(pdb)
    second = sha256_file(pdb)

    assert first == second
    assert len(first) == 64


def test_metadata_records_configuration_and_results(tmp_path):
    pdb = tmp_path / "example.pdb"
    pdb.write_text("TEST STRUCTURE\n")

    result = pd.DataFrame({
        "status": ["scored", "scored", "skipped"],
        "candidate_tier": [
            "geometry_favorable",
            "geometry_limited",
            "not_evaluated",
        ],
        "n_rotamers": [12, 12, 0],
    })

    metadata = build_run_metadata(
        pdb_path=pdb,
        chain="A",
        ncaa="pazf",
        seed=42,
        low_clash_threshold=10.0,
        favorable_fraction=0.5,
        result=result,
    )

    assert metadata["input"]["pdb_sha256"] == sha256_file(pdb)
    assert metadata["configuration"]["seed"] == 42
    assert metadata["results"]["n_residues"] == 3
    assert metadata["results"]["status_counts"]["scored"] == 2
    assert metadata["sampling"]["n_rotamers_observed"] == [0, 12]


def test_metadata_json_roundtrip(tmp_path):
    output = tmp_path / "nested" / "run.metadata.json"

    metadata = {
        "tool": "RANA",
        "schema_version": "1.0",
    }

    write_run_metadata(metadata, output)

    assert output.is_file()

    loaded = json.loads(output.read_text(encoding="utf-8"))
    assert loaded == metadata

def test_git_revision_schema():
    from ncaa_site_rec.io.run_metadata import get_git_revision

    revision = get_git_revision()

    assert set(revision) == {
        "git_commit",
        "tracked_worktree_modified",
    }

    assert (
        revision["git_commit"] is None
        or len(revision["git_commit"]) == 40
    )

    assert revision["tracked_worktree_modified"] in {
        True, False, None
    }