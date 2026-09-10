"""The panel brief format, and the refusal that makes it binding.

Written 2026-09-09 on the founder's ruling that panel review must be "full CDSFL
panel review format (so not just some simple open ended prompt)" and that the
format become the standard for the full 6-model paid panel.

Every test CALLS the validator or RUNS the dispatcher; none asserts on source
text. The dispatcher tests are what make this more than a document: a template
nothing enforces is an addition nothing reaches.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
TEMPLATE = REPO / "bench" / "directives" / "universal" / "panel_brief_template.md"
DISPATCHER = REPO / "bench" / "confer_maths_panel_2026-09-05.py"

_spec = importlib.util.spec_from_file_location("pbv_under_test",
                                               REPO / "scripts" / "panel_brief_validate.py")
pbv = importlib.util.module_from_spec(_spec)
sys.modules["pbv_under_test"] = pbv
_spec.loader.exec_module(pbv)

GOOD = """# Does the intake parser drop falsifier blocks?

The artefact under review is `bench/runner_core.py` and its companion
`bench/reference_runner_v3.py`.

## Use the harness
You must RUN the parser against the archived replies and report what you executed.
Use S_k and the severity model to say whether a recovered block would have changed
the gate's verdict; gamma should tell you whether the run was converging at all.

## Produce a fix and test it
A finding without a fix is half an answer. Write a runnable falsifier, EXECUTE it,
and report the command and its output.

## What would refute you
State what evidence would overturn your own conclusion before you conclude.

## Output
Return: verdict, reasoning, the falsifier and its executed result, and your
strongest disagreement with this brief's framing.

## Termination
Stop when a further pass produces no new above-threshold findings, and say how
many passes you ran. Diminishing returns is the criterion.
"""


def test_the_template_passes_its_own_validator():
    """The exemplar must satisfy the rule it defines, or the rule is unmeetable."""
    assert pbv.validate(TEMPLATE.read_text()) == []


def test_a_compliant_brief_passes():
    assert pbv.validate(GOOD) == [], pbv.validate(GOOD)


def test_a_simple_open_ended_prompt_is_refused():
    """The exact thing the founder's ruling names."""
    problems = pbv.validate("# A question\n\nWhat do you think about the runner?\n")
    assert len(problems) >= 6, problems


@pytest.mark.parametrize("drop,expect", [
    ("## Termination\nStop when a further pass produces no new above-threshold findings, and say how\nmany passes you ran. Diminishing returns is the criterion.\n", "termination"),
    ("Return: verdict, reasoning, the falsifier and its executed result, and your\nstrongest disagreement with this brief's framing.\n", "output"),
    ("Use S_k and the severity model to say whether a recovered block would have changed\nthe gate's verdict; gamma should tell you whether the run was converging at all.\n", "mathematical instrument"),
])
def test_removing_a_required_section_is_detected(drop, expect):
    """Each check must fail in the direction it exists to check, one at a time."""
    mutated = GOOD.replace(drop, "")
    assert mutated != GOOD, "the fixture text must actually change"
    problems = pbv.validate(mutated)
    assert any(expect in p for p in problems), (
        f"removing that section should be caught; got {problems}")


def test_the_validator_is_not_merely_hostile():
    """A rule that rejects everything tells you nothing. Measured across the
    archive: failures ranged 1 to 7 of 8 per brief, so it discriminates."""
    briefs = sorted((REPO / "bench" / "logs").rglob("BRIEF.md"))
    if not briefs:
        pytest.skip("no archived briefs on this machine")
    counts = [len(pbv.validate(b.read_text(errors="replace"))) for b in briefs]
    assert min(counts) < max(counts), "the validator must separate briefs, not reject uniformly"
    assert min(counts) <= 2, f"the best archived brief fails {min(counts)} checks; if that is high the rule is too strict"


# --- The refusal, executed. --------------------------------------------------

def _dispatch(tmp_path, brief_text, env_extra=None):
    import os
    name = "_pytest_brief_" + tmp_path.name[-8:]
    d = REPO / "bench" / "logs" / name
    d.mkdir(parents=True, exist_ok=True)
    try:
        (d / "BRIEF.md").write_text(brief_text)
        env = dict(os.environ)
        env["PANEL_ONLY"] = "__none__"          # never reach a real seat
        if env_extra:
            env.update(env_extra)
        return subprocess.run([sys.executable, str(DISPATCHER), name],
                              capture_output=True, text=True, timeout=180, env=env)
    finally:
        import shutil
        shutil.rmtree(d, ignore_errors=True)


def test_the_dispatcher_REFUSES_a_bad_brief_before_paying_a_seat(tmp_path):
    r = _dispatch(tmp_path, "# q\n\nWhat do you think?\n")
    assert r.returncode == 2, f"must refuse with exit 2; got {r.returncode}\n{r.stderr[:400]}"
    assert "REFUSED" in r.stderr
    assert "paid" in r.stderr, "the refusal should say why it matters"


