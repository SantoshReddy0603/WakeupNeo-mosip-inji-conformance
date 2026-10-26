# Stock Certify interruption triage

Stock run `019bf015dcef47029010faa06a2cf788`, issuer export `plan-UYoPyoeGriNRN-export.zip`: 2 PASSED, 10
INTERRUPTED, 3 SKIPPED. Diagnostic, patched build run `d39d9f65b0f04db79eb3d25501c9f26c`, issuer export
`plan-yfOPDtRoNo2xZ-export.zip`: 12 PASSED, 3 SKIPPED. The preserved exports were read directly; their JSON
testInfo results and event logs support the comparison below. Original exports and signatures remain unchanged
in private evidence.

All ten interruptions in the original DPoP-selected run classify as PRODUCT_GAP; this classification is scoped
to that path, with the later alternative-variant observations below. None establishes a missing plan
parameter, unfinished WAITING handoff, poll timeout, TLS error or unreachable endpoint. No stock patch,
configuration workaround or single-test before/after fix was applied. Patch attribution identifies the
implemented behavior and the successful combined patched build; isolated patch-ablation causality is **not
verified**. Later checks hidden behind an earlier stock failure are not claimed to have executed on stock. The
diagnostic also includes the native keymanager positive-serial fix described in docker/RELEASES.md; the table
is not a claim that each listed patch alone reproduces the complete diagnostic PASS.

Test names below share prefix `oid4vci-1_0-issuer-`; patch paths share `docker/native-certify/`.

| Test name | Status | Class | Evidence | Patch that fixes it | Action taken |
|---|---|---|---|---|---|
| `metadata-test-signed` | Stock INTERRUPTED / diagnostic PASSED | PRODUCT_GAP | `B61Vqr31wC8p2Rk`: 200 OK, empty body | `signed-metadata.patch` | Retain stock failure |
| `happy-flow` | Stock INTERRUPTED / diagnostic PASSED | PRODUCT_GAP | `iqk1VhClUfgzhkl`: 500 INTERNAL_SERVER_ERROR, unknown_error: unrecognized extension field | `extensions.patch`, `dpop.patch`, `holder-binding.patch` | Retain stock failure |
| `happy-flow-additional-requests` | Stock INTERRUPTED / diagnostic PASSED | PRODUCT_GAP | `0LUs3j7U97cH1vZ`: 401 UNAUTHORIZED, {"error":"invalid_token","error_description":"invalid_token"} | `dpop.patch`, `extensions.patch`, `holder-binding.patch` | Retain stock failure |
| `happy-flow-multiple-clients` | Stock INTERRUPTED / diagnostic PASSED | PRODUCT_GAP | `zoskf1s65ZJqWV6`: 401 UNAUTHORIZED, {"error":"invalid_token","error_description":"invalid_token"} | `dpop.patch`, `extensions.patch`, `holder-binding.patch` | Retain stock failure |
| `happy-flow-skip-notification` | Stock INTERRUPTED / diagnostic PASSED | PRODUCT_GAP | `H3hsOeWhUSaZn5x`: 401 UNAUTHORIZED, {"error":"invalid_token","error_description":"invalid_token"} | `dpop.patch`, `extensions.patch`, `holder-binding.patch` | Retain stock failure |
| `fail-invalid-nonce` | Stock INTERRUPTED / diagnostic PASSED | PRODUCT_GAP | `QoyggTSnn6w5sAo`: 401 UNAUTHORIZED, {"error":"invalid_token","error_description":"invalid_token"} | `dpop.patch` | Retain stock failure |
| `fail-invalid-jwt-proof-signature` | Stock INTERRUPTED / diagnostic PASSED | PRODUCT_GAP | `s8WWjo8wtU8MEpq`: 401 UNAUTHORIZED, {"error":"invalid_token","error_description":"invalid_token"} | `dpop.patch` | Retain stock failure |
| `fail-unknown-credential-configuration` | Stock INTERRUPTED / diagnostic PASSED | PRODUCT_GAP | `dJqxkp28p6TKPud`: 401 UNAUTHORIZED, {"error":"invalid_token","error_description":"invalid_token"} | `dpop.patch`, `credential-errors.patch` | Retain stock failure |
| `fail-unknown-credential-identifier` | Stock INTERRUPTED / diagnostic PASSED | PRODUCT_GAP | `wZUaQwM0lQnFZDW`: 500 INTERNAL_SERVER_ERROR, unknown_error: unrecognized credential_identifier | `credential-errors.patch` | Retain stock failure |
| `fail-on-access-token-in-query` | Stock INTERRUPTED / diagnostic PASSED | PRODUCT_GAP | `O2E2YHPFYOnxRY4`: 401 UNAUTHORIZED, {"error":"invalid_token","error_description":"invalid_token"} | `dpop.patch`, `extensions.patch`, `holder-binding.patch` | Retain stock failure |

