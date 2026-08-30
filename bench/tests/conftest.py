"""Suite-wide offline guarantee for bench/tests (installed 2026-07-31).

THE DEFECT THIS CLOSES
----------------------
Measured 2026-07-31: `python3 -m pytest bench/tests/` made real outbound calls
from 62 distinct tests, to 5 distinct external targets, and NONE of those tests
carried `pytest.mark.network`. The marker deselected 3 tests out of ~2,060, so
`-m "not network"` had never been an offline run. Three families:

  * claude CLI (Haiku classifier) — 17 tests, 93 dispatches, serialised behind
    a lock at 15 s each: up to ~1,395 s of Max-subscription model time per
    suite run, and outcomes that varied with the model's reply.
  * huggingface.co — 35 tests, via
    `bench/dm/_similarity.py::_get_embedding_model` loading all-MiniLM-L6-v2.
  * export.arxiv.org / api.openalex.org / api.semanticscholar.org — 10 tests,
    via the ouroboros cell's literature search.

Every one of the 62 passes with those calls denied. Not one asserted on live
model behaviour; they all reached the wire incidentally on the way to
assertions about local state.

THE THREE MECHANISMS HERE, AND WHY EACH IS NEEDED
-------------------------------------------------
1. HF_HUB_OFFLINE / TRANSFORMERS_OFFLINE, set at import time below.
   all-MiniLM-L6-v2 is already in the local huggingface cache; the network
   call was only the hub's revision check. Pinning offline keeps the embedding
   backend FULLY FUNCTIONAL from cache with zero network — so the 35
   huggingface offenders lose no coverage at all, rather than being pushed
   onto the lexical-Jaccard fallback. Verified: the model loads and encodes
   with every socket denied. On a machine with no cache the existing
   `except Exception -> lexical fallback` still applies, exactly as today.

2. CDSFL_UNDER_PYTEST=1, so `bench/live_dispatch_policy.live_dispatch_allowed()`
   is False. That closes the claude-CLI chain at its source, in one function,
   via a fail-open branch the code already had.

3. The socket / subprocess guard. This is the containment layer and the
   regression guard. It is what covers the scholarly-API family — whose source
   file `bench/ouroboros_cell.py` was under concurrent edit and could not be
   touched — and it is what will catch the NEXT dispatch site somebody adds,
   which mechanisms 1 and 2 cannot.

DENIAL IS SOFT BY DESIGN
------------------------
Sockets are denied with `ConnectionError`, DNS with `socket.gaierror`,
subprocess launch with `FileNotFoundError` — all ordinary, catchable `OSError`
subclasses. That is deliberate: it simulates a machine with no network and no
model CLI, so the application's own offline fallbacks engage and the suite
stays green (measured: 2055 passed / 2058 selected in 276 s). A guard that
raised something uncatchable would instead convert a well-handled absence into
a hard failure and tell us nothing new.

STRICT MODE — the regression guard
----------------------------------
    python3 -m pytest bench/tests/ --netguard-strict
    CDSFL_NETGUARD_STRICT=1 python3 -m pytest bench/tests/

additionally FAILS any test that *attempted* an outbound call, even if the
attempt was swallowed. That swallowing is real: 11 of the 62 offenders never
raised anything visible, because `bench/immune_agents.py` catches
`(sp.TimeoutExpired, OSError, Exception)`. They were caught only by recording.

Strict mode is opt-in rather than the default for one honest reason: the
ouroboros tests still attempt scholarly-API calls, and their source file was
off-limits in the window this guard was written. They are listed by name in
`KNOWN_OUTBOUND` below so strict mode is green TODAY and goes red on any NEW
offender. When the ouroboros literature search grows a seam for injecting a
fake client, delete its entries here and the exemption goes with it.

RUNNING THE LIVE PATH ON PURPOSE
--------------------------------
    CDSFL_ALLOW_LIVE_DISPATCH=1 python3 -m pytest bench/tests/test_exp29_integration.py

One switch: it disables this guard AND re-enables `_get_claude_cli()`. The
live path is disabled by default; it is never unreachable.
"""

