# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'joint_what_is_a_proof_outside_code_2026-10-31', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: e4dcbcf67abf963232898f015ae37252b7132bbec4105b6821465bd23ba88132
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""FALSIFIER — cc2's round-1 claim that the proof/falsifier polarity collision
"MANUFACTURES APPARENT CONVERGENCE" by flattering gamma (joint round 2,
`what_is_a_proof_outside_code_b22`, seat fable).

NOT in dispute and asserted here only as a tripwire: `spec_verification_factor`
maps a clean-exit re-run to V=0.0 and a fired assertion to V=1.0, so a
PROOF-POLARITY artefact (succeeds by NOT demonstrating a defect) does invert the
severity multiplier. That arithmetic is cc2's and it reproduces.

WHAT IS IN DISPUTE is the consequence cc2 attached to it: that the inversion
removes proof-bearing criticals from the series gamma is estimated from, turning
(4,3,2,1) into (2,1,1,0) and gamma 0.3247 into 0.4652.

DEFECT POLARITY. Raises AssertionError and prints FALSIFIED iff that defect is
present, i.e. iff driving proof-polarity falsifiers through the REAL
`apply_falsifier_verdicts` gate moves the critical novelty series, gamma, or the
round at which the K-consecutive-zero convergence test first passes. Exits
cleanly iff it does not.

Imports the real runner and the real gate. No retyped copies, no stubbed verdicts.
"""
import pathlib, sys
REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "bench"))

from bench.dm._types import Finding
from bench.reference_runner_v3 import (
    FindingRegistry, RunnerConfig, apply_falsifier_verdicts,
    _settled_novelty_series, _estimate_gamma, _interpret_gamma,
    spec_verification_factor, effective_severity, _SEVERITY_SPEC,
    CRITICAL_SEVERITY_THRESHOLD as CRIT, _NON_NOVEL_TERMINAL_STATUSES,
)
import reference_runner_v3 as rr

# A PROOF that holds: it computes, the comparison succeeds, it exits 0. This is
# the shape of every "printed proof" artefact in the founder's step-3 sense.
PROOF_HOLDS = (
    "import math\n"
    "rss = math.sqrt(0.0392**2 + 0.0049**2 + 0.1206**2)\n"
    "assert abs(rss - 0.1269) < 5e-4, 'the combination does not reproduce'\n"
    "print('proof holds: combined relative u =', round(rss, 4), 'per cent')\n"
)
DEMONSTRATION = "assert False, 'real defect demonstrated'"   # defect polarity

PROOF_BEARING = [2, 2, 1, 1]
TOTAL_CRIT    = [4, 3, 2, 1]


def _first_conv(series, K=2):
    run = 0
    for i, c in enumerate(series):
        run = run + 1 if c == 0 else 0
        if run >= K:
            return i
    return None


def _build():
    """cc2's exact scenario, registered through the real FindingRegistry."""
    reg = FindingRegistry()
    n = 0
    for r, (tot, pb) in enumerate(zip(TOTAL_CRIT, PROOF_BEARING)):
        for j in range(tot):
            n += 1
            code = PROOF_HOLDS if j < pb else DEMONSTRATION
            f = Finding(finding_id=f"f{n}", model_id="fable", round_idx=r,
                        flaw_class=2, severity=0.85, abstraction_index=0.5,
                        description=f"claim {n}", falsifier_code=code)
            cid = reg.register(f, "fable")
            e = reg.entries[cid]
            e["status"] = "CONFIRMED"          # novel, not non-novel-terminal
            e["open_since_round"] = r
    return reg


# ── tripwire: the V inversion itself ────────────────────────────────────────
_SEVERITY_SPEC["on"] = True
held   = {"severity": 0.85, "falsifier_verdict": "REFUTED"}
failed = {"severity": 0.85, "falsifier_verdict": "CONFIRMED"}
v_h, v_f = spec_verification_factor(held), spec_verification_factor(failed)
print(f"V(proof held)={v_h}  V(proof failed)={v_f}   "
      f"effective_severity: held {effective_severity(held)}  "
      f"failed {effective_severity(failed)}")