## Per-test official log excerpts

### `oid4vci-1_0-issuer-metadata-test-signed`

- Stock export member: `plan-UYoPyoeGriNRN-export.zip / test-log-oid4vci-1_0-issuer-metadata-test-signed-B61Vqr31wC8p2Rk.json`.
- Matched patched PASSED member: `plan-yfOPDtRoNo2xZ-export.zip / test-log-oid4vci-1_0-issuer-metadata-test-signed-p14c98NHyeP27Wk.json`.
- Last successful logged step: `VCIGetDynamicCredentialIssuerMetadata` — Fetched credential issuer metadata from https://host.docker.internal:8446/.well-known/openid-credential-issuer
- Last suite-to-Certify request: `GET https://host.docker.internal:8446/.well-known/openid-credential-issuer`.
- Last response: `200 OK`; content type `None`; body `""` (empty).
- Exact FAILURE (`EnsureContentTypeApplicationJwt`): Couldn't find content-type header in endpoint_response
- Exact FAILURE (`VCIDecodeSignedCredentialIssuerMetadata`): If present, a string is expected for credential_issuer_metadata_endpoint_response body but JsonNull was found
- Exact INTERRUPTED (`oid4vci-1_0-issuer-metadata-test-signed`): Test was interrupted before it could
  complete. The failure 'VCIDecodeSignedCredentialIssuerMetadata: If present, a string is expected for
  credential_issuer_metadata_endpoint_response body but JsonNull was found' means the test cannot continue.
- Classification evidence: Signed metadata request returns an empty HTTP 200 body without application/jwt.
- Patch behavior: `docker/native-certify/signed-metadata.patch`. No production behavior is added to the harness.

### `oid4vci-1_0-issuer-happy-flow`

- Stock export member: `plan-UYoPyoeGriNRN-export.zip / test-log-oid4vci-1_0-issuer-happy-flow-iqk1VhClUfgzhkl.json`.
- Matched patched PASSED member: `plan-yfOPDtRoNo2xZ-export.zip / test-log-oid4vci-1_0-issuer-happy-flow-ytKNgqReHaAvVVl.json`.
- Last successful logged step: `CallProtectedResourceAllowingDpopNonceError` — Got a response from the resource endpoint
- Last suite-to-Certify request: `POST https://host.docker.internal:8446/v1/certify/issuance/credential`; authorization scheme `DPoP` (token omitted).
- Last response: `500 INTERNAL_SERVER_ERROR`; content type `application/json`; body `{"error":"unknown_error","error_description":"JSON parse error: Unrecognized field \"4FkbIGgoNblt1P2t\" (class io.mosip.certify.core.dto.CredentialRequest), not marked as ignorable"}`.
- Exact FAILURE (`EnsureHttpStatusCodeIsAnyOf`): resource endpoint returned an unexpected http status
- Exact INTERRUPTED (`oid4vci-1_0-issuer-happy-flow`): Test was interrupted before it could complete. The failure 'EnsureHttpStatusCodeIsAnyOf: resource endpoint returned an unexpected http status' means the test cannot continue.
- Classification evidence: Stock CredentialRequest rejects the suite extension field with HTTP 500; the diagnostic also adds DPoP and holder binding for later checks.
- Patch behavior: `docker/native-certify/extensions.patch`, `docker/native-certify/dpop.patch`, `docker/native-certify/holder-binding.patch`. No production behavior is added to the harness.

### `oid4vci-1_0-issuer-happy-flow-additional-requests`

