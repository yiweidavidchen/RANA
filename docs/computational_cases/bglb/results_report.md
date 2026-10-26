# BglB pAzF computational application: results

Protein: **β-glucosidase B (BglB) from Paenibacillus polymyxa**.
Input: **2O9P chain A, H376Q/G377R engineered apo reference**, not natural WT,
D2D standard or the maintainer's experimental construct. All output identities
use input PDB author chain, residue number and insertion code, not Foldit numbers.
Case selection originated from the maintainer's BglB research experience. This
is an independent RANA computation and does not imply that the preprint, any
laboratory or D2D has conducted ncAA experiments. There are no corresponding
pAzF experimental validation data in this case.

## Preparation and actual scan

Prepared only the 2O9P monomer's 3626 protein heavy atoms, preserving all source
ATOM records and coordinates, author positions A:4–448 and blank insertion codes.
Removed 138 waters; no organic ligand or ion was present in this deposited apo
input. No mutation, filling, relaxation or coordinate renumbering was performed.
SASA, packing and steric screening are **protein-only**. A ligand in an original
file does not imply RANA considered ligand sterics. Removing ligand from a holo
model retains the holo conformation and does not create an experimental apo.

One scan used RANA 2c690edaae77d4160134c6382abf00901d88d529, seed 42, the frozen 12-rotamer pAzF
library, 10.0 Å² cutoff and favorable fraction 0.5. Functional annotations were
joined afterward without modifying scores, tiers or independent ranks. The
[execution summary](execution_summary.json) preserves code, hashes, actual times,
environment and the detailed local run locator; it is software execution evidence,
not experimental predictive validation.

Status counts: {"scored": 445}.
Geometric tier counts: {"geometry_favorable": 112, "geometry_limited": 175, "geometry_unfavorable": 158}.
The [complete curated table](results/per_site.csv) retains every attempted row.
The [nine coordinate absences](results/coordinate_absences.csv) are separate from
scoring failures and never treated as tested experimental negatives.

## Predefined independent displays

All cutoff ties are included at the tenth order statistic. Actual list sizes:
steric_rank: 10; rsa_rank: 10; rotamer_robustness_rank: 20.
Their union contains **31** sites, displayed in structural identity
order in [candidate_overview.csv](results/candidate_overview.csv) and
[the full overview table](candidate_overview.md). This union is not a composite
ranking. Original ranks, individual memberships and boundaries remain in
[top_list_memberships.csv](results/top_list_memberships.csv) and
[top_lists.json](results/top_lists.json). No functional site was filtered out.

## All eleven functional-context sites

These are maintainer-provided flags with verified parent/number mapping, not a
model-derived exclusion set. UniProt reference annotations identify E167 as
proton donor and E356 as nucleophile (original ECO:0000255 evidence retained).
Other sites are not newly assigned specific experimentally proven roles here.
The [full context CSV](results/functional_context.csv) carries evidence sources.
Numbers below are rounded for display only; machine-readable files retain full
source precision. All scores/ranks come from the same run and same-named raw
fields, as located by source hash and source row in `per_site.csv`.

| PDB author site | RSA | Packing | Min steric (Å²) | Low-clash count/12 | Geometric tier | Steric/RSA/fraction ranks | Functional flag |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A:Q22 | 0.002 | 14 | 69.029 | 0/12 | geometry_unfavorable | 443/390/288 | True |
| A:R79 | 0.001 | 14 | 23.260 | 0/12 | geometry_unfavorable | 368/408/288 | True |
| A:H122 | 0.020 | 13 | 8.096 | 1/12 | geometry_limited | 279/315/274 | True |
| A:N166 | 0.002 | 13 | 17.150 | 0/12 | geometry_unfavorable | 333/387/288 | True |
| A:E167 | 0.062 | 11 | 48.815 | 0/12 | geometry_unfavorable | 435/262/288 | True |
| A:N296 | 0.007 | 13 | 26.274 | 0/12 | geometry_unfavorable | 380/365/288 | True |
| A:Y298 | 0.129 | 11 | 1.276 | 5/12 | geometry_limited | 174/217/113 | True |
| A:E356 | 0.038 | 13 | 37.464 | 0/12 | geometry_unfavorable | 419/288/288 | True |
| A:W402 | 0.024 | 14 | 2.416 | 4/12 | geometry_limited | 205/306/132 | True |
| A:E409 | 0.082 | 11 | 12.172 | 0/12 | geometry_unfavorable | 306/248/288 | True |
| A:W410 | 0.043 | 8 | 5.295 | 5/12 | geometry_limited | 248/282/113 | True |

Functional annotations and original Gly/Pro cautions must remain visible even
where a geometric tier is favorable. Low-clash fraction is the fraction of 12
sampled conformers scoring <=10.0 Å²; it is neither experimental success
probability nor the fraction of all physical conformations. No interpretation
of activity, incorporation, expression, stability or conjugation follows.

## Engineered-background context

Both engineered sites are retained separately, not hidden by the functional list:

| PDB author site | RSA | Packing | Min steric (Å²) | Low-clash count/12 | Geometric tier | Steric/RSA/fraction ranks | Functional flag |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A:Q376 | 0.209 | 11 | 21.127 | 0/12 | geometry_unfavorable | 357/168/288 | False |
| A:R377 | 0.562 | 8 | 0.670 | 8/12 | geometry_favorable | 128/36/32 | False |

Their structural background can affect the rest of the protein; this case does
not compare them with a natural sequence or perform mutational-effect inference.

## Scope and remaining limits

2JIE remains a mechanism/ligand reference, without a new scan. 2Z1S, 2O9R and
2O9T are future candidates pending review only: no download, comparison or new
analysis was performed for them. The D2D holo candidate was not rescored.
Single fixed reference, monomer-only environment, omitted ligand/water effects,
discrete rotamers and heuristic tiers limit interpretation. There is no fitted
model, experiment correlation, performance evaluation or experimental success claim.
No private paths, HPC models, unpublished experiments, MD, ML or second ncAA
were used. Source/preparation history limits from the [structure review](structure_review.md)
remain explicit. No fresh-environment or cross-platform validation is claimed.
