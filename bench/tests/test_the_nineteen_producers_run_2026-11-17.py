"""The producers behind the 2026-11-17 panel round must RUN, not merely exist.

`test_an_unreached_producer_set_cannot_grow_2026-11-08.py` refused the batch of
2026-11-17 because 4 new producers were reached by no test. Its remediation says
to have a test EXECUTE them, and the surveyor behind it checks only whether a
test NAMES one -- so a mention would have silenced the refusal while proving
nothing. That is the addition-nothing-reaches half of the additive standard, and
satisfying it with a string would be the exact failure the standard describes.

So each producer is RUN here, in a subprocess, and its exit code and a named
line of its output are asserted. NO FIGURE IS PINNED. Every one of these reads
live state -- the task list, the decisions file, the ticket register -- and this
project has already measured what pinning such a figure costs: the same 3
archive numbers drifted 3 times in 10 days, and 2 sibling pins were converted to
floors for that reason. The assertions are therefore on the producer RUNNING, on
it reporting the quantity it claims to report, and on its own self-check
verdict, never on the value.

Two of them require `--round`, and a bare run exits 2 from argparse. That is
checked too, because `a --help must never cost money` and an argument error is
the cheap path: a producer that silently ran a full measurement on no arguments
would bill the founder's machine for a typo.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
SCRIPTS = REPO / "scripts"
ROUND = "the_nineteen_2026-11-17"

#: name -> (argv, a substring its output must contain)
NO_ARG = {
    "how_many_of_the_nineteen_were_already_built_2026-11-17.py": "decisions put to him",
    "why_are_the_open_entries_open_2026-11-17.py": "open",
    "the_shouted_word_predicate_spares_identifiers_2026-11-17.py": "controls",
    "what_a_cheap_preflight_is_worth_2026-11-17.py": "break-even",
}
#: name -> (argv, needle). These carry a reduced mode so a guard can execute
#: them without paying for the full measurement. The FULL run is what the
#: entry's figures come from; what is checked here is that the producer still
#: works, which is the property a citation depends on.
REDUCED = {
    "the_board_cannot_stream_its_test_phase_2026-11-17.py":
        (["--quick"], "the pipeline loses the exit code"),
    "the_board_verdict_mutations_2026-11-17.py":
        ([], "mutations caught"),
    "the_mirror_ordering_mutations_2026-11-17.py":
        ([], "mutations caught"),
}

NEEDS_ROUND = {
    "build_the_nineteen_panel_brief_2026-11-17.py": ["--round", ROUND, "--dry-run"],
    "did_the_panel_match_me_2026-11-17.py": ["--round", ROUND],
}


def _run(name: str, argv: list[str], timeout: int = 300):
    p = SCRIPTS / name
    assert p.is_file(), f"{name} is not on disk; this guard names a producer that is gone"
    return subprocess.run([sys.executable, str(p), *argv], cwd=REPO,
                          capture_output=True, text=True, timeout=timeout)


class TestEachProducerRuns:
    @pytest.mark.parametrize("name,needle", sorted(NO_ARG.items()))
    def test_a_no_argument_producer_runs_clean(self, name, needle):
        r = _run(name, [])
        assert r.returncode == 0, (
            f"{name} exited {r.returncode}; a producer that cannot run cannot "
            f"support the figure it is cited for.\n{r.stdout[-1200:]}\n{r.stderr[-600:]}")
        assert needle.lower() in r.stdout.lower(), (
            f"{name} ran but never reported {needle!r}, so it is not measuring "
            f"what this guard believes it measures.\n{r.stdout[-800:]}")

    @pytest.mark.parametrize("name,argv", sorted(NEEDS_ROUND.items()))
    def test_a_round_producer_runs_against_the_real_round(self, name, argv):
        r = _run(name, argv)
        assert r.returncode == 0, (
            f"{name} exited {r.returncode} on the real round.\n"
            f"{r.stdout[-1500:]}\n{r.stderr[-600:]}")

    @pytest.mark.parametrize("name", sorted(NEEDS_ROUND))
    def test_a_missing_round_is_an_argument_error_not_a_measurement(self, name):
        """Cheap failure on a typo, rather than a full run against nothing."""
        r = _run(name, [])
        assert r.returncode == 2, (
            f"{name} exited {r.returncode} with no --round; argparse should "
            f"refuse at 2 so a typo costs nothing")
        assert "usage:" in (r.stderr + r.stdout).lower()


class TestTheBoardVerdictProducersRun:
    """B202's producers, in their reduced modes."""

    @pytest.mark.parametrize("name,spec", sorted(REDUCED.items()))
    def test_a_reduced_producer_runs(self, name, spec):
        argv, needle = spec
        r = _run(name, argv, timeout=600)
        assert r.returncode == 0, (
            f"{name} exited {r.returncode}.\n{r.stdout[-1500:]}\n{r.stderr[-600:]}")
        assert needle.lower() in r.stdout.lower(), (
            f"{name} ran but never reported {needle!r}.\n{r.stdout[-900:]}")

    def test_the_pipeline_really_does_lose_the_exit_code(self):
        """The finding B202 rests on, re-established by execution each run.

        If this ever reports otherwise, the shell's pipeline semantics changed
        and B202's whole argument needs revisiting -- which is why it is
        asserted rather than remembered.
        """
        r = _run("the_board_cannot_stream_its_test_phase_2026-11-17.py",
                 ["--quick"], timeout=600)
        assert "the pipeline loses the exit code: True" in r.stdout, (
            "piping pytest through tee no longer zeroes the recorded exit code; "
            "re-read B202, the board's silent test phase, before trusting its "
            f"conclusion.\n{r.stdout[-900:]}")


