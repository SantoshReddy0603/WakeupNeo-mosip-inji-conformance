"""Configure and smoke-test real local PostgreSQL-backed course issuance.

This smoke result is separate from official OpenID conformance evidence.
Passwords/tokens and holder private keys are never written to the result.
"""
import argparse
import base64
import hashlib
import json
import time
import uuid
import warnings
from pathlib import Path
import requests
from cryptography import x509
from cryptography.utils import CryptographyDeprecationWarning
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, utils

ROOT = Path(__file__).resolve().parents[1]
ISSUER = 'https://host.docker.internal:8446'
CONFIG_ID = 'course-completion-sdjwt'
VCT = 'urn:inji:development:course-completion:1'


def b64(value):
    return base64.urlsafe_b64encode(value).decode().rstrip('=')


def decode(value):
    return base64.urlsafe_b64decode(value + '=' * (-len(value) % 4))


def public_jwk(key):
    numbers = key.public_key().public_numbers()
    return {'kty': 'EC', 'crv': 'P-256', 'x': b64(numbers.x.to_bytes(32, 'big')),
            'y': b64(numbers.y.to_bytes(32, 'big'))}


def signed_jwt(key, header, claims):
    message = '.'.join(b64(json.dumps(part, separators=(',', ':')).encode()) for part in [header, claims])
    r, s = utils.decode_dss_signature(key.sign(message.encode(), ec.ECDSA(hashes.SHA256())))
    return message + '.' + b64(r.to_bytes(32, 'big') + s.to_bytes(32, 'big'))


def dpop_proof(key, url, token=None, overrides=None):
    claims = {'jti': uuid.uuid4().hex, 'htm': 'POST', 'htu': url, 'iat': int(time.time())}
    if token:
        claims['ath'] = b64(hashlib.sha256(token.encode('ascii')).digest())
    if overrides:
        claims.update(overrides)
    return signed_jwt(key, {'typ': 'dpop+jwt', 'alg': 'ES256', 'jwk': public_jwk(key)}, claims)


def configure(session, holder_binding=False):
    template = '''{"iss":"$iss","vct":"$vct",
      "iat":$issued_at,"exp":$expires_at,
      "learner_name":"$_esc.java($learner_name)",
      "course_id":"$_esc.java($course_id)",
      "course_name":"$_esc.java($course_name)",
      "completed_on":"$_esc.java($completed_on)"}'''
    if holder_binding:
        template = template.replace('"vct":"$vct",', '"vct":"$vct","cnf":$cnf,')
    config = {'credentialConfigKeyId': CONFIG_ID, 'credentialFormat': 'dc+sd-jwt',
        'sdJwtVct': VCT, 'signatureAlgo': 'ES256',
        'keyManagerAppId': 'CERTIFY_VC_SIGN_EC_R1', 'keyManagerRefId': 'EC_SECP256R1_SIGN',
        'sdClaim': '$.learner_name,$.course_name,$.completed_on',
        'metaDataDisplay': [{'name': 'Development Course Completion', 'locale': 'en',
            'logo': {'uri': ISSUER + '/course-logo.svg', 'alt_text': 'Development course'},
            'text_color': '#ffffff', 'background_color': '#15324f',
            'background_image': {'uri': ISSUER + '/course-logo.svg'}}],
        'displayOrder': ['learner_name', 'course_id', 'course_name', 'completed_on'],
        'sdJwtClaims': {name: {'display': [{'name': label, 'locale': 'en'}]} for name, label in
            [('learner_name', 'Learner'), ('course_id', 'Course identifier'),
             ('course_name', 'Course name'), ('completed_on', 'Completion date')]},
        'scope': 'course_completion', 'vcTemplate': base64.b64encode(template.encode()).decode()}
    endpoint = ISSUER + '/v1/certify/credential-configurations'
    current = session.get(endpoint + '/' + CONFIG_ID, timeout=15)
    response = (session.put(endpoint + '/' + CONFIG_ID, json=config, timeout=30)
                if current.ok and not current.json().get('errors')
                else session.post(endpoint, json=config, timeout=30))
    if not response.ok or response.json().get('errors'):
        raise RuntimeError(f'Configuration rejected: {response.status_code} {response.text[:1000]}')
    return response.json()


