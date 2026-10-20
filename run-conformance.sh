#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
mode=()
runner_args=()
skip_docker=false
runner_only=false
native_certify=false
native_dpop=false
native_binding=false
native_metadata=false
native_final=false
native_positive=false
component=''
existing_run=''
run_id=''
reports_dir="$(pwd)/reports"
max_report_age=7200
report_args=()
while (($#)); do
  case "$1" in
    --component|--existing-run|--run-id|--reports-dir|--max-report-age-seconds|--parallel|--poll-timeout|--diff|--expected-failures|--certify-url|--verify-url|--oidf-url|--certify-config|--verify-config|--endpoint)
      (($# >= 2)) && [[ "$2" != --* ]] || { echo "Missing value for $1"; exit 2; } ;;
  esac
  case "$1" in
    --component) ((${#mode[@]} == 0)) || { echo "Select exactly one mode"; exit 2; }; [[ "$2" == certify || "$2" == verify ]] || { echo "Invalid component"; exit 2; }; component="$2"; mode=(--component "$2"); shift 2 ;;
    --combined) ((${#mode[@]} == 0)) || { echo "Select exactly one mode"; exit 2; }; mode=(--combined); shift ;;
    --skip-docker) skip_docker=true; shift ;;
    --runner-only) runner_only=true; shift ;;
    --native-certify) native_certify=true; shift ;;
    --native-dpop) native_certify=true; native_dpop=true; shift ;;
    --native-binding) native_certify=true; native_dpop=true; native_binding=true; shift ;;
    --native-metadata) native_certify=true; native_dpop=true; native_binding=true; native_metadata=true; shift ;;
    --native-final) native_certify=true; native_dpop=true; native_binding=true; native_metadata=true; native_final=true; shift ;;
    --native-positive) native_certify=true; native_dpop=true; native_binding=true; native_metadata=true; native_final=true; native_positive=true; shift ;;
    --insecure) runner_args+=(--insecure); shift ;;
    --existing-run) existing_run="$2"; shift 2 ;;
    --run-id) run_id="$2"; shift 2 ;;
    --reports-dir) reports_dir="$2"; shift 2 ;;
    --max-report-age-seconds) max_report_age="$2"; shift 2 ;;
    --parallel|--poll-timeout|--diff|--expected-failures|--certify-url|--verify-url|--oidf-url|--certify-config|--verify-config)
      runner_args+=("$1" "$2"); shift 2 ;;
    --endpoint)
      [[ "$component" == certify || "$component" == verify ]] || { echo '--endpoint requires --component first'; exit 2; }
      runner_args+=("--${component}-url" "$2"); shift 2 ;;
    --help) echo 'Use --component certify|verify or --combined; --skip-docker targets an existing deployment; --runner-only omits Java reporting. --existing-run DIR --run-id ID --reports-dir EMPTY_DIR validates retained official results without creating plans. --max-report-age-seconds N explicitly bounds historical report age.'; exit 0 ;;
    *) echo "Unknown option: $1"; exit 2 ;;
  esac
