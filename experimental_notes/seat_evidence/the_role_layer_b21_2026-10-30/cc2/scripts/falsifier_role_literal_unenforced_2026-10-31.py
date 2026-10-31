# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'the_role_layer_b21_2026-10-30', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 9736a47e5026e9bf157d1074c551b5fadf53d8ca7531982491fbc39969d69eef
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""FALSIFIER: `ModelConfig.role` accepts a spelling `Role` does not declare.

Imports the REAL target -- `bench.experiment_11_orchestrator` -- and constructs
real `ModelConfig` objects. Nothing is retyped or paraphrased.

FAILS IFF THE DEFECT IS PRESENT. The defect is that `Role` is a bare `Literal`
annotation that no runtime check reads, so a construction site may set a role
value outside the declared members and every downstream predicate silently
treats it as a reviewer. If any undeclared spelling SURVIVES construction
unchanged, this prints FALSIFIED and raises AssertionError. If every undeclared
spelling is either normalised to a declared member or rejected, it exits
cleanly: the defect is not demonstrated.

The two spellings tested are not invented. They are the ones an AST scan of
every live `ModelConfig(role=...)` call site finds outside the literal --
`player` at 9 sites, `reviewer` at 4 -- per
`scripts/how_many_role_values_does_the_code_construct_2026-10-31.py`.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import get_args

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bench.experiment_11_orchestrator import ExperimentConfig, ModelConfig, Role  # noqa: E402

DRIFTED = ["player", "reviewer"]          # found at live call sites by AST scan
MEMBERS = get_args(Role)

print(f"declared Role members : {list(MEMBERS)}")
print(f"spellings under test  : {DRIFTED}")

survived: list[str] = []
for spelling in DRIFTED:
    assert spelling not in MEMBERS, f"test premise wrong: {spelling!r} is declared"
    try:
        mc = ModelConfig(label="F", model_id="sim", api="sim",
                         role=spelling, system_prompt_path=None)
    except ValueError as exc:
        print(f"  {spelling!r:12} REJECTED at construction: {str(exc).split(';')[0]}")
        continue
    if mc.role not in MEMBERS:
        print(f"  {spelling!r:12} SURVIVED as {mc.role!r} -- outside {list(MEMBERS)}")
        survived.append(spelling)
    else:
        print(f"  {spelling!r:12} normalised to {mc.role!r}")

# The consequence, measured rather than asserted: a role-KEYED lookup misses a
# seat whose role is an undeclared synonym, while the `!= "collator"` dispatch
# filter does not. That asymmetry is what makes the drift latent.
probe = ModelConfig(label="P", model_id="sim", api="sim",
                    role=DRIFTED[0] if not survived else DRIFTED[0],
                    system_prompt_path=None)
found = ExperimentConfig(models=[probe]).get_by_role("participant")
print(f"  get_by_role('participant') finds the {DRIFTED[0]!r} seat : {len(found) == 1}")
print(f"  dispatch filter (role != 'collator') passes it          : {probe.role != 'collator'}")

if survived:
    print("FALSIFIED")
    raise AssertionError(
        f"`Role` is unenforced: {survived} survived construction outside "
        f"{list(MEMBERS)}. Every live read is `!= \"collator\"`, so such a seat "
        f"is dispatched as a reviewer while a role-keyed lookup misses it."
    )

print("CLEAN: no undeclared spelling survives construction; the defect is not demonstrated.")
