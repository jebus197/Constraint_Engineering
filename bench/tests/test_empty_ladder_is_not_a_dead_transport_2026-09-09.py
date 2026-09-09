"""An empty routing ladder must defer, not be retried forever as a dead transport.

Found by fable in panel review 2026-09-09 and confirmed here by execution before
the fix was applied.

`_apply_routing` reached one branch for two different situations: no rung reached
a model because the transport failed, and no rung reached a model because there
were no rungs. Both took the "retry a later round" path. That is right for a
transport fault, which may clear, and wrong for an empty ladder, which cannot:
`route` excludes the finding's own source model, so a roster carrying only that
model yields the empty set every round forever.

The consequence was not a slow retry loop. The finding got neither
`irreducible_escalation` nor `routing_deferred`, and `unverified_critical_count`
counts exactly those two -- so the critical blocked convergence to the round cap
while never entering the irreducible-queue count, and
HALTED_IRREDUCIBLE_QUEUE_ALARM could not fire. The exp56 1-seat arm pre-registers
that halt as its reportable outcome, in its own words "a reportable outcome of
this design, not a mechanical fault to be tuned away".

THE PATH IS NEWLY REACHABLE. It was unreachable while all 3 arms held
`routing_enabled: false`, and became reachable the moment routing was enabled on
2026-09-09. Enabling a capability opened a hole in the arm that most depends on
the alarm.

Every test here EXECUTES `_apply_routing` or `rank_falsifier_writers` against a
stubbed dispatcher. None reads source text, because the defect is a branch taken
at runtime and both branches are individually well-described in the source.
"""

import sys
import types
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

from bench.reference_runner_v3 import (  # noqa: E402
    CRITICAL_SEVERITY_THRESHOLD, FindingRegistry, RunnerConfig, _apply_routing,
)
from bench.routing import rank_falsifier_writers  # noqa: E402


@pytest.fixture
def mini_repo(tmp_path):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "pkg" / "spec.py").write_text("VALUE = 1\n", encoding="utf-8")
    return tmp_path


TARGET_REL = "pkg/spec.py"


def _registry(cid="C0001", model="CC2", **over):
    reg = FindingRegistry()
    entry = {
        "canonical_id": cid,
        "severity": 0.9,
        "description": "the stated clearance is the retracted value",
        "falsifier_code": "",
        "status": "OPEN",
        "verdicts": [],
        "source_model": model,
        "source_aliases": ["F001"],
        "open_since_round": 0,
        "last_status_change_round": 0,
        "escalated": True,
        "falsifier_verdict": "UNTOOLABLE",
    }
    entry.update(over)
    reg.entries[cid] = entry
    reg._alias_map[f"{model}:F001"] = cid
    return reg


def _roster(*labels):
    return types.SimpleNamespace(
        models=[types.SimpleNamespace(label=lbl, timeout=10) for lbl in labels])


def _cfg(declared):
    cfg = RunnerConfig(test_article=TARGET_REL, routing_enabled=True,
                       falsifier_gate_enabled=True)
    cfg.models = list(declared)
    return cfg


# --- 1. THE PREMISE, EXECUTED. The ladder really is empty by construction. ---

def test_a_one_seat_roster_yields_no_rungs():
    """Not argued from the source: the helper is called."""
    assert rank_falsifier_writers(["CC2"], exclude=("CC2",)) == []


def test_a_two_seat_roster_yields_a_rung():
    """The contrast that shows the emptiness is about seat count, not a bug."""
    assert rank_falsifier_writers(["Codex", "ChatGPT"], exclude=("Codex",)) != []


# --- 2. THE FIX. -------------------------------------------------------------

def test_an_empty_ladder_stamps_routing_deferred(mini_repo, monkeypatch):
    from bench import reference_runner_v3 as _R
    dispatched = []
    monkeypatch.setattr(
        _R, "dispatch_to_model",
        lambda mc, p, s, **kw: (dispatched.append(getattr(mc, "label", mc)), ("", 0.1))[1])
    reg = _registry(model="CC2")
    _apply_routing(reg, 4, _roster("CC2"), cfg=_cfg(["CC2"]),
                   repo_root=str(mini_repo))
    e = reg.entries["C0001"]
    assert dispatched == [], f"an empty ladder must dispatch to nobody, got {dispatched}"
    assert e.get("routing_deferred") is True, (
        "an empty ladder must be deferred; retried as a dead transport it never "
        "enters the irreducible-queue count and the alarm cannot fire")
    assert "empty by construction" in (e.get("routing_deferred_reason") or ""), (
        "the deferral must say WHY, or a reader cannot tell it from an "
        "equipment-failure deferral")


def test_the_deferred_finding_now_counts_toward_the_alarm(mini_repo, monkeypatch):
    """THE POINT OF THE FIX, asserted on the counter rather than on the flag.

    Stamping a flag nothing reads would be an addition nothing reaches. The
    counter that matters is `irreducible_queue_count`, which is what
    `build_irreducible_queue_alarm` calls -- NOT `unverified_critical_count`,
    which this test asserted on first and which requires status UNCONFIRMED."""
    from bench import reference_runner_v3 as _R
    monkeypatch.setattr(_R, "dispatch_to_model", lambda mc, p, s, **kw: ("", 0.1))
    reg = _registry(model="CC2")
    assert reg.irreducible_queue_count() == 0, "precondition: not yet routed"
    _apply_routing(reg, 4, _roster("CC2"), cfg=_cfg(["CC2"]),
                   repo_root=str(mini_repo))
    assert reg.irreducible_queue_count() == 1, (
        "the deferred critical must be countable, or the 1-seat arm burns to "
        "max_rounds instead of halting with an evidence bundle")


