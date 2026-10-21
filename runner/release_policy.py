"""Fail-closed event policy; ancestry is additionally checked by the hosted job."""
import json
import os
import re


def eligible(event_name, payload, ref):
    branch = payload.get('repository', {}).get('default_branch')
    if not branch:
        return False
    if event_name == 'workflow_dispatch':
        return ref == f'refs/heads/{branch}'
    release = payload.get('release', {})
    return (event_name == 'release' and payload.get('action') == 'published'
            and release.get('draft') is False and release.get('prerelease') is False
            and bool(release.get('tag_name'))
            and ref == f"refs/tags/{release['tag_name']}")


if __name__ == '__main__':
    with open(os.environ['GITHUB_EVENT_PATH'], encoding='utf-8') as stream:
        event = json.load(stream)
    if not eligible(os.environ['GITHUB_EVENT_NAME'], event, os.environ['GITHUB_REF']):
        raise SystemExit('Live conformance requires a published production release or default-branch dispatch')
    if not re.fullmatch(r'[0-9a-f]{40}', os.environ['GITHUB_SHA']):
        raise SystemExit('Expected immutable GitHub commit SHA')
