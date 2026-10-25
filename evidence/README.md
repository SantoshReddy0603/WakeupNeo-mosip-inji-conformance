# Evidence handoff

The source baseline is main commit `7d80dc06e8d8745d01c8b82d6a08c8f3d32dc80b`,
merged through PR #8. Post-merge CI run `40178792370` passed all five jobs,
including 196 Python tests after setup. Hosted full-stack evidence remains
scratch run `40165722639` at `9c8d94ad9da42ac458ea304192118266577469f9`;
no new live conformance execution is claimed by this documentation update.

This repository contains this evidence index, not the reports or exports it lists.
The private handoff is not included in the repository. Listed report filenames
refer to that separate handoff; raw exports, private keys and generated configuration
are excluded from it. The original raw exports remain outside the handoff.

The source repository contains this index only. The retained private handoff folder is private evidence (not
included in the repository), which is not bundled with source. The table identifies filenames in that separate handoff. They are actual copied outputs, not newly executed tests. SHA256 receipts and
existence checks are in private `evidence-audit.json` (not included in the repository). Reviewer access is not
verified until this folder is handed over through a controlled channel.

hosted validation ran on scratch repository `SantoshReddy0603/inji-conformance-b2-scratch`, run `40165722639`,
commit `9c8d94ad9da42ac458ea304192118266577469f9`; it did not run on the original repository. All five
implementation criteria passed; strict conformance gates remain FAILED. hosted validation artifacts and logs
are retained locally, so access does not depend on the private repository's artifact retention.

The deployment and REST rows support the Compose and official runner deliverables; native/consolidated reports
support TestNG/Extent integration and combined execution; storage receipts support artifact handling; JDK and
regression outputs support compatibility and harness checks; hosted receipts support CI/CD.

| Verified claim | Retained proving files |
|---|---|
| Unified ten-service deployment, fresh owned volumes | `commands.json` (not included in the repository); `deployment-state.json` (not included in the repository) |
| Stock Certify: 2 PASSED, 10 INTERRUPTED, 3 SKIPPED; gate FAILED | `stock-results.json` (not included in the repository) |
| Patched issuer diagnostic: 12 PASSED, 3 SKIPPED; not stock qualification | `patched-results.json` (not included in the repository) |
| Stock combined: 6 PASS, 10 INTERRUPTED, 6 REVIEW, 3 SKIP; gate FAILED | `stock-results.json` (not included in the repository) |
| Patched combined: 16 PASS, 6 REVIEW, 3 SKIP; gate FAILED | `patched-results.json` (not included in the repository) |
| Latest local verifier: 4 PASSED, 6 REVIEW; gate FAILED | `results.json` (not included in the repository) |
| Both real module OpenIDConformanceTest integrations and consolidated Extent/TestNG reports | private evidence (not included in the repository); `testng-results.xml` (not included in the repository); `reporter-exit-statuses.json` (not included in the repository) |
| REVIEW remains failed TestNG assertion and rejects the gate | `testng-results.xml` (not included in the repository); `reporter-exit-statuses.json` (not included in the repository) |
| Latest local verifier: 65 storage artifacts verified; five owned volumes removed | `artifact-storage-validation.json` (not included in the repository); `deployment-state.json` (not included in the repository) |
| Java 11 fresh standalone bridge compilation and seven scenarios | `jdk11-checks.json` (not included in the repository); `jdk11-scenarios.log` (not included in the repository) |
| Upstream modules target 21; JDK 11 reports invalid target release: 21 | `jdk11-certify-real-metadata.log` (not included in the repository); `jdk11-verify-real-metadata.log` (not included in the repository) |
| Python harness contracts, including expected failures, diff and parallel execution | `python-tests.xml` (not included in the repository); `triage-tests.xml` (not included in the repository) |
| Historical hosted implementation CI on its own revision | `hosted-ci.json` (not included in the repository); `final-status.json` (not included in the repository) |
| Initial candidate hosted CI patch portability failure | `hosted-keymanager-failure.log` (not included in the repository); `patch-line-ending-reproduction.json` (not included in the repository) |
| Original patch bytes restored; actual native keymanager build passed | `build-provenance.json` (not included in the repository) |
| Runtime candidate hosted CI | `pr-ci-status.json` (not included in the repository) |
| Managed GitHub-hosted Linux execution in private scratch repository | `assessment.json` (not included in the repository) |
| Stable 1.0.x availability checked on 24 October 2026, none found in checked image repositories | `registry-version-inventory.json` (not included in the repository); `upstream-release-inventory.json` (not included in the repository) |
| Allowed variants, actual metadata and selected mTLS probe: 2 PASSED, 4 FAILED, 1 INTERRUPTED | See detail 1. |
| Scratch hosted attempt: authorization and ubuntu-24.04 selection | `run-state.json` (not included in the repository); `run-40164823727-logs.zip` (not included in the repository) |
| Approved workflow correction and one hosted validation retry | `final-workflow.diff` (not included in the repository); `assessment.json` (not included in the repository) |
| hosted validation: ten hosted services and both official plans execute | `run-state.json` (not included in the repository); `run-40165722639-logs.zip` (not included in the repository) |
| hosted validation: expected stock/verifier counts with strict FAILED gates | `ci-summary.json` (not included in the repository) |
| hosted validation: native/consolidated reports and storage receipts uploaded | `artifact-12587654719.zip` (not included in the repository); `artifact-12587788827.zip` (not included in the repository); `download-receipts.json` (not included in the repository) |
| hosted validation: storage read-back and cleanup | `assessment.json` (not included in the repository); `artifact-storage-validation.json` (not included in the repository) |
| repository integration merge of PR #7 after five green CI jobs | `merge-verification.json` (not included in the repository) |

