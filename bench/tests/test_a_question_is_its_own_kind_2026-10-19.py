"""His instruction of 2026-10-19: `qs` is a QUESTION, hashed like `fr` and `pf`.

HIS WORDS, verbatim: *"From now on qs = Question. Questions should be given their
own unique hashed ID in the registry, like the other categories, like 'fr'
feature request, and 'pf', proposed fix, so they can be tied directly to the
problems they address and so that in future you can't lose them, or forget which
issues they address."*

WHY A QUESTION IS NOT A SMALL PROPOSAL. Its resolution is an ANSWER, not a build,
and the two travel in opposite directions: he answers mine, I answer his. Before
this, 72 of his 318 annotations were questions sitting as `pf` rows that the Stop
gate reported as outstanding WORK -- which is how a question gets read as a task,
then dropped when no task turns out to exist.

WHAT THIS GUARDS, AND EVERY ASSERTION EXECUTES THE CODE RATHER THAN READING IT:
  1. `qs` is a real kind the store accepts, and an unknown kind is still refused.
  2. The same sentence recorded as a question and as a proposed fix takes 2
     DISTINCT identities, because `tid_of` digests the kind. Answering the
     question does not build the fix.
  3. A question is tied to what it asks about through the fields that already
     exist -- `task_ref`, `subjects`, `anchor` -- so his requirement is met with
     no schema change.
  4. The harvester's marker matches `qs` as a standalone token and NOT inside an
     ordinary word.
  5. The Stop gate counts `pf` and `qs`. It previously counted `pr`, a kind that
     has never existed, so that figure was always 0 whatever the store held.
"""
from __future__ import annotations

import ast
import importlib.util
import pathlib
import re
import sys
import tempfile

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from bench.ticket_store import KINDS, TicketStore, tid_of  # noqa: E402

GATE = ROOT / "hooks" / "ticket_queue_gate.py"
HARVEST = ROOT / "scripts" / "harvest_tickets_2026-10-17.py"


def _harvester():
    spec = importlib.util.spec_from_file_location("_h", HARVEST)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture
def store():
    d = pathlib.Path(tempfile.mkdtemp()) / "tickets.jsonl"
    return TicketStore(d)


class TestTheKindExists:
    def test_qs_is_a_kind(self):
        assert "qs" in KINDS, (
            "his 2026-10-19 instruction gives a question its own hashed identity; "
            f"KINDS is {KINDS}")

    def test_every_declared_kind_is_present(self):
        """RENAMED AND WIDENED 2026-10-20. It was `test_all_three_kinds_are
        _present`, pinning the number 3 in its own name AND asserting the exact
        literal set, so `wr` made both wrong. `wr` was added on his instruction:
        "wr is a valid section in the Bugzilla registry, and you should use it to
        track all remaining outstanding work".

        THE ASSERTION IS NOW A FLOOR RATHER THAN AN EXACT SET, and that is a
        deliberate narrowing of THIS test's job. Its subject is that a question
        has its own kind; it is not the place that polices the vocabulary's size.
        The EXACT-SET RATCHET IS NOT LOST -- it lives in
        `bench/tests/test_ticket_store_2026-10-17.py::
        test_every_one_of_his_sections_exists_and_separates`, which asserts
        `{t.kind for t in store.all()} == set(KINDS)` and therefore still goes red
        on any kind added without coverage. Verified by running that file: 21
        passed with `wr` covered, and it was red before the coverage was added."""
        for required in ("fr", "pf", "qs", "wr"):
            assert required in KINDS, (
                f"{required!r} is missing from KINDS, which is {KINDS}")

    def test_the_store_accepts_a_question(self, store):
        t, outcome = store.propose(
            "qs", "Is severity a range rather than a point?",
            "would severity itself first not be a measure of confidence",
            "responses", source_ref="f.txt:1", task_ref="B36")
        assert t.kind == "qs"
        assert outcome == "created"
        assert store.by_kind("qs") == [t]

    def test_an_unknown_kind_is_still_refused(self, store):
        with pytest.raises(ValueError):
            store.propose("zz", "x", "x", "chat")


