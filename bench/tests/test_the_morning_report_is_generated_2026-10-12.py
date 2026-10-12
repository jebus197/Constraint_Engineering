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

    def test_a19_is_reported_as_already_built(self):
        """THE MISLABEL THAT PROMPTED THIS. Its marker says TESTED."""
        md = _run(expect=0).stdout
        i = md.index("A19")
        block = md[i:i + 2500]
        assert "already BUILT and TESTED" in block, (
            "A19 is reported without its BUILT/TESTED state, which is how the "
            "hand-written report called it unbuilt")

    def test_the_state_comes_from_the_marker_not_from_prose(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("g", str(GEN))
        g = importlib.util.module_from_spec(spec)
        sys.modules["g"] = g
        spec.loader.exec_module(g)
        items = {i["ident"]: i for i in g.task_items()}
        assert items["A19"]["status"] == "TESTED"
        assert items["A19"]["already_built"] is True
        assert items["R1"]["already_built"] is False

    def test_all_three_ruling_seeking_defects_are_found(self):
        """One of the 3 records its request under `provenance_question_for_the_founder`
        rather than `needs`; keying on one field name reported a false zero."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("g2", str(GEN))
        g = importlib.util.module_from_spec(spec)
        sys.modules["g2"] = g
        spec.loader.exec_module(g)
        defects = [i for i in g.study_items() if i["key"].startswith("defect:")]
        assert len(defects) == 3, f"found {len(defects)} of 3 ruling-seeking defects"

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
        original = DETAIL.read_text(encoding="utf-8")
        d = json.loads(original)
        removed = d.pop("task:A19")
        try:
            DETAIL.write_text(json.dumps(d, indent=1, ensure_ascii=False),
                              encoding="utf-8")
            r = _run("--check", expect=3)
            assert "NO AUTHORED DETAIL for a live item: task:A19" in r.stdout
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
        """The hand-written report spent 0.1695 of its words on decisions. A report
        for deciding should not be mostly narrative."""
        md = _run(expect=0).stdout
        i1 = md.index("## 1. Decisions that need you")
        i2 = md.index("## 2. Work done this session")
        share = len(md[i1:i2].split()) / len(md.split())
        assert share > 0.40, f"decisions are only {share:.4f} of the words"

    def test_every_decision_states_its_options_and_where_it_lives(self):
        """'Don't leave me guessing what you are talking about.'"""
        md = _run(expect=0).stdout
        i1 = md.index("## 1. Decisions that need you")
        i2 = md.index("## 2. Work done this session")
        blocks = [b for b in md[i1:i2].split("\n### ")[1:]]
        assert blocks, "no decisions rendered at all"
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
        assert len(lines) >= 5, f"only {len(lines)} commits in the ledger"
        for l in lines:
            assert len(l) < 220, f"a ledger line is narrative, not one line: {l[:90]}"


class TestTheTTSVersionIsSpeakable:
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
        return g.render_tts(decs, outstanding, g.work_done("2026-10-11T12:00:00+01:00"),
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
        assert "bench/tests/" not in t
        assert "**State.**" not in t and "State." not in t.split("SECTION 2")[0][:200]

    def test_it_carries_every_decision_with_its_options(self):
        t = self._tts()
        head = t.split("SECTION 2")[0]
        assert head.count("DECISION ") >= 5, "decisions are missing from the spoken form"
        assert head.count("The options.") >= 5, "options are missing"
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
