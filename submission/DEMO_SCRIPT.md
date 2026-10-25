# Draft demo script — 6 minutes 30 seconds

Recording is **not verified**: this is a proposed shot list, not a video or execution receipt. Record genuine output. Cut or visibly time-lapse long downloads, startup and suite execution; the test run itself is not promised to complete within the video's duration. Never replace an official result with a staged PASS. Commands below are prepared instructions; this exact demo sequence is **not verified**. Existing command evidence is indexed in EVIDENCE_INDEX.md.

Before recording, use a dedicated local checkout with prepared images, Docker/Compose, Python dependencies, matching Chromium, Java 21 and Maven 3.8.7 as described in README. Activate the prepared virtual environment. Set EVIDENCE_ROOT to the existing private outputs directory and PROJECT_ROOT to this checkout. Keep runtime secrets and raw credentials out of the recording. No GitHub workflow is triggered by this script.

| Video time | Shot | Exact command / action |
|---|---|---|
| 0:00–0:30 | State assignment, stock build, strict gate and exact verifier plan | `cat config/verify-oid4vp-config.json.template` |
| 0:30–1:10 | Show actual stack startup and ten services | Commands 1 below; show suite at https://localhost:8443 and Verify at https://localhost:8445/verify |
| 1:10–2:15 | Run the one-command combined harness; visibly cut waiting | Commands 2; retain the real exit code and run ID |
| 2:15–3:20 | Open both native module reports | Commands 3; open the two exact native report URLs |
| 3:20–4:00 | Show consolidated report and failed benchmark honestly | Open http://localhost:8765/extent-report.html; show summary/reporters |
| 4:00–4:50 | Explain empty expected-failures file and actual-result diff | Commands 4; label tests as harness contracts and stock/patched diff as a build comparison |
| 4:50–5:35 | Explain CI and artifact retention | Commands 5; view the historical CI URL, label its exact revision |
| 5:35–6:30 | State product gaps, six REVIEWs, unverified coverage and cleanup | `cat submission/LIMITATIONS.md`; Commands 6 after recording |

## 1. Stack startup

```bash
cd "$PROJECT_ROOT"
export PYTHON="$(command -v python)"
export CONFORMANCE_RESOLVE_LOCAL=true
python runner/setup.py
docker compose --env-file docker/.env -f docker/docker-compose.yml --profile certify --profile verify --profile storage up -d --no-build
docker compose --env-file docker/.env -f docker/docker-compose.yml --profile certify --profile verify --profile storage ps
```

This uses the stock image selected in docker/.env. It starts persistent development volumes; it is not the gated empty-cache test. Use an unused dedicated demo deployment and keep its keys/configuration out of the source package.

## 2. One-command run

```bash
DEMO_REPORTS="$(mktemp -d "$HOME/inji-demo-reports-XXXXXXXX")"
DEMO_ASSETS="$(mktemp -d "$HOME/inji-demo-assets-XXXXXXXX")"
export DEMO_REPORTS DEMO_ASSETS
set +e
bash run-full-stack-conformance.sh --insecure --parallel 2 --reports-dir "$DEMO_REPORTS"
RUN_EXIT=$?
set -e
printf 'Actual conformance exit: %s\n' "$RUN_EXIT"
export RUN_ID="$(python -c 'import json,os; print(json.load(open(os.path.join(os.environ["DEMO_REPORTS"],"conformance-summary.json")))["run_id"])')"
cat "$DEMO_REPORTS/reporter-exit-statuses.json"
```

Show the current run's results, not assumed counts. The preserved stock reference 019bf015dcef47029010faa06a2cf788 failed its combined gate. Component-only alternatives are `bash run-conformance.sh --component certify --insecure --reports-dir "$HOME/inji-demo-certify"` and the corresponding `--component verify` with a distinct empty report directory; do not run those during this shot merely to imply extra coverage.

## 3. Reports

In a second terminal, with DEMO_REPORTS set to the directory printed above:

```bash
python -m http.server 8765 --bind 127.0.0.1 --directory "$DEMO_REPORTS"
```

Open http://localhost:8765/existing-certify/ACTUAL_RUN_ID/index.html and http://localhost:8765/existing-verify/ACTUAL_RUN_ID/index.html, replacing ACTUAL_RUN_ID with RUN_ID. Then open http://localhost:8765/extent-report.html. The native index.html paths exist in stock reference run 019bf015dcef47029010faa06a2cf788; reports from a new failed startup may be absent and must not be substituted silently. Serve only on loopback, then stop the server with Ctrl+C.

## 4. Expected failures and diff

```bash
cat config/expected-failures.json
python -m pytest tests/test_optional_features.py -q -k 'exception_file or expected_failure or diff_records'
export EVIDENCE_ROOT
PYTHONPATH=runner python - <<'PY'
import json, os
from pathlib import Path
from diff_engine import DiffEngine
root = Path(os.environ['EVIDENCE_ROOT']) / 'implementation-completion'
old = json.loads((root / 'stock-321cd46f/reports/conformance-summary.json').read_text())
new = json.loads((root / 'patched-40d8d65d/reports/conformance-summary.json').read_text())
result = DiffEngine.compare_runs(old, new)
destination = Path(os.environ['DEMO_ASSETS']) / 'stock-versus-patched-diff.json'
destination.write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
PY
```

The exception tests use labelled synthetic harness fixtures, not official conformance evidence. No exemption is added to the shipped file. The diff reads actual preserved results from different builds; it does not prove an unmodified stock release was fixed, and neither input is modified.

## 5. CI

```bash
cat .github/workflows/ci.yml
cat .github/workflows/full-stack-conformance.yml
```

View https://github.com/SantoshReddy0603/mosip-inji-conformance/actions/runs/39772274219 in an authenticated browser. This is historical hosted CI for 2594b3d6f9590caa9d28c6fa2048249ac300f274, supported by github-source-publication/hosted-ci.json; it is not current candidate validation. Show a new candidate CI run only after its exact SHA and conclusion are checked. Do not dispatch the managed workflow for the video without separate approval.

## 6. Finish and stop the dedicated demo stack

```bash
docker compose --env-file docker/.env -f docker/docker-compose.yml --profile certify --profile verify --profile storage down
```

This command stops that persistent demo project's containers without deleting volumes. It is prepared only, not executed by creating this script. Do not stop an unrelated deployment. The separate run-clean-conformance.sh entrypoint performs owned cleanup automatically when used for a fresh source-only extraction.
