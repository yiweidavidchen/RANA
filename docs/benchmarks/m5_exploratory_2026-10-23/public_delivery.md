# Public reproducibility preparation and remaining conditions

## Current human-review status: 2026-10-24

Yiwei Chen completed human image checks of K16, S44, N53, L91, K135 and H31
on **2026-10-24**, reporting all six as pass. The
[dated human review](review/human_review_2026-10-24.md) and
[machine-readable record](review/human_review_2026-10-24.json) preserve the actual
feedback. This is the maintainer's check of the agent's digitization against
original figures and unannotated/annotated images, not blinded review, a second
independent digitization, or experimental prediction-performance validation.
Frozen values, analysis results and the original pending checklist remain unchanged.

## Proposed files, not staged publication

[`public_manifest.json`](public_manifest.json) explicitly inventories the small
benchmark documentation, curated CSV/JSON, scripts, and our own two scatter PNGs
with sizes and SHA-256. This includes the pre-existing evidence and freeze records
as append-only history. It excludes the local pause handoff, publisher images,
full papers and raw/processed data. The seven root exploratory scripts are not
part of this manifest. Nothing has been staged, committed or pushed.

[`delivery_checks.json`](delivery_checks.json) lists local links and their
fresh-clone classification. A link to ignored data is not made public just
because it works on the curator's machine. The historical digitization-method
and current human-review documents link six publisher-derived native/crop/overlay
images under ignored `data/processed/`; these remain local-only until regenerated.
Local drive paths in source metadata are provenance, not public download links.
Literature DOI entries are available in the inventory.

Small frozen tables already contain the columns needed to run the exploratory
analysis: no raw scans or paper PDFs are required for that level of reproduction.
Keep those tables and `frozen_records.json`, the plan, scripts and calibration
JSON trackable under docs/benchmarks. Do not add a global data-directory ignore
exception. Review the exact manifest before any later authorized staging.

## Reproduce the analysis from a fresh checkout

Use a separate environment with Python >=3.10, NumPy, pandas and Matplotlib.
The actual run used Python 3.13.12, NumPy 2.5.4, pandas 3.0.6 and Matplotlib
3.11.2; the generated JSON records exact versions, HEAD, dirty status, code hash
and input hashes. These are analysis dependencies, not new RANA dependencies.
An optional version snapshot is [requirements-analysis.txt](requirements-analysis.txt).

From the repository root:

```powershell
python -B docs/benchmarks/m5_exploratory_2026-10-23/analyze.py --output data/processed/m5_exploratory_reproduction_new
```

The directory must not exist. Expected outputs: results.json, results.md,
t4l_scatter.png, ferritin_scatter.png. The result Markdown's plan link assumes
the canonical documentation layout; for a reproduction in a data directory,
read the original plan in docs/benchmarks. Numerical coefficients should match;
execution time/status metadata and figure rendering can differ across hosts.
The script refuses duplicate observation IDs, checks all 52 full/deletion
coefficient pairs by alternative rank/sign-matrix calculations, and includes
perfect/reversed/tied/constant diagnostic examples. No SciPy dependency or
p-values are needed. Kendall's normalization follows the
[official tau-b definition](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kendalltau.html);
see also the [Spearman reference](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html).
These checks verify implementation of this analysis, not experimental validity.

The [2026-10-24 replay record](curated_reproduction_check_2026-10-24.json)
documents a targeted replay of this unchanged analysis in the existing analysis
environment, from a working directory outside the repository. An access guard
denied papers, ignored raw/processed inputs and RANA scientific source. All eight
cohort/metric results and 44 leave-one-out results, plus the existing output
Markdown and two plot hashes, matched. Only the two curated input CSVs were read.
This is a reproducibility check, not a new analysis or an independent validation.
The [verification script](verify_curated_reproduction.py) can repeat this check:

```powershell
python -B docs/benchmarks/m5_exploratory_2026-10-23/verify_curated_reproduction.py --output <new-replay-directory> --report <new-report.json>
```

Use fresh paths. The strict plot-hash comparison is intended for the recorded
environment; other rendering environments may differ. No clean-environment
dependency installation was tested and full structure-to-scan reproduction is
not claimed. The original script's historical pending-review fields remain
execution metadata; the dated maintainer review above is the current status.

## Regenerate digitization materials: user-supplied PDFs required

