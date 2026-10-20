# Automated Inji conformance harness

This project runs real OpenID Foundation issuer/verifier test plans, maps results into TestNG and ExtentReports, exports official plan archives, and gates releases. Production entry points have no mock mode or fallback service. Controlled HTTP fixtures live only under `tests/`; their results validate the harness, not Inji conformance.

See [SETUP.md](SETUP.md) for local deployment, [REQUIREMENTS_STATUS.md](REQUIREMENTS_STATUS.md) for the complete evidence checklist, [ARCHITECTURE.md](ARCHITECTURE.md) for API automation and handoffs, and [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for failure diagnosis. [REVIEW_PROCESS.md](REVIEW_PROCESS.md) explains the external review and self-certification boundaries.

## Local checks

```sh
python -m pip install -r runner/requirements-dev.txt
python -m pytest tests -q
mvn -f testrig/pom.xml test-compile
```

## Prepare and start the official suite

```sh
python runner/setup.py
docker compose --env-file docker/.env -f docker/docker-compose.yml up -d --build
```

The suite is built from upstream commit `11999aad62ec292f36101410d9d5b761d44903ff`, with its real Git metadata. The build needs Java 21 inside Docker; the bridge targets Java 11. The local HTTPS endpoint is `https://localhost:8443`.

## Run against real configured Inji services

Configure the files/environment described in SETUP.md, then:

```sh
bash run-conformance.sh --component certify --skip-docker --insecure
bash run-conformance.sh --component verify --skip-docker --insecure
bash run-conformance.sh --combined --skip-docker --insecure
```

PowerShell supports `-Component certify`, `-Component verify`, `-Combined`, `-SkipDocker`, and `-Insecure`. `--insecure` / `-Insecure` explicitly permits a local self-signed certificate. Use `CA_BUNDLE` for a trusted TLS setup.

Omit `--skip-docker` to launch the real local course issuer, Keycloak, selected verifier, official suite and MinIO. Secrets, real signing keys and application registrations are generated automatically. The course credential uses the official PostgreSQL data-provider plugin. Maven is required unless you explicitly choose `--runner-only` / `-RunnerOnly`. Use `--native-positive` / `-NativePositive` for all verified native Certify/key-manager fixes. Latest official run: Certify 12 PASS/3 optional SKIP; Verify 4 PASS/6 REVIEW. The combined gate remains failed. See SETUP.md for backed-up development key rotation.

Modules execute serially within a plan because the suite shares aliases/session state. `--parallel 2` can run the two combined component plans concurrently using independent HTTP sessions.

## Output and release policy

Outputs go under `reports/` or an explicit `--reports-dir`: consolidated and per-component JSON, raw test logs, official ZIP exports, SVG status badges, native HTML and Extent HTML. TestNG XML is copied from `testrig/target/surefire-reports/` into that output directory. Configured S3/MinIO uploads use `openid-conformance/<run_id>/` inside S3_BUCKET; retained validation uses a separate namespace and preserves original official artifacts.

A component needs at least one pass/warning, no unapproved failures, and a valid official export. REVIEW, TIMEOUT, ERROR, INTERRUPTED, and CANCELLED fail. Expected failures need a reason, real issue reference, explicit FAILED status, and unexpired date; the shipped list is empty. An all-exception/all-skip run fails. A result diff also fails for any removed test or degradation of a previously passing test. Report, badge, and exit status are written after that decision.

Standalone Maven executes a fresh runner by default. Report consumption requires `-Dconformance.consumeReport=true`, `-Dconformance.summary=<path>` and the matching `-Dconformance.runId=<id>`. This prevents old reports from passing a new build.

## CI

The workflow tests Python, both native product fixes and both existing-module Java integrations on pull requests. Live release checks require a self-hosted runner labeled `inji-conformance` with connectivity to the real deployment and configured repository variables/secrets. Live failures are fatal; the workflow uploads artifacts even when the gate fails. No live conformance claim is inferred from unit tests.
