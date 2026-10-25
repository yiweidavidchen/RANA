"""Portable preparation must preserve identities/coordinates and reject ambiguity."""
import gzip
import hashlib
import json

import numpy as np
import pytest
from Bio.PDB import Atom, Chain, MMCIFIO, MMCIFParser, Model, PDBParser, Residue, Structure
from Bio.PDB.Atom import DisorderedAtom

from ncaa_site_rec.io.prepare_structure import (
    atom_records,
    coordinate_difference,
    prepare_expanded_assembly,
)


@pytest.fixture
def source(tmp_path):
    structure = Structure.Structure("fixture")
    model = Model.Model(0, serial_num=1)
    structure.add(model)
    for chain_id, shift in [("A", 0.0), ("B", 10.0)]:
        chain = Chain.Chain(chain_id)
        model.add(chain)
        residue = Residue.Residue((" ", 5, " "), "ALA", "")
        chain.add(residue)
        for serial, (name, xyz) in enumerate([
            ("N", [0.0, 1.0, 0.0]), ("CA", [0.0, 0.0, 0.0]),
            ("C", [1.5, 0.0, 0.0]), ("O", [2.0, -1.0, 0.0]),
        ], 1):
            residue.add(Atom.Atom(name, np.array(xyz) + shift, 20.0, 1.0,
                                  " ", name.rjust(4), serial, element=name[0]))
    chain = Chain.Chain("C")
    model.add(chain)
    for number, (name, flag, element) in enumerate([
        ("HOH", "W", "O"), ("CS", "H_CS", "CS"),
    ], 1):
        residue = Residue.Residue((flag, number, " "), name, "")
        chain.add(residue)
        residue.add(Atom.Atom(element, np.array([30., number, 0.]), 20., 1.,
                              " ", element.rjust(4), 20+number, element=element))
    path = tmp_path / "expanded.cif"
    writer = MMCIFIO()
    writer.set_structure(structure)
    writer.save(str(path))
    profile = {
        "profile_id": "synthetic", "reference_pdb": "TEST", "biological_assembly_id": "1",
        "source_url": "https://example.invalid/fixture.cif",
        "expanded_mmcif_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "source_chain_ids": ["A", "B"], "residues_per_chain": 1,
        "author_residue_start": 5, "author_residue_end": 5, "sequence": "A",
        "target_source_chain": "A", "scan": {"chain": "A"},
        "comparison_policy_declared_before_execution": {"source_to_PDB_max_abs_coordinate_A": 0.0006},
    }
    config = tmp_path / "profile.json"
    config.write_text(json.dumps(profile), encoding="utf-8")
    return path, config, profile


@pytest.mark.parametrize("compressed", [False, True])
def test_expanded_coordinates_and_identity_are_not_transformed(source, tmp_path, compressed):
    path, config, profile = source
    if compressed:
        compressed_path = tmp_path / "expanded.cif.gz"
        compressed_path.write_bytes(gzip.compress(path.read_bytes()))
        path = compressed_path
    out = tmp_path / "new"
    manifest = prepare_expanded_assembly(path, out, config, target_source_chain="B")
    assembly = PDBParser(QUIET=True).get_structure("a", out / "assembly1_protein.pdb")
    monomer = PDBParser(QUIET=True).get_structure("m", out / "target_monomer.pdb")
    assert len(assembly) == len(monomer) == 1
    assert list(assembly[0].child_dict) == ["A", "B"]
    assert list(monomer[0].child_dict) == ["B"]
    assert len(atom_records(assembly[0])) == 8
    assert manifest["target_source_chain"] == manifest["target_output_chain"] == "B"
    assert manifest["omitted_residue_counts"] == {"HOH": 1, "CS": 1}
    assert manifest["maximum_coordinate_serialization_change_A"] == 0
    np.testing.assert_array_equal(assembly[0]["A"][5]["N"].coord, [0., 1., 0.])
    np.testing.assert_array_equal(assembly[0]["B"][5]["N"].coord, [10., 11., 10.])
    for filename in ["assembly1_protein.pdb", "target_monomer.pdb"]:
        text = (out / filename).read_text()
        assert sum(line.startswith("MODEL ") for line in text.splitlines()) == 1
        assert sum(line.startswith("ENDMDL") for line in text.splitlines()) == 1
    assert manifest["input"]["expanded_mmcif_sha256"] == profile["expanded_mmcif_sha256"]


