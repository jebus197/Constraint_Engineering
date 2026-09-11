"""The citation repair must not damage the citations it is not repairing.

FOUND 2026-09-11 BY DELIBERATELY BREAKING ONE CITATION AND COMMITTING.

The probe was for something else -- proving that a stage-0 repair now reaches
the commit -- so 1 citation in the master task list was staled to
`reference_runner_v3.py:1` and the commit was allowed to run. The repair landed
at HEAD, which is what the probe was testing. It also did this, in the same
pass:

    in reference_runner_v3.py, line number before -> after:
        10934  ->  114560934
        12638  ->  114562638
        14984  ->  114564984

    They are written bare rather than as `path:number` tokens: a scanner cannot
    tell a warning about a corrupted citation from a corrupted citation, and
    test_no_citation_carries_a_corrupted_number flagged this paragraph when it
    was written the other way.

3 correct citations destroyed while repairing 1, and they reached HEAD.

THE CAUSE was a single line: `txt.replace(f"{target}:{line}", f"{target}:{lo}")`.
An unbounded substring replace with no digit boundary, so a SHORT stale number
rewrites the PREFIX of every longer one; and a GLOBAL one, so a correct citation
sharing the stale number is moved along with it.

WHY THIS IS NOT AN ARTEFACT OF A CONTRIVED PROBE. The probe used `:1` because it
was convenient, but the fault needs only that a stale number be a prefix of
another number for the same file. `reference_runner_v3.py` is 15,587 lines, so
its citations are 2 to 5 digits and collide constantly: `:1135` eats `:11354`,
`:963` eats `:9634`. The class below demonstrates the 4-digit/5-digit case with
no `:1` anywhere.

EVERY TEST HERE CALLS `repair`. The corrupting line was present, readable and
obviously a string replace for a full day; reading it is what failed.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "citation_content_guard_2026-09-10.py"


@pytest.fixture()
def guard(tmp_path, monkeypatch):
    """The real module, pointed at a scratch tree instead of the repository."""
    spec = importlib.util.spec_from_file_location("citguard", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    monkeypatch.setattr(m, "REPO", tmp_path)
    monkeypatch.setattr(m, "CITED", ("toy_target.py",))
    monkeypatch.setattr(m, "SEARCH", ("*.md",))
    return m


def _toy_target(tmp_path: Path, defs: dict[int, str]) -> None:
    """Write toy_target.py with each named symbol defined at the given line.

    NAMED `toy_target` DELIBERATELY. Its fixture strings are citation-shaped --
    `name.py:NNN` -- and this file is tracked, so
    test_line_citations_resolve_2026-09-01.py reads them as real citations to a
    file that does not exist. It refused the first commit of this file with 13
    findings, every one a fixture string. `toy_target` is already in that
    guard's PLACEHOLDER list, which is the project's existing way of saying
    "illustrative, not a citation"; inventing a second mechanism would have been
    the worse fix.
    """
    top = max(defs) + 2
    lines = ["# padding"] * top
    for line, name in defs.items():
        lines[line - 1] = f"def {name}():"
        lines[line] = "    pass"
    (tmp_path / "toy_target.py").write_text("\n".join(lines) + "\n", encoding="utf-8")


class TestTheShortNumberDoesNotEatTheLongOne:
    def test_a_correct_citation_is_left_alone(self, guard, tmp_path):
        _toy_target(tmp_path, {100: "alpha", 12: "beta"})
        doc = tmp_path / "doc.md"
        doc.write_text(
            "The gate `alpha` lives at toy_target.py:1 today.\n"
            "The helper `beta` lives at toy_target.py:12 today.\n", encoding="utf-8")

        assert guard.repair("toy_target.py") == 1, "exactly 1 citation is stale"
        out = doc.read_text(encoding="utf-8")
        assert "toy_target.py:100 today" in out, "the stale citation was not repaired"
        assert "toy_target.py:12 today" in out, (
            "the CORRECT citation was rewritten as a side effect -- this is the "
            "2026-09-11 corruption")
        assert "toy_target.py:1002" not in out

    def test_the_old_one_line_replace_does_corrupt_it(self, tmp_path):
        """MUTATION CONTROL. If the defect does not reproduce here, the test
        above is passing for a reason unconnected to the fix."""
        text = ("The gate `alpha` lives at toy_target.py:1 today.\n"
                "The helper `beta` lives at toy_target.py:12 today.\n")
        corrupted = text.replace("toy_target.py:1", "toy_target.py:100")
        assert "toy_target.py:1002" in corrupted, (
            "the unbounded replace no longer corrupts, so this file's premise "
            "is wrong")

    def test_four_digits_eating_five_digits(self, guard, tmp_path):
        """NO `:1` ANYWHERE. The fault is about prefixes, not about small
        numbers, and the repository's own citations are 4 and 5 digits."""
        _toy_target(tmp_path, {9001: "alpha", 11354: "beta"})
        doc = tmp_path / "doc.md"
        doc.write_text(
            "`alpha` at toy_target.py:1135 is stale.\n"
            "`beta` at toy_target.py:11354 is correct.\n", encoding="utf-8")

        assert guard.repair("toy_target.py") == 1
        out = doc.read_text(encoding="utf-8")
        assert "toy_target.py:9001 is stale" in out
        assert "toy_target.py:11354 is correct" in out, (
            "a 5-digit citation was eaten by a 4-digit repair")


