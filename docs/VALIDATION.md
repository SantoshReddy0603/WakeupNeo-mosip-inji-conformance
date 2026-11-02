# Validation evidence and limits

Historical checks apply to the named revisions, not automatically to later changes.
Post-merge CI `40178792370` passed five jobs, including 196 Python tests, at
`7d80dc06e8d8745d01c8b82d6a08c8f3d32dc80b`. The original final source revision is
`5795dbc97293322f466f0b8bcc58b852f0211b8b`.

Reports and logs referenced here belong to the separate local evidence handoff.
They are not bundled in this source repository. [The evidence index](../evidence/README.md)
identifies their retained paths. Drive upload and reviewer access are **not verified**.
Raw exports and generated keys remain excluded.

## Local source checks

[Local check receipt](../evidence/local-checks.json) records 213 passing Python
checks after setup, shell/PowerShell/workflow syntax checks, a fresh Java 11
bridge compilation and seven bridge scenarios. Source hashes identify the four
changed implementation/test files covered by that receipt.

Log retrieval failures preserve the observed official status and separately reject
the gate for missing evidence. Retained validation requires complete module/variant
coverage and matching official instance identity. These fixes were checked locally;
a fresh live conformance run of these changes is **not verified**. Docker is not
available in the current WSL distribution, and hosted CI for this candidate is
**not verified**.

## Java compatibility

The standalone bridge retains `maven.compiler.release=11` and compiler `<release>11</release>` in
`testrig/pom.xml`. Preserved output `fresh-jdk11-validation.json` records
fresh compile exit 0; `fresh-jdk11-testng.log` records seven successful scenario checks (expected
assertion-failure scenarios return 1). The 25 October local rerun also passed fresh compilation and all seven
scenarios on Temurin 11.0.18: `jdk11-checks.json` and `jdk11-scenarios.log`,
both checks exit 0.

Upstream Certify pin `8fdf71656979a72fa8263766d4dec3cc25127b76`, `api-test/pom.xml:57`, and Verify pin
`4c4289026968beb535d3dbdd500947152c43f708`, `api-test/pom.xml:79`, both set
`<maven.compiler.target>21</maven.compiler.target>`. Their compiler configurations consume that property at
lines 139 and 129 respectively. Actual JDK 11 compiler attempts failed with `Fatal error compiling: error:
invalid target release: 21` (`jdk11-certify-real-metadata.log` and
`jdk11-verify-real-metadata.log`, both exit 1). Upstream POMs were not modified; actual integrated reporting
used Java 21 in stock run `019bf015dcef47029010faa06a2cf788` and diagnostic run
`d39d9f65b0f04db79eb3d25501c9f26c`.

Organizer question (draft only, not sent):

> Our standalone OpenIDConformanceTest bridge compiles with --release 11 and passes seven actual JDK 11 TestNG scenarios.  
> The pinned upstream inji-certify and inji-verify api-test modules declare maven.compiler.target=21.  
> On JDK 11 both fail compilation with “error: invalid target release: 21”.  
> We have retained those upstream POMs and run the integrated modules on JDK 21.  
> Is JDK 21 acceptable for these integrated modules while the standalone bridge remains Java 11 compatible?

## Verifier coverage

The preserved stock verifier export `plan-fnLpdorj2jZAD-export.zip`, run `019bf015dcef47029010faa06a2cf788`,
records request-URI-POST instance `49xL7f98HbXNJZr` as REVIEW and happy-flow instance `qyHOyhAz17GKHWo` as
REVIEW. The exact screenshot condition is `ExpectVerifierSuccessfulVerificationPage`: “Upload a screenshot
showing that the verifier successfully verified the presented credential (for example, a page displaying the
credential contents).” These are not observed POST or status-list failures.

At suite pin `11999aad62ec292f36101410d9d5b761d44903ff`,
`AbstractVP1FinalVerifierTest.extractAuthorizationEndpointRequestParameters()` calls
`fetchAndProcessRequestUri()` only for REQUEST_URI_SIGNED. With the retained `request_method=url_query`,
`VP1FinalVerifierRequestUriMethodPost` neither invokes `CreateWalletNonce`,
`PostToRequestUriAndExtractRequestObject`, `EnsureWalletNonceClaimMatchesPostedValue`, nor its own
not-applicable SKIP. This is the suite applicability gap. The pinned Verify request service supplies a request
URI only for its decentralized_identifier branch; that is not proof that the selected redirect_uri variant
supports POST. Native POST interoperability is **not verified**, and the plan/variant was not switched.

