# Assignment requirement checklist

Verified means the stated scope has evidence; it does not mean product conformance.
Historical stock run S is `019bf015dcef47029010faa06a2cf788`; patched diagnostic
run P is `d39d9f65b0f04db79eb3d25501c9f26c`. Their official export names and
counts are recorded in [README results](README.md#recorded-stock-and-patched-results).
The original run `141a3630f7874e98ae4964653f953899` remains preserved.

Report and compiler filenames below refer to the separate local evidence handoff.
[The evidence index](evidence/README.md) gives their actual retained paths.
They are not bundled with source. Drive upload and reviewer access are **not verified**.

| Requirement | Verified scope and evidence | Remaining scope |
|---|---|---|
| One Compose file for suite, Certify, Verify and storage | verified: S and P, commands.json, deployment-state.json; ten services and five fresh owned volumes | verified: scratch hosted run 40165722639 at 9c8d94ad9da42ac458ea304192118266577469f9; ten services started |
| Official REST create/configure/execute/poll/retrieve | verified: S/P official exports named above; actual component reports and conformance-summary.json | not verified: arbitrary other profiles |
| OpenIDConformanceTest in both actual API rigs | verified: S/P reports/existing-certify and reports/existing-verify, reporter-exit-statuses.json on Java 21 | external pending: organizer acceptance of current upstream module locations and Java 21 |
| Correct TestNG result mapping, Extent and strict gates | verified: S/P native/consolidated XML and HTML; triage-tests.xml plus actual JDK 11 seven-scenario output | not verified: any official REVIEW approval; no waiver added |
| Combined cross-module reports | verified: S/P reports/extent-report.html, testng-results.xml and failed combined gate | not verified: course-to-PID interoperability, which combined execution does not establish |
| One-command certify, verify and combined modes | verified: S/P full-stack combined commands.json; triage-tests.xml CLI checks and shell syntax outputs | not verified: fresh individual Certify live rerun in that validation or PowerShell end-to-end runtime |
| CI/CD workflow implementation | verified: workflow-policy.log and actionlint.log, both exit 0 | Historical CI `40165694278`; hosted scratch `40165722639`. |
| Selective component and plan configuration | verified: triage-tests.xml runner contracts; S/P actual selected plans | not verified: other profiles, which were not substituted |
| Expected-failure handling | verified: triage-tests.xml contract cases; empty config/expected-failures.json retained | not verified: real exemptions; none applied |
| Cross-run regression diff | verified: triage-tests.xml diff contract cases | not verified: a new live regression scenario in that validation |
| Setup, architecture and API documentation | verified: source-checks.json local link/AST checks and syntax outputs; S/P support documented routes | not verified: completely cold independent installation |
| Parallel component execution | verified: S/P commands.json parallel 2 and both real plan exports | not verified: parallel modules inside one plan; not claimed |
| Issuer and verifier 1.0 plan JSON templates | verified: S/P exports record exact templates/variants; verifier remains oid4vp-1final-verifier-test-plan | Stable 1.0.x availability is external pending; dated inventory found none. |
| run-full-stack-conformance.sh | verified: S/P commands.json plus shell-full.log exit 0 | not verified: empty-cache execution |
| Architecture explanation | verified: source-checks.json links and S/P observed service graph | not verified: hosted host-gateway; absent intentionally because internal DNS alias routes to ingress |
| REST API automation explanation | verified: API_REFERENCE.md, S/P actual exports and triage-tests.xml client contracts | not verified: unused API routes |
| Native component handoffs and evidence | verified: S/P official logs, native transaction IDs and captured screenshot exports | not verified: POST wallet_nonce or status-list coverage in these fixtures |
| Self-certification procedure | verified: REVIEW_PROCESS.md source deliverable, source-checks.json | external pending: applicable official review, authorized signature/payment/submission/acceptance; not performed |
| Troubleshooting | verified: docs/STOCK_CERTIFY_TRIAGE.md exact S/P export messages and source-checks.json | not verified: resolving product gaps through configuration; no such claim |
| Java 11 standalone bridge | verified: JDK 11 fresh compilation and seven scenarios; `jdk11-checks.json`. | external pending: upstream modules target 21; exact compiler failures and POM lines in docs/VALIDATION.md |
| MinIO/S3 artifact lifecycle and integrity | verified: S/P artifact-storage-validation.json and independent storage-integrity.json, cleanup exit 0 | not verified: separate cloud S3 provider |
| Stock release qualification | verified: S reports 2 PASSED, 10 INTERRUPTED, 3 SKIPPED; gate FAILED; all ten classified PRODUCT_GAP from exports | external pending: native product changes; patched P issuer PASS does not qualify stock |
| Verifier qualification | verified: S/P report 4 PASSED, 6 REVIEW; gate FAILED | external pending: applicable official review; not verified: native POST and status-list interoperability |
| Fully empty-cache machine | not verified: prepared exact command sequence in docs/VALIDATION.md only | external pending: explicit approval; destructive prune not executed |


## Current source checks

Verified locally: `python runner/setup.py` followed by `python -m pytest tests -q`
returned 213 passed. [The check receipt](evidence/local-checks.json) also records
shell, PowerShell, workflow and Java 11 bridge checks. The original official runs
remain unchanged. End-to-end validation of the new reporting fixes is **not verified**.

## Hosted verification scope

Private scratch repository `SantoshReddy0603/inji-conformance-b2-scratch` ran
`40165722639` at `9c8d94ad9da42ac458ea304192118266577469f9`. It was not an
execution on the main repository. Official run `2583bed425d64f5abb0c86993d402116`
matched S: Certify 2 PASSED / 10 INTERRUPTED / 3 SKIPPED and Verify 4 PASSED /
6 REVIEW. Ten services started on ubuntu-24.04; reports were uploaded in artifacts
`12587654719` and `12587788827`; 114 storage objects were verified and five owned
volumes were removed with none remaining. Both product gates and the combined
gate remained FAILED.

Hosted reports and logs are retained locally. Raw hosted official export ZIPs were
not retained as GitHub artifacts, so offline raw-export inspection is **not verified**.
The observed hosted issuer image ID differs from the older local ID; byte-identical
image reproducibility is **not verified**.

## Local compatibility and remaining requirements

Historical Python output `implementation-completion/triage-tests.xml` records
196 passed, exit 0. JDK 11 records in `implementation-triage/jdk11-checks.json`
and `jdk11-scenarios.log` verify fresh bridge compilation and seven scenarios.
Both pinned upstream API modules require JDK 21. Their compiler failures and POM
lines are documented in [validation limits](docs/VALIDATION.md).

Verifier reproduction `0d9b58120a964f628a34dd0c658d6c8f`, export
`plan-IpxODLyKkxZNN-export.zip`, again returned 4 PASSED / 6 REVIEW. Native POST
and status-list interoperability remain **not verified**. Sender-constraining probe
plan `45vEXNrkMzWtm` returned 2 PASSED / 4 FAILED / 1 INTERRUPTED; its unbound
Bearer tokens do not establish conformant mTLS. Defaults and gates were not relaxed.

Independent empty-cache execution is **not verified**. Organizer acceptance of
integrated Java 21, applicable official review and final submission materials are
external pending. New source changes require their own local and CI validation;
historical green checks must not be presented as checks on an untested revision.
