"""Prepare a pinned, already-expanded protein assembly without symmetry expansion.

Local mmCIF / mmCIF.gz input only. The profile pins identity and chain order;
no paper, historical scan, sequence service or host-specific path is needed.
Run with ``python -m ncaa_site_rec.io.prepare_structure --help``.
"""

import argparse
import gzip
import hashlib
import io
import json
import platform
import string
from collections import Counter
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

import numpy as np
from Bio.PDB import MMCIFParser, Model, PDBIO, PDBParser, Structure
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from Bio.PDB.Polypeptide import is_aa
from Bio.SeqUtils import seq1


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def atom_records(model) -> dict:
    """Preserve full identity, including alternate conformers and insertion code."""
    return {
        (chain.id, residue.id, residue.resname, atom.name, atom.altloc, atom.element): atom
        for chain in model for residue in chain
        for atom in residue.get_unpacked_list()
    }


def coordinate_difference(before, after) -> float:
    """Reject identity loss before measuring coordinate serialization error."""
    if before.keys() != after.keys():
        raise ValueError("Atom identities changed during PDB serialization")
    return max((float(np.max(np.abs(before[k].coord - after[k].coord)))
                for k in before), default=0.0)


def prepare_expanded_assembly(
    input_path: Path,
    output_dir: Path,
    profile_path: Path,
    target_source_chain: str | None = None,
    source_record_path: Path | None = None,
) -> dict:
    """Validate and serialize a single expanded model; refuse existing output.

    Chain order is checked against the pinned profile, then mapped bijectively
    to single-character PDB IDs. No coordinate transformation or symmetry
    operation is applied. Output PDBs contain one explicit MODEL 1.
    """
    input_path, output_dir, profile_path = map(Path, (input_path, output_dir, profile_path))
    if output_dir.exists() or output_dir.is_symlink():
        raise FileExistsError(f"Refusing existing output directory: {output_dir}")
    profile_bytes = profile_path.read_bytes()
    profile = json.loads(profile_bytes)
    source_bytes = input_path.read_bytes()
    payload = gzip.decompress(source_bytes) if source_bytes.startswith(b"\x1f\x8b") else source_bytes
    if sha256_bytes(payload) != profile["expanded_mmcif_sha256"]:
        raise ValueError("Expanded mmCIF SHA-256 does not match the profile; do not silently substitute a source revision")
    retrieval = None
    if source_record_path is not None:
        retrieval = json.loads(Path(source_record_path).read_text(encoding="utf-8"))
        if retrieval["sha256"] != sha256_bytes(source_bytes):
            raise ValueError("Retrieval record does not match supplied input bytes")
        if retrieval["url"] != profile["source_url"]:
            raise ValueError("Retrieval URL does not match the explicit public source")
        if not retrieval.get("retrieved_utc"):
            raise ValueError("Retrieval time is missing")
    text = payload.decode("utf-8")
    structure = MMCIFParser(QUIET=True, auth_chains=False).get_structure(
        "expanded", io.StringIO(text),
    )
    if len(structure) != 1:
        raise ValueError("Expected one already-expanded source model; refusing to discard models")
    source_model = next(structure.get_models())
    protein_chains = [c for c in source_model
                      if any(is_aa(r, standard=True) for r in c)]
    chain_ids = [c.id for c in protein_chains]
    if chain_ids != profile["source_chain_ids"]:
        raise ValueError("Protein chain identities/order differ from the pinned expanded assembly profile")
    if not chain_ids or len(chain_ids) > len(string.ascii_uppercase):
        raise ValueError("Single-character chain mapping supports 1..26 chains")
    target = target_source_chain or profile["target_source_chain"]
    if target not in chain_ids:
        raise ValueError(f"Target source chain {target!r} is not a retained protein chain")
    prepared = Structure.Structure("protein_assembly")
    model = Model.Model(0, serial_num=1)
    prepared.add(model)
    mappings, missing_backbone = [], []
    expected_ids = [(" ", n, " ") for n in range(
        profile["author_residue_start"], profile["author_residue_end"] + 1,
    )]
    for source_chain, output_id in zip(protein_chains, string.ascii_uppercase):
        copy = source_chain.copy()
        copy.detach_parent()
        copy.id = output_id
        for residue in list(copy):
            if not is_aa(residue, standard=True):
                copy.detach_child(residue.id)
        residues = list(copy)
        if len(residues) != profile["residues_per_chain"]:
            raise ValueError(f"Unexpected residue count in source chain {source_chain.id}")
        if seq1("".join(r.resname for r in residues)) != profile["sequence"]:
            raise ValueError(f"Unexpected parent sequence in source chain {source_chain.id}")
        if [r.id for r in residues] != expected_ids:
            raise ValueError(f"Unexpected author residue IDs in source chain {source_chain.id}")
        for residue in residues:
            missing = sorted({"N", "CA", "C"} - {a.name for a in residue})
            if missing:
                missing_backbone.append({"chain": output_id, "residue_id": residue.id, "missing": missing})
            # Copying/filtering must not alter any coordinates, before formatting.
            original = source_chain[residue.id]
            if not all(np.array_equal(a.coord, original[a.name].disordered_get(a.altloc).coord
                                      if original[a.name].is_disordered() else original[a.name].coord)
                       for a in residue.get_unpacked_list()):
                raise ValueError("Coordinates changed while copying source atoms")
        model.add(copy)
        mappings.append({"source_assembly_label_asym_id": source_chain.id,
                         "output_pdb_chain_id": output_id, "standard_residues": len(residues)})
    omitted_residues = Counter(r.resname for c in source_model for r in c
                              if not is_aa(r, standard=True))
    omitted_atoms = Counter(a.element for c in source_model for r in c
                           if not is_aa(r, standard=True) for a in r.get_unpacked_list())
    target_id = next(m["output_pdb_chain_id"] for m in mappings
                     if m["source_assembly_label_asym_id"] == target)
    mono = Structure.Structure("protein_monomer")
    mono_model = Model.Model(0, serial_num=1)
    mono.add(mono_model)
    mono_model.add(model[target_id].copy())
    # All source/profile validation above precedes creating an output directory.
    output_dir.mkdir(parents=True, exist_ok=False)
    assembly_path = output_dir / "assembly1_protein.pdb"
    monomer_path = output_dir / "target_monomer.pdb"
    writer = PDBIO(use_model_flag=1)
    for output, value in [(assembly_path, prepared), (monomer_path, mono)]:
        writer.set_structure(value)
        writer.save(str(output))
    parser = PDBParser(QUIET=True)
    reread = parser.get_structure("assembly", assembly_path)
    mono_read = parser.get_structure("monomer", monomer_path)
    if len(reread) != 1 or len(mono_read) != 1:
        raise ValueError("Serialized output must contain exactly one model")
    after = next(reread.get_models())
    mono_after = next(mono_read.get_models())
    error = coordinate_difference(atom_records(model), atom_records(after))
    allowed = profile["comparison_policy_declared_before_execution"]["source_to_PDB_max_abs_coordinate_A"]
    if error > allowed:
        raise ValueError(f"PDB coordinate serialization error {error} exceeds {allowed} Å")
    expected_mono = {k: v for k, v in atom_records(after).items() if k[0] == target_id}
    if coordinate_difference(expected_mono, atom_records(mono_after)) != 0:
        raise ValueError("Monomer coordinates differ from the selected assembly chain")
    if list(after.child_dict) != [m["output_pdb_chain_id"] for m in mappings]:
        raise ValueError("Output chain mapping differs from prepared model")
    manifest = {
        "profile_id": profile["profile_id"], "reference_pdb": profile["reference_pdb"],
        "biological_assembly_id": profile["biological_assembly_id"],
        "prepared_utc": datetime.now(timezone.utc).isoformat(),
        "input": {"file": str(input_path), "sha256": sha256_bytes(source_bytes),
                  "expanded_mmcif_sha256": sha256_bytes(payload),
                  "source_entry_id": MMCIF2Dict(io.StringIO(text)).get("_entry.id"),
                  "retrieval": retrieval, "profile_source_url": profile["source_url"],
                  "retrieval_status": "verified record supplied" if retrieval else "local input; retrieval time not asserted"},
        "profile_sha256": sha256_bytes(profile_bytes),
        "preparation_module_sha256": sha256_bytes(Path(__file__).read_bytes()),
        "environment": {"python": platform.python_version(), "biopython": version("biopython"), "numpy": np.__version__},
        "model_count": 1, "explicit_MODEL_serial": 1,
        "chain_mapping": mappings, "target_source_chain": target, "target_output_chain": target_id,
        "total_protein_residues": sum(len(c) for c in model),
        "protein_atoms_including_altlocs": len(atom_records(model)),
        "missing_backbone": missing_backbone,
        "nonprotein_policy": "Drop all nonstandard/nonprotein residues, including water, metals and ligands; retain standard protein residues and their atom/altloc records. No hydrogen addition/removal.",
        "omitted_residue_counts": dict(omitted_residues), "omitted_atom_element_counts": dict(omitted_atoms),
        "coordinate_policy": "No transform, symmetry application, relaxation or reconstruction; only PDB numeric formatting, audited by atom identity.",
        "maximum_coordinate_serialization_change_A": error,
        "scan_configuration": {**profile["scan"], "chain": target_id},
        "identity_limit": profile.get("identity_limit", ""),
        "outputs": {p.name: {"sha256": sha256_bytes(p.read_bytes()), "bytes": p.stat().st_size}
                    for p in [assembly_path, monomer_path]},
    }
    (output_dir / "preparation.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Official already-expanded mmCIF or mmCIF.gz")
    parser.add_argument("--profile", type=Path, required=True, help="Pinned preparation/configuration JSON")
    parser.add_argument("--output-dir", type=Path, required=True, help="New directory; existing paths are refused")
    parser.add_argument("--target-source-chain", default=None)
    parser.add_argument("--source-record", type=Path, default=None, help="Optional URL/time/SHA-256 retrieval JSON")
    args = parser.parse_args(argv)
    result = prepare_expanded_assembly(args.input, args.output_dir, args.profile,
                                      args.target_source_chain, args.source_record)
    print(json.dumps({k: result[k] for k in ["model_count", "target_output_chain", "total_protein_residues", "protein_atoms_including_altlocs"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
