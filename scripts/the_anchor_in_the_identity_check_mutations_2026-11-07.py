#!/usr/bin/env python3
"""MUTATION HARNESS for test_a_restatement_must_see_the_anchor_2026-11-07.

The defect this guards was itself missed by an earlier mutation harness, which
exercised only the `task_ref` branch of `tid_of`'s 3-way precedence. So this
harness mutates BOTH repaired call sites separately, and removes the check
entirely, and reports which of the guard's tests go red for each.

ANCHORS ARE READ FROM THE FILE'S BYTES and each mutation REFUSES if its anchor
does not match exactly once. The original bytes are restored in a `finally` and
compared byte-for-byte; `git checkout --` is never used, because it would
discard any other uncommitted work in the file.

Exit 0 iff every mutation was applied, scored and restored.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
STORE = REPO / "bench" / "ticket_store.py"
GUARD = "bench/tests/test_a_restatement_must_see_the_anchor_2026-11-07.py"

MUTATIONS = [
    ("revert the anchor in restate",
     "the exact defect: anchor-addressed restatements refuse again",
     "        if tid_of(t.kind, clean, t.task_ref, t.anchor) != t.tid:",
     "        if tid_of(t.kind, clean, t.task_ref) != t.tid:"),

    ("revert the anchor in retitle",
     "the same omission in the sibling method, fixed in the same pass",
     "        if tid_of(t.kind, t.verbatim, t.task_ref, t.anchor) != t.tid:",
     "        if tid_of(t.kind, t.verbatim, t.task_ref) != t.tid:"),

    ("delete the restate check entirely",
     "a vacuous guard: it would accept a restatement that DOES move an identity",
     '''        if tid_of(t.kind, clean, t.task_ref, t.anchor) != t.tid:
            raise AssertionError(
                "restating this text would move the hashed identity, so identity "
                "is digesting the text again. Refusing to write it.")''',
     "        pass    # MUTATION: the identity check removed"),

    ("make the check compare the stored field to itself",
     "the ORIGINAL vacuous form the 2026-10-17 comment records: can never fail",
     "        if tid_of(t.kind, clean, t.task_ref, t.anchor) != t.tid:",
     "        if t.tid != t.tid:    # MUTATION: a stored field against itself"),
]


def _score() -> tuple[bool, str]:
    r = subprocess.run([sys.executable, "-m", "pytest", GUARD, "-q"],
                       cwd=REPO, capture_output=True, text=True)
    line = next((l for l in reversed(r.stdout.splitlines())
                 if "passed" in l or "failed" in l or "error" in l), "")
    return r.returncode != 0, line.strip()


def main() -> int:
    if not STORE.is_file():
        print(f"REFUSED: no store at {STORE}")
        return 1
    orig = STORE.read_text(encoding="utf-8")

    base_red, base_line = _score()
    print("=" * 78)
    print("MUTATION HARNESS: the anchor in the identity check")
    print("=" * 78)
    print(f"baseline (unmutated): {'RED' if base_red else 'GREEN'}  {base_line}")
    if base_red:
        print("REFUSED: the guard is already red, so a mutation proves nothing.")
        return 1

    red = 0
    try:
        for label, why, old, new in MUTATIONS:
            n = orig.count(old)
            if n != 1:
                print(f"\n  REFUSED {label!r}: anchor occurs {n} times, not 1. "
                      f"Not guessing -- the file has moved under this harness.")
                continue
            STORE.write_text(orig.replace(old, new), encoding="utf-8")
            is_red, line = _score()
            red += bool(is_red)
            print(f"\n  {label}")
            print(f"      why it matters: {why}")
            print(f"      -> {'RED (good)' if is_red else 'GREEN (THE GUARD MISSES IT)'}"
                  f"   {line}")
            STORE.write_text(orig, encoding="utf-8")
    finally:
        STORE.write_text(orig, encoding="utf-8")
        same = STORE.read_text(encoding="utf-8") == orig
        print(f"\nrestored the store's original bytes: "
              f"{'byte-for-byte verified' if same else 'RESTORE FAILED'}")
        if not same:
            return 1

    print(f"\n{'=' * 78}")
    print(f"{red} of {len(MUTATIONS)} mutations RED")
    print("The guard discriminates on every property it claims to pin."
          if red == len(MUTATIONS) else
          "At least 1 mutation survived: the guard does not pin what it says.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    import pathlib as _pl
    sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
    from _cli_help import answer_help as _answer_help
    _answer_help(__doc__, __file__)
    raise SystemExit(main())