from __future__ import annotations

import os
import socket
import subprocess
import sys
from typing import Any, Dict, List, Optional

import pytest

# ---------------------------------------------------------------------------
# Environment pinning — MUST happen at conftest import, before any test module
# imports huggingface_hub / sentence_transformers. Those libraries read these
# variables once, into module constants, at *their* import time.
# ---------------------------------------------------------------------------

OPT_IN_ENV = "CDSFL_ALLOW_LIVE_DISPATCH"
_LIVE = os.environ.get(OPT_IN_ENV) == "1"

if not _LIVE:
    os.environ["CDSFL_UNDER_PYTEST"] = "1"
    # Load models from the local cache; skip the hub revision check.
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    os.environ.setdefault("HF_DATASETS_OFFLINE", "1")
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")

_STRICT = (
    os.environ.get("CDSFL_NETGUARD_STRICT") == "1"
    or "--netguard-strict" in sys.argv
)

# Tests that still reach the wire, with the reason. Exempt in strict mode only.
# Every entry is a nodeid substring. Shrink this list; never grow it without
# writing down why here.
KNOWN_OUTBOUND: Dict[str, str] = {
    "test_ouroboros_query_quality.py":
        "OuroborosCell literature search hits arxiv/openalex/semanticscholar. "
        "bench/ouroboros_cell.py was under concurrent edit on 2026-07-31 and "
        "could not be given a fake-client seam. Calls are still DENIED here — "
        "these tests pass offline — they are merely exempt from the strict "
        "auto-fail.",
    "test_immune_agents.py::TestOuroborosCell":
        "same OuroborosCell literature search, exercised from the immune "
        "agent test module.",
    "test_ouroboros_loop_close.py::TestRunShadowCellsGating::"
    "test_reader_backend_defaults_to_haiku":
        "the ouroboros reader backend defaults to 'haiku' and spawns the "
        "claude CLI from a path that does NOT route through "
        "immune_agents._get_claude_cli, so the source-level gate cannot reach "
        "it. Same off-limits file. The spawn is denied here; the assertion "
        "(that the default is still 'haiku') does not depend on it.",
}


class _NetguardState:
    def __init__(self) -> None:
        self.current_nodeid: Optional[str] = None
        self.per_test: Dict[str, List[Dict[str, Any]]] = {}
        self.total = 0


_state = _NetguardState()

# argv[0] basenames that mean "this shells out to a model or the network".
# Everything else is recorded-but-permitted: the B-Cell verifiers legitimately
# spawn local python for sympy/z3/statsmodels, and blocking those would break
# real offline coverage.
_NETWORK_BINARIES = {
    "claude", "codex", "gemini", "chatgpt", "llm", "ollama",
    "curl", "wget", "http", "httpie", "nc", "ncat", "telnet", "ssh", "scp",
    "gh", "pip", "pip3", "npm", "npx", "brew",
}

_LOOPBACK_HOSTS = {
    "localhost", "127.0.0.1", "::1", "0.0.0.0", "",
    "localhost.localdomain", "ip6-localhost",
}


def _is_loopback(host: Any) -> bool:
    if host is None or host in _LOOPBACK_HOSTS:
        return True
    h = str(host)
    return h.startswith("127.") or h == "::1" or h.startswith("unix:")


def _record(kind: str, target: str, detail: str) -> None:
    _state.total += 1
    nodeid = _state.current_nodeid or "<outside-test>"
    _state.per_test.setdefault(nodeid, []).append(
        {"kind": kind, "target": target, "detail": detail[:400]}
    )


def _deny(kind: str, target: str, detail: str) -> None:
    """Record the attempt, then deny it with a realistic, catchable error."""
    _record(kind, target, detail)
    msg = (
        f"CDSFL netguard denied {kind} -> {target}. The test suite is offline "
        f"by default; set {OPT_IN_ENV}=1 to allow live calls."
    )
    if kind == "subprocess":
        raise FileNotFoundError(2, msg, target)
    if kind == "dns":
        raise socket.gaierror(socket.EAI_NONAME, msg)
    raise ConnectionError(msg)


