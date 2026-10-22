"""Build/test the native source fix; never change suite requests or validation."""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile
import importlib.util
from process_control import run
from preflight import validate_java

ROOT = Path(__file__).resolve().parents[1]
PIN = '8fdf71656979a72fa8263766d4dec3cc25127b76'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / 'docker/local/native-certify-source',
                        help='Pinned source cache; each build uses a fresh checkout and the selected patches')
    parser.add_argument('--dpop', action='store_true', help='Build the native sender-constrained token validator too')
    parser.add_argument('--holder-binding', action='store_true', help='Also embed the validated holder public key in SD-JWT cnf.jwk')
    parser.add_argument('--signed-metadata', action='store_true', help='Also sign issuer metadata using the native issuer key manager')
    parser.add_argument('--credential-errors', action='store_true', help='Build all Final-profile fixes including credential selector/error handling')
    parser.add_argument('--positive-serial', action='store_true', help='Also rebuild the native key manager with positive bounded certificate serials')
    parser.add_argument('--keymanager-source', type=Path, help='Optional pinned key-manager source cache')
    args = parser.parse_args()
    errors=validate_java(21)
    if errors:raise ValueError('; '.join(errors))
    args.credential_errors = args.credential_errors or args.positive_serial
    args.signed_metadata = args.signed_metadata or args.credential_errors
    args.holder_binding = args.holder_binding or args.signed_metadata
    args.dpop = args.dpop or args.holder_binding
    source = args.source.resolve()
    if not (source / '.git').exists():
        source.parent.mkdir(parents=True, exist_ok=True)
        run(['git', 'clone', 'https://github.com/inji/inji-certify.git', str(source)], check=True)
        run(['git', 'checkout', PIN], cwd=source, check=True)
    current = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=source, text=True).strip()
    if current != PIN:
        raise ValueError('Native source must match the tested release commit')
    # Overlapping patches cannot safely be re-applied to a previously
    # patched checkout. Clone the pinned commit for every build/profile instead.
    with tempfile.TemporaryDirectory(prefix='inji-native-build-') as temporary:
        build_profile(args,source,Path(temporary)/'source')


def build_profile(args,source,clean_source):
    run(['git', 'clone', '--no-hardlinks', str(source), str(clean_source)], check=True)
    source = clean_source
    for name in ['extensions.patch'] + (['dpop.patch'] if args.dpop else []) + (['holder-binding.patch'] if args.holder_binding else []) + (['signed-metadata.patch'] if args.signed_metadata else []) + (['credential-errors.patch'] if args.credential_errors else []):
        patch = ROOT / 'docker/native-certify' / name
        run(['git', 'apply', '--check', str(patch)], cwd=source, check=True)
        run(['git', 'apply', str(patch)], cwd=source, check=True)
    module = 'certify-service' if args.dpop else 'certify-core'
    tests = 'CredentialRequestExtensionTest' + (',DpopProofValidatorTest,AccessTokenValidationFilterTest' if args.dpop else '')
    if args.holder_binding:
        tests += ',SDJwtHolderBindingTest'
    if args.signed_metadata:
        tests += ',SignedIssuerMetadataServiceTest'
    if args.credential_errors:
        tests += ',CredentialSelectorTest,CredentialErrorResponseTest'
    run(['mvn', '-B', '-s', str(ROOT / 'integration/maven-settings.xml'), '-pl', module, '-am',
        'package', '-Dtest=' + tests, '-Dsurefire.failIfNoSpecifiedTests=false',
        '-Dgpg.skip=true', '-Dmaven.javadoc.skip=true', '-Dsource.skip=true'],
        cwd=source, check=True)
    build = ROOT / 'docker/local/native-certify-build'
    build.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source / (module + '/target/' + module + '-1.0.0-alpha.1.jar'),
                    build / ('certify-service.jar' if args.dpop else 'certify-core.jar'))
    if args.positive_serial:
        from build_native_keymanager import build as build_keymanager
        library = build_keymanager(args.keymanager_source)
        spec = importlib.util.spec_from_file_location('native_library', ROOT / 'docker/native-keymanager/replace_library.py')
        replacement = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(replacement)
        rebuilt = build / 'certify-positive.jar'
        replacement.replace(build / 'certify-service.jar', library, rebuilt)
        shutil.copyfile(rebuilt, build / 'certify-service.jar')
    shutil.copyfile(ROOT / 'docker/native-certify/replace_core.py', build / 'replace_core.py')
    run(['docker', 'build', '-f', str(ROOT / 'docker/native-certify' / ('Dockerfile.dpop' if args.dpop else 'Dockerfile')),
                    '-t', 'inji-harness/certify-positive:local' if args.positive_serial else 'inji-harness/certify-final:local' if args.credential_errors else 'inji-harness/certify-metadata:local' if args.signed_metadata else 'inji-harness/certify-binding:local' if args.holder_binding else 'inji-harness/certify-dpop:local' if args.dpop else 'inji-harness/certify-native:local', str(build)], check=True)

if __name__ == '__main__':
    main()