done
((${#mode[@]})) || { echo 'Select --component certify|verify or --combined'; exit 2; }
if [[ -n "$existing_run" ]]; then
  [[ -n "$run_id" && "$reports_dir" != "$(pwd)/reports" ]] || { echo 'Retained validation requires --run-id and a separate --reports-dir'; exit 2; }
fi
python_cmd="${PYTHON:-python3}"
command -v "$python_cmd" >/dev/null
if ! $runner_only; then command -v mvn >/dev/null; fi
if ! $skip_docker; then
  "$python_cmd" runner/setup.py
  "$python_cmd" runner/preflight.py
  docker compose --env-file docker/.env -f docker/docker-compose.yml up -d --build
  if [[ "$component" != certify ]]; then
    docker compose --env-file docker/.env -f docker/verify-final.compose.yml up -d
    export VERIFY_UI_URL="${VERIFY_UI_URL:-https://host.docker.internal:8445/verify}"
  fi
  if [[ "$component" != verify ]]; then
    issuer_compose=(-f docker/certify-final.compose.yml)
    if $native_certify; then
      native_args=()
      export CERTIFY_NATIVE_IMAGE=inji-harness/certify-native:local
      if $native_dpop; then
        native_args+=(--dpop)
        export CERTIFY_NATIVE_IMAGE=inji-harness/certify-dpop:local
      fi
      if $native_binding; then
        native_args+=(--holder-binding)
        export CERTIFY_NATIVE_IMAGE=inji-harness/certify-binding:local
      fi
      if $native_metadata; then
        native_args+=(--signed-metadata)
        export CERTIFY_NATIVE_IMAGE=inji-harness/certify-metadata:local
      fi
      if $native_final; then
        native_args+=(--credential-errors)
        export CERTIFY_NATIVE_IMAGE=inji-harness/certify-final:local
      fi
      if $native_positive; then
        native_args+=(--positive-serial)
        export CERTIFY_NATIVE_IMAGE=inji-harness/certify-positive:local
      fi
      "$python_cmd" runner/build_native_certify.py "${native_args[@]}"
      issuer_compose+=(-f docker/certify-native.compose.yml)
    fi
    docker compose --env-file docker/.env "${issuer_compose[@]}" up -d
    if $native_dpop; then
      docker compose --env-file docker/.env "${issuer_compose[@]}" exec -T course-database \
        psql -v ON_ERROR_STOP=1 -U postgres -d inji_certify -f /docker-entrypoint-initdb.d/03-dpop-replay.sql
    fi
  fi
  "$python_cmd" runner/wait_ready.py "${mode[@]}" "${runner_args[@]}"
  docker compose --env-file docker/.env -f docker/storage.compose.yml up -d --build
  if [[ "$component" != verify ]]; then
    issuer_args=()
    [[ " ${runner_args[*]} " != *' --insecure '* ]] || issuer_args+=(--insecure)
    "$python_cmd" runner/course_issuer.py --configure-only "${issuer_args[@]}"
    if $native_positive; then
      "$python_cmd" runner/rotate_development_keys.py "${issuer_args[@]}"
    fi
  fi
  # Load generated local storage settings only when the caller has not supplied them.
  while IFS='=' read -r name value; do
    case "$name" in AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY|AWS_REGION|S3_ENDPOINT|S3_BUCKET|ISSUER_LOGIN_USERNAME|ISSUER_LOGIN_PASSWORD)
      [[ -n "${!name:-}" ]] || export "$name=$value" ;;
    esac
  done < docker/.env
  if [[ "$component" != verify ]]; then
    export VCI_CLIENT_ID="${VCI_CLIENT_ID:-conformance-course-wallet}"
    export VCI_CLIENT2_ID="${VCI_CLIENT2_ID:-conformance-course-wallet-2}"
    export VCI_WALLET_JWKS_FILE="${VCI_WALLET_JWKS_FILE:-docker/local/wallet-keys/conformance-course-wallet.private.json}"
    export VCI_WALLET2_JWKS_FILE="${VCI_WALLET2_JWKS_FILE:-docker/local/wallet-keys/conformance-course-wallet-2.private.json}"
    export VCI_AUTHORIZATION_SERVER="${VCI_AUTHORIZATION_SERVER:-https://host.docker.internal:8446/auth/realms/course}"
    export VCI_SCOPE="${VCI_SCOPE:-course_completion}"
    export VCI_CREDENTIAL_CONFIGURATION_ID="${VCI_CREDENTIAL_CONFIGURATION_ID:-course-completion-sdjwt}"
    export VCI_CREDENTIAL_FORMAT="${VCI_CREDENTIAL_FORMAT:-sd_jwt_vc}"
    export VCI_CLIENT_AUTH_TYPE="${VCI_CLIENT_AUTH_TYPE:-private_key_jwt}"
    export VCI_SENDER_CONSTRAIN="${VCI_SENDER_CONSTRAIN:-dpop}"
    export ISSUER_BROWSER_STEPS_FILE="${ISSUER_BROWSER_STEPS_FILE:-config/course-browser.json}"
  fi
fi
runner_code=0
if $skip_docker && [[ -z "$existing_run" ]]; then
  "$python_cmd" runner/wait_ready.py "${mode[@]}" "${runner_args[@]}"
fi
if [[ -n "$existing_run" ]]; then
  retained_args=()
  for ((i=0; i<${#runner_args[@]}; i++)); do
    case "${runner_args[i]}" in
      --insecure) retained_args+=(--insecure) ;;
      --oidf-url|--diff) retained_args+=("${runner_args[i]}" "${runner_args[i+1]}"); ((i+=1)) ;;
      --certify-config|--verify-config|--expected-failures) echo "${runner_args[i]} cannot change a retained official run"; exit 2 ;;
    esac
  done
  "$python_cmd" runner/retained_run.py "${mode[@]}" --existing-run "$existing_run" --run-id "$run_id" --reports-dir "$reports_dir" "${retained_args[@]}" || runner_code=$?
  report_args+=(--historical)
else
  "$python_cmd" runner/runner.py "${mode[@]}" --reports-dir "$reports_dir" "${runner_args[@]}" || runner_code=$?
fi
((runner_code <= 1)) || exit "$runner_code"
bridge_code=0
if ! $runner_only; then
  for ((i=0; i<${#runner_args[@]}; i++)); do
    case "${runner_args[i]}" in
      --certify-url|--verify-url) report_args+=("${runner_args[i]}" "${runner_args[i+1]}"); ((i+=1)) ;;
    esac
  done
  "$python_cmd" runner/report_lifecycle.py "${mode[@]}" --reports-dir "$reports_dir" --max-report-age-seconds "$max_report_age" "${report_args[@]}" || bridge_code=$?
fi
((runner_code == 0)) || exit "$runner_code"
exit "$bridge_code"



