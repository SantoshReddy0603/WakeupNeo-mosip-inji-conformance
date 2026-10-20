> Stage 18: 124 Python tests, 49 native Certify tests, 3 native key-manager tests, both native 11-status mapping validators and seven standalone TestNG contract scenarios passed locally. Hosted/live workflows are separated and pinned. Native Request URI POST returned 405 (Allow: GET); it remains unsupported. Published to ci/stage-18 in draft PR #1; hosted CI verification is recorded in the PR Actions checks and the local Stage 18 delivery report. See CI_CD_SETUP.md and REQUEST_URI_POST_STATUS.md. Earlier dated runs below remain historical; combined official gate stays FAILED.

# Results — Stage 17

Original reference `141a3630f7874e98ae4964653f953899` and Stage 16 serial evidence preserved byte for byte. Fresh official combined parallel run `c4633b091cdd4b8eb4facd3c36986c94`: Certify plan `qJ6tKNfFZCfzm`, Verify plan `tSq9qkf5JI4G6`. Exact target `oid4vp-1final-verifier-test-plan` retained.

| Execution | Kind | Official counts | Gate | TestNG P/F/S | S3 objects verified |
|---|---|---|---|---|---|
| fresh | fresh_official_parallel_execution | 16 PASSED, 6 REVIEW, 3 SKIPPED | FAILED | 16/7/3 | 115 |
| retained-certify | retained_retrieval_no_new_plan | 12 PASSED, 3 SKIPPED | PASSED | 13/0/3 | 81 |
| retained-verify | retained_retrieval_no_new_plan | 4 PASSED, 6 REVIEW | FAILED | 4/7/0 | 89 |
| retained-combined | retained_retrieval_no_new_plan | 16 PASSED, 6 REVIEW, 3 SKIPPED | FAILED | 16/7/3 | 116 |

Issuer gate PASSED: 12 PASS / 3 optional SKIP. Verify gate FAILED: 4 PASS / 6 REVIEW. Combined gate FAILED: 16 PASS / 6 REVIEW / 3 SKIP. Combined TestNG adds the failing release assertion: 16 PASS / 7 FAIL / 3 SKIP. In combined native module reporting the Certify release assertion also checks the combined gate; its nonzero reporter exit is not an issuer protocol failure.

117 harness tests passed (106 existing + 11 new audit regression cases), no failures/skips. Workflow actionlint passed with shellcheck disabled; no shellcheck or remote CI success claimed. Fresh parallel command exited 1, retained Certify-only 0, retained Verify-only 1, retained combined 1. Evidence audits exited 0; all six actual uploaded images matched suite bytes and native IDs. MinIO uploaded and read back genuine artifacts; exact counts and SHA-256 checks are in the evidence. Local CI export succeeded without replacing failed gates. The original and fresh 25 official statuses are unchanged.

Minimal runtime changes: `runner/audit_verifier_review.py` fails closed on changed/nonfinal official status and contradictory native failure fields, and structurally inspects available status references without claiming signature validation; `runner/verifier_browser.py` records actual SDK response URL/time; `tests/test_review_audit.py` adds 11 regressions. No native protocol or official suite change was justified by the six transactions.

See [six-case findings](REVIEW_FINDINGS.md), [draft email, NOT SENT](OIDF_CLARIFICATION_DRAFT.md), [requirement checklist](REQUIREMENTS_STATUS.md), [illustrated report](outputs/stage-17-review-resolution/FINAL_REPORT.html), [commands/exits](outputs/stage-17-review-resolution/evidence/checks/commands.json), [official outcomes](outputs/stage-17-review-resolution/official-outcomes.json). All screenshots are genuine; exported logs are sanitized with hashes. Originals remain private.

Limitations: status-list revocation interoperability was not exercised; this general alpha plan is outside certification and a legitimate authoritative review disposition path remains externally pending. Remote Actions is deferred; clean empty-volume deployment, empty Maven cache, full upstream master suite and native Windows Java execution were not newly verified. Stage 16 clean native tests (49 Certify, 3 keymanager) remain historical; native source was not changed or rebuilt this stage. No email was sent, no remote repository created, no certification claimed. No new user credentials are needed for the completed local work.

**Additional confirmed coverage blocker:** Request URI POST/wallet_nonce coverage is not established: this url_query run bypassed the named module's POST fetch override; native request URI support is tied to a different DID scheme. Applicable upstream assessment or further explicitly authorized compatible native work is required. The official REVIEW is preserved. This corrects any earlier implication that a named POST module result alone verified POST support.
