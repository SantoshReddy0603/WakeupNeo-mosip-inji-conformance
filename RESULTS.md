# Project status

The project automates the official issuer and verifier test plans, integrates both existing api-testrigs, generates native TestNG/Extent and combined reports, validates MinIO storage and supports component selection, parallel execution, expected-failure rules, regression comparison and GitHub Actions.

Latest verified official run: 0183b076faa14f69aa2aa67f08d9a3f4. Certify plan RlhCGTYnoEqcH: 12 PASS and 3 optional SKIP, gate PASSED. Verify plan PwUs9TdCQg6ue: 4 PASS and 6 REVIEW, gate FAILED. Combined: 16 PASS, 6 REVIEW and 3 SKIP, gate FAILED. Verifier target: oid4vp-1final-verifier-test-plan. No REVIEW outcome is a PASS.

Hosted CI run 39716320075 passed all five jobs. Release-triggered workflow 39717011976, attempt 2, executed 12 services, the real plans, native reporting, 115 MinIO upload/read-backs, restricted artifact upload and owned cleanup. Native reporter exits: Certify 0, Verify 1, combined 1. A separate storage observer exited 1 after racing automatic cleanup and is not counted as passed. The temporary runner unregistered after completion.

The first release attempt failed before official tests because a temporary launch helper's restrictive file-creation mask made database initialization files unreadable. The launch helper was corrected; the retry used unchanged project logic. That failed attempt is not a conformance result.

Limits: six unresolved official REVIEW outcomes; request URI POST coverage not established; completely empty Docker/Maven caches on a separate machine unverified; required-reviewer enforcement unavailable on the current private repository plan. The unrelated complete master functional suites were not executed. Full OpenID certification is not claimed.

This folder contains source, tests, configuration and operating documentation. Execution artifacts are stored separately. Fresh official run 901c0cb782044f6da8790f2144cf3073 verified the implementation: Certify returned 12 PASS and 3 optional SKIP; Verify returned 4 PASS and 6 REVIEW. The combined conformance gate remains FAILED.

Use SETUP.md to run locally, RUNNER_OPERATIONS.md for approved ephemeral runner operation, ARCHITECTURE.md for integration details and REVIEW_PROCESS.md for result handling.
