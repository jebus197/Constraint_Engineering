#!/usr/bin/env python3
"""The morning report's markdown companion is GENERATED, and the generator is
reachable from a fresh clone.

WHY THIS FILE EXISTS, AND IT CLOSES A GAP I CREATED THE SAME NIGHT. On
2026-10-30 a note-lint finding in `experimental_notes/Morning_Report_2026-10-30.md`
was fixed BY HAND and the next rebuild put it straight back, because the file is
generated from `scripts/rebuild_morning_report_markdown_2026-10-30.py`. The
generator was committed so the fix would survive -- and committed with **0 test
files naming it**, measured by `grep -rl` over `bench/tests/`. That is the
addition-nothing-reaches half of the additive standard, the shape this project
has confirmed 11 times, committed about an hour after a memory about producers
was extended to cover exactly it.

THE SECOND DEFECT WAS WORSE AND LESS VISIBLE. The generator's source was
`~/Desktop/CDSFL_tts/Morning_Report_2026-10-30.txt`, an UNVERSIONED file on one
machine's Desktop. A generated artefact whose source is not in the repository
cannot be rebuilt from a clone, which is entry A2's whole subject, and an
unversioned file on one Desktop is the single point of failure this project
already named when it made the repo copy of the task list canonical. The source
is now the repo copy, with the Desktop copy a fallback that is then brought back
into agreement. Both were byte-identical at 37,058 bytes when this changed.

WHAT THIS PINS. That the committed markdown MATCHES a rebuild, so a hand edit to
it fails here rather than being silently reverted later; that the generator reads
a VERSIONED source; that `--check` writes nothing, so a guard cannot mutate the
tree; and that a deliberate corruption is DETECTED, which is the control that
makes the match assertion worth anything.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

GENERATOR = (REPO / "scripts"
             / "rebuild_morning_report_markdown_2026-10-30.py")
DST = REPO / "experimental_notes" / "Morning_Report_2026-10-30.md"


def _gen():
    assert GENERATOR.is_file(), f"generator absent: {GENERATOR}"
    spec = importlib.util.spec_from_file_location("mr_md_rebuild", GENERATOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def gen():
    return _gen()


class TestItIsReproducibleFromTheRepository:
    def test_the_source_is_versioned(self, gen):
        """A generated file whose source is not tracked cannot be rebuilt from
        a clone, which is entry A2's subject."""
        # ASKS the generator for its paths rather than restating them. They
        # were module constants until 2026-10-31, when `--date` made them a
        # function of the report date; a test that hardcoded the filenames would
        # have gone on passing against the wrong day's file.
        repo_txt, _desktop_txt, _dst = gen.paths(gen.DEFAULT_DATE)
        src = gen.source()
        assert src == repo_txt, (
            f"the generator is reading {src}, not the repository copy "
            f"{repo_txt}. If the repo copy has gone, restore it rather "
            f"than letting the Desktop fallback become the source of truth.")
        r = subprocess.run(["git", "ls-files", "--error-unmatch",
                            str(src.relative_to(REPO))],
                           capture_output=True, text=True, cwd=str(REPO))
        assert r.returncode == 0, (
            f"{src.relative_to(REPO)} is not tracked by git: {r.stderr.strip()}")

    def test_the_two_spoken_copies_agree(self, gen):
        """They diverged once already, 85 lines against 115."""
        repo_txt, desktop_txt, _dst = gen.paths(gen.DEFAULT_DATE)
        if not desktop_txt.is_file():
            pytest.skip("no Desktop copy on this machine; nothing to compare")
        assert repo_txt.read_text() == desktop_txt.read_text(), (
            "the repository and Desktop spoken copies have diverged; run the "
            "generator to bring them back into agreement")


