#!/usr/bin/env python3
"""`ds` is a ticket kind for his annotations and a SEAT NAME in chat.

HIS RULING, 2026-10-30, verbatim from his annotation of
`Decisions_Awaiting_You_2026-10-30.txt` line 187: *"If a comment I make has no
marker, and does not end with a question mark, then treat it as a ds. fr"*

THE COLLISION THIS GUARDS. `ds` is also the DeepSeek V4 Pro seat in the
dispatch table of `.claude/CLAUDE.md`. Measured by
`scripts/the_ds_label_and_the_kind_allowlist_2026-10-30.py`: 0 of his 794
annotations use it as a seat name, Wilson [0.000000, 0.004815], while 46 of 53
user-role transcript entries carrying the token do, Wilson [0.751597,
0.934521]. So the kind is admitted for annotations and refused for chat, and
BOTH halves are asserted here, because the chat half is currently safe only
because `MARKER` happens not to list `ds` -- accidental safety that anyone
deduplicating the kind vocabulary would remove.

EVERYTHING HERE EXECUTES THE LIVE CODE. Per `execute-do-not-grep`, a test that
reads the source of a regex asserts only that the regex describes itself. The 1
exception is `test_the_chat_marker_must_not_list_ds`, which inspects `MARKER`'s
own pattern DELIBERATELY: it is a ratchet against a future edit, and the
behavioural half of the same property is asserted beside it by calling
`raises_a_marker`.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def _load(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def reader():
    return _load(REPO / "scripts" / "read_founder_responses_2026-10-11.py", "rdr_ds")


@pytest.fixture(scope="module")
def harv():
    return _load(REPO / "scripts" / "harvest_tickets_2026-10-17.py", "harv_ds")


class TestTheVocabulary:
    def test_ds_is_a_kind(self):
        from bench.ticket_store import KINDS
        assert "ds" in KINDS

    def test_the_four_older_kinds_survive(self):
        from bench.ticket_store import KINDS
        for k in ("fr", "pf", "qs", "wr"):
            assert k in KINDS, f"{k} was lost"

    def test_the_store_declares_its_epoch(self):
        from bench.ticket_store import STORE_EPOCH
        assert STORE_EPOCH == "2026-10-17"

    def test_the_head_of_the_store_states_the_epoch_in_words(self):
        """His ruling was to mark it AT THE HEAD, so the docstring carries it."""
        import bench.ticket_store as ts
        # Whitespace-normalised: a docstring wraps, and his wording is the
        # property, not where the lines break.
        doc = " ".join((ts.__doc__ or "").split())
        assert "2026-10-17" in doc
        assert "17th of October 2026" in doc

    def test_a_kind_is_part_of_identity(self):
        """His 2026-10-19 ruling; `ds` must not collapse onto another kind."""
        from bench.ticket_store import tid_of, KINDS
        txt = "Please check anyway before proceeding."
        ids = {tid_of(k, txt, "B22") for k in KINDS}
        assert len(ids) == len(KINDS), "a kind collides"


class TestHisMarkerIsRead:
    @pytest.mark.parametrize("text,expect", [
        ("Please check anyway before proceeding. ds", "ds"),
        ("I accept your recommendation. fr", "fr"),
        ("Is this a repeat of the question already asked above? qs", "qs"),
        ("Put it to the free panel. qs,pf", "qs,pf"),
        ("The zero plant control will be run after. wr", "wr"),
    ])
    def test_a_trailing_marker_of_his_is_read(self, reader, text, expect):
        assert reader._marker_of(text) == expect

    def test_his_three_real_ds_annotations_are_read(self, reader):
        """The exact texts he wrote on 2026-10-30, read from his own file."""
        out = subprocess.run(
            [sys.executable,
             str(REPO / "scripts" / "read_founder_responses_2026-10-11.py"),
             "--since", "2026-10-30", "--json"],
            capture_output=True, text=True, cwd=str(REPO), check=True)
        anns = json.loads(out.stdout)["annotations"]
        mine = [a for a in anns if "Decisions_Awaiting_You" in a["file"]]
        assert mine, "his file is not being read at all"
        ds = [a for a in mine if (a.get("marker") or "").startswith("ds")]
        assert len(ds) >= 3, (
            f"{len(ds)} of his `ds` annotations read; he wrote 3 in that file")

    @pytest.mark.parametrize("text", [
        "Put it to the panel cx ge ds",
        "Run it past cc2, ds",
        "confer with cgpt ds",
        "ask fable, ds",
    ])
    def test_a_seat_list_ending_in_ds_is_not_his_marker(self, reader, text):
        assert reader._marker_of(text) == "", (
            "a dispatch instruction was read as a discussion marker")

    def test_the_seat_guard_does_not_swallow_a_real_marker(self, reader):
        """It must bite ONLY on an adjacent seat, not on any `ds` at all."""
        assert reader._marker_of("We discussed the cx route at length. ds") == "ds"


class TestHisDefaultRule:
    @pytest.mark.parametrize("text,expect", [
        ("Is this a repeat of the question already asked above?", "qs"),
        ("How do we avoid it?", "qs"),
        ("But is it earning it's keep?", "qs"),
        ("Please check anyway before proceeding.", "ds"),
        ("Then mark this clearly at the head of the ticket store.", "ds"),
        ("I chose option 1", "ds"),
    ])
    def test_the_unmarked_default(self, harv, text, expect):
        assert harv._unmarked_kind(text) == expect

    def test_pf_is_no_longer_a_default(self, harv):
        """The defect his complaint named: an unmarked comment became a repair."""
        for text in ("Please check anyway before proceeding.",
                     "Is this a question?"):
            assert harv._unmarked_kind(text) != "pf"

    def test_trailing_whitespace_does_not_defeat_the_question_rule(self, harv):
        assert harv._unmarked_kind("Is this a question?   \n") == "qs"


class TestTheAllowListIsTheVocabulary:
    """★ THE SECOND MUTATION THAT SURVIVED. The first version of this class
    restated the allow-list expression inside the test, so reverting the
    harvester to its hand-written ("fr", "pf", "qs") tuple left the file
    green. That is `execute-do-not-grep` broken by the test rather than by the
    product: a reimplementation agrees with itself. These call
    `from_responses`, which is where the allow-list actually decides."""

    @pytest.fixture(scope="class")
    def harvested(self, harv):
        # Below the epoch on purpose: `from_responses` takes the window it is
        # given, and his `wr` annotation is dated 2026-10-19. The epoch floor
        # is enforced in `main`, and is asserted separately.
        return harv.from_responses("2026-10-01")

    def test_his_wr_annotation_is_filed_as_wr_not_pf(self, harvested):
        rows = [r for r in harvested
                if r["source_ref"].endswith(
                    "Morning_Report_2026-10-19_GENERATED.txt:153")]
        assert rows, "his wr annotation is not being harvested at all"
        assert rows[0]["kind"] == "wr", (
            f"filed as {rows[0]['kind']}; the hand-written allow-list dropped "
            "`wr` and refiled it as a proposed fix")

    def test_his_ds_annotations_are_filed_as_ds(self, harvested):
        rows = [r for r in harvested if r["kind"] == "ds" and r["marked"]]
        assert len(rows) >= 3, (
            f"{len(rows)} explicitly-marked `ds` rows; he wrote 3 on 2026-10-30")

    def test_no_row_is_filed_pf_by_default_any_more(self, harvested):
        """His complaint: an unmarked comment became a proposed repair."""
        bad = [r for r in harvested if r["kind"] == "pf" and not r["marked"]]
        assert not bad, (
            f"{len(bad)} unmarked annotations still filed as proposed fixes, "
            f"e.g. {bad[0]['source_ref']}")


class TestChatRefusesDs:
    def test_chat_does_not_raise_on_a_bare_ds(self, harv):
        assert harv.raises_a_marker("we should talk about this\nds") is None

    def test_the_exclusion_is_REACHED_and_not_merely_present(self, harv,
                                                             monkeypatch):
        """★ THE MUTATION THAT SURVIVED, AND WHY THIS TEST EXISTS.

        Deleting the exclusion from `raises_a_marker` left this file GREEN,
        because `MARKER` does not list `ds` and so `marked_kind` returns None
        whatever the exclusion does. The test above therefore asserted
        MARKER's accidental silence, not the exclusion -- and an addition
        nothing reaches is not additive. This test simulates the exact future
        the exclusion exists for: a `MARKER` that DOES list `ds`, which is
        what deriving it from `KINDS` would produce. 46 of 53 user-role
        transcript entries carrying the token use it as a seat name, so in
        that future the exclusion is the only thing standing between a
        dispatch prompt and a ticket.
        """
        import re
        widened = re.compile(
            harv.MARKER.pattern.replace("(fr|pf|qs|wr)", "(fr|pf|qs|wr|ds)"),
            harv.MARKER.flags)
        assert "ds" in widened.pattern
        monkeypatch.setattr(harv, "MARKER", widened)
        # The widening must really reach `ds`, or this test is hollow too.
        assert harv.marked_kind("we should talk about this\nds") == "ds"
        assert harv.raises_a_marker("we should talk about this\nds") is None, (
            "with `ds` in MARKER, the chat half raised on a seat name")
        assert harv.raises_a_marker("we should build this\nfr") == "fr"

    def test_chat_still_raises_on_the_other_kinds(self, harv):
        for k in ("fr", "pf", "qs", "wr"):
            assert harv.raises_a_marker(f"we should do this\n{k}") == k, (
                f"chat stopped raising on {k}")

    def test_ds_is_named_as_excluded_rather_than_merely_absent(self, harv):
        assert "ds" in harv.CHAT_EXCLUDED_KINDS

    def test_the_chat_marker_must_not_list_ds(self, harv):
        """A RATCHET, and deliberately a source assertion -- see the module
        docstring. Deriving `MARKER` from `KINDS` to remove the duplicate
        vocabulary would reintroduce a collision realised in 46 of 53
        transcript entries. The behavioural assertion above covers the
        present; this one covers the next edit."""
        assert "ds" not in harv.MARKER.pattern, (
            "MARKER lists `ds`; the exclusion in raises_a_marker is now the "
            "only thing standing between a dispatch prompt and a ticket")


class TestTheEpochIsAFloorNotADefault:
    def test_a_caller_cannot_argue_below_the_epoch(self, tmp_path):
        from bench.ticket_store import STORE_EPOCH
        out = subprocess.run(
            [sys.executable,
             str(REPO / "scripts" / "harvest_tickets_2026-10-17.py"),
             "--since", "2026-08-01", "--sources", "responses",
             "--store", str(tmp_path / "t.jsonl")],
            capture_output=True, text=True, cwd=str(REPO))
        assert out.returncode == 0, out.stderr[-600:]
        assert STORE_EPOCH in out.stdout
        assert "raised to the epoch" in out.stdout

    def test_the_default_window_is_the_epoch(self):
        from bench.ticket_store import STORE_EPOCH
        src = (REPO / "scripts" / "harvest_tickets_2026-10-17.py").read_text()
        assert 'default=STORE_EPOCH' in src
        assert '"2026-10-01"' not in src.split("def main")[-1]
        assert STORE_EPOCH == "2026-10-17"


class TestRegisterReachesTheNewKind:
    def test_the_cli_accepts_ds(self):
        out = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "register.py"),
             "--kind", "ds", "--summary"],
            capture_output=True, text=True, cwd=str(REPO))
        assert out.returncode == 0, out.stderr[-500:]

    def test_the_cli_lists_every_kind_when_it_refuses_one(self):
        out = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "register.py"),
             "--kind", "definitely-not-a-kind", "--summary"],
            capture_output=True, text=True, cwd=str(REPO))
        assert out.returncode != 0
        from bench.ticket_store import KINDS
        for k in KINDS:
            assert k in out.stderr, f"{k} missing from the refusal"


class TestAReclassificationIsNotASecondTicket:
    PRODUCER = "a_reclassification_is_not_a_second_ticket_2026-10-30.py"

    def test_the_live_store_has_no_open_duplicate_pair_left(self):
        """The 94 pairs the kind change created must not be in the queue."""
        import collections
        from bench.ticket_store import TicketStore, LIVE
        store = TicketStore()
        by_anchor = collections.defaultdict(list)
        for t in store.all():
            if getattr(t, "anchor", "") and t.status in LIVE:
                by_anchor[t.anchor].append(t)
        bad = {a: sorted({t.kind for t in v}) for a, v in by_anchor.items()
               if len({t.kind for t in v}) > 1}
        assert not bad, f"{len(bad)} anchors still carry 2 open kinds: " \
                        f"{list(bad.items())[:4]}"

    def test_the_repair_is_idempotent(self):
        out = subprocess.run(
            [sys.executable, str(REPO / "scripts" / self.PRODUCER)],
            capture_output=True, text=True, cwd=str(REPO))
        assert out.returncode == 0, out.stderr[-500:]
        assert "deprecations planned: 0" in out.stdout, (
            "a second run would deprecate again; it is not idempotent")

    def test_a_deprecated_row_keeps_its_evidence(self):
        from bench.ticket_store import TicketStore
        store = TicketStore()
        dep = [t for t in store.all() if getattr(t, "superseded_by", "")
               and self.PRODUCER in getattr(t, "supersession_evidence", "")]
        assert len(dep) >= 94, f"{len(dep)} rows carry the producer's evidence"
        for t in dep[:5]:
            assert t.superseded_by and t.superseded_by != t.tid


class TestUndeprecateUndoesOnlyADeprecation:
    """`TicketStore.undeprecate`, added 2026-10-30 because a deprecation made
    in error had no way back. Exercised against a TEMPORARY store, so these
    tests never write to the live one."""

    @staticmethod
    def _two(tmp_path):
        from bench.ticket_store import TicketStore
        st = TicketStore(str(tmp_path / "t.jsonl"))
        # `propose` returns (ticket, outcome), not a ticket.
        a, _ = st.propose("pf", "First", "He marked this one pf explicitly.",
                          "responses", anchor="f.txt#aaaa#0")
        b, _ = st.propose("ds", "Second", "A kind derived by guesswork.",
                          "responses", anchor="f.txt#bbbb#0")
        return st, a, b

    REASON = ("The deprecation overrode an explicit marker of his, which this "
              "mechanism must never do; recorded with its producer.")

    def test_a_deprecated_row_comes_back_unconfirmed(self, tmp_path):
        st, a, b = self._two(tmp_path)
        st.deprecate(a.tid, b.tid, "x" * 40)
        assert st.get(a.tid).status == "DEPRECATED"
        back = st.undeprecate(a.tid, self.REASON)
        assert back.status == "UNCONFIRMED"

    def test_the_supersession_link_is_cleared(self, tmp_path):
        st, a, b = self._two(tmp_path)
        st.deprecate(a.tid, b.tid, "x" * 40)
        back = st.undeprecate(a.tid, self.REASON)
        assert back.superseded_by == ""
        assert back.supersession_evidence == ""

    def test_the_reason_survives_on_the_record(self, tmp_path):
        st, a, b = self._two(tmp_path)
        st.deprecate(a.tid, b.tid, "x" * 40)
        back = st.undeprecate(a.tid, self.REASON)
        assert any("UNDEPRECATED" in n for n in back.notes)

    def test_it_refuses_a_row_that_is_not_deprecated(self, tmp_path):
        st, a, _ = self._two(tmp_path)
        with pytest.raises(ValueError, match="not DEPRECATED"):
            st.undeprecate(a.tid, self.REASON)

    def test_it_cannot_resurrect_a_closed_ticket(self, tmp_path):
        """The property `reopen`'s founder-only guard protects."""
        st, a, _ = self._two(tmp_path)
        st.close(a.tid, "done", "verified by execution on a temporary store")
        with pytest.raises(ValueError, match="not DEPRECATED"):
            st.undeprecate(a.tid, self.REASON)

    def test_it_refuses_an_unexplained_undo(self, tmp_path):
        st, a, b = self._two(tmp_path)
        st.deprecate(a.tid, b.tid, "x" * 40)
        with pytest.raises(ValueError, match="reason"):
            st.undeprecate(a.tid, "oops")

    def test_it_refuses_an_unknown_ticket(self, tmp_path):
        st, _, _ = self._two(tmp_path)
        with pytest.raises(KeyError):
            st.undeprecate("0" * 12, self.REASON)

    def test_the_live_store_records_the_one_real_correction(self):
        """The error this method was built for must stay auditable."""
        from bench.ticket_store import TicketStore
        st = TicketStore()
        got = [t for t in st.all()
               if any("UNDEPRECATED" in n for n in getattr(t, "notes", []))]
        assert got, "the 2026-10-30 correction is no longer on the record"
        assert any("own-line marker" in n for t in got for n in t.notes)
