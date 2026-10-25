[CmdletBinding()]
param(
    [ValidateSet('certify','verify')][string]$Component,
    [switch]$Combined,
    [int]$Parallel = 1,
    [int]$PollTimeout = 300,
    [string]$Diff = '',
    [string]$CertifyConfig = '',
    [string]$VerifyConfig = '',
    [string]$ExpectedFailures = '',
    [switch]$SkipDocker,
    [switch]$RunnerOnly,
    [switch]$NativeCertify,
    [switch]$NativeDpop,
    [switch]$NativeBinding,
    [switch]$NativeMetadata,
    [switch]$NativeFinal,
    [switch]$NativePositive,
    [switch]$Insecure,
    [string]$Endpoint = '',
    [string]$CertifyUrl = '',
    [string]$VerifyUrl = '',
    [string]$OidfUrl = '',
    [string]$ExistingRun = '',
    [string]$RunId = '',
    [string]$ReportsDir = '',
    [int]$MaxReportAgeSeconds = 7200,
    [string]$Python = 'python',
    [string]$Maven = 'mvn'
)
$ErrorActionPreference = 'Stop'
if ($NativePositive) { $NativeFinal = $true }
if ($NativeFinal) { $NativeMetadata = $true }
if ($NativeMetadata) { $NativeBinding = $true }
if ($NativeBinding) { $NativeDpop = $true }
Set-Location -LiteralPath $PSScriptRoot
if (-not $ReportsDir) { $ReportsDir = Join-Path $PSScriptRoot 'reports' }
if ($ExistingRun -and (-not $RunId -or $ReportsDir -eq (Join-Path $PSScriptRoot 'reports'))) {
    throw 'Retained validation requires -RunId and a separate -ReportsDir'
}
if ((-not $Component -and -not $Combined) -or ($Component -and $Combined)) {
    throw 'Select exactly one of -Component certify, -Component verify, or -Combined'
}
if ($Endpoint) {
    if ($Combined) { throw '-Endpoint requires a single component; use -CertifyUrl and -VerifyUrl for combined mode' }
    if ($Component -eq 'certify') { $CertifyUrl = $Endpoint } else { $VerifyUrl = $Endpoint }
}
if (-not (Get-Command $Python -ErrorAction SilentlyContinue)) { throw 'Python is required; see SETUP.md' }
if (-not $RunnerOnly -and -not (Get-Command $Maven -ErrorAction SilentlyContinue)) { throw 'Maven is required for TestNG reporting; use -RunnerOnly to explicitly run Python alone' }
if (-not $SkipDocker) {
    if (-not ($NativeCertify -or $NativeDpop)) { $env:CERTIFY_NATIVE_IMAGE = $null }
    & $Python runner/setup.py
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & $Python runner/preflight.py
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    $composeFiles = @('-f','docker/docker-compose.yml')
    $profiles = @('--profile','storage')
    if ($Component -ne 'certify') {
        $profiles += '--profile','verify'
        if (-not $env:VERIFY_UI_URL) { $env:VERIFY_UI_URL = 'https://host.docker.internal:8445/verify' }
    }
    if ($Component -ne 'verify') {
        $profiles += '--profile','certify'
        if ($NativeCertify -or $NativeDpop) {
            $nativeArgs = @()
            $env:CERTIFY_NATIVE_IMAGE = 'inji-harness/certify-native:local'
            if ($NativeDpop) { $nativeArgs += '--dpop'; $env:CERTIFY_NATIVE_IMAGE = 'inji-harness/certify-dpop:local' }
            if ($NativeBinding) { $nativeArgs += '--holder-binding'; $env:CERTIFY_NATIVE_IMAGE = 'inji-harness/certify-binding:local' }
            if ($NativeMetadata) { $nativeArgs += '--signed-metadata'; $env:CERTIFY_NATIVE_IMAGE = 'inji-harness/certify-metadata:local' }
            if ($NativeFinal) { $nativeArgs += '--credential-errors'; $env:CERTIFY_NATIVE_IMAGE = 'inji-harness/certify-final:local' }
            if ($NativePositive) { $nativeArgs += '--positive-serial'; $env:CERTIFY_NATIVE_IMAGE = 'inji-harness/certify-positive:local' }
            & $Python runner/build_native_certify.py @nativeArgs
            if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
            $composeFiles += '-f','docker/certify-native.compose.yml'
        }
    }
    docker compose --env-file docker/.env @composeFiles @profiles up -d --build
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    if ($NativeDpop) {
        docker compose --env-file docker/.env @composeFiles @profiles exec -T course-database psql -v ON_ERROR_STOP=1 -U postgres -d inji_certify -f /docker-entrypoint-initdb.d/03-dpop-replay.sql
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
    $readyArgs = if ($Combined) { @('--combined') } else { @('--component', $Component) }
    if ($Insecure) { $readyArgs += '--insecure' }
    if ($VerifyUrl) { $readyArgs += '--verify-url', $VerifyUrl }
    if ($CertifyUrl) { $readyArgs += '--certify-url', $CertifyUrl }
    if ($OidfUrl) { $readyArgs += '--oidf-url', $OidfUrl }
    & $Python runner/wait_ready.py @readyArgs
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & $Python runner/init_local_storage.py
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    foreach ($line in Get-Content docker/.env) {
        $setting = $line -split '=', 2
        if ($setting.Count -eq 2 -and $setting[0] -in @('AWS_ACCESS_KEY_ID','AWS_SECRET_ACCESS_KEY','AWS_REGION','S3_ENDPOINT','S3_BUCKET','ISSUER_LOGIN_USERNAME','ISSUER_LOGIN_PASSWORD')) {
            if (-not [Environment]::GetEnvironmentVariable($setting[0])) {
                [Environment]::SetEnvironmentVariable($setting[0], $setting[1])
            }
        }
    }
    if ($Component -ne 'verify') {
        $issuerArgs = @('--configure-only')
        if ($Insecure) { $issuerArgs += '--insecure' }
        & $Python runner/course_issuer.py @issuerArgs
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        if ($NativePositive) {
            $rotationArgs = @()
            if ($Insecure) { $rotationArgs += '--insecure' }
            & $Python runner/rotate_development_keys.py @rotationArgs
            if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        }
        $defaults = @{
            VCI_CLIENT_ID='conformance-course-wallet'; VCI_CLIENT2_ID='conformance-course-wallet-2'; VCI_WALLET_JWKS_FILE='docker/local/wallet-keys/conformance-course-wallet.private.json'; VCI_WALLET2_JWKS_FILE='docker/local/wallet-keys/conformance-course-wallet-2.private.json'; VCI_SCOPE='course_completion'; VCI_AUTHORIZATION_SERVER='https://host.docker.internal:8446/auth/realms/course';
            VCI_CREDENTIAL_CONFIGURATION_ID='course-completion-sdjwt'; VCI_CREDENTIAL_FORMAT='sd_jwt_vc';
            VCI_CLIENT_AUTH_TYPE='private_key_jwt'; VCI_SENDER_CONSTRAIN='dpop';
            ISSUER_BROWSER_STEPS_FILE='config/course-browser.json'
        }
        foreach ($settingName in $defaults.Keys) {
            if (-not [Environment]::GetEnvironmentVariable($settingName)) {
                [Environment]::SetEnvironmentVariable($settingName, $defaults[$settingName])
            }
        }
    }
}
$argsList = @('runner/runner.py','--parallel',"$Parallel",'--poll-timeout',"$PollTimeout")
if ($Combined) { $argsList += '--combined' } else { $argsList += '--component', $Component }
if ($Diff) { $argsList += '--diff', $Diff }
if ($CertifyConfig) { $argsList += '--certify-config', $CertifyConfig }
if ($VerifyConfig) { $argsList += '--verify-config', $VerifyConfig }
if ($ExpectedFailures) { $argsList += '--expected-failures', $ExpectedFailures }
if ($Insecure) { $argsList += '--insecure' }
if ($CertifyUrl) { $argsList += '--certify-url', $CertifyUrl }
if ($VerifyUrl) { $argsList += '--verify-url', $VerifyUrl }
if ($OidfUrl) { $argsList += '--oidf-url', $OidfUrl }
if ($ExistingRun) {
    if ($CertifyConfig -or $VerifyConfig -or $ExpectedFailures) { throw 'Plan or exception files cannot change a retained official run' }
    $argsList = @('runner/retained_run.py','--existing-run',$ExistingRun,'--run-id',$RunId,'--reports-dir',$ReportsDir)
    if ($Combined) { $argsList += '--combined' } else { $argsList += '--component',$Component }
    if ($Insecure) { $argsList += '--insecure' }
    if ($OidfUrl) { $argsList += '--oidf-url',$OidfUrl }
    if ($Diff) { $argsList += '--diff',$Diff }
} else { $argsList += '--reports-dir',$ReportsDir }
if ($SkipDocker -and -not $ExistingRun) {
    $readyArgs = @('runner/wait_ready.py')
    if ($Combined) { $readyArgs += '--combined' } else { $readyArgs += '--component',$Component }
    if ($Insecure) { $readyArgs += '--insecure' }
    if ($OidfUrl) { $readyArgs += '--oidf-url',$OidfUrl }
    if ($CertifyUrl) { $readyArgs += '--certify-url',$CertifyUrl }
    if ($VerifyUrl) { $readyArgs += '--verify-url',$VerifyUrl }
    & $Python @readyArgs
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
& $Python @argsList
$runnerCode = $LASTEXITCODE
if ($runnerCode -gt 1) { exit $runnerCode }
$bridgeCode = 0
if (-not $RunnerOnly) {
    $reportArgs = @('runner/report_lifecycle.py','--reports-dir',$ReportsDir,'--max-report-age-seconds',"$MaxReportAgeSeconds")
    if ($Combined) { $reportArgs += '--combined' } else { $reportArgs += '--component',$Component }
    if ($ExistingRun) { $reportArgs += '--historical' }
    if ($CertifyUrl) { $reportArgs += '--certify-url',$CertifyUrl }
    if ($VerifyUrl) { $reportArgs += '--verify-url',$VerifyUrl }
    $env:MAVEN = $Maven
    & $Python @reportArgs
    $bridgeCode = $LASTEXITCODE
}
if ($runnerCode -ne 0) { exit $runnerCode }
exit $bridgeCode



