from pathlib import Path
import importlib.util
import json
import yaml
from preflight import validate
from oid4vp_handoff import PostForm

ROOT = Path(__file__).resolve().parents[1]


def test_compose_has_only_real_services_and_valid_mounts():
    compose = yaml.safe_load((ROOT / 'docker/docker-compose.yml').read_text(encoding='utf-8-sig'))
    services = dict(compose['services'])
    assert 'inji-verify-adapter' not in services
    assert set(['mongodb', 'conformance-server', 'conformance-httpd', 'course-certify', 'course-auth', 'final-verify']) <= services.keys()
    assert services['course-certify']['image'] == 'injistack/inji-certify-with-plugins:${CERTIFY_VERSION:?Run runner/setup.py}'
    assert services['final-verify']['image'] == 'injistack/inji-verify-service:${VERIFY_VERSION:?Run runner/setup.py}'
    assert len(services) == 10
    assert services['course-certify']['profiles'] == ['certify']
    assert services['final-verify']['profiles'] == ['verify']
    assert services['minio']['profiles'] == ['storage']
    assert services['conformance-server']['build']['args']['OIDF_REF'].endswith('11999aad62ec292f36101410d9d5b761d44903ff}')
    for service in services.values():
        if 'build' in service:
            assert (ROOT / 'docker' / service['build']['context'] / 'Dockerfile').is_file()
        for mount in service.get('volumes', []):
            if isinstance(mount, str) and mount.startswith('./'):
                assert (ROOT / 'docker' / mount.split(':')[0]).exists()


def test_preflight_reports_missing_real_issuer_inputs(tmp_path):
    errors = validate(tmp_path / 'config', tmp_path / 'plugins')
    assert any('issuer' in e for e in errors)
    assert any('plugin JAR' in e for e in errors)


def test_preflight_rejects_mock_identity_plugin(tmp_path):
    (tmp_path / 'certify-default.properties').write_text('mosip.certify.integration.vci-plugin=MockVCIssuancePlugin')
    assert any('demo/mock' in e for e in validate(tmp_path, tmp_path))


def test_html_form_extracts_encoded_suite_values():
    parser = PostForm()
    parser.feed('<form method="POST" action="https://verify/submit"><input name="vp_token" value="a&amp;b"><input name="state" value="s"></form>')
    assert parser.forms == [{'action': 'https://verify/submit', 'method': 'post', 'fields': {'vp_token': 'a&b', 'state': 's'}}]


def test_default_exceptions_are_empty():
    data = json.loads((ROOT / 'config/expected-failures.json').read_text())
    assert all(not entries for entries in data['expected_failures'].values())


def test_no_mock_mode_in_production_entrypoint():
    for name in ['runner/runner.py', 'run-conformance.sh', 'run-conformance.ps1']:
        text = (ROOT / name).read_text(encoding='utf-8-sig')
        assert '--mock' not in text
        assert 'MockServerThread' not in text
