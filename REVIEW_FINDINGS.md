> Review/certification discussion is optional. No OIDF contact, formal certification, review disposition or new POST protocol implementation is needed to deliver the assignment harness. Preserve REVIEW and the strict failed gate.

# Six-case verifier investigation

Fresh run `c4633b091cdd4b8eb4facd3c36986c94`; issuer plan `qJ6tKNfFZCfzm`; verifier plan `tSq9qkf5JI4G6`; exact target `oid4vp-1final-verifier-test-plan`. Historical run `141a3630f7874e98ae4964653f953899` and earlier serial-execution evidence are byte-preserved.

Certify: **12 PASS, 3 optional SKIP; gate PASSED**. Verify: **4 PASS, 6 REVIEW; gate FAILED**. Combined: **16 PASS, 6 REVIEW, 3 SKIP; gate FAILED**. No TIMEOUT, no manual dispositions. Native observations match expectations in the six reviewed transactions; that is not an official PASS.

## Why REVIEW remains
The pinned suite requests a screenshot after a successful HTTP response. `ImageAPI` and `waitForPlaceholders` deliberately record REVIEW after image submission. A filled placeholder is evidence, not an approval. Negative tests explicitly support immediate HTTP 4xx rejection or deferred HTTP 2xx followed by rejection evidence; the latter takes the screenshot/REVIEW branch. No protocol defect is established merely by choosing the supported deferred path. Changing response timing solely to obtain PASS is not a remedy.

The inspected local OpenAPI document returned HTTP 200 and lists 51 operations. Together with ImageAPI, TestInfoApi, LogApi and TestRunner source inspection, it exposes retrieval and image submission but no documented review-disposition operation. The substring match `previewBulkPlanDelete` is unrelated. This establishes a limit of this pinned API, not a claim about every OIDF service. No undocumented write operation or database update was attempted. Source inspection does not establish an authorized REVIEW-to-PASS procedure for this alpha plan; OIDF clarification is pending. Any later written assessment must be retained separately and cannot silently replace these raw results.

The selected general plan declares itself alpha and outside certification. Current OIDF guidance lists Final 1.0 with HAIP for verifier certification. The target remains unchanged. An advisory assessment of these alpha instances and formal certification are separate questions. No eligibility or authoritative approval is claimed.

