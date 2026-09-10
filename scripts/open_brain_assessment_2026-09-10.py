#!/usr/bin/env python3
"""Task A1: how complete, functional and useful is Open Brain?

MEASURED, and committed alongside the figures (`measured-rate-travels-with-its-script`).

HIS INSTRUCTION, verbatim: "This is the problem OpenBrain was original built to
solve. I have never fully tested yet how complete/functional, or useful it is,
but perhaps this is another task you can add to the bottom of the existing task
list."

THREE QUESTIONS, EACH MADE FALSIFIABLE BEFORE BEING ANSWERED.

  FUNCTIONAL -- does each subcommand run to a result? Every read-only one is
  invoked and its exit status recorded. Nothing that writes is run.

  COMPLETE -- is every advertised subcommand backed by something that works? A
  command that exists in `--help` and fails on a missing table is advertised and
  not delivered, which is the additive standard's unwired half in a CLI.

  USEFUL -- is it actually reached? Usage is measured from the corpus: how much
  is stored, how recently, and how many places in this repository invoke it.

MY FIRST PASS REPORTED 5 WORKING SUBCOMMANDS AS BROKEN. A shell loop split their
arguments wrongly, so each returned its usage text and I read that as a failure.
That is why this is a script and not a session of hand-typed commands: the
harness is now the thing under test as much as the tool is.
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

#: Read-only invocations. Each is a full argv, so nothing is word-split by a
#: shell -- the mistake that produced the first, wrong assessment.
READ_ONLY = [
    ["status"],
    ["project-labels"],
    ["verify"],
    ["list-recent", "--limit", "3"],
    ["pending-tasks"],
    ["session-context", "--agent", "cc"],
    ["search", "convergence", "--limit", "3"],
    ["list-epochs"],
    ["verify-epochs"],
]

#: Advertised but NOT run here, and why. Naming them is part of the answer.
NOT_RUN = {
    "capture": "writes a memory",
    "update-task": "writes a task status",
    "import": "writes many memories",
    "export": "writes a file",
    "seal-epoch": "writes an epoch, and is irreversible by design",
    "migrate": "changes the schema",
    "generate-keys": "writes a keypair",
    "prove": "needs a memory id",
    "reasoning": "needs an agent argument that varies",
    "verify-reasoning": "needs an agent argument that varies",
    "im": "a separate sub-CLI with its own surface",
}


def run(args, timeout=180):
    r = subprocess.run([sys.executable, "-m", "open_brain.cli", *args],
                       cwd=REPO, capture_output=True, text=True, timeout=timeout)
    out = (r.stdout or "") + (r.stderr or "")
    # A subcommand that prints its own usage did not do what was asked, whatever
    # its exit status. That distinction is what the first assessment missed.
    printed_usage = out.lstrip().startswith("usage:")
    # A NON-ZERO EXIT IS NOT A FAILURE, and conflating them would have
    # mislabelled the most informative command in the set. `verify` exits 1
    # because it FOUND something -- 7 memories written after the hashing
    # migration that carry no hash -- and reports it in full. That is the tool
    # working. "Failed" here means it could not run to a result at all.
    failed = bool(re.search(r"^Error:|Traceback", out, re.M)) or printed_usage
    return {"argv": " ".join(args), "exit": r.returncode, "failed": failed,
            "printed_usage": printed_usage, "out": out,
            "nonzero_but_ran": (r.returncode != 0 and not failed),
            "first_line": (out.strip().splitlines() or [""])[0][:100]}


def advertised() -> list:
    r = subprocess.run([sys.executable, "-m", "open_brain.cli", "--help"],
                       cwd=REPO, capture_output=True, text=True, timeout=120)
    m = re.search(r"\{([a-z0-9,\-]+)\}", r.stdout)
    return m.group(1).split(",") if m else []


def callers() -> dict:
    """Where in THIS repository is Open Brain actually invoked?"""
    hits = {}
    for pat in ("*.py", "*.sh", "*.md"):
        for d in ("scripts", "bench", "resources", "hooks", ".claude", "docs"):
            base = REPO / d
            if not base.is_dir():
                continue
            for p in base.rglob(pat):
                try:
                    t = p.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                n = t.count("open_brain")
                if n:
                    hits[str(p.relative_to(REPO))] = n
    return hits


def main() -> int:
    cmds = advertised()
    print(f"--- ADVERTISED SUBCOMMANDS: {len(cmds)} ---")
    print(f"  {', '.join(cmds)}\n")

    print("--- FUNCTIONAL: every read-only subcommand, invoked ---")
    results = [run(a) for a in READ_ONLY]
    for r in results:
        mark = "FAIL" if r["failed"] else ("ran" if r["nonzero_but_ran"] else "ok ")
        print(f"  [{mark}] {r['argv']:34s} exit={r['exit']}  {r['first_line']}")
    ok = sum(1 for r in results if not r["failed"])
    from statsmodels.stats.proportion import proportion_confint
    lo, hi = proportion_confint(ok, len(results), method="wilson")
    lo_c, hi_c = proportion_confint(ok, len(results), method="beta")
    print(f"\n  {ok} of {len(results)} run to a result = {ok/len(results):.4%}")
    print(f"  Wilson 95%          : [{lo:.4%}, {hi:.4%}]")
    print(f"  Clopper-Pearson 95% : [{lo_c:.4%}, {hi_c:.4%}]")

    print(f"\n--- COMPLETE: advertised against exercised ---")
    print(f"  advertised: {len(cmds)}")
    print(f"  exercised here: {len({a[0] for a in READ_ONLY})}")
    print(f"  NOT run, and why:")
    for k, why in sorted(NOT_RUN.items()):
        print(f"    {k:18s} {why}")
    broken = [r for r in results if r["failed"]]
    if broken:
        print(f"\n  ADVERTISED BUT NOT DELIVERED: {len(broken)}")
        for r in broken:
            print(f"    {r['argv']}: {r['first_line']}")

    print("\n--- INTEGRITY: what the hash chain actually covers ---")
    v = run(["verify"])
    for line in v["out"].splitlines()[:4]:
        print("  " + line)
    m_valid = re.search(r"Valid:\s*(\d+)", v["out"])
    m_tot = re.search(r"verification:\s*(\d+)", v["out"])
    m_after = re.search(r"WRITTEN AFTER MIGRATION:\s*(\d+)", v["out"])
    if m_valid and m_tot:
        k2, n2 = int(m_valid.group(1)), int(m_tot.group(1))
        lo_v, hi_v = proportion_confint(k2, n2, method="wilson")
        print("  hashed and valid: %d of %d = %.4f%%  Wilson [%.4f%%, %.4f%%]"
              % (k2, n2, 100*k2/n2, 100*lo_v, 100*hi_v))
    if m_after:
        print("  written AFTER the migration with no hash: %s -- a capture path "
              "not under the chain" % m_after.group(1))

    print("\n--- USEFUL: is it reached? ---")
    lbl = run(["project-labels"])
    print(f"  {lbl['first_line']}")
    rec = run(["list-recent", "--limit", "1"])
    m = re.search(r"(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)", rec["first_line"])
    print(f"  most recent memory: {m.group(1) if m else '(none parsed)'}")
    c = callers()
    print(f"  files in this repository that name open_brain: {len(c)}")
    for k, v in sorted(c.items(), key=lambda x: -x[1])[:8]:
        print(f"    {v:4d}x  {k}")
    if len(c) > 8:
        print(f"    ... and {len(c) - 8} more not shown")
    return 0


if __name__ == "__main__":
    sys.exit(main())
