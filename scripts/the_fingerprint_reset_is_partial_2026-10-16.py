#!/usr/bin/env python3
"""Is the per-experiment fingerprint reset total, or bypassed on one path?

MEASURED AS PARTIAL ON 2026-10-16, REPAIRED 2026-10-17, and this script is
kept because it is the only thing that would notice the bypass returning.
THE FILENAME IS LEFT ALONE DELIBERATELY: it records the finding as it stood
on 2026-10-16, it is cited by task B12 and by the task list, and renaming a
cited producer costs more than the stale adjective it would fix. This
docstring and the verdict are the authority on the current state.
Its own verdict was VACUOUS until 2026-10-17: it read the second loader once
without declaring a scope, so its condition held whatever the code did and it
would have reported PARTIAL for ever, including after the repair.

HIS QUESTION, verbatim from Responses/Runway_Status_And_Is_It_Safe_To_Merge_2026-10-16.txt:
"The fingerprints should be recomputed in the first/blind run of any experiment
anyway. So they should be reset after the next live experiment runs. Please make
sure that is the case and that is how this facility will work?"

THE ANSWER IS "YES ON THE MAIN PATH, NO ON THE DECOMPOSITION PATH."

Two different loaders read `bench/fingerprints/` inside one run:

  1. `reference_runner_v3._load_fingerprints(scope)` -- the run's main observation
     load, called at reference_runner_v3.py:17712 with `cfg.fingerprint_scope`.
     HONOURS the scope. Under "experiment" (the RunnerConfig default, on his
     ruling of 2026-10-16) it returns an EMPTY mapping and clears the at-load
     snapshot, so the run measures its seats afresh in the blind round and at
     save time every seat correctly reads as changed.

  2. `run_exp17_immune._load_fingerprint_cache()` -- imported into the runner at
     reference_runner_v3.py:250 and called at :459, inside the DECOMPOSITION
     FUTILITY GUARD. Takes NO scope parameter, reads the same directory from
     disk, and caches module-globally. So the decomposition decision for THIS
     run is taken against a PRIOR experiment's observed capacity.

WHY IT MATTERS RATHER THAN BEING A TIDINESS POINT. The value it reads,
`max_successful_prompt_chars`, is multiplied by 0.9 to set the effective ceiling
that decides whether a payload is split. A run that believes it is measuring its
seats afresh is therefore splitting payloads on inherited numbers.

WHAT THIS DOES NOT BREAK: the merge-safety argument for carrying the 6 stand-in
fingerprints to the canonical branch. Both loaders key on the SEAT LABEL, so a
live run asking for "CC2" reads CC2.json and never CC2-SIM.json. The stand-in
files stay unreachable to a live run. That protection comes from the LABEL, not
from the scope switch.

`--help` runs no measurement and costs nothing.
"""
from __future__ import annotations
import argparse, sys

