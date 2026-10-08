# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'dynamic_roster_and_derived_ladder_2026-10-07', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: e6adb360b8ee03f8e78d1fec2028afaeab457495aff1741f25f5e91bdf02608f
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""What a researcher must do to add or remove a model -- and the one list that is
currently two.

THE ANSWER, AND IT IS SHORT BY DESIGN. Adding a model requires editing exactly ONE
thing: the `models` list in the experiment config. Nothing else, because:
  * `rank_falsifier_writers` (bench/routing.py:118) already appends labels absent
    from `DEFAULT_FALSIFIER_STRENGTH` AFTER the ranked ones, so the tuple is a
    priority prefix, not an allowlist. A new model is already tried, just last.
  * the derived key gives a 0-attempt seat a Wilson lower bound of exactly 0.0, so
    it also sorts last and then climbs on evidence. No placement decision.
So neither the ladder nor the estimator needs a human edit. That is the whole
benefit of ordering by a derived key (req 3) rather than by a stored list.

EXCEPT THAT THE ROSTER IS DECLARED TWICE, AND ONLY ONE OF THE TWO IS EDITED.
`exp_config.models` holds the ModelConfigs actually dispatched. `cfg.models` is a
separate List[str] whose default is a hardcoded five. reference_runner_v3.py
documents this itself at the top of `run_experiment` -- *"Every count, every
per-model denominator and every `set(cfg.models) - {source}` in this file reads the
second list"* -- and the runner's existing response is to PRINT A WARNING and
proceed, with *"every per-model denominator in this run uses the COUNTED list."*
A researcher who adds a model to the config and not to `cfg.models` therefore gets
a run that dispatches N+1 seats and scores N, and the only signal is a log line.
That is the launcher config-drop class the runner says it has now hit seven times.

WHAT THIS MODULE ADDS. `validate_roster` turns that warning into a refusal the
caller can act on, and `add_model_checklist` / `remove_model_checklist` state the
edits mechanically so the UX surface can execute them.

HOW IT MEETS THE UX DESIGN ALREADY ON FILE.
`experimental_notes/CDSFL_UX_Vision_Sketch_2026-03-28.md` specifies, for Model
Selection: *"The backend reads this from a configuration dataclass, not from
hardcoded values. The model list is extensible. When a new model becomes available,
the user adds it. No code change required."* A hardcoded default five IS a
hardcoded value, and it is exactly what makes a code change required. So this is not
a new requirement -- it is the one the sketch already set, unmet.

NOTE ON NAMING: the sketch's Phase Progression surface already asks for *"whether
any circuit breaker conditions have triggered"* and specifies a *"Circuit Breaker
Display"*, and already offers the researcher the option to *"proceed without the
failed model"*. So `bench/seat_circuit_breaker_2026-10-07.py` uses this project's
existing term, not a coined one. The sketch uses it for a single halt condition;
the three-state form (CLOSED / OPEN / HALF_OPEN) is the standard pattern's full
version and is a superset -- the halt is the OPEN state.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Sequence


def declared_roster(config_path: Path) -> list:
    """The `models` list a config declares. The single source of truth it should be."""
    d = json.loads(Path(config_path).read_text())
    return list(d.get("models") or [])


def validate_roster(dispatched: Sequence[str],
                    counted: Sequence[str]) -> Optional[str]:
    """REFUSE when the dispatched and counted rosters differ.

    The runner currently warns and proceeds. A per-model denominator computed over
    the wrong roster is a verification-integrity defect (CDSFL §10 category 3), not
    a cosmetic mismatch, so the honest response is a refusal the caller must handle.
    """
    d, c = set(dispatched), set(counted)
    if not d or d == c:
        return None
    return ("REFUSED: dispatched and counted rosters differ. "
            f"dispatched-not-counted={sorted(d - c)}, "
            f"counted-not-dispatched={sorted(c - d)}. Every per-model denominator "
            f"would be computed over the counted list.")


def add_model_checklist(label: str, config_path: Path,
                        strength_order: Sequence[str] = ()) -> dict:
    """The complete set of edits to add a seat. Deliberately 1 required item."""
    declared = declared_roster(config_path)
    return {
        "required": [] if label in declared else
                    [f"add {label!r} to 'models' in {config_path}"],
        "not_required": [
            f"{label!r} does NOT need adding to DEFAULT_FALSIFIER_STRENGTH: "
            f"rank_falsifier_writers appends unknown labels after the ranked ones",
            f"{label!r} does NOT need a capability estimate: 0 attempts gives a "
            f"Wilson lower bound of 0.0, so it sorts last and climbs on evidence",
            "no placement decision by a human is needed or permitted (req 3)",
        ],
        "must_also_hold": [
            "the counted roster must equal the dispatched roster "
            "(validate_roster), or per-model denominators are wrong",
            f"{label!r} must answer the aliveness probe, or its breaker opens and "
            f"it is re-probed -- not benched",
        ],
        "already_in_ladder": label in tuple(strength_order),
        "already_declared": label in declared,
    }


def remove_model_checklist(label: str, config_path: Path) -> dict:
    """Removing a seat is a POLICY act and must be distinguished from a fault.

    This is the requirement-9 boundary in operational form. Taking a model out of
    `models` is the researcher deciding it is not in the panel -- which is the
    permanent setting-aside the standing rule forbids the SYSTEM from doing, and
    which only the researcher may do, deliberately, with a reason recorded. A seat
    that merely stopped answering must NOT travel this path: that is a transient
    fault, and its route is the circuit breaker.
    """
    declared = declared_roster(config_path)
    return {
        "required": [f"remove {label!r} from 'models' in {config_path}",
                     "record the reason: removal is a policy act, not a fault",
                     "mirror the removal in the counted roster (validate_roster)"],
        "forbidden": [
            "do NOT remove a seat because it failed to answer -- that is a "
            "transient fault and belongs in seat_circuit_breaker_2026-10-07.py; "
            "removing it is benching, which the standing rule forbids",
        ],
        "consequence": [
            "the convergence record's seats_declared falls, so a later run is not "
            "labelled CONVERGED_DEGRADED_ROSTER for the absence of this seat -- "
            "which is correct, and is exactly why removal must be deliberate",
        ],
        "was_declared": label in declared,
    }
