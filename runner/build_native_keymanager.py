"""Build the pinned native key-manager certificate-generation fix."""
import argparse
from pathlib import Path
import subprocess
import tempfile
import shutil
import hashlib
import json
import uuid
from process_control import run
from preflight import validate_java

ROOT = Path(__file__).resolve().parents[1]
PIN = '7c53fc9d3c972347a603fd66e9ab0812db60ccec'

def build(source=None, output_dir=None):
    errors=validate_java(21)
    if errors:raise ValueError('; '.join(errors))
    source = Path(source or ROOT / 'docker/local/native-keymanager-source').resolve()
    if not (source / '.git').exists():
        source.parent.mkdir(parents=True, exist_ok=True)
        run(['git', 'clone', '--depth', '1', '--branch', 'v1.4.0',
                        'https://github.com/mosip/keymanager.git', str(source)], check=True)
    if run(['git', 'rev-parse', 'HEAD'], cwd=source, text=True, capture_output=True, check=True).stdout.strip() != PIN:
        raise ValueError('Key-manager source must match the tested 1.4.0 commit')
    output = Path(output_dir or ROOT/'docker/local/native-keymanager-build'/uuid.uuid4().hex).resolve()
    output.mkdir(parents=True, exist_ok=False)
    patch = ROOT/'docker/native-keymanager/positive-serial.patch'
    # On WSL, the default temporary directory is Linux ext4. Do not package a
    # Windows-mounted working tree: Maven performs thousands of metadata reads.
    with tempfile.TemporaryDirectory(prefix='inji-native-keymanager-') as temporary:
        clean = Path(temporary)/'source'
        run(['git', 'clone', '--no-hardlinks', str(source), str(clean)], check=True)
        run(['git', 'apply', str(patch)], cwd=clean, check=True)
        command=['mvn', '-B', '-s', str(ROOT/'integration/maven-settings.xml'), '-f', str(clean/'kernel/pom.xml'),
            '-pl', 'kernel-keymanager-service', '-am', 'package', '-Dtest=CertificateSerialNumberTest',
            '-Dsurefire.failIfNoSpecifiedTests=false', '-Dgpg.skip=true', '-Dmaven.javadoc.skip=true', '-Dsource.skip=true']
        try:
            run(command, check=True)
            artifact=output/'kernel-keymanager-service-1.4.0-lib.jar'
            shutil.copyfile(clean/'kernel/kernel-keymanager-service/target'/artifact.name, artifact)
            (output/'build-provenance.json').write_text(json.dumps({'source_pin':PIN,
                'patch_sha256':hashlib.sha256(patch.read_bytes()).hexdigest(),
                'artifact_sha256':hashlib.sha256(artifact.read_bytes()).hexdigest(),
                'command':command,'exit_status':0,'scratch_directory':str(clean),
                'official_conformance_result':False},indent=2))
        finally:
            for path in clean.glob('kernel/*/target/surefire-reports'):
                shutil.copytree(path,output/'test-results'/path.parents[1].name,dirs_exist_ok=True)
    return artifact

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--output-dir',type=Path,help='New output directory for the library, tests and provenance')
    args = parser.parse_args()
    print(build(args.source,args.output_dir))
