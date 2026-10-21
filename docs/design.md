# RANA design and implementation status

This document describes `0.1.0.dev0` at M4.6. The active CLI and its tests,
rather than historical design sketches, define current behavior. RANA screens
fixed-structure **geometric accommodation** of pAzF; it has not demonstrated
predictive validity for incorporation, expression, retained function, stability,
or labeling efficiency.

## Implemented pipeline

`rana rank` calls `build_ranked_pazf_table` in
[`site_features.py`](../ncaa_site_rec/features/site_features.py):

```text
PDB first model, standard amino acids, all supplied protein chains
    -> residue identities and C-alpha packing
    -> selected-chain structural features and optional functional distances
    -> 12 pAzF rotamers per selected-chain site in the protein environment
    -> three independent ranks, geometric tiers, and diagnostics
    -> residue-ordered CSV and JSON run metadata
```

There is no composite score, functional exclusion gate, structural veto, or
objective-specific scoring in this path. Rows are sorted in ascending order by
chain ID, residue number, and insertion code, matching `build_pazf_feature_table`.
The CSV is not sorted by a single overall recommendation rank.

### Inputs and structure handling

- Required CLI arguments: `--pdb`, `--ncaa`, and `--output`.
- Supported ncAA aliases: `pazf`, `azf`, and `4ii` (case insensitive).
- Defaults: chain `A`, seed `42`, low-clash threshold `10.0`, favorable fraction
  `0.5`. No catalytic or binding-site annotation is required.
- `--functional-residues A:11,A:20,A:10B` optionally supplies chain-qualified
  residue numbers with insertion codes. In `rank`, these must occur in the
  selected chain and have C-alpha coordinates; other-chain annotations are
  rejected because the distance table has already been filtered to that chain.
- Nonempty `--catalytic-residues` and `--binding-site-residues` lists are legacy
  placeholders rejected by the CLI. There is no user exclusion-list option.
- The parser uses the first PDB model and Biopython's selected alternate
  locations. Only standard amino-acid residues are retained. Waters, ligands,
  nonstandard residues, and their atoms do not contribute to the calculations.
  Supplied protein chains contribute to the environment; biological assemblies
  and crystal symmetry mates are not generated automatically.
- Sites missing N, CA, or C are retained as `skipped` with
  `incomplete_backbone`; handled site-scoring errors are retained as `failed`.
  Nonstandard residues are filtered upstream of the CLI scan, even though the
  lower-level scanner can mark them as skipped.

`rana inspect --pdb ... --output ...` exports structural features for all
retained chains, optionally with functional distances, without pAzF screening
or a metadata sidecar.

### Structural features

[`structural.py`](../ncaa_site_rec/features/structural.py) computes:

- WT residue SASA with Biopython Shrake-Rupley, 500 sampling points per atom.
  Only standard protein residues remain, but explicit H/D atoms are not removed
  by this SASA function. The heavy-atom-only policy below applies to sterics.
- RSA as observed SASA divided by the residue-specific Tien 2013 maximum ASA
  constants in `asa_reference.py`; it is not clipped to [0, 1].
- `ca_neighbors_8a`: other C-alpha atoms at distance strictly less than 8 Å,
  across all supplied protein chains. This is a count, not a normalized packing
  tolerance score.
- Optional `distance_to_functional_site_ca`: minimum C-alpha distance to the
  supplied annotations, including zero at an annotated residue. This feature
  does not alter ranks or tiers and does not establish functional tolerance.

### pAzF geometry and steric score

[`pazf.py`](../ncaa_site_rec/features/pazf.py) builds L-pAzF from its hard-coded
SMILES using RDKit ETKDGv3 and the supplied seed. The rotamer grid is the
Cartesian product:

```text
chi1 = -60, 60, 180 degrees
chi2 = -90, 0, 90, 180 degrees
3 x 4 = 12 equally counted conformers per successfully scored site
```

These are discrete Phe-like proxy states, not a validated pAzF energetic
rotamer library or a probability-weighted conformational ensemble. The seed
controls initial embedding, not random selection of the 12 angle pairs.
The side chain is placed using the target N/CA/C geometry and a constructed
CB, with rigid side-chain alignment and no protein relaxation.

The environment removes the target side chain and target CA, retains its
N/C/O/OXT, and includes other retained protein residues across chains.
Hydrogen and deuterium are removed from the steric environment. pAzF scoring
uses side-chain heavy atoms. The radius lookup supports C/N/O/S with radii
1.70/1.55/1.52/1.80 Å. Unsupported environment elements can cause site failures.
CB-to-target-N/C contacts are excluded from the overlap penalty for the
blank-insertion-code sites in the public examples. A confirmed omission in
`score_pazf_site` leaves `insertion_code` out of the call to
`exclude_bonded_neighbor_overlaps`, so the helper uses its blank-code default.
For nonblank insertion codes, target CB-to-N/C penalties can remain, while
contacts to a different blank-code residue with the same chain and residue
number can be incorrectly excluded. This can alter clash scores, steric and
rotamer-robustness rankings, and geometric tiers. Both public examples have
blank insertion codes and do not test this case. A fix and focused regression
test belong to separate maintainer-authorized work; M4.6 documents the omission
without changing scientific code.

