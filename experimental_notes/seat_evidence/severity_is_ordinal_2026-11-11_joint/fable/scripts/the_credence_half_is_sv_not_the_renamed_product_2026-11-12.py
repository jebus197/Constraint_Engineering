# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'severity_is_ordinal_2026-11-11_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 1177217ea507b865d68f08ae4f5cedd9bf99cfea0cceb3bdbc4b57decf6b9998
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The pair's credence half is S_v (section 7.8), not section 7.7's renamed product.

Joint round `severity_is_ordinal_2026-11-11_joint`, fable seat, 2026-11-12.

CLAIM UNDER TEST. docs/MATHEMATICAL_APPENDIX.md section 7.7.1 defines severity
as an ordered pair. Two candidates exist for the credence slot:

    candidate P (superseded) : W(class) * confidence * Ver(verification)
    candidate S (adopted)    : S_v(f) = sigmoid(Lambda_total)   (section 7.8 B)

This script is the committed producer for the 4 grounds on which P fails as a
credence and for the archive measurement showing the correction flips 0
archived decisions. DIRECTION OF FAILURE: this is a fix-verifier, so it raises
AssertionError and prints FALSIFIED iff one of the ADOPTED amendment's claims
is false, and exits 0 iff every claim checks. Grounds are checked with SymPy
and, where decidable, independently with z3.

