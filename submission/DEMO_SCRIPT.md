# Demo script — approximately 5 minutes

Recording is **not verified**: this is a shot list, not a video or execution receipt. Record genuine
output. Cut or visibly time-lapse long downloads, startup and suite execution; the test run itself is not
promised to complete within the video's duration. Never replace an official result with a staged PASS.
Commands below are prepared instructions; this exact demo sequence is **not verified**. Existing command
evidence is indexed in EVIDENCE_INDEX.md.

Before recording, use a dedicated local checkout with prepared images, Docker/Compose, Python dependencies,
matching Chromium, Java 21 and Maven 3.8.7 as described in README. Activate the prepared virtual environment.
Set PROJECT_ROOT to this checkout. Keep runtime
secrets and raw credentials out of the recording. No GitHub workflow is triggered by this script.

| Video time | Shot | Exact command / action |
|---|---|---|
| 0:00–0:30 | State assignment, stock build, strict gate and exact verifier plan | `cat config/verify-oid4vp-config.json.template` |
| 0:30–1:00 | Show ten prepared services | Commands 1 below; show suite at https://localhost:8443 and Verify at https://localhost:8445/verify |
| 1:00–2:00 | Run the one-command combined harness; visibly cut waiting | Commands 2; retain the real exit code and run ID |
| 2:00–3:00 | Open both native module reports | Commands 3; open the two exact native report URLs |
| 3:00–3:35 | Show consolidated report and failed benchmark honestly | Open http://localhost:8765/extent-report.html; show summary/reporters |
| 3:35–4:05 | Explain empty expected-failures file and tested diff support | Commands 4; label tests as harness contracts and stock/patched diff as a build comparison |
| 4:05–4:35 | Explain CI and artifact retention | Commands 5; view the historical CI URL, label its exact revision |
| 4:35–5:00 | State product gaps, six REVIEWs, unverified coverage and cleanup | `cat submission/LIMITATIONS.md`; Commands 6 after recording |

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
export DEMO_REPORTS
printf 'Report folder: %s\n' "$DEMO_REPORTS"
set +e
bash run-full-stack-conformance.sh --insecure --parallel 2 --reports-dir "$DEMO_REPORTS"
RUN_EXIT=$?
set -e
printf 'Actual conformance exit: %s\n' "$RUN_EXIT"
test -s "$DEMO_REPORTS/conformance-summary.json" || exit 1
export RUN_ID="$(python -c 'import json,os; print(json.load(open(os.path.join(os.environ["DEMO_REPORTS"],"conformance-summary.json")))["run_id"])')"
cat "$DEMO_REPORTS/reporter-exit-statuses.json"
```

Show the current run's results, not assumed counts. The preserved stock reference
019bf015dcef47029010faa06a2cf788 failed its combined gate. Component-only alternatives are `bash
run-conformance.sh --component certify --insecure --reports-dir "$HOME/inji-demo-certify"` and the
corresponding `--component verify` with a distinct empty report directory; do not run those during this shot
merely to imply extra coverage.

## 3. Reports

In a second terminal, with DEMO_REPORTS set to the directory printed above:

```bash
python -m http.server 8765 --bind 127.0.0.1 --directory "$DEMO_REPORTS"
```

Open http://localhost:8765/existing-certify/ACTUAL_RUN_ID/index.html and
http://localhost:8765/existing-verify/ACTUAL_RUN_ID/index.html, replacing ACTUAL_RUN_ID with RUN_ID. Then open
http://localhost:8765/extent-report.html. The native index.html paths exist in stock reference run
019bf015dcef47029010faa06a2cf788; reports from a new failed startup may be absent and must not be substituted
silently. Serve only on loopback, then stop the server with Ctrl+C.

## 4. Expected failures and diff

```bash
cat config/expected-failures.json
python -m pytest tests/test_optional_features.py -q -k 'exception_file or expected_failure or diff_records'
```

These tests demonstrate labelled synthetic harness fixtures for exception handling
and regression comparison. They are not official conformance evidence. No exemption
is added to the shipped configuration. For a recorded comparison, use the preserved
stock and diagnostic result receipts in the evidence handoff; they describe different
builds and do not prove a stock release was fixed.

## 5. CI

```bash
cat .github/workflows/ci.yml
cat .github/workflows/full-stack-conformance.yml
```

View https://github.com/SantoshReddy0603/mosip-inji-conformance/actions/runs/40165694278 for the passed
ordinary CI and cite private scratch run `40165722639` for the recorded hosted execution. Both used commit
9c8d94ad9da42ac458ea304192118266577469f9. Explain that the full-stack gate job is red because the official
stock interruptions and six REVIEWs correctly reject release; all five recorded hosted implementation criteria
passed. Downloaded evidence is indexed in evidence/README.md; the reports and logs are not included in the
repository. Google Drive handoff is deferred and reviewer access is not verified. Show retained evidence as a
recorded run, not a newly executed demo. Do not dispatch another managed workflow for the video without fresh
approval.

## 6. Finish and stop the dedicated demo stack

```bash
docker compose --env-file docker/.env -f docker/docker-compose.yml --profile certify --profile verify --profile storage down
```

This command stops that persistent demo project's containers without deleting volumes. It is prepared only,
not executed by creating this script. Do not stop an unrelated deployment. The separate
run-clean-conformance.sh entrypoint performs owned cleanup automatically when used for a fresh source-only
extraction.
