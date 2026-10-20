"""Install the verified Maven baseline without relying on hosted image defaults."""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
from urllib.request import urlopen

VERSION = '3.8.7'
SHA512 = '21c2be0a180a326353e8f6d12289f74bc7cd53080305f05358936f3a1b6dd4d91203f4cc799e81761cf5c53c5bbe9dcc13bdb27ec8f57ecf21b2f9ceec3c8d27'
URL = f'https://archive.apache.org/dist/maven/maven-3/{VERSION}/binaries/apache-maven-{VERSION}-bin.tar.gz'


def install(directory):
    directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    with urlopen(URL, timeout=120) as response:
        archive = response.read()
    if hashlib.sha512(archive).hexdigest() != SHA512:
        raise ValueError('Maven distribution checksum mismatch; refusing to install')
    with tempfile.TemporaryFile() as file:
        file.write(archive)
        file.seek(0)
        with tarfile.open(fileobj=file, mode='r:gz') as package:
            package.extractall(directory, filter='data')
    home = directory / ('apache-maven-' + VERSION)
    executable = home / 'bin/mvn'
    subprocess.run([str(executable), '--version'], check=True)
    if os.getenv('GITHUB_PATH'):
        with open(os.environ['GITHUB_PATH'], 'a') as file:
            file.write(str(home / 'bin') + '\n')
        with open(os.environ['GITHUB_ENV'], 'a') as file:
            file.write('MAVEN_HOME=' + str(home) + '\n')
    return home


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, required=True)
    print(install(parser.parse_args().directory))
