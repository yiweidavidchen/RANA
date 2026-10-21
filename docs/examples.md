# Reproducible public pAzF examples

These examples exercise software execution and fixed-structure geometry only.
They do not benchmark experimental incorporation, expression, function, or
labeling. Use the repository root as the working directory throughout.

## Environment

Python >=3.10 is required. Create and activate an isolated environment:

```bash
python -m venv .venv
# POSIX shells:
source .venv/bin/activate
# Windows PowerShell alternative:
# .\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

RDKit is already a declared dependency. No extra scientific dependency is
needed. `python -m ncaa_site_rec.cli` and the installed `rana` entry point
call the same CLI. Single-line commands below work in Bash and PowerShell
after environment activation. If PowerShell activation is unavailable, invoke
`.\.venv\Scripts\python.exe` in place of `python`.

## Public inputs

Download the unmodified RCSB PDB files. These download commands were executed
with Windows `curl.exe`, avoiding PowerShell's possible `curl` alias. In a
POSIX shell use `curl` in place of `curl.exe`:

```bash
python -c "from pathlib import Path; Path('data/raw').mkdir(parents=True, exist_ok=True)"
curl.exe -fL https://files.rcsb.org/download/1L63.pdb -o data/raw/1L63.pdb
curl.exe -fL https://files.rcsb.org/download/7RSA.pdb -o data/raw/7RSA.pdb
```

Sources: [1L63 PDB file](https://files.rcsb.org/download/1L63.pdb) and
[7RSA PDB file](https://files.rcsb.org/download/7RSA.pdb).
Files were retrieved on 2026-10-20 for the reference runs. Check input hashes
against `examples/reference-results.json`; a later RCSB revision may differ.
No PDB file or full generated CSV is included in Git. The existing ignore rules
for `data/raw/` and `data/processed/` remain unchanged.

The examples select chain A from the first model and retain standard
amino-acid residues only. Waters/ligands are omitted by the implementation;
the supplied structure is not relaxed and biological assemblies are not built.
No functional annotations or exclusion rules are applied.

## Run both screens

```bash
python -m ncaa_site_rec.cli rank --pdb data/raw/1L63.pdb --chain A --ncaa pazf --seed 42 --low-clash-threshold 10.0 --favorable-fraction 0.5 --output data/processed/t4l_pazf_ranked.csv
python -m ncaa_site_rec.cli rank --pdb data/raw/7RSA.pdb --chain A --ncaa pazf --seed 42 --low-clash-threshold 10.0 --favorable-fraction 0.5 --output data/processed/rnase_a_pazf_ranked.csv
```

Each produces the CSV named above and a same-stem `.metadata.json` sidecar.
The complete CSV stays in residue order and contains three independent ranks;
there is no combined score. Inspect `status`, `reason`, `n_rotamers`,
`candidate_tier`, and `ranking_reason` before interpreting any ranks.

Summarize the actual sidecars:

```bash
python -c "import json; from pathlib import Path; names = ['t4l_pazf_ranked', 'rnase_a_pazf_ranked']; print(json.dumps({name: json.loads((Path('data/processed') / (name + '.metadata.json')).read_text())['results'] for name in names}, indent=2))"
```

Exit 0 alone is insufficient: a partially failed scan also exits 0 with a
warning. After artifacts are written, zero scored sites gives exit 1.

## Verify provenance and retain the environment

```bash
python -c "import json; from pathlib import Path; from ncaa_site_rec.io.run_metadata import sha256_file; names = ['t4l_pazf_ranked', 'rnase_a_pazf_ranked']; records = [json.loads((Path('data/processed') / (name + '.metadata.json')).read_text()) for name in names]; assert all(sha256_file(m['input']['pdb_path']) == m['input']['pdb_sha256'] and sha256_file(m['output']['csv_path']) == m['output']['csv_sha256'] for m in records); print('Input and output hashes verified')"
python -m pip freeze --exclude-editable > data/processed/environment.txt
python --version
git rev-parse HEAD
git diff
```

The small `examples/reference-results.json` stores observed summaries and
hashes, and `examples/requirements-m46.txt` records the reference environment's
installed distributions (excluding editable RANA). These are a run snapshot,
not new package requirements or a universal cross-platform lockfile. To compare
with the reference on a compatible Python/platform, install the snapshot first
with `python -m pip install -r docs/examples/requirements-m46.txt`, then install
RANA with `python -m pip install -e ".[dev]"`.

The CLI metadata omits dependency versions and its Git dirty flag covers tracked
changes only. Keep the environment record and diff with your run. Byte-for-byte
CSV identity can depend on versions and line endings; metadata paths and Git
state can differ. Compare numeric values with an explicit tolerance where
appropriate. Investigate changed inputs/versions before interpreting changed
tiers. Seeds alone do not guarantee identical results across RDKit versions.

## Existing automated tests

The full suite requires `data/raw/1L63.pdb`, including its numeric regression
checks; a fresh clone without the public input is insufficient. After downloading:

```bash
python -m pytest tests/ -q
```

See the reference run record below for the independently observed result.

## M4.6 reference run

Run on 2026-10-20 from implementation commit
`0f938eca19a8f5dd0eed06986b2d7cda29d1f78f` with documentation edits in the
working tree and no code, test, dependency-declaration, or ignore-rule changes.
Environment: Windows AMD64, Python 3.12.14, NumPy 2.5.4, pandas 3.0.6,
Biopython 1.88, RDKit 2026.9.1, pytest 9.1.1.

On this workstation, pip 25.0.1's Windows certificate backend failed during
the initial install. Installation succeeded with the same command plus
`--use-deprecated=legacy-certs`; this is a local environment workaround,
not a change to RANA's dependency declarations.

Observed results from the two commands above (both exit 0):

```text
1L63 / chain A: 162 scored, 0 failed, 0 skipped, 12 rotamers per site
  geometry_favorable: 60
  geometry_limited: 63
  geometry_unfavorable: 39

7RSA / chain A: 124 scored, 0 failed, 0 skipped, 12 rotamers per site
  geometry_favorable: 54
  geometry_limited: 40
  geometry_unfavorable: 30
```

These counts reproduce the historical M4.4 smoke summaries. Both input and
output hashes were checked against the generated sidecars. The compact
[reference record](examples/reference-results.json) contains the actual hashes,
configuration, counts, and Git provenance; full CSVs and metadata remain ignored
under `data/processed/`.

The existing suite was independently run using:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ -q --basetemp=data/processed/pytest-m46
```

Result: **85 passed in 185.00 seconds**, exit 0, with no failures or skips.
The `--basetemp` option keeps test temporary files inside this workspace's
ignored output directory; it does not select a subset of tests. Use a dedicated
directory for this option because pytest clears its contents on a subsequent run.
The original source and test files were unchanged.

The CLI help and `inspect` command were also exercised on the committed
`tests/fixtures/mini_protein.pdb` fixture (4 residues, no missing C-alpha or SASA).
These checks and the public screens establish execution only; M5 experimental
benchmarking remains outstanding.