- Stock export member: `plan-UYoPyoeGriNRN-export.zip / test-log-oid4vci-1_0-issuer-happy-flow-additional-requests-0LUs3j7U97cH1vZ.json`.
- Matched patched PASSED member: `plan-yfOPDtRoNo2xZ-export.zip / test-log-oid4vci-1_0-issuer-happy-flow-additional-requests-p0jZCTn5P3nGTnW.json`.
- Last successful logged step: `CallProtectedResourceAllowingDpopNonceError` — Got a response from the resource endpoint
- Last suite-to-Certify request: `POST https://host.docker.internal:8446/v1/certify/issuance/credential`; authorization scheme `DPoP` (token omitted).
- Last response: `401 UNAUTHORIZED`; content type `application/json`; body `{"error":"invalid_token","error_description":"invalid_token"}`.
- Exact FAILURE (`EnsureHttpStatusCodeIsAnyOf`): resource endpoint returned an unexpected http status
- Exact INTERRUPTED (`oid4vci-1_0-issuer-happy-flow-additional-requests`): Test was interrupted before it could complete. The failure 'EnsureHttpStatusCodeIsAnyOf: resource endpoint returned an unexpected http status' means the test cannot continue.
- Classification evidence: A DPoP-authenticated credential request receives HTTP 401 invalid_token; the stock access-token filter only accepts the Bearer scheme.
- Patch behavior: `docker/native-certify/dpop.patch`, `docker/native-certify/extensions.patch`, `docker/native-certify/holder-binding.patch`. No production behavior is added to the harness.

### `oid4vci-1_0-issuer-happy-flow-multiple-clients`

- Stock export member: `plan-UYoPyoeGriNRN-export.zip / test-log-oid4vci-1_0-issuer-happy-flow-multiple-clients-zoskf1s65ZJqWV6.json`.
- Matched patched PASSED member: `plan-yfOPDtRoNo2xZ-export.zip / test-log-oid4vci-1_0-issuer-happy-flow-multiple-clients-cT0Iz2glSfaBFgZ.json`.
- Last successful logged step: `CallProtectedResourceAllowingDpopNonceError` — Got a response from the resource endpoint
- Last suite-to-Certify request: `POST https://host.docker.internal:8446/v1/certify/issuance/credential`; authorization scheme `DPoP` (token omitted).
- Last response: `401 UNAUTHORIZED`; content type `application/json`; body `{"error":"invalid_token","error_description":"invalid_token"}`.
- Exact FAILURE (`EnsureHttpStatusCodeIsAnyOf`): resource endpoint returned an unexpected http status
- Exact INTERRUPTED (`oid4vci-1_0-issuer-happy-flow-multiple-clients`): Test was interrupted before it could complete. The failure 'EnsureHttpStatusCodeIsAnyOf: resource endpoint returned an unexpected http status' means the test cannot continue.
- Classification evidence: A DPoP-authenticated credential request receives HTTP 401 invalid_token; the stock access-token filter only accepts the Bearer scheme.
- Patch behavior: `docker/native-certify/dpop.patch`, `docker/native-certify/extensions.patch`, `docker/native-certify/holder-binding.patch`. No production behavior is added to the harness.

### `oid4vci-1_0-issuer-happy-flow-skip-notification`

- Stock export member: `plan-UYoPyoeGriNRN-export.zip / test-log-oid4vci-1_0-issuer-happy-flow-skip-notification-H3hsOeWhUSaZn5x.json`.
- Matched patched PASSED member: `plan-yfOPDtRoNo2xZ-export.zip / test-log-oid4vci-1_0-issuer-happy-flow-skip-notification-9oEVexRut8MldbU.json`.
- Last successful logged step: `CallProtectedResourceAllowingDpopNonceError` — Got a response from the resource endpoint
- Last suite-to-Certify request: `POST https://host.docker.internal:8446/v1/certify/issuance/credential`; authorization scheme `DPoP` (token omitted).
- Last response: `401 UNAUTHORIZED`; content type `application/json`; body `{"error":"invalid_token","error_description":"invalid_token"}`.
- Exact FAILURE (`EnsureHttpStatusCodeIsAnyOf`): resource endpoint returned an unexpected http status
- Exact INTERRUPTED (`oid4vci-1_0-issuer-happy-flow-skip-notification`): Test was interrupted before it could complete. The failure 'EnsureHttpStatusCodeIsAnyOf: resource endpoint returned an unexpected http status' means the test cannot continue.
- Classification evidence: A DPoP-authenticated credential request receives HTTP 401 invalid_token; the stock access-token filter only accepts the Bearer scheme.
- Patch behavior: `docker/native-certify/dpop.patch`, `docker/native-certify/extensions.patch`, `docker/native-certify/holder-binding.patch`. No production behavior is added to the harness.

