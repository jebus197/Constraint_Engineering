#!/usr/bin/env python3
"""Does every STATED Wilson interval agree with the STATED count beside it?

WHY THIS EXISTS (2026-09-07). `reference_runner_v3.sk_threshold_shadow` carried
"s_star reads 0.0 in 3181 of 3181 archived records, Wilson [99.88%, 100.00%]".
The count was wrong -- 3181 is the line count of the Experiment 12 artefact,
pasted where the gate count belonged; the true figure is 3816, stated correctly
at 5 other sites. A panel seat raised it and CC1 refuted the seat, wrongly.

WHAT THIS CANNOT CATCH, STATED FIRST BECAUSE THE FIRST DRAFT OF THIS FILE GOT
IT WRONG. It cannot catch the defect above. [99.88%, 100.00%] is EXACTLY the
Wilson interval for 3181 of 3181: the sentence was internally consistent and
merely described the wrong archive. Run against the original defect this script
printed "Every stated interval agrees" and exited 0. A first draft claimed the
defect "was legible in the sentence that carried it". It was not, and that
claim was the `execute-do-not-grep` failure -- a check that asserts a claim
against itself -- committed inside the tool written to prevent it. Only
re-measuring the archive finds a wrong-but-coherent count; see
`scripts/measure_sk_threshold_gate_fire_rate.py` and the test that pins the
prose to it, `bench/tests/test_stated_gate_count_matches_measurement_2026-09-07.py`.
(The cc2 seat reported that test as never committed. It was committed -- but
AFTER `panel_sandbox.build` took the seat's copy, so it was genuinely absent
from the tree cc2 could see. A seat's "file not found" is evidence about the
copy, not about the repository, whenever the tree is edited while a panel runs.
It should not have been: the standing rule is not to edit during a live panel.)

WHAT IT DOES CATCH: the HALF-DONE CORRECTION, in both directions -- but the
upward direction needed a second mechanism, and an earlier draft claimed to
catch it while structurally could not.

A Wilson interval is a function of k and n -- at k = n the lower bound is
n/(n + z**2) in closed form -- so correcting a count and leaving its interval
behind produces a pair that is arithmetically impossible. The catch, found by
the cc2 seat on 2026-09-07: n/(n + z**2) is STRICTLY INCREASING in n, so a
stale interval left behind by an UPWARD correction is always NARROWER than the
truth at the lower bound and therefore always WIDER as a stated interval --
which the "wider is conservative" rule below then forgave. Every upward
correction at k = n was routed to `loose` and exited 0. The single defect class
this file was written for was the one class it could never fail on, and its own
docstring asserted the opposite.

The repair is `_n_that_fits`: at k = n the stated lower bound names a BAND of n
that could have produced it, and if the stated n falls outside that band the
pair is STALE rather than loose, whichever side it is wider on. That function
already existed and was consulted only on the failing path.

So the 2 instruments are COMPLEMENTARY, not alternatives: this one proves a
claim is internally coherent, the measurement test proves it is true. A claim
needs both, and neither implies the other.

Not a style check. It reports only ARITHMETIC disagreement, and only when both
halves are present -- a count with no interval is out of scope, and so is an
interval with no count. Exit 1 on any disagreement.
"""
from __future__ import annotations
import argparse, math, pathlib, re, sys
from typing import List, Optional, Tuple

Z = 1.959963984540054  # 97.5th percentile of the standard normal

def wilson(k: int, n: int, z: float = Z) -> Tuple[float, float]:
    """Wilson score interval, as a fraction of 1. Closed form, no scipy needed."""
    if n <= 0:
        raise ValueError("n must be positive")
    p = k / n
    d = 1.0 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)

# "3816 of 3816", "0 of 3816", "282 of 711" -- commas tolerated in either half.
_FRAC = re.compile(r"(?<![\d.])(\d[\d,]*)\s+of\s+(\d[\d,]*)(?![\d.])")
# "[99.88%, 100.00%]" or "[0.0000, 0.0010]" -- percent sign optional but must
# be consistent across the pair, since a bare pair may be a fraction of 1.
_CI = re.compile(r"\[\s*(\d+(?:\.\d+)?)\s*(%?)\s*,\s*(\d+(?:\.\d+)?)\s*(%?)\s*\]")

