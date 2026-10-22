"""Storage CLI contracts; controlled transport, never official test evidence."""
import hashlib
import io
import json
from pathlib import Path
import runpy
import sys
import boto3
import pytest


@pytest.mark.parametrize('historical', [True, False])
def test_verifier_uses_actual_lifecycle_namespace(tmp_path, monkeypatch, historical):
    data = {'schema_version': 2, 'run_id': 'controlled-run', 'runs': {}, 'consolidated': {'gate_met': False}}
    payload = json.dumps(data).encode()
    (tmp_path / 'conformance-summary.json').write_bytes(payload)
    prefix = ('openid-conformance-validation/' if historical else 'openid-conformance/') + 'controlled-run/'
    if historical:
        prefix += 'a' * 32 + '/'
    key = prefix + 'conformance-summary.json'
    manifest = {'configured': True, 'run_id': 'controlled-run', 'prefix': prefix, 'bucket': 'automationtests',
                'verified': [{'file': 'conformance-summary.json', 'key': key, 'sha256': hashlib.sha256(payload).hexdigest()}]}
    (tmp_path / 'artifact-storage-validation.json').write_text(json.dumps(manifest))
    class ControlledTransport:
        def get_object(self, **kwargs):
            assert kwargs == {'Bucket': 'automationtests', 'Key': key}
            return {'Body': io.BytesIO(payload)}
    monkeypatch.setattr(boto3, 'client', lambda *args, **kwargs: ControlledTransport())
    for name, value in {'S3_ENDPOINT': 'http://fixture.invalid', 'S3_BUCKET': 'automationtests',
                        'AWS_ACCESS_KEY_ID': 'fixture', 'AWS_SECRET_ACCESS_KEY': 'fixture'}.items():
        monkeypatch.setenv(name, value)
    output = tmp_path / 'validation.json'
    monkeypatch.setattr(sys, 'argv', ['verify_storage.py', str(tmp_path), '--output', str(output)])
    runpy.run_path(str(Path(__file__).resolve().parents[1] / 'runner/verify_storage.py'), run_name='__main__')
    assert json.loads(output.read_text())['verified'][0]['key'] == key


def test_foreign_manifest_fails_before_storage_access(tmp_path, monkeypatch):
    (tmp_path / 'conformance-summary.json').write_text(json.dumps({'run_id': 'current'}))
    (tmp_path / 'artifact-storage-validation.json').write_text(json.dumps({'configured': True, 'run_id': 'other'}))
    monkeypatch.setattr(sys, 'argv', ['verify_storage.py', str(tmp_path), '--output', str(tmp_path / 'result.json')])
    with pytest.raises(ValueError, match='identity'):
        runpy.run_path(str(Path(__file__).resolve().parents[1] / 'runner/verify_storage.py'), run_name='__main__')
