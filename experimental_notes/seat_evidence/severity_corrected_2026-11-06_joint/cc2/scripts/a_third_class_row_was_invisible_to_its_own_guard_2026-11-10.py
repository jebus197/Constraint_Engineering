# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'severity_corrected_2026-11-06_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 0321782cf65e59fa8008464f536cf5704ad76aadc87238626f3c320c50cc45af
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""FALSIFIER: the 2026-11-06 shape-theorem producer did not detect the
refutation its own `refutation_condition` named.

THE CLAIM UNDER TEST, quoted from the delivering seat's reply:

  "The reachable refutation is an edit, not a measurement: add a third row to
   section 7.7's W table with a value strictly between W(SOFT) and W(HARD).
   [...] I have made it self-reporting: both new producers parse the W and V
   tables out of the appendix at run time, so the derivation goes red
   (`SPEC PARSE FAILED (the appendix moved)`) or re-derives at the new values
   rather than quoting a stale result."

As delivered it did neither. The parse patterns were

    W_ROW = r"\\|\\s*W\\((HARD|SOFT)\\)\\s*\\|\\s*([0-9.]+)\\s*\\|"
    V_ROW = r"\\|\\s*V\\((True|None|False)\\)\\s*\\|\\s*([0-9.]+)\\s*\\|"

and the completeness check `sorted(W) != ["HARD", "SOFT"]` can only fire on a
key the regex CAPTURED. A third row is not captured, so it is not missing, so
the check passes and the two-valued theorem is re-derived and reported PASS --
while being FALSE of the spec on disk.

WHY THIS IS ABOVE THRESHOLD (cdsfl_core.txt section 10, category 3 --
verification-integrity corruption): the guard is the project's own instrument
for detecting that caution 3's theorem has gone stale. An instrument that reads
green in the single condition it was built to detect reports soundness it has
not measured.

WHAT THIS FALSIFIER DOES. It never touches the repository's appendix. It writes
a three-level copy to a temporary directory, points the REAL producer module's
APPENDIX at it, and calls the REAL `read_spec`.

  * DEFECT PRESENT  -> `read_spec` returns a two-key W; this script prints
                       FALSIFIED and raises AssertionError.
  * DEFECT ABSENT   -> `read_spec` raises SystemExit("SPEC PARSE FAILED ...");
                       this script exits 0.

It also demonstrates the MECHANISM separately (re-binding the narrow pattern
reproduces the green read) and the CONSEQUENCE with z3 (a counterexample to the
theorem over a three-level W), so a reader can see both that the guard missed
it and that there was something to miss. Neither of those decides the verdict.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import sys
import tempfile

import z3

REPO = pathlib.Path(__file__).resolve().parents[1]
PRODUCER = REPO / "scripts" / "no_severity_bound_above_one_half_is_a_magnitude_test_2026-11-06.py"
APPENDIX = REPO / "docs" / "MATHEMATICAL_APPENDIX.md"

SOFT_ROW = "| W(SOFT) | 0.5 | Soft preference |"
THIRD_ROW = "| W(MEDIUM) | 0.75 | Intermediate consequence |"

#: The patterns EXACTLY AS DELIVERED on 2026-11-06, for the mechanism
#: demonstration only. Retyped here deliberately and labelled as a historical
#: quotation; the VERDICT below is computed from the live module, never from
#: these.
DELIVERED_W_ROW = re.compile(r"\|\s*W\((HARD|SOFT)\)\s*\|\s*([0-9.]+)\s*\|")


def _load_producer():
    """Import the REAL producer module, not a copy of its logic."""
    spec = importlib.util.spec_from_file_location("_sev_shape_producer", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_sev_shape_producer"] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    assert PRODUCER.is_file(), "the producer under test is missing: %s" % PRODUCER
    assert APPENDIX.is_file(), "the appendix is missing: %s" % APPENDIX
    mod = _load_producer()

    text = APPENDIX.read_text(encoding="utf-8")
    assert text.count(SOFT_ROW) == 1, (
        "the W(SOFT) row is not where this falsifier expects it; the 7.7 table "
        "moved and this script must be re-derived before it is quoted.")
    mutated = text.replace(SOFT_ROW, SOFT_ROW + "\n" + THIRD_ROW)

    print("=" * 78)
    print("FALSIFIER: a third class row against the guard that claims to catch it")
    print("  producer : %s" % PRODUCER.relative_to(REPO))
    print("  mutation : %s  (inserted into a TEMP copy, never the repo)" % THIRD_ROW)
    print("=" * 78)

    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td) / "MATHEMATICAL_APPENDIX.md"
        tmp.write_text(mutated, encoding="utf-8")
        mod.APPENDIX = tmp

        # ---- MECHANISM (not the verdict): the delivered pattern reads green --
        hist = {m.group(1): m.group(2) for m in DELIVERED_W_ROW.finditer(mutated)}
        live = {m.group(1): m.group(2) for m in mod.W_ROW.finditer(mutated)}
        print("\nM1  W rows seen in the three-level table")
        print("      delivered 2026-11-06 pattern : %s" % sorted(hist))
        print("      pattern in the file today    : %s" % sorted(live))

        # ---- CONSEQUENCE (not the verdict): the theorem is false of that spec
        s = z3.Solver()
        w, b, c = z3.Reals("W B c")
        s.add(z3.Or(w == z3.RealVal(1) / 2, w == z3.RealVal(3) / 4, w == z3.RealVal(1)))
        s.add(b >= 0, b <= 1, c > z3.RealVal(1) / 2, c <= z3.RealVal(1))
        s.add(z3.Not((w * b >= c) == z3.And(w == z3.RealVal(1), b >= c)))
        cex = s.check()
        print("\nM2  z3 over a three-level W: counterexample to")
        print("      `Sev >= c  <=>  W = W(HARD) and B >= c`  ->  %s" % cex)
        assert cex == z3.sat, (
            "z3 found no counterexample over a three-level W, so there was "
            "nothing for the guard to detect and this falsifier is void.")
        print("      witness: %s" % s.model())
        print("      arithmetic check: W=0.75, B=0.9, c=0.6 -> Sev=%.4f >= c is %s, "
              "while (W == W(HARD)) is False" % (0.75 * 0.9, 0.75 * 0.9 >= 0.6))

        # ---- THE VERDICT: the live module's own read_spec, computed ----------
        print("\nV1  calling the REAL `read_spec` on the three-level table")
        try:
            W, V, llr = mod.read_spec()
        except SystemExit as exc:
            msg = str(exc)
            print("      SystemExit: %s" % msg)
            assert "SPEC PARSE FAILED" in msg and "MEDIUM" in msg, (
                "the parse refused, but not for the third row: %r" % msg)
            print("\n" + "=" * 78)
            print("NOT FALSIFIED: the guard detects the refutation it names.")
            print("=" * 78)
            return 0

        print("      read_spec RETURNED, W = %s" % {k: str(v) for k, v in W.items()})
        print("FALSIFIED")
        print("=" * 78)
        raise AssertionError(
            "the guard did not detect a third class row. `read_spec` returned "
            "W = %s from a table that declares %d class rows, so the two-valued "
            "shape theorem is re-derived and reported PASS while a z3 "
            "counterexample to it exists (M2 above). The producer's stated "
            "self-reporting property does not hold."
            % ({k: str(v) for k, v in W.items()}, len(hist) + 1))


if __name__ == "__main__":
    sys.exit(main())
