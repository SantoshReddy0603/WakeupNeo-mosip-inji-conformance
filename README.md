# Automated Conformance Testing for Inji Certify and Inji Verify

Run the OpenID Foundation conformance suite against real Inji services, feed official outcomes into both existing API test rigs, and produce consolidated reports with strict release gates.

![Architecture: official suite, real issuer and verifier, native reporting, storage and gates](docs/images/architecture.svg)

## What the project provides

- Docker Compose orchestration for the official suite, Inji Certify, Inji Verify, Keycloak, PostgreSQL, MongoDB and MinIO.
- Official REST API automation to configure plans, execute modules, poll outcomes and retrieve exports.
- `OpenIDConformanceTest` integration in both existing api-testrigs, with TestNG and Extent reporting.
- Certify-only, Verify-only and combined execution; independent component gates and consolidated results.
- Real PostgreSQL-backed synthetic course issuance, native security fixes and genuine browser evidence capture.
- Artifact upload and byte-for-byte read-back, regression comparison, selective plans and parallel component execution.
- Hosted CI plus an actual release-triggered full-stack workflow, with artifacts retained on benchmark failure.

## Verified results

![Recorded conformance outcomes: Certify 12 PASS and 3 SKIP; Verify 4 PASS and 6 REVIEW; combined gate FAILED](docs/images/recorded-results.svg)

Latest recorded manual run: `ec11687365de477282d0f8c2d0e8d4fb`.

| Component | Official results | Gate | Reporter exit |
|---|---|---|---:|
| Certify | 12 PASS, 3 optional SKIP | PASSED | 0 |
| Verify | 4 PASS, 6 REVIEW | FAILED | 1 |
| Combined | 16 PASS, 6 REVIEW, 3 SKIP | FAILED | 1 |

The manual run verified 115 uploaded artifacts and cleaned up its twelve services and five owned volumes. A separate full validation passed all 182 harness tests and independently read back 72 core stored artifacts. Component and combined native TestNG/Extent reports were generated.

**REVIEW remains REVIEW.** The harness maps it to a failed TestNG assertion and rejects the release gate. It does not manufacture PASS results. TestNG includes an extra gate assertion, so its counts differ from the official module counts. These results establish working automation, not complete OpenID conformance or certification. The diagrams summarize recorded results; official outputs remain authoritative.

## Requirements

The validated environment is Windows with Ubuntu/WSL, Docker Desktop Linux containers and Ubuntu integration, Python 3.12, Java 21 and Maven 3.8.7. Use at least 6 GiB of Linux memory; the tested environment had about 7.6 GiB. Keep ports `8443`, `8445`, `8446`, `9000` and `9001` available.

Internet access is required for upstream source, images, Maven dependencies and the matching Playwright browser. No external issuer account, real personal records or GitHub token is needed for local synthetic issuance. Native hosted Linux networking has not been validated for these manifests.

## Prepare the environment and images

Run inside Ubuntu/WSL from this repository. Keep the virtual environment outside the source tree:

```bash
umask 022
python3 -m venv ~/inji-conformance-venv
source ~/inji-conformance-venv/bin/activate
python -m pip install -r runner/requirements-dev.txt
python -m playwright install --with-deps chromium
export PYTHON="$(command -v python)"
export CONFORMANCE_RESOLVE_LOCAL=true
docker info
docker compose version
```

Prepare the pinned native images once. These commands generate development configuration in this checkout; use a separate clean extraction for execution:

```bash
python runner/setup.py
python runner/build_native_certify.py --positive-serial
docker compose --env-file docker/.env -f docker/docker-compose.yml build conformance-server
docker compose --env-file docker/.env -f docker/storage.compose.yml build minio

for image in mongo:6.0.13 postgres:15 nginx:1.28-alpine \
  quay.io/keycloak/keycloak:26.4.0 \
  injistack/inji-verify-service:1.0.0-alpha.1 \
  injistack/inji-verify-ui:1.0.0-alpha.1; do
  docker pull "$image"
done
```

The prepared native Certify image contains the verified fixes; it is a local build of pinned source, not an unmodified upstream release. See [native release details](docker/RELEASES.md).

## Run both components with fresh data

After committing or checking out the desired source revision, create a new source-only extraction for each run. Do not copy `.env`, generated keys or old reports into it:

```bash
SOURCE_ROOT="$PWD"
STAMP="$(date +%Y%m%d-%H%M%S)"
RUN_DIR="$HOME/inji-conformance/run-$STAMP"
REPORT_DIR="$HOME/inji-conformance/reports-$STAMP"
mkdir -p "$RUN_DIR"
git -C "$SOURCE_ROOT" archive HEAD | tar -x -C "$RUN_DIR"
cd "$RUN_DIR"

bash run-clean-conformance.sh --combined --parallel 2 --reports-dir "$REPORT_DIR"
RUN_EXIT=$?
echo "Execution exit code: $RUN_EXIT"
cat "$REPORT_DIR/reporter-exit-statuses.json"
```

The clean wrapper starts twelve real services with fresh keys and five owned volumes, runs the normal reporting lifecycle, and cleans up only its owned deployment on exit. It expects the images prepared above. With the recorded six REVIEW results, combined execution exits **1**. Inspect reports to distinguish that benchmark failure from startup, browser, reporting or storage errors. Each run needs a fresh extraction.

### Component and persistent development modes

The ordinary wrapper supports one-command execution with a persistent local development deployment:

```bash
bash run-conformance.sh --component certify --native-positive --insecure
bash run-conformance.sh --component verify --insecure
bash run-conformance.sh --combined --native-positive --parallel 2 --insecure
```

Choose one command at a time. `--native-positive` selects all verified Certify/key-manager fixes. Use distinct `--reports-dir` paths to preserve runs. `--skip-docker` targets an already configured deployment and requires its actual environment settings. `--insecure` is explicitly for local self-signed TLS; use a trusted CA for other environments. PowerShell equivalents are available in `run-conformance.ps1`. See [SETUP.md](SETUP.md) before reusing existing database volumes or credentials.

## Reports and interfaces

| Artifact | Purpose |
|---|---|
| `conformance-summary.json` | Official module outcomes and component/combined gates |
| `extent-report.html`, `testng-results.xml` | Consolidated visual and machine-readable reports |
| `existing-certify/`, `existing-verify/` | Actual native module reports |
| `reporter-exit-statuses.json` | Native and consolidated reporter exit codes |
| `plan-*-export.zip` | Official plan exports |
| `artifact-storage-validation.json` | Verified storage object hashes and keys |

On Windows/WSL, open reports with `explorer.exe "$(wslpath -w "$REPORT_DIR")"`. While the services are running, the suite is at `https://localhost:8443`, Verify UI at `https://localhost:8445/verify`, and MinIO console at `http://localhost:9001`. The clean wrapper tears them down at completion. Raw exports, credentials, keys and runtime evidence stay outside committed source.

## CI and validation

- [Hosted CI on the validated merged source](https://github.com/SantoshReddy0603/mosip-inji-conformance/actions/runs/39716320075): all five jobs passed.
- [Actual release-triggered full-stack run](https://github.com/SantoshReddy0603/mosip-inji-conformance/actions/runs/39717011976/attempts/2): reporting, storage, artifact upload and cleanup succeeded; six REVIEW outcomes failed the strict gate.

Pull requests run harness checks, both API test-rig integrations and native product tests. Privileged live release/manual jobs require an approved environment and reachable deployment or ephemeral local runner. No live conformance claim follows from unit tests alone. See [CI/CD setup](CI_CD_SETUP.md) and [runner operations](RUNNER_OPERATIONS.md).

Local checks after environment/image preparation:

```bash
python -m pytest tests -q
bash -n run-conformance.sh run-clean-conformance.sh run-full-stack-conformance.sh
mvn -f testrig/pom.xml test-compile
```

## Scope and remaining limits

- Official verifier target: **`oid4vp-1final-verifier-test-plan`**. No alternative profile or protocol-translation proxy is substituted.
- Six official verifier REVIEW outcomes remain unresolved. Request URI POST coverage and status-list interoperability are not established.
- Fresh keys, volumes and source extraction were tested; a separate machine with completely empty Docker/Maven caches remains unverified.
- Required-reviewer enforcement is unavailable on the current private repository plan; explicit operator approval is used.
- Course issuance and the verifier plan's PID fixture are independent plans; combined execution does not prove course-to-PID credential interoperability.
- Unrelated complete master functional suites were not executed. Formal certification is not claimed.

## Documentation

[Setup](SETUP.md) · [Architecture](ARCHITECTURE.md) · [Requirement checklist](REQUIREMENTS_STATUS.md) · [Current status](PROJECT_STATUS.md) · [Troubleshooting](TROUBLESHOOTING.md) · [Review handling](REVIEW_PROCESS.md) · [Cold-start validation](COLD_START_VALIDATION.md)
