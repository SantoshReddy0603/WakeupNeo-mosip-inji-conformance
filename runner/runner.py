"""Live OpenID conformance orchestration with fail-closed release gating.

Official module outcomes and export retrieval both contribute to qualification;
reporting a completed request alone cannot establish conformance."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
import json
import logging
import os
from pathlib import Path
import re
import sys
import uuid
import hashlib
from threading import Lock

from badge_generator import BadgeGenerator
from diff_engine import DiffEngine
from oidf_client import OIDFClient, TERMINAL
from oid4vp_handoff import OID4VPHandoffClient, generate_signing_jwk
from local_network import configure as configure_network
from preflight import validate_storage
from gate_policy import apply_component_gates
from deployment_provenance import deployment_metadata

ROOT = Path(__file__).resolve().parents[1]
LOG = logging.getLogger('conformance')


def resolve_path(path):
    """Resolve user-supplied paths without requiring execution from the repository root."""
    path = Path(path)
    return path if path.is_absolute() or path.exists() else ROOT / path


def render_template(path, variables):
    """Render JSON safely and reject unset variables before creating an official plan."""
    text = resolve_path(path).read_text(encoding='utf-8-sig')
    # Replace inside JSON strings by escaped JSON string contents, not raw text.
    for key, value in variables.items():
        token = '${' + key + '}'
        if token in text and (value is None or value == ''):
            raise ValueError('Empty configuration variable: ' + key)
        if isinstance(value, (dict, list)):
            text = text.replace('"' + token + '"', json.dumps(value))
            text = text.replace(token, json.dumps(value))
        else:
            text = text.replace(token, json.dumps(str(value))[1:-1])
    missing = re.findall(r'\$\{([^}]+)\}', text)
    if missing:
        raise ValueError('Missing configuration variables: ' + ', '.join(sorted(set(missing))))
    return json.loads(text)


def is_entry_valid(entry):
    """Accept only documented, unexpired FAILED baselines; incomplete runs are ineligible."""
    try:
        return (isinstance(entry, dict)
            and all(isinstance(entry.get(k), str) and entry[k].strip() for k in ('reason', 'jira_id', 'expiry_date'))
            and isinstance(entry.get('statuses'), list) and entry['statuses'] == ['FAILED']
            and date.fromisoformat(entry['expiry_date']) >= date.today())
    except (KeyError, ValueError, TypeError):
        return False


def load_expected_failures(path):
    """Validate component-scoped baselines before they can affect result classification."""
    data = json.loads(resolve_path(path).read_text(encoding='utf-8-sig'))
    if not isinstance(data, dict) or not isinstance(data.get('expected_failures'), dict):
        raise ValueError('Expected-failure configuration must contain an expected_failures object')
    failures = data['expected_failures']
    if set(failures) - {'certify', 'verify'}:
        raise ValueError('Unknown component in expected-failure configuration')
    for entries in failures.values():
        if not isinstance(entries, list) or any(not is_entry_valid(e)
                or not isinstance(e.get('test_name'), str) or not e['test_name'].strip() for e in entries):
            raise ValueError('Each expected failure requires a test_name, reason, issue reference, unexpired date and statuses: [FAILED]')
        names = [e['test_name'] for e in entries]
        if len(names) != len(set(names)):
            raise ValueError('Duplicate expected failure entries')
    return failures


def classify(status, entry=None):
    """Preserve official outcomes except eligible, explicitly configured FAILED baselines."""
    if status in {'PASSED', 'WARNING', 'SKIPPED'}:
        return status
    # Operational errors and incomplete runs must never be waived.
    if status == 'FAILED' and entry and is_entry_valid(entry) and status in entry['statuses']:
        return 'EXPECTED_FAILURE'
    return status if status in {'REVIEW', 'TIMEOUT', 'ERROR', 'INTERRUPTED', 'CANCELLED'} else 'FAILED'


def atomic_json(path, value):
    """Replace a complete JSON file so readers cannot observe a partially written report."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, indent=2), encoding='utf-8')
    temp.replace(path)


def instance_id(info):
    """Require an official instance identifier before associating evidence with a test."""
    value = info.get('id') or info.get('_id')
    if not isinstance(value, str) or not value:
        raise ValueError('Suite returned no instance ID')
    return value


def module_key(module):
    """Keep different variants of the same module distinct in reports and comparisons."""
    variant = module.get('variant') or {}
    return module['testModule'] + (' [' + json.dumps(variant, sort_keys=True) + ']' if variant else '')


