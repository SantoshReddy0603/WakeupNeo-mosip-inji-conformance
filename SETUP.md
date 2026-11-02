# Local setup and execution

The local synthetic issuer, authentication provider, database, signing keys, verifier, suite and MinIO are configured automatically. No external issuer registry, personal data, account or GitHub token is required. Current compatibility limits are listed in the README scope section. Recorded patched issuer evidence passes; it does not describe the stock default. Verifier/combined reference gates fail on six REVIEW results. This setup does not claim certification.

## Requirements

Docker Desktop with Linux containers and sufficient memory, Python 3.12+, and Java/Maven. The standalone reporting bridge targets Java 11. The official suite and selected Inji API-test modules use Java 21. Builds require access to upstream GitLab/GitHub, Maven Central, Google's Android Maven repository, DanubeTech and JitPack. MinIO is built from pinned official source because the registry image was unavailable during validation.

```sh
python -m pip install -r runner/requirements-dev.txt
python -m playwright install chromium
python runner/setup.py
python runner/preflight.py
python -m pytest tests -q
mvn -f testrig/pom.xml test-compile
```

On Linux, Playwright may require its documented system dependencies (`python -m playwright install --with-deps chromium`). WSL can use `CONFORMANCE_RESOLVE_LOCAL=true` to resolve host.docker.internal to loopback within the runner/browser process. URLs, TLS identities and protocol values are retained unchanged.

## One command

```sh
bash run-conformance.sh --component verify --insecure
bash run-conformance.sh --component certify --insecure
bash run-conformance.sh --combined --parallel 2 --insecure
```

PowerShell equivalents use `-Component verify`, `-Component certify`, or `-Combined -Parallel 2`, and `-Insecure`. Use `-Python` and `-Maven` to select installed executables. WSL can set `PYTHON=/absolute/venv/bin/python`. The wrapper checks dependencies, generates/preserves secrets, starts the suite and selected real services, waits for readiness, configures the real course template, starts MinIO, executes official plans, then runs the actual component api-test reporters. Every mode retains standalone Extent/TestNG output; combined mode consolidates both components. Artifacts are uploaded and read back byte-for-byte. A failed conformance gate exits nonzero while retaining evidence. `--runner-only` explicitly omits Java reporting.

The reporter lifecycle automatically checks out the pinned commons and component repositories under `docker/local/api-test` if absent, installs newly checked-out commons, installs the conformance classes, and compiles/runs the existing reporter. Reuse existing matching checkouts with `MOSIP_FUNCTIONAL_TESTS_REPO`, `CERTIFY_API_TEST_REPO`, and `VERIFY_API_TEST_REPO`. `MAVEN_OFFLINE=true` uses already cached dependencies. Missing tools, incompatible source revisions and build/storage failures remain fatal. The OIDF client now calls the unmodified pinned `scripts/conformance.py` library vendored with its license and SHA-256 provenance; browser interaction and export integrity checks remain in the harness.

For an already built pinned api-test module, `CERTIFY_API_TEST_CLASSPATH_FILE` and `VERIFY_API_TEST_CLASSPATH_FILE` may point to real Maven `dependency:build-classpath` output files. Every referenced JAR must exist. The lifecycle then compiles both conformance bridge sources with `javac` against those dependencies; it does not substitute a mock compiler or skip bridge compilation. Omit these variables for the normal Maven bootstrap/build path.

To validate the complete reporting entrypoint without creating official plans, use the retained-run mode with an explicit identity and a separate empty output directory:

```sh
bash run-conformance.sh --combined --skip-docker --insecure \
  --existing-run /absolute/path/to/original-run \
  --run-id ACTUAL_ORIGINAL_RUN_ID \
  --reports-dir /absolute/path/to/empty-validation-output \
  --max-report-age-seconds 86400
```

Use `--component certify` or `--component verify` for per-module validation and the matching source run ID. PowerShell accepts `-ExistingRun`, `-RunId`, `-ReportsDir`, and `-MaxReportAgeSeconds`. This mode reads existing official plan/instance records, checks exact results/mapping/gates and copies original artifacts without changing their timestamp. It does not issue credentials, start tests or create plans. Historical validation artifacts use a separate `openid-conformance-validation/<run-id>/<validation-id>/` storage namespace. A historical failed gate still exits 1; validation errors exit 2. This is reporting/implementation validation, not a new conformance run. Omit retained-run arguments for fresh execution.

`--insecure` is explicit for local self-signed TLS. For trusted TLS set CA_BUNDLE and omit it. The suite JVM imports the generated development certificate into a copy of its default truststore; it does not disable server certificate validation. Replace development certificates for another environment.

## Tested native Certify fixes

The stock release remains available for baseline comparisons. Explicit native build flags compile pinned source, apply reviewable patches, run native tests and deploy the rebuilt service with the actual PostgreSQL plugin:

