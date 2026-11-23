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
    #: ADDED 2026-11-23, BECAUSE THE BOARD CAUGHT IT AS REACHED BY NO TEST.
    #: `test_an_unreached_producer_set_cannot_grow_2026-11-08.py` refused the
    #: batch naming it, and its message is the right one: "Either have a test
    #: execute them, or -- if one is deliberately exempt -- say so beside the
    #: exemption. Re-pinning to silence this is how a ratchet becomes a rubber
    #: stamp." It is executed here rather than pinned. Self-contained: it reads
    #: no file and spawns nothing, computing from 2 pinned ledger figures.
    ("how_many_boards_does_a_batch_cost_2026-11-22.py",
     "boards per landed batch, closed form against 400,000 draws"),
    #: ADDED 2026-11-23, AND THE RATCHET WOULD HAVE REFUSED THE BATCH WITHOUT IT.
    #: `test_an_unreached_producer_set_cannot_grow_2026-11-08.py` named it
    #: verbatim -- "1 producer(s) are reached by NO test and are not in the
    #: admitted set" -- so this entry is the producer being EXECUTED, not pinned.
    #:
    #: ★ THE LADDER COULD NOT HAVE CAUGHT THIS, AND THAT IS THE POINT. The
    #: pre-board ladder passed clean at 2269 tests on the same staged diff while
    #: that ratchet was red, because a whole-tree invariant guard fires on an
    #: addition ELSEWHERE and a diff-derived selector never names it. Seat
    #: `fable` named this exact guard as class (i) of the 3 a selector is blind
    #: to, in round `panel_joint_b12_boardpolicy_20261123T201748Z`, hours before
    #: it fired here. Recorded under B216 as evidence that the ladder is a
    #: pre-filter and never a substitute.
    #:
    #: ADMITTED ON A MEASUREMENT, not on a preference: it spawns no pytest, and
    #: runs in 1.44 to 2.46 s over 3 runs against a mean producer-guard cost of
    #: 38.3484 s on batch 12's own durations table -- about 0.00046 of a 3290 s
    #: board. It reads the duration ledger and the hook, and calls `git log`.
    ("why_is_the_board_getting_slower_2026-11-23.py",
     "board cost: 113 boards, 0 over 3 h, growth per day, and the day-level share"),
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


# ===========================================================================
# THE 2 PRODUCERS WRITTEN FOR THE BATCH 4-10 PANEL BRIEF. Appended 2026-11-23.
#
# Both were caught by `test_an_unreached_producer_set_cannot_grow_2026-11-08.py`
# BEFORE the board ran -- the FOLLOW step the ffafp gate said was owed, which
# would otherwise have refused the batch after about 31 minutes.
#
# COST MEASURED BEFORE WIRING, because the board runs on his machine: 1.90 s
# and 1.11 s, so 3.01 s in total.
#
# ★ THE PANEL-LINE PRODUCER'S FIGURE IS DELIBERATELY NOT PINNED, AND THAT IS
# THE WHOLE POINT OF THIS COMMENT. Its default range is `HEAD~10..HEAD`, so the
# proportion MOVES with every commit that lands. Pinning the measured 7 of 10
# would mean that PANELLING EVERY FUTURE BATCH -- the fix -- turns this test
# red, which is `feedback_a_guard_can_pin_the_defect_as_current_behaviour`
# exactly. So the STRUCTURE and the 2-route agreement are asserted and the
# value is not.
# ===========================================================================


