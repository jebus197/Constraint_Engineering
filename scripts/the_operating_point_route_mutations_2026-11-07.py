#!/usr/bin/env python3
"""MUTATION HARNESS for test_the_operating_point_is_imported_not_parsed_2026-11-07.

A guard that has never been seen to fail is a hypothesis. This reverts the B56
repair -- putting the SOURCE-TEXT PARSE back into
`scripts/the_shadow_demotion_report_2026-11-02.py` -- and in 2 further variants
weakens the route in ways that leave the function returning 0.02 today, then
reports which of the guard's tests go red.

ANCHORS ARE DERIVED FROM THE FILE'S BYTES, never from a remembered shape, and
each mutation REFUSES if its anchor does not match exactly once. The original
bytes are restored in a `finally` and compared byte-for-byte; `git checkout --`
is never used, because it would discard any other uncommitted work in the file.

Exit 0 iff every mutation was applied, scored and restored.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
READER = REPO / "scripts" / "the_shadow_demotion_report_2026-11-02.py"
GUARD = ("bench/tests/"
         "test_the_operating_point_is_imported_not_parsed_2026-11-07.py")

#: the body as it stands, read from the file so the anchor cannot go stale
CURRENT_HEAD = '    import importlib.util\n'

MUTATIONS = [
    ("revert to the source-text parse",
     "the pre-B56 mechanism: reads the SPELLING, dies on `1.0 / 50`",
     '''    import importlib.util
    p = REPO / "scripts" / "can_we_do_better_than_one_in_twenty_2026-10-30.py"
    if not p.is_file():
        raise SystemExit(f"the operating point's owner is gone: {p}")
    spec = importlib.util.spec_from_file_location("cwdbt_operating_point", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "CHOSEN_TARGET"):
        raise SystemExit(
            "CHOSEN_TARGET is not defined in its owning script; refusing to "
            "guess. It was renamed or moved -- update this reader rather than "
            "retyping the number here.")
    return float(mod.CHOSEN_TARGET)''',
     '''    p = REPO / "scripts" / "can_we_do_better_than_one_in_twenty_2026-10-30.py"
    for ln in p.read_text().splitlines():
        if ln.strip().startswith("CHOSEN_TARGET"):
            return float(ln.split("=")[1].split("#")[0].strip())
    raise SystemExit("CHOSEN_TARGET is not in its owning script")'''),

    ("retype the number as a literal",
     "returns 0.02 today and cannot follow a ruling of his that moves it",
     '''    spec = importlib.util.spec_from_file_location("cwdbt_operating_point", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)''',
     '''    class mod:            # MUTATION: the number retyped, owner ignored
        CHOSEN_TARGET = 0.02'''),

    ("default silently instead of refusing",
     "a missing owner yields the comparison size, the 'restore' the pin forbids",
     '''    if not p.is_file():
        raise SystemExit(f"the operating point's owner is gone: {p}")''',
     '''    if not p.is_file():
        return 0.05           # MUTATION: fail OPEN to the comparison size'''),
]


def _score(label: str) -> tuple[bool, str]:
    r = subprocess.run([sys.executable, "-m", "pytest", GUARD, "-q"],
                       cwd=REPO, capture_output=True, text=True)
    line = next((l for l in reversed(r.stdout.splitlines())
                 if "passed" in l or "failed" in l or "error" in l), "")
    return r.returncode != 0, line.strip()


def main() -> int:
    if not READER.is_file():
        print(f"REFUSED: no reader at {READER}")
        return 1
    orig = READER.read_text(encoding="utf-8")

    base_red, base_line = _score("baseline")
    print("=" * 78)
    print("MUTATION HARNESS: the operating point's ROUTE")
    print("=" * 78)
    print(f"baseline (unmutated): {'RED' if base_red else 'GREEN'}  {base_line}")
    if base_red:
        print("REFUSED: the guard is already red, so a mutation proves nothing. "
              "Fix the guard first.")
        return 1

    red = 0
    try:
        for label, why, old, new in MUTATIONS:
            n = orig.count(old)
            if n != 1:
                print(f"\n  REFUSED {label!r}: anchor occurs {n} times, not 1. "
                      f"Not guessing -- the file has moved under this harness.")
                continue
            READER.write_text(orig.replace(old, new), encoding="utf-8")
            is_red, line = _score(label)
            red += bool(is_red)
            print(f"\n  {label}")
            print(f"      why it matters: {why}")
            print(f"      -> {'RED (good)' if is_red else 'GREEN (THE GUARD MISSES IT)'}"
                  f"   {line}")
            READER.write_text(orig, encoding="utf-8")
    finally:
        READER.write_text(orig, encoding="utf-8")
        same = READER.read_text(encoding="utf-8") == orig
        print(f"\nrestored the reader's original bytes: "
              f"{'byte-for-byte verified' if same else 'RESTORE FAILED'}")
        if not same:
            return 1

    print(f"\n{'=' * 78}")
    print(f"{red} of {len(MUTATIONS)} mutations RED")
    if red == len(MUTATIONS):
        print("The guard discriminates on every property it claims to pin.")
    else:
        print("At least 1 mutation survived: the guard does not pin what it says.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    import pathlib as _pl
    sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
    from _cli_help import answer_help as _answer_help
    _answer_help(__doc__, __file__)
    raise SystemExit(main())
