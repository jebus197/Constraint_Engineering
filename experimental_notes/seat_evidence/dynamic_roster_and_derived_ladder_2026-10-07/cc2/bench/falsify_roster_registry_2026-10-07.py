# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'dynamic_roster_and_derived_ladder_2026-10-07', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 74011419d0eccf697fdb23831cf90b496ef3994eb4c750823e386193f42af3c1
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""FALSIFIER for finding F5: the roster is declared twice and the mismatch only warns.

CLAIM: across the 47 experiment configs, `models` is the declared roster, 0 declare
Fable, and `RunnerConfig.models` defaults to a hardcoded five that differs from what
several configs dispatch -- and the runner's only response is a log line.
"""
import importlib.util, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "bench"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); sys.modules[name] = m
    spec.loader.exec_module(m); return m


RR = load(BENCH / "reference_runner_v3.py", "real_rrv3")
RT = load(BENCH / "routing.py", "real_routing2")
REG = load(BENCH / "roster_registry_2026-10-07.py", "real_roster_registry")

configs = sorted(BENCH.glob("*configs*/*.json"))
defects = []
print(f"configs found: {len(configs)}")
assert len(configs) == 47, f"expected 47 configs, found {len(configs)}"

rosters = {p: REG.declared_roster(p) for p in configs}
fable = [p.name for p, r in rosters.items() if "Fable" in r]
print(f"configs declaring Fable: {len(fable)}")
if not fable:
    defects.append(f"0 of {len(configs)} configs declare Fable, yet it is rung 6 of "
                   f"DEFAULT_FALSIFIER_STRENGTH {RT.DEFAULT_FALSIFIER_STRENGTH} -- "
                   f"an addition nothing reaches")

default_counted = set(RR.RunnerConfig().models)
print(f"RunnerConfig.models default = {sorted(default_counted)}")
mismatched = {p.name: sorted(set(r) ^ default_counted)
              for p, r in rosters.items() if r and set(r) != default_counted}
if mismatched:
    defects.append(f"{len(mismatched)} of {len(configs)} configs declare a roster "
                   f"differing from the hardcoded counted default; e.g. "
                   f"{list(mismatched.items())[:2]}")

src = (BENCH / "reference_runner_v3.py").read_text()
if "PANEL MISMATCH" in src:
    blk = src[src.index("PANEL MISMATCH") - 2000: src.index("PANEL MISMATCH") + 1200]
    raises = bool(re.search(r"PANEL MISMATCH[\s\S]{0,1400}?(raise |return \{)", blk))
    if not raises:
        defects.append("on PANEL MISMATCH the runner only calls _log and proceeds: "
                       "no raise and no refusal dict follows the warning")

if defects:
    print("\nFALSIFIED -- the defect is present:")
    for d in defects:
        print("  *", d)
else:
    print("defect NOT demonstrated"); sys.exit(0)

print()
print("---- the fix refuses what the runner only warns about ----")
r = REG.validate_roster(["CC2", "Codex", "Gemini", "DeepSeek", "ChatGPT", "Fable"],
                        ["CC2", "Codex", "Gemini", "DeepSeek", "ChatGPT"])
print("  " + r)
assert r is not None and "Fable" in r
assert REG.validate_roster(["A", "B"], ["B", "A"]) is None, "order must not matter"
assert REG.validate_roster([], ["A"]) is None, "an empty dispatch list is not a drop"

print()
print("---- adding a model requires exactly 1 edit ----")
cfgp = BENCH / "exp56_configs" / "d9_multi_model_panel.json"
chk = REG.add_model_checklist("Fable", cfgp,
                              strength_order=RT.DEFAULT_FALSIFIER_STRENGTH)
print(f"  required edits to add Fable: {len(chk['required'])}")
for x in chk["required"]:
    print("    -", x)
print(f"  already in ladder: {chk['already_in_ladder']}  "
      f"already declared: {chk['already_declared']}")
assert len(chk["required"]) == 1 and chk["already_in_ladder"] is True
# and the ladder genuinely needs no edit: an unknown label is still tried
unknown = RT.rank_falsifier_writers(["Codex", "BrandNewModel", "DeepSeek"])
print(f"  rank_falsifier_writers with an unknown label: {unknown}")
assert "BrandNewModel" in unknown and unknown[-1] == "BrandNewModel"
print("  -> a brand-new model is already tried, last. No ladder edit, confirmed.")

print()
print("---- removal is a POLICY act, kept distinct from a fault ----")
rem = REG.remove_model_checklist("DeepSeek", cfgp)
print(f"  required: {len(rem['required'])} items; forbidden: {rem['forbidden'][0][:80]}...")
assert any("benching" in f for f in rem["forbidden"])
assert any("reason" in x for x in rem["required"])

print()
print("---- the UX sketch already specifies both the term and the requirement ----")
ux = (ROOT / "experimental_notes" / "CDSFL_UX_Vision_Sketch_2026-03-28.md").read_text()
for phrase in ("Circuit Breaker Display", "proceed without the failed model",
               "not from hardcoded values", "No code change required"):
    assert phrase in ux, f"missing from the sketch: {phrase}"
    print(f"  sketch contains: {phrase!r}")
print("  -> the circuit-breaker term is this project's existing vocabulary, and the")
print("     'no hardcoded values / no code change required' requirement predates me.")

print()
print("FIX VERIFIED: the two-roster mismatch is refusable rather than merely logged, "
      "adding a model is 1 edit with no ladder or estimator change, and removal is "
      "separated from transient failure.")
