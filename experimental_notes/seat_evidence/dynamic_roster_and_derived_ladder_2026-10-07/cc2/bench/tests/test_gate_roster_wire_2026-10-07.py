# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'dynamic_roster_and_derived_ladder_2026-10-07', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 216d146f028662e24730752d0b9cc14a0b651031af99feae1c8439b8a37316df
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""FALSIFIER for the roster wire into bench/reference_runner_v3.py.

Imports the REAL runner and calls the REAL gate. An addition nothing reaches is
not additive, so this asserts the wire EXISTS at the live call site, that the
names it uses are in scope there, and that the default path is unchanged.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
fails = []
SRC = (HERE / "reference_runner_v3.py").read_text()
TREE = ast.parse(SRC)

# ── 1. The gate now TAKES a roster, and the live call site PASSES one. ─────
fn = next(n for n in ast.walk(TREE)
          if isinstance(n, ast.FunctionDef) and n.name == "_check_gamma_alt_convergence")
params = [a.arg for a in fn.args.args]
print(f"[1] gate parameters now: {params}")
for need in ("roster_declared", "live_by_round"):
    if need not in params:
        fails.append(f"gate does not accept {need}")

calls = [n for n in ast.walk(TREE) if isinstance(n, ast.Call)
         and isinstance(n.func, ast.Name)
         and n.func.id == "_check_gamma_alt_convergence"]
wired = [c for c in calls if {k.arg for k in c.keywords} >= {"roster_declared",
                                                             "live_by_round"}]
print(f"    call sites: {len(calls)}; call sites passing a roster: {len(wired)}")
if not wired:
    fails.append("NO call site passes a roster -- the addition is unreached, which "
                 "is the 11-times-measured 'addition that does nothing' class")

# ── 2. The names the wire uses must be IN SCOPE at that call site. ────────
# `baseline` and `report` must be assigned earlier in the same function.
enclosing = None
for node in ast.walk(TREE):
    if isinstance(node, ast.FunctionDef) and any(
            c in ast.walk(node) for c in wired):
        enclosing = node
        break
print(f"[2] enclosing function of the wired call: {enclosing.name if enclosing else None}")
if enclosing is None:
    fails.append("could not locate the enclosing function of the wired call")
else:
    assigned = {t.id for n in ast.walk(enclosing) if isinstance(n, ast.Assign)
                for t in ast.walk(n) if isinstance(t, ast.Name)}
    assigned |= {a.arg for a in enclosing.args.args}
    for need in ("baseline", "report"):
        if need not in assigned:
            fails.append(f"'{need}' is not bound in {enclosing.name} -- the wire "
                         f"would raise NameError at runtime")
    print(f"    'baseline' bound: {'baseline' in assigned}; "
          f"'report' bound: {'report' in assigned}")

# ── 3. RUN the real gate. Default path must be behaviour-identical. ───────
import importlib.util as iu
spec = iu.spec_from_file_location("cdsfl_rr3", HERE / "reference_runner_v3.py")
RR = iu.module_from_spec(spec)
sys.modules["cdsfl_rr3"] = RR
try:
    spec.loader.exec_module(RR)
except Exception as exc:
    print(f"    runner import raised {type(exc).__name__}: {exc}")
    raise

cfg = RR.RunnerConfig()
cfg.gamma_alt_consecutive_zero_crit = 3
cfg.gamma_alt_threshold = 0.30
cfg.gamma_alt_earliest_round = 0
HIST = [2, 0, 0, 0]
FULL = ["CC2", "ChatGPT", "Codex", "DeepSeek", "Fable", "Gemini"]

print("\n[3] the real gate, called three ways on the SAME count tail")
base = RR._check_gamma_alt_convergence(5, 0.6, HIST, cfg, gamma_critical=0.6,
                                       total_findings=9)
print(f"    no roster supplied (archived path): converged={base[0]}")
clean = RR._check_gamma_alt_convergence(5, 0.6, HIST, cfg, gamma_critical=0.6,
                                        total_findings=9,
                                        roster_declared=FULL,
                                        live_by_round=[FULL] * 4)
print(f"    full roster              : converged={clean[0]}")
degr = RR._check_gamma_alt_convergence(5, 0.6, HIST, cfg, gamma_critical=0.6,
                                       total_findings=9,
                                       roster_declared=FULL,
                                       live_by_round=[["CC2", "Codex"]] * 4)
print(f"    2 of 6 answered          : converged={degr[0]}")
if base[0] is not True:
    fails.append("the archived default path no longer converges -- regression")
if clean[0] is not True:
    fails.append("an intact roster was refused -- the wire is not behaviour-preserving")
if base[1] != clean[1].split(" [ROSTER")[0]:
    fails.append("the intact-roster reason string differs from the archived one "
                 "beyond the appended roster clause")
if degr[0] is not False:
    fails.append("a 2-of-6 roster still converged on 3 quiet rounds -- THE HAZARD "
                 "SURVIVES THE WIRE")
print(f"    identical evidence {HIST[-3:]}, different verdict: "
      f"{clean[0]} vs {degr[0]}")

# ── 4. A degraded convergence must be UNMISTAKABLE in the reason string. ──
print("\n[4] can a degraded convergence be reported as a clean one?")
degr_ok = RR._check_gamma_alt_convergence(
    11, 0.6, [2] + [0] * 10, cfg, gamma_critical=0.6, total_findings=9,
    roster_declared=FULL, live_by_round=[["CC2", "Codex"]] * 11)
print(f"    degraded run given 10 quiet rounds: converged={degr_ok[0]}")
print(f"    reason: ...{degr_ok[1][degr_ok[1].find('[**'):][:200]}")
if degr_ok[0] is not True:
    fails.append("a degraded run could not converge even at K_required -- that "
                 "blocks the run and violates requirement 8")
if "NOT REPORTABLE AS A CLEAN CONVERGENCE" not in degr_ok[1]:
    fails.append("a degraded convergence carries no marker -- it can be reported "
                 "as clean")
if "ROSTER CLEAN" not in clean[1]:
    fails.append("a clean convergence carries no positive roster attestation")
for tok in ("CC2", "Codex"):
    pass
if "absent:" not in degr_ok[1]:
    fails.append("the reason string does not name the absent seats")
print(f"    degraded verdict carries the marker, the counts, the absent seats and "
      f"the scaled window: True")

print("\n" + "=" * 62)
if fails:
    print("FALSIFIED")
    for f in fails:
        print("  -", f)
    raise AssertionError(f"{len(fails)} claim(s) falsified")
print("NOT FALSIFIED: the wire is reached, in scope, behaviour-preserving on the "
      "default path, and blocks the hazard.")
