# Evidence handoff

The historical execution reports listed below are not bundled here. The
[local check receipt](local-checks.json) is included and covers the current reporting
fixes, syntax checks and standalone bridge checks. Paths in the historical table below
are relative to the separate retained evidence package. Google Drive upload and
reviewer access are **not verified**; no public evidence destination is claimed.
Original raw exports are preserved separately and excluded from this package.

Stock reference run: `019bf015dcef47029010faa06a2cf788`.
Patched diagnostic run: `d39d9f65b0f04db79eb3d25501c9f26c`.
Verifier reproduction: `0d9b58120a964f628a34dd0c658d6c8f`.
Hosted execution: private scratch repository
`SantoshReddy0603/inji-conformance-b2-scratch`, run `40165722639`, commit
`9c8d94ad9da42ac458ea304192118266577469f9`.
The hosted execution was not on the original main repository. Its implementation
criteria passed while the official conformance gates remained FAILED.

| Verified claim | Retained proving files |
|---|---|
| Unified ten-service deployment, fresh owned volumes | `implementation-completion/stock-321cd46f/commands.json`; `implementation-completion/stock-321cd46f/deployment-state.json` |
| Stock Certify: 2 PASSED, 10 INTERRUPTED, 3 SKIPPED; gate FAILED | `implementation-completion/stock-321cd46f/stock-results.json` |
| Patched issuer diagnostic: 12 PASSED, 3 SKIPPED; not stock qualification | `implementation-completion/patched-40d8d65d/patched-results.json` |
| Stock combined: 6 PASS, 10 INTERRUPTED, 6 REVIEW, 3 SKIP; gate FAILED | `implementation-completion/stock-321cd46f/stock-results.json` |
| Patched combined: 16 PASS, 6 REVIEW, 3 SKIP; gate FAILED | `implementation-completion/patched-40d8d65d/patched-results.json` |
| Latest local verifier: 4 PASSED, 6 REVIEW; gate FAILED | `implementation-triage/verify-d11d275d/results.json` |
| Both real module OpenIDConformanceTest integrations and consolidated Extent/TestNG reports | `implementation-completion/stock-321cd46f/reports/extent-report.html`; `implementation-completion/stock-321cd46f/reports/testng-results.xml`; `implementation-completion/stock-321cd46f/reports/reporter-exit-statuses.json` |
| REVIEW remains failed TestNG assertion and rejects the gate | `implementation-triage/verify-d11d275d/reports/testng-results.xml`; `implementation-triage/verify-d11d275d/reports/reporter-exit-statuses.json` |
| Latest local verifier: 65 storage artifacts verified; five owned volumes removed | `implementation-triage/verify-d11d275d/reports/artifact-storage-validation.json`; `implementation-triage/verify-d11d275d/deployment-state.json` |
| Java 11 fresh standalone bridge compilation and seven scenarios | `implementation-triage/jdk11-checks.json`; `implementation-triage/jdk11-scenarios.log` |
| Upstream modules target 21; JDK 11 reports invalid target release: 21 | `implementation-completion/jdk11-certify-real-metadata.log`; `implementation-completion/jdk11-verify-real-metadata.log` |
| Python harness contracts, including expected failures, diff and parallel execution | `closeout/python-tests.xml`; `implementation-completion/triage-tests.xml` |
| Historical hosted implementation CI on its own revision | `github-source-publication/hosted-ci.json`; `github-source-publication/final-status.json` |
| Initial candidate hosted CI patch portability failure | `closeout/hosted-keymanager-failure.log`; `closeout/patch-line-ending-reproduction.json` |
| Original patch bytes restored; actual native keymanager build passed | `closeout/native-keymanager-build/build-provenance.json` |
| Runtime candidate hosted CI | `b2-scratch/retry1/pr-ci-status.json` |
| Managed GitHub-hosted Linux execution in private scratch repository | `b2-scratch/retry1/assessment.json` |
| Stable 1.0.x availability checked on 24 October 2026, none found in checked image repositories | `implementation-completion/registry-version-inventory.json`; `implementation-completion/upstream-release-inventory.json` |
| Allowed variants, actual metadata and selected mTLS probe: 2 PASSED, 4 FAILED, 1 INTERRUPTED | `closeout/a1-decision.json`; `closeout/variant-a3037a5d/issuer-plan-available.json`; `closeout/variant-a3037a5d/issuer-metadata.json`; `closeout/variant-a3037a5d/authorization-server-metadata.json` |
| Scratch hosted attempt: authorization and ubuntu-24.04 selection | `b2-scratch/run-state.json`; `b2-scratch/run-40164823727-logs.zip` |
| Workflow correction and hosted retry | `b2-scratch/retry1/final-workflow.diff`; `b2-scratch/retry1/assessment.json` |
| Hosted run: ten hosted services and both official plans execute | `b2-scratch/retry1/run-state.json`; `b2-scratch/retry1/run-40165722639-logs.zip` |
| Hosted run: expected stock/verifier counts with strict FAILED gates | `b2-scratch/retry1/artifact-12587654719/ci-summary.json` |
| Hosted run: native/consolidated reports and storage receipts uploaded | `b2-scratch/retry1/artifact-12587654719.zip`; `b2-scratch/retry1/artifact-12587788827.zip`; `b2-scratch/retry1/download-receipts.json` |
| Hosted run: storage read-back and cleanup | `b2-scratch/retry1/assessment.json`; `b2-scratch/retry1/artifact-12587788827/artifact-storage-validation.json` |
| Repository merge of PR #7 after five green CI jobs | `b3-closeout/merge-verification.json` |