Frame: the archive census reuses the exact frame of
scripts/severity_was_never_computed_from_the_model_2026-10-12.py --
LOGS.glob("**/runner_state.json"), sha256 whole-file dedup, registry.entries.
"""
import hashlib
import json
import math
import pathlib
import sys

import sympy as sp

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"

#: Section 7.8's declared verifier operating characteristics (TPR, FPR).
RATES = {"sympy": (0.99, 0.001), "dimensional": (0.80, 0.10),
         "numerical": (0.70, 0.15)}

FAILED = []


def check(name, ok, detail=""):
    tag = "PASS" if ok else "FALSIFIED"
    print(f"[{tag}] {name}" + (f"  {detail}" if detail else ""))
    if not ok:
        FAILED.append(name)


def s_v(outcomes):
    """Section 7.8 Approach B. outcomes: {verifier: 1|0|None}. None = indeterminate."""
    lam = 0.0  # Lambda_prior = 0, uniform prior
    for v, o in outcomes.items():
        if o is None:
            continue  # excluded from D_det: the neutral update is ADDITIVE zero
        tpr, fpr = RATES[v]
        fnr, tnr = 1.0 - tpr, 1.0 - fpr
        lam += math.log(tpr / fpr) if o == 1 else math.log(fnr / tnr)
    return 1.0 / (1.0 + math.exp(-lam))


# ---------------------------------------------------------------- ground 1
# Class-invariance: candidate P depends on the consequence class at EQUAL
# evidence. (S_v is class-invariant by construction: Lambda has no class term.)
c, v = sp.symbols("c v", positive=True)
ratio = sp.simplify((sp.Integer(1) * c * v) / (sp.Rational(1, 2) * c * v))
check("G1a sympy: P(HARD)/P(SOFT) == 2 at equal (confidence, Ver), all c,v>0",
      ratio == 2, f"ratio={ratio}")
try:
    import z3
    zc, zv = z3.Reals("zc zv")
    s = z3.Solver()
    # sat = there EXISTS an equal-evidence input where the classes differ.
    s.add(zc > 0, zv > 0, zc <= 1, zv <= 1, 1.0 * zc * zv != 0.5 * zc * zv)
    check("G1b z3: class-dependence of P at equal evidence is sat",
          s.check() == z3.sat)
except ImportError:
    print("[skip] z3 not installed; G1b rests on sympy G1a")
soft_verified = 0.5 * 1.0 * 1.0
check("G1c a fully verified SOFT finding gets P-credence <= 0.5",
      soft_verified <= 0.5, f"P = {soft_verified}")

# ---------------------------------------------------------------- ground 3
# Neutral update: under S, no determinate verifier leaves belief at the prior;
# under P, Ver(None)=0.5 halves it. (Ground 2, provenance, is measured below.)
check("G3a S: D_det empty => S_v == 0.5 == prior, belief unmoved",
      s_v({"sympy": None, "dimensional": None, "numerical": None}) == 0.5)
p = sp.symbols("p", positive=True)
sols = sp.solve(sp.Eq(sp.Rational(1, 2) * p, p), p)
check("G3b sympy: 0.5*belief == belief has NO positive solution -- the "
      "multiplicative 0.5 is never the identity update", sols == [])

# ---------------------------------------------------------------- ground 4
# Key property relocates: S_v is never exactly 0, yet every falsification
# routes the finding below the 0.5 selection threshold of section 7.11.
lam_s = sp.symbols("lam", real=True)
sig = 1 / (1 + sp.exp(-lam_s))
check("G4a sympy: sigmoid(Lambda) = 0 has no real solution",
      sp.solve(sp.Eq(sig, 0), lam_s) == [])
check("G4b sympy: the Lambda -> -oo limit is 0 and unattained",
      sp.limit(sig, lam_s, -sp.oo) == 0)
for name in RATES:
    tpr, fpr = RATES[name]
    fnr, tnr = 1 - tpr, 1 - fpr
    check(f"G4c {name}: FNR < TNR so a lone falsification gives S_v < 0.5",
          fnr < tnr and s_v({name: 0}) < 0.5, f"S_v = {s_v({name: 0}):.6f}")
veto = s_v({"sympy": 0, "dimensional": 1, "numerical": 1})
check("G4d veto: SymPy falsified + others verified => S_v < 0.5 "
      "(appendix verified line: 0.272)", veto < 0.5, f"S_v = {veto:.6f}")
check("G4e veto inequality: |log(FNR/TNR)|_sympy > sum of other positive weights",
      abs(math.log(0.01 / 0.999)) > math.log(0.80 / 0.10) + math.log(0.70 / 0.15),
      f"{abs(math.log(0.01/0.999)):.4f} > "
      f"{math.log(0.80/0.10) + math.log(0.70/0.15):.4f}")

# ------------------------------------------------- ground 2 + the archive
# Provenance and decision-invariance, on the SAME frame as the 2026-10-12
# producer: each distinct registry counted once, by whole-file sha256.
seen, n = {}, 0
n_conf = n_class = 0
flips = 0
tpr, fpr = RATES["sympy"]
SV1 = {"CONFIRMED": 1 / (1 + math.exp(-math.log(tpr / fpr))),
       None: 0.5,
       "REFUTED": 1 / (1 + math.exp(-math.log((1 - tpr) / (1 - fpr))))}
for fp in sorted(LOGS.glob("**/runner_state.json")):
    try:
        raw = fp.read_bytes()
    except OSError:
        continue
    dig = hashlib.sha256(raw).hexdigest()
    if dig in seen:
        continue
    seen[dig] = fp
    try:
        d = json.loads(raw.decode("utf-8", errors="ignore"))
    except Exception:  # noqa: BLE001
        continue
    for cid, e in (((d or {}).get("registry") or {}).get("entries") or {}).items():
        if not isinstance(e, dict) or not isinstance(e.get("severity"), (int, float)):
            continue
        n += 1
        if "confidence" in e:
            n_conf += 1
        if "constraint_class" in e:
            n_class += 1
        verdict = str(e.get("falsifier_verdict") or "").strip().upper()
        verdict = verdict if verdict in ("CONFIRMED", "REFUTED") else None
        # candidate P on the archive: both missing factors default to their
        # stricter readings (W=1, confidence=1), reducing P to Ver alone.
        p_cred = {"CONFIRMED": 1.0, None: 0.5, "REFUTED": 0.0}[verdict]
        s_cred = SV1[verdict]
        if (p_cred >= 0.5) != (s_cred >= 0.5):
            flips += 1
print(f"\n[frame] distinct registries: {len(seen)}; entries with numeric severity: {n}")
check("G2a archive: `confidence` present on 0 entries (candidate P's "
      "model-asserted factor has no writer)", n_conf == 0, f"present on {n_conf}/{n}")
print(f"[info] constraint_class present on {n_class}/{n} "
      "(writer exists since B84; population pending)")
check("M1 archive: 7.11 selection at >= 0.5 decides IDENTICALLY under both "
      "candidates on every entry -- 0 decision flips", flips == 0,
      f"flips = {flips}/{n}")
check("M2 archive frame is non-empty (else the measurement is void)", n > 0)

# ------------------------------------------------- the amendment is wired in
appendix = (REPO / "docs" / "MATHEMATICAL_APPENDIX.md").read_text(encoding="utf-8")
check("W1 appendix pair now reads ( c_d(f) , S_v(f) )",
      "severity_d(f) = ( c_d(f) , S_v(f) )" in appendix)
check("W2 appendix keeps the superseded form visible and cites this producer",
      "the_credence_half_is_sv_not_the_renamed_product_2026-11-12.py" in appendix
      and "under its own name" in appendix)
check("W3 section 7.7 is NOT removed (additive standard)",
      "### 7.7 Per-Finding Severity" in appendix and "NOT removed" in appendix)

print()
if FAILED:
    print("FALSIFIED: " + "; ".join(FAILED))
    raise AssertionError(f"{len(FAILED)} claim(s) failed: {FAILED}")
print(f"ALL CHECKS PASS ({n} archived entries; 0 decision flips; "
      "4 grounds verified with sympy" + ("+z3" if "z3" in sys.modules else "") + ")")
