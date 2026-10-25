# Validation limits and approval-only commands

> Current B2 status: **verified for scratch run 40165722639 at commit 9c8d94ad9da42ac458ea304192118266577469f9**. The strict conformance gate remains FAILED. Earlier pending/failure sections below describe historical attempts; see the verified retry section.

## Java compatibility

The standalone bridge retains `maven.compiler.release=11` and compiler `<release>11</release>` in `testrig/pom.xml`. Preserved output `implementation-completion/fresh-jdk11-validation.json` records fresh compile exit 0; `fresh-jdk11-testng.log` records seven successful scenario checks (expected assertion-failure scenarios return 1). The 25 October local rerun also passed fresh compilation and all seven scenarios on Temurin 11.0.18: `implementation-triage/jdk11-checks.json` and `jdk11-scenarios.log`, both checks exit 0.

Upstream Certify pin `8fdf71656979a72fa8263766d4dec3cc25127b76`, `api-test/pom.xml:57`, and Verify pin `4c4289026968beb535d3dbdd500947152c43f708`, `api-test/pom.xml:79`, both set `<maven.compiler.target>21</maven.compiler.target>`. Their compiler configurations consume that property at lines 139 and 129 respectively. Actual JDK 11 compiler attempts failed with `Fatal error compiling: error: invalid target release: 21` (`implementation-completion/jdk11-certify-real-metadata.log` and `jdk11-verify-real-metadata.log`, both exit 1). Upstream POMs were not modified; actual integrated reporting used Java 21 in stock run `019bf015dcef47029010faa06a2cf788` and diagnostic run `d39d9f65b0f04db79eb3d25501c9f26c`.

Organizer question (draft only, not sent):

> Our standalone OpenIDConformanceTest bridge compiles with --release 11 and passes seven actual JDK 11 TestNG scenarios.  
> The pinned upstream inji-certify and inji-verify api-test modules declare maven.compiler.target=21.  
> On JDK 11 both fail compilation with “error: invalid target release: 21”.  
> We have retained those upstream POMs and run the integrated modules on JDK 21.  
> Is JDK 21 acceptable for these integrated modules while the standalone bridge remains Java 11 compatible?

## Verifier coverage

The preserved stock verifier export `plan-fnLpdorj2jZAD-export.zip`, run `019bf015dcef47029010faa06a2cf788`, records request-URI-POST instance `49xL7f98HbXNJZr` as REVIEW and happy-flow instance `qyHOyhAz17GKHWo` as REVIEW. The exact screenshot condition is `ExpectVerifierSuccessfulVerificationPage`: “Upload a screenshot showing that the verifier successfully verified the presented credential (for example, a page displaying the credential contents).” These are not observed POST or status-list failures.

At suite pin `11999aad62ec292f36101410d9d5b761d44903ff`, `AbstractVP1FinalVerifierTest.extractAuthorizationEndpointRequestParameters()` calls `fetchAndProcessRequestUri()` only for REQUEST_URI_SIGNED. With the retained `request_method=url_query`, `VP1FinalVerifierRequestUriMethodPost` neither invokes `CreateWalletNonce`, `PostToRequestUriAndExtractRequestObject`, `EnsureWalletNonceClaimMatchesPostedValue`, nor its own not-applicable SKIP. This is the suite applicability gap. The pinned Verify request service supplies a request URI only for its decentralized_identifier branch; that is not proof that the selected redirect_uri variant supports POST. Native POST interoperability is **not verified**, and the plan/variant was not switched.

The selected suite's SD-JWT PID fixture has no credential status reference. The actual native happy-flow result has `statusCheck: []`; cryptographic negative tests can short-circuit before status processing. There is no status-list-specific failure message or failing instance in this plan export to reproduce. Status-list interoperability is **not verified**; assigning a product defect from an empty status array would be unsupported. The local evidence inspection is recorded in `implementation-triage/verifier-coverage.json`.

