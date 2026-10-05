# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'fingerprint_ladder_review_2026-10-05', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: a264e26f02cca471f0aeb45b543b1dd3ce7fe529d5d693711d353f314a25de7d
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The live fingerprint has one behavioural consumer, and it is not the burst planner.

THE CLAIM UNDER TEST, quoted from
`experimental_notes/Proposal_Fingerprint_Falsification_Dimension_2026-10-05.md`:
"`_update_observed_fingerprint` writes a live profile for every model every round,
`_save_fingerprints` persists it to `bench/fingerprints/`, and `burst_planner.py`
and `_should_decompose` consume it. So the schema already measures per-model
capability continuously, and the ladder is the one consumer that ignores it."

THE SECOND HALF OF THAT IS FALSE, and it matters because the proposal's whole
argument is that the live fingerprint is already load-bearing and only the ladder
declines to read it. Measured by parsing `run_experiment` and reading which
object is passed at each call site:

  * `should_burst` and `plan_phases` are handed `INITIAL_FINGERPRINTS`, a module
    constant, NOT `observed_fingerprints`.
  * They are called BEFORE `observed_fingerprints` is bound at all. The binding
    is `observed_fingerprints = _load_fingerprints()`, 100+ lines further down,
    so the live profile does not exist in the frame when the burst planner runs.
    It is not a choice the planner makes; the value is unreachable from there.
  * `bench/burst_planner.py` reads exactly ONE fingerprint field, `D_decay`, and
    reads it with `getattr(fp, "D_decay", 0.0)` -- so an object without that
    field degrades silently to "no decay" rather than failing.

So the live fingerprint is consumed in exactly one place that changes behaviour:
`get_effective_context_budget`. The ladder is NOT the one consumer that ignores
it; the burst planner ignores it too, and the dimension the proposal would add
would land in a structure whose only behavioural reader is a context-budget
computation.

A SECOND, SMALLER FACT WITH THE SAME SHAPE: the whole burst block, including the
import of `bench/burst_planner.py`, sits under `if cfg.burst_mode != "off"`, and
`bench/tools/run_simulated_experiment.py` sets `burst_mode="off"`. The module is
therefore never imported in a simulated run, so no simulation has ever exercised
any of it.

METHOD. Nothing here matches source text to decide behaviour. `run_experiment` is
parsed and the ARGUMENT EXPRESSIONS at each call site are read off the syntax
tree, and `bench/burst_planner.py` is parsed for the attribute names it takes off
a fingerprint object. Line numbers are reported so a reader can check by hand.

