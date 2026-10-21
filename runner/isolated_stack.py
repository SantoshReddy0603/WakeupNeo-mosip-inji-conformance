"""Fresh data-volume deployment using existing manifests; never touches historical projects.

Run from a fresh source extraction. Images/dependency caches may be reused, data and keys may not.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import yaml
import setup as local_setup

ROOT = Path(__file__).resolve().parents[1]


def merged(root, project, issuer_image):
    if not re.fullmatch(r'inji-clean-[a-z0-9-]{8,48}', project):
        raise ValueError('Use a unique inji-clean- project name with at least eight suffix characters')
    result = {'name': project, 'services': {}, 'networks': {'conformance': None}, 'volumes': {}}
    for name in ['docker-compose.yml', 'verify-final.compose.yml', 'certify-final.compose.yml', 'storage.compose.yml']:
        document = yaml.safe_load((root / 'docker' / name).read_text())
        for service, config in document['services'].items():
            if service in result['services']:
                raise ValueError('Duplicate service in source manifests')
            config['networks'] = ['conformance']
            if service == 'course-certify':
                config['image'] = issuer_image
            result['services'][service] = config
        result['volumes'].update(document.get('volumes', {}))
    return result


def docker(*args, capture=False):
    return subprocess.run(['docker', *args], check=True, text=True,
                          stdout=subprocess.PIPE if capture else None).stdout


def owned_volumes(project, expected):
    names = docker('volume', 'ls', '--filter', f'label=com.docker.compose.project={project}',
                   '--format', '{{.Name}}', capture=True).splitlines()
    for name in names:
        metadata = json.loads(docker('volume', 'inspect', name, capture=True))[0]
        labels = metadata.get('Labels') or {}
        logical = labels.get('com.docker.compose.volume')
        if (labels.get('com.docker.compose.project') != project or logical not in expected
                or name != f'{project}_{logical}'):
            raise ValueError('Refusing cleanup: volume ownership does not match isolated manifest')
    return names


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['up', 'down'])
    parser.add_argument('--project', required=True)
    parser.add_argument('--issuer-image', default='inji-harness/certify-positive:local')
    args = parser.parse_args()
    config = merged(ROOT, args.project, args.issuer_image)
    state = ROOT / 'docker/isolated-state.json'
    manifest = ROOT / 'docker/isolated.compose.yml'
    prefix = ['compose', '--env-file', str(ROOT / 'docker/.env'), '-p', args.project, '-f', str(manifest)]
    if args.action == 'up':
        if state.exists() or (ROOT / 'docker/.env').exists() or (ROOT / 'docker/local').exists():
            raise ValueError('Fresh deployment requires a source-only extraction with no prior local state')
        if owned_volumes(args.project, config['volumes']):
            raise ValueError('Project already has volumes; choose a fresh project name')
        if docker('ps', '-aq', '--filter', f'label=com.docker.compose.project={args.project}', capture=True).strip():
            raise ValueError('Project already has containers')
        local_setup.prepare()
        manifest.write_text(yaml.safe_dump(config, sort_keys=False), encoding='utf-8')
        images = {}
        for service, definition in config['services'].items():
            images[service] = json.loads(docker('image', 'inspect', definition['image'], capture=True))[0]['Id']
        state.write_text(json.dumps({'project': args.project, 'volumes': list(config['volumes']),
                                     'images': images, 'initial_volumes': []}, indent=2))
        docker(*prefix, 'config', '--quiet')
        docker(*prefix, 'up', '-d', '--no-build', '--pull', 'never')
        print(json.dumps({'project': args.project, 'volumes': owned_volumes(args.project, config['volumes']),
                          'images_reused': images}))
    else:
        record = json.loads(state.read_text())
        if record['project'] != args.project or set(record['volumes']) != set(config['volumes']):
            raise ValueError('Refusing cleanup of an unowned project')
        before = owned_volumes(args.project, record['volumes'])
        docker(*prefix, 'down', '--volumes', '--remove-orphans')
        after = owned_volumes(args.project, record['volumes'])
        if after:
            raise RuntimeError('Isolated volumes remain after cleanup')
        record['cleanup'] = {'removed_owned_volumes': before, 'remaining_volumes': after}
        state.write_text(json.dumps(record, indent=2))
        print(json.dumps(record['cleanup']))


if __name__ == '__main__':
    main()
