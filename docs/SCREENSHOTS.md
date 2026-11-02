# Recorded report screenshots

Run: `019bf015dcef47029010faa06a2cf788`. These screenshots show the retained stock
reports, rendered from their original HTML at a 1920 x 1080 browser viewport.
The combined report uses its existing dashboard tab; module reports use their
existing TestNG index pages. No result, HTML source or screenshot pixels were edited.

The original HTML bytes were hashed before and after capture and stayed unchanged.
Source paths below are relative to that run's retained report directory. They are
not additional report files bundled in this repository.

| Report | Source page | Screenshot |
|---|---|---|
| Combined | `extent-report.html` | [PNG](images/recorded-combined-report.png) |
| Certify | `existing-certify/019bf015dcef47029010faa06a2cf788/index.html` | [PNG](images/recorded-certify-report.png) |
| Verify | `existing-verify/019bf015dcef47029010faa06a2cf788/index.html` | [PNG](images/recorded-verify-report.png) |

## Integrity hashes

| Report | Original HTML SHA-256 | Screenshot SHA-256 |
|---|---|---|
| Combined | `64536340b3638d817b2a355ba3b3260e0e6d5df1e24f160eadcf50f02ede2f13` | `995ca676748b948cdf3c1b46aea9f384c4ec5c3bb765fc09c4ab9a687555cc7d` |
| Certify | `5dd9117486325b0436da0f7bb35cb0c440eaefd2c4e2bce93b08f5f0c15b1cdf` | `4c0db910e9b092ab214d733e99f6c371febbc2fb3a445b4cecca639e148ed9b0` |
| Verify | `487fa02fe1f67e806058ce967483901e7c7fed2c472dadc01bf2736a6599e929` | `4e9997f009ab23defb7ea52a429602886276f67b3cd993cdf8438ff7eef5b78e` |

These are report screenshots, not fresh suite, MinIO-console or GitHub Actions
screenshots. No new official conformance execution was performed for these images.
Original module outcomes and failed gates remain unchanged.
