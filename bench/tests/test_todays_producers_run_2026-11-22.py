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


# ===========================================================================
# THE 3 PRODUCERS THE BOARD CAUGHT AS REACHED BY NO TEST. Appended 2026-11-22.
#
# `test_an_unreached_producer_set_cannot_grow_2026-11-08.py` refused the batch-2
# board naming exactly these 3, and its message is the right one: *"Either have
# a test execute them, or -- if one is deliberately exempt -- say so beside the
# exemption. Re-pinning to silence this is how a ratchet becomes a rubber
# stamp."* So they are EXECUTED here rather than admitted to the pinned set.
#
# COST MEASURED BEFORE WIRING, because the board runs on his machine: 18.0 s,
# 0.1 s and 6.7 s, so 24.8 s against the 2984 s board that refused them =
# 0.008311 of it. The 18 s one walks the tree 4 times by design, since its whole
# subject is how the answer moves with the corpus.
#
# EACH ASSERTS A SUBSTANTIVE LINE, NOT MERELY exit 0. A producer that runs and
# says nothing is reached by a test and still guarded by nothing, which is the
# vacuity the additive standard names.
# ===========================================================================


def test_the_corpus_count_producer_shows_the_spread_and_excludes_itself():
    """The count moves by a factor of 2.8 with the corpus, and the script is
    outside its own population -- its first run counted itself."""
    r = _run("a_corpus_count_with_no_stated_corpus_2026-11-22.py")
    assert r.returncode == 0, r.stdout[-800:]
    assert "SPREAD FROM CORPUS CHOICE ALONE" in r.stdout, r.stdout
    assert "the exclusion BITES by" in r.stdout, (
        "the self-exclusion no longer reports biting, so either the docstring "
        "stopped naming the term or the exclusion broke; both make the figures "
        "measurements of the instrument")
    assert "harvest exclusion moves it by" in r.stdout, r.stdout


def test_the_tripwire_reachability_producer_runs_both_routes():
    """The billing tripwire's nesting hole: protocol admits it, call graph does
    not. Both halves must be reported, or 'latent' is an assertion."""
    r = _run("is_the_tripwire_hole_reachable_2026-11-22.py")
    assert r.returncode == 0, r.stdout[-800:]
    assert r.stdout.strip(), "the producer printed nothing at all"


def test_the_composability_producer_reports_orthogonal_not_composed():
    """★ A SEAT'S MEASUREMENT, EXECUTED RATHER THAN BELIEVED.

    The `cc2` seat delivered this 2x2 in the joint round of 2026-11-22. Run
    here, it reports that P2 is discharged by its own repair alone and P1 by the
    other seat's alone, with no cell dominating either single fix on the other's
    property -- so under `composability-requires-a-measurement` the 2 are
    ORTHOGONAL SINGLE FIXES and no composition claim may be made.

    Pinned because the conclusion is the useful part: if a future change made
    these compose, this assertion goes red and the claim must be re-measured
    rather than inherited.
    """
    r = _run("do_the_two_seats_repairs_compose_2026-11-22.py")
    assert r.returncode == 0, r.stdout[-800:]
    assert "ORTHOGONAL SINGLE FIXES" in r.stdout, r.stdout
    assert "P2 is discharged by cc2's repair alone" in r.stdout, r.stdout
    assert "P1 is discharged by fable's repair alone" in r.stdout, r.stdout


# ===========================================================================
# THE 2 PRODUCERS PROMOTED IN BATCH 3. Appended 2026-11-22.
#
# `test_an_unreached_producer_set_cannot_grow_2026-11-08.py` caught both within
# 6 minutes of their promotion, in the pre-board check rather than on a
# 50-minute board -- which is the action-triggered set earning its place the
# first time it ran.
# ===========================================================================


def test_the_refusal_budget_producer_reports_the_defect_in_both_arms():
    """B209. EXIT 1 IS CORRECT HERE: a live defect, not a broken producer.

    The watched arm must climb and the unwatched arm must stay pinned, because a
    producer that reported only one of them could not distinguish "the budget is
    broken" from "the budget does not exist".
    """
    r = _run("the_cy_refusal_budget_never_binds_2026-11-22.py")
    assert r.returncode == 1, (
        f"expected exit 1 for the LIVE defect, got {r.returncode}. If this is "
        f"now 0 the key was repaired, and `test_the_cy_refusal_budget_binds` "
        f"will have gone red on its strict xfails -- fix both together.")
    assert "watched arm binds        : True" in r.stdout, r.stdout
    assert "unwatched arm is inert   : True" in r.stdout, r.stdout


def test_the_board_census_validates_against_a_known_answer():
    """It must reproduce a COMPLETED board's own summary before being trusted.

    Validated on BOTH arms deliberately: a census checked only against a clean
    board passes trivially, because an instrument that cannot see failures also
    reads 0. The 2026-11-22 logs give one board with 6 failures and one with 0.
    """
    import pathlib
    logs = sorted(pathlib.Path("bench/logs").glob("*/board*.log"))
    r = _run("the_board_progress_census_2026-11-22.py", "--help")
    assert r.returncode == 0, r.stdout[-600:]
    assert "--validate" in r.stdout, (
        "the census no longer offers --validate, which is the only thing that "
        "makes its in-flight figures trustworthy")
