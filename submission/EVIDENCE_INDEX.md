# Evidence index

The source baseline is main commit `7d80dc06e8d8745d01c8b82d6a08c8f3d32dc80b`,
merged through PR #8. Post-merge CI run `40178792370` passed all five jobs,
including 196 Python tests after setup. Hosted full-stack evidence remains
scratch run `40165722639` at `9c8d94ad9da42ac458ea304192118266577469f9`;
no new live conformance execution is claimed by this documentation update.

Report, export and log filenames in this document identify private evidence, not files
bundled in the repository. The repository includes only the evidence mapping in
[evidence/README.md](../evidence/README.md). Raw exports, private keys and generated configuration
are excluded. Missing hosted raw-export bytes remain not verified.

This is a draft submission aid, not a certification claim. `EVIDENCE_ROOT` means the existing private
`outputs/` directory associated with this project. Paths below beginning private evidence (not included in the
repository), private evidence (not included in the repository), private evidence (not included in the
repository) or private evidence (not included in the repository) are relative to that directory; source paths
are relative to the project root. Raw exports contain sensitive runtime material and are not included in this
source-only folder. Reviewer access to that private evidence is **not verified**; grant controlled access
before submission. Original run `141a3630f7874e98ae4964653f953899` remains preserved; the comparisons below
identify separate runs.

| Claim | Run ID / check | Proving file or command output | Status |
|---|---|---|---|
| Unified ten-service deployment, fresh owned volumes | 019bf015dcef47029010faa06a2cf788 | `commands.json` (not included in the repository); deployment-state.json | verified |
| Stock Certify: 2 PASSED, 10 INTERRUPTED, 3 SKIPPED; gate FAILED | 019bf015dcef47029010faa06a2cf788 | `plan-UYoPyoeGriNRN-export.zip` (not included in the repository); stock-results.json | verified |
| Patched issuer diagnostic: 12 PASSED, 3 SKIPPED; not stock qualification | d39d9f65b0f04db79eb3d25501c9f26c | `plan-yfOPDtRoNo2xZ-export.zip` (not included in the repository); patched-results.json | verified |
| Stock combined: 6 PASS, 10 INTERRUPTED, 6 REVIEW, 3 SKIP; gate FAILED | 019bf015dcef47029010faa06a2cf788 | `conformance-summary.json` (not included in the repository) | verified |
| Patched combined: 16 PASS, 6 REVIEW, 3 SKIP; gate FAILED | d39d9f65b0f04db79eb3d25501c9f26c | `conformance-summary.json` (not included in the repository) | verified |
| Latest local verifier: 4 PASSED, 6 REVIEW; gate FAILED | 0d9b58120a964f628a34dd0c658d6c8f | `results.json` (not included in the repository); reports/plan-IpxODLyKkxZNN-export.zip | verified |
| Both real module OpenIDConformanceTest integrations and consolidated Extent/TestNG reports | 019bf015dcef47029010faa06a2cf788 | private evidence (not included in the repository); existing-verify; extent-report.html; testng-results.xml; reporter-exit-statuses.json | verified |
| REVIEW remains failed TestNG assertion and rejects the gate | 0d9b58120a964f628a34dd0c658d6c8f | `testng-results.xml` (not included in the repository); reporter-exit-statuses.json | verified |
| Latest local verifier: 65 storage artifacts verified; five owned volumes removed | 0d9b58120a964f628a34dd0c658d6c8f | `artifact-storage-validation.json` (not included in the repository); deployment-state.json | verified |
| Java 11 fresh standalone bridge compilation and seven scenarios | JDK 11 local check | `jdk11-checks.json` (not included in the repository); jdk11-scenarios.log | verified |
| Upstream modules target 21; JDK 11 reports invalid target release: 21 | Pinned upstream sources, not a conformance run | `jdk11-certify-real-metadata.log` (not included in the repository); jdk11-verify-real-metadata.log; docs/VALIDATION.md cites upstream POM lines | verified |
| Organizer acceptance of integrated JDK 21 | No response obtained | docs/VALIDATION.md organizer question; not sent | external pending |
| Python harness contracts, including expected failures, diff and parallel execution | Local regression | `python-tests.xml` (not included in the repository); earlier `triage-tests.xml` (not included in the repository) has 196 passes | verified |
| Historical hosted implementation CI on its own revision | 39772274219; head 2594b3d6f9590caa9d28c6fa2048249ac300f274 | `hosted-ci.json` (not included in the repository); final-status.json | verified |
| Initial candidate hosted CI patch portability failure | 40163129216; head 6f1e31b5ffe60740ab9db6bc1ffa5463708e0c0f | `hosted-keymanager-failure.log` (not included in the repository); patch-line-ending-reproduction.json | verified |
| Original patch bytes restored; actual native keymanager build passed | Pinned 7c53fc9d3c972347a603fd66e9ab0812db60ccec | `build-provenance.json` (not included in the repository) exit_status=0 and test-results | verified |
| Runtime candidate hosted CI | 40165694278; head 9c8d94ad9da42ac458ea304192118266577469f9 | `pr-ci-status.json` (not included in the repository); final documentation head requires its own CI | verified |
| Managed GitHub-hosted Linux execution in private scratch repository | 40165722639; head 9c8d94ad9da42ac458ea304192118266577469f9 | See detail 1. | verified |
| Request URI POST interoperability | 0d9b58120a964f628a34dd0c658d6c8f | `verifier-coverage.json` (not included in the repository): E1FPVnumrtRlZHU bypasses POST conditions; REVIEW screenshot branch | not verified |
| Status-list interoperability | 0d9b58120a964f628a34dd0c658d6c8f | `verifier-coverage.json` (not included in the repository): oTZgMqIEscOyRW9 has no status reference and statusCheck=[] | not verified |
| Stable 1.0.x availability checked on 24 October 2026, none found in checked image repositories | Dated inventory, not refreshed | `registry-version-inventory.json` (not included in the repository); upstream-release-inventory.json | verified |
| Empty-cache independent installation | No run | docs/VALIDATION.md prepared commands; no destructive cleanup executed | not verified |
| Official review disposition or certification | No approval obtained | REVIEW_PROCESS.md; six official REVIEW outcomes retained | external pending |
| This proposed 5–7 minute video | Not recorded | submission/DEMO_SCRIPT.md is a draft shot list | not verified |

