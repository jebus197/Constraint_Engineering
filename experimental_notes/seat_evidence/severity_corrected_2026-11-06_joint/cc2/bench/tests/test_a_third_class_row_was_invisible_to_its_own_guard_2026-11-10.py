# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'severity_corrected_2026-11-06_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 24dba16a81b76ee14d1b6c1636f1ef561da309d4b71d58cef9c0f7e182cb0995
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The 7.7 factor parse must be COMPLETE, not just correct on known keys.

WHY THIS EXISTS. The 2026-11-06 free round delivered
`scripts/no_severity_bound_above_one_half_is_a_magnitude_test_2026-11-06.py`,
whose `refutation_condition` names exactly one reachable refutation -- "add a
third row to section 7.7's W table with a value strictly between W(SOFT) and
W(HARD)" -- and claims the producer is self-reporting against it: it would go
red with `SPEC PARSE FAILED (the appendix moved)` or re-derive at the new
values. MEASURED 2026-11-10: it did neither. The patterns captured a FIXED
alternation `W\\((HARD|SOFT)\\)`, and the completeness check
`sorted(W) != ["HARD", "SOFT"]` can only fire on a key the regex captured, so a
third row was invisible. With `| W(MEDIUM) | 0.75 | Intermediate consequence |`
in the table the producer printed `W = {HARD: 1, SOFT: 1/2}`, reported T2 PASS
and exited 0, while z3 returns `sat` for a counterexample to T2 over a
three-level W (W = 0.75, B = 0.9, c = 0.6 gives Sev = 0.675 >= c with
W != W(HARD)). All 66 tests across the 3 severity guard files stayed green.

That is `cdsfl_core.txt` section 10 category 3: the instrument built to detect
a stale theorem read green in the one condition it was built for.

`test_the_severity_factor_values_are_pinned_2026-11-06.py` pins the VALUES of
the 5 known rows and cannot see a 6th, so it is not a substitute for these
assertions and these are not a substitute for it.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PRODUCER = (REPO / "scripts"
            / "no_severity_bound_above_one_half_is_a_magnitude_test_2026-11-06.py")
FALSIFIER = (REPO / "scripts"
             / "a_third_class_row_was_invisible_to_its_own_guard_2026-11-10.py")
APPENDIX = REPO / "docs" / "MATHEMATICAL_APPENDIX.md"
SOFT_ROW = "| W(SOFT) | 0.5 | Soft preference |"
THIRD_ROW = "| W(MEDIUM) | 0.75 | Intermediate consequence |"


@pytest.fixture(scope="module")
def producer():
    assert PRODUCER.is_file(), "the producer under test is missing"
    spec = importlib.util.spec_from_file_location("_sev_shape_producer_t", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_sev_shape_producer_t"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestTheParseIsComplete:
    def test_the_w_pattern_captures_an_unknown_class_name(self, producer):
        """A fixed alternation cannot report a row it never matched."""
        row = "| W(MEDIUM) | 0.75 | Intermediate consequence |"
        got = [m.group(1) for m in producer.W_ROW.finditer(row)]
        assert got == ["MEDIUM"], (
            f"W_ROW saw {got} in {row!r}. A class row the pattern does not "
            f"capture cannot reach the `sorted(W) != ['HARD','SOFT']` check, "
            f"so a third consequence level would be silently dropped and the "
            f"two-valued shape theorem re-derived as though it still held.")

    def test_the_v_pattern_captures_an_unknown_verification_name(self, producer):
        row = "| V(Partial) | 0.75 | Partially assessed |"
        got = [m.group(1) for m in producer.V_ROW.finditer(row)]
        assert got == ["Partial"], f"V_ROW saw {got} in {row!r}"

    def test_read_spec_refuses_a_three_level_table(self, producer, tmp_path):
        """EXECUTED against the real `read_spec`, on a temp copy of the real
        appendix. The repository's own appendix is never touched."""
        assert APPENDIX.is_file(), "the appendix is missing"
        text = APPENDIX.read_text(encoding="utf-8")
        assert text.count(SOFT_ROW) == 1, (
            "the W(SOFT) row moved; re-derive this test before trusting it")
        tmp = tmp_path / "MATHEMATICAL_APPENDIX.md"
        tmp.write_text(text.replace(SOFT_ROW, SOFT_ROW + "\n" + THIRD_ROW),
                       encoding="utf-8")
        original = producer.APPENDIX
        producer.APPENDIX = tmp
        try:
            with pytest.raises(SystemExit) as exc:
                producer.read_spec()
        finally:
            producer.APPENDIX = original
        msg = str(exc.value)
        assert "SPEC PARSE FAILED" in msg and "MEDIUM" in msg, (
            f"read_spec refused, but not for the third row: {msg!r}")

    def test_read_spec_still_accepts_the_appendix_as_it_stands(self, producer):
        """The widened capture must not make the live spec unparseable."""
        W, V, llr = producer.read_spec()
        assert sorted(W) == ["HARD", "SOFT"]
        assert sorted(V) == ["False", "None", "True"]
        assert sorted(llr) == ["Dimensional", "Numerical", "SymPy"]


class TestTheFalsifierRuns:
    def test_the_falsifier_exits_zero_on_the_repaired_guard(self):
        assert FALSIFIER.is_file(), "the falsifier for this finding is missing"
        r = subprocess.run([sys.executable, str(FALSIFIER)],
                           capture_output=True, text=True, cwd=str(REPO))
        assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-2000:]
        assert "NOT FALSIFIED" in r.stdout
        assert "FALSIFIED\n" not in r.stdout.replace("NOT FALSIFIED", "")


