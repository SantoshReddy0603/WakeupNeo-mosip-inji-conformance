"""Read-only validation/replay of existing official results; never creates a plan."""
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


def hashes(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def validate_and_copy(source, destination, components, expected_id, client, baseline=None):
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
        official_modules = {m['testModule'] for m in plan['modules']}
        for module in run['modules']:
            if module['module_name'] not in official_modules:
                raise ValueError('Module missing from retained official plan')
            info = client.get_test_status(module['test_id'])
            if info.get('status') != 'FINISHED' or info.get('result') != module['status']:
                raise ValueError('Official result changed or is incomplete: ' + module['test_id'])
            if run['results'].get(module['test_name']) != module['status']:
                raise ValueError('Retained result mapping differs from official outcome')
            observed.append({'component':component, 'id':module['test_id'],
                             'status':info['status'], 'result':info['result']})
        if len(run['results']) != len(run['modules']) or not run['modules']:
            raise ValueError('Missing/extra retained module results')
        passed = sum(m['status'] in {'PASSED','WARNING'} for m in run['modules'])
        failed = sum(m['status'] not in {'PASSED','WARNING','SKIPPED'} for m in run['modules'])
        expected_gate = bool(passed and not failed and not run['summary'].get('artifact_error'))
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
