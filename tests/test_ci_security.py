"""Security regression contracts for trusted live versus untrusted code CI."""
import shutil
from pathlib import Path
import pytest
from validate_workflows import check

ROOT = Path(__file__).resolve().parents[1]


def test_shipped_workflows_keep_live_gates_out_of_pull_requests():
    assert len(check()) == 2


@pytest.mark.parametrize('change', ['event', 'permissions', 'pin'])
def test_unsafe_workflow_changes_are_rejected(tmp_path, change):
    target = tmp_path / '.github/workflows'
    shutil.copytree(ROOT / '.github/workflows', target)
    file = target / 'full-stack-conformance.yml'
    text = file.read_text()
    if change == 'event':
        text = text.replace('workflow_dispatch:', 'pull_request:')
    elif change == 'permissions':
        text = text.replace('contents: read', 'contents: write')
    else:
        import re
        text = re.sub(r'actions/checkout@[a-f0-9]{40}', 'actions/checkout@main', text)
    file.write_text(text)
    with pytest.raises(ValueError):
        check(tmp_path)
