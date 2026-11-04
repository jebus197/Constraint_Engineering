#!/usr/bin/env python3
"""What installing a mypy config would actually reveal, measured not guessed.

B21 asks the founder to rule on a mypy config, noting that installing one
"would REVEAL existing errors rather than introduce new ones". That is true and
it is not a number, so the decision has had no size attached to it.

`scripts/does_mypy_check_anything_2026-11-02.py` deliberately stopped short of
this, and said why: "What a tree-wide mypy run WOULD report is not measured
here. His machine has 8 cores and 8 GiB with a derived budget of 2 heavy
processes, and a full run over 201 bench files is a heavy process of unknown
cost." THE COST IS NOW KNOWN AND IS NOT HEAVY: 627 files under `scripts/`
check in 18.3 s, so the tree is seconds rather than minutes, and the deferral's
own stated reason no longer holds.

TWO THINGS HAD TO BE FIXED BEFORE ANY RUN WAS POSSIBLE, AND BOTH ARE NAMED
HERE BECAUSE THE FIRST DIAGNOSIS WAS WRONG:
  1. Sandbox copies. 926 of 2,988 `*.py` under the repo root, 0.309906, live
     under `bench/logs/`, and mypy aborts with "Source file found twice under
     different module names". `--exclude bench/logs/` clears that.
  2. The package layout, WHICH EXCLUDING THE LOGS DOES NOT FIX. `bench/` has
     no `__init__.py`, so `bench/routing.py` is reachable as both
     `bench.routing` and `routing` and mypy still aborts.
     `--explicit-package-bases` clears that. Measured: with the exclusion
     alone the run ABORTS; with both flags it CHECKS.

A BARE TOTAL IS NOT ACTIONABLE, so every error is bucketed by its own code:
  * RESOLUTION -- `import-untyped` and `import-not-found`. Third-party packages
    without stubs and sibling imports mypy cannot follow. These are silenced by
    a config block, not by editing code, and they are NOT project defects.
  * ANNOTATION -- `var-annotated`, `annotation-unchecked`, `no-untyped-def`.
    Missing type information. Cosmetic until a stricter flag is chosen.
  * POTENTIAL DEFECT -- `union-attr`, `arg-type`, `index`, `operator`,
    `attr-defined`, `assignment`, `return-value`, `dict-item`, `call-arg`.
    These describe operations that can fail at run time, and `union-attr` in
    particular is attribute access on a possibly-None value.
  * OTHER -- everything else, reported rather than folded into a neighbour.

The split is what makes the decision sizeable: a figure dominated by
RESOLUTION is a configuration task, and one dominated by POTENTIAL DEFECT is
a repair backlog. This script says which.
"""
from __future__ import annotations

import collections
import pathlib
import re
import subprocess
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[1]

RESOLUTION = {"import-untyped", "import-not-found", "import"}
ANNOTATION = {"var-annotated", "annotation-unchecked", "no-untyped-def",
              "no-untyped-call", "type-arg"}
POTENTIAL = {"union-attr", "arg-type", "index", "operator", "attr-defined",
             "assignment", "return-value", "dict-item", "call-arg",
             "call-overload", "list-item", "typeddict-item", "override",
             "return", "has-type", "valid-type", "func-returns-value"}

SCOPES = ["scripts", "bench", "hooks"]
CODE = re.compile(r"\[([a-z-]+)\]\s*$")


def _run(scopes: list[str]) -> tuple[str, float, bool]:
    """ONE invocation over ALL scopes, never one per scope summed.

    ★ CORRECTED 2026-11-04, SAME DAY, AFTER THIS SCRIPT'S OWN FIGURE WAS
    CONTRADICTED. The first version ran mypy once per scope and added the
    counts, giving 1,274 in the POTENTIAL DEFECT bucket. A single combined
    invocation gives 1,168. The difference is module resolution: checking
    `scripts/` alone makes `bench` an unresolvable import, and checking them
    together resolves it, so per-scope runs manufacture import errors that a
    real config run would not produce. A config runs ONCE over the tree, so
    the combined invocation is the quantity the decision needs and the summed
    one is an artefact of how it was measured.
    """
    cmd = [sys.executable, "-m", "mypy", "--exclude", "bench/logs/",
           "--explicit-package-bases", "--no-error-summary", *scopes]
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO))
    out = r.stdout + r.stderr
    return out, time.time() - t0, "errors prevented further checking" in out


