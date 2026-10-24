"""Prepare a provenance-audited hFTL reference environment; no RANA scoring changes.

Run from the repository root with the existing RANA development environment.
The official mmCIF inputs must already be present at the recorded paths.
"""

import hashlib
import json
import string
import subprocess
from collections import Counter
from pathlib import Path

import numpy as np
from Bio.PDB import MMCIFParser, Model, PDBIO, PDBParser, Structure
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from Bio.PDB.Polypeptide import is_aa
from Bio.SeqUtils import seq1

RAW = Path('data/raw/khoshnejad2018_hftl')
OUT = Path('data/processed/khoshnejad2018_hftl')
ASSEMBLY = RAW / '2FG8-assembly1.cif'
ASU = RAW / '2FG8_asymmetric_unit.cif'
SITES = {2: 'SER', 5: 'ILE', 9: 'TYR', 79: 'PHE', 83: 'LYS',
         105: 'LYS', 112: 'LEU', 155: 'LEU'}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def selected_atoms(model):
    return {(c.id, r.id, a.name): a for c in model for r in c
            if is_aa(r, standard=True) for a in r.get_atoms()}


def prepare():
    OUT.mkdir(parents=True, exist_ok=True)
    paths = subprocess.check_output(
        ['git', '--no-optional-locks', 'ls-files', '--cached', '--others', '--exclude-standard'],
        text=True,
    ).splitlines()
    # Preserve unrelated working-tree files and existing public example inputs/outputs.
    protected = [Path(p) for p in paths if not p.startswith('docs/benchmarks/khoshnejad2018_hftl')]
    protected.extend(p for folder in [Path('data/raw'), Path('data/processed')]
                     for p in folder.glob('*') if p.is_file())
    baseline = {str(p): sha256(p) for p in protected}
    (OUT / 'protected_files_before.json').write_text(json.dumps(baseline, indent=2), encoding='utf-8')

    source = MMCIFParser(QUIET=True, auth_chains=False).get_structure('official', ASSEMBLY)
    assert len(source) == 1, 'Do not silently drop assembly models'
    original = next(source.get_models())
    protein_chains = [c for c in original if any(is_aa(r, standard=True) for r in c)]
    assert len(protein_chains) == 24
    uniprot = ''.join(line.strip() for line in (RAW / 'P02792.fasta').read_text().splitlines()
                      if not line.startswith('>'))
    declared = ''.join(MMCIF2Dict(ASU)['_entity_poly.pdbx_seq_one_letter_code_can'][0].split())
    assert len(uniprot) == 175 and len(declared) == 174 and declared == uniprot[1:]

    prepared = Structure.Structure('reference_24mer')
    model = Model.Model(0)
    prepared.add(model)
    mapping = []
    missing_backbone = []
    for chain, new_id in zip(protein_chains, string.ascii_uppercase):
        copy = chain.copy()
        copy.detach_parent()
        copy.id = new_id
        for residue in list(copy):
            if not is_aa(residue, standard=True):
                copy.detach_child(residue.id)
        residues = list(copy)
        assert len(residues) == 174 and seq1(''.join(r.resname for r in residues)) == declared
        assert [r.id for r in residues] == [(' ', n, ' ') for n in range(5, 179)]
        for residue in residues:
            missing = sorted({'N', 'CA', 'C'} - {a.name for a in residue.get_atoms()})
            if missing:
                missing_backbone.append({'chain': new_id, 'residue_id': residue.id, 'missing': missing})
        model.add(copy)
        source_chain, sep, operation = chain.id.partition('-')
        mapping.append({'source_assembly_label_asym_id': chain.id,
                        'source_asymmetric_unit_label_asym_id': source_chain,
                        'assembly_operation_id': operation if sep else '1',
                        'prepared_pdb_chain_id': new_id, 'standard_residues': len(residues)})
    assert mapping[0]['source_assembly_label_asym_id'] == 'A'
    assembly_pdb = RAW / '2FG8_assembly1_protein_A-X.pdb'
    mono_pdb = RAW / '2FG8_monomer_A.pdb'
    assert not assembly_pdb.exists() and not mono_pdb.exists(), 'Refuse to overwrite prepared inputs'
    io = PDBIO()
    io.set_structure(prepared)
    io.save(str(assembly_pdb))
    monomer = Structure.Structure('reference_monomer')
    mono_model = Model.Model(0)
    monomer.add(mono_model)
    mono_model.add(model['A'].copy())
    io.set_structure(monomer)
    io.save(str(mono_pdb))

    reread = next(PDBParser(QUIET=True).get_structure('reread', assembly_pdb).get_models())
    assert len(reread) == 24 and [c.id for c in reread] == list(string.ascii_uppercase[:24])
    before, after = selected_atoms(model), selected_atoms(reread)
    assert before.keys() == after.keys()
    max_coordinate_change = max(float(np.max(np.abs(before[k].coord - after[k].coord))) for k in before)
    assert max_coordinate_change <= 0.0006, max_coordinate_change
    mono = next(PDBParser(QUIET=True).get_structure('mono', mono_pdb).get_models())
    assert len(mono) == 1
    assert all(np.array_equal(a.coord, mono['A'][r.id][a.name].coord)
               for r in reread['A'] for a in r.get_atoms())
    elements = Counter(a.element for a in after.values())
    assert set(elements) <= {'C', 'N', 'O', 'S', 'H', 'D'}, elements
    residue_mapping = []
    for residue in reread['A']:
        position = residue.id[1] - 3
        assert seq1(residue.resname) == uniprot[position - 1]
        residue_mapping.append({'reference_uniprot_position': position, 'pdb_author_chain': 'A',
                                'pdb_author_residue_number': residue.id[1], 'insertion_code': '',
                                'parent_residue': residue.resname,
                                'literature_position_candidate': position if position in SITES else None,
                                'literature_site_parent_match': residue.resname == SITES[position]
                                if position in SITES else None})
    assert all(r['literature_site_parent_match'] for r in residue_mapping
               if r['literature_position_candidate'] is not None)
    # Quantify real cross-subunit contacts without modifying the screening algorithm.
    target_ca = np.array([r['CA'].coord for r in reread['A']])
    other_ca = np.array([r['CA'].coord for c in reread if c.id != 'A' for r in c])
    cross_counts = ((target_ca[:, None, :] - other_ca[None, :, :]) ** 2).sum(axis=2) < 8.0 ** 2
    cross_counts = cross_counts.sum(axis=1)
    manifest = {
        'reference_pdb': '2FG8', 'biological_assembly_id': '1',
        'identity_status': 'maintainer_authorized_reference; authors_exact_PDB_not_confirmed',
        'experimental_construct': 'hFTL full-length cDNA SC120074 in pRSET A; full expressed fusion/junction/tag sequence unconfirmed',
        'literature_numbering_status': 'eight SI Figure S1 parent identities match UniProt positions; full construct equivalence unconfirmed',
        'mapping_evidence': 'deposited entity sequence exactly equals current P02792 residues 2..175; observed author IDs 5..178; no arbitrary offset assumed',
        'legacy_alignment_warning': 'mmCIF _struct_ref_seq db_align_beg/end=1/174 disagrees with current P02792 175-aa sequence; use saved sequence and full residue mapping instead',
        'background_mutations': 'no substitutions relative to current P02792 residues 2..175; initiator Met1 absent from deposited entity',
        'missing_coordinates_relative_to_deposited_entity': [],
        'missing_reference_positions': [{'uniprot_position': 1, 'residue': 'MET', 'reason': 'not in deposited entity; not rebuilt; no scan output row'}],
        'incomplete_backbone_residues': missing_backbone,
        'model_count': 1, 'retained_protein_chains': list(string.ascii_uppercase[:24]),
        'target_chain': 'A', 'residues_per_chain': 174, 'total_protein_residues': 4176,
        'selected_protein_atom_count': len(after), 'selected_elements': dict(elements),
        'all_environment_nonprotein_residue_counts_before_filter': dict(Counter(
            r.resname for c in original for r in c if not is_aa(r, standard=True))),
        'preparation': 'official expanded assembly coordinates; retain standard protein residues; bijective chain IDs A-X; preserve residue IDs/altloc records; PDB precision only; no relaxation, sequence mutation, missing-atom modeling, or custom symmetry',
        'maximum_selected_coordinate_rounding_A': max_coordinate_change,
        'chain_mapping': mapping, 'residue_mapping': residue_mapping,
        'target_sites_with_other_subunit_CA_within_strict_8A': int((cross_counts > 0).sum()),
        'maximum_cross_subunit_CA_neighbors': int(cross_counts.max()),
        'cross_subunit_CA_counts_by_target_author_residue': {str(r.id[1]): int(n) for r, n in zip(reread['A'], cross_counts)},
        'git_commit': subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        'configuration': {'ncaa':'pazf','seed':42,'low_clash_threshold':10.0,'favorable_fraction':0.5,'functional_residues':None},
        'files': {str(p): {'sha256': sha256(p), 'bytes': p.stat().st_size}
                  for p in [ASU, ASSEMBLY, RAW/'2FG8-assembly1.cif.gz', RAW/'2FG8_entry.json',
                            RAW/'2FG8_assembly1.json', RAW/'P02792.fasta', RAW/'PMC6686135.html',
                            RAW/'figshare_5899219.json', RAW/'bc8b00004_si_001.pdf',
                            assembly_pdb, mono_pdb, Path(__file__)]},
    }
    (OUT/'preparation_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({k:manifest[k] for k in ['model_count','retained_protein_chains',
                      'residues_per_chain','selected_protein_atom_count','maximum_selected_coordinate_rounding_A',
                      'target_sites_with_other_subunit_CA_within_strict_8A']},indent=2))


if __name__ == '__main__':
    prepare()
