#!/usr/bin/env python3
"""A note is held to the version its foot-line declares, and never silently exempted.

THE HOLE, FOUND 2026-09-17. The v1.7 enforcement decided a note's version with
`FOOTLINE.search`, which returns the FIRST mention of "CDSFL note standard vX.Y"
anywhere in the text. A note quoting an older version in its prose before its own
v1.7 foot-line was classified by the quotation and silently exempted from Rules
27 and 28. The revision reader in `scripts/lint_reach_over_notes_2026-09-10.py`
counted ANY mention, so the 2 halves also disagreed whenever a note's mentions
fell on both sides of v1.7 -- which turned the suite red at 05:56 that morning.

THE ADOPTED RULE, AND WHY IT IS THE ONE THAT FAILS CLOSED. A note is held to the
HIGHEST version declared on any line shaped like a foot-line, however that line is
formatted; a mention in the middle of a sentence never counts. Under-enforcement
is silent and over-enforcement is loud, so when the rules must err, this one errs
loudly. The first version of the fix took the LAST foot-line with a strict
pattern, and an independent review showed both choices silently exempting notes.

EACH REJECTED RULE IS SHOWN WRONG ON ITS OWN FIXTURE below, so these tests prove
the rules actually differ rather than assuming it. The format and prose-only
tests pin properties of the adopted rule and are not claimed to fool anything.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
GUARD = ROOT / "bench" / "tests" / "test_note_standard_v17_enforced_2026-08-26.py"
SCRIPT = ROOT / "scripts" / "lint_reach_over_notes_2026-09-10.py"

FOOT17 = "Written under CDSFL note standard v1.7 (26 August 2026)."
FOOT14 = "Written under CDSFL note standard v1.4 (13 August 2026)."

FIXTURES = {
    # a prose mention of an OLDER version before the real v1.7 foot-line
    "quote_first.md": ("# A note\n\nThe earlier record cites CDSFL note standard v1.4 throughout.\n\n"
                       f"Body text.\n\n{FOOT17}\n"),
    # a prose mention of a NEWER version in a note whose foot-line is v1.4
    "mention_ahead.md": ("# An older note\n\nThis will move to CDSFL note standard v1.7 once revised.\n\n"
                         f"{FOOT14}\n"),
    # the real v1.7 foot-line, then a later prose mention of an older version
    "later_prose.md": (f"# A note\n\nBody.\n\n{FOOT17}\n\n"
                       "Appendix: the older CDSFL note standard v1.4 is superseded.\n"),
    # the real v1.7 foot-line, then a QUOTED older foot-line, blockquoted
    "quoted_old_footline.md": (f"# A note\n\nBody.\n\n{FOOT17}\n\nFrom the old record:\n\n> {FOOT14}\n"),
}
HELD_V17 = {"quote_first.md", "later_prose.md", "quoted_old_footline.md"}

OLD = re.compile(r"CDSFL note standard v(\d+)\.(\d+)")
STRICT_FIRST_FIX = re.compile(r"^[\s*_>]*Written under CDSFL note standard v(\d+)\.(\d+)")


def _v(m):
    return (int(m.group(1)), int(m.group(2)))


def first_mention(t):
    m = OLD.search(t)
    return _v(m) if m else None


def any_mention_v17(t):
    return any(_v(m) >= (1, 7) for m in OLD.finditer(t))


def last_mention(t):
    ms = list(OLD.finditer(t))
    return _v(ms[-1]) if ms else None


def last_strict_footline(t):
    found = None
    for line in t.split("\n"):
        m = STRICT_FIRST_FIX.match(line)
        if m:
            found = _v(m)
    return found


def _load(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def g():
    return _load(GUARD, "v17_guard_footline")


class TestEveryRejectedRuleFailsOnItsFixture:
    """ANTI-VACUITY. If a rejected rule got its fixture right, the adopted rule's
    passing on that fixture would prove nothing about the choice."""

    def test_first_mention_is_fooled_by_an_earlier_quotation(self):
        assert first_mention(FIXTURES["quote_first.md"]) == (1, 4)

    def test_any_mention_is_fooled_by_a_forward_mention(self):
        assert any_mention_v17(FIXTURES["mention_ahead.md"]) is True

    def test_last_mention_is_fooled_by_a_later_quotation(self):
        assert last_mention(FIXTURES["later_prose.md"]) == (1, 4)

    def test_the_first_fix_was_fooled_by_a_quoted_old_footline(self):
        assert last_strict_footline(FIXTURES["quoted_old_footline.md"]) == (1, 4)

    def test_the_first_fix_silently_skipped_a_list_formatted_footline(self):
        assert last_strict_footline(f"text\n\n- {FOOT17}\n") is None


class TestTheAdoptedRule:
    @pytest.mark.parametrize("name", sorted(FIXTURES))
    def test_each_fixture_is_held_to_the_right_version(self, g, name):
        want = (1, 7) if name in HELD_V17 else (1, 4)
        assert g.declared_version(FIXTURES[name]) == want

    def test_a_mid_sentence_mention_alone_declares_nothing(self, g):
        assert g.declared_version("This project follows CDSFL note standard v1.7.\n") is None

    def test_an_older_note_quoting_a_newer_footline_is_enforced(self, g):
        """THE FAIL-SAFE DIRECTION, pinned deliberately: over-enforcement is loud."""
        assert g.declared_version(f"{FOOT14}\n\nQuoted:\n\n{FOOT17}\n") == (1, 7)

    @pytest.mark.parametrize("line", [
        FOOT17,
        f"*{FOOT17}*",
        f"_{FOOT17}_",
        f"- {FOOT17}",
        f"<p>{FOOT17}</p>",
        f"#### {FOOT17}",
        f"`{FOOT17}`",
        "**Written under** CDSFL note standard v1.7 (26 August 2026).",
        "Written under CDSFL note standard v1.7 (26 August 2026).",
        "Written under the CDSFL note standard v1.7 (26 August 2026).",
        "written under CDSFL note standard v1.7 (26 August 2026).",
        f"​{FOOT17}",
        f"<!-- {FOOT17} -->",
        f"<!--{FOOT17}-->",
        f"2026-09-17, 10:00 BST. {FOOT17}",
        f"1. {FOOT17}",
    ])
    def test_every_footline_format_is_read(self, g, line):
        assert g.declared_version(f"text\n\n{line}\n") == (1, 7)

    @pytest.mark.parametrize("line", [
        "<!-- -->" * 40 + "x",
        "<>" * 40 + "x",
        "<br>" * 200 + "no foot-line here",
        "<" * 80000 + "x",
    ])
    def test_a_line_of_tags_cannot_stall_the_reader(self, g, line):
        """A RATCHET ON CATASTROPHIC BACKTRACKING. The first tolerant pattern took
        0.254 s on 20 repeats of `<!-- -->` and grew about 15 times per 4 more, so
        40 would not finish. The bound is deliberately loose; the possessive form
        takes microseconds."""
        import time
        t0 = time.perf_counter()
        assert g.declared_version(line + "\n") is None
        assert time.perf_counter() - t0 < 1.0

    def test_a_label_before_the_footline_is_a_known_gap(self, g):
        """PINNED AS A LIMITATION, NOT A FEATURE. The first-mention rule read this;
        the adopted rule does not. A real note in this shape would lose enforcement,
        which TestNoRealNoteIsExempted refuses."""
        assert g.declared_version(f"Footer: {FOOT17}\n") is None
        assert first_mention(f"Footer: {FOOT17}\n") == (1, 7)

    def test_case_folds_in_ascii_as_git_grep_does(self, g):
        """`git grep -i` does not fold a dotted capital I to "i"; neither may the
        rule, or the 2 readers disagree about the same bytes."""
        assert g.declared_version("Wr\u0130tten under CDSFL note standard v1.7.\n") is None

    def test_a_missing_minor_version_reads_as_zero(self, g):
        assert g.declared_version("Written under CDSFL note standard v1 (21 April 2026).\n") == (1, 0)


class TestEveryReaderUsesIt:
    def _tree(self, tmp_path):
        for name, text in FIXTURES.items():
            (tmp_path / name).write_text(text, encoding="utf-8")
        return tmp_path

    def test_the_live_selector(self, g, tmp_path, monkeypatch):
        monkeypatch.setattr(g, "NOTES", self._tree(tmp_path))
        assert {p.name for p in g._v17_notes()} == HELD_V17

    def test_the_working_tree_population_reader(self, g, tmp_path):
        """`declaring()` had no test at all until an independent review found that
        reverting it, emptying it, or lowering its floor passed every assertion."""
        mod = _load(SCRIPT, "lint_reach_footline_decl")
        tree = self._tree(tmp_path)
        got = mod.declaring(sorted(tree.glob("*.md")), g.FOOTLINE)
        assert {p.name for p in got} == HELD_V17

    def test_a_substituted_pattern_cannot_change_the_answer(self, g, tmp_path):
        """A pattern written differently from the live one, matching the same
        strings, used to switch `declaring()` silently back to first-mention."""
        mod = _load(SCRIPT, "lint_reach_footline_sub")
        tree = self._tree(tmp_path)
        equivalent = re.compile(r"CDSFL note standard v(\d+)\.(\d+)(?:)")
        got = mod.declaring(sorted(tree.glob("*.md")), equivalent)
        assert {p.name for p in got} == HELD_V17


GIT_FIXTURES = {
    **{name: text.encode("utf-8") for name, text in FIXTURES.items()},
    "html_comment.md": f"# A note\n\nBody.\n\n<!-- {FOOT17} -->\n".encode("utf-8"),
    "date_stamped.md": f"# A note\n\nBody.\n\n2026-09-17, 10:00 BST. {FOOT17}\n".encode("utf-8"),
    "crlf.md": f"# A note\r\n\r\nBody.\r\n\r\n{FOOT17}\r\n".encode("utf-8"),
    "cr_only.md": f"# A note\r\rBody.\r\r{FOOT17}\r".encode("utf-8"),
    "latin1_older.md": f"# Caf\xe9\n\nIt was written at the caf\xe9.\n\n{FOOT14}\n".encode("latin-1"),
}
GIT_HELD_V17 = HELD_V17 | {"html_comment.md", "date_stamped.md", "crlf.md", "cr_only.md"}


def _git_repo(tmp_path: pathlib.Path) -> pathlib.Path:
    """A throwaway repository holding the fixtures, committed, plus a Latin-1
    non-note file containing "written" -- the input that crashed the text-mode
    reader once its search was widened."""
    root = tmp_path / "repo"
    notes = root / "experimental_notes"
    (notes / "evidence").mkdir(parents=True)
    for name, data in GIT_FIXTURES.items():
        (notes / name).write_bytes(data)
    (notes / "evidence" / "seat_transcript.txt").write_bytes("caf\xe9, written\n".encode("latin-1"))

    def git(*args):
        subprocess.run(["git", "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid",
                        "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null",
                        "-c", "core.autocrlf=false", *args],
                       cwd=root, check=True, capture_output=True, timeout=60)

    git("init", "-q")
    git("add", "-A")
    git("commit", "-q", "-m", "fixtures")
    return root


class TestAgainstRealGit:
    """The revision reader driven by a REAL `git grep` over a throwaway repository.

    A synthesised grep output proves only that the parser reads what the test's
    author imagined git prints. Round 2 of the review showed that is not enough:
    narrowing the real search back to a case-sensitive literal passed every
    synthesised test, and a git setting that adds line numbers made the real
    reader return 0 of 379.
    """

    def test_the_revision_reader_matches_the_live_selector(self, g, tmp_path, monkeypatch):
        root = _git_repo(tmp_path)
        monkeypatch.setattr(g, "NOTES", root / "experimental_notes")
        assert {p.name for p in g._v17_notes()} == GIT_HELD_V17
        mod = _load(SCRIPT, "lint_reach_realgit")
        monkeypatch.setattr(mod, "REPO", root)
        got = mod._revision_declaring.__wrapped__("HEAD")
        assert {pathlib.PurePosixPath(p).name for p in got} == GIT_HELD_V17

    def test_git_settings_cannot_change_the_answer(self, tmp_path, monkeypatch):
        root = _git_repo(tmp_path)
        mod = _load(SCRIPT, "lint_reach_realgit_cfg")
        monkeypatch.setattr(mod, "REPO", root)
        monkeypatch.setenv("GIT_CONFIG_COUNT", "2")
        monkeypatch.setenv("GIT_CONFIG_KEY_0", "grep.lineNumber")
        monkeypatch.setenv("GIT_CONFIG_VALUE_0", "true")
        monkeypatch.setenv("GIT_CONFIG_KEY_1", "grep.column")
        monkeypatch.setenv("GIT_CONFIG_VALUE_1", "true")
        got = mod._revision_declaring.__wrapped__("HEAD")
        assert {pathlib.PurePosixPath(p).name for p in got} == GIT_HELD_V17

    def test_the_slow_fallback_decides_the_same_way(self, tmp_path, monkeypatch):
        """No caller reaches this path today, so it is reached here: a pattern
        written differently from the live one forces it."""
        root = _git_repo(tmp_path)
        mod = _load(SCRIPT, "lint_reach_realgit_fb")
        monkeypatch.setattr(mod, "REPO", root)
        equivalent = re.compile(r"CDSFL note standard v(\d+)\.(\d+)(?:)")
        assert mod.at_revision("HEAD", True, equivalent) == (len(GIT_HELD_V17), len(GIT_FIXTURES))


class TestNoRealNoteIsExempted:
    def test_no_note_loses_enforcement_it_had_under_first_mention(self, g):
        """DIRECTION-AWARE. A note the old rule enforced and the new rule exempts is
        the silent failure this whole change exists to prevent. It must never be
        accepted as "a quotation the fix correctly ignores": find the format the
        reader missed and teach `FOOTLINE_LINE` it."""
        lost = []
        for p in sorted(g.NOTES.rglob("*.md")):
            t = p.read_text(encoding="utf-8", errors="replace")
            old = first_mention(t)
            new = g.declared_version(t)
            if old and old >= (1, 7) and not (new and new >= (1, 7)):
                lost.append(str(p.relative_to(ROOT)))
        assert not lost, f"notes silently exempted by the new rule: {lost}"

    def test_any_note_gaining_enforcement_is_reviewed(self, g):
        """The loud direction. A note the new rule enforces and the old did not is
        allowed in principle -- that is failing closed -- but each one is named so
        it is looked at, not absorbed. None exists at adoption."""
        gained = []
        for p in sorted(g.NOTES.rglob("*.md")):
            t = p.read_text(encoding="utf-8", errors="replace")
            old = first_mention(t)
            new = g.declared_version(t)
            if new and new >= (1, 7) and not (old and old >= (1, 7)):
                gained.append(str(p.relative_to(ROOT)))
        assert not gained, (
            f"now enforced under v1.7 and previously not: {gained}. Confirm each is "
            f"genuinely a v1.7 note or lints clean, then update this assertion.")