def test_the_panel_line_producer_reports_a_proportion_on_two_agreeing_routes():
    """It must report coverage and have both interval routes agree.

    The VALUE is not asserted, on purpose -- see the block comment above. What
    is asserted is that the producer still computes a proportion, still reports
    both routes, and still carries its own stated boundary, because a producer
    that quietly stopped reporting one route would look identical in prose.
    """
    r = _run("was_the_panel_line_ignored_2026-11-23.py")
    assert r.returncode == 0, r.stdout[-900:] + r.stderr[-400:]
    assert "UNCOVERED:" in r.stdout, r.stdout[-600:]
    assert "landed with no useful panel round" in r.stdout, r.stdout[-600:]
    assert "Wilson 95%" in r.stdout and "Clopper-Pearson 95%" in r.stdout, (
        "a proportion reported on 1 route only")
    #: The agreement figures are printed; a disagreement would have tripped the
    #: producer's own assertions and exited non-zero, so reaching here means
    #: both pairs agreed. Assert the AGREEMENT IS REPORTED, so a future edit
    #: cannot drop the cross-check and still look the same.
    assert "closed form agrees to" in r.stdout, r.stdout[-600:]
    assert "exact-tail bisection agrees to" in r.stdout, r.stdout[-600:]
    #: ITS STATED LIMIT MUST SURVIVE. The producer measures the GATE'S
    #: predicate, not "was the work reviewed by any means", and a reader who
    #: loses that distinction over-reads the figure.
    assert "does NOT establish" in r.stdout, (
        "the producer stopped stating what its figure does not support")


