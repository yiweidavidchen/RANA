# M6 plan: structure reliability, sensitivity and computational applications

Status: **planned only; not started in the M5 closeout**. Scope supplied by the
maintainer on 2026-10-24. No new wet experiments are required. M6 extends the
[M5 curated-evidence pilot](m5_closeout_2026-10-24.md); it is not a claim that
structure-to-scan portability or scientific validation was already completed.

## Planned work and acceptance evidence

1. **Insertion-code reliability.** Repair the confirmed forwarding omission
   documented in the [call-chain review](m5_exploratory_2026-10-23/insertion_code_review.md).
   Add focused regression tests for nonblank codes, same-number blank/nonblank
   residues and chain disambiguation. Verify blank-code case rotamer scores,
   minima, fractions, tiers and existing independent ranks remain unchanged.
   Any changed output is a new versioned run, not a replacement of the M5 freeze.
2. **Reference-structure sensitivity.** Compare multiple reasonable structures
   of the same protein. Record selection rationale, identity, construct/sequence
   differences, missing residues/atoms, chains, mapping and preparation before
   inspecting agreement. Compare site scores, tiers and existing ranks under a
   declared common-site and rank-population policy. Do not choose structures
   based on better agreement with literature outcomes.
3. **Ferritin environment sensitivity.** Continue assembly/monomer comparisons
   with explicit cage, chain, cross-subunit-contact and modeling assumptions.
   Retain assembly as the primary M5 environment and its discordant observations.
   Distinguish target-subunit substitution in a parent cage from simultaneous
   mutation of every subunit. Record new sensitivity runs separately.
4. **BglB pAzF computational site-selection case.** Establish structure identity,
   numbering and parent mapping before scanning; associate sourced functional
   site annotations with candidate selection. Explicitly state that corresponding
   ncAA experimental validation is unavailable. Do not create experimental
   success/failure labels or claim validated incorporation, activity or stability.
5. **Portable preparation and scanning.** Replace host-specific assumptions with
   explicit input/output paths, public source retrieval instructions, hash checks
   and reproducible configurations. Test reconstruction and scans in a new
   environment using fresh output directories. Record actual commit, dirty state,
   dependencies and preparation decisions. Keep publisher PDFs optional to the
   computational structure workflow and preserve old provenance gaps.

## Boundaries

M6 does not include a new ncAA, ML models, MD, literature-driven tuning or a new
composite score. A second ncAA is only an **M7 candidate**, not an approved M6
deliverable. Apart from the separately justified insertion-code repair, do not
silently change frozen sampling, thresholds or the rotamer library. Any additional
scientific behavior change needs maintainer authorization, rationale and regression
evidence. Existing independent rankings do not become a new combined ranking.

Structure sensitivity and successful execution are computational evidence, not
wet-lab or predictive-performance validation. No new wet experiments are an M6
completion requirement. Scientific uncertainty about old experimental constructs
or replicate counts may remain documented without inventing missing data.

## Execution gate

This document records a future plan only. Start M6 implementation in a separately
authorized task/branch, preserve all M5 snapshots and seven exploratory scripts,
and use new versioned outputs. Do not commit, push or publish without explicit
maintainer approval. The M5 closeout performs documentation and reproducibility
checks only; it implements none of the work listed above.
