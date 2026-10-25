"""Audit a bounded T4L shortlist from local official PDB/mmCIF/API files."""
import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np
from Bio.PDB import PDBParser
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from Bio.PDB.Polypeptide import is_aa
from Bio.SeqUtils import seq1

CANDIDATES = ["1L63", "1LW9", "219L", "2LZM", "1L97"]
SELECTED = ["1L63", "1LW9", "219L"]
SIDECHAINS = {
    "ALA": "CB", "ARG": "CB CG CD NE CZ NH1 NH2", "ASN": "CB CG OD1 ND2",
    "ASP": "CB CG OD1 OD2", "CYS": "CB SG", "GLN": "CB CG CD OE1 NE2",
    "GLU": "CB CG CD OE1 OE2", "GLY": "", "HIS": "CB CG ND1 CD2 CE1 NE2",
    "ILE": "CB CG1 CG2 CD1", "LEU": "CB CG CD1 CD2", "LYS": "CB CG CD CE NZ",
    "MET": "CB CG SD CE", "PHE": "CB CG CD1 CD2 CE1 CE2 CZ", "PRO": "CB CG CD",
    "SER": "CB OG", "THR": "CB OG1 CG2", "TRP": "CB CG CD1 CD2 NE1 CE2 CE3 CZ2 CZ3 CH2",
    "TYR": "CB CG CD1 CD2 CE1 CE2 CZ OH", "VAL": "CB CG1 CG2",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path, rows):
    if not rows:
        raise ValueError("Cannot write a table without defined fields")
    with path.open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def protein_atoms(model):
    return {(c.id, r.id[1], r.id[2].strip(), r.resname, a.name, a.altloc.strip()): a
            for c in model for r in c if is_aa(r, standard=True)
            for a in r.get_unpacked_list() if a.element not in {"H", "D"}}


def cif_atoms(cif):
    fields = ["group_PDB", "auth_asym_id", "auth_seq_id", "pdbx_PDB_ins_code", "auth_comp_id",
              "auth_atom_id", "label_alt_id", "Cartn_x", "Cartn_y", "Cartn_z", "type_symbol", "pdbx_PDB_model_num"]
    atoms = {}
    for row in zip(*(cif["_atom_site." + f] for f in fields)):
        group, chain, num, ins, parent, name, alt, x, y, z, element, model = row
        if group != "ATOM" or element in {"H", "D"} or model != "1":
            continue
        key = (chain, int(num), "" if ins in {"?", "."} else ins, parent, name,
               "" if alt in {"?", "."} else alt)
        if key in atoms:
            raise ValueError(f"Duplicate mmCIF atom identity {key}")
        atoms[key] = np.array([x, y, z], dtype=float)
    return atoms


