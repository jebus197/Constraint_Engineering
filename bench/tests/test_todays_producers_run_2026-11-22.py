"""Every figure quoted from 2026-11-22's panel round must be re-executable.

`measured-rate-travels-with-its-script`: a measured rate, proportion or count may
be cited only if the script that produced it is committed alongside it. A number
that exists only as prose in a note, a commit message or a CODE COMMENT is a
claim about evidence, not evidence. One of this night's findings was exactly
that -- a comment in `hooks/work_not_narrate.py` declaring "correct in 5 of 5"
with no producer anywhere -- so this file exists to stop the same thing being
true of its own repairs.

These run the producers END TO END rather than reading them, per
`execute-do-not-grep`: a test asserting on a script's source text asserts only
that the script describes itself consistently.
"""
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
S = REPO / "scripts"

PRODUCERS = [
    ("does_the_board_detector_hold_its_polarity_2026-11-22.py",
     "the triage's fail-toward-writing direction, 3 arms"),
    ("the_commit_flag_asks_git_2026-11-22.py",
     "the commit flag over 6 cases"),
    ("the_budget_gates_vocabulary_2026-11-22.py",
     "the budget gate in 3 directions"),
    #: ADDED 2026-11-22. Both are self-contained and cheap, so the board can
    #: execute them. 2 further producers landed the same day are NOT here and
    #: the reason is deliberate: `record_the_failing_set_2026-11-22.py` needs a
    #: pytest log as input and wants a fixture, and
    #: `prove_the_hidden_ruling_check_still_bites_2026-11-22.py` drives pytest
    #: itself, which must never be nested inside the board. Wiring those 2 is
    #: batch-2 work.
    ("the_watchdog_trouble_channel_2026-11-22.py",
     "the watchdog's TROUBLE regex, before and after the word boundary"),
    ("the_gate_decides_on_the_pulse_2026-11-22.py",
     "the cy gate's discriminator, both directions"),
]


def _run(name, *args, timeout=600):
    return subprocess.run([sys.executable, str(S / name), *args],
                          cwd=REPO, capture_output=True, text=True, timeout=timeout)


@pytest.mark.parametrize("name,what", PRODUCERS, ids=[p[0] for p in PRODUCERS])
def test_the_producer_exists(name, what):
    assert (S / name).is_file(), f"{what}: producer missing"


@pytest.mark.parametrize("name,what", PRODUCERS, ids=[p[0] for p in PRODUCERS])
def test_the_producer_runs_green(name, what):
    r = _run(name)
    assert r.returncode == 0, f"{what}\n{r.stdout[-1200:]}\n{r.stderr[-400:]}"


def test_the_vocabulary_producer_catches_the_projects_own_sentences():
    """The 2 sentences this project writes at itself, named explicitly.

    They are the reason the widening was more than a vocabulary quibble: the
    hook's own refusal message and the panel brief's section 2 are both
    instructions of the shape the gate exists to refuse, and both passed
    through it before 2026-11-22.
    """
    r = _run("the_budget_gates_vocabulary_2026-11-22.py")
    assert r.returncode == 0, r.stdout[-800:]
    assert "10 of 10 caught" in r.stdout, r.stdout
    assert "MISSED" not in r.stdout, r.stdout


def test_the_vocabulary_producer_reports_no_new_false_refusals():
    """Widening an ACCEPTING predicate is a tightening; both costs are checked."""
    r = _run("the_budget_gates_vocabulary_2026-11-22.py")
    assert "6 of 6 correct" in r.stdout, r.stdout
    assert "4 of 4 correct" in r.stdout, r.stdout
    assert "WRONGLY REFUSED" not in r.stdout, r.stdout


def test_the_polarity_producer_runs_all_three_arms():
    """Arm C is the anti-vacuity arm: a predicate repaired into always
    answering '' would pass arms A and B and be useless."""
    r = _run("does_the_board_detector_hold_its_polarity_2026-11-22.py")
    assert r.returncode == 0, r.stdout[-800:]
    for arm in ("arm A", "arm B", "arm C"):
        assert arm in r.stdout, f"{arm} did not run:\n{r.stdout}"


def test_the_commit_flag_producer_separates_the_fail_safe_direction():
    """The hit rate and the never-claim-a-commit property are counted apart."""
    r = _run("the_commit_flag_asks_git_2026-11-22.py")
    assert r.returncode == 0, r.stdout[-800:]
    assert "correct in 6 of 6" in r.stdout, r.stdout
    assert "wrongly reported as a commit: 0" in r.stdout, r.stdout


def test_the_hook_comment_names_its_producer():
    """The finding that prompted this file: a figure with no script behind it."""
    t = (REPO / "hooks" / "work_not_narrate.py").read_text()
    assert "the_commit_flag_asks_git_2026-11-22.py" in t, (
        "the commit-flag comment quotes a figure without naming its producer")
    assert "DRIVEN OVER 6 CASES" in t, "the live figure was not updated"
    assert "DRIVEN OVER 5 CASES" not in t, "the superseded figure is still live"
    #: ★ A SUPERSEDED FIGURE MAY BE QUOTED; IT MAY NOT BE DECLARED. This project
    #: names retired numbers on purpose, so a reader who remembers one can see
    #: which moved -- so a flat "the string is absent" assertion would forbid
    #: the correction itself. A scar is not a wound. Every surviving mention
    #: must sit on a line that marks it as superseded.
    for i, line in enumerate(t.splitlines(), 1):
        if "5 of 5" in line:
            assert "previously" in line.lower(), (
                f"line {i} declares the retired figure rather than quoting it: "
                f"{line.strip()}")
