"""Drive the suite wallet with an authorization request produced by Inji Verify.

The selected upstream SDK determines request construction. Test signing keys
belong to the suite configuration, not a replacement verifier or protocol proxy."""
import base64
import json
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit, urlencode
import requests
from release_versions import verifier_sdk_version


def generate_signing_jwk(include_certificate=False):
    """Generate a development issuer key for the official suite credential configuration."""
    from cryptography.hazmat.primitives.asymmetric import ec
    key = ec.generate_private_key(ec.SECP256R1())
    numbers = key.private_numbers()
    def encode(value):
        return base64.urlsafe_b64encode(value.to_bytes(32, 'big')).decode().rstrip('=')
    jwk = {'kty': 'EC', 'crv': 'P-256', 'x': encode(numbers.public_numbers.x),
            'y': encode(numbers.public_numbers.y), 'd': encode(numbers.private_value),
            'kid': 'suite-credential-signing-key'}
    if include_certificate:
        # Official suite supports x5c in credential.signing_jwk and signs with this real key.
        from datetime import datetime, timedelta, timezone
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        now = datetime.now(timezone.utc)
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'OIDF local test issuer')])
        cert = (x509.CertificateBuilder().subject_name(name).issuer_name(name)
            .public_key(key.public_key()).serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(minutes=5)).not_valid_after(now + timedelta(days=1))
            .sign(key, hashes.SHA256()))
        jwk['x5c'] = [base64.b64encode(cert.public_bytes(serialization.Encoding.DER)).decode()]
    return jwk


class PostForm(HTMLParser):
    def __init__(self):
        super().__init__()
        self.forms = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        """Collect form fields needed to submit the suite-generated browser response unchanged."""
        attrs = dict(attrs)
        if tag == 'form':
            self.current = {'action': attrs.get('action', ''),
                            'method': attrs.get('method', 'get').lower(), 'fields': {}}
            self.forms.append(self.current)
        if tag == 'input' and self.current is not None and attrs.get('name'):
            self.current['fields'][attrs['name']] = attrs.get('value', '')

    def handle_endtag(self, tag):
        """End field collection at the matching form boundary."""
        if tag == 'form':
            self.current = None


