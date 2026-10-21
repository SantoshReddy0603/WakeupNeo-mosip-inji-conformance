"""Security regression contracts for trusted live versus untrusted code CI."""
import shutil
from pathlib import Path
import pytest
from validate_workflows import check

ROOT = Path(__file__).resolve().parents[1]


def test_shipped_workflows_keep_live_gates_out_of_pull_requests():
    assert len(check()) == 2


@pytest.mark.parametrize('change', ['event', 'permissions', 'pin', 'ancestry', 'prerelease', 'revision'])
def test_unsafe_workflow_changes_are_rejected(tmp_path, change):
    target = tmp_path / '.github/workflows'
    shutil.copytree(ROOT / '.github/workflows', target)
    file = target / 'full-stack-conformance.yml'
    text = file.read_text()
    if change == 'event':
        text = text.replace('workflow_dispatch:', 'pull_request:')
    elif change == 'permissions':
        text = text.replace('contents: read', 'contents: write')
    elif change == 'pin':
        import re
        text = re.sub(r'actions/checkout@[a-f0-9]{40}', 'actions/checkout@main', text)
    elif change == 'ancestry':
        text = text.replace('git merge-base --is-ancestor', 'echo')
    elif change == 'prerelease':
        text = text.replace('!github.event.release.prerelease', 'true')
    else:
        text = text.replace('${{ needs.authorize-revision.outputs.sha }}', '${{ github.ref }}')
    file.write_text(text)
    with pytest.raises(ValueError):
        check(tmp_path)