The selected suite's SD-JWT PID fixture has no credential status reference. The actual native happy-flow
result has `statusCheck: []`; cryptographic negative tests can short-circuit before status processing. There
is no status-list-specific failure message or failing instance in this plan export to reproduce. Status-list
interoperability is **not verified**; assigning a product defect from an empty status array would be
unsupported. The local evidence inspection is recorded in `verifier-coverage.json` outside the source package.

Fresh local reproduction on 25 October: run `0d9b58120a964f628a34dd0c658d6c8f`, official export
`plan-IpxODLyKkxZNN-export.zip`, again records 4 PASSED and 6 REVIEW with a failed verifier gate. POST-named
instance `E1FPVnumrtRlZHU` again reaches `ExpectVerifierSuccessfulVerificationPage` with the exact screenshot
message above and none of the three POST conditions; its native transaction is
`txn_ae0cbbba-6271-4568-ba2d-6e5ef5d64606`. Happy-flow instance `oTZgMqIEscOyRW9`, transaction
`txn_76109d07-1936-4aa0-955d-40b476e70804`, again has no status reference and `statusCheck: []`. The
observations reproduce the coverage gaps, not actual POST/status-list failures. The first local deployment
attempt exited 1 before creating a plan because Docker was unavailable; the retry's stack and readiness exited
0 (`commands.json` and `verify-d11d275d/commands.json`). Original runs and
screenshots were not altered.

That reproduction completed with conformance command exit 1, native Verify reporter exit 1 and consolidated
Extent reporter exit 1. Both actual TestNG XML reports contain 11 checks, 4 passed and 7 failed: six REVIEW
assertions and one release-gate assertion. The storage lifecycle verified 65 artifacts by read-back; owned
cleanup exited 0 and removed all five owned volumes, leaving none
(`verify-d11d275d/reports/reporter-exit-statuses.json`, `artifact-storage-validation.json`, both
`testng-results.xml` files, `commands.json` and `deployment-state.json`). No failure was hidden or converted
to success.


## Hosted validation — 25 October 2026

Private scratch repository `SantoshReddy0603/inji-conformance-b2-scratch` ran
`40165722639` at exact commit `9c8d94ad9da42ac458ea304192118266577469f9`.
This was not a run on the main repository. Official run ID:
`2583bed425d64f5abb0c86993d402116`.

| Implementation criterion | Outcome | Recorded evidence |
|---|---|---|
| Ten services start on ubuntu-24.04 | Verified | `run-state.json` and workflow startup logs |
| Both official plans execute | Verified | Issuer `vir0sD8It1IDI`, verifier `UZtgjxUuLpdPj`, `ci-summary.json` |
| Native and combined reports uploaded | Verified | Artifacts `12587654719` and `12587788827`, downloaded and CRC checked |
| Storage verification and owned cleanup succeed | Verified | 114 objects verified; five owned volumes removed; zero remain |
| Counts match the stock reference | Verified | Certify 2 PASSED / 10 INTERRUPTED / 3 SKIPPED; Verify 4 PASSED / 6 REVIEW |

The authorization job succeeded. The stock release-gate job failed at execution,
because its actual official outcomes fail the strict benchmark. Image preparation,
report upload and cleanup succeeded. Native reporter exit codes were Certify=1,
Verify=1 and combined=1. Combined TestNG reports have 26 checks: 6 passed,
17 failed and 3 skipped, including the extra gate assertion.

The retained handoff contains `b2-scratch/retry1/run-40165722639-logs.zip`,
`artifact-12587654719.zip`, `artifact-12587788827.zip`, `assessment.json`
and download receipts. Twenty-three downloaded reports matched storage hashes.
The first cleanup removed five volumes; the second idempotent cleanup removed
zero and left zero. The final state records the second call; log lines 16592
and 16643 distinguish both calls.

Hosted Certify image ID was
`sha256:75170c3bb5ccb13869637e7450c16994f496104529bb4ce56f336d19475d1f46`.
It differs from the older local image ID. Byte-identical image reproducibility
is **not verified**. Hosted raw official export ZIPs were verified in ephemeral
MinIO but not retained as GitHub artifacts. Offline reinspection of those raw
bytes is **not verified**; reports and logs must not be described as raw exports.

The earlier attempt, run `40164823727` at
`ce7a50e81cdea4081fa1061573e24c8d76094d68`, stopped before stack startup:
empty inherited AWS variables overrode generated configuration. No official plan
executed. The correction removed job-level AWS credentials, loaded nonempty
credentials only in external mode, and retained sanitized reports on gate failure.
The successful run above includes that correction. It does not establish product
conformance, official review approval or certification.

## Hosted workflow operation

Source: `.github/workflows/full-stack-conformance.yml`. Its default-branch guard is:

