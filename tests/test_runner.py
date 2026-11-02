"""Harness tests use controlled API responses; these are not conformance results."""
import io
import json
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread, Lock
from urllib.parse import parse_qs, urlsplit
import zipfile

import pytest
from oidf_client import OIDFClient
from runner import ConformanceRunner, classify, main, render_template
from diff_engine import DiffEngine
from oid4vp_handoff import OID4VPHandoffClient, generate_signing_jwk


def test_browser_queue_selects_each_real_unvisited_url():
    from browser_handoff import browser_url, browser_urls
    browser = {'urls': ['https://issuer.example/client1', 'https://issuer.example/client2'], 'visited': []}
    assert browser_urls({'browser': browser}, {}) == browser['urls']
    assert browser_urls({'browser': browser}, {}, {browser['urls'][0]}) == [browser['urls'][1]]
    assert browser_url({'browser': browser}, {}) == browser['urls'][0]
    browser['visited'].append(browser['urls'][0])
    assert browser_url({'browser': browser}, {}) == browser['urls'][1]
    browser['visited'].append(browser['urls'][1])
    assert browser_url({'browser': browser}, {}) is None


def test_terminal_transition_during_runtime_fetch_retains_official_failure(monkeypatch):
    client = OIDFClient()
    statuses = iter([{'status': 'WAITING'}, {'status': 'INTERRUPTED', 'result': 'FAILED'}])
    monkeypatch.setattr(client, 'get_test_status', lambda _: next(statuses))
    monkeypatch.setattr(client, 'get_test_runtime', lambda _: {'browser': {'urls': []}})
    def unexpected_handoff(*_):
        pytest.fail('A completed test must not require a browser URL')
    assert client.poll_test_completion('real-id', on_waiting=unexpected_handoff)['status'] == 'INTERRUPTED'


def test_unavailable_browser_interaction_is_retried_and_times_out(monkeypatch):
    client = OIDFClient()
    monkeypatch.setattr(client, 'get_test_status', lambda _: {'status': 'WAITING', 'result': 'PASSED'})
    monkeypatch.setattr(client, 'get_test_runtime', lambda _: {'browser': {'urls': []}})
    attempts = []
    def not_ready(*_):
        attempts.append(True)
        return False
    result = client.poll_test_completion('real-id', on_waiting=not_ready,
                                         poll_interval_sec=0.001, max_timeout_sec=0.03)
    assert len(attempts) > 1
    assert result['status'] == result['result'] == 'TIMEOUT'


