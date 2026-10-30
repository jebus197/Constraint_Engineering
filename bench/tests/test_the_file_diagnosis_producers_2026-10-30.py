"""The 3 producers written for his 2026-10-30 complaint are executed, not described.

WHY THIS FILE EXISTS. 3 producers were added on 2026-10-30 to measure why the
consolidated verdicts file could not be ruled on, which panel briefs were never
run, and whether the demotion rule can do better than a 1-in-20 false-demotion
rate. The additive standard's symmetric half applies to all 3: *"an addition
that nothing reaches is not additive either."* The project's own ratchet,
`test_scripts_are_reached_2026-09-11.py`, caught exactly this on 2026-10-19 when
4 producers were written with no caller.

WHAT IS PINNED, AND WHY IT IS NOT THE OUTPUT NUMBERS. The document these
producers measure is about to be rewritten, so pinning its measured figures
would pin a moving target and the test would fail for the wrong reason -- the
shape this project records as a text assertion that cannot follow a door when it
moves. Instead each predicate is driven on a CONSTRUCTED input whose correct
answer is known by hand, so a broken predicate gives a wrong answer here rather
than a plausible one on real data.

Plus the 2 facts that are independent of any document: the critical-value table
agrees between scipy and exact rational arithmetic, and the fast sign test is
the same decision as the panel's own function on real streams.

And `--help` is asserted to exit 0 on all 3, because a help text must never cost
anything to read.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "scripts"
DIAG = SCRIPTS / "why_the_consolidated_file_was_unusable_2026-10-30.py"
BRIEFS = SCRIPTS / "which_panel_briefs_were_never_run_2026-10-30.py"
TRADE = SCRIPTS / "can_we_do_better_than_one_in_twenty_2026-10-30.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def diag_instrument_words() -> tuple[str, ...]:
    """Read the live list at collection time, so a deletion changes the test set.

    Parametrising from the module under test means removing a word removes its
    case rather than silently leaving it uncovered -- so the COUNT is asserted
    separately below, and that is what makes a deletion visible.
    """
    return tuple(_load(DIAG, "diag_for_params").INSTRUMENT_WORDS)


@pytest.fixture(scope="module")
def diag():
    return _load(DIAG, "diag_producer")


@pytest.fixture(scope="module")
def briefs():
    return _load(BRIEFS, "briefs_producer")


@pytest.fixture(scope="module")
def trade():
    return _load(TRADE, "trade_producer")


class TestHelpCostsNothing:
    @pytest.mark.parametrize("path", [DIAG, BRIEFS, TRADE], ids=lambda p: p.name)
    def test_help_exits_zero(self, path):
        r = subprocess.run([sys.executable, str(path), "--help"],
                           capture_output=True, text=True, timeout=120)
        assert r.returncode == 0, r.stderr[-600:]
        assert "usage:" in r.stdout


class TestTheDiagnosisPredicates:
    """Each charge driven on text whose correct answer is known by hand."""

    def test_a_bare_identifier_shares_no_phrase_with_its_title(self, diag):
        # A document that names B50 and nothing else about it. The strict test
        # must find 0 shared 3-word phrases; the lenient one must be low.
        bare = "You must rule on B50. It is open and it is yours."
        titles = diag.entry_titles()
        assert "B50" in titles, "the task list no longer carries B50"
        shared = diag.trigrams(titles["B50"]) & diag.trigrams(bare)
        assert shared == set(), f"expected no shared phrase, got {shared}"

    def test_a_document_that_does_explain_is_scored_as_explaining(self, diag):
        # The same predicate must PASS when the subject is actually named --
        # otherwise it would condemn every document and measure nothing.
        titles = diag.entry_titles()
        explained = "You must rule on B50. " + titles["B50"]
        shared = diag.trigrams(titles["B50"]) & diag.trigrams(explained)
        assert len(shared) > 0, "a document quoting the title scored as unexplained"

    def test_the_standards_census_counts_what_it_says(self, diag):
        text = ("This is additive, it is composable with the rest, and it is "
                "the simplest sufficient fix. Additive again.")
        got = diag.charge_standards_absent(text)
        assert got["additive"] == 2, got
        assert got["composability"] == 1, got
        assert got["simplest sufficient"] == 1, got
        assert sum(diag.charge_standards_absent("nothing of the sort").values()) == 0

    def test_a_recommendation_is_detected_only_where_one_exists(self, diag):
        with_rec = "B50 is open and the recommendation is to take option 1."
        without = "B50 is open and it is yours to settle."
        assert diag.charge_recommendations(with_rec)["with_recommendation"] == 1
        assert diag.charge_recommendations(without)["with_recommendation"] == 0

    def test_a_recommendation_in_a_later_paragraph_of_a_section_is_found(self, diag):
        """The defect that made a correct document score 0 of 6.

        The first predicate owned a paragraph only when it repeated the bare
        identifier, so a heading plus several explaining paragraphs scored no
        recommendation at all.
        """
        doc = ("B50. 6 tests now fail after a reset.\n"
               "\n"
               "What it is. The memory was emptied on your order.\n"
               "\n"
               "Recommendation: option 1, because it keeps every assertion.\n")
        got = diag.charge_recommendations(doc)
        row = {r["ident"]: r for r in got["rows"]}["B50"]
        assert row["has_recommendation"], row
        assert got["with_recommendation"] == 1, got

    def test_a_section_ends_at_the_next_document_heading(self, diag):
        """Without a terminator the last entry swallows the rest of the file.

        Measured on the real document: R1's section read 9,159 characters and
        had absorbed 4 later parts, so anything appearing anywhere below it
        would have been credited to R1.
        """
        doc = ("R1. Restart the control run.\n"
               "\n"
               "What it is. It measures invented faults.\n"
               "\n"
               "PART 5. SOMETHING ELSE ENTIRELY\n"
               "\n"
               "Recommendation: add the test files to the gate.\n")
        sections = diag._sections(doc)
        assert "Recommendation" not in sections["R1"], \
            "the section ran past its own heading boundary"
        assert "invented faults" in sections["R1"]

    def test_a_flat_document_still_measures_by_mention(self, diag):
        """The older files carry no headings; the fallback must still work."""
        doc = ("Everything awaiting you. B50 is open and the recommendation "
               "is option 1. C1 needs a number.\n")
        sections = diag._sections(doc)
        assert "recommendation" in sections["B50"].lower()
        assert diag.charge_recommendations(doc)["with_recommendation"] >= 1

    def test_repetition_needs_both_measures_to_agree(self, diag):
        same = ("The gate refuses a paid dispatch without his authorisation. "
                "The gate refuses a paid dispatch without his authorisation.")
        got = diag.charge_repetition(same)
        assert got["agreed_by_both"] == 1, got
        apart = ("The gate refuses a paid dispatch without his authorisation. "
                 "Seven immune memory assertions now fail on every run.")
        assert diag.charge_repetition(apart)["agreed_by_both"] == 0

    def test_substance_is_not_counted_as_narration(self, diag):
        subs = "Option 1 removes the stale constant and leaves 5 untouched."
        assert diag.charge_narration(subs)["narration_sentences"] == 0

    @pytest.mark.parametrize("word", list(diag_instrument_words()))
    def test_every_instrument_word_is_detected_on_its_own(self, diag, word):
        """One sentence per trigger, so deleting ANY of them turns this red.

        The first version of this test put several triggers in one sentence,
        so emptying most of the list left it GREEN -- a surviving word carried
        the whole assertion. That is the same hollow shape this project records
        from a helper tested without its caller.
        """
        sentence = f"The {word} says so."
        got = diag.charge_narration(sentence)
        assert got["narration_sentences"] == 1, (word, sentence, got)

    @pytest.mark.parametrize("marker", ["I", "my"])
    def test_first_person_is_detected_on_its_own(self, diag, marker):
        sentence = f"So {marker} reading of it stands."
        assert diag.charge_narration(sentence)["narration_sentences"] == 1, marker

    def test_the_instrument_list_may_not_be_gutted(self, diag):
        """The floor the parametrised cases above cannot supply themselves.

        Those cases are generated FROM the list, so deleting a word deletes its
        own case and the suite would stay green -- a test that disappears when
        the thing it tests disappears. This pins a minimum size and the words
        whose absence would make the narration measure meaningless.
        """
        words = set(diag.INSTRUMENT_WORDS)
        assert len(words) >= 14, f"the instrument list shrank to {len(words)}"
        for required in ("producer", "script", "guard", "wilson", "interval",
                         "mutation", "census", "denominator"):
            assert required in words, f"{required!r} was dropped from the measure"

    def test_the_two_readability_indices_order_known_texts_the_same_way(self, diag):
        easy = ("The dial is set to zero. Nothing uses it yet. "
                "You pick one number. Then it works.")
        hard = ("The monotonicity enforcement in the hierarchical policy "
                "merge engine establishes that a subordinate layer cannot "
                "weaken a universal hard constraint, which is the "
                "exchangeability precondition the relegation identifiability "
                "argument depends upon throughout.")
        assert diag.flesch_reading_ease(easy) > diag.flesch_reading_ease(hard)
        assert diag.coleman_liau(easy) < diag.coleman_liau(hard)

    def test_wilson_agrees_between_the_two_routes(self, diag):
        for k, n in ((9, 27), (0, 400), (8, 134), (35, 147)):
            a = diag.wilson_direct(k, n)
            b = diag.wilson_statsmodels(k, n)
            assert b is not None, "statsmodels is required for the cross-check"
            assert max(abs(a[0] - b[0]), abs(a[1] - b[1])) < 1e-9, (k, n, a, b)

    def test_the_real_run_completes_and_reports_all_six_entries(self, diag):
        delivered = diag.read_text_any_encoding(diag.DELIVERED) \
            if diag.DELIVERED.exists() else None
        if delivered is None:
            pytest.skip("the delivered file is not present in this checkout")
        got = diag.charge_subject_never_named(delivered)
        assert got["entries"] == len(diag.DECISION_ENTRIES)
        assert 0 <= got["no_shared_phrase"] <= got["entries"]


class TestTheBriefCensus:
    def test_a_brief_with_no_reply_is_unrun_and_one_with_a_reply_is_not(
            self, briefs, tmp_path, monkeypatch):
        logs = tmp_path / "logs"
        (logs / "never_ran").mkdir(parents=True)
        (logs / "never_ran" / "BRIEF.md").write_text("Entry B21 of the list.")
        (logs / "did_run").mkdir(parents=True)
        (logs / "did_run" / "BRIEF.md").write_text("Entry B22 of the list.")
        (logs / "did_run" / "cc2.json").write_text("{}")
        (logs / "bookkeeping_only").mkdir(parents=True)
        (logs / "bookkeeping_only" / "BRIEF.md").write_text("Entry C1 of the list.")
        (logs / "bookkeeping_only" / "topology.json").write_text("{}")
        monkeypatch.setattr(briefs, "LOGS", logs)
        dirs = briefs.brief_dirs()
        assert {d.name for d in dirs} == {"never_ran", "did_run", "bookkeeping_only"}
        assert briefs.seat_replies(logs / "did_run") == ["cc2.json"]
        # A bookkeeping file is NOT a seat's answer, so this one is still unrun.
        assert briefs.seat_replies(logs / "bookkeeping_only") == []

    def test_a_sandbox_harvest_counts_as_having_run(self, briefs, tmp_path):
        d = tmp_path / "round"
        (d / "sandbox_harvest" / "cc2").mkdir(parents=True)
        assert briefs.harvest_count(d) == 1
        assert briefs.harvest_count(tmp_path / "absent") == 0

    def test_attribution_never_promotes_a_bare_identifier(self, briefs, tmp_path):
        d = tmp_path / "round"
        d.mkdir()
        (d / "BRIEF.md").write_text(
            "# PANEL BRIEF\nThis concerns B29, B31 and B33 together.\n")
        primary, mentions = briefs.entries_for(d)
        assert primary == "", "a bare identifier was promoted to the attribution"
        assert mentions == ["B29", "B31", "B33"], mentions

    def test_an_explicit_entry_phrase_is_promoted(self, briefs, tmp_path):
        d = tmp_path / "round2"
        d.mkdir()
        (d / "BRIEF.md").write_text("Round x. Entry B21 of the master list. Also B22.")
        primary, mentions = briefs.entries_for(d)
        assert primary == "B21"
        assert "B22" in mentions


class TestTheDemotionTradeOff:
    def test_the_critical_table_agrees_between_scipy_and_exact_rationals(self, trade):
        for alpha in (0.05, 0.01, 0.001):
            a = trade.critical_table_scipy(alpha, 24)
            b = trade.critical_table_mpmath(alpha, 24)
            assert a == b, (alpha, [i for i, (x, y) in enumerate(zip(a, b)) if x != y])

    def test_a_tighter_alpha_never_lowers_the_critical_count(self, trade):
        loose = trade.critical_table_scipy(0.05, 24)
        tight = trade.critical_table_scipy(0.001, 24)
        for nd in range(1, 25):
            assert tight[nd] >= loose[nd], nd

    def test_the_fast_sign_test_is_the_panels_own_decision(self, trade):
        import numpy as np
        mod = trade.load_panel_module()
        crit = trade.critical_table_scipy(0.01, mod.WIN)
        got = trade.check_fidelity(mod, np, 0.01, crit, 40, 7)
        assert got["identical"], got
        assert got["original_fired"] > 0, \
            "the fidelity check fired on nothing, so it compared nothing"

    def test_a_wrong_critical_table_is_caught_by_that_same_check(self, trade):
        """The fidelity check must be able to FAIL, or it proves nothing."""
        import numpy as np
        mod = trade.load_panel_module()
        broken = [0] * (mod.WIN + 1)  # fires on any discordant pair at all
        got = trade.check_fidelity(mod, np, 1e-9, broken, 20, 7)
        assert not got["identical"], \
            "a table that fires on everything agreed with the real rule"