class ConformanceRunner:
    def __init__(self, client, reports_dir='reports', max_workers=1, poll_timeout=300,
                 verify_url='', verify_request=None, browser_steps=None, alias_registry=None):
        self.client = client
        self.reports_dir = Path(reports_dir)
        self.max_workers = max_workers
        self.poll_timeout = poll_timeout
        self.verify_url = verify_url
        self.verify_request = verify_request
        self.browser_steps = browser_steps
        self.alias_registry = alias_registry
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def execute_test_module(self, plan_id, module, component):
        """Drive one official instance and retain its outcome, native handoff and log identity."""
        key = module_key(module)
        result = {'test_name': key, 'module_name': module['testModule'], 'variant': module.get('variant', {}),
                  'status': 'ERROR', 'evidence_uploaded': False}
        try:
            created = self.client.create_test_from_plan(plan_id, module['testModule'], module.get('variant'))
            test_id = instance_id(created)
            result['test_id'] = test_id
            visited_browser_urls = set()
            def handoff(info, remaining):
                if component == 'verify':
                    if not self.verify_request:
                        raise ValueError('Set VERIFY_REQUEST_FILE to an Inji VP request JSON body')
                    if os.getenv('VERIFY_UI_URL'):
                        from verifier_browser import drive_verifier_browser
                        result['handoff'] = drive_verifier_browser(self.client, info, test_id,
                            os.environ['VERIFY_UI_URL'], self.verify_request, self.reports_dir / test_id, remaining)
                        result['evidence_uploaded'] = result['handoff']['evidence_uploaded']
                        return
                    handler = OID4VPHandoffClient(self.client.base_url, self.verify_url, self.verify_request,
                                                 self.client.session.verify,
                                                 sdk_version=os.getenv('VERIFY_SDK_VERSION') or None)
                    result['handoff'] = handler.execute_presentation_handoff(info, remaining)
                elif self.browser_steps:
                    from browser_handoff import drive_browser, browser_url
                    if not browser_url(info, self.browser_steps, visited_browser_urls):
                        return False
                    result['handoff'] = drive_browser(info, self.browser_steps, self.reports_dir / test_id,
                                                      self.client.session.verify, remaining, visited_browser_urls)
                else:
                    raise ValueError('Issuer requires login/consent automation: set ISSUER_BROWSER_STEPS_FILE')
            info = self.client.poll_test_completion(test_id, max_timeout_sec=self.poll_timeout, on_waiting=handoff)
            state = str(info.get('status', '')).upper()
            raw = str(info.get('result', '')).upper()
            result['details'] = info
            result['status'] = raw if state == 'FINISHED' and raw in {'PASSED', 'FAILED', 'WARNING', 'REVIEW', 'SKIPPED'} else state if state in TERMINAL | {'TIMEOUT'} else 'ERROR'
            if result['status'] == 'FINISHED':
                result['status'] = 'ERROR'
            logs = self.client.get_test_log(test_id)
            atomic_json(self.reports_dir / f'{test_id}-log.json', logs)
            result['log_file'] = f'{test_id}-log.json'
        except Exception as exc:
            result['status'] = 'ERROR'
            result['error'] = str(exc)
        LOG.info('%s: %s', key, result['status'])
        return result

    def run_plan(self, component, config_template_path, env_vars, expected_failures):
        """Execute an isolated plan and require passing results plus a retrievable official export."""
        config = render_template(config_template_path, env_vars)
        if (not isinstance(config,dict) or not isinstance(config.get('plan_name'),str) or not config['plan_name'].strip()
                or not isinstance(config.get('configuration'),dict) or not isinstance(config.get('variant',{}),dict)):
            raise ValueError('Plan configuration requires a nonblank plan_name, configuration object and variant object')
        config['configuration'].setdefault('alias', 'inji-' + component + '-' + uuid.uuid4().hex[:12])
        alias = config['configuration']['alias']
        if not isinstance(alias,str) or not alias.strip():
            raise ValueError('Plan alias must be a nonblank string')
        if self.alias_registry is not None:
            with self.alias_registry['lock']:
                if alias in self.alias_registry['aliases']:
                    raise ValueError('Component plans require distinct aliases')
                self.alias_registry['aliases'].add(alias)
        plan_id = instance_id(self.client.create_test_plan(config['plan_name'], config['configuration'], config.get('variant')))
        details = self.client.get_test_plan(plan_id)
        atomic_json(self.reports_dir / f'{component}-plan.json', details)
        modules = details.get('modules', [])
        if not modules or any(not isinstance(m, dict) or not m.get('testModule') for m in modules):
            raise ValueError('Plan contains no valid test modules')
        keys = [module_key(m) for m in modules]
        if len(keys) != len(set(keys)):
            raise ValueError('Plan contains duplicate module/variant pairs')
        # Suite modules share an alias and verifier session; execute each plan serially.
        # Combined plans may run concurrently with independent aliases and HTTP sessions.
        results = [self.execute_test_module(plan_id, m, component) for m in modules]
        exceptions = {e['test_name']: e for e in expected_failures}
        classified = {r['test_name']: classify(r['status'], exceptions.get(r['test_name'])) for r in results}
        counts = {s: list(classified.values()).count(s) for s in {'PASSED', 'WARNING', 'SKIPPED', 'EXPECTED_FAILURE'}}
        failures = sum(v not in {'PASSED', 'WARNING', 'SKIPPED', 'EXPECTED_FAILURE'} for v in classified.values())
        artifact_error = None
        try:
            self.client.export_plan_results(plan_id, str(self.reports_dir))
        except Exception as exc:
            artifact_error = str(exc)
        passed = counts['PASSED'] + counts['WARNING']
        # Skips alone do not qualify a release; missing official exports also reject it.
        gate = failures == 0 and passed > 0 and artifact_error is None
        summary = {'component': component, 'plan_name': config['plan_name'], 'plan_id': plan_id,
                   'status': ('BASELINE_ACCEPTED' if counts['EXPECTED_FAILURE'] else 'PASSED') if gate else 'FAILED',
                   'total': len(results), 'passed': passed, 'failed': failures,
                   'warnings': counts['WARNING'], 'skipped': counts['SKIPPED'],
                   'expected_failures': counts['EXPECTED_FAILURE'], 'is_gated_pass': gate}
        if artifact_error:
            summary['artifact_error'] = artifact_error
        output = {'summary': summary, 'results': classified, 'modules': results}
        atomic_json(self.reports_dir / f'{component}-conformance-report.json', output)
        save_badge(self.reports_dir / f'{component}-conformance-badge.svg', component, summary['status'])
        return output


