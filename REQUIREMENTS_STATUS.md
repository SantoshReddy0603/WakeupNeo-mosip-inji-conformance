# Assignment requirement checklist

Verified means the stated scope has actual evidence; it does not mean the product conforms. Official stock run S = `019bf015dcef47029010faa06a2cf788`; diagnostic, patched build run P = `d39d9f65b0f04db79eb3d25501c9f26c`. Stock issuer export: `plan-UYoPyoeGriNRN-export.zip`; stock verifier export: `plan-fnLpdorj2jZAD-export.zip`; patched issuer export: `plan-yfOPDtRoNo2xZ-export.zip`; patched verifier export: `plan-Z4PgzIS2ImHJi-export.zip`. Original run `141a3630f7874e98ae4964653f953899` is preserved and not replaced by these comparisons.

Local test outputs are retained under `implementation-triage/` outside this source-only package. Preserved deployment/report/storage/compiler records are under `implementation-completion/`. Evidence filenames below refer to those directories, not invented runs.

| ID | Requirement | Status and exact evidence | Unverified or external portion |
|---|---|---|---|
| M1 / D1 | One Compose file for suite, Certify, Verify and storage | verified: S and P, commands.json, deployment-state.json; ten services and five fresh owned volumes | verified: scratch hosted run 40165722639 at 9c8d94ad9da42ac458ea304192118266577469f9; ten services started |
| M2 | Official REST create/configure/execute/poll/retrieve | verified: S/P official exports named above; actual component reports and conformance-summary.json | not verified: arbitrary other profiles |
| M3 | OpenIDConformanceTest in both actual API rigs | verified: S/P reports/existing-certify and reports/existing-verify, reporter-exit-statuses.json on Java 21 | external pending: organizer acceptance of current upstream module locations and Java 21 |
| M4 | Correct TestNG result mapping, Extent and strict gates | verified: S/P native/consolidated XML and HTML; triage-tests.xml plus actual JDK 11 seven-scenario output | not verified: any official REVIEW approval; no waiver added |
| M5 | Combined cross-module reports | verified: S/P reports/extent-report.html, testng-results.xml and failed combined gate | not verified: course-to-PID interoperability, which combined execution does not establish |
| M6 | One-command certify, verify and combined modes | verified: S/P full-stack combined commands.json; triage-tests.xml CLI checks and shell syntax outputs | not verified: fresh individual Certify live rerun in this task or PowerShell end-to-end runtime |
| G1 / D4 | CI/CD workflow implementation | verified: workflow-policy.log and actionlint.log, both exit 0 | verified: ordinary CI 40165694278 and scratch B2 40165722639; verified: B3 PR #7 merged at fd89d1f4d8e960e5ad3f0fdb7b2fb975f70d41be after CI 40177192785; conformance gate still FAILED |
| G2 | Selective component and plan configuration | verified: triage-tests.xml runner contracts; S/P actual selected plans | not verified: other profiles, which were not substituted |
| G3 | Expected-failure handling | verified: triage-tests.xml contract cases; empty config/expected-failures.json retained | not verified: real exemptions; none applied |
| G4 | Cross-run regression diff | verified: triage-tests.xml diff contract cases | not verified: a new live regression scenario in this task |
| G5 | Setup, architecture and API documentation | verified: source-checks.json local link/AST checks and syntax outputs; S/P support documented routes | not verified: completely cold independent installation |
| B1 | Parallel component execution | verified: S/P commands.json parallel 2 and both real plan exports | not verified: parallel modules inside one plan; not claimed |
| D2 | Issuer and verifier 1.0 plan JSON templates | verified: S/P exports record exact templates/variants; verifier remains oid4vp-1final-verifier-test-plan | external pending: upstream stable 1.0.x availability; registry-version-inventory.json from 24 October 2026 lists no stable 1.0.x images |
| D3 | run-full-stack-conformance.sh | verified: S/P commands.json plus shell-full.log exit 0 | not verified: empty-cache execution |
| D5a | Architecture explanation | verified: source-checks.json links and S/P observed service graph | not verified: hosted host-gateway; absent intentionally because internal DNS alias routes to ingress |
| D5b | REST API automation explanation | verified: API_REFERENCE.md, S/P actual exports and triage-tests.xml client contracts | not verified: unused API routes |
| D5c | Native component handoffs and evidence | verified: S/P official logs, native transaction IDs and captured screenshot exports | not verified: POST wallet_nonce or status-list coverage in these fixtures |
| D5d | Self-certification procedure | verified: REVIEW_PROCESS.md source deliverable, source-checks.json | external pending: applicable official review, authorized signature/payment/submission/acceptance; not performed |
| D5e | Troubleshooting | verified: docs/STOCK_CERTIFY_TRIAGE.md exact S/P export messages and source-checks.json | not verified: resolving product gaps through configuration; no such claim |
| C1 | Java 11 standalone bridge | verified: fresh-jdk11-validation.json and fresh-jdk11-testng.log; new jdk11-checks.json/jdk11-scenarios.log record this task's actual rerun | external pending: upstream modules target 21; exact compiler failures and POM lines in docs/VALIDATION.md |
| C2 | MinIO/S3 artifact lifecycle and integrity | verified: S/P artifact-storage-validation.json and independent storage-integrity.json, cleanup exit 0 | not verified: separate cloud S3 provider |
| C3 | Stock release qualification | verified: S reports 2 PASSED, 10 INTERRUPTED, 3 SKIPPED; gate FAILED; all ten classified PRODUCT_GAP from exports | external pending: native product changes; patched P issuer PASS does not qualify stock |
| C4 | Verifier qualification | verified: S/P report 4 PASSED, 6 REVIEW; gate FAILED | external pending: applicable official review; not verified: native POST and status-list interoperability |
| C5 | Fully empty-cache machine | not verified: prepared exact command sequence in docs/VALIDATION.md only | external pending: explicit approval; destructive prune not executed |

