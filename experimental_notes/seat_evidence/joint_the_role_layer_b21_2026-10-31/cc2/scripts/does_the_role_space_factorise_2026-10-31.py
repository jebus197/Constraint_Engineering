# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'joint_the_role_layer_b21_2026-10-31', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: fb0e78cae539dfe606d71172af370efe36a4e0e2242526b6fe45e7396743e54c
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Round 2, seat fable - does the live role space FACTORISE into 2 axes, or not?

Round 1 left cc2 (UNIFIED: 1 dimension, 1 discriminating bit, 4 spellings) and
fable (NEITHER: 2 dimensions, 1 layer) disagreeing. This instrument decides the
disagreement MECHANICALLY rather than by argument, by executing the real
dispatch and prompt-construction code.

Sub-questions, each answered by execution, never by re-implementation:

  A. CELL COUNT. How many distinct behavioural cells do the live role-reading
     predicates induce on `ModelConfig.role`? cc2 says 1 bit (2 cells).
  B. 4th-CELL REACHABILITY. Is (not dispatched) AND (arbitrates) reachable for
     ANY single value of a single `role` field?
  C. FACTORIAL. Vary the STRUCTURAL input (is_arbitrator) and the FUNCTIONAL
     input (the policy-selected classification directive) independently.
  D. ROLE-BLINDNESS of the policy engine (`composer.py`, `registry.py`).
  E. THE OTHER DECLARATION. Does `bench.dm` construct a collator-class seat?
     cc2's AST scan covered `ModelConfig(role=<literal>)` only, and named this
     as its own weakest link (its refutation condition 1).
  F. Z3 on the factorisation question itself.