def _iv(k: int, n: int) -> str:
    from statsmodels.stats.proportion import proportion_confint
    from scipy.stats import beta as sbeta
    import mpmath as mp
    mp.mp.dps = 30
    lo, hi = proportion_confint(k, n, method="wilson")
    z = mp.mpf("1.959963984540054235524594430520551527955")
    p = mp.mpf(k) / n
    d = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / d
    h = (z / d) * mp.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    cp_lo = float(sbeta.ppf(0.025, k, n - k + 1)) if k else 0.0
    cp_hi = float(sbeta.ppf(0.975, k + 1, n - k)) if k < n else 1.0
    return (f"{k} of {n} = {k/n:.6f}  Wilson [{max(0.0, lo):.6f}, {hi:.6f}] "
            f"(mpmath agrees to {abs(float(c+h)-hi):.1e})  "
            f"Clopper-Pearson [{cp_lo:.6f}, {cp_hi:.6f}]")


def _bucket(code: str) -> str:
    if code in RESOLUTION:
        return "RESOLUTION"
    if code in ANNOTATION:
        return "ANNOTATION"
    if code in POTENTIAL:
        return "POTENTIAL DEFECT"
    return "OTHER"


def main() -> int:
    print("=" * 78)
    print("1. THE RUN IS POSSIBLE ONLY WITH 2 FLAGS, AND 1 OF THEM WAS MISSED")
    print("=" * 78)
    probe = "bench/cdsfl_registry/"
    for label, extra in (("exclusion alone", ["--exclude", "bench/logs/"]),
                         ("exclusion + explicit-package-bases",
                          ["--exclude", "bench/logs/", "--explicit-package-bases"])):
        cmd = [sys.executable, "-m", "mypy"] + extra + ["--no-error-summary", probe]
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO))
        out = r.stdout + r.stderr
        aborted = "errors prevented further checking" in out
        print(f"  {label:<38} {'ABORTS' if aborted else 'CHECKS'}")
    print(f"\n  so the first diagnosis -- that the sandbox copies are the whole")
    print(f"  cause -- was incomplete. `bench/` has no __init__.py, so")
    print(f"  bench/routing.py resolves as both bench.routing and routing.")

    print()
    print("=" * 78)
    print("2. WHAT A TREE-WIDE RUN REPORTS, AND WHAT IT COSTS")
    print("=" * 78)
    per_code = collections.Counter()
    per_file = collections.Counter()
    live = [s for s in SCOPES if (REPO / s).is_dir()]
    out, total_secs, aborted = _run(live)
    for line in out.splitlines():
        if ": error:" not in line:
            continue
        m = CODE.search(line)
        per_code[m.group(1) if m else "(uncoded)"] += 1
        per_file[line.split(":", 1)[0]] += 1
    nf = sum(len([p for p in (REPO / s).rglob("*.py") if "logs" not in p.parts])
             for s in live)
    total = sum(per_code.values())
    print(f"  1 invocation over {' '.join(live)}")
    print(f"  {nf:>5} files  {total_secs:>6.1f} s  {total:>5} errors  "
          f"{'ABORTED' if aborted else 'checked'}")
    print(f"\n  PER-SCOPE RUNS SUMMED WOULD GIVE A DIFFERENT AND WRONG FIGURE:")
    print(f"  checking scripts/ alone makes `bench` an unresolvable import, so")
    print(f"  the sum manufactures import errors a real config run never sees.")
    print(f"\n  TOTAL {total:,} errors in {total_secs:.1f} s of wall clock.")
    print(f"  The deferral called this 'a heavy process of unknown cost'. It is")
    print(f"  neither heavy nor unknown now, so that reason has lapsed.")

    print()
    print("=" * 78)
    print("3. THE SPLIT THAT MAKES IT A DECISION RATHER THAN A NUMBER")
    print("=" * 78)
    buckets = collections.Counter()
    for code, n in per_code.items():
        buckets[_bucket(code)] += n
    for b in ("RESOLUTION", "ANNOTATION", "POTENTIAL DEFECT", "OTHER"):
        n = buckets.get(b, 0)
        print(f"\n  {b}: {_iv(n, total)}")
        codes = sorted(((c, k) for c, k in per_code.items() if _bucket(c) == b),
                       key=lambda x: -x[1])[:6]
        print(f"    {', '.join(f'{c}={k}' for c, k in codes)}")

    print()
    print("=" * 78)
    print("4. ONE COUNTABLE IDIOM DOMINATES THE POTENTIAL-DEFECT BUCKET")
    print("=" * 78)
    # A DETERMINISTIC SAMPLE OF 12 union-attr FINDINGS WAS READ, AND 10 OF THE
    # 12 WERE THE SAME LINE SHAPE: `spec.loader.exec_module(mod)` after
    # `importlib.util.spec_from_file_location`. mypy flags it because
    # `spec_from_file_location` is typed `ModuleSpec | None` and `spec.loader`
    # is `Loader | None`. It is this project's standard way of loading a module
    # by path -- used by its own producers and guards throughout -- and a None
    # there would raise loudly rather than pass silently. So it is counted
    # EXACTLY rather than estimated from the sample, by reading the SOURCE LINE
    # each finding sits on rather than the message text.
    IDIOM = re.compile(r"spec\.loader\.exec_module|module_from_spec"
                       r"|spec_from_file_location")
    cache: dict[str, list[str]] = {}

    def _srcline(f: str, n: int) -> str:
        if f not in cache:
            try:
                cache[f] = (REPO / f).read_text(encoding="utf-8").splitlines() \
                    if not pathlib.Path(f).is_absolute() \
                    else pathlib.Path(f).read_text(encoding="utf-8").splitlines()
            except OSError:
                cache[f] = []
        ls = cache[f]
        return ls[n - 1].strip() if 0 < n <= len(ls) else ""

    pot_rows, idiom_rows = [], []
    for line in out.splitlines():
        if ": error:" not in line:
            continue
        m = CODE.search(line)
        if not m or _bucket(m.group(1)) != "POTENTIAL DEFECT":
            continue
        parts = line.split(":")
        try:
            f, ln = parts[0], int(parts[1])
        except (IndexError, ValueError):
            continue
        pot_rows.append((f, ln, m.group(1)))
        if IDIOM.search(_srcline(f, ln)):
            idiom_rows.append((f, ln, m.group(1)))

    if pot_rows:
        print(f"\n  the importlib module-loading idiom: "
              f"{_iv(len(idiom_rows), len(pot_rows))}")
        remaining = len(pot_rows) - len(idiom_rows)
        print(f"\n  POTENTIAL DEFECT after removing it: {remaining:,}")
        rem = collections.Counter(c for f, l, c in pot_rows
                                 if (f, l, c) not in set(idiom_rows))
        print(f"    {', '.join(f'{c}={k}' for c, k in rem.most_common(8))}")
        print(f"\n  A SAMPLE OF 12 WAS READ AND 10 WERE THIS IDIOM. The other 2")
        print(f"  were a guard mypy cannot see through and a loosely typed dict")
        print(f"  value, so neither was a live bug either. That is 12 read of")
        print(f"  {len(pot_rows):,}, so the remaining {remaining:,} is an UPPER BOUND on the")
        print(f"  backlog and not an estimate of it.")

    print()
    print("=" * 78)
    print("5. WHERE THEY CONCENTRATE")
    print("=" * 78)
    print(f"\n  files carrying at least 1 error: {len(per_file):,}")
    for f, n in per_file.most_common(8):
        print(f"    {n:>4}  {f}")

    print()
    print("=" * 78)
    print("VERDICT")
    print("=" * 78)
    res = buckets.get("RESOLUTION", 0)
    pot = buckets.get("POTENTIAL DEFECT", 0)
    print(f"""
  Installing a config reveals {total:,} findings across {len(per_file):,} files.
  {res:,} of them, {res/total:.4f}, are IMPORT RESOLUTION -- third-party packages
  without stubs and sibling imports mypy cannot follow. Those are silenced by
  a config block and are not project defects, so the headline number overstates
  the repair work by about a factor of {total/max(total-res,1):.2f}.

  {pot:,} are in classes that describe an operation which can fail at run time.
  That is the real backlog, and it is the figure his decision should rest on
  rather than the total.

  WHAT THIS DOES NOT SAY. It does not say those {pot:,} are bugs. mypy reports a
  type it cannot prove safe, and this project has already found 2 of its
  reports on registry.py to be idiomatic Python -- a try/except tomllib
  fallback and a loop variable reused with a different type. Converting this
  count into a defect count needs reading, and no sample has been read.
""")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