@pytest.fixture
def api():
    creation_lock = Lock()
    test_ids = []
    state = {'calls': [], 'status': 'CONFIGURED', 'result': 'PASSED',
             'export_valid': True, 'modules': [{'testModule': 'test-a', 'variant': {'mode': 'a'}},
                                               {'testModule': 'test-a', 'variant': {'mode': 'b'}}]}
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass
        def do_GET(self):
            self.handle_api()
        def do_POST(self):
            self.handle_api()
        def handle_api(self):
            path = urlsplit(self.path).path
            params = parse_qs(urlsplit(self.path).query)
            body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
            state['calls'].append((self.command, path, params, body))
            code, value = 200, {}
            if path == '/api/runner/available':
                value = [{'testName': 'test-a'}]
            elif path == '/api/plan' and self.command == 'POST':
                code, value = 201, {'id': 'plan-1'}
            elif path == '/api/plan/plan-1':
                value = {'modules': state['modules']}
            elif path == '/api/runner' and self.command == 'POST':
                with creation_lock:
                    test_id = f'test-{len(test_ids) + 1}'
                    test_ids.append(test_id)
                code, value = 201, {'id': test_id}
            elif path.startswith('/api/runner/test-') and self.command == 'POST':
                state['status'] = 'FINISHED'
            elif path.startswith('/api/runner/test-'):
                value = {'status': state['status'], 'exposed': {'authorization_endpoint': state['url'] + '/wallet'}}
            elif path.startswith('/api/info/test-'):
                value = {'status': state['status'], 'result': state['result']}
            elif path == '/api/log/test-1/images/placeholder-1' and self.command == 'POST':
                state['result'] = 'REVIEW'
                value = {'_id': 'test-1-image-1', 'img': body.decode()} if state.get('accept_image', True) else None
            elif path.startswith('/api/log/test-'):
                value = [{'msg': 'actual transport fixture log'}]
            elif path == '/api/plan/export/plan-1':
                if self.headers.get('Accept') != 'application/zip':
                    self.send_response(406)
                    self.end_headers()
                    return
                data = io.BytesIO()
                with zipfile.ZipFile(data, 'w') as z:
                    z.writestr('result.json', '{}')
                value = data.getvalue() if state['export_valid'] else b'not a zip'
            elif path in {'/v1/verify/vp-request', '/v1/verify/v2/vp-request'}:
                code = 201
                value = {'requestId': 'real-request-id', 'transactionId': 'real-transaction-id',
                         'authorizationDetails': {'clientId': 'backend-client', 'nonce': 'backend-nonce',
                          'responseType': 'vp_token', 'responseMode': 'direct_post',
                          'responseUri': state['url'] + '/v1/verify/direct-post',
                          'presentationDefinition': {'id': 'backend-definition'}}}
                value = state.get('verify_response', value)
            elif path == '/wallet':
                state['wallet_params'] = params
                value = ('<form method="post" action="' + state['url'] + '/v1/verify/direct-post">'
                         '<input name="vp_token" value="suite-token"><input name="state" value="real-request-id"></form>').encode()
            elif path == '/v1/verify/direct-post':
                state['submission'] = parse_qs(body.decode())
                code = 400
            elif path.startswith('/v1/verify/vp-result/'):
                value = {'verificationStatus': 'INVALID'}
            else:
                code = 404
            data = value if isinstance(value, bytes) else json.dumps(value).encode()
            self.send_response(code)
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    state['url'] = f'http://127.0.0.1:{server.server_port}'
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield state
    server.shutdown()
    thread.join()
    server.server_close()


def template(tmp_path):
    p = tmp_path / 'plan.json'
    p.write_text(json.dumps({'plan_name': 'test-plan', 'variant': {}, 'configuration': {}}))
    return p


def test_real_transport_create_start_poll_export(api, tmp_path):
    client = OIDFClient(api['url'])
    plan = client.create_test_plan('test-plan', {'alias': 'run'}, {'mode': 'a'})
    instance = client.create_test_from_plan(plan['id'], 'test-a', {'mode': 'b'})
    info = client.poll_test_completion(instance['id'], poll_interval_sec=0.001)
    assert info['status'] == 'FINISHED'
    exported = client.export_plan_results(plan['id'], tmp_path)
    assert zipfile.is_zipfile(exported['export_file'])
    create = next(c for c in api['calls'] if c[1] == '/api/runner')
    assert create[3] == b''
    assert json.loads(create[2]['variant'][0]) == {'mode': 'b'}
    assert any(c[:2] == ('POST', '/api/runner/test-1') for c in api['calls'])


@pytest.mark.parametrize('token', [None, '', '   ', 'development-test-token'])
def test_optional_token_matches_in_both_real_http_clients(api, token):
    client = OIDFClient(api['url'], token=token)
    try:
        # Exercises the official HTTP transport: blank headers previously fail
        # locally in httpx before reaching even a development suite endpoint.
        assert client.create_test_plan('test-plan', {'alias': 'token-regression'}, {})['id']
        expected = 'Bearer development-test-token' if token == 'development-test-token' else None
        assert client.session.headers.get('Authorization') == expected
        assert client._upstream.httpclient.headers.get('Authorization') == expected
    finally:
        client.close()


@pytest.mark.parametrize('state', ['RUNNING', 'WAITING', 'CREATED'])
def test_interim_pass_cannot_pass_timeout(api, state):
    api['status'] = state
    result = OIDFClient(api['url']).poll_test_completion('test-1', poll_interval_sec=0.001, max_timeout_sec=0.03)
    assert result['result'] == 'TIMEOUT'


def test_variant_results_preserved_and_logs_saved(api, tmp_path):
    run = ConformanceRunner(OIDFClient(api['url']), tmp_path, poll_timeout=1)
    result = run.run_plan('certify', template(tmp_path), {}, [])
    assert len(result['results']) == 2
    assert result['summary']['is_gated_pass']
    assert (tmp_path / 'test-1-log.json').exists()


