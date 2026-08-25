# Validation plan (v1)

Goal: check whether top-ranked candidate sites overlap with real, published
incorporation sites — turns this from a demo into a checked result.

## Steps

1. Identify a published azido-alanine (or close azide-bearing analog)
   incorporation in some protein — doesn't need to be BglB.
2. Run the pipeline on that protein's structure with the same
   catalytic/binding-site annotations used in the source paper.
3. Compare top-N ranked sites (recommended tier) against the site(s) actually
   used in the paper.
4. Report overlap honestly, including partial matches and misses — a partial
   match ("3 of top 5 predicted sites align with literature-validated sites")
   is a legitimate, citable result. Do not overstate.

## Stretch (later, wet-lab)

Thought-experiment design discussed: mutate a panel of ranked surface
residues to azA, click on a fluorescent alkyne/DBCO-dye conjugate, and read
out (a) labeling efficiency as a check on SASA/accessibility prediction, and
(b) residual enzymatic activity as a check on ddG/load-bearing prediction.
Two independent readouts from one experiment. Not in scope until BglB
publication-phase work has eased up.

## Known limitations to disclose in any writeup

- ddG for ncAAs without dedicated Rosetta params is a canonical-analog proxy,
  not a true ncAA-specific estimate — must be labeled as such, not presented
  as equivalent precision to native ddG predictions.
- v1 validates on a single ncAA (azA) and a small site panel — coverage
  claims should stay scoped to what was actually tested.
- Catalytic-zone sites are out of scope for this ranking; do not claim the
  tool evaluates them.