def test_the_panel_line_producer_imports_the_gates_own_predicate():
    """Re-implementing the gate's decision is the 2-forms-disagree defect.

    Asserted by EXECUTION, not by reading the import line: the module is loaded
    and its loader function is called, so a stub that merely named the gate
    file would not pass.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_plip", S / "was_the_panel_line_ignored_2026-11-23.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    gate = m.load_gate_predicate()
    assert hasattr(gate, "rounds_since"), (
        "the loaded module is not the gate predicate")
    assert callable(gate.rounds_since)
    #: And it must be the SAME object the gate itself uses -- same file.
    assert m.GATE_PREDICATE.name == "was_this_batch_reviewed_2026-11-22.py"
    assert m.GATE_PREDICATE.is_file()


def test_the_suite_rate_producer_separates_one_sided_from_two_sided():
    """★ THE FINDING THIS PRODUCER EXISTS TO PIN, and it is pinnable because
    the producer computes from 2 PINNED observation pairs rather than from a
    corpus that grows.

    A draft of the batch 4-10 brief was about to offer the one-sided tail of a
    Fisher test to a panel as a '3rd route' sitting below 0.05, which would
    have switched the question from 'are the rates different' to 'is the new
    rate lower' after the first answer was known. These assertions keep the
    two-sided and one-sided figures LABELLED APART.
    """
    r = _run("are_the_two_suite_rates_distinguishable_2026-11-23.py")
    assert r.returncode == 0, r.stdout[-900:] + r.stderr[-400:]
    assert "TWO-SIDED TESTS" in r.stdout and "ONE-SIDED TEST" in r.stdout, (
        "the 2 kinds of test are no longer labelled apart, which is the entire "
        "point of this producer")
    assert "p = 4.649438e-02" in r.stdout, r.stdout[-700:]
    assert "p = 5.005710e-02" in r.stdout, r.stdout[-700:]
    assert "p = 2.461612e-02" in r.stdout, r.stdout[-700:]
    #: ★ THE STRADDLE IS STILL PRINTED BUT IS NO LONGER THE REASON, and this
    #: assertion was changed on 2026-11-23 because it pinned a superseded
    #: conclusion as current behaviour. The joint panel's cc2 seat showed that
    #: "the 2 routes straddle 0.05" is a fact about CHOOSING Fisher and Yates:
    #: driven, 5 of 6 two-sided routes REJECT, Yates alone does not, and
    #: Barnard and Boschloo are unconditional exact tests independent of
    #: Fisher's construction. Pinning the straddle as the justification would
    #: make correcting the reasoning turn this test red.
    assert "two-sided routes reject at 0.05" in r.stdout, (
        "the producer no longer reports the whole route family, so a reader "
        "sees 2 selected routes as though they bounded it")
    assert "interval methods on the DIFFERENCE exclude 0" in r.stdout, (
        "the interval on the difference is the right object for comparing 2 "
        "proportions; its absence leaves the invalid Wilson-overlap argument "
        "as the only interval evidence")
    assert "ADDED tests ->" in r.stdout, (
        "the composition sensitivity is what actually refuses the rate claim; "
        "without it the refusal rests on a threshold again")
    assert "not a 3rd route" in r.stdout, (
        "the producer stopped saying the one-sided figure is not independent")


def test_the_suite_rate_producer_names_the_population_change():
    """The objection that outranks every p-value here: the suites differ.

    611 tests were added between the 2 runs, so a rate comparison assumes the
    added tests fail at the same rate as the existing ones. That assumption is
    untested, and it is a stronger reason to prefer the count statement than
    any threshold argument.
    """
    r = _run("are_the_two_suite_rates_distinguishable_2026-11-23.py")
    assert "611 tests" in r.stdout, r.stdout[-700:]
    #: The Wilson overlap is REPORTED and explicitly labelled invalid as an
    #: argument; it is not asserted as evidence. See the note above.
    assert "overlap of 2 single-proportion intervals is not a test" in r.stdout, (
        "the producer stopped warning that its own Wilson-overlap line is not "
        "a test of the difference, which is how that fallacy got into the "
        "record in the first place")


# ===========================================================================
# THE MUTATION HARNESS FOR THE BOARD-SCOPED SNAPSHOT. Appended 2026-11-23.
#
# ★ IT IS NAMED AND PARTIALLY EXERCISED HERE, NOT RUN TO COMPLETION, AND THE
# REASON IS A HARD CONSTRAINT RATHER THAN A CONVENIENCE: it drives `pytest`,
# and a test under `bench/tests/` runs INSIDE pytest, so executing it here
# would nest the runner inside itself. The same exemption already covers
# `prove_the_hidden_ruling_check_still_bites_2026-11-22.py` a few blocks above.
#
# WHAT IS CHECKED WITHOUT RUNNING IT: that it exists, that `--help` answers
# without performing the measurement (B212's class -- a flag that runs the work
# can edit the tree), and that it still declares a mutation for EACH branch of
# the predicate it guards. The last is the part that rots: a branch added to
# the subject with no mutation beside it is an untested branch, and the harness
# cannot notice its own omission.
#
# ITS RESULT WHEN RUN BY HAND, 2026-11-23: 4 of 4 reversions RED, baseline
# GREEN, restore sha256 f4628b6b7de711db MATCHES what was found.
# ===========================================================================


def test_the_snapshot_mutation_harness_answers_help_without_working():
    """`--help` must not run the measurement. B212's whole subject."""
    r = _run("the_board_scoped_snapshot_mutations_2026-11-23.py", "--help")
    assert r.returncode == 0, r.stdout[-600:] + r.stderr[-400:]
    #: THE REAL CONTRACT, and the first version of this assertion got it
    #: wrong. `answer_help` INTERCEPTS `--help` before the caller's parser, so
    #: the flags are deliberately NOT listed -- the fall-through that would
    #: list them could make `--help` do work in any script that acts before
    #: `parse_args`. What the help must do is describe the script and say that
    #: options exist, so a reader is not told there are none.
    assert "mutation" in r.stdout.lower() or "reversion" in r.stdout.lower(), (
        "the help text does not describe what the script does")
    assert "has its own options" in r.stdout, (
        "the help claims or implies the script takes no arguments, while it "
        "declares --quiet; that sentence is what made this test wrong first "
        "time round")
    #: DISCRIMINATE ON STRINGS ONLY `main()` PRINTS. The first version
    #: asserted the absence of the word "reversion", which appears in the
    #: DOCSTRING that `--help` is supposed to show -- so it accused correct
    #: behaviour. The measurement's own progress markers are the right test.
    for marker in ("baseline (unmutated)", "restored sha256",
                   "turned the guard RED"):
        assert marker not in r.stdout, (
            f"--help printed {marker!r}, so it ran the measurement instead of "
            f"describing it; a flag that works can edit the tree (B212)")


def test_the_snapshot_mutation_harness_covers_every_branch_it_guards():
    """A branch with no mutation beside it is an untested branch.

    Derived from the SUBJECT, not from a typed list: each anchor the harness
    declares must still be present in the file it mutates, and the count of
    anchors must not fall below the number of decision points the predicate
    has. An anchor that silently stops matching makes the harness SKIP, and a
    skip reads like a pass.
    """
    import importlib.util
    h = S / "the_board_scoped_snapshot_mutations_2026-11-23.py"
    assert h.is_file(), "the mutation harness is missing"
    spec = importlib.util.spec_from_file_location("_snapmut", h)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    subject = m.SUBJECT.read_text()
    assert m.SUBJECT.is_file(), f"the harness points at a missing subject: {m.SUBJECT}"
    missing = [label for label, find, _repl in m.MUTATIONS if find not in subject]
    assert not missing, (
        f"{len(missing)} mutation anchor(s) no longer match the subject, so the "
        f"harness would SKIP them and a skip reads like a pass: {missing}")
    assert len(m.MUTATIONS) >= 4, (
        f"the harness declares {len(m.MUTATIONS)} mutation(s); the liveness "
        f"predicate has 4 decision points (no pid, bad pid, dead pid, and "
        f"whether the snapshot is consulted at all)")


