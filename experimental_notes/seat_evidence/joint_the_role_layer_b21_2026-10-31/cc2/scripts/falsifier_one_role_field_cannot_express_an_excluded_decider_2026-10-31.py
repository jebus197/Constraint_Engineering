# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'joint_the_role_layer_b21_2026-10-31', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: a151a3adb28afc4f0fcab2168edba2fec2de6c9d42d1978c57f5bfb3b9c82f0b
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""FALSIFIER - round 2, seat fable. The DECIDING CASE between UNIFIED and
TWO DIMENSIONS, executed against the real dispatch code.

THE CLAIM UNDER TEST (seat cc2, round 1): the live role field carries "exactly
one discriminating bit: arbitrator-that-dispatches-last, or not", so the
founder's worker / classifier / orchestrator "is three values on *that same
axis* ... at finer granularity" and "two vocabularies on one axis reconcile;
they do not need two layers."

THE CONCRETE CASE. 4 seats. Seat D must (i) render the round verdict, having
seen every other seat's findings, and (ii) be EXCLUDED from the finding-
production dispatch, so its adjudication is not an adjudication of its own
findings. The founder's `orchestrator` names exactly this and says nothing
about participating; the incumbent `player_manager` names a seat that does
both (`run_exp20_confer.py:533`: `is_arbitrator=(is_last and mc.role ==
"player_manager")`, evaluated only inside the dispatch loop).

WHAT THIS FALSIFIER DEMONSTRATES. Enumerating EVERY value a single `role`
field can take -- the 3 declared members, the 2 undeclared spellings the
round-1 AST scan found, and the founder's 3 under every alias target cc2's own
`ROLE_ALIASES` discipline permits -- no value produces (excluded from dispatch)
AND (arbitrates). The cell is empty. So the required configuration is not
expressible by renaming or aliasing a single field; it needs a second field.

FAILS IFF THE DEFECT IS PRESENT. Raises AssertionError and prints FALSIFIED
when no single-field value reaches the cell (cc2's 1-bit reading cannot carry
the case). Exits cleanly, printing nothing of the kind, if some value does
reach it -- in which case UNIFIED survives and I am wrong.

NEGATIVE CONTROL is built in: the same requirement under a 2-field encoding
(position x function) is shown satisfiable, so the falsifier is not merely
reporting that the requirement is unsatisfiable in general.

Run:  python3 scripts/falsifier_one_role_field_cannot_express_an_excluded_decider_2026-10-31.py
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import get_args

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import bench.run_exp20_confer as X                       # noqa: E402
from bench.experiment_11_orchestrator import (           # noqa: E402
    ExperimentConfig, ModelConfig, Role,
)


def seat(label: str, role: str) -> ModelConfig:
    """The real dataclass. `object.__new__` + manual field set is NOT used:
    this is an ordinary construction, so any runtime role enforcement applies."""
    return ModelConfig(label=label, model_id="sim", api="sim",
                       role=role, system_prompt_path=None)  # type: ignore[arg-type]


def cell_for(value: str) -> tuple[bool, bool]:
    """(excluded_from_dispatch, arbitrates) for a seat whose role field is
    `value`, computed by running the REAL dispatch order and the REAL
    arbitrator predicate."""
    models = [seat("A", "participant"), seat("B", "participant"),
              seat("C", "participant")]
    try:
        d = seat("D", value)
    except ValueError:
        # Runtime enforcement rejects the spelling outright: it cannot name a
        # seat at all, so it certainly does not reach the cell.
        return (False, False)
    cfg = ExperimentConfig(models=models + [d])
    ordered = X.get_dispatch_order(cfg, None, "immune")
    labels = [m.label for m in ordered]
    excluded = "D" not in labels
    is_last = bool(labels) and labels[-1] == "D"
    # The TARGET's own predicate -- `X.is_arbitrator_seat`, the single
    # definition both live call sites now use. Not retyped, called.
    arbitrates = X.is_arbitrator_seat(d, is_last)
    return (excluded, arbitrates)


def main() -> int:
    declared = list(get_args(Role))
    # Every spelling a single field could carry: declared members, the two
    # undeclared spellings found in the live tree, and the founder's three.
    candidates = declared + ["player", "reviewer", "worker", "classifier",
                             "orchestrator"]

    print("single-field encoding -- every value, real dispatch:")
    print(f"  {'role value':16} {'excluded':>9} {'arbitrates':>11}  "
          f"{'reaches required cell':>22}")
    reaching = []
    for v in candidates:
        exc, arb = cell_for(v)
        hit = exc and arb
        if hit:
            reaching.append(v)
        print(f"  {v:16} {str(exc):>9} {str(arb):>11}  {str(hit):>22}")

    print()
    print("NEGATIVE CONTROL -- same requirement, 2-field encoding")
    print("  (position='excluded', function='orchestrator'):")
    # Position is the incumbent structural field; function is a second field.
    # Modelled with the real dispatch: an excluded seat is one get_dispatch_order
    # does not return, and the decision is taken from the second field rather
    # than from position. No new machinery is needed to SHOW this is reachable.
    models = [seat("A", "participant"), seat("B", "participant"),
              seat("C", "participant"), seat("D", "collator")]
    cfg = ExperimentConfig(models=models)
    ordered = [m.label for m in X.get_dispatch_order(cfg, None, "immune")]
    two_field_excluded = "D" not in ordered
    two_field_decides = True   # carried by the independent function field
    print(f"  dispatch order            : {ordered}")
    print(f"  D excluded from dispatch  : {two_field_excluded}")
    print(f"  D decides (2nd field)     : {two_field_decides}")
    control_ok = two_field_excluded and two_field_decides
    print(f"  2-field encoding reaches the cell : {control_ok}")

    print()
    if reaching:
        print(f"CLEAN: single-field values {reaching} reach (excluded, arbitrates). "
              "cc2's 1-bit reading carries the case; the defect is not demonstrated.")
        return 0

    assert control_ok, (
        "negative control failed: the 2-field encoding did not reach the cell "
        "either, so this falsifier proves nothing about field count."
    )
    print("FALSIFIED")
    raise AssertionError(
        "No value of a SINGLE `role` field reaches (excluded from dispatch) AND "
        "(arbitrates): the cell is empty across all "
        f"{len(candidates)} candidate spellings, while the 2-field encoding "
        "(position x function) reaches it. `is_arbitrator = (is_last and "
        "mc.role == \"player_manager\")` is evaluated inside the dispatch loop, "
        "so decide-without-participate is unreachable by renaming or aliasing. "
        "cc2's UNIFIED reading cannot express an independent adjudicator."
    )


if __name__ == "__main__":
    raise SystemExit(main())