## Exclusions and limits

Raw credential export ZIPs, private keys, generated configuration and `.env` files
are excluded from both source and this handoff. Two historical
`conformance-summary.json` files contain development private JWKs; retained
`stock-results.json` and `patched-results.json` receipts report their counts instead.
Original files have not been altered.

The following hashes identify preserved private originals outside this handoff:

| Private original outside this handoff | SHA256 |
|---|---|
| `implementation-completion/stock-321cd46f/reports/plan-UYoPyoeGriNRN-export.zip` | `a2c82ba986207e97ad851dbd982af73276fb9509a74d30dfd1baee19f66363e6` |
| `implementation-completion/stock-321cd46f/reports/plan-fnLpdorj2jZAD-export.zip` | `ef307ee6b3ae43aaa1399c6e3d0e21c05ee92e1b338e10e883107b5df4cd2b77` |
| `implementation-completion/patched-40d8d65d/reports/plan-yfOPDtRoNo2xZ-export.zip` | `8804b148233ab0f3f2047ba19b6c5ff0d9ec838ad3e92e9e5c53d23a964281d6` |
| `implementation-completion/patched-40d8d65d/reports/plan-Z4PgzIS2ImHJi-export.zip` | `f12edcb2de6d9546c3439f8e8788406bd2ac3e06197135c1b1fb2a0e127617c5` |
| `implementation-triage/verify-d11d275d/reports/plan-IpxODLyKkxZNN-export.zip` | `898cfa5579865efdc0d48761753fbefe75e655596f2b944f053aaa4a5b9a3a39` |
| `closeout/variant-a3037a5d/mtls-reports/plan-45vEXNrkMzWtm-export.zip` | `f4fb750388c3ec9ebd933c92a9ee1c71a074ff948cb050265ad4e6cb18f04dbd` |


Hosted raw official export ZIPs were not retained as GitHub artifacts. Their
verification in ephemeral MinIO is recorded, but offline reinspection is **not
verified**. The retained hosted log ZIP and two report artifacts are available
locally for the future handoff. They must not be described as raw official exports.

Independent empty-cache execution, POST/status-list interoperability and organizer
acceptance of integrated Java 21 remain outside the verified scope. See
[validation limits](../docs/VALIDATION.md) and the
[requirement checklist](../REQUIREMENTS_STATUS.md).
