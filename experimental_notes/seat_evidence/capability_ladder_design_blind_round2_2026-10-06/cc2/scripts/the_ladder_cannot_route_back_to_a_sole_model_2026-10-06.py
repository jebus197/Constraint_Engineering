# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'capability_ladder_design_blind_cc2_2026-10-06', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 5c499d4ce590fc4a80d81f3fc69e4c517a3c2424a53b710ae83db4f9a67ccdd5
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
r"""A one-model panel gets ZERO rungs, so the ladder never has "another go".

THE FOUNDER'S REQUIREMENT, verbatim 2026-10-06: the system "shouldn't care at all
what a model is called ... so it shouldn't matter if all the models are different, or
all the models are the same, or if they are all models from a single vendor, or even a
single model operating on its own (in which case the ladder would just route the issue
back to itself and would have another go at resolving it by using the rest of the
machinery of the harness.)"

THE CODE DOES THE OPPOSITE. `bench/routing.route` builds its rung list with

    rungs = rank_falsifier_writers(available_models, exclude=(source,) if source else ())

so the finding's own source model is unconditionally removed. On a one-model panel the
source model IS the only model: `rungs` comes back EMPTY, the `for model in rungs`
loop in `resolve_via_routing` never executes, and the function returns
`RoutingResult(verdict="UNTOOLABLE", resolved=False, model_used=None, rungs_tried=0)`.
The sole model is never asked a second time. There is no self-route.

The exclusion is right on a multi-model panel -- re-asking a model that just failed is
the behaviour the module's own docstring exists to avoid ("should NOT endlessly re-ask
the weak model"). It is wrong when it empties the candidate set, because then the
alternative is not a stronger model, it is nothing at all.

ALREADY VISIBLE IN THE ARCHIVE. Across `bench/logs/*/runner_state.json`, 161 recorded
routing events carry `rungs_available`; 21 of them have `rungs_available == 1`, and
every one of those 21 records `rungs_tried == 0` and `verdict == "UNTOOLABLE"`.
Wilson 95% interval on that proportion is printed below. Those are 21 criticals that
went straight to human escalation without a single falsification attempt being made.

THE REPAIR is one line and is additive -- nothing is removed, and the multi-model
behaviour is bit-identical: exclude the source model only when doing so leaves at
least one other candidate. See `suggested_repair()`.

This script imports the REAL `bench/routing.py`. It does not reimplement it. It reads
only that module and the repository's own archived run state -- no scoring key, no
answer file, no planted-defect manifest.

Run:  python3 scripts/the_ladder_cannot_route_back_to_a_sole_model_2026-10-06.py
"""
from __future__ import annotations

import collections
import glob
import json
import math
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from bench.routing import route, rank_falsifier_writers   # the REAL module


def wilson(k: int, n: int, z: float = 1.959963984540054):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1.0 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def falsifier() -> None:
    """Fails iff a one-model panel produces zero falsification attempts."""
    calls = []

    def resolve_fn(model, finding):
        calls.append(model)
        # A plausible second attempt by the same model. Irrelevant to the defect:
        # on a one-model panel this is never called at all.
        return "assert False, 'FALSIFIED'"

    def reverify_fn(code):
        return "CONFIRMED"

    def similarity_fn(a, b):
        return 0.0

    finding = {"finding_id": "C9001", "source_model": "SoleModel",
               "severity": "CRITICAL", "description": "a critical finding"}

    # Sanity anchor: the ranker itself empties the list.
    rungs = rank_falsifier_writers(["SoleModel"], exclude=("SoleModel",))
    res = route(finding, ["SoleModel"], [], resolve_fn, reverify_fn, similarity_fn,
                max_rungs=0)       # 0 == "exhaust the ladder", the founder's setting

    print(f"  rank_falsifier_writers(['SoleModel'], exclude=('SoleModel',)) -> {rungs}")
    print(f"  route(... max_rungs=0) -> verdict={res.verdict!r} "
          f"resolved={res.resolved} model_used={res.model_used!r} "
          f"rungs_tried={res.rungs_tried}")
    print(f"  resolve_fn was called {len(calls)} time(s): {calls}")

    if res.rungs_tried == 0 and len(calls) == 0:
        print("FALSIFIED")
        raise AssertionError(
            "A one-model panel produced ZERO falsification attempts: "
            f"rungs_tried={res.rungs_tried}, resolve_fn calls={len(calls)}, "
            f"verdict={res.verdict!r}. The founder's ruling requires the ladder to "
            "'route the issue back to itself and have another go'; "
            "`exclude=(source,)` empties the candidate set instead, and the "
            "max_rungs=0 'exhaust the ladder' setting cannot help because the "
            "ladder it exhausts is empty."
        )
    print("  defect absent: the sole model was given at least one attempt")


