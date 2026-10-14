"""Star topology is 2 halves, and the second half was almost never run.

THE FOUNDER, 2026-10-08: *"And you don't seem to have been running recent panels
under star topology, blind run first?"* He was right. Produced by
`scripts/the_joint_round_was_almost_never_run_2026-10-08.py`: of 99 archived
rounds that collected 2 or more landed replies, **15 have a joint round**,
0.151515, Wilson [0.094023, 0.235041]. Since his ruling of 2026-10-06 that the
topology be built in so it could not be skipped, **1 of 5**, Wilson [0.036224,
0.624465] -- and the 4 unpaired rounds were all dispatched by CC1 and all
reported to him as star topology.

WHY THE EXISTING GUARD COULD NOT CATCH IT, which is the finding rather than the
rate. `_refuse_if_topology_is_skipped` refuses a round whose SIBLING on the same
brief holds a landed reply and is not declared blind. A round with NO sibling
passes trivially, so a lone blind round with no joint round ever following is
precisely the case it cannot see. It guards contamination BETWEEN rounds; it has
no concept of an unrun second half.

AND THE DECLARATION LEFT NO TRACE, which is why nothing after the fact could
measure it either: `PANEL_BLIND_OF` and `PANEL_JOINT_OF` are environment
variables. Two fixes follow, and both are held here: the dispatcher now WRITES
`topology.json` before dispatch, and it refuses a new blind round while an
earlier one still owes its joint half.

THE DEBT FORM IS DELIBERATE. A blind round cannot be refused for lacking a joint
round at the moment it lands -- the joint round does not exist yet. The failure
that actually happened was opening a NEW blind round while owing one, 4 times in
2 days, so that is what is refused.
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
REGISTRY = REPO / "bench" / "directives" / "universal" / "joint_round_debt.json"
PRODUCER = REPO / "scripts" / "the_joint_round_was_almost_never_run_2026-10-08.py"


@pytest.fixture(scope="module")
def P():
    spec = importlib.util.spec_from_file_location("joint_dbt", PRODUCER)
    m = importlib.util.module_from_spec(spec)
    sys.modules["joint_dbt"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def D():
    # NO `PANEL_BRIEF_UNCHECKED` HERE, AND THAT IS DELIBERATE.
    #
    # A first version of this fixture did `os.environ.setdefault(
    # "PANEL_BRIEF_UNCHECKED", "1")` to get the module imported. `setdefault`
    # NEVER RESTORES, so the variable leaked into every test that ran after it in
    # the same process -- and that variable makes the dispatcher SKIP brief
    # validation. The guard it disabled is
    # `test_panel_brief_format_2026-09-09.py::test_the_dispatcher_REFUSES_a_bad_brief_before_paying_a_seat`,
    # whose whole purpose is to stop money being spent on a defective brief. It
    # passed alone and failed in the batch, which is how the leak was found.
    #
    # A22 moved the brief binding out of import time, so the variable is not needed
    # for an import at all: verified by importing this module with the variable
    # absent from the environment. Setting a flag that disables a money guard, to
    # solve a problem that no longer exists, is the kind of leftover this project's
    # additive standard exists to catch.
    argv = list(sys.argv)
    sys.argv = ["test", "_guard_only"]
    try:
        spec = importlib.util.spec_from_file_location(
            "cmp_joint", REPO / "bench" / "confer_maths_panel_2026-09-05.py")
        m = importlib.util.module_from_spec(spec)
        sys.modules["cmp_joint"] = m
        spec.loader.exec_module(m)
    finally:
        sys.argv = argv
    return m


class TestTheRegistryIsHonest:
    def test_it_exists_and_every_entry_carries_a_status_and_a_reason(self):
        d = json.loads(REGISTRY.read_text())
        assert d["entries"], "an empty registry would make the check vacuous"
        for r, v in d["entries"].items():
            assert v["status"] in ("OWED", "SUPERSEDED", "DISCHARGED"), (r, v)
            assert v.get("reason"), f"{r} carries no reason"
            if v["status"] == "SUPERSEDED":
                assert v.get("superseded_by"), (
                    f"{r} claims supersession and names no successor, which is a "
                    "waiver dressed as a discharge")

    def test_the_4_rounds_the_founder_caught_are_all_named(self):
        """These must not quietly vanish from the record."""
        d = json.loads(REGISTRY.read_text())
        for r in ("dynamic_roster_and_derived_ladder_2026-10-07",
                  "ladder_allocation_resolution_2026-10-07",
                  "rung_promotion_and_model_ids_2026-10-08",
                  "gamma_gates_everywhere_2026-10-08"):
            assert r in d["entries"], f"{r} is missing from the debt registry"


class TestTheRateIsMeasuredNotAsserted:
    def test_the_producer_reproduces_the_committed_figures(self, P):
        d = P.claim_the_joint_half_is_usually_missing()
        assert d["rounds_with_2_or_more_landed_replies"] >= 90, d
        assert d["paired_with_a_joint_round"] < d[
            "rounds_with_2_or_more_landed_replies"], (
            "if every round were paired this file would be measuring nothing")
        lo, hi = d["paired_wilson"]
        assert lo <= d["paired_rate"] <= hi, d

    def test_the_rate_since_the_ruling_is_reported_separately(self, P):
        """Pooling history with compliance would flatter the recent record."""
        d = P.claim_the_joint_half_is_usually_missing()
        assert d["ruling_date"] == "2026-10-06"
        assert d["since_the_ruling_total"] >= 1, d
        assert isinstance(d["since_the_ruling_missing"], list)

    def test_the_bound_direction_is_stated(self, P):
        """The pairing is name-based, so the count is an UPPER bound. Saying so
        is the difference between a measurement and an overclaim."""
        d = P.claim_the_joint_half_is_usually_missing()
        assert d["pairing_is_a_heuristic"] is True
        assert "UPPER bound" in d["bound_direction"]


class TestTheWriterIsWiredNotMerelyDefined:
    def test_the_topology_writer_is_called_from_main(self, P):
        d = P.claim_the_record_is_now_writable()
        assert d["wired"], d
        assert d["called_from_main"], (
            "an addition nothing reaches is not additive")

    def test_the_record_names_the_fields_an_audit_needs(self, D, tmp_path,
                                                        monkeypatch):
        """CALL the writer and read what it produced."""
        logs = tmp_path / "a_round_2026-10-08"
        logs.mkdir(parents=True)
        brief = logs / "BRIEF.md"
        brief.write_text("a brief\n")
        monkeypatch.setattr(D, "LOGS", logs, raising=False)
        monkeypatch.setattr(D, "BRIEF", brief, raising=False)
        monkeypatch.setattr(D, "MODELS", [("cc2", "opus", "claude_cli"),
                                          ("fable", "fable", "claude_cli")],
                            raising=False)
        out = D._write_topology_record()
        rec = json.loads(out.read_text())
        for k in ("round", "kind", "blind_of", "joint_of", "seats", "paid_seats",
                  "stagger_s", "brief_sha256"):
            assert k in rec, (k, rec)
        assert rec["kind"] in ("blind", "joint")
        assert rec["paid_seats"] == [], rec
        assert len(rec["brief_sha256"]) == 64, rec


class TestTheDebtCheckRefusesANewBlindRound:
    """The behaviour is a REFUSAL, so it is exercised by calling it."""

    def _registry(self, tmp_path, entries):
        d = tmp_path / "bench" / "directives" / "universal"
        d.mkdir(parents=True)
        (d / "joint_round_debt.json").write_text(json.dumps({"entries": entries}))
        return tmp_path

    def test_an_owed_round_refuses_a_new_blind_round(self, D, tmp_path, monkeypatch):
        root = self._registry(tmp_path, {"r1_2026-10-01": {"status": "OWED",
                                                           "reason": "x"}})
        monkeypatch.setattr(D, "_REPO", root, raising=False)
        monkeypatch.setattr(D, "_JOINT_OF", (), raising=False)
        monkeypatch.delenv("PANEL_SKIP_TOPOLOGY", raising=False)
        assert D._refuse_if_a_joint_round_is_owed() != 0

    def _joint_tree(self, tmp_path, parent, brief_text):
        """A registry with `parent` OWED, plus a logs tree for the joint round.

        ADDED 2026-10-14. The original version of the test below built only the
        registry, because the gate then looked no further than `PANEL_JOINT_OF`.
        It now reads the joint round's own BRIEF.md, so the tree has to exist.
        """
        root = self._registry(tmp_path, {parent: {"status": "OWED",
                                                  "reason": "x"}})
        logs = root / "bench" / "logs"
        body = "P" * 1200
        d = logs / parent
        d.mkdir(parents=True, exist_ok=True)
        (d / "BRIEF.md").write_text("parent brief")
        for seat in ("cc2", "fable"):
            (d / f"{seat}.json").write_text(json.dumps(
                {"ok": True, "chars": len(body), "response": body}))
        me = logs / f"joint_{parent}"
        me.mkdir(parents=True, exist_ok=True)
        (me / "BRIEF.md").write_text(brief_text.replace("<<REPLY>>", body))
        return root, me

    def test_a_joint_round_is_allowed_through_while_debt_stands(self, D, tmp_path,
                                                               monkeypatch):
        """Otherwise the only way to clear the debt would be blocked by it.

        THE ASSERTION WAS SHARPENED 2026-10-14, NOT WEAKENED. It used to pass on
        `PANEL_JOINT_OF` alone, which measured only that the operator had set an
        environment variable. A brief carrying none of the parent's words would
        satisfy it -- and on 2026-10-14 one did: CC1's joint brief for
        `his_rulings_2026-10-13` pointed at two directories that do not exist and
        was accepted as the joint half. The property this test exists to protect
        (the escape hatch must not be blocked by the thing it escapes) is kept
        and asserted below; what is added is that the hatch opens only for a
        brief that actually carries the parent's replies.
        """
        root, me = self._joint_tree(
            tmp_path, "r1_2026-10-01",
            "Here is the parent reply in full:\n<<REPLY>>")
        monkeypatch.setattr(D, "_REPO", root, raising=False)
        monkeypatch.setattr(D, "_JOINT_OF", ("r1_2026-10-01",), raising=False)
        monkeypatch.setattr(D, "_logs_dir", lambda: me, raising=False)
        monkeypatch.delenv("PANEL_SKIP_TOPOLOGY", raising=False)
        assert D._refuse_if_a_joint_round_is_owed() == 0, (
            "a joint round carrying its parent's replies must be allowed "
            "through, or the debt could never be discharged")

    def test_a_joint_round_quoting_nothing_is_NOT_allowed_through(
            self, D, tmp_path, monkeypatch):
        """The other half of the sharpened assertion above.

        Measured 2026-10-14: 2 of the 6 rounds carrying a recorded kind declared
        `joint` while `bench/star_topology_2026-10-06.py::round_kind` detected
        `blind`. Producer:
        `scripts/the_joint_debt_is_discharged_by_a_directory_2026-10-14.py`.
        """
        root, me = self._joint_tree(
            tmp_path, "r1_2026-10-01",
            "Read bench/logs/r1_2026-10-01/cc2/ and fable/ for the replies.")
        monkeypatch.setattr(D, "_REPO", root, raising=False)
        monkeypatch.setattr(D, "_JOINT_OF", ("r1_2026-10-01",), raising=False)
        monkeypatch.setattr(D, "_logs_dir", lambda: me, raising=False)
        monkeypatch.delenv("PANEL_SKIP_TOPOLOGY", raising=False)
        assert D._refuse_if_a_joint_round_is_owed() != 0, (
            "a brief that merely POINTS at the parent's replies is not the "
            "joint half: nothing checks that the seat read it")

    def test_superseded_entries_do_not_block(self, D, tmp_path, monkeypatch):
        root = self._registry(tmp_path, {"r1_2026-10-01": {
            "status": "SUPERSEDED", "superseded_by": "r2", "reason": "x"}})
        monkeypatch.setattr(D, "_REPO", root, raising=False)
        monkeypatch.setattr(D, "_JOINT_OF", (), raising=False)
        monkeypatch.delenv("PANEL_SKIP_TOPOLOGY", raising=False)
        assert D._refuse_if_a_joint_round_is_owed() == 0

    def test_an_unreadable_registry_refuses_rather_than_passes(self, D, tmp_path,
                                                              monkeypatch):
        """MUTATION-GRADE: a bare `except: return 0` would pass this file's other
        tests and silently disable the check on a corrupt registry."""
        d = tmp_path / "bench" / "directives" / "universal"
        d.mkdir(parents=True)
        (d / "joint_round_debt.json").write_text("{ not json")
        monkeypatch.setattr(D, "_REPO", tmp_path, raising=False)
        monkeypatch.setattr(D, "_JOINT_OF", (), raising=False)
        monkeypatch.delenv("PANEL_SKIP_TOPOLOGY", raising=False)
        assert D._refuse_if_a_joint_round_is_owed() != 0

    def test_an_explicit_override_is_honoured(self, D, tmp_path, monkeypatch):
        """An explicit override is a decision; a silent omission is not. That
        distinction is the whole point of the founder's ruling."""
        root = self._registry(tmp_path, {"r1_2026-10-01": {"status": "OWED",
                                                           "reason": "x"}})
        monkeypatch.setattr(D, "_REPO", root, raising=False)
        monkeypatch.setattr(D, "_JOINT_OF", (), raising=False)
        monkeypatch.setenv("PANEL_SKIP_TOPOLOGY", "1")
        assert D._refuse_if_a_joint_round_is_owed() == 0

    def test_the_live_registry_blocks_nothing_right_now(self, D):
        """The 4 real entries are SUPERSEDED, so the live tree must dispatch."""
        import os as _o
        prev = _o.environ.pop("PANEL_SKIP_TOPOLOGY", None)
        try:
            D._JOINT_OF = ()
            assert D._refuse_if_a_joint_round_is_owed() == 0, (
                "the live registry is blocking dispatch; if that is intended, run "
                "a joint round rather than editing the registry")
        finally:
            if prev is not None:
                _o.environ["PANEL_SKIP_TOPOLOGY"] = prev