# PROXIMITY IS NOT ATTRIBUTION -- the lesson that cost the most drafts here.
# An interval near a count very often belongs to a DIFFERENT statistic:
#   "86 of 93 (92.5%, Cohen's kappa 0.837 [0.721, 0.953])"   <- kappa's interval
#   "9 of 12 critical rows. ... Evidence provenance. 88.4% [80.4%, 93.4%]"
# Both were reported as defects by an earlier draft. Neither is one. Measured
# across the repo, a genuine pair carries an explicit CI marker within ~30 chars
# ("..., Wilson ["), while every false positive either has NO marker or a gap of
# 140+ chars reaching into the next sentence. So attribution must be EXPLICIT.
GAP = 60                       # max chars between the count and its interval
MARKER = re.compile(r"Wilson|\bCI\b|confidence\s+interval", re.I)
# Enough tail to FIND an interval and then judge the gap; GAP does the deciding.
WINDOW = GAP + 80

# PAIRING IS THE HARD PART, AND THE FIRST DRAFT GOT IT WRONG 3 WAYS.
#
# 1. It paired a fraction with the NEXT interval in range even when ANOTHER
#    fraction sat between them, so "714 of 2286" on one line stole the interval
#    belonging to "1375 of 2286" on the next and was reported as a defect. The
#    interval directly below IS correct for 1375. Rule now: an intervening
#    fraction breaks the pairing, because the nearer claim owns the interval.
# 2. It read an unsigned "[52.4, 85.7]" as a fraction of 1 and reported a
#    disagreement against [0.5242, 0.8572] -- the SAME numbers in percent. A
#    proportion cannot exceed 1, so a bound above 1 is percent, unsigned or not.
# 3. It scanned itself and flagged the worked examples in its own docstring.
#
# All 3 were false positives, and a checker that cries wolf is a checker that
# gets muted. Precision is load-bearing for an instrument nobody is paid to read.

_NUM = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)(?![\w])")
_CONF_LEVELS = (90.0, 95.0, 98.0, 99.0)

def _bridge_carries_another_statistic(bridge: str, k: int, n: int) -> bool:
    """Does a DIFFERENT statistic sit between the count and the interval?

    THE LAST AND SUBTLEST FALSE-POSITIVE CLASS. Requiring a CI marker is not
    enough, because the marker often belongs to another statistic entirely:

        "truncated criticals 81 of 165 (49%) ... AUC 0.976, 95% CI [0.939, 0.998]"
        "agreed ... on 86 of 93 (92.5%, Cohen's kappa 0.837, 95% CI [0.721, 0.953])"

    Both carry "95% CI" within 40 chars, and in both the interval belongs to
    the AUC or the kappa, not to the count. An earlier draft reported them as
    defects. They are not.

    The signal is arithmetic, so no vocabulary of statistic names is needed and
    none can be forgotten: the ONLY numbers legitimately standing between a
    count and its own interval are a restatement of k/n and the confidence
    level. Anything else -- 0.976, 0.837 -- is another statistic claiming the
    interval, and 1 such number is enough to break the attribution.
    """
    pct = 100.0 * k / n
    for tok in _NUM.findall(bridge):
        v = float(tok)
        if any(abs(v - c) < 1e-9 for c in _CONF_LEVELS):
            continue                       # "95% CI"
        if abs(v - pct) <= 0.15 or abs(v - k / n) <= 0.002:
            continue                       # a restatement of the count itself
        if v in (float(k), float(n)):
            continue                       # the count restated literally
        if "." not in tok:
            # A BARE INTEGER DISARMED THE WHOLE CHECK. cc2, 2026-09-07: the
            # sentence "3816 of 3816 across 70 files, Wilson 95% CI [...]" was
            # silently skipped, because 70 -- the real file count from this very
            # archive -- was read as another statistic claiming the interval.
            # The natural sentence an author here would write defeated the tool.
            # Competing statistics in this corpus are decimals (kappa 0.837,
            # AUC 0.976); bare integers are counts, dates and file tallies. So
            # integers no longer break attribution and decimals still do.
            continue
        return True
    return False