class TestSection7_11IsNotASecondVetoOnARefutedFinding:
    """Added 2026-11-10. The joint round's other seat wrote that a disproved
    finding "is rejected by EACH conjunct independently" of 7.11. The
    `Sev(f) > tau_sev` conjunct does reject it. The `S_v >= 0.5` conjunct does
    NOT, in general: `S_v` is computed over 7.8's determinate VERIFIER set,
    while `V` comes from the runner's falsifier re-run, so the two can point
    opposite ways. This matters because the overclaim, if believed, makes
    deleting the `V` column look safe -- 7.11 would appear to catch refuted
    findings anyway. It does not. COMPUTED here, from the 7.8 table, not read.
    """

    def test_a_refuted_finding_can_clear_the_credence_conjunct(self):
        import sympy as sp
        from z3 import Real, Solver, RealVal, And, Or, sat

        # 7.8 table, exact rationals: Dimensional + 2.08, Numerical + 1.54,
        # SymPy indeterminate so excluded from D_det.
        lam = sp.Rational(52, 25) + sp.Rational(77, 50)
        assert lam == sp.Rational(181, 50), lam
        s_v = 1 / (1 + sp.exp(-lam))
        assert s_v >= sp.Rational(1, 2), (
            "the witness does not clear 7.11's credence threshold; "
            f"S_v = {float(s_v)}")
        assert abs(float(s_v) - 0.97391592485361706) < 1e-15, float(s_v)

        # z3, independently: a refuted finding (V = 0, hence Sev = 0) with
        # S_v >= 0.5 is satisfiable, so the credence conjunct does not veto it.
        z = Solver()
        sv, w, sev = Real("S_v"), Real("W"), Real("Sev")
        z.add(sv >= 0, sv <= 1, sv >= RealVal(1) / 2)
        z.add(Or(w == RealVal(1), w == RealVal(1) / 2))
        z.add(sev == w * sv * RealVal(0))          # V(False) = 0
        assert z.check() == sat, (
            "z3 cannot build a refuted finding that clears S_v >= 0.5; if that "
            "is genuinely unsatisfiable the 7.8 paragraph added 2026-11-10 is "
            "wrong and must be withdrawn")
        m = z.model()
        assert m[sev].as_fraction() == 0, (
            "the severity of the witness is not 0, so it is not the case that "
            "`V` is what rejects it")

    def test_the_rejection_really_comes_from_the_severity_conjunct(self):
        """`Sev(f) > tau_sev` with Sev = 0 and tau_sev >= 0 is unsatisfiable."""
        from z3 import Real, Solver, RealVal, unsat
        z = Solver()
        tau = Real("tau_sev")
        z.add(tau >= 0, RealVal(0) > tau)
        assert z.check() == unsat, (
            "a zero severity passes `Sev > tau_sev` for some tau_sev >= 0, "
            "which would remove the only conjunct that rejects a refuted "
            "finding")