@pytest.mark.parametrize('modules', [[], [{'name': 'bad'}], [{'testModule': 'a'}, {'testModule': 'a'}]])
def test_invalid_plan_fails(api, tmp_path, modules):
    api['modules'] = modules
    with pytest.raises(ValueError):
        ConformanceRunner(OIDFClient(api['url']), tmp_path).run_plan('certify', template(tmp_path), {}, [])


def test_corrupt_export_fails_gate(api, tmp_path):
    api['export_valid'] = False
    result = ConformanceRunner(OIDFClient(api['url']), tmp_path).run_plan('certify', template(tmp_path), {}, [])
    assert not result['summary']['is_gated_pass']
    assert result['summary']['artifact_error']


def test_empty_export_cannot_pass_gate(api,tmp_path,monkeypatch):
    client=OIDFClient(api['url'])
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w'): pass
    response=type('Export',(),{'content':stream.getvalue()})()
    original=client.request
    monkeypatch.setattr(client,'request',lambda method,path,**kw:
        response if path.startswith('/api/plan/export/') else original(method,path,**kw))
    result=ConformanceRunner(client,tmp_path).run_plan('certify',template(tmp_path),{},[])
    assert result['summary']['is_gated_pass'] is False
    assert 'no result artifacts' in result['summary']['artifact_error']
    client.close()


@pytest.mark.parametrize('status', ['ERROR', 'REVIEW', 'TIMEOUT', 'INTERRUPTED', 'CANCELLED'])
def test_operational_failures_never_waived(status):
    entry = {'reason': 'reviewed issue', 'jira_id': 'verified-123', 'statuses': [status],
             'expiry_date': (date.today() + timedelta(days=1)).isoformat()}
    assert classify(status, entry) == status


def test_expected_failure_requires_expiry_reason_issue_and_status():
    entry = {'reason': 'documented gap', 'jira_id': 'verified-123', 'statuses': ['FAILED'],
             'expiry_date': (date.today() + timedelta(days=1)).isoformat()}
    assert classify('FAILED', entry) == 'EXPECTED_FAILURE'
    entry['expiry_date'] = (date.today() - timedelta(days=1)).isoformat()
    assert classify('FAILED', entry) == 'FAILED'
    assert classify('FAILED', {}) == 'FAILED'


def test_template_escaping_and_unresolved(tmp_path):
    p = tmp_path / 'template.json'
    p.write_text('{"value":"${VALUE}","key":${KEY}}')
    assert render_template(p, {'VALUE': 'a"b\\c', 'KEY': {'d': 'secret'}}) == {'value': 'a"b\\c', 'key': {'d': 'secret'}}
    with pytest.raises(ValueError, match='Missing configuration'):
        render_template(p, {'VALUE': 'x'})


@pytest.mark.parametrize('status', ['REVIEW', 'SKIPPED', 'EXPECTED_FAILURE', 'WARNING', 'TIMEOUT'])
def test_diff_regressions(status):
    result = DiffEngine.compare_runs({'results': {'a': 'PASSED'}}, {'results': {'a': status}})
    assert result['has_regressions'] == (status != 'WARNING')


def test_removed_test_is_regression():
    assert DiffEngine.compare_runs({'results': {'a': 'PASSED'}}, {'results': {}})['has_regressions']


def test_verify_uses_backend_nonce_and_suite_token(api):
    handoff = OID4VPHandoffClient(api['url'], api['url'] + '/v1/verify', {'clientId': 'backend-client'})
    evidence = handoff.execute_presentation_handoff({'urls': {'authorization_endpoint': api['url'] + '/wallet'}})
    assert api['wallet_params']['nonce'] == ['backend-nonce']
    assert api['wallet_params']['state'] == ['real-request-id']
    assert api['submission']['vp_token'] == ['suite-token']
    assert evidence['submission_http_status'] == 400
    assert not evidence['evidence_uploaded']


def test_missing_wallet_endpoint_raises(api):
    with pytest.raises(ValueError, match='no wallet authorization'):
        OID4VPHandoffClient(api['url'], api['url'], {}).execute_presentation_handoff({})