Local Python regression output `triage-tests.xml`: 196 passed, 31 deprecation warnings, exit 0. Shell and workflow syntax outputs exit 0; PowerShell parser output is recorded in `source-checks.json`. These checks validate harness behavior and source, not stock product conformance. The ten interruptions remain product findings; no stock patch, expected-failure exemption, mapping change or gate-policy change was made.

Fresh local verifier execution is verified by run `0d9b58120a964f628a34dd0c658d6c8f`, export `plan-IpxODLyKkxZNN-export.zip`: 4 PASSED, 6 REVIEW, verifier gate FAILED. `verifier-coverage.json` records POST-named instance `E1FPVnumrtRlZHU` and happy-flow instance `oTZgMqIEscOyRW9`; actual native POST and status-list interoperability remain not verified.

Sender-constraining inspection is verified by closeout/a1-decision.json and official selected-case plan `45vEXNrkMzWtm`, export `plan-45vEXNrkMzWtm-export.zip`: allowed dpop/mtls, no unconstrained Bearer; mTLS-labelled probe 2 PASSED, 4 FAILED, 1 INTERRUPTED. End-to-end mTLS binding remains not verified because issued tokens lacked cnf. No default/profile/gate change was made.

Initial B2 attempt 40164823727: **not verified at that point**, superseded by the successful implementation retry below. Scratch run `40164823727` at commit `ce7a50e81cdea4081fa1061573e24c8d76094d68` passed authorization and built integrations on ubuntu-24.04, but image preparation failed before startup because empty inherited AWS variables overrode docker/.env. Zero official plans executed and zero artifacts uploaded; stack/reports/storage/cleanup and expected result counts remain not verified. See docs/VALIDATION.md and b2-scratch/run-state.json/log ZIP. Two proposed diffs remain unapplied; no rerun or merge occurred.


## Verified B2 scratch implementation run

B2 is **verified** under the owner's implementation criteria: scratch run `40165722639`, candidate `9c8d94ad9da42ac458ea304192118266577469f9`, official run `2583bed425d64f5abb0c86993d402116`. All ten services started on ubuntu-24.04; issuer plan `vir0sD8It1IDI` and verifier plan `UZtgjxUuLpdPj` executed; Certify 2 PASSED / 10 INTERRUPTED / 3 SKIPPED and Verify 4 PASSED / 6 REVIEW match the reference. Native and consolidated reports were uploaded in two GitHub artifacts, storage verified 114 objects, and five owned volumes were removed with none remaining. Evidence: b2-scratch/retry1/assessment.json, ci-summary.json inside artifact-12587654719, reports/receipts inside artifact-12587788827, and original run log ZIP. Twenty-three downloaded report files matched storage hashes. Authorization job passed; gate job failed solely on the expected strict result rejection; all three reporters exit 1. These are actual FAILED conformance gates, not waivers.

Ordinary PR CI `40165694278` passed on the same candidate. The single authorized retry is complete; no further retry, merge, release or scratch deletion occurred. Raw hosted official export bytes were verified in ephemeral MinIO but not retained as GitHub artifacts; later offline raw-export inspection is not verified. The observed hosted issuer image ID differs from the earlier local ID, so byte-identical release reproducibility is not verified. B4 independent empty-cache run, organizer acceptance of JDK 21 and final submission materials remain pending. See docs/VALIDATION.md for per-criterion evidence and cleanup-log/state distinctions.

## Retained B2 evidence for B3

B2 is verified only for private scratch repository `SantoshReddy0603/inji-conformance-b2-scratch`, run `40165722639`, commit `9c8d94ad9da42ac458ea304192118266577469f9`; it was not a main-repository run. The previously downloaded logs and both artifacts were copied into private `EVIDENCE_ROOT/b3-closeout/evidence/` and rechecked against their download SHA256 receipts and ZIP CRCs. `manifest.json` records their hashes and source run; `assessment.json` records the five verified B2 implementation criteria. This evidence folder is separate from the source repository and must accompany a controlled evidence handoff.

| Retained file | Evidence |
|---|---|
| b3-closeout/evidence/run-40165722639-logs.zip | Complete hosted workflow logs |
| b3-closeout/evidence/artifact-12587654719.zip | live-conformance-results: summary and report |
| b3-closeout/evidence/artifact-12587788827.zip | managed-reporting-evidence: native/consolidated reports, storage and cleanup receipts |

The strict conformance gates remain FAILED; raw hosted official export ZIP bytes were not retained in these artifacts. B3 approval covers final documentation publication and a merge only after all CI jobs pass on the final PR head; B4, further live runs and scratch deletion remain unperformed.

Final source comparison and evidence handoff audit: docs/VALIDATION.md and submission/EVIDENCE_INDEX.md record the documentation-only difference from B2 commit 9c8d94ad9da42ac458ea304192118266577469f9. Evidence handoff mapping: evidence/README.md; private audit: EVIDENCE_ROOT/final-sync/evidence-audit.json. B3 was verified by b3-closeout/merge-verification.json; B4 remains not verified.