### `oid4vci-1_0-issuer-fail-invalid-nonce`

- Stock export member: `plan-UYoPyoeGriNRN-export.zip / test-log-oid4vci-1_0-issuer-fail-invalid-nonce-QoyggTSnn6w5sAo.json`.
- Matched patched PASSED member: `plan-yfOPDtRoNo2xZ-export.zip / test-log-oid4vci-1_0-issuer-fail-invalid-nonce-21w36A9e1t3bzsQ.json`.
- Last successful logged step: `VCIEnsureCredentialResponseIsNotAnEncryptedJwe` — Credential error response is not an encrypted JWE
- Last suite-to-Certify request: `POST https://host.docker.internal:8446/v1/certify/issuance/credential`; authorization scheme `DPoP` (token omitted).
- Last response: `401 UNAUTHORIZED`; content type `application/json`; body `{"error":"invalid_token","error_description":"invalid_token"}`.
- Exact FAILURE (`EnsureHttpStatusCodeIs400`): resource endpoint returned an unexpected http status
- Exact FAILURE (`VCIValidateCredentialErrorResponse`): Non-standard credential error response error code found: invalid_token
- Exact INTERRUPTED (`oid4vci-1_0-issuer-fail-invalid-nonce`): Test was interrupted before it could complete. The failure 'VCIValidateCredentialErrorResponse: Non-standard credential error response error code found: invalid_token' means the test cannot continue.
- Classification evidence: A DPoP-authenticated credential request receives HTTP 401 invalid_token; the stock access-token filter only accepts the Bearer scheme.
- Patch behavior: `docker/native-certify/dpop.patch`. No production behavior is added to the harness.

### `oid4vci-1_0-issuer-fail-invalid-jwt-proof-signature`

- Stock export member: `plan-UYoPyoeGriNRN-export.zip / test-log-oid4vci-1_0-issuer-fail-invalid-jwt-proof-signature-s8WWjo8wtU8MEpq.json`.
- Matched patched PASSED member: `plan-yfOPDtRoNo2xZ-export.zip / test-log-oid4vci-1_0-issuer-fail-invalid-jwt-proof-signature-CCowkI7oTjzIKqx.json`.
- Last successful logged step: `VCIEnsureCredentialResponseIsNotAnEncryptedJwe` — Credential error response is not an encrypted JWE
- Last suite-to-Certify request: `POST https://host.docker.internal:8446/v1/certify/issuance/credential`; authorization scheme `DPoP` (token omitted).
- Last response: `401 UNAUTHORIZED`; content type `application/json`; body `{"error":"invalid_token","error_description":"invalid_token"}`.
- Exact FAILURE (`EnsureHttpStatusCodeIs400`): resource endpoint returned an unexpected http status
- Exact FAILURE (`VCIValidateCredentialErrorResponse`): Non-standard credential error response error code found: invalid_token
- Exact INTERRUPTED (`oid4vci-1_0-issuer-fail-invalid-jwt-proof-signature`): Test was interrupted before it could complete. The failure 'VCIValidateCredentialErrorResponse: Non-standard credential error response error code found: invalid_token' means the test cannot continue.
- Classification evidence: A DPoP-authenticated credential request receives HTTP 401 invalid_token; the stock access-token filter only accepts the Bearer scheme.
- Patch behavior: `docker/native-certify/dpop.patch`. No production behavior is added to the harness.

### `oid4vci-1_0-issuer-fail-unknown-credential-configuration`