## Exclusions and limits

Raw credential export ZIPs, private keys and .env files are excluded from this handoff folder and from the
source commit. Original private exports below were located and hashed; they were not modified or copied into
the handoff. Controlled raw-export inspection requires a separate authorized private handoff. This reconciles
the request to check those originals with the requirement to exclude raw credential exports.

| Private original outside this handoff | SHA256 |
|---|---|
| `plan-UYoPyoeGriNRN-export.zip` (not included in the repository) | `a2c82ba986207e97ad851dbd982af73276fb9509a74d30dfd1baee19f66363e6` |
| `plan-fnLpdorj2jZAD-export.zip` (not included in the repository) | `ef307ee6b3ae43aaa1399c6e3d0e21c05ee92e1b338e10e883107b5df4cd2b77` |
| `plan-yfOPDtRoNo2xZ-export.zip` (not included in the repository) | `8804b148233ab0f3f2047ba19b6c5ff0d9ec838ad3e92e9e5c53d23a964281d6` |
| `plan-Z4PgzIS2ImHJi-export.zip` (not included in the repository) | `f12edcb2de6d9546c3439f8e8788406bd2ac3e06197135c1b1fb2a0e127617c5` |
| `plan-IpxODLyKkxZNN-export.zip` (not included in the repository) | `898cfa5579865efdc0d48761753fbefe75e655596f2b944f053aaa4a5b9a3a39` |
| `plan-45vEXNrkMzWtm-export.zip` (not included in the repository) | `f4fb750388c3ec9ebd933c92a9ee1c71a074ff948cb050265ad4e6cb18f04dbd` |

No primary evidence file in the audited verified-claim mapping was missing after correcting the stale
triage-tests.xml path. Raw hosted validation official exports were not retained by the workflow and
remain not verified for offline inspection. independent empty-cache validation, organizer acceptance of
upstream Java 21, actual request URI POST and status-list interoperability remain not verified or external
pending. Standalone Java 11 execution is verified by the listed logs; acceptance of integrated Java 21 is
external pending. No official result, gate, default or protocol behavior was changed.

Two historical conformance-summary.json files contain embedded development private JWKs and are excluded from this handoff. Existing stock-results.json and patched-results.json receipts prove the combined outcomes instead; the originals remain unchanged outside this folder.

## Evidence table details

Detail 1: `a1-decision.json` (not included in the repository); `issuer-plan-available.json` (not included in
the repository); `issuer-metadata.json` (not included in the repository); `authorization-server-metadata.json`
(not included in the repository)
