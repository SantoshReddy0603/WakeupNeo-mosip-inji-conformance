> Stage 17: 117 harness tests passed; fresh parallel official execution and retained three-mode reporting verified. Verify remains 4 PASS/6 REVIEW, combined gate FAILED. See RESULTS.md and REVIEW_FINDINGS.md for evidence and limits; earlier stage notes below are historical.

> Stage 16 update (20 October 2026): 106 harness tests passed; 10 focused repetitions passed (220 checks); clean native tests reproduced (49 Certify, 3 key-manager). Fresh Certify-only, Verify-only, serial combined and parallel combined official plans were executed, with real TestNG/Extent/S3 reporting. Results remain 12 PASS/3 SKIP for Certify and 4 PASS/6 REVIEW for Verify. See [RESULTS.md](RESULTS.md) for current IDs, evidence and limits. Statements about earlier stages below are historical.

# Local implementation checklist

The verifier target remains `oid4vp-1final-verifier-test-plan`. Preserved historical official reference run: `141a3630f7874e98ae4964653f953899` in `outputs/live-combined-positive-final`. Certify returned **12 PASS, 3 SKIP**; Verify returned **4 PASS, 6 REVIEW**. The combined gate is **FAILED**. Unit/security smoke tests are separate from official evidence.

## 1. Already configured and verified

- Docker Compose runs the pinned official suite/MongoDB, isolated Certify/PostgreSQL, Verify and its actual UI, Keycloak and MinIO. The original Downloads deployment/data was preserved.
- Keycloak 26.4.0 has DPoP enabled, a generated synthetic learner, required claims/audience/scope, a public smoke wallet and two registered private_key_jwt conformance clients with real public JWKS. No external account is needed.
- Real PostgresDataProviderPlugin reads synthetic course-completion records using the validated subject and scope; the supported SD-JWT credential/template uses `urn:inji:development:course-completion:1`.
- Native pinned Certify fixes implement request extensions, signature-validated DPoP with persistent atomic replay rejection, holder cnf.jwk, genuinely signed issuer metadata and exact credential selector/error behavior. 49 selected native tests passed; actual issuance and nine security/five selector rejection checks passed.
- Native key-manager 1.4.0 generates positive bounded X.509 serials. Three native tests passed, including 10,000 generated serials and both certificate-generation paths. Actual development signing keys were rotated with backups; credential and signed-metadata cryptography passed, and a second rotation was a no-op. Historical keys remain retained after successful rotation.
- Six genuine Verify UI transaction images were uploaded to the official suite and verified byte-for-byte with actual transaction IDs and SDK status checks enabled. All six remain REVIEW.
- Official exports, strict gates, component/combined reports, badges, selective runs, parallel independent plans, regression comparison and expiring expected-failure rules are implemented. No shipped exception waives a failure.
- mosip-functional-tests commons and the real moved api-test modules are checked out at pinned commits. Both existing reporter integrations were compiled/executed. Latest issuer-only reporter: 13 passes, zero failures and three skips, including its passing gate. Verify reporter: four passes and seven failures, including its failed gate. Their actual HTML uploads were read back byte-for-byte; the combined bridge produced 26 tests (16 passes, seven failures, three skips).
- MinIO and generated local credentials are configured; real artifacts are uploaded and read back byte-for-byte.
- GitHub Actions includes harness tests, both existing-module compile jobs, 49 native Certify tests, three native key-manager tests and live release/manual gates with failed-run artifacts. Actionlint and Bash/PowerShell syntax passed locally. Stage 14 passed 84 harness tests. See REQUIREMENTS_STATUS.md for the complete current PDF checklist and verification limits.

## 2. Missing configuration the agent can implement automatically

- No missing prerequisite remains for the verified local conformance stack. Setup regenerates local keys, account/client registrations, synthetic records and storage settings after extraction.
- Broader unrelated API functional suites can be run when their separate deployment/test-data prerequisites are available. Their complete master-suite results are not claimed by the conformance integration checks.

## 3. Actions genuinely requiring user input or credentials

- No external issuer registry, personal records, login or secret is required for local implementation.
- Six official REVIEW results require the applicable reviewer process because screenshot submission alone cannot produce PASS. Review the preserved official plans/evidence and use the official review/certification process; the agent will not approve its own evidence or rewrite outcomes.
- GitHub execution is deferred at your request. When ready, supply the repository URL and register a reachable self-hosted runner labelled `inji-conformance`; configure the endpoint/profile/file variables and GitHub secret references listed in SETUP.md. Credentials stay in the runner/secret store, not chat. No remote repository has been created.

## 4. Compatibility blockers that configuration alone cannot solve

- The stock Certify alpha image lacks the required native request-extension, DPoP, holder-binding, signed-metadata and selector/error behavior. These are resolved in the explicitly patched native build, rather than attributed to the stock image. Use `--native-positive` / `-NativePositive` for all verified fixes, including key-manager serial generation.
- Six verifier modules remain official REVIEW despite authentic evidence. The automated combined release gate remains failed until the official process supplies acceptable results; no configuration flag converts REVIEW to PASS.
- Three issuer modules are actual optional SKIPs (batch issuance, key attestation and response encryption), absent advertisement. They remain SKIP and are not implementation passes. Supporting those features would require native product work and a separately scoped credential/security profile.
- Course issuance and the official verifier's PID fixture (`urn:eudi:pid:1`) are independent plans. A combined run does not prove course-to-PID interoperability; credentials are not relabelled or translated.
- The pinned general suite plans are labelled alpha and do not themselves grant formal certification.

## PDF task coverage

| Category | Task | Implementation / validation |
|---|---|---|
| Mandatory | Compose stack | Real local services started; separate Compose files orchestrated by one entry point |
| Mandatory | Programmatic issuer/verifier plans | Implemented; official live runs and exports collected; issuer gate passes; verifier/combined gates fail on REVIEW |
| Mandatory | Per-module existing api-testrig bridge | Installed and compiled in both actual modules; both suites executed through the actual existing reporter and S3 lifecycle; real HTML bytes verified |
| Mandatory | Combined consolidated run | Implemented and executed against both real services |
| Mandatory | One-command execution | Bash/PowerShell wrappers implemented; dependency/runtime/profile failures propagate |
| Good-to-have | GitHub Actions | File and local checks prepared; remote execution deferred |
| Good-to-have | Selective component/plan | Certify, Verify and combined modes supported; custom plan config paths supported |
| Good-to-have | Expected failures | Explicit, reason/issue/expiry-backed; defaults empty; incomplete results cannot be waived |
| Good-to-have | Result diff | Regression and removed-test gates implemented and tested |
| Good-to-have | Documentation | Local setup, integration and this checklist supplied |
| Bonus | Parallel execution | Independent component plans run concurrently; shared-alias modules remain serial |
| Additional | Real dev issuer + crypto smoke | Implemented and passed; separate from official results |
| Additional | MinIO read-back verification | Real files downloaded and compared byte-for-byte |

The harness is implemented; verifier review, formal certification and complete unrelated master-suite validation remain outstanding. See the delivered `RESULTS.md` for exact current live counts and artifact locations.

