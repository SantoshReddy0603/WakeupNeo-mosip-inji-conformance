# API reference

This harness uses the official suite and product APIs; it does not add a public application server. This reference covers the routes used by the pinned implementation. Examples are schemas or commands, not fabricated test evidence.

## Addresses and authentication

| Service | Local address | Authentication |
|---|---|---|
| Official suite | https://localhost:8443 | Local development mode needs no API token. For an authenticated deployment, OIDF_TOKEN supplies Authorization: Bearer. |
| Certify issuer | https://host.docker.internal:8446 | Issuance uses the real Keycloak access token and the configured sender constraint. |
| Keycloak | Issuer origin + /auth/realms/course | Official clients use private_key_jwt, PKCE S256 and DPoP in the selected plan. |
| Verify | https://localhost:8445/v1/verify | The UI session uses its native HttpOnly transaction cookie. It is not a JSON transactionId authentication substitute. |
| MinIO | http://localhost:9000 | AWS Signature V4 with generated local credentials. Console: port 9001. |

Use CONFORMANCE_RESOLVE_LOCAL=true for the host runner/browser. Containers resolve the same advertised hostname through the ingress network alias. Development self-signed TLS requires the explicit local --insecure flag; use a trusted CA elsewhere. Never place tokens, passwords or private JWKs in committed examples.

## Official suite REST API

Implementation: runner/oidf_client.py and the licensed, hash-pinned runner/vendor/oidf/conformance.py. JSON requests use Content-Type: application/json unless noted.

| Method and route | Input | Output and use |
|---|---|---|
| GET /api/runner/available | None | JSON array of available modules, used for readiness. |
| POST /api/plan | Query planName and JSON-encoded variant; JSON configuration body | HTTP 201, JSON plan identity. Render the issuer/verifier template before creation. |
| GET /api/plan/{planId} | Returned plan ID | JSON plan configuration and modules; the runner rejects duplicate/missing module-variant pairs. |
| POST /api/runner | Query test, plan and JSON-encoded variant | HTTP 201, JSON instance identity used for subsequent calls. |
| POST /api/runner/{testId} | Configured instance ID | HTTP 200 starts the real module. |
| GET /api/info/{testId} | Instance ID | JSON status/result and instance data. Terminal status is required before reporting completion. |
| GET /api/runner/{testId} | Instance ID | Exposed URLs and interaction data, used for a WAITING state. |
| GET /api/log/{testId} | Instance ID | Official JSON log entries retained unchanged. |
| GET /api/log/{testId}/images | Instance ID | Image/placeholder entries. Missing img with an upload ID requests genuine evidence. |
| POST /api/log/{testId}/images/{placeholder} | Content-Type: text/plain; data:image/png;base64,... or JPEG data URL | Filled image record. The client verifies returned bytes; upload does not approve REVIEW. |
| GET /api/plan/export/{planId} | Plan ID; Accept: application/zip | Original ZIP bytes. The runner verifies nonempty content and ZIP CRCs. |

The harness uses official conformance.py methods rather than invoking run-test-plan.py as a subprocess. No review-disposition write API is implemented. Polling deadlines create a TIMEOUT failure, never a PASS.

Example read-only inspection, replacing the placeholder with an actual returned ID:

```bash
curl --cacert docker/nginx/certs/server.crt \
  https://localhost:8443/api/info/ACTUAL_TEST_ID
```

