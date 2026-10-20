"""Prepare local deployment secrets/TLS; never fabricate identity or test results."""
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
import secrets
import json
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.asymmetric import ec
import base64
from cryptography.hazmat.primitives.serialization import pkcs12

ROOT = Path(__file__).resolve().parents[1]


def prepare():
    docker = ROOT / 'docker'
    env = docker / '.env'
    if not env.exists():
        env.write_text('POSTGRES_PASSWORD=' + secrets.token_urlsafe(32) + '\n'
                       'VERIFY_KEYSTORE_PASSWORD=' + secrets.token_urlsafe(32) + '\n'
                       'OIDF_PUBLIC_URL=https://host.docker.internal:8443\n'
                       'INJI_PUBLIC_URL=https://host.docker.internal:8445\n', encoding='utf-8')
    existing = dict(line.split('=', 1) for line in env.read_text().splitlines()
                    if '=' in line and not line.startswith('#'))
    storage_defaults = {'CERTIFY_KEYSTORE_PASSWORD': secrets.token_urlsafe(32),
                        'ISSUER_LOGIN_USERNAME': 'development-learner',
                        'ISSUER_LOGIN_PASSWORD': secrets.token_urlsafe(24),
                        'AWS_ACCESS_KEY_ID': 'local-' + secrets.token_hex(8),
                        'AWS_SECRET_ACCESS_KEY': secrets.token_urlsafe(32),
                        'S3_ENDPOINT': 'http://localhost:9000', 'S3_BUCKET': 'automationtests',
                        'AWS_REGION': 'us-east-1'}
    with env.open('a', encoding='utf-8') as stream:
        for setting, value in storage_defaults.items():
            if setting not in existing:
                stream.write(setting + '=' + value + '\n')
    values = dict(line.split('=', 1) for line in env.read_text().splitlines()
                  if '=' in line and not line.startswith('#'))
    auth_dir = docker / 'local/keycloak'
    auth_dir.mkdir(parents=True, exist_ok=True)
    realm_path = auth_dir / 'course-realm.json'
    wallet_dir = docker / 'local/wallet-keys'
    wallet_dir.mkdir(parents=True, exist_ok=True)
    public_wallet_dir = docker / 'local/public-wallet-keys'
    public_wallet_dir.mkdir(parents=True, exist_ok=True)
    for wallet in ['conformance-course-wallet', 'conformance-course-wallet-2']:
        private_path = wallet_dir / (wallet + '.private.json')
        if not private_path.exists():
            key = ec.generate_private_key(ec.SECP256R1()).private_numbers()
            encode = lambda number: base64.urlsafe_b64encode(number.to_bytes(32, 'big')).decode().rstrip('=')
            jwk = {'kty': 'EC', 'crv': 'P-256', 'alg': 'ES256', 'use': 'sig', 'kid': wallet,
                   'x': encode(key.public_numbers.x), 'y': encode(key.public_numbers.y), 'd': encode(key.private_value)}
            private_path.write_text(json.dumps({'keys': [jwk]}))
            (public_wallet_dir / (wallet + '.public.json')).write_text(json.dumps({'keys': [
                {name: value for name, value in jwk.items() if name != 'd'}]}))
        jwks = json.loads(private_path.read_text())
        (public_wallet_dir / (wallet + '.public.json')).write_text(json.dumps({'keys': [
            {name: value for name, value in key.items() if name != 'd'} for key in jwks['keys']]}))
    if not realm_path.exists():
        realm = {'realm': 'course', 'enabled': True, 'sslRequired': 'none',
                 'registrationAllowed': False,
                 'clientScopes': [{'name': 'course_completion', 'protocol': 'openid-connect',
                     'attributes': {'include.in.token.scope': 'true'},
                     'protocolMappers': [{'name': 'subject', 'protocol': 'openid-connect',
                         'protocolMapper': 'oidc-sub-mapper', 'config': {'access.token.claim': 'true'}},
                         {'name': 'certify-audience', 'protocol': 'openid-connect',
                         'protocolMapper': 'oidc-audience-mapper', 'config': {
                             'included.custom.audience': 'https://host.docker.internal:8446/v1/certify/issuance/credential',
                             'access.token.claim': 'true'}},
                         {'name': 'certify-client-id', 'protocol': 'openid-connect',
                          'protocolMapper': 'oidc-hardcoded-claim-mapper', 'config': {
                              'claim.name': 'client_id', 'claim.value': 'course-wallet',
                              'jsonType.label': 'String', 'access.token.claim': 'true'}}]}],
                 'clients': [{'clientId': 'course-wallet', 'enabled': True,
                     'publicClient': True, 'protocol': 'openid-connect',
                     'standardFlowEnabled': True, 'directAccessGrantsEnabled': True,
                     'redirectUris': ['https://host.docker.internal:8443/test/a/*'],
                     'defaultClientScopes': [], 'optionalClientScopes': ['course_completion'],
                     'attributes': {'pkce.code.challenge.method': 'S256'}}],
                 'users': [{'id': '11111111-1111-4111-8111-111111111111',
                     'username': values['ISSUER_LOGIN_USERNAME'], 'enabled': True,
                     'email': 'development-learner@example.invalid', 'emailVerified': True,
                     'firstName': 'Development', 'lastName': 'Learner',
                     'credentials': [{'type': 'password', 'value': values['ISSUER_LOGIN_PASSWORD'],
                                      'temporary': False}]}]}
        realm_path.write_text(json.dumps(realm, indent=2), encoding='utf-8')
    # Preserve users/passwords while adding genuine private_key_jwt clients.
    realm = json.loads(realm_path.read_text(encoding='utf-8-sig'))
    realm['clientScopes'][0]['protocolMappers'] = [mapper for mapper in
        realm['clientScopes'][0]['protocolMappers'] if mapper['name'] != 'certify-client-id']
    for client_id in ['course-wallet', 'conformance-course-wallet', 'conformance-course-wallet-2']:
        clients = [client for client in realm['clients'] if client['clientId'] == client_id]
        if clients:
            client = clients[0]
        else:
            client = {'clientId': client_id, 'enabled': True, 'protocol': 'openid-connect',
                'publicClient': False, 'clientAuthenticatorType': 'client-jwt',
                'standardFlowEnabled': True, 'directAccessGrantsEnabled': False,
                'redirectUris': ['https://host.docker.internal:8443/test/a/*'],
                'defaultClientScopes': [], 'optionalClientScopes': ['course_completion'],
                'attributes': {'pkce.code.challenge.method': 'S256', 'use.jwks.url': 'true',
                    'jwks.url': 'http://course-httpd:8080/' + client_id + '.public.json',
                    'token.endpoint.auth.signing.alg': 'ES256'}}
            realm['clients'].append(client)
        client['redirectUris'] = ['https://host.docker.internal:8443/test/a/*']
        client['protocolMappers'] = [{'name': 'certify-client-id', 'protocol': 'openid-connect',
            'protocolMapper': 'oidc-hardcoded-claim-mapper', 'config': {'claim.name': 'client_id',
                'claim.value': client_id, 'jsonType.label': 'String', 'access.token.claim': 'true'}}]
    realm_path.write_text(json.dumps(realm, indent=2))
    (docker / 'local/certify-keys').mkdir(parents=True, exist_ok=True)
    cert_dir = docker / 'nginx/certs'
    cert_dir.mkdir(parents=True, exist_ok=True)
    cert_path, key_path = cert_dir / 'server.crt', cert_dir / 'server.key'
    if not cert_path.exists() and not key_path.exists():
        key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'Inji local conformance')])
        now = datetime.now(timezone.utc)
        certificate = (x509.CertificateBuilder().subject_name(name).issuer_name(name)
            .public_key(key.public_key()).serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(minutes=5)).not_valid_after(now + timedelta(days=30))
            .add_extension(x509.SubjectAlternativeName([x509.DNSName('localhost'),
                x509.DNSName('host.docker.internal'), x509.DNSName('conformance-httpd'),
                x509.DNSName('inji-httpd')]), critical=False).sign(key, hashes.SHA256()))
        key_path.write_bytes(key.private_bytes(serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
        cert_path.write_bytes(certificate.public_bytes(serialization.Encoding.PEM))
    elif not cert_path.exists() or not key_path.exists():
        raise ValueError('TLS certificate/key pair incomplete; restore the matching pair')
    for name in ['certify', 'plugins']:
        (docker / 'local' / name).mkdir(parents=True, exist_ok=True)
    signing_dir = docker / 'local/verify-keys'
    signing_dir.mkdir(parents=True, exist_ok=True)
    signing_path = signing_dir / 'verify.p12'
    if not signing_path.exists():
        values = dict(line.split('=', 1) for line in env.read_text().splitlines()
                      if '=' in line and not line.startswith('#'))
        password = values['VERIFY_KEYSTORE_PASSWORD'].encode()
        signing_key = ed25519.Ed25519PrivateKey.generate()
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'Local Inji Verify signing')])
        now = datetime.now(timezone.utc)
        signing_certificate = (x509.CertificateBuilder().subject_name(name).issuer_name(name)
            .public_key(signing_key.public_key()).serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(minutes=5)).not_valid_after(now + timedelta(days=365))
            .sign(signing_key, algorithm=None))
        signing_path.write_bytes(pkcs12.serialize_key_and_certificates(
            b'verify', signing_key, signing_certificate, None, serialization.BestAvailableEncryption(password)))
    print('Created/preserved local secrets and TLS certificate. Nothing has been started.')
    print('Start suite: docker compose --env-file docker/.env -f docker/docker-compose.yml up -d --build')
    print('Local course issuer: docker compose --env-file docker/.env -f docker/certify-final.compose.yml up -d')


if __name__ == '__main__':
    prepare()

