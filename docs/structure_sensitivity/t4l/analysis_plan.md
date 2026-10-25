# Frozen M6.3 T4L reference-structure sensitivity plan

This is a retrospective computational input-sensitivity study, not new independent
experimental validation. The historical M5 1L63 input and results remain intact.
Selection and analysis rules were saved before any M6.3 scan. Actual freeze UTC,
input/audit hashes and parameters are in [frozen_plan.json](frozen_plan.json).

## Scope and selection

Use three separate experimental X-ray structures: 1L63 (historical reference),
1LW9 and 219L. All have the same complete 164-residue C54T/C97A entity sequence,
verified against PDB SEQRES and observed author numbering/parent identities, with
PDB/mmCIF atom-level cross-checks. Author chain A, positions 1–164, blank insertion
codes map directly to entity positions. 1L63 lacks coordinates for N163/L164;
1LW9 and 219L are complete. No missing heavy atoms were found in modeled residues
relative to standard residue templates (terminal OXT/hydrogens not required).

The bounded RCSB sequence search returned 124 entities; only its first 100 hits
were inspected, then full-sequence equality was checked locally. This is not an
exhaustive catalogue or a claim of optimal reference selection. Five candidates
received full local sequence/coordinate/metadata audits. Same-background, complete,
ordinary X-ray references with good resolution were preferred over noble-gas,
high-pressure, deuterated/neutron, ligand-soak and complex/fusion cases. 1LW9 is
1.45 Å and 219L is 1.66 Å; the reference 1L63 is 1.75 Å. Structure titles about
mutant series do not define an individual entry's sequence.

2LZM has native C54/C97; 1L97 additionally has I3P and two ASU protein chains.
They are excluded, not pooled as conformational replicates and not scanned in
this study. No different-background supplement is needed to reach three inputs.
No structure was selected by its agreement with experimental outcomes. Literature
ΔTm values will not be used in this analysis.

## Frozen environment and execution

- Current merged PR #5 scientific code, recorded by Git commit and source hashes.
- pAzF, seed 42, 12 discrete library rotamers, low-clash score cutoff 10.0 Å²,
  favorable fraction 0.5; no functional annotation, relaxation or reconstruction.
- All three official biological assemblies are monomers using identity operator
  1. Use the native ASU coordinates of chain A only. Retain every available
  standard-protein heavy-atom ATOM record, including alternate records in original
  order. Exclude waters, ions, other nonprotein components and H/D consistently.
  No H/D is present in these three protein inputs. Do not apply symmetry or add
  lattice neighbors. SASA, packing and steric screening all see this same input.
- Preserve names, residue numbers, insertion codes, selected/all altloc coordinates,
  occupancies and B factors exactly. Existing Biopython selection is highest
  occupancy; ties keep the first encountered conformer. Do not average altlocs or
  optimize their selection. Verify selected identities/coordinates after writing.
- Save full original scans/metadata/logs and prepared inputs in a new ignored run
  directory. Refuse overwriting. Record source URLs, retrieval UTC/hashes,
  plan hash, exact commands, environment and scientific/script hashes.
- Failures/skips are preserved and explained, never converted to experimental
  negatives. The 2FG8-specific profile/174-site validator is not used for T4L.

## Common-site and ranking rules

The main set is the intersection of verified mappings with identical parent
residues, successful `scored` status and finite RSA, packing, minimum steric score
and low-clash fraction in all three inputs. This is expected to contain 162
positions, but actual eligibility and reasons must be reported for all 164
positions in each structure. A modeled site outside the intersection retains its
original full-structure output and rank. No failed row is silently discarded.

Report the four metrics for every common site and their across-structure minimum,
maximum and range, plus per-site common-rank ranges. Compare all three pairs;
do not select a favorable pair after seeing results. Rank directions: RSA and
low-clash fraction descending; packing and minimum steric score ascending.

Keep the CLI's three original full-structure independent ranks separately from
comparison-only common-set ranks. Use minimum/competition ranks for displayed
common ranks (matching the CLI's tie convention), and average ranks for Spearman
rho. Retain ties. Packing's common-set rank is an explicitly labeled comparison
of an existing scalar feature, not a new RANA output rank. No combined rank.

For each metric, inclusive top-10 membership means all values at least as good
as the 10th order statistic within the common set. Include the entire boundary
tie; never break ties by residue number. Report set sizes, intersection/union,
site IDs and Jaccard = intersection/union. Inclusive sets may exceed ten sites;
intersection/10 is not a valid overlap percentage. Report all four metrics, with
the three native rank metrics identified separately from packing.

Report pairwise tier transition counts, all-three tier agreement and sites with
any tier change. "Tier-stable" only means identical existing tier labels across
these inputs, not accurate experiment prediction. Do not set a data-derived
numeric cutoff for "robust" scores. Show per-site ranges and top-list membership
instead. No significance tests, fitted model, experimental correlations or
classification performance. Constant rank vectors yield blank rho with a reason.

Show K16, H31, S44, N53, L91 and K135 separately, with the same fields and rules.
Wilding sites and Wilkerson H31 are labels only; no experimental values enter
structure choice or sensitivity calculations. Plots will show pairwise metric
scatter, score/rank ranges and the six pilot sites without optimizing axes or
subsets for experimental agreement.

## Interpretation limits

Same sequence removes background-substitution differences from the primary
comparison; it does not isolate pure conformational effects. Crystal conditions,
refinement/resolution, alternate-atom representation and missing terminal
coordinates also differ. Full retained environments have 162/164/164 residues;
the common scoring set does not remove terminal atoms from the complete inputs.
The complete-input pair 1LW9/219L provides a useful separately identified pair
within the same global common set. No causal contribution is assigned by fitting.
All three share a limited crystallographic setting; they do not sample solution
ensembles, all plausible structures or experimental success probabilities.

Coordinate preservation requires exact atom/selected-coordinate correspondence
to the source PDB; PDB/mmCIF audit allows 0.0006 Å component serialization error.
Metrics are compared descriptively, not forced equal. Exact equality is required
only for parent mapping and copied coordinates; no matching tolerance is tuned
against scan results. No M5 record, scientific code or exploratory script changes.
