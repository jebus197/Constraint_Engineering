# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'dynamic_roster_and_derived_ladder_2026-10-07', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 5ed2e124b24b64bb44d47976e42770aacefeeeba02015fcd6c766c1932077f79
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""FALSIFIER for bench/degraded_convergence_2026-10-07.py.

Fails (AssertionError / prints FALSIFIED) iff the claimed defect or the claimed
repair is wrong. Imports the REAL modules; defines no copy of anything under test.
"""
from __future__ import annotations

import importlib.util as iu
import inspect
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent          # bench/
sys.path.insert(0, str(HERE))


def _load(name, filename):
    spec = iu.spec_from_file_location(name, HERE / filename)
    m = iu.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


DC = _load("cdsfl_degraded_convergence", "degraded_convergence_2026-10-07.py")
fails = []


# ── 1. THE DEFECT, AND ITS REPAIR IN THE REAL RUNNER. ──────────────────────
# Before 2026-10-07 the gate's signature carried no roster term, so the
# shrinking-roster hazard was invisible to it. This now asserts the REPAIR is
# present: the falsifier fails if the roster parameters are missing OR if the
# scaled window is not actually applied inside the gate body.
src = (HERE / "reference_runner_v3.py").read_text()
i = src.index("def _check_gamma_alt_convergence(")
sig = src[i:src.index("-> Tuple[bool, str]:", i)]
params = [p.split(":")[0].strip() for p in sig.split("(", 1)[1].split(",")]
print(f"[1] real gate parameters: {params}")
for need in ("roster_declared", "live_by_round"):
    if not any(need in p for p in params):
        fails.append(f"the gate does NOT accept {need} -- the hazard is still "
                     f"invisible to it")
body = src[i:src.index("\ndef ", i + 10)]
if "k_required" not in body or "window = _roster_record.k_required" not in body:
    fails.append("the gate accepts a roster but never scales `window` by it -- an "
                 "addition nothing reaches")
if "_roster_note(" not in body:
    fails.append("the gate's verdict strings carry no roster integrity clause")
print(f"    accepts a roster, scales `window` by k_required, and labels every "
      f"verdict: True")

# ── 2. THE DERIVATION. K' = ceil(K*n_dec/n_live) is sufficient at EVERY rho. ──
# Independence is claimed to be the worst case because f(n) = -ln A(n) is concave
# through the origin. Check that claim by exact integration over a beta-mixture
# latent, NOT by assuming it.
from mpmath import mp, mpf, quad, log, ceil as mceil
mp.dps = 40

Q, K, N_DEC = mpf("0.3"), 3, 6


def beta_mix(rho):
    """p(u) ~ Beta(a,b) with mean Q and intra-round correlation rho."""
    if rho <= 0:
        return None
    nu = (1 - rho) / rho
    return (Q * nu, (1 - Q) * nu)


def A(n, rho):
    """A(n) = E_u[(1-p(u))^n]."""
    if rho <= 0:
        return (1 - Q) ** n
    a, b = beta_mix(rho)
    from mpmath import beta as B
    # E[(1-p)^n] for p~Beta(a,b) = B(a, b+n)/B(a,b)
    return B(a, b + n) / B(a, b)


print("\n[2] is the independence-derived window sufficient at every rho?")
for rho in ["0", "0.05", "0.1", "0.3", "0.5", "0.8", "0.95"]:
    r = mpf(rho)
    for n_live in (1, 2, 3, 4, 5):
        f_dec = -log(A(N_DEC, r))
        f_liv = -log(A(n_live, r))
        k_exact = K * f_dec / f_liv              # the TRUE requirement at this rho
        k_used = DC.required_quiet_window(N_DEC, n_live, K)
        # The module's window must be at least the true requirement.
        if k_used + mpf("1e-25") < k_exact:
            fails.append(f"window UNDER-corrects at rho={rho}, n_live={n_live}: "
                         f"used {k_used} < required {float(k_exact):.6f}")
        # And the concavity bound f(n_dec)/f(n_live) <= n_dec/n_live must hold.
        if f_dec / f_liv > mpf(N_DEC) / n_live + mpf("1e-25"):
            fails.append(f"concavity bound VIOLATED at rho={rho}, n_live={n_live}")
    print(f"    rho={rho:>5}  K_exact(n_live=2)={float(K*(-log(A(N_DEC,r)))/(-log(A(2,r)))):.4f}"
          f"  K_used={DC.required_quiet_window(N_DEC,2,K)}  sufficient=True")

# Tightness at independence: the bound must be EQUALITY there, else it is loose
# and the repair over-corrects without cause.
f_ratio_indep = float((-log(A(N_DEC, mpf(0)))) / (-log(A(2, mpf(0)))))
if abs(f_ratio_indep - N_DEC / 2) > 1e-20:
    fails.append(f"bound not tight at independence: {f_ratio_indep} != {N_DEC/2}")
print(f"    tight at independence: f(6)/f(2) = {f_ratio_indep:.12f} == 6/2 = 3.0")

# And the scaled window must actually hold P_spurious at or below the declared level.
print("\n[3] does the scaled window hold P_spurious at the declared level?")
base = DC.p_quiet_independent(N_DEC, K, float(Q))
for n_live in (1, 2, 3, 4, 5, 6):
    kr = DC.required_quiet_window(N_DEC, n_live, K)
    p = DC.p_quiet_independent(n_live, kr, float(Q))
    if p > base + 1e-15:
        fails.append(f"scaled window still exceeds declared risk at n_live={n_live}: "
                     f"{p:.3e} > {base:.3e}")
    print(f"    n_live={n_live}  K_req={kr}  P={p:.6e}  <= declared {base:.6e}: {p <= base + 1e-15}")


# ── 4. THE TWO GUARDS a naive implementation gets wrong. ────────────────────
print("\n[4] guards")
try:
    DC.required_quiet_window(6, 0, 3)
    fails.append("n_live=0 did NOT raise: an empty panel was given a finite window")
except ValueError:
    print("    n_live=0 raises ValueError (no window repairs an empty panel): OK")
if DC.required_quiet_window(6, 12, 3) != 3:
    fails.append("an OVER-sized roster weakened the declared window below K")
print(f"    n_live(12) > n_declared(6) -> K_req={DC.required_quiet_window(6,12,3)} "
      f"(clamped to K=3, never below): OK")
if DC.required_quiet_window(6, 6, 3) != 3:
    fails.append("intact roster changed the window -- not behaviour-preserving")
print(f"    intact roster -> K_req={DC.required_quiet_window(6,6,3)} == K_declared=3: OK")
# Requirement 1: a DECLARED 1-seat roster is clean, not degraded.
r1 = DC.assess_roster(["CC2"], [["CC2"], ["CC2"], ["CC2"]], [1, 0, 0, 0], 3)
if r1.integrity != DC.CLEAN:
    fails.append(f"a declared 1-seat roster was marked {r1.integrity}, not CLEAN "
                 f"-- violates requirement 1 (roster size is arbitrary)")
print(f"    declared 1-seat roster -> {r1.integrity} (requirement 1): OK")


# ── 5. THE SEPARATION. Clean and degraded must be distinguishable. ──────────
print("\n[5] the two causes, same count tail, different verdict")
hist = [2, 0, 0, 0]
clean = DC.assess_roster(
    ["CC2", "Codex", "ChatGPT", "Gemini", "DeepSeek", "Fable"],
    [["CC2", "Codex", "ChatGPT", "Gemini", "DeepSeek", "Fable"]] * 3, hist, 3)
degr = DC.assess_roster(
    ["CC2", "Codex", "ChatGPT", "Gemini", "DeepSeek", "Fable"],
    [["CC2", "Codex"]] * 3, hist, 3)
print(f"    clean : tail={clean.quiet_tail} integrity={clean.integrity} "
      f"K_req={clean.k_required} met={DC.count_side_is_met(clean)}")
print(f"    degr  : tail={degr.quiet_tail} integrity={degr.integrity} "
      f"K_req={degr.k_required} met={DC.count_side_is_met(degr)}")
if clean.quiet_tail != degr.quiet_tail:
    fails.append("the two cases were handed different count tails -- not the real test")
if clean.integrity == degr.integrity:
    fails.append("clean and degraded got the SAME integrity class -- no separation")
if DC.count_side_is_met(clean) is not True:
    fails.append("an intact roster with a full streak was refused -- regression")
if DC.count_side_is_met(degr) is not False:
    fails.append("a 2-of-6 roster converged on 3 quiet rounds -- the hazard survives")
if clean.to_dict()["reportable_as_clean"] is not True or \
        degr.to_dict()["reportable_as_clean"] is not False:
    fails.append("reportable_as_clean does not separate the two")
print(f"    identical integer evidence, different verdict: "
      f"{DC.count_side_is_met(clean)} vs {DC.count_side_is_met(degr)}")

# A degraded run MUST still be able to converge (requirement 8): give it K_req.
degr_long = DC.assess_roster(
    ["CC2", "Codex", "ChatGPT", "Gemini", "DeepSeek", "Fable"],
    [["CC2", "Codex"]] * 9, [2] + [0] * 9, 3)
if not DC.count_side_is_met(degr_long):
    fails.append("a degraded run could NOT converge even at K_required -- that "
                 "blocks the run and violates requirement 8")
print(f"    degraded run with {degr_long.k_observed} quiet rounds >= K_req="
      f"{degr_long.k_required} converges as {degr_long.integrity} "
      f"(requirement 8 honoured): {DC.count_side_is_met(degr_long)}")


# ── 6. THE UX HOLE: an edited declared roster must not launder a run. ──────
print("\n[6] can a mid-run roster edit turn DEGRADED into CLEAN?")
FULL6 = ["CC2", "Codex", "ChatGPT", "Gemini", "DeepSeek", "Fable"]
fp0 = DC.roster_fingerprint(FULL6)
# The researcher takes the UX's third option and drops the failed seat from the
# DECLARED list. Live == declared now, so the naive check would say CLEAN.
EDITED = [m for m in FULL6 if m != "Gemini"]
laundered = DC.assess_roster(EDITED, [EDITED] * 3, [2, 0, 0, 0], 3,
                             expected_fingerprint=fp0)
print(f"    declared edited 6 -> {len(EDITED)}; live == declared")
print(f"    integrity = {laundered.integrity}; converges = "
      f"{DC.count_side_is_met(laundered)}")
if laundered.integrity != DC.TAMPERED:
    fails.append(f"an edited declared roster was classed {laundered.integrity} -- "
                 f"a degraded run can be laundered into a clean one through the UI")
if DC.count_side_is_met(laundered):
    fails.append("a tampered run converged")
# And the honest path -- same roster, unedited -- is unaffected.
honest = DC.assess_roster(FULL6, [FULL6] * 3, [2, 0, 0, 0], 3,
                          expected_fingerprint=fp0)
if honest.integrity != DC.CLEAN or not DC.count_side_is_met(honest):
    fails.append("the fingerprint check broke the honest clean path")
print(f"    the unedited roster still converges CLEAN: "
      f"{honest.integrity == DC.CLEAN and DC.count_side_is_met(honest)}")
print(f"    fingerprint is omitted -> no check, archived behaviour unchanged: "
      f"{DC.assess_roster(FULL6, [FULL6]*3, [2,0,0,0], 3).integrity == DC.CLEAN}")

print("\n" + "=" * 62)
if fails:
    print("FALSIFIED")
    for f in fails:
        print("  -", f)
    raise AssertionError(f"{len(fails)} claim(s) falsified")
print("NOT FALSIFIED: the defect is real and the repair discharges it.")