```text
(github.event_name == 'workflow_dispatch' && github.ref == format('refs/heads/{0}', github.event.repository.default_branch)) ||
(github.event_name == 'release' && github.event.action == 'published' && !github.event.release.draft && !github.event.release.prerelease)
```

Pushes and merges do not trigger this live workflow. A permitted manual dispatch
or eligible published release must also pass immutable revision and ancestry checks.
Authorization uses ubuntu-24.04; execution defaults to ubuntu-24.04 unless
`INJI_USE_SELF_HOSTED_RUNNER=true`. No WSL or Windows paths are required.

`host-gateway` extra_hosts is absent. Compose assigns `host.docker.internal` to
its internal TLS ingress; host-side resolution uses loopback. This routing was
verified by scratch run `40165722639`. Arbitrary Linux distributions remain
outside that verification scope.

A managed stock run uses `INJI_MANAGED_LOCAL_STACK=true`, `component=combined`,
`issuer_build=stock` and no true self-hosted override. It needs no copied issuer
or storage secrets: setup generates development values. The live job declares the `inji-conformance` environment. Configure its reviewer
protection separately; enforcement on the new repository is **not verified**.
Repository authorization and workflow policy still apply.

The workflow will:

1. Validate the event/revision and check out pinned source and API rigs.
2. Install Python 3.12, Java 21, Maven 3.8.7 and Chromium dependencies.
3. Compile the native reporting integrations; generate development configuration.
4. Build the suite and MinIO, pull stock images, and extract a clean source tree.
5. Start ten services with five owned volumes and run both official plans.
6. Retrieve evidence, produce native/combined reports and verify MinIO read-back.
7. Enforce the strict gates, clean owned resources and upload sanitized artifacts
   for seven days, including when the benchmark fails.

Remote execution is a separate operation. No new dispatch, release or destructive
cleanup is performed by following these documentation checks. The 180-minute
workflow timeout is a limit, not a promised duration. Resource limits, dependency
downloads and account artifact-storage quota can prevent completion.

External deployment inputs are mapped as follows. The two AWS credential rows are
loaded only by the external-mode credential step, not exported at job scope:

| Environment name | Workflow source |
|---|---|
| `ISSUER_BUILD` | `${{ github.event_name == 'workflow_dispatch' && inputs.issuer_build \|\| 'stock' }}` |
| `OIDF_URL` | `${{ vars.OIDF_URL }}` |
| `CERTIFY_ISSUER_URL` | `${{ vars.CERTIFY_ISSUER_URL }}` |
| `VERIFY_API_URL` | `${{ vars.VERIFY_API_URL }}` |
| `VERIFY_UI_URL` | `${{ vars.VERIFY_UI_URL }}` |
| `VERIFY_SDK_VERSION` | `${{ vars.VERIFY_SDK_VERSION }}` |
| `S3_ENDPOINT` | `${{ vars.S3_ENDPOINT }}` |
| `S3_BUCKET` | `${{ vars.S3_BUCKET \|\| 'automationtests' }}` |
| `AWS_REGION` | `${{ vars.AWS_REGION \|\| 'us-east-1' }}` |
| `AWS_ACCESS_KEY_ID` | Nonempty `${{ secrets.AWS_ACCESS_KEY_ID }}` loaded into `GITHUB_ENV` only in external mode |
| `AWS_SECRET_ACCESS_KEY` | Nonempty `${{ secrets.AWS_SECRET_ACCESS_KEY }}` loaded into `GITHUB_ENV` only in external mode |
| `CA_BUNDLE` | `${{ vars.CA_BUNDLE }}` |
| `OIDF_TOKEN` | `${{ secrets.OIDF_TOKEN }}` |
| `CERTIFY_PLAN_CONFIG` | `${{ vars.CERTIFY_PLAN_CONFIG }}` |
| `VERIFY_PLAN_CONFIG` | `${{ vars.VERIFY_PLAN_CONFIG }}` |
| `VERIFY_REQUEST_FILE` | `${{ vars.VERIFY_REQUEST_FILE }}` |
| `ISSUER_BROWSER_STEPS_FILE` | `${{ vars.ISSUER_BROWSER_STEPS_FILE }}` |
| `VCI_CLIENT_ID` | `${{ vars.VCI_CLIENT_ID }}` |
| `VCI_CLIENT2_ID` | `${{ vars.VCI_CLIENT2_ID }}` |
| `VCI_AUTHORIZATION_SERVER` | `${{ vars.VCI_AUTHORIZATION_SERVER }}` |
| `VCI_WALLET_JWKS_FILE` | `${{ vars.VCI_WALLET_JWKS_FILE }}` |
| `VCI_WALLET2_JWKS_FILE` | `${{ vars.VCI_WALLET2_JWKS_FILE }}` |
| `VCI_CLIENT_SECRET` | `${{ secrets.VCI_CLIENT_SECRET }}` |
| `VCI_SCOPE` | `${{ vars.VCI_SCOPE }}` |
| `VCI_CREDENTIAL_FORMAT` | `${{ vars.VCI_CREDENTIAL_FORMAT }}` |
| `VCI_CREDENTIAL_CONFIGURATION_ID` | `${{ vars.VCI_CREDENTIAL_CONFIGURATION_ID }}` |
| `VCI_CLIENT_AUTH_TYPE` | `${{ vars.VCI_CLIENT_AUTH_TYPE }}` |
| `VCI_SENDER_CONSTRAIN` | `${{ vars.VCI_SENDER_CONSTRAIN }}` |
| `ISSUER_LOGIN_USERNAME` | `${{ secrets.ISSUER_LOGIN_USERNAME }}` |
| `ISSUER_LOGIN_PASSWORD` | `${{ secrets.ISSUER_LOGIN_PASSWORD }}` |

