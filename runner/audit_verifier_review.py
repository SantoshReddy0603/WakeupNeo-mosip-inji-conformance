"""Read-only evidence audit. Success means consistent evidence, never conformance PASS."""
import argparse
import base64
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
from datetime import datetime, timezone
from oidf_client import OIDFClient

ERRORS = {
    'oid4vp-1final-verifier-invalid-kb-jwt-signature': 'ERR_INVALID_KB_SIGNATURE',
    'oid4vp-1final-verifier-invalid-credential-signature': 'ERR_SIGNATURE_VERIFICATION_FAILED',
    'oid4vp-1final-verifier-invalid-sd-hash': 'ERR_INVALID_SD_HASH',
}
POSITIVE = {'oid4vp-1final-verifier-happy-flow', 'oid4vp-1final-verifier-minimal-cnf-jwk',
            'oid4vp-1final-verifier-request-uri-method-post'}


def inspect_post_coverage(entries):
    """Require actual successful conditions, never infer coverage from a test name."""
    required = ['CreateWalletNonce', 'PostToRequestUriAndExtractRequestObject',
                'EnsureWalletNonceClaimMatchesPostedValue']
    checks = {name: any(e.get('src') == name and e.get('result') == 'SUCCESS'
                        for e in entries) for name in required}
    return {'conditions': checks, 'exercised': all(checks.values())}

def require(condition, message='Evidence consistency check failed'):
    # These checks must also run under Python's optimized mode.
    if not condition:
        raise AssertionError(message)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect_status_reference(credential):
    """Inspect recorded SD-JWT structure, not its validity; SDK supplies validation."""
    unavailable = {'decoded': False, 'status_reference_present': None,
                   'signature_validation_performed_by_this_inspection': False}
    if not isinstance(credential, str):
        return unavailable
    try:
        segments = credential.split('~')
        encoded = segments[0].split('.')[1]
        payload = json.loads(base64.b64decode(encoded + '=' * (-len(encoded) % 4), altchars=b'-_', validate=True))
        if not isinstance(payload, dict):
            return unavailable
        names = set(payload)
        for disclosure in segments[1:]:
            if not disclosure or '.' in disclosure:
                continue  # final KB-JWT is not a disclosure
            item = json.loads(base64.b64decode(disclosure + '=' * (-len(disclosure) % 4), altchars=b'-_', validate=True))
            if isinstance(item, list) and len(item) == 3 and isinstance(item[1], str):
                names.add(item[1])
        return {'decoded': True, 'credential_sha256': hashlib.sha256(credential.encode()).hexdigest(),
                'status_reference_present': bool({'status', 'credentialStatus'} & names),
                'status_member_present': 'status' in names, 'credential_status_member_present': 'credentialStatus' in names,
                'signature_validation_performed_by_this_inspection': False}
    except (ValueError, IndexError, UnicodeError):
        return unavailable


def assess_review(row):
    """Explain retained observations without adjudicating an official result."""
    negative=row['module'] in ERRORS
    expected=ERRORS.get(row['module'])
    correlated=bool(row.get('request_id') and row.get('transaction_id'))
    native_matches=(row.get('observed_error')==expected and row.get('all_checks_successful') is False
        if negative else row.get('all_checks_successful') is True)
    limits=[]
    if not correlated:limits.append('Missing request/transaction correlation')
    if not row.get('official_image_bytes_match') or row.get('unfilled_placeholders'):
        limits.append('Screenshot submission is missing or does not match official stored bytes')
    if row.get('status_check_entries',0)==0:
        limits.append('No credential revocation/status check was exercised in the recorded response')
    if row['module'] == 'oid4vp-1final-verifier-request-uri-method-post' and not row.get('request_uri_post_coverage', {}).get('exercised'):
        limits.append('Request URI POST/wallet_nonce coverage is NOT established; the named module can bypass POST in url_query')
    if negative and not row.get('native_log',{}).get('expected_error_logged'):
        limits.append('Specific rejection code is evidenced by the SDK response, not the retained backend log window')
    limits.append('Generic UI images require transaction IDs, suite logs and SDK responses to distinguish transactions')
    return {'test_id':row['test_id'],'module':row['module'],'official_result':row['observed_official_result'],
        'expected_behavior':('Reject with '+expected) if negative else 'Accept the valid presentation',
        'observed_behavior':row.get('observed_error') or row.get('ui_result_text'),
        'request_id':row.get('request_id'),'transaction_id':row.get('transaction_id'),
        'screenshot_sha256':row.get('screenshot_sha256'),
        'native_observation_matches_expectation':native_matches,'transaction_correlated':correlated,
        'missing_or_inconclusive_evidence':limits,'requires_authoritative_manual_review':True,
        'implementation_defect':('No defect established by the retained observations; this is not conformance approval'
            if native_matches and correlated else 'Inconclusive or contradictory observation; investigate before requesting approval'),
        'review_checklist':['Check native UI acceptance/rejection against this official test requirement',
            'Verify screenshot hash and request/transaction/SDK/suite-log correlation',
            'Obtain applicable authoritative review and supported recording of disposition'],
        'official_conformance_result':False}