class OID4VPHandoffClient:
    def __init__(self, oidf_base_url, verify_url, request_body, verify_ssl=True, sdk_version=None):
        sdk_version = sdk_version or verifier_sdk_version()
        if sdk_version not in {'0.17.0', '1.0.0-alpha.1'}:
            raise ValueError('Unsupported Verify SDK version; validate its URL construction first')
        self.sdk_version = sdk_version
        self.oidf_base_url = oidf_base_url.rstrip('/')
        self.verify_url = verify_url.rstrip('/')
        self.request_body = request_body
        self.session = requests.Session()
        self.session.verify = verify_ssl

    def execute_presentation_handoff(self, info, max_wait_sec=30):
        """Use native Verify request data and the selected SDK rules to drive the suite wallet."""
        urls = info.get('urls', {})
        endpoint = urls.get('authorization_endpoint') or urls.get('authorizationEndpoint')
        if not endpoint:
            raise ValueError('Suite WAITING response has no wallet authorization endpoint')
        # The suite's advertised origin can be container-only. Route its own endpoint
        # through the configured API origin; keep all verifier parameters unchanged.
        parts = urlsplit(endpoint)
        endpoint = self.oidf_base_url + parts.path + ('?' + parts.query if parts.query else '')
        timeout = min(30, max_wait_sec)
        request_path = '/v2/vp-request' if self.sdk_version == '1.0.0-alpha.1' else '/vp-request'
        response = self.session.post(self.verify_url + request_path,
                                     json=self.request_body, timeout=timeout)
        response.raise_for_status()
        request = response.json()
        details = request.get('authorizationDetails')
        if details:
            names = {'responseType': 'response_type', 'responseMode': 'response_mode',
                     'clientId': 'client_id', 'responseUri': 'response_uri',
                     'presentationDefinition': 'presentation_definition',
                     'presentationDefinitionUri': 'presentation_definition_uri',
                     'clientMetadata': 'client_metadata', 'dcqlQuery': 'dcql_query'}
            params = {names.get(k, k): json.dumps(v) if isinstance(v, (dict, list)) else v
                      for k, v in details.items()
                      if k not in {'issuedAt', 'acceptVPWithoutHolderProof'} and v is not None}
            if self.sdk_version == '1.0.0-alpha.1':
                # The SDK forwards these protocol fields; backend bookkeeping is not a query parameter.
                params = {k: v for k, v in params.items() if k in {
                    'response_type', 'response_mode', 'nonce', 'response_uri',
                    'dcql_query', 'client_metadata', 'client_id'}}
            if not request.get('requestId'):
                raise ValueError('Verify response has no requestId')
            params['state'] = request['requestId']
            # Reproduce the selected upstream SDK, never translate backend queries.
            # Source: inji/inji-verify tag v1.0.0-alpha.1, OpenID4VPVerification.tsx.
            if 'client_metadata' not in params:
                formats = {'ldp_vp': {'proof_type': ['Ed25519Signature2018', 'Ed25519Signature2020', 'RsaSignature2018']},
                           'vc+sd-jwt': {'sd-jwt_alg_values': ['RS256', 'ES256', 'ES256K', 'EdDSA'],
                                         'kb-jwt_alg_values': ['RS256', 'ES256', 'ES256K', 'EdDSA']}}
                if self.sdk_version == '0.17.0':
                    params['client_metadata'] = json.dumps({'client_name': self.request_body['clientId'], 'vp_formats': formats})
                else:
                    params['client_id'] = self.request_body['clientId']
                    if params['client_id'].startswith(('redirect_uri:', 'decentralized_identifier:')):
                        formats['dc+sd-jwt'] = formats['vc+sd-jwt'].copy()
                        params['client_metadata'] = json.dumps({'vp_formats_supported': formats})
        elif request.get('requestUri'):
            params = {'client_id': self.request_body['clientId'], 'request_uri': request['requestUri']}
        else:
            raise ValueError('Verify response has no authorizationDetails or requestUri')
        # These values are emitted by the verifier; preserve even invalid values for conformance.
        wallet = self.session.get(endpoint, params=params, timeout=timeout, allow_redirects=False)
        # A protocol rejection is judged by the suite's terminal result.
        evidence = {'request_id': request.get('requestId'), 'transaction_id': request.get('transactionId'),
                    'wallet_http_status': wallet.status_code, 'evidence_uploaded': False}
        if wallet.is_redirect:
            evidence['redirect'] = wallet.headers.get('Location')
            return evidence
        parser = PostForm()
        parser.feed(wallet.text)
        forms = [f for f in parser.forms if f['method'] == 'post' and
                 ('vp_token' in f['fields'] or 'error' in f['fields'])]
        # The final suite sends direct_post itself and returns resultCaptured HTML.
        # Older suites may instead return a form for the wallet browser to submit.
        if not forms:
            if request.get('transactionId'):
                result = self.session.get(self.verify_url + '/vp-result/' + request['transactionId'], timeout=timeout)
                evidence['verification_http_status'] = result.status_code
                try:
                    evidence['verification_result'] = result.json()
                except ValueError:
                    evidence['verification_result'] = result.text[:2000]
            return evidence
        if len(forms) != 1:
            raise ValueError('Suite returned multiple direct_post forms')
        form = forms[0]
        action = urljoin(wallet.url, form['action'])
        # Deliver only to the verifier-supplied response_uri, never an arbitrary HTML target.
        expected = params.get('response_uri')
        if expected and action != expected:
            raise ValueError('Suite form action differs from verifier response_uri')
        if not expected and urlsplit(action).netloc != urlsplit(self.verify_url).netloc:
            raise ValueError('Cannot validate wallet submission destination for request_uri flow')
        submission = self.session.post(action, data=form['fields'], timeout=timeout, allow_redirects=False)
        # A 4xx may be an expected negative test outcome: retain it for the suite to judge.
        if submission.status_code >= 500:
            submission.raise_for_status()
        evidence['submission_http_status'] = submission.status_code
        if request.get('transactionId'):
            result = self.session.get(self.verify_url + '/vp-result/' + request['transactionId'], timeout=timeout)
            evidence['verification_http_status'] = result.status_code
            try:
                evidence['verification_result'] = result.json()
            except ValueError:
                evidence['verification_result'] = result.text[:2000]
        return evidence
