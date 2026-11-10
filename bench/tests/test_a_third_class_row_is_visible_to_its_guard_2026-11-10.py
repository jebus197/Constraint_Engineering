"""A COMPLETENESS CHECK OVER CAPTURED KEYS CANNOT SEE A KEY IT CANNOT CAPTURE.

Both findings here came from the severity joint round of 2026-11-10, from
2 different free panel seats, and both were verified by execution before
being acted on.

FINDING 1. `scripts/no_severity_bound_above_one_half_is_a_magnitude_test_2026-11-06.py`
read the appendix's consequence-weight table with a FIXED ALTERNATION,
`W\\((HARD|SOFT)\\)`, and then checked completeness with
`sorted(W) != ["HARD", "SOFT"]`. A check over the keys the pattern captured
can never fire on a key the pattern cannot capture. So a `W(MEDIUM)` row added
to the appendix was not MISSING from the producer's view -- it was INVISIBLE,
and the producer reported its shape theorem PASS and exited 0 while z3 returns
`sat` for a counterexample over that very table.

WHY IT IS ABOVE THRESHOLD. That theorem is the only instrument the project has
for detecting that the appendix's caution 3 has gone stale, and the theorem is
load-bearing on the founder's own question about whether severity should bound
convergence. Adding a third consequence level is the one change caution 3
itself invites, by pointing at the 5 material-defect categories as the
vocabulary for a real consequence scale. An instrument that reads green in the
single condition it was built to detect reports a soundness it did not measure.

FINDING 2, CONFIRMED IN SUBSTANCE AND CORRECTED IN ITS HARM. A byte-copy of a
severity producer sat at the REPOSITORY ROOT beside the real one in `scripts/`.
The seat that found it reported that the copy "exits 0 having measured
nothing". IT DOES NOT: it exits 1 and prints that no archive was found, so it
is loud rather than silent, and that half of the seat's finding is refuted.
The duplicate was still an orphan, and the removal clause was satisfied on 3
NAMED properties measured by the producer below: the `scripts/` copy resolves
its archive path and measures, exits 0, and is named in 9 places in the
record, against 0 for the root path. Both copies were committed in the SAME
commit, and the `scripts/` copy carries a later correction the root copy does
not, so the root copy was an accidental deposit of a superseded version. Its
bytes survive in git history and in the panel sandbox archive.

Producer: `scripts/a_third_class_row_was_invisible_to_its_own_guard_2026-11-10.py`.
"""
import pathlib
import re
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
READER = REPO / "scripts" / \
    "no_severity_bound_above_one_half_is_a_magnitude_test_2026-11-06.py"
PRODUCER = REPO / "scripts" / \
    "a_third_class_row_was_invisible_to_its_own_guard_2026-11-10.py"

#: A table with a level strictly between the 2 the appendix declares. This is
#: the one edit caution 3 invites, so it is the one the guard must survive.
THREE_LEVEL = """| W(HARD) | 1 | Hard consequence |
| W(MEDIUM) | 0.75 | Intermediate consequence |
| W(SOFT) | 0.5 | Soft consequence |"""


