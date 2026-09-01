"""Target-type detection in the harness core, and S_k's NO_SCORE outcome.

WHAT THIS GUARDS (A1 + A2, prose adaptation, 2026-08-01)
--------------------------------------------------------
The instrument was built when every target was a Python module. Targets are now
prose documents carrying claims plus fenced Python listings, and every mechanism
that treats the whole target as compilable source fails on them SILENTLY.

Measured, by execution, on the 2026-08-01 zero-plant control:

  * The S_k hard gates ran ``ast.parse`` on the whole markdown document. Prose is
    not parseable Python, so A = g1*g2 = 0 and EVERY fix was rejected — 38
    findings, 29 of them by the AST gate.
  * Repairing that so A=1 exposed the worse half: the EFFECT gates CANNOT FAIL on
    prose. ruff error-recovers over markdown and reported ~2752 phantom
    diagnostics as the BASELINE, so its delta measures how much English the fix
    added. bandit cannot parse the file, returns an empty result set, and
    therefore reports "0 HIGH / 0 MEDIUM" forever — at weight 2.0, the heaviest
    in the set. The regression gate is permanently unavailable, because prose
    targets live outside the repository and no prose config sets ``test_cmd``.
  * End to end: a fix injecting ``subprocess.call("rm -rf ...", shell=True)`` into
    a fenced listing scored sk=1.0000 ADMISSIBLE. A correct prose fix scored
    0.6667. The ranking was INVERTED and nothing was ever rejected.

The fix is not to tune those gates. It is to establish, in the harness core, what
kind of thing the target is, and to make S_k decline to speak about a substrate
it was not defined over.

WHY ENFORCEMENT IS NOT A CONFIG FLAG
------------------------------------
The launcher has silently dropped config keys six times, twenty of them latent as
of the 2026-08-01 sweep. A safety property whose enforcement depends on a key
surviving two ingestion paths is not enforced. The config MAY declare
``target_kind``; the harness reads the path and the bytes and DECIDES, and a
declaration that disagrees stops the run.

WHAT MUST NOT BREAK
-------------------
Exp 48 (chemistry) and Exp 49 (engineering) are maths-in-prose targets that
ALREADY converged, at rounds 5 and 6, with 31/32 and 31/31 criticals
falsifier-CONFIRMED and closed — while S_k rejected 100% of fixes. Findings are
resolved by FALSIFIERS, not by S_k. Nothing here touches that path.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_root = Path(__file__).resolve().parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from bench.reference_runner_v3 import (  # noqa: E402
    RunnerConfig,
    SK_ADMISSIBLE,
    SK_NO_SCORE,
    TARGET_KIND_PROSE,
    TARGET_KIND_PYTHON,
    TargetKindMismatch,
    apply_sk_to_rk,
    compute_rk,
    compute_sk,
    detect_target_kind,
    resolve_target_kind,
)

# A prose target of the shape the remaining arc actually uses: claims in
# English, plus a fenced Python listing. Includes the table of byte offsets
# whose leading zeros made ast.parse raise on the real control document.
PROSE_TARGET = '''# SW-21 Reference — clearance and offsets

The nominal bearing clearance is 0.29 mm at 20 degrees Celsius.

| Field | Offset |
|-------|--------|
| head  | 032    |
| body  | 0100   |

The offset table is octal, retained from the 1987 specification.

```python
def clearance_mm(temp_c: float) -> float:
    return 0.29 + 0.0004 * (temp_c - 20.0)
```

Values above 80 degrees Celsius are extrapolated and were never measured.
'''

PY_TARGET = '''"""A small module."""


def clearance_mm(temp_c: float) -> float:
    return 0.29 + 0.0004 * (temp_c - 20.0)
'''

# The measured exploit: a shell-injection call smuggled into a fenced listing.
# Under the repaired hard gates (A=1) and the prose-blind effect gates this
# scored sk=1.0000 ADMISSIBLE.
SHELL_INJECTION_FIX = '''<<<< SEARCH
def clearance_mm(temp_c: float) -> float:
    return 0.29 + 0.0004 * (temp_c - 20.0)
====
import subprocess


def clearance_mm(temp_c: float) -> float:
    subprocess.call("rm -rf /tmp/cdsfl_targets", shell=True)
    return 0.29 + 0.0004 * (temp_c - 20.0)
>>>> REPLACE
'''

CORRECT_PROSE_FIX = '''<<<< SEARCH
The nominal bearing clearance is 0.29 mm at 20 degrees Celsius.
====
The nominal bearing clearance is 0.31 mm at 20 degrees Celsius.
>>>> REPLACE
'''


class TestClassificationFromPath:
    @pytest.mark.parametrize("name", ["m.py", "pkg/m.py", "stubs/m.pyi"])
    def test_python_suffixes_are_python(self, name):
        kind, _ = detect_target_kind(name, PY_TARGET)
        assert kind == TARGET_KIND_PYTHON

    @pytest.mark.parametrize(
        "name",
        ["ref.md", "ref.markdown", "notes.txt", "notes.text", "spec.rst", "log.org"])
    def test_prose_suffixes_are_prose(self, name):
        kind, _ = detect_target_kind(name, PROSE_TARGET)
        assert kind == TARGET_KIND_PROSE

    def test_the_real_control_document_is_prose(self):
        kind, reason = detect_target_kind(
            "/Users/x/CDSFL_review_targets/SW-21-REF-04.md", PROSE_TARGET)
        assert kind == TARGET_KIND_PROSE
        assert "suffix .md" in reason


class TestClassificationFromContent:
    """Path alone is not enough — the bytes get a vote, in the safe direction."""

    def test_prose_under_a_python_extension_is_prose(self):
        """A markdown document named .py. Extension lies; content does not."""
        kind, reason = detect_target_kind("target.py", PROSE_TARGET)
        assert kind == TARGET_KIND_PROSE
        assert "does not parse as Python" in reason

    def test_a_python_module_with_a_syntax_error_is_still_a_python_module(self):
        """A broken .py file must not be demoted to prose — it has no fences,
        so nothing suggests it is a document."""
        kind, _ = detect_target_kind("m.py", "def f(:\n    pass\n")
        assert kind == TARGET_KIND_PYTHON

    def test_a_docstring_containing_a_fence_is_still_a_python_module(self):
        """Fences alone must not demote a .py file that parses. Runner source
        is full of them; demoting on fences alone would disable S_k on every
        Python target this project reviews."""
        src = 'def f():\n    """Example:\n\n    ```python\n    f()\n    ```\n    """\n'
        kind, _ = detect_target_kind("m.py", src)
        assert kind == TARGET_KIND_PYTHON

    def test_no_extension_falls_to_content(self):
        assert detect_target_kind("TARGET", PY_TARGET)[0] == TARGET_KIND_PYTHON
        assert detect_target_kind("TARGET", PROSE_TARGET)[0] == TARGET_KIND_PROSE

    def test_python_comments_do_not_read_as_markdown_headings(self):
        """`# Heading` is a heading in markdown and a comment in Python. A
        naive heading heuristic would classify every Python module as prose and
        silently disable S_k across the whole code arc."""
        src = "# Heading\n# Another\nimport os\n\n\ndef f():\n    return os\n"
        assert detect_target_kind("m.py", src)[0] == TARGET_KIND_PYTHON
        assert detect_target_kind("noext", src)[0] == TARGET_KIND_PYTHON


class TestAmbiguityResolvesToProse:
    """The asymmetry IS the safety argument.

    Misreading prose as Python inverted the fix ranking and admitted a
    shell-injection fix at sk=1.0. Misreading Python as prose only forgoes
    scoring. Every ambiguous case must land on the second."""

    def test_unknown_extension_without_content_is_prose(self):
        kind, reason = detect_target_kind("target.dat")
        assert kind == TARGET_KIND_PROSE
        assert "no content available" in reason

    def test_empty_target_is_prose(self):
        """An empty string is valid, parseable Python. It must not earn the
        scoreable classification by vacuity."""
        assert detect_target_kind("target.dat", "")[0] == TARGET_KIND_PROSE
        assert detect_target_kind("target.dat", "   \n\n")[0] == TARGET_KIND_PROSE

    def test_a_short_markdown_file_that_parses_as_python_is_still_prose(self):
        """`Hello` is a valid Python expression statement AND a one-line
        document. The .md suffix decides, and it decides prose."""
        assert detect_target_kind("note.md", "Hello\n")[0] == TARGET_KIND_PROSE

    def test_unknown_extension_with_fences_is_prose(self):
        body = "```python\nx = 1\n```\n"
        assert detect_target_kind("t.dat", body)[0] == TARGET_KIND_PROSE


class TestTheHarnessDecidesTheConfigOnlyDeclares:
    def test_an_agreeing_declaration_is_accepted(self):
        kind, _ = resolve_target_kind(
            "ref.md", PROSE_TARGET, declared=TARGET_KIND_PROSE)
        assert kind == TARGET_KIND_PROSE

    def test_a_disagreeing_declaration_is_an_error(self):
        with pytest.raises(TargetKindMismatch) as exc:
            resolve_target_kind("ref.md", PROSE_TARGET,
                                declared=TARGET_KIND_PYTHON)
        assert "REFUSING TO START" in str(exc.value)

    def test_a_declaration_cannot_redirect_the_classification(self):
        """The failure mode this forecloses: a config declaring `python_module`
        on a prose target and getting scored as one."""
        with pytest.raises(TargetKindMismatch):
            resolve_target_kind("SW-21-REF-04.md", PROSE_TARGET,
                                declared="python_module")

    def test_an_unknown_declaration_is_an_error(self):
        with pytest.raises(TargetKindMismatch):
            resolve_target_kind("ref.md", PROSE_TARGET, declared="markdown")

    def test_no_declaration_is_the_normal_case(self):
        assert RunnerConfig().target_kind == ""
        assert resolve_target_kind("ref.md", PROSE_TARGET, declared=None)[0] \
            == TARGET_KIND_PROSE
        assert resolve_target_kind("ref.md", PROSE_TARGET, declared="")[0] \
            == TARGET_KIND_PROSE


class TestSkReturnsNoScoreOnProse:
    def test_a_correct_prose_fix_is_not_scored(self):
        r = compute_sk(CORRECT_PROSE_FIX, PROSE_TARGET, "SW-21-REF-04.md")
        assert r.tristate == SK_NO_SCORE
        assert r.tristate not in ("ADMISSIBLE", "REJECTED")

    def test_the_measured_shell_injection_fix_is_not_admitted(self):
        """THE MEASUREMENT THIS EXISTS FOR. With the hard gates repaired, this
        exact fix scored sk=1.0000 ADMISSIBLE against 0.6667 for the correct
        prose fix — the ranking inverted, nothing ever rejected."""
        r = compute_sk(SHELL_INJECTION_FIX, PROSE_TARGET, "SW-21-REF-04.md")
        assert r.tristate == SK_NO_SCORE, (
            "a shell-injection fix inside a fenced listing must never be "
            "ADMISSIBLE on a prose target")
        assert r.sk == 0.0

    def test_neither_fix_outranks_the_other(self):
        """Not merely 'both unscored' — the two must be INDISTINGUISHABLE by
        score, because the ranking is what inverted."""
        good = compute_sk(CORRECT_PROSE_FIX, PROSE_TARGET, "SW-21-REF-04.md")
        bad = compute_sk(SHELL_INJECTION_FIX, PROSE_TARGET, "SW-21-REF-04.md")
        assert good.sk == bad.sk == 0.0
        assert good.tristate == bad.tristate == SK_NO_SCORE

    def test_no_gate_runs_at_all(self):
        """NO_SCORE means the gates never spoke, not that they were silent.
        A gate_details dict carrying g1/e3/e4 entries would mean ruff and
        bandit ran on markdown again."""
        r = compute_sk(CORRECT_PROSE_FIX, PROSE_TARGET, "SW-21-REF-04.md")
        for gate in ("g1_ast", "g2_compile", "e2_regression", "e3_ruff",
                     "e4_bandit"):
            assert gate not in r.gate_details
        assert r.gate_details["target_kind"] == TARGET_KIND_PROSE

    def test_no_score_is_declared_neither_admitted_nor_rejected(self):
        r = compute_sk(CORRECT_PROSE_FIX, PROSE_TARGET, "SW-21-REF-04.md")
        assert "neither admitted nor rejected" in r.gate_details["reason"]

    def test_a_python_target_is_still_scored(self):
        """The regression that would matter most: A2 must not disable S_k on
        the code targets it was built for."""
        fix = ('<<<< SEARCH\n    return 0.29 + 0.0004 * (temp_c - 20.0)\n'
               '====\n    return 0.31 + 0.0004 * (temp_c - 20.0)\n'
               '>>>> REPLACE\n')
        r = compute_sk(fix, PY_TARGET, "m.py",
                       baseline={"ruff_violations": 0,
                                 "bandit_findings": {"high": 0, "medium": 0}})
        assert r.tristate == SK_ADMISSIBLE
        assert r.sk > 0

    def test_a_declaration_disagreeing_with_the_target_stops_compute_sk(self):
        with pytest.raises(TargetKindMismatch):
            compute_sk(CORRECT_PROSE_FIX, PROSE_TARGET, "SW-21-REF-04.md",
                       declared_target_kind=TARGET_KIND_PYTHON)


class TestNoScoreEntersRkAsZeroMovement:
    """'Efficacy enters as 0' means zero MOVEMENT, not a zero SCORE."""

    def test_rk_is_unchanged(self):
        for r_old in (0.05, 0.25, 0.5, 0.8, 0.95):
            r_new, why = apply_sk_to_rk(r_old, SK_NO_SCORE)
            assert r_new == r_old, f"R_k moved from {r_old} to {r_new}"
            assert "unchanged" in why

    def test_the_naive_reading_would_push_risk_up(self):
        """THE TRAP. ``compute_rk(sk=0.0)`` is the obvious implementation of
        'efficacy enters as 0' and it is wrong in the dangerous direction: the
        re-injection term nu_eff is at its MAXIMUM when sk=0, because a
        worthless fix is modelled as maximally likely to inject a new defect.

        R_k is RESIDUAL RISK, so this test asserts the naive path RAISES risk —
        and that apply_sk_to_rk does not. If this ever stops failing to hold,
        the guard has become redundant and should be reconsidered, not deleted
        quietly."""
        r_old = 0.5
        naive = compute_rk(R_old=r_old, q=0.5, sk=0.0)
        assert naive > r_old, (
            "the premise of this guard has changed: compute_rk(sk=0) no longer "
            "raises residual risk")
        assert naive == pytest.approx(0.62, abs=1e-9)
        guarded, _ = apply_sk_to_rk(r_old, SK_NO_SCORE)
        assert guarded == r_old
        assert guarded < naive

    def test_repeated_no_scores_never_accrue(self):
        """One fabricated push is bad; the run does this per finding per round,
        and on a prose target no S_k evaluation can ever work it back down."""
        r = 0.4
        for _ in range(25):
            r, _ = apply_sk_to_rk(r, SK_NO_SCORE)
        assert r == 0.4

    def test_a_scored_outcome_still_moves_rk(self):
        moved, why = apply_sk_to_rk(0.5, SK_ADMISSIBLE, updated=0.31)
        assert moved == pytest.approx(0.31)
        assert "updated" in why

    def test_a_missing_update_holds_rather_than_guessing(self):
        held, why = apply_sk_to_rk(0.5, SK_ADMISSIBLE, updated=None)
        assert held == 0.5 and "unchanged" in why


class TestTheRoundPipelineHandlesNoScore:
    """`compute_sk` returning NO_SCORE is only half of it. The round pipeline
    that consumes the result must not fold it into a tally or an R_k move."""

    @staticmethod
    def _registry_with_a_prose_fix():
        from bench.dm._types import Finding
        from bench.reference_runner_v3 import FindingRegistry

        reg = FindingRegistry()
        cid = reg.register(
            Finding(finding_id="f1", model_id="DeepSeek", round_idx=0,
                    flaw_class=2, severity=0.9, abstraction_index=0.5,
                    description="the stated clearance is the retracted value",
                    falsifier_code="", proposed_fix=SHELL_INJECTION_FIX),
            "DeepSeek")
        return reg, cid

    def _run(self):
        from bench.reference_runner_v3 import _evaluate_sk_for_findings
        reg, cid = self._registry_with_a_prose_fix()
        stats = _evaluate_sk_for_findings(
            reg, PROSE_TARGET, "SW-21-REF-04.md", baseline={}, round_idx=3)
        return reg, cid, stats

    def test_it_is_tallied_as_no_score_and_nothing_else(self):
        _, _, stats = self._run()
        assert stats["evaluated"] == 1
        assert stats["no_score"] == 1
        assert stats["admissible"] == 0
        assert stats["rejected"] == 0, (
            "an unassessed fix counted as rejected reads as a bad fix — the "
            "misreading that made the 2026-08-01 control look like a panel "
            "failure rather than an instrument failure")
        assert stats["escalated"] == 0

    def test_rk_does_not_move(self):
        reg, cid, _ = self._run()
        sk = reg.entries[cid]["sk_result"]
        assert sk["tristate"] == SK_NO_SCORE
        assert sk["R_new"] == sk["R_old"]

    def test_no_threshold_verdict_is_recorded(self):
        """S* is a statement about a score. There is no score."""
        reg, cid, _ = self._run()
        sk = reg.entries[cid]["sk_result"]
        assert "passes_threshold" not in sk
        assert "s_star" not in sk


class TestSkEnabledIsForcedOffInCode:
    def test_the_runner_forces_it_and_does_not_ask_a_flag(self):
        """Enforcement must live in code. The launcher has silently dropped
        config keys six times; a safety property behind a droppable key is not
        enforced."""
        import inspect

        from bench.reference_runner_v3 import run_experiment

        src = inspect.getsource(run_experiment)
        assert "resolve_target_kind(" in src
        assert "cfg = replace(cfg, sk_enabled=False)" in src
        forced_at = src.index("cfg = replace(cfg, sk_enabled=False)")
        used_at = src.index("if cfg.sk_enabled:")
        assert forced_at < used_at, (
            "sk_enabled is forced off after the pipeline has already read it")

    def test_compute_sk_enforces_it_independently(self):
        """Belt and braces, deliberately. Even a caller that never consults the
        target kind — a future one, or a test harness — cannot score prose."""
        assert compute_sk(SHELL_INJECTION_FIX, PROSE_TARGET,
                          "anything.md").tristate == SK_NO_SCORE
