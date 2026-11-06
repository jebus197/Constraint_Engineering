# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'severity_corrected_2026-11-06', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 36052c39421be224130831bb99e4c3a957a727e1e431d675e9faf7d5afd61e41
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The 2026-11-06 severity-round fix, pinned.

The round asked whether `docs/MATHEMATICAL_APPENDIX.md` §7.7 and §7.8 disagree
("a disproved finding scores 0 under 7.7 and 0.273 under 7.8 Approach B"). They
do not, as written: §7.8's `S_v` is a posterior credence over "the claim is
true" and §7.7's `Sev(f)` is a severity, and §7.7 caution 1's substitution
replaces `confidence` ALONE, leaving `V` in place. The disagreement appears only
if the `V` column is DELETED -- which one joint-round seat proposed and the
other warned against. This file pins the clarification and, more importantly,
FAILS if the deletion is ever applied.

Three mechanisms, each with its own check:

1. THE DELETION GUARD. `S_v = 1/(1+exp(-Lambda))` has no zero, so `W . S_v`
   cannot represent `V(False) = 0`. Removing the KEY PROPERTY paragraph or the
   `V(False)` row therefore makes the property unrepresentable, not merely
   unstated. Tests 1a-1c fail on that edit.

2. THE LIVE IMPLEMENTATION STILL HONOURS THE KEY PROPERTY. `compute_sev_f` is
   exercised over a grid of classes and confidences; REFUTED must give exactly
   0.0 at every point. (This is about the computed `sev_f` field, NOT about the
   model-asserted `severity` float the gate reads -- 27 of 32 archived disproved
   findings carry severity above 0, producer
   `scripts/severity_was_never_computed_from_the_model_2026-10-12.py`.)

3. THE COLLAPSE THEOREM, re-derived here rather than cited. For `Sev = W . B`
   with `W in {W(SOFT), W(HARD)}` and `B in [0,1]`, every cut
   `c in (W(SOFT), W(HARD)]` satisfies `Sev >= c  <=>  W = W(HARD) and B >= c`.
   So no cut above `W(SOFT)` constrains consequence magnitude under ANY belief
   factor, including both repairs proposed to the panel.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

import pytest

import bench.reference_runner_v3 as rr

REPO = pathlib.Path(rr.__file__).resolve().parent.parent
APPENDIX = REPO / "docs" / "MATHEMATICAL_APPENDIX.md"
PRODUCER = (REPO / "scripts"
            / "no_severity_bound_above_one_half_is_a_magnitude_test_2026-11-06.py")


@pytest.fixture(scope="module")
def appendix() -> str:
    return APPENDIX.read_text(encoding="utf-8")


class TestTheKeyPropertyCannotBeSilentlyDeleted:
    def test_1a_key_property_paragraph_is_present(self, appendix):
        assert "**Key property:** Disproved findings always receive zero" in appendix, (
            "§7.7's KEY PROPERTY paragraph is gone. S_v has no zero, so "
            "`Sev = W . S_v` cannot represent V(False)=0; deleting this "
            "paragraph adopts the loss, it does not merely tidy the text."
        )

    def test_1b_v_false_row_is_present_and_zero(self, appendix):
        m = re.search(r"\|\s*V\(False\)\s*\|\s*([0-9.]+)\s*\|", appendix)
        assert m is not None, "§7.7's V(False) table row is gone."
        assert float(m.group(1)) == 0.0

    def test_1c_caution_1_names_confidence_as_the_only_substitution_target(self, appendix):
        assert "replaces `confidence` ALONE" in appendix, (
            "§7.7 caution 1 no longer disambiguates whether §7.8's S_v "
            "substitutes for `confidence` or for `confidence . V`. That "
            "ambiguity is what produced two contradictory joint-round fixes."
        )

    def test_1d_section_7_8_marks_S_v_as_a_credence(self, appendix):
        assert "`S_v` is a credence, not a severity" in appendix, (
            "§7.8's heading says 'Severity' while the section derives "
            "P(claim true). Without the clarification the 0 vs 0.273 "
            "type confusion recurs."
        )


