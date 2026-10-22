"""Controlled replay safety checks, never official conformance evidence."""
import json
import pytest
from retained_run import validate_and_copy, hashes

@pytest.fixture
def retained(tmp_path):
    source = tmp_path/'original'
    source.mkdir()
    module = {'module_name':'test-a','test_name':'test-a','test_id':'retained-id','status':'REVIEW'}
    run = {'summary':{'plan_id':'retained-plan','is_gated_pass':False},
           'results':{'test-a':'REVIEW'},'modules':[module]}
    report = {'schema_version':2,'run_id':'retained-run','runs':{'certify':run},
              'consolidated':{'gate_met':False,'timestamp':'2026-01-01T00:00:00Z'}}
    (source/'conformance-summary.json').write_text(json.dumps(report))
    class ReadOnlyClient:
        def get_test_plan(self, _): return {'modules':[{'testModule':'test-a'}]}
        def get_test_status(self, _): return {'status':'FINISHED','result':'REVIEW'}
    return source,tmp_path/'derived',ReadOnlyClient(),report

def test_retained_replay_preserves_results_timestamp_and_original(retained):
    source,destination,client,_ = retained
    before = hashes(source)
    result = validate_and_copy(source,destination,['certify'],'retained-run',client)
    assert result['consolidated']['gate_met'] is False
    assert hashes(source) == before
    assert (source/'conformance-summary.json').read_bytes() == (destination/'original-conformance-summary.json').read_bytes()
    assert result['runs']['certify']['summary']['gate_met'] is False
    assert result['consolidated']['timestamp'] == '2026-01-01T00:00:00Z'

@pytest.mark.parametrize('defect',['identity','live_status','mapping','gate','output'])
def test_retained_replay_rejects_invalid_provenance(retained,defect):
    source,destination,client,report = retained
    identity = 'retained-run'
    if defect == 'identity': identity = 'wrong-run'
    if defect == 'live_status': client.get_test_status = lambda _: {'status':'RUNNING','result':'PASSED'}
    if defect == 'mapping': report['runs']['certify']['results']['test-a'] = 'PASSED'
    if defect == 'gate': report['runs']['certify']['summary']['is_gated_pass'] = True
    if defect == 'output': destination = source
    (source/'conformance-summary.json').write_text(json.dumps(report))
    before = hashes(source)
    with pytest.raises(ValueError): validate_and_copy(source,destination,['certify'],identity,client)
    assert hashes(source) == before


def test_component_projection_keeps_original_failed_combined_gate(retained):
    source,destination,client,report=retained
    report['runs']['certify']['modules'][0]['status']='PASSED'
    report['runs']['certify']['results']['test-a']='PASSED'
    report['runs']['certify']['summary'].update(is_gated_pass=True,passed=1,total=1)
    report['runs']['verify']={'summary':{'is_gated_pass':False},'results':{'v':'REVIEW'}}
    (source/'conformance-summary.json').write_text(json.dumps(report))
    client.get_test_status=lambda _: {'status':'FINISHED','result':'PASSED'}
    before=hashes(source)
    result=validate_and_copy(source,destination,['certify'],'retained-run',client)
    assert result['consolidated']['gate_met'] is True
    assert result['retained_source']['combined_gate_met'] is False
    assert set(result['runs'])=={'certify'}
    assert json.loads((destination/'original-conformance-summary.json').read_text())['consolidated']['gate_met'] is False
    assert hashes(source)==before
    badge=(destination/'combined-conformance-badge.svg').read_text()
    assert 'certify retained validation' in badge and 'PASSED' in badge


def test_retained_diff_preserves_review_and_source_hashes(retained,tmp_path):
    source,destination,client,report=retained
    report['consolidated']['results']={'certify::test-a':'REVIEW'}
    (source/'conformance-summary.json').write_text(json.dumps(report))
    baseline=tmp_path/'previous.json'
    baseline.write_text(json.dumps({'run_id':'previous','consolidated':{'results':{'certify::test-a':'PASSED'}}}))
    before=hashes(source)
    result=validate_and_copy(source,destination,['certify'],'retained-run',client,baseline)
    diff=json.loads((destination/'conformance-diff.json').read_text())
    assert diff['has_regressions'] is True
    assert result['runs']['certify']['results']['test-a']=='REVIEW'
    assert result['consolidated']['gate_met'] is False
    assert hashes(source)==before


def test_invalid_retained_diff_cannot_leave_a_passing_output(retained,tmp_path):
    source,destination,client,_=retained
    baseline=tmp_path/'baseline.json'
    baseline.write_text(json.dumps({'consolidated':{'results':{'verify::unrelated':'PASSED'}}}))
    with pytest.raises(ValueError,match='Baseline'):
        validate_and_copy(source,destination,['certify'],'retained-run',client,baseline)
    assert not destination.exists()
