#!/usr/bin/env python3
"""Does the `cy` watchdog's TROUBLE channel raise alarms on ordinary prose?

READY TO DROP INTO `scripts/` AFTER THE BATCH 1 COMMIT. Written while that
board ran, when the tree must not be edited.

WHAT IS WRONG. `scripts/cy_watchdog_2026-10-02.py` builds `TROUBLE` with a bare
`OOM` under `re.I` and no word boundary, so it matches the letters `oom`
wherever they fall: `Headroom`, `bedroom`, `zoom`, `mushroom`, `showroom`,
`broom`, and `the room was quiet`.

OBSERVED, NOT HYPOTHESISED. Attaching a watchdog to the batch 1 commit board on
2026-11-22 produced 3 TROUBLE events within its first second. 2 of the 3 matched
`oom` inside `Headroom:` — and one of those lines reads
`[PASS] memory-index-headroom`, so a PASS was reported as trouble. The 3rd
matched `32 FAILED` inside `sv`'s citation of a PAST measurement, which is a
DIFFERENT and harder problem (a citation is not an event) and is deliberately
NOT addressed here.

WHY IT MATTERS MORE THAN ITS RATE. This is the channel the founder's standing
`cy` directive depends on, and the watchdog's own source already argues the
point at length: *"A channel that cries wolf teaches its reader to ignore it,
and an ignored alarm is the 9-hour hole again by another route."* The file had
already removed bare status codes for exactly this reason.

WHY THE FIX IS A WORD BOUNDARY AND NOT CASE SENSITIVITY. Making `OOM`
case-sensitive would also stop the false matches, and it would be WRONG: Linux
writes `oom-killer` in lower case, so a case fix loses a genuine signal while
the boundary form keeps it (a hyphen is a word boundary). Both directions are
measured below rather than argued.

BOTH DIRECTIONS, BECAUSE NARROWING A TROUBLE CHANNEL RISKS LOSING A CRASHLOOP.
Over-catching costs one spurious notification. Under-catching costs hours of an
unobserved run. So the genuine-signal set is checked FIRST and a single loss
fails this script.
"""
from __future__ import annotations

import glob
import importlib.util
import pathlib
import re
import sys

def _find_repo() -> pathlib.Path:
    """Walk up for the watchdog this script measures.

    Resolving `parents[1]` from __file__ is correct ONLY once this script sits
    in `scripts/`. It was written and verified from a scratch directory while a
    commit board held the tree, so it locates the repository by looking for the
    file it measures instead of by counting directories.
    """
    here = pathlib.Path(__file__).resolve()
    for cand in [here.parent, *here.parents]:
        if (cand / "scripts" / "cy_watchdog_2026-10-02.py").is_file():
            return cand
    fallback = pathlib.Path.home()/"Developer_Projects"/"Constraint_Engineering"
    if (fallback / "scripts" / "cy_watchdog_2026-10-02.py").is_file():
        return fallback
    raise SystemExit("cannot locate the repository: cy_watchdog_2026-10-02.py not found")


REPO = _find_repo()
WATCHDOG = REPO / "scripts" / "cy_watchdog_2026-10-02.py"

#: Signals that MUST still speak. A single loss here fails the script.
MUST_CATCH = [
    "OOM",
    "oom",
    "OOM-killer invoked",
    "oom-killer invoked",
    "Out of memory: Killed process 123 (python)",
    "Killed: 9",
    "java.lang.OutOfMemoryError: Java heap space",
    "cgroup out of memory: OOM victim",
]

#: Ordinary prose that must NOT speak.
MUST_NOT = [
    "Headroom: 1563 characters",
    "[PASS] memory-index-headroom: 22937 characters (1563 left)",
    "bedroom", "zoom in on the chart", "the room was quiet",
    "mushroom", "showroom floor", "broom closet",
]


def live_trouble():
    spec = importlib.util.spec_from_file_location("wd_probe", WATCHDOG)
    m = importlib.util.module_from_spec(spec)
    sys.modules["wd_probe"] = m
    spec.loader.exec_module(m)
    return m.TROUBLE


def boundaried(rx):
    """The proposed regex: the ONLY change is a word boundary on OOM."""
    assert "OOM" in rx.pattern, "the OOM token has moved; re-read the regex"
    return re.compile(rx.pattern.replace(r"OOM", r"\bOOM\b"), rx.flags)


def corpus_rows():
    """Every TROUBLE/BACKLOG line the watchdog has ever written, on record."""
    rows = []
    for f in sorted(glob.glob(str(REPO / "bench" / "logs" / "*" / "cy_watchdog.log"))):
        for ln in pathlib.Path(f).read_text(errors="ignore").splitlines():
            if "TROUBLE" in ln or "BACKLOG LINE" in ln:
                rows.append(ln.split("] ", 1)[-1])
    return rows