# ===========================================================================
# THE "SIGNIFICANT BATCH" PRODUCER. Appended 2026-11-23.
#
# The founder was asked how a significant batch should be defined and answered
# with a measurable proxy rather than a rule: that his verdict asks usually run
# at 10 to 12 items each, and that an average over the last month should be
# taken as the guide. This producer checks that recollection against the files.
#
# ★ NO VALUE IS PINNED. The corpus GROWS with every decisions file written, so
# pinning the measured median would turn a correct future measurement red --
# `feedback_a_guard_can_pin_the_defect_as_current_behaviour`. The STRUCTURE,
# the 2-route agreement and the stated limit are asserted instead.
#
# ONE CORPUS IS OUTSIDE THE REPOSITORY (his Desktop), so these assertions must
# hold on a machine that has only the versioned twins.
# ===========================================================================


def test_the_batch_definition_producer_reports_both_corpora_and_its_limit():
    r = _run("what_is_a_significant_batch_2026-11-23.py")
    assert r.returncode == 0, r.stdout[-900:] + r.stderr[-400:]
    assert "his recall : between 10 and 12 verdicts per ask" in r.stdout, (
        "the producer no longer states the claim it is checking, so a reader "
        "cannot tell what the figures are being compared against")
    assert "PER FILE" in r.stdout and "versioned twins" in r.stdout, (
        "a single-corpus answer: the whole point is that the count moves with "
        "the corpus chosen")
    #: THE LIMIT IS THE LOAD-BEARING PART. He offered a proxy; recording it as
    #: the definition of a work batch without that caveat is how a proxy
    #: becomes a fact.
    assert "DOES NOT SUPPORT" in r.stdout, (
        "the producer stopped stating what its figure does not support")
    assert "UNVERSIONED" in r.stdout, (
        "the spoken corpus is on the Desktop; a figure drawn from it is not "
        "reproducible from the repository and must say so")


