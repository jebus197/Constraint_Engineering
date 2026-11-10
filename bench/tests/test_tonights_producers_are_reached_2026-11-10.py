"""Every measurement producer written on 2026-11-10 must be EXECUTED by something.

WHY THIS FILE EXISTS, AND IT IS A DEBT I INCURRED RATHER THAN A RULE I CHOSE.
`test_an_unreached_producer_set_cannot_grow_2026-11-08.py` refused the night's
commit by name: 4 producers dated 2026-11-10 were reached by NO test and were
not in the admitted set. Its own words are the remedy and the warning --
"Either have a test execute them, or -- if one is deliberately exempt -- say so
beside the exemption. Re-pinning to silence this is how a ratchet becomes a
rubber stamp." So this file executes them rather than pinning them.

THE SHAPE IS THE 2026-11-08 SIBLING'S, NOT AN INVENTION. A `DATE`, a glob over
`scripts/*{DATE}*.py`, a `MUST_RUN` tuple, a parametrised run, a `--help` check,
and an accounted-for test that puts what is ON DISK to the real decision so a
producer added later cannot be covered by neither list. That design is read from
the sibling and reused here deliberately: 2 dated guards with different shapes
would be 2 definitions of "reached".

THE `--help` RULE WAS NOT MET WHEN THE PRODUCERS WERE WRITTEN, AND THAT IS
RECORDED RATHER THAN QUIETLY FIXED. 7 of the 10 were written with NO argparse at all,
so `--help` was ignored and the whole measurement ran -- and 1 of them walks the
entire run archive. His standing rule is that a `--help` must never cost money
or minutes. Each now parses `--help` and nothing else, taking its description
from its own module docstring so the usage text cannot drift from the file.
Measured after the change: 10 of 10 exit 0 with a usage line in 0.06 s. The
worst case repaired was 66.56 s of real measurement answering a `--help`.

WHAT EACH PRODUCER MEASURES, so a reader need not run them to find out:
  * `the_prose_gates_sentinel_admitted_nothing` -- the prose apply-back branch
    compared its verdict against a constant `fix_efficacy` does not define, so
    it admitted 0 of 7 reachable verdicts.
  * `the_baselines_filename_changes_the_rule_set` -- a lint baseline whose
    FILENAME loses its date is held to a different rule set, reading 88
    findings where the truth is 22, which HIDES a worsening.
  * `the_rho_replay_reads_the_wrong_two_keys` -- `replay_rho.py` divides the
    wrong numerator by the wrong denominator; both correct series are in the
    archive and it reads neither.
  * `is_the_harness_domain_general_in_its_decisions` -- 47 of 206 live modules
    mention a domain and only 10 DECIDE on one; the canonical runner carried 0
    domain-conditioned branches before 2026-11-10.

EXIT CODES ARE NOT ASSERTED TO BE 0, DELIBERATELY. 3 of the 4 are DEFECT
producers that exit 1 once their defect is repaired, so that they cannot outlive
it. What is asserted is that each RUNS -- it must not raise, time out, or print
nothing -- which is the property the ratchet's textual predicate cannot see.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "scripts"
DATE = "2026-11-10"

#: Producers that must RUN. Every one was executed and timed before listing,
#: not added and hoped for.
MUST_RUN = (
    "is_the_harness_domain_general_in_its_decisions_2026-11-10.py",
    "the_baselines_filename_changes_the_rule_set_2026-11-10.py",
    "the_claim_patterns_key_on_symbols_not_words_2026-11-10.py",      # 0.91 s
    "the_dimensional_check_tests_homogeneity_not_correctness_2026-11-10.py",
                                                                      # 5.64 s
    "the_prose_gates_sentinel_admitted_nothing_2026-11-10.py",
    "the_rho_replay_reads_the_wrong_two_keys_2026-11-10.py",
    "the_topics_tools_on_the_projects_own_corpus_2026-11-10.py",     # 61.55 s
    "what_a_claim_pattern_widening_would_route_2026-11-10.py",        # 1.06 s
    "which_admissions_are_truth_blind_2026-11-10.py",                # 11.31 s
    "a_third_class_row_was_invisible_to_its_own_guard_2026-11-10.py",
                                                                    # 4.79 s
)

#: ★ 4 -> 10 ON 2026-11-10, AND A FREE PANEL SEAT IS WHY. The 3 added here
#: were CITED as producers by task entries B22 and B136 while living only in
#: a scratchpad directory, so those entries cited evidence a clone could not
#: reach -- `measured-rate-travels-with-its-script` broken in the entries that
#: record a measurement. The seat's strongest disagreement named it: a brief
#: quoting a 2-of-5 rate from a producer absent from the dispatched tree.
#: THE SLOWEST IS 61.55 s AND IT IS IN `MUST_RUN` RATHER THAN `EXEMPT`,
#: deliberately: an exemption written by the author of the thing the rule is
#: about is how the accounting stops meaning anything. 61.55 s sits inside
#: this file's existing 600 s per-producer timeout.
#: `the_dimensional_check...` exits 0 TODAY because the defect it measures is
#: live, and is designed to exit 1 once the predicate is repaired. The run
#: test accepts 0 and 1 as its 2 findings, so that flip needs no edit here.
#: `which_admissions_are_truth_blind...` was added LAST, after a free panel
#: seat refuted the first narrowing of the false-admit defect. It exits 0
#: while the branch gate dominates the tool-level exclusion it was measured
#: against, and 1 if that ever reverses -- so it cannot outlive its finding.

#: name -> the mechanical reason it is exempt from RUNNING.
#: ★ THE FIRST ENTRY WAS ADDED 2026-11-10 AND A FREE PANEL SEAT FOUND IT, NOT
#: ME. `scripts/build_joint_brief_2026-11-10.py` -- the script that built the
#: brief that seat was answering -- was in neither list, so the accounting
#: ratchet was RED in the tree it was dispatched against. That is the
#: added-and-unwired class committed by the author of the rule's own brief.
#: `MUST_RUN` WOULD BE MECHANICALLY WRONG, not merely awkward, and the reason
#: is measured rather than asserted: a bare invocation exits 2 by argparse
#: design because it requires a parent round, and `test_the_producer_still_runs`
#: refuses anything outside (0, 1) as a broken producer. It also WRITES a
#: BRIEF.md into a round directory, so running it bare would have side effects
#: on the panel archive.
#: AN EXEMPTION FROM RUNNING IS NOT AN EXEMPTION FROM BEING REACHED: the
#: `--help` test below is parametrised over EXEMPT as well, so an exempt
#: producer still has to answer for itself (measured: exit 0 with a usage
#: line in 0.06 s).
EXEMPT: dict[str, str] = {
    "build_joint_brief_2026-11-10.py":
        "requires a parent round as a positional argument, so a bare run exits "
        "2 by argparse design, outside the run test's 0-or-1 contract; and it "
        "WRITES a BRIEF.md into a round directory, so a bare run would alter "
        "the panel archive. Reached by the --help test instead.",
}


@pytest.mark.parametrize("name", MUST_RUN)
def test_the_producer_still_runs(name):
    """It must RUN. Its exit code is its finding and is not asserted here."""
    p = SCRIPTS / name
    if not p.is_file():
        pytest.skip(f"{name} is not in this checkout")
    r = subprocess.run([sys.executable, str(p)], capture_output=True,
                       text=True, timeout=600, cwd=str(REPO))
    assert r.returncode in (0, 1), (
        f"{name} exited {r.returncode}; 0 and 1 are its 2 findings and "
        f"anything else is a broken producer.\n{r.stderr[-1200:]}")
    assert (r.stdout + r.stderr).strip(), (
        f"{name} printed nothing, so it measured nothing a reader can see")


@pytest.mark.parametrize("name", sorted(set(MUST_RUN) | set(EXEMPT)))
def test_the_producer_answers_help_without_doing_the_work(name):
    """A `--help` must never cost money or minutes -- his standing rule.

    All 4 were written WITHOUT argparse, so this check would have failed on
    every one of them and the measurement would have run instead.
    """
    p = SCRIPTS / name
    if not p.is_file():
        pytest.skip(f"{name} is not in this checkout")
    r = subprocess.run([sys.executable, str(p), "--help"], capture_output=True,
                       text=True, timeout=60, cwd=str(REPO))
    assert r.returncode == 0, f"{name} --help exited {r.returncode}"
    assert "usage:" in (r.stdout + r.stderr).lower(), (
        f"{name} --help printed no usage line, so a reader cannot learn what "
        f"it does without running it")


def test_every_2026_11_10_producer_is_accounted_for():
    """ANTI-VACUITY: what is ON DISK, put to the real decision.

    The lists above are hand-written, so a producer added later would be
    covered by neither and this file would pass while the rule went unmet --
    which is the exact shape that refused tonight's commit.
    """
    on_disk = {p.name for p in SCRIPTS.glob(f"*{DATE}*.py")}
    assert on_disk, (
        f"no producer matches *{DATE}*.py, so every test here is vacuous")
    accounted = set(MUST_RUN) | set(EXEMPT)
    missing = sorted(on_disk - accounted)
    assert not missing, (
        f"{len(missing)} producer(s) dated {DATE} are in neither MUST_RUN nor "
        f"EXEMPT: {missing}. Add them to one, with a reason if exempt.")


def test_the_exemptions_each_state_a_mechanical_reason():
    for name, reason in EXEMPT.items():
        assert len(reason) > 20, (
            f"{name} is exempt for {reason!r}, which is not a reason")


def test_the_decision_can_actually_refuse():
    """The accounting check must FAIL on an unaccounted producer.

    Without this, an empty glob or a list that happens to cover everything
    would satisfy the test above on nothing.
    """
    on_disk = {p.name for p in SCRIPTS.glob(f"*{DATE}*.py")}
    pretend = on_disk | {f"a_producer_nothing_runs_{DATE}.py"}
    accounted = set(MUST_RUN) | set(EXEMPT)
    assert sorted(pretend - accounted) == [f"a_producer_nothing_runs_{DATE}.py"], (
        "the accounting predicate does not notice an unaccounted producer, so "
        "it cannot refuse one")
