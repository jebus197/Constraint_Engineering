#!/usr/bin/env python3
"""Revert each piece of the steering recovery path and prove its guard goes RED.

★ WHY. `bench/cdsfl_registry/domain_proposer.py` gained the recovery path on
2026-11-12 as entry B161, on his instruction and to his design. A claim that its
guard bites is a claim about evidence, so the producer is committed beside it.

★ IT MUTATES 3 SEPARABLE PIECES, because the entry is 3 pieces: the repair
phrasings, the additive profile, and the mismatch test. A harness that mutated
only the mismatch test would report a score the other 2 had not earned.

★ ANCHORS DERIVED FROM THE LIVE FILE. A retyped anchor is a second spelling of
the subject, and this project's harnesses produced 2 false misses from exactly
that on this day.

★ RESTORE IS BYTE-EXACT, sha256 compared after writing back, because the subject
is a module the reference runner reaches.

Costs nothing but local CPU: 1 pytest file per mutation, no model dispatch.
"""
from __future__ import annotations

import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SUBJECT = REPO / "bench" / "cdsfl_registry" / "domain_proposer.py"
GUARD = REPO / "bench" / "tests" / "test_the_steering_chat_can_recover_2026-11-12.py"


def mutations(src: str) -> list[tuple[str, str, str]]:
    m = []
    a = "    return REPAIR_PHRASINGS[int(attempt) % len(REPAIR_PHRASINGS)]"
    m.append(("the repair always says the same thing, so it reads as a script",
              a, "    return REPAIR_PHRASINGS[0]"))
    b = '    if pr.get("ambiguous"):'
    m.append(("an ambiguous proposal is absorbed by the loaded profile",
              b, "    if False:"))
    c = "    if not loaded:"
    m.append(("no loaded profile no longer triggers the first steering chat",
              c, "    if False:"))
    d = '    if pr.get("domain") in loaded:'
    m.append(("a domain already loaded is asked about again anyway",
              d, "    if True:"))
    e = "    if d not in doms:\n        doms.append(d)"
    m.append(("the profile stops being additive and drops what was loaded",
              e, "    doms = [d]"))
    f = "    d = V.resolve(domain)   # the ONE vocabulary, never a second resolver"
    m.append(("an alias is stored unnormalised, so the profile holds 2 names "
              "for 1 domain", f, "    d = domain"))
    g = "    out = dict(profile or {})"
    m.append(("accept mutates the profile it was given",
              g, "    out = profile if profile is not None else {}"))
    h = "    pr = propose(task, vocab)"
    m.append(("the mismatch test decides again instead of delegating to propose",
              h, '    pr = {"domain": loaded[0] if loaded else None, '
                 '"ambiguous": False, "subdomain": None, "reason": "", '
                 '"top": [], "margin": 1.0}'))
    return m


def run_guard() -> tuple[int, str]:
    p = subprocess.run([sys.executable, "-m", "pytest", str(GUARD), "-q",
                        "--no-header", "-p", "no:cacheprovider"],
                       capture_output=True, text=True, cwd=str(REPO))
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main() -> int:
    original = SUBJECT.read_bytes()
    sha = hashlib.sha256(original).hexdigest()
    src = original.decode("utf-8")

    rc, out = run_guard()
    print(f"BASELINE: rc={rc}  {out.strip().splitlines()[-1] if out.strip() else ''}")
    if rc != 0:
        print("REFUSED: not green before any mutation, so no kill can be "
              "attributed to a mutation.")
        return 2

    rows, applied, killed = [], 0, 0
    try:
        for name, find, repl in mutations(src):
            if src.count(find) != 1:
                rows.append((name, "NOT APPLIED",
                             f"anchor occurs {src.count(find)} times, not once"))
                continue
            applied += 1
            with open(SUBJECT, "w", encoding="utf-8") as fh:
                fh.write(src.replace(find, repl, 1))
            rc, out = run_guard()
            tail = out.strip().splitlines()[-1] if out.strip() else ""
            if rc != 0:
                killed += 1
                rows.append((name, "RED", tail))
            else:
                rows.append((name, "SURVIVED", tail))
    finally:
        with open(SUBJECT, "w", encoding="utf-8") as fh:
            fh.write(src)
        ok = hashlib.sha256(SUBJECT.read_bytes()).hexdigest() == sha
        print(f"\nRESTORE: sha256 {'MATCHES' if ok else 'DIFFERS -- INVESTIGATE'}")
        if not ok:
            return 3

    print()
    for name, verdict, tail in rows:
        print(f"  [{verdict:11s}] {name}")
        if verdict != "RED":
            print(f"                {tail}")
    print(f"\n{killed} of {applied} applied mutation(s) RED"
          f"  ({len(rows) - applied} not applied)")
    return 0 if applied and killed == applied else 1


if __name__ == "__main__":
    # A `--help` MUST NOT run: this script WRITES, mutating a tracked file
    # in place and restoring it from the bytes it read first.
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    raise SystemExit(main())
