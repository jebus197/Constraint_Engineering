#!/usr/bin/env python3
"""Re-derive `resources/MEMORY_EXCLUSIONS.md` from the private memory directory.

WHY THIS EXISTS, AND IT IS THE GATE'S OWN LESSON APPLIED TO THE ONE LEDGER THAT
MISSED IT. `hooks/pre-commit` carries 3 REPAIR stages that run BEFORE its
guards -- the Desktop mirror, the experiment run ledger and the citation
content guard -- and its own comment states the reason:

    WHY IT RUNS FIRST, AND IT DID NOT UNTIL 2026-09-10. This was the LAST
    stage, after the guards. One of the guards is the mirror drift check. So a
    commit that edited a mirrored file made that guard red, the hook exited 1,
    and the stage that would have repaired the drift was never reached -- the
    repair sat downstream of the check that needed it. ... ORDER IS THE WHOLE
    FIX: repair first, then check.

THE MEMORY EXCLUSIONS LEDGER IS THE ONE LEDGER WHOSE CHECK IS INSIDE THE GATE
AND WHOSE REPAIR IS NOT. 2 guards read it --
`test_documentation_drift_guards_2026-08-25.test_memory_ledger_total_matches_the_directory`
and `test_recovery_memory_doc_repairs.TestMemoryExclusionsAccounting` -- and
both sit in the gate's board. The derivation that fixes them,
`cdsfl_sv._update_memory_exclusions_ledger`, has existed since commit `b312b84`
on 2026-08-23 and runs only inside a full `sv`, which commits and pushes and so
cannot be invoked from a pre-commit hook.

MEASURED COST, 2026-11-07: writing a memory file outside `sv` drifted the
ledger TWICE in one session, 322 -> 323 and then 324 -> 325, and each drift
refused a commit AFTER its 11-minute board had already run. The ledger's own
file records 7 consecutive manual corrections before these 2. The gate was
right every time; the board time was wasted every time.

THIS SCRIPT IS THE MISSING SEAM: it calls the existing derivation and nothing
else, so there is exactly 1 implementation of the rule. It never commits, never
pushes, and prints what it did. `--check` reports drift WITHOUT writing, for a
caller that wants to know rather than to fix.

Exit 0 when the ledger is correct afterwards, 1 when it could not be made so.
"""
from __future__ import annotations

import argparse
import importlib.util
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent


def _sv():
    """The 1 implementation of the rule, loaded rather than reimplemented."""
    spec = importlib.util.spec_from_file_location(
        "cdsfl_sv_for_ledger", REPO / "scripts" / "cdsfl_sv.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["cdsfl_sv_for_ledger"] = mod
    sys.path.insert(0, str(REPO / "scripts"))
    spec.loader.exec_module(mod)
    return mod


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="report drift without writing")
    a = ap.parse_args(argv)

    try:
        sv = _sv()
    except Exception as err:                                  # noqa: BLE001
        #: LOUD, NOT SILENT. A repair that crashed used to print nothing at all
        #: in this gate's run-ledger stage and the commit went through with the
        #: repair not done -- the defect the stage exists to close, re-entering
        #: through its own reporting. Found by the fable seat, round 14.
        print(f"memory ledger: REFUSED -- could not load the derivation: "
              f"{type(err).__name__}: {err}")
        return 1

    try:
        changed = sv._update_memory_exclusions_ledger(REPO, dry_run=a.check)
    except Exception as err:                                  # noqa: BLE001
        print(f"memory ledger: REFUSED -- the derivation raised "
              f"{type(err).__name__}: {err}")
        return 1

    if a.check:
        #: ★ SAY WHAT THE RETURN VALUE LICENSES AND NOT MORE. Measured by
        #: calling the derivation twice in write mode: the 1st returned True
        #: and wrote, the 2nd returned False on the now-current ledger. So the
        #: value means "the file would be rewritten", which is NOT the same as
        #: "the counts have drifted" -- the recount also stamps a count date,
        #: so a new day can make it True with every bucket unchanged. A first
        #: version of this line said "drift present" and would have reported a
        #: defect once a day on a correct ledger.
        print("memory ledger: WOULD BE REWRITTEN (a count or the count date "
              "differs; run without --check to see which)" if changed
              else "memory ledger: already current, byte for byte")
        return 0
    print("memory ledger: refreshed resources/MEMORY_EXCLUSIONS.md" if changed
          else "memory ledger: already current")
    return 0


if __name__ == "__main__":
    import pathlib as _pl
    sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
    raise SystemExit(main(sys.argv[1:]))