class TestThePreflightArithmeticHolds:
    """The negative result is the load-bearing one, so it is asserted.

    NO FIGURE IS PINNED. The ledger grows by a row per board -- it gained one
    between the figures being quoted and this guard being written, moving the
    break-even from 0.142151 to 0.143139 -- so what is held is the DIRECTION:
    the narrow subset can pay for itself and the wide one cannot.
    """

    def test_the_wide_subset_is_refused_on_arithmetic(self):
        r = _run("what_a_cheap_preflight_is_worth_2026-11-17.py", [], timeout=300)
        assert r.returncode == 0, r.stdout[-1200:]
        assert "UNREACHABLE" in r.stdout, (
            "the 16-file pre-flight no longer reports as unreachable. Either the "
            "board got much slower or the refusal rate rose; re-read the verdict "
            "before widening the pre-flight.")
        assert "the narrow subset can pay for itself : True" in r.stdout
        assert "the wide subset can pay for itself   : False" in r.stdout

    def test_it_refuses_to_claim_a_catch_rate(self):
        """The post-hoc limit must travel with the figures, not be dropped."""
        r = _run("what_a_cheap_preflight_is_worth_2026-11-17.py", [], timeout=300)
        assert "NOT MEASURED: the actual catch rate" in r.stdout, (
            "the producer stopped stating that its file selection was post-hoc, "
            "which is the one thing that keeps its figures honest")


class TestTheScoringReadsFrozenArtefacts:
    """The repair of 2026-11-17: figures must survive the live file moving."""

    def test_the_matcher_reads_the_delivered_brief(self):
        r = _run("did_the_panel_match_me_2026-11-17.py", ["--round", ROUND])
        assert r.returncode == 0, r.stdout[-900:]
        assert "letters read from the DELIVERED brief" in r.stdout, (
            "the matcher no longer reports reading the frozen brief, so it may "
            "have reverted to replaying the live decisions file -- which stops "
            "reproducing as soon as a recommendation is edited")

    def test_a_joint_round_resolves_to_its_parent(self):
        r = _run("did_the_panel_match_me_2026-11-17.py", ["--round", f"{ROUND}_joint"])
        assert r.returncode == 0, r.stdout[-900:]
        assert ROUND in r.stdout, (
            "the joint round did not resolve its letters from the blind parent; "
            "the joint brief carries no lettered options, so looking for them "
            "there reports all items as missing")

    def test_the_builder_refuses_a_leaky_brief(self):
        """Blindness is enforced by construction, so the builder must say so."""
        r = _run("build_the_nineteen_panel_brief_2026-11-17.py",
                 ["--round", ROUND, "--dry-run"])
        assert r.returncode == 0, r.stdout[-900:]
        assert "surviving" in r.stdout.lower(), (
            "the builder no longer reports how many recommendation markers "
            "survived, so a leak would be undetectable from its output")
