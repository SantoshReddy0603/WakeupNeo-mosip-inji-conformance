"""Check executable CI security boundaries; does not certify remote execution."""
from pathlib import Path
import re
import yaml

ROOT = Path(__file__).resolve().parents[1]


def check(root=ROOT):
    workflows = []
    for path in (root / '.github/workflows').glob('*.yml'):
        workflow = yaml.safe_load(path.read_text())
        events = workflow.get('on', workflow.get(True, {}))
        if workflow.get('permissions') != {'contents': 'read'}:
            raise ValueError(f'{path.name}: workflow permissions must be read-only')
        if 'pull_request_target' in events:
            raise ValueError(f'{path.name}: privileged PR event is forbidden')
        for name, job in workflow['jobs'].items():
            if job.get('continue-on-error'):
                raise ValueError(f'{name}: required jobs cannot hide failures')
            if 'self-hosted' in job.get('runs-on', []):
                if set(events) != {'workflow_dispatch'} or not job.get('environment'):
                    raise ValueError(f'{name}: self-hosted execution requires manual dispatch and a protected environment')
                if 'github.event.repository.default_branch' not in job.get('if', ''):
                    raise ValueError(f'{name}: self-hosted code must be from the default branch')
            for step in job['steps']:
                action = step.get('uses', '')
                if action and not re.fullmatch(r'actions/[a-z-]+@[0-9a-f]{40}', action):
                    raise ValueError(f'{path.name}: action must be pinned by commit: {action}')
                if action.startswith('actions/checkout@') and step.get('with', {}).get('persist-credentials') is not False:
                    raise ValueError('Checkout must not persist publication credentials')
                if step.get('continue-on-error'):
                    raise ValueError('Required steps cannot hide failures')
        workflows.append(path.name)
    if not workflows:
        raise ValueError('No workflows found')
    return workflows


if __name__ == '__main__':
    print('Validated workflow security boundaries:', ', '.join(check()))
