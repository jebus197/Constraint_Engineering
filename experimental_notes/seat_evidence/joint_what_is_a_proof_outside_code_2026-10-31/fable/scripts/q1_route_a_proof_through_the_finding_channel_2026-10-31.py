# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'joint_what_is_a_proof_outside_code_2026-10-31', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 73e0bf865b2d7f90ff3e41a2cdc469d670dbe14ec7d9947390c9a92b5573e167
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Q1 attack, executed on the LIVE unmodified tree.

Constructs two REAL proof artefacts (proof polarity: clean exit <=> the
proposed result holds), re-runs each through `reverify_falsifier` (the real
step 4), then routes the resulting verdict through EVERY committed consumer
of `falsifier_verdict`:

  1. `spec_verification_factor` / `effective_severity`  (severity channel)
  2. `apply_falsifier_verdicts`                          (status/gate channel)
  3. `_settled_novelty_series` + `_estimate_gamma`       (convergence series)
  4. `unverified_critical_count`                         (blocker door)

No dict is hand-stamped with a verdict: the verdicts come from the harness
re-running the scripts.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bench.falsifier_verify import reverify_falsifier
from bench.reference_runner_v3 import (
    FindingRegistry, RunnerConfig, apply_falsifier_verdicts,
    spec_verification_factor, effective_severity, wire_module_mirrors,
    _settled_novelty_series, _estimate_gamma, CRITICAL_SEVERITY_THRESHOLD,
)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(REPO, "bench", "tests", "fixtures", "stem", "docs",
                   "MET-12-REF-01.md")

PROOF_HELD = f'''
import math, re
text = open({FIX!r}).read()
comps = [0.0392, 0.0049, 0.1206]          # the document's own components, %
assert all(("%.4f" % c) in text for c in comps), "components not in document"
rss = math.sqrt(sum(c*c for c in comps))
assert abs(rss - 0.1269) < 5e-4, "corrected RSS combination is 0.1269 per cent"
assert abs((0.0392 + 0.0049 + 0.1206) - 0.165) < 5e-4, \\
    "the document's 0.165 is the LINEAR sum, not RSS"
print("proof held: u_c(c)/c = %.4f per cent by RSS" % rss)
'''

PROOF_FAILED = f'''
import math
text = open({FIX!r}).read()
comps = [0.0392, 0.0049, 0.1206]
rss = math.sqrt(sum(c*c for c in comps))
assert abs(rss - 0.165) < 5e-4, "FALSIFIED"   # wrong: 0.165 is the linear sum
print("proof held")
'''

print("== step 4, real re-run (reverify_falsifier) ==")
v_held = reverify_falsifier(PROOF_HELD, repo_root=REPO)
v_failed = reverify_falsifier(PROOF_FAILED, repo_root=REPO)
print(f"  correct proof  -> {v_held}")
print(f"  mistaken proof -> {v_failed}")

print("\n== consumer 1: severity channel (spec ON) ==")
class _Cfg: severity_spec_enabled = True
wire_module_mirrors(_Cfg())
e_held = {"severity": 0.85, "falsifier_verdict": v_held}
e_failed = {"severity": 0.85, "falsifier_verdict": v_failed}
print(f"  V(correct proof)  = {spec_verification_factor(e_held)}   "
      f"effective_severity: 0.85 -> {effective_severity(e_held)}")
print(f"  V(mistaken proof) = {spec_verification_factor(e_failed)}   "
      f"effective_severity: 0.85 -> {effective_severity(e_failed)}")

print("\n== consumers 2-4: the gate itself, real registry ==")
from bench.dm._types import Finding
def _f(fid, sev, model):
    return Finding(finding_id=fid, model_id=model, round_idx=0, flaw_class=2,
                   severity=sev, abstraction_index=0.5,
                   description=f"MET-12 CM-06 proof-routing case {fid}")
cfg = RunnerConfig(falsifier_gate_enabled=True)
reg = FindingRegistry()
cid_crit = reg.register(_f("f1", 0.85, "m1"), "m1")
cid_non = reg.register(_f("f2", 0.50, "m2"), "m2")
cid_fail = reg.register(_f("f3", 0.85, "m3"), "m3")
reg.entries[cid_crit]["falsifier_code"] = PROOF_HELD
reg.entries[cid_non]["falsifier_code"] = PROOF_HELD
reg.entries[cid_fail]["falsifier_code"] = PROOF_FAILED
apply_falsifier_verdicts(reg, round_idx=1, cfg=cfg, repo_root=REPO)
for cid, label in ((cid_crit, "critical, proof HELD   "),
                   (cid_non,  "non-crit, proof HELD   "),
                   (cid_fail, "critical, proof FAILED ")):
    e = reg.entries[cid]
    print(f"  {label}: verdict={e.get('falsifier_verdict')!r:12} "
          f"status={e.get('status')!r:14} escalated={e.get('escalated')} "
          f"verified={e.get('verified')}")

print("\n== convergence series (asserted severity, terminal statuses dropped) ==")
all_s, crit_s = _settled_novelty_series(reg, 1)
print(f"  all_per_round={all_s}  critical_per_round={crit_s}")
try:
    n_block = reg.unverified_critical_count()
    print(f"  unverified_critical_count (blocker door) = {n_block}")
except Exception as ex:
    print(f"  blocker door raised: {ex!r}")

print("\n== gamma on cc2's hypothetical vs what the series actually permits ==")
print(f"  _estimate_gamma([4,3,2,1]) = {_estimate_gamma([4,3,2,1]):.4f}")
print(f"  _estimate_gamma([2,1,1,0]) = {_estimate_gamma([2,1,1,0]):.4f}")
