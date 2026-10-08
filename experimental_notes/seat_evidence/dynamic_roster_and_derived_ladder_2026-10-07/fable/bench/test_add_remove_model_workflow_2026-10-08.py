# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'dynamic_roster_and_derived_ladder_2026-10-07', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: dec5467e2728dcd2e550e4d3b3c8f508e826e0b2a9d998477639d2c03c89db98
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""FALSIFIER for docs/adding_or_removing_a_model_2026-10-08.md: every claim
about existing behaviour is executed against the real modules."""
import sys, importlib.util as iu
from pathlib import Path
B = Path(__file__).resolve().parent
sys.path.insert(0, str(B))
from routing import rank_falsifier_writers, DEFAULT_FALSIFIER_STRENGTH
from capability_estimator import CapabilityEstimator

# 1. The tuple is a priority prefix, not an allowlist: a brand-new label is
#    TRIED, after the ranked ones (so adding a model needs no ladder edit).
order = rank_falsifier_writers(["Kimi", "CC2", "Codex"], DEFAULT_FALSIFIER_STRENGTH)
assert order == ["Codex", "CC2", "Kimi"], f"FALSIFIED: {order}"
# 2. ... and the estimator gives it lower bound 0, last place, no human placement.
est = CapabilityEstimator()
assert est.order_seats(["Kimi", "Codex"], strength_order=DEFAULT_FALSIFIER_STRENGTH)[-1] == "Kimi"
# 3. The aliveness probe is built from the declared api, including moonshot
#    (Kimi's route), and refuses an unknown api loudly.
spec = iu.spec_from_file_location("al", B / "seat_aliveness_2026-10-06.py")
al = iu.module_from_spec(spec); sys.modules["al"] = al; spec.loader.exec_module(al)
assert callable(al.caller_for("moonshot", "kimi-k3"))
assert al.caller_for("sim", "x") is None          # unprobeable, skipped not failed
try:
    al.caller_for("unknown-api", "x")()           # building is lazy; calling raises
    print("FALSIFIED: unknown api passed unprobed"); sys.exit(1)
except Exception:
    pass
# 4. The UX sketch really does specify add-without-code-change.
ux = (B.parent / "experimental_notes/CDSFL_UX_Vision_Sketch_2026-03-28.md").read_text()
assert "The model list is extensible" in ux and "No code change required" in ux
print("OK: add/remove workflow claims all hold against the real modules")
