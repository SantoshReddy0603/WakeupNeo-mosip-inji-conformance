"""Measured local integration fixtures; never official conformance evidence."""
import io
import json
import time
import zipfile
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Barrier, Lock, Thread
from urllib.parse import parse_qs, urlsplit

import pytest
from runner import main, load_expected_failures, classify
from oidf_client import OIDFClient
from diff_engine import DiffEngine


def exception(**changes):
    return {'test_name':'module-a', 'reason':'Controlled test of exception rules',
        'jira_id':'fixture-issue-1', 'expiry_date':(date.today()+timedelta(days=1)).isoformat(),
        'statuses':['FAILED'], **changes}


@pytest.mark.parametrize('changes',[
    {'reason':' '}, {'jira_id':''}, {'statuses':'FAILED'}, {'statuses':['REVIEW']},
    {'statuses':['FAILED','TIMEOUT']}, {'test_name':''}, {'expiry_date':'invalid'},
    {'expiry_date':(date.today()-timedelta(days=1)).isoformat()}, {'reason':True},
])
def test_exception_file_rejects_invalid_metadata(tmp_path,changes):
    p=tmp_path/'exceptions.json'
    p.write_text(json.dumps({'expected_failures':{'certify':[exception(**changes)]}}))
    with pytest.raises(ValueError): load_expected_failures(p)


def test_exception_file_valid_and_duplicate_entries(tmp_path):
    p=tmp_path/'exceptions.json'
    entry=exception()
    p.write_text(json.dumps({'expected_failures':{'certify':[entry]}}))
    assert classify('FAILED',load_expected_failures(p)['certify'][0])=='EXPECTED_FAILURE'
    assert classify('REVIEW',entry)=='REVIEW'
    p.write_text(json.dumps({'expected_failures':{'certify':[entry,entry]}}))
    with pytest.raises(ValueError,match='Duplicate'): load_expected_failures(p)


@pytest.mark.parametrize('status',['REVIEW','CANCELLED','FAILED','TIMEOUT'])
def test_diff_records_legitimate_fixes_without_modifying_input(status):
    previous={'results':{'test':status}}
    current={'results':{'test':'WARNING'}}
    assert DiffEngine.compare_runs(previous,current)['fixes_count']==1
    assert previous['results']['test']==status


