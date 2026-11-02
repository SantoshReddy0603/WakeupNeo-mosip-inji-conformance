# Scope and limitations

The harness is implemented, but the identified stock release is not fully conformant. Stock run
`019bf015dcef47029010faa06a2cf788` has 2 issuer PASSED, 10 INTERRUPTED and 3 SKIPPED; its combined gate fails.
The separately labelled patched diagnostic `d39d9f65b0f04db79eb3d25501c9f26c` has 12 issuer PASSED and 3
SKIPPED and does not qualify stock. Evidence: respective official issuer exports listed in EVIDENCE_INDEX.md.

Three directly observed non-DPoP stock product gaps are: signed metadata returns
an empty HTTP 200 response; a legitimate unknown extension field causes HTTP 500;
and the standard credential_identifier field causes HTTP 500. Exact response bodies and native
patch associations are in [stock triage](../docs/STOCK_CERTIFY_TRIAGE.md). The separate sender-constraining check must not be
mistaken for a fix to these three failures. Additional stock holder-binding/error behavior appeared in the
mTLS-labelled partial plan 45vEXNrkMzWtm (2 PASSED, 4 FAILED, 1 INTERRUPTED): token cnf was absent, issued
credential cnf.jwk was absent, multiple-client rejection failed, and unknown-configuration error differed from
the suite expectation. End-to-end mTLS is **not verified**; defaults were not switched to an unbound-token
flow.

Six verifier instances remain REVIEW in fresh local run `0d9b58120a964f628a34dd0c658d6c8f`, official export `plan-IpxODLyKkxZNN-export.zip`:

- `oid4vp-1final-verifier-happy-flow`
- `oid4vp-1final-verifier-minimal-cnf-jwk`
- `oid4vp-1final-verifier-request-uri-method-post`
- `oid4vp-1final-verifier-invalid-kb-jwt-signature`
- `oid4vp-1final-verifier-invalid-credential-signature`
- `oid4vp-1final-verifier-invalid-sd-hash`

REVIEW is preserved as a failed TestNG assertion; the verifier and combined gates remain failed. Screenshots do not authorize converting REVIEW into PASS, and applicable official review is external pending.

Request URI POST interoperability is **not verified**: the POST-named case E1FPVnumrtRlZHU uses url_query and
bypasses its POST/wallet_nonce conditions. Status-list interoperability is **not verified**: happy-flow
oTZgMqIEscOyRW9 has no status reference and native statusCheck=[]. Evidence: verifier-coverage.json and the same official export.

The standalone bridge compiles for Java 11 and passed seven actual JDK 11 scenarios (jdk11-checks.json). Both upstream API rigs target Java 21 and JDK 11 reports “error: invalid target
release: 21” (compiler logs and exact POM lines in [validation limits](../docs/VALIDATION.md)). Organizer acceptance of integrated
Java 21 is external pending; no upstream POM was downgraded.

No stable 1.0.x image tags were found in the checked Certify/service/UI inventories on 24 October 2026; this
was a dated complete Docker Hub tag enumeration plus GitHub release/tag check, not a claim about all future
releases (registry-version-inventory.json and
upstream-release-inventory.json). Alpha versions remain explicit in generated docker/.env. Managed
GitHub-hosted ubuntu-24.04 full-stack execution is verified by scratch run `40165722639` at commit
`9c8d94ad9da42ac458ea304192118266577469f9`, official run `2583bed425d64f5abb0c86993d402116`: both plans,
reports, storage and cleanup completed while the strict gate FAILED. A separate empty-cache procedure remains
**not verified**. The observed hosted stock image ID differs from the older local ID; raw hosted exports were
verified in ephemeral MinIO but not retained for offline raw-export inspection. See [validation limits](../docs/VALIDATION.md) for
exact evidence scope. Formal certification and the submission video's recording are **not verified**.

Evidence access: Google Drive handoff is deferred, and reviewer access is **not verified**. See [evidence/README.md](../evidence/README.md) for the retained-file index and exclusions.
