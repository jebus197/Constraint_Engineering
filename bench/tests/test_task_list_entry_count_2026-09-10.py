"""M1's figures must be reproducible, and 29 must stay unreproducible.

`measured-rate-travels-with-its-script` says a rate may be cited only if the
script that produced it is committed alongside. M1 cited "15 of 48, 31.25%" with
no producing script, and its first correction repaired the denominator while
inventing a provenance for the discarded one: *"2 different regular expressions
over this file counted 29 entries and 48 entries"*. No counter reads 29 at any
revision of the file.

THESE TESTS CALL THE SCRIPT AND THE ENGINE. None asserts on source text. The
distinction is `execute-do-not-grep`: a test that reads a module's source can
only confirm the module describes itself consistently, and this project has
found 4 defects by executing 2 forms against each other and 0 by reading.
"""
from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "task_list_entry_count_2026-09-10.py"
LIST = ROOT / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"


def _load():
    """Import the script as a module so its functions can be driven directly."""
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location("m1_count", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _load()


@pytest.fixture(scope="module")
def run_output():
    """RUN IT. A script that is cited and never executed is the 6.2 defect."""
    r = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT,
                       capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, (
        f"the script that backs M1's figures does not run: exit {r.returncode}\n"
        f"{r.stdout[-2000:]}\n{r.stderr[-2000:]}")
    return r.stdout


class TestTheScriptRuns:
    def test_it_exits_zero_and_produces_the_figure_m1_quotes(self, run_output):
        assert "15 of 48 = 31.2500%" in run_output, (
            "M1 quotes 15 of 48 = 31.25%; the script did not produce it")

    def test_the_two_interval_tools_agree(self, run_output):
        agreements = re.findall(r"agree to 1e-9: (True|False)", run_output)
        assert agreements, "no cross-tool agreement line was printed at all"
        assert set(agreements) == {"True"}, (
            f"statsmodels and mpmath disagreed: {agreements}")

    def test_the_interval_matches_what_the_entry_claims(self, run_output):
        assert "[19.9457%, 45.3331%]" in run_output, (
            "M1 quotes Wilson [19.9%, 45.3%]")
        assert "[18.6596%, 46.2514%]" in run_output, (
            "M1 quotes Clopper-Pearson [18.7%, 46.3%]")


class TestTwentyNineIsUnreproducible:
    """The claim the second correction rests on."""

    def test_no_counter_reads_29_at_any_revision(self, run_output):
        assert "revisions at which ANY counter reads 29: NONE" in run_output, (
            "a counter now reads 29 somewhere in history — M1's second "
            "correction says none does, and the entry must be revisited")

    def test_the_floors_are_reported_so_the_claim_is_checkable(self, run_output):
        assert "lowest value each counter has ever returned:" in run_output
        assert "engine=35" in run_output, (
            "the engine's historical floor is the number that makes 29 "
            "unreachable; it must be printed, not merely relied upon")

    def test_the_scan_covers_every_revision_not_a_sample(self, mod):
        """A scan of 3 revisions could miss a 29 in the other 24."""
        revs = mod.revisions()
        n_git = subprocess.run(
            ["git", "log", "--format=%h", "--",
             "experimental_notes/CDSFL_MASTER_TASK_LIST.md"],
            cwd=ROOT, capture_output=True, text=True, timeout=120)
        assert len(revs) == len(n_git.stdout.strip().splitlines()), (
            "the script scans fewer revisions than git reports for the file")
        assert len(revs) >= 27, f"only {len(revs)} revisions found"


class TestTheCountersAreDistinguishable:
    """A measurement whose readings cannot differ measures nothing."""

    def test_the_engine_and_the_narrow_pattern_disagree_at_head(self, mod):
        c = mod.counters(LIST.read_text(encoding="utf-8"))
        assert c["engine"] > c["narrow"], (
            "the narrow pattern must miss the lettered sections; if it does not, "
            "the whole argument for a machine-readable marker is gone")
        assert c["engine"] != c["ENTRY raw"], (
            "`_is_entry` drops NOT_ENTRIES headings, so the 2 must differ")

    def test_the_engine_is_the_shipped_one_not_a_copy(self, mod):
        """If this script reimplemented the parser it would prove nothing."""
        import task_list_markers as shipped
        assert mod.ENTRY is shipped.ENTRY, (
            "the script must import the committed ENTRY regex, not retype it")
        assert mod.parse_entries is shipped.parse_entries

    def test_the_engine_count_matches_the_shipped_parser_on_the_live_file(self, mod):
        import task_list_markers as shipped
        assert mod._engine_count(LIST.read_text(encoding="utf-8")) == \
            len(shipped.parse_entries(LIST))


class TestTheNumeratorIsEstablishedNotAssumed:
    def test_fifteen_is_found_under_both_patterns(self, mod):
        text = subprocess.run(
            ["git", "show", "4b697af:experimental_notes/CDSFL_MASTER_TASK_LIST.md"],
            cwd=ROOT, capture_output=True, text=True, timeout=60).stdout
        wide = mod.with_status(text, mod.ENTRY, mod.PROSE_STATUS)
        narrow = mod.with_status(text, mod.NARROW, mod.PROSE_STATUS)
        assert wide == narrow == 15, (
            f"the numerator must not depend on the pattern: wide={wide} narrow={narrow}")

    def test_the_marker_form_finds_none_at_that_revision(self, mod):
        """The first version of the script searched only this form and got 0 of 48."""
        text = subprocess.run(
            ["git", "show", "4b697af:experimental_notes/CDSFL_MASTER_TASK_LIST.md"],
            cwd=ROOT, capture_output=True, text=True, timeout=60).stdout
        assert mod.with_status(text, mod.ENTRY, mod.MARKER_STATUS) == 0, (
            "marker comments did not exist at 4b697af; if this is non-zero the "
            "prose/marker distinction the script documents is wrong")


class TestMutationsAreCaught:
    """Each mutation is asserted APPLIED, and asserted to land on an executed line.

    A mutation that applies to the file but not to a line the fixture runs reads
    as SURVIVED and is not one — that happened twice on 2026-09-09.
    """

    def _mutate(self, old: str, new: str) -> Path:
        """Write the mutant INSIDE scripts/, and prove it still runs.

        THIS HARNESS WAS BROKEN WHEN FIRST WRITTEN, 2026-09-10, and the way it
        was broken is the exact failure it exists to detect. The mutant was
        written to the system temp directory, so the script's own
        `REPO = Path(__file__).resolve().parents[1]` resolved outside the
        repository and every mutant died at startup with FileNotFoundError. Its
        stdout was empty, and `assert "<figure>" not in ""` passes. **A mutant
        that crashes reads as caught.** 3 of 4 mutations here were vacuous and
        reported green.

        So: the mutant lives beside the original, and `_run` REFUSES a mutant
        that did not execute. A mutation is evidence only if the mutated program
        ran and produced a different answer.
        """
        src = SCRIPT.read_text(encoding="utf-8")
        assert old in src, f"MUTATION ANCHOR ABSENT, never applied: {old!r}"
        mutated = src.replace(old, new, 1)
        assert mutated != src, "the replacement changed nothing"
        # `.mutants/` and NOT `scripts/`: a mutant written into scripts/ is
        # visible to every suite-wide scanner that walks that directory, and
        # one showed up as a full-suite failure the moment this harness was
        # first used. `Path("<repo>/.mutants/x.py").parents[1]` is still the
        # repo root, so the script under test resolves its own paths exactly
        # as it does in place.
        pen = SCRIPT.parent.parent / ".mutants"
        pen.mkdir(exist_ok=True)
        p = pen / f"_mutant_{abs(hash(old)) % 10**8}.py"
        p.write_text(mutated, encoding="utf-8")
        return p

    def _run(self, p: Path):
        r = subprocess.run([sys.executable, str(p)], cwd=ROOT,
                           capture_output=True, text=True, timeout=900)
        assert r.returncode == 0 and r.stdout.strip(), (
            "THE MUTANT DID NOT RUN, so it cannot be 'caught' — a crashing "
            f"mutant produces empty output and every `not in` check passes.\n"
            f"exit {r.returncode}\nstdout: {r.stdout[-800:]}\n"
            f"stderr: {r.stderr[-1500:]}")
        return r

    def test_mutation_narrow_pattern_widened_to_match_everything(self):
        """If NARROW stops being narrow, the disagreement vanishes."""
        m = self._mutate(
            r'NARROW = re.compile(r"^\*\*(\d+(?:\.\d+)?[a-z]?)(?:\.\*\*|\*\*|\.|)\s")',
            r'NARROW = re.compile(r"^\*\*((?:[A-Z]{1,2})?\d+(?:\.\d+)?[a-z]?)(?:\.\*\*|\*\*|\.|)\s")')
        try:
            out = self._run(m).stdout
            assert "narrow=37" not in out.split("AT HEAD:")[-1], (
                "widening NARROW did not change the reported count — the "
                "counter is not reading the pattern")
        finally:
            m.unlink(missing_ok=True)

    def test_mutation_scan_truncated_to_three_revisions(self):
        """A sampled scan cannot support 'no revision reads 29'."""
        m = self._mutate("    return rows", "    return rows[:3]")
        try:
            out = self._run(m).stdout
            assert "27 of them" not in out and "revisions — 27" not in out
            mod = _load()
            assert len(mod.revisions()) > 3, "the live script is itself truncated"
        finally:
            m.unlink(missing_ok=True)

    def test_mutation_prose_status_pattern_broken(self):
        """Breaking the status pattern must move the numerator off 15."""
        m = self._mutate(
            r'PROSE_STATUS = re.compile(r"\bStatus\s+(?:is\s+)?(" + "|".join(STATUSES) + r")\b")',
            r'PROSE_STATUS = re.compile(r"\bStatus\s+(?:is\s+)?(COMMITTED)\b")')
        try:
            out = self._run(m).stdout
            assert "15 of 48 = 31.2500%" not in out, (
                "restricting the status vocabulary left the numerator at 15 — "
                "the count is not reading the pattern")
        finally:
            m.unlink(missing_ok=True)

    def test_mutation_engine_replaced_by_the_raw_regex(self):
        """The denominator must come from the engine, not from a raw match.

        RETARGETED 2026-09-10 after the first version SURVIVED. It mutated the
        `counters()` dictionary entry, which the headline figure does not read --
        the "15 of 48" line calls `_engine_count` directly. A mutation on a line
        the assertion does not depend on is not a test of that assertion, which
        is I30 in this project's own numbering. The mutation now lands inside
        `_engine_count`, which the figure does execute.
        """
        m = self._mutate(
            "        return len(parse_entries(tmp))",
            "        return sum(1 for ln in text.splitlines() if ENTRY.match(ln))")
        try:
            out = self._run(m).stdout
            assert "15 of 48 = 31.2500%" not in out, (
                "swapping the engine for the raw regex left 48 unchanged — "
                "`_is_entry` is then doing nothing and the denominator is untested")
        finally:
            m.unlink(missing_ok=True)