```sh
bash run-conformance.sh --component certify --native-certify --insecure
bash run-conformance.sh --component certify --native-dpop --insecure
bash run-conformance.sh --component certify --native-binding --insecure
bash run-conformance.sh --combined --native-positive --parallel 2 --insecure
```

PowerShell supports `-NativeCertify`, `-NativeDpop`, `-NativeBinding`, `-NativeMetadata`, `-NativeFinal` and `-NativePositive`. Each includes the earlier fixes. **Use `--native-positive` / `-NativePositive` for the complete verified build**: request extensions, native DPoP/replay validation, holder cnf.jwk, signed issuer metadata, selector/error semantics and positive certificate serials. This builds/tests pinned Certify and key-manager source and deploys their native implementations with the actual PostgreSQL provider.

The positive flag also checks the isolated course issuer's signing certificates. If legacy serials are non-positive, it stops only that issuer, backs up the complete synthetic certify schema and keystore under `docker/local/key-rotation-backups`, retains retired aliases/material and generates new keys through the native key manager. Its date-based unique identifiers require archival identifiers for retired same-day aliases; original identifiers remain in the backup. On failure, database and keystore are restored together from the offline snapshot and the exception remains fatal. It never edits/re-signs a certificate in the harness. This helper refuses another running image or deployment. Keep backups private and excluded from source.

Native patches are in `docker/native-certify` and `docker/native-keymanager`; Java 21 and the documented Maven repositories are required. The tested image and commits are recorded in docker/RELEASES.md. Check the running implementation independently:

```sh
python runner/course_issuer.py --insecure --dpop --request-extension --require-cnf-jwk --signed-metadata --credential-errors --positive-serial --output reports/course-native-smoke.json
# Add --resolve-local in WSL when needed.
```

This genuine issuance/security check is explicitly separate from official conformance evidence. The browser callback is completed before its context closes. Official outcomes and raw exports remain authoritative.

## Endpoints

- Suite: https://localhost:8443 (advertised https://host.docker.internal:8443)
- Certify issuer identifier: https://host.docker.internal:8446
- Certify API: /v1/certify; discovery at /.well-known/openid-credential-issuer
- Keycloak: https://host.docker.internal:8446/auth/realms/course
- Verify: https://localhost:8445/v1/verify; native final routes under /v2
- Verify UI: https://localhost:8445/verify (the wrapper configures this for actual browser evidence)
- MinIO API: http://localhost:9000; console: http://localhost:9001

The issuer discovery route for RFC 8414 goes directly to Keycloak's genuine native OAuth metadata endpoint. The proxy changes only routing; no metadata, authorization request, token, credential or result is translated.

## Real course issuance smoke test

```sh
python runner/course_issuer.py --insecure
# In WSL, add --resolve-local if Docker Desktop's hostname is unavailable.
```

This configures/updates `course-completion-sdjwt`, obtains a real development OAuth token, sends a real holder proof and nonce, and checks the actual returned credential. It verifies the ES256 signature, SD disclosure hashes, holder key, issuer/VCT, expiry and synthetic DB values. Its output explicitly says `official_conformance_result: false`.

The public `course-wallet` client supports the local development smoke flow. Two distinct `conformance-course-wallet` clients use actual private_key_jwt authentication for the official plan; generated private JWKS live in docker/local/wallet-keys and are never served. Only public JWKS are mounted into the HTTP proxy. The PostgreSQL data-provider selects the learner record using the validated token's sub and the exact course_completion scope. The release key manager persists signing keys in the isolated keystore and DB.

## Reusing an existing deployment

Use `--skip-docker` / `-SkipDocker`, with configured endpoints and credentials already available in your environment. This mode does not import local secrets or change the deployment.

Verifier variables: OIDF_URL, VERIFY_API_URL, VERIFY_SDK_VERSION (1.0.0-alpha.1), optionally VERIFY_REQUEST_FILE and VERIFY_PLAN_CONFIG. The default request uses native DCQL. The verifier plan remains oid4vp-1final-verifier-test-plan. `VERIFY_CREDENTIAL_KEY_PROFILE=x509` is the default matching certificate/key profile; bare `jwk` exposes the product's unsupported-key case rather than hiding it.

Issuer variables: CERTIFY_ISSUER_URL, VCI_AUTHORIZATION_SERVER, VCI_CLIENT_ID, VCI_CLIENT2_ID, VCI_SCOPE, VCI_CREDENTIAL_CONFIGURATION_ID, VCI_CREDENTIAL_FORMAT=sd_jwt_vc, VCI_CLIENT_AUTH_TYPE=private_key_jwt, VCI_SENDER_CONSTRAIN=dpop, VCI_WALLET_JWKS_FILE, VCI_WALLET2_JWKS_FILE, ISSUER_BROWSER_STEPS_FILE, ISSUER_LOGIN_USERNAME and ISSUER_LOGIN_PASSWORD. Local wrappers supply these from the real generated configuration. For another supported profile, use CERTIFY_PLAN_CONFIG with actual registered clients/keys. OIDF_TOKEN is only necessary for an authenticated remote suite.

