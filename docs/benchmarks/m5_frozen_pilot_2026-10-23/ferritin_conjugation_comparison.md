# Ferritin: separate eight-site conjugation comparison

This comparison retains the eight original continuous TLC endpoints from [the previous experimental addendum](../literature_m5_2026-10-23/khoshnejad2018_evidence_addendum.md), now paired in [a separate CSV](ferritin_conjugation_comparison.csv). It is not T4L stability data. Every number has its original source file/field, row and hash in the frozen records. No scan is rerun or environment selected by experimental agreement.

## Endpoint and environment fixed for this comparison

The endpoint is **reported percent fluorophore conjugated**, not successful pAzF incorporation, subunit labeling probability, soluble expression or activity. Khoshnejad main PDF p3 (1211) explicitly lists the percentages; SI p2 Figure S2 shows TLC/bar evidence. Main Methods p7 (1215) uses final 1 uM hFTL-X and hFTL-X:DBCO-AlexaFluor488 ratio 1:24, room temperature overnight. Quantitative TLC distinguishes conjugated and free fluorophore. The paper's reported denominator/concentration convention is retained without a new per-subunit conversion. Original numeric values are text transcriptions, not bar-height estimates. Site-specific N/error type/value remain missing; Figure S2's error bars are not defined.

**Assembly is primary**: the preserved 2FG8 assembly-1 prepared input retains all 24 protein chains A-X, target A, so RSA, packing and sterics include cross-subunit parent contacts. **Monomer is sensitivity analysis**: target A alone. Other 23 subunits are not simultaneously mutated, and nonprotein species are omitted. Cage interior/exterior accessibility, DBCO approach paths, conjugation kinetics and assembly energetics are not predicted. The original computational case established these two environments before this data association.

| Site | Fluorophore conjugated (%) | Assembly RSA | Assembly min score (Å²) | Assembly low-clash / 12 | Assembly tier | Monomer RSA | Monomer min score (Å²) | Monomer low-clash / 12 | Monomer tier |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S2 | 30 | 0.8231 | 0.4681 | 5 / 12 | `geometry_limited` | 0.8231 | 0.4681 | 5 / 12 | `geometry_limited` |
| I5 | 57 | 0.0383 | 11.6826 | 0 / 12 | `geometry_unfavorable` | 0.4391 | 0.7110 | 10 / 12 | `geometry_favorable` |
| Y9 | 10 | 0.0577 | 4.9697 | 1 / 12 | `geometry_limited` | 0.0577 | 4.9697 | 1 / 12 | `geometry_limited` |
| F79 | 14 | 0.0628 | 2.0560 | 3 / 12 | `geometry_limited` | 0.5292 | 0.1935 | 7 / 12 | `geometry_favorable` |
| K83 | 16 | 0.4469 | 0.1283 | 8 / 12 | `geometry_favorable` | 0.5396 | 0.1283 | 8 / 12 | `geometry_favorable` |
| K105 | 18 | 0.2497 | 9.8830 | 1 / 12 | `geometry_limited` | 0.5129 | 0.2077 | 5 / 12 | `geometry_limited` |
| L112 | 14 | 0.1173 | 2.5690 | 4 / 12 | `geometry_limited` | 0.3874 | 0.2113 | 8 / 12 | `geometry_favorable` |
| L155 | 18 | 0.0324 | 44.9199 | 0 / 12 | `geometry_unfavorable` | 0.2929 | 0.4988 | 4 / 12 | `geometry_limited` |

The CSV additionally retains packing, low-clash fraction, all three original independent ranks, input/output/sidecar hashes and exact source rows for both environments. Each rank population is the corresponding 174 scored sites, not this eight-site subset. Display values are rounded; original source strings remain in the JSON. The count uses sampled scores <=10.0 Å² from the unchanged twelve-rotamer library. Overall rank is undefined and blank in both environments.

## Reference and observed disagreement retained

2FG8 remains a maintainer-authorized **reference**, not a proven author-used PDB. The paper cites Wang 2006's 2.5 Å hFTL structure without an accession; the supplied SI does not resolve it. Eight printed SI Figure S1a parent identities and the saved full-sequence mapping support the reference joins: S2->A5 SER, I5->A8 ILE, Y9->A12 TYR, F79->A82 PHE, K83->A86 LYS, K105->A108 LYS, L112->A115 LEU, L155->A158 LEU, all insertion codes blank. Full pRSET-A fusion/junction/tag equivalence is unconfirmed.

I5 has the highest reported conjugation percentage (57%) while the **primary assembly** run is geometrically unfavorable, with 0/12 low-clash sampled rotamers. Its monomer run is favorable (10/12). Both results are shown and the primary environment is not changed to improve agreement. K83 has 8/12 low-clash assembly rotamers with 16% reported conjugation; L155 has 0/12 with 18%. This discordance is retained without reassigning thresholds or experimental success/failure. Geometry and fluorophore conjugation quantify different processes; assembly-state and full-construct uncertainties remain open.

Variant-resolved native PAGE (SI S3), TEM (S4) and SEC-HPLC (S5) are qualitative assembly evidence, not a numerical assembled fraction or independent eight-site expression/incorporation dataset. S6 covers denaturing gels for only sites 2/5/9; S7 +/-pAzF expression fractions only site 5. See the prior addendum for precise panel mapping. No pooled T4L/ferritin metric or binary performance analysis is made.