# ---------------------------------------------------------------------------
# Patched entry points. socket.socket.connect is the single choke point for
# requests / httpx / urllib / http.client / urllib3 / the anthropic SDK /
# google-genai / openai and anything else that speaks TCP from Python.
# ---------------------------------------------------------------------------

_orig = {
    "getaddrinfo": socket.getaddrinfo,
    "gethostbyname": socket.gethostbyname,
    "create_connection": socket.create_connection,
    "connect": socket.socket.connect,
    "connect_ex": socket.socket.connect_ex,
    "popen_init": subprocess.Popen.__init__,
}


#: Endpoints that COST MONEY. This is the guard's real subject and it is
#: untouched by anything below.
#:
#: Founder ruling 2026-08-30: "the internet here is always enabled... ouroboros
#: outreach clearly only needs to cost money during a real experimental run.
#: Testing it here, or before an experimental run, clearly needs to cost nothing
#: more than my Max subscription."
#:
#: So the free window is a PAID DENY-LIST, not a free ALLOW-LIST. An allow-list
#: was tried first and was the wrong shape: literature retrieval follows a DOI
#: to whichever publisher happens to host the paper (measured: www.mdpi.com),
#: so the set of hosts it legitimately needs cannot be enumerated in advance.
#: Enumerating it would have produced a guard that passes by denying the very
#: fetch the test exists to exercise -- which is how these 3 tests spent 49 days
#: "passing" without ever running.
_PAID_HOSTS = frozenset({
    "openrouter.ai", "api.openai.com", "api.anthropic.com",
    "api.deepseek.com", "generativelanguage.googleapis.com",
    "api.groq.com", "api.mistral.ai", "api.cohere.ai",
})
#: Metered model CLIs. `claude` is DELIBERATELY absent: it runs on the Max
#: subscription, which the ruling above names as the permitted cost floor.
_PAID_BINARIES = frozenset({"codex", "gemini", "chatgpt", "llm"})

#: Open ONLY while a `free_network`-marked test is executing.
_free_window = False
#: IPs resolved during the window, so a follow-up connect() -- which sees an IP,
#: not a name -- is matched to the name that was checked.
_free_ips: set = set()


def _free_allowed(host) -> bool:
    """True inside a free_network test for any host that is not PAID.

    The money guard is unchanged: a paid endpoint is denied here exactly as it
    is outside the window.
    """
    if not _free_window:
        return False
    h = str(host).lower().rstrip(".").strip("'\"")
    if h.startswith("b'") or h.startswith('b"'):     # bytes hostname repr
        h = h[2:].rstrip("'\"")
    if h in _free_ips:
        return True
    return not any(h == d or h.endswith("." + d) for d in _PAID_HOSTS)


def set_free_window(on: bool) -> None:
    global _free_window
    _free_window = bool(on)
    if not on:
        _free_ips.clear()


def _guard_getaddrinfo(host, port, *a, **kw):
    if _free_allowed(host):
        res = _orig["getaddrinfo"](host, port, *a, **kw)
        for entry in res:                       # remember the resolved IPs
            try:
                _free_ips.add(str(entry[4][0]).lower())
            except Exception:                   # noqa: BLE001
                pass
        return res
    if _is_loopback(host):
        return _orig["getaddrinfo"](host, port, *a, **kw)
    _deny("dns", str(host), f"getaddrinfo({host!r}, {port!r})")


def _guard_gethostbyname(host):
    if _free_allowed(host):
        ip = _orig["gethostbyname"](host)
        _free_ips.add(str(ip).lower())
        return ip
    if _is_loopback(host):
        return _orig["gethostbyname"](host)
    _deny("dns", str(host), f"gethostbyname({host!r})")


