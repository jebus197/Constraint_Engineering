# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'asking_predicate_and_fourth_standard_2026-11-14_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 34e7d83bd97e863f90785be652bf38e3b65e5bc04230f38b021018b0d97c4494
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""FALSIFIER: the ruling-residue date proxy SILENTLY removes work from the stop gate.

THE CLAIM UNDER TEST. The joint brief's F5 asserted that predicate A is "noisy in
the safe direction", because the founder can see and dismiss a wrong entry on the
banner and cannot see an absent one. That is a statement about ONE surface. At
`hooks/work_not_narrate.py:805` the same verdict is read with the OPPOSITE sign:
`if kind == "OWED" or _residue_is_his(body): continue` -- so a phantom OWED
SKIPS the entry, removing it from the set the stop gate can name as the next
unstarted piece of work, on a surface the founder never reads.

FAILS IF AND ONLY IF the defect is present: it prints FALSIFIED and raises
AssertionError when turning the proxy off CHANGES the entry the real
`_first_movable` names. If the proxy does not gate the queue the entry is the
same either way and this exits cleanly.

IT IMPORTS THE REAL TARGETS and retypes nothing: `hooks/work_not_narrate.py` and
`scripts/how_many_decisions_actually_need_him_2026-11-01.py`, both by path.

WHY IT PATCHES THE FILE RATHER THAN THE MODULE, and this is the correction that
made the first attempt honest. `_first_movable` loads the classifier FROM DISK on
every call via `spec.loader.exec_module`, so rebinding the loaded module's
`_DATED_IN_BODY` in memory reaches nothing. The first version of this measurement
did exactly that and printed a clean negative -- "the named entry MOVED: False"
-- which was an artefact of the probe and not a fact about the gate. The patch is
written to the file, the result read, and the original bytes restored and
VERIFIED BY SHA256 before any verdict is printed. A run that cannot restore
prints nothing and exits non-zero.

IT REDIRECTS THE HOOK'S ROOT FIRST. `work_not_narrate.py` hardcodes `REPO` to
`~/Developer_Projects/Constraint_Engineering` -- correctly, because the live hook
executes from `~/.claude/hooks/` where a `__file__`-derived root would resolve to
`~/.claude`. Unredirected, this falsifier would measure the HOME checkout and not
the tree it is run against; in the review sandbox of 2026-11-14 those 2 task
lists differed by 1,988 bytes, so the redirect is load-bearing.

READS ONLY the artefact under review and the repository modules it imports.
WRITES only the target file's own bytes, and only to restore them.
"""
from __future__ import annotations

import hashlib
import importlib.util
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
TARGET = REPO / "scripts" / "how_many_decisions_actually_need_him_2026-11-01.py"

#: The single implementation of the proxy, as `residue_proxy_fired` returns it,
#: and the same body with the comparison forced False. Matching on the whole
#: return statement rather than on a date literal means a reworded docstring
#: cannot silently make this probe inert.
LIVE = (b"    if not ruled:\n        return False\n"
        b"    return any(d > ruled for d in _DATED_IN_BODY.findall(txt))")
OFF = (b"    if not ruled:\n        return False\n"
       b"    return False  # PROXY OFF, falsifier only")


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, REPO / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def main() -> int:
    hook = _load("_h", "hooks/work_not_narrate.py")
    print(f"hook's own hardcoded root : {hook.REPO}")
    hook.REPO = REPO
    hook.TASKS = LIST
    hook.MARKERS = REPO / "scripts"
    print(f"REDIRECTED to             : {REPO}")

    src = TARGET.read_bytes()
    before = hashlib.sha256(src).hexdigest()
    print(f"sha256 before             : {before[:16]}")
    if LIVE not in src:
        print("CANNOT PROBE: `residue_proxy_fired` does not read as expected.")
        print("This falsifier is INERT, which is not a refutation. Exiting 2.")
        return 2

    n_open, live = hook.open_items()
    print(f"OPEN entries              : {n_open}")
    print(f"entry the REAL gate names, proxy LIVE : {live!r}")

    try:
        TARGET.write_bytes(src.replace(LIVE, OFF))
        off = hook.open_items()[1]
    finally:
        TARGET.write_bytes(src)
    after = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    print(f"sha256 after restore      : {after[:16]}  "
          f"{'RESTORED OK' if after == before else 'RESTORE FAILED'}")
    if after != before:
        print("RESTORE FAILED -- no verdict is printed from a mutated tree.")
        return 3
    print(f"entry the REAL gate names, proxy OFF  : {off!r}")

    #: ★ THE ATTRIBUTION, so the finding is not larger than its evidence. 5
    #: entries carry a residue the 3 predicates cannot decide, and 4 of them
    #: are ALSO caught by `_residue_is_his`, so they would be skipped whatever
    #: the proxy said. The proxy is the SOLE reason for the skip on 1 of the 5,
    #: 0.200000, Wilson 95% [0.036224, 0.624465]. The mechanism is the finding;
    #: "all 5 are silently removed" over-attributes by 4.
    print()
    if off != live:
        print("FALSIFIED")
        print(f"  The ruling-residue proxy GATES THE WORK QUEUE. Turning it off")
        print(f"  moved the entry the real stop gate names from {live!r} to")
        print(f"  {off!r}. {live!r} is named on every prod of every turn and")
        print(f"  {off!r} is named on none, so an entry the proxy wrongly calls")
        print(f"  OWED is removed from the session's work with no surface")
        print(f"  reporting it. Over-reporting is NOT uniformly safe: it is")
        print(f"  dismissible on the banner and SILENT here.")
        raise AssertionError(
            "over-reporting is NOT uniformly safe -- the proxy decides which "
            "entry the stop gate names")
    print("NOT FALSIFIED: the named entry is unchanged, so on this tree the "
          "proxy does not gate the queue.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
