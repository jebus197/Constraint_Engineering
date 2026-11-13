# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'standards_currency_2026-11-13', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 6839428e35143957665499e1c50e8610c468239e1c3f73ffb88cc39e2400fe3e
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The aliveness probe must report WHICH model answered, from the TRANSPORT.

WHAT GOES RED IF THE FIX IS REVERTED.
  * Delete `bench/model_identity.py` -> every test here errors on import.
  * Revert the `identity=` parameter on `seat_aliveness.probe_seat` or the
    `identities=` parameter on `probe_roster` -> `test_probe_seat_records_identity`
    and `test_probe_roster_threads_identities` fail on TypeError.
  * Revert the `_identity_caller` wiring in `confer_maths_panel_2026-09-05.py` ->
    `test_dispatcher_wires_an_identity_caller` and
    `test_dispatcher_preflight_passes_identities_to_the_probe` fail, which is the
    guard against an addition nothing reaches.
  * Make the verdict trust the model's own words instead of the envelope ->
    `test_self_report_is_not_accepted_as_identity` fails.

EVERY FIXTURE HERE IS A REAL OBSERVATION. The envelope shape is the one
`claude --model opus -p "say ok" --output-format json` returned on this machine
on 2026-11-13 (`modelUsage` keyed `claude-opus-5`), and the version pair is the
measured one: `claude-fable-5-2` requires client 2.1.290, 2.1.220 is installed.
"""

from __future__ import annotations

import ast
import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "bench"))

import model_identity as MI  # noqa: E402


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, REPO / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


AL = _load("sa_identity_under_test", "bench/seat_aliveness_2026-10-06.py")

#: The LIVE envelope, measured 2026-11-13.
LIVE_ENVELOPE = {"modelUsage": {"claude-opus-5": {"outputTokens": 9276}}}
#: The LIVE refusal text shape and the LIVE installed client.
FABLE_52_REFUSAL = "This model requires Claude Code version 2.1.290 or newer."
INSTALLED_CLI = "2.1.220"


# ---------------------------------------------------------------- the verdict

def test_resolved_id_comes_from_the_transport_envelope():
    assert MI.resolved_from_envelope(LIVE_ENVELOPE) == ["claude-opus-5"]


def test_busiest_model_sorts_first_when_two_served():
    env = {"modelUsage": {"a-1": {"outputTokens": 3},
                          "b-2": {"outputTokens": 99}}}
    assert MI.resolved_from_envelope(env)[0] == "b-2"


@pytest.mark.parametrize("bad", [None, "not-a-dict", 7, {}, {"modelUsage": 5}])
def test_a_malformed_envelope_claims_nothing(bad):
    assert MI.resolved_from_envelope(bad) == []
    assert MI.identity_verdict("opus", bad, INSTALLED_CLI)["how"] == "unknown"


def test_self_report_is_not_accepted_as_identity():
    """A reply SAYING it is Fable 5.2 must not produce a Fable 5.2 verdict.

    This is the `tools decide, not votes` clause applied to identity. The
    envelope says opus; the prose says otherwise; the envelope governs.
    """
    v = MI.identity_verdict("fable", LIVE_ENVELOPE, INSTALLED_CLI)
    assert v["how"] == "mismatch"
    assert v["resolved"] == ["claude-opus-5"]


def test_the_measured_patch_gap_is_derived_not_typed():
    """70 is DERIVED from the refusal's own stated requirement, not stored."""
    v = MI.identity_verdict("claude-fable-5-2", None, INSTALLED_CLI,
                            FABLE_52_REFUSAL)
    assert v["how"] == "unreachable"
    assert v["gate"]["patch_gap"] == 70
    assert MI.parse_required_cli(FABLE_52_REFUSAL) == "2.1.290"
    # Nothing in the module stores a model name or a version.
    src = (REPO / "bench" / "model_identity.py").read_text()
    body = "\n".join(l for l in src.splitlines()
                     if not l.lstrip().startswith("#"))
    body = body.split('"""')
    code = "".join(body[i] for i in range(0, len(body), 2))
    assert "2.1.290" not in code and "fable-5-2" not in code


