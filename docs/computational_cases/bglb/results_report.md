# BglB pAzF computational application: results

Protein: **β-glucosidase B (BglB) from Paenibacillus polymyxa**.
RANA scored all 445 attempted sites. The geometric tiers were
`geometry_favorable` at 112 sites, `geometry_limited` at 175 sites and
`geometry_unfavorable` at 158 sites. These heuristic categories describe
fixed-structure geometry. This case has no corresponding pAzF experimental
validation data.

The input was **2O9P chain A, H376Q/G377R engineered apo reference**. It is not
natural WT, D2D standard or the maintainer's experimental construct. All output
identities retain the input PDB author chain, residue number and insertion code;
they do not use Foldit numbering.

The maintainer's BglB research experience motivated the choice of this case.
This is an independent RANA computation. It does not imply that the preprint,
any laboratory or D2D has conducted ncAA experiments.

## Preparation and actual scan

The prepared input retained only the 2O9P monomer's 3626 protein heavy atoms.
All source ATOM records and coordinates were preserved, including author
positions A:4–448 and blank insertion codes. Preparation removed 138 waters;
the deposited apo input contained no organic ligand or ion. No mutation,
filling, relaxation or coordinate renumbering was performed.

Solvent-accessible surface area (SASA), packing and steric screening were
**protein-only**. A ligand's presence in an original file does not mean that
RANA included its steric contacts. Removing a ligand from a holo model retains
the holo conformation; it does not produce an experimental apo structure.

Rotamers are the sampled side-chain conformations.

The [complete curated table](results/per_site.csv) retains every attempted row.
The [nine coordinate absences](results/coordinate_absences.csv) are recorded
separately from scoring failures. They are never treated as tested experimental
negatives.

## Predefined independent displays

The three independent lists contain 10 sites for `steric_rank`, 10 for `rsa_rank`
and 20 for `rotamer_robustness_rank`. For each ranking, the list includes every
site tied with the site in tenth position, so its size can exceed the nominal
cutoff. The union of these lists contains **31** sites. It is displayed in
structural identity order in [candidate_overview.csv](results/candidate_overview.csv)
and [the full overview table](candidate_overview.md), without a composite ranking.
Original ranks, individual memberships and cutoff boundaries remain in
[top_list_memberships.csv](results/top_list_memberships.csv) and
[top_lists.json](results/top_lists.json).

Functional annotations were added after scoring and did not change scores,
tiers or independent ranks. All eleven functional-context sites remain in the
complete results and in their separate table below. The overview union includes
only sites selected by at least one of the three inclusive ranking lists.
Functional flags neither exclude sites from selection nor guarantee membership
in that union. In this run, none of the flagged sites belongs to the overview
union.

## All eleven functional-context sites

Among the maintainer's eleven functional-context sites, 7 are
`geometry_unfavorable` and 4 are `geometry_limited`; none is
`geometry_favorable`. This is a description of their geometric results, not
evidence of functional-site identification or experimental predictive performance.

The table retains all eleven sites, with verified parent residues and numbering
mappings. UniProt reference annotations identify E167 as the
proton donor and E356 as the nucleophile; the original ECO:0000255 evidence is
retained. No specific experimentally proven roles are newly assigned to the
other sites here. Evidence sources remain in the
[full context CSV](results/functional_context.csv).

A separate [literature source check](site_mapping.md#post-scan-literature-supplement-2026-10-27),
completed after scanning on 2026-10-27, records site-level evidence from
[Isorna et al. (2007)](https://doi.org/10.1016/j.jmb.2007.05.082) and
[Carlin et al. (2016)](https://doi.org/10.1371/journal.pone.0147596). It distinguishes
structural contacts and the authors' mechanistic interpretations from direct
conventional-substitution experiments. Below-detection protein yield is not
evidence of catalytic inactivity, and unresolved source discrepancies remain
explicit. This later review does not change the frozen flags or rankings and
provides no experimental validation of pAzF substitutions.

RSA describes residue solvent exposure relative to a reference area, and
packing counts nearby C-alpha atoms. The minimum steric score is the lowest
overlap score among the sampled conformations. Numbers below are rounded only
for display; machine-readable files retain full source precision. All scores
and ranks come from the same run and the same-named raw fields. The source hash
and source row in `per_site.csv` locate each result.

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

Functional annotations and the original Gly/Pro cautions must remain visible
even when a geometric tier is favorable. The low-clash fraction is the proportion
of the 12 sampled conformers with scores <=10.0 Å². It is neither an
experimental success probability nor the fraction of all physical conformations.
These geometric results do not support inferences about activity, incorporation,
expression, stability or conjugation.

## Engineered-background context

Both engineered sites are shown separately from the functional list:

| PDB author site | RSA | Packing | Min steric (Å²) | Low-clash count/12 | Geometric tier | Steric/RSA/fraction ranks | Functional flag |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A:Q376 | 0.209 | 11 | 21.127 | 0/12 | geometry_unfavorable | 357/168/288 | False |
| A:R377 | 0.562 | 8 | 0.670 | 8/12 | geometry_favorable | 128/36/32 | False |

Their structural background can affect the rest of the protein. This case does
not compare them with a natural sequence or infer mutational effects.

## Scope and remaining limits

2JIE remains a reference for mechanism and ligand context, with no new scan.
2Z1S, 2O9R and 2O9T remain future candidates pending review. They were not
downloaded, compared or newly analyzed. The D2D holo candidate was not rescored.

Interpretation is limited by the single fixed reference, the monomer-only
environment, omitted ligand and water effects, discrete rotamers and heuristic
tiers. This case includes no fitted model, correlation with experiments or
performance evaluation, and makes no experimental success claim. It used no
private paths, HPC models, unpublished experiments, MD, ML or second ncAA.

## Execution and source records

One scan used RANA 2c690edaae77d4160134c6382abf00901d88d529 with seed 42,
the frozen 12-rotamer pAzF library, a 10.0 Å² cutoff and the favorable-fraction
setting of 0.5. Commands, dependencies and reproduction scope are described in
[reproduction](reproduction.md). The [execution summary](execution_summary.json)
records the code, hashes, actual execution times, environment and detailed local
run locator. The [structure review](structure_review.md) documents source and
preparation history and their limitations. These records document software
execution and input provenance. No fresh-environment or cross-platform validation
is claimed.
