#!/usr/bin/env python3
"""Stranded seat evidence may only ever decrease.

THE FAULT, MEASURED RATHER THAN DESCRIBED. A panel harvest lands under
`bench/logs/<run>/.../files/<rel>` and `.gitignore:48` ignores `bench/logs/**`,
so every seat-written file is invisible to git by construction. Measured by
`scripts/seat_evidence_is_gitignored_2026-09-30.py`, which decides each case by
CALLING `git check-ignore` and `git ls-files`: 251 seat `.py` files across 22
panel rounds, 251 of 251 = 100% ignored, and 46 of 251 = 18.3267% UNPRESERVED
(Wilson [14.0302%, 23.5781%]) -- existing nowhere a clone could reach -- spread
over 11 rounds.

12 scripts and 2 design notes were rescued BY HAND on 2026-09-30. The founder,
shown that the fault recurs: "clearly that also needs to be repaired."

TWO THINGS WERE DONE, AND THIS FILE HOLDS THE SECOND.

  1. REPAIR AT SOURCE. `bench/panel_sandbox.py:preserve_seat_evidence`, called
     from `harvest()`, copies every seat-written file with no tracked
     counterpart into `experimental_notes/seat_evidence/<round>/<seat>/`, with
     provenance in the file and the seat's own sha256 recorded before the
     header is prepended. Held by
     `bench/tests/test_seat_evidence_reaches_a_clone_2026-10-01.py`.

  2. THE RATCHET, here. A repair that works only until someone adds a fourth
     harvest shape is not a repair. This asserts that no round's stranded count
     GROWS, and -- the load-bearing half -- that any round NOT in the baseline
     has ZERO stranded files, because a round archived after the repair should
     have preserved its own evidence as it ran.

WHY A BASELINE RATHER THAN A FLAT ZERO. The 46 already-stranded files predate
the repair and cannot be preserved by it: their sandboxes are gone and in
several cases the harvest copy is all that survives. Asserting 0 today would
make the suite red for history rather than for a defect, and "a guard that
fires on the ordinary case is on its way to being ignored" is this project's own
warning. The baseline is a BACKLOG that may only shrink, which is the same
convention `bench/directives/universal/section_p_shortfalls.json` uses.

Run:  python3 -m pytest bench/tests/test_seat_evidence_stranding_does_not_grow_2026-10-01.py -q
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
for _p in (str(REPO), str(REPO / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

MEASURE = REPO / "scripts" / "seat_evidence_is_gitignored_2026-09-30.py"
BASELINE = (REPO / "bench" / "directives" / "universal"
            / "seat_evidence_stranding_baseline.json")


@pytest.fixture(scope="module")
def measurer():
    if not MEASURE.is_file():
        pytest.fail(f"{MEASURE.name} is missing: the measurement this guard "
                    f"calls no longer exists")
    spec = importlib.util.spec_from_file_location("seat_evidence_measure",
                                                  MEASURE)
    m = importlib.util.module_from_spec(spec)
    sys.modules["seat_evidence_measure"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def baseline():
    if not BASELINE.is_file():
        pytest.fail(f"{BASELINE.name} is missing: without it this guard has "
                    f"nothing to ratchet against and would pass vacuously")
    return json.loads(BASELINE.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def rows(measurer):
    # GIT-ABSENCE IS NOT A DEFECT OF THE REPAIR. `survey()` now REFUSES
    # where git cannot answer (panel sandbox, tarball) rather than
    # reporting every file unpreserved and none ignored, which made the
    # premise test assert 0 == len(rows). Skip, do not fail, where the
    # measurement is undefined -- the same honesty the grep-wrapper figure
    # gets by exclusion. Added 2026-10-01 by the day-review panel.
    gu = getattr(measurer, "GitUnavailable", None)
    try:
        return measurer.survey()
    except Exception as exc:  # noqa: BLE001
        if gu is not None and isinstance(exc, gu):
            pytest.skip(f"git unavailable in this environment: {exc}")
        raise


@pytest.fixture(scope="module")
def current(measurer, rows):
    return measurer.unpreserved_by_round(rows)


class TestTheMeasurementIsNotVacuous:
    def test_the_survey_finds_seat_files_at_all(self, rows):
        """A glob that matched nothing would make every assertion below pass."""
        if not (REPO / "bench" / "logs").is_dir():
            pytest.skip("no archive in this clone")
        assert len(rows) >= 50, (
            f"the survey found only {len(rows)} seat files; either the archive "
            f"is absent or the harvest layout changed and the glob no longer "
            f"matches it -- in which case this guard is blind, not green")

    def test_the_harvest_is_still_ignored_by_git(self, rows):
        """The PREMISE. If this ever stops being true the repair is moot and
        the baseline should be deleted rather than maintained."""
        if not rows:
            pytest.skip("no archive in this clone")
        ignored = sum(1 for r in rows if r["ignored"])
        assert ignored == len(rows), (
            f"{len(rows) - ignored} harvest files are NO LONGER ignored by git. "
            f"That is a change in the premise: re-read "
            f"`.gitignore` and this file's docstring before touching anything.")


class TestNothingNewIsStranded:
    def test_no_round_outside_the_baseline_has_stranded_evidence(self, current,
                                                                 baseline):
        """THE LOAD-BEARING ASSERTION. A round archived after the repair must
        preserve its own evidence as it runs."""
        known = baseline["unpreserved_by_round"]
        fresh = {r: n for r, n in current.items() if r not in known and n}
        assert fresh == {}, (
            "a panel round has stranded seat evidence and is not in the "
            f"baseline: {fresh}\n"
            "That means `preserve_seat_evidence` did not run, or ran and did "
            "not cover these files. Do NOT add the round to the baseline -- "
            "the baseline is history, and this is a live regression. Check "
            "harvest()'s report field `seat_evidence_preserved`.")

    def test_no_round_has_more_stranded_files_than_its_baseline(self, current,
                                                               baseline):
        known = baseline["unpreserved_by_round"]
        grew = {r: (known[r], current[r]) for r in known
                if current.get(r, 0) > known[r]}
        assert grew == {}, (
            f"stranded counts grew, baseline -> now: {grew}. Counts may only "
            f"fall.")

    def test_the_total_has_not_grown(self, current, baseline):
        before = baseline["totals_at_baseline"]["unpreserved"]
        now = sum(current.values())
        assert now <= before, (
            f"{now} seat files are stranded against a baseline of {before}")


class TestTheBaselineIsABacklogAndNotAnExemption:
    def test_it_names_how_it_was_measured(self, baseline):
        assert "measured_by" in baseline and baseline["measured_by"], (
            "a baseline with no named producer is a claim about evidence "
            "rather than evidence (`measured-rate-travels-with-its-script`)")
        named = baseline["measured_by"].split()[0]
        assert (REPO / named).is_file(), named

    def test_it_explains_itself_to_a_reader_who_finds_it_red(self, baseline):
        what = "\n".join(baseline.get("_what_this_is", []))
        assert len(what) > 400, "the baseline does not explain what it is"
        assert "may only fall" in what or "only shrink" in what

    def test_a_round_whose_evidence_is_rescued_can_be_lowered(self, current,
                                                              baseline):
        """The ratchet must not FORBID progress: a count that has fallen is
        fine, and this records which rounds have improved so the backlog can
        be worked down deliberately."""
        known = baseline["unpreserved_by_round"]
        improved = {r: (known[r], current.get(r, 0)) for r in known
                    if current.get(r, 0) < known[r]}
        # Not an assertion about progress -- an assertion that progress is
        # ALLOWED, plus a report of it so the backlog is visible.
        if improved:
            print("\n  rounds whose stranded evidence has been rescued "
                  "(baseline -> now):")
            for r, (was, now) in sorted(improved.items()):
                print(f"    {r:52s} {was} -> {now}")
            print("  Lower these in the baseline, and delete entries at 0.")
        assert all(now <= was for was, now in improved.values())
