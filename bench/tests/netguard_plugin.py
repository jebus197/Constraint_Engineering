"""NETGUARD — diagnostic pytest plugin: record-and-raise on outbound attempts.

DIAGNOSTIC ONLY. This file is NOT a conftest.py and is NOT auto-loaded.
It does nothing unless explicitly enabled:

    PYTHONPATH=bench/tests python3 -m pytest bench/tests/ -p netguard_plugin ...

Optional env vars:
    NETGUARD_REPORT=/path/to/report.jsonl   where to append the ground-truth log
    NETGUARD_RECORD_ONLY=1                  record attempts but do NOT raise/fail
                                            (useful for a first pass that must not
                                            perturb control flow)

What it covers
--------------
* DNS resolution:      socket.getaddrinfo / socket.gethostbyname
* Raw sockets:         socket.socket.connect / connect_ex / socket.create_connection
  -> this single choke point catches requests, httpx, urllib, http.client,
     urllib3, the anthropic SDK, google-genai, openai, and anything else that
     speaks TCP from Python.
* Subprocess launch:   subprocess.Popen.__init__ (subprocess.run / call /
  check_output / check_call all route through Popen)

Loopback (localhost, 127.0.0.0/8, ::1) and AF_UNIX are allowed — they are not
outbound.

Two-tier subprocess policy
--------------------------
Tier BLOCK: the argv looks like it reaches a model/network endpoint
            (claude, codex, gemini, curl, wget, ... or any argv token
            containing a http(s):// URL).
Tier NOTE:  every other subprocess is recorded but permitted, so that
            legitimate local subprocess use (python, git status, sandboxes)
            is not misreported as a network call.

Why both raise AND fail-in-teardown
-----------------------------------
Several call sites in bench/immune_agents.py swallow broad exceptions
("fail-open"), e.g. `except (sp.TimeoutExpired, OSError, Exception)`. A raised
exception alone would therefore be silently absorbed and the test would still
pass, hiding the attempt. So:
  1. the guard raises `OutboundBlocked`, a *BaseException* subclass, so it
     escapes `except Exception:` handlers, and
  2. every attempt is recorded against the running test's nodeid, and the
     test is failed in teardown even if the exception was swallowed anyway.
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest


class OutboundBlocked(BaseException):
    """Raised when test code attempts an outbound call. BaseException on purpose."""


# --------------------------------------------------------------------------
# state
# --------------------------------------------------------------------------

_CURRENT_NODEID: Optional[str] = None
_ATTEMPTS: List[Dict[str, Any]] = []           # everything, whole session
_PER_TEST: Dict[str, List[Dict[str, Any]]] = {}  # blocking attempts only
_RECORD_ONLY = os.environ.get("NETGUARD_RECORD_ONLY") == "1"
# SOFT mode simulates "a machine with no network and no model CLI": attempts are
# recorded and denied, but with an ordinary catchable OSError (ConnectionError /
# FileNotFoundError) so the application's own offline fallbacks engage normally,
# and the test is NOT auto-failed in teardown. Use it to separate "this test
# genuinely asserts on live behaviour" from "this test merely touches the wire".
_SOFT = os.environ.get("NETGUARD_SOFT") == "1"
_REPORT_PATH = Path(
    os.environ.get("NETGUARD_REPORT", "netguard_report.jsonl")
).expanduser()

# argv[0] basenames that mean "this shells out to a model / the network"
_NETWORK_BINARIES = {
    "claude", "codex", "gemini", "chatgpt", "llm", "ollama",
    "curl", "wget", "http", "httpie", "nc", "ncat", "telnet", "ssh", "scp",
    "gh", "pip", "pip3", "npm", "npx", "brew",
}

_LOOPBACK_HOSTS = {
    "localhost", "127.0.0.1", "::1", "0.0.0.0", "", None,
    "localhost.localdomain", "ip6-localhost",
}


def _is_loopback(host: Any) -> bool:
    if host in _LOOPBACK_HOSTS:
        return True
    h = str(host)
    return h.startswith("127.") or h == "::1" or h.startswith("unix:")


def _record(kind: str, target: str, detail: str, blocking: bool) -> Dict[str, Any]:
    rec = {
        "nodeid": _CURRENT_NODEID or "<outside-test>",
        "kind": kind,
        "target": target,
        "detail": detail[:600],
        "blocking": blocking,
        "ts": time.time(),
    }
    _ATTEMPTS.append(rec)
    if blocking:
        _PER_TEST.setdefault(rec["nodeid"], []).append(rec)
    return rec


def _trip(kind: str, target: str, detail: str) -> None:
    _record(kind, target, detail, blocking=True)
    if _RECORD_ONLY:
        return
    if _SOFT:
        msg = f"NETGUARD(soft) denied {kind} -> {target}"
        if kind == "subprocess":
            raise FileNotFoundError(2, msg, target)
        raise ConnectionError(msg)
    raise OutboundBlocked(
        f"NETGUARD blocked {kind} -> {target} during {_CURRENT_NODEID}: {detail[:300]}"
    )


# --------------------------------------------------------------------------
# originals
# --------------------------------------------------------------------------

_orig_getaddrinfo = socket.getaddrinfo
_orig_gethostbyname = socket.gethostbyname
_orig_create_connection = socket.create_connection
_orig_sock_connect = socket.socket.connect
_orig_sock_connect_ex = socket.socket.connect_ex
_orig_popen_init = subprocess.Popen.__init__


def _guard_getaddrinfo(host, port, *a, **kw):
    if _is_loopback(host):
        return _orig_getaddrinfo(host, port, *a, **kw)
    _trip("dns", str(host), f"getaddrinfo({host!r}, {port!r})")
    return _orig_getaddrinfo(host, port, *a, **kw)


def _guard_gethostbyname(host):
    if _is_loopback(host):
        return _orig_gethostbyname(host)
    _trip("dns", str(host), f"gethostbyname({host!r})")
    return _orig_gethostbyname(host)


def _guard_create_connection(address, *a, **kw):
    host = address[0] if isinstance(address, tuple) else address
    if not _is_loopback(host):
        _trip("tcp", str(host), f"create_connection({address!r})")
    return _orig_create_connection(address, *a, **kw)


def _guard_connect(self, address):
    try:
        fam = self.family
    except Exception:
        fam = None
    if fam in (getattr(socket, "AF_INET", None), getattr(socket, "AF_INET6", None)):
        host = address[0] if isinstance(address, (tuple, list)) else address
        if not _is_loopback(host):
            _trip("tcp", str(host), f"socket.connect({address!r})")
    return _orig_sock_connect(self, address)


def _guard_connect_ex(self, address):
    try:
        fam = self.family
    except Exception:
        fam = None
    if fam in (getattr(socket, "AF_INET", None), getattr(socket, "AF_INET6", None)):
        host = address[0] if isinstance(address, (tuple, list)) else address
        if not _is_loopback(host):
            _trip("tcp", str(host), f"socket.connect_ex({address!r})")
    return _orig_sock_connect_ex(self, address)


def _argv_of(args) -> List[str]:
    if isinstance(args, (list, tuple)):
        return [str(x) for x in args]
    return [str(args)]


def _guard_popen_init(self, args, *a, **kw):
    argv = _argv_of(args)
    exe = os.path.basename(argv[0]) if argv else "<empty>"
    joined = " ".join(argv)
    url_like = "http://" in joined or "https://" in joined
    if exe in _NETWORK_BINARIES or url_like:
        _trip("subprocess", exe, joined)
    else:
        _record("subprocess", exe, joined, blocking=False)
    return _orig_popen_init(self, args, *a, **kw)


def _install() -> None:
    socket.getaddrinfo = _guard_getaddrinfo
    socket.gethostbyname = _guard_gethostbyname
    socket.create_connection = _guard_create_connection
    socket.socket.connect = _guard_connect
    socket.socket.connect_ex = _guard_connect_ex
    subprocess.Popen.__init__ = _guard_popen_init


def _uninstall() -> None:
    socket.getaddrinfo = _orig_getaddrinfo
    socket.gethostbyname = _orig_gethostbyname
    socket.create_connection = _orig_create_connection
    socket.socket.connect = _orig_sock_connect
    socket.socket.connect_ex = _orig_sock_connect_ex
    subprocess.Popen.__init__ = _orig_popen_init


# --------------------------------------------------------------------------
# pytest hooks
# --------------------------------------------------------------------------

def pytest_configure(config):
    _install()
    config._netguard_t0 = time.time()


def pytest_unconfigure(config):
    _uninstall()
    try:
        with _REPORT_PATH.open("a") as fh:
            for rec in _ATTEMPTS:
                fh.write(json.dumps(rec) + "\n")
    except OSError:
        pass


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_protocol(item, nextitem):
    global _CURRENT_NODEID
    _CURRENT_NODEID = item.nodeid
    yield
    _CURRENT_NODEID = None


@pytest.fixture(autouse=True)
def _netguard_autouse(request):
    """Fail the test in teardown if an outbound attempt was recorded.

    Necessary because fail-open handlers in bench/immune_agents.py swallow
    exceptions, so raising alone is not a reliable signal.
    """
    nodeid = request.node.nodeid
    before = len(_PER_TEST.get(nodeid, []))
    yield
    after = _PER_TEST.get(nodeid, [])
    if len(after) > before and not _RECORD_ONLY and not _SOFT:
        targets = sorted({r["target"] for r in after[before:]})
        pytest.fail(
            "NETGUARD: test attempted %d outbound call(s) -> %s"
            % (len(after) - before, ", ".join(targets)),
            pytrace=False,
        )


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    tr = terminalreporter
    tr.write_sep("=", "NETGUARD outbound attempt summary")
    blocking = [r for r in _ATTEMPTS if r["blocking"]]
    if not blocking:
        tr.write_line("no outbound attempts recorded")
    else:
        by_test: Dict[str, Dict[str, int]] = {}
        for r in blocking:
            by_test.setdefault(r["nodeid"], {})
            key = f"{r['kind']}:{r['target']}"
            by_test[r["nodeid"]][key] = by_test[r["nodeid"]].get(key, 0) + 1
        tr.write_line(f"{len(blocking)} attempt(s) across {len(by_test)} test(s):")
        for nodeid in sorted(by_test):
            parts = ", ".join(f"{k} x{v}" for k, v in sorted(by_test[nodeid].items()))
            tr.write_line(f"  {nodeid}  ->  {parts}")
    noted = [r for r in _ATTEMPTS if not r["blocking"]]
    if noted:
        execs: Dict[str, int] = {}
        for r in noted:
            execs[r["target"]] = execs.get(r["target"], 0) + 1
        tr.write_line(
            "local (permitted) subprocess launches: "
            + ", ".join(f"{k} x{v}" for k, v in sorted(execs.items(), key=lambda p: -p[1]))
        )
    tr.write_line(f"netguard report: {_REPORT_PATH}")
