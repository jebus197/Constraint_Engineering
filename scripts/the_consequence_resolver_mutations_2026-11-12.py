#!/usr/bin/env python3
"""Revert each branch of the consequence resolver and prove its guard goes RED.

★ WHY. `bench/cdsfl_registry/domain_vocabulary.py:consequence_domain` was added
on 2026-11-12 as entry B162, on his instruction to build the fix for the
steering disagreement. A claim that its guard bites is a claim about evidence,
so the producer is committed beside it -- `measured-rate-travels-with-its-script`.

★ ITS GUARD ALREADY CAUGHT ONE FAULT IN THE SUBJECT, BEFORE THIS HARNESS RAN.
The first version returned `scale: "composed"` while reporting
`resolved: False`, which is a scale on an answer that has none.
`test_a_resolved_answer_always_carries_a_scale_and_an_unresolved_never_does`
failed on it, and the CONTRACT was tightened rather than the test weakened.

★ ANCHORS ARE DERIVED FROM THE LIVE FILE, never retyped, so a rename cannot
leave a mutation silently matching nothing and reporting a pass as a kill --
the fault recorded twice in this project's own mutation harnesses on this day.

★ RESTORE IS BYTE-EXACT AND FROM WHAT WAS FOUND, with the sha256 compared after
writing back, because the subject is a module 9 other files import.

Costs nothing but local CPU: 1 pytest file per mutation, no model dispatch.
"""
from __future__ import annotations

import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SUBJECT = REPO / "bench" / "cdsfl_registry" / "domain_vocabulary.py"
GUARD = REPO / "bench" / "tests" / "test_the_consequence_domain_is_resolved_2026-11-12.py"


def mutations(src: str) -> list[tuple[str, str, str]]:
    """(name, find, replace), every `find` lifted from the live source."""
    m = []
    a = 'if sev["scale"] not in (None, "none", "composed"):'
    m.append(("a declared scale is no longer preferred over inheritance", a,
              'if False:'))
    b = 'if application is None:'
    m.append(("a missing application silently inherits instead of refusing", b,
              'if False:'))
    c = 'if app_sev["scale"] in (None, "none", "composed"):'
    m.append(("an inheritance chain that does not terminate is accepted", c,
              'if False:'))
    d = 'if not sev["inherits_from_application"]:'
    m.append(("the inheritance FLAG is ignored, as it was before this entry", d,
              'if False:'))
    e = '"subject": subj, "consequence": app, "how": "inherited"'
    m.append(("the subject is overwritten by the consequence", e,
              '"subject": app, "consequence": app, "how": "inherited"'))
    f = '"scale": None, "critical_level": None, "resolved": False,\n                "why": (f"{subj} inherits its scale from the application it "'
    m.append(("an unresolved answer claims to be resolved", f,
              '"scale": None, "critical_level": None, "resolved": True,\n                "why": (f"{subj} inherits its scale from the application it "'))
    g = 'if (sev["inherits_from_application"] or sev["composes_from_selected"]'
    m.append(("the inheriting-domain census stops counting inheritance", g,
              'if (False or sev["composes_from_selected"]'))
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
        print("REFUSED: the guard is not green before any mutation, so no kill "
              "can be attributed to a mutation.")
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
