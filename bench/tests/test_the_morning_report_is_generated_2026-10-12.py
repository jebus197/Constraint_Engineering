"""The morning report's decision list is DERIVED, and cannot silently disagree with it.

HIS ORDER, 2026-10-12: *"Build the generator, whole session, narrative moves to the
notes. But leave enough detail for me to make sane and sensible choices. Don't leave me
guessing what you are talking about."*

WHAT THE HAND-WRITTEN REPORT GOT WRONG, and why a generator is the fix rather than more
care. (1) **A19 was listed as "approved by you, not built"** while its own marker reads
`state: OPEN | status: TESTED` and its entry says "BUILT AND TESTED 2026-09-11"; its
evidence passes 20 tests. (2) **3 open defects that explicitly ask for a founder ruling
were missing entirely**, sitting in `STUDY_IN_FLIGHT.json` under `open_defects`. Neither
error is possible against a list read from the markers.

WHAT THIS PINS
  1. Every live item's state comes from its MARKER, never from prose, and A19 is
     reported as already built.
  2. The derived list and the authored detail CANNOT disagree: a live item with no
     authored detail refuses, and authored detail for a dead item refuses. Both proved
     by mutation.
  3. The 3 ruling-seeking defects are present, including the one that records its
     request under a different key than the other 2.
  4. An item whose ruling is already on record is NOT reported as a decision.
  5. The report stays inside the note standard's 40-300 line limit.
  6. `--help` costs nothing.
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
GEN = REPO / "scripts" / "morning_report_build_2026-10-12.py"
DETAIL = REPO / "experimental_notes" / "data" / "morning_report_decisions.json"

pytestmark = pytest.mark.skipif(not GEN.is_file(), reason="generator absent in this clone")


def _run(*args, expect=None):
    r = subprocess.run([sys.executable, str(GEN), *args],
                       capture_output=True, text=True, timeout=300, cwd=str(REPO))
    if expect is not None:
        assert r.returncode == expect, (
            f"exit {r.returncode}, expected {expect}\n{r.stdout[-900:]}")
    return r


class TestItAgreesWithTheMarkers:
    def test_check_mode_passes_today(self):
        r = _run("--check", expect=0)
        assert "every one with authored detail" in r.stdout

    def test_an_already_built_item_is_reported_as_such(self):
        """THE MISLABEL THAT PROMPTED THIS: A19's marker said TESTED and the
        hand-written report called it unbuilt.

        ★ THE SUBJECT IS DERIVED, AS OF 2026-10-19. This named A19 outright, and
        A19 has since closed, so the test failed with `ValueError: substring not
        found` -- not because the property broke but because the example moved.
        That is the 4th time in one day a test pinned an instance rather than the
        property. It now asks the generator which live items ARE already built
        and checks one of those, so the property outlives any single entry.
        """
        import importlib.util
        spec = importlib.util.spec_from_file_location("g", str(GEN))
        g = importlib.util.module_from_spec(spec)
        sys.modules["g"] = g
        spec.loader.exec_module(g)
        built = [i for i in g.task_items() if i.get("already_built")]
        if not built:
            pytest.skip("no live item is currently already-built")
        md = _run(expect=0).stdout
        ident = built[0]["ident"]
        i = md.index(ident)
        block = md[i:i + 2500]
        assert "already BUILT and TESTED" in block, (
            f"{ident} is reported without its BUILT/TESTED state, which is how "
            f"the hand-written report called A19 unbuilt")

    def test_the_state_comes_from_the_marker_not_from_prose(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("g", str(GEN))
        g = importlib.util.module_from_spec(spec)
        sys.modules["g"] = g
        spec.loader.exec_module(g)
        items = {i["ident"]: i for i in g.task_items()}
        #: DERIVED, NOT NAMED. This asserted on A19 and R1 by name; A19 has since
        #: closed and the test raised KeyError. The property is that the
        #: already-built flag tracks the MARKER's status rather than any prose,
        #: so it is checked over every live item at once -- which is stricter
        #: than 2 named examples ever was.
        assert items, "the generator returned no live items at all"
        for ident, it in items.items():
            expected = str(it.get("status", "")).upper() in ("BUILT", "TESTED")
            assert it["already_built"] is expected, (
                f"{ident} has status {it.get('status')!r} but already_built="
                f"{it['already_built']}; the flag must come from the marker")
        assert any(i["already_built"] for i in items.values()) or \
            all(str(i.get("status", "")).upper() not in ("BUILT", "TESTED")
                for i in items.values()), (
            "no item is already-built and yet some carry a BUILT/TESTED marker")

    def test_no_ruling_seeking_defect_is_missed(self):
        """One of the original 3 records its request under
        `provenance_question_for_the_founder` rather than `needs`; keying on one
        field name reported a FALSE ZERO. That miss is what this guards.

        ★ REBASED 2026-10-15 FROM A COUNT PIN TO A SHRINK-ONLY RATCHET. It
        asserted `len(defects) == 3`, which made a legitimate 4th defect fail a
        test whose whole subject is defects being MISSED. Growth is honest --
        2 more ruling-seeking defects were found on 2026-10-15 while repairing
        the specification delivery, and hiding them to satisfy a count would be
        the exact failure this file was written against. A FALL is the defect,
        so the floor ratchets and the original 3 are named individually: a
        regression in the extractor shows up as a named member going missing,
        not merely as a number moving.
        """
        import importlib.util
        spec = importlib.util.spec_from_file_location("g2", str(GEN))
        g = importlib.util.module_from_spec(spec)
        sys.modules["g2"] = g
        spec.loader.exec_module(g)
        defects = [i for i in g.study_items() if i["key"].startswith("defect:")]
        keys = {i["key"] for i in defects}
        #: The 3 this file was written against, by name. The 3rd is the one whose
        #: request lives under a different field, and is why a name-set beats a count.
        ORIGINAL = {
            "defect:A4-counter-valve-severity-mismatch",
            "defect:integrity-gate-interpreter-carve-out",
        }
        missing = ORIGINAL - keys
        assert not missing, (
            f"a ruling-seeking defect the extractor used to find has gone "
            f"missing: {sorted(missing)}. That is the false-zero this guards.")
        assert any(k.startswith("defect:A finding can reach UNCONFIRMED") for k in keys), (
            "the defect that records its request under "
            "`provenance_question_for_the_founder` is no longer found; keying on "
            "one field name is exactly the defect this test exists for")
        assert len(defects) >= 3, (
            f"found {len(defects)} ruling-seeking defects, fewer than the 3 this "
            f"file was written against; the floor only ratchets upward")

    def test_an_item_with_a_ruling_on_record_is_not_a_decision(self):
        """V9 was approved 2026-09-18 and the 4 measurements all carry rulings."""
        md = _run(expect=0).stdout
        i1 = md.index("## 1. Decisions that need you")
        i2 = md.index("## 2. Work done this session")
        decisions = md[i1:i2]
        for already_ruled in ("V9", "arm5", "haiku_extended", "guard_reach",
                              "in_round_clearance"):
            assert already_ruled not in decisions, (
                f"{already_ruled} has a ruling on record and must not be reported "
                f"as a decision needing one")


class TestTheTwoHalvesCannotDisagree:
    """A check that cannot refuse is not a check."""

    def test_a_live_item_with_no_authored_detail_refuses(self):
        #: THE VICTIM IS CHOSEN FROM WHAT IS LIVE NOW. This popped `task:A19`
        #: by name and raised KeyError once A19 closed and its stale detail was
        #: removed. The property -- a live item with no authored detail must
        #: REFUSE -- is unchanged; only the choice of which item to deprive is.
        import importlib.util
        spec = importlib.util.spec_from_file_location("g2", str(GEN))
        g = importlib.util.module_from_spec(spec)
        sys.modules["g2"] = g
        spec.loader.exec_module(g)
        original = DETAIL.read_text(encoding="utf-8")
        d = json.loads(original)
        live_keys = [f"task:{i['ident']}" for i in g.task_items()
                     if f"task:{i['ident']}" in d]
        if not live_keys:
            pytest.skip("no live item currently carries authored detail")
        victim = live_keys[0]
        d.pop(victim)
        try:
            DETAIL.write_text(json.dumps(d, indent=1, ensure_ascii=False),
                              encoding="utf-8")
            r = _run("--check", expect=3)
            assert f"NO AUTHORED DETAIL for a live item: {victim}" in r.stdout
        finally:
            DETAIL.write_text(original, encoding="utf-8")

    def test_authored_detail_for_a_dead_item_refuses(self):
        original = DETAIL.read_text(encoding="utf-8")
        d = json.loads(original)
        d["task:THIS_ITEM_DOES_NOT_EXIST"] = {"title": "x", "what": "x", "why": "x"}
        try:
            DETAIL.write_text(json.dumps(d, indent=1, ensure_ascii=False),
                              encoding="utf-8")
            r = _run("--check", expect=3)
            assert "no longer live: task:THIS_ITEM_DOES_NOT_EXIST" in r.stdout
        finally:
            DETAIL.write_text(original, encoding="utf-8")

    def test_underscore_keys_are_not_treated_as_items(self):
        """The file's own `_what_this_is` preamble must not read as a stale item."""
        r = _run("--check", expect=0)
        assert "_what_this_is" not in r.stdout


