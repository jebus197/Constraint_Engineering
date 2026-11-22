#!/usr/bin/env python3
"""How many guards restore the BYTES they mutate but not the TIMESTAMP?

ENTRY B201 recorded this defect in 1 guard and fixed it there: a test mutated a
live record, restored the bytes in a `finally`, and left the modification time
moved -- which made a downstream currency check go red on 3 separate sweeps,
naming a record whose CONTENT had not changed. The fix was a context manager
restoring bytes AND `os.utime`.

THIS SCRIPT ASKS WHETHER THAT FIX REACHED ITS CLASS, and it exists because a
figure quoted in prose is a claim about evidence rather than evidence.

CAUGHT LIVE, 2026-11-22, WHICH IS WHY THE QUESTION WAS ASKED. During a commit
board, 3 repository files were modified while `git status --porcelain` reported
nothing unstaged -- all 3 byte-identical to their HEAD blobs, so invisible to git
by construction:

    experimental_notes/Morning_Report_2026-10-30.md
    bench/tests/test_the_severity_proxy_was_never_tested_2026-10-28.py
    experimental_notes/Mathematical_Model_Audit_2026-04-08.md

and `test_the_severity_frame_counts_one_run_twice_2026-11-04.py:103` writes the
2nd of those, restores it in a `finally`, and calls `os.utime` 0 times.

★ WHAT THIS MEASURES AND WHAT IT DOES NOT, STATED BECAUSE THE DIFFERENCE IS THE
WHOLE HONESTY OF THE FIGURE. The predicate is a TEXT scan: a file that calls
`write_text` and carries a `finally` and never calls `utime`. It CANNOT tell a
guard writing a scratch path from one writing a repository path, and a guard
writing only under `tmp_path` is harmless. **So the result is an UPPER BOUND on
the population at risk, never a count of defects.** Narrowing it would need each
write target resolved, which is a different and much larger instrument.

It is reported, never enforced. Nothing here refuses a commit.
"""
from __future__ import annotations

import math
import pathlib
import re
import sys

WRITE = re.compile(r"\.write_text\(")
FINALLY = re.compile(r"\bfinally\b")
UTIME = re.compile(r"os\.utime|\butime\(")
#: A guard writing only under a temp directory cannot move a repository
#: timestamp. This NARROWS the population; it does NOT clear what it excludes,
#: because a file may mention `tmp_path` AND also write a repository path --
#: which is exactly what the confirmed instance does.
TEMP = re.compile(r"tmp_path|TemporaryDirectory|mkdtemp|tmpdir")


def scan(root: pathlib.Path) -> tuple[list[str], list[str], int]:
    """(at_risk, restores_timestamp, files_scanned)."""
    at_risk, safe, n = [], [], 0
    for p in sorted(root.glob("test_*.py")):
        n += 1
        t = p.read_text(errors="ignore")
        if not (WRITE.search(t) and FINALLY.search(t)):
            continue
        if UTIME.search(t):
            safe.append(p.name)
        else:
            at_risk.append((p.name, bool(TEMP.search(t))))
    return at_risk, safe, n


def _intervals(k: int, n: int):
    """Wilson and Clopper-Pearson, each on 2 routes, as this project requires."""
    from statsmodels.stats.proportion import proportion_confint
    import scipy.stats as st
    p = k / n
    lo1, hi1 = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = st.norm.ppf(0.975)
    den = 1 + z * z / n
    cen = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    lo3, hi3 = proportion_confint(k, n, alpha=0.05, method="beta")
    return (p, (lo1, hi1), (cen - half, cen + half), (lo3, hi3))


def main() -> int:
    here = pathlib.Path(__file__).resolve()
    repo = next((c for c in [here.parent, *here.parents]
                 if (c / "bench" / "tests").is_dir()),
                pathlib.Path.home() / "Developer_Projects" / "Constraint_Engineering")
    tests = repo / "bench" / "tests"
    if not tests.is_dir():
        print(f"no guard directory at {tests}")
        return 2

    at_risk, safe, scanned = scan(tests)
    n = len(at_risk) + len(safe)
    print("=" * 74)
    print("DOES B201's TIMESTAMP-RESTORE FIX REACH ITS CLASS?")
    print("=" * 74)
    print(f"  guard files scanned                        : {scanned}")
    print(f"  writing a path AND restoring in a `finally`: {n}")
    print(f"  of those, restoring the timestamp too      : {len(safe)}")
    print(f"  of those, NOT restoring it                 : {len(at_risk)}")

    if n:
        p, w1, w2, cp = _intervals(len(at_risk), n)
        print(f"\n  share at risk: {len(at_risk)}/{n} = {p:.6f}")
        print(f"    Wilson statsmodels [{w1[0]:.6f}, {w1[1]:.6f}]")
        print(f"    Wilson closed form [{w2[0]:.6f}, {w2[1]:.6f}]"
              f"  agree {max(abs(w1[0]-w2[0]), abs(w1[1]-w2[1])):.2e}")
        print(f"    Clopper-Pearson    [{cp[0]:.6f}, {cp[1]:.6f}]")

    print(f"\n  the {len(safe)} that DO restore the timestamp:")
    for x in safe:
        print(f"    {x}")

    no_temp = [name for name, has_temp in at_risk if not has_temp]
    if at_risk:
        p2, w1b, w2b, cpb = _intervals(len(no_temp), len(at_risk))
        print(f"\n  NARROWED: of the {len(at_risk)} at risk, {len(no_temp)} mention no temp")
        print(f"  directory at all, so are likelier to write a repository path.")
        print(f"    {len(no_temp)}/{len(at_risk)} = {p2:.6f}")
        print(f"    Wilson statsmodels [{w1b[0]:.6f}, {w1b[1]:.6f}]")
        print(f"    Clopper-Pearson    [{cpb[0]:.6f}, {cpb[1]:.6f}]")
        for x in no_temp:
            print(f"      {x}")

    print("\n  UPPER BOUND, NOT A DEFECT COUNT. The predicate is a text scan and")
    print("  cannot distinguish a write to a scratch path from a write to a")
    print("  repository path. A guard writing only under `tmp_path` is harmless")
    print("  and is counted here anyway.")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
    try:
        from _cli_help import answer_help
        answer_help(__doc__, __file__)
    except ImportError:
        pass
    sys.exit(main())
