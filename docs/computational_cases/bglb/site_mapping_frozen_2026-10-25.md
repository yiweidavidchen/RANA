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

## Annotation sources and evidence levels

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