class Finding:
    def __init__(self, path, line, k, n, lo, hi, elo, ehi, pct, lo_s):
        self.path, self.line, self.k, self.n = path, line, k, n
        self.lo, self.hi, self.elo, self.ehi, self.pct = lo, hi, elo, ehi, pct
        self.lo_s = lo_s

def _tol(text: str) -> float:
    """Half a unit in the last decimal place stated, so a rounded bound passes."""
    dp = len(text.split(".")[1]) if "." in text else 0
    return 0.5 * 10 ** (-dp)

def scan_text(path: str, text: str, loose: Optional[List['Finding']] = None) -> List[Finding]:
    out: List[Finding] = []
    loose = [] if loose is None else loose
    for m in _FRAC.finditer(text):
        try:
            k = int(m.group(1).replace(",", "")); n = int(m.group(2).replace(",", ""))
        except ValueError:
            continue
        if n == 0 or k > n:
            continue  # "1 of 3" prose, or a ratio that isn't a proportion
        tail = text[m.end(): m.end() + WINDOW]
        nxt = _FRAC.search(tail)          # a nearer claim owns the interval
        if nxt:
            tail = tail[: nxt.start()]
        ci = _CI.search(tail)
        if not ci:
            continue
        # AN OPT-OUT IS NECESSARY, because a test that PROVES this checker
        # works must contain a deliberately wrong pair as fixture data, and a
        # checker that fails on its own test fixtures cannot be run in a suite.
        # Marker on the same line or the line before, as linters conventionally
        # do. It must be explicit and greppable -- never a silent path-based
        # exemption, which would let real defects hide in test files.
        _ls = text.rfind("\n", 0, m.start()) + 1
        _le = text.find("\n", m.end())
        _prev0 = text.rfind("\n", 0, _ls - 1) + 1 if _ls else 0
        _ctx = text[_prev0: _le if _le != -1 else len(text)]
        if "wilson-lint: expected-defect" in _ctx:
            continue
        bridge = tail[: ci.start()]
        if len(bridge) > GAP or not MARKER.search(bridge):
            continue                    # the interval is not attributable here
        if _bridge_carries_another_statistic(bridge, k, n):
            continue
        lo_s, lo_p, hi_s, hi_p = ci.groups()
        if lo_p != hi_p:
            continue  # mixed units: not a well-formed pair, don't guess
        lo, hi = float(lo_s), float(hi_s)
        # A proportion cannot exceed 1, so a bound above 1 is percent whether or
        # not the sign was typed. Only an all-below-1 unsigned pair is ambiguous,
        # and there the fraction reading is the literal one.
        pct = (lo_p == "%") or lo > 1.0 or hi > 1.0
        # `[0.0, 1.0]` is the unit interval -- a clamp range, a domain, a
        # probability's support. It is never a reported CI (only n = 0 yields
        # it) and it appears beside counts all over this codebase. Skip it.
        if (lo, hi) == (0.0, 1.0) and not pct:
            continue
        elo, ehi = wilson(k, n)
        if pct:
            elo, ehi = elo * 100.0, ehi * 100.0
        if abs(lo - elo) <= _tol(lo_s) and abs(hi - ehi) <= _tol(hi_s):
            continue
        # A STATED INTERVAL WIDER THAN THE COMPUTED ONE IS NOT A DEFECT.
        # Rounding a bound outward is the conservative direction: it can only
        # weaken the claim, never overstate it. "[58.1%, 62.2%]" for a computed
        # [58.1263%, 62.1371%] is a correct interval reported loosely. Flagging
        # it trains the reader to ignore this tool. NARROWING is the defect --
        # it asserts more precision than the data supports -- and so is a shift.
        if lo <= elo + _tol(lo_s) and hi >= ehi - _tol(hi_s):
            line = text[: m.start()].count("\n") + 1
            f = Finding(path, line, k, n, lo, hi, elo, ehi, pct, lo_s)
            # WIDER, BUT IS IT STALE? At k = n the stated lower bound names the
            # band of n that could have produced it. A stated n outside that
            # band is not a conservative rounding -- it is an interval left
            # behind by a corrected count. Without this, an upward correction
            # NEVER fails, because n/(n+z**2) rises with n and the stale bound
            # is therefore always the wider one. (cc2, 2026-09-07.)
            band = _n_that_fits(lo_s, k == n, pct)
            if band is not None and not (band[0] <= n <= band[1]):
                out.append(f)
                continue
            loose.append(f)
            continue
        line = text[: m.start()].count("\n") + 1
        out.append(Finding(path, line, k, n, lo, hi, elo, ehi, pct, lo_s))
    return out

