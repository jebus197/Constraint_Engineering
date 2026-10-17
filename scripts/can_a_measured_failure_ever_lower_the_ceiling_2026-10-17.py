#!/usr/bin/env python3
"""Can a recorded dispatch failure ever lower a seat's routing ceiling?

WHY THIS EXISTS. Task B12 records that `max_successful_prompt_chars` is a
lifetime high-water mark standing 6.49x above what CC2 has handled in its last
50 dispatches, and that *"the arm that would lower the number has never fired"*.
That is true, and this script asks the next question, which is stronger and had
not been asked: COULD it fire? The answer decides which of the founder's 3
options is even available.

WHAT IT MEASURES, BY EXECUTION RATHER THAN BY READING.

1. THE EFFECTIVE CEILING, probed by bisecting `_decomposition_is_futile` over
   `fixed_chars` with a crafted fingerprint, so the figure is the one the live
   routing path computes rather than one re-derived from the formula.

2. WHETHER A RECORDED FAILURE CHANGES IT. Measured 2026-10-17: a paid seat as it
   stands has an effective ceiling of 418,686 characters. Injecting a FAILURE at
   80,000 characters leaves it at 418,686 -- UNCHANGED. The failure only applies
   when `max_successful_prompt_chars` is 0, where the ceiling becomes 80,001.
   The reason is the structure of the consumer: `max_failed_prompt_chars` is read
   inside the `else` of `if observed > 0`, and every paid seat has a non-zero
   observed maximum. So `max_failed_prompt_chars` can never reach the ceiling, not
   merely unfired, and option 2 -- bound the ceiling by a measured failure --
   requires changing the CONSUMER, not only the recorder.

3. WHY IT HAS NEVER FIRED, which turned out not to be the detector. The writer is
   gated on the literal phrase `"context length"` appearing in the dispatch
   error, and a narrow phrase was the obvious suspect. The archive REFUTES that:
   across 172 archived json files carrying an error field and 37 distinct error
   strings, 0 are overflow-shaped under a deliberately broad pattern covering
   `context length`, token limits, `413`, `context_length_exceeded`, "too long",
   "request too large" and "reduce the length". No dispatch has ever hit a
   context limit, so the narrow phrase is UNTESTED rather than wrong. It is left
   alone: widening an untested predicate on no evidence is the shape of fix the
   founder objected to on 2026-10-13 and 2026-10-14.

WHAT THIS DOES NOT DO. It changes nothing. Which of the 3 options to take alters
routing for paid seats and is the founder's decision, as
`bench/reference_runner_v3.py` says in its own words: *"a ratchet that cannot
climb ... Changing it alters routing for paid seats and is a design decision,
not a repair."*

Costs nothing and dispatches no model. Run: python3 scripts/<this file>
"""
from __future__ import annotations

import collections
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"

#: Deliberately broad: every phrasing a vendor is known to use for an
#: over-length request, so a miss cannot be blamed on the pattern.
OVERFLOW = re.compile(
    r"context[_ ]length|too (?:many|long)|maximum context|token limit|"
    r"exceeds?.{0,20}(?:limit|maximum|context)|prompt is too|input too|"
    r"request too large|\b413\b|context_length_exceeded|reduce the length",
    re.I)
#: What the live writer in `reference_runner_v3.py` actually tests for.
LIVE_PREDICATE = re.compile(r"context length", re.I)


class _Cfg:
    pre_decompose_models = ()


class _Mgr:
    config = _Cfg()


def effective_ceiling(runner, fingerprint: dict) -> int:
    """Bisect the live routing predicate for the largest size it admits."""
    original = runner._load_fingerprint_cache
    runner._load_fingerprint_cache = lambda: {"PROBE": dict(fingerprint)}
    try:
        lo, hi = 0, 4_000_000
        for _ in range(48):
            mid = (lo + hi) // 2
            if runner._decomposition_is_futile("PROBE", _Mgr(), mid):
                hi = mid
            else:
                lo = mid
        return hi
    finally:
        runner._load_fingerprint_cache = original