For authenticated suites, supply OIDF_TOKEN securely in the environment. Do not echo it in recordings. The [official API documentation](https://www.certification.openid.net/api-document.html) and pinned source remain authoritative.

## Certify and OAuth

Issuer discovery: GET /.well-known/openid-credential-issuer with Accept: application/json. The returned credential_issuer, credential_configurations_supported, nonce_endpoint and credential_endpoint drive issuance. The optional signed response uses Accept: application/jwt and must pass the native metadata/signing checks.

OAuth discovery: GET /.well-known/oauth-authorization-server/auth/realms/course routes to Keycloak's genuine metadata. The authorization endpoint drives the browser callback. The token endpoint is /auth/realms/course/protocol/openid-connect/token, with application/x-www-form-urlencoded requests.

The official plan uses two registered confidential wallet clients, private_key_jwt assertions and DPoP. The standalone development smoke flow uses the separate public course-wallet client and its generated synthetic learner. Its password grant is local smoke setup, not the official plan's authorization flow.

POST to the discovered nonce_endpoint returns a c_nonce. POST to the discovered credential_endpoint sends a real holder proof and access token. DPoP requests also carry the DPoP header. The proof contains the issuer audience, real nonce, iat and holder public JWK. The selected request shape is:

```json
{
  "credential_configuration_id": "course-completion-sdjwt",
  "proofs": {"jwt": ["<real-signed-holder-proof>"]}
}
```

A successful response contains credentials, whose entries include credential. The smoke check verifies the returned signature/disclosures and configured synthetic values. Failures preserve the actual HTTP status and error response. Strict security/error checks apply only to the build that implements them; stock and patched runs remain distinct.

The local configuration helper uses GET /v1/certify/credential-configurations/{id}, and POST/PUT /v1/certify/credential-configurations to create/update the real development template. Its JSON includes credentialConfigKeyId, credentialFormat=dc+sd-jwt, sdJwtVct, ES256 settings, scope, display data and base64 vcTemplate. See runner/course_issuer.py for the complete actual body. Stock templates omit the patch-only cnf context. Production administrative access policies must be configured for the deployed product.

## Verify and genuine browser evidence

The selected native request body is config/verify-request.final.json. It contains clientId, a DCQL credentials query (format dc+sd-jwt and the PID vct_values), and responseCodeValidationRequired. It is separate from the course credential issued by Certify.

| Route under /v1/verify | Purpose |
|---|---|
| POST /v2/vp-request | API handoff creates a native request. The adapter consumes authorizationDetails and requestId, or the native requestUri response. |
| POST /v2/vp-session-request | The unmodified UI/SDK creates the QR transaction. HTTP 201 includes authorizationDetails, requestId and transactionId. |
| POST /v2/vp-submission/direct-post | The official wallet posts the protocol response to the native verifier; the harness does not synthesize it. |
| POST /vp-session-results | The SDK retrieves native verification data using its transaction cookie. The observed request must retain skipStatusChecks=false. |

The actual UI captures and decodes the rendered QR, verifies state/request identity, observes the SDK response and correlates its transactionId. Screenshots and original SDK observations are retained, then submitted only to the requesting official placeholder. Unknown SDK versions fail closed until native URL construction is validated.

Example API request, using the supplied real configuration:

```bash
curl --cacert docker/nginx/certs/server.crt \
  -H 'Content-Type: application/json' \
  --data-binary @config/verify-request.final.json \
  https://localhost:8445/v1/verify/v2/vp-request
```

This creates a real transaction; its response is not conformance evidence by itself. For a complete run, use the harness so official plan IDs, callbacks and evidence remain correlated.

## Storage, reports and failures

MinIO uses the automationtests bucket by default. Native and consolidated artifacts use openid-conformance/{runId}/; retained validation uses a distinct validation namespace. Every uploaded object is downloaded and byte-compared. No private key or generated password is an intended report artifact.

Conformance JSON schema version 2 contains run_id, runs, module results and consolidated gates. deployment identifies the observed managed issuer image/version; unknown external deployments remain unidentified. Native TestNG and Extent consume the matching run identity, reject stale reports and add explicit gate assertions.

CLI exits: 0 means the selected gate/report lifecycle passed; 1 indicates a failed gate or reporter; setup/operational errors may return other nonzero statuses. Inspect the summary and lifecycle manifest instead of interpreting every nonzero exit as an expected REVIEW outcome. The official verifier plan remains oid4vp-1final-verifier-test-plan.