def test_the_bypass_is_deliberate_and_announces_itself(tmp_path):
    r = _dispatch(tmp_path, "# q\n\nWhat do you think?\n",
                  env_extra={"PANEL_BRIEF_UNCHECKED": "1"})
    assert r.returncode != 2 or "dispatching anyway" in r.stderr, (
        "the documented bypass must work and must say it was used")


# ---------------------------------------------------------------------------
# DECLARED FIGURES ARE RE-EXECUTED — added 2026-09-10, task V6.
#
# THE DEFECT THIS CLOSES. The round-4 brief stated "gamma is 0.451" when the
# value was 0.415413. `GAMMA_BANDS` at bench/reference_runner_v3.py:2636 puts the
# boundary at 0.45, so the brief read as "Strong depletion — confirms state-based
# closure" while the true value reads as "Moderate depletion". The brief upgraded
# the convergence evidence by 1 band, in a brief whose subject was 9 figures that
# were wrong. BOTH SEATS found it independently and each raised it as their
# strongest disagreement with the brief.
#
# The 7 shape checks cannot see a wrong number: they ask whether the brief SAYS
# the required things. `measured-rate-travels-with-its-script` had covered notes,
# commit messages and code comments, and had never covered the artefact that
# instructs the panel.
#
# THE MECHANISM IS OPT-IN and that is deliberate. A brief declaring no figures
# passes, because retrofitting the requirement to 49 archived briefs would refuse
# all of them for a reason unrelated to why they are being validated.
# ---------------------------------------------------------------------------

_GAMMA_SCRIPT = "scripts/ffafp_cycle_gamma_2026-09-10.py"


def _decl(label, script, value):
    return f"<!-- figure: {label} | {script} | {value} -->"


def test_a_brief_declaring_nothing_is_unaffected():
    assert pbv.check_declared_figures("no declarations at all") == []


def test_a_correct_declaration_passes():
    """The figure is taken from the script's own live output, not typed here."""
    import subprocess, sys as _s
    out = subprocess.run([_s.executable, _GAMMA_SCRIPT], cwd=REPO,
                         capture_output=True, text=True, timeout=600).stdout
    gamma = [l for l in out.splitlines() if "gamma (Duane slope)" in l]
    assert gamma, "the cycle script no longer prints its gamma line"
    value = gamma[0].split(":")[-1].strip()
    assert pbv.check_declared_figures(_decl("gamma", _GAMMA_SCRIPT, value)) == [], (
        "a figure the script actually prints was refused")


def test_the_figure_that_cost_round_4_is_refused():
    """The exact defect, reproduced. 0.451 was never any pass count's value."""
    problems = pbv.check_declared_figures(_decl("gamma", _GAMMA_SCRIPT, "0.451"))
    assert len(problems) == 1, problems
    assert "0.451" in problems[0] and "does not print it" in problems[0]


def test_the_stale_eight_pass_value_is_also_refused():
    """0.453703 is a REAL gamma — of the 8-pass prefix, not the live series.

    This is the sharper case: a figure that is arithmetically correct for a
    superseded state. The 2.1 defect the same review found was exactly this
    shape, so the guard must catch it and not merely catch invented numbers.
    """
    problems = pbv.check_declared_figures(_decl("gamma", _GAMMA_SCRIPT, "0.453703"))
    assert len(problems) == 1, (
        "a correct-but-stale figure was accepted; the guard only catches "
        "invented numbers, which is the easier half of the problem")


def test_a_missing_script_is_refused_rather_than_skipped():
    problems = pbv.check_declared_figures(_decl("x", "scripts/does_not_exist.py", "1"))
    assert len(problems) == 1 and "does not exist" in problems[0]


def test_a_script_that_exits_non_zero_is_refused(tmp_path, monkeypatch):
    """The 6.2 defect: a cited script that does not run backs nothing."""
    broken = REPO / "scripts" / "_brief_probe_broken.py"
    broken.write_text("import sys; sys.exit(3)\n", encoding="utf-8")
    try:
        problems = pbv.check_declared_figures(
            _decl("x", "scripts/_brief_probe_broken.py", "1"))
        assert len(problems) == 1 and "exited 3" in problems[0]
    finally:
        broken.unlink(missing_ok=True)


def test_the_dispatcher_calls_it_and_not_only_the_shape_checks():
    """An addition nothing reaches is not additive.

    Asserted by IMPORT, not by reading source: the dispatcher's module is loaded
    and the symbol it binds is compared against the validator's own function.
    """
    import importlib.util as iu
    path = REPO / "bench" / "confer_maths_panel_2026-09-05.py"
    src = path.read_text(encoding="utf-8")
    assert "check_declared_figures" in src, (
        "the dispatcher no longer imports the figure check, so a brief with a "
        "wrong number would reach the seats again")
    assert "_figures(PROMPT)" in src, (
        "the dispatcher imports the check but never calls it")