def _guard_create_connection(address, *a, **kw):
    host = address[0] if isinstance(address, (tuple, list)) else address
    if _free_allowed(host):
        return _orig["create_connection"](address, *a, **kw)
    if _is_loopback(host):
        return _orig["create_connection"](address, *a, **kw)
    _deny("tcp", str(host), f"create_connection({address!r})")


def _guard_connect(self, address):
    if self.family in (socket.AF_INET, socket.AF_INET6):
        host = address[0] if isinstance(address, (tuple, list)) else address
        if not _is_loopback(host) and not _free_allowed(host):
            _deny("tcp", str(host), f"socket.connect({address!r})")
    return _orig["connect"](self, address)


def _guard_connect_ex(self, address):
    if self.family in (socket.AF_INET, socket.AF_INET6):
        host = address[0] if isinstance(address, (tuple, list)) else address
        if not _is_loopback(host) and not _free_allowed(host):
            _deny("tcp", str(host), f"socket.connect_ex({address!r})")
    return _orig["connect_ex"](self, address)


def _guard_popen_init(self, args, *a, **kw):
    argv = [str(x) for x in args] if isinstance(args, (list, tuple)) else [str(args)]
    exe = os.path.basename(argv[0]) if argv else "<empty>"
    joined = " ".join(argv)
    if _free_window and exe not in _PAID_BINARIES:
        # Inside a free_network test, a Max-plan CLI and a plain fetch are the
        # permitted cost floor. Metered CLIs stay denied.
        return _orig["popen_init"](self, args, *a, **kw)
    if exe in _NETWORK_BINARIES or "http://" in joined or "https://" in joined:
        _deny("subprocess", exe, joined)
    return _orig["popen_init"](self, args, *a, **kw)


def install_netguard() -> None:
    socket.getaddrinfo = _guard_getaddrinfo
    socket.gethostbyname = _guard_gethostbyname
    socket.create_connection = _guard_create_connection
    socket.socket.connect = _guard_connect
    socket.socket.connect_ex = _guard_connect_ex
    subprocess.Popen.__init__ = _guard_popen_init


def uninstall_netguard() -> None:
    socket.getaddrinfo = _orig["getaddrinfo"]
    socket.gethostbyname = _orig["gethostbyname"]
    socket.create_connection = _orig["create_connection"]
    socket.socket.connect = _orig["connect"]
    socket.socket.connect_ex = _orig["connect_ex"]
    subprocess.Popen.__init__ = _orig["popen_init"]


def netguard_attempts(nodeid: str) -> List[Dict[str, Any]]:
    """Attempts recorded against a nodeid. Used by the pinning tests."""
    return list(_state.per_test.get(nodeid, []))


def netguard_active() -> bool:
    return socket.socket.connect is _guard_connect


# ---------------------------------------------------------------------------
# pytest hooks
# ---------------------------------------------------------------------------

def pytest_addoption(parser):
    parser.addoption(
        "--netguard-strict", action="store_true", default=False,
        help="Fail any test that ATTEMPTS an outbound call, not just deny it.",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "allow_outbound: test is permitted to attempt outbound calls under "
        "--netguard-strict (it is still denied unless "
        "CDSFL_ALLOW_LIVE_DISPATCH=1).",
    )
    config.addinivalue_line(
        "markers",
        "free_network: reaches only FREE external services (arXiv, Semantic "
        "Scholar, OpenAlex, Unpaywall, doi.org). No API key, no metered call, "
        "no paid model. Runs by default; the guard opens a host allow-list for "
        "the duration of the test only.",
    )
    if not _LIVE:
        install_netguard()


