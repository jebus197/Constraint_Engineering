#!/usr/bin/env python3
"""Mutations against the board-verdict guard. Each must turn it RED.

A guard that cannot fail is not a guard. Each mutation rewrites the hook's
board line into a form that breaks the verdict, points the guard at the
mutant, and requires the guard to refuse it.
"""
from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
GUARD = REPO / "bench" / "tests" / "test_the_board_verdict_reaches_the_refusal_2026-11-17.py"
REAL_HOOK = REPO / "hooks" / "pre-commit"

ORIGINAL = "OUT=$(python3 -m pytest -q -p no:cacheprovider $GUARDS 2>&1)"

MUTATIONS = {
    "tee_pipeline":
        'OUT=$(python3 -m pytest -q -p no:cacheprovider $GUARDS 2>&1 | tee /dev/stderr)',
    "cat_pipeline":
        'OUT=$(python3 -m pytest -q -p no:cacheprovider $GUARDS 2>&1 | cat)',
    "tee_to_file":
        'OUT=$(python3 -m pytest -q -p no:cacheprovider $GUARDS 2>&1 | tee /dev/null)',
    "swallowed_code":
        'OUT=$(python3 -m pytest -q -p no:cacheprovider $GUARDS 2>&1 || true)',
    "head_pipeline":
        'OUT=$(python3 -m pytest -q -p no:cacheprovider $GUARDS 2>&1 | head -200)',
}


def run_guard_against(hook_path: pathlib.Path) -> tuple[int, str]:
    """Run the guard with its HOOK pointed at `hook_path`. Returns (rc, tail)."""
    with tempfile.TemporaryDirectory(prefix="cdsfl_mut_") as td:
        d = pathlib.Path(td)
        g = d / GUARD.name
        shutil.copy(GUARD, g)   # byte-identical: the guard under test is the real one
        env = dict(os.environ, CDSFL_HOOK_PATH=str(hook_path))
        r = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
             str(g), "-k", "code or verdicts"],
            cwd=d, env=env, capture_output=True, text=True, timeout=600)
        tail = [ln for ln in r.stdout.splitlines() if ln.strip()]
        return r.returncode, (tail[-1] if tail else "")


def _cli(doc: str) -> None:
    """Answer --help WITHOUT running the measurement.

    `a --help must never cost money`: 15 of 17 runners in this project once
    billed for the flag. This parser takes no options and exists so the flag
    prints usage and exits before anything is measured.
    """
    import argparse                                        # noqa: PLC0415
    argparse.ArgumentParser(
        description=doc.strip().split("\n")[0],
        epilog="Takes no options. Running it performs the measurement.",
    ).parse_args()


def main() -> int:
    _cli(__doc__)
    assert GUARD.is_file(), GUARD
    assert ORIGINAL in REAL_HOOK.read_text(encoding="utf-8"), (
        "the board line is not in the hook verbatim; update ORIGINAL")

    print("== baseline: the guard must PASS against the real hook ==")
    rc, tail = run_guard_against(REAL_HOOK)
    print(f"   rc={rc}  {tail}")
    if rc != 0:
        print("   BASELINE RED -- the guard fails on correct code. Stop.")
        return 1

    print()
    print("== mutations: each must turn the guard RED ==")
    red = 0
    with tempfile.TemporaryDirectory(prefix="cdsfl_hooks_") as td:
        for name, repl in MUTATIONS.items():
            mut = pathlib.Path(td) / f"pre-commit-{name}"
            shutil.copy(REAL_HOOK, mut)
            s = mut.read_text(encoding="utf-8")
            assert s.count(ORIGINAL) == 1, name
            mut.write_text(s.replace(ORIGINAL, repl, 1), encoding="utf-8")
            rc, tail = run_guard_against(mut)
            ok = rc != 0
            red += ok
            print(f"   {name:16s} rc={rc}  {'RED  (caught)' if ok else 'GREEN (MISSED)'}"
                  f"   {tail[:54]}")

    print()
    print(f"   {red} of {len(MUTATIONS)} mutations caught")
    return 0 if red == len(MUTATIONS) else 1


if __name__ == "__main__":
    sys.exit(main())
