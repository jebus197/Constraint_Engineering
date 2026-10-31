# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'joint_what_is_a_proof_outside_code_2026-10-31', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: dcebc19481dfdfe4802544d76360e9e4b5a653f0c8b784d05b808f04c8c6afa3
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""FALSIFIER: `apply_falsifier_verdicts` reads a DECLARED proof-polarity
artefact as a finding falsifier.

Imports the REAL target module. The defect: `spec_verification_factor` now
consults `proof_polarity_collision` (seat cc2's round-1 guard), but the
verdict field has a SECOND gate-deciding consumer, `apply_falsifier_verdicts`,
which resolves statuses from the same string with no polarity check. So with
the round-1 guard fully in place, an entry that DECLARES proof polarity and
carries a CORRECT proof is still resolved status=REFUTED when non-critical --
silent evidence loss (core directives section 10, category 4) -- and a
MISTAKEN proof on a critical is still resolved status=CONFIRMED, verified=True,
at full asserted severity.

Raises AssertionError and prints FALSIFIED iff the defect is present.
Exits cleanly when the status channel honours the declared polarity.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from bench.reference_runner_v3 import (  # the REAL target, not a copy
    FindingRegistry, RunnerConfig, apply_falsifier_verdicts,
)
from bench.dm._types import Finding

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FIX = os.path.join(REPO, "bench", "tests", "fixtures", "stem", "docs",
                   "MET-12-REF-01.md")

PROOF_HELD = f'''
import math
text = open({FIX!r}).read()
comps = [0.0392, 0.0049, 0.1206]
rss = math.sqrt(sum(c*c for c in comps))
assert abs(rss - 0.1269) < 5e-4, "corrected RSS combination is 0.1269 per cent"
print("proof held")
'''
PROOF_FAILED = f'''
import math
comps = [0.0392, 0.0049, 0.1206]
rss = math.sqrt(sum(c*c for c in comps))
assert abs(rss - 0.165) < 5e-4, "FALSIFIED"
'''

def _f(fid, sev, model):
    return Finding(finding_id=fid, model_id=model, round_idx=0, flaw_class=2,
                   severity=sev, abstraction_index=0.5,
                   description=f"declared-proof routing case {fid}")

cfg = RunnerConfig(falsifier_gate_enabled=True)
reg = FindingRegistry()
cid_non = reg.register(_f("p1", 0.50, "m1"), "m1")   # non-crit, held proof
cid_crit = reg.register(_f("p2", 0.85, "m2"), "m2")  # critical, failed proof
for cid, code in ((cid_non, PROOF_HELD), (cid_crit, PROOF_FAILED)):
    reg.entries[cid]["falsifier_code"] = code
    reg.entries[cid]["verification_polarity"] = "proof"   # the DECLARED sense

apply_falsifier_verdicts(reg, round_idx=1, cfg=cfg, repo_root=REPO)

e_non, e_crit = reg.entries[cid_non], reg.entries[cid_crit]
bad = []
if e_non.get("status") == "REFUTED":
    bad.append(f"non-critical with a DECLARED correct proof was silently "
               f"retired: status={e_non.get('status')!r}")
if e_crit.get("status") == "CONFIRMED" or e_crit.get("verified"):
    bad.append(f"critical with a DECLARED mistaken proof was confirmed as a "
               f"real defect: status={e_crit.get('status')!r} "
               f"verified={e_crit.get('verified')}")

if bad:
    print("FALSIFIED")
    for b in bad:
        print("  " + b)
    raise AssertionError("the status channel is polarity-blind: " + "; ".join(bad))

print("NOT FALSIFIED: the status channel honours declared proof polarity "
      f"(non-crit status={e_non.get('status')!r}, "
      f"crit status={e_crit.get('status')!r}, "
      f"crit proof_tristate={e_crit.get('proof_tristate')!r}, "
      f"non-crit proof_tristate={e_non.get('proof_tristate')!r})")