def suggested_repair() -> str:
    return '''
    # bench/routing.py, in route():
    #
    #   source = finding.get("source_model")
    #   rungs = rank_falsifier_writers(
    #       available_models, strength_order=strength_order,
    #       exclude=(source,) if source else (),
    #   )
    #
    # becomes
    #
    #   source = finding.get("source_model")
    #   rungs = rank_falsifier_writers(
    #       available_models, strength_order=strength_order,
    #       exclude=(source,) if source else (),
    #   )
    #   if not rungs:
    #       # Founder ruling 2026-10-06: a sole model routes BACK TO ITSELF and has
    #       # another go with the rest of the harness. Excluding the source is
    #       # correct only while a different candidate remains; when it empties the
    #       # set the alternative is not a stronger model, it is no attempt at all.
    #       # Multi-model behaviour is unchanged: this branch is unreachable
    #       # whenever any candidate other than the source exists.
    #       rungs = rank_falsifier_writers(available_models,
    #                                      strength_order=strength_order)
    '''


def archive_evidence():
    total = sole = sole_untried = 0
    verdicts: collections.Counter = collections.Counter()
    for p in sorted(glob.glob(str(REPO / "bench" / "logs" / "*" / "runner_state.json"))):
        try:
            j = json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        for _fid, e in ((j.get("registry") or {}).get("entries") or {}).items():
            for h in (e.get("routing_history") or []):
                if h.get("rungs_available") is None:
                    continue
                total += 1
                verdicts[h.get("verdict")] += 1
                if h.get("rungs_available") == 1:
                    sole += 1
                    if h.get("rungs_tried") == 0:
                        sole_untried += 1
    print(f"\n  archived routing events with rungs_available recorded : {total}")
    lo, hi = wilson(sole, total)
    print(f"  of those, rungs_available == 1                         : {sole}"
          f"  = {sole / total:.2%}  Wilson95 [{lo:.2%}, {hi:.2%}]")
    lo, hi = wilson(sole_untried, sole) if sole else (0, 0)
    print(f"  of THOSE, rungs_tried == 0 (no attempt made at all)    : {sole_untried}"
          f"  = {sole_untried / sole:.2%}  Wilson95 [{lo:.2%}, {hi:.2%}]"
          if sole else "  (none)")
    print(f"  routing verdict distribution: {dict(verdicts)}")
    try:
        from statsmodels.stats.proportion import proportion_confint
        a, b = proportion_confint(sole, total, alpha=0.05, method="wilson")
        c, d = wilson(sole, total)
        print(f"  statsmodels cross-check on {sole}/{total}: [{a:.6f}, {b:.6f}] vs "
              f"closed form [{c:.6f}, {d:.6f}]  agree="
              f"{abs(a - c) < 1e-12 and abs(b - d) < 1e-12}")
    except Exception as exc:
        print(f"  statsmodels unavailable: {exc}")


def main() -> int:
    print("=" * 78)
    print("FALSIFIER - one-model panel, bench/routing.route")
    print("=" * 78)
    failed = False
    try:
        falsifier()
    except AssertionError as exc:
        print(f"AssertionError: {exc}")
        failed = True
    archive_evidence()
    print("\n  SUGGESTED REPAIR (additive, multi-model behaviour bit-identical):")
    print(suggested_repair())
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
