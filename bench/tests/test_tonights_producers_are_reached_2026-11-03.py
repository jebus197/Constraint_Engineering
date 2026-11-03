"""Every measurement producer written on 2026-11-03 must be EXECUTED by something.

WHY THIS FILE EXISTS, AND IT IS A FAULT OF MINE FOUND BY ITS OWN SIBLING. The
2026-11-02 guard states the rule: a producer nothing runs is the
addition-nothing-reaches half of the additive standard, which this project has
confirmed 11 times. On 2026-11-03 I wrote 7 producers and then checked, against
that rule rather than against my intentions, how many were named by any test.
**5 of the 7 were named by none** -- including
`b96_the_report_against_the_note_standard_2026-11-03.py`, which I had written
20 minutes earlier for the express purpose of paying off exactly this kind of
debt, in an entry citing `measured-rate-travels-with-its-script`.

So the rule caught its own advocate for the 2nd time in 1 night, which is the
argument for having it written down rather than relying on the author to
remember it.

WHAT IS IN SCOPE AND WHAT IS DELIBERATELY NOT. The 2 mutation harnesses are
EXCLUDED by name with their mechanical reason, exactly as the sibling guard
excludes 4 of its own: a harness invokes pytest, so running it from inside the
suite recurses. That exemption is listed beside the thing it exempts rather than
hidden in a ratchet, so it can be argued with.

THE FIGURES THESE PRODUCERS CARRY are the ones quoted to the founder on
2026-11-03: the 34 of 412 closures resting on a model's own VERIFIED flag, the
16 of 53 false accusations in the note linter, the v_bar weight of 0.350000 for
the orchestrator seat, C0001's unreconciled provenance clause, and the spoken
morning report's 2 of 15. A producer that stops running is a silent loss of
their support, and silence is the failure mode this file exists to break.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "scripts"

#: Producers that must RUN. Each is read-only and exits 0.
MUST_RUN = (
    "a_models_own_verified_flag_closes_it_2026-11-03.py",
    "a_bare_clock_was_dated_from_the_mtime_2026-11-03.py",
    "what_a_self_reported_v_bar_is_worth_2026-11-03.py",
    "c0001_provenance_does_not_reconcile_2026-11-03.py",
    "b96_the_report_against_the_note_standard_2026-11-03.py",
)

#: Harnesses that must NOT be run from inside the suite, with the mechanical
#: reason, following the sibling guard's convention.
NOT_RUN_HERE = {
    "the_models_word_mutations_2026-11-03.py": "invokes pytest; would recurse",
    "the_bare_clock_dating_mutations_2026-11-03.py": "invokes pytest; would recurse",
}


@pytest.mark.parametrize("name", MUST_RUN)
def test_the_producer_still_runs(name):
    """EXECUTED, not inspected. A producer that cannot run is not evidence."""
    p = SCRIPTS / name
    if not p.is_file():
        pytest.skip(f"{name} is not in this checkout")
    r = subprocess.run([sys.executable, str(p)], capture_output=True,
                       text=True, timeout=300, cwd=str(REPO))
    assert r.returncode == 0, (
        f"{name} exited {r.returncode}. The figures it produced were quoted to "
        f"the founder, so this is a silent loss of their support.\n"
        f"stderr tail:\n{r.stderr[-900:]}")
    assert r.stdout.strip(), f"{name} ran and printed nothing"


@pytest.mark.parametrize("name", sorted(MUST_RUN))
def test_the_producer_answers_help_without_doing_the_work(name):
    """A `--help` must never cost money or minutes -- his standing rule."""
    p = SCRIPTS / name
    if not p.is_file():
        pytest.skip(f"{name} is not in this checkout")
    r = subprocess.run([sys.executable, str(p), "--help"], capture_output=True,
                       text=True, timeout=60, cwd=str(REPO))
    assert r.returncode == 0, f"{name} --help exited {r.returncode}"
    assert "usage:" in (r.stdout + r.stderr).lower(), (
        f"{name} --help printed no usage line, so a reader cannot learn what it "
        f"does without running it")


def test_every_2026_11_03_producer_is_accounted_for():
    """ANTI-VACUITY, and the assertion that actually closes the gap.

    The 2 lists above are hand-written, so a producer added later would be
    covered by neither and this file would pass while the rule it enforces went
    unmet -- the shape it was written to stop. This enumerates what is ON DISK
    and requires every one to appear in exactly 1 of the 2 lists.
    """
    on_disk = {p.name for p in SCRIPTS.glob("*2026-11-03*.py")}
    if not on_disk:
        pytest.skip("no 2026-11-03 producer is in this checkout")
    declared = set(MUST_RUN) | set(NOT_RUN_HERE)
    missing = sorted(on_disk - declared)
    phantom = sorted(declared - on_disk)
    assert not missing, (
        f"{len(missing)} producer(s) dated 2026-11-03 are in neither list, so "
        f"nothing runs them and nothing says why not: {missing}")
    assert not phantom, (
        f"{len(phantom)} name(s) are declared but not on disk, so this guard is "
        f"asserting about files that do not exist: {phantom}")
    overlap = sorted(set(MUST_RUN) & set(NOT_RUN_HERE))
    assert not overlap, f"{overlap} appear in both MUST_RUN and NOT_RUN_HERE"


def test_each_exemption_states_a_mechanical_reason():
    """An exemption without a reason is an exemption nobody can argue with."""
    for name, why in NOT_RUN_HERE.items():
        assert len(why) > 12 and not why.lower().startswith("todo"), (
            f"{name} is exempted with the unhelpful reason {why!r}")
        assert "recurse" in why or "s," in why or "scratchpad" in why, (
            f"{name}'s reason {why!r} names no mechanical obstacle")
