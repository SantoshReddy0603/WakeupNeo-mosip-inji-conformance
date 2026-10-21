"""Isolation preserves the real configuration, service graph and data initialization."""
from pathlib import Path
import pytest
from isolated_stack import merged, owned_volumes

ROOT = Path(__file__).resolve().parents[1]


def test_isolated_stack_has_fresh_owned_volumes_and_shared_network():
    config = merged(ROOT, 'inji-clean-test1234', 'inji-harness/certify-positive:local')
    assert len(config['services']) == 12
    assert len(config['volumes']) == 5
    assert config['networks'] == {'conformance': None}
    assert all(item['networks'] == ['conformance'] for item in config['services'].values())
    assert config['services']['course-certify']['image'] == 'inji-harness/certify-positive:local'
    assert './certify-final-init:/docker-entrypoint-initdb.d:ro' in config['services']['course-database']['volumes']
    assert config['services']['conformance-server']['environment']['FINTECHLABS_DEVMODE'] == 'true'


@pytest.mark.parametrize('project', ['inji-certify-final', 'inji-clean-short', '../historical', ''])
def test_existing_or_unsafe_project_names_are_rejected(project):
    with pytest.raises(ValueError):
        merged(ROOT, project, 'unused')


def test_cleanup_refuses_volume_with_wrong_project_label(monkeypatch):
    import json
    import isolated_stack
    name = 'inji-clean-test1234_course-data'
    def inspect(*args, **kwargs):
        if args[0] == 'volume' and args[1] == 'ls':
            return name + '\n'
        return json.dumps([{'Labels': {'com.docker.compose.project': 'historical',
                                       'com.docker.compose.volume': 'course-data'}}])
    monkeypatch.setattr(isolated_stack, 'docker', inspect)
    with pytest.raises(ValueError, match='ownership'):
        owned_volumes('inji-clean-test1234', ['course-data'])