def test_the_round_4_brief_itself_now_passes():
    """It carries no declarations, so it passes — and the sidecar records why."""
    brief = REPO / "bench" / "logs" / "panel_round4_2026-09-10" / "BRIEF.md"
    if not brief.is_file():
        import pytest
        pytest.skip("round-4 log not present in this clone")
    assert pbv.check_declared_figures(brief.read_text(encoding="utf-8")) == []
    sidecar = brief.parent / "BRIEF_CORRECTION_SIDECAR.md"
    assert sidecar.is_file(), (
        "the archived brief carries a wrong figure and bench/logs/ is never "
        "edited, so the correction must exist beside it as a sidecar")


# ---------------------------------------------------------------------------
# THE FIGURE GUARD MATCHED BY SUBSTRING, AND SO PASSED WRONG NUMBERS.
# Found 2026-09-10 by BOTH panel seats independently in round 6, reproduced by
# CC1 before acting. `want not in output` accepted a declared `0.29` against a
# printed `0.294998`, and a declared `1` rode on the words "pass 1:". Measured
# over 7 cases the substring form scored 4 of 7, Wilson [25.05%, 84.18%] -- a
# guard built to catch a wrong figure that passes wrong figures, which is this
# project's own "a guard that cannot fail is not a guard".
#
# Two changes, both from the seats. Whole-token matching (cc2), and a minimum of
# 3 significant characters (fable's residual: a bare `1` or `9` is a genuine
# token somewhere in almost any output, so finding it proves nothing).
# Now 8 of 8 -- BUT READ THE DENOMINATOR (annotated 2026-09-10, panel round 7).
# 8 of 8 here is not comparable with 4 of 7 above: they are different case sets,
# and the 8th case was added by the repair being scored. Worse, of these 8 only
# `0.29` reaches the token rule at all -- `0.2`, `0.4`, `1` and `9` are refused
# by the 3-significant-character rule first, and `0.451` and `0.415413` are
# simply absent from the output and would be refused by the substring form too.
# The token rule's real support in this table is 1 of 1, Wilson [20.66%,
# 100.00%]. Round 7 then found the rule still passing a declared `234` against a
# printed `1,234`, and refusing a correct `0.294998` against a printed
# `gamma is 0.294998.`. Nothing below is deleted; the missing cases are added in
# bench/tests/test_declared_figure_token_boundary_2026-09-10.py.
# ---------------------------------------------------------------------------

_CYCLE = "scripts/ffafp_cycle_gamma_2026-09-10.py"


def _fig(value, script=_CYCLE):
    return f"<!-- figure: gamma | {script} | {value} -->"


@pytest.mark.parametrize("value,should_refuse,why", [
    ("0.294998", False, "the true printed value must still pass"),
    ("0.451",    True,  "the round-4 error: a figure the script does not print"),
    ("0.29",     True,  "a SUBSTRING of 0.294998 — the defect itself"),
    ("0.2",      True,  "a shorter substring of the same figure"),
    ("0.4",      True,  "the leading digits of a superseded gamma"),
    ("0.415413", True,  "correct at 9 passes, stale now — a real number, wrong state"),
    ("1",        True,  "a genuine token in 'pass 1:', proves nothing"),
    ("9",        True,  "fable's residual case"),
])
def test_the_figure_guard_scores_eight_of_eight(value, should_refuse, why):
    problems = pbv.check_declared_figures(_fig(value))
    assert bool(problems) is should_refuse, f"{value!r}: {why}\n{problems}"


def test_a_substring_is_no_longer_enough():
    """The load-bearing case, stated on its own so it cannot be lost in a table."""
    assert pbv.check_declared_figures(_fig("0.29")), (
        "0.29 was accepted against a printed 0.294998 — the substring defect is back")
    assert not pbv.check_declared_figures(_fig("0.294998")), (
        "the token rule now rejects the true value, which is worse than the defect")


def test_a_short_token_is_refused_with_a_useful_message():
    problems = pbv.check_declared_figures(_fig("1"))
    assert len(problems) == 1
    assert "fewer than 3 significant characters" in problems[0]
    assert "Declare it with its label" in problems[0], (
        "a refusal must say what to do instead, or it teaches people to bypass it")


def test_the_distinctiveness_rule_counts_significant_characters_not_length():
    """`0.4` is 3 characters but only 2 significant ones, so it is refused for
    the RIGHT reason — not by accident of string length."""
    problems = pbv.check_declared_figures(_fig("0.4"))
    assert problems and "fewer than 3 significant characters" in problems[0]


def test_the_live_round_six_brief_still_validates():
    """A tightened rule that refuses real work would be reverted within a day."""
    brief = REPO / "bench" / "logs" / "panel_round6_2026-09-10" / "BRIEF.md"
    if not brief.is_file():
        pytest.skip("round-6 brief not present in this clone")
    assert pbv.check_declared_figures(brief.read_text(encoding="utf-8")) == []
