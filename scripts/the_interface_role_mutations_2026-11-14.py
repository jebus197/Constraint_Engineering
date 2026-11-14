#!/usr/bin/env python3
"""Does the interface-role guard fail when the B142 repair is reverted?

8 reversions of the 2026-11-14 role-mapping repair, each of which must turn
`bench/tests/test_the_interface_roles_reach_the_selector_2026-11-14.py` RED.

★ 2 KINDS OF MUTATION, handled separately because they restore differently.
TEXT mutations edit `bench/model_catalogue.py`; the FILE mutation removes a role
file. Both are restored from bytes captured BEFORE the first mutation, never
with `git checkout --`, which in this project once ate the file under test. The
restore is verified by comparing bytes, because a restore is a mutation too.

★ EVERY MUTATION IS VERIFIED TO HAVE CHANGED SOMETHING. An edit whose anchor no
longer matches leaves the subject intact and the guard green, and reporting that
as a MISS blames the guard for a stale probe.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CAT = REPO / "bench" / "model_catalogue.py"
ROLES = REPO / "bench" / "cdsfl_registry" / "roles"
GUARD = REPO / "bench" / "tests" / "test_the_interface_roles_reach_the_selector_2026-11-14.py"

TEXT_MUTATIONS = [
    ("classifier is quietly pointed at participant",
     '    "classifier": None,', '    "classifier": "participant",'),
    ("researcher is quietly pointed at participant",
     '    "researcher": None,', '    "researcher": "participant",'),
    ("known_roles ignores the axis argument",
     "    if axis is None:\n        return stems\n    return [s for s in stems if role_axis(s) == axis]",
     "    return stems"),
    ("role_axis stops reading the file and uses a fixed list",
     '    path = ROLES_DIR / f"{role}.toml"',
     '    return {"collator": "structural", "participant": "structural",\n'
     '            "player_manager": "structural"}.get(role)\n'
     '    path = ROLES_DIR / f"{role}.toml"'),
    # ★ THIS MUTATION WAS REWRITTEN ON 2026-11-14 AFTER IT REPORTED A FALSE
    # MISS. Its first form replaced the membership test with `if False:`, which
    # fell straight through to `FUNCTIONAL_TO_STRUCTURAL[functional]` -- and a
    # dict lookup raises `KeyError` all by itself, so the guard was right to
    # stay green. The probe was broken, not the guard. It now returns None,
    # which is the behaviour the guard actually exists to refuse.
    ("structural_for returns None for an unknown name instead of raising",
     "    if functional not in FUNCTIONAL_TO_STRUCTURAL:\n        raise KeyError(",
     "    if functional not in FUNCTIONAL_TO_STRUCTURAL:\n        return None\n    if False:\n        raise KeyError("),
    ("collator is given a functional counterpart",
     '    "collator": None,', '    "collator": "worker",'),
    ("the renderer goes back to 1 mixed list",
     '''             f"roles available -- structural: "''',
     '''             f"roles available: {', '.join(known_roles()) or 'none'}" or "''' + '''"
             f"'''),
]

FILE_MUTATIONS = [("researcher.toml is removed", ROLES / "researcher.toml")]


def _run_guard() -> bool:
    r = subprocess.run([sys.executable, "-m", "pytest", str(GUARD), "-q", "--no-header"],
                       cwd=REPO, capture_output=True, text=True)
    return r.returncode == 0


def main() -> int:
    cat_bytes = CAT.read_bytes()
    cat_text = cat_bytes.decode("utf-8")
    file_bytes = {p: p.read_bytes() for _l, p in FILE_MUTATIONS}

    if not _run_guard():
        print("REFUSED: the guard is RED before any mutation.")
        return 2

    red = misses = probe = 0
    try:
        for label, old, new in TEXT_MUTATIONS:
            if old not in cat_text:
                probe += 1
                print(f"  [PROBE FAILED] {label}: anchor absent, nothing mutated.")
                continue
            CAT.write_text(cat_text.replace(old, new, 1), encoding="utf-8")
            if CAT.read_bytes() == cat_bytes:
                probe += 1
                print(f"  [PROBE FAILED] {label}: bytes unchanged.")
                CAT.write_bytes(cat_bytes)
                continue
            if _run_guard():
                misses += 1
                print(f"  [MISS]  {label}: guard stayed GREEN.")
            else:
                red += 1
                print(f"  [RED]   {label}")
            CAT.write_bytes(cat_bytes)

        for label, path in FILE_MUTATIONS:
            path.unlink()
            if path.exists():
                probe += 1
                print(f"  [PROBE FAILED] {label}: the file is still there.")
                continue
            if _run_guard():
                misses += 1
                print(f"  [MISS]  {label}: guard stayed GREEN.")
            else:
                red += 1
                print(f"  [RED]   {label}")
            path.write_bytes(file_bytes[path])
    finally:
        CAT.write_bytes(cat_bytes)
        for p, b in file_bytes.items():
            p.write_bytes(b)

    ok = CAT.read_bytes() == cat_bytes and all(p.read_bytes() == b for p, b in file_bytes.items())
    n = len(TEXT_MUTATIONS) + len(FILE_MUTATIONS)
    print(f"\n  subjects restored byte-for-byte: {ok}")
    print(f"  {red} of {n} mutations turned the guard RED; {misses} MISS; {probe} probe failure(s)")
    if not ok:
        print("  RESTORE FAILED.")
        return 2
    if not _run_guard():
        print("  THE GUARD IS RED AFTER RESTORE — the restore did not restore.")
        return 2
    print("  guard GREEN again after restore")
    return 0 if (misses == 0 and probe == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
