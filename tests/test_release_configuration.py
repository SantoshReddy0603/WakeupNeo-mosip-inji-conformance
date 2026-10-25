"""Stock and custom deployments retain distinct configuration and provenance."""
import base64
import json
from types import SimpleNamespace
import pytest
from release_versions import configured_versions
from deployment_provenance import deployment_metadata, holder_binding_template_enabled
from course_issuer import configure
from oid4vp_handoff import OID4VPHandoffClient


def test_versions_follow_defaults_local_configuration_and_nonempty_environment(tmp_path, monkeypatch):
    docker = tmp_path / 'docker'
    docker.mkdir()
    (docker / 'versions.env').write_text('VERIFY_VERSION=default\nVERIFY_SDK_VERSION=default\n')
    (docker / '.env').write_text('VERIFY_VERSION=local\nAWS_SECRET_ACCESS_KEY=do-not-return\n')
    monkeypatch.setenv('VERIFY_VERSION', '')
    assert configured_versions(tmp_path) == {'VERIFY_VERSION': 'local', 'VERIFY_SDK_VERSION': 'default'}
    monkeypatch.setenv('VERIFY_VERSION', 'selected')
    assert configured_versions(tmp_path)['VERIFY_VERSION'] == 'selected'


def test_unvalidated_sdk_release_fails_instead_of_reusing_another_protocol_adapter():
    with pytest.raises(ValueError, match='Unsupported Verify SDK version'):
        OID4VPHandoffClient('https://suite', 'https://verify', {}, sdk_version='1.0.99')


@pytest.mark.parametrize('binding', [False, True])
def test_stock_template_does_not_require_patch_only_holder_context(binding):
    captured = {}
    response = SimpleNamespace(ok=True, status_code=200, json=lambda: {})
    class Session:
        def get(self, *args, **kwargs):
            return response
        def put(self, url, json, **kwargs):
            captured.update(json)
            return response
    configure(Session(), holder_binding=binding)
    template = base64.b64decode(captured['vcTemplate']).decode()
    assert ('"cnf":$cnf' in template) == binding
    assert captured['credentialFormat'] == 'dc+sd-jwt'


@pytest.mark.parametrize('image,stock,binding', [
    ('injistack/inji-certify-with-plugins:1.0.0-alpha.1', True, False),
    ('inji-harness/certify-positive:local', False, True),
    ('inji-harness/certify-dpop:local', False, False),
])
def test_managed_provenance_uses_the_observed_image(tmp_path, image, stock, binding):
    docker = tmp_path / 'docker'
    docker.mkdir()
    (docker / 'isolated-state.json').write_text(json.dumps({
        'image_references': {'course-certify': image},
        'images': {'course-certify': 'sha256:' + 'a' * 64}}))
    metadata = deployment_metadata(tmp_path)
    assert (metadata['issuer_build'] == 'stock-release') == stock
    assert metadata['issuer_image'] == image
    assert holder_binding_template_enabled(tmp_path) == binding


def test_public_ci_provenance_rejects_untrusted_values_and_credentials(tmp_path):
    from ci_artifacts import export
    private = tmp_path / 'private'
    private.mkdir()
    summary = {'schema_version': 2, 'run_id': 'fixture',
        'runs': {'certify': {'summary': {'gate_met': False}, 'results': {'fixture': 'REVIEW'}}},
        'consolidated': {'gate_met': False},
        'deployment': {'issuer_build': 'stock-release', 'issuer_image': 'https://user:DO-NOT-EXPORT@host',
            'issuer_image_id': 'DO-NOT-EXPORT', 'secret': 'DO-NOT-EXPORT',
            'versions': {'VERIFY_VERSION': '1.0.0-alpha.1', 'AWS_SECRET_ACCESS_KEY': 'DO-NOT-EXPORT',
                         'CERTIFY_VERSION': 'DO-NOT-EXPORT\npassword'}}}
    (private / 'conformance-summary.json').write_text(json.dumps(summary))
    safe = tmp_path / 'safe'
    result = export(private, safe)
    assert result['deployment'] == {'issuer_build': 'stock-release',
                                    'versions': {'VERIFY_VERSION': '1.0.0-alpha.1'}}
    assert 'DO-NOT-EXPORT' not in (safe / 'ci-summary.json').read_text()
