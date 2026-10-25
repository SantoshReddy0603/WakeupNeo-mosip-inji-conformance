"""Linux operator tool for one ephemeral GitHub runner job; never publishes releases.

Registration uses a short-lived local token file with owner-only permissions.
Each subsequent registration needs a new token instead of retained access."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import re
import shutil
import signal
import socket
import subprocess
import sys
import urllib.request

NODE_OPTIONS = '--no-network-family-autoselection --dns-result-order=ipv4first'
PORTS = (8443, 8445, 8446, 9000, 9001)


def repository_url(value=None):
    """Restrict runner registration to an explicit HTTPS GitHub repository URL."""
    value = value or os.getenv('INJI_GITHUB_REPOSITORY', '')
    if not re.fullmatch(r'https://github\.com/[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+/?', value):
        raise ValueError('Set --repository or INJI_GITHUB_REPOSITORY to an HTTPS GitHub repository URL')
    return value.rstrip('/')


def command(args, cwd=None, env=None, timeout=30):
    """Capture bounded dependency checks and propagate failed subprocesses."""
    return subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True,
                          timeout=timeout, check=True).stdout.strip()


def registration(directory, repository=None):
    """Check that an existing runner registration belongs to the selected repository."""
    repository = repository_url(repository)
    marker = directory / '.runner'
    if not marker.exists():
        if (directory / '.credentials').exists():
            raise ValueError('Orphan credentials: use GitHub removal/recovery before registration')
        return None
    data = json.loads(marker.read_text(encoding='utf-8-sig'))
    if data.get('gitHubUrl', '').rstrip('/').lower() != repository.rstrip('/').lower():
        raise ValueError('Runner belongs to a different repository')
    if data.get('ephemeral') is not True:
        raise ValueError('This procedure requires an ephemeral runner')
    if not (directory / '.credentials').is_file():
        raise ValueError('Registration is incomplete; recover it through GitHub runner settings')
    return data


def busy_ports():
    """Detect listeners that would conflict with the isolated development stack."""
    occupied = []
    for port in PORTS:
        with socket.socket() as sock:
            try:
                sock.bind(('127.0.0.1', port))
            except OSError:
                occupied.append(port)
    return occupied


def preflight(directory, require_registration=True, repository=None):
    """Check dependencies, resources, networking and registration before privileged execution."""
    repository = repository_url(repository)
    checks = {}
    errors = []
    def check(name, callback):
        try:
            checks[name] = callback()
        except Exception as exc:
            # Never include subprocess stderr, HTTP authorization or token text.
            checks[name] = False
            errors.append(name + ': ' + type(exc).__name__)
    def dependencies():
        required = ['git', 'java', 'javac', 'mvn', 'docker', 'openssl', 'bash']
        missing = [name for name in required if not shutil.which(name)]
        if missing:
            raise ValueError('Missing required dependencies')
        if not command(['javac', '-version']).startswith('javac 21.'):
            raise ValueError('Java 21 required')
        if 'Apache Maven 3.8.7' not in command(['mvn', '-version']):
            raise ValueError('Use the validated Maven 3.8.7 baseline')
        command(['docker', 'compose', 'version'])
        return required
    def docker():
        value = command(['docker', 'info', '--format', '{{.OSType}}'])
        if value.strip() != 'linux':
            raise ValueError('Managed stack requires a Linux Docker engine')
        return value
    def resources():
        memory = int(Path('/proc/meminfo').read_text().split('MemTotal:')[1].split()[0]) // 1024
        disk = shutil.disk_usage(directory).free // (1024 ** 3)
        if memory < 6144 or disk < 30:
            raise ValueError('At least 6 GiB Linux memory and 30 GiB disk required; 8 GiB+ recommended')
        return {'linux_memory_mib': memory, 'free_disk_gib': disk}
    def ports():
        occupied = busy_ports()
        if occupied:
            checks['occupied_ports'] = occupied
            raise ValueError('Managed stack ports occupied; do not stop unrelated services')
        return list(PORTS)
    def network():
        node = directory / 'externals/node24/bin/node'
        env = dict(os.environ, NODE_OPTIONS=NODE_OPTIONS)
        command([str(node), '-e', "require('https').get('https://results-receiver.actions.githubusercontent.com/',r=>{r.resume();process.exit(0)}).on('error',()=>process.exit(1))"],
                env=env, timeout=40)
        # The GitLab landing page may reject automated browsers even when the
        # repository's actual Git transport works. Check the required service.
        remote = command(['git', 'ls-remote', 'https://gitlab.com/openid/conformance-suite.git', 'HEAD'], timeout=40)
        if not remote or len(remote.split()[0]) != 40:
            raise ValueError('Official suite Git source unavailable')
        for url in ['https://github.com', 'https://api.github.com',
                    'https://repo.maven.apache.org/maven2/', 'https://pypi.org/simple/']:
            with urllib.request.urlopen(url, timeout=20) as response:
                if response.status >= 400:
                    raise ValueError('Dependency endpoint unavailable')
        return 'TLS, official suite Git transport and scoped Node IPv4 configuration verified'
    def registered():
        value = registration(directory, repository)
        if value is None and require_registration:
            raise ValueError('Not registered')
        return {'registered': value is not None, 'repository': repository,
                'repository_access': 'Verified by runner connection when started; metadata alone is insufficient'}
    check('dependencies', dependencies)
    check('docker', docker)
    check('resources', resources)
    check('ports', ports)
    check('network', network)
    check('registration', registered)
    return {'checks': checks, 'errors': errors, 'ready': not errors}


def read_token(path):
    """Read a short-lived registration token only from an owner-only regular file."""
    if path.is_symlink() or not path.is_file() or path.stat().st_uid != os.getuid() or path.stat().st_mode & 0o077:
        raise ValueError('Token must be an owner-only regular file (chmod 600)')
    token = path.read_text().strip()
    if not token or any(c.isspace() for c in token):
        raise ValueError('Invalid registration token file')
    return token


def register(directory, token_file, repository=None):
    """Create a nonpersistent runner registration without retaining its token file."""
    repository = repository_url(repository)
    if registration(directory, repository) is not None:
        raise ValueError('Already registered; refusing duplicate registration')
    token = read_token(token_file)
    result = subprocess.run([str(directory / 'config.sh'), '--url', repository,
        '--token', token, '--name', 'mosip-inji-approved-local', '--labels', 'inji-conformance',
        '--work', '_work', '--unattended', '--ephemeral'], cwd=directory,
        text=True, capture_output=True, timeout=120)
    # Registration output can contain sensitive values. Print only the exit code.
    if result.returncode:
        raise RuntimeError('Registration failed (exit ' + str(result.returncode) + '); inspect GitHub settings')
    token_file.unlink()
    return registration(directory, repository)


def main(argv=None):
    """Run one explicitly approved ephemeral listener and leave service cleanup to its workflow."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['preflight', 'status', 'start'])
    parser.add_argument('--runner-dir', required=True, type=Path)
    parser.add_argument('--repository', help='HTTPS GitHub repository URL; defaults to INJI_GITHUB_REPOSITORY')
    parser.add_argument('--registration-token-file', type=Path)
    parser.add_argument('--owner-approved', action='store_true', help='Operator attests approval for this single job')
    args = parser.parse_args(argv)
    try:
        repository = repository_url(args.repository)
    except ValueError as exc:
        parser.error(str(exc))
    directory = args.runner_dir.resolve(strict=True)
    if not (directory / 'run.sh').is_file() or not (directory / 'config.sh').is_file():
        parser.error('Expected an extracted official Linux runner directory')
    # One lock covers registration and the entire foreground listener lifetime.
    with (directory / '.inji-operator.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print('An operator-managed runner is already active; no duplicate started')
            return 2
        active = [p for p in Path('/proc').glob('[0-9]*/cwd') if _listener_in(p, directory)]
        if active:
            print('An existing Runner.Listener uses this directory; no duplicate started')
            return 2
        if args.action == 'status':
            print(json.dumps({'registered': registration(directory, repository) is not None,
                              'running': False, 'service_installed_by_this_tool': False}))
            return 0
        result = preflight(directory, require_registration=args.action != 'start', repository=repository)
        print(json.dumps(result, indent=2))
        if not result['ready']:
            return 2
        if args.action == 'preflight':
            return 0 if registration(directory, repository) is not None else 2
        if not args.owner_approved:
            parser.error('Start requires explicit owner approval for this job (--owner-approved)')
        if registration(directory, repository) is None:
            if args.registration_token_file is None:
                parser.error('Unregistered: supply a short-lived owner-only registration token file')
            register(directory, args.registration_token_file, repository)
        elif args.registration_token_file is not None:
            parser.error('Already registered; do not supply another token')
        env = dict(os.environ, NODE_OPTIONS=NODE_OPTIONS)
        child = subprocess.Popen([str(directory / 'run.sh'), '--once'], cwd=directory,
                                 env=env, start_new_session=True)
        def stop(_signum, _frame):
            if child.poll() is None:
                os.killpg(child.pid, signal.SIGTERM)
        signal.signal(signal.SIGINT, stop)
        signal.signal(signal.SIGTERM, stop)
        try:
            code = child.wait()
        finally:
            if child.poll() is None:
                stop(None, None)
                child.wait(timeout=30)
        print(json.dumps({'listener_exit': code, 'still_registered': (directory / '.runner').exists(),
                          'cleanup': 'Workflow owns service cleanup; this tool never deletes Docker resources'}))
        return code


def _listener_in(cwd, directory):
    try:
        return cwd.resolve() == directory and b'Runner.Listener' in (cwd.parent / 'cmdline').read_bytes()
    except (OSError, RuntimeError):
        return False


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError):
        print('Runner operation failed. No credentials printed; check registration, dependencies and network.', file=sys.stderr)
        raise SystemExit(2)
