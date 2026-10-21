"""Production releases execute once; drafts, prereleases and PRs never execute live."""
import pytest
from release_policy import eligible


def event(**release):
    return {'repository': {'default_branch': 'main'}, 'action': 'published',
            'release': {'draft': False, 'prerelease': False, 'tag_name': 'v1', **release}}


def test_production_release_and_default_dispatch():
    assert eligible('release', event(), 'refs/tags/v1')
    assert eligible('workflow_dispatch', event(), 'refs/heads/main')


@pytest.mark.parametrize('name,payload,ref', [
    ('release', event(draft=True), 'refs/tags/v1'),
    ('release', event(prerelease=True), 'refs/tags/v1'),
    ('release', {**event(), 'action': 'created'}, 'refs/tags/v1'),
    ('release', event(), 'refs/tags/other'),
    ('release', event(tag_name=''), 'refs/tags/'),
    ('push', event(), 'refs/tags/v1'),
    ('pull_request', event(), 'refs/pull/1/merge'),
    ('workflow_dispatch', event(), 'refs/heads/ci/stage-18'),
    ('release', {}, 'refs/tags/v1'),
])
def test_ineligible_events(name, payload, ref):
    assert not eligible(name, payload, ref)