def test_the_batch_definition_predicate_admits_a_markdown_heading():
    """★ THE DEFECT THIS PRODUCER HAD ON ITS FIRST RUN, pinned as a property.

    The first version anchored `DECISION` at line start with no prefix. The
    versioned twins write `## DECISION 1`, so it found 3 files where 20 exist
    and the SPOKEN corpus looked richer than the versioned one -- which nearly
    became a finding that his verdict record was unversioned. It was the
    instrument, not the record.

    Asserted by EXECUTING the compiled pattern, not by reading its source.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_sigbatch", S / "what_is_a_significant_batch_2026-11-23.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    assert m.DECISION.findall("## DECISION 1\n"), (
        "a markdown heading is not matched, so every versioned twin is invisible")
    assert m.DECISION.findall("DECISION 7\n"), "the plain spoken form broke"
    assert m.DECISION.findall("#### Decision 12\n"), "mixed case broke"
    #: AND IT MUST NOT OVER-MATCH: prose mentioning a decision is not a heading.
    assert not m.DECISION.findall("the DECISION 1 was recorded in prose\n"), (
        "the pattern matches mid-sentence prose, which would inflate every count")


# ===========================================================================
# THE PROBE THAT SETTLES WHAT THE 2 SEATS WEIGHED DIFFERENTLY. 2026-11-23.
#
# The joint round's seats disagreed on entry B209's repair. Driven, BOTH their
# scorers reproduce, and the disagreement is narrower than it looked: cc2's
# scenario S3 and fable's scenario R1 are the SAME scenario -- the overlap key
# failing when the matched process set is fully replaced between 2 consecutive
# polls. They agree on the fact and differ on its WEIGHT, which only a
# measurement of whether the scenario is REALISABLE can settle.
#
# ★ THE TEST BELOW RUNS IT WITH NOTHING MATCHING, ON PURPOSE. Running it while
# a suite is live would nest pytest inside pytest, which this project forbids.
# The property that CAN be checked without that is the fail-safe direction: with
# nothing matched it must report itself UNINFORMATIVE rather than reporting 0
# full replacements as though 0 were a finding. A probe that reads "0 of 0" and
# calls it evidence is the vacuity this whole session kept meeting.
# ===========================================================================


def test_the_replacement_probe_reports_no_bound_without_opportunities():
    """★ UPDATED 2026-11-23 BY THE BATCH-12 PANEL, AND THE OLD ASSERTION WAS
    TOO WEAK RATHER THAN WRONG.

    The first version only required the word UNINFORMATIVE when nothing
    matched. A seat showed the deeper defect: the probe reported a Wilson
    interval over a denominator of POLL PAIRS, and at 0 events that bound is
    exactly z^2/(n + z^2) -- strictly decreasing in n, where n is the poll
    count. So the bound was set by `--interval`, a free parameter. Measured on
    the same unchanging process over 20 s: 69 pairs give an upper bound of
    0.052737 at 0.25 s spacing against 9 pairs and 0.299145 at 2.0 s. A factor
    of 5.7 on identical evidence.

    The denominator is now OPPORTUNITIES -- pairs where the matched set
    actually changed with both sides non-empty -- and the binding requirement
    is that with 0 of them the probe prints NO BOUND AT ALL.
    """
    #: ★ THIS TEST WAS WRONG BY CONSTRUCTION AND THE BOARD CAUGHT IT. Its
    #: first version asserted that the probe reports UNIDENTIFIED, which holds
    #: only when NOTHING matches `pgrep -f "pytest.*bench/tests"`. Run on the
    #: commit board it matches THE BOARD ITSELF, plus any sibling pytest, so
    #: opportunities were non-zero and a bound was correctly printed. The test
    #: failed on a 47 min 55 s board for a reason that was its own.
    #:
    #: `feedback_a_watcher_is_part_of_what_it_watches` names exactly this. The
    #: repair is to assert the INVARIANT rather than the ambient state: a bound
    #: may appear ONLY when opportunities are non-zero, whatever happens to be
    #: running. That holds inside a board, outside one, and on an idle machine.
    r = _run("does_the_matched_set_ever_fully_replace_2026-11-23.py",
             "--seconds", "4", "--interval", "1")
    assert r.returncode == 0, r.stdout[-700:] + r.stderr[-400:]
    out = r.stdout
    import re as _re
    m = _re.search(r"FULL REPLACEMENTS[^:]*:\s*(\d+)", out)
    assert m, f"the probe no longer reports a full-replacement count:\n{out[-500:]}"
    opp = _re.search(r"opportunit[^\n]*?(\d+)", out, _re.I)
    reported_bound = "Wilson 95%" in out
    if "UNIDENTIFIED" in out or "NO BOUND IS REPORTED" in out:
        assert not reported_bound, (
            "the probe said the rate is unidentified AND printed a bound; those "
            "cannot both be true")
    else:
        #: a bound appeared, so the probe must have had opportunities to justify
        #: it -- the whole point of the batch-12 repair.
        assert opp is not None, (
            "a bound was printed with no opportunity count reported, which is "
            "the defect the panel found: a Wilson width set by the polling rate")
    #: AND THE AMBIENT-INDEPENDENT HALF, driven directly rather than observed:
    #: 0 opportunities must be reported for an unchanging set however many
    #: polls are taken.
    import importlib.util, sys as _sys
    spec = importlib.util.spec_from_file_location(
        "_rp2", S / "does_the_matched_set_ever_fully_replace_2026-11-23.py")
    mod = importlib.util.module_from_spec(spec)
    _sys.modules["_rp2"] = mod
    spec.loader.exec_module(mod)
    assert mod.classify([{1}] * 20)[4] == 0, (
        "an unchanging set reported a non-zero opportunity count, so the "
        "denominator is still the polling rate")
    assert mod.classify([{1, 2}, {3, 4}])[4] == 1, (
        "a genuine full replacement is no longer counted as an opportunity")


def test_the_replacement_probe_reads_the_gates_own_patterns():
    """It must not spell the matcher itself -- that would measure the probe.

    Asserted by CALLING the accessor, so a hardcoded tuple would not pass.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_repl", S / "does_the_matched_set_ever_fully_replace_2026-11-23.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    pats = m.gate_patterns()
    assert pats, "no patterns returned"
    gate = m.GATE.read_text()
    for pat in pats:
        assert pat in gate, (
            f"pattern {pat!r} is not in {m.GATE.name}, so the probe is "
            f"measuring a population the gate does not watch")