```text
overlap(i,j) = max(0, radius(i) + radius(j) - distance(i,j))
steric_score = sum(overlap(i,j)^2) over included atom pairs
low_clash_fraction = count(rotamer score <= threshold) / 12
```

The score is a squared-distance overlap penalty (Å²), not an energy or a
substitution free energy. The scan reports all rotamer scores, their minimum,
mean and median, best sampled chi1/chi2, and low-clash fraction.

### Ranks and tiers

[`site_ranking.py`](../ncaa_site_rec/features/site_ranking.py) ranks scored
sites independently by minimum steric score ascending, RSA descending, and
low-clash fraction descending. Ties receive the minimum shared rank
(`1, 1, 3`, for example). Missing values remain unranked.

With threshold `T = 10.0` and favorable fraction `F = 0.5`:

- `geometry_favorable`: minimum score <= T and low-clash fraction >= F
  (at least 6 of 12 at defaults).
- `geometry_limited`: minimum score <= T and low-clash fraction < F.
- `geometry_unfavorable`: minimum score > T.
- `not_evaluated`: unscored or missing tier-defining values.

RSA, packing, and functional distances do not enter the tier rules. Glycine
and proline receive backbone caution flags without changing the tier. The
`reason` column describes scan diagnostics; `ranking_reason` explains tier
assignment. None of these tiers establishes experimental suitability.

### Output and reproducibility

The CSV preserves residue identity, features, ranks, tiers, and diagnostics.
The `.metadata.json` sidecar records input/output SHA-256 hashes, parameters
(including optional functional IDs), observed rotamer counts, status/tier
counts, and available Git revision and tracked-change status. Git lookup uses
the working directory; run from the repository root. The sidecar does not
record dependency versions, timestamps, or all hard-coded scientific constants.
See [reproducible examples](examples.md) for a separate environment record.

After producing artifacts, `rank` exits 1 if no site was scored; it exits 0
with a warning if some sites failed and at least one scored. Earlier input or
feature-building errors may stop before artifacts are produced.

## Historical proposals and inactive scaffolding

Earlier design notes described a broader safe-incorporation recommender.
Those proposals are retained here as historical context, not current behavior:

- Catalytic/binding annotations as required inputs, a 6 Å functional exclusion
  zone, structural vetoes, and user-defined exclusions.
- A weighted geometric-mean compatibility score using accessibility, rotamer
  compatibility, packing tolerance, and load-bearing risk. Proposed weights
  0.30/0.35/0.25/0.10 were hypotheses; they were never implemented in the active
  pipeline or fitted to experimental evidence.
- `recommended`, `conditional`, and `avoid` tiers, confidence downgrades,
  minimum heavy-atom functional distances, and energetic refinement.
- Rich `NCAA`/`Structure`/`CandidateSite` schemas as the main pipeline interface.

`models.py` and `scoring/rank.py` retain dataclass scaffolding and a separate
functional-gate function with unit tests. They are not called by `rana rank`.
The latter's `score_site` returns a placeholder 0.0 for ungated sites.
`features/ddg.py` returns a not-run stability record; `load_bearing.py` returns
None; `structural.compute_pazf_steric_proxy` raises `NotImplementedError`.
The pAzF YAML contains pending identity/geometry fields and is not loaded by
the active conformer generator. It is not a runtime parameter file.
Presence of these modules does not mean these features are implemented.

## Future research and release decisions

- M1–M4.5 cover the initial pipeline and computational smoke validation.
- M4.6 is documentation and reproducibility cleanup, with no scoring changes.
- M5 is a literature-grounded retrospective benchmark: experimentally tested
  sites, baseline comparisons, evaluation metrics, and uncertainty analysis.
  It remains unimplemented; see [validation plan](validation.md).
- Later work may address functional/disulfide constraints, reactive-handle
  accessibility, additional ncAAs, energetic/ensemble methods, experimental
  validation, and potentially ML. These are research directions, not release
  commitments or available CLI modes.

The former instruction to tag `v0.1.0` after a T4L scan, functional gates, and
literature overlay was an outdated proposal. The version remains
`0.1.0.dev0`. M4.6 completion means documentation agrees with code, examples
and automated checks have been run with their environment and limitations
recorded, and unresolved issues are disclosed. It does not authorize a release
tag or establish experimental predictive validity. A stable release's scope,
evidence requirements, and packaging checks require a separate maintainer
decision.