- Stock export member: `plan-UYoPyoeGriNRN-export.zip / test-log-oid4vci-1_0-issuer-fail-unknown-credential-configuration-dJqxkp28p6TKPud.json`.
- Matched patched PASSED member: `plan-yfOPDtRoNo2xZ-export.zip / test-log-oid4vci-1_0-issuer-fail-unknown-credential-configuration-83u1HXTYw5tIFus.json`.
- Last successful logged step: `VCIEnsureCredentialResponseIsNotAnEncryptedJwe` — Credential error response is not an encrypted JWE
- Last suite-to-Certify request: `POST https://host.docker.internal:8446/v1/certify/issuance/credential`; authorization scheme `DPoP` (token omitted).
- Last response: `401 UNAUTHORIZED`; content type `application/json`; body `{"error":"invalid_token","error_description":"invalid_token"}`.
- Exact FAILURE (`EnsureHttpStatusCodeIs400`): resource endpoint returned an unexpected http status
- Exact FAILURE (`VCIValidateCredentialErrorResponse`): Non-standard credential error response error code found: invalid_token
- Exact INTERRUPTED (`oid4vci-1_0-issuer-fail-unknown-credential-configuration`): Test was interrupted before
  it could complete. The failure 'VCIValidateCredentialErrorResponse: Non-standard credential error response
  error code found: invalid_token' means the test cannot continue.
- Classification evidence: A DPoP-authenticated credential request receives HTTP 401 invalid_token; the stock access-token filter only accepts the Bearer scheme.
- Patch behavior: `docker/native-certify/dpop.patch`, `docker/native-certify/credential-errors.patch`. No production behavior is added to the harness.

### `oid4vci-1_0-issuer-fail-unknown-credential-identifier`

- Stock export member: `plan-UYoPyoeGriNRN-export.zip / test-log-oid4vci-1_0-issuer-fail-unknown-credential-identifier-wZUaQwM0lQnFZDW.json`.
- Matched patched PASSED member: `plan-yfOPDtRoNo2xZ-export.zip / test-log-oid4vci-1_0-issuer-fail-unknown-credential-identifier-DVdlowvoZgBngXo.json`.
- Last successful logged step: `VCIEnsureCredentialResponseIsNotAnEncryptedJwe` — Credential error response is not an encrypted JWE
- Last suite-to-Certify request: `POST https://host.docker.internal:8446/v1/certify/issuance/credential`; authorization scheme `DPoP` (token omitted).
- Last response: `500 INTERNAL_SERVER_ERROR`; content type `application/json`; body `{"error":"unknown_error","error_description":"JSON parse error: Unrecognized field \"credential_identifier\" (class io.mosip.certify.core.dto.CredentialRequest), not marked as ignorable"}`.
- Exact FAILURE (`EnsureHttpStatusCodeIs400`): resource endpoint returned an unexpected http status
- Exact FAILURE (`VCIValidateCredentialErrorResponse`): Non-standard credential error response error code found: unknown_error
- Exact INTERRUPTED (`oid4vci-1_0-issuer-fail-unknown-credential-identifier`): Test was interrupted before it could complete. The failure 'VCIValidateCredentialErrorResponse: Non-standard credential error response error code found: unknown_error' means the test cannot continue.
- Classification evidence: Stock CredentialRequest rejects credential_identifier with HTTP 500 unknown_error.
- Patch behavior: `docker/native-certify/credential-errors.patch`. No production behavior is added to the harness.

### `oid4vci-1_0-issuer-fail-on-access-token-in-query`

- Stock export member: `plan-UYoPyoeGriNRN-export.zip / test-log-oid4vci-1_0-issuer-fail-on-access-token-in-query-O2E2YHPFYOnxRY4.json`.
- Matched patched PASSED member: `plan-yfOPDtRoNo2xZ-export.zip / test-log-oid4vci-1_0-issuer-fail-on-access-token-in-query-SAED0c1R0ukBBwl.json`.
- Last successful logged step: `CallProtectedResourceAllowingDpopNonceError` — Got a response from the resource endpoint
- Last suite-to-Certify request: `POST https://host.docker.internal:8446/v1/certify/issuance/credential`; authorization scheme `DPoP` (token omitted).
- Last response: `401 UNAUTHORIZED`; content type `application/json`; body `{"error":"invalid_token","error_description":"invalid_token"}`.
- Exact FAILURE (`EnsureHttpStatusCodeIsAnyOf`): resource endpoint returned an unexpected http status
- Exact INTERRUPTED (`oid4vci-1_0-issuer-fail-on-access-token-in-query`): Test was interrupted before it could complete. The failure 'EnsureHttpStatusCodeIsAnyOf: resource endpoint returned an unexpected http status' means the test cannot continue.
- Classification evidence: A DPoP-authenticated credential request receives HTTP 401 invalid_token; the stock access-token filter only accepts the Bearer scheme.
- Patch behavior: `docker/native-certify/dpop.patch`, `docker/native-certify/extensions.patch`, `docker/native-certify/holder-binding.patch`. No production behavior is added to the harness.