Fresh local reproduction on 25 October: run `0d9b58120a964f628a34dd0c658d6c8f`, official export `plan-IpxODLyKkxZNN-export.zip`, again records 4 PASSED and 6 REVIEW with a failed verifier gate. POST-named instance `E1FPVnumrtRlZHU` again reaches `ExpectVerifierSuccessfulVerificationPage` with the exact screenshot message above and none of the three POST conditions; its native transaction is `txn_ae0cbbba-6271-4568-ba2d-6e5ef5d64606`. Happy-flow instance `oTZgMqIEscOyRW9`, transaction `txn_76109d07-1936-4aa0-955d-40b476e70804`, again has no status reference and `statusCheck: []`. The observations reproduce the coverage gaps, not actual POST/status-list failures. The first local deployment attempt exited 1 before creating a plan because Docker was unavailable; the retry's stack and readiness exited 0 (`implementation-triage/verify-4935661f/commands.json` and `verify-d11d275d/commands.json`). Original runs and screenshots were not altered.

That reproduction completed with conformance command exit 1, native Verify reporter exit 1 and consolidated Extent reporter exit 1. Both actual TestNG XML reports contain 11 checks, 4 passed and 7 failed: six REVIEW assertions and one release-gate assertion. The storage lifecycle verified 65 artifacts by read-back; owned cleanup exited 0 and removed all five owned volumes, leaving none (`verify-d11d275d/reports/reporter-exit-statuses.json`, `artifact-storage-validation.json`, both `testng-results.xml` files, `commands.json` and `deployment-state.json`). No failure was hidden or converted to success.

## Hosted Linux preparation: not verified

No hosted workflow was dispatched for this candidate. Source inspection of `.github/workflows/full-stack-conformance.yml` shows `ubuntu-24.04` for authorization and as the default live runner; `INJI_USE_SELF_HOSTED_RUNNER=true` is an explicit override. The managed path uses normal Linux Docker, Python and Java commands, RUNNER_TEMP, git archive and relative paths, with no WSL commands or /mnt/c paths. This is source inspection, not a verified native Linux deployment.

`host-gateway` extra_hosts is **absent**, so that requested property cannot be confirmed. `docker/docker-compose.yml` instead assigns `host.docker.internal` to the shared TLS ingress on the internal Docker network, and the runner resolves that hostname to loopback for host-side clients. Docker-internal traffic goes directly to ingress; host listeners bind to loopback. Overriding that same hostname with host-gateway would redirect container calls away from the validated ingress alias to host ports which may not listen on the bridge address. No untested networking change was made merely to match that setting. Stock run `019bf015dcef47029010faa06a2cf788` verifies the current design on Docker Desktop, not native hosted Linux.

After separate approval, the managed hosted run would:

1. Validate an authorized default-branch/manual or eligible release revision and its ancestry.
2. Check out the exact harness SHA and pinned commons, Certify and Verify API rigs without persisted checkout credentials.
3. Install Python 3.12, Java 21, checksum-verified Maven 3.8.7, Python dependencies and Chromium with OS dependencies.
4. Build commons and compile both native reporting integrations and classpaths.
5. Generate development keys/configuration, build the pinned suite and MinIO images, and pull stock product/dependency images; patched issuer build is excluded from the stock path.
6. Extract git archive into RUNNER_TEMP and start ten services with five freshly owned volumes; configure synthetic local issuance and native handoffs.
7. Execute the selected official issuer/verifier plans, retrieve exports/screenshots, run native and consolidated TestNG/Extent reporting, upload artifacts to local MinIO and verify read-back.
8. Enforce the existing gates without exemptions, clean only owned resources, sanitize CI artifacts and upload them for seven-day retention, including on failure.

Required dispatch settings would be `INJI_MANAGED_LOCAL_STACK=true`, no true self-hosted override, `component=combined`, `issuer_build=stock`, and the existing protected environment approval. Both gates may fail on the documented product/REVIEW outcomes; workflow success is not promised. Capacity, cold downloads and native Linux networking are **not verified**. No push, merge, publication, release, repository setting change or live workflow was performed in this task.

## Empty-cache Linux run: prepare only, not verified

Run only after approval, on a disposable dedicated Ubuntu 24.04 machine with Docker Engine/Compose, Git, Python 3.12/venv and JDK 21 installed. The prune removes unused Docker resources on that machine; never use it on a shared development host. A fresh machine also needs an empty Maven cache and the approved candidate available as a commit; the currently unpublished working tree is not included in an existing remote HEAD.

