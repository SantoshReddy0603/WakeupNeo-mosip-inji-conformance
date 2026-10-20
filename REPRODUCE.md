# Reproducing Stage 16

Use Linux or WSL Ubuntu, Python 3.12, Java 21, Maven, Docker Compose and a running Docker Desktop/Linux engine. Full Windows Java reporting was not verified. Keep generated development credentials local.

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r runner/requirements-dev.txt
python -m playwright install chromium
python runner/setup.py
export PYTHON="$PWD/.venv/bin/python"
export CONFORMANCE_RESOLVE_LOCAL=true
python -m pytest tests -q --junitxml=reports/harness-tests.xml
for n in $(seq 1 10); do python -m pytest tests/test_reliability.py -q || exit; done
bash -n run-conformance.sh
bash -n run-full-stack-conformance.sh
mvn -B -f testrig/pom.xml test-compile
```

`evidence/core/environment.log` records actual tool versions. `evidence/python-dependencies.json` records installed Python versions. Requirements retain their existing compatible ranges; an empty dependency cache was not tested. Actionlint was run with `-shellcheck= -config-file .github/actionlint.yaml .github/workflows/full-stack-conformance.yml`; this validates workflow syntax and expressions, while Bash was parsed separately. No shellcheck or remote Actions success is claimed.

Clean native builds (use new output directories; build helpers validate pinned caches and use Linux temporary sources):

```sh
python runner/build_native_keymanager.py --output-dir reports/new-keymanager-build
python runner/build_native_certify.py --positive-serial
```

The Certify helper also builds the supported native Docker image. Stage 16 independently cloned the pinned source to `/tmp`, applied all five shipped patches and ran the native Maven `package` selection recorded verbatim in `evidence/core/commands.json`. Existing Maven dependencies were reused; source targets were clean. Selected native test counts are 49 and 3, not a claim that every upstream test ran.

For a new local deployment and fresh official plans:

```sh
./run-conformance.sh --component certify --native-positive --insecure --reports-dir reports/new-certify
./run-conformance.sh --component verify --insecure --reports-dir reports/new-verify
./run-conformance.sh --combined --native-positive --insecure --reports-dir reports/new-combined
./run-conformance.sh --combined --parallel 2 --skip-docker --insecure --reports-dir reports/new-parallel
```

Use `SETUP.md` for environment variables when `--skip-docker` targets an already configured deployment; it deliberately does not generate issuer registrations or wallet settings. Stage 16 started/validated Compose separately, supplied generated settings locally and exercised the fresh entry points using `--skip-docker`. A fresh empty-volume bootstrap was not repeated. `--insecure` is the existing local self-signed HTTPS option used by the browser handoffs; it does not disable protocol/signature/holder checks. Separate readiness checks passed with `CA_BUNDLE` pointing to the actual development certificate. Configure trusted certificates for a non-development deployment.

Verify/combined are expected to exit 1 while six official results remain REVIEW. Do not append a success override or convert statuses to pass. `RESULTS.md` records actual run IDs; every test instance ID and native transaction correlation is in `official-outcomes.json` and the review audits. `run-full-stack-conformance.sh` was checked by retained retrieval of the fresh combined run, without creating duplicate plans.

The submission contains redacted unsigned derivatives of official exports, labelled `SANITIZED`; original signed exports remain intact locally because they contain credentials/private key material. See each derivative's `REDACTION_NOTICE.json` and evidence manifest for hashes. Images are unedited actual UI/report captures. Historical evidence is explicitly separate. Evidence-directory names in original logs describe the capture environment; use the portable commands above after extraction.

When extracting beside an existing deployment, preserve its matching generated `.env` and local keys privately; do not combine newly generated database passwords with existing database volumes. This ZIP excludes that private state. The deployment commands above describe a fresh development environment, while the captured Stage 16 command records target the preserved configured stack.

## Stage 17 review investigation

The current full suite contains 117 tests. Run setup before pytest in a clean extraction; the setup materializes the existing api-testrig integration. Use the existing Stage 16 commands above with new output directories. A new official run creates plans; an `--existing-run <retained-directory>` replay retrieves existing instances without creating plans. Stage 17 created only two new plans using `--combined --parallel 2 --skip-docker --insecure`, then validated all three entrypoint modes against that retained run. Verify/combined must exit 1 on REVIEW.

To re-audit an existing run read-only:

```sh
python runner/audit_verifier_review.py reports/new-combined --output reports/new-review-audit --native-log /path/to/genuine-native-docker.log
```

Use an unused output directory and the actual native logs from the same execution interval. The audit fetches official test and image state; source JSON is never rewritten. Status-reference inspection is structural and does not replace native cryptographic verification. The SDK is transaction-cookie-bound; do not fabricate a JSON transaction ID or capture authentication cookies in review evidence. See REVIEW_FINDINGS.md and evidence/checks/commands.json for precise actual commands, timestamps and exits. No request to send the prepared email or publish evidence has been executed.
