# Existing Inji API-test integration

The current `mosip/mosip-functional-tests` repository contains shared `apitest-commons`; the component modules now live in the Inji repositories. Tested sources:

- commons: `085cfa94301738d901c5b70547dbf005cb762c2b`
- Certify v1.0.0-alpha.1: `8fdf71656979a72fa8263766d4dec3cc25127b76`
- Verify v1.0.0-alpha.1: `4c4289026968beb535d3dbdd500947152c43f708`

```sh
python integration/install.py --certify-repo /path/to/inji-certify --verify-repo /path/to/inji-verify
mvn -B -s integration/maven-settings.xml -f /path/to/mosip-functional-tests/pom.xml install -DskipTests
mvn -B -s integration/maven-settings.xml -f /path/to/inji-certify/api-test/pom.xml compile -DskipTests
mvn -B -s integration/maven-settings.xml -f /path/to/inji-verify/api-test/pom.xml compile -DskipTests
```

The installer adds `testscripts/OpenIDConformanceTest.java`, a component conformance suite, its entry in the existing master suite, and `ConformanceReporterMain`. The existing master's `EmailableReport` listener receives TestNG results/`TestCaseName`; the class does not create a second reporter or uploader. Both actual conformance classes were executed through that existing reporter/S3 lifecycle. Their full/error HTML files were downloaded from MinIO and compared byte-for-byte. The unrelated master functional tests were not run.

The integration provides `ConformanceReporterMain$PreservingReporter`, a subclass that calls the existing `EmailableReport` and restores the same original TestNG result objects afterward. The upstream error-only HTML generation clears passed results; without restoration, later TestNG XML loses genuine passes. The installer selects this subclass in the master listener and the component entrypoint uses it directly. No result status is changed. Full/error HTML still comes from the existing reporter. Report storage uses a run/validation namespace to avoid overwriting earlier fixed-name HTML objects.

`ConformanceReporterMain <suite.xml> <report-directory>` initializes the normal commons reporter with local environment and optional S3 settings, then invokes TestNG. Use the module's actual Maven dependency classpath plus `target/classes`. It reads S3_ENDPOINT/AWS_REGION/AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY/S3_BUCKET; it supplies no usable Slack endpoint. The upstream reporter logs an empty-URL notification error locally; no outgoing message is sent. The workflow builds and executes this entry point for each selected component even when the official gate fails, retaining the real existing-module reports.

Fresh runs require JVM properties `conformance.runnerRoot`, `env.endpoint`, optionally `conformance.python`, `conformance.oidfUrl`, and `conformance.insecure=true` only for local TLS. For Verify an origin receives `/v1/verify`; for Certify use the issuer identifier exactly as advertised. Set the issuer client/key/browser environment variables in SETUP.md.

External result consumption is explicit: `conformance.consumeReport=true`, `conformance.summary=/absolute/conformance-summary.json`, `conformance.runId=<actual matching run_id>`. Identity, age, schema and component presence are checked. REVIEW/TIMEOUT/ERROR fail, warnings retain their original status, skips remain skips, and a positive full gate is required. The standalone `testrig/` directory supplies independently validated Extent/S3 reporting for local combined runs.

Each component reporter evaluates its own conformance and regression gates. Combined execution preserves these independent decisions and fails its consolidated gate when either component fails. REVIEW outcomes fail the affected component and combined gates without failing a healthy component.
