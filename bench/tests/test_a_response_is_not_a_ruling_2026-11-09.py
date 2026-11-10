"""`responded:` records that he REPLIED; `ruled:` SETTLES. They must not merge.

WHY THIS EXISTS. On 2026-11-09, 8 of 14 live task-list entries carried a ruling
in their PROSE that the marker did not hold, so every machine surface believed
he had never replied and the original question was put to him again. The
obvious repair -- write the date into `ruled:` -- was tried and FALSIFIED the
same hour: `morning_report_build.decisions()` routes any entry carrying a
`ruled:` date to `no_ruling_needed` unless `ruling_is_spent` says otherwise, so
backfilling 5 entries REMOVED all 5 from the decision list while each still
asked him something. `bench/tests/test_the_two_decision_surfaces_cannot_diverge_2026-11-01.py`
caught it and all 5 were reverted.

THESE TESTS EXECUTE. None asserts on source text. The suppression test calls
the real routing predicate, and the rendering test calls the real renderer and
reads its output string, because a producer and a consumer that disagree are
each individually correct and only running both can see it.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, REPO / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def tlm():
    return _load("tlm_resp", "scripts/task_list_markers.py")


@pytest.fixture(scope="module")
def mrb():
    return _load("mrb_resp", "scripts/morning_report_build_2026-10-12.py")


@pytest.fixture(scope="module")
def bdf():
    return _load("bdf_resp", "scripts/build_decisions_file_2026-11-07.py")


class TestTheFieldExistsAndParses:
    def test_the_marker_pattern_reads_responded(self, tlm):
        m = tlm.MARKER.match(
            "<!-- task: Z9 | state: OPEN | status: PROPOSED | ruled: 2026-01-01 "
            "| responded: 2026-02-02 -->")
        assert m is not None, "the extended marker no longer parses"
        assert m.group(5).strip() == "2026-01-01"
        assert m.group(6).strip() == "2026-02-02", (
            "group 6 must be `responded`; if this is None the field was removed")

    def test_a_marker_without_responded_still_parses(self, tlm):
        m = tlm.MARKER.match("<!-- task: Z9 | state: OPEN | status: PROPOSED -->")
        assert m is not None and (m.group(6) or "") == "", (
            "the field must stay OPTIONAL -- an entry predating it cannot break")

    def test_the_entry_carries_the_field(self, tlm):
        assert "responded" in tlm.Entry.__dataclass_fields__, (
            "Entry lost the `responded` field, so nothing downstream can read it")

    def test_the_live_list_parses_and_some_entry_uses_it(self, tlm):
        es = tlm.parse_entries()
        assert len(es) > 200, "the live list stopped parsing"
        used = [e.ident for e in es if e.responded]
        assert used, (
            "no live entry carries `responded:`, so this field is an addition "
            "nothing reaches -- the failure mode `additive-standard` names")


def _row(rows, **over):
    """A real row with fields overridden, so the schema can never drift.

    ★ WHY SYNTHETIC ROWS. The 5 tests below used the LIVE decision queue and 5
    of them were RED on 2026-11-10 -- 2 because the configuration they need
    (`responded` with NO `ruled`) has 0 live instances, and 3 because they
    asserted the reply note for any row carrying a reply date, which
    contradicts the renderer's deliberate precedence. A guard whose subject
    depends on today's queue reports the queue, not the code; and this file was
    off the commit gate, so it had been red unnoticed.
    """
    base = dict(rows[0])
    base.update(over)
    return base


class TestAResponseNeverSuppresses:
    """The whole point. A `ruled` date silences an entry; a `responded` must not."""

    def test_a_reply_without_a_ruling_is_not_treated_as_a_ruling(self, tlm):
        """The PARSE-level contract, on a marker this test writes itself."""
        m = tlm.MARKER.match(
            "<!-- task: Z8 | state: OPEN | status: PROPOSED "
            "| responded: 2026-02-02 -->")
        assert m is not None
        assert (m.group(5) or "").strip() == "", (
            "a reply date leaked into the `ruled` group, which would silence "
            "the entry")
        assert (m.group(6) or "").strip() == "2026-02-02"

    def test_a_reply_without_a_ruling_now_has_a_live_instance(self, tlm, bdf):
        """★ THIS TEST WAS A RATCHET ON 0 AND IS NOW A CHECK ON 1 OR MORE.

        When it was written on 2026-11-10 it asserted that NO live entry
        carried `responded:` without `ruled:`, because all 7 that carried a
        reply date also carried a ruling date -- so the configuration the field
        was built for had 0 instances and the renderer's reply note was
        unreachable on real data. Its own message said that when the answer
        changed, the reply note should be run against the live case.

        IT CHANGED WITHIN THE HOUR, AND BY MY OWN MISTAKE. B141 was raised with
        `ruled: 2026-11-10` on its marker because he had instructed half of it
        -- and a ruling date SUPPRESSES an entry, which is the whole of N1's
        finding. The two-surface guard caught it: *1 authored decision carries
        a spoken_heading and is rendered nowhere*. Corrected to `responded:`,
        which is exactly what the field exists for, and the entry reaches him
        again.
        """
        live = [e for e in tlm.parse_entries()
                if e.responded and not e.ruled
                and (e.state or "").upper() not in ("DONE", "WITHDRAWN")]
        if not live:
            pytest.skip(
                "no live entry carries a reply without a ruling; the field's "
                "own configuration has 0 instances again, which is a state "
                "rather than a fault")
        mrb_mod, rows = bdf.collect()
        rendered = {r["ident"] for r in rows}
        missing = [e.ident for e in live if e.ident not in rendered]
        assert not missing, (
            f"these entries carry a reply, no ruling, and reach him nowhere: "
            f"{missing} — a reply must never suppress an entry")
        out = bdf.render(mrb_mod, rows, spoken=True)
        assert "You responded on this on" in out, (
            f"{[e.ident for e in live]} carry a reply with no ruling and the "
            f"spoken file does not say so, which is the N1 defect")

    def test_every_responder_still_reaches_the_decision_list(self, mrb, tlm):
        """A reply must never remove an entry from the queue he reads."""
        es = {e.ident: e for e in tlm.parse_entries()}
        responders = {i for i, e in es.items()
                      if e.responded
                      and (e.state or "").upper() not in ("DONE", "WITHDRAWN")}
        assert responders, "no OPEN entry carries a reply date at all"
        got = {d.get("ident") for d in mrb.decisions(mrb.task_items())[0]}
        missing = sorted(responders - got)
        assert not missing, (
            f"these entries carry a reply and vanished from the decision "
            f"list, which is the suppression this field exists to avoid: "
            f"{missing}")

    def test_task_items_carries_it_through(self, mrb):
        items = {i["ident"]: i for i in mrb.task_items()}
        assert any("responded" in v for v in items.values()), (
            "task_items dropped `responded`, so the renderer can never see it")


class TestTheRenderedFileSaysSo:
    """Execute the renderer and read its OUTPUT, never its source."""

    def test_a_ruled_entry_is_told_it_was_ruled(self, bdf):
        """★ THE DEFECT THIS CAUGHT, 2026-11-10. The `if r["ruled"]` branch
        BUILT its note and never emitted it -- both `A(...)` calls sat inside
        the `elif`. Measured on the live queue before the fix: 6 rows carried a
        ruling date and the note was emitted for 0 of them, so 36,943 bytes of
        the file he reads carried 0 mentions of his having ruled on 6 of the 7
        decisions put to him."""
        mrb_mod, rows = bdf.collect()
        r = _row(rows, ruled="2026-11-08", responded="", owed="the tier split")
        for spoken in (True, False):
            out = bdf.render(mrb_mod, [r], spoken=spoken)
            assert "You ruled on this entry on 2026-11-08" in out, (
                f"the {'spoken' if spoken else 'written'} surface drops the "
                f"ruling note; he reads both")
            assert "the tier split" in out, "what is still owed is not named"

    def test_a_reply_without_a_ruling_gets_the_reply_note(self, bdf):
        mrb_mod, rows = bdf.collect()
        r = _row(rows, ruled="", responded="2026-11-08", owed="his ruling")
        for spoken in (True, False):
            out = bdf.render(mrb_mod, [r], spoken=spoken)
            assert "You responded on this on 2026-11-08" in out, (
                f"the {'spoken' if spoken else 'written'} surface lost the "
                f"reply note; he reads both")
            assert "still open" in out, (
                "the note must say the entry is STILL OPEN, or it reads as a "
                "closure")

    def test_a_ruling_takes_precedence_over_a_reply_on_the_same_entry(self, bdf):
        """DELIBERATE, not an oversight. The ruling note already says the
        ruling was on a different question and names what is owed, so emitting
        both would be redundant and would read as self-contradicting."""
        mrb_mod, rows = bdf.collect()
        r = _row(rows, ruled="2026-11-08", responded="2026-11-08",
                 owed="the bound")
        out = bdf.render(mrb_mod, [r], spoken=True)
        assert "You ruled on this entry on" in out, out[:200]
        assert "You responded on this on" not in out, (
            "both notes were emitted for one entry; the precedence is the "
            "design, so if it is being changed this test must change with it")

    def test_an_entry_with_neither_date_gets_no_note(self, bdf):
        """ANTI-VACUITY: if a note appeared unconditionally, every assertion
        above would pass for the wrong reason."""
        mrb_mod, rows = bdf.collect()
        r = _row(rows, ruled="", responded="")
        out = bdf.render(mrb_mod, [r], spoken=True)
        assert "You ruled on this entry on" not in out
        assert "You responded on this on" not in out

    def test_the_live_queue_now_carries_the_ruling_note(self, bdf):
        """The observable outcome on the file he actually receives."""
        mrb_mod, rows = bdf.collect()
        n_ruled = sum(1 for r in rows if r["ruled"])
        if not n_ruled:
            pytest.skip("no queued decision carries a ruling date")
        out = bdf.render(mrb_mod, rows, spoken=True)
        assert out.count("You ruled on this entry on") == n_ruled, (
            f"{n_ruled} rows carry a ruling date but the file mentions it "
            f"{out.count('You ruled on this entry on')} time(s)")

    def test_a_ruling_note_and_a_reply_note_are_different_sentences(self, bdf):
        """BOTH BRANCHES REACHABLE, each on its own row -- which is not the
        same as both appearing for ONE row.

        ★ THIS TEST ACCUSED CORRECT CODE AND IS CORRECTED, 2026-11-10. It read
        that if the ruling note appears the reply note must appear in the same
        render, which is false by design: the precedence gives a row with both
        dates the ruling note alone, and today ALL 3 rows carrying a reply date
        also carry a ruling date, so a single render of the live queue can
        never satisfy it. Before the emit was repaired it passed VACUOUSLY,
        because the ruling note appeared 0 times and the `if` never ran -- a
        test green for the absence of the thing it was checking.

        The property that is true and worth holding is that the 2 notes are
        DISTINCT SENTENCES and each is reachable, so that is what is asserted,
        on 2 rows built for the purpose.
        """
        mrb_mod, rows = bdf.collect()
        ruled_out = bdf.render(
            mrb_mod, [_row(rows, ruled="2026-11-08", responded="")],
            spoken=True)
        reply_out = bdf.render(
            mrb_mod, [_row(rows, ruled="", responded="2026-11-08")],
            spoken=True)
        assert "You ruled on this entry on" in ruled_out
        assert "You responded on this on" in reply_out
        assert "You responded on this on" not in ruled_out
        assert "You ruled on this entry on" not in reply_out

class TestTheWritePathKeepsThemApart:
    """★ ADDED AFTER A MUTATION SURVIVED, 2026-11-09.

    The first version of this file read markers from disk and never called
    `set_marker`, so the mutation `new_ruled = new_ruled or responded` -- the
    exact repair that was falsified an hour earlier -- left all 11 tests GREEN.
    A guard that cannot see the defect it was written for is the failure
    `execute-do-not-grep` names. These tests WRITE and read back.
    """

    def _scratch(self, tmp_path, tlm):
        dst = tmp_path / "list.md"
        dst.write_text(
            "**Z9. A planted entry.**\n"
            "<!-- task: Z9 | state: OPEN | status: PROPOSED -->\n",
            encoding="utf-8")
        return dst

    def test_a_reply_lands_in_responded_and_not_in_ruled(self, tlm, tmp_path):
        dst = self._scratch(tmp_path, tlm)
        line = tlm.set_marker("Z9", responded="2026-02-02", path=dst)
        assert "responded: 2026-02-02" in line, (
            f"set_marker did not write the reply date as `responded`: {line}")
        assert "ruled:" not in line, (
            f"A REPLY WAS WRITTEN AS A RULING, which SUPPRESSES the entry. "
            f"This is the repair that was tried and falsified on 2026-11-09: "
            f"{line}")
        e = tlm.parse_entries(dst)[0]
        assert e.responded == "2026-02-02" and e.ruled is None

    def test_a_ruling_still_lands_in_ruled(self, tlm, tmp_path):
        dst = self._scratch(tmp_path, tlm)
        line = tlm.set_marker("Z9", ruled="2026-03-03", path=dst)
        assert "ruled: 2026-03-03" in line and "responded:" not in line, line
        e = tlm.parse_entries(dst)[0]
        assert e.ruled == "2026-03-03" and e.responded is None

    def test_both_can_coexist_and_neither_eats_the_other(self, tlm, tmp_path):
        dst = self._scratch(tmp_path, tlm)
        tlm.set_marker("Z9", ruled="2026-03-03", path=dst)
        tlm.set_marker("Z9", responded="2026-04-04", path=dst)
        e = tlm.parse_entries(dst)[0]
        assert e.ruled == "2026-03-03", "writing a reply dropped his ruling date"
        assert e.responded == "2026-04-04"

    def test_advancing_state_carries_both_over(self, tlm, tmp_path):
        dst = self._scratch(tmp_path, tlm)
        tlm.set_marker("Z9", ruled="2026-03-03", responded="2026-04-04", path=dst)
        tlm.set_marker("Z9", status="TESTED", path=dst)
        e = tlm.parse_entries(dst)[0]
        assert (e.ruled, e.responded) == ("2026-03-03", "2026-04-04"), (
            "advancing status silently dropped a date the founder earned")


# ─────────────────────────────────────────────────────────────────────────────
# WHAT IS STILL OWED must be NAMED, not deferred to "recorded in the entry".
#
# ★ MEASURED 2026-11-10. `collect()` read `d.get("still_owed")` from the
# authored detail file and that key is present on **1 of 24** detail entries,
# `task:B77`. So 6 of the 7 live decisions ended their ruling note with
# *"What is still owed is recorded in the entry."* -- a non-answer in the one
# sentence that tells him what to decide. Nothing had noticed because the note
# carrying it was itself never emitted: the `if r["ruled"]` branch built the
# string and threw it away.
#
# THE REPAIR DERIVES FROM THE ENTRY'S OWN EXPLICIT MARKER, never from a shape.
# After the emit was fixed and the derivation added, 4 of 7 decisions name what
# is owed. The remaining 3 entries do not state it, and the honest fallback
# stands rather than a guess being put under that heading.
# ─────────────────────────────────────────────────────────────────────────────

class TestWhatIsOwedIsNamed:

    def test_the_marker_is_read_and_its_text_returned(self, bdf):
        got = bdf.derive_still_owed(
            "**B1. T.** noise **WHAT IS STILL OWED:** his ruling on the tier "
            "split, which is a budget question. **NEXT THING**")
        assert got == ("his ruling on the tier split, which is a budget "
                       "question."), repr(got)

    def test_all_three_observed_spellings_are_accepted(self, bdf):
        for head in ("WHAT IS STILL OWED:",
                     "AND WHAT IS STILL OWED, RESTATED HERE:",
                     "★ WHAT IS ACTUALLY OWED:"):
            got = bdf.derive_still_owed(
                f"**B1. T.** **{head}** a decision from him on the bound, "
                f"which is an execution budget. **END**")
            assert "decision from him on the bound" in got, (head, got)

    def test_no_marker_means_no_claim(self, bdf):
        """CONSERVATIVE BY DESIGN: this text goes under the heading *what is
        still owed*, so a guess there misinforms the decision."""
        assert bdf.derive_still_owed("**B1. T.** prose with no marker") == ""
        assert bdf.derive_still_owed("") == ""

    def test_the_last_marker_wins(self, bdf):
        """Entries are APPENDED to, so the freshest statement is operative."""
        got = bdf.derive_still_owed(
            "**B1. T.** **WHAT IS STILL OWED:** the older statement, long "
            "since superseded by events. **★ LATER** "
            "**WHAT IS STILL OWED:** the newer statement, which is the live "
            "one today. **END**")
        assert "newer statement" in got, got
        assert "older statement" not in got, got

    def test_a_long_statement_is_cut_and_never_dropped(self, bdf):
        """★ MY OWN DEFECT, FOUND BY EXERCISING THE HELPER. The capture bound
        was 400 characters behind a lookahead, so a statement LONGER than that
        matched nothing and the derivation returned "" -- a silent miss on
        exactly the entries with most to say. Widening it also recovered a 4th
        live decision, B81."""
        body = "**B1. T.** **WHAT IS STILL OWED:** " + ("word " * 200) + "**E**"
        got = bdf.derive_still_owed(body)
        assert got, "a long statement was dropped entirely"
        assert len(got) <= bdf.STILL_OWED_MAX_CHARS + 8, len(got)

    def test_the_cut_never_lands_mid_word(self, bdf):
        """He reads these aloud. A split word is worse than a short sentence."""
        body = ("**B1. T.** **WHAT IS STILL OWED:** "
                + "alpha beta gamma delta epsilon " * 20 + "**E**")
        got = bdf.derive_still_owed(body)
        tail = got.removesuffix(" ...").rstrip()
        assert tail.split()[-1] in {"alpha", "beta", "gamma", "delta",
                                    "epsilon"}, repr(got[-40:])

    def test_an_authored_statement_beats_the_derived_one(self, bdf):
        """A human sentence is the primary; the derivation is the fallback."""
        mrb_mod, rows = bdf.collect()
        b77 = [r for r in rows if r["ident"] == "B77"]
        if not b77:
            pytest.skip("B77 is not in the live queue")
        assert b77[0]["owed"], "the authored still_owed was lost"

    def test_the_live_file_names_what_is_owed_more_often_than_not_naming_it(
            self, bdf):
        """THE OUTCOME ON THE FILE HE RECEIVES, and a ratchet in 1 direction.

        It is a FLOOR rather than an exact count, because the number moves
        whenever an entry is appended to -- and an exact pin on a growing
        document is the drift this project has corrected 3 times in 10 days.
        """
        mrb_mod, rows = bdf.collect()
        named = sum(1 for r in rows if r["owed"])
        #: ★ A RATIO, NOT A COUNT. The first version of this assertion pinned
        #: `named >= 4` and went RED within the hour -- not from a defect but
        #: because B81 CLOSED, taking the queue from 7 decisions to 6 and the
        #: named ones from 4 to 3 at an unchanged ratio. A floor on a count
        #: that shrinks when work finishes punishes finishing the work, which
        #: is the pin-drift this project has corrected 3 times in 10 days.
        assert rows, "no decisions in the queue; nothing to assert"
        assert named * 2 >= len(rows), (
            f"only {named} of {len(rows)} decisions name what is owed; it was "
            f"1 of 7 before the 2026-11-10 repair and half or better after it")

    def test_the_fallback_wording_is_still_reachable(self, bdf):
        """ANTI-VACUITY in the other direction: if everything were named, the
        fallback branch would be dead and this file would not notice."""
        mrb_mod, rows = bdf.collect()
        r = dict(rows[0])
        r["owed"] = ""
        r["ruled"] = "2026-11-08"
        out = bdf.render(mrb_mod, [r], spoken=True)
        assert "recorded in the entry" in out, (
            "the honest fallback was removed; an entry that states nothing "
            "would then have nothing said about it")


# ─────────────────────────────────────────────────────────────────────────────
# ★★★ 7 DEFECTS IN THE OWED DERIVATION, 4 FOUND BY A FREE PANEL AND 3 MY OWN.
#
# A 2-seat free panel (cc2, fable) was dispatched on 2026-11-10 and asked to
# attack this helper specifically, because it is the only change of that night
# that puts DERIVED PROSE in front of the founder as a statement of fact under
# a heading he decides from. BOTH SEATS INDEPENDENTLY FOUND THE SAME 4, and all
# 4 reproduced here by execution before anything was repaired:
#
#   D1  the capture ended at the first interior `**`, which in this corpus is
#       usually EMPHASIS inside a sentence. B103 reached him as "taking it to
#       about 891 s —", losing the magnitude and the operative ask, with no
#       ellipsis, because the sentence rule ran on only 1 arm of the `if`.
#   D2  the author's words inside the marker's own bold span were discarded in
#       8 of 8 cases, and ON B81 THAT INVERTED THE MEANING: the heading read
#       "WHAT IS OWED IS HIS, AND IT IS THE LIMIT RATHER THAN THE ADDITION:"
#       and he was shown only "he ruled the addition ... so it stands" -- told,
#       under *what is still owed*, that the thing was settled.
#   D3  a statement under 30 characters forced the lazy capture PAST the next
#       bold span, quoting an unrelated heading to him as the answer.
#   D4  the FRAME coerced a copula onto a clause and doubled the full stop,
#       including on B77, the only entry whose value is AUTHORED.
#
# AND 3 MORE THAT THE REPAIR ITSELF INTRODUCED, each found by running it:
#   M1  the sentence splitter broke "1.35" into "1. 35" -- read aloud as 2
#       numbers.
#   M2  a trailing all-caps bold word survived the cut, so " ..." was appended
#       after a complete sentence, implying withheld text that did not exist.
#   M3  the case rule kept all-caps words of 4 characters or fewer and lowered
#       the rest, giving "WHAT is OWED IS HIS, AND IT IS THE limit rather THAN
#       THE addition" -- worse than the original.
#
# WHAT SURVIVED THE ATTACK, both seats agreeing: LAST MARKER WINS, and NO
# MARKER MEANS NO CLAIM.
# ─────────────────────────────────────────────────────────────────────────────

class TestTheSevenOwedDefects:

    def test_D1_an_interior_bold_span_does_not_truncate_the_sentence(self, bdf):
        got = bdf.derive_still_owed(
            "**B1. T.** **WHAT IS STILL OWED:** the gate runs 891 s, "
            "**1.35 times that stated limit**, and which gives way is yours. "
            "**END**")
        assert "1.35" in got, f"the magnitude was dropped: {got!r}"
        assert "yours" in got, f"the operative ask was dropped: {got!r}"
        assert got.rstrip().endswith("."), f"ends mid-sentence: {got!r}"

    def test_D2_the_headings_own_clause_is_kept(self, bdf):
        got = bdf.derive_still_owed(
            "**B1. T.** **WHAT IS OWED IS HIS, AND IT IS THE LIMIT RATHER "
            "THAN THE ADDITION:** he ruled the addition with the figure in "
            "hand, so it stands. **END**")
        assert "limit rather than the addition" in got.lower(), (
            f"the heading's clause was discarded, which on B81 told him the "
            f"thing was SETTLED: {got!r}")

    def test_D3_a_short_statement_does_not_drag_the_next_heading_in(self, bdf):
        got = bdf.derive_still_owed(
            "**B1. T.** **WHAT IS STILL OWED:** his ruling. "
            "**DO NOT DELETE THE LEDGER:** more text")
        assert "**" not in got, f"literal asterisks reached him: {got!r}"
        assert "DELETE" not in got.upper(), (
            f"an unrelated heading was quoted as the answer: {got!r}")

    def test_D4_the_frame_never_coerces_a_copula_onto_a_clause(self, bdf):
        s = bdf._owed_sentence("he ruled the addition, so it stands.")
        assert "owed is he" not in s.lower(), s
        assert ".." not in s.replace("...", ""), f"doubled full stop: {s!r}"
        n = bdf._owed_sentence("your ruling on the bound")
        assert n.rstrip().endswith("."), n

    def test_D4_an_authored_value_ending_in_a_stop_is_not_doubled(self, bdf):
        s = bdf._owed_sentence("a fresh full suite after the repairs.")
        assert ".." not in s.replace("...", ""), s

    def test_M1_a_decimal_point_is_not_a_sentence_boundary(self, bdf):
        got = bdf.derive_still_owed(
            "**B1. T.** **WHAT IS STILL OWED:** it ran at 1.35 times the "
            "limit and 598.13 s. **END**")
        assert "1.35" in got and "598.13" in got, got
        assert "1. 35" not in got and "598. 13" not in got, (
            f"a decimal was split, which is read aloud as 2 numbers: {got!r}")

    def test_M2_no_ellipsis_is_added_after_a_complete_sentence(self, bdf):
        got = bdf.derive_still_owed(
            "**B1. T.** **WHAT IS STILL OWED:** his ruling on the bound. "
            "**END**")
        assert not got.rstrip().endswith("..."), (
            f"an ellipsis implies withheld text that does not exist: {got!r}")

    def test_D4b_a_value_that_already_opens_What_is_gets_no_second_lead(
            self, bdf):
        """★ ADDED AFTER A MUTATION SURVIVED. Removing the skip left the guard
        GREEN, because no probe fed `_owed_sentence` a value that already
        begins with its own lead -- which is exactly what the repaired
        derivation now produces for every entry whose heading continues."""
        s = bdf._owed_sentence(
            "What is owed is his, and it is the limit rather than the "
            "addition: he ruled the addition.")
        assert s.lower().count("what is") == 1, (
            f"the lead was prepended to a value that already carried one: "
            f"{s!r}")
        assert not s.lower().startswith("what is still owed: what is"), s

    def test_M2_a_fragment_after_a_whole_sentence_is_dropped_not_ellipsised(
            self, bdf):
        """★ ADDED AFTER A MUTATION SURVIVED. `test_M2` above returns on the
        FIRST branch, because its probe yields a single complete sentence and
        never reaches the trailing-fragment path. A probe has to carry a
        complete sentence AND a terminator-less tail for that branch to run."""
        got = bdf.derive_still_owed(
            "**B1. T.** **WHAT IS STILL OWED:** his ruling on the bound. "
            "and then a trailing clause that carries no terminator at all")
        assert got.rstrip().endswith("."), (
            f"the complete sentence was replaced by an ellipsised cut: "
            f"{got!r}")
        assert not got.rstrip().endswith("..."), (
            f"an ellipsis implies withheld text where a whole sentence was "
            f"available: {got!r}")
        assert "his ruling on the bound." in got, got

    def test_M3_a_kept_heading_is_not_shouted(self, bdf):
        got = bdf.derive_still_owed(
            "**B1. T.** **WHAT IS OWED TO YOU, AND IT IS A COST QUESTION "
            "RATHER THAN A CORRECTNESS ONE:** the gate ran 2,427 passed. "
            "**END**")
        shouted = [w for w in got.split()
                   if w.strip(".,;:!?)").isupper()
                   and w.strip(".,;:!?)") not in ("I",)
                   and not any(c in w for c in ("`", "_", "/", "-", "("))]
        assert not shouted, (
            f"a text-to-speech reader does not whisper: {shouted} in {got!r}")
        assert got[:1].isupper(), got

    def test_an_identifier_keeps_its_case(self, bdf):
        got = bdf.derive_still_owed(
            "**B1. T.** **WHAT IS OWED AND WHERE THE HARD/SOFT CLASS COMES "
            "FROM:** it touches `spec_verification_factor` today. **END**")
        assert "HARD/SOFT" in got, f"a compound was lowered: {got!r}"
        assert "spec_verification_factor" in got, got

    def test_what_survived_the_attack_last_marker_wins(self, bdf):
        got = bdf.derive_still_owed(
            "**B1. T.** **WHAT IS STILL OWED:** the older statement, since "
            "superseded. **★ LATER:** **WHAT IS STILL OWED:** the newer "
            "statement, live today. **END**")
        assert "newer statement" in got, got
        assert "older statement" not in got, got

    def test_what_survived_the_attack_no_marker_no_claim(self, bdf):
        assert bdf.derive_still_owed("**B1. T.** prose with no marker") == ""
        assert bdf.derive_still_owed("") == ""

    def test_every_live_derivation_reads_as_english(self, bdf):
        """THE OUTCOME ON THE FILE HE RECEIVES, over every entry that derives."""
        import re as _re
        import sys as _sys
        _sys.path.insert(0, str(REPO / "scripts"))
        import task_list_markers as _tlm
        derived = 0
        for e in _tlm.parse_entries():
            v = bdf.derive_still_owed(e.text)
            if not v:
                continue
            derived += 1
            s = bdf._owed_sentence(v)
            assert "**" not in s, (e.ident, s)
            assert ".." not in s.replace("...", ""), (e.ident, s)
            assert not _re.search(r"\d\. \d", s), (e.ident, s)
            assert not _re.search(r":\s+(is|are|was)\b", s), (e.ident, s)
            shouted = [w for w in s.split()
                       if w.strip(".,;:!?)").isupper()
                       and w.strip(".,;:!?)") != "I"
                       and not any(c in w for c in ("`", "_", "/", "-", "("))]
            assert not shouted, (e.ident, shouted, s)
        assert derived >= 8, (
            f"only {derived} entries derive a value; it was 8 when the panel "
            f"round landed, and a drop means the marker stopped matching")
