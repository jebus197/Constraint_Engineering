#!/usr/bin/env python3
"""ARM 5, the paired baseline: what reaches a seat at a2a0197 against what reaches one now.

WHY THIS EXISTS. Arm 5 is the last of the 12 programme measurements to carry a
result. It asks whether the runner and composer as they now stand deliver the
project's own specification to a seat better than they did at commit `a2a0197`
(2026-09-06). Every other arm was answered from a run's completed logs; this one
needs 2 runs, because a composer cannot be asked what it would have sent -- it
has to send it.

WHAT IS HELD FIXED, MEASURED RATHER THAN ASSUMED. A paired comparison that moves
2 things answers nothing, so each of these was checked before either arm ran and
each is re-checked by this script at every invocation:

  * the review TARGET is byte-identical at both commits;
  * the CORE DIRECTIVE FILE is byte-identical at both commits, so the HARD-block
    population is shared by construction;
  * `_block_is_hard` and `_split_packet_directives` are byte-identical as ASTs,
    so the predicate that decides WHICH blocks are HARD is one predicate;
  * the dispatched SEAT COUNT is 6 on both sides and the DOMAIN is `statistics`
    on both sides;
  * the per-dispatch TIMEOUT is pinned to the same value on both arms, because
    the defaults differ (900 s at the baseline, 3600 s now) and a killed seat
    reads as a composer effect;
  * the STAND-IN SEAT MODEL is pinned to `sonnet` on both arms. THIS ONE IS A
    NAMED CHOICE AND NOT A NEUTRAL ONE. The baseline shim cannot dispatch
    anything else -- `SHIM.install(timeout=...)` passes no model, so it takes the
    shim default -- while the current launcher defaults to `opus` on the
    founder's ruling of 2026-09-07. Running each arm on its own default would
    vary seat CAPABILITY and composer TOGETHER, and opus against sonnet is the
    larger of the 2 effects, so it would plausibly swamp the thing under test.
    Pinning isolates the composer. The cost is explicit: ARM 5 THEREFORE SAYS
    NOTHING ABOUT THE OPUS UPGRADE, which is a separate change already carrying
    its own justification.

WHAT IS LEFT VARYING, which is the whole point: of the 3 composer functions that
bear on delivery, 2 are identical across the 2 commits and the 1 that DIFFERS is
`_render_universal_minimal` -- the rulebook repair of 2026-10-15. Arm 5 is a test
of that function and of the runner changes around it.

THE INSTRUMENT IS VERBATIM CONTAINMENT, and it is the same instrument used on
2026-10-15 for the pre- and post-repair reduced forms. A first-8-words probe
space-joins across newlines and cannot match a multi-line block; 9 of the HARD
blocks are multi-line, so that probe understates. This script therefore asks only
whether each HARD block appears in the delivered prompt character for character.

A CAPTURE CAVEAT THAT MATTERS. The delivered prompt is recovered from the live
process table (`ps -ww -o command=`), which renders newlines as the 4 characters
backslash-0-1-2. Verbatim containment against a multi-line block fails silently
on an undecoded capture, so decoding is done here and the decode is asserted:
a capture that still holds the literal token after decoding is refused rather
than measured.

NOTHING HERE DISPATCHES ANYTHING AND NOTHING COSTS MONEY. It reads 2 captured
prompt files and the 2 checkouts.
"""
from __future__ import annotations

import ast
import hashlib
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

from _cli_help import answer_help                                  # noqa: E402

BASELINE_TREE = pathlib.Path(
    "/Users/georgejackson/Developer_Projects/arm5_baseline_a2a0197")
EVIDENCE = BASELINE_TREE / "bench/logs/arm5_evidence"
BASELINE_PROMPT = EVIDENCE / "baseline_seat_prompt_full.txt"
HEAD_PROMPT = EVIDENCE / "head_seat_prompt_full.txt"

CORE_REL = "bench/directives/universal/cdsfl_core_formal.md"
TARGET_REL = "bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md"
COMPOSER_REL = "bench/cdsfl_registry/composer.py"
PINNED = ("_block_is_hard", "_split_packet_directives")
VARYING = ("_render_universal_minimal",)


def wilson(k: int, n: int) -> str:
    """A 95% interval, computed twice by 2 independent libraries."""
    if n == 0:
        return "n=0, no interval"
    from statsmodels.stats.proportion import proportion_confint
    lo_a, hi_a = proportion_confint(k, n, alpha=0.05, method="wilson")
    import scipy.stats as st
    z = st.norm.ppf(0.975)
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    lo_b, hi_b = centre - half, centre + half
    agree = max(abs(lo_a - lo_b), abs(hi_a - hi_b))
    assert agree < 1e-9, f"the 2 interval routes disagree by {agree:.3e}"
    return (f"{100 * k / n:.4f}%, 95% Wilson [{100 * lo_a:.4f}%, "
            f"{100 * hi_a:.4f}%] (2 routes agree to {agree:.2e})")


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16] if path.exists() else "ABSENT"