class TestTheCommittedMarkdownMatchesARebuild:
    def test_check_mode_passes_on_the_committed_file(self, gen):
        assert gen.main(["--check"]) == 0, (
            "the committed markdown differs from a rebuild. Fix the GENERATOR, "
            "not the markdown: a hand edit to the .md is undone by the next "
            "rebuild, which is how this guard came to exist.")

    def test_check_mode_writes_nothing(self, gen):
        """A guard that mutates the tree is worse than no guard."""
        before = DST.read_bytes()
        gen.main(["--check"])
        assert DST.read_bytes() == before, (
            "--check modified the markdown file, so running the guard changes "
            "the thing it checks")

    def test_a_corrupted_markdown_is_detected(self, gen):
        """THE CONTROL. Without it, `--check` returning 0 says nothing: a
        generator that always agreed with itself would pass the test above."""
        original = DST.read_bytes()
        try:
            DST.write_text(DST.read_text() + "\na line no rebuild would emit\n")
            assert gen.main(["--check"]) == 1, (
                "an appended line was NOT detected, so --check cannot tell the "
                "committed file from a rebuild and every 0 it returns is "
                "uninformative")
        finally:
            DST.write_bytes(original)
        assert DST.read_bytes() == original, "the control failed to restore"

    def test_a_truncated_diff_states_what_it_withheld(self, gen, capsys):
        """★ ADDED 2026-10-30, after the full board caught the 3rd defect in
        this generator in a single day.

        `test_no_script_prints_a_capped_listing_in_silence` in
        `bench/tests/test_operational_scripts.py` reported
        *"main() prints diff[:40] and never says what it withheld"*. A cap is
        right -- a 2,000-line diff in a terminal is unreadable -- but a cap that
        does not name its remainder reads as a complete list, which is the
        silent falsehood that test exists to refuse.

        THAT DETECTOR ALREADY GUARDS THE PATTERN. This guards the ARITHMETIC,
        because the detector is satisfied by the presence of a disclosure and
        cannot tell `len(diff) - 40` from any other expression. Measured by
        execution with 60 appended lines: 64 diff lines, 40 shown, 24 named.
        """
        original = DST.read_bytes()
        try:
            extra = "\n".join(f"synthetic line {i}" for i in range(60))
            DST.write_text(DST.read_text() + "\n" + extra)
            capsys.readouterr()
            assert gen.main(["--check"]) == 1
            out = capsys.readouterr().out
        finally:
            DST.write_bytes(original)
        assert DST.read_bytes() == original, "the control failed to restore"

        shown = gen._DIFF_LINES_SHOWN
        printed = [l for l in out.split("\n") if l.startswith("  ")
                   and "further diff line(s) not shown" not in l]
        assert len(printed) == shown, (
            f"{len(printed)} diff line(s) were printed, not the capped {shown}")
        tail = [l for l in out.split("\n") if "further diff line(s) not shown" in l]
        assert tail, (
            "a diff longer than the cap printed no remainder line, so the "
            "listing reads as complete when it is not")
        import re as _re
        m = _re.search(r"and (\d+) further diff line\(s\)", tail[0])
        assert m, f"the remainder line names no count: {tail[0]!r}"
        total = int(_re.search(r"(\d+) diff line\(s\)", out).group(1))
        assert int(m.group(1)) == total - shown, (
            f"the remainder says {m.group(1)} but {total} - {shown} = "
            f"{total - shown}; a disclosed cap with wrong arithmetic is worse "
            f"than none, because it looks checked")

    def test_render_is_deterministic(self, gen):
        """2 renders of the same source must agree, or the match above is luck."""
        assert gen.render() == gen.render()


