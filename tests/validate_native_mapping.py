"""Execute real native TestNG integration with controlled result-mapping fixtures.

These outputs test reporting contracts and are never official conformance results.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET


def validate(component, repo, classpath_file, output):
    module = Path(repo).resolve() / 'api-test'
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    states = ['PASSED', 'WARNING', 'SKIPPED', 'EXPECTED_FAILURE', 'FAILED', 'REVIEW',
              'TIMEOUT', 'ERROR', 'INTERRUPTED', 'CANCELLED', 'UNKNOWN']
    summary = output / 'conformance-summary.json'
    summary.write_text(json.dumps({'schema_version': 2, 'run_id': 'controlled-mapping-fixture',
        'official_conformance_result': False, 'runs': {component: {
            'summary': {'passed': 2, 'is_gated_pass': False},
            'results': {state + '-controlled-fixture': state for state in states}}},
        'consolidated': {'timestamp': datetime.now(timezone.utc).isoformat(), 'gate_met': False}}))
    env = {k: v for k, v in os.environ.items()
           if k not in {'S3_ENDPOINT', 'S3_BUCKET', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_REGION'}}
    command = ['java', '-Dconformance.consumeReport=true', '-Dconformance.summary=' + str(summary),
        '-Dconformance.runId=controlled-mapping-fixture', '-Denv.endpoint=https://fixture.invalid',
        '-cp', str(module / 'target/classes') + os.pathsep + Path(classpath_file).resolve().read_text().strip(),
        'io.inji.testrig.apirig.inji' + component + '.testscripts.ConformanceReporterMain',
        'testNgXmlFiles/inji' + component + 'ConformanceSuite.xml', str(output / 'report')]
    with (output / 'command.log').open('w') as log:
        result = subprocess.run(command, cwd=module, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=180)
    tree = ET.parse(output / 'report/testng-results.xml')
    actual = {}
    for case in tree.findall('.//test-method'):
        if case.get('name') == 'conformanceModule':
            state = case.findall('./params/param/value')[1].text.strip().strip('"')
            actual[state] = case.get('status')
    expected = {s: 'PASS' if s in {'PASSED', 'WARNING'} else 'SKIP'
                if s in {'SKIPPED', 'EXPECTED_FAILURE'} else 'FAIL' for s in states}
    record = {'component': component, 'command': command, 'exit_status': result.returncode,
              'expected_failure_exit': True, 'mapping': actual, 'expected': expected,
              'testng_counts': tree.getroot().attrib, 'official_conformance_result': False}
    (output / 'validation.json').write_text(json.dumps(record, indent=2))
    if result.returncode != 1 or actual != expected or tree.getroot().get('failed') != '8':
        raise RuntimeError('Native TestNG mapping differs from required contract; see validation.json')
    print(component + ': all 11 statuses correctly mapped; native exit 1 expected; validator exit 0')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--component', required=True, choices=['certify', 'verify'])
    parser.add_argument('--repo', required=True, type=Path)
    parser.add_argument('--classpath-file', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    validate(args.component, args.repo, args.classpath_file, args.output)
