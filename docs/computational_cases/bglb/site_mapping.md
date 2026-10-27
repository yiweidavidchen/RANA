# Numbering and functional annotation check

Coordinates retain their own chain, residue number and insertion code. All
reported sites have blank insertion code (`""` in JSON). Output will remain in
the selected input's coordinate numbering, never converted to Foldit numbering.

The maintainer supplied 11 functional labels and two background checks, with an
expected +3 attachment mapping. **All 13 expected attachment positions fail their
specified parent checks.** The supplied/public file instead numbers its modeled
chain 1–445, matching the Foldit labels at the same numeric positions. The public
[D2D sequence tooltips](https://www.d2dcure.com/about/BglB/sequence.php) explicitly
map these Foldit labels to RCSB-style positions +3. These distinctions are verified
by all 445 aligned residues, not inferred from a filename or one matching site.

| Provided Foldit label | Supplied +3 attachment expectation: actual parent there | Verified attachment identity | Verified 2JIE identity | Verified 2O9P identity |
| --- | --- | --- | --- | --- |
| Q19 | A:22 GLY | A:19 GLN | A:22 GLN | A:22 GLN |
| R76 | A:79 VAL | A:76 ARG | A:79 ARG | A:79 ARG |
| H119 | A:122 LEU | A:119 HIS | A:122 HIS | A:122 HIS |
| N163 | A:166 TYR | A:163 ASN | A:166 ASN | A:166 ASN |
| E164 | A:167 CYS | A:164 GLU | A:167 GLU | A:167 GLU |
| N293 | A:296 THR | A:293 ASN | A:296 ASN | A:296 ASN |
| Y295 | A:298 SER | A:295 TYR | A:298 TYR | A:298 TYR |
| E353 | A:356 ALA | A:353 GLU | A:356 GLU | A:356 GLU |
| W399 | A:402 LEU | A:399 TRP | A:402 TRP | A:402 TRP |
| E406 | A:409 TRP | A:406 GLU | A:409 GLU | A:409 GLU |
| W407 | A:410 GLY | A:407 TRP | A:410 TRP | A:410 TRP |
| H373 | A:376 ILE | A:373 HIS | A:376 HIS | A:376 GLN |
| G374 | A:377 GLU | A:374 GLY | A:377 GLY | A:377 ARG |

The first 11 rows are the maintainer's functional list. H373/G374 are background
identity checks, not two additional functional-site claims. In 2O9P they map to
**Q376/R377**, so their parent differences are retained, not corrected or hidden.
Do not generalize +3 to another PDB or use it to renumber the supplied file.

## Annotation sources and evidence levels (pre-scan record, 2026-10-25)

- The 11-site functional list is maintainer-provided, recorded from the
  2026-10-25 request. Parent identity and mapping are verified separately from
  whether a site has an experimentally established functional role.
- [UniProt P22505](https://www.uniprot.org/uniprotkb/P22505/entry), JSON `features`,
  annotates **E167: Proton donor**, evidence `ECO:0000255`, and **E356: Nucleophile**,
  evidence `ECO:0000255`, PROSITE-ProRule `PRU10055`. These evidence codes are
  retained; this audit does not reclassify them as new experimental measurements.
  They map to attachment E164/E353 and to 2JIE/2O9P E167/E356.
- Other nine sites remain maintainer-supplied functional-context flags; no
  specific indispensable/catalytic role or ncAA tolerance is independently
  assigned here. The public D2D page supports numbering, not such role claims.
- 2JIE PDB LINK GLU A:356 OE1–G2F A:1449 C1 supplies separate covalent-ligand
  structural context. See [Isorna et al. 2007](https://doi.org/10.1016/j.jmb.2007.05.082)
  for the structural study; no per-site pAzF outcome is taken from it.

Machine-readable originals, exact parent checks, tooltip text and UniProt
features/ECO codes are in `candidate_audit.json.functional_mappings`.
[residue_crosswalk.json](residue_crosswalk.json) retains all 1335 coordinate
residue mappings (445 per candidate), including both 2O9P parent mismatches.
All 11 proposed main-input annotation parents match the supplied functional list.
These flags will be joined to geometry results after scoring and will not alter
scores, tiers, sampling, eligibility, independent ranks or candidate selection.

## Post-scan literature supplement (2026-10-27)

This source check is separate from the documentation readability edit and was
completed after the scan. It supplements the maintainer's existing annotations;
it does not redefine the frozen functional flags or retrospectively claim that
this literature review preceded selection or scoring. The pre-scan statements
above and the original machine-readable audit retain their historical meaning.
No experimental pAzF outcome, functional score or exclusion rule is added.

### Sources, access and locators

- **I07:** Isorna, P., Polaina, J., Latorre-García, L., Cañada, F. J.,
  González, B., and Sanz-Aparicio, J. (2007), *Crystal Structures of Paenibacillus
  polymyxa β-Glucosidase B Complexes Reveal the Molecular Basis of Substrate
  Specificity and Give New Insights into the Catalytic Machinery of Family I
  Glycosidases*, Journal of Molecular Biology 371, 1204-1218.
  DOI: [10.1016/j.jmb.2007.05.082](https://doi.org/10.1016/j.jmb.2007.05.082).
  The supplied 15-page PDF was read, including the complete relevant pages and
  Figures 3-5. Printed page 1204 is PDF page 1. Figure 3(a-c) is on printed
  pages 1209-1210 (PDF pages 6-7), and Figure 4 is on printed page 1211
  (PDF page 8). No separate supplement was supplied or verified: publisher
  access was blocked, and the supplied main text does not identify a separate
  supplement. Its availability remains unresolved; this is not a claim that
  none exists. No residue mechanism was inferred from an abstract.
- **C16:** Carlin, D. A., Caster, R. W., Wang, X., et al. (2016), *Kinetic
  Characterization of 100 Glycoside Hydrolase Mutants Enables the Discovery of
  Structural Features Correlated with Kinetic Constants*, PLOS ONE 11, e0147596.
  DOI: [10.1371/journal.pone.0147596](https://doi.org/10.1371/journal.pone.0147596).
  Both the supplied full text and the [publisher full text](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0147596)
  were checked. The supplied PDF includes an eScholarship cover: printed page
  5/14, containing “Observed sequence-structure-function relationships in BglB,”
  is PDF page 6. Figure 2 is on printed page 4/14 (PDF page 5); Figure 3 is on
  printed page 6/14 (PDF page 7). Mutant-row labels below are exact locators in
  [S1 Table, DOI suffix s006](https://doi.org/10.1371/journal.pone.0147596.s006).
  [S3 Table, suffix s008](https://doi.org/10.1371/journal.pone.0147596.s008),
  [S1 Text, suffix s009](https://doi.org/10.1371/journal.pone.0147596.s009), and
  [S1 Code, suffix s001](https://doi.org/10.1371/journal.pone.0147596.s001)
  were retrieved from the publisher and inspected. The DOCX supplements are
  valid ZIP containers with `word/document.xml`, not HTML error responses.

The I07/C16 identifiers in each row below resolve to these DOIs. Supplemental
table rows are identified by mutation label rather than viewer-dependent page
breaks. Local extraction/rendering and downloaded supplements are retained only
under `data/processed/m6_bglb_annotation_sources_2026-10-27/`; no paper or
publisher figure is added to the public manifest.

| Source file | SHA-256 of original bytes |
| --- | --- |
| Supplied Isorna 2007 PDF | `b01b1b33189ab455f05382083467514c12cce19c61d46b3d79ca57776eae0bf9` |
| Supplied `2016 Carlin.pdf` | `8a16aa9d90fb76a833e9d6b6a0a0c7ea3113770df0032cc4827bb9da2d6f6e82` |
| C16 S1 Table, `carlin2016_s006.docx` | `b580e7573ece03bf1dba2c0dc27238a12b1bf627eb1307f35a0cedffbc1b2a73` |
| C16 S3 Table, `carlin2016_s008.docx` | `d08605c3f5370061b1cdfe5119e215e45338b4ff173f0c56ee244af964bdf0e9` |
| C16 S1 Text, `carlin2016_s009.docx` | `3b5cab3fdd1d3a4242add86ad6bc1437d644838d10f4f63a1735cbe42d2f864f` |
| C16 S1 Code, `carlin2016_s001.zip` | `b53a2cd02ec6ca977f606105689c44d48df9f9028b5bdd4a027c311ed8a15d0c` |

### Numbering and construct checks

I07 uses the author-style labels visible in Figures 3 and 4, such as Q22,
H122, E167, E356 and W410. Each label in the evidence table was checked against
the corresponding residue in the existing 2JIE/2O9P coordinate identity audit.
The structures retain chain A and blank insertion codes for these sites.

C16 uses different labels, including Q19, E164, Y295 and E353. This review did
not assign their mapping by assuming a constant offset. The protein ATOM records
in C16 S1 Code's `S1 Code/bagel.pdb` contain a single modeled chain A with 445
residues numbered 1-445. Its complete ordered modeled protein sequence matches
the 445 residues in the existing 2JIE audit, author positions A:4-448. Pairing
those complete sequences and checking each parent yields the eleven
correspondences below. For this particular pair, the resulting author numbers
are three higher; this is a verified result, not a general numbering rule.
The original ZIP member's raw SHA-256 is
`329ea3179b623a7cf8471f6aed53615793bd7f7b97fe90d17e3a4951bbcb642b`.
No modeling instructions from the archive were executed.

Comparison with the existing 2O9P identity audit retains two background
differences: C16 model H373/G374 corresponds to 2O9P Q376/R377. All eleven
functional-context parents match, but the entire backgrounds do not. C16 S1 Text
describes a P22505-based gene codon-optimized for E. coli in pET29b with a
C-terminal His tag. I07 Materials and Methods, “Cloning of the bglB gene and
construction of his-tagged derivatives” (printed p. 1215), describes tagged
derivatives; the deposited reference's tags/background remain as documented in
the original structure review. A published model's sequence correspondence is
not proof that the complete experimental constructs, tags and the RANA input
are identical. None is identified with the maintainer's experimental construct.

### Site-by-site evidence and limited conclusions

All rows retain their original **maintainer-supplied functional-context flag**.
“Structural environment” means a residue is depicted around the bound ligand;
it does not, by itself, establish a direct ligand bond. “Contact” refers to a
contact drawn or described by the authors, not a newly calculated distance.
Mechanistic explanations are kept separate from direct substitution experiments.
All C16 substitutions below are conventional amino-acid changes, not pAzF
substitutions. The kinetic assays used pNPG; protein production was recorded
separately. S1 Table's `ND` denotes protein not detected above
the authors' production/yield detection limit; blank kinetics are not zero.

| Current 2O9P author identity | I07: original structural evidence / mechanism | C16 label and direct experiment locator | Supported conclusion and remaining limit |
| --- | --- | --- | --- |
| A:Q22 GLN | Q22 in Figure 3(a,c) and the ligand hydrogen-bond diagrams in Figure 4(a,c), pp. 1209-1211. | Q19; S1 Table rows Q19A, Q19C, Q19S; Results “Observed sequence-structure-function relationships,” p. 5/14, and Figure 3A. | I07 supplies contact context; C16 supplies direct pNPG kinetic endpoints, including a censored entry. C16's substrate-orientation explanation and S2 Figure are interpretation/modeling, not an experimentally solved Q19A structure or proof of the proposed mechanism. |
| A:R79 ARG | R79 is depicted in the 2FGlc active-site environment in Figure 3(a), p. 1209. No specific catalytic role is assigned from this depiction. | R76; S1 Table row R76A; Figure 2. | A direct substitution was tested, but protein yield is ND and kinetic fields are blank. This supports a production/yield limitation under that protocol, not demonstrated catalytic inactivity or a specific reaction role. |
| A:H122 HIS | H122 in Figure 3(a,c) and Figure 4(a,c), pp. 1209-1211, provides ligand-contact context. | H119; S1 Table rows H119A, H119E, H119N. | H119A/H119N have reported pNPG kinetic endpoints; H119E has ND yield and blank kinetics. These substitution outcomes do not establish a unique catalytic mechanism or pAzF tolerance. |
| A:N166 ASN | N166 in Figure 4(a,c); the 2FGlc-complex Results text on p. 1206 describes an interaction stabilizing the fluorine substituent. | N163; S1 Table rows N163A, N163C, N163D. | Original inhibitor-contact evidence and direct conventional-substitution kinetic endpoints are available. An inhibitor-specific contact is not automatically the same contact with every substrate. |
| A:E167 GLU | E167 is identified as the acid/base in Results on p. 1206; Figures 4(a-d) and the glucose-complex text on pp. 1210-1211 give contact evidence consistent with the proposed proton-donor role. | E164; S1 Table row E164A; Introduction, p. 2/14, and Results, p. 5/14. | I07 supports a structural/mechanistic acid/base assignment. C16 adds a direct conventional-mutant kinetic entry; its mechanistic introduction cites I07 rather than supplying another independent structural determination. The main-text quantitative generalization needs reconciliation with S1 Table, as noted below. |
| A:N296 ASN | N296 is depicted in Figure 3(a-c), pp. 1209-1210. This review records active-site structural environment without assigning an unverified specific bond or catalytic role. | N293; S1 Table row N293A. | A direct pNPG kinetic endpoint is reported for N293A. Neither the depiction nor that substitution alone establishes that the parent residue performs a particular chemical step. |
| A:Y298 TYR | Figure 4(a,b), the covalent-complex Results on p. 1206, and Figure 5(a) show contact/conformational context. I07 discusses a possible deglycosylation role by analogy; it is not a demonstrated BglB mutant mechanism. | Y295; S1 Table rows Y295A, Y295G; Introduction and Figure 3A for the proposed glutamate-orientation role. | C16 adds direct, below-detection kinetic endpoints for conventional substitutions. Its mechanistic explanation is distinct from these measurements and is not counted as an independent confirmation of every proposed I07 role. |
| A:E356 GLU | The covalent 2FGlc complex on p. 1206 and Figures 3(a), 4(a) show the sugar linked to E356; I07 assigns the nucleophile role. | E353; S1 Table row E353A; Results, p. 5/14. | Original covalent-intermediate structural evidence and a direct censored pNPG mutant endpoint support different aspects of the annotation. The existing PDB LINK and later discussion describe the same structural observation, not additional independent experiments. |
| A:W402 TRP | Results pp. 1206-1208 describes sugar stacking in the covalent complex and a different recognition pattern in the thiocellobiose complex; Figure 4(b) depicts its contact. | W399; S1 Table rows W399A, W399C, W399G, W399S. | Ligand-dependent structural contact context and direct conventional-substitution kinetic endpoints, some censored, are available. No general ncAA acceptability or indispensable reaction role follows. |
| A:E409 GLU | Figures 4(a-d), 5(a), Results pp. 1208-1211 and Discussion p. 1214 describe ligand contacts and alternative conformations. The proposed switching role is an author interpretation. | E406; S1 Table rows E406A, E406D. | E406A has a censored kinetic endpoint and E406D has reported kinetic constants. These are direct substitution outcomes, not direct experimental proof of the switching mechanism. |
| A:W410 TRP | W410 in Figure 3(a,c) and Figure 4(a,c), pp. 1209-1211, provides ligand-contact context. | W407; S1 Table rows W407A, W407G, W407Q, W407R; Figure 2. | All listed substitutions have ND protein yield and blank kinetic fields. Preserve these as production/yield observations, not measured catalytic zeros. A unique mechanistic role remains unassigned. |

### Evidence reuse, conflicts and unresolved items

- I07 is the original structural study for the contacts and covalent complex
  cited here. C16 Introduction and modeling sections cite I07 (reference 15)
  when discussing E164/E353/Y295. That restatement is not an additional
  independent structural experiment. C16's conventional-substitution experiments
  are distinct evidence, with their own construct and pNPG assay conditions.
- C16 Figures 2 and 3, S1 Table and S3 Table describe or summarize the same
  mutation study. They are not counted as independent mutant observations.
  S2 Figure is explicitly a modeled comparison; it is not a new mutant crystal
  structure. The UniProt/PROSITE-ProRule assignments and the already-recorded
  2JIE LINK retain their original provenance and are not recounted as new data.
- C16 S1 Table reports ND protein yield with blank kinetics for R76A and the
  W407 substitutions, while S3 Table gives finite log-relative entries for
  R76A and W407A. These cannot be silently promoted to measured kinetics.
  Their reconciliation remains pending; this supplement uses the directly
  labeled S1 endpoints and preserves the discrepancy.
- C16 Results, p. 5/14, groups E164A with E353A/Y295A in a greater-than-85,000-fold
  catalytic-efficiency statement. S1 Table instead gives E164A a non-censored
  entry of 190 ± 33 and the native row 176,000 ± 8000, both in M^-1 min^-1.
  The same paragraph's 57,000-fold Q19A statement also needs reconciliation with
  S1 Table's Q19A entry of 11 ± 3 and native entry. These source inconsistencies
  are recorded, not resolved by inventing values or transferring the blanket
  claims into a new benchmark. S3 Table does not constitute an independent
  repetition that settles them.
- The I07 supplement remains unverified. No site-specific I07 substitution
  experiment for these eleven residues was established from the inspected main
  text; its structures and mechanistic interpretations are not reclassified as
  direct mutational evidence. Unverified specific roles, especially for the
  structural-environment-only R79/N296 assignments, remain unassigned. The
  maintainer flags remain unchanged regardless of the available evidence level.

### Current document versus frozen execution dependency

The maintained document contains post-scan explanation and literature evidence;
it is not parsed for parameters or functional labels. The original document was
restored from approved commit `4ead407025a4ac7fb6c4cb1e2dfc9ea8351c6f25` as
[site_mapping_frozen_2026-10-25.md](site_mapping_frozen_2026-10-25.md), preserving
its original bytes and the historical plan's SHA-256
`6be8b8bd81f13df8c55ba32af247876e6afd19316ca0c49824d76e516289b7d4`.

The current entry points map the historical plan key `site_mapping.md` to that
frozen dependency and check the same approved hash. This document can therefore
be updated without changing computational inputs. Actual configuration and
annotation fields still come from the hash-checked execution-plan and audit
JSON files; their checks are unchanged. The
[current tool approval](tool_revision_2026-10-27.json) is separate from the
unchanged original plan, previous tool approval and historical execution and
validation records. The restored file is the historical version; the current
literature supplement is not labeled as a pre-scan source. See
[reproduction](reproduction.md#documentation-dependency-compatibility-2026-10-27)
for this compatibility change and the re-curation check.