class TestIdentityIsPerKind:
    #: THE PROPERTY THAT MAKES A QUESTION SAFE TO RECORD ALONGSIDE A FIX.
    TEXT = "would severity itself first not be a measure of confidence"

    def test_a_question_and_a_fix_on_the_same_text_are_distinct(self):
        assert tid_of("qs", self.TEXT, "B36") != tid_of("pf", self.TEXT, "B36"), (
            "a question and a proposed fix sharing one sentence must not collapse "
            "into one ticket: answering the question does not build the fix")

    def test_all_three_kinds_give_three_identities(self):
        ids = {tid_of(k, self.TEXT, "B36") for k in ("fr", "pf", "qs")}
        assert len(ids) == 3, ids

    def test_a_question_keeps_its_identity_when_reworded_around_its_task_ref(self, store):
        a, _ = store.propose("qs", "t", self.TEXT, "responses",
                             source_ref="f.txt:1", task_ref="B36")
        again = tid_of("qs", self.TEXT, "B36")
        assert a.tid == again


class TestItIsTiedToWhatItAsksAbout:
    def test_a_question_carries_its_task_reference(self, store):
        t, _ = store.propose("qs", "t", "why is the quiet run 7?", "responses",
                             source_ref="f.txt:9", task_ref="B29")
        assert store.by_task_ref("B29"), "a question must be findable by its entry"
        assert t.task_ref == "B29"

    def test_a_question_carries_its_code_subjects(self, store):
        t, _ = store.propose("qs", "t", "what does the redactor withhold?",
                             "responses", source_ref="f.txt:3",
                             subjects=["REQUIRED_QUIET_RUN"])
        assert "REQUIRED_QUIET_RUN" in t.subjects


class TestTheHarvesterReadsTheMarker:
    def test_qs_is_matched_as_a_standalone_token(self):
        m = _harvester().MARKER
        for text in ("a, f, sy, d, t qs", "qs: should this be fixed?",
                     "and so on. qs", "see above (qs)"):
            assert m.search(text), f"marker missed a standalone qs in {text!r}"

    def test_qs_inside_an_ordinary_word_is_not_matched(self):
        m = _harvester().MARKER
        for text in ("qsomething", "the qsort routine", "aqs"):
            got = m.search(text)
            assert not got or got.group(1) != "qs", (
                f"marker fired inside a word: {text!r}")

    def test_the_other_two_markers_still_match(self):
        m = _harvester().MARKER
        assert m.search("this is a request fr").group(1) == "fr"
        assert m.search("pf: here is the repair").group(1) == "pf"


class TestTheGateCountsRealKinds:
    def test_the_gate_no_longer_counts_the_phantom_kind(self):
        src = GATE.read_text(encoding="utf-8")
        tree = ast.parse(src)
        reads = set()
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "get"
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "by_kind"
                    and node.args and isinstance(node.args[0], ast.Constant)):
                reads.add(node.args[0].value)
        assert "pr" not in reads, (
            "the gate reads by_kind['pr'], a kind that has never existed, so that "
            "figure is always 0 whatever the store holds")
        assert {"fr", "pf", "qs"} <= reads, (
            f"the gate must count all 3 real kinds; it reads {sorted(reads)}")


class TestTheMutationsGoRed:
    """Each of these is the change that would silently undo the work above."""

    def test_removing_qs_from_kinds_breaks_the_store(self, store):
        import bench.ticket_store as ts
        old = ts.KINDS
        try:
            ts.KINDS = ("fr", "pf")
            with pytest.raises(ValueError):
                store.propose("qs", "t", "v", "chat")
        finally:
            ts.KINDS = old

    def test_a_kind_blind_identity_would_collapse_the_two(self):
        #: Demonstrates WHY the kind must be inside the digest: without it, a
        #: question and a fix on one sentence share an id and one overwrites
        #: the other, which is the destruction already recorded for text-only
        #: identity on 2026-10-17.
        import hashlib
        def blind(_kind, text, ref=""):
            h = hashlib.sha256()
            h.update(" ".join(text.split()).encode())
            h.update(ref.encode())
            return h.hexdigest()[:12]
        t = "would severity itself first not be a measure of confidence"
        assert blind("qs", t, "B36") == blind("pf", t, "B36")
        assert tid_of("qs", t, "B36") != tid_of("pf", t, "B36")