def test_final_sdk_preserves_native_dcql_and_metadata(api):
    client_id = 'redirect_uri:' + api['url'] + '/v1/verify/direct-post'
    query = {'credentials': [{'id': 'pid', 'format': 'dc+sd-jwt',
                              'meta': {'vct_values': ['urn:eudi:pid:1']}}]}
    api['verify_response'] = {'requestId': 'real-request-id',
        'authorizationDetails': {'nonce': 'backend-nonce', 'responseType': 'vp_token',
          'responseMode': 'direct_post', 'responseUri': api['url'] + '/v1/verify/direct-post',
          'dcqlQuery': query, 'responseCodeValidationRequired': False}}
    OID4VPHandoffClient(api['url'], api['url'] + '/v1/verify',
                       {'clientId': client_id, 'dcqlQuery': query}).execute_presentation_handoff(
                           {'urls': {'authorization_endpoint': api['url'] + '/wallet'}})
    params = api['wallet_params']
    assert params['client_id'] == [client_id]
    assert json.loads(params['dcql_query'][0]) == query
    assert params['nonce'] == ['backend-nonce']
    assert 'presentation_definition' not in params
    assert 'responseCodeValidationRequired' not in params
    metadata = json.loads(params['client_metadata'][0])
    assert 'vp_formats' not in metadata
    assert 'dc+sd-jwt' in metadata['vp_formats_supported']


def test_legacy_sdk_remains_legacy_without_dcql_translation(api):
    OID4VPHandoffClient(api['url'], api['url'] + '/v1/verify',
                       {'clientId': 'backend-client'}, sdk_version='0.17.0').execute_presentation_handoff(
                           {'urls': {'authorization_endpoint': api['url'] + '/wallet'}})
    assert 'dcql_query' not in api['wallet_params']
    assert 'vp_formats' in json.loads(api['wallet_params']['client_metadata'][0])


def test_suite_certificate_matches_generated_signing_key():
    import base64
    from cryptography import x509
    from cryptography.hazmat.primitives.asymmetric import ec
    jwk = generate_signing_jwk(include_certificate=True)
    cert = x509.load_der_x509_certificate(base64.b64decode(jwk['x5c'][0]))
    public = cert.public_key().public_numbers()
    decode = lambda value: int.from_bytes(base64.urlsafe_b64decode(value + '=='), 'big')
    assert public.x == decode(jwk['x']) and public.y == decode(jwk['y'])
    assert ec.derive_private_key(decode(jwk['d']), ec.SECP256R1()).public_key().public_numbers() == public


def test_container_suite_origin_is_routed_without_changing_verifier_values(api):
    handoff = OID4VPHandoffClient(api['url'], api['url'] + '/v1/verify', {'clientId': 'backend-client'})
    handoff.execute_presentation_handoff({'urls': {'authorization_endpoint': 'https://container-only.invalid/wallet'}})
    assert api['wallet_params']['client_id'] == ['backend-client']
    assert api['wallet_params']['nonce'] == ['backend-nonce']


def test_waiting_reads_exposed_values_from_runtime(api):
    api['status'] = 'WAITING'
    seen = []
    def waiting(info, remaining):
        seen.append(info['urls']['authorization_endpoint'])
        api['status'] = 'FINISHED'
    result = OIDFClient(api['url']).poll_test_completion('test-1', on_waiting=waiting, poll_interval_sec=0.001)
    assert result['status'] == 'FINISHED'
    assert seen == [api['url'] + '/wallet']


def test_signing_keys_are_fresh_and_valid():
    from cryptography.hazmat.primitives.asymmetric import ec
    import base64
    one, two = generate_signing_jwk(), generate_signing_jwk()
    assert one['d'] != two['d']
    decode = lambda s: int.from_bytes(base64.urlsafe_b64decode(s + '=' * (-len(s) % 4)), 'big')
    key = ec.derive_private_key(decode(one['d']), ec.SECP256R1())
    assert key.public_key().public_numbers().x == decode(one['x'])


def test_startup_error_replaces_stale_pass(api, tmp_path):
    (tmp_path / 'conformance-summary.json').write_text('{"consolidated":{"gate_met":true}}')
    code = main(['--component', 'certify', '--oidf-url', api['url'], '--reports-dir', str(tmp_path),
                 '--expected-failures', str(tmp_path / 'missing.json')])
    assert code == 1
    assert not json.loads((tmp_path / 'conformance-summary.json').read_text())['consolidated']['gate_met']


