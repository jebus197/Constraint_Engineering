#!/usr/bin/env python3
"""How many real files could the temp-tree cleanup reach, and how many it changed.

WHY THIS EXISTS. `bench/tests/conftest.py` carried an autouse teardown that
walked `tmp_path` setting every file to 600 and every directory to 700, to make
pytest's own temp trees deletable. `pathlib.Path.chmod` follows a symlink, so for
any test that symlinked a real path into `tmp_path` the chmod landed on the
TARGET. This script measures the reach and the damage rather than describing it.

WHAT IT MEASURES.
1. How many tracked files disagree with the git index on the execute bit, with a
   confidence interval, cross-verified across statsmodels and scipy.
2. How many test files symlink a real path into a pytest temp tree, and what each
   one points at, so the reach is enumerated rather than asserted.
3. The mode census of the tracked script tree, against what this machine's umask
   would produce, which is the evidence that the two literals 600 and 700 came
   from the fixture and not from file creation.

MEASURED 2026-10-17, before the repair: 22 of 406 tracked files under `scripts/`
had lost the execute bit the index records, and the umask is 022, so nothing a
tool creates here is 600.

Costs nothing and dispatches no model. Run: python3 scripts/<this file>
"""
from __future__ import annotations

import os
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
TREES = ("scripts", "bench", "hooks")


def _tracked(trees=TREES):
    out = subprocess.run(["git", "ls-files", "-s", *trees],
                         capture_output=True, text=True, cwd=str(REPO))
    if out.returncode != 0:
        return []
    rows = []
    for line in out.stdout.splitlines():
        meta, _, path = line.partition("\t")
        rows.append((meta.split()[0], path))
    return rows


def _interval(k: int, n: int) -> None:
    """Wilson and Clopper-Pearson, computed TWICE with different libraries."""
    if n == 0:
        print("    no denominator; no interval")
        return
    from statsmodels.stats.proportion import proportion_confint
    import scipy.stats as st
    import mpmath as mp

    w_lo, w_hi = proportion_confint(k, n, method="wilson")
    b_lo, b_hi = proportion_confint(k, n, method="beta")
    # SECOND TOOL, SAME QUANTITIES, derived independently.
    z = st.norm.ppf(0.975)
    ph = k / n
    centre = (ph + z * z / (2 * n)) / (1 + z * z / n)
    half = (z / (1 + z * z / n)) * mp.sqrt(ph * (1 - ph) / n
                                           + z * z / (4 * n * n))
    s_lo, s_hi = float(centre - half), float(centre + half)
    cp_lo = 0.0 if k == 0 else float(st.beta.ppf(0.025, k, n - k + 1))
    cp_hi = 1.0 if k == n else float(st.beta.ppf(0.975, k + 1, n - k))

    print(f"    {k} of {n} = {100*k/n:.4f}%")
    print(f"    Wilson          statsmodels [{w_lo*100:.4f}%, {w_hi*100:.4f}%]")
    print(f"                    scipy+mpmath [{s_lo*100:.4f}%, {s_hi*100:.4f}%]")
    print(f"    Clopper-Pearson statsmodels [{b_lo*100:.4f}%, {b_hi*100:.4f}%]")
    print(f"                    scipy        [{cp_lo*100:.4f}%, {cp_hi*100:.4f}%]")
    agree = (abs(w_lo - s_lo) < 1e-9 and abs(w_hi - s_hi) < 1e-9
             and abs(b_lo - cp_lo) < 1e-9 and abs(b_hi - cp_hi) < 1e-9)
    print(f"    the 2 tools {'AGREE' if agree else 'DISAGREE -- do not quote this'}")


def main() -> int:
    answer_help(__doc__, __file__)
    rows = _tracked()
    if not rows:
        print("not a git checkout, or nothing tracked. Measurement void.")
        return 3

    print(f"THE EXECUTE BIT, DISK AGAINST INDEX ({', '.join(TREES)})")
    wrong, checked = [], 0
    for mode, path in rows:
        f = REPO / path
        if not f.is_file() or f.is_symlink():
            continue
        checked += 1
        if bool(f.stat().st_mode & 0o111) != (mode == "100755"):
            wrong.append((path, mode, oct(f.stat().st_mode)[-3:]))
    print(f"  tracked regular files checked: {checked}")
    print(f"  disagreeing with the index   : {len(wrong)}")
    _interval(len(wrong), checked)
    for path, mode, disk in wrong[:25]:
        print(f"      {path}: git {mode}, disk {disk}")

    print("\nWHAT A TEST SYMLINKS INTO A PYTEST TEMP TREE")
    found = 0
    for t in sorted((REPO / "bench" / "tests").glob("test_*.py")):
        src = t.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"^(.*\.symlink_to\(.*)$", src, flags=re.M):
            line = m.group(1).strip()
            if line.lstrip().startswith("#"):
                continue
            found += 1
            print(f"  {t.name}:{src[:m.start()].count(chr(10)) + 1}")
            print(f"      {line[:96]}")
    print(f"  call sites: {found}")

    print("\nMODE CENSUS OF THE TRACKED SCRIPT TREE, AGAINST THIS UMASK")
    prev = os.umask(0o022)
    os.umask(prev)
    print(f"  umask                    : {oct(prev)[2:].zfill(4)}")
    print(f"  a tool-created FILE would be: "
          f"{oct(0o666 & ~prev)[-3:]}")
    print(f"  a tool-created DIR  would be: {oct(0o777 & ~prev)[-3:]}")
    census: dict[str, int] = {}
    for mode, path in rows:
        f = REPO / path
        if f.is_file() and not f.is_symlink():
            census[oct(f.stat().st_mode)[-3:]] = \
                census.get(oct(f.stat().st_mode)[-3:], 0) + 1
    for m, n in sorted(census.items(), key=lambda kv: -kv[1]):
        flag = ""
        if m == "600":
            flag = "  <- the literal the fixture wrote for a file"
        elif m == "700":
            flag = "  <- the literal the fixture wrote for a directory"
        print(f"    {n:>5}  mode {m}{flag}")
    print(f"  repository root          : {oct((REPO).stat().st_mode)[-3:]}")
    return 0 if not wrong else 1


if __name__ == "__main__":
    raise SystemExit(main())
