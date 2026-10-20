"""Validate deployment inputs before attempting to start Inji containers."""
import argparse
from pathlib import Path
import sys
import os
import shutil
import re
from process_control import run
from datetime import datetime, timezone
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


def validate(config_dir, plugin_dir=None):
    errors = []
    properties = Path(config_dir) / 'certify-default.properties'
    if not properties.is_file():
        errors.append(f'Missing {properties}: supply real Certify/authentication/issuer configuration')
    else:
        text = '\n'.join(path.read_text(encoding='utf-8-sig') for path in sorted(Path(config_dir).glob('*.properties')))
        if 'MockVCIssuancePlugin' in text or 'mock.integration' in text or 'esignet-mock' in text:
            errors.append('Certify configuration still selects a demo/mock identity integration')
        if ('mosip.certify.integration.vci-plugin' not in text
            and 'mosip.certify.integration.data-provider-plugin=PostgresDataProviderPlugin' not in text):
            errors.append('Certify configuration has no credential issuance plugin')
    if plugin_dir is not None:
        plugins = Path(plugin_dir)
        if not plugins.is_dir() or not list(plugins.glob('*.jar')):
            errors.append(f'No real issuer plugin JAR in {plugins}; see SETUP.md')
    if not (ROOT / 'docker/.env').is_file():
        errors.append('Missing docker/.env: run python runner/setup.py')
    if not (ROOT / 'docker/nginx/certs/server.crt').is_file():
        errors.append('Missing local TLS certificate: run python runner/setup.py')
    else:
        errors.extend(validate_tls(ROOT/'docker/nginx/certs'))
    return errors


def validate_tls(directory):
    from cryptography import x509
    from cryptography.hazmat.primitives import serialization
    try:
        cert=x509.load_pem_x509_certificate((Path(directory)/'server.crt').read_bytes())
        key=serialization.load_pem_private_key((Path(directory)/'server.key').read_bytes(),password=None)
        if not cert.not_valid_before_utc <= datetime.now(timezone.utc) <= cert.not_valid_after_utc:
            return ['Local TLS certificate is expired or not yet valid; renew it before deployment']
        public=lambda value:value.public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo)
        if public(cert.public_key()) != public(key.public_key()):
            return ['Local TLS certificate/private key mismatch; restore the matching development pair']
    except (OSError,ValueError,TypeError):
        return ['Local TLS certificate/private key missing or unreadable; run runner/setup.py or restore the development pair']
    return []


def validate_storage(settings=None,connect=False):
    settings=os.environ if settings is None else settings
    names=['S3_ENDPOINT','AWS_ACCESS_KEY_ID','AWS_SECRET_ACCESS_KEY']
    if not any(settings.get(name) for name in names):return []
    missing=[name for name in names if not settings.get(name)]
    if missing:return ['Incomplete artifact storage configuration: set '+', '.join(missing)]
    endpoint=urlsplit(settings['S3_ENDPOINT'])
    if endpoint.scheme not in {'http','https'} or not endpoint.hostname or endpoint.username or endpoint.password:
        return ['S3_ENDPOINT must be an HTTP(S) URL without embedded credentials']
    if connect:
        import boto3
        from botocore.config import Config
        try:
            client=boto3.client('s3',endpoint_url=settings['S3_ENDPOINT'],
                aws_access_key_id=settings['AWS_ACCESS_KEY_ID'],aws_secret_access_key=settings['AWS_SECRET_ACCESS_KEY'],
                region_name=settings.get('AWS_REGION') or 'us-east-1',
                config=Config(connect_timeout=3,read_timeout=3,retries={'max_attempts':0},s3={'addressing_style':'path'}))
            try:client.head_bucket(Bucket=settings.get('S3_BUCKET') or 'automationtests')
            finally:client.close()
        except Exception:
            return ['Artifact bucket is inaccessible: check S3_ENDPOINT, bucket existence, network access and credential permissions']
    return []


def validate_java(minimum=11):
    try:
        result=run(['java','-version'],capture_output=True,text=True,timeout=5,check=True)
        version=re.search(r'version "(?:1\.)?(\d+)',result.stderr+result.stdout)
        if not version or int(version.group(1))<minimum:
            return ['Unsupported Java runtime: Java '+str(minimum)+' or newer is required']
    except Exception:
        # Do not echo arbitrary process output or environment values.
        return ['Java runtime unavailable: install Java '+str(minimum)+' or newer and check PATH']
    return []


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config-dir', default=str(ROOT / 'docker/certify-config'))
    parser.add_argument('--plugin-dir', help='Only needed for an external plugin build; default uses the official bundled PostgreSQL plugin')
    parser.add_argument('--runtime',action='store_true',help='Also verify local tools and read-only artifact bucket access')
    args = parser.parse_args()
    errors = validate(args.config_dir, args.plugin_dir)
    if args.runtime:
        errors.extend('Missing dependency: install '+tool for tool in ['docker','mvn','java'] if not shutil.which(tool))
        errors.extend(validate_java())
        errors.extend(validate_storage(connect=True))
    for error in errors:
        print('ERROR: ' + error, file=sys.stderr)
    sys.exit(1 if errors else 0)
