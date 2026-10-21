"""Bound local commands and reap their process trees after timeout/interruption."""
import os
import signal
import subprocess


def _terminate(process):
    """Best-effort tree cleanup; never replace the caller's original exception."""
    diagnostics = []
    descendants = set()
    if os.name == 'posix':
        try:
            snapshot = subprocess.run(['ps', '-eo', 'pid=,ppid='], capture_output=True,
                                      text=True, timeout=5, check=True)
            pairs = [tuple(map(int, line.split())) for line in snapshot.stdout.splitlines()]
            descendants = {process.pid}
            while True:
                expanded = descendants | {pid for pid, parent in pairs if parent in descendants}
                if expanded == descendants:
                    break
                descendants = expanded
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            diagnostics.append('Process-tree snapshot failed: ' + type(error).__name__)
        for sig in (signal.SIGTERM, signal.SIGKILL):
            try:
                os.killpg(process.pid, sig)
            except ProcessLookupError:
                pass
            except OSError as error:
                diagnostics.append('Process-group signal failed: ' + type(error).__name__)
            for pid in descendants - {process.pid}:
                try:
                    os.kill(pid, sig)
                except ProcessLookupError:
                    pass
                except OSError as error:
                    diagnostics.append('Descendant signal failed: ' + type(error).__name__)
            if sig == signal.SIGTERM:
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    pass
    else:
        try:
            subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           timeout=15, check=True)
        except (OSError, subprocess.SubprocessError) as error:
            diagnostics.append('Windows tree termination failed: ' + type(error).__name__)
    # Always terminate/reap the managed root, including when tree inspection fails.
    try:
        if process.poll() is None:
            process.kill()
        stdout, stderr = process.communicate(timeout=3)
        return stdout, stderr, diagnostics
    except (OSError, subprocess.SubprocessError) as error:
        diagnostics.append('Final process drain failed: ' + type(error).__name__)
        for pipe in (process.stdout, process.stderr):
            if pipe is not None:
                pipe.close()
        return None, None, diagnostics


def run(args, *, timeout=600, check=False, capture_output=False, **kwargs):
    if timeout <= 0:
        raise ValueError('Command timeout must be positive')
    if capture_output:
        if 'stdout' in kwargs or 'stderr' in kwargs:
            raise ValueError('capture_output conflicts with stdout/stderr')
        kwargs.update(stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if os.name == 'posix':
        kwargs['start_new_session'] = True
    process = subprocess.Popen(args, **kwargs)
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except (subprocess.TimeoutExpired, KeyboardInterrupt) as original:
        stdout, stderr, diagnostics = _terminate(process)
        if isinstance(original, subprocess.TimeoutExpired):
            # Match communicate(): timeout output remains bytes even in text mode.
            if stdout is not None:
                original.output = stdout.encode() if isinstance(stdout, str) else stdout
            if stderr is not None:
                original.stderr = stderr.encode() if isinstance(stderr, str) else stderr
        if diagnostics and hasattr(original, 'add_note'):
            original.add_note('; '.join(diagnostics))
        raise
    result = subprocess.CompletedProcess(args, process.returncode, stdout, stderr)
    if check:
        result.check_returncode()
    return result
