"""Execute actual native TestNG/Extent reporters for labeled gate fixtures.

These are reporting regression tests, never official conformance results.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runner'))
from gate_policy import apply_component_gates

CASES = [('certify-pass-verify-review', True, False, None),
         ('certify-review-verify-pass', False, True, None),
         ('both-pass', True, True, None), ('both-review', False, False, None),
         ('certify-regression', True, True, 'certify'),
         ('verify-regression', True, True, 'verify')]


def fixture(name, certify, verify, regression):
    runs = {}
    for c, passed in [('certify', certify), ('verify', verify)]:
        results = {c + '-valid-controlled-fixture': 'PASSED'}
        if not passed:
            results[c + '-review-controlled-fixture'] = 'REVIEW'
        runs[c] = {'summary': {'component': c, 'passed': 1, 'is_gated_pass': passed}, 'results': results}
    data = {'schema_version': 2, 'run_id': 'controlled-gates-' + name,
            'official_conformance_result': False, 'runs': runs, 'consolidated': {
                'passed': 2, 'timestamp': datetime.now(timezone.utc).isoformat(),
                'results': {c + '::' + k: v for c, r in runs.items() for k, v in r['results'].items()}}}
    diff = {'has_regressions': True, 'component_regressions': {regression: [{'test': regression + '::removed-fixture'}]}} if regression else None
    apply_component_gates(data, ['certify', 'verify'], diff)
    return data


def validate(component, repo, classpath, output):
    module = Path(repo).resolve() / 'api-test' if repo else None
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    records = []
    env = {k: v for k, v in os.environ.items() if k not in {
        'S3_ENDPOINT', 'S3_BUCKET', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_REGION'}}
    for name, certify, verify, regression in CASES:
        folder = output / name
        folder.mkdir()
        data = fixture(name, certify, verify, regression)
        summary = folder / 'conformance-summary.json'
        summary.write_text(json.dumps(data, indent=2))
        props = ['-Dconformance.consumeReport=true', '-Dconformance.summary=' + str(summary),
                 '-Dconformance.runId=' + data['run_id'], '-Denv.endpoint=https://fixture.invalid']
        if component == 'combined':
            args = ['mvn', '-o', '-B', '-f', str(ROOT / 'testrig/pom.xml'), 'test',
                    '-DsuiteXmlFile=' + str(ROOT / 'testrig/testng-combined.xml'), *props]
            cwd = ROOT
            xml = ROOT / 'testrig/target/surefire-reports/testng-results.xml'
            xml.unlink(missing_ok=True)
            expected = data['consolidated']['gate_met']
        else:
            args = ['java', *props, '-cp', str(module / 'target/classes') + os.pathsep + Path(classpath).read_text().strip(),
                'io.inji.testrig.apirig.inji' + component + '.testscripts.ConformanceReporterMain',
                'testNgXmlFiles/inji' + component + 'ConformanceSuite.xml', str(folder / 'native-report')]
            cwd = module
            xml = folder / 'native-report/testng-results.xml'
            expected = data['runs'][component]['summary']['gate_met']
        with (folder / 'command.log').open('w') as log:
            result = subprocess.run(args, cwd=cwd, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=180)
        tree = ET.parse(xml).getroot()
        if component == 'combined':
            shutil.copyfile(xml, folder / 'testng-results.xml')
            html = folder / 'extent-report.html'
        else:
            htmls = list((folder / 'native-report').glob('*-report_T-*.html'))
            if not htmls:
                raise RuntimeError('Native Extent HTML missing: ' + name)
            html = htmls[0]
        gate_name = 'testReleaseGateBenchmark' if component == 'combined' else 'conformanceReleaseGate'
        gates = tree.findall('.//test-method[@name="' + gate_name + '"]')
        if len(gates) != 1 or gates[0].get('status') != ('PASS' if expected else 'FAIL'):
            raise RuntimeError('Gate assertion differs: ' + name)
        if result.returncode != (0 if expected else 1) or not html.is_file():
            raise RuntimeError('Reporter exit/HTML differs: ' + name)
        if any(v == 'REVIEW' for r in data['runs'].values() for v in r['results'].values()):
            assert 'REVIEW' in summary.read_text()
        records.append({'scenario': name, 'command': args, 'exit_status': result.returncode,
            'expected_exit_status': 0 if expected else 1, 'gate': gates[0].get('status'),
            'testng_counts': tree.attrib, 'html': str(html.relative_to(output)),
            'official_conformance_result': False})
    (output / 'validation.json').write_text(json.dumps(records, indent=2))
    print(component + ': six actual TestNG/Extent gate scenarios verified; validator exit 0')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--component', required=True, choices=['certify', 'verify', 'combined'])
    parser.add_argument('--repo', type=Path)
    parser.add_argument('--classpath-file', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    validate(args.component, args.repo, args.classpath_file, args.output)
