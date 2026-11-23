# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'panel_joint_b12_boardpolicy_20261123T201748Z', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 5249a3bbef454d6c54f9f07c79d5a30842334cda9ec0cab38505974323482b71
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The board guard count was short by 2, and the 2 were the ends of the list.

DESTINATION `scripts/`. Written 2026-11-23. FALSIFIER for
`scripts/why_is_the_board_getting_slower_2026-11-23.py`.

WHAT IS CLAIMED. `board_guard_count()` matched whole LINES against
`bench/tests/test_[A-Za-z0-9_-]+\\.py`. The first entry of the hook `GUARDS`
list shares its line with `GUARDS="` and the last carries the closing `"`, so
neither is a bare path and neither was ever counted. The figure printed as
"guards on the board NOW" was therefore 2 below the list the board runs,
below the hook own ledger `guards` field, and below the 2 parsers already in
the tree. 3 parsers for 1 quantity gave 3 values.

WHY THE SIGN OF THE ERROR MATTERS RATHER THAN ITS SIZE. The same function
supplies the denominator of the per-guard cost in the growth decomposition, so
a count short at both ends inflates per-guard cost -- and per-guard cost is the
factor that decomposition reports as dominant.

HOW IT IS CHECKED, AGAINST 3 INDEPENDENT ROUTES AND 1 CONSTRUCTED CASE:

  1. a synthetic 3-entry GUARDS block, where the correct answer is 3 and the
     line-regex answer is 1. This arm does not depend on the real hook at all,
     so it still discriminates if the hook changes shape.
  2. the REAL hook, against a block-parser count written here independently.
  3. the REAL hook, against the hook OWN counting expression,
     `printf '%s\\n' "$GUARDS" | grep -c 'bench/tests/'`, executed by `sh`.
  4. the decomposition identity: the 2 ratios must multiply to the total, and
     both must be computed from the same window endpoints.

AND THE DOCSTRING IS CHECKED FOR VOLATILE FIGURES, because `answer_help`
renders it verbatim: the header carried a longest-board figure, a day share and
a guard count that were all superseded within hours, and `--help` printed them
as current. A measured minute or a 6-decimal fraction in that header is
therefore refused.

VERDICT PROTOCOL. Prints `FALSIFIED` and exits 1 when any arm fails; exits 0
when all pass.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import pathlib
import re
import subprocess
import sys

SYNTHETIC_HOOK = '''#!/bin/sh
GUARDS="bench/tests/test_first_2026-01-01.py
bench/tests/test_middle_2026-02-02.py
bench/tests/test_last_2026-03-03.py"
echo done
'''


def _repo_root() -> pathlib.Path:
    for base in (pathlib.Path(__file__).resolve(), pathlib.Path.cwd().resolve()):
        for d in (base, *base.parents):
            if (d / "hooks" / "pre-commit").is_file() and (d / "bench").is_dir():
                return d
    raise RuntimeError("cannot locate the repository root")


REPO = _repo_root()
TARGET = REPO / "scripts" / "why_is_the_board_getting_slower_2026-11-23.py"
HOOK = REPO / "hooks" / "pre-commit"


def real_producer():
    """Import the REAL producer, never a retyped copy of its predicate."""
    spec = importlib.util.spec_from_file_location("_cdsfl_board_growth", TARGET)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def independent_block_count(text: str) -> int:
    """A second route to the same count, written here and not imported."""
    m = re.search(r'GUARDS="(.*?)"', text, re.S)
    return len({x.strip() for x in m.group(1).split() if x.strip()})


def hooks_own_count(text: str) -> int:
    """The hook OWN expression, executed rather than paraphrased."""
    m = re.search(r'(GUARDS=".*?")', text, re.S)
    script = (m.group(1) + "\n"
              "printf '%s\\n' \"$GUARDS\" | grep -c 'bench/tests/' | head -1\n")
    r = subprocess.run(["sh", "-c", script], capture_output=True, text=True,
                       timeout=30)
    return int(r.stdout.strip())


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.parse_args(argv)
    mod = real_producer()
    bad = []

    n = mod.board_guard_count(SYNTHETIC_HOOK)
    print(f"  1. synthetic 3-entry GUARDS block -> {n} (must be 3)")
    if n != 3:
        bad.append(f"the synthetic block of 3 guards counted as {n}; the first "
                   "and/or last entry is being dropped")

    hook_text = HOOK.read_text()
    got = mod.board_guard_count()
    indep = independent_block_count(hook_text)
    print(f"  2. real hook: producer {got} vs independent block parser {indep}")
    if got != indep:
        bad.append(f"the producer counts {got} where the block parser counts {indep}")

    own = hooks_own_count(hook_text)
    print(f"  3. real hook: producer {got} vs the hook own grep -c {own}")
    if got != own:
        bad.append(f"the producer counts {got} where the hook itself counts {own}")

    rows = mod.determinate_rows()
    if not hasattr(mod, "decompose"):
        # ARM 4 IS SKIPPED RATHER THAN CRASHING, AND THE REASON IS THE TOOL
        # OWN VACUITY CASE 2. Driven against the pre-fix target this raised
        # AttributeError at this line, so the run failed by ABSENCE and never
        # printed the count arms that had ALREADY detected the real defect.
        # A falsifier that dies before reporting gives the right exit code for
        # the wrong reason.
        print("  4. decomposition SKIPPED: the target has no `decompose`")
        bad.append("the target exposes no `decompose`, so the growth split has "
                   "no producer and the 2 ratios cannot be shown to share a window")
    elif len(rows) >= 8:
        d = mod.decompose(rows)
        prod = d["count_ratio"] * d["per_guard_ratio"]
        print(f"  4. decomposition {d['count_ratio']:.4f} x "
              f"{d['per_guard_ratio']:.4f} = {prod:.4f} vs total "
              f"{d['total_ratio']:.4f}  window {d['window'][0]}..{d['window'][1]}")
        if abs(prod - d["total_ratio"]) > 1e-9:
            bad.append("the 2 decomposition ratios do not multiply to the total, "
                       "so they are not computed over one window")
        if d["guards"][0] <= 0 or d["minutes"][0] <= 0:
            bad.append("the decomposition endpoint is degenerate")
    else:
        print(f"  4. decomposition SKIPPED: only {len(rows)} determinate rows")

    doc = mod.__doc__ or ""
    volatile = [p for p in (r"\d+\.\d+ min", r"0\.\d{6}", r"\d+\.\d{4}x")
                if re.search(p, doc)]
    print(f"  5. volatile figures in the docstring: {volatile or 'none'}")
    if volatile:
        bad.append("the docstring carries a measured figure that `--help` will "
                   f"print as current: patterns {volatile}")

    if bad:
        print("FALSIFIED")
        for b in bad:
            print(f"    - {b}")
        raise AssertionError("; ".join(bad))
    print("  the count agrees with its own subject on 3 routes and the "
          "decomposition is one window. Defect ABSENT.")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    try:
        from _cli_help import answer_help
        answer_help(__doc__, __file__, takes_no_arguments=False)
    except ImportError:
        pass
    raise SystemExit(main())
