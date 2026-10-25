# Draft evidence index

This is a draft submission aid, not a certification claim. `EVIDENCE_ROOT` means the existing private `outputs/` directory associated with this project. Paths below beginning implementation-completion/, implementation-triage/, closeout/ or github-source-publication/ are relative to that directory; source paths are relative to the project root. Raw exports contain sensitive runtime material and are not included in this source-only folder. Reviewer access to that private evidence is **not verified**; grant controlled access before submission. Original run `141a3630f7874e98ae4964653f953899` remains preserved; the comparisons below identify separate runs.

| Claim | Run ID / check | Proving file or command output | Status |
|---|---|---|---|
| Unified ten-service deployment, fresh owned volumes | 019bf015dcef47029010faa06a2cf788 | implementation-completion/stock-321cd46f/commands.json; deployment-state.json | verified |
| Stock Certify: 2 PASSED, 10 INTERRUPTED, 3 SKIPPED; gate FAILED | 019bf015dcef47029010faa06a2cf788 | implementation-completion/stock-321cd46f/reports/plan-UYoPyoeGriNRN-export.zip; stock-results.json | verified |
| Patched issuer diagnostic: 12 PASSED, 3 SKIPPED; not stock qualification | d39d9f65b0f04db79eb3d25501c9f26c | implementation-completion/patched-40d8d65d/reports/plan-yfOPDtRoNo2xZ-export.zip; patched-results.json | verified |
| Stock combined: 6 PASS, 10 INTERRUPTED, 6 REVIEW, 3 SKIP; gate FAILED | 019bf015dcef47029010faa06a2cf788 | implementation-completion/stock-321cd46f/reports/conformance-summary.json | verified |
| Patched combined: 16 PASS, 6 REVIEW, 3 SKIP; gate FAILED | d39d9f65b0f04db79eb3d25501c9f26c | implementation-completion/patched-40d8d65d/reports/conformance-summary.json | verified |
| Latest local verifier: 4 PASSED, 6 REVIEW; gate FAILED | 0d9b58120a964f628a34dd0c658d6c8f | implementation-triage/verify-d11d275d/results.json; reports/plan-IpxODLyKkxZNN-export.zip | verified |
| Both real module OpenIDConformanceTest integrations and consolidated Extent/TestNG reports | 019bf015dcef47029010faa06a2cf788 | implementation-completion/stock-321cd46f/reports/existing-certify; existing-verify; extent-report.html; testng-results.xml; reporter-exit-statuses.json | verified |
| REVIEW remains failed TestNG assertion and rejects the gate | 0d9b58120a964f628a34dd0c658d6c8f | implementation-triage/verify-d11d275d/reports/testng-results.xml; reporter-exit-statuses.json | verified |
| Latest local verifier: 65 storage artifacts verified; five owned volumes removed | 0d9b58120a964f628a34dd0c658d6c8f | implementation-triage/verify-d11d275d/reports/artifact-storage-validation.json; deployment-state.json | verified |
| Java 11 fresh standalone bridge compilation and seven scenarios | JDK 11 local check | implementation-triage/jdk11-checks.json; jdk11-scenarios.log | verified |
| Upstream modules target 21; JDK 11 reports invalid target release: 21 | Pinned upstream sources, not a conformance run | implementation-completion/jdk11-certify-real-metadata.log; jdk11-verify-real-metadata.log; docs/VALIDATION.md cites upstream POM lines | verified |
| Organizer acceptance of integrated JDK 21 | No response obtained | docs/VALIDATION.md organizer question; not sent | external pending |
| Python harness contracts, including expected failures, diff and parallel execution | Local regression | closeout/python-tests.xml; earlier implementation-triage/triage-tests.xml has 196 passes | verified |
| Historical hosted implementation CI on its own revision | 39772274219; head 2594b3d6f9590caa9d28c6fa2048249ac300f274 | github-source-publication/hosted-ci.json; final-status.json | verified |
| Current candidate hosted CI | Not run when draft prepared | B1 authorized separately; completion must be checked against the published candidate SHA | not verified |
| Managed native GitHub-hosted Linux execution of this candidate | No run | docs/VALIDATION.md; .github/workflows/full-stack-conformance.yml | not verified |
| Request URI POST interoperability | 0d9b58120a964f628a34dd0c658d6c8f | implementation-triage/verifier-coverage.json: E1FPVnumrtRlZHU bypasses POST conditions; REVIEW screenshot branch | not verified |
| Status-list interoperability | 0d9b58120a964f628a34dd0c658d6c8f | implementation-triage/verifier-coverage.json: oTZgMqIEscOyRW9 has no status reference and statusCheck=[] | not verified |
| Stable 1.0.x availability checked on 24 October 2026, none found in checked image repositories | Dated inventory, not refreshed | implementation-completion/registry-version-inventory.json; upstream-release-inventory.json | verified |
| Empty-cache independent installation | No run | docs/VALIDATION.md prepared commands; no destructive cleanup executed | not verified |
| Official review disposition or certification | No approval obtained | REVIEW_PROCESS.md; six official REVIEW outcomes retained | external pending |
| This proposed 5–7 minute video | Not recorded | submission/DEMO_SCRIPT.md is a draft shot list | not verified |

| Allowed variants, actual metadata and selected mTLS probe: 2 PASSED, 4 FAILED, 1 INTERRUPTED | Official partial plan 45vEXNrkMzWtm | closeout/a1-decision.json; closeout/variant-a3037a5d/issuer-plan-available.json, issuer-metadata.json, authorization-server-metadata.json and mtls-reports/plan-45vEXNrkMzWtm-export.zip | verified |
| Certificate-bound mTLS end-to-end qualification | Same partial plan | Observed token_type=Bearer, missing token cnf; no complete plan qualification | not verified |
