"""Routing must not be able to remove a finding from the gamma series.

WHY THIS EXISTS. Routing and the post-convergence sweep were switched ON in all
3 exp56 arms on 2026-09-09, where they had been held OFF. Routing is an ABSORBER:
it takes an escalated critical and tries to resolve it. That raises a question
nobody had asked, and it is the question the standing directive in
.claude/CLAUDE.md makes load-bearing -- "GAMMA IS LOAD-BEARING, DO NOT DEMOTE
IT". If routing removed resolved findings from the novelty series, a run could
converge on a flattened decay curve that flattened because findings were routed
AWAY, not because the problem space was exhausted. That is not a demotion of
gamma; it is worse, because gamma would still gate while silently measuring
something else.

MEASURED ANSWER: IT CANNOT, and this file pins the reason rather than the
result. `_settled_novelty_series` counts an entry in the round it was DISCOVERED
(`open_since_round`) and excludes only MERGED, DUPLICATE, UNCONFIRMED and
REFUTED. Routing's success path writes CONFIRMED, which is not in that set, so a
routed-and-resolved finding stays counted. Executed with the strongest possible
absorber -- every finding resolved -- the critical series was unchanged and
gamma_critical was identical to 17 significant figures.

The DUPLICATE path is the one that could break this, and it is safe for a reason
that has nothing to do with gamma: the founder's NO VOTING ruling of 2026-08-19
makes the runner WITHHOLD the merge, writing `merge_candidate_of` and
`merge_blocked_reason` and leaving the status alone, because a word-overlap
similarity score is not a tool verdict. Gamma is protected here as a side effect
of that ruling. If anyone ever "helpfully" completes the merge, gamma silently
flattens -- so this file tests the property directly rather than trusting the
ruling to stay in force.
"""

import sys
import tempfile
import types
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

import bench.falsifier_verify as fv  # noqa: E402
import bench.reference_runner_v3 as rr  # noqa: E402
from bench.reference_runner_v3 import (  # noqa: E402
    _NON_NOVEL_TERMINAL_STATUSES, FindingRegistry, RunnerConfig, _apply_routing,
    _estimate_gamma, _settled_novelty_series,
)

DISCOVERY_ROUNDS = [0, 0, 1, 1, 2, 3]


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "pkg" / "spec.py").write_text("VALUE = 1\n", encoding="utf-8")
    return tmp_path


def _registry():
    reg = FindingRegistry()
    for i, r in enumerate(DISCOVERY_ROUNDS):
        cid = f"C{i:04d}"
        reg.entries[cid] = {
            "canonical_id": cid, "status": "OPEN", "severity": 0.9,
            "description": f"a distinct critical numbered {i}",
            "falsifier_code": "", "verdicts": [], "source_model": "Codex",
            "source_aliases": [f"F{i}"], "open_since_round": r,
            "last_status_change_round": r, "escalated": True,
            "falsifier_verdict": "UNTOOLABLE",
        }
    return reg


def _cfg():
    cfg = RunnerConfig(test_article="pkg/spec.py", routing_enabled=True,
                       falsifier_gate_enabled=True)
    cfg.models = ["Codex", "ChatGPT", "Gemini"]
    return cfg


def _exp():
    return types.SimpleNamespace(models=[
        types.SimpleNamespace(label=lbl, timeout=10)
        for lbl in ("Codex", "ChatGPT", "Gemini")])


def test_confirmed_is_not_a_non_novel_status():
    """The single fact the whole property rests on, asserted on its own.

    If CONFIRMED is ever added to this set, every test below still passes for
    the wrong reason -- routing would then be removing findings from the series
    and the fixtures would simply have nothing left to compare."""
    assert "CONFIRMED" not in _NON_NOVEL_TERMINAL_STATUSES, (
        "a routed-and-resolved finding would now drop out of the novelty "
        "series, so gamma would flatten as findings are absorbed")