The course VCT is urn:inji:development:course-completion:1. The official verifier plan uses its PID fixture; the combined run means both independent component plans, not cross-product credential interoperability.

## Existing module integration

Both wrappers expose component-specific plan configuration and expected-failure files: Bash `--certify-config`, `--verify-config`, `--expected-failures`; PowerShell `-CertifyConfig`, `-VerifyConfig`, `-ExpectedFailures`. `--diff` / `-Diff` compares a previous summary. Invalid exception metadata fails before any plan creation; defaults remain empty.

For read-only historical validation, use `--existing-run DIR --run-id ID --reports-dir EMPTY_DIR --skip-docker` (PowerShell: `-ExistingRun`, `-RunId`, `-ReportsDir`, `-SkipDocker`). `--diff` is supported here too. Plan/exception files cannot change retained results. Component-only validation preserves the original combined summary/gate as provenance while reporting the selected component's existing gate. Historical reporting requires an explicit `--max-report-age-seconds` / `-MaxReportAgeSeconds` bound appropriate to the retained timestamp. This is implementation validation, not a fresh official release run.

See ARCHITECTURE.md for the lifecycle and TROUBLESHOOTING.md for diagnosis.

See integration/README.md. The component api-test modules moved from mosip-functional-tests to the Inji repositories; the installer targets the actual modules and their existing master listener. The tested source commits are pinned in the workflow.

## GitHub Actions

The code CI workflow contains harness, native-product and real module integration checks. The separate full-stack-conformance.yml authorizes a production-release or default-branch manual run, then selects hosted Linux by default or an explicitly enabled dedicated inji-conformance runner. Both stock and patched diagnostics retain strict gates and artifacts on failure. This candidate passed ordinary CI 40165694278 and verified managed hosted execution in scratch run 40165722639, both at 9c8d94ad9da42ac458ea304192118266577469f9. The strict product gate remains FAILED; see docs/VALIDATION.md for the retained evidence and limits.

For another live run, register an approved ephemeral runner that can reach the real services; follow RUNNER_OPERATIONS.md. Configure the endpoint/client/profile/key-file/browser-file variables above as repository variables. Store runtime passwords, optional OIDF token and AWS access keys using the referenced GitHub secrets, never in a committed file. Key-file/browser-file variables must reference files available on that runner; generated private JWKS are excluded from source. Set S3_ENDPOINT, S3_BUCKET and AWS_REGION for MinIO/S3. Use protected environment controls for shared environments.

## Reports and stopping

reports/ holds the summary, component reports, badges, official ZIP exports, raw logs and genuine browser screenshots. TestNG consumes only an explicitly matching run ID when reusing reports. S3 upload includes only artifact IDs belonging to the current run, plus its reports and TestNG/Extent output; stale previous-run logs are excluded. verify_storage.py downloads and compares the uploaded bytes.

Stop services without deleting their data:

```sh
docker compose --env-file docker/.env -f docker/docker-compose.yml --profile certify --profile verify --profile storage stop
```

Do not migrate historical volumes automatically. Use a fresh extraction for acceptance tests and retain old evidence separately.

Setup preserves generated passwords/keys and existing realm/data volumes. To update an already imported local realm, stop course-auth, run its official offline import with the new generated JSON, then restart it and reload conformance-httpd. Ordinary start-up imports skip existing realms. See https://www.keycloak.org/server/importExport for the supported procedure. Do not delete or overwrite another deployment's data.

For local workflow lint outside a Git checkout, supply the bundled label configuration explicitly:

```sh
actionlint -config-file .github/actionlint.yaml .github/workflows/full-stack-conformance.yml
```


## Fresh empty-volume reproduction

Use Docker Desktop Linux containers with Linux/WSL Python and Java 21, Maven 3.8.7, Docker Compose, and the requirements-dev dependencies. Install Playwright Chromium. Keep the virtual environment outside the fresh source directory or point PYTHON to its absolute executable. Reserve loopback ports 8443, 8445, 8446, 9000 and 9001; stop conflicting services deliberately without deleting their volumes.

Prepare the pinned images once from the normal source checkout:

```sh
python runner/setup.py
docker compose --env-file docker/.env -f docker/docker-compose.yml build conformance-server
docker compose --env-file docker/.env -f docker/docker-compose.yml --profile storage build minio
while IFS= read -r image; do
  if ! docker image inspect "$image" >/dev/null 2>&1; then
    docker pull "$image" || exit
  fi
done < <(docker compose --env-file docker/.env -f docker/docker-compose.yml --profile certify --profile verify --profile storage config --images | sort -u)
mkdir ../mosip-clean-run
git archive HEAD | tar -x -C ../mosip-clean-run
cd ../mosip-clean-run
bash run-clean-conformance.sh --combined --parallel 2 --reports-dir reports/fresh
```

For the submission ZIP, extract its source directory again into a new directory instead of git archive. Do not copy docker/.env, docker/local, generated certificates or previous reports. Build/image and Maven/Python caches may be reused; the clean wrapper explicitly refuses old source-local state and existing project volumes. The ordinary one-command scripts remain available for component selection; the clean wrapper forwards --component certify, --component verify or --combined to the same runner.

The wrapper creates a unique inji-clean-* project, ten real services, five new volumes and fresh signing/development credentials. It initializes only the loopback MinIO bucket, configures real course issuance, executes the normal runner/TestNG/Extent/S3 lifecycle and returns the genuine gate status. An EXIT trap verifies ownership and cleans only its isolated volumes, including on failures. The ownership/image record remains in docker/isolated-state.json; keep it as local evidence, never copy generated keys into submissions. No historical project is removed. An interrupted hard kill can be recovered with `python runner/isolated_stack.py down --project <project-recorded-in-isolated-state.json>` from the same extraction. Cleanup rejects an inconsistent project or volume label.

Expected acceptance: stock Certify keeps its actual interruption failures. The explicit patched diagnostic may pass its issuer gate with three optional skips. Six verifier screenshot REVIEW outcomes keep Verify/combined gates failed with exit 1. A storage error, empty result set, missing TestNG XML, missing Extent HTML or absent upload verification is an implementation/infrastructure failure, not evidence of an expected benchmark failure. Inspect conformance-summary.json, reporter-exit-statuses.json and artifact-storage-validation.json before interpreting exit 1. Real status counts from the current clean validation are recorded in the final evidence, independently of historical results.

## Reproduce independent module and combined reporting

From the configured development deployment, use the same real endpoints and native fixes:

```bash
bash run-conformance.sh --component certify --native-positive --insecure
bash run-conformance.sh --component verify --insecure
bash run-conformance.sh --combined --native-positive --parallel 2 --insecure
```

Use distinct `--reports-dir` paths to preserve each run. Managed clean-volume execution uses `run-clean-conformance.sh` with the same component/combined selection after preparing the pinned images. A standalone Certify run passes when its own conformance and regression benchmarks pass; Verify and combined remain failures while the official REVIEWs persist. A combined report now preserves those independent gates inside both native TestNG suites. TestNG includes an additional harness gate assertion; it is not an official test module. For an existing deployment, use `--skip-docker` and configure its real plan/authentication/storage inputs. For retained online validation use `--existing-run DIR --run-id ID --reports-dir EMPTY_DIR` with the original suite database still available. Removed isolated suite volumes cannot supply live checks for old IDs; offline archived-result re-reporting must say so explicitly.

See [RUNNER_OPERATIONS.md](RUNNER_OPERATIONS.md) for approved one-job startup/recovery and [SETUP.md](SETUP.md#isolated-reproduction) for isolated empty-cache deployment.

## Isolated reproduction

Use fresh source with no docker/.env, generated keys or reports. Prepare pinned images first, then run the clean wrapper. Stock is the default. Select the patched image explicitly for separate diagnostics. It starts ten services and five owned volumes, retains reports and cleans only its deployment.

Caches may be reused. Empty-cache reproduction requires a separate compatible disposable machine and a record that caches were empty before setup. Do not prune this machine or historical volumes to simulate it.

## Versions and Java

The four version settings in docker/.env come from docker/versions.env. Alpha pins remain explicit because stable 1.0.x release tags were not found in official inventories checked on 24 October 2026. New SDK versions require adapter validation.

The standalone bridge targets Java 11 APIs. Its JDK 11 runtime check is separate from pinned mosip-functional-tests commons and Inji api-test modules, whose actual POMs target Java 21. Do not lower dependencies or claim native Java 11 execution without evidence.

## Linux connectivity

The TLS ingress owns the Docker network alias host.docker.internal on ports 8443, 8445 and 8446. Containers use Docker DNS. The runner/browser use CONFORMANCE_RESOLVE_LOCAL=true for loopback. Published host ports remain 127.0.0.1. This connectivity was verified in GitHub-hosted ubuntu-24.04 scratch run 40165722639 at 9c8d94ad9da42ac458ea304192118266577469f9. Arbitrary Linux environments and the separate empty-cache procedure remain not verified.

The verifier fixture does not establish status-list interoperability. Request URI POST coverage remains unestablished. These limits remain visible after removing the status journals.