def save_badge(path, label, status):
    """Render the effective gate outcome without changing the underlying report."""
    color = '#4c1' if status == 'PASSED' else '#dfb317' if status == 'BASELINE_ACCEPTED' else '#e05d44'
    path.write_text(BadgeGenerator.generate_svg(label, status, color), encoding='utf-8')


def main(argv=None):
    """Run the selected components and return failure if any required gate rejects the run."""
    configure_network()
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--component', choices=['certify', 'verify'])
    mode.add_argument('--combined', action='store_true')
    parser.add_argument('--oidf-url', default=os.getenv('OIDF_URL', 'https://localhost:8443'))
    parser.add_argument('--certify-url', default=os.getenv('CERTIFY_ISSUER_URL', 'https://host.docker.internal:8446'))
    parser.add_argument('--verify-url', default=os.getenv('VERIFY_API_URL', 'https://localhost:8445/v1/verify'))
    parser.add_argument('--parallel', type=int, default=1, help='Concurrent component plans; modules inside a plan remain serial')
    parser.add_argument('--poll-timeout', type=int, default=300)
    parser.add_argument('--insecure', action='store_true', help='Allow local self-signed TLS only')
    parser.add_argument('--diff')
    parser.add_argument('--expected-failures', default='config/expected-failures.json')
    parser.add_argument('--reports-dir', default=str(ROOT / 'reports'))
    parser.add_argument('--certify-config', default=(os.getenv('CERTIFY_PLAN_CONFIG') or 'config/certify-oid4vci-config.json.template'))
    parser.add_argument('--verify-config', default=(os.getenv('VERIFY_PLAN_CONFIG') or 'config/verify-oid4vp-config.json.template'))
    args = parser.parse_args(argv)
    if args.parallel < 1 or args.poll_timeout <= 0:
        parser.error('parallel and poll-timeout must be positive')
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    output_dir = Path(args.reports_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output = {'schema_version': 2, 'run_id': uuid.uuid4().hex, 'runs': {},
              'deployment': deployment_metadata()}
    components = ['certify', 'verify'] if args.combined else [args.component]
    # Replace stale summaries before any network operation, including startup failures.
    output['consolidated'] = {'status': 'RUNNING', 'gate_met': False, 'components': components}
    atomic_json(output_dir / 'conformance-summary.json', output)
    save_badge(output_dir / 'combined-conformance-badge.svg', 'Inji OpenID', 'RUNNING')
    client = OIDFClient(args.oidf_url, os.getenv('OIDF_TOKEN'), verify_ssl=False if args.insecure else (os.getenv('CA_BUNDLE') or True))
    try:
        exceptions = load_expected_failures(args.expected_failures)
        storage_errors=validate_storage(connect=True)
        if storage_errors:raise ValueError('; '.join(storage_errors))
        verify_request = json.loads(resolve_path(os.getenv('VERIFY_REQUEST_FILE') or 'config/verify-request.final.json').read_text(encoding='utf-8-sig')) if 'verify' in components else None
        browser_steps = json.loads(resolve_path(os.environ['ISSUER_BROWSER_STEPS_FILE']).read_text(encoding='utf-8-sig')) if 'certify' in components and os.getenv('ISSUER_BROWSER_STEPS_FILE') else None
        if not client.check_health():
            raise RuntimeError('OpenID suite unavailable: check Docker, OIDF_URL and TLS CA configuration')
        alias_registry = {'aliases':set(), 'lock':Lock()}
        def run_component(component):
            own_client = OIDFClient(args.oidf_url, os.getenv('OIDF_TOKEN'), verify_ssl=client.session.verify)
            runner = ConformanceRunner(own_client, output_dir, 1, args.poll_timeout,
                                       args.verify_url, verify_request, browser_steps,alias_registry)
            try:
                variables = dict(os.environ)
                wallet_path = os.getenv('VCI_WALLET_JWKS_FILE')
                wallet2_path = os.getenv('VCI_WALLET2_JWKS_FILE')
                variables.update(CERTIFY_BASE_URL=args.certify_url, VERIFY_BASE_URL=args.verify_url)
                if component == 'certify':
                    variables.update(
                        WALLET_JWKS=json.loads(resolve_path(wallet_path).read_text()) if wallet_path else {'keys': [generate_signing_jwk()]},
                        WALLET2_JWKS=json.loads(resolve_path(wallet2_path).read_text()) if wallet2_path else {'keys': [generate_signing_jwk()]})
                else:
                    variables['SIGNING_JWK'] = generate_signing_jwk(include_certificate=
                        os.getenv('VERIFY_CREDENTIAL_KEY_PROFILE', 'x509') == 'x509')
                template = args.certify_config if component == 'certify' else args.verify_config
                return component, runner.run_plan(component, template, variables, exceptions.get(component, []))
            except Exception as exc:
                LOG.error('%s could not run: %s', component, exc)
                return component, {'summary': {'component': component, 'status': 'ERROR',
                    'is_gated_pass': False, 'total': 0, 'passed': 0, 'failed': 1, 'expected_failures': 0,
                    'error': str(exc)}, 'results': {}, 'modules': []}
            finally:
                own_client.close()
        with ThreadPoolExecutor(max_workers=min(args.parallel, len(components))) as pool:
            output['runs'] = dict(pool.map(run_component, components))

    except Exception as exc:
        output['error'] = str(exc)
        LOG.error('%s', exc)
    finally:
        client.close()
    runs = output['runs']
    gate = len(runs) == len(components) and all(r['summary']['is_gated_pass'] for r in runs.values())
    totals = {k: sum(r['summary'].get(k, 0) for r in runs.values()) for k in ['total', 'passed', 'failed', 'expected_failures', 'warnings', 'skipped']}
    status = ('BASELINE_ACCEPTED' if totals['expected_failures'] else 'PASSED') if gate else 'FAILED'
    current_results = {f'{c}::{k}': v for c, run in runs.items() for k, v in run['results'].items()}
    diff = None
    if args.diff:
        try:
            baseline = json.loads(resolve_path(args.diff).read_text(encoding='utf-8-sig'))
            baseline = baseline.get('consolidated', baseline)
            # Only compare the requested components in a per-component execution.
            baseline = {**baseline, 'results': {k: v for k, v in baseline['results'].items() if k.split('::')[0] in components}}
            if not baseline['results']:
                raise ValueError('Baseline contains no results for requested components')
            diff = DiffEngine.compare_runs(baseline, {'results': current_results,'gate_met':gate,
                'benchmark':{'policy':'all-required-results-pass-with-evidence-v1',
                    'expected_failures_sha256':hashlib.sha256(resolve_path(args.expected_failures).read_bytes()).hexdigest()}})
            atomic_json(output_dir / 'conformance-diff.json', diff)
            if diff['has_regressions']:
                gate, status = False, 'FAILED'
        except Exception as exc:
            output['diff_error'] = str(exc)
            gate, status = False, 'FAILED'
    output['consolidated'] = {**totals, 'total_tests': totals['total'], 'status': status,
        'gate_met': gate, 'components': components, 'results': current_results,
        'timestamp': datetime.now(timezone.utc).isoformat()}
    if resolve_path(args.expected_failures).is_file():
        output['consolidated']['benchmark']={'policy':'all-required-results-pass-with-evidence-v1',
            'expected_failures_sha256':hashlib.sha256(resolve_path(args.expected_failures).read_bytes()).hexdigest()}
    gate = apply_component_gates(output, components, diff)
    status = output['consolidated']['status']
    for component, result in runs.items():
        atomic_json(output_dir / f'{component}-conformance-report.json', result)
        component_status = result['summary'].get('status', 'FAILED') if result['summary']['gate_met'] else 'FAILED'
        save_badge(output_dir / f'{component}-conformance-badge.svg', component, component_status)
    atomic_json(output_dir / 'conformance-summary.json', output)
    save_badge(output_dir / 'combined-conformance-badge.svg', 'Inji OpenID', status)
    print(json.dumps(output['consolidated'], indent=2))
    return 0 if gate else 1


if __name__ == '__main__':
    sys.exit(main())