def inspect(pdb_id, sources, reference_sequence):
    pdb = sources / f"{pdb_id}.pdb"
    cif = MMCIF2Dict(str(sources / f"{pdb_id}.cif"))
    entry = json.loads((sources / f"{pdb_id}_entry.json").read_text())
    entity = json.loads((sources / f"{pdb_id}_entity.json").read_text())
    sequence = entity["entity_poly"]["pdbx_seq_one_letter_code_can"].replace("\n", "")
    if len(sequence) != len(reference_sequence):
        raise ValueError("Shortlist numbering audit expects equal 164-residue entity sequences")
    structure = PDBParser(QUIET=True).get_structure(pdb_id, pdb)
    if len(structure) != 1:
        raise ValueError("Shortlist requires a single experimental model")
    model = structure[0]
    atoms, coordinate_atoms = protein_atoms(model), cif_atoms(cif)
    if atoms.keys() != coordinate_atoms.keys():
        raise ValueError(f"{pdb_id}: PDB/mmCIF protein atom identities differ")
    delta = max(float(np.max(np.abs(a.coord - coordinate_atoms[k]))) for k, a in atoms.items())
    if not np.isfinite(delta) or delta > 0.0006:
        raise ValueError(f"{pdb_id}: PDB/mmCIF coordinate mismatch {delta}")
    differences = [f"{a}{i}{b}" for i, (a, b) in enumerate(zip(reference_sequence, sequence), 1) if a != b]
    chains, mapping, missing_atoms, selected_altlocs = {}, [], {}, {}
    for chain in model:
        residues = {r.id[1]: r for r in chain if is_aa(r, standard=True)}
        if not residues:
            continue
        if any(r.id[2].strip() or not 1 <= r.id[1] <= 164 for r in residues.values()):
            raise ValueError(f"{pdb_id}: nontrivial author numbering needs a separate mapping")
        tokens = [res for line in pdb.read_text().splitlines() if line.startswith("SEQRES")
                  and line[11] == chain.id for res in line[19:].split()]
        seqres = "".join(seq1(name) for name in tokens)
        if seqres != sequence:
            raise ValueError(f"{pdb_id} chain {chain.id}: SEQRES/entity mismatch")
        absent = sorted(set(range(1, 165)) - residues.keys())
        for n in range(1, 165):
            residue = residues.get(n)
            missing, altlocs = [], []
            if residue is not None:
                if seq1(residue.resname) != sequence[n - 1]:
                    raise ValueError(f"{pdb_id} {chain.id}{n}: coordinate parent/entity mismatch")
                expected_atoms = {"N", "CA", "C", "O"} | set(SIDECHAINS[residue.resname].split())
                missing = sorted(expected_atoms - {a.name for a in residue})
                altlocs = [f"{a.name}:{a.altloc.strip()}" for a in residue if a.is_disordered()]
                if missing:
                    missing_atoms[f"{chain.id}:{n}"] = missing
                if altlocs:
                    selected_altlocs[f"{chain.id}:{n}"] = altlocs
            mapping.append({"pdb_id": pdb_id, "chain": chain.id, "canonical_position": n,
                            "author_residue_number": n, "insertion_code": "",
                            "entity_parent": sequence[n - 1], "reference_parent": reference_sequence[n - 1],
                            "coordinate_parent": residue.resname if residue is not None else "",
                            "modeled": residue is not None, "missing_heavy_atoms": ";".join(missing),
                            "selected_altloc_atoms": ";".join(altlocs),
                            "mapping_basis": "PDB SEQRES and coordinate parent; author number equals entity sequence index; mmCIF atom identity cross-check"})
        chains[chain.id] = {"modeled_residues": len(residues), "missing_residue_numbers": absent,
                            "coordinate_sequence": "".join(seq1(r.resname) for r in residues.values())}
    categories = {prefix: {k: v for k, v in cif.items() if k.startswith(prefix)}
                  for prefix in ["_pdbx_struct_assembly.", "_pdbx_struct_assembly_gen.", "_pdbx_struct_oper_list.",
                                 "_pdbx_unobs_or_zero_occ_residues.", "_pdbx_unobs_or_zero_occ_atoms.", "_exptl_crystal_grow."]}
    nonprotein = dict(Counter(r.resname for r in model.get_residues() if not is_aa(r, standard=True)))
    reasons = {"1L63": "Historical M5 reference; retain despite missing terminal residues.",
               "1LW9": "Same full C54T/C97A sequence, complete chain A, 1.45-A X-ray reference; alternate atoms retained with frozen parser selection.",
               "219L": "Same full C54T/C97A sequence, complete chain A, 1.66-A X-ray reference; title concerns a mutant series, but this entry sequence has no extra substitution/insertion/deletion.",
               "2LZM": "Excluded: native C54/C97 background differs from 1L63. Not a pure same-background comparison; no supplemental scan needed to reach three structures.",
               "1L97": "Excluded: I3P plus native C54/C97 background and two ASU protein chains. Not a same-background comparison."}
    info = {"pdb_id": pdb_id, "selected": pdb_id in SELECTED, "reason": reasons[pdb_id],
            "source_page": f"https://www.rcsb.org/structure/{pdb_id}", "pdb_doi": f"https://doi.org/10.2210/pdb{pdb_id}/pdb",
            "title": entry["struct"]["title"], "methods": [e["method"] for e in entry["exptl"]],
            "resolution_A": entry["rcsb_entry_info"]["resolution_combined"], "full_entity_sequence": sequence,
            "sequence_sha256": hashlib.sha256(sequence.encode()).hexdigest(), "differences_from_1L63": differences,
            "seqadv_records": [s for s in pdb.read_text().splitlines() if s.startswith("SEQADV")],
            "chains": chains, "target_chain": "A", "models": len(structure),
            "missing_heavy_atoms": missing_atoms, "selected_altloc_atoms": selected_altlocs,
            "atom_altloc_counts": dict(Counter(k[-1] or "blank" for k in atoms)),
            "zero_occupancy_atom_count": sum(a.occupancy == 0 for a in atoms.values()),
            "excluded_nonprotein_residue_counts": nonprotein, "official_mmcif_categories": categories,
            "pdb_mmcif_max_abs_coordinate_difference_A": delta,
            "heavy_atom_template_policy": "Standard heavy atoms N/CA/C/O plus residue sidechain; optional terminal OXT and hydrogen atoms are not required.",
            "pdb_sha256": sha(pdb), "cif_sha256": sha(sources / f"{pdb_id}.cif")}
    return info, mapping


def audit(sources, output):
    if output.exists():
        raise FileExistsError(output)
    sequence = json.loads((sources / "1L63_entity.json").read_text())["entity_poly"]["pdbx_seq_one_letter_code_can"].replace("\n", "")
    infos, mapping = [], []
    for pdb in CANDIDATES:
        info, rows = inspect(pdb, sources, sequence)
        infos.append(info)
        mapping.extend(rows)
    output.mkdir(parents=True, exist_ok=False)
    (output / "structure_audit.json").write_text(json.dumps(infos, indent=2) + "\n", encoding="utf-8")
    write_csv(output / "site_mapping.csv", mapping)
    rows = [{"pdb_id": i["pdb_id"], "selected": i["selected"], "reason": i["reason"],
             "methods": ";".join(i["methods"]), "resolution_A": ";".join(map(str, i["resolution_A"])),
             "full_entity_sequence": i["full_entity_sequence"], "sequence_sha256": i["sequence_sha256"],
             "differences_from_1L63": ";".join(i["differences_from_1L63"]),
             "protein_chains": ";".join(i["chains"]), "target_chain": "A",
             "modeled_residues_A": i["chains"]["A"]["modeled_residues"],
             "missing_residues_A": ";".join(map(str, i["chains"]["A"]["missing_residue_numbers"])),
             "residues_with_missing_heavy_atoms": len(i["missing_heavy_atoms"]),
             "residues_with_selected_altlocs": len(i["selected_altloc_atoms"]),
             "omitted_nonprotein_counts": json.dumps(i["excluded_nonprotein_residue_counts"]),
             "source_locator": "structure_audit.json; official PDB/mmCIF and RCSB entry/entity JSON",
             "source_page": i["source_page"], "pdb_sha256": i["pdb_sha256"], "cif_sha256": i["cif_sha256"]} for i in infos]
    write_csv(output / "structure_selection.csv", rows)
    print(json.dumps([{k: i[k] for k in ["pdb_id", "chains", "missing_heavy_atoms", "selected_altloc_atoms"]} for i in infos], indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    audit(args.sources, args.output)
