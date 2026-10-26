# Candidate identity, provenance and recommendation

Protein: **β-glucosidase B (BglB) from Paenibacillus polymyxa**. This selection
originated from the maintainer's research experience but is an independent RANA
computational application, not evidence of ncAA experiments by any laboratory.
The maintainer accepted **2O9P A, H376Q/G377R engineered apo reference**; it is
not natural WT, D2D standard or the maintainer's experimental construct. All
case output uses input PDB author numbering. See the [completed results](results_report.md).
The original structure-only review remains archived with the execution records.

The accepted scan is protein-only. Ligand presence in an original candidate does
not imply ligand sterics are included by RANA; removing ligand from a holo model
does not turn its conformation into an experimentally determined apo structure.
2JIE remains mechanism/ligand context without a new scan. 2Z1S, 2O9R and 2O9T
are future candidates pending review only, with no download, comparison or new
analysis in this phase.

## Source scope

The original attachment filename is `Standard_D2D_BglB_WT.pdb`. Its exact
SHA-256 is `242d4d11f773a532e304986f73c3f9613918fc2733d7a83e6844cc27d00f7aec` (580205 bytes).
The maintainer reported downloading it from the old D2D site but supplied no
historical page/direct URL; those fields remain null. Independent inspection
found the [D2D resources page](https://www.d2dcure.com/resources/) and its
[public BglB.pdb](https://www.d2dcure.com/resources/structures/BglB.pdb).
The current public download is **byte-identical** to the attachment. This verifies
a current public source, not the historical download event or preparation history.
No specific redistribution license was established; neither raw D2D copy is
included in public documents. Obtain it from that page and verify the hash after
reviewing the provider's terms.

The [D2D sequence page](https://www.d2dcure.com/about/BglB/sequence.php) gives a
448-residue standard sequence and explicit Foldit/PDB tooltips. The page sequence
matches [UniProt P22505](https://www.uniprot.org/uniprotkb/P22505/entry) exactly.
The listed FASTA download returned HTTP 404; the archived HTML was used instead.
This public sequence does not independently establish the supplied experimental
construct, tags or preparation pipeline.

The official [2JIE](https://www.rcsb.org/structure/2JIE) and
[2O9P](https://www.rcsb.org/structure/2O9P) PDB/mmCIF, entity/entry and assembly
records were downloaded directly from RCSB. Their structural paper is
[Isorna et al. (2007), J. Mol. Biol.](https://doi.org/10.1016/j.jmb.2007.05.082).
All source files, exact locators, retrieval times and hashes are in
[source_manifest.json](source_manifest.json) and
[candidate_audit.json](candidate_audit.json). Numbers below refer to these
named PDB ATOM/HETATM records unless the row explicitly identifies metadata.

## Three-candidate comparison

All three are consistent with BglB from Paenibacillus polymyxa. “WT” in the
attachment filename is not proof of natural-WT or experimental-construct identity.

| Property | D2D attachment / public file | 2JIE | 2O9P |
| --- | --- | --- | --- |
| Classification | Prepared holo reference; exact processing history unknown | Deposited covalent-inhibitor complex | Deposited substrate-free/apo reference |
| Coordinate protein | A:1–445, 445 residues | A:4–448, 445 residues | A:4–448, 445 residues |
| Full polymer declaration | Absent; not inferred from filename | 454-residue tagged construct | 454-residue tagged construct |
| Observed sequence vs public standard | Matches positions 4–448 | Matches positions 4–448 | H376Q and G377R |
| Method / resolution | Not stated; not assigned from 2JIE | X-ray / 2.30 Å | X-ray / 2.10 Å |
| Protein heavy atoms / H,D | 3620 / 3415 | 3619 / 0 | 3626 / 0 |
| Other components | LG1 X:1; 36 atoms | G2F A:1449; 129 waters | 138 waters; no organic ligand or ions |
| Protein insertion codes / altlocs | None / none | None / none | None / none |
| Missing standard heavy atoms | None in observed residues | None in observed residues | None in observed residues |
| Assembly | One protein chain; biological assembly not declared | Assembly 1: monomer, PISA | Assembly 1: monomer, author-assigned |
| Selection | Holo alternative, not scanned | Functional/ligand context only | Recommended sole main input |

Complete deposited and coordinate sequences are preserved in
`candidate_audit.json` fields `structures.*.full_polymer_sequence` and
`coordinate_sequence`; the D2D full-polymer field is null because no SEQRES is
present. The public standard sequence is a separate, explicitly identified field.
Both RCSB constructs contain `MHHHHHH` followed by standard residues 2–448.
The nine unobserved author positions are **-5, -4, -3, -2, -1, 0, 1, 2, 3**,
as declared in mmCIF and PDB REMARK 465. Their coordinates cover 4–448.
D2D has contiguous coordinate numbers 1–445 and covers standard positions
4–448; absence of standard M1/S2/E3 is reference-coverage information, not an
experimental missing-residue declaration for an unknown D2D construct.

2O9P's engineered direction is independently supported by `_struct_ref_seq_dif`:
author 376 is GLN versus reference HIS, and 377 is ARG versus reference GLY.
Entity-sequence indices 382/383 are not author residue numbers. D2D A:373 HIS /
A:374 GLY and 2JIE A:376 HIS / A:377 GLY agree with the public standard at these
mapped sites. No reverse mutation or numbering direction was assumed.

No missing required standard heavy atom, protein altloc, zero-occupancy protein
atom or insertion code was found in the modeled residues. Optional terminal OXT
is excluded from the missing-atom requirement. D2D has an OXT at PHE A:445;
it is the one additional heavy atom relative to the aligned 2JIE protein.
The RCSB metadata has no separate unobserved-atom entries. Raw waters remain
archived, but they will not enter the proposed protein-only scan.

## Holo identity and processing uncertainty

The maintainer supplied the D2D holo/pNPG and unchanged Foldit H373/G374
identities. The file supports the latter directly and contains one LG1 residue
on chain X, with **12 C, 15 H, 1 N and 8 O**, consistent with pNPG's elemental
formula C12H15NO8. [CCD PNW](https://www.rcsb.org/ligand/PNW) is the chemical
reference for 4-nitrophenyl beta-D-glucopyranoside. LG1 is not itself that CCD ID.
An attempted neutral RDKit bond-order/stereochemistry reconstruction failed;
the error and null match result are retained. Beta stereochemistry was therefore
not independently established, and no ligand bonds were forced to fit a template.
This does not change the maintainer-assigned **holo candidate** classification.

The D2D file lacks HEADER/EXPDTA/SEQRES/experimental-resolution records, contains
hydrogens, zero protein B factors and template/motif REMARKs. These are preparation
signatures, not proof of a specific Rosetta mutation, relaxation command, software
version or new independent experimental determination. The checked public pages
do not establish that history. It is not the maintainer's private HPC model.

2JIE instead contains **G2F**, 2-deoxy-2-fluoro-alpha-D-glucopyranose, not pNPG.
Its PDB LINK records GLU A:356 OE1–G2F A:1449 C1 (reported length 1.41 Å).
It supplies inhibitor/catalytic context only; its ligand must not be substituted
conceptually for the D2D reporter substrate.

## Coordinate correspondence (Å)

Full coordinate-sequence alignment, not residue-number offset, establishes the
atom correspondence. Same-parent, same-name heavy atoms are compared after a
proper rigid Kabsch fit. Cα/backbone fits use their own corresponding subsets.
Unlike-parent residues 376/377 are excluded from comparisons involving 2O9P;
this does not remove their biological background influence elsewhere.

| Pair | Matched heavy atoms | Raw heavy RMSD | Fitted heavy RMSD | Matched Cα / fitted RMSD | Fitted backbone RMSD | Max Cα pair-distance difference |
| --- | --- | --- | --- | --- | --- | --- |
| D2D_attachment / 2JIE | 3619 | 18.4534 | 1.0748 | 445 / 0.5786 | 0.5793 | 3.9254 |
| D2D_attachment / 2O9P | 3606 | 18.0417 | 1.1427 | 443 / 0.6428 | 0.6431 | 4.1620 |
| 2JIE / 2O9P | 3605 | 0.8747 | 0.5627 | 443 / 0.2746 | 0.2904 | 1.9006 |

All fitted residuals exceed the conservative serialization bounds stated in
[methods.md](methods.md). The D2D difference from 2JIE includes internal geometry,
not only a rigid move or rounding. Cα pair-distance differences provide a
rigid-motion-invariant check. Same-name heavy-atom RMSD can also reflect side-chain
atom naming/symmetry. None of these comparisons identifies a modeling history;
comparisons involving 2O9P additionally mix background and ligand-state differences.

## Recommendation and open items

Recommend **2O9P A, H376Q/G377R, substrate-free/apo reference** as the sole future
scan input. It has traceable experimental origin, adequate observed-atom coverage,
explicit background and an official reproducible source. This choice uses source
clarity, not scores: no pAzF scoring has been performed. It does not claim the
D2D standard sequence or the maintainer's experimental construct.

D2D remains an explicitly labeled holo alternative, not a second planned scan.
Before recommending it instead, resolve or explicitly authorize its unknown
preparation history and ligand-topology assumptions in a new pre-scan plan.
Any future ligand removal must be labeled **ligand-removed D2D holo reference**,
retaining the holo conformation, never an experimental apo structure.
Its historical download URL and redistribution permission also remain unresolved.
The attachment-specific +3 expectation is contradicted by actual numbering; see
the [complete site check](site_mapping.md). No coordinate renumbering was done.