@pytest.fixture
def concurrent_api():
    lock=Lock()
    state={'plans':{},'instances':{},'starts':[], 'active':0,'peak':0,'active_by_plan':{},
           'plan_peak':{},'barrier':None,'failed_component':None,'failed_module':None,'clients':{},'evidence_kind':'controlled_http_fixture'}
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args): pass
        def do_GET(self): self.handle_api()
        def do_POST(self): self.handle_api()
        def handle_api(self):
            path=urlsplit(self.path).path
            params=parse_qs(urlsplit(self.path).query)
            body=self.rfile.read(int(self.headers.get('Content-Length',0)))
            code,value=200,{}
            if path=='/api/runner/available': value=[]
            elif path=='/api/plan' and self.command=='POST':
                config=json.loads(body)
                component=params['planName'][0]
                with lock:
                    plan='plan-'+component
                    state['plans'][plan]={'component':component,'config':config}
                code,value=201,{'id':plan}
            elif path.startswith('/api/plan/export/'):
                plan=path.rsplit('/',1)[-1]
                stream=io.BytesIO()
                with zipfile.ZipFile(stream,'w') as archive:
                    archive.writestr('fixture.json',json.dumps({'plan':plan,'official_conformance_result':False}))
                value=stream.getvalue()
            elif path.startswith('/api/plan/'):
                value={'modules':[{'testModule':'module-a'},{'testModule':'module-b'}]}
            elif path=='/api/runner' and self.command=='POST':
                plan=params['plan'][0]
                module=params['test'][0]
                identifier=plan+'-'+module
                with lock: state['instances'][identifier]={'plan':plan,'module':module,'status':'CONFIGURED'}
                code,value=201,{'id':identifier}
            elif path.startswith('/api/runner/') and self.command=='POST':
                identifier=path.rsplit('/',1)[-1]
                instance=state['instances'][identifier]
                plan=instance['plan']
                with lock:
                    state['active']+=1
                    state['peak']=max(state['peak'],state['active'])
                    state['active_by_plan'][plan]=state['active_by_plan'].get(plan,0)+1
                    state['plan_peak'][plan]=max(state['plan_peak'].get(plan,0),state['active_by_plan'][plan])
                    state['starts'].append(identifier)
                try:
                    if state['barrier'] and instance['module']=='module-a':
                        state['barrier'].wait(timeout=8)
                    time.sleep(0.04)
                    instance['status']='FINISHED'
                finally:
                    with lock:
                        state['active']-=1
                        state['active_by_plan'][plan]-=1
            elif path.startswith('/api/info/'):
                instance=state['instances'][path.rsplit('/',1)[-1]]
                component=state['plans'][instance['plan']]['component']
                value={'status':instance['status'],'result':'FAILED' if component==state['failed_component'] or instance['module']==state['failed_module'] else 'PASSED'}
            elif path.startswith('/api/log/'):
                value=[{'kind':'controlled_fixture','instance':path.rsplit('/',1)[-1]}]
            else: code=404
            data=value if isinstance(value,bytes) else json.dumps(value).encode()
            self.send_response(code)
            self.send_header('Content-Length',str(len(data)))
            self.end_headers()
            self.wfile.write(data)
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    state['url']=f'http://127.0.0.1:{server.server_port}'
    thread=Thread(target=server.serve_forever,daemon=True)
    thread.start()
    yield state
    server.shutdown(); thread.join(); server.server_close()


@pytest.mark.parametrize('workers,failed',[(1,None),(2,None),(2,'certify')])
def test_measured_parallel_isolation_and_failure_handling(concurrent_api,tmp_path,monkeypatch,workers,failed):
    api=concurrent_api
    api.update(barrier=Barrier(2) if workers==2 else None,failed_component=failed)
    official=OIDFClient._official
    def observe(self,method,*args):
        if method=='create_test_plan': api['clients'][args[0]]=self
        return official(self,method,*args)
    monkeypatch.setattr(OIDFClient,'_official',observe)
    for name in ('VCI_WALLET_JWKS_FILE','VCI_WALLET2_JWKS_FILE','ISSUER_BROWSER_STEPS_FILE','VERIFY_REQUEST_FILE'):
        monkeypatch.delenv(name,raising=False)
    configs=[]
    for component in ('certify','verify'):
        config=tmp_path/(component+'.json')
        config.write_text(json.dumps({'plan_name':component,'configuration':{},'variant':{}}))
        configs.extend(['--'+component+'-config',str(config)])
    output=tmp_path/'report'
    code=main(['--combined','--parallel',str(workers),'--oidf-url',api['url'],'--reports-dir',str(output),*configs])
    report=json.loads((output/'conformance-summary.json').read_text())
    assert code==(1 if failed else 0)
    assert api['peak']==workers
    assert all(peak==1 for peak in api['plan_peak'].values())
    assert api['clients']['certify'] is not api['clients']['verify']
    assert api['clients']['certify'].session is not api['clients']['verify'].session
    assert len({p['config']['alias'] for p in api['plans'].values()})==2
    assert len(list(output.glob('*-log.json')))==4
    assert len(list(output.glob('plan-*-export.zip')))==2
    assert len(report['consolidated']['results'])==4
    assert report['runs']['verify']['summary']['is_gated_pass'] is True
    if failed: assert report['runs']['certify']['summary']['is_gated_pass'] is False
    (tmp_path/'measured-concurrency.json').write_text(json.dumps({
        'peak_concurrent_http_starts':api['peak'],'peak_per_plan':api['plan_peak'],
        'unique_aliases':2,'separate_clients':True,'failed_component':failed,'exit_status':code,
        'official_conformance_result':False},indent=2))


