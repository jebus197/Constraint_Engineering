# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'rung_promotion_and_model_ids_2026-10-08', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 0e7bcf6583245119a0ba60307a4dd904e1e3095db239216595b5b323f5f47464
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Falsifier: `rungs_tried` under strongest-first routing is a LEFT-CENSORED
difficulty label, not the measured difficulty the 2026-10-08 brief claims.

Imports the REAL bench/routing.py and drives resolve_via_routing with a
deterministic capability model: model strength s, finding difficulty d,
confirm iff s >= d. Strongest-first means every finding the strongest model
can confirm gets rungs_tried == 1 REGARDLESS of how easy it is, so the label
cannot distinguish any two difficulties below the top model's ceiling.

FAILS (AssertionError) iff rungs_tried DOES separate sub-ceiling difficulties
under strongest-first order -- i.e. iff the brief's reconciliation claim holds
as stated. Exits cleanly iff the label is censored as this falsifier claims,
and shows the weakest-first order recovers the full difficulty ranking.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bench.routing import resolve_via_routing  # noqa: E402  -- REAL module

STRENGTH = {"M5": 5, "M4": 4, "M3": 3, "M2": 2, "M1": 1}   # M5 strongest
LADDER_STRONG_FIRST = ["M5", "M4", "M3", "M2", "M1"]
LADDER_WEAK_FIRST = list(reversed(LADDER_STRONG_FIRST))


def resolve_fn(model, finding):
    # deterministic: a model emits a working falsifier iff strong enough
    return "ok" if STRENGTH[model] >= finding["difficulty"] else "broken"


def reverify_fn(code):
    return "CONFIRMED" if code == "ok" else "REFUTED"


def depths(ladder):
    out = {}
    for d in (1, 2, 3, 4, 5):
        r = resolve_via_routing({"finding_id": f"F{d}", "difficulty": d},
                                ladder, resolve_fn, reverify_fn, max_rungs=0)
        out[d] = (r.rungs_tried, r.resolved)
    return out


strong = depths(LADDER_STRONG_FIRST)
weak = depths(LADDER_WEAK_FIRST)
print(f"  strongest-first rungs_tried by true difficulty: "
      f"{ {d: v[0] for d, v in strong.items()} }")
print(f"  weakest-first   rungs_tried by true difficulty: "
      f"{ {d: v[0] for d, v in weak.items()} }")

# Under strongest-first, every difficulty M5 can handle resolves at rung 1.
censored = {v[0] for d, v in strong.items() if d <= 5}
assert censored == {1}, (
    "FALSIFIED: strongest-first rungs_tried separated sub-ceiling "
    f"difficulties ({censored}) -- the brief's claim would stand")
# Under weakest-first, rungs_tried IS the difficulty rank (depth d needs the
# d-th weakest model), at the cost of d-1 wasted dispatches per finding.
assert all(weak[d][0] == d for d in (1, 2, 3, 4, 5)), "weak-first not rank"
wasted = sum(weak[d][0] - 1 for d in (1, 2, 3, 4, 5))
print(f"  weakest-first recovers the full ranking at the cost of {wasted} "
      f"extra dispatches over 5 findings (strongest-first: 0 extra)")
print("CONFIRMED: rungs_tried is left-censored at 1 under the live "
      "strongest-first order; it measures difficulty ONLY above the top "
      "model's ceiling. The brief's reconciliation holds only for the "
      "minority of findings the strongest rung fails (1 of 7 in Exp 42).")
