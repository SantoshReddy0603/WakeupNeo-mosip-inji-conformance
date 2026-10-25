# Architecture and API automation

Bash and PowerShell select profiles from one docker/docker-compose.yml containing the suite, issuer, verifier and MinIO. Components retain independent databases and gates. A shared TLS ingress reuses existing routes and Docker DNS for the unchanged advertised hostname, publishing only loopback host ports. The isolated launcher generates a run-specific configuration and verifies ownership before cleanup.

The supported development course credential comes from Certify's actual PostgreSQL data-provider plugin and synthetic course-completion rows. Authentication uses real registered Keycloak clients and users. Generated development keys, private wallet JWKS, realm imports and runtime configuration are excluded from the distributable archive. The passing issuer evidence applies to the pinned native-positive product build and its supplied patches. The untouched stock image is a reproducible baseline, not an equivalent passing implementation.

The runner imports the vendored official conformance.py library, also used by upstream run-test-plan.py. It does not invoke run-test-plan.py itself. The vendored license and hash provenance remain unchanged.

## Programmatic plan lifecycle

1. Render the selected JSON template with configured endpoints, actual wallet keys and variants. Reject missing configuration. Generate an independent alias unless one is explicitly supplied.
2. Use the unmodified pinned OIDF `scripts/conformance.py` library to create/configure each plan. Read the returned module list and reject absent or duplicate module/variant pairs.
3. Create and start the real instances using the upstream API, then poll module information with bounded deadlines. A running or waiting instance cannot pass on an interim result.
4. When the suite requests interaction, Certify's browser flow completes real authorization and consent. Verify uses native DCQL/QR/UI transaction handling and submits genuine evidence to the requesting official instance. No protocol translation is performed.
5. Preserve raw official statuses, retrieve logs and download the original plan ZIP. Reject corrupt or empty exports. Classify only eligible documented FAILED exceptions as EXPECTED_FAILURE; REVIEW, TIMEOUT and operational errors remain failures.
6. Write component summaries, the consolidated decision and badges, then feed those exact results into both actual module TestNG reporters and the standalone Extent/TestNG lifecycle. A failed conformance gate still produces reports and a nonzero exit.

## Isolation and result policy

`--parallel 2` schedules independent component plans concurrently, using separate clients, sessions, aliases and upstream event loops. Explicit duplicate aliases are rejected before the second plan is created. Modules within each plan stay serial because their aliases and sessions are shared. Local HTTP integration fixtures measure this concurrency and check that a failed component does not discard the other component's artifacts. Fixtures are explicitly not official conformance evidence.

PASSED/WARNING map to TestNG PASS; SKIPPED/EXPECTED_FAILURE map to SKIP; FAILED, REVIEW, TIMEOUT, ERROR, INTERRUPTED, CANCELLED and unknown outcomes map to FAIL. A component needs a genuine pass/warning, no unacceptable outcomes and a valid export. Exceptions produce BASELINE_ACCEPTED, never an official PASS. A removed test or degradation of a previously passing test rejects the comparison gate. The TestNG gate tests explain why XML totals exceed official module totals.

The existing commons HTML reporter clears its passed-result map while generating its filtered report. The installed preserving adapter restores the same actual result objects after report generation, so subsequent TestNG XML retains every status. It does not change any result status.

## Retained validation and storage

`--existing-run` only reads official plans/instances. It verifies identity, status, mapping and gates and creates a separate validation output directory. Component selection projects only that component's already-established outcomes; the original combined gate and summary remain preserved separately. All original inputs retain their hashes and timestamps. `--diff` compares genuine retained results without rerunning or approving them. Derived reports and badges are labelled retained validation.

Native and consolidated artifacts are uploaded and read back byte-for-byte. Fresh runs use `openid-conformance/<run_id>/`; retained checks use `openid-conformance-validation/<run_id>/<validation_id>/`. The uploader includes only current artifact IDs and report files, excluding stale unrelated logs. Original screenshots are never modified.

## Deliverable boundaries

The api-test modules are in the current pinned Inji repositories and use mosip-functional-tests commons. Installation adds OpenIDConformanceTest and its suite entry to both actual master suites. The wrapper can automatically check out absent repositories and compile the integrations, or reuse explicitly configured pinned checkouts and actual Maven-generated dependency classpaths.

The GitHub workflow uses this same lifecycle, validates the harness/native fixes/module compilation, and authorizes production-release/default-branch manual revisions on hosted Linux, then prepares the live gate on hosted Linux for reachable or managed deployments, with an explicitly selected dedicated Linux runner as an alternative. Historical hosted CI and a release-triggered live execution are recorded separately. The live execution generated reports and storage evidence while the strict combined gate failed on REVIEW. A changed revision or another environment requires new validation. Combined execution validates two independent plans; it does not claim interoperability between the course credential and the verifier plan's PID fixture. See REQUIREMENTS_STATUS.md for scoped evidence and REVIEW_PROCESS.md for review limits. REVIEW_PROCESS.md includes the self-certification procedure. It does not authorize certification or changing the selected plan.
