"""Initialize the managed loopback MinIO bucket; never provision external S3 storage."""
import argparse
from pathlib import Path
import time
from urllib.parse import urlsplit
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, EndpointConnectionError, ConnectionClosedError


def ensure_bucket(client, bucket):
    try:
        client.head_bucket(Bucket=bucket)
        return False
    except ClientError as exc:
        if str(exc.response['Error']['Code']) not in {'404', 'NoSuchBucket', 'NotFound'}:
            raise
    client.create_bucket(Bucket=bucket)
    client.head_bucket(Bucket=bucket)
    return True


def initialize(values, timeout=60):
    endpoint = values['S3_ENDPOINT']
    parsed = urlsplit(endpoint)
    if parsed.scheme != 'http' or parsed.hostname not in {'localhost', '127.0.0.1'} or parsed.port != 9000:
        raise ValueError('Managed bootstrap may initialize only loopback MinIO on port 9000')
    client = boto3.client('s3', endpoint_url=endpoint,
                          aws_access_key_id=values['AWS_ACCESS_KEY_ID'],
                          aws_secret_access_key=values['AWS_SECRET_ACCESS_KEY'],
                          region_name=values.get('AWS_REGION', 'us-east-1'),
                          config=Config(connect_timeout=2, read_timeout=2, retries={'max_attempts': 0},
                                        s3={'addressing_style': 'path'}))
    deadline = time.monotonic() + timeout
    while True:
        try:
            created = ensure_bucket(client, values.get('S3_BUCKET', 'automationtests'))
            print('Managed artifact bucket ready; created=' + str(created))
            return
        except (EndpointConnectionError, ConnectionClosedError):
            if time.monotonic() >= deadline:
                raise
            time.sleep(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--env-file', type=Path, default=Path(__file__).resolve().parents[1] / 'docker/.env')
    args = parser.parse_args()
    initialize(dict(line.split('=', 1) for line in args.env_file.read_text().splitlines()
                    if '=' in line and not line.startswith('#')))
