#!/usr/bin/env python3
"""Every measurement producer written on 2026-11-02 must be EXECUTED by something.

★ WHY THIS EXISTS: IT IS MY OWN BREACH OF HIS ADDITIVE STANDARD, CAUGHT BY THE
PROJECT'S OWN RATCHET. `scripts/scripts_are_reached_2026-09-11.py` reported 12
scripts reached by nothing, and all 12 were written that day. The symmetric half
of `additive-standard` is explicit: *"an addition that nothing reaches is not
additive either: every new flag, gate, subcommand or entry point must be wired to
a caller and executed by a test."* 12 producers quoting figures into reports,
with nothing running them, is precisely that.

AND PROSE DOES NOT FIX IT. The ratchet's `vouches()` rule is asymmetric on
purpose: *"AN INSTRUMENT FILE MAY ONLY VOUCH FOR ANOTHER INSTRUMENT FILE [...]
Writing ABOUT an orphan is not reaching it: 4 times in one morning a sentence
explaining why a script could not be wired made that script read as reached."*
So citing a producer in the master task list does NOT reach it, and the remedy
had to be execution.

WHAT THIS GUARDS, BEYOND THE RATCHET. A producer that no longer runs is a figure
that can no longer be reproduced, and `measured-rate-travels-with-its-script`
makes an unreproducible figure a claim about evidence rather than evidence. These
scripts carry the numbers quoted to the founder today, so a silent breakage of
one is a silent loss of the support for a number he was given.

★ 5 PRODUCERS ARE DELIBERATELY NOT RUN HERE, AND THE REASON IS STATED RATHER
THAN THE CONVENIENT ONE. The ratchet's own message offers 3 remedies -- wire it,
cite it, or *"add it to UNREACHED deliberately with the reason"* -- and for these
5 the reason is mechanical, not a preference:
  * the 4 mutation harnesses each invoke `python3 -m pytest` on a guard file, so
    a test that called one would run pytest inside pytest, repeatedly. They are
    validation harnesses for guards, run by hand when a guard changes.
  * `the_stop_gate_tail_read_is_behaviour_preserving` takes 13.90 s and compares
    the live hook against a PRE-CHANGE COPY held in a session scratchpad, which
    does not exist on a fresh checkout. It would fail for an absent file rather
    than for a defect.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "scripts"

#: Producers that must RUN. Each is read-only, exits 0, and completes in under
#: 2 s measured on 2026-11-02 -- so running all of them costs the suite a few
#: seconds and buys reproducibility of every figure quoted to him today.
MUST_RUN = (
    "can_a_simulated_seat_ever_refute_2026-11-02.py",
    "the_stop_gate_is_killed_by_a_timeout_2026-11-02.py",
    "what_passes_and_seats_actually_buy_2026-11-02.py",
    "what_the_fable_gap_actually_cost_2026-11-02.py",
    "does_a_falsifier_read_its_target_2026-11-02.py",
    "the_seats_strip_the_power_operator_2026-11-02.py",
    "was_p2_ever_testable_on_one_run_2026-11-02.py",
    "has_the_bound_orchestrator_been_built_or_run_2026-11-02.py",
    "can_a_prereg_be_scored_mid_run_2026-11-02.py",
    "would_a_round_predicate_catch_what_the_detectors_miss_2026-11-02.py",
    "triage_the_unadopted_seat_designs_2026-11-02.py",
    "the_merge_engine_is_reached_after_all_2026-11-02.py",
    "the_shadow_demotion_report_2026-11-02.py",
    "which_seat_designs_bear_on_his_open_decisions_2026-11-02.py",
    "the_paid_fingerprints_name_a_simulated_run_2026-11-02.py",
    "settle_the_review_backlog_2026-11-02.py",
)

#: Harnesses that must NOT be run from inside the suite, with the mechanical
#: reason each one cannot be. Listed here so the exemption is visible beside the
#: thing it exempts, rather than only in a ratchet file.
NOT_RUN_HERE = {
    "the_cy_gate_mutations_2026-11-02.py": "invokes pytest; would recurse",
    "the_fix_comparator_mutations_2026-11-02.py": "invokes pytest; would recurse",
    "the_round_clock_mutations_2026-11-02.py": "invokes pytest; would recurse",
    "the_two_directive_repairs_mutations_2026-11-02.py": "invokes pytest; would recurse",
    "the_stop_gate_tail_read_is_behaviour_preserving_2026-11-02.py":
        "13.90 s, and needs a pre-change copy held in a session scratchpad "
        "that does not exist on a fresh checkout",
}


@pytest.mark.parametrize("name", MUST_RUN)
def test_the_producer_still_runs(name):
    """EXECUTED, not inspected. A producer that cannot run is not evidence."""
    p = SCRIPTS / name
    if not p.is_file():
        pytest.skip(f"{name} is not in this checkout")
    r = subprocess.run([sys.executable, str(p)], capture_output=True,
                       text=True, timeout=180, cwd=str(REPO))
    assert r.returncode == 0, (
        f"{name} exited {r.returncode}. The figures it produced were quoted to "
        f"the founder, so this is a silent loss of their support.\n"
        f"stderr tail:\n{r.stderr[-900:]}")
    assert r.stdout.strip(), f"{name} ran and printed nothing"


@pytest.mark.parametrize("name", sorted(MUST_RUN))
def test_the_producer_answers_help_without_doing_the_work(name):
    """A --help must never cost anything. His standing rule, and the 2026-10-01
    sweep found 15 of 17 runners billing for one."""
    p = SCRIPTS / name
    if not p.is_file():
        pytest.skip(f"{name} is not in this checkout")
    r = subprocess.run([sys.executable, str(p), "--help"], capture_output=True,
                       text=True, timeout=60, cwd=str(REPO))
    assert "usage:" in (r.stdout + r.stderr).lower(), (
        f"{name} --help printed no usage line, so the flag was ignored and the "
        f"whole measurement ran")


@pytest.mark.parametrize("name,reason", sorted(NOT_RUN_HERE.items()))
def test_an_exempted_harness_still_exists_and_its_reason_still_holds(name, reason):
    """An exemption must not outlive its cause.

    If a mutation harness stops invoking pytest, or the behaviour-preserving
    comparison stops needing a scratchpad copy, the exemption is slack in the
    ratchet and must be removed rather than left standing.
    """
    p = SCRIPTS / name
    if not p.is_file():
        pytest.skip(f"{name} is not in this checkout")
    src = p.read_text()
    if "recurse" in reason:
        assert '"-m", "pytest"' in src or "-m\", \"pytest" in src, (
            f"{name} no longer invokes pytest, so the recursion reason is "
            f"stale; run it from the suite or re-derive the exemption")
    else:
        assert "scratchpad" in src or "bak-" in src, (
            f"{name} no longer depends on a scratchpad copy, so its exemption "
            f"is stale")


def test_no_producer_is_in_both_lists():
    """A name in both would be exempted and run, which hides which rule applies."""
    overlap = set(MUST_RUN) & set(NOT_RUN_HERE)
    assert not overlap, f"{overlap} appear in both MUST_RUN and NOT_RUN_HERE"
