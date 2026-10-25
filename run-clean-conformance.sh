#!/usr/bin/env bash
# Execute a fresh owned development stack, then clean only that deployment.
# Flags: --component certify|verify or --combined; forwards --parallel, --reports-dir
# and other main-wrapper options. Each execution requires a fresh source extraction.
# Prerequisites: cached pinned images, Docker Compose, Python dependencies, browser,
# Java 21/Maven and native API-rig configuration; isolated setup generates local keys.
# Exit: preserves the run failure; cleanup failure sets 2. Exit 0 requires both
# accepted reporting/gates and successful owned-resource cleanup.
#
# Fresh source extraction and cached pinned images; no historical keys or volumes.
set -euo pipefail
cd "$(dirname "$0")"
source_root="$(pwd -P)"
python_cmd="${PYTHON:-python3}"
project="${INJI_CLEAN_PROJECT:-inji-clean-$(date +%s)-$$}"
issuer_args=()
if [[ -n "${CERTIFY_NATIVE_IMAGE:-}" ]]; then issuer_args=(--issuer-image "$CERTIFY_NATIVE_IMAGE"); fi
cleanup() {
  local result=$?
  trap - EXIT
  cd "$source_root" || exit 2
  if [[ -f docker/isolated-state.json ]]; then
    "$python_cmd" runner/isolated_stack.py down --project "$project" "${issuer_args[@]}" || result=2
  fi
  exit "$result"
}
trap cleanup EXIT
"$python_cmd" runner/isolated_stack.py up --project "$project" "${issuer_args[@]}"
# Docker Desktop can refresh a Windows bind mount while Compose initializes it.
# Re-enter by absolute path instead of retaining a stale WSL directory handle.
cd "$source_root"
"$python_cmd" runner/init_local_storage.py
export CA_BUNDLE="$(pwd)/docker/nginx/certs/server.crt"
export CONFORMANCE_RESOLVE_LOCAL=true
export OIDF_URL=https://localhost:8443
export CERTIFY_ISSUER_URL=https://host.docker.internal:8446
export VERIFY_API_URL=https://localhost:8445/v1/verify
export VERIFY_UI_URL=https://host.docker.internal:8445/verify
# Only setup.py-generated, shell-safe development values are loaded.
while IFS='=' read -r name value; do
  case "$name" in AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY|AWS_REGION|S3_ENDPOINT|S3_BUCKET|ISSUER_LOGIN_USERNAME|ISSUER_LOGIN_PASSWORD)
    export "$name=$value" ;;
  esac
done < docker/.env
export VCI_CLIENT_ID=conformance-course-wallet
export VCI_CLIENT2_ID=conformance-course-wallet-2
export VCI_WALLET_JWKS_FILE=docker/local/wallet-keys/conformance-course-wallet.private.json
export VCI_WALLET2_JWKS_FILE=docker/local/wallet-keys/conformance-course-wallet-2.private.json
export VCI_AUTHORIZATION_SERVER=https://host.docker.internal:8446/auth/realms/course
export VCI_SCOPE=course_completion
export VCI_CREDENTIAL_CONFIGURATION_ID=course-completion-sdjwt
export VCI_CREDENTIAL_FORMAT=sd_jwt_vc
export VCI_CLIENT_AUTH_TYPE=private_key_jwt
export VCI_SENDER_CONSTRAIN=dpop
export ISSUER_BROWSER_STEPS_FILE=config/course-browser.json
"$python_cmd" runner/wait_ready.py --combined --insecure
"$python_cmd" runner/course_issuer.py --configure-only --insecure --resolve-local
bash run-conformance.sh --skip-docker --insecure "$@"
