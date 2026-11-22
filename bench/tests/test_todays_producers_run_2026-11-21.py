#!/usr/bin/env python3
"""TODAY'S PRODUCERS ARE EXECUTED, not merely mentioned.

★ WHY THIS FILE EXISTS, AND IT IS THE CONVENTION RATHER THAN AN INVENTION.
`test_an_unreached_producer_set_cannot_grow_2026-11-08.py` states its own honest
limit: its reached predicate is TEXTUAL, asking only whether a producer's
filename appears somewhere under `bench/tests/`. It cannot tell a producer that
is EXECUTED from one that is merely named, so a producer that has stopped working
keeps its mention and passes. The dated siblings -- 2026-11-03, 2026-11-08,
2026-11-09, 2026-11-10 and 2026-11-17 -- are what actually run them, and neither
half subsumes the other.

Without this file the 2 producers behind the 2026-11-21 batch would be named in
their guards' docstrings and run by nothing, which is `additive-standard`'s
symmetric form broken: an addition nothing reaches is not additive. 11 confirmed
defects in this project were additions that did nothing.

★ THE 3 MUTATION HARNESSES OF THIS BATCH ARE DELIBERATELY EXEMPT, AND THE
EXEMPTION IS STATED HERE RATHER THAN LEFT TO BE INFERRED, as the admitted-set
convention requires. `the_index_relief_mutations_2026-11-21.py`,
`the_streaming_board_mutations_2026-11-21.py` and
`the_status_flag_mutations_2026-11-21.py` each EDIT A LIVE SOURCE FILE and invoke
pytest once per mutation. Executing one from inside pytest would run the suite
within the suite, which is exactly what `test_the_nested_suite_stays_bounded_2026-10-28.py`
exists to bound, and it would mutate the tree while a board runs -- a recorded
defect of its own. Their `--help` inertness IS tested below, because that is the
part of them a board can afford to check.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]

#: (filename, args, a regex the output MUST carry so a silent no-op cannot pass)
PRODUCERS = [
    ("the_index_can_never_stop_filling_2026-11-21.py", [],
     r"z3 -> unsat"),
    ("the_index_can_never_stop_filling_2026-11-21.py", ["--json"],
     r'"rate_u16_per_day":'),
    ("the_board_can_stream_without_losing_its_verdict_2026-11-21.py", [],
     r"The only form that satisfies all 3: logfile \+ background tail"),
    #: ★ ADDED 2026-11-21 AFTER THIS GUARD REFUSED THE SCRIPT, which is the
    #: guard doing its job: a producer the suite does not run is the
    #: addition-nothing-reaches half of the additive standard. It backs a
    #: COUNT quoted to the founder -- that 4 exit-code and observability
    #: faults this session were in the project's own tooling rather than in
    #: the subject -- and a count quoted to him with no committed script is
    #: `measured-rate-travels-with-its-script` broken inside the analysis
    #: that cites the rule. It REPRODUCES each trap rather than tallying
    #: mentions, because the prose is the thing under suspicion.
    ("four_exit_code_traps_in_my_own_tooling_2026-11-21.py", [],
     r"4 of 4 judged arm\(s\) reproduced"),
    ("four_exit_code_traps_in_my_own_tooling_2026-11-21.py", ["--json"],
     r'"status": "REPRODUCED"'),
    #: ★ ADDED 2026-11-21 on his instruction, *"give me a tts that will bring me
    #: fully up to speed"*, after he said the 29 decisions of 2026-11-08 had
    #: demoralised him and asked when it would end. The view answers that from
    #: the record, and it is allowed to answer badly: the assertion below pins
    #: only that it REACHES a convergence verdict, never which verdict, because
    #: a view that can only reassure is not a measurement.
    ("since_you_last_looked_2026-11-21.py", [],
     r"DOES THIS CONVERGE\? arrivals against closures"),
    ("since_you_last_looked_2026-11-21.py", ["--since", "2026-11-08"],
     r"SINCE YOU LAST LOOKED — 2026-11-08"),
]

HARNESSES = [
    "the_index_relief_mutations_2026-11-21.py",
    "the_streaming_board_mutations_2026-11-21.py",
    "the_status_flag_mutations_2026-11-21.py",
]


def _run(name: str, args: list[str], timeout: int = 240):
    path = REPO / "scripts" / name
    assert path.is_file(), f"{name} does not exist"
    return subprocess.run([sys.executable, str(path), *args],
                          capture_output=True, text=True, cwd=REPO,
                          timeout=timeout)


@pytest.mark.parametrize("name,args,must_match", PRODUCERS,
                         ids=[f"{n}{'-'.join(a)}" for n, a, _m in PRODUCERS])
def test_the_producer_runs_and_says_something(name, args, must_match):
    """It must exit 0 AND print the thing it exists to print.

    Exit 0 alone is not enough: a script whose measurement silently produced
    nothing also exits 0, which is the same blindness the `--help` guard was
    written to close.
    """
    r = _run(name, args)
    assert r.returncode == 0, (
        f"{name} {' '.join(args)} exited {r.returncode}\n"
        f"{r.stdout[-1500:]}\n{r.stderr[-1500:]}")
    assert re.search(must_match, r.stdout), (
        f"{name} exited 0 but its output does not carry {must_match!r}; "
        f"a producer that prints nothing is not a measurement\n{r.stdout[-800:]}")


@pytest.mark.parametrize("name", HARNESSES)
def test_a_mutation_harness_answers_help_without_touching_the_tree(name):
    """The exempt scripts are still held to the one check a board can afford.

    `--help` must print a usage line, exit 0, and leave the subject file
    byte-identical -- a harness whose `--help` ran the work would edit live
    source to answer a question about itself.
    """
    subjects = [REPO / "scripts" / "cdsfl_sv.py",
                REPO / "hooks" / "pre-commit",
                REPO / "scripts" / "build_decisions_file_2026-11-07.py"]
    before = {p: p.read_bytes() for p in subjects if p.is_file()}
    r = _run(name, ["--help"], timeout=60)
    assert r.returncode == 0, r.stderr[-600:]
    assert r.stdout.lstrip().startswith("usage:"), r.stdout[:200]
    for p, b in before.items():
        assert p.read_bytes() == b, f"{name} --help modified {p.name}"


def test_the_exemption_is_stated_in_this_file():
    """An exemption that is not written down is indistinguishable from an oversight."""
    src = pathlib.Path(__file__).read_text(encoding="utf-8")
    for name in HARNESSES:
        assert name in src, name
    assert "DELIBERATELY EXEMPT" in src


def test_every_script_this_batch_added_is_accounted_for():
    """★ DERIVED FROM THE TREE, so a 6th script added later cannot slip past.

    The list is built by globbing today's date rather than typed, which is the
    difference between a guard and a snapshot: a typed list stays green when the
    thing it is meant to notice happens.
    """
    found = {p.name for p in (REPO / "scripts").glob("*_2026-11-21.py")}
    accounted = {n for n, _a, _m in PRODUCERS} | set(HARNESSES)
    assert found == accounted, (
        f"unaccounted scripts dated 2026-11-21: {sorted(found - accounted)}; "
        f"either run them here or state an exemption beside them")
