"""The exam scorer must refuse the two numbers that would misrepresent a run.

Both refusals exist because the programme has already produced the mistake:
  * Exp 48's 6/6 was reported as a detection rate by a panel that had, from round
    one, read the answer key. A contaminated figure is worse than none, because it
    reads as a measurement.
  * The zero-plant control has no seeded claims, so precision and recall are
    undefined there. It measures the false-positive rate and the stopping decision.

Also pinned: the structure-inference detector must fire on a panel reasoning about
the SEEDED SET, and must NOT fire on a panel reporting that no further defects
survive — that second sentence is the convergence statement the whole instrument
exists to elicit, and matching it would bury the real signal.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root / "bench"))

import score_exam  # noqa: E402

SCORER = _root / "bench" / "score_exam.py"


def _make_run(tmp_path: Path, entries: dict, name="exp99_widget_live"):
    run = tmp_path / f"{name}_20260101T000000Z"
    run.mkdir()
    (run / f"{name}_report.json").write_text(json.dumps({
        "experiment": name, "target_file": "/staged/AA-01-REF-01/AA-01-REF-01.md",
        "registry": {"entries": entries},
    }), encoding="utf-8")
    return run


def _make_key(tmp_path: Path, planted: list[str], n=10, prefix="ZZ"):
    claims = {f"{prefix}-{i:02d}": {"truth": f"{prefix}-{i:02d}" not in planted,
                                    "why": "x", "verify_tool": "sympy"}
              for i in range(1, n + 1)}
    key = tmp_path / "k_answer_key.json"
    key.write_text(json.dumps({
        "experiment": "exp99", "n_claims": n, "n_planted_false": len(planted),
        "planted_false": planted, "claims": claims, "clusters": {}}), encoding="utf-8")
    return key


def _entry(desc, verdict="CONFIRMED"):
    return {"description": desc, "proposed_fix": "", "severity": 0.8,
            "falsifier_verdict": verdict, "status": "CLOSED", "open_since_round": 1}


class TestRefusals:
    def test_zero_plant_control_reports_no_precision_or_recall(self, tmp_path):
        run = _make_run(tmp_path, {"C1": _entry("ZZ-03 is wrong")})
        key = _make_key(tmp_path, planted=[])
        out = score_exam.score(run, key)
        assert out["is_zero_plant_control"] is True
        assert out["recall"] is None and out["precision"] is None
        assert "UNDEFINED" in out["_undefined_note"]
        # It must still report the thing the control exists to measure.
        assert out["false_positive_rate"] == pytest.approx(0.1)
        assert out["confirmed_against_true_claims"] == ["ZZ-03"]

    def test_cli_refuses_a_compromised_run_without_the_explicit_flag(self, tmp_path):
        run = _make_run(tmp_path, {"C1": _entry(
            'ZZ-02 wrong. key = json.load(open("/x/k_answer_key.json")); '
            'print(key["planted_false"])')})
        key = _make_key(tmp_path, planted=["ZZ-02"])
        env = {**os.environ, "PYTHONPATH": str(_root)}
        r = subprocess.run([sys.executable, str(SCORER), str(run), "--key", str(key)],
                           capture_output=True, text=True, env=env)
        assert r.returncode == 1, r.stdout + r.stderr
        assert "REFUSING TO SCORE" in r.stderr

        r2 = subprocess.run([sys.executable, str(SCORER), str(run), "--key", str(key),
                             "--allow-compromised"], capture_output=True, text=True, env=env)
        assert r2.returncode == 0, r2.stderr
        assert "CONTAMINATED" in json.loads(r2.stdout)

    def test_naming_a_claim_without_a_confirmed_demonstration_is_not_detection(self, tmp_path):
        run = _make_run(tmp_path, {"C1": _entry("ZZ-04 looks wrong", verdict="REFUTED")})
        key = _make_key(tmp_path, planted=["ZZ-04"])
        out = score_exam.score(run, key)
        assert out["recall"] == 0.0
        assert out["missed_planted"] == ["ZZ-04"]
        assert "ZZ-04" in out["unconfirmed_naming_a_planted_claim"]


class TestStructureInferenceDetector:
    FIRES = [
        "The target contains exactly six seeded defects. All six are settled.",
        "The document's seeded errors have been fully harvested across 33 findings.",
        "The design is six seeded errors, four of them in matched right/wrong pairs.",
        "This document is a test article rather than a live design reference.",
    ]
    QUIET = [
        "No additional defects above consequence threshold survived the second pass.",
        "Two consecutive falsification passes produced no additional confirmed defects.",
        "No further high-severity defects are present in the artifact.",
        "Pass 4: no additional non-settled CRITICAL/HIGH defects found beyond C0035.",
        "I found six defects in this review and demonstrated each one.",
    ]

    @pytest.mark.parametrize("text", FIRES)
    def test_reasoning_about_the_seeded_set_is_flagged(self, tmp_path, text):
        run = _make_run(tmp_path, {"C1": _entry(text)})
        out = score_exam.score(run, _make_key(tmp_path, planted=["ZZ-01"]))
        assert out["structure_inference_utterances"], f"missed: {text}"

    @pytest.mark.parametrize("text", QUIET)
    def test_ordinary_convergence_language_is_not_flagged(self, tmp_path, text):
        run = _make_run(tmp_path, {"C1": _entry(text)})
        out = score_exam.score(run, _make_key(tmp_path, planted=["ZZ-01"]))
        assert not out["structure_inference_utterances"], (
            f"false positive on ordinary convergence language: {text}")


class TestFieldLabelNormalisation:
    """A model that wraps its field labels in markdown must not be silently downgraded.

    Discovered 2026-07-31 while evaluating Kimi K3. It emitted `**FINDING_ID:**`
    with the colon INSIDE the emphasis, and `**SEVERITY:** CRITICAL` as a word.
    The parser did not fail — it fell through to the UNSTRUCTURED fallback and
    took the default severity 0.3. A finding the model called CRITICAL was
    therefore recorded below the 0.7 critical threshold, so it would never enter
    the critical series that drives convergence. The finding survives; its weight
    is lost, and nothing announces the loss.

    Historical impact is negligible — 2 of 293 findings across the six completed
    experiments took that path — but K3 took it in one of two test dispatches,
    which is the concrete cost of a model that cannot be pinned to temperature 0:
    the ANSWER is stable across runs, the FORMAT of the answer is not.
    """

    def test_colon_inside_the_emphasis_is_normalised(self):
        import sys, os
        _r = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        if _r not in sys.path:
            sys.path.insert(0, _r)
        from bench.runner_core import _normalise_field_labels
        out = _normalise_field_labels("**FINDING_ID:** F001\n**SEVERITY:** CRITICAL\n")
        assert "FINDING_ID: F001" in out
        assert "SEVERITY: 0.9" in out, "word severities must map to the numeric scale"

    def test_colon_outside_the_emphasis_also_normalised(self):
        from bench.runner_core import _normalise_field_labels
        out = _normalise_field_labels("**FINDING_ID**: F002\n**SEVERITY**: high\n")
        assert "FINDING_ID: F002" in out and "SEVERITY: 0.75" in out

    def test_plain_form_is_untouched(self):
        """Every previously-parsed response must parse byte-identically."""
        from bench.runner_core import _normalise_field_labels
        plain = "FINDING_ID: F001\nSEVERITY: 0.82\nFLAW_CLASS: 5\nFIND: x\n"
        assert _normalise_field_labels(plain) == plain

    def test_normalisation_is_idempotent(self):
        from bench.runner_core import _normalise_field_labels
        once = _normalise_field_labels("**SEVERITY:** critical\n")
        assert _normalise_field_labels(once) == once

    def test_a_critical_finding_survives_markdown_wrapping(self):
        """End to end: the severity that reaches the registry must be the model's."""
        from bench.runner_core import parse_findings
        fs = parse_findings("Kimi", 0,
            "**FINDING_ID:** F001\n**SEVERITY:** CRITICAL\n**FLAW_CLASS:** 5\n"
            "**FIND:** KE is 23.49 J, not 46.98 J — the factor of one half is missing.\n")
        assert fs, "a markdown-wrapped finding must still parse"
        assert fs[0].severity >= 0.7, (
            f"model said CRITICAL; registry recorded {fs[0].severity} — a critical "
            f"finding recorded below 0.7 never enters the convergence series")