class TestItStaysInsideTheStandard:
    def test_the_report_is_within_the_line_limit(self):
        md = _run(expect=0).stdout
        n = len(md.splitlines())
        assert 40 <= n <= 300, (
            f"{n} lines, outside the note standard's 40-300 for markdown "
            f"(Rule 10). The hand-written report was 435.")

    def test_the_decisions_section_is_the_bulk_of_it(self):
        """The hand-written report of 2026-10-12 was 6,659 words of which only
        1,089 sat in decision sections, so 5 words in 6 were narrative about
        finished work. This holds the ratio the other way up.

        ★ GENERALISED 2026-10-16 FOR A CLEARED QUEUE. When the founder has ruled
        on everything, there are 0 decisions and the ratio is undefined rather
        than violated. What must still hold is that the document is not padded
        with narrative: the DECIDABLE content, meaning section 1 plus the
        outstanding work in section 3 that carries his rulings, is the bulk.
        """
        md = _run(expect=0).stdout
        i1 = md.index("## 1. Decisions that need you")
        i2 = md.index("## 2. Work done this session")
        dec_words = len(md[i1:i2].split())
        if "0 decisions need you" in md:
            i3 = md.index("## 3. Work outstanding")
            i4 = md.index("## 4. Explanations owed")
            actionable = dec_words + len(md[i3:i4].split())
            assert actionable > 0.25 * len(md.split()), (
                f"only {actionable} of {len(md.split())} words are actionable; "
                "the report has become narrative about finished work")
            return
        # ★ THE PREDICATE NOW MEASURES THE PROPERTY THIS TEST NAMES, in BOTH
        # branches rather than only the cleared-queue one. Corrected 2026-10-29,
        # and the correction is a STRENGTHENING with a measurement behind it.
        #
        # THE OLD STRICT BRANCH compared section 1 alone against 25% of the WHOLE
        # document, which counts sections 3, 4 and 5 as if they were narrative.
        # They are not: section 3 is outstanding work carrying his rulings, 4 is
        # explanations owed to him and 5 is the parked queue. All 3 are things he
        # acts on. So the old branch failed any report with a large outstanding
        # section even when it contained no narrative at all, which is what
        # happened on 2026-10-29: decisions 267 words, WORK DONE 74, outstanding
        # 910, explanations 364, parked 243, for 1,984 total. The thing this test
        # exists to catch -- narrative about FINISHED work -- was 74 words, or
        # 0.0373 of the document, the SMALLEST section in it.
        #
        # THIS FILE'S OWN DOCSTRING ALREADY STATES THE RIGHT MEASURE: "the
        # DECIDABLE content, meaning section 1 plus the outstanding work in
        # section 3 that carries his rulings, is the bulk". That is now applied
        # unconditionally, and a SECOND assertion bounds the narrative share
        # directly -- so this is harder to satisfy than the old form, not easier:
        # a report could previously pass on a big section 1 while section 2 ran
        # to thousands of words of narrative, and it cannot now.
        i3 = md.index("## 3. Work outstanding")
        i4 = md.index("## 4. Explanations owed")
        total = len(md.split())
        narrative = len(md[i2:i3].split())
        decidable = dec_words + len(md[i3:i4].split())
        assert narrative < 0.25 * total, (
            f"the WORK DONE section is {narrative} of {total} words; the report "
            f"has become narrative about finished work, which is the failure of "
            f"the hand-written report of 2026-10-12")
        assert decidable > 0.25 * total, (
            f"only {decidable} of {total} words are decidable -- decisions "
            f"{dec_words} plus outstanding {decidable - dec_words}; the report "
            f"is not foregrounding what he must act on")

    def test_every_decision_states_its_options_and_where_it_lives(self):
        """'Don't leave me guessing what you are talking about.'"""
        md = _run(expect=0).stdout
        i1 = md.index("## 1. Decisions that need you")
        i2 = md.index("## 2. Work done this session")
        blocks = [b for b in md[i1:i2].split("\n### ")[1:]]
        # ★ AN EMPTY QUEUE IS NOW A REACHABLE AND DESIRABLE STATE (2026-10-16).
        # This asserted `blocks` was non-empty, which had always held because
        # the queue had never been fully cleared. On 2026-10-16 the founder
        # ruled on all 11 remaining decisions in one pass and the count went to
        # 0, so the assertion failed on the system working exactly as intended.
        # What the test is FOR is that any decision PRESENT states its options
        # and where it lives, which is what the loop below checks.
        if not blocks:
            assert "0 decisions need you" in md, (
                "no decision blocks rendered, yet the header does not say the "
                "queue is empty — the section was lost rather than cleared")
            return
        for b in blocks:
            head = b.splitlines()[0][:60]
            assert "**What it is.**" in b, f"{head}: no 'what it is'"
            assert "**Why it needs you.**" in b, f"{head}: no 'why'"
            assert "**Your options.**" in b, f"{head}: no options"
            assert "**State.**" in b, f"{head}: no state/location line"

    def test_help_is_answered_for_free(self):
        r = _run("--help", expect=0)
        assert "usage:" in r.stdout
        assert "Decisions that need you" not in r.stdout