def main() -> int:
    argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter).parse_args()
    sys.path.insert(0, ".")
    from bench import reference_runner_v3 as m
    from bench import run_exp17_immune as im
    import dataclasses

    cfgcls = next(o for o in (getattr(m, n) for n in dir(m))
                  if dataclasses.is_dataclass(o)
                  and any(f.name == "fingerprint_scope" for f in dataclasses.fields(o)))
    default = {f.name: f.default for f in dataclasses.fields(cfgcls)}["fingerprint_scope"]

    print("=" * 72)
    print("IS THE PER-EXPERIMENT FINGERPRINT RESET TOTAL? executed, not read")
    print("=" * 72)
    print(f"\n  {cfgcls.__name__}.fingerprint_scope default: {default!r}")

    main_persist = m._load_fingerprints("persist")
    main_exp = m._load_fingerprints("experiment")
    print(f"\n  LOADER 1  _load_fingerprints('persist')    -> {len(main_persist)} records")
    print(f"  LOADER 1  _load_fingerprints('experiment') -> {len(main_exp)} records"
          f"   <-- honours the scope")
    print(f"  LOADER 1  at-load snapshot after 'experiment': "
          f"{len(m._FINGERPRINTS_AT_LOAD)} entries")

    # LOADER 2 IS ASKED UNDER BOTH SCOPES, which is the whole measurement.
    # Until 2026-10-17 this read loader 2 ONCE, without declaring a scope, so it
    # got the module default `persist` and 11 records -- and the verdict's
    # condition `len(main_exp) == 0 and len(cache) > 0` was then TRUE whatever
    # the code did. It would have reported "the reset is PARTIAL" for ever,
    # including after the repair, which is a check that cannot see its own
    # subject being fixed.
    im.set_fingerprint_scope("persist")
    im._fp_cache = None
    cache = im._load_fingerprint_cache()
    im.set_fingerprint_scope("experiment")
    cache_exp = im._load_fingerprint_cache()
    im.set_fingerprint_scope("persist")
    im._fp_cache = None
    print(f"\n  LOADER 2  _load_fingerprint_cache() under 'persist'    -> "
          f"{len(cache)} records")
    print(f"  LOADER 2  _load_fingerprint_cache() under 'experiment' -> "
          f"{len(cache_exp)} records"
          + ("   <-- honours the scope" if not cache_exp
             else "   <-- IGNORES the scope"))

    paid = {k: v.get("max_successful_prompt_chars") for k, v in cache.items()
            if not k.endswith("-SIM")}
    carrying = {k: v for k, v in paid.items() if v}
    print(f"\n  of the {len(cache)} records loader 2 sees, {len(carrying)} are PAID"
          f" carrying a capacity:")
    for k, v in sorted(carrying.items()):
        print(f"    {k:10s} max_successful_prompt_chars = {v:>8d}"
              f"  -> effective ceiling {int(v * 0.9)}")
    sim = sorted(k for k in cache if k.endswith("-SIM"))
    print(f"  and {len(sim)} stand-in records: {sim}")
    base = {k[:-4] if k.endswith("-SIM") else k for k in cache}
    print(f"\n  THESE ARE RECORDS, NOT SEATS. {len(cache)} records cover"
          f" {len(base)} DISTINCT MODELS: {sorted(base)}.")
    print("  The loaders return a dict keyed by LABEL, so its length counts")
    print("  labels accumulated across ALL runs. No run has ever seated 11.")

    distinct = sorted(set(carrying.values()))
    print(f"\n  distinct capacities among the {len(carrying)} paid seats: {distinct}")
    if len(distinct) < len(carrying):
        shared = max(set(carrying.values()), key=list(carrying.values()).count)
        n = list(carrying.values()).count(shared)
        print(f"  {n} of {len(carrying)} paid seats share the identical value {shared}."
              f" This is task B12's high-water-mark finding, and it is what the"
              f" decomposition guard uses UNDER 'persist' -- under"
              f" 'experiment' it has none and falls to the hard floor.")

    partial = len(main_exp) == 0 and len(cache_exp) > 0
    print("\n" + "=" * 72)
    if partial:
        print("VERDICT: the reset is PARTIAL.")
        print("The main observation path re-measures under 'experiment' and the")
        print("decomposition decision does not, so a run that believes it is")
        print("measuring afresh splits payloads on a prior experiment's ceiling.")
        print("=" * 72)
        return 1
    print("VERDICT: the reset is TOTAL. Both loaders honour the scope.")
    print("MEASURED AS PARTIAL ON 2026-10-16 and repaired on 2026-10-17: loader 2")
    print("took no scope at all, so with the main path returning 0 records it")
    print("returned 11, and the ceiling that decides whether a payload is SPLIT")
    print("came from a prior experiment. Through the live routing predicate the")
    print("difference is 418,686 characters under 'persist' against 80,001 under")
    print("'experiment', and the seats have actually handled 70,045 to 95,045.")
    print("This script is kept because it is the only thing that would notice")
    print("the bypass returning, and its own verdict was vacuous until today:")
    print("it read loader 2 once without declaring a scope, so it would have")
    print("reported PARTIAL for ever, including now.")
    print("=" * 72)
    return 0

if __name__ == "__main__":
    sys.exit(main())
