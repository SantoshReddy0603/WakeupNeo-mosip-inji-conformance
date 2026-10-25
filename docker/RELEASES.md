# Validated upstream versions

These are the exact sources/images used in the local validation. Product conformance is not implied by an image version.

| Component | Release/source | Observed image digest |
|---|---|---|
| Certify with official bundled plugins | v1.0.0-alpha.1; source 8fdf71656979a72fa8263766d4dec3cc25127b76 | sha256:1579b2449f1a7213fe25de1f6a1509b5636f1fedf0d7f5c4cfd07b9f0fc5b346 |
| Verify | v1.0.0-alpha.1; source 4c4289026968beb535d3dbdd500947152c43f708 | sha256:064fcfa12773ec11834d5d769f2b6bb6bcc61cf9ae89ae918f8ae3934419907d |
| Keycloak | 26.4.0 | sha256:5f3fb534cde6bf006d79f5912473e5d2c828c707cdfc52e16972803aca9d43dd |
| OIDF suite | 11999aad62ec292f36101410d9d5b761d44903ff | Locally built from pinned GitLab source |
| MinIO | RELEASE.2025-09-07T16-13-09Z; source 01ce918d8279a20e4706b96a64396146894adee4 | Locally built from official pinned source |
| API-test commons | 085cfa94301738d901c5b70547dbf005cb762c2b | Maven source build |

Only `PostgresDataProviderPlugin` is selected/scanned for issuance. The official with-plugins image also bundles inactive integration JARs; no mock issuance/data-provider plugin is selected. Certify's built-in logger audit implementation is used.

Native blocker sources: [access-token filter](https://github.com/inji/inji-certify/blob/8fdf71656979a72fa8263766d4dec3cc25127b76/certify-service/src/main/java/io/mosip/certify/filter/AccessTokenValidationFilter.java), [custom JSON mapper](https://github.com/inji/inji-certify/blob/8fdf71656979a72fa8263766d4dec3cc25127b76/certify-service/src/main/java/io/mosip/certify/config/AppConfig.java), [credential request DTO](https://github.com/inji/inji-certify/blob/8fdf71656979a72fa8263766d4dec3cc25127b76/certify-core/src/main/java/io/mosip/certify/core/dto/CredentialRequest.java).

## Explicit native implementation

The tested `inji-harness/certify-positive:local` image ID is `sha256:5aa0ba5750b177b10348344708ae86b64a173ea3657b75272dab7014b943a2a6`. It is a local source build, not an upstream published image. Certify source remains `8fdf71656979a72fa8263766d4dec3cc25127b76`; five ordered patches in docker/native-certify implement request extensions, DPoP/replay, holder binding, signed metadata and selector errors. The real PostgreSQL provider is retained; inactive mock/MOSIP/Sunbird integration JARs are removed.

Native key-manager source is v1.4.0 commit `7c53fc9d3c972347a603fd66e9ab0812db60ccec`; docker/native-keymanager/positive-serial.patch fixes both X.509 certificate constructors. The actual rebuilt library replaces the same Spring Boot nested library with ZIP integrity/storage checks. 49 Certify and three key-manager tests passed through the delivered build entry point.

The actual Verify UI image digest is `sha256:e30b69ca51ab98cafd2ccf24f9c8c7da3c56cbb1b266d4e222f772a8fca82167`. Its browser/SDK transactions produced the genuine official evidence. No protocol proxy or stand-in UI was used.

## Unmodified stock baseline

The unified-stack stock run used exactly the unmodified Certify image ID listed in the table. It returned 2 PASS, 10 INTERRUPTED and 3 optional SKIP. Verify returned 4 PASS and 6 REVIEW. All gates failed, and native/consolidated reporters preserved those outcomes. README identifies the single reference run; raw official exports remain outside source.

Observed official interruption conditions include:
- Signed issuer metadata: missing expected application/jwt response and absent signed metadata body.
- Happy-flow and repeated/multiple-client issuance: resource endpoint HTTP status differed from the official requirement.
- Invalid nonce/proof and selector tests: actual invalid_token or unknown_error responses did not satisfy the expected credential error behavior.

These are observations under the selected private_key_jwt/DPoP profile. They do not establish that every untested product feature is defective. Native fixes remain separately identified: request extensions, DPoP/replay validation, holder binding, signed metadata, credential selector/errors and positive certificate serials. No stock result was replaced by a patched result.

## Available 1.0 versions

Official GitHub release/tag inventories and all published Docker Hub tags for Certify-with-plugins, Verify service and Verify UI were checked on 24 October 2026. Each image repository published 1.0.0-alpha.1 and no stable 1.0.x tag. Keep the alpha label. CERTIFY_VERSION, VERIFY_VERSION, VERIFY_UI_VERSION and VERIFY_SDK_VERSION are generated into docker/.env from docker/versions.env. The native patch source/artifact names remain deliberately pinned; changing a stock version requires a separate compatibility validation.
