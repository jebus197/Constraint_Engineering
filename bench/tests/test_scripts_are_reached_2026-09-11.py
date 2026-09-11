"""A committed script that nothing reaches is the additive standard's own failure.

THE STANDARD, verbatim: *"Symmetrically, an addition that nothing reaches is not
additive either: every new flag, gate, subcommand or entry point must be wired to
a caller and executed by a test."* `test_additive_standard_2026-09-07.py`
ratchets config fields nothing READS. Scripts had no equivalent, and the
project's record holds 11 confirmed defects that were additions doing nothing.

MEASURED 2026-09-11: **112 of 120 scripts are reached -- 93.3333%, Wilson
[87.3949%, 96.5835%], Clopper-Pearson [87.2863%, 97.0781%]**, both intervals
cross-checked by 2 tools (statsmodels against a 50-digit mpmath Wilson closed
form; statsmodels `beta` against `scipy.stats.beta` for Clopper-Pearson).

REACHED MEANS 3 THINGS, and a script can be legitimate with no caller at all:
something CALLS it; a note CITES it as a figure's producer, which
`measured-rate-travels-with-its-script` requires; or a canonical document names
it as a command to run.

THE ARCHIVAL EXCLUSION IS WHAT MAKES THE NUMBER HONEST. A first pass counted
mentions inside `experimental_notes/evidence/*/seat_proposals.diff` -- archival
copies of what reviewing models proposed, committed that same morning -- and
reported 5 unreached instead of 8. **The flattering figure came from the review
record being filed, not from anything calling those scripts.** A measurement that
improves when you file your paperwork is measuring the filing.

THIS DECIDES NOTHING ABOUT THE 8. Wire or retire is a disposition, and the
additive standard's removal clause needs a committed measurement that something
better replaces them -- which is precisely what is absent. They are recorded for
the founder, as `update_drift` was under I31. What this holds is that the set may
not GROW.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "scripts_are_reached_2026-09-11.py"


@pytest.fixture(scope="module")
def mod():
    if subprocess.run(["git", "rev-parse", "--git-dir"], cwd=REPO,
                      capture_output=True).returncode != 0:
        pytest.skip("reachability cannot be decided outside a git checkout, and "
                    "reporting everything unreached would be a fabricated figure")
    spec = importlib.util.spec_from_file_location("scripts_reached", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TestTheRatchet:
    def test_the_unreached_set_has_not_grown(self, mod):
        now = set(mod.unreached())
        new = sorted(now - set(mod.UNREACHED))
        assert not new, (
            f"{len(new)} script(s) are reached by nothing -- no caller, no note "
            f"citing them as a figure's producer, no document naming them as a "
            f"command: {new}\n"
            f"Wire one to a caller, cite it where its figure is quoted, or add "
            f"it to UNREACHED deliberately with the reason.")

    def test_the_recorded_set_is_still_accurate(self, mod):
        """A name that has since become reached must be REMOVED from the
        ratchet, or the bound quietly loosens by the width of the stale entry."""
        now = set(mod.unreached())
        stale = sorted(set(mod.UNREACHED) - now)
        assert not stale, (
            f"{stale} are listed as unreached and are now reached; lower the "
            f"ratchet rather than leaving slack in it")


class TestTheMeasurementIsHonest:
    def test_an_archival_mention_does_not_count_as_reaching(self, mod):
        """THE DEFECT THAT MADE THE FIRST FIGURE FLATTERING.

        All 8 unreached scripts are mentioned inside
        `experimental_notes/evidence/*/seat_proposals.diff`. If archival copies
        counted, every one would read as reached -- and the improvement would
        have come from committing the review record that morning.
        """
        assert mod.ARCHIVAL, "the archival exclusion has been removed"
        hits = []
        for s in mod.UNREACHED:
            stem = Path(s).name
            r = subprocess.run(
                ["git", "grep", "-l", stem, "--",
                 "experimental_notes/evidence/"],
                cwd=REPO, capture_output=True, text=True)
            if r.stdout.strip():
                hits.append(stem)
        assert hits, (
            "no unreached script is mentioned in the archival tree, so this "
            "test is no longer exercising the exclusion it exists to protect")

    def test_a_script_with_a_caller_is_not_flagged(self, mod):
        """POSITIVE CONTROL. Something obviously called must never appear."""
        now = mod.unreached()
        for certainly_reached in ("scripts/note_vagueness_lint.py",
                                  "scripts/task_list_markers.py"):
            assert certainly_reached not in now, certainly_reached

    def test_the_population_is_not_empty(self, mod):
        n = len([f for f in mod._tracked()
                 if f.startswith("scripts/") and f.endswith(".py")])
        assert n >= 100, f"only {n} scripts found; the ratchet guards nothing"


class TestItRuns:
    def test_check_mode_exits_zero_today(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "--check"], cwd=REPO,
                           capture_output=True, text=True, timeout=900)
        assert r.returncode == 0, r.stdout[-1200:]
        assert "reached by NOTHING" in r.stdout

    def test_an_unknown_flag_is_refused(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "--nope"], cwd=REPO,
                           capture_output=True, text=True, timeout=300)
        assert r.returncode != 0
        assert "unrecognized arguments" in r.stderr


class TestTheExclusionListCannotHide:
    """`SELF_REFERENTIAL` is the one place an inconvenient orphan could be made
    to vanish, so it is held to files that demonstrably carry a roll-call and to
    a filter that drops lines rather than files."""

    def test_every_self_referential_file_carries_a_roll_call(self, mod):
        for rel in mod.SELF_REFERENTIAL:
            body = (mod.REPO / rel).read_text(encoding="utf-8", errors="replace")
            hits = [ln for ln in body.splitlines()
                    if mod._ROLL_CALL.fullmatch(ln.strip())]
            assert hits, (
                f"{rel} is excluded as self-referential but carries 0 roll-call "
                f"lines, so nothing in it was ever going to be ignored -- "
                f"listing it only removes whatever REAL references it holds. "
                f"That is how this script came to report itself unreached.")

    def test_the_diagnostic_file_cannot_vouch_for_anything(self, mod):
        """A file whose job is to NAME orphans is never evidence about them.

        Line-wise was not enough for this one. The module docstring explains why
        `priority_starvation_simulation.py` cannot be wired, and writing that
        sentence made the script read as REACHED -- a prose mention is not a
        roll-call line. So the diagnostic module is excluded WHOLLY, which is
        safe here and nowhere else: it calls none of the scripts it measures, so
        it holds no real reference to lose.
        """
        assert mod.DIAGNOSTIC, "the diagnostic exclusion has been removed"
        for rel in mod.DIAGNOSTIC:
            body = (mod.REPO / rel).read_text(encoding="utf-8", errors="replace")
            named = [u for u in mod.UNREACHED if u in body]
            assert named, (
                f"{rel} names 0 unreached scripts, so excluding it wholly "
                f"protects nothing and only risks hiding a real caller")
        assert set(mod.UNREACHED) <= set(mod.unreached()), (
            "a script this file merely writes ABOUT is being counted as reached")

    def test_an_instrument_may_still_vouch_for_an_instrument(self, mod):
        """The failure the FIRST fix caused, pinned alongside the one it cured.

        The rule is asymmetric on purpose. An instrument file cannot vouch for a
        script it merely writes about, because prose is not a caller. It CAN
        vouch for another instrument file, because this test genuinely runs the
        module -- and deleting that reference is exactly what made the module
        report itself unreached on the first attempt.
        """
        me = "bench/tests/test_scripts_are_reached_2026-09-11.py"
        assert me in mod.INSTRUMENT, "the test is no longer treated as instrument"
        assert "scripts/scripts_are_reached_2026-09-11.py" in mod.INSTRUMENT
        assert "scripts/scripts_are_reached_2026-09-11.py" not in set(mod.unreached()), (
            "the module reports ITSELF unreached: the instrument rule has "
            "stopped letting this test vouch for the script it runs")

    def test_the_vouching_rule_is_asymmetric(self, mod):
        """CALL THE PREDICATE. Mutating the rule to its symmetric form left all
        13 tests green, because `CDSFL_OUTCOMES_LOG.md` happens to name this
        module -- so the test meant to prove the asymmetry was passing for an
        unrelated reason. Asserting on the live corpus could not see it; calling
        `vouches` with the 4 cases can."""
        instrument_script = "scripts/scripts_are_reached_2026-09-11.py"
        instrument_test = "bench/tests/test_scripts_are_reached_2026-09-11.py"
        orphan = mod.UNREACHED[0]
        assert not mod.vouches(instrument_script, orphan), (
            "an instrument file vouches for a script it merely writes about")
        assert mod.vouches(instrument_test, instrument_script), (
            "the test can no longer vouch for the module it runs; that is what "
            "made the module report itself unreached the first time")
        assert mod.vouches("experimental_notes/Ordinary_Note.md", orphan), (
            "an ordinary document can no longer cite a producer at all")
        assert not mod.vouches(orphan, orphan), "a file vouches for itself"

    def test_prose_in_this_very_file_does_not_reach(self, mod):
        """ANTI-VACUITY, and self-referential on purpose: the docstring above
        NAMES an unreached script, which is how the defect happened the 4th
        time. If naming it here were enough to reach it, this assertion fails.

        scripts/priority_starvation_simulation.py
        """
        assert "scripts/priority_starvation_simulation.py" in set(mod.unreached()), (
            "writing a script's name into a test docstring made it read as "
            "reached; prose is being counted as a caller again")

    def test_a_non_roll_call_mention_still_counts_as_reaching(self, mod):
        """The test file names this script on a line that is not a bare path.
        If that stopped counting, the instrument would orphan itself."""
        assert "scripts/scripts_are_reached_2026-09-11.py" not in set(mod.unreached())

    def test_the_filter_drops_lines_not_files(self, mod):
        """Positive control: a roll-call line is ignored, a line with any other
        content on it is not -- proven by feeding both forms to the matcher."""
        assert mod._ROLL_CALL.fullmatch('"scripts/foo.py",')
        assert mod._ROLL_CALL.fullmatch("scripts/foo.py")
        assert not mod._ROLL_CALL.fullmatch('SCRIPT = REPO / "scripts/foo.py"')
        assert not mod._ROLL_CALL.fullmatch("python3 scripts/foo.py --check")