class TestTheLiveImplementationHonoursTheKeyProperty:
    @pytest.mark.parametrize("cls", ["HARD", "SOFT", "hard", "soft", None, "WAT"])
    @pytest.mark.parametrize("conf", [0.0, 0.1, 0.5, 0.9, 1.0, None, "0.95"])
    def test_2a_refuted_is_exactly_zero_everywhere(self, cls, conf):
        assert rr.compute_sev_f(cls, conf, "REFUTED") == 0.0

    def test_2b_the_appendix_worked_examples_hold(self):
        assert rr.compute_sev_f("HARD", 0.9, "CONFIRMED") == pytest.approx(0.90)
        assert rr.compute_sev_f("HARD", 0.9, "REFUTED") == 0.00

    def test_2c_no_input_can_reach_the_critical_cut_unless_hard_and_confirmed(self):
        """The collapse, exercised against the real function rather than a model."""
        cut = rr.CRITICAL_SEVERITY_THRESHOLD
        assert cut > rr.SEV_F_W["SOFT"], (
            "This test, and §7.7 caution 3, assume the critical cut sits above "
            "W(SOFT). If the cut is lowered to or below W(SOFT) the collapse "
            "argument no longer applies and caution 3 must be re-derived."
        )
        for cls in ("HARD", "SOFT"):
            for verdict in ("CONFIRMED", "REFUTED", None, "UNTOOLABLE"):
                for conf in (0.0, 0.25, 0.5, 0.7, 0.75, 0.9, 1.0):
                    sev = rr.compute_sev_f(cls, conf, verdict)
                    if sev >= cut:
                        assert cls == "HARD" and verdict == "CONFIRMED"
                        assert sev == pytest.approx(conf)


class TestTheCollapseTheoremItself:
    def test_3a_z3_finds_no_counterexample_over_all_cuts(self):
        z3 = pytest.importorskip("z3")
        w_soft = z3.RealVal(1) / 2
        w_hard = z3.RealVal(1)
        s = z3.Solver()
        W, B, c = z3.Real("W"), z3.Real("B"), z3.Real("c")
        s.add(z3.Or(W == w_soft, W == w_hard))
        s.add(B >= 0, B <= 1)
        s.add(c > w_soft, c <= w_hard)
        s.add(z3.Not((W * B >= c) == z3.And(W == w_hard, B >= c)))
        assert s.check() == z3.unsat, s.model()

    def test_3b_S_v_has_no_zero(self):
        sp = pytest.importorskip("sympy")
        lam = sp.Symbol("Lambda", real=True)
        S_v = 1 / (1 + sp.exp(-lam))
        assert sp.solve(sp.Eq(S_v, 0), lam) == []
        assert sp.limit(S_v, lam, -sp.oo) == 0

    def test_3c_the_disproved_finding_scores_zero_under_the_substitution(self):
        sp = pytest.importorskip("sympy")
        # Lambda_total: SymPy falsified (-4.60) + Dimensional (+2.08) + Numerical (+1.54)
        lam_total = sp.Rational(-460, 100) + sp.Rational(208, 100) + sp.Rational(154, 100)
        S_v = 1 / (1 + sp.exp(-lam_total))
        assert abs(float(sp.N(S_v, 20)) - 0.27289178365887046) < 1e-15
        assert sp.simplify(rr.SEV_F_W["HARD"] * S_v * rr.SEV_F_V["REFUTED"]) == 0


class TestTheProducerDischarges:
    def test_4a_producer_exits_zero(self):
        assert PRODUCER.exists(), PRODUCER
        r = subprocess.run([sys.executable, str(PRODUCER)],
                           capture_output=True, text=True, timeout=600)
        assert r.returncode == 0, r.stdout[-4000:] + r.stderr[-2000:]
        for tag in ("T1_", "T2_", "T3_", "T4_", "T5_"):
            assert ("PASS  " + tag) in r.stdout, (tag, r.stdout[-2000:])
