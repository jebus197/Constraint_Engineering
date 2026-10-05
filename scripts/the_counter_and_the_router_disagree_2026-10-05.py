#!/usr/bin/env python3
"""The A4 counter counts a class of finding that the router refuses to service.

THE ASYMMETRY. Two live predicates in `bench/reference_runner_v3.py` disagree about
which findings matter:

  * `unverified_critical_count` — the A4 fail-safe that gates convergence — has NO
    severity test. It was removed in commit 6c10fe4 on 2026-09-06 (founder ruling 23,
    rejected at 22:15 the same day; the removal still stands in code). So a finding at
    severity 0.45 counts as a convergence blocker.
  * `_apply_routing` — the only in-round machinery that offers an unresolved finding
    back to a model for repair — requires `escalated` AND
    `severity >= CRITICAL_SEVERITY_THRESHOLD` (0.7). So a finding at severity 0.45 is
    never offered to anybody.

A finding below 0.7 therefore BLOCKS convergence while having no in-round route to
resolution. The only machinery that services it is `_post_convergence_sweep`, which by
design runs after the verdict. That is why the closing sweep is load-bearing for
convergence rather than cosmetic, and why leaving it post-verdict leaves a class of
finding permanently unresolvable before the gate decides.

Observed instance: the two blockers on the final study_run1b registry were C0066
(severity 0.45) and C0073 (0.50). Both UNCONFIRMED, both with empty `verdicts`, both
with no `routing_history`.

WHAT THIS MEASURES, on archived registries: the severity distribution of residual
findings that were never offered to a model in-round, and the size of the population
that is simultaneously (a) counted by the A4 predicate and (b) refused by the router.

CAVEAT RECORDED. `escalated` is reset to False at :6944 and :6956, so the final state
cannot be used to reconstruct whether the escalation half of the router's predicate
was met. This script therefore measures the SEVERITY half only, which is a lower
bound on the refused population: adding the escalation condition can only refuse more.

Run:  python3 scripts/the_counter_and_the_router_disagree_2026-10-05.py
"""
from __future__ import annotations

import argparse
import ast
import glob
import json
import math
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"
RUNNER = REPO / "bench" / "reference_runner_v3.py"

TERMINAL = frozenset({"MERGED", "CLOSED", "REFUTED", "DUPLICATE"})
CRITICAL_SEVERITY_THRESHOLD = 0.7
#: A4 counts these as unresolved. Read from the runner's own constant below where
#: possible; this is the documented fallback.
A4_UNRESOLVED = frozenset({"UNCONFIRMED", "CONTESTED", "OPEN", "ESCALATED"})


def wilson(k: int, n: int):
    if n == 0:
        return (0.0, 0.0)
    z = 1.959963984540054
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, (c - m) / d) * 100.0, min(1.0, (c + m) / d) * 100.0)


def _parse_args(argv=None):
    p = argparse.ArgumentParser(
        prog="the_counter_and_the_router_disagree_2026-10-05.py",
        description=__doc__.split("\n\n")[0])
    p.add_argument("--run", default=None, help="one run directory under bench/logs")
    return p.parse_args(argv)


