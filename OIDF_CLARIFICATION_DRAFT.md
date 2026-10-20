# Draft only — NOT SENT

To: certification@oidf.org
Subject: Clarification of six screenshot REVIEW outcomes in OID4VP Final general alpha verifier plan

Hello OpenID certification team,

We are evaluating a local Inji Verify development implementation using the exact `oid4vp-1final-verifier-test-plan`, suite revision 11999aad62ec292f36101410d9d5b761d44903ff, SD-JWT VC, redirect_uri/plain_vp configuration. We understand this general plan is alpha and outside formal certification; we are not submitting it as a certification request or requesting a profile change.

Fresh run c4633b091cdd4b8eb4facd3c36986c94, plan tSq9qkf5JI4G6, finished with four PASS and six REVIEW. The six instances are:

- oid4vp-1final-verifier-happy-flow: 4QxprhVb9DdS5QF
- oid4vp-1final-verifier-minimal-cnf-jwk: 3AaIDb69rsa7Lvf
- oid4vp-1final-verifier-request-uri-method-post: HP1TBvN42w3mBIl
- oid4vp-1final-verifier-invalid-kb-jwt-signature: 0rrHl0D1hFKNAG5
- oid4vp-1final-verifier-invalid-credential-signature: D4F9uRokdl7B3YB
- oid4vp-1final-verifier-invalid-sd-hash: aY3aS4cDDokQ7Wi

The native UI and cookie-bound SDK responses accept all three valid presentations and reject the three invalid presentations with the expected KB-signature, credential-signature and SD-hash errors. All six screenshot placeholders are filled, and fetched suite image bytes match original UI captures. The pinned source intentionally records REVIEW after image submission, including the supported deferred HTTP 2xx rejection branch. We have not changed any suite result, database record or release policy.

One coverage issue needs clarification: in the selected url_query variant, AbstractVP1FinalVerifierTest bypasses fetchAndProcessRequestUri. Consequently the named request-uri-method-post instance contains no successful POST/wallet_nonce conditions and does not take the subclass's not-applicable SKIP branch. Its REVIEW proves only the ordinary valid presentation/screenshot path. Is that module applicable to url_query, and how should the unexercised POST coverage be reported? We have preserved the raw result and do not claim POST support based on it. The native release exposes request URIs for a DID client scheme, whereas this run uses redirect_uri; we have not translated or altered the scheme.

Could you clarify (1) whether authoritative/advisory assessment is available for these general alpha instances; (2) the supported process and evidence requirements; (3) whether review changes raw REVIEW to PASS or is recorded separately, and by whom; and (4) whether any further genuine transaction evidence is needed? Our inspected 51-operation local OpenAPI document exposes no review-disposition operation. We do not assume an undocumented API exists.

All six presented fixture credentials lack a status reference, and the three invalid presentations fail cryptographic verification. Native status checking was requested but statusCheck arrays are empty. We do not claim this establishes revocation-list interoperability; please advise if additional status evidence is required for assessment of this exact configuration.

Proposed attachment: MOSIP-verifier-review-stage-17.zip, containing six-case index, unedited images/QRs, transaction IDs, timestamps, SHA-256 provenance, redacted SDK/backend/official logs and pinned source references. Localhost links are not externally reachable. Original exports include development secret material and remain private; the bundled exports are labelled sanitized unsigned derivatives. Please specify an appropriate secure channel if originals or additional sensitive logs are needed.

Formal certification, if pursued later, would require an eligible profile and separately authorized work. No formal certification is claimed. Please assess applicability and advise on legitimate next steps without assuming the alpha results are certification eligible.

Thank you.

[Sender name and implementation contact to be supplied by the user before sending.]
