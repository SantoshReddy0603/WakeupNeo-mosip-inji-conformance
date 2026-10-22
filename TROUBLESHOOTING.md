# Troubleshooting

| Symptom | Required check or action |
|---|---|
| Docker is unavailable or services are not ready | Start Docker Desktop, validate the relevant manifests and inspect `docker compose ... ps` and service logs. `runner/wait_ready.py` fails on unavailable or unhealthy real endpoints. |
| Port 8443/8445/8446 or 9000 is occupied | Identify the existing service before changing deployment settings. Reuse the configured deployment with `--skip-docker`; preserve its volumes and reports. |
| TLS verification fails | Use CA_BUNDLE for a trusted CA. `--insecure` is an explicit option for the supplied local development certificate. |
| `host.docker.internal` does not resolve inside WSL | Set CONFORMANCE_RESOLVE_LOCAL=true; only process-local transport resolution changes. Protocol identifiers and TLS hostnames remain unchanged. |
| Stock issuer rejects extension fields, DPoP or signed metadata | Use the documented `--native-positive` build containing the actual native patches. Configuration alone does not implement missing protocol support. |
| Unknown client or authorization/login failure | Check generated Keycloak client registration, actual public JWKS route, configured issuer/AS endpoints and the development user. Re-import an existing realm only using the supported offline procedure in SETUP.md. |
| Missing Maven, Java or Python dependency | Install runner requirements in an isolated Python environment. Native builds and the pinned module/commons runtime require Java 21; the supplied bridge classes target Java 11. `--runner-only` deliberately omits Java reporting and does not validate it. |
| Fresh commons build cannot resolve dependencies offline | Use normal online Maven resolution on the first build. MAVEN_OFFLINE=true requires every declared dependency already present; a prepared reporter classpath does not imply a complete fresh-build cache. |
| Unexpected repository revision | Use the exact pinned checkout or an empty bootstrap directory. The reporting lifecycle rejects a different HEAD rather than silently accepting unrelated source. |
| Stale report or mismatched run ID | Supply the exact original run ID. Retained validation needs a separate empty output directory and an explicit historical age bound. Never refresh original evidence timestamps to satisfy a fresh-release check. |
| Expected-failure file is rejected | Each entry needs a test_name, nonblank reason and issue reference, a valid unexpired ISO date, and statuses exactly `["FAILED"]`. Duplicate names, unknown components and operational-result waivers are rejected. |
| Verify/combined exits 1 with six REVIEW results | This is the correct current gate outcome. Inspect the real evidence and applicable review requirements in REVIEW_PROCESS.md; screenshots are not review approval. |
| Diff gate fails | Inspect conformance-diff.json for degraded or removed passing tests. Repair the actual implementation; do not edit the baseline or results. |
| MinIO read-back differs or upload fails | Check the configured endpoint, bucket, access policy and artifact-storage-validation.json. A differing byte hash is a failed validation, not a successful upload. |

Execution logs and validation evidence are retained separately from the source distribution. Runtime reports and official exports can contain sensitive development configuration; keep them separate from source distribution.


Clean deployment behavior: the managed wrappers now run runner/init_local_storage.py after MinIO starts. A fresh storage-data volume has no automationtests bucket; read-only preflight correctly rejects it until initialized. The initializer creates a missing bucket only on loopback port 9000, preserves an existing bucket and propagates access-denied errors. External storage is never automatically provisioned. The isolated wrapper also re-enters its absolute source directory after Docker Desktop mount initialization to avoid retaining a stale WSL directory handle. Both original failed attempts remain in the validation evidence. Cleanup validates Compose project and volume labels before deleting this run's five volumes.
