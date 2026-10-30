#!/usr/bin/env python3
"""A question's DIRECTION is derived from its anchor, and an absent anchor is loud.

WHY THIS GUARD EXISTS. Task entry B51 reports how many explanations are owed to
the founder and the figure had NO producer: it came from matching the word
"explain" anywhere in a ticket's text. The entry itself records that predicate
over-matching by 1, and a later check found it reaches 1 of the 11 live questions.
A number quoted to him with no script behind it is a claim about evidence rather
than evidence, which `measured-rate-travels-with-its-script` forbids in his words.

WHAT THE PRODUCER DOES INSTEAD. It reads the register's own `qs` kind, which
exists because he ruled on 2026-10-19 that a question carries its own hashed
identity, and splits by DIRECTION. That split is the useful part: a question of
his is work the assistant owes, a question of the assistant's is a decision he
owes, and conflating them is exactly how 7 of his questions came to be filed as
debts HE owed in a report of 2026-10-29.

THIS FILE IS ALSO WHAT MAKES THE PRODUCER REACHED. A script with no caller and no
test is the addition-nothing-reaches half of the additive standard, and this
project has 12 recorded instances of it, 1 of them from this same night.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PRODUCER = REPO / "scripts" / "what_questions_are_owed_2026-10-30.py"


def _mod():
    spec = importlib.util.spec_from_file_location("questions_owed", PRODUCER)
    m = importlib.util.module_from_spec(spec)
    sys.modules["questions_owed"] = m
    spec.loader.exec_module(m)
    return m


def test_the_producer_exists_and_is_where_the_entry_can_cite_it():
    assert PRODUCER.is_file(), f"the producer is absent: {PRODUCER}"


def test_help_answers_without_running_the_measurement():
    """A `--help` MUST NEVER COST ANYTHING.

    Measured across 15 of 17 runners that once billed for one, and a script
    written earlier this same night was caught by
    `bench/tests/test_help_is_answered_2026-09-11.py` for exactly this.
    """
    r = subprocess.run([sys.executable, str(PRODUCER), "--help"],
                       capture_output=True, text=True, cwd=str(REPO), timeout=120)
    assert r.returncode == 0, r.stderr[-300:]
    assert "usage:" in r.stdout, "no usage line: the flag ran the measurement"
    assert "live question" not in r.stdout, (
        "the help output contains measurement text, so --help did work")


class TestTheDirectionPredicate:
    """The predicate, exercised on SYNTHETIC anchors rather than on live data.

    Live data would make this test a restatement of whatever the register
    happens to hold today. Synthetic anchors test the RULE, so it keeps working
    when the register changes.
    """

    def test_a_responses_file_anchor_is_his(self):
        m = _mod()
        assert m.classify("Closing_Report_Overnight_Task_List_2026-10-17.txt#ab#0") == "his"
        assert m.classify("Decisions_Awaiting_You_2026-10-29.txt#95f20186#1") == "his"

    def test_a_chat_anchor_is_the_assistants(self):
        m = _mod()
        assert m.classify("chat#2026-10-29T18:55:17+00:00#5a290780") == "mine"

    def test_a_repository_artefact_anchor_is_the_assistants(self):
        m = _mod()
        for a in ("experimental_notes/CDSFL_MASTER_TASK_LIST.md",
                  "bench/routing.py", "scripts/register.py", "docs/GLOSSARY.md"):
            assert m.classify(a) == "mine", a

    def test_an_absent_anchor_is_UNATTRIBUTED_AND_NOT_DEFAULTED(self):
        """TASK C18's RULING, applied to a direction rather than an identity.

        An absent field must be LOUD, never defaulted. 1 of the 11 live
        questions carries no anchor and would fall through to "mine" by accident
        rather than by the rule -- and the assistant's own hand classification on
        2026-10-29 did exactly that, reporting 4 of its questions where the
        producer reports 3 and names the 4th as unattributable. Silently
        assigning it makes the totals add up and mean nothing.
        """
        m = _mod()
        for a in ("", "   ", None):
            assert m.classify(a) == "unattributed", repr(a)


def test_the_three_buckets_partition_the_live_questions():
    """ANTI-VACUITY: the split must account for every live question, exactly once."""
    m = _mod()
    g = m.collect()
    assert set(g) == {"his", "mine", "unattributed"}
    tids = [r["tid"] for v in g.values() for r in v]
    assert len(tids) == len(set(tids)), "a question appears in more than 1 bucket"

    sys.path.insert(0, str(REPO))
    from bench.ticket_store import TicketStore
    s = TicketStore()
    s.load()
    live_qs = {t.tid for t in s.live() if t.kind == "qs"}
    assert set(tids) == live_qs, (
        f"the split does not cover the live questions exactly: "
        f"missing {sorted(live_qs - set(tids))}, extra {sorted(set(tids) - live_qs)}")


def test_the_json_flag_is_wired_to_an_outcome():
    """A FLAG ACCEPTED AND IGNORED IS AN ADDITION NOTHING REACHES."""
    import json
    r = subprocess.run([sys.executable, str(PRODUCER), "--json"],
                       capture_output=True, text=True, cwd=str(REPO), timeout=300)
    assert r.returncode == 0, r.stderr[-300:]
    d = json.loads(r.stdout)
    assert set(d) >= {"total", "his", "mine", "unattributed"}
    assert d["total"] == len(d["his"]) + len(d["mine"]) + len(d["unattributed"])


def test_collect_ROUTES_each_question_the_way_classify_judges_it():
    """THE 2 FORMS MUST AGREE, and a mutation showed they need not.

    ★ ADDED 2026-10-30 after mutation testing found this hole in the guard
    above. `classify` is exercised directly on synthetic anchors and `collect`
    is exercised for coverage, but NOTHING compared them: re-routing the
    unattributed bucket into "mine" inside `collect` left all 8 tests green,
    which is the producer-and-consumer-disagree shape `execute-do-not-grep`
    names -- each form individually correct about itself and silently at odds.

    So this CALLS both and compares, for every live question, rather than
    asserting on either alone.
    """
    m = _mod()
    g = m.collect()
    for bucket, rows in g.items():
        for r in rows:
            judged = m.classify(r["anchor"])
            assert judged == bucket, (
                f"qs:{r['tid']} sits in the {bucket!r} bucket while classify() "
                f"judges its anchor {r['anchor']!r} as {judged!r}; collect() and "
                f"classify() disagree, so the split is not the predicate's")
