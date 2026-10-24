# M5 literature inventory and first curation batch

This is a literature-curation addendum dated 2026-10-23, not a performance-validation result. It preserves the existing Wilkerson pilot and hFTL computational case byte for byte. The five supplied main/supplement pairs are readable research documents, not HTML error pages. No paper or supplement is copied into Git.

- [Data availability matrix and scope decisions](data_availability.md)
- [Khoshnejad: eight sites, conjugation and assembly evidence, existing scan associations](khoshnejad2018_evidence_addendum.md)
- [Wilding: original observations, conditions, and Wilkerson reuse](wilding2018_context_addendum.md)
- [Machine-readable inventory, paths, sizes, validation and hashes](literature_inventory.json)
- [Khoshnejad observation records](khoshnejad2018_observations.json) and [Wilding observation records](wilding2018_observations.json)
- [Curation checks, file preservation, and test results](curation_verification.json)

## Source conventions and attachment integrity

Source IDs below are used in every curated observation. PDF page numbers refer to the physical PDF page, starting at 1; printed journal pages are also given where applicable. DOCX locators use section/table names and body paragraph indices, counting blank paragraphs, because page breaks depend on rendering. Local originals are in `E:\Papers for RANA`; exact paths and byte lengths are in the JSON inventory. DOI links provide public literature entry points independent of these local paths.

All nine PDFs passed signature, strict parser, and all-page extraction checks. The DOCX passed ZIP CRC and required OOXML-part/XML parsing checks. Its tables and embedded-media inventory were inspected. Cover title and authors match the paired main publication, including Schinn DOCX paragraphs 3 and 7. Selected table/figure pages were also rendered and visually checked. Poppler emitted missing-font fallback messages for Symbol/ArialUnicode in some ACS supplements; rendered labels and printed numbers used here were legible. No curves or bar heights were estimated.

| Source ID | Supplied file | Valid format / extent | SHA-256 |
| --- | --- | --- | --- |
| K-M | `Khoshnejad_2018.pdf` | PDF / 10 pages | `bcb05ed8f13bc83cc7ba3b223fb9fad85978f73ab6de55a960b140b05d51270c` |
| K-S | `Khoshnejad_2018_Supp.pdf` | PDF / 6 pages | `22bca251e6eb0b46d17515cd8152cae84ef4aad51151cc177a379e001de9eb1a` |
| W-M | `Wilding_2018.pdf` | PDF / 12 pages | `c9042894c0b0080686f3be8debbe6ab73d611ec4911231ad766fc490d26e6f15` |
| W-S | `Wilding_2018_Supp.pdf` | PDF / 10 pages | `d3a835c426789cb07c6c00cf9b805ddd904e392cbb8dbe8ef17ae0e8fe80136f` |
| S-M | `Schinn_2017.pdf` | PDF / 6 pages | `0c55560b2392e1c170177e12b731d1dd12f42a4d14cfda0cdc9f27eb17f049e9` |
| S-S | `Schinn_2017_Supp.docx` | DOCX / 245 body paragraphs, 2 tables, 7 embedded images | `7a51ffc790de18e08b3183b678fb0db9375174252fee8a49a94ddb072be6061b` |
| L-M | `Lopez_2014.pdf` | PDF / 9 pages | `b134f551ffe9861e95f90b4e19f6ab50454eaad1da3ca13b17fdde9122904964` |
| L-S | `Lopez_2014_Supp.pdf` | PDF / 13 pages | `cad034f9eef495d17e1891bf510588a02589726c6ac5c6365bdd37362a843384` |
| R-M | `Reddington_2015.pdf` | PDF / 8 pages | `ce627f9bc6839ccb50ecc03ad5b22abc0501be1f91fba08e3716ffd8114af4c2` |
| R-S | `Reddington_2015_Supp.pdf` | PDF / 17 pages | `d340f447e78f3070a4de565bb0826f2ea82c2ef41c648f683d568a0e543bb7ff` |