def _n_that_fits(lo_s: str, k_over_n_is_one: bool, pct: bool) -> Optional[Tuple[int, int]]:
    """If k == n, invert n/(n + z**2) to bracket the n the interval DOES fit.

    A RANGE, not a point. The stated bound is rounded, so it is consistent with
    a band of n. Reporting one integer here would invent precision the printed
    bound cannot carry -- an early draft did exactly that, naming n = 3197 for a
    true 3181. The band is honest and still localises the mistake.
    """
    if not k_over_n_is_one:
        return None
    t = _tol(lo_s)
    out = []
    for edge in (float(lo_s) - t, float(lo_s) + t):
        frac = edge / 100.0 if pct else edge
        if not 0.0 < frac < 1.0:
            return None
        out.append(int(round(frac * Z * Z / (1.0 - frac))))
    lo_n, hi_n = min(out), max(out)
    return (lo_n, hi_n) if lo_n > 0 else None

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", default=None,
                    help="files or dirs to scan (default: the repo)")
    ap.add_argument("--ext", default=".py,.md,.txt,.sh",
                    help="comma-separated suffixes to scan")
    args = ap.parse_args()

    exts = tuple(e if e.startswith(".") else "." + e for e in args.ext.split(","))
    roots = [pathlib.Path(p) for p in (args.paths or ["."])]
    files: List[pathlib.Path] = []
    for r in roots:
        if r.is_file():
            files.append(r)
        elif r.is_dir():
            files += [p for p in r.rglob("*")
                      if p.is_file() and p.suffix in exts
                      and ".git" not in p.parts and "node_modules" not in p.parts]
    # This file's own docstring carries worked examples OF the defect. Scanning
    # them is a guaranteed false positive, so skip self unless asked by name.
    me = pathlib.Path(__file__).resolve()
    if not any(pathlib.Path(x).resolve() == me for x in (args.paths or [])):
        files = [f for f in files if f.resolve() != me]

    findings: List[Finding] = []
    loose: List[Finding] = []
    scanned = 0
    for p in sorted(set(files)):
        try:
            findings += scan_text(str(p), p.read_text(errors="replace"), loose)
            scanned += 1
        except OSError:
            continue

    print(f"Wilson interval consistency -- {scanned} files scanned, "
          f"{len(findings)} disagreement(s)\n")
    for f in findings:
        mark = "%" if f.pct else ""
        print(f"{f.path}:{f.line}")
        print(f"    states   : {f.k} of {f.n}, [{f.lo}{mark}, {f.hi}{mark}]")
        print(f"    Wilson   : [{f.elo:.4f}{mark}, {f.ehi:.4f}{mark}]  for {f.k} of {f.n}")
        alt = _n_that_fits(f.lo_s, f.k == f.n, f.pct)
        if alt is not None and not (alt[0] <= f.n <= alt[1]):
            print(f"    that interval is what n in [{alt[0]}, {alt[1]}] produces, not {f.n}")
        print()
    if loose:
        # WIDER THAN COMPUTED: correct but loose, so a note and NOT a failure.
        # This is where a half-done correction surfaces -- fixing 3181 -> 3816
        # and leaving [99.88%, 100.00%] lands here, since that interval still
        # CONTAINS the truth. Worth seeing, not worth failing a suite over.
        print(f"{len(loose)} interval(s) wider than computed -- valid but loose:")
        for f in loose:
            mark = "%" if f.pct else ""
            print(f"  {f.path}:{f.line}  states [{f.lo}{mark}, {f.hi}{mark}], "
                  f"computed [{f.elo:.4f}{mark}, {f.ehi:.4f}{mark}] for {f.k} of {f.n}")
        print()
    if findings:
        print("A count and its interval disagree. Correct BOTH -- fixing one "
              "leaves the pair still lying.")
        return 1
    print("Every stated interval agrees with the count beside it.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