def fn_ast_hash(path: pathlib.Path, name: str) -> str:
    if not path.exists():
        return "ABSENT"
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return hashlib.sha256(ast.dump(node).encode()).hexdigest()[:12]
    return "ABSENT"


def decode_ps_capture(path: pathlib.Path) -> str:
    """Undo `ps` newline encoding, and REFUSE a capture that did not decode."""
    raw = path.read_text(errors="replace")
    out = raw.replace("\\012", "\n").replace("\\011", "\t")
    if "\\012" in out:
        raise SystemExit(f"FATAL: {path.name} still holds the literal newline "
                         "token after decoding; refusing to measure it.")
    return out


def hard_blocks() -> list[str]:
    from bench.cdsfl_registry import composer as C
    core = (REPO / CORE_REL).read_text()
    blocks = C._split_packet_directives(core)
    return [b for b in blocks if C._block_is_hard(b)]


def controls() -> bool:
    print("=" * 78)
    print("1. WHAT IS HELD FIXED — CHECKED, NOT ASSUMED")
    print("=" * 78)
    ok = True
    for rel, label in ((CORE_REL, "core directive file"),
                       (TARGET_REL, "review target")):
        a, b = sha(BASELINE_TREE / rel), sha(REPO / rel)
        same = a == b and a != "ABSENT"
        ok &= same
        print(f"  {label:<24} baseline={a}  head={b}  "
              f"{'IDENTICAL' if same else '*** DIFFERS ***'}")
    for fn in PINNED:
        a = fn_ast_hash(BASELINE_TREE / COMPOSER_REL, fn)
        b = fn_ast_hash(REPO / COMPOSER_REL, fn)
        same = a == b and a != "ABSENT"
        ok &= same
        print(f"  {fn:<24} baseline={a}      head={b}          "
              f"{'IDENTICAL' if same else '*** DIFFERS ***'}")
    print()
    print("  THE FUNCTION UNDER TEST — it is supposed to differ:")
    for fn in VARYING:
        a = fn_ast_hash(BASELINE_TREE / COMPOSER_REL, fn)
        b = fn_ast_hash(REPO / COMPOSER_REL, fn)
        print(f"  {fn:<24} baseline={a}      head={b}          "
              f"{'DIFFERS (expected)' if a != b else '*** IDENTICAL: arm 5 has nothing to measure ***'}")
        ok &= (a != b)
    return ok


def measure() -> int:
    hard = hard_blocks()
    print()
    print("=" * 78)
    print("2. HARD BLOCKS THAT ACTUALLY REACHED A SEAT")
    print("=" * 78)
    print(f"  the project's own predicate finds {len(hard)} HARD blocks in the "
          f"core directive file")
    results = {}
    for label, path in (("BASELINE a2a0197", BASELINE_PROMPT),
                        ("HEAD (current)", HEAD_PROMPT)):
        if not path.exists():
            print(f"  {label:<18} NOT YET CAPTURED ({path.name})")
            continue
        text = decode_ps_capture(path)
        carried = sum(1 for b in hard if b in text)
        results[label] = carried
        print(f"  {label:<18} prompt {len(text):>7,} chars   "
              f"HARD carried {carried} of {len(hard)}")
        print(f"                     {wilson(carried, len(hard))}")
    if len(results) == 2:
        a, b = results["BASELINE a2a0197"], results["HEAD (current)"]
        print()
        print(f"  PAIRED DIFFERENCE: {b - a:+d} HARD blocks of {len(hard)}")
        if a == b:
            print("  THE ARM RETURNS NO DIFFERENCE ON THIS MEASURE.")
        missing_head = [x.split("\n")[0][:84] for x in hard
                        if x not in decode_ps_capture(HEAD_PROMPT)]
        missing_base = [x.split("\n")[0][:84] for x in hard
                        if x not in decode_ps_capture(BASELINE_PROMPT)]
        for name, miss in (("BASELINE", missing_base), ("HEAD", missing_head)):
            print(f"  EVERY HARD BLOCK {name} DROPPED, UNFILTERED "
                  f"({len(miss)}):")
            for m in miss:
                print(f"    - {m!r}")
    else:
        print()
        print("  ONE ARM OUTSTANDING. The paired figure is not computed from a "
              "single arm, and no difference is reported here.")
    return 0


def main() -> int:
    print("ARM 5 — THE PAIRED BASELINE")
    print("commit a2a0197 (2026-09-06) against current HEAD")
    ok = controls()
    rc = measure()
    print()
    print("=" * 78)
    if not ok:
        print("CONTROLS FAILED. A figure from this run is NOT a paired "
              "comparison; fix the control before quoting anything above.")
        return 1
    print("CONTROLS HELD. Every quantity above is produced by this script.")
    return rc


if __name__ == "__main__":
    answer_help(__doc__, __file__)
    raise SystemExit(main())
