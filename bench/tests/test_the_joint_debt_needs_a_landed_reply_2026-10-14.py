"""A joint round discharges a debt by ANSWERING, not by existing.

MEASURED 2026-10-14. CC1 dispatched a joint round for `his_rulings_2026-10-13`,
killed it 30 seconds in with 0 seat replies, and the parent's debt disappeared
from the derived owed set. Two independent routes did it, neither requiring a
single reply:

  1. A sibling directory whose name carries a marker ("joint", "star", "_r2",
     "round2") and the parent's 18-character stem.
  2. A `topology.json` whose `joint_of` names the parent -- and that file is
     written AT DISPATCH, before any seat answers.

A third defect sat beside them: the debt gate accepted `PANEL_JOINT_OF` as proof
of jointness, which `bench/star_topology_2026-10-06.py` had already identified as
the wrong inference for the round KIND ("THE ROUND KIND MUST NOT BE INFERRED FROM
THE DECLARATION IT REQUIRES"). The brief CC1 declared as the joint half pointed at
`bench/logs/his_rulings_2026-10-13/cc2/` and `fable/`, directories that do not
exist -- the replies are `cc2.json` and `fable.json` -- so a seat following it
would have found nothing.

THESE TESTS CALL THE PREDICATES. They do not read the module's source. A test that
asserts on source text asserts only that the module describes itself consistently,
and 2 forms that disagree are each individually correct in their own description.

Producer for the figures:
`scripts/the_joint_debt_is_discharged_by_a_directory_2026-10-14.py`.
"""
from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]


def _load(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def panel():
    """Import the dispatcher without LEAKING its import-time environment.

    The first version set `PANEL_BRIEF_UNCHECKED` with a bare `os.environ[...]`
    at module scope and never restored it. pytest runs these files in one
    process, so the variable survived into every later test -- and
    `test_panel_brief_format_2026-09-09.py` spawns the dispatcher as a
    SUBPROCESS, which inherited it, skipped the brief check it exists to verify
    and returned a different exit code. A fixture that contaminates its
    neighbours is worse than no fixture, because the neighbour's failure points
    at the wrong file.
    """
    prior = os.environ.get("PANEL_BRIEF_UNCHECKED")
    os.environ["PANEL_BRIEF_UNCHECKED"] = "1"
    try:
        yield _load(REPO / "bench" / "confer_maths_panel_2026-09-05.py",
                    "_panel_dbt")
    finally:
        if prior is None:
            os.environ.pop("PANEL_BRIEF_UNCHECKED", None)
        else:
            os.environ["PANEL_BRIEF_UNCHECKED"] = prior


@pytest.fixture(scope="module")
def star():
    return _load(REPO / "bench" / "star_topology_2026-10-06.py", "_star_dbt")


def _round(logs: pathlib.Path, name: str, seats=(), joint_of=None, kind=None,
           body: str = "", brief: str = "a brief"):
    """Build a synthetic round. `seats` land a reply; an empty tuple lands none."""
    d = logs / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "BRIEF.md").write_text(brief, encoding="utf-8")
    for s in seats:
        text = body or ("x" * 900)
        (d / f"{s}.json").write_text(json.dumps(
            {"ok": True, "chars": len(text), "response": text}), encoding="utf-8")
    if joint_of is not None or kind is not None:
        (d / "topology.json").write_text(json.dumps(
            {"kind": kind, "joint_of": list(joint_of or [])}), encoding="utf-8")
    return d


def _owed(panel, logs_root: pathlib.Path, monkeypatch):
    monkeypatch.setattr(panel, "_REPO", logs_root)
    return panel._rounds_owing_a_joint_round()


# ───────────────────── the two false discharges ─────────────────────

def test_a_marker_named_partner_with_no_replies_does_not_discharge(
        panel, tmp_path, monkeypatch):
    """ROUTE 1. The exact shape of the 2026-10-14 incident."""
    logs = tmp_path / "bench" / "logs"
    _round(logs, "his_question_2026-10-10", seats=("cc2", "fable"))
    _round(logs, "joint_his_question_2026-10-10", seats=())      # killed, 0 replies
    assert "his_question_2026-10-10" in _owed(panel, tmp_path, monkeypatch)


def test_a_topology_declaration_with_no_replies_does_not_discharge(
        panel, tmp_path, monkeypatch):
    """ROUTE 2. `topology.json` is written at dispatch, before any seat answers."""
    logs = tmp_path / "bench" / "logs"
    _round(logs, "his_question_2026-10-10", seats=("cc2", "fable"))
    # A name with NO marker, so only the declaration could discharge it.
    _round(logs, "followup_2026-10-11", seats=(),
           joint_of=["his_question_2026-10-10"], kind="joint")
    assert "his_question_2026-10-10" in _owed(panel, tmp_path, monkeypatch)


# ─────────── and the fix is not a blanket refusal: it still discharges ───────────