def test_selective_verify_ignores_unrelated_issuer_configuration(concurrent_api,tmp_path,monkeypatch):
    for name in ('VCI_WALLET_JWKS_FILE','VCI_WALLET2_JWKS_FILE','ISSUER_BROWSER_STEPS_FILE'):
        monkeypatch.setenv(name,str(tmp_path/'missing-issuer-file'))
    monkeypatch.delenv('VERIFY_REQUEST_FILE',raising=False)
    config=tmp_path/'verify.json'
    config.write_text(json.dumps({'plan_name':'verify','configuration':{},'variant':{}}))
    output=tmp_path/'report'
    assert main(['--component','verify','--oidf-url',concurrent_api['url'],
                 '--verify-config',str(config),'--reports-dir',str(output)])==0
    assert set(json.loads((output/'conformance-summary.json').read_text())['runs'])=={'verify'}
    assert len(concurrent_api['plans'])==1


@pytest.mark.parametrize('expired',[False,True])
def test_expected_failure_full_runner_preserves_raw_failed_status(concurrent_api,tmp_path,monkeypatch,expired):
    monkeypatch.delenv('ISSUER_BROWSER_STEPS_FILE',raising=False)
    monkeypatch.delenv('VCI_WALLET_JWKS_FILE',raising=False)
    monkeypatch.delenv('VCI_WALLET2_JWKS_FILE',raising=False)
    concurrent_api['failed_module']='module-b'
    config=tmp_path/'certify.json'
    config.write_text(json.dumps({'plan_name':'certify','configuration':{},'variant':{}}))
    exceptions=tmp_path/'exceptions.json'
    entry=exception(test_name='module-b')
    if expired: entry['expiry_date']=(date.today()-timedelta(days=1)).isoformat()
    exceptions.write_text(json.dumps({'expected_failures':{'certify':[entry]}}))
    output=tmp_path/'report'
    code=main(['--component','certify','--oidf-url',concurrent_api['url'],
        '--certify-config',str(config),'--expected-failures',str(exceptions),'--reports-dir',str(output)])
    report=json.loads((output/'conformance-summary.json').read_text())
    assert code==(1 if expired else 0)
    if expired:
        assert not concurrent_api['plans']
        assert report['consolidated']['gate_met'] is False
    else:
        run=report['runs']['certify']
        assert run['results']['module-b']=='EXPECTED_FAILURE'
        assert run['modules'][1]['status']=='FAILED'
        assert report['consolidated']['status']=='BASELINE_ACCEPTED'


@pytest.mark.parametrize('defect',['shared_alias','invalid_issuer_key'])
def test_component_setup_failure_keeps_other_component_evidence(concurrent_api,tmp_path,monkeypatch,defect):
    for name in ('VCI_WALLET_JWKS_FILE','VCI_WALLET2_JWKS_FILE','ISSUER_BROWSER_STEPS_FILE','VERIFY_REQUEST_FILE'):
        monkeypatch.delenv(name,raising=False)
    configs=[]
    for component in ('certify','verify'):
        p=tmp_path/(component+'.json')
        p.write_text(json.dumps({'plan_name':component,'variant':{},
            'configuration':{'alias':'shared'} if defect=='shared_alias' else {}}))
        configs+=['--'+component+'-config',str(p)]
    if defect=='invalid_issuer_key':monkeypatch.setenv('VCI_WALLET_JWKS_FILE',str(tmp_path/'missing-key'))
    output=tmp_path/'reports'
    code=main(['--combined','--parallel','2','--oidf-url',concurrent_api['url'],'--reports-dir',str(output),*configs])
    report=json.loads((output/'conformance-summary.json').read_text())
    assert code==1 and len(concurrent_api['plans'])==1
    assert len(report['runs'])==2
    assert sum(r['summary']['is_gated_pass'] for r in report['runs'].values())==1
    assert len(list(output.glob('*-log.json')))==2
    assert len(list(output.glob('plan-*-export.zip')))==1
