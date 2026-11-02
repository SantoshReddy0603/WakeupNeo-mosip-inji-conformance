"""Read-only validation of existing official results; never creates a plan.

Derived reporting remains separate from the preserved source bytes and is never
presented as a fresh official execution or an approval of REVIEW outcomes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import copy
from diff_engine import DiffEngine
from badge_generator import BadgeGenerator
from oidf_client import OIDFClient
from local_network import configure
from gate_policy import apply_component_gates
from runner import module_key, TERMINAL


def hashes(root):
    """Fingerprint retained source files so replay can prove that originals stayed unchanged."""
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def validate_and_copy(source, destination, components, expected_id, client, baseline=None):
    """Recheck retained run identity, official outcomes and gates before deriving separate reports."""
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError('Retained run and validation output must be separate')
    if destination.exists() and any(destination.iterdir()):
        raise ValueError('Validation output must be empty; preserve previous outputs')
    before = hashes(source)
    report = json.loads((source / 'conformance-summary.json').read_text())
    if report.get('schema_version') != 2 or report.get('run_id') != expected_id:
        raise ValueError('Retained report identity/schema mismatch')
    observed = []
    for component in components:
        run = report['runs'][component]
        if component == 'verify' and run['summary']['plan_name'] != 'oid4vp-1final-verifier-test-plan':
            raise ValueError('Unexpected verifier plan')
        plan = client.get_test_plan(run['summary']['plan_id'])
        official_modules = [module_key(m) for m in plan['modules']]
        retained_modules = [module_key({'testModule': m['module_name'],
                            'variant': m.get('variant', {})}) for m in run['modules']]
        instance_ids = [m['test_id'] for m in run['modules']]
        if (len(set(official_modules)) != len(official_modules)
                or len(set(retained_modules)) != len(retained_modules)
                or set(retained_modules) != set(official_modules)
                or len(set(instance_ids)) != len(instance_ids)):
            raise ValueError('Retained module/variant coverage or instance identity mismatch')
        for module, key in zip(run['modules'], retained_modules):
            if module['test_name'] != key:
                raise ValueError('Retained module result key mismatch')
            info = client.get_test_status(module['test_id'])
            variant = {**plan.get('variant', {}), **module.get('variant', {})}
            if (info.get('planId') != run['summary']['plan_id']
                    or info.get('testName') != module['module_name']
                    or info.get('variant') != variant
                    or info.get('testId') != module['test_id']):
                raise ValueError('Official instance does not match retained plan/module/variant')
            state = info.get('status')
            outcome = info.get('result') if state == 'FINISHED' else state
            if state not in TERMINAL or outcome != module['status']:
                raise ValueError('Official result changed or is incomplete: ' + module['test_id'])
            if run['results'].get(module['test_name']) != module['status']:
                raise ValueError('Retained result mapping differs from official outcome')
            observed.append({'component':component, 'id':module['test_id'],
                             'status':info['status'], 'result':info['result']})
        if len(run['results']) != len(run['modules']) or not run['modules']:
            raise ValueError('Missing/extra retained module results')
        passed = sum(m['status'] in {'PASSED','WARNING'} for m in run['modules'])
        failed = sum(m['status'] not in {'PASSED','WARNING','SKIPPED'} for m in run['modules'])
        expected_gate = bool(passed and not failed and not run['summary'].get('artifact_error')
                             and not any('evidence_error' in m for m in run['modules']))
        if run['summary']['is_gated_pass'] != expected_gate:
            raise ValueError('Component gate inconsistent with actual official outcomes')
    if report['consolidated']['gate_met'] and not all(
            r['summary']['is_gated_pass'] for r in report['runs'].values()):
        raise ValueError('Combined gate cannot accept a failed component')
    if baseline:
        baseline_path = Path(baseline).resolve()
        previous = json.loads(baseline_path.read_text(encoding='utf-8-sig'))
        results = previous.get('consolidated', previous).get('results', {})
        selected = {k:v for k,v in results.items() if k.split('::')[0] in components}
        if not selected:
            raise ValueError('Baseline has no results for requested components')
    shutil.copytree(source, destination, dirs_exist_ok=True)
    # A component-only replay has a component-only gate. Preserve the original
    # consolidated gate and bytes separately; never promote the official run.
    source_gate = report['consolidated']['gate_met']
    inherited_diff = None
    diff_path = source / 'conformance-diff.json'
    if diff_path.is_file():
        inherited_diff = json.loads(diff_path.read_text())
    # Do not discard an existing per-component rejection when projecting a run.
    inherited = {c: [{'reason': 'retained component regression rejection'}]
                 for c, r in report['runs'].items()
                 if r['summary'].get('regression_gate_met') is False}
    if inherited:
        inherited_diff = {'has_regressions': True, 'component_regressions': inherited}
    legacy_unexplained_failure = (not source_gate and all(
        r['summary'].get('is_gated_pass') is True for r in report['runs'].values())
        and inherited_diff is None)
    if set(components) != set(report['runs']):
        report = copy.deepcopy(report)
        report['runs'] = {c: report['runs'][c] for c in components}
        totals = {k: sum(r['summary'].get(k, 0) for r in report['runs'].values())
                  for k in ('total', 'passed', 'failed', 'expected_failures', 'warnings', 'skipped')}
        gate = all(r['summary']['is_gated_pass'] for r in report['runs'].values())
        report['consolidated'] = {**report['consolidated'], **totals,
            'total_tests': totals['total'], 'components': components, 'gate_met': gate,
            'status': 'PASSED' if gate else 'FAILED',
            'results': {f'{c}::{k}': v for c, r in report['runs'].items() for k,v in r['results'].items()}}
        report['retained_source'] = {'run_id':expected_id, 'combined_gate_met':source_gate,
            'kind':'component_projection', 'official_conformance_result':False}
        shutil.copyfile(source/'conformance-summary.json',destination/'original-conformance-summary.json')
    diff = inherited_diff
    if baseline:
        diff = DiffEngine.compare_runs({'results':selected},report)
        diff.update(baseline_run_id=previous.get('run_id'), current_run_id=expected_id,
            baseline_sha256=hashlib.sha256(baseline_path.read_bytes()).hexdigest(),
            current_sha256=before['conformance-summary.json'],
            kind='comparison_of_retained_results', official_conformance_result=False)
        (destination/'conformance-diff.json').write_text(json.dumps(diff,indent=2))
        if diff['has_regressions']:
            report = copy.deepcopy(report)
            report['consolidated'].update(gate_met=False,status='FAILED')
            shutil.copyfile(source/'conformance-summary.json',destination/'original-conformance-summary.json')
        if inherited_diff and inherited_diff.get('has_regressions'):
            for c, failures in inherited_diff.get('component_regressions', {}).items():
                diff.setdefault('component_regressions', {}).setdefault(c, []).extend(failures)
            diff['has_regressions'] = True
        (destination/'conformance-diff.json').write_text(json.dumps(diff,indent=2))
    apply_component_gates(report, components, diff,
                          error='Unexplained retained failed gate' if legacy_unexplained_failure else None)
    report['retained_source'] = {**report.get('retained_source', {}),
        'run_id': expected_id, 'combined_gate_met': source_gate,
        'kind': 'component_gate_recalculation', 'official_conformance_result': False,
        'summary_sha256': before['conformance-summary.json']}
    shutil.copyfile(source/'conformance-summary.json',destination/'original-conformance-summary.json')
    for c in components:
        original_report = source / (c + '-conformance-report.json')
        if original_report.is_file():
            shutil.copyfile(original_report, destination / ('original-' + c + '-conformance-report.json'))
        (destination / (c + '-conformance-report.json')).write_text(json.dumps(report['runs'][c], indent=2))
        effective = report['runs'][c]['summary']['gate_met']
        (destination / (c + '-conformance-badge.svg')).write_text(BadgeGenerator.generate_svg(
            c + ' retained validation', 'PASSED' if effective else 'FAILED', '#4c1' if effective else '#e05d44'))
    if report != json.loads((source/'conformance-summary.json').read_text()):
        (destination/'conformance-summary.json').write_text(json.dumps(report,indent=2))
        original_badge = source/'combined-conformance-badge.svg'
        if original_badge.is_file():
            shutil.copyfile(original_badge,destination/'original-combined-conformance-badge.svg')
        status=report['consolidated']['status']
        label='/'.join(components)+' retained validation'
        (destination/'combined-conformance-badge.svg').write_text(BadgeGenerator.generate_svg(
            label,status,'#4c1' if report['consolidated']['gate_met'] else '#e05d44'))
    if hashes(source) != before:
        raise ValueError('Original retained run changed during validation')
    (destination / 'retained-run-validation.json').write_text(json.dumps({
        'kind':'read_only_existing_run_validation', 'official_conformance_result':False,
        'run_id':expected_id, 'original_files_unchanged':True, 'original_files_sha256':before,
        'observed':observed, 'gate_met':report['consolidated']['gate_met'],
        'original_combined_gate_met':source_gate, 'selected_components':components}, indent=2))
    return report


def main():
    """Validate selected retained components and return their effective gate exit status."""
    configure()
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--component', choices=['certify','verify'])
    mode.add_argument('--combined', action='store_true')
    parser.add_argument('--existing-run', required=True, type=Path)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--reports-dir', required=True, type=Path)
    parser.add_argument('--oidf-url', default=os.getenv('OIDF_URL') or 'https://localhost:8443')
    parser.add_argument('--insecure', action='store_true')
    parser.add_argument('--diff', type=Path)
    args = parser.parse_args()
    client = OIDFClient(args.oidf_url, os.getenv('OIDF_TOKEN'),
                        verify_ssl=False if args.insecure else os.getenv('CA_BUNDLE') or True)
    try:
        report = validate_and_copy(args.existing_run, args.reports_dir,
            ['certify','verify'] if args.combined else [args.component], args.run_id, client,args.diff)
    except Exception as exc:
        print('Retained-run validation failed: ' + str(exc), file=os.sys.stderr)
        return 2
    finally:
        client.close()
    print('Retained official results verified; original timestamp and results preserved.')
    return 0 if report['consolidated']['gate_met'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
