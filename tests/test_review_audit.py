"""Controlled unit fixtures only; these are not official conformance evidence."""
import base64
import hashlib
import json
import pytest
from audit_verifier_review import audit, ERRORS, inspect_status_reference, inspect_post_coverage

@pytest.fixture
def fixture(tmp_path):
    reports = tmp_path / 'original'
    reports.mkdir()
    modules = []
    images = {}
    names = ['oid4vp-1final-verifier-happy-flow', 'oid4vp-1final-verifier-minimal-cnf-jwk',
             'oid4vp-1final-verifier-request-uri-method-post', *ERRORS]
    for i, name in enumerate(names):
        test = 'unit-' + str(i)
        folder = reports / test
        folder.mkdir()
        data = b'controlled unit fixture bytes'
        (folder / 'verifier-browser.jpg').write_bytes(data)
        (folder / 'verifier-qr.png').write_bytes(data)
        (reports / (test + '-log.json')).write_text('[]')
        negative = name in ERRORS
        checks = {'schemaAndSignatureCheck': {'valid': not negative, 'error':
                  {'errorCode': ERRORS[name]} if negative else None},
                  'holderProofCheck': {'valid': not negative}, 'statusCheck': []}
        (folder / 'verifier-session-results.json').write_text(json.dumps([{
            'http_status': 200, 'request': {'skipStatusChecks': False},
            'response': {'transactionId': test, 'allChecksSuccessful': not negative,
                         'credentialResults': [checks]}}]))
        modules.append({'test_id': test, 'module_name': name, 'status': 'REVIEW', 'handoff': {
            'log_entry_id': test, 'screenshot_sha256': hashlib.sha256(data).hexdigest(),
            'transaction_id': test, 'request_id': test, 'placeholder': test,
            'ui_result_text': 'credential is invalid' if negative else 'credential is valid'}})
        images[test] = [{'_id': test, 'img': 'data:image/jpeg;base64,' + base64.b64encode(data).decode()}]
    (reports / 'conformance-summary.json').write_text(json.dumps({'run_id': 'unit-fixture',
        'consolidated': {'gate_met': False}, 'runs': {'verify': {'summary': {
            'plan_name': 'oid4vp-1final-verifier-test-plan', 'plan_id': 'unit-plan',
            'is_gated_pass': False}, 'modules': modules}}}))
    (reports / 'plan-unit-plan-export.zip').write_bytes(b'unit export fixture')
    class ReadOnlyFixtureClient:
        base_url = 'https://unit.invalid'
        def get_test_status(self, test):
            return {'status': 'FINISHED', 'result': 'REVIEW'}
        def get_test_images(self, test):
            return images[test]
    return reports, tmp_path / 'audit', ReadOnlyFixtureClient(), images

def test_audit_preserves_results_and_original_bytes(fixture):
    reports, output, client, _ = fixture
    before = {p.name: p.read_bytes() for p in reports.iterdir() if p.is_file()}
    result = audit(reports, output, client)
    assert result['official_conformance_result'] is False
    assert result['original_files_unchanged'] is True
    assert result['original_combined_gate'] is False
    assert all(r['observed_official_result'] == 'REVIEW' for r in result['reviews'])
    assert before == {p.name: p.read_bytes() for p in reports.iterdir() if p.is_file()}

@pytest.mark.parametrize('defect', ['image_bytes', 'transaction', 'pending'])
def test_audit_rejects_mismatched_or_incomplete_evidence(fixture, defect):
    reports, output, client, images = fixture
    if defect == 'image_bytes':
        images['unit-0'][0]['img'] = 'data:image/jpeg;base64,' + base64.b64encode(b'changed').decode()
    elif defect == 'pending':
        images['unit-0'].append({'_id': 'unfilled', 'upload': 'placeholder'})
    else:
        path = reports / 'unit-0/verifier-session-results.json'
        data = json.loads(path.read_text())
        data[0]['response']['transactionId'] = 'different'
        path.write_text(json.dumps(data))
    with pytest.raises(AssertionError):
        audit(reports, output, client)

def test_audit_requires_the_specific_native_rejection(fixture):
    reports, output, client, _ = fixture
    path = reports / 'unit-3/verifier-session-results.json'
    data = json.loads(path.read_text())
    data[0]['response']['credentialResults'][0]['schemaAndSignatureCheck']['error']['errorCode'] = 'UNRELATED'
    path.write_text(json.dumps(data))
    with pytest.raises(AssertionError):
        audit(reports, output, client)


@pytest.mark.parametrize('state,result', [('RUNNING','REVIEW'),('FINISHED','FAILED'),('FINISHED','PASSED')])
def test_audit_rejects_nonfinal_or_changed_official_outcome(fixture,state,result):
    reports,output,client,_=fixture
    client.get_test_status=lambda test:{'status':state,'result':result}
    with pytest.raises(AssertionError,match='not final'):
        audit(reports,output,client)


def test_audit_rejects_contradictory_native_verification(fixture):
    reports,output,client,_=fixture
    path=reports/'unit-3/verifier-session-results.json'
    data=json.loads(path.read_text())
    data[0]['response']['credentialResults'][0]['schemaAndSignatureCheck']['valid']=True
    path.write_text(json.dumps(data))
    with pytest.raises(AssertionError,match='contradict'):
        audit(reports,output,client)


@pytest.mark.parametrize('present,disclosed',[(False,False),(True,False),(True,True)])
def test_status_reference_inspection_is_not_signature_validation(present,disclosed):
    encode=lambda obj:base64.urlsafe_b64encode(json.dumps(obj).encode()).decode().rstrip('=')
    # Deliberately unsigned controlled structure, never conformance evidence.
    payload={'vct':'fixture'}
    if present and not disclosed:payload['status']={'status_list':{'uri':'https://fixture.invalid','idx':0}}
    credential=encode({'alg':'none'})+'.'+encode(payload)+'.fixture~'
    if disclosed:credential+=encode(['fixture-salt','status',{}])+'~'
    value=inspect_status_reference(credential)
    assert value['decoded'] and value['status_reference_present'] is present
    assert value['signature_validation_performed_by_this_inspection'] is False


@pytest.mark.parametrize('credential',[None,'not-a-jwt','a.W10.x~','a.%%%.x~'])
def test_unreadable_status_evidence_is_not_treated_as_absent(credential):
    value=inspect_status_reference(credential)
    assert value['decoded'] is False and value['status_reference_present'] is None


@pytest.mark.parametrize('missing,failed', [(True,False),(False,True),(False,False)])
def test_post_coverage_requires_actual_successful_conditions(missing,failed):
    names=['CreateWalletNonce','PostToRequestUriAndExtractRequestObject','EnsureWalletNonceClaimMatchesPostedValue']
    logs=[{'src':n,'result':'SUCCESS'} for n in names]
    if missing:logs.pop()
    if failed:logs[1]['result']='FAILURE'
    assert inspect_post_coverage(logs)['exercised'] is (not missing and not failed)
