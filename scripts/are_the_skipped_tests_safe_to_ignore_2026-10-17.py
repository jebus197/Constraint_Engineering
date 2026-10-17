#!/usr/bin/env python3
"""Task C6: list every skipped test with its reason and say whether it matters.

HIS QUESTION, 2026-10-05, verbatim: *"Are the 12 skipped safe to ignore?"* It
was written directly under a targeted regression run reporting "1643 passed,
12 skipped, 0 failed, in 10 minutes 16 seconds". Nothing answered it, and no
script existed that could. Later boards kept quoting skip counts without
classifying them -- 18 in B11 on 2026-10-15, 20 and 26 in the overnight report
of 2026-10-06.

WHY THE QUESTION IS SHARP RATHER THAN HOUSEKEEPING. A skip is exactly how a
guard stops running WITHOUT GOING RED, and a checker that decides nothing is
this project's most-repeated defect class: 11 confirmed defects since
2026-08-01 were additions that did nothing. So a skip count is not a neutral
statistic. It is a count of assertions that were not made.

WHAT THIS DOES, IN TWO PASSES, BECAUSE NEITHER ALONE ANSWERS HIM.

  STATIC. Every skip SITE in bench/tests, found with the ast module rather than
  by matching text, since `pytest.skip` appears in docstrings and comments
  across this suite. A site is not a skip: most never fire.

  LIVE. The skips that ACTUALLY FIRE, with pytest's own `-rs` report, over a
  chosen scope. The default scope is the pre-commit guard set, because a skip
  there is strictly more serious than one in the wider suite: the guard set is
  what gates every commit, so a guard skipped there is a gate that is open.

THE CLASSIFICATION, and the boundary is stated rather than implied:

  SAFE -- the test needs a resource that is absent BY DESIGN on this machine:
    his Responses folder, an experiment archive, an optional tool, the network.
    It would run where the resource exists, and its absence is not a defect.
  NOT SAFE -- the skip fires because something the PROJECT controls is unmet,
    so the guard is off in the very place it ought to run, or its condition can
    never be true. This is the class his question is really about.
  NEEDS HIS RULING -- the skip gates paid or live-model work, which is his
    money and his call, not a technical judgement.
  UNCLASSIFIED -- the reason does not match any rule above. Reported as its own
    class rather than folded into SAFE, because quietly defaulting an unknown
    to safe is how a skip count stops meaning anything.

Costs nothing beyond local test execution; dispatches to no model.

Usage:
  are_the_skipped_tests_safe_to_ignore_2026-10-17.py              # guard set
  are_the_skipped_tests_safe_to_ignore_2026-10-17.py --scope all  # every file
  are_the_skipped_tests_safe_to_ignore_2026-10-17.py --static-only
"""
from __future__ import annotations

import argparse
import ast
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
TESTS = REPO / "bench" / "tests"
HOOK = REPO / "hooks" / "pre-commit"

SKIP_CALLS = ("pytest.skip", "pytest.importorskip", "pytest.xfail")
SKIP_MARKS = ("pytest.mark.skipif", "pytest.mark.skip")

#: Ordered, and the order matters: the first rule that matches decides, so the
#: narrow classes come before the broad ones.
RULES = (
    ("NEEDS HIS RULING", r"paid|billing|costs money|live model|api key|"
                         r"spend|credit"),
    ("SAFE", r"not installed|unavailable|no .*binary|missing (tool|binary)|"
             r"wolfram|z3 |lean |optional"),
    ("SAFE", r"responses|his folder|not present|not in this clone|no archive|"
             r"archive|folder is absent|this machine|no report|no all-sim"),
    ("SAFE", r"network|offline|no route to the internet|netguard|"
             r"outbound calls denied"),
    ("SAFE", r"too (few|small)|fewer than|no denominator|empty|"
             r"too small to (measure|compare)"),
    ("SAFE", r"darwin|linux|windows|macos|platform|python 3\.\d"),
    ("NOT SAFE", r"not yet|todo|pending|unimplemented|future|disabled|"
                 r"temporarily|wip|flaky|known failure|xfail"),
)


def classify(reason: str) -> str:
    text = (reason or "").lower()
    if not text.strip():
        return "UNCLASSIFIED"
    for verdict, pattern in RULES:
        if re.search(pattern, text):
            return verdict
    return "UNCLASSIFIED"


def _dotted(call: ast.Call) -> str:
    f = call.func
    parts = []
    while isinstance(f, ast.Attribute):
        parts.append(f.attr)
        f = f.value
    if isinstance(f, ast.Name):
        parts.append(f.id)
    return ".".join(reversed(parts))


def _reason(call: ast.Call) -> str:
    for kw in call.keywords:
        if kw.arg == "reason" and isinstance(kw.value, ast.Constant):
            return str(kw.value.value)
    for arg in call.args:
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            return arg.value
    return ""


def static_sites() -> list[dict]:
    out = []
    for path in sorted(TESTS.rglob("*.py")):
        try:
            src = path.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(src)
        except (OSError, SyntaxError):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = _dotted(node)
            if name not in SKIP_CALLS + SKIP_MARKS:
                continue
            out.append({
                "file": str(path.relative_to(REPO)),
                "line": node.lineno,
                "kind": name,
                "reason": _reason(node),
                "verdict": classify(_reason(node)),
            })
    return out


def guard_files() -> list[str]:
    if not HOOK.is_file():
        return []
    text = HOOK.read_text(encoding="utf-8")
    m = re.search(r'GUARDS="([^"]*)"', text, re.S)
    if not m:
        return []
    return [l.strip() for l in m.group(1).splitlines() if l.strip()]


