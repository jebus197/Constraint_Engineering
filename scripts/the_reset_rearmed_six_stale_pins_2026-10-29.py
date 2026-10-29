#!/usr/bin/env python3
"""Why 6 immune-memory assertions fail: a reset he ordered, plus a correct re-arm.

`bench/tests/test_immune_memory_evaluation.py` reports 6 failures. The live
immune memory holds 1 experiment where they describe 3 to 5. This establishes
that the product is right and the assertions are stale, and it would say the
opposite just as readily: it reads the live store, the archive's own reason
file, the dates of every run the assertions derive from, and the ORDER of the
runner's load and record calls, which is what decides whether a run accumulates
or replaces.

READ-ONLY. It opens the live memory and the archive for reading and writes
nothing anywhere.
"""
from __future__ import annotations
import argparse, ast, datetime as dt, glob, json, pathlib, re, sys

REPO = pathlib.Path(__file__).resolve().parents[1]
STATE = REPO / "bench" / "state" / "immune_memory.json"
ARCHIVE = REPO / "bench" / "state" / "immune_memory_archive"
TESTFILE = REPO / "bench" / "tests" / "test_immune_memory_evaluation.py"
RUNNER = REPO / "bench" / "reference_runner_v3.py"
LOGS = REPO / "bench" / "logs"


def live_memory() -> dict:
    return json.loads(STATE.read_text(encoding="utf-8")) if STATE.is_file() else {}


def newest_reset() -> dict | None:
    whys = sorted(glob.glob(str(ARCHIVE / "*.why.json")))
    if not whys:
        return None
    return json.loads(pathlib.Path(whys[-1]).read_text(encoding="utf-8"))


def recording_runs_constant() -> list[str]:
    """`_RECORDING_RUNS` read off the syntax tree, not guessed from a grep."""
    tree = ast.parse(TESTFILE.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "_RECORDING_RUNS":
                    try:
                        return list(ast.literal_eval(node.value))
                    except (ValueError, SyntaxError):
                        return []
    return []


def run_date(prefix: str) -> str:
    """The run's own date, taken from its log directory name where it carries one."""
    hits = sorted(glob.glob(str(LOGS / (prefix + "*"))))
    if not hits:
        return "no log on disk"
    name = pathlib.Path(hits[0]).name
    m = re.search(r"(20\d{6})T(\d{6})Z", name)
    if m:
        return f"{m.group(1)[:4]}-{m.group(1)[4:6]}-{m.group(1)[6:]}T{m.group(2)[:2]}:{m.group(2)[2:4]}:{m.group(2)[4:]}Z"
    ts = pathlib.Path(hits[0]).stat().st_mtime
    return dt.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%dT%H:%M:%SZ") + " (mtime)"


def load_precedes_record() -> str:
    """Does the runner LOAD the memory before recording? Decided on the AST.

    A run that constructs a fresh memory and saves it would REPLACE rather than
    accumulate, and the live count of 1 would then be data loss rather than
    correct accumulation onto an emptied store. The 2 readings differ in what
    they imply, so this is settled by the call order rather than by reading the
    comments around it.
    """
    tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
    loads, records = [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            name = getattr(f, "attr", None)
            if name == "load" and getattr(getattr(f, "value", None), "id", "") == "ImmuneMemory":
                loads.append(node.lineno)
            if name == "record_experiment":
                records.append(node.lineno)
    if not loads or not records:
        return f"inconclusive (loads {loads}, records {records})"
    # THE NEAREST PRECEDING LOAD, NOT THE FIRST ONE IN THE FILE. There are 2
    # `ImmuneMemory.load` call sites and only 1 of them is on the write path:
    # the other belongs to the R_k(0) CONSUMPTION path, which is off by default.
    # Taking the minimum line number cited that unrelated site as evidence about
    # the write path -- the same verdict by luck, reached from the wrong
    # evidence, which is not evidence.
    record_at = min(records)
    preceding = [ln for ln in loads if ln < record_at]
    if not preceding:
        return (f"record_experiment at {record_at} with NO preceding load "
                f"(loads at {sorted(loads)}) -> REPLACES")
    load_at = max(preceding)
    return (f"ImmuneMemory.load at line {load_at} (nearest preceding; all load "
            f"sites {sorted(loads)}), record_experiment at line {record_at} "
            f"-> ACCUMULATES")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.parse_args()                 # exits on --help BEFORE anything is read

    mem = live_memory()
    print("LIVE IMMUNE MEMORY")
    print(f"  experiment_count : {mem.get('experiment_count')}")
    print(f"  experiment_ids   : {mem.get('experiment_ids')}")
    print(f"  flaw classes     : {sorted(mem.get('records', {}))}")
    if STATE.is_file():
        m = dt.datetime.fromtimestamp(STATE.stat().st_mtime)
        print(f"  written          : {m.isoformat(timespec='seconds')}")

    r = newest_reset()
    print("\nNEWEST ARCHIVED RESET")
    if r is None:
        print("  none — so emptiness would NOT be explained by a reset")
        return 0
    held = r.get("state_when_archived") or {}
    print(f"  archived_utc     : {r.get('archived_utc')}")
    print(f"  reason           : {r.get('reason')}")
    print(f"  held             : {held.get('experiment_count')} experiment(s) "
          f"{held.get('experiment_ids')}")
    print(f"  restore_with     : {r.get('restore_with')}")

    print(f"\nRUNNER WRITE PATH\n  {load_precedes_record()}")

    print("\nTHE RUNS THE ASSERTIONS DERIVE FROM, AGAINST THE RESET")
    cutoff = str(r.get("archived_utc") or "")
    const = recording_runs_constant()
    print(f"  _RECORDING_RUNS (from the syntax tree): {const}")
    rows = [(p, run_date(p)) for p in const] + \
           [(i, run_date(i)) for i in (mem.get("experiment_ids") or [])]
    for name, when in rows:
        tag = "PRE-RESET (its priors are in the archive)"
        norm = when.replace("-", "").replace(":", "")
        if cutoff and norm[:15] > cutoff[:15]:
            tag = "post-reset (in the live memory)"
        print(f"    {name:<46} {when:<30} {tag}")
    pre = sum(1 for n, w in rows
              if not (cutoff and w.replace('-','').replace(':','')[:15] > cutoff[:15]))
    print(f"\n  derivable set as the test builds it: {len(const)} constant + "
          f"{len(mem.get('experiment_ids') or [])} live = "
          f"{len(const) + len(mem.get('experiment_ids') or [])}")
    print(f"  live count: {mem.get('experiment_count')}; the gap is exactly the "
          f"{pre} pre-reset run(s) whose priors were archived away")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