The separately accessed Wilkerson 2020 main PDF is context for reuse checks, not an additional member of the ten-file intake. Its hash and inspected locations are recorded in the inventory. The pre-existing downloaded Khoshnejad SI and the newly supplied SI have different bytes/hashes; both source versions are retained, with no claim of byte identity or replacement.

## Verified publications

### Khoshnejad2018

**Ferritin Nanocages with Biologically Orthogonal Conjugation for Vascular Targeting and Imaging**

Makan Khoshnejad; Colin F. Greineder; Katherine W. Pulsipher; Carlos H. Villa; Burcin Altun; Daniel C. Pan; Andrew Tsourkas; Ivan J. Dmochowski; Vladimir R. Muzykantov.

Bioconjugate Chemistry 29, 1209–1218 (2018). [DOI: 10.1021/acs.bioconjchem.8b00004](https://doi.org/10.1021/acs.bioconjchem.8b00004).

Identity checked against main PDF page 1; matching title and complete author list on supplement pdf page 1.

### Wilding2018

**The Locational Impact of Site-Specific PEGylation: Streamlined Screening with Cell-Free Protein Expression and Coarse-Grain Simulation**

Kristen M. Wilding; Addison K. Smith; Joshua W. Wilkerson; Derek B. Bush; Thomas A. Knotts IV; Bradley C. Bundy.

ACS Synthetic Biology 7, 510–521 (2018). [DOI: 10.1021/acssynbio.7b00316](https://doi.org/10.1021/acssynbio.7b00316).

Identity checked against main PDF page 1; matching title and complete author list on supplement pdf page 1.

### Schinn2017

**Rapid In Vitro Screening for the Location-Dependent Effects of Unnatural Amino Acids on Protein Expression and Activity**

Song-Min Schinn; William Bradley; Ashtyn Groesbeck; Jeffrey C. Wu; Andrew Broadbent; Bradley C. Bundy.

Biotechnology and Bioengineering 114, 2412–2417 (2017). [DOI: 10.1002/bit.26305](https://doi.org/10.1002/bit.26305).

Identity checked against main PDF page 1; matching title and complete author list in docx body paragraphs 3 and 7.

### Lopez2014

**Stationary-Phase EPR for Exploring Protein Structure, Conformation, and Dynamics in Spin-Labeled Proteins**

Carlos J. López; Mark R. Fleissner; Evan K. Brooks; Wayne L. Hubbell.

Biochemistry 53, 7067–7075 (2014). [DOI: 10.1021/bi5011128](https://doi.org/10.1021/bi5011128).

Identity checked against main PDF page 1; matching title and complete author list on supplement pdf page 1.

### Reddington2015

**Directed evolution of GFP with non-natural amino acids identifies residues for augmenting and photoswitching fluorescence**

Samuel C. Reddington; Amy J. Baldwin; Rebecca Thompson; Andrea Brancale; Eric M. Tippmann; D. Dafydd Jones.

Chemical Science 6, 1159–1166 (2015). [DOI: 10.1039/c4sc02827a](https://doi.org/10.1039/c4sc02827a).

Identity checked against main PDF page 1; matching title and complete author list on supplement pdf page 1.

Publication citation is 2015; acceptance and SI copyright are 2014. Filename year is not used as evidence.

## Curation rules

`null` in JSON and an em dash in a table mean missing or not extracted, never zero. Reasons distinguish `not_reported`, `pending_digitization`, `not_applicable`, and unresolved identity or provenance. Printed numbers in text or a table may be transcribed directly; graph coordinates remain empty until formal digitization. A plot caption can establish the reported error type and replicate bound without supplying numerical bar heights.

Keep endpoint, construct, ncAA, expression system, conjugation reagent, PEG size, incubation, normalization, and source together. Assay controls are not failed-site examples. Sites absent from a selected library, not selected, not tested, or not reported are not negatives. Reused observations retain one original-data-source key; repeated plots and different computational environments do not increase experimental sample size.

No RANA scientific code, score, threshold, rotamer library, original scan, previous benchmark, README validation claim, or exploratory script is changed. No new scan, statistical significance calculation, pooled correlation, or parameter selection is performed.
