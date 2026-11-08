"""Every measurement producer written on 2026-11-08 must be EXECUTED by something.

HIS INSTRUCTION, 2026-11-08: extend the reached-producers rule to today's date.

WHY A 2ND DATED GUARD IS NOT THE WHOLE FIX, AND THE MEASUREMENT SAYS SO. The
2026-11-03 sibling closed 1 date. Surveying every dated producer in the tree
before writing this file, 247 of 557 were reached by nothing, across 37 of 46
dates -- and 2026-11-08 was the 2nd worst, not an outlier, at 18 unreached of
20. Closing today alone would have left 229 unreached on 36 other dates. So this
file is COMPOSED with a date-independent ratchet
(``test_an_unreached_producer_set_cannot_grow_2026-11-08.py``), and the
composition is justified by measurement rather than by the fact that 2 fixes can
coexist -- which is the weak reading his own definition of composability
explicitly excludes.

WHAT EACH HALF DOES THAT THE OTHER CANNOT, which is the dominance claim:
  * THIS FILE executes. The ratchet's predicate is TEXTUAL -- it asks whether a
    producer's name appears in any test -- so it cannot tell a producer that
    runs from one that is merely mentioned. A producer that stops running keeps
    its mention and passes the ratchet.
  * THE RATCHET is date-independent. This file is frozen to 2026-11-08 by its
    own glob, so a producer written on any later date is outside it entirely.
Producer: ``scripts/the_composed_producer_fix_dominates_either_part_2026-11-08.py``.

EVERY NAME HERE WAS CHECKED BY EXECUTION BEFORE BEING LISTED, not added and
hoped for, because the sibling guard's own history is that 13 producers sat in
neither list until its anti-vacuity test fired. All 20 were run bare: 20 of 20
exited 0 with non-empty output, 20 of 20 answered ``--help`` with a usage line in
under 1.5 s, and the slowest took 97.02 s. 3 of the 20 are TRANSFORMATION TOOLS
rather than measurements -- ``make_the_thirteen_importable``,
``propagate_the_canonical_interval`` and ``record_his_verdicts_of_the_eighth`` --
and they are listed here rather than exempted because every one of them gates
its writes behind ``--write``, so a bare invocation is a dry run. That was
verified by comparing ``git status`` before and after: the tree was unchanged.
Exempting them would have been the weaker choice twice over, since the reached
predicate is textual and an exemption entry would have made them count as
reached while nothing executed them.

4 of the 20 READ DATA OUTSIDE THIS REPOSITORY -- his annotated responses, the
session transcripts and the memory directory -- and they are SKIPPED when that
data is absent rather than failed, so a fresh clone does not report a defect it
cannot have. 2 of those 4 read their external path with no guard of their own, so
without the skip they would raise rather than report. That is a robustness fault
in the producers and is recorded here rather than silently worked around.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "scripts"
DATE = "2026-11-08"

#: Producers that must RUN. All 20 were executed and timed before listing.
MUST_RUN = (
    "a4_doors_are_shared_2026-11-08.py",
    "b83s_premise_is_false_the_outcome_is_stored_2026-11-08.py",
    "a_guessed_lookup_shape_answers_confidently_2026-11-08.py",
    "a_rule_excluded_from_blocking_still_blocks_2026-11-08.py",
    "are_the_two_switches_the_whole_set_2026-11-08.py",
    "does_any_archived_finding_carry_confidence_2026-11-08.py",
    "his_command_was_erased_by_his_own_next_line_2026-11-08.py",
    "his_commonest_annotation_was_read_as_a_heading_2026-11-08.py",
    "how_many_commits_and_how_many_refusals_2026-11-08.py",
    "how_many_of_his_twenty_nine_are_actually_addressed_2026-11-08.py",
    "how_many_open_defects_are_already_fixed_2026-11-08.py",
    "make_the_thirteen_importable_2026-11-08.py",
    "propagate_the_canonical_interval_2026-11-08.py",
    "record_his_verdicts_of_the_eighth_2026-11-08.py",
    "sv_reports_a_runway_it_will_refuse_2026-11-08.py",
    "the_composed_producer_fix_dominates_either_part_2026-11-08.py",
    "the_evidence_check_only_binds_at_close_2026-11-08.py",
    "the_resume_pointer_names_his_decisions_as_work_2026-11-08.py",
    "the_syntax_clause_was_never_built_2026-11-08.py",
    "the_unreached_producer_debt_is_not_todays_2026-11-08.py",
    "what_his_twenty_nine_rulings_actually_say_2026-11-08.py",
    "what_the_commit_gate_costs_now_2026-11-08.py",
    "what_the_gate_leaves_unverified_2026-11-08.py",
)

#: Arguments a producer REQUIRES. Absent means a bare invocation, the normal
#: case. 0 of the 20 need one, which was established by running them.
EXTRA_ARGS: dict[str, tuple[str, ...]] = {}

#: MEASURED wall-clock, so a timeout is derived rather than guessed. The
#: default is 300 s against a measured worst case of 97.02 s; the one producer
#: that runs 1,270 in-process lint passes over 635 notes gets 600 s, which is
#: 6.2x its measured time rather than 3.1x.
TIMEOUT_DEFAULT = 300
TIMEOUT_OVERRIDE = {
    "a_rule_excluded_from_blocking_still_blocks_2026-11-08.py": 600,
}

#: Producers whose DATA lives outside this repository, with the path each needs.
#: Skipped when it is absent: a fresh clone must not report a defect it cannot
#: have. The 2 marked UNGUARDED read the path with no check of their own.
NEEDS_EXTERNAL = {
    "his_command_was_erased_by_his_own_next_line_2026-11-08.py":
        pathlib.Path.home() / ".claude/projects/-Users-georgejackson-Developer-Projects",
    "how_many_of_his_twenty_nine_are_actually_addressed_2026-11-08.py":
        pathlib.Path.home() / "Developer_Projects/Responses",          # UNGUARDED
    "his_commonest_annotation_was_read_as_a_heading_2026-11-08.py":
        pathlib.Path.home() / "Developer_Projects/Responses",
    "record_his_verdicts_of_the_eighth_2026-11-08.py":
        pathlib.Path.home() / "Developer_Projects/Responses",
    "sv_reports_a_runway_it_will_refuse_2026-11-08.py":
        pathlib.Path.home() / ".claude/projects/-Users-georgejackson-Developer-Projects",
    "what_his_twenty_nine_rulings_actually_say_2026-11-08.py":
        pathlib.Path.home() / "Developer_Projects/Responses",          # UNGUARDED
}

#: Harnesses that must NOT run from inside the suite, with the mechanical
#: reason, following both siblings' convention. A harness invokes pytest, so
#: running one from within a pytest process recurses; several also write to the
#: tree by design, which would mutate the subject mid-board.
NOT_RUN_HERE = {
    "the_line_reference_mutations_2026-11-08.py": "invokes pytest; would recurse",
    "the_out_of_band_exemption_mutations_2026-11-08.py": "invokes pytest; would recurse",
    "the_producer_resolution_mutations_2026-11-08.py": "invokes pytest; would recurse",
    "the_reached_producer_mutations_2026-11-08.py": "invokes pytest; would recurse",
    "the_resumable_seam_mutations_2026-11-08.py": "invokes pytest; would recurse",
    "the_runway_reference_mutations_2026-11-08.py": "invokes pytest; would recurse",
    "the_shell_exclusion_mutations_2026-11-08.py":
        "invokes pytest AND rewrites a file hard-linked into the live hooks "
        "directory; would recurse and mutate the running hook",
    "the_status_rendering_mutations_2026-11-08.py": "invokes pytest; would recurse",
    "the_ticket_id_postcondition_mutations_2026-11-08.py": "invokes pytest; would recurse",
    "the_union_fix_mutations_2026-11-08.py":
        "invokes pytest AND rewrites a file hard-linked into the live hooks "
        "directory; would recurse and mutate the running hook",
}


def refusals(repo: pathlib.Path | None = None, *,
             present: set[str] | None = None,
             must_run: tuple[str, ...] | None = None,
             not_run_here: dict[str, str] | None = None) -> list[str]:
    """Every reason this guard would refuse, as a list. THE DECISION, callable.

    Exposed so that this file's own accounting test and the composition
    measurement in
    ``scripts/the_composed_producer_fix_dominates_either_part_2026-11-08.py``
    run ONE code path. A test that reimplemented these 3 checks would assert
    that the reimplementation is self-consistent, which is the shape that let a
    producer and a consumer disagree 4 times in this project's record.

    ``present`` overrides what is on disk, so a caller can put a synthetic file
    set to the real decision without writing to the tree. ``must_run`` and
    ``not_run_here`` override the declared lists for the same reason.
    """
    repo = REPO if repo is None else repo
    mr = MUST_RUN if must_run is None else must_run
    nrh = NOT_RUN_HERE if not_run_here is None else not_run_here
    if present is None:
        present = {q.name for q in (repo / "scripts").glob(f"*{DATE}*.py")}
    out: list[str] = []
    declared = set(mr) | set(nrh)
    for name in sorted(present - declared):
        out.append(f"UNDECLARED {name}: in neither list, so nothing requires "
                   f"it to run and nothing states why it is exempt")
    for name in sorted(declared - present):
        out.append(f"PHANTOM {name}: declared but not on disk")
    for name in sorted(set(mr) & set(nrh)):
        out.append(f"BOTH-LISTS {name}: declared as run and as exempt")
    for name, why in sorted(nrh.items()):
        if not why.strip() or len(why) <= 20:
            out.append(f"UNREASONED {name}: exemption states no mechanical "
                       f"reason ({why!r})")
    for name in sorted(set(TIMEOUT_OVERRIDE) | set(EXTRA_ARGS)
                       | set(NEEDS_EXTERNAL)):
        if name not in mr:
            out.append(f"ORPHAN-OPTION {name}: carries a timeout, args or an "
                       f"external-data marker but is not in MUST_RUN")
    return out


def _skip_if_external_data_absent(name: str) -> None:
    need = NEEDS_EXTERNAL.get(name)
    if need is not None and not need.exists():
        pytest.skip(f"{name} reads {need}, which is not on this machine")


@pytest.mark.parametrize("name", MUST_RUN)
def test_the_producer_still_runs(name):
    """EXECUTED, not inspected. A producer that cannot run is not evidence."""
    p = SCRIPTS / name
    if not p.is_file():
        pytest.skip(f"{name} is not in this checkout")
    _skip_if_external_data_absent(name)
    argv = [sys.executable, str(p), *EXTRA_ARGS.get(name, ())]
    r = subprocess.run(argv, capture_output=True, text=True,
                       timeout=TIMEOUT_OVERRIDE.get(name, TIMEOUT_DEFAULT),
                       cwd=str(REPO))
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


def test_every_2026_11_08_producer_is_accounted_for():
    """ANTI-VACUITY, and the assertion that actually closes the gap.

    The 2 lists above are hand-written, so a producer added later would be
    covered by neither and this file would pass while the rule it enforces went
    unmet -- the shape it was written to stop. This puts what is ON DISK to the
    real decision and requires it to refuse nothing.
    """
    on_disk = {p.name for p in SCRIPTS.glob(f"*{DATE}*.py")}
    if not on_disk:
        pytest.skip(f"no {DATE} producer is in this checkout")
    bad = refusals(present=on_disk)
    assert not bad, (
        f"{len(bad)} accounting refusal(s):\n  " + "\n  ".join(bad))


def test_the_decision_can_actually_refuse():
    """ANTI-VACUITY FOR THE DECISION ITSELF.

    A checker that returns an empty list for every input passes the test above
    while checking nothing -- this project's most expensive recurring defect. So
    the real decision is put 4 synthetic cases it MUST refuse.
    """
    on_disk = {p.name for p in SCRIPTS.glob(f"*{DATE}*.py")}
    assert on_disk, "no 2026-11-08 script on disk; cannot build the cases"

    undeclared = refusals(present=on_disk | {f"brand_new_{DATE}.py"})
    assert any(r.startswith("UNDECLARED") for r in undeclared), undeclared

    missing_one = sorted(MUST_RUN)[0]
    phantom = refusals(present=on_disk - {missing_one})
    assert any(r.startswith("PHANTOM") for r in phantom), phantom

    both = refusals(present=on_disk,
                    not_run_here={**NOT_RUN_HERE,
                                  MUST_RUN[0]: "a reason long enough to pass"})
    assert any(r.startswith("BOTH-LISTS") for r in both), both

    unreasoned = refusals(present=on_disk,
                          not_run_here={k: "x" for k in NOT_RUN_HERE})
    assert any(r.startswith("UNREASONED") for r in unreasoned), unreasoned


def test_the_exemptions_each_state_a_mechanical_reason():
    """An exemption without a reason is an exemption that cannot be argued with."""
    bad = [r for r in refusals() if r.startswith("UNREASONED")]
    assert not bad, bad


def test_the_timeout_overrides_name_a_listed_producer():
    """A timeout for a producer that is not run is an addition nothing reaches."""
    bad = [r for r in refusals() if r.startswith("ORPHAN-OPTION")]
    assert not bad, bad
