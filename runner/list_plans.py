import argparse,json,os
from oidf_client import OIDFClient

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='List real OpenID suite plans and variants')
    parser.add_argument('--oidf-url',default=os.getenv('OIDF_URL','https://localhost:8443'))
    parser.add_argument('--insecure',action='store_true')
    args=parser.parse_args()
    client=OIDFClient(args.oidf_url,os.getenv('OIDF_TOKEN'),verify_ssl=False if args.insecure else (os.getenv('CA_BUNDLE') or True))
    plans=client.request('GET','/api/plan/available').json()
    for plan in plans:
        if any(word in plan.get('planName','') for word in ['oid4vp','oid4vci']):
            print(json.dumps(plan,indent=2))