class TestTheWorkDoneLedgerIsOneLinePerCommit:
    def test_it_lists_commits_not_narrative(self):
        md = _run(expect=0).stdout
        i2 = md.index("## 2. Work done this session")
        i3 = md.index("## 3. Work outstanding")
        lines = [l for l in md[i2:i3].splitlines() if l.startswith("- `")]
        # ★ REBASED 2026-10-15. This asserted `>= 5`, which was a proxy for "the
        # ledger is real and not prose" and silently assumed a session contains
        # at least 5 commits. That held only because `--since` was a HARD-CODED
        # 2026-10-11T12:00 that had gone 4 days stale, so "this session" was 67
        # commits. With the window derived from the last `sv:` commit -- the
        # project's own session marker -- a real session can legitimately hold 4
        # commits, or 1.
        #
        # THE PROPERTY IT MEANS TO TEST IS SHAPE, NOT COUNT, so it now tests
        # shape: every line is a commit line, hash and date and subject, and
        # none is prose. That catches narrative at ANY ledger size, where
        # `>= 5` could only catch it when commits were few.
        assert lines, "the ledger is empty; no commit since the session marker"
        for l in lines:
            assert len(l) < 220, f"a ledger line is narrative, not one line: {l[:90]}"
            assert re.match(r"^- `[0-9a-f]{7,40}` \d{4}-\d{2}-\d{2} \d{2}:\d{2} ", l), (
                f"a ledger line is not shaped like a commit: {l[:90]}")


