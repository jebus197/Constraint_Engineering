# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'falsifier_supply_and_integrity_r2_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: c80d39b9c392974fc744b2fd4eb9da2be8cca4b8021a5efaf70c17322a2b1e0e
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The general template decides bidirectionally and refuses to pass vacuously.

The two shipped cannot-fail incidents are reproduced here AGAINST the guard,
and the guard is demonstrated FAILING them -- the brief's requirement: "you
must demonstrate that guard failing".
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bench.falsifier_template import (  # noqa: E402
    FalsifierCannotFail, run_general_falsifier)

DOC = """# Pendulum report
The period of a 1 m pendulum at g = 9.81 m/s^2 is T = 2.37 s.
"""
# sympy re-derivation: T = 2*pi*sqrt(L/g) = 2.006 s, so 2.37 s is planted.
FIX = DOC.replace("T = 2.37 s", "T = 2.01 s")


def _planted_period(text: str) -> bool:
    """Delegates the judgement to sympy: the claim is false iff the quoted
    period disagrees with the derived one by more than rounding."""
    import sympy as sp
    m = re.search(r"T = ([0-9.]+) s", text)
    if not m:
        raise ValueError("no period claim found")   # ERROR, never a verdict
    claimed = sp.Float(m.group(1))
    derived = 2 * sp.pi * sp.sqrt(sp.Rational(1) / sp.Float("9.81"))
    return bool(sp.Abs(claimed - derived) > sp.Float("0.01"))


class TestBidirectionalDecision:
    def test_confirms_on_the_planted_claim(self, tmp_path):
        t = tmp_path / "doc.md"
        t.write_text(DOC)
        assert run_general_falsifier(t, _planted_period,
                                     lambda s: FIX) == "CONFIRMED"

    def test_refutes_once_corrected(self, tmp_path):
        t = tmp_path / "doc.md"
        t.write_text(FIX)
        assert run_general_falsifier(
            t, _planted_period,
            lambda s: s.replace("2.01", "2.37")) == "REFUTED"

    def test_repointable_without_edits(self, tmp_path):
        """The founder's generality: the SAME falsifier, new target, no
        edits -- the property the 31.46% file-naming stratum lacks."""
        for name, text, want in (("a.md", DOC, "CONFIRMED"),
                                 ("b.md", FIX, "REFUTED")):
            t = tmp_path / name
            t.write_text(text)
            got = run_general_falsifier(
                t, _planted_period,
                lambda s: FIX if "2.37" in s else DOC)
            assert got == want


class TestTheCannotFailGuard:
    def test_the_check_sk_threshold_shape_is_refused(self, tmp_path):
        """`return True` passed 321 tests. Here it cannot return at all."""
        t = tmp_path / "doc.md"
        t.write_text(DOC)
        with pytest.raises(FalsifierCannotFail, match="does not depend"):
            run_general_falsifier(t, lambda s: True, lambda s: FIX)

    def test_the_e4_bandit_shape_is_refused(self, tmp_path):
        """No metrics on prose, 0 HIGH forever: an instrument that silently
        measures nothing answers alike everywhere, and the guard throws."""
        t = tmp_path / "doc.md"
        t.write_text(DOC)

        def bandit_like(text: str) -> bool:
            findings = []        # the scanner had no purchase and said so to nobody
            return len(findings) > 0
        with pytest.raises(FalsifierCannotFail):
            run_general_falsifier(t, bandit_like, lambda s: FIX)

    def test_a_missing_control_is_refused(self, tmp_path):
        t = tmp_path / "doc.md"
        t.write_text(DOC)
        with pytest.raises(FalsifierCannotFail, match="no control"):
            run_general_falsifier(t, _planted_period, lambda s: s)

    def test_a_missing_claim_is_error_not_verdict(self, tmp_path):
        t = tmp_path / "doc.md"
        t.write_text("no period here\n")
        with pytest.raises(ValueError):
            run_general_falsifier(t, _planted_period, lambda s: s + "x")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