def test_existing_output_is_never_overwritten(source, tmp_path):
    path, config, _ = source
    out = tmp_path / "existing"
    out.mkdir()
    sentinel = out / "sentinel"
    sentinel.write_text("preserve me")
    with pytest.raises(FileExistsError, match="Refusing"):
        prepare_expanded_assembly(path, out, config)
    assert sentinel.read_text() == "preserve me"
    assert list(out.iterdir()) == [sentinel]


@pytest.mark.parametrize("mutation", ["hash", "chain_order", "sequence", "residue_id", "target"])
def test_profile_mismatch_rejected_before_output(source, tmp_path, mutation):
    path, config, profile = source
    target = None
    if mutation == "hash":
        profile["expanded_mmcif_sha256"] = "0" * 64
    elif mutation == "chain_order":
        profile["source_chain_ids"] = ["B", "A"]
    elif mutation == "sequence":
        profile["sequence"] = "G"
    elif mutation == "residue_id":
        profile["author_residue_start"] = profile["author_residue_end"] = 6
    else:
        target = "Z"
    config.write_text(json.dumps(profile), encoding="utf-8")
    out = tmp_path / "rejected"
    with pytest.raises(ValueError):
        prepare_expanded_assembly(path, out, config, target_source_chain=target)
    assert not out.exists()


def test_multiple_models_are_not_silently_dropped(source, tmp_path):
    path, config, profile = source
    structure = MMCIFParser(QUIET=True, auth_chains=False).get_structure("two", path)
    second = structure[0].copy()
    second.id = 1
    second.serial_num = 2
    structure.add(second)
    writer = MMCIFIO()
    writer.set_structure(structure)
    writer.save(str(path))
    profile["expanded_mmcif_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    config.write_text(json.dumps(profile), encoding="utf-8")
    with pytest.raises(ValueError, match="one already-expanded source model"):
        prepare_expanded_assembly(path, tmp_path / "rejected", config)


def test_atom_identity_loss_is_not_a_coordinate_tolerance(source, tmp_path):
    path, config, _ = source
    prepare_expanded_assembly(path, tmp_path / "new", config)
    model = PDBParser(QUIET=True).get_structure("a", tmp_path / "new/assembly1_protein.pdb")[0]
    before = atom_records(model)
    missing = dict(before)
    missing.pop(next(iter(missing)))
    with pytest.raises(ValueError, match="Atom identities"):
        coordinate_difference(before, missing)


@pytest.mark.parametrize("field", ["sha256", "url", "retrieved_utc"])
def test_incorrect_retrieval_record_rejected(source, tmp_path, field):
    path, config, profile = source
    record = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
              "url": profile["source_url"], "retrieved_utc": "2026-10-24T00:00:00+00:00"}
    record[field] = "" if field == "retrieved_utc" else "incorrect"
    metadata = tmp_path / "retrieval.json"
    metadata.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(ValueError):
        prepare_expanded_assembly(path, tmp_path / "rejected", config, source_record_path=metadata)
    assert not (tmp_path / "rejected").exists()


def test_alternate_atom_identities_and_occupancies_are_retained(source, tmp_path):
    path, config, profile = source
    structure = MMCIFParser(QUIET=True, auth_chains=False).get_structure("alt", path)
    alternate = DisorderedAtom("CB")
    for altloc, occupancy, coordinate in [("A", 0.6, 1.0), ("B", 0.4, 2.0)]:
        alternate.disordered_add(Atom.Atom(
            "CB", np.array([coordinate] * 3), 20., occupancy, altloc, " CB ", 30, element="C",
        ))
    structure[0]["A"][5].add(alternate)
    writer = MMCIFIO()
    writer.set_structure(structure)
    writer.save(str(path))
    profile["expanded_mmcif_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    config.write_text(json.dumps(profile), encoding="utf-8")
    out = tmp_path / "new"
    manifest = prepare_expanded_assembly(path, out, config)
    assembly = PDBParser(QUIET=True).get_structure("a", out / "assembly1_protein.pdb")
    cb = assembly[0]["A"][5]["CB"]
    assert cb.disordered_get("A").occupancy == 0.6
    assert cb.disordered_get("B").occupancy == 0.4
    assert manifest["protein_atoms_including_altlocs"] == 10
    assert manifest["maximum_coordinate_serialization_change_A"] == 0
