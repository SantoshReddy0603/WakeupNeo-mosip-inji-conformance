"""Controlled reliability fixtures; never official conformance evidence."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import threading
import pytest
import requests
from process_control import run
from preflight import validate_storage,validate_tls
from diff_engine import DiffEngine
from wait_ready import wait


def test_process_nonzero_is_not_ignored():
    with pytest.raises(subprocess.CalledProcessError) as exc:
        run([sys.executable,'-c','raise SystemExit(7)'],check=True,capture_output=True)
    assert exc.value.returncode==7


def bounded_wait(predicate, timeout=10):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        threading.Event().wait(0.01)
    raise AssertionError('Fixture did not reach its expected state within the deadline')


def process_running(pid):
    state = subprocess.run(['ps', '-o', 'stat=', '-p', str(pid)],
                           capture_output=True, text=True, timeout=3).stdout.strip()
    return bool(state) and not state.startswith('Z')


@pytest.mark.skipif(os.name!='posix',reason='POSIX process tree fixture; Windows uses taskkill /T')
@pytest.mark.parametrize('startup_delay', [0, 0.1, 1.0])
def test_timeout_kills_nested_session_and_retains_original_timeout(tmp_path, monkeypatch, startup_delay):
    heartbeat=tmp_path/'heartbeat'
    ready=tmp_path/'ready.json'
    child=f'''import json, os, signal, time
from pathlib import Path
signal.signal(signal.SIGTERM, signal.SIG_IGN)
time.sleep({startup_delay!r})
heartbeat=Path({str(heartbeat)!r})
heartbeat.write_text(str(time.monotonic()))
ready=Path({str(ready)!r})
temporary=ready.with_suffix('.tmp')
temporary.write_text(json.dumps({{'pid':os.getpid(),'session':os.getsid(0)}}))
temporary.replace(ready)
while True:
    heartbeat.write_text(str(time.monotonic()))
    time.sleep(0.02)
'''
    parent='import subprocess,sys,time; subprocess.Popen([sys.executable,"-c",'+repr(child)+'],start_new_session=True); print("parent-started",flush=True); time.sleep(30)'
    args=[sys.executable,'-c',parent]
    popen=subprocess.Popen
    processes=[]
    class ReadyProcess(popen):
        synchronized=False
        def communicate(self,*a,**kw):
            if not self.synchronized:
                self.synchronized=True
                # Startup is measured separately from the cleanup deadline. Slow
                # filesystem/interpreter startup must not invalidate this fixture.
                bounded_wait(ready.exists)
            return super().communicate(*a,**kw)
    def start(command,**kw):
        process=(ReadyProcess if command==args else popen)(command,**kw)
        if command==args:processes.append(process)
        return process
    monkeypatch.setattr('process_control.subprocess.Popen',start)
    try:
        with pytest.raises(subprocess.TimeoutExpired) as exc:
            run(args,timeout=0.15,capture_output=True)
        pid=json.loads(ready.read_text())['pid']
        assert json.loads(ready.read_text())['session']==pid
        assert exc.value.cmd==args and exc.value.timeout==0.15
        assert b'parent-started' in exc.value.output
        bounded_wait(lambda:not process_running(pid),timeout=3)
        assert not process_running(processes[0].pid)
        assert heartbeat.exists()
    finally:
        # Even fixture synchronization/assertion failures must leave no children.
        if ready.exists():
            try:os.kill(json.loads(ready.read_text())['pid'],9)
            except ProcessLookupError:pass
        for process in processes:
            if process.poll() is None:
                from process_control import _terminate
                _terminate(process)
            process.wait(timeout=3)


@pytest.mark.skipif(os.name!='posix',reason='POSIX snapshot failure fixture')
def test_cleanup_snapshot_failure_preserves_timeout_and_kills_root(monkeypatch):
    original=subprocess.run
    def failed_snapshot(command,**kw):
        if command[:2]==['ps','-eo']:raise FileNotFoundError('ps unavailable')
        return original(command,**kw)
    monkeypatch.setattr('process_control.subprocess.run',failed_snapshot)
    processes=[]
    popen=subprocess.Popen
    def start(*a,**kw):
        process=popen(*a,**kw);processes.append(process);return process
    monkeypatch.setattr('process_control.subprocess.Popen',start)
    with pytest.raises(subprocess.TimeoutExpired) as exc:
        run([sys.executable,'-c','import time;time.sleep(30)'],timeout=0.1)
    assert processes[0].poll() is not None
    assert any('snapshot failed' in note for note in exc.value.__notes__)


def test_process_start_failure_is_preserved():
    with pytest.raises(FileNotFoundError):run(['/nonexistent-conformance-executable'])


@pytest.mark.skipif(os.name!='posix',reason='POSIX interrupted process fixture')
def test_keyboard_interrupt_cleans_root_and_preserves_original(monkeypatch):
    popen=subprocess.Popen
    processes=[]
    original=KeyboardInterrupt('controlled interruption')
    args=[sys.executable,'-c','import time;time.sleep(30)']
    class Interrupted(popen):
        interrupted=False
        def communicate(self,*a,**kw):
            if not self.interrupted:
                self.interrupted=True
                raise original
            return super().communicate(*a,**kw)
    def start(command,**kw):
        process=(Interrupted if command==args else popen)(command,**kw)
        if command==args:processes.append(process)
        return process
    monkeypatch.setattr('process_control.subprocess.Popen',start)
    with pytest.raises(KeyboardInterrupt) as exc:
        run(args)
    assert exc.value is original and processes[0].poll() is not None


def test_storage_preflight_is_read_only_and_does_not_disclose_secrets(monkeypatch):
    assert 'AWS_SECRET_ACCESS_KEY' in validate_storage({'S3_ENDPOINT':'http://localhost:9000','AWS_ACCESS_KEY_ID':'test'})[0]
    state=[]
    class Storage:
        def head_bucket(self,**kw):state.append(kw);raise RuntimeError('secret-that-must-not-be-reported')
        def close(self):state.append('closed')
    monkeypatch.setattr('boto3.client',lambda *a,**k:Storage())
    errors=validate_storage({'S3_ENDPOINT':'http://127.0.0.1:1','AWS_ACCESS_KEY_ID':'a','AWS_SECRET_ACCESS_KEY':'b'},connect=True)
    assert state==[{'Bucket':'automationtests'},'closed']
    assert 'secret-that' not in errors[0] and 'inaccessible' in errors[0]


def test_missing_tls_key_is_actionable(tmp_path):
    assert 'missing or unreadable' in validate_tls(tmp_path)[0]


@pytest.mark.parametrize('error,expected',[(requests.Timeout(),'timed out'),
    (requests.exceptions.SSLError(),'CA_BUNDLE'),(requests.ConnectionError(),'port mappings')])
def test_readiness_failure_is_bounded_and_diagnosable(monkeypatch,error,expected):
    def failure(*a,**k):raise error
    monkeypatch.setattr('wait_ready.requests.get',failure)
    start=time.monotonic()
    errors=wait(['http://127.0.0.1:1/actuator/health'],timeout=0.02,interval=0.001)
    assert expected in next(iter(errors.values()))
    assert time.monotonic()-start<0.5


def test_readiness_rejects_bad_url_and_negative_timeout():
    with pytest.raises(ValueError):wait(['file:///tmp/a'])
    with pytest.raises(ValueError):wait(['http://localhost'],timeout=-1)


def test_readiness_waits_for_actual_authorization_metadata_after_502(monkeypatch):
    from wait_ready import authorization_metadata_url
    issuer='https://issuer.example/auth/realms/course'
    endpoint=authorization_metadata_url(issuer)
    assert endpoint=='https://issuer.example/.well-known/oauth-authorization-server/auth/realms/course'
    calls=[]
    def get(url,**kwargs):
        calls.append(url)
        response=requests.Response()
        response.status_code=502 if len(calls)==1 else 200
        response._content=json.dumps({'issuer':issuer,'authorization_endpoint':issuer+'/authorize',
            'token_endpoint':issuer+'/token','jwks_uri':issuer+'/keys'}).encode()
        return response
    monkeypatch.setattr('wait_ready.requests.get',get)
    assert wait([],authorization_server=issuer,timeout=1,interval=0.001)=={}
    assert calls==[endpoint,endpoint]


@pytest.mark.parametrize('metadata',[{'issuer':'https://wrong.example'},
    {'issuer':'https://issuer.example/auth/realms/course','authorization_endpoint':'a','token_endpoint':'t'}])
def test_authorization_metadata_requires_correct_issuer_and_endpoints(monkeypatch,metadata):
    def get(*args,**kwargs):
        response=requests.Response();response.status_code=200;response._content=json.dumps(metadata).encode()
        return response
    monkeypatch.setattr('wait_ready.requests.get',get)
    errors=wait([],authorization_server='https://issuer.example/auth/realms/course',timeout=0.02,interval=0.001)
    assert errors and 'expected' in next(iter(errors.values()))


def test_diff_does_not_hide_failure_to_skip_or_review_changes():
    old={'results':{'verify::negative':'FAILED','verify::happy':'REVIEW'},'gate_met':False,'benchmark':{'policy':'a'}}
    new={'results':{'verify::negative':'SKIPPED','verify::happy':'PASSED'},'gate_met':True,'benchmark':{'policy':'b'}}
    value=DiffEngine.compare_runs(old,new)
    assert value['has_regressions'] and len(value['unexpected_skips'])==1
    assert value['review_changes'][0]['current']=='PASSED'
    assert value['benchmark_changes'] and value['gate_changes']
    assert 'verify' in value['component_regressions']
    assert value['unchanged']==[]
    assert old['results']['verify::happy']=='REVIEW'


def test_incomplete_storage_prevents_plan_creation(tmp_path,monkeypatch):
    from runner import main
    monkeypatch.setenv('S3_ENDPOINT','http://127.0.0.1:1')
    for key in ['AWS_ACCESS_KEY_ID','AWS_SECRET_ACCESS_KEY']:monkeypatch.delenv(key,raising=False)
    def forbidden(*a,**k):pytest.fail('A plan must not be created when artifact storage is incomplete')
    monkeypatch.setattr('runner.OIDFClient.create_test_plan',forbidden)
    assert main(['--component','verify','--reports-dir',str(tmp_path)])==1
    data=json.loads((tmp_path/'conformance-summary.json').read_text())
    assert not data['consolidated']['gate_met'] and 'Incomplete artifact storage' in data['error']


def test_ci_export_retains_failed_review_without_private_runtime_data(tmp_path):
    from ci_artifacts import export
    private=tmp_path/'private';private.mkdir()
    source={'schema_version':2,'run_id':'controlled-fixture','runs':{'verify':{
        'summary':{'is_gated_pass':False,'plan_id':'fixture-plan','client_secret':'DO-NOT-EXPORT'},
        'results':{'fixture-module':'REVIEW'},'modules':[{'access_token':'DO-NOT-EXPORT'}]}},
        'consolidated':{'gate_met':False,'status':'FAILED','private_key':'DO-NOT-EXPORT'}}
    (private/'conformance-summary.json').write_text(json.dumps(source))
    result=export(private,tmp_path/'safe')
    assert result['runs']['verify']['results']['fixture-module']=='REVIEW'
    assert not result['consolidated']['gate_met']
    assert 'DO-NOT-EXPORT' not in (tmp_path/'safe/ci-summary.json').read_text()
    assert 'FAILED' in (tmp_path/'safe/ci-report.html').read_text()
    source['consolidated']['gate_met']=True
    (private/'conformance-summary.json').write_text(json.dumps(source))
    with pytest.raises(ValueError,match='false-green'):export(private,tmp_path/'invalid')


def test_reporter_failure_cannot_reuse_old_xml_or_extent(tmp_path,monkeypatch):
    import report_lifecycle as lifecycle
    reports=tmp_path/'reports';reports.mkdir()
    (reports/'conformance-summary.json').write_text(json.dumps({'run_id':'controlled-fixture',
        'runs':{'verify':{}},'consolidated':{'gate_met':False}}))
    old_xml=tmp_path/'testrig/target/surefire-reports/testng-results.xml'
    old_xml.parent.mkdir(parents=True);old_xml.write_text('<old-passing-report/>')
    (reports/'extent-report.html').write_text('old passing report')
    jar=tmp_path/'fixture.jar';jar.write_bytes(b'fixture')
    cp=tmp_path/'cp';cp.write_text(str(jar))
    monkeypatch.setenv('VERIFY_API_TEST_CLASSPATH_FILE',str(cp))
    monkeypatch.setattr(lifecycle,'ROOT',tmp_path)
    monkeypatch.setattr(lifecycle,'checkout',lambda name:(tmp_path/('repo-'+name),False))
    monkeypatch.setattr(lifecycle,'validate_storage',lambda **kw:[])
    monkeypatch.setattr(lifecycle,'run',lambda args,**kw:subprocess.CompletedProcess(args,1 if args[0]=='mvn' else 0))
    monkeypatch.setattr(sys,'argv',['report_lifecycle.py','--component','verify','--reports-dir',str(reports)])
    with pytest.raises(RuntimeError,match='no new TestNG'):lifecycle.main()
    assert not old_xml.exists() and not (reports/'extent-report.html').exists()
    assert json.loads((reports/'reporter-exit-statuses.json').read_text())['extent']==1


def test_review_diagnosis_is_not_review_approval():
    from audit_verifier_review import assess_review
    result=assess_review({'module':'oid4vp-1final-verifier-invalid-sd-hash','test_id':'fixture',
        'request_id':'req-fixture','transaction_id':'txn-fixture','all_checks_successful':False,
        'observed_error':'ERR_INVALID_SD_HASH','observed_official_result':'REVIEW',
        'official_image_bytes_match':True,'unfilled_placeholders':[]})
    assert result['official_result']=='REVIEW' and result['native_observation_matches_expectation']
    assert result['requires_authoritative_manual_review'] and not result['official_conformance_result']
    assert len(result['missing_or_inconclusive_evidence'])==3


@pytest.mark.parametrize('value',[[],{'plan_name':'x','configuration':[]},{'plan_name':'x','configuration':{},'variant':[]}])
def test_plan_structure_fails_before_api_use(tmp_path,value):
    from runner import ConformanceRunner
    from types import SimpleNamespace
    path=tmp_path/'bad.json';path.write_text(json.dumps(value))
    def forbidden(*a,**k):pytest.fail('Invalid configuration must not create an official plan')
    runner=ConformanceRunner(SimpleNamespace(create_test_plan=forbidden),tmp_path/'reports')
    with pytest.raises(ValueError,match='Plan configuration requires'):runner.run_plan('verify',path,{},[])


def test_unsupported_java_has_actionable_diagnostic(monkeypatch):
    from preflight import validate_java
    monkeypatch.setattr('preflight.run',lambda *a,**kw:subprocess.CompletedProcess(a,0,'','java version "1.8.0"'))
    assert 'Java 21 or newer' in validate_java(21)[0]