```bash
set -euo pipefail
docker system prune --all --volumes --force
REVISION='<approved full commit SHA containing this candidate>'
ROOT_DIR="$(mktemp -d "$HOME/inji-cold-XXXXXXXX")"
git clone https://github.com/SantoshReddy0603/mosip-inji-conformance.git "$ROOT_DIR/repository"
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

This sequence is prepared, not executed. Exit 1 must be diagnosed from official results and reporting/storage receipts; it must not be converted to success. The clean wrapper handles owned deployment cleanup. A private repository may require interactive Git authentication; no token is needed in chat.


## Hosted inputs and gated action commands

B1 implementation CI run `40163129216` on candidate `6f1e31b5ffe60740ab9db6bc1ffa5463708e0c0f` exposed a native keymanager patch-application failure before Maven tests (`closeout/hosted-keymanager-failure.log`). LF normalization had changed CRLF context required by the pinned upstream CertificateUtility.java. The original audited patch bytes were restored exactly, with a targeted -text attribute preventing Git renormalization; all shell files remain LF. Strict git apply --check fails for normalized bytes and succeeds for the restored original (`closeout/patch-line-ending-reproduction.json`). The actual pinned native build then passed, exit 0 (`closeout/native-keymanager-build/build-provenance.json` and test-results). No native logic or stock issuer behavior changed. Updated hosted CI must be verified separately.

Readiness is source-verified by `.github/workflows/full-stack-conformance.yml`, not verified by a new hosted full-stack execution. Its authorization job uses ubuntu-24.04 and its live job defaults to ubuntu-24.04 unless INJI_USE_SELF_HOSTED_RUNNER=true. No WSL command, Windows drive path or /mnt/c path occurs in the workflow. Results are sanitized by runner/ci_artifacts.py and uploaded with actions/upload-artifact under live-conformance-results on success or failure, with seven-day retention. Source/flags and local syntax checks are recorded in closeout/runbook-checks.json and static-checks.json.

For managed stock execution, set INJI_MANAGED_LOCAL_STACK=true and keep INJI_USE_SELF_HOSTED_RUNNER unset or false. The clean wrapper generates development issuer/storage/login keys and credentials and exports its native client IDs, JWKS file paths, scope, configuration ID, authorization-server URL, private_key_jwt and the selected sender-constraining default. No external issuer account or chat-provided secret is required. Nonempty version defaults come from docker/.env; unknown SDK versions are rejected. The external deployment mode instead needs reachable endpoint URLs, the real registered issuer clients and browser steps, available files named by configuration paths, trusted CA material and writable S3 credentials. OIDF_TOKEN is needed only for an authenticated suite; VCI_CLIENT_SECRET only for a client authentication method using it. File-path variables must point to real files available on that runner; setting a path string does not provision a file.

The exact job environment mapping is:

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
| `AWS_ACCESS_KEY_ID` | `${{ secrets.AWS_ACCESS_KEY_ID }}` |
| `AWS_SECRET_ACCESS_KEY` | `${{ secrets.AWS_SECRET_ACCESS_KEY }}` |
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

VCI_SENDER_CONSTRAIN is explicitly mapped from vars in external mode. Managed mode exports its locally validated selection in run-clean-conformance.sh, together with VCI_CLIENT_ID, VCI_CLIENT2_ID, VCI_WALLET_JWKS_FILE, VCI_WALLET2_JWKS_FILE, VCI_AUTHORIZATION_SERVER, VCI_SCOPE, VCI_CREDENTIAL_CONFIGURATION_ID, VCI_CREDENTIAL_FORMAT and VCI_CLIENT_AUTH_TYPE. Managed mode intentionally does not inherit unrelated external issuer secrets. Configure no stock expected-failure waiver or patched-image override.

B1 was explicitly authorized in this conversation after the local scope was clarified: publish only a candidate branch and draft PR, which triggers ordinary hosted CI. No main-branch push, merge, release or managed workflow was included. Equivalent commands after the exact source is tested are:

```bash
git switch -c fix/stock-validation-closeout
git add -A
git commit -m "Complete stock validation and submission drafts"
git push -u origin fix/stock-validation-closeout
gh pr create --draft --base main --head fix/stock-validation-closeout --title "Complete stock validation and submission drafts" --body-file /path/to/reviewed-pr-body.md
gh pr checks --watch
```

The actual execution may use the connected GitHub API instead of gh; GitHub CLI installation/authentication is not verified. Estimated B1 time is 15–45 minutes, not verified: repository/workflow write permission, dependency downloads, stale base or hosted checks can fail. No fixed duration is promised. Use an immutable tested candidate SHA when evaluating checks.

B2 remains approval-gated. After authorization and a legally runnable default-branch candidate, the equivalent commands would be:

```bash
gh workflow run full-stack-conformance.yml --repo SantoshReddy0603/mosip-inji-conformance --ref main -f component=combined -f issuer_build=stock
gh run list --repo SantoshReddy0603/mosip-inji-conformance --workflow full-stack-conformance.yml --limit 5
gh run watch ACTUAL_RUN_ID --repo SantoshReddy0603/mosip-inji-conformance --exit-status
```

Estimated B2 time is 30–180 minutes, not verified; timeout is 180 minutes in the workflow. Cold image/Maven/browser downloads, disk/memory capacity, native Linux ingress, environment approval and actual stock/REVIEW gate failures can prevent success. The existing workflow is restricted to default-branch dispatch or eligible published releases and validates ancestry. Therefore it cannot test the unmerged candidate branch as requested before B3. Do not publish a release, merge early or weaken that authorization to bypass this circular dependency. A separately authorized design decision is needed before candidate B2 can run.

B3 remains approval-gated and blocked unless both B1 and B2 genuinely pass. If that condition is met, the equivalent guarded command is:

```bash
gh pr merge ACTUAL_PR_NUMBER --repo SantoshReddy0603/mosip-inji-conformance --squash --match-head-commit ACTUAL_TESTED_CANDIDATE_SHA --delete-branch
```

Estimated merge time is 1–5 minutes, not verified; protected-branch requirements, a changed head, conflicts or a failed live gate must stop it. Known failed stock and REVIEW gates are not B2 success. No merge is authorized by B1.

B4 remains approval-gated: use the exact empty-cache sequence above only after naming and approving a disposable clean machine. Estimated time is 1–3 hours, not verified; prune removes unused Docker resources, downloads may fail and hardware capacity may be insufficient. No docker system prune command was executed. The prepared source revision placeholder must be replaced by the actual approved candidate commit; remote main currently need not contain this unpublished candidate.


## B2 scratch hosted attempt — not verified

On 25 October 2026, one approved workflow_dispatch ran in private scratch repository `SantoshReddy0603/inji-conformance-b2-scratch`, default branch main, exact unmerged PR #7 commit `ce7a50e81cdea4081fa1061573e24c8d76094d68`. Run [40164823727](https://github.com/SantoshReddy0603/inji-conformance-b2-scratch/actions/runs/40164823727) used component=combined and issuer_build=stock. Scratch configuration contained only INJI_MANAGED_LOCAL_STACK=true, an inji-conformance environment allowing main, and zero repository secrets; no main-repository secrets/settings/policy were copied or changed. Main PR #7 remains unmerged. Evidence: b2-scratch/configuration.json, dispatch-receipt.json and run-state.json.

The authorize-revision job PASSED. The Stock release conformance gate job used a GitHub-hosted ubuntu-24.04 runner and built the native reporting integrations, but FAILED in Prepare pinned development images when absent. Its exact fatal message was `error while interpolating services.minio.environment.MINIO_ROOT_USER: required variable AWS_ACCESS_KEY_ID is missing a value: Run runner/setup.py` (image preparation log lines 58–63, exit 1). Classification: WORKFLOW_BUG. Empty job-level AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY environment values override generated nonempty docker/.env values during direct Compose commands. The isolated runner already handles owned configuration, but this earlier workflow step does not. Dependency/plugin warnings in the integration log are not the fatal cause: those integration builds finished successfully.

The stack was not started: ten-service startup is not verified. Issuer/verifier official plan execution and expected stock 2 PASSED / 10 INTERRUPTED / 3 SKIPPED and Verify 4 PASSED / 6 REVIEW are not verified on hosted Linux. No new official counts or plan IDs exist; local historical counts must not be substituted. Reports, Extent/TestNG output, MinIO read-back and owned-volume cleanup are not verified. The cleanup step returned success without an isolated-state file, so it was a no-op and does not establish cleanup of a started stack. No conformance summary existed; restricted export and artifact upload consequently failed. GitHub lists zero artifacts. This is an implementation startup failure, not the expected strict conformance-gate rejection.

The complete workflow log ZIP was downloaded and CRC checked: b2-scratch/run-40164823727-logs.zip, SHA256 `381c1e65bfb9af798dd6ca119d8cde98efced9351ae11067c03fa6c20cbeac9c`. Artifacts were requested but none exist; none were fabricated. Structured job/step timestamps and conclusions are in run-state.json. Only one dispatch was made, with zero reruns.

Proposed minimal startup correction, not applied: unset the two inherited AWS variables immediately after setup.py in the managed image-preparation step so Compose consumes generated docker/.env. Diff: b2-scratch/proposed-startup-fix.diff. A separate proposed evidence-retention step, also not applied, uploads native/consolidated HTML/XML reports and storage/cleanup receipts needed to judge B2; the existing restricted-summary-only upload does not retain those deliverables. Diff: b2-scratch/proposed-report-retention.diff. It excludes raw credential exports, private keys and generated .env. Both preserve the default-branch guard, selected stock path, result mapping, strict gates and read-only workflow permissions. Approval is required before applying either diff, publishing an updated candidate or making the first rerun; at most two reruns are permitted. No workflow code was modified in this attempt.

The scratch repository is preserved pending the owner's deletion decision. B3 merge, B4 independent empty-cache validation, organizer acceptance of Java 21, final video/pitch and submission approval remain pending. No release was published. The expected failed conformance gate will be acceptable evidence for B2 only if every requested execution/report/storage/cleanup criterion is actually verified in a later approved run.


## Approved B2 retry preparation

The owner approved both proposed fixes, publication to PR #7 and exactly one scratch retry, requiring a cross-step AWS audit. The final correction removes AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY from job env entirely; an external-mode-only step validates nonempty secret inputs and writes them to GITHUB_ENV. Managed image preparation, execution and cleanup therefore inherit no empty workflow-exported AWS credential variables. Image preparation reads generated docker/.env directly; isolated_stack.py merges owned .env for execution/cleanup, and run-clean-conformance.sh loads generated storage credentials before reporting. The original single-step unset proposal is superseded. The approved report-retention action preserves native/consolidated HTML/XML reports and storage/cleanup receipts without raw key/config exports. Exact diff and validation: b2-scratch/retry1/final-workflow.diff and local-checks.json. Workflow/actionlint and shell checks passed; guards, permissions, timeout, stock behavior, REVIEW handling and gates are unchanged. Retry outcome is not verified until its actual run completes. No further retry or scratch deletion is authorized.


## B2 verified scratch retry — 25 October 2026

All five owner-defined B2 implementation criteria are verified in private scratch repository [SantoshReddy0603/inji-conformance-b2-scratch](https://github.com/SantoshReddy0603/inji-conformance-b2-scratch), default branch main, exact unmerged PR #7 candidate `9c8d94ad9da42ac458ea304192118266577469f9`. Hosted [run 40165722639](https://github.com/SantoshReddy0603/inji-conformance-b2-scratch/actions/runs/40165722639) was the single approved retry. Ordinary PR CI also passed for that candidate ([40165694278](https://github.com/SantoshReddy0603/mosip-inji-conformance/actions/runs/40165694278)). No merge, release, main-repository setting/policy change, copied secret, further retry or scratch deletion occurred.

| B2 success criterion | Result | Evidence |
|---|---|---|
| Ten-service stack starts on ubuntu-24.04 | PASS | run-state.json hosted runner labels; execution log has Started for all ten services; isolated-stack-state.json records ten images and five owned volumes |
| Official issuer and selected verifier plans execute | PASS | issuer plan vir0sD8It1IDI; verifier plan UZtgjxUuLpdPj; official run 2583bed425d64f5abb0c86993d402116; runner REST calls and module outcomes in logs and ci-summary.json |
| Native/consolidated reports and storage evidence produced/uploaded | PASS | managed-reporting-evidence artifact 12587788827 and live-conformance-results artifact 12587654719; both downloaded and CRC checked |
| Storage verification and owned cleanup succeed | PASS | artifact-storage-validation.json verifies 114 objects; execution log reports all five owned volumes removed with zero remaining; cleanup step success |
| Expected stock and verifier counts match local reference | PASS | ci-summary.json: Certify 2 PASSED / 10 INTERRUPTED / 3 SKIPPED; Verify 4 PASSED / 6 REVIEW |

Evidence paths in this section are under private outputs/b2-scratch/retry1/. Structured assessment: assessment.json. Download manifests: download-receipts.json. Full logs: run-40165722639-logs.zip, SHA256 `b1d256636d9b1b27afc2f8cce6ccb580955e747189c9b46074820f23948d6ff2`. Restricted results artifact 12587654719 contains ci-summary.json and ci-report.html. Reporting artifact 12587788827 contains both real API-rig reports, consolidated extent-report.html/testng-results.xml, reporter exit codes, storage receipt and final owned deployment state. Twenty-three downloaded report files matched their recorded storage SHA256 and byte counts.

Per-job results: authorize-revision SUCCESS; Stock release conformance gate FAILURE. The sole failed step was Execute and gate live plans, exit 1, supported by actual nonpassing official outcomes; native/consolidated reporter exits were certify=1, verify=1, combined=1. Image preparation, restricted summary export, both artifact uploads and the explicit cleanup step succeeded. Combined official counts are 6 PASSED, 10 INTERRUPTED, 6 REVIEW and 3 SKIPPED. Both product gates and the combined release gate remain FAILED. TestNG includes its extra gate assertion: combined 26 checks / 6 passed / 17 failed / 3 skipped; native Certify 16 / 2 / 11 / 3; native Verify 11 / 4 / 7 / 0. B2 verification is implementation validation under the owner's stated criteria, not stock conformance, REVIEW approval or certification.

The execution wrapper's first cleanup log records removal of five volumes. The workflow's second idempotent cleanup records zero removed/zero remaining and overwrites the final state file's removed list. Therefore the final state alone proves absence, while original log lines 16592 and 16643 prove both cleanup calls; no evidence was edited to hide that distinction. No deployment/data leak was inferred from the overwritten list.

Stock image reference was injistack/inji-certify-with-plugins:1.0.0-alpha.1, observed image ID `sha256:75170c3bb5ccb13869637e7450c16994f496104529bb4ce56f336d19475d1f46`. This differs from the earlier local image ID; claim scope is this recorded hosted image, not byte-identical release reproducibility. Actual official export ZIPs were uploaded to ephemeral MinIO and verified by storage receipt/logs (plan-vir0sD8It1IDI-export.zip and plan-UZtgjxUuLpdPj-export.zip). Their raw bytes were not retained as GitHub artifacts, so offline reinspection of those raw export ZIPs is not verified; original local exports remain preserved separately. This does not imply that raw credentials/private keys were published.

Applied code change remains only .github/workflows/full-stack-conformance.yml: job-level AWS credential exports removed; external-mode-only nonempty credential loader added; managed reporting artifact upload added. Authorization guard, immutable revision/ancestry checks, stock path, REVIEW mapping, strict gates, permissions and 180-minute timeout were preserved. Final diff: final-workflow.diff; local policy/actionlint/loader checks: local-checks.json; full Python regression: python-tests.xml, 196 passed / 31 warnings / exit 0. No shell source changed and all .sh files remain LF.

The scratch repository remains private and retained for the owner's deletion decision. Further retry requires fresh approval. B3 merge is still unperformed and requires its own authorization; the owner-defined B2 harness success does not convert the conformance gate into PASS. B4 separate clean-machine validation, the organizer's Java 21 answer and final submission/demo materials remain external pending or not verified as described in the checklist.

## Retained B2 evidence for B3

B2 is verified only for private scratch repository `SantoshReddy0603/inji-conformance-b2-scratch`, run `40165722639`, commit `9c8d94ad9da42ac458ea304192118266577469f9`; it was not a main-repository run. The previously downloaded logs and both artifacts were copied into private `EVIDENCE_ROOT/b3-closeout/evidence/` and rechecked against their download SHA256 receipts and ZIP CRCs. `manifest.json` records their hashes and source run; `assessment.json` records the five verified B2 implementation criteria. This evidence folder is separate from the source repository and must accompany a controlled evidence handoff.

| Retained file | Evidence |
|---|---|
| b3-closeout/evidence/run-40165722639-logs.zip | Complete hosted workflow logs |
| b3-closeout/evidence/artifact-12587654719.zip | live-conformance-results: summary and report |
| b3-closeout/evidence/artifact-12587788827.zip | managed-reporting-evidence: native/consolidated reports, storage and cleanup receipts |

The strict conformance gates remain FAILED; raw hosted official export ZIP bytes were not retained in these artifacts. B3 approval covers final documentation publication and a merge only after all CI jobs pass on the final PR head; B4, further live runs and scratch deletion remain unperformed.