def test_full_absorption_does_not_move_the_critical_series(repo, monkeypatch):
    """THE PROPERTY, driven with the strongest absorber that can exist."""
    monkeypatch.setattr(
        rr, "dispatch_to_model",
        lambda mc, p, s, **kw: ("```python\nassert 0, 'FALSIFIED'\n```", 0.1))
    monkeypatch.setattr(
        fv, "reverify_falsifier",
        lambda code, repo_root=None, timeout=None, **kw: "CONFIRMED")
    monkeypatch.setattr(rr, "reverify_falsifier", fv.reverify_falsifier,
                        raising=False)

    before = _registry()
    _, crit_before = _settled_novelty_series(before, 3)

    after = _registry()
    _apply_routing(after, 3, _exp(), cfg=_cfg(), repo_root=str(repo))

    resolved = sum(1 for e in after.entries.values() if e.get("resolved_by_routing"))
    assert resolved == len(DISCOVERY_ROUNDS), (
        f"the fixture must actually absorb everything or the test is vacuous; "
        f"only {resolved} of {len(DISCOVERY_ROUNDS)} were resolved")

    _, crit_after = _settled_novelty_series(after, 3)
    assert crit_after == crit_before, (
        f"routing moved the critical novelty series from {crit_before} to "
        f"{crit_after}; a run could then converge on a decay curve that "
        f"flattened because findings were routed away")


def test_gamma_critical_is_bit_identical_after_full_absorption(repo, monkeypatch):
    """The series is the mechanism; gamma is what the gate actually reads."""
    monkeypatch.setattr(
        rr, "dispatch_to_model",
        lambda mc, p, s, **kw: ("```python\nassert 0, 'FALSIFIED'\n```", 0.1))
    monkeypatch.setattr(
        fv, "reverify_falsifier",
        lambda code, repo_root=None, timeout=None, **kw: "CONFIRMED")
    monkeypatch.setattr(rr, "reverify_falsifier", fv.reverify_falsifier,
                        raising=False)

    before = _registry()
    after = _registry()
    _apply_routing(after, 3, _exp(), cfg=_cfg(), repo_root=str(repo))

    g_before = _estimate_gamma(_settled_novelty_series(before, 3)[1], 2)
    g_after = _estimate_gamma(_settled_novelty_series(after, 3)[1], 2)
    assert g_before == g_after, f"{g_before} != {g_after}"


def test_a_withheld_duplicate_stays_in_the_series(repo, monkeypatch):
    """The one path that could remove a finding, and why it does not.

    `route` can return DUPLICATE. The runner deliberately WITHHOLDS the merge on
    the founder's NO VOTING ruling, because a word-overlap similarity score is
    not a tool verdict -- so the status is left alone and the finding stays
    counted. This asserts the observable consequence, so that completing the
    merge later cannot silently flatten gamma."""
    monkeypatch.setattr(
        rr, "dispatch_to_model",
        lambda mc, p, s, **kw: ("```python\nassert 0, 'FALSIFIED'\n```", 0.1))
    monkeypatch.setattr(
        fv, "reverify_falsifier",
        lambda code, repo_root=None, timeout=None, **kw: "CONFIRMED")
    monkeypatch.setattr(rr, "reverify_falsifier", fv.reverify_falsifier,
                        raising=False)

    reg = _registry()
    # Two entries with identical descriptions: the duplicate detector's input.
    reg.entries["C0001"]["description"] = reg.entries["C0000"]["description"]
    _, crit_before = _settled_novelty_series(reg, 3)
    _apply_routing(reg, 3, _exp(), cfg=_cfg(), repo_root=str(repo))
    _, crit_after = _settled_novelty_series(reg, 3)

    merged = [cid for cid, e in reg.entries.items()
              if e.get("status") in _NON_NOVEL_TERMINAL_STATUSES]
    assert not merged, (
        f"{merged} left the novelty series through routing; the merge is "
        f"supposed to be WITHHELD, and completing it flattens gamma")
    assert crit_after == crit_before