| Allowed variants, actual metadata and selected mTLS probe: 2 PASSED, 4 FAILED, 1 INTERRUPTED | Official partial plan 45vEXNrkMzWtm | See detail 2. | verified |
| Certificate-bound mTLS end-to-end qualification | Same partial plan | Observed token_type=Bearer, missing token cnf; no complete plan qualification | not verified |

| Scratch hosted attempt: authorization and ubuntu-24.04 selection | 40164823727; ce7a50e81cdea4081fa1061573e24c8d76094d68 | `run-state.json` (not included in the repository); run-40164823727-logs.zip | verified |
| Initial hosted validation attempt before approved correction | 40164823727 | WORKFLOW_BUG: empty AWS variables override generated .env; image preparation exit 1 before stack startup; zero official plans and zero uploaded artifacts | not verified |
| Approved workflow correction and one hosted validation retry | 40165722639; 9c8d94ad9da42ac458ea304192118266577469f9 | See detail 3. | verified |

| hosted validation: ten hosted services and both official plans execute | 40165722639; official run 2583bed425d64f5abb0c86993d402116 | `run-state.json` (not included in the repository); original execution log; issuer vir0sD8It1IDI and verifier UZtgjxUuLpdPj | verified |
| hosted validation: expected stock/verifier counts with strict FAILED gates | Same run | artifact-12587654719/ci-summary.json: 2 PASS / 10 INTERRUPTED / 3 SKIP; 4 PASS / 6 REVIEW; no exceptions | verified |
| hosted validation: native/consolidated reports and storage receipts uploaded | Same run | managed-reporting-evidence artifact 12587788827; live-conformance-results artifact 12587654719; download-receipts.json and assessment.json | verified |
| hosted validation: storage read-back and cleanup | Same run | 114 verified storage objects; 23 downloaded report files match storage hashes; original cleanup log removes five volumes, zero remain; final state reflects second idempotent cleanup | verified |
| Hosted raw official export offline reinspection | Same run | Export ZIP objects were uploaded/verified in ephemeral MinIO, but their raw bytes were not retained in GitHub artifacts | not verified |
| repository integration merge of PR #7 | fd89d1f4d8e960e5ad3f0fdb7b2fb975f70d41be; head 8ef076aa3eec784dee8c32a97cd9a9bd5eb01355 | `merge-verification.json` (not included in the repository); CI 40177192785, all five jobs passed | verified |
| Further scratch rerun/deletion | No action | One retry used; scratch retained; fresh approval required | external pending |