VCI_SENDER_CONSTRAIN is explicitly mapped from vars in external mode. Managed mode exports its locally
validated selection in run-clean-conformance.sh, together with VCI_CLIENT_ID, VCI_CLIENT2_ID,
VCI_WALLET_JWKS_FILE, VCI_WALLET2_JWKS_FILE, VCI_AUTHORIZATION_SERVER, VCI_SCOPE,
VCI_CREDENTIAL_CONFIGURATION_ID, VCI_CREDENTIAL_FORMAT and VCI_CLIENT_AUTH_TYPE. Managed mode intentionally
does not inherit unrelated external issuer secrets. Configure no stock expected-failure waiver or
patched-image override.


## Empty-cache Linux run: prepare only, not verified

Run only after approval, on a disposable dedicated Ubuntu 24.04 machine with Docker Engine/Compose, Git,
Python 3.12/venv and JDK 21 installed. The prune removes unused Docker resources on that machine; never use it
on a shared development host. A fresh machine also needs an empty Maven cache and the approved candidate
available as a commit; uncommitted working-tree changes are not included in a Git archive.

```bash
set -euo pipefail
docker system prune --all --volumes --force
REVISION='<full commit SHA selected for validation>'
ROOT_DIR="$(mktemp -d "$HOME/inji-cold-XXXXXXXX")"
git clone https://github.com/SantoshReddy0603/mosip-inji-conformance-submission.git "$ROOT_DIR/repository"
git -C "$ROOT_DIR/repository" checkout --detach "$REVISION"
test "$(git -C "$ROOT_DIR/repository" rev-parse HEAD)" = "$REVISION"
mkdir "$ROOT_DIR/build" "$ROOT_DIR/run"
git -C "$ROOT_DIR/repository" archive HEAD | tar -x -C "$ROOT_DIR/build"
git -C "$ROOT_DIR/repository" archive HEAD | tar -x -C "$ROOT_DIR/run"
python3 -m venv "$ROOT_DIR/venv"
source "$ROOT_DIR/venv/bin/activate"
cd "$ROOT_DIR/build"
python -m pip install -r runner/requirements-dev.txt
python -m playwright install --with-deps chromium
python runner/install_maven.py --directory "$ROOT_DIR/tools"
export PATH="$ROOT_DIR/tools/apache-maven-3.8.7/bin:$PATH"
java -version
mvn -version
export PYTHON="$(command -v python)"
python runner/setup.py
docker compose --env-file docker/.env -f docker/docker-compose.yml build conformance-server
docker compose --env-file docker/.env -f docker/docker-compose.yml --profile storage build minio
while IFS= read -r image; do
  if ! docker image inspect "$image" >/dev/null 2>&1; then docker pull "$image"; fi
done < <(docker compose --env-file docker/.env -f docker/docker-compose.yml --profile certify --profile verify --profile storage config --images | sort -u)
unset CERTIFY_NATIVE_IMAGE
cd "$ROOT_DIR/run"
set +e
bash run-clean-conformance.sh --combined --parallel 2 --reports-dir "$ROOT_DIR/reports"
RUN_EXIT=$?
set -e
printf 'Conformance command exit: %s\n' "$RUN_EXIT"
test -s "$ROOT_DIR/reports/conformance-summary.json"
cat "$ROOT_DIR/reports/reporter-exit-statuses.json"
exit "$RUN_EXIT"
```

This sequence is prepared, not executed. Exit 1 must be diagnosed from official results and reporting/storage
receipts; it must not be converted to success. The clean wrapper handles owned deployment cleanup. A private
repository may require interactive Git authentication; no token is needed in chat.
