#!/usr/bin/env python3
"""Mutations against the repaired mirror-ordering guard. Each must turn it RED.

B203. The guard used to run the whole pre-commit hook under a 900 s cap and
could not complete, because the board inside the hook takes about 2718 s. It
now checks the 2 claims it actually makes -- that stage 0 repairs a stale
Desktop copy, and that no live refusal in the hook keys on mirror drift -- and
completes in about 21 s.

A GUARD THAT CANNOT FAIL IS NOT A GUARD, and the replacement is only an
improvement if it still refuses the defects the original was aimed at. Each
mutation below breaks exactly 1 of the 2 claims, re-aims the guard at the
mutated copy through its own documented seam, and requires a red result.

THE SEAM IS DRIVEN, NOT THE SOURCE. An earlier harness in this project
rewrote a guard's source text to re-point it, which stops matching the moment
the guard is edited and then reports a pass it never established. The guard
reads CDSFL_SYNC_PATH and CDSFL_HOOK_PATH, so the harness sets those and
copies the guard byte-identically.
"""
from __future__ import annotations

import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
GUARD = REPO / "bench" / "tests" / "test_desktop_mirrors_stay_current_2026-09-10.py"
REAL_SYNC = REPO / "scripts" / "sync_desktop_mirrors.py"
REAL_HOOK = REPO / "hooks" / "pre-commit"

#: Only the ordering test is selected: the rest of the file guards other
#: properties and would mask which claim a mutation actually broke.
SELECT = "a_drifted_mirror_does_not_refuse_the_commit"


def _cli(doc: str) -> None:
    """Answer --help WITHOUT running a single mutation."""
    import argparse                                        # noqa: PLC0415
    argparse.ArgumentParser(
        description=doc.strip().split("\n")[0],
        epilog="Takes no options. Running it performs the mutations.",
    ).parse_args()


def run_guard(sync: pathlib.Path, hook: pathlib.Path) -> tuple[int, str]:
    with tempfile.TemporaryDirectory(prefix="cdsfl_mirror_mut_") as td:
        d = pathlib.Path(td)
        g = d / GUARD.name
        shutil.copy(GUARD, g)          # byte-identical: the real guard under test
        env = dict(os.environ,
                   CDSFL_SYNC_PATH=str(sync), CDSFL_HOOK_PATH=str(hook))
        r = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
             str(g), "-k", SELECT],
            cwd=d, env=env, capture_output=True, text=True, timeout=600)
        tail = [ln for ln in r.stdout.splitlines() if ln.strip()]
        return r.returncode, (tail[-1] if tail else "")


def mutate_sync_into_a_noop(d: pathlib.Path) -> pathlib.Path:
    """Claim 1 broken: the sync runs clean and repairs nothing."""
    out = d / "sync_noop.py"
    src = REAL_SYNC.read_text(encoding="utf-8")
    mirrors = re.search(r"^MIRRORS\s*=.*?^\)", src, re.M | re.S)
    keep = mirrors.group(0) if mirrors else 'MIRRORS = ()'
    out.write_text(
        "#!/usr/bin/env python3\n"
        '"""A sync that exits 0 and copies nothing."""\n'
        "import sys\n" + keep + "\n"
        "if __name__ == '__main__':\n    sys.exit(0)\n",
        encoding="utf-8")
    return out


def mutate_hook_with_a_drift_refusal(d: pathlib.Path) -> pathlib.Path:
    """Claim 2 broken: a live refusal keys on mirror drift again."""
    out = d / "pre-commit-drift"
    src = REAL_HOOK.read_text(encoding="utf-8")
    anchor = 'CDSFL_REFUSAL="guard-file-missing"'
    assert src.count(anchor) == 1, anchor
    src = src.replace(anchor,
                      anchor + '\n    CDSFL_REFUSAL="desktop-mirror-drifted"', 1)
    out.write_text(src, encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    _cli(__doc__)
    print(__doc__.strip().split("\n")[0])
    print()

    print("== baseline: the guard must PASS against the real files ==")
    rc, tail = run_guard(REAL_SYNC, REAL_HOOK)
    print(f"   rc={rc}  {tail}")
    if rc != 0:
        print("   BASELINE RED -- the guard fails on correct code. Stop.")
        return 1
    print()

    print("== mutations: each must turn the guard RED ==")
    red = 0
    with tempfile.TemporaryDirectory(prefix="cdsfl_mirror_src_") as td:
        d = pathlib.Path(td)
        cases = {
            "sync_is_a_noop": (mutate_sync_into_a_noop(d), REAL_HOOK),
            "hook_refuses_on_drift": (REAL_SYNC, mutate_hook_with_a_drift_refusal(d)),
        }
        for name, (sync, hook) in cases.items():
            rc, tail = run_guard(sync, hook)
            ok = rc != 0
            red += ok
            print(f"   {name:24s} rc={rc}  "
                  f"{'RED  (caught)' if ok else 'GREEN (MISSED)'}   {tail[:48]}")
    print()
    print(f"   {red} of {len(cases)} mutations caught")
    return 0 if red == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
