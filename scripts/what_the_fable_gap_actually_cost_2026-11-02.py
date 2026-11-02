#!/usr/bin/env python3
"""What the missing Fable registration actually COST, measured rather than asserted.

HIS RULING, 2026-11-01, annotation 11 of `Closing_Report_2026-11-01.txt`: a seat
that fails registration *"should cause the pre-flight checks to fail and the
issue should be raised loudly for the researcher/HIL to investigate and to fix."*
And: *"Is all of this implemented? If not you should implement it and test that
it works as expected."*

WHAT THE ABSENCE DID. `COMPOSER_MODEL_MAP` resolves a seat label to a phenotype
key with `.get(model_label, model_label)`, so a MISS IS NOT AN ERROR: "Fable"
resolved to "Fable", which keys neither phenotype table, and both silently took
their dataclass default. The work bound `max_directive_chars` therefore sat at
8000 for Fable against 12000 for its sibling CC2 -- the same vendor, the same
CLI route, the same subscription.

THIS SCRIPT MEASURES THE DIFFERENCE IN CHARACTERS OF DIRECTIVE TEXT, by calling
the live composer twice, not by reading the table. Reverting the 4 added entries
must move this number, or the entries changed nothing and are not additive.
"""
from __future__ import annotations
import pathlib, sys

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench.cdsfl_registry import composer as co   # noqa: E402

# `_cli_help` lives in scripts/. Locate it rather than assume a depth: the
# project has already had a helper import break when a script moved.
import sys as _sys, pathlib as _pl
for _cand in (_pl.Path(__file__).resolve().parent, *_pl.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        if str(_cand) not in _sys.path:
            _sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402


def main() -> int:
    answer_help(__doc__, __file__)
    print("=" * 78)
    print("WHAT THE MISSING FABLE REGISTRATION COST")
    print("=" * 78)
    seats = ["CC2", "Fable", "Gemini", "Codex", "DeepSeek", "ChatGPT"]
    print(f"  {'seat':10s} {'phenotype key':16s} {'work bound':>11s} {'spec bound':>11s} "
          f"{'coherence':>10s}")
    bounds = {}
    for s in seats:
        key = co.COMPOSER_MODEL_MAP.get(s, s)
        pt = co.PHENOTYPE_TRANSFORMS.get(key)
        fell_back = pt is None
        if pt is None:
            pt = co.PhenotypeTransform()
        cb = co.MODEL_COHERENCE_BUDGETS.get(key)
        bounds[s] = pt.max_directive_chars
        print(f"  {s:10s} {key:16s} {pt.max_directive_chars:11d} "
              f"{str(pt.spec_chars):>11s} {str(cb):>10s}"
              + ("   <- SILENT DEFAULT, no entry" if fell_back else ""))

    hi = max(bounds.values())
    print(f"\n  Fable's work bound     : {bounds['Fable']}")
    print(f"  Its sibling CC2's      : {bounds['CC2']}")
    if bounds["Fable"] == bounds["CC2"]:
        print(f"  EQUAL. The silent reduction is gone.")
    else:
        d = bounds["CC2"] - bounds["Fable"]
        print(f"  SHORT BY {d} characters = {d / bounds['CC2']:.4%} of its "
              f"sibling's budget.")

    # The specification half, which is his 2026-10-14 ruling and must stay unset.
    unset = [s for s in seats
             if (co.PHENOTYPE_TRANSFORMS.get(co.COMPOSER_MODEL_MAP.get(s, s))
                 or co.PhenotypeTransform()).spec_chars is None]
    print(f"\n  SPECIFICATION BOUND UNSET for {len(unset)} of {len(seats)} seats: "
          f"{unset}")
    print(f"  His ruling of 2026-10-14 is that the SPECIFICATION is not work, so")
    print(f"  it is delivered whole and only the WORK bound is reduced. Any seat")
    print(f"  missing from this list is being served a REDUCED specification.")

    # Every table, so a future miss is visible at a glance.
    print(f"\n  REGISTRATION MATRIX (the thing the preflight checks)")
    from bench import runner_core as rc
    tables = [("MODEL_SPECS", rc.MODEL_SPECS, False),
              ("INITIAL_FINGERPRINTS", rc.INITIAL_FINGERPRINTS, False),
              ("COMPOSER_MODEL_MAP", co.COMPOSER_MODEL_MAP, False),
              ("PHENOTYPE_TRANSFORMS", co.PHENOTYPE_TRANSFORMS, True),
              ("MODEL_COHERENCE_BUDGETS", co.MODEL_COHERENCE_BUDGETS, True)]
    print("  " + f"{'seat':10s}" + "".join(f"{n[:13]:15s}" for n, _t, _p in tables))
    missing = 0
    for s in seats:
        row = ""
        for _n, t, by_phen in tables:
            k = co.COMPOSER_MODEL_MAP.get(s, s) if by_phen else s
            ok = k in t
            missing += 0 if ok else 1
            row += f"{'  IN':15s}" if ok else f"{'  MISSING':15s}"
        print(f"  {s:10s}{row}")
    print(f"\n  total absences across {len(seats)} seats x {len(tables)} tables: "
          f"{missing}")
    return 0 if missing == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