def test_the_alarm_can_actually_fire_end_to_end(mini_repo, monkeypatch):
    """THE WHOLE CLAIM, driven through the real alarm builder.

    A count is not a halt. This routes 3 criticals in a 1-seat arm -- one more
    than the default `max_irreducible_queue` of 2 -- and asserts the alarm
    object is built. Before the fix the count stayed 0 and this returned None
    however many criticals piled up."""
    from bench import reference_runner_v3 as _R
    monkeypatch.setattr(_R, "dispatch_to_model", lambda mc, p, s, **kw: ("", 0.1))
    reg = _registry(model="CC2")
    for extra in ("C0002", "C0003"):
        reg.entries[extra] = dict(reg.entries["C0001"], canonical_id=extra)
    cfg = _cfg(["CC2"])
    assert _R.build_irreducible_queue_alarm(reg, cfg, 4) is None, (
        "precondition: nothing is deferred yet, so no alarm")
    _apply_routing(reg, 4, _roster("CC2"), cfg=cfg, repo_root=str(mini_repo))
    assert reg.irreducible_queue_count() == 3
    alarm = _R.build_irreducible_queue_alarm(reg, cfg, 4)
    assert alarm is not None, (
        "3 deferred criticals exceed max_irreducible_queue=2, so the arm's "
        "pre-registered reportable outcome must be reachable")


def test_severity_still_gates_the_count(mini_repo, monkeypatch):
    """The fix must not make every empty-ladder finding an alarm item."""
    from bench import reference_runner_v3 as _R
    monkeypatch.setattr(_R, "dispatch_to_model", lambda mc, p, s, **kw: ("", 0.1))
    reg = _registry(model="CC2", severity=CRITICAL_SEVERITY_THRESHOLD - 0.2)
    _apply_routing(reg, 4, _roster("CC2"), cfg=_cfg(["CC2"]),
                   repo_root=str(mini_repo))
    assert reg.irreducible_queue_count() == 0


# --- 3. THE DISTINCTION THE FIX EXISTS TO MAKE. ------------------------------

def test_a_dead_transport_is_still_retried_not_deferred(mini_repo, monkeypatch):
    """THE FALSIFICATION. If this goes green with the fix reverted, the fix is
    not doing what it claims; if it goes RED with the fix in, the fix has
    swallowed the transport-dead case it was required to leave alone.

    Rungs exist here -- a 2-seat roster with a different source -- and every
    dispatch raises, which is the 402-cascade class. That must stay retryable."""
    from bench import reference_runner_v3 as _R

    def _boom(mc, p, s, **kw):
        raise RuntimeError("HTTP 402 payment required")
    monkeypatch.setattr(_R, "dispatch_to_model", _boom)
    reg = _registry(model="Codex")
    _apply_routing(reg, 4, _roster("Codex", "ChatGPT", "Gemini"),
                   cfg=_cfg(["Codex", "ChatGPT", "Gemini"]),
                   repo_root=str(mini_repo))
    e = reg.entries["C0001"]
    assert e.get("routing_deferred") is not True, (
        "a transport fault may clear next round; deferring it converts a "
        "recoverable network failure into a permanent verdict")


# --- 4. THE BOUNDARY, closed after cc2 measured it open. ---------------------

def test_severity_exactly_at_the_threshold_counts(mini_repo, monkeypatch):
    """`>=` MUST STAY `>=`, and nothing asserted that.

    cc2 measured this in panel review 2026-09-09 by mutating
    `irreducible_queue_count`'s comparison from `>=` to `>`: 44 tests stayed
    green. The shipped code was correct, so this is a coverage hole rather than
    a live defect -- but a boundary nothing pins is a boundary that moves. The
    existing severity test used threshold minus 0.2, which is far enough from
    the edge to miss the mutation entirely."""
    from bench import reference_runner_v3 as _R
    monkeypatch.setattr(_R, "dispatch_to_model", lambda mc, p, s, **kw: ("", 0.1))
    reg = _registry(model="CC2", severity=CRITICAL_SEVERITY_THRESHOLD)
    _apply_routing(reg, 4, _roster("CC2"), cfg=_cfg(["CC2"]),
                   repo_root=str(mini_repo))
    assert reg.irreducible_queue_count() == 1, (
        f"a critical at exactly {CRITICAL_SEVERITY_THRESHOLD} must count; with "
        f"`>` it silently drops out of the queue the alarm reads")


def test_severity_just_below_the_threshold_does_not_count(mini_repo, monkeypatch):
    """The other side of the same edge, so the test cannot pass by counting
    everything."""
    from bench import reference_runner_v3 as _R
    monkeypatch.setattr(_R, "dispatch_to_model", lambda mc, p, s, **kw: ("", 0.1))
    reg = _registry(model="CC2", severity=CRITICAL_SEVERITY_THRESHOLD - 1e-9)
    _apply_routing(reg, 4, _roster("CC2"), cfg=_cfg(["CC2"]),
                   repo_root=str(mini_repo))
    assert reg.irreducible_queue_count() == 0