def test_a_marker_named_partner_that_answered_DOES_discharge(
        panel, tmp_path, monkeypatch):
    logs = tmp_path / "bench" / "logs"
    _round(logs, "his_question_2026-10-10", seats=("cc2", "fable"))
    _round(logs, "joint_his_question_2026-10-10", seats=("cc2", "fable"))
    assert "his_question_2026-10-10" not in _owed(panel, tmp_path, monkeypatch)


def test_a_declaration_from_a_round_that_answered_DOES_discharge(
        panel, tmp_path, monkeypatch):
    logs = tmp_path / "bench" / "logs"
    _round(logs, "his_question_2026-10-10", seats=("cc2", "fable"))
    _round(logs, "followup_2026-10-11", seats=("cc2", "fable"),
           joint_of=["his_question_2026-10-10"], kind="joint")
    assert "his_question_2026-10-10" not in _owed(panel, tmp_path, monkeypatch)


def test_one_landed_reply_is_not_a_round(panel, tmp_path, monkeypatch):
    """A debt is owed by rounds with 2+ replies, so 1 reply discharges nothing."""
    logs = tmp_path / "bench" / "logs"
    _round(logs, "his_question_2026-10-10", seats=("cc2", "fable"))
    _round(logs, "joint_his_question_2026-10-10", seats=("cc2",))
    assert "his_question_2026-10-10" in _owed(panel, tmp_path, monkeypatch)


# ───────── the declaration is not proof: the brief must quote the parent ─────────

def _gate(panel, star, tmp_path, monkeypatch, brief_text, joint_of):
    """Run the live debt gate against a synthetic tree and capture its verdict."""
    logs = tmp_path / "bench" / "logs"
    parent_body = "P" * 1200
    _round(logs, "parent_2026-10-10", seats=("cc2", "fable"), body=parent_body)
    me = _round(logs, "joint_parent_2026-10-10", seats=(), brief=brief_text)
    reg = tmp_path / "bench" / "directives" / "universal"
    reg.mkdir(parents=True, exist_ok=True)
    (reg / "joint_round_debt.json").write_text(
        json.dumps({"entries": {}}), encoding="utf-8")
    monkeypatch.setattr(panel, "_REPO", tmp_path)
    monkeypatch.setattr(panel, "_JOINT_OF", tuple(joint_of))
    monkeypatch.setattr(panel, "_logs_dir", lambda: me)
    monkeypatch.delenv("PANEL_SKIP_TOPOLOGY", raising=False)
    return panel._refuse_if_a_joint_round_is_owed(), parent_body


def test_the_gate_refuses_a_declared_joint_round_that_quotes_nothing(
        panel, star, tmp_path, monkeypatch):
    """The brief CC1 actually wrote: it POINTED at paths and quoted no reply."""
    rc, _ = _gate(panel, star, tmp_path, monkeypatch,
                  brief_text="Read bench/logs/parent_2026-10-10/cc2/ and fable/.",
                  joint_of=["parent_2026-10-10"])
    assert rc != 0, "a joint brief quoting nothing must be refused"


def test_the_gate_accepts_a_joint_round_that_carries_the_replies(
        panel, star, tmp_path, monkeypatch):
    rc, body = None, None
    logs = tmp_path / "bench" / "logs"
    parent_body = "P" * 1200
    _round(logs, "parent_2026-10-10", seats=("cc2", "fable"), body=parent_body)
    me = _round(logs, "joint_parent_2026-10-10", seats=(),
                brief="Here is the reply in full:\n" + parent_body)
    reg = tmp_path / "bench" / "directives" / "universal"
    reg.mkdir(parents=True, exist_ok=True)
    (reg / "joint_round_debt.json").write_text(
        json.dumps({"entries": {}}), encoding="utf-8")
    monkeypatch.setattr(panel, "_REPO", tmp_path)
    monkeypatch.setattr(panel, "_JOINT_OF", ("parent_2026-10-10",))
    monkeypatch.setattr(panel, "_logs_dir", lambda: me)
    assert panel._refuse_if_a_joint_round_is_owed() == 0


# ───────── EXECUTE BOTH FORMS against the live round, not its description ─────────

def test_the_live_joint_round_is_detected_not_merely_declared(star):
    """The recorded kind and the DETECTED kind must agree on the live round.

    This is the `execute-do-not-grep` form: `topology.json` describes itself
    correctly and `round_kind` describes itself correctly, and until 2026-10-14
    they disagreed on 2 of the 6 rounds carrying a recorded kind.
    """
    logs = REPO / "bench" / "logs"
    d = logs / "joint_his_rulings_2026-10-13"
    if not (d / "topology.json").is_file():
        pytest.skip("the 2026-10-14 joint round is not in this tree")
    declared = json.loads((d / "topology.json").read_text()).get("kind")
    detected = star.round_kind(logs, d.name)
    assert declared == detected == "joint", (
        f"declared={declared} detected={detected}: a round recorded as joint "
        f"whose brief carries no parent reply was never a joint round")
