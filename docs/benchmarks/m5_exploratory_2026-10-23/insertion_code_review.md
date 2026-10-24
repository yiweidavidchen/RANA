# Insertion-code forwarding: confirmed narrow defect

Reviewed against Git HEAD `b3029b934779fa8d03d00dbf7fe4c4d7e4a592ee`.
This record supplements the earlier unresolved list without editing that frozen
snapshot. No scientific source file was modified.

## Actual call chain

1. [`scan_pazf_sites`](../../../ncaa_site_rec/features/site_scan.py)
   calls `score_pazf_site` at lines 118–124 and **does** forward
   `insertion_code=insertion_code`.
2. [`score_pazf_site`](../../../ncaa_site_rec/features/pazf.py), line 368,
   passes the code to `get_target_backbone` and `get_environment_atoms`
   (lines 385–397); target placement and environment selection preserve it.
3. Its call to `exclude_bonded_neighbor_overlaps` at lines 454–460 passes
   chain and residue number but **omits insertion_code**.
4. The helper at lines 241–279 defaults the argument to `""` and uses it in
   the target mask. It is intended to zero the target CB-to-N/C 1–3 overlaps.
   For a nonblank target, the intended self contacts are retained. If a blank-code
   residue shares its chain/number, that other residue's N/C contacts are wrongly
   exempted instead. The total score is the sum of squared overlap values.

## Minimal reproducible evidence

[`probe_insertion_code.py`](probe_insertion_code.py) calls the current helper
on a one-row overlap matrix `[1, 2, 3, 4]`, environment atoms A:31:A N/C then
A:31:blank N/C, and sidechain index `[2]` (CB). Omitted argument returns
`[1, 2, 0, 0]`; explicit `insertion_code="A"` returns `[0, 0, 3, 4]`.
This isolates the wrong mask without assumptions about experimental measurements.

An additional label-only probe scores 1L63 A31 with identical coordinates before
and after relabeling only that residue's blank code to A in an in-memory copy.
Minimum scores change from 0.7073242040962118 to 2.1260110962059193 Å².
Instrumentation observes all 12 helper calls omit the code. Low-clash count stays
4/12 in this example: a numeric score difference does not imply that the tier
must change. This is diagnostic evidence, not a replacement scan or a new
physical structure/experimental variant. Exact hashes and calls are in
[`insertion_code_evidence.json`](insertion_code_evidence.json).

From the repository root in an installed RANA environment:

```powershell
$env:PYTHONPATH = (Get-Location).Path
python -B docs/benchmarks/m5_exploratory_2026-10-23/probe_insertion_code.py
python -B docs/benchmarks/m5_exploratory_2026-10-23/probe_insertion_code.py --pdb data/raw/1L63.pdb
```

The synthetic probe needs no PDB. Both commands print JSON; do not redirect into
the existing evidence file. The optional input is available from the public
1L63 structure entry as described in the benchmark reproduction guide.

## Impact and separate repair proposal

Targets with nonblank insertion codes are affected through this call chain.
Scores can be inflated by retained self overlaps and, where a same-number blank
residue exists, reduced by exemptions of other-residue contacts. The net effect
is input-dependent; minima, low-clash counts/fractions, ranks and tiers can change.
No magnitude or direction is assumed universally.

Blank-code targets use the intended default, so this particular omission does
not affect the six current T4L targets or eight mapped ferritin targets. Their
frozen CSV mappings explicitly retain blank codes; prepared input structures
are checked separately. This conclusion concerns this defect only, not every
possible insertion-code behavior or full scientific correctness.

A separate maintainer-approved change should forward the argument at this one
call. Add regression coverage for (a) scan-to-score-to-helper forwarding of A/B
codes, (b) simultaneous chain/number matches with blank and nonblank codes,
(c) another chain with the same number, (d) invariance under residue-label-only
changes with no colliding identity, and (e) unchanged blank-code outputs.
Use a frozen deterministic fixture and assert rotamer scores as well as retained
identity and diagnostic/status rows. This task records the proposal only; no
issue was opened and no fix was implemented.