Obtain lawful copies of Wilding 2018 and Wilkerson 2020 main PDFs matching the
SHA-256 values in the frozen calibration JSON. Obtain their SI as well to review
the original exact-value search and assay context. Other literature intake
revalidation requires the ten main/SI attachments listed in the inventory.
No paper PDF or original publisher raster is proposed for redistribution.

Use the separate digitization environment: recorded Python 3.12.14, pypdf 6.10.0,
pdfplumber 0.11.9, NumPy 2.3.5, Pillow 12.3.0. From the repository root:

```powershell
python -B docs/benchmarks/m5_frozen_pilot_2026-10-23/digitize_stability.py --sources-dir <your-PDF-directory> --output data/processed/m5_digitization_new
```

Output must be new; source hashes are checked before interpretation. Numerical
calibration should match the frozen JSON. Annotation raster hashes can depend
on the available Arial font/rendering environment; do not infer a numeric change
from font-only differences. The preserved historical pending checklist links the canonical
local `digitization_final` archive; use newly regenerated equivalents when
reviewing elsewhere. `prepare_review.py` checks that canonical archive and
original source paths from the historical calibration, so it is a local curation
check, not a portable first-time reconstruction command. It never approves a
human review. Current sign-off comes solely from Yiwei Chen's dated feedback,
not from this script or an inferred independent reader.

## Public structure sources and new scan records

1L63 is available from the [public RCSB PDB file](https://files.rcsb.org/download/1L63.pdb);
follow [existing example commands](../../examples.md), compare the recorded input
digest, and use a fresh output path. Source revisions may change hashes. It is
a reference (SEQADV C54T/C97A), not a confirmed complete experimental construct.

For 2FG8, the original case record lists public URLs and hashes for the
[asymmetric-unit mmCIF](https://files.rcsb.org/download/2FG8.cif),
[expanded biological assembly 1](https://files.rcsb.org/download/2FG8-assembly1.cif.gz),
[entry metadata](https://data.rcsb.org/rest/v1/core/entry/2FG8),
[assembly metadata](https://data.rcsb.org/rest/v1/core/assembly/2FG8/1), and
[UniProt P02792 FASTA](https://rest.uniprot.org/uniprotkb/P02792.fasta).
These structures are publicly reconstructable without the supplied paper PDFs.
The approved reference identity remains uncertain as the authors' actual input.

The preserved `khoshnejad2018_hftl_prepare.py` documents the actual 24-chain
preparation: official expanded coordinates, protein chains A–X, target A,
monomer sensitivity, no relaxation or missing-atom reconstruction. Its current
entry point uses fixed archival paths and requires additional saved paper/web
source files. **Do not rerun it in place over the existing record.** A clean-room
portable structure-preparation wrapper is deferred to M6;
the original is retained as execution evidence, not advertised as a one-command
fresh-clone pipeline. The curated-table analysis above is portable now.

Any future rescan must use a fresh case/run directory and the frozen v0.1
configuration: pAzF, seed 42, 12 library rotamers, low-clash score <=10.0 Å²,
favorable fraction 0.5, no functional annotations. Record structure, software,
configuration and script hashes plus actual commit and worktree state at execution.
Do not replace the old T4L scan's missing local execution commit/environment with
the matching reference-run provenance. This round ran no new frozen scans.

## M5 completion boundary and deferred gaps

The [M5 closeout](../m5_closeout_2026-10-24.md) separates completion blockers from
documented limitations and the [M6 plan](../m6_plan.md). M5 requires the current
human-review status, usable curated tables/scripts, a curated-table replay check,
and accurate final conclusions/limitations. These are delivered here; no unresolved
technical blocker remains at that stated level. Nothing has been committed or
published, and final maintainer acceptance/publication authorization is separate.

Insertion-code repair/regressions, multi-structure sensitivity, continued ferritin
environment assessment, a BglB pAzF computational case with functional annotations,
and further structure-preparation/scan portability are M6 work, not prerequisites
for M5 curated-table analysis closeout. No such implementation starts this round.

Full construct/tag/junction equivalence, exact experimental N, reused SD/SEM
definitions, ferritin author-used PDB/fusion and undefined TLC errors remain
scientific limitations. Exact N stays unreported (N >= 3 for T4L). These are
not invented or made mandatory M6 wet-lab deliverables. Stronger prediction or
generalization claims would require additional independent endpoint-specific
evidence and an appropriate future evaluation design.

The current reproducibility level is curated tables to exploratory analysis in
the recorded environment. It is not a completed portable end-to-end
structure/PDF/scan pipeline. Repository README validation claims were not expanded.
