"""Offline harness for the legal review: runs the reader CLI in-process with every
name lookup and connection recorded and refused (loopback allowed only when asked)."""
from __future__ import annotations

import io
import json
import os
import socket
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

SKILL = Path("/home/user/ux-research-qa-skills/skills/remorsearch-ux-qa")
sys.path.insert(0, str(SKILL))

for name in list(os.environ):
    if name.lower() in ("http_proxy", "https_proxy", "all_proxy") or "YOUTUBE" in name or name.startswith("REMORSEARCH_"):
        if name not in ("REMORSEARCH_ALLOW_PRIVATE", "REMORSEARCH_TEST_RESOLVE"):
            del os.environ[name]

NET_LOG: list = []
ALLOW_LOOPBACK = os.environ.get("HARNESS_ALLOW_LOOPBACK") == "1"
_real_gai = socket.getaddrinfo
_real_cc = socket.create_connection
_real_connect = socket.socket.connect


def _gai(host, *a, **k):
    NET_LOG.append(("getaddrinfo", str(host)))
    if ALLOW_LOOPBACK and str(host) in ("127.0.0.1", "localhost", "::1"):
        return _real_gai(host, *a, **k)
    raise socket.gaierror(f"harness: lookup of {host} refused")


def _cc(address, *a, **k):
    NET_LOG.append(("create_connection", str(address[0])))
    if ALLOW_LOOPBACK and str(address[0]) in ("127.0.0.1", "::1"):
        return _real_cc(address, *a, **k)
    raise OSError(f"harness: connection to {address[0]} refused")


def _connect(self, address):
    NET_LOG.append(("socket.connect", str(address)))
    if ALLOW_LOOPBACK and isinstance(address, tuple) and str(address[0]) in ("127.0.0.1", "::1"):
        return _real_connect(self, address)
    raise OSError(f"harness: connect to {address} refused")


socket.getaddrinfo = _gai
socket.create_connection = _cc
socket.socket.connect = _connect

from uxresearch.cli import main as cli_main  # noqa: E402


class _Clock:
    def __init__(self):
        import time
        self.t = time.time()

    def __call__(self):
        return self.t


CLOCK = _Clock()


def _sleep(seconds):
    CLOCK.t += seconds


def run(argv, stdin_text=None):
    """(exit code, stdout, stderr, network events made during the call)."""
    out, err = io.StringIO(), io.StringIO()
    before = len(NET_LOG)
    old_stdin = sys.stdin
    if stdin_text is not None:
        sys.stdin = io.StringIO(stdin_text)
    try:
        with redirect_stdout(out), redirect_stderr(err):
            code = cli_main(argv, clock=CLOCK, sleeper=_sleep, jitter=lambda: 0.0)
    finally:
        sys.stdin = old_stdin
    return code, out.getvalue(), err.getvalue(), NET_LOG[before:]


def summary(err_text):
    try:
        return json.loads(err_text.strip().splitlines()[-1])
    except Exception:
        return None