def test_cli_combined_with_real_transport_contract(api, tmp_path):
    p = template(tmp_path)
    code = main(['--combined', '--parallel', '2', '--oidf-url', api['url'], '--reports-dir', str(tmp_path),
                 '--certify-config', str(p), '--verify-config', str(p)])
    assert code == 0
    summary = json.loads((tmp_path / 'conformance-summary.json').read_text())
    assert set(summary['runs']) == {'certify', 'verify'}
    assert summary['consolidated']['gate_met']
    assert len(summary['consolidated']['results']) == 4


@pytest.mark.parametrize('regressed_component', ['certify', 'verify'])
def test_cli_combined_regression_does_not_contaminate_other_component(api, tmp_path, regressed_component):
    plan = template(tmp_path)
    first, second = tmp_path / 'first', tmp_path / 'second'
    args = ['--combined', '--parallel', '2', '--oidf-url', api['url'],
            '--certify-config', str(plan), '--verify-config', str(plan)]
    assert main([*args, '--reports-dir', str(first)]) == 0
    baseline = json.loads((first / 'conformance-summary.json').read_text())
    baseline['consolidated']['results'][regressed_component + '::removed-controlled-fixture'] = 'PASSED'
    baseline_path = tmp_path / 'baseline.json'
    baseline_path.write_text(json.dumps(baseline))
    assert main([*args, '--reports-dir', str(second), '--diff', str(baseline_path)]) == 1
    report = json.loads((second / 'conformance-summary.json').read_text())
    for c in ['certify', 'verify']:
        assert report['runs'][c]['summary']['is_gated_pass'] is True
        assert report['runs'][c]['summary']['gate_met'] == (c != regressed_component)
    assert not report['consolidated']['gate_met']


def test_screenshot_receipt_preserves_official_review(api, tmp_path):
    image = tmp_path / 'screen.png'
    image.write_bytes(b'\x89PNG\r\n\x1a\ncontrolled-unit-fixture')
    client = OIDFClient(api['url'])
    receipt = client.upload_test_image('test-1', 'placeholder-1', image)
    assert receipt['placeholder'] == 'placeholder-1'
    api['status'] = 'FINISHED'
    result = client.poll_test_completion('test-1')
    assert result['result'] == 'REVIEW'
    assert classify(result['result']) == 'REVIEW'


def test_unfilled_screenshot_receipt_is_an_error(api, tmp_path):
    image = tmp_path / 'screen.jpg'
    image.write_bytes(b'\xff\xd8\xffcontrolled-unit-fixture')
    api['accept_image'] = False
    with pytest.raises(ValueError, match='did not fill'):
        OIDFClient(api['url']).upload_test_image('test-1', 'placeholder-1', image)


def test_non_image_cannot_be_uploaded_as_screenshot(api, tmp_path):
    image = tmp_path / 'screen.png'
    image.write_bytes(b'<html>backend stand-in</html>')
    with pytest.raises(ValueError, match='actual PNG or JPEG'):
        OIDFClient(api['url']).upload_test_image('test-1', 'placeholder-1', image)
    assert not api['calls']


@pytest.mark.parametrize('status', ['PASSED', 'REVIEW', 'INTERRUPTED', 'TIMEOUT'])
@pytest.mark.parametrize('error', [RuntimeError('log download unavailable'), TimeoutError()])
def test_log_failure_preserves_official_outcome_and_rejects_gate(api, tmp_path, status, error):
    client = OIDFClient(api['url'])
    client.poll_test_completion = lambda *args, **kwargs: {
        'status':'FINISHED' if status in {'PASSED','REVIEW'} else status, 'result':status}
    def unavailable_log(_):
        raise error
    client.get_test_log = unavailable_log
    result = ConformanceRunner(client,tmp_path).run_plan('certify',template(tmp_path),{},[])
    assert all(m['status'] == status for m in result['modules'])
    assert all(m['evidence_error'] == (str(error) or type(error).__name__) for m in result['modules'])
    assert set(result['results'].values()) == {status}
    assert result['summary']['is_gated_pass'] is False
    assert (str(error) or type(error).__name__) in result['summary']['artifact_error']
    client.close()
