"""Operator safety contracts; no real runner is registered by these fixtures."""
import json
import os
from pathlib import Path
import pytest

pytestmark = pytest.mark.skipif(os.name != 'posix', reason='WSL/Linux operator tool')
if os.name == 'posix':
    from local_runner import REPOSITORY, registration, read_token, register, NODE_OPTIONS


def test_registration_is_repository_bound_and_ephemeral(tmp_path):
    assert registration(tmp_path) is None
    data = {'gitHubUrl': REPOSITORY, 'ephemeral': True}
    (tmp_path / '.runner').write_text(json.dumps(data), encoding='utf-8-sig')
    (tmp_path / '.credentials').write_text('controlled fixture')
    assert registration(tmp_path)['ephemeral']
    for update in [{'gitHubUrl': 'https://github.com/other/repo'}, {'ephemeral': False}]:
        (tmp_path / '.runner').write_text(json.dumps({**data, **update}))
        with pytest.raises(ValueError):
            registration(tmp_path)


def test_incomplete_registration_is_not_silently_replaced(tmp_path):
    (tmp_path / '.credentials').write_text('controlled fixture')
    with pytest.raises(ValueError, match='Orphan'):
        registration(tmp_path)


def test_token_requires_private_regular_file(tmp_path):
    token = tmp_path / 'token'
    token.write_text('controlled-fixture')
    token.chmod(0o600)
    assert read_token(token) == 'controlled-fixture'
    token.chmod(0o644)
    with pytest.raises(ValueError):
        read_token(token)
    token.chmod(0o600)
    link = tmp_path / 'link'
    link.symlink_to(token)
    with pytest.raises(ValueError):
        read_token(link)


def test_registered_runner_refuses_duplicate_before_reading_token(tmp_path):
    (tmp_path / '.runner').write_text(json.dumps({'gitHubUrl': REPOSITORY, 'ephemeral': True}))
    (tmp_path / '.credentials').write_text('controlled fixture')
    with pytest.raises(ValueError, match='Already'):
        register(tmp_path, tmp_path / 'nonexistent')


def test_network_settings_preserve_tls_and_tested_ipv4():
    assert NODE_OPTIONS == '--no-network-family-autoselection --dns-result-order=ipv4first'
    assert 'tls' not in NODE_OPTIONS.lower()


def test_other_users_proc_entries_do_not_break_status():
    from local_runner import _listener_in
    class InaccessibleProcEntry:
        def resolve(self):
            raise PermissionError('Controlled inaccessible proc fixture')
    assert _listener_in(InaccessibleProcEntry(), Path('/fixture')) is False


def test_active_operator_lock_prevents_second_start(tmp_path):
    import fcntl
    from local_runner import main
    for name in ['run.sh', 'config.sh']:
        (tmp_path / name).write_text('# controlled fixture')
    with (tmp_path / '.inji-operator.lock').open('a') as first:
        fcntl.flock(first, fcntl.LOCK_EX | fcntl.LOCK_NB)
        assert main(['start', '--runner-dir', str(tmp_path), '--owner-approved']) == 2


@pytest.mark.parametrize('success', [True, False])
def test_registration_token_lifecycle_and_redaction(tmp_path, monkeypatch, capsys, success):
    import local_runner
    from types import SimpleNamespace
    token = tmp_path / 'token'
    token.write_text('controlled-token-canary')
    token.chmod(0o600)
    def configure(args, **kwargs):
        assert '--ephemeral' in args and 'controlled-token-canary' in args
        if success:
            (tmp_path / '.runner').write_text(json.dumps({'gitHubUrl': REPOSITORY, 'ephemeral': True}))
            (tmp_path / '.credentials').write_text('controlled fixture')
        return SimpleNamespace(returncode=0 if success else 1, stdout='controlled-token-canary')
    monkeypatch.setattr(local_runner.subprocess, 'run', configure)
    if success:
        assert register(tmp_path, token)['ephemeral']
        assert not token.exists()
    else:
        with pytest.raises(RuntimeError) as exc:
            register(tmp_path, token)
        assert 'controlled-token-canary' not in str(exc.value)
        assert token.exists()
    assert 'controlled-token-canary' not in capsys.readouterr().out
