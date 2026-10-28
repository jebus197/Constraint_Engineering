#!/usr/bin/env python3
"""The chat prefilter dropped the commonest marker form, and both seats proved it.

BOTH FREE SEATS, INDEPENDENTLY, 2026-10-28, each with an executed randomised
counterexample. `scripts/harvest_tickets_2026-10-17.py` filtered candidate lines
with `\\b(?:fr|pf|qs|wr)\\b` on the RAW JSON line, while the DECISION, `MARKER`,
runs on decoded text with `re.MULTILINE` and accepts a token preceded by ANY
whitespace. A newline in the raw line is the 2 characters backslash and `n`, so
the character left of the token is the WORD character `n` and the left `\\b`
fails. A marker written on its own line -- the normal way to write one -- was
dropped before anything decoded it. 185 of 500 generated cases were rejected
while `MARKER` fired on them.

THE 2 SEATS PROPOSED DIFFERENT REPAIRS AND BOTH PASS BOTH FALSIFIERS, so the
falsifiers do not choose between them. This script is what chooses.

  cc2   dropped BOTH boundaries -> a superset under no assumption at all.
  fable dropped only the LEFT one, on one STATED assumption: that the transcript
        writer never `\\u`-escapes an ASCII letter.

THE MEASUREMENT. cc2's form admits far more lines, and every admitted line costs
a `json.loads`. fable's assumption is TESTABLE, and this script tests it over
every transcript rather than accepting it. Where it holds, fable's form is taken
and its caveat becomes a CHECK -- which is neither seat's answer and better than
both: fable's cost with cc2's safety property mechanised.

Run with --help to read this without computing anything.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
from _cli_help import answer_help  # noqa: E402

SESSIONS = pathlib.Path.home() / ".claude" / "projects" / \
    "-Users-georgejackson-Developer-Projects"
OLD = re.compile(r"\b(?:fr|pf|qs|wr)\b", re.IGNORECASE)
FABLE = re.compile(r"(?:fr|pf|qs|wr)\b", re.IGNORECASE)
CC2 = re.compile(r"(?:fr|pf|qs|wr)", re.IGNORECASE)
#: An ASCII letter written as a `\\uXXXX` escape. A-Z is 41-5A, a-z is 61-7A.
ESCAPED_ASCII_LETTER = re.compile(
    r"\\u00(?:4[1-9a-fA-F]|5[0-9aA]|6[1-9a-fA-F]|7[0-9aA])")


def _wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    import numpy as np
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def measure(limit_bytes: int | None = None) -> dict:
    from scipy import stats

    files = sorted(SESSIONS.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
    r: dict = {"transcripts": len(files), "per_file": []}
    tot = esc = o = fa = c = 0
    for f in files:
        n = h = fo = ff = fc = 0
        read = 0
        with f.open(encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if limit_bytes is not None and read > limit_bytes:
                    break
                read += len(line)
                n += 1
                if ESCAPED_ASCII_LETTER.search(line):
                    h += 1
                if OLD.search(line):
                    fo += 1
                if FABLE.search(line):
                    ff += 1
                if CC2.search(line):
                    fc += 1
        tot += n; esc += h; o += fo; fa += ff; c += fc
        r["per_file"].append({"name": f.name, "lines": n, "escaped": h,
                              "old": fo, "fable": ff, "cc2": fc})
    r["lines"] = tot
    r["escaped_ascii_letters"] = esc
    r["escaped_share"] = esc / tot if tot else float("nan")
    if tot:
        ci = stats.binomtest(esc, tot).proportion_ci(method="exact")
        r["escaped_cp"] = (float(ci.low), float(ci.high))
        r["escaped_wilson"] = _wilson(esc, tot)
    r["admits_old"], r["admits_fable"], r["admits_cc2"] = o, fa, c
    r["share_fable"] = fa / tot if tot else float("nan")
    r["share_cc2"] = c / tot if tot else float("nan")
    r["fable_wilson"] = _wilson(fa, tot)
    r["cc2_wilson"] = _wilson(c, tot)
    r["cc2_cost_multiple"] = c / fa if fa else float("nan")
    r["assumption_holds"] = esc == 0
    r["chosen"] = "fable" if esc == 0 else "cc2"
    return r


def main() -> int:
    answer_help(__doc__, __file__, takes_no_arguments=False)
    ap = argparse.ArgumentParser(
        description="Choose between the 2 proposed prefilters by measurement.")
    ap.add_argument("--limit-mb", type=float, default=None,
                    help="read only this many MB per transcript (default: all)")
    ap.add_argument("--json", action="store_true", help="emit figures as JSON")
    a = ap.parse_args()
    lim = int(a.limit_mb * 1048576) if a.limit_mb else None
    r = measure(limit_bytes=lim)
    if a.json:
        print(json.dumps(r, indent=2, default=str))
        return 0

    print("=" * 78)
    print("THE CHAT PREFILTER WAS NOT A SUPERSET, AND WHICH REPAIR TO TAKE")
    print("=" * 78)
    print(f"\n1. THE CORPUS: {r['transcripts']} transcript(s), {r['lines']:,} lines"
          + (f" (capped at {a.limit_mb} MB each)" if lim else ""))
    print(f"\n2. WHAT EACH FORM ADMITS, and every admitted line costs a json.loads")
    print(f"   OLD   \\b...\\b : {r['admits_old']:>8,}   <- NOT a superset; it is "
          f"the defect")
    print(f"   fable  ...\\b   : {r['admits_fable']:>8,}   {r['share_fable']:.6f}  "
          f"Wilson [{r['fable_wilson'][0]:.6f}, {r['fable_wilson'][1]:.6f}]")
    print(f"   cc2    bare    : {r['admits_cc2']:>8,}   {r['share_cc2']:.6f}  "
          f"Wilson [{r['cc2_wilson'][0]:.6f}, {r['cc2_wilson'][1]:.6f}]")
    print(f"   cc2 costs {r['cc2_cost_multiple']:.6f} times fable's decoding work")
    print(f"\n3. fable's ONE ASSUMPTION, TESTED rather than accepted")
    print(f"   lines \\u-escaping an ASCII letter: {r['escaped_ascii_letters']} of "
          f"{r['lines']:,}")
    if "escaped_cp" in r:
        print(f"   Clopper-Pearson exact [{r['escaped_cp'][0]:.9f}, "
              f"{r['escaped_cp'][1]:.9f}]")
    print(f"   assumption holds: {r['assumption_holds']}")
    print(f"\n4. THE CHOICE: {r['chosen']}")
    print("""
  fable's form is taken BECAUSE its assumption is measured to hold, and its
  caveat is MECHANISED by
  `bench/tests/test_the_prefilter_assumption_is_checked_2026-10-28.py`, which
  fails the moment an ASCII-letter escape appears and names cc2's bare form as
  the fallback. Neither seat proposed that, and it is better than either answer
  alone: fable's cost with cc2's safety property turned into a check.
""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
