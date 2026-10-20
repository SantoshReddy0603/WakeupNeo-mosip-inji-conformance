"""Controlled storage fixtures, separate from actual MinIO/conformance evidence."""
import json
import pytest
from report_lifecycle import upload_artifacts

@pytest.mark.parametrize('corrupt',[False,True])
def test_artifact_lifecycle_excludes_stale_ids_and_checks_received_bytes(tmp_path,monkeypatch,corrupt):
    report = {'runs':{'verify':{'summary':{'plan_id':'current-plan'},
                               'modules':[{'test_id':'current-test'}]}}}
    (tmp_path/'conformance-summary.json').write_text(json.dumps(report))
    for name in ['current-test','old-test']:
        (tmp_path/name).mkdir()
        (tmp_path/name/'screenshot.jpg').write_bytes(b'controlled transport bytes')
    for name in ['current-run','old-run']:
        directory = tmp_path/'existing-verify'/name
        directory.mkdir(parents=True)
        (directory/'testng-results.xml').write_text('<unit-fixture/>')
    stored = {}
    class StorageFixture:
        def put_object(self,**kwargs): stored[kwargs['Key']] = kwargs['Body']
        def get_object(self,**kwargs):
            import io
            return {'Body':io.BytesIO(b'corrupt' if corrupt else stored[kwargs['Key']])}
    monkeypatch.setattr('report_lifecycle.boto3.client',lambda *a,**k:StorageFixture())
    for key in ['S3_ENDPOINT','AWS_ACCESS_KEY_ID','AWS_SECRET_ACCESS_KEY']:
        monkeypatch.setenv(key,'controlled-unit-fixture')
    if corrupt:
        with pytest.raises(ValueError,match='read-back mismatch'):
            upload_artifacts(tmp_path,'current-run','validation-fixture/')
    else:
        result = upload_artifacts(tmp_path,'current-run','validation-fixture/')
        assert len(result['verified']) == 3
        assert not any('old-' in key for key in stored)