## Source corroboration and boundaries

The pinned upstream Certify source `8fdf71656979a72fa8263766d4dec3cc25127b76`,
`certify-service/src/main/java/io/mosip/certify/filter/AccessTokenValidationFilter.java`, accepts only
`Authorization: Bearer`; `dpop.patch` adds DPoP proof and binding validation. `extensions.patch` adds ignoring
unknown request properties, `credential-errors.patch` adds credential_identifier validation and standard
credential errors, `signed-metadata.patch` adds signed metadata, and `holder-binding.patch` adds the holder
cnf context needed by the diagnostic credential. The HTTP 401 negative cases are blocked before the intended
nonce/signature/selector error checks, so those stock downstream checks are not verified separately.

Changing sender-constraining, removing the suite's extension parameter or adding a response translator would
hide product behavior. Those changes were not made. Stock remains the default release gate; a diagnostic
issuer PASS is not stock conformance. The six verifier REVIEWs and failed combined gates are preserved.


## Sender-constraining cross-check on 25 October 2026

The real suite `GET /api/plan/available` and `python runner/list_plans.py --insecure` (exit 0) list exactly
`dpop` and `mtls` for oid4vci-1_0-issuer-test-plan; there is no `none` or unconstrained `bearer` variant. The
selected fapi_profile=vci does not exclude either value. mTLS requires mtls/mtls2 key, cert and ca fields.
Evidence: closeout/variant-a3037a5d/issuer-plan-available.json, list-plans.log and commands.json; original
first capture variant-a7880211 recorded the same enumeration.

Fresh unmodified stock issuer metadata returned HTTP 200 from
`https://host.docker.internal:8446/.well-known/openid-credential-issuer`: authorization_servers points to the
course realm, with no dpop_signing_alg_values_supported, token_type or token_types_supported field. The exact
RFC8414 authorization-server metadata URL used by the original plan,
`https://host.docker.internal:8446/.well-known/oauth-authorization-server/auth/realms/course`, returned HTTP
200 and advertises DPoP algorithms PS384, RS384, EdDSA, ES384, ES256, RS256, ES512, PS256, PS512 and RS512;
tls_client_certificate_bound_access_tokens=true; and mtls_endpoint_aliases. Neither metadata response declares
token_type/token_types_supported. Issuer metadata absence alone is not proof of unsupported DPoP; its token
processing and the actual responses must be inspected. Evidence: issuer-metadata.json and
authorization-server-metadata.json in the same capture.

Because the authorization server advertises mTLS, all seven original 401 cases were rerun with
sender_constrain=mtls, keeping the same plan, credential, clients and stock image. Real development CA/client
TLS certificates were supplied as plan inputs; no Certify, ingress, registered client or product behavior was
patched. Official plan `45vEXNrkMzWtm`, export `plan-45vEXNrkMzWtm-export.zip`, contains only these seven
executed instances: **2 PASSED, 4 FAILED, 1 INTERRUPTED**. This is a selected-case diagnostic, not a complete
plan qualification or a new passing release gate. The collection script exit 0 means evidence collection
completed; it does not mean conformance passed. Owned cleanup exited 0 with no owned volumes remaining
(closeout/variant-a3037a5d/commands.json and deployment-state.json).

