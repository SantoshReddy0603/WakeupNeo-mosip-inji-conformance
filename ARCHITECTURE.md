# Architecture and API automation

The Bash and PowerShell entrypoints orchestrate the existing service manifests and then invoke the runner and report lifecycle. The manifests retain separate Compose project identities and persistent volumes: the suite provides MongoDB, the official server and HTTPS httpd; Certify provides its PostgreSQL source, Keycloak and issuer; Verify provides its database, native API and UI; storage provides MinIO. Component manifests use the suite network. This is one coordinated local environment with multiple manifests, preserving existing deployment data.

The supported development course credential comes from Certify's actual PostgreSQL data-provider plugin and synthetic course-completion rows. Authentication uses real registered Keycloak clients and users. Generated development keys, private wallet JWKS, realm imports and runtime configuration are excluded from the distributable archive. The passing issuer evidence applies to the pinned native-positive product build and its supplied patches. The untouched stock image is a reproducible baseline, not an equivalent passing implementation.

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

The GitHub workflow uses this same lifecycle, validates the harness/native fixes/module compilation, and authorizes production-release/default-branch manual revisions on hosted Linux, then runs the live gate on hosted Linux for reachable deployments or a dedicated Docker Desktop-connected runner for managed local services. Ordinary hosted CI passed; live GitHub execution remains unverified pending an approved main deployment and authorized environment. Combined execution validates two independent plans; it does not claim interoperability between the course credential and the verifier plan's PID fixture. See REQUIREMENTS_STATUS.md for evidence and REVIEW_PROCESS.md for the external review and self-certification procedure.