def main() -> int:
    cur = live_trouble()
    prop = boundaried(cur)

    lost = [s for s in MUST_CATCH if cur.search(s) and not prop.search(s)]
    fixed = [s for s in MUST_NOT if cur.search(s) and not prop.search(s)]
    still = [s for s in MUST_NOT if prop.search(s)]

    print("GENUINE SIGNALS — a single loss fails this script")
    for s in MUST_CATCH:
        a, b = bool(cur.search(s)), bool(prop.search(s))
        print(f"  cur={str(a):5s} prop={str(b):5s} {'LOST' if a and not b else '    '} {s[:56]}")
    print(f"\n  genuine signals lost: {len(lost)} of {len(MUST_CATCH)}")

    print("\nORDINARY PROSE — must not speak")
    for s in MUST_NOT:
        a, b = bool(cur.search(s)), bool(prop.search(s))
        print(f"  cur={str(a):5s} prop={str(b):5s} {'fixed' if a and not b else '     '} {s[:56]}")
    print(f"\n  false alarms removed: {len(fixed)} of {len(MUST_NOT)}")
    print(f"  false alarms remaining: {len(still)}")

    rows = corpus_rows()
    flagged = [r for r in rows if cur.search(r)]
    kept = [r for r in flagged if prop.search(r)]
    dropped = [r for r in flagged if not prop.search(r)]
    print(f"\nTHE WHOLE CORPUS, so the change is not judged on tonight alone")
    print(f"  watchdog logs on record       : "
          f"{len(set(glob.glob(str(REPO/'bench'/'logs'/'*'/'cy_watchdog.log'))))}")
    print(f"  lines the current regex flags : {len(flagged)}")
    print(f"  still flagged after the fix   : {len(kept)}")
    print(f"  dropped by the word boundary  : {len(dropped)}")
    #: ★ THE CAP IS KEPT AND THE REMAINDER IS NAMED. 4 examples is the useful
    #: number -- a reader wants to see the SHAPE of what the word boundary
    #: removed, not every instance -- but a list cut to 4 under a heading that
    #: already printed the full count reads as complete, which is a silent
    #: falsehood. Raised by the free panel's joint round on 2026-11-22 and
    #: confirmed by running the project's own guard rather than on the seat's
    #: word: `TestTruncatedListsStateTheirRemainder` was RED on this line.
    _SHOW = 4
    for d in dropped[:_SHOW]:
        print(f"      dropped: {d.strip()[:92]}")
    if len(dropped) > _SHOW:
        print(f"      ... and {len(dropped) - _SHOW} more not shown "
              f"({len(dropped)} dropped in all; this listing is capped at "
              f"{_SHOW} examples)")

    if flagged:
        from statsmodels.stats.proportion import proportion_confint
        import numpy as np
        import scipy.stats as st
        n, k = len(flagged), len(dropped)
        p = k / n
        lo1, hi1 = proportion_confint(k, n, 0.05, "wilson")
        lo2, hi2 = proportion_confint(k, n, 0.05, "beta")
        z = st.norm.ppf(0.975)
        den = 1 + z * z / n
        c = (p + z * z / (2 * n)) / den
        hw = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
        print(f"\n  spurious share : {p:.6f}")
        print(f"    Wilson statsmodels [{lo1:.6f}, {hi1:.6f}]")
        print(f"    Wilson closed form [{c-hw:.6f}, {c+hw:.6f}]  agree {abs((c-hw)-lo1):.3e}")
        print(f"    Clopper-Pearson    [{lo2:.6f}, {hi2:.6f}]")
        print("\n  AND THE HONEST READING: a low share here does NOT mean a low")
        print("  forward rate. The corpus barely exercises the defect, because")
        print("  no watchdog had ever watched an `sv` log before 2026-11-22.")
        print("  State the MECHANISM and the DOMINANCE, never the frequency.")

    ok = not lost and not still
    print(f"\n{'STRICTLY DOMINANT: false alarms removed at 0 cost to genuine signals.' if ok else 'FAILED'}")
    return 0 if ok else 1


if __name__ == "__main__":
    #: ANSWER `--help` WITHOUT DOING THE WORK. The guard EXECUTES any
    #: script whose behaviour it cannot establish structurally, so a
    #: producer without this runs its whole body merely by being asked
    #: what it does. That fault caused 3 of the 15 board failures on
    #: 2026-11-22.
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
