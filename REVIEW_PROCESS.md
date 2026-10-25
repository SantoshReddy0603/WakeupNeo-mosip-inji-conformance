> Review/certification discussion is optional. No OIDF contact, formal certification, review disposition or new POST protocol implementation is needed to deliver the assignment harness. Preserve REVIEW and the strict failed gate.

# Verifier review process

The pinned suite requests a screenshot after a successful HTTP response. `ImageAPI` and `waitForPlaceholders` deliberately record REVIEW after image submission. A filled placeholder is evidence, not an approval. Negative tests explicitly support immediate HTTP 4xx rejection or deferred HTTP 2xx followed by rejection evidence; the latter takes the screenshot/REVIEW branch. No protocol defect is established merely by choosing the supported deferred path. Changing response timing solely to obtain PASS is not a remedy.

The inspected local OpenAPI document returned HTTP 200 and lists 51 operations. Together with ImageAPI, TestInfoApi, LogApi and TestRunner source inspection, it exposes retrieval and image submission but no documented review-disposition operation. The substring match `previewBulkPlanDelete` is unrelated. This establishes a limit of this pinned API, not a claim about every OIDF service. No undocumented write operation or database update was attempted. Source inspection does not establish an authorized REVIEW-to-PASS procedure for this alpha plan; OIDF clarification is pending. Any later written assessment must be retained separately and cannot silently replace these raw results.

The selected general plan declares itself alpha and outside certification. Current OIDF guidance lists Final 1.0 with HAIP for verifier certification. The target remains unchanged. An advisory assessment of these alpha instances and formal certification are separate questions. No eligibility or authoritative approval is claimed.

All six actual responses requested `skipStatusChecks=false` with the Revocation filter. Their signed credential payloads and provided disclosures contain no `status` or `credentialStatus` reference (structural inspection only; cryptographic verification is the native verifier's job). The suite's VP fixture uses CreateSdJwtKbCredential / AbstractCreateSdJwtCredential without additional status claims; the similarly named issuer fixture is a different path. Native VCVerificationServiceImpl populates status entries only after schema/signature success; Utils maps unavailable status to an empty list. The three cryptographic failures short-circuit that branch. Therefore empty arrays are consistent with these exact fixtures and are not evidence of working revocation checking. OID4VP 1.0 section 8.6 makes credential revocation/expiration policy checks applicable to the credential and policy; this run exercises no status-list credential. No status result has been fabricated, and broader status-list interoperability remains unverified.

SDK correlation is cookie-bound: the real `/vp-session-results` request uses an HttpOnly transaction cookie, not a JSON transactionId. We retain the returned transaction ID, native creation IDs, request URL, observation time, suite/image identifiers and QR hash without exposing cookies. Identical generic success/failure screens across some transactions are expected; screenshots alone are insufficient to distinguish them. The backend windows correlate native request and transaction IDs but may contain interleaved threads; specific negative codes are established by SDK responses, not by those backend windows.

Evidence remains outside the source distribution. Preserve original images, transaction correlations and official results. No documented local review-disposition endpoint has been established. README contains the single reference-run identity.

## Self-certification submission procedure

This is an operator procedure, not a submission performed by the harness. The failed verifier gate is not certification-ready. The selected general plan is distinct from eligible profiles in the [official verifier guidance](https://openid.net/certification/conformance-testing-for-openid-for-verifiable-presentations/). Keep this project's target unchanged.

Follow the [official submission instructions](https://openid.net/certification/how-to-submit-your-certification-request/) when eligible:

1. Confirm the certification profile and software version. Complete required tests and resolve outstanding outcomes through the applicable review process.
2. Use Publish for certification in the suite to obtain each profile ZIP. Ordinary harness exports are not automatically certification packages.
3. Include required implementation evidence with test-specific filenames demonstrating the required acceptance or rejection.
4. Consult the official fee page and obtain the payment code through the implementer's approved payment/invoice process.
5. Open https://submissions.openid.net/ and supply the requested implementation identity, contact details, payment code and exported packages.
6. Have the authorized representative complete the declaration/signature process. Retain correspondence and wait for official acceptance before claiming certification.

The implementer performs payment, signatures and submission. This project performs no contact, fee, legal declaration, approval or profile switch.
