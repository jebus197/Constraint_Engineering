#!/usr/bin/env python3
"""Move 4 producers' module-level work into `main()` so they can be IMPORTED.

WHY, AND IT IS B135'S UNNAMED PREREQUISITE. His ruling of 2026-11-08 is option
1: replace the Wilson detector's pattern match with EXECUTION of a shared `_iv`
helper. Execution requires the producer to be importable, and measured
2026-11-08 only 10 of 13 are -- 0.769231, Wilson 95% [0.497436, 0.918205],
Clopper-Pearson [0.461868, 0.949619]. 3 raise `SystemExit: 2`, because they
build an `ArgumentParser` and call `parse_args()` at MODULE level, so importing
them hands argparse the importing process's own argv; and 1 more prints 899
characters on import.

THE COST OF NOT DOING THIS FIRST IS KNOWN, because I paid it hours earlier.
`scripts/what_his_twenty_nine_rulings_actually_say_2026-11-08.py` ran its whole
measurement at module level and ended in `sys.exit(0)`. The guard that loads
every `_iv` catches `Exception`; `SystemExit` derives from `BaseException`. 12
of that guard's tests died. Adding `_iv` to a file that cannot be imported
makes the helper unreachable and the guard red at the same time.

WHAT IS AND IS NOT CHANGED. The body moves verbatim into `main()`; `sys.exit(n)`
becomes `return n`; an `if __name__` guard calls it. Behaviour from the command
line is unchanged, which is asserted by comparing stdout BYTE FOR BYTE against a
baseline captured before any edit. A body carrying a NON-DOCSTRING multi-line
string refuses the edit, because re-indenting a data literal changes its value
while re-indenting a docstring correctly tracks its new nesting.

Exit 0 when every file transformed, parses, and still imports silently.
"""
from __future__ import annotations

import argparse
import ast
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent

#: (file stem, 1-indexed line at which the module-level WORK begins). The cut
#: is stated per file rather than guessed: a heuristic that picked the first
#: `Assign` would have swept up the constants above it.
TARGETS = [
    ("a4_blockers_lock_audit_2026-10-03", 23),
    ("rk_pairing_reach_2026-10-03", 20),
    ("routing_severity_gate_2026-10-03", 22),
    ("gate_input_is_not_persisted_2026-10-03", 59),
]

NOTE = '''

def main() -> int:
    """★ THE BODY MOVED HERE ON 2026-11-08 SO THIS FILE CAN BE IMPORTED.

    It ran at module level, so importing it either handed argparse the
    importing process's argv and raised `SystemExit: 2`, or printed its whole
    report. B135's option 1 requires the shared interval helper to be EXECUTED
    by `bench/tests/test_an_interval_rests_on_two_routes_2026-11-03.py`, which
    imports every script defining one; an unimportable producer makes that
    helper unreachable. Command-line behaviour is unchanged and was asserted
    byte for byte against a baseline taken before the edit.
    """
'''


def transform(path: pathlib.Path, cut: int) -> str:
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.ClassDef, ast.Module)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) \
                    and isinstance(body[0].value, ast.Constant) \
                    and isinstance(body[0].value.value, str):
                docstrings.add((body[0].value.lineno, body[0].value.end_lineno))
    # * ONLY A TRIPLE-QUOTED LITERAL IS UNSAFE, and the first version of this
    # check was too strict. It flagged every multi-line `Constant`, which
    # includes IMPLICIT CONCATENATION: a call whose argument is split across 2
    # lines is 1 Constant whose VALUE contains neither the newline nor the
    # indentation, so re-indenting the continuation cannot change it. It
    # refused `a4_blockers_lock_audit` on 6 such spans. A triple-quoted literal
    # that is not a docstring IS unsafe, because its interior lines ARE its
    # value. The distinction is read from the source text, never inferred.
    _tq = ('"' * 3, "'" * 3)
    _pre = ("", "r", "f", "b", "rb", "br", "fr", "rf")
    offenders = []
    for n in ast.walk(tree):
        if not (isinstance(n, ast.Constant) and isinstance(n.value, str)):
            continue
        if n.end_lineno <= n.lineno or n.lineno < cut:
            continue
        if (n.lineno, n.end_lineno) in docstrings:
            continue
        seg = (ast.get_source_segment(src, n) or "").lstrip()
        if any(seg.startswith(a + b) for a in _pre for b in _tq):
            offenders.append((n.lineno, n.end_lineno))
    if offenders:
        raise SystemExit(f"{path.name}: non-docstring multi-line literal(s) "
                         f"at {offenders}; refusing to re-indent")
    lines = src.splitlines(keepends=True)
    head, body = lines[:cut - 1], lines[cut - 1:]
    moved = "".join(("    " + ln) if ln.strip() else ln for ln in body)
    moved = moved.replace("    sys.exit(", "    return (").replace(
        "    return (0)", "    return 0").replace("    return (1)", "    return 1")
    out = ("".join(head).rstrip("\n") + NOTE + moved.rstrip("\n")
           + '\n\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n')
    ast.parse(out)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true", help="apply the transform")
    a = ap.parse_args()
    for stem, cut in TARGETS:
        p = REPO / "scripts" / f"{stem}.py"
        if not p.is_file():
            print(f"  {stem}: ABSENT"); return 1
        src = p.read_text(encoding="utf-8")
        if "\nif __name__ == \"__main__\":\n    raise SystemExit(main())" in src:
            print(f"  {stem[:52]:54s} already transformed")
            continue
        out = transform(p, cut)
        print(f"  {stem[:52]:54s} {len(src)} -> {len(out)} chars")
        if a.write:
            p.write_text(out, encoding="utf-8")
    if not a.write:
        print("\nDRY RUN -- nothing written. Re-run with --write.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
