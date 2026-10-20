"""Run actual TestNG bridge contract checks using labeled synthetic report fixtures.
Execute from a shell with Maven and Java: python tests/validate_bridge.py.
These are bridge validation reports, not Inji conformance evidence.
"""
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CASES = ['pass', 'review', 'gate-failed', 'missing-component', 'stale', 'identity-mismatch', 'status-mapping']


def run():
    directory = ROOT / 'testrig/target/bridge-fixtures'
    env = dict(os.environ)
    for key in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'S3_ENDPOINT', 'S3_BUCKET']:
        env.pop(key, None)
    for case in CASES:
        path = directory / case
        path.mkdir(parents=True, exist_ok=True)
        valid = case != 'review'
        runs = {c: {'summary': {'component': c, 'total': 1, 'passed': int(valid), 'failed': int(not valid), 'is_gated_pass': valid},
                    'results': {c + '-fixture': 'PASSED' if valid else 'REVIEW'}} for c in ['certify', 'verify']}
        if case == 'missing-component':
            runs.pop('verify')
        if case == 'status-mapping':
            runs['verify']['results'].update({'warning-fixture': 'WARNING', 'skipped-fixture': 'SKIPPED', 'expected-failure-fixture': 'EXPECTED_FAILURE'})
        timestamp = datetime.now(timezone.utc) - (timedelta(days=1) if case == 'stale' else timedelta())
        report = {'schema_version': 2, 'run_id': 'bridge-fixture-' + case, 'runs': runs,
            'consolidated': {'timestamp': timestamp.isoformat(), 'gate_met': valid and case != 'gate-failed',
                'passed': 2 if valid else 0,
                'results': {c + '::' + k: v for c, result in runs.items() for k, v in result['results'].items()}}}
        summary = path / 'conformance-summary.json'
        summary.write_text(json.dumps(report), encoding='utf-8')
        run_id = 'wrong-run' if case == 'identity-mismatch' else report['run_id']
        command = ['mvn', '-B', 'test', '-DsuiteXmlFile=testng-combined.xml', '-Dconformance.consumeReport=true',
                   '-Dconformance.summary=' + str(summary), '-Dconformance.runId=' + run_id]
        with (path / 'maven.log').open('w') as log:
            result = subprocess.run(command, cwd=ROOT / 'testrig', env=env, stdout=log, stderr=subprocess.STDOUT)
        should_pass = case in {'pass', 'status-mapping'}
        print(f'{case}: exit={result.returncode}, expected={"success" if should_pass else "failure"}')
        if (result.returncode == 0) != should_pass:
            return 1
    return 0


if __name__ == '__main__':
    sys.exit(run())
