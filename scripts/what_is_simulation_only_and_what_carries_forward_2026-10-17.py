#!/usr/bin/env python3
"""The inventory his 2026-10-12 ruling requires BEFORE the zero-plant control.

HIS RULING, verbatim: *"Run it next after the outstanding simulated run. But take
care that the caveats in place for simulated runs that do not and should not
apply to real/paid runs carry over into this run. We keep all the useful lessons
we have learned from the simulated runs and apply them. But we exclude things
that only apply in simulated runs."*

THE READING TAKEN, stated because the first sentence admits two. Read literally
it could ask that the simulation-only caveats DO carry over, which contradicts
its own "do not and should not apply". The 2 sentences that follow settle it:
keep the lessons, exclude what is simulation-only. So this script asks which
behaviour is gated on simulation and whether any of it could leak into a paid
run.

WHAT IT MEASURES, by reading the live code rather than a list someone wrote.
Every branch on `run_is_simulated`, every use of the `-SIM` label suffix in the
live harness path, and every stand-in fingerprint record, each classified as:

  * CAVEAT -- it only labels or annotates output, and keys off the `-SIM`
    suffix, so a paid run turns it off by having no such seat. Nothing to do.
  * BEHAVIOUR -- it changes what the harness DOES. These are the ones that would
    need excluding by hand, and any found here is a finding.
  * LESSON -- an unconditional repair made during the simulated runs. These
    carry forward by construction, because nothing gates them on simulation.

MEASURED 2026-10-17, by AST so that comments and docstrings cannot be mistaken
for code:

  * 5 live branches on `run_is_simulated`, ALL CAVEAT, 0 BEHAVIOUR.
  * 6 `-SIM` string literals in the live path, of which 5 are the suffix
    constant used to strip a label back to its vendor base and 1 is a log
    message. All label handling; none changes a decision.
  * 12 further literals inside the simulation facility itself, which is the
    facility rather than a leak.
  * The stand-in fingerprints cannot reach a paid run:
    `RunnerConfig.fingerprint_scope` defaults to `experiment`, which returns 0
    inherited observations against 11 under `persist`, 6 of them stand-ins.

So the exclusion his ruling asks for is STRUCTURAL rather than something to
remember, and the lessons carry forward because they were never conditional on
simulation in the first place.

TWO OF MY OWN INSTRUMENTS WERE WRONG BEFORE THIS ONE, and both are recorded
because the shape recurs. Scanning the whole repository reported 5 BEHAVIOUR
branches, every one a line of this script's own source or another producer's --
a detector reading its own documentation as evidence. Then a line filter that
skipped every line opening with a quote dropped the 2 dict-literal branches that
emit the caveat, so it lost the cases it exists to find. A line scan also
reported `bench/evidence.py:897 authored_by="CC2-SIM"` as live code; it is a
usage example inside a docstring, which the AST correctly excludes.

Costs nothing and dispatches no model. Run: python3 scripts/<this file>
"""
from __future__ import annotations

import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))
from _cli_help import answer_help  # noqa: E402

#: Files that ARE the simulation facility: a reference here is the facility
#: itself, not a leak into the live path. Listed so the exemption is explicit.
SIMULATION_FACILITY = (
    "bench/tools/sim_dispatch_shim.py",
    "bench/tools/run_simulated_experiment.py",
)
#: Output-shaping only. A branch whose body just labels, logs or annotates is a
#: caveat; one that changes a decision is behaviour.
CAVEAT_MARKERS = ("severity_provenance", "caveat_when_simulated",
                  "severity_magnitudes_calibrated", "_log(", "cross_why_not")


#: THE LIVE HARNESS PATH: the code a RUN executes. `scripts/` is excluded
#: deliberately -- those are producers and measurement tools invoked by hand, so
#: a `-SIM` string in one is a measurement ABOUT simulation, not simulation
#: leaking into a run. The first version of this script scanned the whole
#: repository and reported 5 BEHAVIOUR branches, every one of which was a line
#: of ITS OWN SOURCE or another producer's: a detector reading its own
#: documentation as evidence, which is the fifth instrument of this shape found
#: on 2026-10-17 alone.
LIVE_ROOTS = ("bench/", )
LIVE_EXCLUDE = ("bench/logs/", "bench/tests/", "bench/tools/fixtures/")


def _live_python():
    for p in sorted((REPO / "bench").rglob("*.py")):
        rel = p.relative_to(REPO).as_posix()
        if "__pycache__" in rel or any(rel.startswith(x) for x in LIVE_EXCLUDE):
            continue
        if "/tests/" in rel:
            continue
        yield p, rel