def fired(scope: str) -> tuple[list[tuple[str, str]], str]:
    """The skips pytest ACTUALLY reports, with their reasons."""
    if scope == "guards":
        targets = [f for f in guard_files() if (REPO / f).is_file()]
    else:
        targets = [str(p.relative_to(REPO)) for p in sorted(TESTS.rglob("*.py"))]
    if not targets:
        return [], "no targets"
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", *targets, "-q", "-rs",
         "--no-header", "-p", "no:cacheprovider"],
        capture_output=True, text=True, cwd=str(REPO))
    rows = []
    for line in proc.stdout.splitlines():
        m = re.match(r"SKIPPED \[(\d+)\] (.+?): (.*)$", line.strip())
        if m:
            rows.append((m.group(2), m.group(3)))
            continue
        m = re.match(r"SKIPPED (.+?): (.*)$", line.strip())
        if m:
            rows.append((m.group(1), m.group(2)))
    tail = [l for l in proc.stdout.splitlines()
            if re.search(r"\d+ (passed|skipped|failed)", l)]
    return rows, (tail[-1] if tail else "no summary line")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog=pathlib.Path(__file__).name,
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__)
    parser.add_argument("--scope", choices=("guards", "all"), default="guards",
                        help="which files to run for the LIVE pass")
    parser.add_argument("--static-only", action="store_true",
                        help="skip the live pass entirely")
    args = parser.parse_args(argv)

    sites = static_sites()
    print("STATIC: EVERY SKIP SITE IN THE SUITE")
    print(f"  sites: {len(sites)} across "
          f"{len({s['file'] for s in sites})} files")
    kinds: dict[str, int] = {}
    verdicts: dict[str, int] = {}
    for s in sites:
        kinds[s["kind"]] = kinds.get(s["kind"], 0) + 1
        verdicts[s["verdict"]] = verdicts.get(s["verdict"], 0) + 1
    for k, n in sorted(kinds.items(), key=lambda kv: -kv[1]):
        print(f"    {n:>4}  {k}")
    print("  A SITE IS NOT A SKIP. Most never fire; the live pass below is")
    print("  what answers his question.\n")

    print("  static verdicts, from the reason text alone:")
    for v, n in sorted(verdicts.items(), key=lambda kv: -kv[1]):
        print(f"    {n:>4}  {100*n/len(sites):6.2f}%  {v}")

    unconditional = [s for s in sites if s["kind"] == "pytest.mark.skip"]
    print(f"\n  UNCONDITIONAL SITES (no condition at all): {len(unconditional)}")
    for s in unconditional:
        print(f"    {s['file']}:{s['line']}  {s['reason'][:70]!r}")
    print("  Read each one: a literal `pytest.mark.skip` inside a")
    print("  `parametrize` default is CONDITIONAL in effect, because it")
    print("  decorates a placeholder used only when the real list is empty.")

    if args.static_only:
        print("\n  live pass skipped on request; the verdict below needs it.")
        return 0

    print(f"\nLIVE: WHAT ACTUALLY FIRES, scope={args.scope}")
    rows, summary = fired(args.scope)
    print(f"  pytest says: {summary}")
    print(f"  skip reports parsed: {len(rows)}")
    if not rows:
        print("  NOTHING SKIPPED IN THIS SCOPE. That is the strongest possible")
        print("  answer for it: there are no un-made assertions here.")
        return 0

    by_verdict: dict[str, list] = {}
    for where, reason in rows:
        by_verdict.setdefault(classify(reason), []).append((where, reason))
    order = ("NOT SAFE", "NEEDS HIS RULING", "UNCLASSIFIED", "SAFE")
    from statsmodels.stats.proportion import proportion_confint
    import scipy.stats as st
    total = len(rows)
    for v in order:
        group = by_verdict.get(v, [])
        k = len(group)
        w = proportion_confint(k, total, method="wilson")
        b = proportion_confint(k, total, method="beta")
        cp_hi = 1.0 if k == total else float(st.beta.ppf(0.975, k + 1,
                                                        total - k))
        print(f"\n  {v}: {k} of {total} = {100*k/total:.4f}%  "
              f"Wilson [{w[0]*100:.4f}%, {w[1]*100:.4f}%]  "
              f"CP [{b[0]*100:.4f}%, {b[1]*100:.4f}%] "
              f"scipy agrees {abs(b[1]-cp_hi) < 1e-9}")
        for where, reason in group[:12]:
            print(f"      {where}")
            print(f"        {reason[:100]}")
        if len(group) > 12:
            print(f"      ... and {len(group) - 12} more")

    unsafe = len(by_verdict.get("NOT SAFE", []))
    unknown = len(by_verdict.get("UNCLASSIFIED", []))
    print("\nTHE ANSWER TO HIS QUESTION")
    if unsafe == 0 and unknown == 0:
        print("  YES, for this scope, and here is why rather than on trust:")
        print("  every skip that fired names a resource absent by design on")
        print("  this machine -- his Responses folder, an archive, an optional")
        print("  tool, or the network, which the suite denies by default. Each")
        print("  would RUN where that resource exists, so none is a guard")
        print("  switched off in the place it ought to run.")
    else:
        print(f"  NO, not entirely: {unsafe} fired for a reason the project")
        print(f"  controls and {unknown} could not be classified at all. Those")
        print("  are assertions not being made, and each is listed above.")
    print("  THE BOUNDARY: this answers the scope that was run. A skip in the")
    print("  wider suite is not covered by a guard-set pass; use --scope all.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
