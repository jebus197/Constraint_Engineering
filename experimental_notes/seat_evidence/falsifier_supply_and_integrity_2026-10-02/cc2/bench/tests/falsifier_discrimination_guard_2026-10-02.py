# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'falsifier_supply_and_integrity_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 047c227160693023dd54212dd67066aae5f819206c99f34da160f8efc7ef7a5e
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""FALSIFIER (Q3). Does the project's EXISTING discrimination control separate
a cannot-fail falsifier from a real one?

Convention per the core directives: a falsifier RAISES AssertionError (or prints
FALSIFIED) when the defect is real and EXITS CLEANLY when the claim is false.

This script raises if the control fails to separate them. It exits clean if the
separation holds, which is my claim: the general cannot-fail guard already
exists and works; the defect is that it is UNREACHED, not that it is absent.
"""
import pathlib, sys, tempfile
ROOT = pathlib.Path('.').resolve(); sys.path.insert(0, str(ROOT))
from bench.falsifier_verify import reverify_falsifier

TARGET = ROOT / "bench" / "logs" / "panel_round11_2026-09-11" / "BRIEF.md"
FIG = "real-rejection rate : 2/640 = 0.3125%"

# Shape 1: `check_sk_threshold` hardwired to `return True` (passed 321 tests).
HARDWIRED = '''
def check_sk_threshold(*a, **k):
    return True
assert not check_sk_threshold(), "defect present"
'''
# Shape 2: A19's `e4_bandit` -- no metrics on prose, so 0 HIGH forever and the
# assertion is over an empty set: vacuously satisfied, cannot ever fire.
VACUOUS = '''
metrics = []                 # the instrument returned nothing on prose
assert len([m for m in metrics if m == "HIGH"]) > 0, "defect present"
'''
# A falsifier that actually reads the target.
REAL = f'''
import pathlib
t = pathlib.Path({str(TARGET)!r}).read_text()
assert {FIG!r} not in t, "defect present: the superseded figure is declared"
'''

real_txt = TARGET.read_text()
print("THE DISCRIMINATION TEST: run the falsifier against the real target and")
print("against a CORRECTED copy. A falsifier that returns the same verdict on")
print("both has told us nothing about the target.\n")
rows = []
for name, src in (("hardwired `return True`", HARDWIRED),
                  ("vacuous: 0 HIGH over an empty metric set", VACUOUS),
                  ("reads the real target", REAL)):
    v_real = reverify_falsifier(src)
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / TARGET.name
        p.write_text(real_txt.replace(FIG, "real-rejection rate : 1/640 = 0.1562%"))
        v_corr = reverify_falsifier(src.replace(str(TARGET), str(p)))
    out = "NON_DISCRIMINATING" if v_real == v_corr else "DISCRIMINATES"
    rows.append((name, out))
    print(f"  {name:42s} real={v_real:10s} corrected={v_corr:10s} -> {out}")

want = ["NON_DISCRIMINATING", "NON_DISCRIMINATING", "DISCRIMINATES"]
got = [r[1] for r in rows]
print()
if got != want:
    print("FALSIFIED")
    raise AssertionError(f"the control did not separate them: got {got}, want {want}")
print("CLEAN EXIT: both cannot-fail shapes are caught, the real falsifier is not.")
print("So the general guard EXISTS. The defect is its reach, measured separately.")
