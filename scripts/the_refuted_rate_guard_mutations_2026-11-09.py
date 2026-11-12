#!/usr/bin/env python3
"""Mutation harness for the refuted-rate correction. 5 reversions.

ANCHORS ARE DERIVED, NOT TYPED. A hand-written test id that matches nothing
makes pytest exit 4 with "no tests ran", which reads as a broken harness rather
than as a bad anchor -- it cost a run earlier on 2026-11-09.

RESTORES BY BYTES, never `git checkout --`: the tree holds uncommitted work and
a checkout would eat it.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
PROD = REPO / "scripts/the_refuted_rate_upper_bound_was_wrong_2026-11-09.py"
TEST = REPO / "bench/tests/test_the_refuted_rate_upper_bound_was_wrong_2026-11-09.py"
RECOVERY = REPO / "resources/RECOVERY.md"

MUTS = [
    ("M1 a live surface reverts to the wrong value",
     RECOVERY,
     lambda t: t.replace("0.022568", "0.022696", 1),
     "test_no_live_surface_states_the_wrong_value"),
    ("M2 the mpmath route uses the wrong confidence level",
     PROD,
     lambda t: t.replace('mpmath.erfinv(mpmath.mpf("0.95"))',
                         'mpmath.erfinv(mpmath.mpf("0.90"))'),
     "test_four_routes_agree"),
    ("M3 the detector reports every surface clean",
     PROD,
     lambda t: t.replace("out.append((rel, p.is_file(), txt.count(WRONG)))",
                         "out.append((rel, True, 0))"),
     "test_the_detector_can_see_a_wrong_value"),
    ("M4 the live surface list is emptied",
     PROD,
     lambda t: t.replace('LIVE = (\n    "resources/RECOVERY.md",',
                         'LIVE = (\n'),
     "test_the_live_list_is_not_empty_and_every_path_exists"),
    ("M5 main() can no longer refuse",
     PROD,
     lambda t: t.replace("    if bad:\n"
                         "        print(f\"\\nFAIL: {len(bad)} live surface(s) "
                         "not corrected: {bad}\")\n        return 1\n", ""),
     "test_it_fails_loudly_if_a_live_surface_regresses"),
]


def collected() -> set:
    r = subprocess.run([sys.executable, "-m", "pytest", "-q",
                        "-p", "no:cacheprovider", "--collect-only",
                        str(TEST.relative_to(REPO))],
                       capture_output=True, text=True, cwd=str(REPO),
                       timeout=600)
    return {ln.strip() for ln in r.stdout.splitlines() if "::" in ln}


def run(node: str):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q",
                        "-p", "no:cacheprovider", "-k", node,
                        str(TEST.relative_to(REPO))],
                       capture_output=True, text=True, cwd=str(REPO),
                       timeout=900)
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    return r.returncode, last


def main() -> int:
    known = collected()
    missing = [n for _, _, _, n in MUTS
               if not any(n in k for k in known)]
    if missing:
        print("these anchors name no collected test:")
        for n in missing:
            print("  ", n)
        return 1
    print(f"all {len(MUTS)} anchors resolve against {len(known)} collected tests")

    print("\nBASELINE -- every anchor must be GREEN first")
    for name, _, _, node in MUTS:
        rc, last = run(node)
        print(f"  {node[:62]:62s} exit {rc}  {last}")
        if rc != 0:
            print("baseline is not green; mutation results would be meaningless")
            return 1

    red = 0
    for name, path, mutate, node in MUTS:
        original = path.read_bytes()
        mutated = mutate(original.decode()).encode()
        if mutated == original:
            print(f"\n{name}\n  !! NOT APPLIED -- the mutation text did not match")
            continue
        path.write_bytes(mutated)
        try:
            rc, last = run(node)
        finally:
            path.write_bytes(original)
            assert path.read_bytes() == original, f"restore failed for {path}"
        verdict = "RED (caught)" if rc != 0 else "GREEN (MISSED)"
        red += rc != 0
        print(f"\n{name}\n  {verdict}   {last}")

    print(f"\n{'=' * 70}\n{red} of {len(MUTS)} reversions RED")
    print("\nPOST-RESTORE -- the whole guard must be green again")
    r = subprocess.run([sys.executable, "-m", "pytest", "-q",
                        "-p", "no:cacheprovider", str(TEST.relative_to(REPO))],
                       capture_output=True, text=True, cwd=str(REPO), timeout=900)
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    print(f"  exit {r.returncode}  {last}")
    return 0 if (red == len(MUTS) and r.returncode == 0) else 1


if __name__ == "__main__":
    # A `--help` MUST NOT run: this script WRITES, mutating a tracked file
    # in place and restoring it from the bytes it read first.
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