def _reader():
    """Import the real module. ★ READ THE LIVE COMPILED OBJECT, NOT THE SOURCE
    TEXT. The first version of this file extracted the pattern with a regex
    over the source and re-decoded it with `unicode_escape`, which raised a
    DeprecationWarning and, worse, asserted on a RENDERING of the pattern
    rather than on the pattern the module actually uses -- the
    `execute-do-not-grep` failure, inside a guard written to catch an
    unreachable check."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("_sev_reader_live", READER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_sev_reader_live"] = mod
    spec.loader.exec_module(mod)
    return mod


def _pattern(name: str) -> str:
    mod = _reader()
    rx = getattr(mod, name, None)
    assert rx is not None, f"{name} is gone from the reader; this guard is blind"
    return rx.pattern


class TestTheCompletenessCheckIsReachable:
    @pytest.mark.parametrize("name", ["W_ROW", "V_ROW"])
    def test_the_row_pattern_is_not_a_fixed_alternation(self, name):
        pat = _pattern(name)
        assert "(HARD|SOFT)" not in pat and "(True|None|False)" not in pat, (
            f"{name} captures a FIXED SET, so the completeness check that "
            f"reads its captures can never fire on a new row. That is how a "
            f"third consequence level became invisible to the one instrument "
            f"built to detect it.")

    def test_a_third_level_is_captured(self):
        live = getattr(_reader(), "W_ROW")
        seen = sorted({m.group(1) for m in live.finditer(THREE_LEVEL)})
        assert seen == ["HARD", "MEDIUM", "SOFT"], (
            f"the pattern captured {seen} from a 3-row table, so the "
            f"completeness check below it stays unreachable")

    def test_the_completeness_check_still_exists(self):
        """ANTI-VACUITY. Widening the pattern is worthless if the check it
        feeds was deleted; then nothing refuses the new table at all."""
        src = READER.read_text(encoding="utf-8")
        assert 'sorted(W) != ["HARD", "SOFT"]' in src, (
            "the W completeness check is gone, so a widened pattern reports "
            "a third level to nobody")

    def test_the_real_reader_refuses_a_three_level_table(self, tmp_path):
        """EXECUTING, not a text check, and the appendix is never touched:
        the real module is imported and its APPENDIX constant repointed at a
        temp copy carrying the extra row."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("_sev_reader", READER)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["_sev_reader"] = mod
        spec.loader.exec_module(mod)
        real = (REPO / "docs" / "MATHEMATICAL_APPENDIX.md").read_text(encoding="utf-8")
        hacked = real.replace("| W(SOFT) |",
                              "| W(MEDIUM) | 0.75 | Intermediate |\n| W(SOFT) |", 1)
        assert hacked != real, "could not place the extra row; the table moved"
        p = tmp_path / "APPENDIX.md"
        p.write_text(hacked, encoding="utf-8")
        mod.APPENDIX = p
        with pytest.raises(SystemExit) as ei:
            mod.read_spec()
        assert "MEDIUM" in str(ei.value) or "W rows parsed" in str(ei.value), (
            f"the reader accepted a 3-level table instead of refusing: {ei.value}")


class TestNoStrayProducerCopiesAtTheRoot:
    def test_the_named_stray_is_gone(self):
        stray = REPO / \
            "the_computed_severity_is_three_valued_on_the_archive_2026-11-06.py"
        assert not stray.exists(), (
            "the stray root copy is back. It cannot resolve its archive path "
            "and exits 1, and 0 places in the record name it.")

    def test_no_root_level_python_duplicates_a_scripts_producer(self):
        """THE PROPERTY, NOT THE INSTANCE, so the next accidental deposit is
        caught rather than this one being pinned by name."""
        dupes = [f.name for f in REPO.glob("*.py")
                 if (REPO / "scripts" / f.name).is_file()]
        assert dupes == [], (
            f"{len(dupes)} file(s) at the repository root duplicate a "
            f"scripts/ producer: {dupes}. A producer run from the root "
            f"resolves the archive path outside the repository.")


class TestTheProducerAnswersForItself:
    def test_the_producer_exits_zero_now_that_both_are_fixed(self):
        r = subprocess.run([sys.executable, str(PRODUCER)],
                           capture_output=True, text=True, cwd=str(REPO))
        assert r.returncode == 0, (
            f"the producer still reports a live defect:\n{r.stdout[-1800:]}")
        assert "both discharged" in r.stdout, r.stdout[-800:]

    def test_the_producer_answers_help_for_free(self):
        r = subprocess.run([sys.executable, str(PRODUCER), "--help"],
                           capture_output=True, text=True, cwd=str(REPO))
        assert r.returncode == 0
        assert "usage" in r.stdout.lower()
        assert "A STRAY BYTE-COPY" not in r.stdout, "--help ran the measurement"
