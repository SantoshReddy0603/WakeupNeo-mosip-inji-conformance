# GitHub CI/CD setup

Source is prepared locally. No GitHub repository or workflow run has been created for this project. Do not confuse successful local validation with GitHub Actions verification.

## Publication boundary

Use the separately prepared source-only archive/checkout, not runtime reports, the reviewer bundle, original suite exports or generated local credentials. Source preparation scans actual environment secrets and private key files. Test fixtures remain explicitly controlled data. Do not publish docker/.env, docker/local, generated certificates, classpaths, caches, target directories, private keys or raw live exports.

The connected GitHub account was verified. No suitable accessible conformance repository was found; the similarly named MOSIP_Quantum5 repository contains a child-health application and must not be overwritten. The connector exposes file/branch/commit publication and Actions read APIs, but no repository creation or workflow-dispatch operation. Repository creation and code publication require user approval. No GitHub password or token is needed in chat.

## Ordinary CI

`.github/workflows/ci.yml` runs on pushes to main and pull requests targeting main, plus manual dispatch. Its jobs are harness-tests, native-certify-tests, native-keymanager-tests, and the Certify/Verify api-rig-integration matrix. They use hosted Ubuntu 24.04, Python 3.12, Java 11 for the standalone bridge and Java 21 for native modules, immutable action/source commits and pip/Maven caches. Required checks do not use continue-on-error. Checkout credentials are not persisted.

The harness job installs requirements-ci.txt, compiles Python, runs Ruff undefined-name checks, validates workflow security and Bash syntax, generates isolated local configuration, validates Compose, runs the complete pytest suite and executes seven real standalone TestNG bridge contract scenarios. The native jobs package and test the shipped fixes. Each API-rig job compiles the real integration and executes all 11 result mappings through native TestNG. Controlled expected-failure fixture exits are asserted by their validators, not presented as official conformance passes. JUnit/TestNG/Extent validation artifacts upload even after failures, with missing artifacts treated as errors.

## Authorized live workflow

`.github/workflows/full-stack-conformance.yml` is manual only and requires the repository default branch, a dedicated self-hosted Linux x64 runner labelled inji-conformance, and the inji-conformance environment. Configure that environment with required reviewers and a default-branch deployment restriction **before dispatching**; a YAML environment name alone does not install those GitHub protections. Reviewers should verify ordinary CI for the exact selected commit before approving a live run. Do not attach this runner to untrusted pull-request workloads.

Choose one deployment mode:

1. Existing deployment (default): configure the workflow's documented vars for OIDF, Certify, Verify, browser handoff, local wallet key file paths and CA trust. Supply only genuinely necessary environment secrets through GitHub environment settings. The runner must reach all URLs; localhost addresses refer to the runner, not this laptop. The workflow calls the existing --skip-docker entrypoint and validates endpoint readiness. No stored laptop credentials are exported by publication.
2. Managed development stack: set environment variable `INJI_MANAGED_LOCAL_STACK=true` in GitHub environment Variables. This uses the actual full --native-positive bootstrap and existing synthetic course data, supported plugins, development keys and MinIO. This mode requires Docker Desktop connectivity from the dedicated Linux/WSL runner, free local service ports, Docker/Maven/Git access and network access to upstream dependencies. Generated local secrets stay on the runner. The trusted primary checkout deliberately uses clean:false to preserve generated credentials used by persistent Docker volumes; do not share this workspace with untrusted jobs. It does not delete volumes. Fresh empty-volume bootstrap and remote execution are not newly verified.

Default component is combined with --parallel 2. Native module and consolidated TestNG/Extent generation and S3 read-back are part of the existing entrypoint. --insecure is limited to managed development TLS; existing-deployment mode uses its configured CA. Protocol validation remains enabled in both. The workflow exports only runner/ci_artifacts.py restricted output after success or failure. Raw screenshots, signed exports, credentials and backend logs remain private. CI artifact retention is seven days.

The live workflow must fail while the six official REVIEW outcomes remain unresolved. The code CI suite is independent of those external assessments. Request URI POST is not supported by the pinned native release; see the Stage 18 HTTP probe and report. The selected plan, profile and original results remain unchanged.

## Shortest next steps

After reviewing the prepared source, choose an existing suitable repository or create a new **private** repository, for example mosip-inji-conformance, with main initialized using a README. Grant the GitHub app access if needed. Share its URL and explicitly approve publication to a development branch and creation of a draft PR. The connector can then publish the source and inspect actual PR Actions runs, logs and artifacts. Repository creation is unavailable through this connector, so it needs the GitHub web UI. No merge is authorized by that approval.

Once ordinary CI passes, review/merge separately, configure the protected environment and register the dedicated runner through Settings > Actions > Runners > New self-hosted runner. Registration tokens belong only in the runner's local configuration command, never in chat or source. Dispatch Authorized live conformance release gate using Actions > Run workflow on the default branch. The connector can inspect its real run through GET /repos/OWNER/REPO/actions/runs and job/log/artifact tools; its commit helper alone only lists PR-triggered runs. Do not report remote success before those actual results exist.