def test_the_replacement_probe_classifies_all_three_pair_kinds():
    """The classifier, driven on constructed sequences rather than described."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_repl2", S / "does_the_matched_set_ever_fully_replace_2026-11-23.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    #: ★ 5 FIELDS SINCE THE BATCH-12 PANEL: the last is OPPORTUNITIES, the
    #: pairs in which the matched set actually changed with both sides
    #: non-empty -- the only occasions on which a full replacement was a
    #: possible outcome, and therefore the only defensible denominator.
    #: a FULL replacement: both non-empty, disjoint -- the disputed scenario
    assert m.classify([{1, 2}, {3, 4}]) == (1, 0, 0, 1, 1)
    #: identical: a pair, but NO opportunity -- nothing could have happened
    assert m.classify([{1}, {1}]) == (0, 1, 0, 1, 0)
    #: partial overlap is not a full replacement, but IS an opportunity
    assert m.classify([{1, 2}, {2, 3}]) == (0, 0, 1, 1, 1)
    #: an empty poll either side cannot contain the event, so no opportunity
    assert m.classify([{1}, set()]) == (0, 0, 1, 1, 0)
    #: two empties contribute no pair at all
    assert m.classify([set(), set()]) == (0, 0, 0, 0, 0)
    #: ★ THE PROPERTY THE WHOLE REPAIR EXISTS FOR: the opportunity count must
    #: NOT move with the polling rate. 10x the polls of an unchanging set is
    #: 10x the pairs and still 0 opportunities.
    assert m.classify([{1}] * 15)[4] == 0
    assert m.classify([{1}] * 150)[4] == 0
    assert m.classify([{1}] * 150)[3] > m.classify([{1}] * 15)[3], (
        "the pair count should grow with the polling rate -- that is exactly "
        "why it is the wrong denominator")


class TestTheDifferentialFalsifierHarness:
    """★ ADOPTED FROM THE 2026-11-23 JOINT PANEL AFTER BEING TESTED IN BOTH
    DIRECTIONS, which is the founder's standing condition: a panel's proposal is
    a hypothesis, not a fix.

    IT ANSWERS A FAILURE THIS SESSION MET TWICE. A falsifier was run against a
    tree where the defect had ALREADY been repaired, so nothing could move, and
    the clean result was one sentence away from being recorded as a refutation
    of a correct diagnosis. "Assert the precondition" cannot be the rule,
    because it requires having already named the way the run could be vacuous.
    The differential rule needs no foresight: run the falsifier with the defect
    PRESENT and with it ABSENT, and require the 2 verdicts to DISAGREE.
    Agreement in either direction is vacuity.

    VALIDATED AGAINST KNOWN ANSWERS before adoption, not merely executed:
    pointed at the real guard for the board-scoped snapshot it reported
    DISCRIMINATES (3 failed with the defect, 21 passed without); pointed at an
    unrelated guard it reported VACUOUS and exited 1, and said in as many words
    that such a run must never auto-confirm and never be read as a refutation.
    The target was restored byte-for-byte in both arms.

    THE FALSIFIERS BELOW ARE NOT pytest, DELIBERATELY. A test under
    `bench/tests/` already runs inside pytest, so driving pytest as the
    falsifier would nest the runner. A `python3 -c` probe exercises the same 2
    code paths without that.
    """

    HARNESS = "a_falsifier_must_disagree_with_itself_2026-11-23.py"

    def _case(self, tmp_path, falsifier_py, good, bad):
        target = tmp_path / "subject.py"
        target.write_text(good)
        defect = tmp_path / "subject_defective.py"
        defect.write_text(bad)
        probe = tmp_path / "probe.py"
        probe.write_text(falsifier_py)
        r = subprocess.run(
            [sys.executable, str(S / self.HARNESS),
             "--target", str(target), "--defect-file", str(defect),
             "--cwd", str(tmp_path),
             "--", sys.executable, str(probe), str(target)],
            capture_output=True, text=True, timeout=600, cwd=REPO)
        return r, target, good

    def test_it_reports_a_discriminating_falsifier(self, tmp_path):
        """A probe that reads the subject must see the difference."""
        probe = ("import sys, pathlib\n"
                 "src = pathlib.Path(sys.argv[1]).read_text()\n"
                 "assert 'GOOD' in src, 'the defect is present'\n")
        r, target, good = self._case(
            tmp_path, probe, "MARKER = 'GOOD'\n", "MARKER = 'BAD'\n")
        assert "DISCRIMINATES" in r.stdout, r.stdout[-700:]
        assert r.returncode == 0, f"exit {r.returncode}: {r.stdout[-400:]}"
        assert target.read_text() == good, "the target was not restored"

    def test_it_reports_a_vacuous_falsifier(self, tmp_path):
        """★ THE DIRECTION THAT MATTERS. A probe blind to the defect passes in
        BOTH arms, and must be refused rather than read either way."""
        probe = "import sys\nassert True\n"
        r, target, good = self._case(
            tmp_path, probe, "MARKER = 'GOOD'\n", "MARKER = 'BAD'\n")
        assert "VACUOUS" in r.stdout, r.stdout[-700:]
        assert r.returncode != 0, (
            "a vacuous falsifier exited 0, so a caller gating on the exit code "
            "would treat 'cannot see the defect' as success")
        assert target.read_text() == good, "the target was not restored"

    def test_it_restores_the_target_even_when_the_falsifier_dies(self, tmp_path):
        """A harness that leaves a mutation behind is worse than none. This
        session found exactly that: a reverted repair sitting uncommitted."""
        probe = "import sys\nraise SystemExit(3)\n"
        r, target, good = self._case(
            tmp_path, probe, "MARKER = 'GOOD'\n", "MARKER = 'BAD'\n")
        assert target.read_text() == good, (
            "the target was left mutated after the falsifier exited non-zero")
        assert "restored byte-for-byte : True" in r.stdout, r.stdout[-500:]


# ===========================================================================
# THE 2 FALSIFIERS THE BATCH-12 PANEL DELIVERED, ADOPTED AFTER BEING RUN.
# Appended 2026-11-23.
#
# Each targets a defect in work I had just built, and each was executed before
# the fix it justifies was accepted:
#
#   * `the_insert_must_carry_the_file_2026-11-23.py` -- my widening of the
#     dash-m predicate asked `inserts` and `uses_file` SEPARATELY of the same
#     node bag, so a CONSTANT-path insert with an unrelated file-derived name
#     beside it was credited. Reproduced in a temporary directory: the
#     predicate said True and the script WROTE A FILE when run as
#     `python3 -m evil --help`.
#   * `the_replacement_denominator_must_be_opportunities_2026-11-23.py` -- my
#     replacement probe reported a Wilson bound over POLL PAIRS, which at 0
#     events is exactly z^2/(n + z^2) and therefore set by `--interval`.
#
# BOTH ARE SELF-CONTAINED: they import the real modules and spawn no pytest, so
# the board can run them.
# ===========================================================================


def test_the_insert_falsifier_upholds_the_joined_condition():
    r = _run("the_insert_must_carry_the_file_2026-11-23.py")
    assert r.returncode == 0, r.stdout[-900:] + r.stderr[-400:]
    assert r.stdout.strip(), "the falsifier printed nothing"


def test_the_denominator_falsifier_shows_rate_invariance():
    """The property that matters: the opportunity count must not move with the
    polling rate, while a real replacement is still counted."""
    r = _run("the_replacement_denominator_must_be_opportunities_2026-11-23.py")
    assert r.returncode == 0, r.stdout[-900:] + r.stderr[-400:]
    assert "invariant to the polling rate" in r.stdout, r.stdout[-700:]
    assert "Upheld in both directions" in r.stdout, (
        "the falsifier no longer reports the anti-vacuity arm, so a fix that "
        "returned 0 opportunities for everything would pass it")
