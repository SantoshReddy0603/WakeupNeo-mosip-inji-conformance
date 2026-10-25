"""Identify the actual managed issuer image, without changing conformance outcomes."""
import json
import os
from pathlib import Path
from release_versions import configured_versions

ROOT = Path(__file__).resolve().parents[1]


def deployment_metadata(root=ROOT):
    metadata = {'versions': configured_versions(root), 'issuer_build': 'unidentified-external-deployment'}
    state = root / 'docker/isolated-state.json'
    if state.is_file():
        record = json.loads(state.read_text())
        reference = record.get('image_references', {}).get('course-certify')
        if reference:
            metadata.update(issuer_image=reference, issuer_image_id=record['images']['course-certify'],
                            issuer_build='stock-release' if reference.startswith('injistack/inji-certify-with-plugins:') else 'custom-image')
    elif os.getenv('CERTIFY_NATIVE_IMAGE'):
        metadata.update(issuer_image=os.environ['CERTIFY_NATIVE_IMAGE'], issuer_build='declared-custom-image')
    return metadata


def holder_binding_template_enabled(root=ROOT):
    image = deployment_metadata(root).get('issuer_image', '')
    return image in {'inji-harness/certify-binding:local', 'inji-harness/certify-metadata:local',
                     'inji-harness/certify-final:local', 'inji-harness/certify-positive:local'}