def test_a_patch_gap_across_a_minor_boundary_is_not_a_distance():
    g = MI.cli_version_gate("2.2.1", "2.1.220")
    assert g["reachable"] is False and g["patch_gap"] is None


def test_an_alias_matches_whatever_the_client_serves():
    assert MI.identity_verdict("opus", LIVE_ENVELOPE, INSTALLED_CLI)["how"] == "match"


def test_every_verdict_is_a_declared_state():
    for args in (("opus", LIVE_ENVELOPE, INSTALLED_CLI, None),
                 ("fable", LIVE_ENVELOPE, INSTALLED_CLI, None),
                 ("claude-fable-5-2", None, INSTALLED_CLI, FABLE_52_REFUSAL),
                 (None, None, None, None)):
        assert MI.identity_verdict(*args)["how"] in MI.IDENTITY_STATES


# ------------------------------------------------------------------ the probe

def test_probe_seat_records_identity():
    r = AL.probe_seat("s", lambda: "Ready!",
                      identity=lambda: (LIVE_ENVELOPE, None, "opus", INSTALLED_CLI))
    assert r.alive is True
    assert r.identity["how"] == "match"
    assert r.identity["resolved"] == ["claude-opus-5"]


def test_no_identity_probe_is_distinguishable_from_an_unknown_one():
    """A check that did not run must not look like a check that found nothing."""
    assert AL.probe_seat("s", lambda: "Ready!").identity is None
    ran = AL.probe_seat("s", lambda: "Ready!", identity=lambda: (None, None, "opus", None))
    assert ran.identity is not None and ran.identity["how"] == "unknown"


def test_a_failing_identity_probe_never_kills_a_live_seat():
    def boom():
        raise RuntimeError("transport gave no envelope")
    r = AL.probe_seat("s", lambda: "Ready!", identity=boom)
    assert r.alive is True
    assert r.identity["how"] == "unknown"
    assert "RuntimeError" in r.identity["why"]


def test_probe_roster_threads_identities():
    res = AL.probe_roster(
        {"a": lambda: "Ready!"},
        identities={"a": lambda: (LIVE_ENVELOPE, None, "opus", INSTALLED_CLI)})
    assert res["a"].identity["how"] == "match"


def test_identity_is_not_asked_of_a_dead_seat():
    asked = []

    def ident():
        asked.append(1)
        return (LIVE_ENVELOPE, None, "opus", INSTALLED_CLI)
    r = AL.probe_seat("s", lambda: "", attempts=1, identity=ident)
    assert r.alive is False and asked == []


# ------------------------------------------------------- the addition is reached

def test_dispatcher_wires_an_identity_caller():
    """Guard against an addition nothing reaches: the dispatcher must build one."""
    src = (REPO / "bench" / "confer_maths_panel_2026-09-05.py").read_text()
    tree = ast.parse(src)
    names = {n.name for n in ast.walk(tree)
             if isinstance(n, ast.FunctionDef)}
    assert "_identity_caller" in names, "the dispatcher defines no identity caller"


def test_dispatcher_preflight_passes_identities_to_the_probe():
    src = (REPO / "bench" / "confer_maths_panel_2026-09-05.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "probe_roster"):
            if any(k.arg == "identities" for k in node.keywords):
                return
    pytest.fail("no probe_roster call in the dispatcher passes identities=")


def test_identity_caller_declines_routes_that_cannot_report_identity():
    src = (REPO / "bench" / "confer_maths_panel_2026-09-05.py").read_text()
    ns = {}
    tree = ast.parse(src)
    fn = next(n for n in tree.body
              if isinstance(n, ast.FunctionDef) and n.name == "_identity_caller")
    exec(compile(ast.Module([fn], []), "<fn>", "exec"), ns)
    assert ns["_identity_caller"]("m", "openrouter", 10) is None
    assert ns["_identity_caller"]("m", "moonshot", 10) is None
    assert ns["_identity_caller"]("m", "claude_cli", 10) is not None
