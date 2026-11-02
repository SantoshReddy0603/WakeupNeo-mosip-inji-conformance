# Submission evidence index

Exact retained paths are listed in [the evidence handoff index](../evidence/README.md).
Historical entries refer to a separate local package. The current local-check
receipt is included in this repository.
Google Drive upload and reviewer access are **not verified**. Raw credential
exports, keys and generated configuration are excluded.

| Claim | Run or revision | Evidence in separate handoff | Status |
|---|---|---|---|
| Current reporting safety regressions and local syntax/bridge checks | Source hashes in receipt; 213 Python tests and seven JDK 11 scenarios | [`evidence/local-checks.json`](../evidence/local-checks.json), retained in this repository | verified locally; fresh live run not verified |
| Unified ten-service deployment and fresh volumes | `019bf015dcef47029010faa06a2cf788` | `implementation-completion/stock-321cd46f/commands.json`, `deployment-state.json` | verified |
| Stock Certify 2 PASSED / 10 INTERRUPTED / 3 SKIPPED; gate FAILED | Same run | `implementation-completion/stock-321cd46f/stock-results.json` | verified |
| Diagnostic patched issuer 12 PASSED / 3 SKIPPED; not stock qualification | `d39d9f65b0f04db79eb3d25501c9f26c` | `implementation-completion/patched-40d8d65d/patched-results.json` | verified |
| Native API-rig and consolidated TestNG/Extent reporting | Stock reference run | `implementation-completion/stock-321cd46f/reports/` receipts and combined reports | verified |
| Verifier 4 PASSED / 6 REVIEW; strict failed gate | `0d9b58120a964f628a34dd0c658d6c8f` | `implementation-triage/verify-d11d275d/results.json` and reporting receipts | verified |
| Verifier storage read-back and owned cleanup | Same run | `implementation-triage/verify-d11d275d/reports/artifact-storage-validation.json`, deployment receipt | verified |
| Standalone bridge JDK 11 compile and seven scenarios | Local JDK 11 check | `implementation-triage/jdk11-checks.json`, `jdk11-scenarios.log` | verified |
| Upstream modules require JDK 21 | Pinned upstream revisions in `docs/VALIDATION.md` | `implementation-completion/jdk11-certify-real-metadata.log`, `jdk11-verify-real-metadata.log` | verified |
| Python contracts: expected-failures, diff and parallel execution | Historical local regression, 196 passed | `closeout/python-tests.xml`, `implementation-completion/triage-tests.xml` | verified |
| Hosted implementation CI | `40165694278`, commit `9c8d94ad9da42ac458ea304192118266577469f9` | `b2-scratch/retry1/pr-ci-status.json` | verified |
| Hosted Linux deployment, plans, reports, storage and cleanup | Scratch run `40165722639`, same commit | `b2-scratch/retry1/assessment.json`, log ZIP and artifacts `12587654719`, `12587788827` | verified |
| Hosted counts match local stock and verifier reference | Official run `2583bed425d64f5abb0c86993d402116` | `b2-scratch/retry1/artifact-12587654719/ci-summary.json` | verified |
| Hosted raw official export offline inspection | Scratch run `40165722639` | Raw ZIP bytes were not retained in GitHub artifacts | not verified |
| Sender-constraining variants and mTLS probe | Plan `45vEXNrkMzWtm`: 2 PASSED / 4 FAILED / 1 INTERRUPTED | `closeout/a1-decision.json`, `closeout/variant-a3037a5d/` metadata | verified |
| End-to-end certificate-bound mTLS | Same partial plan | Bearer tokens lacked `cnf`; no complete qualification | not verified |
| Stable 1.0.x image availability check | 24 October 2026; not a current inventory | `implementation-completion/registry-version-inventory.json`, `upstream-release-inventory.json` | verified |
| Request URI POST and status-list interoperability | Verifier reproduction above | Coverage limitations in `docs/STOCK_CERTIFY_TRIAGE.md`; original export preserved privately | not verified |
| Independent empty-cache installation | No execution | Prepared commands in `docs/VALIDATION.md` | not verified |
| Official reviewer disposition or certification | No approval obtained | Six REVIEW outcomes preserved; `REVIEW_PROCESS.md` | external pending |
| Organizer acceptance of integrated JDK 21 | No answer obtained | Five-line question in `docs/VALIDATION.md` | external pending |
| Submission video, deck and accessible evidence handoff | No completed artifacts linked here | `DEMO_SCRIPT.md` is an instruction sheet, not a recording | external pending |

The hosted authorization job succeeded and its stock gate job failed because of
the preserved official outcomes. Both report artifacts were retained; 114 storage
objects were verified and five owned volumes were removed. Twenty-three retained
reports matched storage hashes. These facts validate automation, not conformance.

Original run `141a3630f7874e98ae4964653f953899` remains preserved. Later stock,
diagnostic and hosted executions are distinct runs, not replacements. Historical
checks do not establish validation of later source changes; use CI and local test
output for the exact revision under review.
