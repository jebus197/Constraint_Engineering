#!/usr/bin/env python3
"""Reverse each part of the shell-exclusion repair and prove the guard reds.

B113's repair stops `pgrep -f run_simulated_experiment.py` reporting a SHELL
whose command line merely names the runner -- observed twice, pids 21974 and
28697, both `git commit` shells carrying a message that described the blocker.
4 reversions are applied to `hooks/cy_monitor_gate.py`, one at a time, and
`bench/tests/test_a_shell_naming_the_runner_is_not_a_run_2026-11-08.py` must
fail for each.

ANCHORS ARE DERIVED AND ASSERTED PRESENT before any edit, per
`feedback_a_mutation_harness_must_derive_its_anchors_2026-11-04`. THE SUBJECT IS
RESTORED FROM BYTES HELD HERE AND VERIFIED BY SHA-256 AND BY INODE, never by
`git checkout --`: the file is hardlinked into `~/.claude/hooks`, so a failed
restore would leave the LIVE gate mutated.
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
HOOK = REPO / "hooks" / "cy_monitor_gate.py"
LIVE = pathlib.Path.home() / ".claude/hooks/cy_monitor_gate.py"
GUARD = REPO / "bench/tests/test_a_shell_naming_the_runner_is_not_a_run_2026-11-08.py"

MUTATIONS = [
    ("drop the shell filter entirely",
     "        pids = [x for x in (out.stdout or \"\").split() if x.strip()]\n"
     "        return [p for p in pids if not _is_shell(p)]",
     "        return [x for x in (out.stdout or \"\").split() if x.strip()]",
     "a_shell_naming_the_runner_is_not_reported"),
    ("compare the raw comm instead of its basename",
     "    return _shell_name(out.stdout or \"\") in _SHELLS",
     "    return (out.stdout or \"\").strip() in _SHELLS",
     "a_shell_naming_the_runner_is_not_reported"),
    ("treat an unreadable comm as a shell (fails toward a silent pass)",
     "    except Exception:                                        # noqa: BLE001\n"
     "        return False                 # unreadable -> KEEP, fail toward refusing",
     "    except Exception:                                        # noqa: BLE001\n"
     "        return True",
     "a_raising_ps_keeps_the_pid"),
    ("exclude the interpreter too, which would UNDER-refuse",
     '_SHELLS = frozenset({"sh", "bash", "zsh", "dash", "ksh", "csh", "tcsh", "fish"})',
     '_SHELLS = frozenset({"sh", "bash", "zsh", "dash", "ksh", "csh", "tcsh",\n'
     '                     "fish", "python3", "python", "Python"})',
     "the_exclusion_is_by_shell_not_by_interpreter"),
]


def main() -> int:
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()
    good = HOOK.read_bytes()
    good_sha = hashlib.sha256(good).hexdigest()
    good_ino = HOOK.stat().st_ino
    print(f"subject : {HOOK.relative_to(REPO)}")
    print(f"sha256  : {good_sha}")
    if HOOK.stat().st_ino != LIVE.stat().st_ino:
        print("REFUSING: the repo copy and the live hook are not the same inode.")
        return 1
    base = subprocess.run([sys.executable, "-m", "pytest", str(GUARD), "-q"],
                          capture_output=True, text=True, cwd=REPO)
    print(f"baseline: {'GREEN' if base.returncode == 0 else 'RED'}")
    if base.returncode != 0:
        print("REFUSING: the guard is not green before mutation.")
        print(base.stdout[-2000:])
        return 1

    failures: list[str] = []
    try:
        for name, anchor, repl, expect in MUTATIONS:
            txt = good.decode("utf-8")
            if anchor not in txt:
                failures.append(f"{name}: ANCHOR ABSENT -- the probe is wrong")
                print(f"\n[{name}] ANCHOR ABSENT; skipped")
                continue
            HOOK.write_text(txt.replace(anchor, repl, 1), encoding="utf-8")
            r = subprocess.run([sys.executable, "-m", "pytest", str(GUARD), "-q"],
                               capture_output=True, text=True, cwd=REPO)
            red, named = r.returncode != 0, expect in r.stdout
            tail = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
            print(f"\n[{name}]\n  guard: {'RED' if red else 'GREEN'}   {tail}")
            print(f"  the expected test is named in the output: {named}")
            if not red:
                failures.append(f"{name}: guard stayed GREEN -- it does not test this")
            elif not named:
                failures.append(f"{name}: red, but {expect!r} is not the failing test")
            HOOK.write_bytes(good)
    finally:
        HOOK.write_bytes(good)
        back = hashlib.sha256(HOOK.read_bytes()).hexdigest()
        same = HOOK.stat().st_ino == good_ino == LIVE.stat().st_ino
        print(f"\nrestored: sha256 matches = {back == good_sha}; inode preserved = {same}")
        if back != good_sha or not same:
            print("★ THE LIVE cy GATE MAY BE MUTATED. Restore it by hand.")
            return 1

    print("\n" + "=" * 70)
    if failures:
        for f in failures:
            print("FAILURE:", f)
        return 1
    print(f"all {len(MUTATIONS)} reversions turn the guard red")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
