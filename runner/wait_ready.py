"""Bounded, read-only service readiness with per-endpoint diagnostics."""
import os
import argparse
import sys
import time
from urllib.parse import urlsplit, urlunsplit
import requests
from local_network import configure


def authorization_metadata_url(issuer):
    parsed=urlsplit(issuer)
    if (parsed.scheme not in {'http','https'} or not parsed.hostname or parsed.username
            or parsed.password or parsed.query or parsed.fragment):
        raise ValueError('Authorization issuer must be an HTTP(S) URL without credentials, query or fragment')
    return urlunsplit((parsed.scheme,parsed.netloc,
        '/.well-known/oauth-authorization-server'+parsed.path,'',''))


def wait(urls,timeout=180,interval=2,request_timeout=5,verify=True,ui_url=None,authorization_server=None):
    if min(timeout,interval,request_timeout)<=0:raise ValueError('Readiness timeouts/interval must be positive')
    urls=list(urls)
    authorization_url=authorization_metadata_url(authorization_server) if authorization_server else None
    if authorization_url:urls.append(authorization_url)
    for url in urls:
        parsed=urlsplit(url)
        if parsed.scheme not in {'http','https'} or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError('Readiness endpoints must be HTTP(S) URLs without embedded credentials')
    pending=dict.fromkeys(urls,'not checked')
    deadline=time.monotonic()+timeout
    while pending and time.monotonic()<deadline:
        for url in list(pending):
            remaining=deadline-time.monotonic()
            if remaining<=0:break
            try:
                headers={'Authorization':'Bearer '+os.environ['OIDF_TOKEN']} if url.endswith('/available') and os.getenv('OIDF_TOKEN') else {}
                response=requests.get(url,verify=verify,headers=headers,timeout=min(request_timeout,remaining))
                response.raise_for_status()
                if url==ui_url:
                    valid='text/html' in response.headers.get('Content-Type','') and 'id="root"' in response.text
                else:
                    value=response.json()
                    if url==authorization_url:
                        valid=(isinstance(value,dict) and value.get('issuer')==authorization_server
                            and all(isinstance(value.get(key),str) and value[key]
                                for key in ['authorization_endpoint','token_endpoint','jwks_uri']))
                    else:
                        valid=(isinstance(value,list) and url.endswith('/available') or isinstance(value,dict)
                            and (value.get('status')=='UP' or url.endswith('/openid-credential-issuer') and value.get('credential_endpoint')))
                if valid:
                    del pending[url]
                    print('Ready: '+url,flush=True)
                else:pending[url]='HTTP response did not contain the expected health/metadata/UI payload'
            except requests.exceptions.SSLError:
                pending[url]='TLS validation failed: configure CA_BUNDLE with the deployment CA'
            except requests.HTTPError as exc:
                pending[url]='HTTP '+str(exc.response.status_code)+': inspect service logs and authentication configuration'
            except requests.Timeout:
                pending[url]='request timed out: check service health and endpoint routing'
            except requests.RequestException:
                pending[url]='connection failed: check Docker services, port mappings and endpoint routing'
            except ValueError:
                pending[url]='response is not the expected JSON health/metadata payload'
        if pending:time.sleep(min(interval,max(0,deadline-time.monotonic())))
    return pending


def main(argv=None):
    configure()
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--component',choices=['certify','verify'])
    parser.add_argument('--combined',action='store_true')
    parser.add_argument('--insecure',action='store_true')
    parser.add_argument('--oidf-url',default=os.getenv('OIDF_URL') or 'https://localhost:8443')
    parser.add_argument('--certify-url',default=os.getenv('CERTIFY_ISSUER_URL') or 'https://host.docker.internal:8446')
    parser.add_argument('--verify-url',default=os.getenv('VERIFY_API_URL') or 'https://localhost:8445/v1/verify')
    parser.add_argument('--timeout',type=float,default=180)
    args,_=parser.parse_known_args(argv)
    component='combined' if args.combined else args.component or 'combined'
    urls=[args.oidf_url.rstrip('/')+'/api/runner/available']
    if component in {'combined','certify'}:
        urls.append(os.getenv('CERTIFY_HEALTH_URL') or args.certify_url.rstrip('/')+'/.well-known/openid-credential-issuer')
    if component in {'combined','verify'}:
        urls.append(os.getenv('VERIFY_HEALTH_URL') or args.verify_url.rstrip('/')+'/actuator/health')
        if os.getenv('VERIFY_UI_URL'):urls.append(os.environ['VERIFY_UI_URL'])
    try:
        failures=wait(urls,timeout=args.timeout,verify=False if args.insecure else os.getenv('CA_BUNDLE') or True,
            ui_url=os.getenv('VERIFY_UI_URL'),
            authorization_server=os.getenv('VCI_AUTHORIZATION_SERVER') if component in {'combined','certify'} else None)
    except ValueError as exc:
        parser.error(str(exc))
    for url,reason in failures.items():print('Startup failed: '+url+' - '+reason,file=sys.stderr)
    return 1 if failures else 0


if __name__=='__main__':sys.exit(main())
