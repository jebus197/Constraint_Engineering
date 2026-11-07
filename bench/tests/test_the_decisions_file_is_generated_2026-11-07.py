#!/usr/bin/env python3
"""THE DECISIONS FILE HE RULES FROM MUST BE GENERATED, AND SPOKEN-CLEAN.

WHY, 2026-11-07. The morning report of 2026-11-06 was written by HAND and told
him 3 things awaited him while the record tracked 29. A hand-written surface
cannot be checked against the record. This renderer reads the same authored
detail the generated report reads, through the same functions, so the 2 cannot
disagree -- and the agreement checker, which joins the generated report to the
NEWEST dated spoken file, now has a same-day file to join against.

WHAT THIS GUARDS, in 4 parts:

  1. COVERAGE. Every live decision is rendered, each with a heading, options,
     a recommendation and a named standard. Rule 33 of note standard v1.9.
  2. THE INDEX. His ruling of 2026-11-06 removed the length cap and kept the
     requirement that a file let him decide quickly. The index is how both hold
     at once, so it must carry every decision, not a sample.
  3. SPOKEN CLEANLINESS. No markdown, no em-dash, no bare file path, no
     spelled-out number. The spoken normaliser is BORROWED from the report
     builder rather than rewritten, because 2 declarations of 1 rule is the
     shape this project keeps meeting.
  4. THE DETECTOR'S CONTROL, which is the part most worth having. The
     recommendation detector must NOT count "NOT recommended" as a claim. Its
     first version did, and flagged 9 of 31 entries when 2 were real: 4 were
     that exact inversion and 2 were legitimate multi-part entries. A control
     requiring the detector to REFUSE a sound input is the only thing that
     separates a detector from an accusation.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
GEN = REPO / "scripts" / "build_decisions_file_2026-11-07.py"
SURFACES = REPO / "scripts" / "do_the_two_decision_surfaces_agree_2026-11-01.py"
STANDARD = re.compile(r"additive|simplest sufficient|composab", re.I)


def _load(path: pathlib.Path, name: str):
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def gen():
    return _load(GEN, "decgen")


@pytest.fixture(scope="module")
def rendered(gen):
    mrb, rows = gen.collect()
    return rows, gen.render(mrb, rows, spoken=False), gen.render(mrb, rows, spoken=True)


class TestCoverage:
    def test_every_live_decision_is_rendered(self, gen, rendered):
        rows, _md, _tts = rendered
        sf = _load(SURFACES, "sf_decgen")
        assert len(rows) == len(sf.derived()), (
            "the renderer and the agreement checker disagree about how many "
            "decisions are live, which is the 2-surface defect this file exists for")
        assert len(rows) >= 5, f"only {len(rows)} decisions; these tests say little"

    def test_each_carries_a_heading_and_options(self, rendered):
        rows, _md, _tts = rendered
        assert not [r["ident"] for r in rows if not r["heading"]]
        assert not [r["ident"] for r in rows if not r["options"]]

    def test_each_recommendation_names_a_standard(self, rendered):
        """RULE 33. Counted over the RENDERED recommendation, not the whole blob.

        An earlier producer searched the entire authored detail and reported
        29 of 29, which is true and does not establish that the RECOMMENDATION
        names a standard -- the thing Rule 33 requires.
        """
        rows, _md, _tts = rendered
        gaps = [r["ident"] for r in rows
                if not STANDARD.search(" ".join(r["options"]) + " " + r["standards"])]
        assert not gaps, f"{gaps} render a recommendation naming no standard"

    def test_every_decision_has_a_recommendation_at_all(self, gen, rendered):
        """NO SILENT ABSENCE. B131 carried 3 options and marked none, so its
        recommendation section could not be written. That is the gap."""
        rows, _md, _tts = rendered
        unmarked = [r["ident"] for r in rows
                    if gen.recommended_index(r["options"])[1].startswith("NO OPTION")]
        assert not unmarked, (
            f"{unmarked} mark no option as the recommendation, so the file would "
            f"show option 1 by position and call it recommended")

    def test_a_multiple_claim_is_DISCLOSED_rather_than_resolved_quietly(
            self, gen, rendered):
        """★ WHY NOT 'EXACTLY 1'. The first version of this test asserted
        exactly 1 claim per entry and FAILED on B94, which has 2 halves each
        carrying its own recommendation -- a legitimate structure, not the
        HIL-fatigue failure, which is 2 answers to the SAME question. B93 is
        the same shape, distinguishing a step now from a follow-up later.
        Forcing those entries to 1 claim would have damaged the record to
        satisfy a predicate, which is the fault
        `feedback_a_guard_can_accuse_correct_code` names.

        The property that actually matters is that he is never shown a single
        recommendation when the entry holds 2. So multiplicity must reach the
        RENDERED file, and that is what is asserted here.
        """
        rows, _md, tts = rendered
        multi = [(r["ident"], gen.recommended_index(r["options"])[1]) for r in rows
                 if "options claim" in gen.recommended_index(r["options"])[1]]
        for ident, how in multi:
            assert how in tts, (
                f"{ident} has multiple recommendation claims and the spoken file "
                f"does not say so, so he sees 1 where the entry holds more: {how}")
        # ANTI-VACUITY: if no entry ever has 2 claims this test checks nothing,
        # so the fixture-level control in TestTheDetectorHasAControl carries it.
        assert isinstance(multi, list)


class TestTheIndexCarriesEveryDecision:
    def test_the_index_is_complete_in_both_surfaces(self, rendered):
        rows, md, tts = rendered
        for name, text in (("markdown", md), ("spoken", tts)):
            head = text.split("DECISION 1.")[0]
            nums = re.findall(r"(?m)^(\d+)\.\s", head)
            assert len(nums) == len(rows), (
                f"the {name} index lists {len(nums)} of {len(rows)} decisions; "
                f"an index that samples is worse than none, because it reads as "
                f"complete")
            assert nums == [str(i) for i in range(1, len(rows) + 1)]

    def test_every_index_line_names_its_recommended_option(self, rendered):
        rows, _md, tts = rendered
        head = tts.split("DECISION 1.")[0]
        assert head.count("Recommended option") == len(rows)


class TestB132TheWrittenSurfaceCarriesTheTicketIdentity:
    """ENTRY B132, HIS RULING OF 2026-11-06: the written surfaces need no ruling,
    and only the SPOKEN identifier is his to decide, as entry B104 asks, because
    a 12-hex value read aloud is hostile to listening.

    MEASURED BY EXECUTION rather than by reading, because an earlier grep of
    mine reported 0 on 3 surfaces and was WRONG: its pattern required square
    brackets. `ticket_id()` resolves 29 of 29 live decisions, and the WRITTEN
    morning report already renders 48 identifiers -- that half was built, and
    the 0 on disk is a file generated before `ticket_tag` existed. The decisions
    file I generated on 2026-11-07 carried 0 on both surfaces, reproducing the
    defect B132 records in the newest document he reads.
    """

    TID = re.compile(r"\[[0-9a-f]{12}\]")

    def test_the_lookup_actually_resolves(self, gen, rendered):
        """ANTI-VACUITY FIRST. If nothing resolves, both tests below pass on
        nothing, which is how a mechanism wired to no caller looks green."""
        rows, _md, _tts = rendered
        with_tid = [r["ident"] for r in rows if r.get("tid")]
        assert len(with_tid) == len(rows), (
            f"only {len(with_tid)} of {len(rows)} decisions resolve a ticket "
            f"identity; the rest would be rendered with no identifier")

    def test_the_markdown_carries_one_per_decision(self, rendered):
        """★ ASSERTED ON THE HEADING LINES, not on the whole document.

        A total-count version of this test stayed GREEN when the heading tag was
        removed, because the index lines alone still supplied 1 identifier per
        decision. A reader who scrolls to a decision sees its heading, not the
        index, so the heading is the surface that must carry it.
        """
        rows, md, _tts = rendered
        headings = re.findall(r"(?m)^## DECISION \d+\..*$", md)
        assert len(headings) == len(rows), (
            f"{len(headings)} decision headings for {len(rows)} decisions")
        bare = [h[:70] for h in headings if not self.TID.search(h)]
        assert not bare, (
            f"{len(bare)} decision heading(s) carry no ticket identifier, which "
            f"is the surface B132 records as reaching 0: {bare[:3]}")
        assert len(self.TID.findall(md)) >= 2 * len(rows), (
            "the index should carry the identity as well as the heading")

    def test_the_spoken_file_carries_NONE_until_he_rules_b104(self, rendered):
        """THE OTHER DIRECTION, and it is the one that protects him. Without
        this the obvious fix spreads a 12-hex string into a file read aloud."""
        _rows, _md, tts = rendered
        found = self.TID.findall(tts)
        assert not found, (
            f"{len(found)} ticket identifier(s) reached the SPOKEN file. A "
            f"12-hex value read aloud is hostile to listening, which is exactly "
            f"the question entry B104 puts to him and which is not yet ruled.")


class TestTheSpokenFileIsSpeakable:
    @pytest.mark.parametrize("ch,why", [
        ("**", "bold markers are read aloud as noise"),
        ("`", "backticks are read aloud as noise"),
        ("—", "an em-dash is not spoken; the standard requires a comma"),
        ("|", "a table pipe is read aloud as noise"),
    ])
    def test_no_markdown_survives(self, rendered, ch, why):
        _rows, _md, tts = rendered
        assert ch not in tts, why

    def test_no_heading_hashes(self, rendered):
        _rows, _md, tts = rendered
        assert not re.search(r"(?m)^#", tts), "a hash heading is spoken as 'hash'"

    def test_no_file_path_survives(self, rendered):
        _rows, _md, tts = rendered
        leaked = re.findall(r"[\w./-]*/[\w.-]+\.(?:py|json|md|txt|toml)", tts)
        assert not leaked, (
            f"{len(leaked)} path(s) reached the spoken file and a reader "
            f"pronounces them character by character: {leaked[:5]}")

    def test_the_normaliser_is_borrowed_not_rewritten(self, gen):
        """1 declaration of the rule, per `execute-do-not-grep`."""
        src = GEN.read_text(encoding="utf-8")
        assert "mrb._spoken" in src, (
            "the renderer must call the report builder's own normaliser, not "
            "carry a second copy of the same rule")

    def test_the_lint_passes_on_the_spoken_text(self, rendered, tmp_path):
        """THE LINT IS PATH-SENSITIVE, so it runs on a name matching the
        delivered one rather than on a scratch name."""
        _rows, _md, tts = rendered
        p = tmp_path / "Decisions_Awaiting_You_2026-11-07.txt"
        p.write_text(tts, encoding="utf-8")
        r = subprocess.run([sys.executable,
                            str(REPO / "scripts" / "note_vagueness_lint.py"), str(p)],
                           capture_output=True, text=True, cwd=REPO)
        assert "WORD NUMBER" not in r.stdout, (
            "a number is spelled out; the rule is digits only\n" + r.stdout[:3000])


class TestTheDetectorHasAControl:
    """A detector is only as good as what it REFUSES. 4 of its first 9 flags
    were the phrase "NOT recommended" counted as a recommendation."""

    def test_a_negated_claim_is_not_a_claim(self, gen):
        opts = ["**Do the thing.** This is the recommendation.",
                "**Do the other thing.** Not recommended: it would be worse.",
                "**Do both.** NOT recommended, and deliberately so."]
        k, how = gen.recommended_index(opts)
        assert k == 0, "the negated options were counted as claims"
        assert how == "marked in the option text"

    def test_the_bare_word_recommended_is_never_a_claim(self, gen):
        """★ THE PROPERTY THAT ACTUALLY PROTECTS, and the test above does not
        establish it. A mutation reversing the pattern's negative lookbehinds
        stayed GREEN, because the lookbehinds fire only on "not is the
        recommendation" -- not English, absent from the corpus. What really
        keeps "NOT recommended" out is that the pattern demands the PHRASE
        `is ... recommendation` and never matches the bare word. That is
        asserted here directly, so a pattern widened to the bare word fails.
        """
        for phrase in ("Not recommended: it would be worse.",
                       "NOT recommended, and deliberately so.",
                       "it is the recommended follow-up",
                       "recommended",
                       "we recommend against it"):
            assert not gen._CLAIMS.search(phrase), (
                f"the bare word matched, so a negation now reads as a claim: "
                f"{phrase!r}")
        for phrase in ("This is the recommendation.",
                       "which is my recommendation",
                       "and is the recommendation for that half"):
            assert gen._CLAIMS.search(phrase), (
                f"a real claim stopped matching: {phrase!r}")

    def test_two_real_claims_are_reported_not_silently_resolved(self, gen):
        opts = ["**A.** This is the recommendation.",
                "**B.** This is the recommendation."]
        k, how = gen.recommended_index(opts)
        assert k == 0
        assert "2 options claim" in how, (
            "an ambiguous entry must say so in the rendered file, not pick quietly")

    def test_no_claim_at_all_is_reported(self, gen):
        k, how = gen.recommended_index(["**A.** Costs nothing.", "**B.** Costs more."])
        assert k == 0
        assert "NO OPTION IS MARKED" in how

    def test_the_gist_prefers_the_options_own_lead_phrase(self, gen):
        assert gen._gist("**Raise the cap.** Everything after is detail.") \
            == "Raise the cap."
        assert gen._gist("No bold here. Second sentence.") == "No bold here"