Run:  python3 scripts/does_the_role_space_factorise_2026-10-31.py
"""
from __future__ import annotations

import inspect
import itertools
import math
import re
import sys
from pathlib import Path
from typing import get_args

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import bench.run_exp20_confer as X                      # noqa: E402
from bench.experiment_11_orchestrator import (          # noqa: E402
    ExperimentConfig, ModelConfig, Role,
)

SEP = "=" * 78


def _mc(label: str, role: str) -> ModelConfig:
    """A real ModelConfig - the real dataclass, the real fields, no retyping."""
    return ModelConfig(
        label=label, model_id="sim", api="sim", role=role,  # type: ignore[arg-type]
        system_prompt_path=None,
    )


def cells_for_role_values(values):
    """EXECUTE the real dispatch ordering + the real arbitrator predicate."""
    out = {}
    for v in values:
        cfg = ExperimentConfig(models=[_mc("other", "participant"), _mc("under_test", v)])
        ordered = X.get_dispatch_order(cfg, None, "immune")
        labels = [m.label for m in ordered]
        dispatched = "under_test" in labels
        is_last = bool(labels) and labels[-1] == "under_test"
        # The real arbitrator predicate, verbatim from run_exp20_confer.py:533.
        arbitrates = dispatched and is_last and v == "player_manager"
        out[v] = (dispatched, is_last, arbitrates)
    return out


STRUCTURAL_MARK = "## Your Role: ARBITRATOR"
FUNCTIONAL_MARK = "classify each finding as PATCH / NOVEL CONSTRUCT"


def functional_directive():
    """The classification directive AS THE POLICY ENGINE HOLDS IT (live read)."""
    import bench.cdsfl_registry.composer as C
    return C._PRESET_THREE_LAYER_SCHEMA


def factorial_prompts():
    directive = functional_directive()
    out = {}
    for struct, func in itertools.product([False, True], repeat=2):
        p = X._build_confer_prompt(
            task_key="immune", round_label="R1", round_type="blind",
            code="pass", math_appendix="", verification_chain="",
            interface_summary="", dispatch_position=1, total_models=2,
            is_arbitrator=struct,
        )
        # The functional directive is injected by the POLICY composer, a
        # separate input path from is_arbitrator. Concatenation models what the
        # runner does: system prompt (policy) + task prompt (position/role).
        out[(struct, func)] = (directive if func else "") + p
    return out


def policy_engine_role_blindness():
    import bench.cdsfl_registry.registry as R
    import bench.cdsfl_registry.composer as C
    counts = {}
    for mod in (R, C):
        path = Path(inspect.getsourcefile(mod))
        counts[path.name] = len(re.findall(r"\brole\b", path.read_text(encoding="utf-8"),
                                          flags=re.IGNORECASE))
    return {
        "load_effective_policy_params": list(inspect.signature(R.load_effective_policy).parameters),
        "compose_params_matching_role": [p for p in inspect.signature(C.compose).parameters
                                         if "role" in p],
        "word_role_occurrences": counts,
    }


def dm_axis():
    from bench.dm._role_assignment import RoleAssignment
    from bench.dm._types import (
        CapabilityFingerprint as DMFP, DynamicManagementConfig, ModelSpec,
        Role as DMRole,
    )
    cfg = DynamicManagementConfig()
    models = [
        ModelSpec("m1", DMFP(0.9, 0.9, 0.9, 0.9)),
        ModelSpec("m2", DMFP(0.5, 0.8, 0.6, 0.5)),
        ModelSpec("m3", DMFP(0.2, 0.3, 0.4, 0.3)),
    ]
    ra = RoleAssignment.assign(models, cfg)
    assigned = sorted({r.value for r in ra.role_map.values()})
    return {
        "dm_Role_members": [r.value for r in DMRole],
        "dm_assigned_values": assigned,
        "dm_constructs_collator": DMRole.COL.value in assigned,
        "role_map": {k: v.value for k, v in ra.role_map.items()},
    }


def main() -> int:
    declared = list(get_args(Role))
    candidates = declared + ["player", "reviewer"]

    print(SEP); print("A. CELL COUNT on the ModelConfig axis (executed, real dispatch)"); print(SEP)
    cells = cells_for_role_values(candidates)
    print(f"{'role value':16} {'dispatched':>11} {'is_last':>8} {'arbitrates':>11}")
    for v, (d, l, a) in cells.items():
        print(f"{v:16} {str(d):>11} {str(l):>8} {str(a):>11}")
    distinct = sorted({(d, a) for (d, _l, a) in cells.values()})
    print(f"\ndistinct (dispatched, arbitrates) cells : {len(distinct)}  -> {distinct}")
    print(f"bits carried by the role field          : log2({len(distinct)}) = "
          f"{math.log2(len(distinct)):.6f}")
    print(f"cc2's claim of exactly 1 bit (2 cells)  : "
          f"{'HOLDS' if len(distinct) == 2 else 'REFUTED by execution'}")

    print(); print(SEP); print("B. 4th-CELL REACHABILITY: (not dispatched) AND (arbitrates)"); print(SEP)
    fourth = [v for v, (d, _l, a) in cells.items() if (not d) and a]
    print(f"role values reaching (not dispatched, arbitrates) : {fourth}")
    print(f"reachable with a SINGLE role field                : {bool(fourth)}")

    print(); print(SEP); print("C. 2x2 FACTORIAL: structural arbitrator x functional classifier"); print(SEP)
    fp = factorial_prompts()
    rows = []
    for (struct, func), text in sorted(fp.items()):
        rows.append((struct, func, STRUCTURAL_MARK in text, FUNCTIONAL_MARK in text))
    print(f"{'is_arbitrator':>13} {'policy=classify':>16} {'ARBITRATOR blk':>15} {'classify blk':>13}")
    for s_, f_, sm, fm in rows:
        print(f"{str(s_):>13} {str(f_):>16} {str(sm):>15} {str(fm):>13}")
    reachable = sum(1 for s_, f_, sm, fm in rows if sm == s_ and fm == f_)
    all_distinct = len(set(fp.values())) == 4
    struct_determines_func = (len({fm for s_, f_, sm, fm in rows if s_}) == 1
                              and len({fm for s_, f_, sm, fm in rows if not s_}) == 1)
    print(f"\ncells whose output matches its input    : {reachable}/4")
    print(f"all 4 prompts textually distinct        : {all_distinct}")
    print(f"structural input determines functional  : {struct_determines_func}")

    print(); print(SEP); print("D. ROLE-BLINDNESS of the policy engine"); print(SEP)
    for k, v in policy_engine_role_blindness().items():
        print(f"{k:32} : {v}")

    print(); print(SEP); print("E. THE OTHER DECLARATION - bench.dm (cc2 refutation condition 1)"); print(SEP)
    for k, v in dm_axis().items():
        print(f"{k:24} : {v}")

    print(); print(SEP)
    print("F. Z3: does a single-field encoding of the founder's 3 values exist")
    print("   over the incumbent cells measured in A?")
    print(SEP)
    import z3
    EXCL, PLAIN, DECIDE = 0, 1, 2
    g_worker, g_classifier, g_orch = z3.Ints("g_worker g_classifier g_orch")
    s = z3.Solver()
    for g in (g_worker, g_classifier, g_orch):
        s.add(z3.Or(g == EXCL, g == PLAIN, g == DECIDE))
    s.add(g_orch == DECIDE)      # R1: the deciding seat is dispatched and last
    s.add(g_worker == PLAIN)     # R2: a worker is dispatched and does not decide
    s.add(g_classifier != g_worker)   # R3: the 3 values must be distinguishable
    s.add(g_classifier != g_orch)
    r1 = s.check()
    print("single field, 3 founder values -> 3 incumbent cells :", r1)
    if r1 == z3.sat:
        m = s.model()
        print("   forced model :", {str(d): m[d].as_long() for d in m.decls()})
    s.push(); s.add(g_classifier != EXCL)   # measured in C: a classifier IS dispatched
    r2 = s.check()
    print("same, plus measured fact 'a classifier is dispatched':", r2)
    s.pop()
    # And the two-field encoding, for contrast.
    pos_c, fun_c = z3.Ints("pos_classifier fun_classifier")
    s2 = z3.Solver()
    s2.add(z3.Or(pos_c == PLAIN, pos_c == DECIDE))   # dispatched, either position
    s2.add(fun_c == 1)                                # function = classify
    print("two-field encoding (position x function)            :", s2.check())
    print()
    print(f"VERDICT-RELEVANT: single-field UNSAT={r2 == z3.unsat}, "
          f"two-field SAT={s2.check() == z3.sat}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
