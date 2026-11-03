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
#:
#: ★ 11 ADDED 2026-11-03 EVENING, AFTER THIS GUARD'S OWN ANTI-VACUITY TEST
#: CAUGHT 13 PRODUCERS IN NEITHER LIST. 12 of the 13 predate the addition that
#: found them, so the debt was already there; writing one more producer is what
#: made the test fire. Each of the 11 was checked before being listed rather
#: than added and hoped for: a static scan for `write_text`, a `w` mode, a
#: `mkdir`, `shutil`, `os.remove` or a `json.dump` returned 0 writes for all 11,
#: and each was then executed and timed. 2 non-zero exits were found by that
#: check and both were real:
#:   * `score_the_orchestrator_arm` exited 2 because a bare invocation is a
#:     usage error BY DESIGN -- it needs `--run <dir>` or `--survey`. It is
#:     listed here WITH its flag rather than exempted, because exempting it
#:     would leave the v_bar weight of 0.350000 quoted to him with nothing
#:     running the script that produced it.
#:   * `why_the_responses_reader_crossed_its_budget` exited 1 on a REFUSED
#:     branch that had become unreachable-as-a-fault: the 11 MB PNG it splits
#:     the corpus by is now excluded by its bytes, so the empty side IS the
#:     earlier fix landing. It now reports the repaired condition and exits 0.
MUST_RUN = (
    "a_models_own_verified_flag_closes_it_2026-11-03.py",
    "a_bare_clock_was_dated_from_the_mtime_2026-11-03.py",
    "what_a_self_reported_v_bar_is_worth_2026-11-03.py",
    "c0001_provenance_does_not_reconcile_2026-11-03.py",
    "b96_the_report_against_the_note_standard_2026-11-03.py",
    "counting_imports_ranks_producers_backwards_2026-11-03.py",
    "what_a_simulated_run_would_actually_test_2026-11-03.py",
    "a_compaction_summary_can_invent_his_question_2026-11-03.py",
    "a_guard_cannot_refuse_his_own_remedy_2026-11-03.py",
    "a_stale_comment_can_be_load_bearing_2026-11-03.py",
    "a_truncated_ruling_reads_as_complete_2026-11-03.py",
    "has_the_ticket_store_earned_its_place_2026-11-03.py",
    "how_many_of_the_nights_errors_were_instruments_2026-11-03.py",
    "score_the_orchestrator_arm_2026-11-03.py",
    "the_subject_index_cannot_answer_a_novelty_question_2026-11-03.py",
    "which_of_his_questions_are_still_open_2026-11-03.py",
    "why_the_responses_reader_crossed_its_budget_2026-11-03.py",
    "would_asterisks_make_his_comments_machine_readable_2026-11-03.py",
)

#: Arguments a producer REQUIRES, so that needing one is not a reason to leave
#: it unrun. Absent here means a bare invocation, which is the normal case.
EXTRA_ARGS = {
    "score_the_orchestrator_arm_2026-11-03.py": ("--survey",),
}

#: Harnesses that must NOT be run from inside the suite, with the mechanical
#: reason, following the sibling guard's convention.
NOT_RUN_HERE = {
    "the_models_word_mutations_2026-11-03.py": "invokes pytest; would recurse",
    "the_bare_clock_dating_mutations_2026-11-03.py": "invokes pytest; would recurse",
    "the_second_route_mutations_2026-11-03.py": "invokes pytest; would recurse",
    "the_events_channel_mutations_2026-11-03.py": "invokes pytest; would recurse",
    "the_actuator_contract_mutations_2026-11-03.py":
        "invokes pytest AND writes; would recurse and mutate the tree",
    "the_orchestrator_scorer_mutations_2026-11-03.py":
        "invokes pytest AND writes; would recurse and mutate the tree",
}


@pytest.mark.parametrize("name", MUST_RUN)
def test_the_producer_still_runs(name):
    """EXECUTED, not inspected. A producer that cannot run is not evidence."""
    p = SCRIPTS / name
    if not p.is_file():
        pytest.skip(f"{name} is not in this checkout")
    argv = [sys.executable, str(p), *EXTRA_ARGS.get(name, ())]
    r = subprocess.run(argv, capture_output=True,
                       text=True, timeout=300, cwd=str(REPO))
    assert r.returncode == 0, (
        f"{name} exited {r.returncode} (argv {argv[2:]}). The figures it "
        f"produced were quoted to the founder, so this is a silent loss of "
        f"their support.\nstderr tail:\n{r.stderr[-900:]}")
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
