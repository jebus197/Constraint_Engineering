# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'dynamic_roster_and_derived_ladder_2026-10-07', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 3f59be237398b6c355709559a9596097e7e0589c9e64b958b453319148f86d51
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""FALSIFIER for the no-cap default (founder ruling 2026-10-06, requirement 2).
Imports the REAL bench/routing.py; AssertionError iff the ladder is still
truncated at the default."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from routing import resolve_via_routing, route
import inspect

# The signature defaults: 0 = exhaust.
assert inspect.signature(resolve_via_routing).parameters["max_rungs"].default == 0
assert inspect.signature(route).parameters["max_rungs"].default == 0

# Behaviour: 6 rungs, none confirms -> ALL SIX are tried at the default
# (pre-ruling behaviour tried exactly 2). The self-rung then fires as rung 7.
asked = []
res = resolve_via_routing(
    {"finding_id": "C9999"},
    rungs=["m1", "m2", "m3", "m4", "m5", "m6"],
    resolve_fn=lambda m, f: asked.append(m) or "print('x')",
    reverify_fn=lambda code: "REFUTED",
    self_rung="src",
)
assert asked[:6] == ["m1", "m2", "m3", "m4", "m5", "m6"], \
    f"FALSIFIED: ladder truncated at default: {asked}"
assert res.rungs_tried == 7 and not res.resolved   # 6 rungs + self-rung

# The cap is STILL EXPRESSIBLE as opt-in spend-insurance (nothing removed).
asked2 = []
resolve_via_routing({"finding_id": "C9998"}, ["m1","m2","m3"],
                    lambda m, f: asked2.append(m) or "print('x')",
                    lambda c: "REFUTED", max_rungs=2)
assert asked2 == ["m1", "m2"], "FALSIFIED: opt-in cap no longer honoured"
print("OK: default exhausts the ladder; a positive cap remains expressible")