Sources: [ImageAPI.java](https://gitlab.com/openid/conformance-suite/-/blob/11999aad62ec292f36101410d9d5b761d44903ff/src/main/java/net/openid/conformance/logging/ImageAPI.java), [AbstractTestModule.java](https://gitlab.com/openid/conformance-suite/-/blob/11999aad62ec292f36101410d9d5b761d44903ff/src/main/java/net/openid/conformance/testmodule/AbstractTestModule.java), [AbstractVP1FinalVerifierTest.java](https://gitlab.com/openid/conformance-suite/-/blob/11999aad62ec292f36101410d9d5b761d44903ff/src/main/java/net/openid/conformance/vp1finalverifier/AbstractVP1FinalVerifierTest.java), [AbstractVP1FinalVerifierNegativeTest.java](https://gitlab.com/openid/conformance-suite/-/blob/11999aad62ec292f36101410d9d5b761d44903ff/src/main/java/net/openid/conformance/vp1finalverifier/AbstractVP1FinalVerifierNegativeTest.java), [VP1FinalVerifierTestPlan.java](https://gitlab.com/openid/conformance-suite/-/blob/11999aad62ec292f36101410d9d5b761d44903ff/src/main/java/net/openid/conformance/vp1finalverifier/VP1FinalVerifierTestPlan.java).

[Current OIDF verifier guidance](https://openid.net/certification/conformance-testing-for-openid-for-verifiable-presentations/); [formal submission procedure](https://openid.net/certification/how-to-submit-your-certification-request/).

## Credential status investigation
All six actual responses requested `skipStatusChecks=false` with the Revocation filter. Their signed credential payloads and provided disclosures contain no `status` or `credentialStatus` reference (structural inspection only; cryptographic verification is the native verifier's job). The suite's VP fixture uses CreateSdJwtKbCredential / AbstractCreateSdJwtCredential without additional status claims; the similarly named issuer fixture is a different path. Native VCVerificationServiceImpl populates status entries only after schema/signature success; Utils maps unavailable status to an empty list. The three cryptographic failures short-circuit that branch. Therefore empty arrays are consistent with these exact fixtures and are not evidence of working revocation checking. OID4VP 1.0 section 8.6 makes credential revocation/expiration policy checks applicable to the credential and policy; this run exercises no status-list credential. No status result has been fabricated, and broader status-list interoperability remains unverified.

SDK correlation is cookie-bound: the real `/vp-session-results` request uses an HttpOnly transaction cookie, not a JSON transactionId. We retain the returned transaction ID, native creation IDs, request URL, observation time, suite/image identifiers and QR hash without exposing cookies. Identical generic success/failure screens across some transactions are expected; screenshots alone are insufficient to distinguish them. The backend windows correlate native request and transaction IDs but may contain interleaved threads; specific negative codes are established by SDK responses, not by those backend windows.

Sources: [CreateSdJwtKbCredential.java](https://gitlab.com/openid/conformance-suite/-/blob/11999aad62ec292f36101410d9d5b761d44903ff/src/main/java/net/openid/conformance/condition/as/CreateSdJwtKbCredential.java), [AbstractCreateSdJwtCredential.java](https://gitlab.com/openid/conformance-suite/-/blob/11999aad62ec292f36101410d9d5b761d44903ff/src/main/java/net/openid/conformance/condition/as/AbstractCreateSdJwtCredential.java), [VCVerificationServiceImpl.java](https://github.com/inji/inji-verify/blob/4c4289026968beb535d3dbdd500947152c43f708/verify-service/src/main/java/io/inji/verify/services/impl/VCVerificationServiceImpl.java), [VerifiablePresentationSubmissionServiceImpl.java](https://github.com/inji/inji-verify/blob/4c4289026968beb535d3dbdd500947152c43f708/verify-service/src/main/java/io/inji/verify/services/impl/VerifiablePresentationSubmissionServiceImpl.java), [api.ts](https://github.com/inji/inji-verify/blob/4c4289026968beb535d3dbdd500947152c43f708/inji-verify-sdk/src/utils/api.ts); [OID4VP 1.0 section 8.6](https://openid.net/specs/openid-4-verifiable-presentations-1_0.html#name-vp-token-validation).

## Minimal harness fixes
- Audit now fails closed when a live test is non-final or differs from retained REVIEW; it never rewrites history.
- Audit rejects contradictory native failure fields instead of accepting an error code alone.
- Evidence records actual SDK response observation time and request URL, screenshot file time and available official timestamps. Structural status-reference inspection reports unknown for undecodable data.
- Eleven regression cases added; controlled fixture data are not official conformance evidence. No native protocol, suite, profile, mapping or gate changed.

## Separate case findings

### oid4vp-1final-verifier-happy-flow
- Official instance `4QxprhVb9DdS5QF`: FINISHED / REVIEW, all requested placeholders filled; uploaded image bytes match the native original.
- Native request `req_e414a1e6-4d86-41a2-831a-10eceae18c28`; transaction `txn_19cef3bd-e527-42f0-83e5-73db9c3d1864`.
- Expected: Accept valid presentation. Observed: Congratulations, the given credential is valid!.
- Schema/signature and holder checks agree with the expected accepted or rejected outcome; SDK response observed `2026-10-20T06:47:52.083745+00:00` at `https://host.docker.internal:8445/v1/verify/vp-session-results`.
- Original UI SHA-256 `839e22ff0f617e6f7053eee9fe9b9b1f24bbe4cded6f30526edb63fdc011c64e`; QR SHA-256 `e70ed2ff072ab7ae2ba29918bea2167b7018479492e806910c9204aaec9b2d26`; original screenshot file time `2026-10-20T06:47:54.116916+00:00` (filesystem metadata, not a signed capture timestamp).
- Official timestamps: `{"started": "2026-10-20T06:47:30.763044488Z"}`.
- SDK status entries: 0; status reference present: False. Native log correlation available: True.
- Evidence for this historical instance is retained separately from the source distribution.
- Finding: valid flow accepted / invalid flow rejected as expected; suite screenshot/REVIEW branch remains. No missing image upload, no local approval, no native bug established. Generic UI and backend-window limits above apply.

### oid4vp-1final-verifier-minimal-cnf-jwk
- Official instance `3AaIDb69rsa7Lvf`: FINISHED / REVIEW, all requested placeholders filled; uploaded image bytes match the native original.
- Native request `req_bdce1f3a-4a04-4c76-a523-7205c3aa501e`; transaction `txn_1514a0e3-9b71-4a97-b502-91de8494cfde`.
- Expected: Accept valid presentation. Observed: Congratulations, the given credential is valid!.
- Schema/signature and holder checks agree with the expected accepted or rejected outcome; SDK response observed `2026-10-20T06:48:04.074127+00:00` at `https://host.docker.internal:8445/v1/verify/vp-session-results`.
- Original UI SHA-256 `ae947f90d1e4d0759e4e9db94f19351be83d0473e1807f1784c4eb26e9e2ca2d`; QR SHA-256 `3c64963f2aa0f0b7ae79e7ea13b96db8932f76f601a000b631b89966a8ab5564`; original screenshot file time `2026-10-20T06:48:05.025620+00:00` (filesystem metadata, not a signed capture timestamp).
- Official timestamps: `{"started": "2026-10-20T06:47:57.198293379Z"}`.
- SDK status entries: 0; status reference present: False. Native log correlation available: True.
- Evidence for this historical instance is retained separately from the source distribution.
- Finding: valid flow accepted / invalid flow rejected as expected; suite screenshot/REVIEW branch remains. No missing image upload, no local approval, no native bug established. Generic UI and backend-window limits above apply.

### oid4vp-1final-verifier-request-uri-method-post
- Official instance `HP1TBvN42w3mBIl`: FINISHED / REVIEW, all requested placeholders filled; uploaded image bytes match the native original.
- Native request `req_e6c83206-fa8f-4d14-96aa-73a580a8edeb`; transaction `txn_4779530c-45d7-479f-864b-56aa8cf405b5`.
- Expected: Accept valid presentation. Observed: Congratulations, the given credential is valid!.
- Schema/signature and holder checks agree with the expected accepted or rejected outcome; SDK response observed `2026-10-20T06:48:16.364995+00:00` at `https://host.docker.internal:8445/v1/verify/vp-session-results`.
- Original UI SHA-256 `ae947f90d1e4d0759e4e9db94f19351be83d0473e1807f1784c4eb26e9e2ca2d`; QR SHA-256 `392ae31a981189d4fc73abe3a8fe8aa7ebf4ae0a461e02b673ecd7e6eb8c2413`; original screenshot file time `2026-10-20T06:48:15.995721+00:00` (filesystem metadata, not a signed capture timestamp).
- Official timestamps: `{"started": "2026-10-20T06:48:07.465020583Z"}`.
- SDK status entries: 0; status reference present: False. Native log correlation available: True.
- Evidence for this historical instance is retained separately from the source distribution.
- Finding: valid flow accepted / invalid flow rejected as expected; suite screenshot/REVIEW branch remains. No missing image upload, no local approval, no native bug established. Generic UI and backend-window limits above apply.
- **Coverage blocker:** despite the module name, this instance does NOT establish request_uri POST support. All three required POST/wallet_nonce condition successes are absent. The exact configured `request_method=url_query` bypasses `fetchAndProcessRequestUri()` in AbstractVP1FinalVerifierTest, so the subclass override neither POSTs nor enters its not-applicable SKIP branch. It instead completes the ordinary valid-presentation/screenshot path and returns REVIEW. This is an upstream applicability/coverage gap, not proof of POST validation.
- The native pinned request service returns a request URI only for its `decentralized_identifier` client scheme; this run uses `redirect_uri`. Native DID support does not establish a compatible signed-request path for this configured suite variant. Configuration alone has not established a usable native POST path. No request-method/client-scheme/profile change, request translation, unsupported support claim or native rewrite was made. OIDF should clarify applicability of this named module in url_query and whether its coverage/result semantics should change upstream. Prior statements implying that this REVIEW proves POST/wallet_nonce validation are corrected here.

### oid4vp-1final-verifier-invalid-kb-jwt-signature
- Official instance `0rrHl0D1hFKNAG5`: FINISHED / REVIEW, all requested placeholders filled; uploaded image bytes match the native original.
- Native request `req_0e66c224-52cf-41f2-a2a1-61b46e24e909`; transaction `txn_717fd3aa-ce75-4694-83eb-cf6120a3dbf1`.
- Expected: Reject ERR_INVALID_KB_SIGNATURE. Observed: ERR_INVALID_KB_SIGNATURE.
- Schema/signature and holder checks agree with the expected accepted or rejected outcome; SDK response observed `2026-10-20T06:48:27.056348+00:00` at `https://host.docker.internal:8445/v1/verify/vp-session-results`.
- Original UI SHA-256 `c54b8aedc8cc4919d7a1e54c1c710b41531f6f0efbeb824db4e1b74d0756ab56`; QR SHA-256 `36bb8416f88d5303b84089663c2a5319843897c1277e01206a7eff5352602b39`; original screenshot file time `2026-10-20T06:48:27.074675+00:00` (filesystem metadata, not a signed capture timestamp).
- Official timestamps: `{"started": "2026-10-20T06:48:18.351742505Z"}`.
- SDK status entries: 0; status reference present: False. Native log correlation available: True.
- Evidence for this historical instance is retained separately from the source distribution.
- Finding: valid flow accepted / invalid flow rejected as expected; suite screenshot/REVIEW branch remains. No missing image upload, no local approval, no native bug established. Generic UI and backend-window limits above apply.

### oid4vp-1final-verifier-invalid-credential-signature
- Official instance `D4F9uRokdl7B3YB`: FINISHED / REVIEW, all requested placeholders filled; uploaded image bytes match the native original.
- Native request `req_444527eb-a05b-417b-8fc9-bb462e775dc5`; transaction `txn_42a78fd7-c055-499f-9944-a50a45634c9b`.
- Expected: Reject ERR_SIGNATURE_VERIFICATION_FAILED. Observed: ERR_SIGNATURE_VERIFICATION_FAILED.
- Schema/signature and holder checks agree with the expected accepted or rejected outcome; SDK response observed `2026-10-20T06:48:33.920340+00:00` at `https://host.docker.internal:8445/v1/verify/vp-session-results`.
- Original UI SHA-256 `c54b8aedc8cc4919d7a1e54c1c710b41531f6f0efbeb824db4e1b74d0756ab56`; QR SHA-256 `9302956639cc2dbc245c90d9afe27a26abe6b890603ac3d1a860db1ace5bbdb7`; original screenshot file time `2026-10-20T06:48:35.101131+00:00` (filesystem metadata, not a signed capture timestamp).
- Official timestamps: `{"started": "2026-10-20T06:48:28.937497190Z"}`.
- SDK status entries: 0; status reference present: False. Native log correlation available: True.
- Evidence for this historical instance is retained separately from the source distribution.
- Finding: valid flow accepted / invalid flow rejected as expected; suite screenshot/REVIEW branch remains. No missing image upload, no local approval, no native bug established. Generic UI and backend-window limits above apply.

### oid4vp-1final-verifier-invalid-sd-hash
- Official instance `aY3aS4cDDokQ7Wi`: FINISHED / REVIEW, all requested placeholders filled; uploaded image bytes match the native original.
- Native request `req_75d7026c-e2d8-4246-8d39-b1212c714d59`; transaction `txn_a2359aca-423e-40f1-9bdb-1cd4dc56e7cd`.
- Expected: Reject ERR_INVALID_SD_HASH. Observed: ERR_INVALID_SD_HASH.
- Schema/signature and holder checks agree with the expected accepted or rejected outcome; SDK response observed `2026-10-20T06:48:45.127520+00:00` at `https://host.docker.internal:8445/v1/verify/vp-session-results`.
- Original UI SHA-256 `446414f913fbfb2a11c08d28d26469cc2e14a202f1be910188fe3f77101e9736`; QR SHA-256 `c60abc07852e5e1e9bde71a01e3bda3e5af1514d7643dc16014b934313ca6cde`; original screenshot file time `2026-10-20T06:48:46.185587+00:00` (filesystem metadata, not a signed capture timestamp).
- Official timestamps: `{"started": "2026-10-20T06:48:37.745251931Z"}`.
- SDK status entries: 0; status reference present: False. Native log correlation available: True.
- Evidence for this historical instance is retained separately from the source distribution.
- Finding: valid flow accepted / invalid flow rejected as expected; suite screenshot/REVIEW branch remains. No missing image upload, no local approval, no native bug established. Generic UI and backend-window limits above apply.

## Remaining dependency
All six historical screenshot placeholders were filled. Their official outcomes remain REVIEW. No authoritative review disposition is claimed. Later local and release-triggered validation verified deployment, reporting, storage and cleanup. Request URI POST coverage and status-list interoperability remain unestablished.

## Reproduction and command evidence
See [RESULTS.md](RESULTS.md) and [PROJECT_STATUS.md](PROJECT_STATUS.md). Historical execution artifacts and original private exports are retained separately.
