"""Read back actual uploaded artifacts and verify bytes; never generate test outcomes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import boto3
from botocore.config import Config

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('report_directory', type=Path)
parser.add_argument('--env-file', type=Path)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
if args.env_file:
    for line in args.env_file.read_text().splitlines():
        if '=' in line and not line.startswith('#'):
            key, value = line.split('=', 1)
            os.environ.setdefault(key, value)
summary = json.loads((args.report_directory / 'conformance-summary.json').read_text())
prefix = 'openid-conformance/' + summary['run_id'] + '/'
bucket = os.getenv('S3_BUCKET') or 'automationtests'
client = boto3.client('s3', endpoint_url=os.environ['S3_ENDPOINT'],
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    region_name=os.getenv('AWS_REGION') or 'us-east-1', config=Config(s3={'addressing_style': 'path'}))
results = []
root_files = {'conformance-summary.json', 'combined-conformance-badge.svg', 'extent-report.html', 'testng-results.xml'}
test_ids = set()
for component, run in summary['runs'].items():
    root_files.update({component + '-conformance-report.json', component + '-conformance-badge.svg',
                       'plan-' + run['summary'].get('plan_id', '') + '-export.zip'})
    for module in run['modules']:
        if module.get('test_id'):
            test_ids.add(module['test_id'])
            root_files.add(module['test_id'] + '-log.json')
for artifact in sorted(args.report_directory.rglob('*')):
    if not artifact.is_file():
        continue
    relative = artifact.relative_to(args.report_directory)
    if not ((len(relative.parts) == 1 and relative.name in root_files)
            or (len(relative.parts) > 1 and relative.parts[0] in test_ids)):
        continue
    key = prefix + relative.as_posix()
    received = client.get_object(Bucket=bucket, Key=key)['Body'].read()
    local = artifact.read_bytes()
    if received != local:
        raise RuntimeError('Uploaded bytes differ: ' + artifact.name)
    results.append({'file': relative.as_posix(), 'key': key, 'sha256': hashlib.sha256(received).hexdigest(), 'bytes': len(received)})
if not results:
    raise RuntimeError('No actual artifacts verified')
args.output.write_text(json.dumps({'bucket': bucket, 'run_id': summary['run_id'], 'verified': results}, indent=2))
print(f'Verified {len(results)} real uploaded artifacts in {bucket}')