def main() -> int:
    answer_help(__doc__, __file__)
    import bench.reference_runner_v3 as runner

    print("THE EFFECTIVE CEILING, PROBED THROUGH THE LIVE ROUTING PREDICATE")
    cases = [
        ("a paid seat as it stands today",
         {"max_successful_prompt_chars": 465206, "max_failed_prompt_chars": 0}),
        ("the same seat, FAILURE recorded at 80,000",
         {"max_successful_prompt_chars": 465206,
          "max_failed_prompt_chars": 80000}),
        ("the same seat, FAILURE recorded at 10,000",
         {"max_successful_prompt_chars": 465206,
          "max_failed_prompt_chars": 10000}),
        ("a seat with NO recorded success, failure at 80,000",
         {"max_successful_prompt_chars": 0, "max_failed_prompt_chars": 80000}),
    ]
    results = {}
    for name, fp in cases:
        got = effective_ceiling(runner, fp)
        results[name] = got
        print(f"  {name:<46} {got:>10,}")

    base = results["a paid seat as it stands today"]
    with_fail = results["the same seat, FAILURE recorded at 80,000"]
    tiny_fail = results["the same seat, FAILURE recorded at 10,000"]
    ignored = (with_fail == base and tiny_fail == base)
    print(f"\n  does a recorded failure move the ceiling? "
          f"{'NO -- it is ignored' if ignored else 'yes'}")
    if ignored:
        print("  `max_failed_prompt_chars` can never reach the ceiling for any seat")
        print("  with a non-zero recorded success, which is all 5 paid seats.")

    print("\nWHY IT HAS NEVER FIRED: WHAT REAL DISPATCH ERRORS SAY")
    errs: collections.Counter[str] = collections.Counter()
    files = 0
    for p in LOGS.rglob("*.json"):
        if "sandbox_harvest" in str(p):
            continue
        try:
            blob = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if '"dispatch_error"' not in blob and '"error"' not in blob:
            continue
        files += 1
        for m in re.finditer(
                r'"(?:dispatch_)?error"\s*:\s*"((?:[^"\\]|\\.){4,400})"', blob):
            e = m.group(1)[:160]
            if e.lower() in ("null", "none", ""):
                continue
            errs[e] += 1
    broad = [e for e in errs if OVERFLOW.search(e)]
    narrow = [e for e in errs if LIVE_PREDICATE.search(e)]
    print(f"  json files carrying an error field : {files}")
    print(f"  distinct error strings             : {len(errs)}")
    print(f"  overflow-shaped, BROAD pattern     : {len(broad)}")
    print(f"  overflow-shaped, LIVE predicate    : {len(narrow)}")
    if not broad:
        print("  so the narrow phrase is UNTESTED, not refuted: no dispatch in")
        print("  the archive has ever hit a context limit. The detector is left")
        print("  alone rather than widened on no evidence.")
    else:
        print("  the LIVE predicate misses these overflow-shaped errors:")
        for e in broad:
            if not LIVE_PREDICATE.search(e):
                print(f"      x{errs[e]:<4} {e[:110]}")

    print("\nTHE 3 OPTIONS, AND WHAT EACH WOULD COST")
    print("  1. DECAY toward the recent window: changes the ceiling on every")
    print("     paid seat at once, and needs a decay rate with a measurement")
    print("     behind it rather than a chosen constant.")
    print("  2. BOUND BY A MEASURED FAILURE: requires changing the CONSUMER as")
    print("     well as the recorder, because a failure is currently ignored")
    print("     whenever a success exists. Nothing would change until a")
    print("     dispatch actually overflows, and none ever has.")
    print("  3. RENAME IT a proven floor and stop calling it a capacity: costs")
    print("     no routing change at all, and leaves the overload detection he")
    print("     described unimplemented.")
    print("\n  THE CHOICE IS HIS. This script changes nothing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
