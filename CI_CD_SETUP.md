# CI/CD execution and security

Ordinary hosted CI and live official conformance have separate acceptance criteria. Historical implementation checks passed five jobs on their tested revisions. Check the Actions tab of your configured repository for the exact source revision; historical success does not establish that later revisions passed.

## Production releases and manual execution

`full-stack-conformance.yml` subscribes only to `release: published` and manual dispatch. It filters draft and prerelease releases. There is no tag-push subscription, avoiding duplicate tag/release executions; edits and draft creation do not run conformance. Manually dispatch only the repository default branch. A published production release uses GitHub's immutable event SHA, which is the tagged release commit. A disposable hosted authorization job checks the event, checks out that SHA and verifies default-branch ancestry before the live job is eligible. Live checkout uses the authorized SHA, never the moving tag or branch. Both jobs have only contents:read. Actions are pinned; checkout never persists credentials. Repository-wide live concurrency queues runs without cancelling active ones. Workflow changes are not deployed until approved for main.

The `inji-conformance` environment restricts deployment to main and v* tags. Required reviewers are unavailable for the current private-repository plan; they are not configured or claimed enforced. Preserve explicit owner approval for each privileged live run and release. See [RUNNER_OPERATIONS.md](RUNNER_OPERATIONS.md) for the operator procedure and its limits. YAML does not create environment protections. Review the exact commit's ordinary CI before approving live execution. Never assign the dedicated runner to PR workflows. Publication/merge/release and runner registration require owner approval; this implementation does not grant it.

## Runner feasibility and deployment modes

Existing reachable deployment (default): the live job uses disposable GitHub-hosted ubuntu-24.04. Docker is available, but services are not initialized or shut down by this mode because they belong to the supplied deployment. Set OIDF_URL, CERTIFY_ISSUER_URL, VERIFY_API_URL, VERIFY_UI_URL, CA_BUNDLE and real plan/browser configuration through repository Actions Variables (Settings > Secrets and variables > Actions > Variables). Wallet private JWK files must be provisioned securely on the runner at the configured paths; use an authorized secret-provisioning mechanism. Set the issuer login, OIDF token and S3 credentials only when the deployment needs them, in environment Secrets. S3_ENDPOINT and S3_BUCKET must point to an existing accessible automationtests bucket. Localhost URLs cannot reach this laptop from a GitHub VM. No password or token belongs in chat.

Managed synthetic stack: set repository Actions variable INJI_MANAGED_LOCAL_STACK=true. The default runner is disposable ubuntu-24.04. Set INJI_USE_SELF_HOSTED_RUNNER=true only when explicitly selecting an approved Linux x64 runner labelled inji-conformance. Repository variables must select runs-on before protected-environment variables become available.

The unified ingress uses a Docker DNS alias and loopback host ports, rather than Docker Desktop host-gateway routing. Managed execution was verified on GitHub-hosted ubuntu-24.04 in [scratch run 40165722639](https://github.com/SantoshReddy0603/inji-conformance-b2-scratch/actions/runs/40165722639) at `9c8d94ad9da42ac458ea304192118266577469f9`: ten services, both official plans, retained reports, 114 storage objects verified and five owned volumes removed. The conformance gate remains FAILED; other configurations remain not verified. Plan for at least 8 GiB memory and sufficient image/Maven/browser disk space; inspect actual capacity before starting. A local success does not prove hosted resource capacity.

The job uses a fresh source extraction, generated development secrets/keys and five fresh owned volumes. Stock is the production-release default. Image/dependency caches may be reused. Cleanup verifies ownership and never prunes the shared daemon. No external issuer registry or personal data is required.

Install a dedicated runner only after approval: repository Settings > Actions > Runners > New self-hosted runner; select Linux x64, follow GitHub's local registration commands and add label inji-conformance. Keep registration tokens local. Use an isolated workspace and Docker daemon for trusted jobs. A historical live workflow executed an approved main revision. Its official six-REVIEW benchmark failed, while service startup, reporting, storage, artifact upload and cleanup completed. The ephemeral runner unregistered afterward. New changes require their own CI and merge approval.

## Execution, artifacts and honest failures

The live entrypoint performs readiness, real issuer/verifier plans, polling/exports, native module TestNG/Extent, consolidated reports, verified MinIO/S3 upload and strict gating. Restricted CI summaries upload after success or failure; raw screenshots, signed exports and credentials remain private. Managed infrastructure cleanup also executes after failure. An infrastructure failure and an official benchmark failure are different diagnoses. A six-REVIEW result must remain exit 1, never a green job. Request URI POST: **POST coverage not established.** Certification and OIDF contact are optional and are not assignment prerequisites.

A recorded release-triggered workflow verified deployment, official plan execution, reporting, storage, artifact upload and cleanup. Its strict gate failed for six REVIEW outcomes. Subsequent live workflows require an approved ephemeral runner and a reviewed source revision.

GitHub variable timing reference: [Configuration variable precedence](https://docs.github.com/en/actions/reference/workflows-and-actions/variables#configuration-variable-precedence). Store workflow configuration variables at repository Actions scope and credentials in protected environment Secrets. Environment protections remain a separate owner configuration.

## Independent component gates

Each component summary preserves its raw conformance decision in `is_gated_pass` and now records `regression_gate_met` and the effective `gate_met`. Known test regressions/removals are scoped by component; invalid/unscoped comparisons fail closed. A failed Verify gate cannot fail Certify's own TestNG gate. The combined gate remains the conjunction of the selected component gates. Older summaries without scoped regression metadata retain the conservative legacy fallback. Read-only retained validation can create explicitly labeled derived summaries after verifying the official API, preserving originals and timestamps. Offline re-reporting of preserved the earlier official run results is separately labeled and never claimed a new official execution.

Runner operation: [RUNNER_OPERATIONS.md](RUNNER_OPERATIONS.md). Empty-cache validation: [SETUP.md](SETUP.md#isolated-reproduction). Recorded summary: [README.md](README.md#recorded-stock-and-patched-results).

## Stock default and remote validation

Managed production-release jobs use the configured unmodified Certify image. Patched builds are an explicit manual diagnostic choice and remain separately labelled in conformance provenance. Their PASS counts never qualify stock releases. REVIEW stays a strict failure for both.

The unified ingress removes the host-gateway dependency. A workflow file alone does not prove hosted execution. Provisioning privileged runners, publication and merges retain the owner-approval boundary. The scope of the verified hosted managed stack is scratch run 40165722639 at 9c8d94ad9da42ac458ea304192118266577469f9; other hosts, profiles and B4 empty-cache execution remain not verified.