class TestThePartStyleReportAndTheDateArgument:
    r"""Added 2026-10-31, when `--date` and the PART renderer were added.

    Without these the new code path is an addition nothing reaches, which is the
    shape this project has confirmed 11 times. Every assertion CALLS the
    generator.

    VERIFIED RED, 1 mutation per assertion, because a test that cannot be made
    to fail proves nothing:

      * drop the `(?=[A-Z0-9])` lookahead  -> the lower-case-continuation test
      * relax `\s+` to `\s*`               -> the decimal test
      * `.capitalize()` the PART heading   -> the heading-case test
      * move DEFAULT_DATE                  -> the default-date test
      * skip `_emphasise_lead`             -> the emphasis test

    The first draft of the decimal test was HOLLOW and the mutation run is what
    exposed it: it passed with and against the lookahead mutation, because a
    decimal has no whitespace after its full stop and so was never a candidate
    boundary either way. It guards the whitespace requirement, not the
    lookahead, and it is only after swapping the mutation that it has teeth.
    """

    def test_the_date_argument_selects_that_days_files(self, gen):
        repo_txt, desktop_txt, dst = gen.paths("2026-10-31")
        assert repo_txt.name == "Morning_Report_2026-10-31.txt"
        assert dst.name == "Morning_Report_2026-10-31.md"
        assert desktop_txt.parent.name == "CDSFL_tts"

    def test_the_default_date_is_unchanged(self, gen):
        # The generalisation must not move the default, or every existing
        # caller silently retargets.
        assert gen.DEFAULT_DATE == "2026-10-30"

    def test_a_part_report_keeps_its_heading_case(self, gen):
        """Every PART heading in the source must reach the markdown with its
        case intact.

        ★ THIS PINNED A LITERAL FROM ONE EDITION AND BROKE ON A LEGITIMATE
        REWRITE, 2026-10-31. It asserted `"## PART 1. 4 CORRECTIONS" in out`,
        which is a sentence from the first edition of that day's report. The
        founder then asked for the report to be rewritten in the agreed format,
        PART 1 was renamed, and the test went red on a document that is more
        correct than the one it was written against -- punishing the repair,
        which is the failure mode `execute-do-not-grep`'s converse names and
        which this project has now recorded 10 times.

        THE PROPERTY IS DOCUMENT-INDEPENDENT AND STRICTLY STRONGER. It reads the
        PART headings out of the SOURCE and requires every one of them to appear
        in the output unchanged, so it holds for any edition, catches a heading
        dropped as well as a heading restyled, and cannot be satisfied by a
        report that happens to contain one remembered string. The anti-vacuity
        control matters here: a source with 0 PART headings would make the
        all() trivially true, so the count is asserted first.
        """
        import re
        src = gen.paths("2026-10-31")[0].read_text()
        heads = [ln.strip() for ln in src.splitlines()
                 if re.match(r"^PART [0-9A-Z]+\.", ln.strip())]
        assert len(heads) >= 5, (
            f"only {len(heads)} PART heading(s) in the source: the check would "
            "be vacuous")
        out = gen.render("2026-10-31")
        # WHOLE LINES, NOT SUBSTRINGS. `"## X"` is a substring of `"### X"`, so a
        # substring test passes on a demoted heading -- found by mutation on
        # 2026-10-31, where changing the emitted level left this green. Matching
        # the line exactly closes that without widening what the test claims.
        lines = set(out.splitlines())
        missing = [h for h in heads if f"## {h}" not in lines]
        assert not missing, (
            "PART heading(s) did not survive into the markdown as a level-2 "
            f"heading with their case intact: {missing[:3]}")
        # The SECTION path lowercases via capitalize(); it must not reach these.
        restyled = [h for h in heads if f"## {h.capitalize()}" in lines]
        assert not restyled, f"PART heading(s) were restyled: {restyled[:3]}"

    def test_a_part_report_emphasises_lead_sentences(self, gen):
        out = gen.render("2026-10-31")
        assert out.count("**") >= 20, "lead sentences are not being emphasised"
        assert out.count("**") % 2 == 0, (
            "unbalanced emphasis markers would corrupt the rendering")

    def test_a_decimal_is_not_read_as_a_sentence_end(self, gen):
        # THE FAILURE MODE THIS PINS. These reports are full of figures like
        # 0.992424, and a full stop inside a number is not a sentence boundary.
        # Treating it as one would bold a fragment and leave the rest of the
        # sentence outside the emphasis.
        line = ("The share was 0.992424 with a 95 per cent interval of "
                "0.980685 to 0.997050. After the wire it was 0.016492.")
        got = gen._emphasise_lead(line)
        assert got.startswith("**The share was 0.992424 with a 95 per cent "
                              "interval of 0.980685 to 0.997050.**"), got
        assert "**The share was 0.992424.**" not in got

    def test_a_lower_case_continuation_is_not_a_boundary(self, gen):
        line = ("The result is in part 4C: nothing is folded back and the "
                "tree is left alone. That is the recommendation.")
        got = gen._emphasise_lead(line)
        assert got.startswith("**The result is in part 4C: nothing is folded "
                              "back and the tree is left alone.**"), got

    def test_a_heading_or_table_row_is_never_emphasised(self, gen):
        for line in ("## PART 5. WHAT IS LEFT", "| a | b |", "- a point",
                     "", "    indented"):
            assert gen._emphasise_lead(line) == line, line

    def test_the_part_report_rebuild_is_stable(self, gen):
        # Rendering twice must give the same bytes, or the committed companion
        # can never match a rebuild.
        assert gen.render("2026-10-31") == gen.render("2026-10-31")

    def test_the_committed_part_companion_matches_a_rebuild(self, gen):
        _r, _d, dst = gen.paths("2026-10-31")
        assert dst.is_file(), f"{dst} missing"
        assert dst.read_text() == gen.render("2026-10-31"), (
            "the 2026-10-31 companion differs from a rebuild; regenerate it "
            "with --date 2026-10-31 rather than editing it by hand")
