# Request URI POST — supported capability investigation

The selected native release is Inji Verify 1.0.0-alpha.1, pinned source 4c4289026968beb535d3dbdd500947152c43f708. **Request URI POST is unsupported in this release/configuration.** This is not fixed by changing a plan template.

Fresh genuine native probe: authorization creation returned 201, requestUri was null for redirect_uri, POST to that native request's /v2/vp-request/{id} returned 405 with Allow: GET and an empty body. GET returned 200 application/oauth-authz-req+jwt. Its claim-name inspection found no wallet_nonce. These are actual HTTP observations, not an official conformance run or a cryptographic verification claim. Request/transaction identifiers, timestamps, HTTP fields and response hashes are retained in the evidence.

Pinned VPRequestController exposes only GET retrieval. VerifiablePresentationRequestServiceImpl returns requestUri only for decentralized_identifier and signs its JWT without wallet_nonce. The SDK adds request_uri but never request_uri_method=post. The suite supports redirect_uri, x509_san_dns and x509_hash client prefixes; DID is not one of them. Its signed request_uri variant is explicitly inapplicable with redirect_uri. Therefore merely changing request_method to request_uri_signed is incompatible with the current native/client configuration.

The selected url_query variant correctly represents the working native direct-query request. However, the named POST test bypasses its fetch override under url_query, completing an ordinary valid-presentation/screenshot path as REVIEW without checking POST or wallet_nonce. This is an upstream test-applicability/coverage limitation, not proof of POST support. The updated read-only audit explicitly flags it and requires successful CreateWalletNonce, PostToRequestUriAndExtractRequestObject and EnsureWalletNonceClaimMatchesPostedValue entries before reporting exercised coverage. It never changes official results or gates. Three added regressions cover missing, failing and successful condition records.

Implementing this feature requires native form-encoded POST request retrieval; correct wallet_nonce binding in the signed request object; applicable wallet metadata handling; a suite-supported authenticated client scheme with valid signing/trust metadata and matching native request object semantics; SDK/QR advertisement of request_uri and request_uri_method=post; native positive/negative tests; and actual official condition success in a compatible variant. This is product/SDK implementation work, not a proxy, JSON toggle or result edit. No such new capability is advertised here, and neither profile nor client scheme was switched. No new official plan was necessary to prove a method that the native endpoint rejects.

References:

- [OID4VP 1.0, sections 5.9.3 and 5.10](https://openid.net/specs/openid-4-verifiable-presentations-1_0.html)
- [Native retrieval controller](https://github.com/inji/inji-verify/blob/4c4289026968beb535d3dbdd500947152c43f708/verify-service/src/main/java/io/inji/verify/controller/VPRequestController.java)
- [Native request service](https://github.com/inji/inji-verify/blob/4c4289026968beb535d3dbdd500947152c43f708/verify-service/src/main/java/io/inji/verify/services/impl/VerifiablePresentationRequestServiceImpl.java)
- [Native SDK request generation](https://github.com/inji/inji-verify/blob/4c4289026968beb535d3dbdd500947152c43f708/inji-verify-sdk/src/components/openid4vp-verification/OpenID4VPVerification.tsx)
- [Pinned suite variant applicability and fetch dispatch](https://gitlab.com/openid/conformance-suite/-/blob/11999aad62ec292f36101410d9d5b761d44903ff/src/main/java/net/openid/conformance/vp1finalverifier/AbstractVP1FinalVerifierTest.java)
- [Pinned POST test](https://gitlab.com/openid/conformance-suite/-/blob/11999aad62ec292f36101410d9d5b761d44903ff/src/main/java/net/openid/conformance/vp1finalverifier/VP1FinalVerifierRequestUriMethodPost.java)
