"""Read version configuration without importing credentials into the process."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMES = {'CERTIFY_VERSION', 'VERIFY_VERSION', 'VERIFY_UI_VERSION', 'VERIFY_SDK_VERSION'}


def configured_versions(root=ROOT):
    values = {}
    for path in (root / 'docker/versions.env', root / 'docker/.env'):
        if path.is_file():
            for line in path.read_text().splitlines():
                if '=' in line and not line.startswith('#'):
                    name, value = line.split('=', 1)
                    if name in NAMES and value:
                        values[name] = value
    values.update({name: os.environ[name] for name in NAMES if os.getenv(name)})
    return values


def verifier_sdk_version():
    return configured_versions()['VERIFY_SDK_VERSION']
