# Evidence handoff

The source repository contains this index only. The retained private handoff folder is `EVIDENCE_ROOT/final-sync/evidence/`, where EVIDENCE_ROOT is the project outputs directory. Paths in the table are relative to that handoff folder. They are actual copied outputs, not newly executed tests. SHA256 receipts and existence checks are in private `EVIDENCE_ROOT/final-sync/evidence-audit.json`. Reviewer access is not verified until this folder is handed over through a controlled channel.

B2 ran on scratch repository `SantoshReddy0603/inji-conformance-b2-scratch`, run `40165722639`, commit `9c8d94ad9da42ac458ea304192118266577469f9`; it did not run on the original repository. All five implementation criteria passed; strict conformance gates remain FAILED. B2 artifacts and logs are retained locally, so access does not depend on the private repository's artifact retention.

The deployment and REST rows support the Compose and official runner deliverables; native/consolidated reports support TestNG/Extent integration and combined execution; storage receipts support artifact handling; JDK and regression outputs support compatibility and harness checks; hosted receipts support CI/CD.

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
| Approved workflow correction and one B2 retry | `b2-scratch/retry1/final-workflow.diff`; `b2-scratch/retry1/assessment.json` |
| B2: ten hosted services and both official plans execute | `b2-scratch/retry1/run-state.json`; `b2-scratch/retry1/run-40165722639-logs.zip` |
| B2: expected stock/verifier counts with strict FAILED gates | `b2-scratch/retry1/artifact-12587654719/ci-summary.json` |
| B2: native/consolidated reports and storage receipts uploaded | `b2-scratch/retry1/artifact-12587654719.zip`; `b2-scratch/retry1/artifact-12587788827.zip`; `b2-scratch/retry1/download-receipts.json` |
| B2: storage read-back and cleanup | `b2-scratch/retry1/assessment.json`; `b2-scratch/retry1/artifact-12587788827/artifact-storage-validation.json` |
| B3 merge of PR #7 after five green CI jobs | `b3-closeout/merge-verification.json` |

## Exclusions and limits

Raw credential export ZIPs, private keys and .env files are excluded from this handoff folder and from the source commit. Original private exports below were located and hashed; they were not modified or copied into the handoff. Controlled raw-export inspection requires a separate authorized private handoff. This reconciles the request to check those originals with the requirement to exclude raw credential exports.

| Private original outside this handoff | SHA256 |
|---|---|
| `implementation-completion/stock-321cd46f/reports/plan-UYoPyoeGriNRN-export.zip` | `a2c82ba986207e97ad851dbd982af73276fb9509a74d30dfd1baee19f66363e6` |
| `implementation-completion/stock-321cd46f/reports/plan-fnLpdorj2jZAD-export.zip` | `ef307ee6b3ae43aaa1399c6e3d0e21c05ee92e1b338e10e883107b5df4cd2b77` |
| `implementation-completion/patched-40d8d65d/reports/plan-yfOPDtRoNo2xZ-export.zip` | `8804b148233ab0f3f2047ba19b6c5ff0d9ec838ad3e92e9e5c53d23a964281d6` |
| `implementation-completion/patched-40d8d65d/reports/plan-Z4PgzIS2ImHJi-export.zip` | `f12edcb2de6d9546c3439f8e8788406bd2ac3e06197135c1b1fb2a0e127617c5` |
| `implementation-triage/verify-d11d275d/reports/plan-IpxODLyKkxZNN-export.zip` | `898cfa5579865efdc0d48761753fbefe75e655596f2b944f053aaa4a5b9a3a39` |
| `closeout/variant-a3037a5d/mtls-reports/plan-45vEXNrkMzWtm-export.zip` | `f4fb750388c3ec9ebd933c92a9ee1c71a074ff948cb050265ad4e6cb18f04dbd` |

No primary evidence file in the audited verified-claim mapping was missing after correcting the stale triage-tests.xml path. Raw hosted B2 official exports were not retained by the workflow and remain not verified for offline inspection. B4, organizer acceptance of upstream Java 21, actual request URI POST and status-list interoperability remain not verified or external pending. Standalone Java 11 execution is verified by the listed logs; acceptance of integrated Java 21 is external pending. No official result, gate, default or protocol behavior was changed.

Two historical conformance-summary.json files contain embedded development private JWKs and are excluded from this handoff. Existing stock-results.json and patched-results.json receipts prove the combined outcomes instead; the originals remain unchanged outside this folder.