def _confirm_the_predicates() -> dict:
    """Read both predicates out of the runner so the premise is not assumed.

    THREE WAYS THIS WAS WRONG BEFORE IT WAS RIGHT, all on 2026-10-05:
      1. A fixed 60/80-line window after the `def`. `_apply_routing` is 502 lines
         and its severity test sits at :6793, 86 lines in — outside the window.
      2. A `startswith("def ")` scan. `unverified_critical_count` is a METHOD of
         `FindingRegistry` (lines 2747-2859), so it is indented and was missed.
      3. Stripping `#` comments but not DOCSTRINGS. The counter's docstring says
         "UNCONFIRMED and severity >= CRITICAL_SEVERITY_THRESHOLD" while
         DESCRIBING THE BEHAVIOUR THAT WAS REMOVED, so a substring search over
         the whole body reported a severity test that the code does not perform.

    So the check is now an AST walk over executable statements with the docstring
    dropped, and it is corroborated by actually CALLING the counter below.
    """
    src = RUNNER.read_text(encoding="utf-8")
    tree = ast.parse(src)
    out = {}

    def _find(name):
        for n in ast.walk(tree):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name:
                return n
        return None

    def _code_compares_to_threshold(fn) -> bool:
        if fn is None:
            return False
        body = list(fn.body)
        if body and isinstance(body[0], ast.Expr) and isinstance(
                getattr(body[0], "value", None), ast.Constant):
            body = body[1:]  # drop the docstring
        for stmt in body:
            for sub in ast.walk(stmt):
                if isinstance(sub, ast.Name) and sub.id == "CRITICAL_SEVERITY_THRESHOLD":
                    return True
        return False

    a4 = _find("unverified_critical_count")
    rt = _find("_apply_routing")
    out["a4_line"] = a4.lineno if a4 else None
    out["a4_span"] = (a4.end_lineno - a4.lineno + 1) if a4 else None
    out["router_line"] = rt.lineno if rt else None
    out["router_span"] = (rt.end_lineno - rt.lineno + 1) if rt else None
    out["a4_has_severity_test"] = _code_compares_to_threshold(a4)
    out["router_has_severity_test"] = _code_compares_to_threshold(rt)
    return out


def _call_the_counter() -> dict:
    """EXECUTE the A4 counter on a sub-critical UNCONFIRMED finding.

    `execute-do-not-grep`: a source scan proves the module describes itself
    consistently. Only a call proves what the counter DOES with a finding at 0.45.
    """
    out = {"ran": False}
    try:
        sys.path.insert(0, str(REPO))
        from bench.reference_runner_v3 import FindingRegistry
        reg = FindingRegistry()
        reg.entries = {
            "C0001": {"status": "UNCONFIRMED", "severity": 0.45, "verified": False,
                      "verdicts": [], "canonical_id": "C0001"},
            "C0002": {"status": "UNCONFIRMED", "severity": 0.95, "verified": False,
                      "verdicts": [], "canonical_id": "C0002"},
        }
        out["both"] = reg.unverified_critical_count()
        reg.entries.pop("C0002")
        out["subcritical_only"] = reg.unverified_critical_count()
        out["ran"] = True
    except Exception as exc:  # noqa: BLE001 — a failed call is reported, not hidden
        out["error"] = f"{type(exc).__name__}: {exc}"
    return out


