"""Optional process-local Docker Desktop name resolution for WSL.

Only the transport address changes; request URLs, TLS hostnames and protocol
identifiers remain exactly those advertised by the real services.
"""
import os
import socket


def configure():
    if os.getenv('CONFORMANCE_RESOLVE_LOCAL') == 'true':
        original = socket.getaddrinfo
        socket.getaddrinfo = lambda host, *args, **kwargs: original(
            '127.0.0.1' if host == 'host.docker.internal' else host, *args, **kwargs)