class TestOnlyTheStaleOccurrenceMoves:
    def test_a_shared_line_number_is_repaired_per_citation(self, guard, tmp_path):
        """The replace was GLOBAL. Two citations carrying the same number, 1
        stale and 1 correct, were both rewritten -- moving a citation that
        pointed inside its own symbol out of it."""
        _toy_target(tmp_path, {50: "alpha", 40: "beta"})
        doc = tmp_path / "doc.md"
        doc.write_text(
            "`alpha` at toy_target.py:40 is stale.\n"
            "`beta` at toy_target.py:40 is correct.\n", encoding="utf-8")

        assert guard.repair("toy_target.py") == 1
        out = doc.read_text(encoding="utf-8")
        assert "toy_target.py:50 is stale" in out
        assert "toy_target.py:40 is correct" in out, (
            "the correct citation moved too; a global replace cannot tell them "
            "apart")

    def test_several_stale_citations_in_one_file_all_land(self, guard, tmp_path):
        """Right-to-left splicing: an early edit must not invalidate a later
        offset."""
        _toy_target(tmp_path, {70: "alpha", 80: "beta", 90: "gamma"})
        doc = tmp_path / "doc.md"
        doc.write_text(
            "`alpha` at toy_target.py:2\n"
            "`beta` at toy_target.py:3\n"
            "`gamma` at toy_target.py:4\n", encoding="utf-8")

        assert guard.repair("toy_target.py") == 3
        out = doc.read_text(encoding="utf-8")
        assert "toy_target.py:70" in out and "toy_target.py:80" in out \
            and "toy_target.py:90" in out, out


class TestItStillDoesItsJob:
    """ANTI-VACUITY: a repair that repaired nothing would pass every test above
    about not corrupting anything."""

    def test_a_clean_document_reports_zero(self, guard, tmp_path):
        _toy_target(tmp_path, {30: "alpha"})
        doc = tmp_path / "doc.md"
        doc.write_text("`alpha` at toy_target.py:30\n", encoding="utf-8")
        before = doc.read_text(encoding="utf-8")
        assert guard.repair("toy_target.py") == 0
        assert doc.read_text(encoding="utf-8") == before

    def test_the_count_it_returns_is_the_count_it_wrote(self, guard, tmp_path):
        """The old version returned `len(bad)` whether or not a write happened."""
        _toy_target(tmp_path, {60: "alpha"})
        doc = tmp_path / "doc.md"
        doc.write_text("`alpha` at toy_target.py:5\n", encoding="utf-8")
        n = guard.repair("toy_target.py")
        assert n == 1
        assert "toy_target.py:60" in doc.read_text(encoding="utf-8")
        assert guard.repair("toy_target.py") == 0, "it should now be idempotent"


