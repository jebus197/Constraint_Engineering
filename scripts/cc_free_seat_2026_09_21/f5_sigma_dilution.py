"""F5. ADVERSARIAL CHECK OF TODAY'S REPAIR (Section 4).

The repair wires `e1_efficacy` -- the ONLY gate that asks whether the fix cured
the defect -- at weight 2.0 into a RENORMALISED WEIGHTED ARITHMETIC MEAN
alongside three gates that measure ABSENCE OF HARM.

CLAIM UNDER TEST: a fix MEASURED not to cure its own falsifier can still be
admitted with a high sk, and that sk is handed to compute_rk as sigma, which
appendix line 214 defines as "does the proposed fix actually resolve the
detected flaw?". If so, the repair reduces but does not close the defect it
was written to close.

FALSIFIED if e1=0 with the other gates clean yields sk = 0 (i.e. the gate is
decisive). Exits clean if the gate is decisive.
"""
import sys
sys.path.insert(0, ".")
from bench.reference_runner_v3 import FIX_EFFICACY_GATE_WEIGHT, compute_rk

# WIRED 2026-09-24 (CC1). Module-level work, so no main() to intercept `--help`.
import sys as _s, pathlib as _p
_s.path.insert(0, str(_p.Path(__file__).resolve().parents[1]))
from _cli_help import answer_help  # noqa: E402
answer_help(__doc__, __file__)

W = {"e1_efficacy": FIX_EFFICACY_GATE_WEIGHT, "e2_regression": 2.0,
     "e3_ruff": 1.0, "e4_bandit": 2.0}

def E_of(scores):
    """Reproduces compute_sk's renormalised weighted arithmetic mean exactly."""
    tot = sum(W[g] for g in scores)
    return sum((W[g]/tot)*s for g, s in scores.items())

print("Gate weights as shipped:", W, " FIX_EFFICACY_GATE_WEIGHT =", FIX_EFFICACY_GATE_WEIGHT)

print("\nA. A FIX MEASURED NOT TO CURE ITS OWN FALSIFIER, ALL OTHER GATES PERFECT")
all4 = {"e1_efficacy": 0.0, "e2_regression": 1.0, "e3_ruff": 1.0, "e4_bandit": 1.0}
E4 = E_of(all4); sk4 = 1.0*E4
print(f"   scores {all4}")
print(f"   E = {E4:.6f}   sk = A*E = {sk4:.6f}   tristate = "
      f"{'ADMISSIBLE' if sk4 > 0 else 'REJECTED'}")
print(f"   e1's share of the mean = {W['e1_efficacy']/sum(W.values()):.4f}")

print("\nB. WHAT compute_rk THEN DOES WITH THAT sk AS sigma")
R_old, q = 0.5, 0.4
r_diluted = compute_rk(R_old, q, sk4, nu_b=0.0, nu_f=0.0)
r_truth   = compute_rk(R_old, q, 0.0,  nu_b=0.0, nu_f=0.0)
print(f"   R_old={R_old} q={q}")
print(f"   sigma = sk = {sk4:.6f} (diluted) -> R_k = {r_diluted:.6f}")
print(f"   sigma = 0 (what the PROBE MEASURED) -> R_k = {r_truth:.6f}")
print(f"   risk understated by {r_truth - r_diluted:.6f} "
      f"({100*(r_truth-r_diluted)/r_truth:.2f}% of the correct residual)")

print("\nC. IS THE GATE EVER DECISIVE? sk=0 requires EVERY available gate = 0.")
only = {"e1_efficacy": 0.0}
print(f"   e1 alone available : E={E_of(only):.4f} sk={E_of(only):.4f} -> REJECTED"
      "   (this is the repair's measured 0-of-1247 new reach)")
for drop in ("e2_regression", "e3_ruff", "e4_bandit"):
    sc = {g: (0.0 if g == "e1_efficacy" else 1.0) for g in all4 if g != drop}
    print(f"   without {drop:<14}: E={E_of(sc):.4f} -> "
          f"{'ADMISSIBLE' if E_of(sc) > 0 else 'REJECTED'}")

print("\nD. THE WEIGHT QUESTION, ANSWERED BY SOLVING RATHER THAN ASSERTING")
print("   With 3 clean harm-gates (total weight 5.0) and e1=0, sk = 5/(5+w).")
for w in (1.0, 2.0, 4.0, 8.0, 20.0):
    print(f"      w={w:<5} -> sk = {5.0/(5.0+w):.4f}")
print("   NO FINITE WEIGHT makes an arithmetic mean decisive. sk -> 0 only as")
print("   w -> infinity. The dilution is a property of the MEAN, not of the weight,")
print("   so re-arguing 2.0 vs 4.0 cannot close it.")

assert sk4 > 0.5, "gate turned out decisive; this finding is refuted"
print("\nFALSIFIED: sk = %.4f > 0.5 ADMISSIBLE for a fix measured to cure NOTHING." % sk4)