def smoke(session, values, request_extension=False, dpop=False, require_cnf_jwk=False, signed_metadata=False, credential_errors=False, positive_serial=False):
    metadata = session.get(ISSUER + '/.well-known/openid-credential-issuer', headers={'Accept': 'application/json'}, timeout=15)
    metadata.raise_for_status()
    metadata = metadata.json()
    assert metadata['credential_issuer'] == ISSUER
    supported = metadata['credential_configurations_supported'][CONFIG_ID]
    assert supported['format'] == 'dc+sd-jwt' and supported['vct'] == VCT
    token_url = ISSUER + '/auth/realms/course/protocol/openid-connect/token'
    dpop_key = ec.generate_private_key(ec.SECP256R1()) if dpop else None
    token_response = session.post(token_url,
        headers={'DPoP': dpop_proof(dpop_key, token_url)} if dpop else {},
        data={'grant_type': 'password', 'client_id': 'course-wallet', 'scope': 'course_completion',
              'username': values['ISSUER_LOGIN_USERNAME'], 'password': values['ISSUER_LOGIN_PASSWORD']}, timeout=20)
    token_response.raise_for_status()
    token_data = token_response.json()
    token = token_data['access_token']
    if dpop:
        assert token_data['token_type'].lower() == 'dpop'
        thumbprint = b64(hashlib.sha256(json.dumps(public_jwk(dpop_key), sort_keys=True,
                            separators=(',', ':')).encode()).digest())
        assert json.loads(decode(token.split('.')[1]))['cnf']['jkt'] == thumbprint
    nonce_response = session.post(metadata['nonce_endpoint'], timeout=15)
    nonce_response.raise_for_status()
    nonce = nonce_response.json()['c_nonce']
    holder = ec.generate_private_key(ec.SECP256R1())
    jwk = public_jwk(holder)
    header = {'alg': 'ES256', 'typ': 'openid4vci-proof+jwt', 'jwk': jwk}
    claims = {'iss': 'course-wallet', 'aud': ISSUER, 'iat': int(time.time()), 'nonce': nonce}
    proof = signed_jwt(holder, header, claims)
    body = {'credential_configuration_id': CONFIG_ID, 'proofs': {'jwt': [proof]}}
    if request_extension:
        body['development_extension_check'] = {'ignored_extension': True}
    headers = {'Authorization': ('DPoP ' if dpop else 'Bearer ') + token}
    if dpop:
        headers['DPoP'] = dpop_proof(dpop_key, metadata['credential_endpoint'], token)
    response = session.post(metadata['credential_endpoint'], headers=headers,
        json=body, timeout=60)
    if not response.ok:
        raise RuntimeError(f'Issuance rejected: {response.status_code} {response.text[:1000]}')
    if dpop:
        replay = session.post(metadata['credential_endpoint'], headers=headers, json=body, timeout=20)
        assert replay.status_code == 401 and replay.json()['error'] == 'invalid_dpop_proof'
        downgrade = session.post(metadata['credential_endpoint'], headers={'Authorization': 'Bearer ' + token},
                                 json=body, timeout=20)
        assert downgrade.status_code == 401
        invalid_cases = {'wrong_method': {'htm': 'GET'},
                         'wrong_resource': {'htu': metadata['credential_endpoint'] + '/other'},
                         'wrong_token_hash': {'ath': 'invalid'},
                         'expired_proof': {'iat': int(time.time()) - 360},
                         'future_proof': {'iat': int(time.time()) + 60}}
        for name, overrides in invalid_cases.items():
            rejected = session.post(metadata['credential_endpoint'],
                headers={'Authorization': 'DPoP ' + token,
                         'DPoP': dpop_proof(dpop_key, metadata['credential_endpoint'], token, overrides)},
                json=body, timeout=20)
            assert rejected.status_code == 401 and rejected.json()['error'] == 'invalid_dpop_proof', name
        for name, proof_value in [('missing_proof', None), ('wrong_key', dpop_proof(
                ec.generate_private_key(ec.SECP256R1()), metadata['credential_endpoint'], token))]:
            negative_headers = {'Authorization': 'DPoP ' + token}
            if proof_value:
                negative_headers['DPoP'] = proof_value
            rejected = session.post(metadata['credential_endpoint'], headers=negative_headers, json=body, timeout=20)
            assert rejected.status_code == 401 and rejected.json()['error'] == 'invalid_dpop_proof', name
    credential = response.json()['credentials'][0]['credential']
    jwt, *disclosures = credential.split('~')
    encoded_header, encoded_claims, signature = jwt.split('.')
    jwt_header = json.loads(decode(encoded_header))
    jwt_claims = json.loads(decode(encoded_claims))
    certificate = x509.load_der_x509_certificate(base64.b64decode(jwt_header['x5c'][0]))
    if positive_serial:
        with warnings.catch_warnings():
            warnings.simplefilter('error', CryptographyDeprecationWarning)
            chain = [x509.load_der_x509_certificate(base64.b64decode(cert)) for cert in jwt_header['x5c']]
        assert all(0 < cert.serial_number and cert.serial_number.bit_length() <= 159 for cert in chain)
    raw_sig = decode(signature)
    certificate.public_key().verify(utils.encode_dss_signature(
        int.from_bytes(raw_sig[:32], 'big'), int.from_bytes(raw_sig[32:], 'big')),
        (encoded_header + '.' + encoded_claims).encode(), ec.ECDSA(hashes.SHA256()))
    disclosed = {}
    for disclosure in filter(None, disclosures):
        assert b64(hashlib.sha256(disclosure.encode()).digest()) in jwt_claims['_sd']
        _, name, value = json.loads(decode(disclosure))
        disclosed[name] = value
    assert jwt_claims['iss'] == ISSUER and jwt_claims['vct'] == VCT
    assert jwt_claims['course_id'] == 'COURSE-DEV-001', repr(jwt_claims['course_id'])
    assert disclosed['learner_name'] == 'Development Learner'
    assert jwt_claims['exp'] > jwt_claims['iat']
    if require_cnf_jwk or 'jwk' in jwt_claims['cnf']:
        bound_key = jwt_claims['cnf']['jwk']
        assert 'd' not in bound_key and bound_key['kty'] != 'oct'
        binding_format = 'cnf.jwk'
    else:
        # Retain a separate smoke check for the stock release's legacy binding.
        assert jwt_claims['cnf']['kid'].startswith('did:jwk:')
        bound_key = json.loads(decode(jwt_claims['cnf']['kid'].removeprefix('did:jwk:')))
        binding_format = 'cnf.kid'
    assert all(bound_key[field] == jwk[field] for field in jwk)
    if credential_errors:
        assert dpop, 'Error-response validation requires the tested bound-token mode'
        cases = [({'credential_configuration_id': 'nonexistent-development-config'}, 'unknown_credential_configuration'),
                 ({'credential_identifier': 'unissued-development-identifier'}, 'unknown_credential_identifier'),
                 ({'credential_configuration_id': CONFIG_ID, 'credential_identifier': 'ambiguous'}, 'invalid_credential_request'),
                 ({}, 'invalid_credential_request'),
                 ({'credential_configuration_id': ' '}, 'invalid_credential_request')]
        for selector, expected in cases:
            fresh_nonce = session.post(metadata['nonce_endpoint'], timeout=15)
            fresh_nonce.raise_for_status()
            fresh_proof = signed_jwt(holder, header, {**claims, 'nonce': fresh_nonce.json()['c_nonce'], 'iat': int(time.time())})
            rejected = session.post(metadata['credential_endpoint'],
                headers={'Authorization': 'DPoP ' + token,
                         'DPoP': dpop_proof(dpop_key, metadata['credential_endpoint'], token)},
                json={**selector, 'proofs': {'jwt': [fresh_proof]}}, timeout=20)
            assert rejected.status_code == 400 and rejected.json()['error'] == expected, expected
    if signed_metadata:
        signed_response = session.get(ISSUER + '/.well-known/openid-credential-issuer',
                                      headers={'Accept': 'application/jwt'}, timeout=20)
        signed_response.raise_for_status()
        assert signed_response.headers['Content-Type'].split(';')[0] == 'application/jwt'
        meta_header, meta_payload, meta_signature = signed_response.text.split('.')
        metadata_header = json.loads(decode(meta_header))
        assert metadata_header['typ'] == 'openidvci-issuer-metadata+jwt' and metadata_header['alg'] == 'ES256'
        # Both are signed by the configured real native issuer key, not a harness fallback.
        assert metadata_header['x5c'][0] == jwt_header['x5c'][0]
        raw = decode(meta_signature)
        certificate.public_key().verify(utils.encode_dss_signature(
            int.from_bytes(raw[:32], 'big'), int.from_bytes(raw[32:], 'big')),
            (meta_header + '.' + meta_payload).encode(), ec.ECDSA(hashes.SHA256()))
        signed_claims = json.loads(decode(meta_payload))
        assert signed_claims['sub'] == signed_claims['iss'] == ISSUER
        assert 0 <= int(time.time()) - signed_claims['iat'] <= 30
        assert signed_claims['exp'] > int(time.time())
        assert {key: value for key, value in signed_claims.items() if key not in {'sub', 'iss', 'iat', 'exp'}} == metadata
    return {'kind': 'local_issuance_smoke', 'status': 'PASSED', 'credential_format': 'dc+sd-jwt',
            'credential_configuration_id': CONFIG_ID, 'vct': VCT,
            'signature_verified': True, 'disclosure_hashes_verified': True,
            'holder_binding_verified': True, 'synthetic_database_record_verified': True,
            'holder_binding_format': binding_format,
            'issuer_metadata_signature_verified': signed_metadata,
            'credential_selector_and_error_responses_verified': credential_errors,
            'certificate_serials_positive_verified': positive_serial,
            'unrecognized_request_parameter_checked': request_extension,
            'dpop_binding_and_replay_verified': dpop,
            'dpop_negative_checks': list(invalid_cases) + ['missing_proof', 'wrong_key', 'replay', 'bearer_downgrade'] if dpop else [],
            'official_conformance_result': False, 'credential_sha256': hashlib.sha256(credential.encode()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--configure-only', action='store_true')
    parser.add_argument('--request-extension', action='store_true',
                        help='Verify native support for ignoring an additional credential-request parameter')
    parser.add_argument('--dpop', action='store_true', help='Verify native DPoP-bound issuance and replay/downgrade rejection')
    parser.add_argument('--require-cnf-jwk', action='store_true', help='Require the Final profile public JWK holder binding')
    parser.add_argument('--signed-metadata', action='store_true', help='Verify native metadata signature against the real credential-signing certificate')
    parser.add_argument('--credential-errors', action='store_true', help='Verify exact native error codes and reject ambiguous/empty selectors')
    parser.add_argument('--positive-serial', action='store_true', help='Require positive bounded serials throughout the actual signing certificate chain')
    parser.add_argument('--insecure', action='store_true')
    parser.add_argument('--resolve-local', action='store_true',
                        help='Resolve host.docker.internal to loopback inside this process (WSL)')
    parser.add_argument('--output', type=Path, default=ROOT / 'reports/course-issuance-smoke.json')
    args = parser.parse_args()
    if args.resolve_local:
        import os
        os.environ['CONFORMANCE_RESOLVE_LOCAL'] = 'true'
    from local_network import configure as configure_network
    configure_network()
    values = dict(line.split('=', 1) for line in (ROOT / 'docker/.env').read_text().splitlines()
                  if '=' in line and not line.startswith('#'))
    session = requests.Session()
    session.verify = not args.insecure
    from deployment_provenance import holder_binding_template_enabled
    configure(session, holder_binding=args.require_cnf_jwk or holder_binding_template_enabled())
    if not args.configure_only:
        result = smoke(session, values, args.request_extension, args.dpop, args.require_cnf_jwk, args.signed_metadata, args.credential_errors, args.positive_serial)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
