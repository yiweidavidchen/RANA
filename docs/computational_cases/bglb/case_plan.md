# Accepted single-input BglB computational case plan

This records the pre-scan plan for β-glucosidase B (BglB) from Paenibacillus
polymyxa, accepted by the maintainer on 2026-10-25. It is a computational
application, not a preregistered experiment or independent experimental validation.
The [original configuration](case_plan.json) remains a historical pre-scan record;
the [frozen execution plan](execution_plan_2026-10-25.json) records acceptance before
execution. See the [results](results_report.md) and [execution record](execution_summary.json).

## Input and environment

Use only **2O9P chain A, H376Q/G377R substrate-free (apo) reference**. The official
input SHA-256 is `94573091f10dd18ffc4d3bae84e90f3c151294d2590818133a3d5ee2c8de328d`. Assembly 1 is a monomer with identity
operator; retain chain A protein heavy atoms in one MODEL, original coordinate
order, author numbers 4–448 and insertion codes. No coordinate transformation,
relaxation, mutation, completion or renumbering will be applied to prepared input.
Rigid fits in the review were in-memory comparisons, not input preparation.
Remove its 138 waters and any H/D/nonprotein records from the future scan input.
No organic ligand or ion is present in this deposited model.

SASA, packing and steric screening will see the same protein-only monomer.
There are no retained partner subunits or crystal neighbors. Current RANA
`io/structure.py` retains standard protein residues for atom tables and
`features/structural.py:compute_sasa` removes nonstandard residues. Merely leaving
LG1/G2F in a raw file does **not** make this a ligand-aware analysis. SASA also
retains protein hydrogens when supplied, so the heavy-atom input policy must be
explicit, rather than relying only on steric scoring's H/D exclusion.

D2D and 2JIE supply context only; there is no second scan or structure selection
based on agreement with expected geometric results. If D2D is later authorized
instead, make a new plan: removing LG1 would yield a **ligand-removed D2D holo
reference**, with its holo conformation, not an experimentally determined apo.

## Frozen pAzF configuration and execution record

Use RANA `0.1.0.dev0`, the merged code at `2c690edaae77d4160134c6382abf00901d88d529`, and existing v0.1 settings:
12 discrete rotamers, seed 42, steric cutoff 10.0 Å², favorable fraction 0.5 and
existing SASA defaults (500 sampling points). No library, thresholds, sampling,
functional penalties, fitting or composite score will change. Supply no
`--functional-residues` to the scoring invocation; join annotations afterward.
At execution record the actual code/environment and source/prepared file hashes.
If code later differs, review that difference before execution rather than
backfilling this plan as though it used the later code.

Portable command pattern (the exact executed arguments are in the local run record):

```text
python -I -B -m ncaa_site_rec.cli rank --pdb NEW_PREPARED_2O9P_A_PDB --chain A --ncaa pazf --seed 42 --low-clash-threshold 10.0 --favorable-fraction 0.5 --output NEW_RUN_DIRECTORY/ranked.csv
```

Use a new ignored directory with overwrite refusal. Preserve input, actual
commands, stdout/stderr, raw CSV and metadata. Validate the exact 445 observed
identities, unique chain/number/insertion-code keys, parent residues, statuses,
diagnostics and 12 finite rotamer scores for each scored row. Keep any failed or
skipped row with its diagnostic; do not label it an experimental failure.
Keep author positions -5 through 3 in a separate declared-coordinate-absence
ledger; do not silently treat absent or unreported sites as tested negatives.

## Candidate display rules, fixed before scanning

1. Publish the complete per-site result, including all statuses/reasons and
   existing Gly/Pro cautions. Show RSA, local packing, minimum steric score,
   low-clash fraction/count interpretation, original tier and independent ranks.
   The fraction counts sampled geometries, not experimental success probability.
2. Retain the existing independent `steric_rank` (ascending minimum score),
   `rsa_rank` (descending RSA) and `rotamer_robustness_rank` (descending fraction).
   Preserve minimum/competition ties. For each top-10 display use the tenth
   order-statistic boundary and include every tie; report actual set sizes.
3. An overview may show the union of these three sets, in chain/author-number/
   insertion-code order with all three rank columns. This is not a new ranking
   or weighted/composite score. Do not pick a preferred metric afterward.
4. Separately show all 11 verified functional-context sites regardless of their
   geometric outcome, plus Q376/R377 background context. Do not remove risky or
   inconvenient sites from the full results, mask the functional region, or
   interpret an unflagged site as functionally safe.
5. Join annotations with the full identity key and checked parent. Role source
   and evidence level remain explicit; no automatic geometry/functional fusion.

## Scientific boundary and remaining conditions

There are no corresponding pAzF experiments in this case. No claim follows about
incorporation, expression, stability, activity, conjugation, the maintainer's
preprint/construct or any laboratory's ncAA work. Do not compute success
probabilities, experiment correlations or performance metrics. No unpublished
measurements, private Hive data, HPC models, nylon hydrolase, MD, ML or second
ncAA is included.

The maintainer accepted the engineered apo background and author numbering;
preparation validation and execution have since completed in a separate new
directory. The earlier structure-review-only task generated no scan-ready input;
its original documents remain archived. Unknown D2D processing history/licensing
remains unresolved for a future D2D-specific case. 2Z1S, 2O9R and 2O9T are only
future candidates pending review; no download or analysis was added for them.
