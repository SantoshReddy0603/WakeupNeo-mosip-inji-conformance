"""Rotate only the isolated synthetic issuer's legacy development certificates.

Existing key material is backed up and retained. New certificates are generated
by the patched native key manager, never edited or re-signed by this script.
"""
import argparse
import base64
import hashlib
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid
import warnings
import requests
from cryptography import x509
from local_network import configure

ROOT = Path(__file__).resolve().parents[1]
APPS = "('ROOT','CERTIFY_VC_SIGN_EC_R1')"
COMPOSE = ['docker', 'compose', '--env-file', 'docker/.env', '-f', 'docker/certify-final.compose.yml',
           '-f', 'docker/certify-native.compose.yml']

def command(arguments, **kwargs):
    return subprocess.run(arguments, cwd=ROOT, check=True, **kwargs)

def query(sql):
    return command(COMPOSE + ['exec', '-T', 'course-database', 'psql', '-v', 'ON_ERROR_STOP=1',
                              '-U', 'postgres', '-d', 'inji_certify', '-At', '-c', sql],
                   stdout=subprocess.PIPE, text=True).stdout.strip()

def serials(insecure):
    response = requests.get('https://host.docker.internal:8446/.well-known/openid-credential-issuer',
        headers={'Accept': 'application/jwt'}, verify=False if insecure else os.getenv('CA_BUNDLE') or True, timeout=30)
    response.raise_for_status()
    header = json.loads(base64.urlsafe_b64decode(response.text.split('.')[0] + '==='))
    assert header['typ'] == 'openidvci-issuer-metadata+jwt' and header['alg'] == 'ES256'
    with warnings.catch_warnings(record=True):
        # Inspect legacy certificates to decide whether rotation is needed.
        warnings.simplefilter('always')
        return [x509.load_der_x509_certificate(base64.b64decode(cert)).serial_number for cert in header['x5c']]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--insecure', action='store_true')
    parser.add_argument('--output', type=Path, default=ROOT / 'reports/development-key-rotation.json')
    args = parser.parse_args()
    configure()
    os.environ['CERTIFY_NATIVE_IMAGE'] = 'inji-harness/certify-positive:local'
    expected = subprocess.check_output(['docker', 'image', 'inspect', 'inji-harness/certify-positive:local',
                                       '--format', '{{.Id}}'], text=True).strip()
    running = subprocess.check_output(['docker', 'inspect', 'inji-certify-final-course-certify-1',
                                      '--format', '{{.Image}}'], text=True).strip()
    if running != expected:
        raise ValueError('Rotation requires the tested positive-serial image in the isolated course stack')
    before = serials(args.insecure)
    if not before:
        raise ValueError('Signed metadata contains no signing certificate chain')
    result = {'kind': 'development_key_rotation', 'official_conformance_result': False,
              'performed': False, 'serials_before': before}
    if any(serial <= 0 or serial.bit_length() > 159 for serial in before):
        aliases = json.loads(query("SELECT coalesce(json_agg(row_to_json(active)), '[]') FROM "
            "(SELECT id, key_expire_dtimes, uni_ident FROM certify.key_alias WHERE app_id IN " + APPS +
            " AND key_expire_dtimes > (now() AT TIME ZONE 'UTC')) active"))
        if not aliases:
            raise ValueError('No active development key aliases found for safe rotation')
        for alias in aliases:
            uuid.UUID(alias['id'])
            datetime.fromisoformat(alias['key_expire_dtimes'])
            if alias['uni_ident'] is not None and not all(c in '0123456789ABCDEFabcdef' for c in alias['uni_ident']):
                raise ValueError('Unexpected native key identifier')
        backup = ROOT / 'docker/local/key-rotation-backups' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8])
        backup.resolve().relative_to((ROOT / 'docker/local').resolve())
        backup.mkdir(parents=True)
        command(COMPOSE + ['stop', 'course-certify'])
        snapshot_complete = False
        try:
            shutil.copytree(ROOT / 'docker/local/certify-keys', backup / 'keystore')
            (backup / 'aliases.json').write_text(json.dumps(aliases, indent=2))
            with (backup / 'certify.dump').open('wb') as database:
                command(COMPOSE + ['exec', '-T', 'course-database', 'pg_dump', '-U', 'postgres',
                                  '-d', 'inji_certify', '-Fc', '--schema=certify'], stdout=database)
            snapshot_complete = True
            # Native identifiers include the date and collide on same-day rotation.
            # Preserve them in the backup; give each retired row an archival identifier.
            # NULL would trigger native auto-update to recreate the colliding date identifier.
            statements = ['BEGIN']
            for alias in aliases:
                retired = hashlib.sha1(('retired-development-key:' + alias['id']).encode()).hexdigest().upper()
                statements.append("UPDATE certify.key_alias SET uni_ident='" + retired + "', key_expire_dtimes=(now() AT TIME ZONE 'UTC') - interval '1 minute' WHERE id='" + alias['id'] + "'")
            query(';'.join(statements + ['COMMIT']))
            command(COMPOSE + ['start', 'course-certify'])
            command([sys.executable, 'runner/wait_ready.py', '--component', 'certify'] + (['--insecure'] if args.insecure else []))
            after = serials(args.insecure)
            if not after or not all(0 < serial and serial.bit_length() <= 159 for serial in after):
                raise ValueError('Native certificate generation did not produce positive bounded serials')
            result.update(performed=True, serials_after=after, prior_key_aliases_retained=len(aliases),
                          backup_directory=str(backup.relative_to(ROOT)))
        except Exception:
            # Restore the matching offline database and keystore snapshot together.
            # Keep the partially generated keystore for local diagnosis.
            command(COMPOSE + ['stop', 'course-certify'])
            if snapshot_complete:
                shutil.copytree(ROOT / 'docker/local/certify-keys', backup / 'failed-keystore')
                command(['docker', 'cp', str(backup / 'keystore') + '/.',
                         'inji-certify-final-course-certify-1:/home/inji/CERTIFY_PKCS12'])
                with (backup / 'certify.dump').open('rb') as database:
                    command(COMPOSE + ['exec', '-T', 'course-database', 'pg_restore', '--clean', '--if-exists',
                        '--no-owner', '-U', 'postgres', '-d', 'inji_certify'], stdin=database)
            command(COMPOSE + ['start', 'course-certify'])
            raise
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
