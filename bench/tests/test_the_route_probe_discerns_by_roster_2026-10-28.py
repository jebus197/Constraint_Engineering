#!/usr/bin/env python3
r"""The route probe reads the roster, so free and paid need no mode flag.

HIS POLICY, 2026-10-28: check the Claude CLI and all other model logins before
beginning any substantial body of work, and issue a loud alert if they are not.

HIS FOLLOW-UP, which is what this file actually guards: *"But how does this solve
needing to run a similar probe during free reviews and simulated runs? The probe
would need to still function and to discern between the two conditions I think."*

THE ANSWER IS THAT THERE ARE NOT 2 CONDITIONS TO TELL APART. A free panel and a
simulated run both dispatch through `claude -p`; a paid dispatch additionally
names a seat whose route is not `claude_cli`. So the probe enumerates the routes
the ROSTER names and probes those. A mode flag would be a second description of
a fact the roster already carries, and 2 descriptions of 1 rule drifting apart is
this project's most frequently measured defect.

HIS RULING on the outbound half, 2026-10-28: *"Run the probe when a paid dispatch
has been authorised, as you suggest."* So a vendor endpoint is contacted only for
a route the roster names.

WHAT IS GUARDED HERE, each with the mutation that reddens it:
  1. A free roster probes `claude_cli` and makes NO network call.
  2. A paid roster surfaces the vendor route rather than silently ignoring it.
  3. A logged-out CLI is DETECTED and the remedy names who can apply it.
  4. `.env` is read honouring `export `, which is the 2026-07-08 regression:
     a line-initial parse saw 2 of 9 declarations and called 7 present keys
     missing. Measured again 2026-10-28.
  5. No credential value ever reaches the result.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PROBE = REPO / "scripts" / "route_auth_probe_2026-10-28.py"


@pytest.fixture(scope="module")
def rp():
    spec = importlib.util.spec_from_file_location("route_probe", PROBE)
    m = importlib.util.module_from_spec(spec)
    sys.modules["route_probe"] = m
    spec.loader.exec_module(m)
    return m


FREE = [("cc2", "opus", "claude_cli"), ("fable", "fable", "claude_cli")]
PAID = FREE + [("cx", "openai/gpt-5.3-codex", "openrouter"),
               ("ds", "deepseek-v4-pro", "deepseek")]


# ----------------------------------------------------------------- 1 and 2

def test_a_free_roster_yields_only_the_local_route(rp):
    assert rp.routes_for(FREE) == ["claude_cli"], (
        "2 free seats share 1 route, so the probe must run once, not twice")


def test_a_paid_roster_yields_the_vendor_routes_too(rp):
    got = rp.routes_for(PAID)
    assert got[0] == "claude_cli"
    assert set(got) == {"claude_cli", "openrouter", "deepseek"}, (
        f"a paid roster must surface its vendor routes; got {got}")


def test_a_free_roster_makes_no_network_call(rp, monkeypatch):
    """THE PROPERTY HIS RULING TURNS ON. A free review must not phone a vendor."""
    calls = []
    monkeypatch.setattr(rp, "probe_vendor",
                        lambda *a, **k: calls.append(a) or {"route": "x", "ok": True})
    monkeypatch.setattr(rp, "probe_claude_cli",
                        lambda *a, **k: {"route": "claude_cli", "ok": True,
                                         "why": "stub"})
    res = rp.probe_routes(FREE)
    assert res["all_ok"]
    assert calls == [], f"a free roster triggered {len(calls)} vendor probe(s)"


def test_a_paid_roster_does_probe_the_vendor(rp, monkeypatch):
    """ANTI-VACUITY for the test above: suppression must be the ROSTER's doing,
    not a probe that never fires for anyone."""
    calls = []

    def fake_vendor(vendor, env, timeout=20):
        calls.append(vendor)
        return {"route": vendor, "ok": True, "why": "stub"}

    monkeypatch.setattr(rp, "probe_vendor", fake_vendor)
    monkeypatch.setattr(rp, "probe_claude_cli",
                        lambda *a, **k: {"route": "claude_cli", "ok": True,
                                         "why": "stub"})
    rp.probe_routes(PAID)
    assert sorted(calls) == ["deepseek", "openrouter"], (
        f"a paid roster must probe both vendors; probed {calls}")


def test_no_outbound_suppresses_the_vendor_probe(rp, monkeypatch):
    calls = []
    monkeypatch.setattr(rp, "probe_vendor",
                        lambda *a, **k: calls.append(a[0]) or {"route": a[0], "ok": True})
    monkeypatch.setattr(rp, "probe_claude_cli",
                        lambda *a, **k: {"route": "claude_cli", "ok": True,
                                         "why": "stub"})
    res = rp.probe_routes(PAID, allow_outbound=False)
    assert calls == []
    assert set(res["skipped_outbound"]) == {"openrouter", "deepseek"}


# ----------------------------------------------------------------------- 3

def test_a_logged_out_cli_is_detected(rp, monkeypatch, tmp_path):
    """THE 2026-10-28 FAILURE, reproduced with a fake CLI.

    His real CLI cannot be logged out to test this, so the subprocess is faked
    with the exact payload the real one returned that night.
    """
    class R:
        stdout = json.dumps({"loggedIn": False, "authMethod": "none",
                             "apiProvider": "firstParty"})
        stderr = "Failed to authenticate: OAuth session expired and could not be refreshed"
    monkeypatch.setattr(rp.subprocess, "run", lambda *a, **k: R())
    out = rp.probe_claude_cli()
    assert out["ok"] is False
    assert "expired" in out["why"], f"the reason is unhelpful: {out}"
    assert "claude login" in out["remedy"]
    assert "founder" in out["remedy"], (
        "the remedy must say who can apply it; `claude login` is interactive")


def test_a_logged_in_cli_passes(rp, monkeypatch):
    class R:
        stdout = json.dumps({"loggedIn": True, "authMethod": "claude.ai"})
        stderr = ""
    monkeypatch.setattr(rp.subprocess, "run", lambda *a, **k: R())
    out = rp.probe_claude_cli()
    assert out["ok"] is True and out["method"] == "claude.ai"


def test_a_missing_cli_is_not_mistaken_for_a_logout(rp, monkeypatch):
    def boom(*a, **k):
        raise FileNotFoundError("claude")
    monkeypatch.setattr(rp.subprocess, "run", boom)
    out = rp.probe_claude_cli()
    assert out["ok"] is False
    assert "PATH" in out["remedy"], f"wrong remedy for a missing binary: {out}"


# ----------------------------------------------------------------------- 4

def test_dotenv_is_read_honouring_the_export_prefix(rp, monkeypatch, tmp_path):
    """THE 2026-07-08 REGRESSION GUARD, and it is executed rather than described.

    A line-initial parse of his real .env sees 2 of 9 declarations and reports 7
    PRESENT keys as missing -- 0.777778, Wilson [0.452589, 0.936775]. That is
    recorded in ONBOARDING as a parser bug, not a missing credential.
    """
    env = tmp_path / ".env"
    env.write_text(
        "# a comment\n"
        "export OPENROUTER_API_KEY=or-value\n"
        "export DEEPSEEK_API_KEY=ds-value\n"
        "SEMANTIC_SCHOLAR_API_KEY=ss-value\n"
        'export QUOTED_KEY="quoted-value"\n', encoding="utf-8")
    monkeypatch.setattr(rp, "REPO", tmp_path)
    got = rp.env_from_dotenv()
    assert got.get("OPENROUTER_API_KEY") == "or-value", (
        "the `export ` prefix defeated the reader, which is the 2026-07-08 bug")
    assert got.get("DEEPSEEK_API_KEY") == "ds-value"
    assert got.get("SEMANTIC_SCHOLAR_API_KEY") == "ss-value", (
        "an unprefixed line must still be read")
    assert got.get("QUOTED_KEY") == "quoted-value", "quotes were not stripped"
    assert len(got) == 4, f"expected 4 declarations, got {sorted(got)}"


def test_the_real_dotenv_yields_the_paid_credentials(rp):
    """Against his actual file. NAMES ONLY -- no value is asserted on."""
    got = rp.env_from_dotenv()
    if not (REPO / ".env").is_file():
        pytest.skip("no .env on this machine")
    for var in ("OPENROUTER_API_KEY", "DEEPSEEK_API_KEY"):
        assert var in got, (
            f"{var} was not read from .env. If it is present in `export` form "
            f"and this fails, the reader has regressed to the 2026-07-08 bug.")


# ----------------------------------------------------------------------- 5

def test_a_credential_value_never_reaches_the_result(rp, monkeypatch, tmp_path):
    """A probe result is printed and logged, so it must not carry the secret."""
    env = tmp_path / ".env"
    env.write_text("export OPENROUTER_API_KEY=sk-secret-do-not-echo\n",
                   encoding="utf-8")
    monkeypatch.setattr(rp, "REPO", tmp_path)

    class FakeResp:
        def getcode(self): return 200
        def read(self, n): return b'{"data":{"label":"acct"}}'
        def __enter__(self): return self
        def __exit__(self, *a): return False
    monkeypatch.setattr(rp.urllib.request, "urlopen",
                        lambda *a, **k: FakeResp())
    out = rp.probe_vendor("openrouter", rp.env_from_dotenv())
    blob = json.dumps(out)
    assert out["ok"] is True
    assert "sk-secret-do-not-echo" not in blob, (
        f"the credential leaked into the probe result: {out}")
    assert "acct" not in blob, (
        "the endpoint body leaked into the result; only the status should")


def test_a_rejected_credential_is_reported_without_its_value(rp, monkeypatch, tmp_path):
    env = tmp_path / ".env"
    env.write_text("export DEEPSEEK_API_KEY=sk-bad-secret\n", encoding="utf-8")
    monkeypatch.setattr(rp, "REPO", tmp_path)

    def raise_401(*a, **k):
        raise rp.urllib.error.HTTPError("u", 401, "Unauthorized", {}, None)
    monkeypatch.setattr(rp.urllib.request, "urlopen", raise_401)
    out = rp.probe_vendor("deepseek", rp.env_from_dotenv())
    assert out["ok"] is False and "401" in out["why"]
    assert "sk-bad-secret" not in json.dumps(out)


def test_an_unknown_route_fails_loudly_rather_than_passing(rp, monkeypatch):
    monkeypatch.setattr(rp, "probe_claude_cli",
                        lambda *a, **k: {"route": "claude_cli", "ok": True,
                                         "why": "stub"})
    res = rp.probe_routes(FREE + [("x", "m", "some_new_vendor")])
    assert res["all_ok"] is False
    assert any("no probe is defined" in f["why"] for f in res["failures"]), (
        f"an unprobeable route passed silently: {res}")


# ------------------------------------------------- wired into the POST, 2026-10-28

@pytest.fixture(scope="module")
def pf():
    spec = importlib.util.spec_from_file_location(
        "preflight_for_auth", REPO / "scripts" / "preflight_health_check_2026-10-06.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["preflight_for_auth"] = m
    spec.loader.exec_module(m)
    return m


def test_the_auth_check_is_in_the_post_and_is_first(pf):
    """HIS POLICY: checked FIRST, before any substantial body of work.

    The POST carried 7 checks and none looked at authentication, which is the
    gap his instruction closes. First in the order matters: under
    halt-at-first-failure a dead route makes every verdict below it moot,
    because nothing will dispatch at all.
    """
    names = [n for n, _, _ in pf.CHECKS]
    assert "model routes are authenticated" in names, (
        f"the auth check is not in the POST; checks are {names}")
    assert names[0] == "model routes are authenticated", (
        f"the auth check must run first; order is {names}")
    assert len(pf.CHECKS) == 8, (
        f"expected 8 checks after adding the auth check, found {len(pf.CHECKS)}")


def test_the_auth_check_wants_the_seats(pf):
    """ANTI-VACUITY. A check that ignores the roster cannot discern route sets,
    which is the whole of his follow-up question."""
    entry = next(c for c in pf.CHECKS if c[0] == "model routes are authenticated")
    assert entry[2] is True, (
        "the auth check is registered as not wanting seats, so it would be "
        "called with no roster and could not derive the route set")


def test_the_post_auth_check_fails_loudly_on_a_dead_route(pf, monkeypatch):
    """EXECUTED. The 2026-10-28 failure, through the POST rather than the probe.

    The POST loads the probe fresh by path, so there is nothing of mine to
    patch in it. Patch the REAL `subprocess.run` instead: the probe imports
    subprocess at module level, so a freshly-loaded copy picks this up. A first
    version patched `importlib.util.module_from_spec` to hand back my own
    module and broke the loader -- cleverness where a 1-line patch was enough.
    """
    import subprocess as real_subprocess

    # THE SHORT-CIRCUIT MUST BE LIFTED OR THIS TEST VERIFIES NOTHING. The POST
    # declines to consult a route under CDSFL_UNDER_PYTEST, which conftest sets,
    # so without this the check would return PASS and the assertion below would
    # be testing the short-circuit rather than the probe.
    monkeypatch.delenv("CDSFL_UNDER_PYTEST", raising=False)

    class R:
        stdout = json.dumps({"loggedIn": False, "authMethod": "none"})
        stderr = ("Failed to authenticate: OAuth session expired and could not "
                  "be refreshed")
    monkeypatch.setattr(real_subprocess, "run", lambda *a, **k: R())
    status, headline, notes = pf.check_routes_are_authenticated(["cc2", "fable"])
    assert status == pf.FAIL, (
        f"a logged-out CLI passed the POST: {status} {headline} {notes}")
    assert "NOT authenticated" in headline
    assert any("claude login" in n for n in notes), (
        f"the POST failure does not name the remedy: {notes}")
    assert any("expired" in n for n in notes), (
        f"the POST failure does not name the cause: {notes}")


def test_the_route_map_is_imported_not_copied(pf):
    """2 spellings of 1 table drift apart. The POST must read the dispatcher's.

    ★ WHAT THIS DOES AND DOES NOT PROVE, stated because the honest limit matters.
    It PARSES the POST and asserts it reads the attribute `_ALL` off the panel
    dispatcher, and that the dispatcher really defines it. That is structural,
    not textual: a comment mentioning the name does not satisfy it, and neither
    does a string.

    IT IS NOT A FULL EXECUTION, AND A SOURCE-TEXT VERSION WAS TRIED FIRST AND
    FAILED FOR A REASON WORTH RECORDING. `assert "pm._ALL" in src` proves only
    that the module mentions the name. The obvious conversion -- mutate the
    dispatcher's roster and watch it reach the POST -- CANNOT WORK here: the POST
    loads the panel module FRESH by path on every call, so an in-memory mutation
    never reaches it. The other conversion, giving the POST a paid seat and
    watching it name that vendor, would make a real outbound call with his
    credentials from inside a test. So the executable half is covered by the
    other 17 tests in this file, which call the probe directly, and this one
    holds the structural property that there is no second copy of the table.
    """
    import ast
    post = (REPO / "scripts" / "preflight_health_check_2026-10-06.py")
    tree = ast.parse(post.read_text(encoding="utf-8"))
    reads_all = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.Attribute) and n.attr == "_ALL"
        and isinstance(n.value, ast.Name)
    ]
    assert reads_all, (
        "the POST does not read an `_ALL` attribute off anything, so it is not "
        "reading the dispatcher's roster. If it now carries its own copy of the "
        "seat-to-route map, the 2 will drift -- which is the defect class this "
        "project has measured more often than any other")

    import importlib.util as ilu
    panel = REPO / "bench" / "confer_maths_panel_2026-09-05.py"
    pspec = ilu.spec_from_file_location("panel_roster_probe", panel)
    pm = ilu.module_from_spec(pspec)
    sys.modules["panel_roster_probe"] = pm
    pspec.loader.exec_module(pm)
    assert hasattr(pm, "_ALL"), (
        "the dispatcher no longer defines `_ALL`, so the POST's import of it is "
        "broken and the structural check above is testing nothing")
    assert all(isinstance(x, (list, tuple)) and len(x) >= 3 for x in pm._ALL), (
        "the dispatcher's roster is not (name, model, route) tuples any more, so "
        "the POST's route derivation cannot be reading it correctly")
    routes = {x[2] for x in pm._ALL}
    assert "claude_cli" in routes, (
        f"the roster names no claude_cli route, which is the one every free "
        f"panel and simulated run uses: {sorted(routes)}")
