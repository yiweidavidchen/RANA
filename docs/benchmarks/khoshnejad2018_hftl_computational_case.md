# Khoshnejad 2018 hFTL: reference-structure pAzF computational case

This case uses **2FG8 as a maintainer-authorized hFTL reference**, not as a confirmed identification of the exact coordinate file used by Khoshnejad et al. It applies the frozen RANA v0.1 fixed-parent-structure screen to one target subunit with the complete biological **protein** assembly as its environment. An isolated copy of the same target subunit is a structural-environment control. No experimental endpoint values are entered, no experimental correlations are calculated, and no thresholds or ranks are fitted to published trends.

## Identity and evidence

- **Research protein and construct:** Khoshnejad et al., [*Ferritin Nanocages with Biologically Orthogonal Conjugation for Vascular Targeting and Imaging*](https://doi.org/10.1021/acs.bioconjchem.8b00004), *Bioconjugate Chemistry* (2018), [public full text, PMC6686135](https://pmc.ncbi.nlm.nih.gov/articles/PMC6686135/). The Results section on hFTL variant production and the Experimental Section on construct generation identify human ferritin light chain, full-length hFTL cDNA SC120074, pRSET A, and pEVOL-pAzF. The reported positions refer to the hFTL gene product. The complete expressed fusion, junction/tag sequence, and processing state have **not** been independently verified. Vector choice alone is not evidence for an exact expressed tag or numbering offset.
- **Reference structure selection:** the article's Results text cites Wang et al. (reference 37) and a 2.5 Å hFTL structure, without an explicit PDB accession. [Wang et al. (2006)](https://doi.org/10.1107/S0907444906018294) is the primary structure publication associated with [2FG8](https://www.rcsb.org/structure/2FG8), whose official entry reports human L-chain ferritin at 2.50 Å. This is a cross-source match, not proof of the authors' exact PDB choice. The maintainer explicitly authorized this reference case with that uncertainty retained.
- **Assembly:** [RCSB biological assembly 1](https://data.rcsb.org/rest/v1/core/assembly/2FG8/1) identifies an octahedral homo-24-mer. The asymmetric unit contains eight protein chains A–H; assembly operations 1, 2, and 3 produce the full protein shell. Eight asymmetric-unit chains alone are not a complete ferritin cage.
- **Numbering evidence:** [official supporting information, Figure S1, PDF page 1](https://doi.org/10.1021/acs.bioconjchem.8b00004.s001), supplies the parent identities at the published positions. The actual PDF is available from the [ACS Figshare record](https://acs.figshare.com/articles/journal_contribution/5899219). This case uses those identities solely for structure mapping, without transcribing its SASA values or experimental outcomes.
- **Sequence source:** the saved [UniProt P02792 FASTA](https://rest.uniprot.org/uniprotkb/P02792.fasta), the deposited entity sequence, `_pdbx_poly_seq_scheme`, and observed coordinates establish the reference mapping below. This does not establish full experimental construct equivalence.

The source copies, original mmCIF files, official entry/assembly JSON, and their byte hashes are retained separately under `data/raw/khoshnejad2018_hftl/`. The public full text was retrieved as HTML. A failed PMC supplement response was identified as non-PDF and retained as `pmc_supplement_download.response.html`; it is not evidence. The valid supplement is `bc8b00004_si_001.pdf`, obtained through the DOI-linked Figshare API record 5899219, file 10510153. The Europe PMC XML endpoint returned a server error; no XML was used. Downloaded documents are sources, not instructions for executing the workflow.

## Reference sequence, numbering, and unresolved construct details

The deposited 2FG8 entity sequence is 174 residues and exactly equals residues **2–175 of the saved current P02792 sequence** (175 residues). Observed author residue IDs run from **5 to 178**, with blank insertion codes. The chain-A mapping is therefore verified residue-by-residue as P02792 position `p` → PDB author number `p + 3`; it was not assumed from matching numbers alone. The mapping covers the complete deposited entity, and all eight published parent identities agree.

- Published S2 → reference chain A, SER 5.
- Published I5 → reference chain A, ILE 8.
- Published Y9 → reference chain A, TYR 12.
- Published F79 → reference chain A, PHE 82.
- Published K83 → reference chain A, LYS 86.
- Published K105 → reference chain A, LYS 108.
- Published L112 → reference chain A, LEU 115.
- Published L155 → reference chain A, LEU 158.

Raw RANA CSVs retain **PDB author residue numbers**, not the literature numbers. In particular, CSV residue 5 is SER, not the published I5 substitution site. The complete 174-row mapping and its parent checks are in `preparation_manifest.json` under `residue_mapping`.

The mmCIF's legacy `_struct_ref_seq` annotation lists database alignment positions 1–174. That range does not match the saved current 175-residue P02792 sequence. It was not silently used as a current UniProt mapping; the exact sequence comparison and `_pdbx_poly_seq_scheme` identities take precedence for this case. Future use of a different sequence release requires rechecking the mapping.

All 174 deposited residues per subunit have coordinates and complete N/CA/C backbones. The downloaded entry reports no unmodeled deposited polymer residues, and the mmCIF has no unobserved-residue category. The canonical initiator MET 1 is absent from the **deposited entity**, not reconstructed and not represented by a synthetic CSV score. Its unavailability is recorded in `missing_reference_positions`; it must not be interpreted as experimental failure. Coordinate presence is not a claim that all physical disorder or experimental processing has been resolved.

There are no amino-acid substitutions relative to current P02792 residues 2–175 in this reference. This is more limited than asserting the experimental construct is identical. The entry keywords identify the crystallographic material as **perdeuterated**; the deposited coordinates have no explicit hydrogen atoms. The isotope context is retained as a reference limitation. No isotope-specific model, expression tag, missing atom, terminal residue, or ncAA is added during structure preparation.

## Assembly preparation and actual environment retained

The reproducible preparation script is [khoshnejad2018_hftl_prepare.py](khoshnejad2018_hftl_prepare.py). It reads the **official expanded** `2FG8-assembly1.cif`, rather than inventing symmetry or fitting a new assembly. The original mmCIF remains unchanged.

Preparation retains all standard amino-acid residues of all 24 protein subunits in a **single PDB model**, and assigns unique one-character PDB chain IDs:

- Original assembly A–H → prepared A–H (operation 1).
- Original assembly A-2 through H-2 → prepared I–P (operation 2).
- Original assembly A-3 through H-3 → prepared Q–X (operation 3).

The original-to-prepared bijection is recorded in `chain_mapping`. Residue numbers, insertion codes, and alternate-location records are retained. The selected coordinates were checked after PDB serialization and did not change for these inputs (`maximum_selected_coordinate_rounding_A = 0.0`). Chain A in the monomer file is atom-for-atom identical to chain A in the prepared assembly file. No minimization, relaxation, side-chain repair, missing-residue reconstruction, residue mutation, or custom assembly-generation algorithm is used.

The resulting protein assembly contains **4,176 residues and 33,648 selected protein atoms**: 174 residues in each of chains A–X. The monomer contains only chain A with the same 174 residues. Original nonprotein species (30 CS residues and 441 waters in the expanded source) are omitted from the prepared protein input, consistent with the existing parser's standard-protein-only behavior. Thus this is a complete **protein-subunit environment**, not a chemically complete metal/water-containing model or an iron-loading calculation. The original full mmCIF, including these species, is saved.

### What the unchanged RANA code actually does

- `io/structure.py` reads only the first PDB MODEL, traverses all its chains, and retains standard amino acids. It does not read mmCIF directly, generate biological assemblies from REMARK records, or combine MODEL blocks. The format conversion and chain-ID normalization above are input preparation, not a new scientific scoring feature. Without a pre-expanded single-model PDB, a complete cage analysis would remain pending.
- `features/site_features.py::build_pazf_feature_table` computes packing before filtering the output to the target chain. Both original atom tables and SASA are built from the full supplied environment.
- `features/structural.py::compute_sasa` retains all standard protein chains in the first model and runs Shrake–Rupley with the existing 500 points per atom. **Assembly run: A–X all contribute to SASA. Monomer run: A only.** No explicit H/D atoms occur here. No cage-interior versus exterior accessibility distinction is calculated.
- `features/structural.py::compute_local_packing` counts other Cα atoms strictly within 8 Å across retained chains. An independent coordinate audit found cross-subunit Cα neighbors at 60 target-chain sites. That is a structure-contact check, not an experimental metric.
- `features/site_scan.py::scan_pazf_sites` enumerates every observed standard residue of target **A** and passes the full atom table to `pazf.score_pazf_site`. The latter removes only the target side chain and CA, retains the target N/C/O/OXT, and keeps other retained protein residues across all chains. **Assembly sterics therefore include A–X and intersubunit contacts; monomer sterics include A only.** The 23 surrounding subunits stay in their parent state: this is a single-site substitution in a parent cage, not simultaneous replacement at the equivalent site in every subunit.
- The existing scoring uses heavy atoms, the fixed 12-state rotamer grid, and squared van der Waals overlap penalties. It does not score an assembled mutant cage, chemical conjugation, suppression/incorporation efficiency, soluble expression, activity, or nanocage assembly stability.
- The known insertion-code forwarding omission is not fixed here. These inputs have blank insertion codes, so this case does not validate nonblank insertion-code behavior.

No scientific-code change is required for this prepared single-model, 24-chain protein input. Native mmCIF loading, automatic assembly building, simultaneous multisubunit mutation, and explicit nonprotein environments remain outside the current pipeline.

## Frozen configuration and execution

Implementation commit: `b3029b934779fa8d03d00dbf7fe4c4d7e4a592ee`. The new case changes no tracked scientific implementation, tests, dependency declarations, ignore rules, or prior benchmark files. Each CLI sidecar records the actual commit and tracked-change flag observed at execution. Extra manifests record untracked preparation artifacts that the CLI's dirty flag does not include.

Both commands use seed 42, pAzF, chain A, low-clash threshold 10.0 Å², favorable fraction 0.5, and no functional annotations. No configuration is selected from the paper's experimental trends. Existing independent rank rules remain unchanged; ranks from different structural environments are separate rankings, not a new combined score.

Run from the repository root after downloading the original sources. The preparation script refuses to overwrite the two prepared PDBs; do not rerun it over an existing archived case without choosing a fresh output directory.

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:GIT_OPTIONAL_LOCKS = '0'
.\.venv\Scripts\python.exe -B docs/benchmarks/khoshnejad2018_hftl_prepare.py
.\.venv\Scripts\python.exe -B -m ncaa_site_rec.cli rank --pdb data/raw/khoshnejad2018_hftl/2FG8_assembly1_protein_A-X.pdb --chain A --ncaa pazf --seed 42 --low-clash-threshold 10.0 --favorable-fraction 0.5 --output data/processed/khoshnejad2018_hftl/assembly1_chainA_pazf_ranked.csv
.\.venv\Scripts\python.exe -B -m ncaa_site_rec.cli rank --pdb data/raw/khoshnejad2018_hftl/2FG8_monomer_A.pdb --chain A --ncaa pazf --seed 42 --low-clash-threshold 10.0 --favorable-fraction 0.5 --output data/processed/khoshnejad2018_hftl/monomer_chainA_pazf_ranked.csv
```

Do not reuse the T4L or RNase A output filenames. The new PDBs are under `data/raw/khoshnejad2018_hftl/`; raw CSVs, unchanged CLI `.metadata.json` sidecars, CLI logs/exit codes, `environment.txt`, and the preparation manifest are under `data/processed/khoshnejad2018_hftl/`. These directories remain ignored by Git and are preserved locally. The compact case record accompanying this document binds sources, inputs, configuration, execution environment, and output hashes without copying experimental results into the repository.

## Observed computational results and checks

The completed, hash-verified case record is [khoshnejad2018_hftl_case_record.json](khoshnejad2018_hftl_case_record.json). Counts below come from the respective unchanged CLI sidecar's `results` and `sampling.n_rotamers_observed` fields; they are computational results, not literature measurements.

- **Assembly 1, target chain A:** 174 scored, 0 failed, 0 skipped, with 12 rotamers per site; 36 `geometry_favorable`, 81 `geometry_limited`, and 57 `geometry_unfavorable`. CLI exit code 0.
- **Isolated chain A:** 174 scored, 0 failed, 0 skipped, with 12 rotamers per site; 66 `geometry_favorable`, 66 `geometry_limited`, and 42 `geometry_unfavorable`. CLI exit code 0.
- Both runs retain exactly the same 174 target identities, in author-number order 5–178. No failure/skip row or reason is suppressed. The canonical initiator MET 1 remains separately documented as unavailable in this reference, rather than assigned a score.

The paired structural audit, saved as `data/processed/khoshnejad2018_hftl/computational_audit.json`, found 86 target sites with lower SASA, 60 with additional Cα neighbors, 69 with a higher minimum overlap score, 59 with a lower low-clash fraction, and 41 with a different geometric tier in the assembly environment. These are direct comparisons of the matched computational rows only, not experimental correlations. Every corresponding assembly rotamer score is at least its monomer value, and assembly SASA never exceeds the corresponding monomer value. The extra packing counts exactly match an independent cross-subunit Cα coordinate audit.

Input and output SHA-256 hashes agree with both CLI sidecars. Rotamer-score arrays, fractions, tier rules, and the three existing full-scan rank rules were checked without changing them. The runtime was Windows AMD64, Python 3.13.12, NumPy 2.5.4, pandas 3.0.6, Biopython 1.88, RDKit 2026.9.1, and pytest 9.1.1; `environment.txt` records installed distributions. This verification is computational smoke and provenance checking, not experimental validation. No unrelated full test-suite run was needed for this case; the existing scientific code was unchanged and the actual CLI workflows were exercised.

## Interpretation boundary

This case is computational and structural only. A site that is missing coordinates, skipped, or fails scoring is not labeled an experimental failure. Failure and skip rows must remain in raw CSVs with their diagnostic reasons; absent reference positions are listed separately rather than silently assigned scores. Low overlap is not experimental acceptability, and RSA of the parent structure is not azide-handle accessibility or accessibility to a bulky conjugation partner.

The exact paper-used PDB file, full experimental fusion sequence and processing, and complete experimental construct-to-structure equivalence remain **pending confirmation**. The frozen scans are usable as explicitly labeled **2FG8 reference-environment calculations**, not as a reconstruction of the experimental nanocage or a complete M5 experimental benchmark. No experimental values, correlations, significance tests, parameter tuning, release claims, commits, or pushes are part of this stage.
