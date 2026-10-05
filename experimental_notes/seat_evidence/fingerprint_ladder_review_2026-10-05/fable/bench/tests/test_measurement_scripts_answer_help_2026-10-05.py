# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'fingerprint_ladder_review_2026-10-05', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 2062789df2d440f3a12147db5c5452c696efffa8b11a4f783a598ec2d5f77998
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The 2026-10-05 measurement scripts answer `--help` -- EXECUTED, not vouched.

WHY THIS EXISTS (panel review, 2026-10-05). After the `answer_help` ->
`_parse_args` rename, these scripts are covered by NO executing guard:

* `test_help_never_acts_2026-09-11.py::test_every_script_that_writes_answers_help`
  never examines them -- its population is scripts whose source matches the
  WRITES pattern, and these are read-only (measured: WRITES=False for all 8).
  "Covered by the sibling guard" would be the wrong description; "outside its
  population, by design" is the right one.
* `test_help_is_answered_2026-09-11.py::TestTheWiringIsReal` includes them in
  its population but vouches for them STRUCTURALLY, because their source
  mentions `argparse` -- and `answers_help` counts an `ArgumentParser`
  constructed ANYWHERE, including inside a function nothing calls. A parser
  that is defined but never reached would pass both static checks while
  `--help` ran the whole measurement.

So this file runs each one with `--help` and requires an answer: exit 0 and a
usage line. All are read-only analytics over the archive (verified 2026-10-05:
no write call, no network use), and each parses argv before importing anything
heavy, so the subprocess cost is milliseconds, not a measurement.
"""
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]

#: Pinned by name, the same convention as `test_every_repaired_guard_survives_dash_m`.
SCRIPTS = (
    "in_round_clearance_is_monotone_2026-10-05.py",
    "in_round_falsifiers_are_discarded_2026-10-05.py",
    "sweep_channels_are_post_verdict_2026-10-05.py",
    "the_blockers_are_shown_as_settled_2026-10-05.py",
    "the_counter_and_the_router_disagree_2026-10-05.py",
    "the_sim_panel_is_not_heterogeneous_2026-10-05.py",
    "what_the_sim_runner_never_carried_over_2026-10-05.py",
    "why_the_blockers_were_never_offered_2026-10-05.py",
    "the_provenance_gate_reads_text_not_behaviour_2026-10-05.py",
)


class TestHelpIsAnsweredByExecution:
    @pytest.mark.parametrize("name", SCRIPTS)
    def test_help_exits_zero_with_a_usage_line(self, name):
        p = REPO / "scripts" / name
        assert p.is_file(), f"{name} is gone; remove it from this pin deliberately"
        r = subprocess.run([sys.executable, str(p), "--help"],
                           capture_output=True, text=True, timeout=120,
                           cwd=str(REPO))
        assert r.returncode == 0, (
            f"{name} --help exited {r.returncode}; stderr: {r.stderr[:300]}")
        first = (r.stdout.splitlines() or [""])[0].lower()
        assert first.startswith("usage:"), (
            f"{name} --help did not lead with a usage line; it may have run "
            f"its measurement instead. stdout starts: {r.stdout[:200]!r}")

    @pytest.mark.parametrize("name", SCRIPTS)
    def test_an_unknown_flag_is_refused(self, name):
        """A flag the parser does not know must exit 2, not be read as data --
        the A16 survey's defect class (a `--help` consumed as a filename)."""
        p = REPO / "scripts" / name
        r = subprocess.run([sys.executable, str(p), "--no-such-flag"],
                           capture_output=True, text=True, timeout=120,
                           cwd=str(REPO))
        assert r.returncode == 2, (
            f"{name} accepted --no-such-flag (exit {r.returncode}); an "
            f"unrecognised argument reading as success is the 118-day no-op "
            f"class again")