## Retained hosted validation evidence for repository integration

hosted validation is verified only for private scratch repository
`SantoshReddy0603/inji-conformance-b2-scratch`, run `40165722639`, commit
`9c8d94ad9da42ac458ea304192118266577469f9`; it was not a main-repository run. The previously downloaded logs
and both artifacts were copied into private private evidence (not included in the repository) and rechecked
against their download SHA256 receipts and ZIP CRCs. `manifest.json` records their hashes and source run;
`assessment.json` records the five verified hosted validation implementation criteria. This evidence folder is
separate from the source repository and must accompany a controlled evidence handoff.

| Retained file | Evidence |
|---|---|
| `run-40165722639-logs.zip` (not included in the repository) | Complete hosted workflow logs |
| `artifact-12587654719.zip` (not included in the repository) | live-conformance-results: summary and report |
| `artifact-12587788827.zip` (not included in the repository) | managed-reporting-evidence: native/consolidated reports, storage and cleanup receipts |

The strict conformance gates remain FAILED; raw hosted official export ZIP bytes were not retained in these
artifacts. Repository integration requires successful CI on the selected revision; independent empty-cache validation, further live runs and scratch
deletion remain unperformed.

## Evidence package audit

The private handoff folder is private evidence (not included in the repository). Its copied files retain their
original relative paths. Every one of the 25 verified claims audited before this update has at least one
existing retained evidence file; the repository integration merge receipt is also retained. See
[evidence/README.md](../evidence/README.md) for the complete claim-to-file mapping and exclusions. The
original index pointed to `triage-tests.xml` (not included in the repository), which does not exist; the
correct retained file is `triage-tests.xml` (not included in the repository). No other required primary
evidence file was missing in this audit. Raw stock, patched, verifier and mTLS export ZIPs exist only at the
original private evidence paths and are intentionally excluded from the clean handoff. Hosted Hosted
validation raw export bytes remain unavailable: offline reinspection is not verified.

## hosted validation coverage of the final code

Scratch repository `SantoshReddy0603/inji-conformance-b2-scratch`, run `40165722639`, tested commit
`9c8d94ad9da42ac458ea304192118266577469f9`. Final PR #7 head `8ef076aa3eec784dee8c32a97cd9a9bd5eb01355`
differs only in the documentation files listed below: all are DOCS_ONLY, with no runtime or workflow changes.
Command: `git diff 9c8d94ad9da42ac458ea304192118266577469f9..8ef076aa3eec784dee8c32a97cd9a9bd5eb01355 --stat`;
output: 8 files changed, 94 insertions(+), 15 deletions(-).

- `CI_CD_SETUP.md`
- `README.md`
- `REQUIREMENTS_STATUS.md`
- `SETUP.md`
- `docs/VALIDATION.md`
- `submission/DEMO_SCRIPT.md`
- `submission/EVIDENCE_INDEX.md`
- `submission/LIMITATIONS.md`

Original repository main was confirmed at PR #7 merge commit `fd89d1f4d8e960e5ad3f0fdb7b2fb975f70d41be`. All
five pre-merge CI jobs passed on the exact final head in run `40177192785`. The project ZIP SHA256
`5182d5ad87cc0e46e96cdd7b0604294ec3c13f4ebab814ba69add528d7b14091` differs from main only in
docs/VALIDATION.md, REQUIREMENTS_STATUS.md and submission/EVIDENCE_INDEX.md; the ZIP copies predate the newer
retained-evidence records on main and were not used to overwrite them. This follow-up changes documentation
only and does not constitute another live hosted validation run. Source comparison output: private
`source-comparison.json` (not included in the repository).

The clean handoff also excludes historical stock/patched conformance-summary.json files because they embed
development private JWKs. Unmodified stock-results.json and patched-results.json receipts are retained
instead; original summaries remain private and unchanged. No private key or raw export is staged.

## Evidence table details

Detail 1: `assessment.json` (not included in the repository); downloaded report artifacts, storage receipt and
log ZIP; strict gate remains FAILED

Detail 2: `a1-decision.json` (not included in the repository); `issuer-plan-available.json` (not included in
the repository), issuer-metadata.json, authorization-server-metadata.json and
mtls-reports/plan-45vEXNrkMzWtm-export.zip

Detail 3: `final-workflow.diff` (not included in the repository) and assessment.json; original single-step
unset proposal superseded by job-level removal and external-only loader