def main(argv=None) -> int:
    args = _parse_args(argv)

    print("=" * 78)
    print("THE A4 COUNTER AND THE ROUTER DISAGREE ABOUT WHICH FINDINGS MATTER")
    print("=" * 78)
    pred = _confirm_the_predicates()
    print("predicates read by AST over EXECUTABLE statements (docstring dropped):")
    print(f"  FindingRegistry.unverified_critical_count at :{pred.get('a4_line')} "
          f"({pred.get('a4_span')} lines) — severity test in code: "
          f"{pred.get('a4_has_severity_test')}")
    print(f"  _apply_routing                           at :{pred.get('router_line')} "
          f"({pred.get('router_span')} lines) — severity test in code: "
          f"{pred.get('router_has_severity_test')}")
    print()
    called = _call_the_counter()
    print("and the counter CALLED, not read:")
    if called.get("ran"):
        print(f"  one 0.45 + one 0.95 UNCONFIRMED -> count = {called['both']}")
        print(f"  the 0.45 alone                  -> count = {called['subcritical_only']}")
        if called["subcritical_only"] >= 1:
            print("  => a sub-critical finding IS counted as a convergence blocker.")
        else:
            print("  => a sub-critical finding is NOT counted; the premise is stale.")
    else:
        print(f"  COULD NOT CALL IT: {called.get('error')}")
    if pred.get("a4_has_severity_test") or not pred.get("router_has_severity_test"):
        print()
        print("  *** THE PREMISE DOES NOT HOLD IN THIS CHECKOUT. Either the counter")
        print("  *** regained a severity test or the router lost one. The numbers")
        print("  *** below describe a condition that may no longer exist.")
    print()

    if args.run:
        paths = [pathlib.Path(args.run) / "runner_state.json"]
    else:
        paths = [pathlib.Path(p) for p in sorted(
            glob.glob(str(LOGS / "*" / "runner_state.json")))]
    paths = [p for p in paths if p.is_file()]

    n_resid = n_sub = n_sub_blocking = n_sub_never_offered = 0
    n_crit_never_offered = n_crit = 0
    sev_buckets = {}

    for p in paths:
        try:
            state = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        reg = state.get("registry") or {}
        ents = reg.get("entries") if isinstance(reg, dict) else None
        if not isinstance(ents, dict):
            continue
        for cid, e in ents.items():
            st = str(e.get("status", "")).upper()
            if st in TERMINAL:
                continue
            n_resid += 1
            sev = float(e.get("severity") or 0.0)
            offered = bool(e.get("routing_history") or e.get("verdicts"))
            b = f"{min(0.9, (int(sev * 10) / 10)):.1f}"
            d = sev_buckets.setdefault(b, {"n": 0, "never": 0})
            d["n"] += 1
            if not offered:
                d["never"] += 1
            if sev < CRITICAL_SEVERITY_THRESHOLD:
                n_sub += 1
                if st in A4_UNRESOLVED and not e.get("verified"):
                    n_sub_blocking += 1
                if not offered:
                    n_sub_never_offered += 1
            else:
                n_crit += 1
                if not offered:
                    n_crit_never_offered += 1

    print("-" * 78)
    print("RESIDUALS BY SEVERITY BUCKET, and how many were never offered in-round")
    print("-" * 78)
    print(f"{'severity':>9} {'residuals':>10} {'never offered':>14} {'rate':>9}")
    for b in sorted(sev_buckets):
        d = sev_buckets[b]
        rate = 100.0 * d["never"] / d["n"] if d["n"] else 0.0
        mark = "  <- router refuses" if float(b) < CRITICAL_SEVERITY_THRESHOLD else ""
        print(f"{b:>9} {d['n']:>10} {d['never']:>14} {rate:>8.2f}%{mark}")

    print()
    print("=" * 78)
    print("THE REFUSED-BUT-COUNTED POPULATION")
    print("=" * 78)
    print(f"residual findings at the stop point          : {n_resid}")
    if n_resid:
        lo, hi = wilson(n_sub, n_resid)
        print(f"  below the router's 0.7 threshold           : {n_sub} "
              f"= {100.0 * n_sub / n_resid:.4f}%, Wilson [{lo:.4f}%, {hi:.4f}%]")
    if n_sub:
        lo, hi = wilson(n_sub_never_offered, n_sub)
        print(f"  of those, never offered in-round           : {n_sub_never_offered} "
              f"= {100.0 * n_sub_never_offered / n_sub:.4f}%, "
              f"Wilson [{lo:.4f}%, {hi:.4f}%]")
        lo, hi = wilson(n_sub_blocking, n_sub)
        print(f"  of those, ALSO counted by A4 as blocking   : {n_sub_blocking} "
              f"= {100.0 * n_sub_blocking / n_sub:.4f}%, "
              f"Wilson [{lo:.4f}%, {hi:.4f}%]")
    if n_crit:
        lo, hi = wilson(n_crit_never_offered, n_crit)
        print(f"critical residuals (>= 0.7)                  : {n_crit}")
        print(f"  never offered in-round                     : {n_crit_never_offered} "
              f"= {100.0 * n_crit_never_offered / n_crit:.4f}%, "
              f"Wilson [{lo:.4f}%, {hi:.4f}%]")
        print("  (criticals ARE in the router's severity band, so a never-offered")
        print("   critical was refused by the OTHER half of the predicate —")
        print("   `escalated` — or the ladder was exhausted.)")

    print()
    print("CONSEQUENCE. A sub-critical residual blocks the gate and has no in-round")
    print("route to resolution. The only machinery that services it is the closing")
    print("sweep, which runs after the verdict. Either the counter stops counting")
    print("that class, or something in-round must start offering it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
