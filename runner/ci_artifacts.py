"""Export allowlisted CI results; raw credential evidence stays in private storage.

Public summaries retain result and provenance fields only. Gate consistency is
checked before export so publishing cannot hide a rejected component."""
import argparse
import hashlib
import html
import json
import re
from pathlib import Path

FIELDS={'component','plan_name','plan_id','status','total','passed','failed','warnings','skipped',
        'expected_failures','is_gated_pass','gate_met','regression_gate_met','components','timestamp','total_tests'}


def export(reports,output):
    """Create a restricted CI summary without copying plan configuration or private credential evidence."""
    reports,output=Path(reports).resolve(),Path(output).resolve()
    if reports==output or reports in output.parents or output in reports.parents:
        raise ValueError('CI export must be separate from private source reports')
    output.mkdir(parents=True,exist_ok=False)
    source=reports/'conformance-summary.json'
    data=json.loads(source.read_text())
    if data.get('schema_version')!=2 or not data.get('run_id') or not data.get('runs'):
        raise ValueError('No valid completed conformance summary; CI artifacts cannot establish success')
    safe={'schema_version':2,'run_id':data['run_id'],'kind':'restricted_ci_summary',
        'source_summary_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'runs':{},
        'consolidated':{k:v for k,v in data['consolidated'].items() if k in FIELDS}}
    if data.get('retained_source'):
        safe['derived_from_retained_results'] = True
        safe['official_conformance_result'] = False
        safe['live_official_api_rechecked'] = data['retained_source'].get('live_official_api_rechecked') is True
    if isinstance(data.get('deployment'), dict):
        deployment = data['deployment']
        safe_deployment = {}
        if deployment.get('issuer_build') in {'stock-release', 'custom-image', 'declared-custom-image', 'unidentified-external-deployment'}:
            safe_deployment['issuer_build'] = deployment['issuer_build']
        image = deployment.get('issuer_image', '')
        if isinstance(image, str) and re.fullmatch(r'(?:injistack/inji-certify-with-plugins|inji-harness/certify-[a-z-]+):[A-Za-z0-9_.-]+', image):
            safe_deployment['issuer_image'] = image
        image_id = deployment.get('issuer_image_id', '')
        if isinstance(image_id, str) and re.fullmatch(r'sha256:[a-f0-9]{64}', image_id):
            safe_deployment['issuer_image_id'] = image_id
        versions = deployment.get('versions', {})
        if isinstance(versions, dict):
            safe_deployment['versions'] = {key: value for key, value in versions.items()
                if key in {'CERTIFY_VERSION', 'VERIFY_VERSION', 'VERIFY_UI_VERSION', 'VERIFY_SDK_VERSION'}
                and isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9_.-]{1,100}', value)}
        safe['deployment'] = safe_deployment
    for component,run in data['runs'].items():
        if component not in {'certify','verify'}:raise ValueError('Unknown component')
        if not isinstance(run['results'],dict) or any(not isinstance(name,str) or not isinstance(status,str) or status not in {
                'PASSED','WARNING','SKIPPED','EXPECTED_FAILURE','FAILED','REVIEW','TIMEOUT','ERROR',
                'INTERRUPTED','CANCELLED','UNKNOWN'} for name,status in run['results'].items()):
            raise ValueError('Invalid result mapping; refusing to export unrestricted runtime data')
        safe['runs'][component]={'summary':{k:v for k,v in run['summary'].items() if k in FIELDS},
            'results':run['results']}
    if data['consolidated'].get('gate_met') and any(
            not r['summary'].get('is_gated_pass') or r['summary'].get('gate_met') is False or not r['results'] or any(
                status not in {'PASSED','WARNING','SKIPPED','EXPECTED_FAILURE'} for status in r['results'].values())
            for r in safe['runs'].values()):
        raise ValueError('Inconsistent positive gate; refusal to publish a false-green summary')
    (output/'ci-summary.json').write_text(json.dumps(safe,indent=2))
    rows=''.join('<tr><td>'+html.escape(component)+'</td><td>'+html.escape(name)+'</td><td>'+html.escape(status)+'</td></tr>'
        for component,run in safe['runs'].items() for name,status in run['results'].items())
    (output/'ci-report.html').write_text('<!doctype html><meta charset="utf-8"><title>CI conformance results</title>'
        '<style>body{font:16px system-ui;margin:35px}td,th{padding:10px;border:1px solid #ccc}table{border-collapse:collapse}</style>'
        '<h1>CI conformance results</h1><p>Run '+html.escape(safe['run_id'])+'</p><p>Gate: '+
        ('PASSED' if safe['consolidated'].get('gate_met') else 'FAILED')+'</p><p>Restricted summary. Raw evidence remains private.</p>'
        '<table><tr><th>Component</th><th>Test</th><th>Official/result-mapping status</th></tr>'+rows+'</table>')
    return safe


def main():
    """Export allowlisted reporting artifacts and reject malformed or inconsistent summaries."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reports-dir',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args()
    try:export(args.reports_dir,args.output_dir)
    except (ValueError,OSError,KeyError,TypeError) as exc:
        print('CI summary export failed: '+str(exc))
        return 1
    return 0


if __name__=='__main__':raise SystemExit(main())