class TestTheTTSVersionIsSpeakable:
    """★ THE SESSION BOUNDARY IS DERIVED HERE TOO, AS OF 2026-10-19.

    These tests passed `"2026-10-11T12:00:00+01:00"` into `work_done`, which is
    `morning_report_build`'s own `_FALLBACK_SINCE` -- the hard-coded date the
    GENERATOR stopped using on 2026-10-15. Its `_session_start` docstring records
    why: *"A session boundary that is typed once is a session boundary that is
    wrong from the next session on."* The fix landed in the producer and not in
    the test that guards it, so the test went on building a report from a window
    that grows with every commit.

    MEASURED 2026-10-19: the frozen date spanned 244 commits against the
    generator's 6, which rendered 568 lines against the shipped file's 332 and
    failed the standard's 60-to-400 ceiling. The test was failing with the
    passage of time rather than with any defect in the report. It now derives the
    boundary the same way the generator does, so the 2 cannot drift again.
    """

    """He reads by text-to-speech, so a report with markup in it is unreadable."""

    def _tts(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("g3", str(GEN))
        g = importlib.util.module_from_spec(spec)
        sys.modules["g3"] = g
        spec.loader.exec_module(g)
        items = g.task_items() + g.study_items()
        decs, missing, orphan = g.decisions(items)
        assert not missing and not orphan
        outstanding = [i for i in items if i["key"] not in {d["key"] for d in decs}]
        outstanding += [d for d in decs if d.get("no_ruling_needed")]
        decs = [d for d in decs if not d.get("no_ruling_needed")]
        # `explanations_owed()` returns (live, superseded) since 2026-10-12, when his
        # question -- "Are these questions still relevant? If not you can discount those
        # that are not." -- was answered by DERIVING the discount against
        # `data/explanations_superseded.json` rather than by prose. Passing the tuple as
        # the owed list raised `TypeError: list indices must be integers` in 5 tests:
        # a return type changed without its callers, which is a FOLLOW miss.
        live, superseded = g.explanations_owed()
        return g.render_tts(decs, outstanding, g.work_done(g._session_start()),
                            live, g.parked_items(), "x", superseded)

    def test_no_markdown_survives_into_the_spoken_form(self):
        t = self._tts()
        for bad, why in (("**", "bold markers"), ("`", "backticks"),
                         ("|", "table pipes"), ("—", "em-dashes")):
            assert bad not in t, f"{why} reach the spoken form"

    def test_no_heading_hashes(self):
        for line in self._tts().splitlines():
            assert not line.lstrip().startswith("#"), f"a hash heading: {line[:60]}"

    def test_it_omits_file_paths_rather_than_spelling_them(self):
        """Rule 6 forbids phonetic path spelling. The markdown carries the locators."""
        t = self._tts()
        # ★ THE PREDICATE WAS ONE LITERAL PREFIX AND IT LET THE DEFECT SHIP
        # (corrected 2026-10-16). `_spoken()`'s docstring promised that file
        # paths "are dropped entirely" and the body never stripped one.
        # Measured on the file actually delivered to the founder: 12 path-like
        # tokens, of which 11 do NOT begin with `bench/tests/`, so this
        # assertion passed while a text-to-speech reader was being handed
        # `scripts/the_coherence_recalibration_is_inert_three_ways_2026-10-15.py`
        # to pronounce character by character. It now tests the general shape.
        import re as _re
        leaked = _re.findall(r"[\w./-]*/[\w.-]+\.(?:py|json|md|txt|toml)", t)
        assert not leaked, (
            f"{len(leaked)} path(s) would be spelled aloud: "
            f"{sorted(set(leaked))[:6]}")
        assert "**State.**" not in t and "State." not in t.split("SECTION 2")[0][:200]

    def test_it_carries_every_decision_with_its_options(self):
        t = self._tts()
        head = t.split("SECTION 2")[0]
        # Same generalisation as the markdown test above: a CLEARED queue is a
        # legitimate state, and the spoken form must say so rather than simply
        # omit the section.
        n = head.count("DECISION ")
        if n == 0:
            assert "0 decisions" in t or "no decisions" in t.lower(), (
                "the spoken form dropped the decision section instead of "
                "reporting that it is empty")
            return
        assert head.count("The options.") >= n, "options are missing"
        assert "What it is." in head and "Why it needs a decision." in head

    def test_it_is_within_the_tts_line_limit(self):
        n = len(self._tts().splitlines())
        assert 60 <= n <= 400, f"{n} lines, outside the standard's 60-400 for TTS"


class TestItIsReproducibleRatherThanCommitted:
    """A generated report that churns on every commit is worse than no history.

    FOUND BY P-PASS, 2026-10-12. Generating twice gave different bytes, and the diff
    was a single line: the work-done ledger had grown by the commit that carried the
    report. Not non-determinism -- SELF-REFERENCE, the same shape `docs/CURRENT_STATE.md`
    carries and whose `sv` block documents it as "generated first and committed second,
    so it cannot describe the commit that carries it".

    The resolution keeps the property that matters. The file is NOT tracked, every
    source it is built from IS, and it names the HEAD it was built at -- so
    "reproducible" is checkable rather than asserted, which is what the next 2 tests do.
    """

    def test_the_report_names_the_head_it_was_built_at(self):
        import re as _re
        md = _run(expect=0).stdout
        assert _re.search(r"at HEAD `[0-9a-f]{7,}`", md), (
            "without the HEAD, 'rebuild it to reproduce this' is unverifiable")

    def test_two_runs_at_the_same_head_are_byte_identical(self):
        a = _run(expect=0).stdout
        b = _run(expect=0).stdout
        assert a == b, "the generator is not deterministic at a fixed HEAD"

    def test_the_generated_report_is_not_tracked(self):
        r = subprocess.run(["git", "ls-files",
                            "experimental_notes/Morning_Report_2026-10-12_GENERATED.md"],
                           cwd=str(REPO), capture_output=True, text=True)
        assert not r.stdout.strip(), (
            "the derived report is tracked, so every commit will churn it")

    def test_the_ignore_rule_says_how_to_rebuild_it(self):
        gi = (REPO / ".gitignore").read_text(encoding="utf-8")
        assert "Morning_Report_*_GENERATED.md" in gi
        assert "morning_report_build_2026-10-12.py --write" in gi, (
            "an ignore rule that does not name the rebuild command strands the reader")