| Test suffix | Original DPoP result | mTLS-labelled probe | Official instance | New observation |
|---|---|---|---|---|
| `happy-flow-additional-requests` | INTERRUPTED, HTTP 401 | FAILED | `tHVEdp9AXWrlfNc` | See note 1. |
| `happy-flow-multiple-clients` | INTERRUPTED, HTTP 401 | FAILED | `mDgvBWFICfKuRb0` | See note 2. |
| `happy-flow-skip-notification` | INTERRUPTED, HTTP 401 | FAILED | `Jac5XbViiyNf9GC` | See note 3. |
| `fail-invalid-nonce` | INTERRUPTED, HTTP 401 | PASSED | `TBNhr5DBr72DfSP` | Selected negative test passed; token was unbound Bearer. |
| `fail-invalid-jwt-proof-signature` | INTERRUPTED, HTTP 401 | PASSED | `rPw9Bx5DisnpSH2` | Selected negative test passed; token was unbound Bearer. |
| `fail-unknown-credential-configuration` | INTERRUPTED, HTTP 401 | INTERRUPTED | `beCk6y4oOy7Pior` | Expected error code not found in credential error response: unknown_credential_configuration |
| `fail-on-access-token-in-query` | INTERRUPTED, HTTP 401 | FAILED | `eQqDONBUtfGSxy0` | See note 4. |

Every observed token response in this probe uses token_type=Bearer and its JWT payload lacks cnf, including
x5t#S256. The advertised mTLS capability therefore did not produce demonstrated certificate-bound tokens for
these registered clients through this ingress. The current ingress does not request/forward client
certificates, and generated clients do not enable certificate-bound access tokens (docker/nginx/course.conf
and runner/setup.py). It would be incorrect to label the two negative-case passes as end-to-end mTLS
conformance. End-to-end mTLS binding is **not verified**; no additional deployment changes were made under
this task's restricted stock-path scope.

Decision: the seven-case success condition for changing the three entry-point defaults was not met, and no
viable passing non-DPoP deployment was established. Keep the original DPoP-path PRODUCT_GAP classification:
the stock Bearer-only filter still rejects DPoP. Do not claim DPoP is the only allowed suite variant, and do
not silently select unbound Bearer tokens under an mTLS label. No defaults, profiles, gate policy or expected
failures were changed. The nonce and proof-signature negative behavior is now verified to work with these
unbound Bearer tokens; it is not itself a proven missing stock feature. The mTLS probe additionally exposes
missing credential holder cnf.jwk, a multiple-client 4xx expectation failure and an incorrect
unknown-credential-configuration error. Those are separate native behavior findings, not evidence that a
variant switch fixes stock conformance. Raw messages, token-field observations and export hash are in
closeout/a1-decision.json.

## Verifier coverage details

Request URI POST: instance `49xL7f98HbXNJZr` in stock run `019bf015dcef47029010faa06a2cf788` ends REVIEW
with “Upload a screenshot showing that the verifier successfully verified the presented credential (for
example, a page displaying the credential contents).” Its `url_query` variant never runs the three
POST/wallet_nonce conditions; pinned suite source only calls that override for signed request URIs,
establishing a suite applicability/coverage gap rather than a POST failure attributable to the harness or
Verify. Actual native POST interoperability is **not verified**; see [validation limits](VALIDATION.md)
for the local reproduction evidence.
Status lists: stock happy-flow instance `qyHOyhAz17GKHWo` has native `statusCheck: []` and a suite
credential without a status reference, while its official message requests a verification screenshot (same
verifier export). This is missing coverage in the suite fixture, not evidence of successful status-list
handling or an observed product rejection; no failing status-list test exists in this selected export to
reproduce. Actual status-list interoperability is **not verified**, and no workaround or fixture substitution
was introduced.

## Table notes

Note 1: cnf.jwk missing or not a JSON object in SD-JWT credential; The issued credential does not contain a
'cnf' claim with a 'jwk' member binding it to one of the keys the proofs in the credential request
demonstrated possession of

Note 2: cnf.jwk missing or not a JSON object in SD-JWT credential; The issued credential does not contain a
'cnf' claim with a 'jwk' member binding it to one of the keys the proofs in the credential request
demonstrated possession of; cnf.jwk missing or not a JSON object in SD-JWT credential; The issued credential
does not contain a 'cnf' claim with a 'jwk' member binding it to one of the keys the proofs in the credential
request demonstrated possession of; resource endpoint returned a different http status than expected

Note 3: cnf.jwk missing or not a JSON object in SD-JWT credential; The issued credential does not contain a
'cnf' claim with a 'jwk' member binding it to one of the keys the proofs in the credential request
demonstrated possession of

Note 4: cnf.jwk missing or not a JSON object in SD-JWT credential; The issued credential does not contain a
'cnf' claim with a 'jwk' member binding it to one of the keys the proofs in the credential request
demonstrated possession of
