#!/usr/bin/env python3
"""Put the canonical help guard into the mutation harnesses that WRITE.

★ THE FAULT, AND IT IS WORSE THAN THE RULE IT BREAKS. His rule is that a
`--help` must never cost money: `scripts/help_writers_rate_2026-09-17.py`
measures how many tracked scripts both WRITE something and ignore the flag.
Measured on the working tree 2026-11-12: 7 of 749, 0.9346 per cent, Wilson
[0.4534, 1.9164] per cent, Clopper-Pearson [0.3766, 1.9161] per cent -- and all
7 were written between 2026-11-09 and 2026-11-12, so all 7 are mine.

6 of the 7 are MUTATION HARNESSES. A harness overwrites a tracked source file in
place and restores it afterwards, so running one with `--help` does not merely
cost money: it EDITS THE REPOSITORY and then restores it, and if the restore
path is not reached the edit stands. `the_permission_predicate_mutations_2026-11-12.py`
mutates `hooks/work_not_narrate.py`, which is hard-linked to the live Stop hook,
so a `--help` on it would rewrite the hook governing this session's stopping.

★ AN 8TH WAS INVISIBLE TO THE MEASUREMENT AND IS REPAIRED HERE TOO. The
detector's working-tree population is `git ls-files -- scripts`, so an UNTRACKED
script is outside it. `the_permission_predicate_mutations_2026-11-12.py` was
written minutes before the measurement and was therefore not counted -- it would
have become an offender at the moment it was staged. A population defined by the
index cannot see a file that is not in the index yet.

★ THE FIX IS THE EXISTING HELPER, NOT A NEW ONE. `scripts/_cli_help.py:answer_help`
answers `-h`/`--help` and returns without doing anything when argv is empty,
which is what makes it safe at the top of a `__main__` block. 3 compliant
mutation harnesses already use exactly this form and it is copied from them
rather than invented.

★ IT REPORTS BY DEFAULT AND WRITES ONLY ON `--apply`, because an instrument's
remedy can destroy work. Each file is checked for the shape it expects, skipped
with a reason where the shape differs, and the result is verified by running the
measurement again rather than by trusting this script.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"

#: The guard, lifted from the compliant harnesses. The comment is part of it:
#: the next reader needs to know WHY a help call sits above `main()`.
#: ★ THE GUARD IS SELF-SUFFICIENT AS OF 2026-11-23, AND THAT IS THE WHOLE
#: REPAIR FOR THE DECLINED CLASS. The previous guard text named `pathlib` and
#: `sys` without importing them, so this fixer had to DECLINE any file that did
#: not already `import pathlib` at module level. Measured on the 2026-11-23
#: working tree, that produced 3 dispositions rather than 2: 9 fixable, 6
#: DECLINED, 2 already compliant -- and all 6 declined files use
#: `from pathlib import Path`, which binds `Path` and not `pathlib`. So the
#: declines were an artefact of this file's own guard text, not a property of
#: the 6 subjects.
#:
#: WHY THIS AND NOT "ADD THE IMPORT TO THE 6". Adding a module-level import
#: edits 6 tracked source files to work around 1 line here; making the guard
#: carry its own imports edits 1 line and makes all 15 repairable. Both reach 0
#: offenders, so the simpler one is preferred -- `simplest-sufficient`,
#: sufficient meaning it discharges the requirement, which the measurement
#: below shows it does.
#:
#: AN IMPORT INSIDE `if __name__ == "__main__":` IS STILL AT MODULE LEVEL, so it
#: binds the global name exactly as a top-of-file import would, and re-importing
#: an already-imported module is a dict lookup. There is no cost to pay here.
GUARD = (
    '    # A `--help` MUST NOT run: this script WRITES, mutating a tracked file\n'
    '    # in place and restoring it from the bytes it read first.\n'
    '    # The imports are LOCAL to this guard so it needs nothing of the host\n'
    '    # file: a subject using `from pathlib import Path` binds `Path`, not\n'
    '    # `pathlib`, and used to be declined for it.\n'
    '    import pathlib as _hp_pathlib\n'
    '    import sys as _hp_sys\n'
    '    _hp_sys.path.insert(\n'
    '        0, str(_hp_pathlib.Path(__file__).resolve().parent))\n'
    '    from _cli_help import answer_help\n'
    '    answer_help(__doc__, __file__)\n'
)

_ENTRY = re.compile(
    r'(if __name__ == "__main__":\n)((?:    )(?:sys\.exit|raise SystemExit)\(main\(\)\)\n?)')


def offenders() -> list[str]:
    """The measurement's own answer, parsed from its output rather than guessed."""
    p = subprocess.run([sys.executable,
                        str(SCRIPTS / "help_writers_rate_2026-09-17.py"), ":worktree"],
                       capture_output=True, text=True, cwd=str(REPO))
    if p.returncode != 0:
        raise RuntimeError(p.stderr)
    found: list[str] = []
    for m in re.finditer(r"\[([^\]]*)\]", p.stdout):
        for q in re.finditer(r"'([^']+\.py)'", m.group(1)):
            if q.group(1) not in found:
                found.append(q.group(1))
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--apply", action="store_true",
                    help="write the guard in; without it, only report")
    ap.add_argument("--also", nargs="*", default=[],
                    help="extra repo-relative scripts to repair, for files the "
                         "measurement cannot see because they are untracked")
    a = ap.parse_args()

    targets = offenders()
    for extra in a.also:
        if extra not in targets:
            targets.append(extra)
    print(f"{len(targets)} script(s) write and ignore --help:")

    changed = skipped = 0
    for rel in targets:
        p = REPO / rel
        if not p.is_file():
            print(f"  SKIP {rel}: not in this checkout")
            skipped += 1
            continue
        src = p.read_text(encoding="utf-8")
        if "answer_help(" in src:
            print(f"  SKIP {rel}: already answers --help")
            skipped += 1
            continue
        m = _ENTRY.search(src)
        if not m:
            print(f"  SKIP {rel}: no `if __name__` block of the expected shape")
            skipped += 1
            continue
        #: ★ THE `import pathlib` / `import sys` PRECONDITION IS GONE, AND IT
        #: WAS REMOVED ONLY BECAUSE THE GUARD ABOVE RENDERS IT REDUNDANT --
        #: `additive-standard` permits a removal exactly on that condition, and
        #: the committed measurement is the one this script prints when run
        #: with `--apply`: 0 offenders remain under BOTH columns, where the
        #: precondition left 6 unrepaired. The guard now imports what it uses
        #: under private names, so NO property of the subject is required.
        #:
        #: WHAT IS STILL CHECKED IS THE SHAPE: `_ENTRY` must match, because the
        #: guard has to sit above the `main()` call and nowhere else. That is a
        #: real precondition and it stays.
        new = src[:m.start()] + m.group(1) + GUARD + m.group(2) + src[m.end():]
        if a.apply:
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(new)
            print(f"  FIXED {rel}")
        else:
            print(f"  WOULD FIX {rel}")
        changed += 1

    print(f"\n{changed} to change, {skipped} skipped"
          + ("" if a.apply else "  (report only; pass --apply to write)"))
    if a.apply:
        print("\nRe-running the measurement rather than trusting this script:")
        p = subprocess.run([sys.executable,
                            str(SCRIPTS / "help_writers_rate_2026-09-17.py"), ":worktree"],
                           capture_output=True, text=True, cwd=str(REPO))
        for line in p.stdout.split("\n"):
            if "direct:" in line or "dash-m:" in line:
                print("  " + line.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
