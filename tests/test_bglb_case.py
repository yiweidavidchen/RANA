"""Targeted checks for the BglB case wrapper; no real scan or download."""
import importlib.util
import json
import subprocess
import sys
import shutil
from pathlib import Path

import pandas as pd
import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "docs/computational_cases/bglb"


@pytest.fixture
def case():
    spec = importlib.util.spec_from_file_location("bglb_case", SCRIPTS / "run_case.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def simulated_output(case, tmp_path):
    cfg = {"ncaa":"pazf", "seed":42, "low_clash_threshold":10.0, "favorable_fraction":.5, "functional_residues":None}
    rows = []
    for n in [4,5]:
        rows.append({**{field:1.0 for field in case.FIELDS}, "chain":"A", "residue_number":n, "insertion_code":"",
                     "residue_name":"ALA", "status":"scored", "reason":"", "candidate_tier":"geometry_favorable",
                     "n_rotamers":12, "rotamer_scores":json.dumps(list(range(1,13))), "low_clash_fraction":10/12,
                     "mean_steric_score":6.5,"median_steric_score":6.5,
                     "special_residue_flag":"", "ranking_reason":"unchanged"})
    path=tmp_path/"ranked.csv"
    def save(frame):
        frame.to_csv(path,index=False)
        metadata={"output":{"csv_sha256":case.sha(path)},"input":{"pdb_sha256":"prepared","chain":"A"},
                  "configuration":cfg,"software":{"git_commit":"code"},
                  "results":{"n_residues":len(frame),"status_counts":frame.status.value_counts().to_dict(),
                             "tier_counts":frame.candidate_tier.value_counts().to_dict()}}
        path.with_suffix('.metadata.json').write_text(json.dumps(metadata), encoding="utf-8")
    frame=pd.DataFrame(rows);save(frame)
    return path, frame, save, cfg, {("A",4,""):"ALA",("A",5,""):"ALA"}


@pytest.mark.parametrize('status',['failed','skipped'])
def test_valid_output_and_diagnosed_failure_preserved(case, simulated_output,status):
    path,frame,save,cfg,expected=simulated_output
    assert case.validate_output(path,expected,cfg,"prepared","code")["status_counts"]=={"scored":2}
    frame.loc[0,["status","reason","candidate_tier"]]=[status,"missing_backbone","not_evaluated"]
    save(frame)
    result=case.validate_output(path,expected,cfg,"prepared","code")
    assert result["rows"]==2 and result["status_counts"]=={status:1,"scored":1}


@pytest.mark.parametrize("damage",["missing","duplicate","parent","chain","rotamer_count","rotamer_length","nan","inf","metric","fraction","minimum","mean","median","tier","diagnostic","sidecar"])
def test_bad_output_rejected_even_after_zero_exit(case,simulated_output,damage):
    path,frame,save,cfg,expected=simulated_output
    if damage=="missing":frame=frame.iloc[:1]
    elif damage=="duplicate":frame=pd.concat([frame,frame.iloc[:1]])
    elif damage=="parent":frame.loc[0,"residue_name"]="GLY"
    elif damage=="chain":frame.loc[0,"chain"]="B"
    elif damage=="rotamer_count":frame.loc[0,"n_rotamers"]=11
    elif damage=="rotamer_length":frame.loc[0,"rotamer_scores"]=json.dumps([1.0]*11)
    elif damage in ["nan","inf"]:frame.loc[0,"rotamer_scores"]=json.dumps([float(damage)]+[1.0]*11)
    elif damage=="metric":frame.loc[0,"rsa"]=float("nan")
    elif damage=="fraction":frame.loc[0,"low_clash_fraction"]=1.0
    elif damage=="minimum":frame.loc[0,"min_steric_score"]=2.0
    elif damage=="mean":frame.loc[0,"mean_steric_score"]=2.0
    elif damage=="median":frame.loc[0,"median_steric_score"]=2.0
    elif damage=="tier":frame.loc[0,"candidate_tier"]="invented"
    elif damage=="diagnostic":frame.loc[0,"reason"]="unexpected"
    save(frame)
    if damage=="sidecar":
        meta=json.loads(path.with_suffix('.metadata.json').read_text(encoding="utf-8"));meta['output']['csv_sha256']='wrong'
        path.with_suffix('.metadata.json').write_text(json.dumps(meta), encoding="utf-8")
    with pytest.raises((ValueError,TypeError)):
        case.validate_output(path,expected,cfg,"prepared","code")


def test_preparation_retains_atom_identity_and_author_number(case,tmp_path):
    source=tmp_path/'source.pdb';output=tmp_path/'prepared.pdb'
    heavy="ATOM      1  CA  ALA A   4       1.000   2.000   3.000  1.00 10.00           C  "
    source.write_text(heavy+'\n'+
                     "ATOM      2  H   ALA A   4       0.000   2.000   3.000  1.00 10.00           H  \n"+
                     "HETATM    3  O   HOH A 500       4.000   2.000   3.000  1.00 10.00           O  \nEND\n")
    record,expected=case.prepare(source,output)
    assert case.protein_lines(output)==[heavy] and expected=={('A',4,''):'ALA'}
    assert record['coordinate_change_A']==0 and record['protein_heavy_atoms']==1
    before=output.read_bytes()
    with pytest.raises(FileExistsError):case.prepare(source,output)
    assert output.read_bytes()==before


@pytest.mark.parametrize('optimize',[False,True])
def test_runtime_checks_and_overwrite_refusal_survive_optimization(tmp_path,optimize):
    target=tmp_path/'existing';target.mkdir()
    prefix=f"import sys;from pathlib import Path;sys.path.insert(0,{str(SCRIPTS)!r});import run_case;"
    for operation,message in [(f"run_case.run(Path('missing'),Path({str(target)!r}))",'FileExistsError'),
                              ("run_case.require(False,'explicit integrity failure')",'explicit integrity failure')]:
        result=subprocess.run([sys.executable,*(['-O'] if optimize else []),'-B','-c',prefix+operation],capture_output=True,text=True)
        assert result.returncode!=0 and message in result.stderr


@pytest.fixture
def curator(monkeypatch):
    monkeypatch.syspath_prepend(str(SCRIPTS))
    spec=importlib.util.spec_from_file_location('bglb_curator',SCRIPTS/'curate_case.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('ascending',[True,False])
def test_inclusive_display_retains_boundary_ties(curator,ascending):
    values=pd.Series([*range(1,10),10,10,10,11])
    if not ascending:values=-values
    members,boundary=curator.inclusive_members(values,ascending)
    assert members==list(range(12)) and boundary==(10 if ascending else -10)
    with pytest.raises(ValueError):curator.inclusive_members(pd.Series([float('nan')]),ascending)


def test_curator_rejects_hash_mismatch_before_parsing(curator,provenance_run,monkeypatch):
    run_dir,record,_,_=provenance_run
    (run_dir/'ranked.csv').write_text('untrusted content\n', encoding="utf-8")
    monkeypatch.setattr(curator.pd,'read_csv',lambda *a,**k:pytest.fail('CSV parsed before hash check'))
    with pytest.raises(ValueError,match='SHA-256 mismatch'):curator.verified_inputs(run_dir)
    with pytest.raises(FileExistsError):curator.curate(run_dir,run_dir)


def test_annotation_join_preserves_science_and_all_flagged_sites(curator):
    original_plan=json.loads((SCRIPTS/'case_plan.json').read_text(encoding="utf-8"))
    audit=json.loads((SCRIPTS/'candidate_audit.json').read_text(encoding="utf-8"))
    annotations=original_plan['functional_annotations']
    identities=annotations+[dict(chain='A',residue_number=376,insertion_code='',residue_name='GLN'),
                            dict(chain='A',residue_number=377,insertion_code='',residue_name='ARG')]
    rows=[]
    for item in identities:
        rows.append({**{k:item[k] for k in ['chain','residue_number','insertion_code','residue_name']},
            'status':'scored','reason':'','sasa_abs':1.0,'rsa':.5,'ca_neighbors_8a':4,'n_rotamers':12,
            'min_steric_score':1.0,'mean_steric_score':6.5,'median_steric_score':6.5,'low_clash_fraction':10/12,
            'best_chi1':-60.,'best_chi2':0.,'candidate_tier':'geometry_favorable','steric_rank':1.,'rsa_rank':1.,
            'rotamer_robustness_rank':1.,'special_residue_flag':'','ranking_reason':'unchanged',
            'rotamer_scores':json.dumps(list(range(1,13)))})
    raw=pd.DataFrame(rows)
    plan={'functional_annotations':annotations,'cli_configuration':{'low_clash_threshold':10.0}}
    full,overview,functional,background,memberships,missing,lists=curator.build_tables(raw,plan,audit,'scan','prepared')
    for column in raw.columns:
        if column in full:pd.testing.assert_series_equal(full[column],raw[column])
    assert len(full)==len(overview)==13 and len(functional)==11 and len(background)==2
    assert len(memberships)==39 and all(item['actual_size']==13 for item in lists.values())
    assert len(missing)==9 and full.low_clash_rotamer_count.eq(10).all()
    bad=raw.copy();bad.loc[0,'residue_name']='ALA'
    with pytest.raises(ValueError,match='annotation missing/parent mismatch'):
        curator.build_tables(bad,plan,audit,'scan','prepared')
    bad=raw.copy();bad.loc[0,'steric_rank']=2.
    with pytest.raises(ValueError,match='Original rank inconsistent'):
        curator.build_tables(bad,plan,audit,'scan','prepared')


@pytest.mark.parametrize('field', ['best_chi1', 'best_chi2'])
@pytest.mark.parametrize('value', ['nan', 'inf', '-inf', '', 'not_numeric', 'missing', 'True'])
def test_invalid_angles_rejected(case, simulated_output, field, value):
    path, frame, save, cfg, expected = simulated_output
    if value == 'missing':
        frame = frame.drop(columns=[field])
    else:
        frame[field] = frame[field].astype(object)
        frame.loc[0, field] = value
    save(frame)
    with pytest.raises(ValueError):
        case.validate_output(path, expected, cfg, 'prepared', 'code')


@pytest.fixture
def provenance_run(curator, simulated_output, tmp_path, monkeypatch):
    """Self-contained simulated run, anchored to the real approved Git source."""
    path, frame, save, cfg, expected = simulated_output
    runner = sys.modules['run_case']
    plan, approval = runner.approved_plan()
    plan = json.loads(json.dumps(plan))
    profile = tmp_path/'profile'
    profile.mkdir()
    original = b'# simulated original approved runner\n'
    archived = tmp_path/'executed_sources'
    archived.mkdir()
    (archived/'run_case.py').write_bytes(original)
    plan['dependencies_sha256']['run_case.py'] = runner.sha(archived/'run_case.py')
    pdb = ''.join(f'ATOM  {n:5d}  CA  ALA A{n:4d}       1.000   2.000   3.000  1.00 10.00           C  \n' for n in [4,5])
    (tmp_path/'2O9P_original.pdb').write_text(pdb, encoding='ascii')
    (tmp_path/'protein_A.pdb').write_text(pdb, encoding='ascii')
    plan['source_sha256'] = runner.sha(tmp_path/'2O9P_original.pdb')
    frozen = archived/'execution_plan_2026-10-25.json'
    frozen.write_text(json.dumps(plan), encoding='utf-8', newline='\n')
    approval = dict(approval, historical_plan_lf_sha256=runner.text_sha(frozen))
    audit = {'structures': {'2O9P': {'observed_residue_identities': [dict(chain=k[0], residue_number=k[1], insertion_code=k[2], residue_name=v) for k,v in expected.items()]}}}
    (profile/'candidate_audit.json').write_text(json.dumps(audit), encoding='utf-8')
    prepared = runner.sha(tmp_path/'protein_A.pdb')
    commit = plan['scientific_base_commit']
    meta = runner.read_json(path.with_suffix('.metadata.json'))
    meta['input']['pdb_sha256'] = prepared
    meta['software']['git_commit'] = commit
    path.with_suffix('.metadata.json').write_text(json.dumps(meta), encoding='utf-8')
    record = {'status':'scan_completed', 'git_commit':commit,
              'scientific_package_sha256':dict(approval['scientific_source_lf_sha256']),
              'source_sha256':plan['source_sha256'], 'configuration':cfg,
              'source_provenance':plan['source_provenance'],
              'wrapper_sha256':runner.sha(archived/'run_case.py'),
              'execution_plan_sha256':runner.sha(frozen), 'preparation':{'prepared_sha256':prepared},
              'output_validation':runner.validate_output(path,expected,cfg,prepared,commit)}
    (tmp_path/'run.json').write_text(json.dumps(record), encoding='utf-8')
    monkeypatch.setattr(curator, 'HERE', profile)
    monkeypatch.setattr(curator, 'approved_plan', lambda: (plan, approval))
    return tmp_path, record, plan, approval


def test_complete_historical_provenance_passes(curator, provenance_run):
    run_dir, record, _, _ = provenance_run
    actual, _, _ = curator.verified_inputs(run_dir)
    assert actual == record


@pytest.mark.parametrize('damage', ['missing_sources', 'incomplete_sources', 'missing_wrapper', 'wrong_source',
                                  'replaced_wrapper', 'replaced_plan', 'wrong_commit', 'wrong_configuration'])
def test_provenance_not_repaired_by_self_reported_hash(curator, provenance_run, damage):
    run_dir, record, plan, _ = provenance_run
    if damage == 'missing_sources': record.pop('scientific_package_sha256')
    elif damage == 'incomplete_sources': record['scientific_package_sha256'].pop(next(iter(record['scientific_package_sha256'])))
    elif damage == 'missing_wrapper': record.pop('wrapper_sha256')
    elif damage == 'wrong_source': record['scientific_package_sha256'][next(iter(record['scientific_package_sha256']))] = '0'*64
    elif damage == 'replaced_wrapper':
        p = run_dir/'executed_sources/run_case.py'
        p.write_text('# replacement\n', encoding='utf-8')
        record['wrapper_sha256'] = curator.sha(p)
    elif damage == 'replaced_plan':
        p = run_dir/'executed_sources/execution_plan_2026-10-25.json'
        p.write_text('{}\n', encoding='utf-8')
        record['execution_plan_sha256'] = curator.sha(p)
    elif damage == 'wrong_commit': record['git_commit'] = 'not-a-commit'
    elif damage == 'wrong_configuration': record['configuration'] = {}
    (run_dir/'run.json').write_text(json.dumps(record), encoding='utf-8')
    with pytest.raises((ValueError, subprocess.CalledProcessError)):
        curator.verified_inputs(run_dir)


@pytest.mark.parametrize('newline', ['\n', '\r\n'])
@pytest.mark.parametrize('optimize', [False, True])
def test_checkout_line_endings_and_utf8(case, tmp_path, newline, optimize):
    """Export a checkout-equivalent public profile; no raw records are converted."""
    profile = tmp_path/'profile'
    shutil.copytree(SCRIPTS, profile, ignore=shutil.ignore_patterns('__pycache__'))
    for p in profile.iterdir():
        if p.suffix in {'.py', '.json', '.md', '.txt'}:
            p.write_bytes(p.read_bytes().replace(b'\r\n', b'\n').replace(b'\n', newline.encode()))
    code = (f'import sys;sys.path.insert(0,{str(profile)!r});import run_case,curate_case;'
            'p,a=run_case.approved_plan();assert p["protein"].startswith(chr(946));'
            'run_case.require(p["protein"].startswith(chr(946)),"lost beta");'
            'print(run_case.text_sha(run_case.HERE/"run_case.py"))')
    result = subprocess.run([sys.executable, *(['-O'] if optimize else []), '-X', 'utf8=0', '-B', '-c', code], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == case.text_sha(SCRIPTS/'run_case.py')
    # Preserve LF/CRLF equivalence only; a real byte change must still fail.
    p = profile/'run_case.py'
    p.write_bytes(p.read_bytes()+b'\n# actual content edit\n')
    result = subprocess.run([sys.executable, '-B', '-c', code], capture_output=True, text=True)
    assert result.returncode != 0 and 'SHA-256 mismatch' in result.stderr


def test_json_io_declares_utf8(case, tmp_path, monkeypatch):
    import io
    original = io.open
    def checked(file, mode='r', *args, **kwargs):
        if 'b' not in mode:
            encoding = kwargs.get('encoding', args[1] if len(args)>1 else None)
            assert encoding == 'utf-8'
        return original(file, mode, *args, **kwargs)
    path = tmp_path/'non_ascii.json'
    path.write_text(json.dumps({'protein':'β-glucosidase'}, ensure_ascii=False), encoding='utf-8')
    monkeypatch.setattr(io, 'open', checked)
    assert case.read_json(path)['protein'] == 'β-glucosidase'


@pytest.mark.parametrize('damage', ['valid_lf', 'valid_crlf', 'edited_archive', 'missing_lf_record', 'wrong_science_lf'])
def test_revised_execution_keeps_distinct_approval(curator, provenance_run, damage):
    run_dir, record, _, approval = provenance_run
    runner = sys.modules['run_case']
    archive = run_dir/'executed_sources/run_case.py'
    data = (SCRIPTS/'run_case.py').read_bytes().replace(b'\r\n', b'\n')
    if damage == 'valid_crlf': data = data.replace(b'\n', b'\r\n')
    if damage == 'edited_archive': data += b'\n# unapproved actual edit\n'
    archive.write_bytes(data)
    record.update(tool_revision=runner.REVISION, text_hash_algorithm=runner.TEXT_HASH_ALGORITHM,
                  wrapper_sha256=runner.sha(archive), wrapper_lf_sha256=approval['current_tools_lf_sha256']['run_case.py'],
                  scientific_package_lf_sha256=approval['scientific_source_lf_sha256'])
    if damage == 'missing_lf_record': record.pop('wrapper_lf_sha256')
    if damage == 'wrong_science_lf': record['scientific_package_lf_sha256'] = {}
    (run_dir/'run.json').write_text(json.dumps(record), encoding='utf-8')
    if damage.startswith('valid'):
        actual, _, _ = curator.verified_inputs(run_dir)
        assert actual['tool_revision'] == runner.REVISION
    else:
        with pytest.raises(ValueError): curator.verified_inputs(run_dir)