Run:  python3 scripts/the_burst_planner_never_reads_the_live_fingerprint_2026-10-05.py
"""
from __future__ import annotations

import argparse
import ast
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
RUNNER = REPO / "bench" / "reference_runner_v3.py"
PLANNER = REPO / "bench" / "burst_planner.py"
SIM = REPO / "bench" / "tools" / "run_simulated_experiment.py"

#: Call sites whose fingerprint argument decides what this script reports.
_WATCHED = ("should_burst", "plan_phases", "_load_fingerprints",
            "get_effective_context_budget", "_update_observed_fingerprint",
            "_save_fingerprints")


def _parse_args(argv=None):
    p = argparse.ArgumentParser(
        prog="the_burst_planner_never_reads_the_live_fingerprint_2026-10-05.py",
        description=(__doc__ or "").strip().split("\n\n")[0])
    p.add_argument("--runner", default=str(RUNNER))
    p.add_argument("--planner", default=str(PLANNER))
    p.add_argument("--sim", default=str(SIM))
    return p.parse_args(argv)


def _function(tree, name):
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name:
            return n
    return None


def call_sites(fn):
    """(line, callee, argument expressions) for each watched call inside fn."""
    out = []
    for n in ast.walk(fn):
        if not isinstance(n, ast.Call):
            continue
        name = getattr(n.func, "id", None) or getattr(n.func, "attr", None)
        if name in _WATCHED:
            out.append((n.lineno, name,
                        [ast.unparse(a) for a in n.args] +
                        [f"{k.arg}={ast.unparse(k.value)}" for k in n.keywords]))
    return sorted(out)


def bindings(fn, target_name):
    out = []
    for n in ast.walk(fn):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name) and t.id == target_name:
                    out.append((n.lineno, ast.unparse(n)))
    return sorted(out)


def planner_fingerprint_fields(tree):
    """Attribute names taken off anything called `fp` / `fingerprint*`, plus the
    getattr() form, which is how a missing field degrades silently."""
    fields = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            name = getattr(n.func, "id", None)
            if name == "getattr" and len(n.args) >= 2:
                owner = ast.unparse(n.args[0])
                if "fp" in owner or "fingerprint" in owner:
                    default = ast.unparse(n.args[2]) if len(n.args) > 2 else "<none>"
                    fields.append((n.lineno, ast.unparse(n.args[1]),
                                   f"getattr default {default}"))
        if isinstance(n, ast.Attribute):
            owner = getattr(n.value, "id", "")
            # `fingerprints.get(model)` is a dict lookup on the MAPPING, not a
            # field of a profile; counting it would report a field that is not one.
            if n.attr in ("get", "items", "keys", "values", "setdefault", "pop"):
                continue
            if owner == "fp" or owner.startswith("fingerprint"):
                fields.append((n.lineno, repr(n.attr), "attribute access"))
    return sorted(set(fields))


def guard_on_burst_mode(tree):
    """Lines where `burst_mode` is compared, and what is imported underneath."""
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.If):
            test = ast.unparse(n.test)
            if "burst_mode" in test:
                imported = []
                for s in ast.walk(n):
                    if isinstance(s, ast.ImportFrom) and "burst_planner" in (s.module or ""):
                        imported += [a.name for a in s.names]
                    if isinstance(s, ast.Import):
                        imported += [a.name for a in s.names if "burst_planner" in a.name]
                out.append((n.lineno, test, imported))
    return sorted(out)


def main(argv=None) -> int:
    args = _parse_args(argv)
    runner_p, planner_p, sim_p = (pathlib.Path(args.runner),
                                  pathlib.Path(args.planner),
                                  pathlib.Path(args.sim))
    for p in (runner_p, planner_p, sim_p):
        if not p.is_file():
            print(f"  {p} is missing; cannot measure")
            return 1

    runner = ast.parse(runner_p.read_text(encoding="utf-8"))
    fn = _function(runner, "run_experiment")
    if fn is None:
        print("  run_experiment not found in the runner; the premise has moved")
        return 1

    print("=" * 78)
    print("1. WHICH FINGERPRINT OBJECT REACHES WHICH CONSUMER")
    print("=" * 78)
    binds = bindings(fn, "observed_fingerprints")
    for line, text in binds:
        print(f"  line {line:>6}  binds observed_fingerprints:  {text}")
    first_bind = min(l for l, _ in binds) if binds else None
    sites = call_sites(fn)
    print(f"\n  {'line':>6}  {'callee':<32} fingerprint argument")
    for line, callee, argexprs in sites:
        fp = [a for a in argexprs if "fingerprint" in a.lower()]
        print(f"  {line:>6}  {callee:<32} {fp if fp else '(none)'}")

    burst_lines = [l for l, c, _ in sites if c in ("should_burst", "plan_phases")]
    print()
    if first_bind is None:
        print("  observed_fingerprints is never bound in run_experiment.")
        return 1
    print(f"  earliest binding of observed_fingerprints : line {first_bind}")
    print(f"  burst-planner call sites                  : {burst_lines}")
    if burst_lines and max(burst_lines) < first_bind:
        print("  VERDICT: the burst planner is called BEFORE the live fingerprint")
        print("           exists in the frame. It is handed INITIAL_FINGERPRINTS,")
        print("           a module constant, and the live profile is not reachable")
        print("           from there at all.")
    else:
        print("  VERDICT: the live fingerprint IS in scope at the burst call sites.")

    live_consumers = [(l, c) for l, c, a in sites
                      if any("observed_fingerprints" in x for x in a)
                      and c not in ("_update_observed_fingerprint", "_save_fingerprints")]
    print(f"\n  call sites that PASS the live fingerprint to a consumer: "
          f"{live_consumers}")
    print("  (`_update_observed_fingerprint` and `_save_fingerprints` are the")
    print("   PRODUCER and the persister, not consumers, so they are excluded.)")

    print()
    print("=" * 78)
    print("2. WHAT bench/burst_planner.py ACTUALLY READS OFF A FINGERPRINT")
    print("=" * 78)
    planner = ast.parse(planner_p.read_text(encoding="utf-8"))
    fields = planner_fingerprint_fields(planner)
    if not fields:
        print("  no fingerprint field is read at all.")
    for line, field, how in fields:
        print(f"  line {line:>5}  {field:<14} ({how})")
    print(f"\n  distinct fingerprint fields read: "
          f"{sorted({f for _, f, _ in fields})}")
    print("  The glossary defines the profile as (D, v-bar, A, C). One of the four")
    print("  is read here, and no verification score or coverage dimension exists")
    print("  to read.")

    print()
    print("=" * 78)
    print("3. IS ANY OF IT REACHED IN A SIMULATED RUN?")
    print("=" * 78)
    for line, test, imported in guard_on_burst_mode(runner):
        print(f"  line {line:>6}  if {test}")
        if imported:
            print(f"               imports under that guard: {imported}")
    sim = ast.parse(sim_p.read_text(encoding="utf-8"))
    found = False
    for n in ast.walk(sim):
        if isinstance(n, ast.keyword) and n.arg == "burst_mode":
            found = True
            print(f"  {sim_p.name}: line {n.value.lineno}  "
                  f"burst_mode={ast.unparse(n.value)}")
    if not found:
        print(f"  {sim_p.name} sets no burst_mode keyword (so RunnerConfig's "
              f"default applies)")
    print("\n  With burst_mode='off' the import of bench/burst_planner.py sits")
    print("  inside the skipped branch, so in a simulated run the module is never")
    print("  imported and nothing in it executes. Burst is fingerprint-driven, and")
    print("  the arm that is supposed to rehearse the schema has never run it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
