"""Execute actual module reporters, consolidated reporting and verified artifact storage."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import uuid
import boto3
from process_control import run
from preflight import validate_storage
from botocore.config import Config

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    'commons':('https://github.com/mosip/mosip-functional-tests.git','085cfa94301738d901c5b70547dbf005cb762c2b'),
    'certify':('https://github.com/inji/inji-certify.git','8fdf71656979a72fa8263766d4dec3cc25127b76'),
    'verify':('https://github.com/inji/inji-verify.git','4c4289026968beb535d3dbdd500947152c43f708'),
}

def checkout(name):
    variable = 'MOSIP_FUNCTIONAL_TESTS_REPO' if name == 'commons' else name.upper() + '_API_TEST_REPO'
    path = Path(os.getenv(variable) or ROOT / 'docker/local/api-test' / name).resolve()
    url, pin = PINS[name]
    created = not path.exists()
    if created:
        path.parent.mkdir(parents=True, exist_ok=True)
        run(['git','init',str(path)],check=True)
        run(['git','-C',str(path),'remote','add','origin',url],check=True)
        # Fetch the audited commit, not all unrelated repository history/data.
        run(['git','-C',str(path),'fetch','--depth','1','--filter=blob:none','origin',pin],check=True)
        run(['git','-C',str(path),'sparse-checkout','set','apitest-commons' if name=='commons' else 'api-test'],check=True)
        run(['git','-C',str(path),'checkout','--detach',pin],check=True)
    actual = subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],text=True).strip()
    if actual != pin:
        raise ValueError('Unexpected api-testrig source revision: ' + name)
    return path, created

def upload_artifacts(reports, run_id, prefix):
    endpoint = os.getenv('S3_ENDPOINT')
    if not endpoint:
        if os.getenv('AWS_ACCESS_KEY_ID') or os.getenv('AWS_SECRET_ACCESS_KEY'):
            raise ValueError('S3_ENDPOINT is required for this MinIO lifecycle')
        return {'configured':False, 'verified':[]}
    client = boto3.client('s3', endpoint_url=endpoint,
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        region_name=os.getenv('AWS_REGION') or 'us-east-1', config=Config(s3={'addressing_style':'path'}))
    bucket = os.getenv('S3_BUCKET') or 'automationtests'
    verified = []
    report = json.loads((reports/'conformance-summary.json').read_text())
    roots = {'conformance-summary.json','combined-conformance-badge.svg','extent-report.html',
             'testng-results.xml','conformance-diff.json','retained-run-validation.json','reporter-exit-statuses.json',
             'original-conformance-summary.json','original-combined-conformance-badge.svg'}
    ids = set()
    for component, run in report['runs'].items():
        roots.update({component+'-conformance-report.json',component+'-conformance-badge.svg',
                      'plan-'+run['summary'].get('plan_id','')+'-export.zip'})
        for module in run['modules']:
            if module.get('test_id'):
                ids.add(module['test_id'])
                roots.add(module['test_id']+'-log.json')
    for path in sorted(reports.rglob('*')):
        if not path.is_file(): continue
        relative = path.relative_to(reports)
        current = (len(relative.parts)==1 and relative.name in roots
                   or len(relative.parts)>1 and relative.parts[0] in ids
                   or len(relative.parts)>2 and relative.parts[0] in {'existing-certify','existing-verify'}
                   and relative.parts[1]==run_id)
        if not current: continue
        key = prefix + relative.as_posix()
        data = path.read_bytes()
        client.put_object(Bucket=bucket, Key=key, Body=data)
        received = client.get_object(Bucket=bucket, Key=key)['Body'].read()
        if received != data: raise ValueError('Artifact read-back mismatch: ' + key)
        verified.append({'file':path.relative_to(reports).as_posix(),'key':key,
                         'sha256':hashlib.sha256(received).hexdigest(),'bytes':len(received)})
    return {'configured':True,'bucket':bucket,'run_id':run_id,'prefix':prefix,'verified':verified}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--component', choices=['certify','verify'])
    mode.add_argument('--combined', action='store_true')
    parser.add_argument('--reports-dir', type=Path, required=True)
    parser.add_argument('--certify-url', default=os.getenv('CERTIFY_ISSUER_URL') or 'https://host.docker.internal:8446')
    parser.add_argument('--verify-url', default=os.getenv('VERIFY_API_URL') or 'https://localhost:8445/v1/verify')
    parser.add_argument('--max-report-age-seconds', type=int, default=7200)
    parser.add_argument('--historical', action='store_true')
    args = parser.parse_args()
    storage_errors=validate_storage(connect=True)
    if storage_errors:raise ValueError('; '.join(storage_errors))
    reports = args.reports_dir.resolve()
    summary = reports / 'conformance-summary.json'
    report = json.loads(summary.read_text())
    components = ['certify','verify'] if args.combined else [args.component]
    maven = os.getenv('MAVEN') or 'mvn'
    java = os.getenv('JAVA') or 'java'
    mvn = [maven,'-B','-s',str(ROOT/'integration/maven-settings.xml')]
    if os.getenv('MAVEN_OFFLINE') == 'true': mvn += ['-o']
    commons, new = checkout('commons')
    installed = commons/'.git/conformance-commons-installed'
    prepared_modules = all(os.getenv(c.upper()+'_API_TEST_CLASSPATH_FILE') for c in components)
    if new or (not prepared_modules and (not installed.exists() or installed.read_text() != PINS['commons'][1])):
        run(mvn+['-f',str(commons/'pom.xml'),'install','-DskipTests',
            '-Dmaven.javadoc.skip=true','-Dgpg.skip=true'],check=True)
        installed.write_text(PINS['commons'][1])
    codes = {}
    # Derived replay artifacts get a new namespace; never overwrite original S3 objects.
    prefix = ('openid-conformance-validation/' if args.historical else 'openid-conformance/') + report['run_id'] + '/'
    if args.historical: prefix += uuid.uuid4().hex + '/'
    for component in components:
        repo, _ = checkout(component)
        run([os.sys.executable,str(ROOT/'integration/install.py'),'--'+component+'-repo',str(repo)],check=True)
        module = repo/'api-test'
        cp = reports / (component+'-classpath.txt')
        prepared = os.getenv(component.upper()+'_API_TEST_CLASSPATH_FILE')
        if prepared:
            # Reuse an actual Maven-generated dependency classpath for an already
            # built pinned module. Compile BOTH bridge sources, never fake a build.
            data = Path(prepared).read_text().strip()
            if not data or not all(Path(p).is_file() for p in data.split(os.pathsep)):
                raise ValueError('Prepared dependency classpath has missing JARs')
            cp.write_text(data)
            sources = module/('src/main/java/io/inji/testrig/apirig/inji'+component+'/testscripts')
            run([os.getenv('JAVAC') or 'javac','--release','11','-proc:none',
                '-cp',str(module/'target/classes')+os.pathsep+data,'-d',str(module/'target/classes'),
                str(sources/'OpenIDConformanceTest.java'),str(sources/'ConformanceReporterMain.java')],check=True)
        else:
            run(mvn+['-f',str(module/'pom.xml'),'compile','dependency:build-classpath',
                               '-DskipTests','-Dmdep.outputFile='+str(cp)],check=True)
        classpath = str(module/'target/classes') + os.pathsep + cp.read_text().strip()
        package = 'io.inji.testrig.apirig.inji'+component+'.testscripts.ConformanceReporterMain'
        endpoint = args.certify_url if component == 'certify' else args.verify_url
        codes[component] = run([java,'-Dconformance.consumeReport=true',
            '-Dconformance.summary='+str(summary),'-Dconformance.runId='+report['run_id'],
            '-Dconformance.maxReportAgeSeconds='+str(args.max_report_age_seconds),
            '-Dconformance.storageModule='+prefix+'existing-'+component+'/'+report['run_id'],
            '-Denv.endpoint='+endpoint,'-cp',classpath,package,
            'testNgXmlFiles/inji'+component+'ConformanceSuite.xml',str(reports/('existing-'+component)/report['run_id'])],cwd=module).returncode
    # Preserve the established Extent/TestNG lifecycle in every run mode.
    suite = 'combined' if args.combined else args.component
    xml = ROOT/'testrig/target/surefire-reports/testng-results.xml'
    # A Maven startup/compile failure must not relabel the previous invocation's
    # XML or copied historical Extent report as newly generated evidence.
    xml.unlink(missing_ok=True)
    (reports/'testng-results.xml').unlink(missing_ok=True)
    (reports/'extent-report.html').unlink(missing_ok=True)
    codes['combined' if args.combined else 'extent'] = run([maven,'-B','-f',str(ROOT/'testrig/pom.xml'),'test',
        '-DsuiteXmlFile='+str(ROOT/('testrig/testng-'+suite+'.xml')),'-Dconformance.consumeReport=true',
        '-Dconformance.summary='+str(summary),'-Dconformance.runId='+report['run_id'],
        '-Dconformance.maxReportAgeSeconds='+str(args.max_report_age_seconds),
        '-Dconformance.artifactPrefix='+prefix]).returncode
    (reports/'reporter-exit-statuses.json').write_text(json.dumps(codes,indent=2))
    if not xml.is_file() or not (reports/'extent-report.html').is_file():
        raise RuntimeError('Reporter produced no new TestNG XML/Extent HTML; inspect Maven output. Historical artifacts are not current evidence.')
    (reports/'testng-results.xml').write_bytes(xml.read_bytes())
    storage = upload_artifacts(reports, report['run_id'], prefix)
    (reports/'artifact-storage-validation.json').write_text(json.dumps(storage,indent=2))
    print(json.dumps({'reporters':codes,'storage_artifacts_verified':len(storage['verified']), 'artifact_prefix':prefix}))
    selected_gate = (report['consolidated']['gate_met'] if args.combined else
        report['runs'][args.component]['summary'].get('gate_met', report['consolidated']['gate_met']))
    return 1 if any(codes.values()) or not selected_gate else 0

if __name__ == '__main__':
    raise SystemExit(main())