def audit(reports, output, client, native_log=None):
    reports, output = Path(reports).resolve(), Path(output).resolve()
    if output == reports or reports in output.parents or output in reports.parents:
        raise ValueError('Audit output must be separate from original reports')
    original = {p.relative_to(reports).as_posix(): digest(p) for p in reports.rglob('*') if p.is_file()}
    summary = json.loads((reports / 'conformance-summary.json').read_text())
    run = summary['runs']['verify']
    if run['summary']['plan_name'] != 'oid4vp-1final-verifier-test-plan':
        raise ValueError('Unexpected verifier target')
    output.mkdir(parents=True, exist_ok=True)
    lines = Path(native_log).read_text().splitlines(keepends=True) if native_log else []
    rows = []
    for module in run['modules']:
        if module['status'] != 'REVIEW':
            continue
        test_id, name = module['test_id'], module['module_name']
        require(name in POSITIVE or name in ERRORS)
        require(re.fullmatch(r'[A-Za-z0-9_-]+', test_id) is not None)
        evidence = module['handoff']
        info = client.get_test_status(test_id)
        require(info.get('status') == 'FINISHED' and info.get('result') == module['status'],
                (test_id, 'Official instance status/result changed or is not final; re-investigate without rewriting history'))
        images = client.get_test_images(test_id)
        pending = [x['_id'] for x in images if x.get('upload') and not x.get('img')]
        screenshot = reports / test_id / 'verifier-browser.jpg'
        receipt = next(x for x in images if x['_id'] == evidence['log_entry_id'])
        require(base64.b64decode(receipt['img'].split(',', 1)[1]) == screenshot.read_bytes(), test_id)
        require(digest(screenshot) == evidence['screenshot_sha256'], test_id)
        require(not pending, (test_id, pending))
        result_path = reports / test_id / 'verifier-session-results.json'
        observed = json.loads(result_path.read_text())[-1]
        require(observed['http_status'] == 200 and observed['request']['skipStatusChecks'] is False)
        response = observed['response']
        require(response['transactionId'] == evidence['transaction_id'])
        checks = response['credentialResults'][0]
        error = checks.get('schemaAndSignatureCheck', {}).get('error') or {}
        expected_error = ERRORS.get(name)
        if expected_error:
            require(response['allChecksSuccessful'] is False and error['errorCode'] == expected_error)
            require(checks['schemaAndSignatureCheck']['valid'] is False,
                    (test_id, 'Native verification fields contradict the reported rejection'))
            require('invalid' in evidence['ui_result_text'].lower())
        else:
            require(response['allChecksSuccessful'] is True)
            require(checks['schemaAndSignatureCheck']['valid'] is True)
            require(checks['holderProofCheck']['valid'] is True)
            require('is valid' in evidence['ui_result_text'].lower())
        prefix = name + '-' + test_id
        for source, suffix in [(screenshot, '-ui.jpg'), (result_path, '-native-session-results.json'),
                               (reports / (test_id + '-log.json'), '-official-log.json'),
                               (reports / test_id / 'verifier-qr.png', '-qr.png')]:
            shutil.copyfile(source, output / (prefix + suffix))
        native = {'available': False}
        matches = [i for i, line in enumerate(lines) if 'authRequest: AuthorizationRequestCreateResponse' in line
                   and evidence['transaction_id'] in line and evidence['request_id'] in line]
        if matches:
            require(len(matches) == 1)
            start = matches[0]
            end = next((i for i in range(start + 1, len(lines))
                        if 'authRequest: AuthorizationRequestCreateResponse' in lines[i]), len(lines))
            segment = ''.join(lines[start:end])
            (output / (prefix + '-native-backend.log')).write_text(segment)
            native = {'available': True, 'first_source_line': start + 1, 'last_source_line': end,
                      'scope': 'contiguous window until next native authorization request; may include other threads',
                      'source_sha256': digest(Path(native_log)),
                      'expected_error_logged': expected_error in segment if expected_error else None}
        row = {'test_id': test_id, 'module': name, 'original_result': module['status'],
               'observed_official_result': info.get('result'), 'observed_official_status': info.get('status'),
               'local_log_url': client.base_url + '/log-detail.html?log=' + test_id,
               'request_id': evidence['request_id'], 'transaction_id': evidence['transaction_id'],
               'placeholder': evidence['placeholder'], 'log_entry_id': evidence['log_entry_id'],
               'unfilled_placeholders': pending, 'screenshot_sha256': digest(screenshot),
               'official_image_bytes_match': True, 'ui_result_text': evidence['ui_result_text'],
               'all_checks_successful': response['allChecksSuccessful'], 'expected_error': expected_error,
               'observed_error': error.get('errorCode'), 'skip_status_checks': observed['request']['skipStatusChecks'],
               'status_check_filters': observed['request'].get('statusCheckFilters'),
               'status_check_entries': len(checks.get('statusCheck', [])), 'native_log': native,
               'credential_status_reference': inspect_status_reference(checks.get('verifiableCredential')),
               'sdk_response_observed_at': observed.get('observed_at'),
               'sdk_response_request_url': observed.get('request_url'),
               'screenshot_file_mtime_utc': datetime.fromtimestamp(screenshot.stat().st_mtime, timezone.utc).isoformat(),
               'official_timestamps': {k: info[k] for k in ('created', 'started', 'finished', 'updated', 'startTime', 'endTime') if k in info}}
        if name == 'oid4vp-1final-verifier-request-uri-method-post':
            row['request_uri_post_coverage'] = inspect_post_coverage(
                json.loads((reports / (test_id + '-log.json')).read_text()))
        rows.append(row)
    require(len(rows) == 6, 'Expected six original REVIEW modules')
    exported = reports / ('plan-' + run['summary']['plan_id'] + '-export.zip')
    shutil.copyfile(exported, output / exported.name)
    require(original == {p.relative_to(reports).as_posix(): digest(p) for p in reports.rglob('*') if p.is_file()})
    result = {'kind': 'read_only_verifier_review_audit', 'official_conformance_result': False,
              'audited_at': datetime.now(timezone.utc).isoformat(), 'run_id': summary['run_id'],
              'plan_id': run['summary']['plan_id'], 'target': run['summary']['plan_name'],
              'original_files_unchanged': True, 'original_files_sha256': original,
              'original_verify_gate': run['summary']['is_gated_pass'],
              'original_combined_gate': summary['consolidated']['gate_met'], 'reviews': rows}
    (output / 'review-audit.json').write_text(json.dumps(result, indent=2))
    (output / 'review-assessments.json').write_text(json.dumps([assess_review(row) for row in rows],indent=2))
    manifest = {p.name: digest(p) for p in output.iterdir() if p.is_file() and p.name != 'manifest.json'}
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reports', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--suite-url', default='https://localhost:8443')
    parser.add_argument('--native-log', type=Path)
    parser.add_argument('--insecure', action='store_true')
    args = parser.parse_args()
    verify = False if args.insecure else os.getenv('CA_BUNDLE') or True
    result = audit(args.reports, args.output, OIDFClient(args.suite_url, os.getenv('OIDF_TOKEN'), verify_ssl=verify), args.native_log)
    print(json.dumps({'audit_consistent': True, 'original_files_unchanged': True,
                      'official_results': [r['observed_official_result'] for r in result['reviews']],
                      'native_log_correlations': sum(r['native_log']['available'] for r in result['reviews']),
                      'official_conformance_result': False}))

if __name__ == '__main__':
    main()