class TestTheRealRepositoryIsClean:
    def test_no_citation_carries_a_corrupted_number(self):
        """The 3 corrupted citations reached HEAD on 2026-09-11 and were
        restored by hand. This keeps them restored: no citation may point past
        the end of the file it names."""
        import re
        target = "bench/reference_runner_v3.py"
        n_lines = len((REPO / target).read_text(encoding="utf-8").splitlines())
        rx = re.compile(re.escape(target.split("/")[-1]) + r":(\d+)")
        offenders = []
        for pat in ("experimental_notes/**/*.md", "resources/*.md",
                    "bench/tests/*.py", "scripts/*.py", ".claude/*.md"):
            for p in REPO.glob(pat):
                if not p.is_file():
                    continue
                for m in rx.finditer(p.read_text(encoding="utf-8", errors="replace")):
                    if int(m.group(1)) > n_lines:
                        offenders.append(f"{p.relative_to(REPO)}:{m.group(1)}")
        assert not offenders, (
            f"{len(offenders)} citation(s) point past line {n_lines} of "
            f"{target}: {offenders}")


class TestOneFileCannotKillTheWholePass:
    """`check()` read with errors="replace" and `repair()` with the strict
    default. One bad byte in one note raised inside `repair()`, the hook's
    `|| true` swallowed it, and NO citation was repaired in that pass -- the
    "repair lags a commit behind" defect re-entering through the repair that
    exists to close it. Found independently by both panel seats, round 14.

    Reachability today is 0: 866 citing files, 0 invalid UTF-8, 0 CRLF, Wilson
    [0.0000%, 0.4416%] for each. Nothing enforces LF or UTF-8 on these paths --
    there is no .gitattributes and no encoding check -- which is why this is a
    mechanism and not a note."""

    def test_an_undecodable_file_is_refused_and_the_good_one_is_repaired(
            self, guard, tmp_path, capsys):
        _toy_target(tmp_path, {40: "alpha"})
        bad = tmp_path / "bad.md"
        bad.write_bytes(b"\xff\xfe `alpha` at toy_target.py:12 here\n")
        good = tmp_path / "good.md"
        good.write_text("`alpha` at toy_target.py:12 here\n", encoding="utf-8")
        before = bad.read_bytes()

        n = guard.repair("toy_target.py")

        assert "toy_target.py:40" in good.read_text(encoding="utf-8"), (
            "one undecodable file stopped the whole pass; every other file "
            "ships stale and HEAD is broken in a clone")
        assert bad.read_bytes() == before, "the undecodable file was rewritten"
        assert n == 1, n
        assert "REFUSED" in capsys.readouterr().err

    def test_crlf_line_endings_survive_a_repair(self, guard, tmp_path):
        """read_text translates CRLF in and write_text writes LF out, so
        repairing 1 number rewrote EVERY line ending. Worse, the translation
        makes check()'s offsets index a different string from the bytes on disk,
        so a positional splice lands in the wrong place."""
        _toy_target(tmp_path, {40: "alpha"})
        doc = tmp_path / "crlf.md"
        doc.write_bytes(b"intro\r\n`alpha` at toy_target.py:12 here\r\nend\r\n")

        assert guard.repair("toy_target.py") == 1
        out = doc.read_bytes()
        assert b"\r\n" in out, "the repair rewrote every line ending in the file"
        assert b"toy_target.py:40" in out, "the splice landed in the wrong place"
        assert out.count(b"\r\n") == 3, out

    def test_the_reader_is_shared_by_check_and_repair(self, guard, tmp_path):
        """ANTI-DRIFT. The 2 faults above both came from 2 readers. This asserts
        there is 1, by calling it -- not by reading the source."""
        doc = tmp_path / "x.md"
        doc.write_bytes(b"line\r\nnext\r\n")
        raw, txt = guard.read_citing(doc)
        assert raw == b"line\r\nnext\r\n"
        assert txt == "line\r\nnext\r\n", (
            "the shared reader translates newlines, so offsets and bytes "
            "disagree again")
        assert txt.encode("utf-8") == raw
