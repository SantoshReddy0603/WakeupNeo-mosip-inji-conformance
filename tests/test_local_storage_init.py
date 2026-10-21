import boto3
from botocore.stub import Stubber
from botocore.exceptions import ClientError
import pytest
from init_local_storage import ensure_bucket, initialize


def client():
    return boto3.client('s3', aws_access_key_id='local-test', aws_secret_access_key='local-test',
                        region_name='us-east-1')


def test_fresh_bucket_created_and_read_back():
    storage = client()
    with Stubber(storage) as stub:
        stub.add_client_error('head_bucket', '404', http_status_code=404, expected_params={'Bucket': 'automationtests'})
        stub.add_response('create_bucket', {}, {'Bucket': 'automationtests'})
        stub.add_response('head_bucket', {}, {'Bucket': 'automationtests'})
        assert ensure_bucket(storage, 'automationtests')
        stub.assert_no_pending_responses()


def test_existing_bucket_is_preserved():
    storage = client()
    with Stubber(storage) as stub:
        stub.add_response('head_bucket', {}, {'Bucket': 'automationtests'})
        assert not ensure_bucket(storage, 'automationtests')


def test_access_denial_is_not_treated_as_missing_bucket():
    storage = client()
    with Stubber(storage) as stub:
        stub.add_client_error('head_bucket', '403', http_status_code=403)
        with pytest.raises(ClientError):
            ensure_bucket(storage, 'automationtests')


def test_external_storage_is_never_provisioned():
    with pytest.raises(ValueError):
        initialize({'S3_ENDPOINT': 'https://external.example.com'})
