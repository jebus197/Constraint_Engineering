"""Task A3: a citation that names a symbol must point inside it.

THE DEFECT. A hand-written `path:LINE` citation breaks whenever anything is
inserted above it, and the existing guard checks only that the FILE exists --
`cdsfl_utils.SUPPRESS_LINE` says so in as many words: "the FILE exists; line
numbers NOT checked". The run ledger self-heals because it has a generator; hand
citations do not.

MEASURED 2026-09-10, after the runner grew by roughly 90 lines that evening: of
the 46 citations into `bench/reference_runner_v3.py`, 6 name a symbol whose span
is known, and ALL 6 pointed outside it. 100%, Wilson [60.9666%, 100.0000%],
Clopper-Pearson [54.0742%, 100.0000%]. The offsets were +17, +19, +59, +424,
+1091 and +6837 lines. The last would send a reader to a completely unrelated
part of a 15,008-line file.

All 6 are repaired. This guard stops them drifting again.

WHY BY AST RATHER THAN BY TEXT. A text search for the symbol near the cited line
is defeated by the name appearing in a comment 400 lines away, and by the fact
that a citation legitimately points INSIDE a long function rather than at its
`def`. An AST span decides containment exactly. A first version of this check
looked for the symbol within 5 lines and reported 12 of 12 failures, several of
which were correct citations deep inside a function body -- the strict version
would have sent me repairing things that were right.

WHAT IT CANNOT CHECK, COUNTED SEPARATELY. 40 of the 46 citations carry no
backticked symbol before them, or name something that is not a def or a class.
Those are UNCHECKABLE, not passing. Folding them into the pass count would be the
"a guard that cannot fail" defect; folding them into the fail count would invent
findings.
"""
from __future__ import annotations

import importlib.util
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "citation_content_guard_2026-09-10.py"


@pytest.fixture(scope="module")
def guard():
    spec = importlib.util.spec_from_file_location("citation_guard", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TestNoCitationPointsOutsideTheSymbolItNames:
    def test_every_anchored_citation_is_inside_its_symbol(self, guard):
        for target in guard.CITED:
            good, bad, _unchecked, _past, _n = guard.check(target)
            assert not bad, "\n".join(
                f"{p.relative_to(ROOT)}:{line} names `{a}`, which spans {lo}-{hi} "
                f"(off by {lo - line:+d})" for p, line, a, lo, hi in bad)
            assert good, (
                f"no citation into {target} could be checked at all; the guard "
                f"would pass vacuously")

    def test_no_citation_points_past_the_end_of_the_file(self, guard):
        for target in guard.CITED:
            _good, _bad, _unchecked, past, n = guard.check(target)
            assert not past, [f"{p.name}:{l} > {n}" for p, l in past]


class TestTheGuardCanActuallyFail:
    """Without this the pass above is worth nothing."""

    def test_a_deliberately_wrong_citation_is_caught(self, guard, tmp_path,
                                                     monkeypatch):
        target = guard.CITED[0]
        sp = guard.spans(target)
        name, (lo, _hi) = next(iter(
            (k, v) for k, v in sp.items() if v[0] > 50))
        bad_note = tmp_path / "fake_note.md"
        bad_note.write_text(
            f"The function `{name}` is at {target}:1 and that is wrong.",
            encoding="utf-8")
        monkeypatch.setattr(guard, "citing_files", lambda: iter([bad_note]))
        _good, bad, _u, _p, _n = guard.check(target)
        assert len(bad) == 1, bad
        assert bad[0][2] == name and bad[0][1] == 1

    def test_a_correct_citation_is_not_flagged(self, guard, tmp_path, monkeypatch):
        target = guard.CITED[0]
        sp = guard.spans(target)
        name, (lo, hi) = next(iter(
            (k, v) for k, v in sp.items() if v[1] > v[0] + 3))
        note = tmp_path / "ok_note.md"
        note.write_text(f"`{name}` at {target}:{lo + 1}", encoding="utf-8")
        monkeypatch.setattr(guard, "citing_files", lambda: iter([note]))
        good, bad, _u, _p, _n = guard.check(target)
        assert not bad and len(good) == 1


class TestTheUncheckableAreCountedNotHidden:
    def test_most_citations_carry_no_symbol_and_that_is_reported(self, guard):
        for target in guard.CITED:
            good, bad, unchecked, _p, _n = guard.check(target)
            assert unchecked > 0, (
                "every citation is now anchored, which would be an improvement "
                "worth noticing rather than a state to assume")
            assert unchecked > len(good) + len(bad), (
                "the checkable set has overtaken the unchecked one; the guard's "
                "stated coverage limit no longer holds")