def pytest_collection_modifyitems(config, items):
    """Skip `network`-marked tests while the guard is denying the network.

    A test that HONESTLY declares `@pytest.mark.network` is asking for the
    wire, and the guard is refusing to give it — leaving it selected would
    turn a correctly-labelled test into a spurious red. This is not an
    exclusion in the sense the fix was told to avoid: those tests were already
    outside every documented offline run (`-m "not network"` deselected exactly
    them), and they are one environment variable from running:

        CDSFL_ALLOW_LIVE_DISPATCH=1 python3 -m pytest bench/tests/ -m network

    `allow_outbound` opts out — that marker means "this test's subject IS the
    guard", so it must still run and see the denial.
    """
    if _LIVE:
        return
    skip = pytest.mark.skip(
        reason=f"netguard: outbound calls denied by default; "
               f"set {OPT_IN_ENV}=1 to run network tests"
    )
    for item in items:
        # `free_network` is NOT gated: it reaches only _FREE_HOSTS, which cost
        # nothing. `network` still means "this may cost money" and stays gated.
        if item.get_closest_marker("free_network"):
            continue
        if item.get_closest_marker("network") and not item.get_closest_marker(
            "allow_outbound"
        ):
            item.add_marker(skip)


def pytest_unconfigure(config):
    if not _LIVE:
        uninstall_netguard()


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_protocol(item, nextitem):
    _state.current_nodeid = item.nodeid
    # The free-host window is open ONLY for the duration of a test that
    # declares `free_network`, and closes in every exit path below.
    set_free_window(item.get_closest_marker("free_network") is not None)
    try:
        yield
    finally:
        set_free_window(False)
        _state.current_nodeid = None


def _is_known_outbound(nodeid: str) -> bool:
    return any(key in nodeid for key in KNOWN_OUTBOUND)


@pytest.fixture(autouse=True)
def _netguard(request):
    """Fail-in-teardown under strict mode.

    Teardown, not the raise, is the reliable signal: several call sites
    (bench/immune_agents.py:5048 among them) catch bare `Exception`, so a
    raised guard error is swallowed and the test passes with the attempt
    invisible. 11 of the 62 measured offenders behaved exactly that way.
    """
    nodeid = request.node.nodeid
    before = len(_state.per_test.get(nodeid, []))
    yield
    if _LIVE:
        return
    strict = _STRICT or request.config.getoption("--netguard-strict", default=False)
    if not strict:
        return
    if _is_known_outbound(nodeid) or request.node.get_closest_marker("allow_outbound"):
        return
    after = _state.per_test.get(nodeid, [])
    if len(after) > before:
        new = after[before:]
        targets = sorted({f"{r['kind']}:{r['target']}" for r in new})
        pytest.fail(
            f"netguard(strict): this test attempted {len(new)} outbound "
            f"call(s) -> {', '.join(targets)}. Tests must be offline. Either "
            f"inject a fake at the call site, or — if the call is genuinely "
            f"the thing under test — mark it "
            f"`@pytest.mark.network` and `@pytest.mark.allow_outbound`.",
            pytrace=False,
        )


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    if _LIVE:
        terminalreporter.write_sep(
            "=", f"netguard DISABLED ({OPT_IN_ENV}=1) — live calls were permitted",
        )
        return
    if not _state.total:
        return
    tr = terminalreporter
    tr.write_sep("=", "netguard: outbound attempts denied")
    for nodeid in sorted(_state.per_test):
        counts: Dict[str, int] = {}
        for r in _state.per_test[nodeid]:
            key = f"{r['kind']}:{r['target']}"
            counts[key] = counts.get(key, 0) + 1
        known = " [known]" if _is_known_outbound(nodeid) else ""
        tr.write_line(
            f"  {nodeid}{known}  ->  "
            + ", ".join(f"{k} x{v}" for k, v in sorted(counts.items()))
        )
    strict = _STRICT or config.getoption("--netguard-strict", default=False)
    tail = (
        "STRICT WAS ACTIVE: every attempting test above is on the "
        "KNOWN_OUTBOUND list or carries @pytest.mark.allow_outbound."
        if strict
        else "Run with --netguard-strict to fail on attempts."
    )
    tr.write_line(
        f"{_state.total} attempt(s) across {len(_state.per_test)} test(s); "
        f"all denied. {tail}"
    )