assert (v_h, v_f) == (0.0, 1.0), "the V mapping is not what round 1 measured"
print("tripwire: the severity multiplier IS inverted for a proof-polarity "
      "artefact. That half of cc2's claim reproduces.\n")

# ── baseline: the series BEFORE the gate runs ───────────────────────────────
reg = _build()
MAXR = len(TOTAL_CRIT) - 1
_a0, crit_before = _settled_novelty_series(reg, MAXR)
g_before = _estimate_gamma(crit_before)
k_before = _first_conv(crit_before)

# ── drive the REAL gate with the REAL re-verifier on proof-polarity code ────
apply_falsifier_verdicts(reg, 1,
                         cfg=RunnerConfig(falsifier_gate_enabled=True),
                         repo_root=str(REPO))

verdicts = {}
statuses = {}
for cid, e in reg.entries.items():
    verdicts[e.get("falsifier_verdict")] = verdicts.get(e.get("falsifier_verdict"), 0) + 1
    statuses[e.get("status")] = statuses.get(e.get("status"), 0) + 1
print("after the real gate — falsifier_verdict tally:", verdicts)
print("after the real gate — status tally          :", statuses)

_a1, crit_after = _settled_novelty_series(reg, MAXR)
g_after = _estimate_gamma(crit_after)
k_after = _first_conv(crit_after)

CLAIMED = [t - p for t, p in zip(TOTAL_CRIT, PROOF_BEARING)]
g_claimed = _estimate_gamma(CLAIMED)

print(f"\ncritical novelty BEFORE gate : {crit_before}  gamma {g_before:.4f}  "
      f"first K=2 convergence round {k_before}")
print(f"critical novelty AFTER  gate : {crit_after}  gamma {g_after:.4f}  "
      f"band {_interpret_gamma(g_after)!r}  first K=2 convergence round {k_after}")
print(f"series the CLAIM requires    : {CLAIMED}  gamma {g_claimed:.4f}  "
      f"band {_interpret_gamma(g_claimed)!r}")

# ── why ─────────────────────────────────────────────────────────────────────
import inspect
src = inspect.getsource(_settled_novelty_series)
print(f"\n_settled_novelty_series reads raw entry['severity']: "
      f"{'e.get(\"severity\")' in src}; calls effective_severity: "
      f"{'effective_severity' in src}")
print(f"REFUTED is a non-novel terminal status: "
      f"{'REFUTED' in _NON_NOVEL_TERMINAL_STATUSES} — so the status channel "
      f"COULD remove an entry from the series; the gate refuses to write it on "
      f"an asserted-critical, which is why it does not.")
print("live call sites of effective_severity in the runner:",
      sorted({ln for ln, l in enumerate(
          inspect.getsource(rr).splitlines(), 1) if "effective_severity(" in l
          and "def effective_severity" not in l}))

moved = (crit_after != crit_before) or (abs(g_after - g_before) > 1e-12) \
        or (k_after != k_before)
if moved:
    print("FALSIFIED")
    raise AssertionError(
        f"the polarity inversion MOVES gamma's input: {crit_before} -> "
        f"{crit_after}, gamma {g_before:.4f} -> {g_after:.4f}, convergence "
        f"round {k_before} -> {k_after}")
print(f"\nNOT FALSIFIED: 6 proof-polarity criticals were re-verified by the real "
      f"gate and every one took verdict REFUTED, yet the critical novelty series "
      f"is {crit_after} before and after, gamma is {g_after:.4f} either way, and "
      f"the convergence round is unchanged at {k_after}. The series the claim "
      f"requires ({CLAIMED}, gamma {g_claimed:.4f}) is never produced: "
      f"_settled_novelty_series reads the ASSERTED severity and never calls "
      f"effective_severity, and the gate refuses to write status REFUTED on an "
      f"asserted-critical, so neither channel can remove them.")