def main() -> int:
    answer_help(__doc__, __file__)

    print("BRANCHES ON `run_is_simulated` IN LIVE CODE")
    print("  Found by AST, not by line matching. A line filter was written")
    print("  first and skipped every line opening with a quote, which dropped")
    print("  the 2 dict-literal branches that emit the caveat -- a filter that")
    print("  silently loses the cases it exists to find.")
    import ast
    branches = []
    for p_, rel in _live_python():
        src = p_.read_text(encoding="utf-8", errors="replace")
        if "run_is_simulated" not in src:
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        lines = src.splitlines()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fn = node.func
            name = (fn.id if isinstance(fn, ast.Name)
                    else fn.attr if isinstance(fn, ast.Attribute) else "")
            if name != "run_is_simulated":
                continue
            n = node.lineno
            if rel.endswith("reference_runner_v3.py") and \
                    lines[n - 1].lstrip().startswith("def "):
                continue
            window = "\n".join(lines[max(0, n - 5):n + 9])
            kind = ("CAVEAT" if any(m in window for m in CAVEAT_MARKERS)
                    else "BEHAVIOUR")
            branches.append((rel, n, kind, lines[n - 1].strip()[:92]))
    seen = set()
    branches = [b for b in branches
                if (b[0], b[1]) not in seen and not seen.add((b[0], b[1]))]
    for rel, n, kind, snippet in sorted(branches, key=lambda b: (b[0], b[1])):
        print(f"  [{kind:<9}] {rel}:{n}")
        print(f"              {snippet}")
    behaviour = [b for b in branches if b[2] == "BEHAVIOUR"]
    print(f"  total {len(branches)}; CAVEAT {len(branches) - len(behaviour)}, "
          f"BEHAVIOUR {len(behaviour)}")

    print("\nTHE `-SIM` SUFFIX IN LIVE STRING LITERALS, not in prose about it")
    lits = []
    for p_, rel in _live_python():
        src = p_.read_text(encoding="utf-8", errors="replace")
        if "-SIM" not in src:
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        doc_nodes = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                                 ast.AsyncFunctionDef)):
                d = ast.get_docstring(node, clean=False)
                if d is not None and node.body:
                    doc_nodes.add(id(node.body[0]))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Constant) or \
                    not isinstance(node.value, str):
                continue
            if "-SIM" not in node.value:
                continue
            parent_is_doc = any(
                isinstance(e, ast.Expr) and e.value is node and id(e) in doc_nodes
                for e in ast.walk(tree))
            if parent_is_doc:
                continue
            where = ("FACILITY" if rel in SIMULATION_FACILITY else "LIVE PATH")
            lits.append((where, rel, node.lineno,
                         node.value.replace("\n", " ")[:72]))
    counts: dict[str, int] = {}
    for where, *_ in lits:
        counts[where] = counts.get(where, 0) + 1
    for where, n in sorted(counts.items()):
        print(f"  {where}: {n} literal(s)")
    for where, rel, n, val in sorted(lits):
        if where == "LIVE PATH":
            print(f"      {rel}:{n}  {val!r}")

    print("\nCAN A STAND-IN FINGERPRINT REACH A PAID RUN?")
    import dataclasses
    import bench.reference_runner_v3 as runner
    declared = {f.name: f.default
                for f in dataclasses.fields(runner.RunnerConfig)}
    scope = declared.get("fingerprint_scope")
    runner.set_fingerprint_scope("experiment")
    under_experiment = len(runner._load_fingerprint_cache())
    runner.set_fingerprint_scope("persist")
    under_persist = runner._load_fingerprint_cache()
    sim_records = sorted(k for k in under_persist if str(k).endswith("-SIM"))
    runner.set_fingerprint_scope(str(scope))
    print(f"  RunnerConfig.fingerprint_scope default : {scope!r}")
    print(f"  records under 'persist'                : {len(under_persist)}"
          f"  (stand-ins: {len(sim_records)})")
    print(f"  records under 'experiment'             : {under_experiment}")
    print(f"  stand-in records present              : {sim_records}")
    reachable = (scope != "experiment") and bool(sim_records)
    print(f"  could a stand-in inform a paid run?    : "
          f"{'YES -- this needs excluding' if reachable else 'no'}")

    print("\nVERDICT")
    clean = not behaviour and not reachable
    if clean:
        print("  every simulation-gated branch is a CAVEAT and keys off the")
        print("  `-SIM` suffix, so a paid run turns them off by having no such")
        print("  seat. No stand-in fingerprint can reach a paid run, because")
        print("  the fingerprint scope defaults to measuring afresh. The")
        print("  exclusion his ruling asks for is STRUCTURAL rather than")
        print("  something to remember, and the lessons carry forward because")
        print("  they were never conditional on simulation in the first place.")
        return 0
    if behaviour:
        print(f"  {len(behaviour)} branch(es) CHANGE BEHAVIOUR on simulation and")
        print("  must be excluded by hand before a paid run:")
        for rel, n, _, snippet in behaviour:
            print(f"      {rel}:{n}  {snippet}")
    if reachable:
        print("  stand-in fingerprints could inform a paid run; set")
        print("  fingerprint_scope to 'experiment' or reset the store first.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
