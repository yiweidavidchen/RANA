# Khoshnejad 2018: experimental evidence addendum

This new record links the eight reported hFTL pAzF sites to the [preserved computational case](../khoshnejad2018_hftl_computational_case.md). It does not replace its computational-only provenance. Source IDs and hashes resolve through the [inventory](literature_inventory.json); all values and source fields are retained in [the observation JSON](khoshnejad2018_observations.json). Public paper: [Khoshnejad et al., 2018](https://doi.org/10.1021/acs.bioconjchem.8b00004).

## Experimental identity and conditions

K-M PDF p7, printed p1215, Methods identifies human ferritin light-chain cDNA SC120074 in pRSET A, with pEVOL-pAzF in E. coli T7 Express Crystal. Production uses 1 mM IPTG and 1 mM pAzF, followed by a 4 h expression period, heat precipitation and FPLC purification. This is an in vivo expression system, distinct from the T4L cell-free studies.

The small-molecule screen used 1 µM final hFTL-X and a 1:24 hFTL-X:DBCO-AlexaFluor488 molar ratio, overnight at room temperature. Quantitative TLC separated free and conjugated fluorophore (K-M p7, Coupling of AlexaFluor488-DBCO to hFTL-X Nanocages). The endpoint is the reported **percent fluorophore conjugated**, not incorporation efficiency, an activity assay, or a probability of experimental success. Retain the paper's concentration/ratio convention; no subunit-level conversion is made.

## Eight-site mapping and directly reported conjugation values

Each percentage below is explicitly listed in K-M PDF p3, printed p1211, Results, conjugation-efficiency paragraph. K-S p2 Figure S2 supplies the matching TLC/bar-plot evidence. These are text transcriptions, not digitized bar heights. Parent identities are printed in K-S p1 Figure S1a. The exact reference join is documented in `preparation_manifest.json`, field `residue_mapping`, and reproduced in the observation JSON with hashes.

| Literature site → pAzF | Reference identity (chain / author number / insertion code / parent) | Fluorophore conjugated (%) | Assembly evidence |
| --- | --- | --- | --- |
| S2 | A / 5 / blank / SER | 30 | S3a; S4a; S5a |
| I5 | A / 8 / blank / ILE | 57 | S3a; S4b; S5b |
| Y9 | A / 12 / blank / TYR | 10 | S3a; S4c; S5c |
| F79 | A / 82 / blank / PHE | 14 | S3a; S4d; S5d |
| K83 | A / 86 / blank / LYS | 16 | S3a; S4e; S5e |
| K105 | A / 108 / blank / LYS | 18 | S3b; S4f; S5f |
| L112 | A / 115 / blank / LEU | 14 | S3b; S4g; S5g |
| L155 | A / 158 / blank / LEU | 18 | S3a; S4h; S5h |

Figure S2 contains error bars, but their type, numerical values, and site-specific replicate counts are not specified. `uncertainty_value`, `uncertainty_type`, and experimental N remain null. N = 3 and SEM reported for downstream mouse experiments (K-M Figure 4; K-S Figure S8) must not be imported into the eight-site TLC screen.

The reference remains **maintainer-authorized 2FG8**, not a confirmed author-used accession. K-M p2 cites Wang 2006's 2.5 Å hFTL structure without an accession; the supplied SI does not resolve it. The deposited 174-residue entity matches saved P02792 positions 2–175, and its observed author IDs are 5–178. This full-sequence match and the Figure S1 parent checks support the mapping above. They do not establish that the complete experimental fusion/junction/tag sequence is identical to the crystallographic reference. Initiator Met1 is outside the deposited entity. The legacy mmCIF database alignment disagreement remains documented in the prior case.

K-S Figure S1a also prints side-chain SASA and random-coil ratios; these are transcribed separately in JSON. They are literature structural descriptors, not independent experimental outcomes and not interchangeable with RANA whole-residue `sasa_abs` or `rsa`. No discrepancy is used to change the input or configuration.

## Assembly evidence and its limits

K-M p3 reports proper assembly and cites K-S Figures S3–S6. Native PAGE is variant-resolved in S3a (sites 2, 5, 9, 79, 83, 155) and S3b (105, 112). S4a–h (p3) provides TEM and S5a–h (p3, method continued on p4) SEC-HPLC for all eight, in that site order. S5 uses BioSep SEC-s3000 with 100% PBS, pH 7.4. These support a qualitative reported assembly/characterization record, without a numerical assembled fraction, exact replicate count, or binary assembly-failure label.

S6 (p4) is denaturing SDS-PAGE for sites 2, 5, and 9 only; it does not establish intact cage assembly by itself. S7 (p4) compares +pAzF/−pAzF lysate and fractions for site 5 only; it is not an eight-site incorporation or soluble-yield table. Antibody-conjugated site-5 DLS/TEM, downstream binding, biodistribution, and near-infrared results are available in K-M Figures 2–5 and K-S S8–S9/Tables S1–S2, but are outside this initial site-screen extraction. AF750 amine labeling and radiolabeling are not the eight-site azide/DBCO endpoint.

## Association with the existing scans

The following are copies of fields from the preserved `assembly1_chainA_pazf_ranked.csv` and `monomer_chainA_pazf_ranked.csv` in `data/processed/khoshnejad2018_hftl/`. CSV lines count the header as line 1. JSON retains the exact CSV strings, field names, input/output/sidecar hashes, and the row identity triplet. This display rounds RSA and minimum score to four decimals; it does not change the raw values.

| Site | Environment | RSA (`rsa`) | Packing (`ca_neighbors_8a`) | Minimum steric score (Å²) | Number of low-clash rotamers | Geometric tier | Separate ranks (steric / RSA / robustness) | CSV line |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S2 | assembly1 | 0.8231 | 6 | 0.4681 | 5 / 12 | `geometry_limited` | 35.0 / 1.0 / 37.0 | 2 |
| S2 | monomer | 0.8231 | 6 | 0.4681 | 5 / 12 | `geometry_limited` | 67.0 / 2.0 / 67.0 | 2 |
| I5 | assembly1 | 0.0383 | 11 | 11.6826 | 0 / 12 | `geometry_unfavorable` | 125.0 / 121.0 / 118.0 | 5 |
| I5 | monomer | 0.4391 | 7 | 0.7110 | 10 / 12 | `geometry_favorable` | 80.0 / 53.0 / 13.0 | 5 |
| Y9 | assembly1 | 0.0577 | 11 | 4.9697 | 1 / 12 | `geometry_limited` | 90.0 / 115.0 / 100.0 | 9 |
| Y9 | monomer | 0.0577 | 11 | 4.9697 | 1 / 12 | `geometry_limited` | 121.0 / 134.0 / 126.0 | 9 |
| F79 | assembly1 | 0.0628 | 10 | 2.0560 | 3 / 12 | `geometry_limited` | 67.0 / 111.0 / 71.0 | 79 |
| F79 | monomer | 0.5292 | 6 | 0.1935 | 7 / 12 | `geometry_favorable` | 20.0 / 24.0 / 51.0 | 79 |
| K83 | assembly1 | 0.4469 | 8 | 0.1283 | 8 / 12 | `geometry_favorable` | 1.0 / 22.0 / 6.0 | 83 |
| K83 | monomer | 0.5396 | 5 | 0.1283 | 8 / 12 | `geometry_favorable` | 4.0 / 21.0 / 18.0 | 83 |
| K105 | assembly1 | 0.2497 | 10 | 9.8830 | 1 / 12 | `geometry_limited` | 117.0 / 52.0 / 100.0 | 105 |
| K105 | monomer | 0.5129 | 9 | 0.2077 | 5 / 12 | `geometry_limited` | 25.0 / 32.0 / 67.0 | 105 |
| L112 | assembly1 | 0.1173 | 10 | 2.5690 | 4 / 12 | `geometry_limited` | 69.0 / 84.0 / 42.0 | 112 |
| L112 | monomer | 0.3874 | 9 | 0.2113 | 8 / 12 | `geometry_favorable` | 27.0 / 68.0 / 18.0 | 112 |
| L155 | assembly1 | 0.0324 | 13 | 44.9199 | 0 / 12 | `geometry_unfavorable` | 173.0 / 126.0 / 118.0 | 155 |
| L155 | monomer | 0.2929 | 10 | 0.4988 | 4 / 12 | `geometry_limited` | 69.0 / 85.0 / 77.0 | 155 |

`rsa = sasa_abs / sasa_max` is parent-structure whole-residue relative exposure. Packing counts other Cα atoms strictly within 8 Å. Steric scores sum squared heavy-atom van der Waals overlaps. Number of low-clash rotamers counts sampled `rotamer_scores <= 10.0 Å²` out of the fixed 12, rather than an experimental acceptability or success probability. There is no composite/overall rank. The separate ranks use `method="min"`: minimum score ascending; RSA and low-clash fraction descending, over the 174 scored rows of each environment. These meanings follow unchanged `features/structural.py`, `features/site_scan.py`, and `features/site_ranking.py`.

Assembly SASA, packing, and sterics include all 24 retained protein chains A–X; the target is A and the other 23 subunits remain in their parent state. The monomer has only A. The assembly input omits the original nonprotein residues/waters. Neither run represents simultaneous mutation of all equivalent sites, fluorophore/DBCO accessibility, cage assembly energetics, suppression, expression, or experimentally validated labeling. Cage-interior and exterior solvent accessibility are not separated. All joined sites have blank insertion codes; this does not validate the known nonblank insertion-code forwarding behavior.

Frozen scan commit/configuration and input details remain in the prior case and JSON. This addendum performs no rescoring, new ranking, correlation, significance test, binary relabeling, or threshold adjustment. The eight TLC observations count once; the two structural environments are paired computational views of the same experiments.
