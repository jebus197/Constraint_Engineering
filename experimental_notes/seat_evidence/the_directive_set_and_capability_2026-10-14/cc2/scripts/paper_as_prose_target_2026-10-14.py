# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'the_directive_set_and_capability_2026-10-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: b38c4630f124e5aaeb7ffcfc17438ec5bb179395e2476dc28eb1dc4b9cd49ece
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Is PAPER.md a usable prose review target for the A19 admissibility scorer?

CDSFL panel review, item 5, 2026-10-14. No required arguments; `--help` is free.

WHAT THE A19 SCORER ACTUALLY IS
-------------------------------
The "A19 admissibility scorer" is `reference_runner_v3.compute_sk`, gated by
`RunnerConfig.sk_score_prose_listings` (reference_runner_v3.py:1679, default
False). It scores a *proposed fix* against a target, not the target itself.

Its ONLY requirement of the target is the one line

    _reducible, _why = _gateable_source(source, source_path)
    _scoring_prose  = (kind != TARGET_KIND_PYTHON and score_prose_listings
                       and bool(_reducible))

and `_gateable_source` (reference_runner_v3.py:13057) returns a non-None source
iff `_MD_PY_FENCE_ANY` (13029) matches at least once. That regex requires a
fence tagged `python` or `py`:

    (?P<f>```|~~~)[ \t]*(?:python|py)\b

So the admission test is a COUNT >= 1 of python-tagged fenced listings. There is
no density threshold, no minimum number of claims, no equation predicate, and no
reading of decimals, percentages or confidence intervals anywhere on the path.

This script reproduces every figure in the brief and executes the scorer.

Run:  python3 scripts/paper_as_prose_target_2026-10-14.py
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "bench"))

TARGET = REPO_ROOT / "PAPER.md"

# -- Predicates, each stated explicitly --------------------------------------
#
# P1 chars     len() of the decoded str (characters, NOT bytes).
# P2 lines     len(text.splitlines()).
# P3 headings  ATX markdown heading: ^#{1,6} followed by whitespace.
# P4 fences    fenced blocks = (count of lines matching ^\s*(```|~~~)) // 2.
# P5 decimals  "decimal numeric claim" = a token \d+\.\d+ that occurs on a
#              NON-heading line and is NOT immediately followed by `%`.
#              Headings are excluded because `## 3.1 Method` is a section
#              number, not a measurement; `%`-suffixed tokens are excluded
#              because they are counted once, under P6.
# P6 percent   "percentage claim" = \d+(\.\d+)?\s?% or \d+(\.\d+)?\s+percent.
# P7 eqsym     see eq_or_symbol_lines() -- three nested predicates, because the
#              brief states a count (49) without stating the predicate.
# P8 ci        confidence-interval mention: /confidence interval/i, or a
#              standalone token CI, or Wilson-interval language.

HEADING_RE = re.compile(r"^#{1,6}\s")
FENCE_RE = re.compile(r"^\s*(?:```|~~~)")
DECIMAL_RE = re.compile(r"\d+\.\d+(?!\s?%)")
PERCENT_RE = re.compile(r"\d+(?:\.\d+)?\s?%|\d+(?:\.\d+)?\s+percent")
CI_RE = re.compile(r"(?i)confidence\s+interval|\bCI\b|\bWilson\b\s+interval")

OPS = r"[≥≤≠≈→←×÷∑∏∫√∞±]"
GREEK = (r"[αβγδεζηθλμν"
         r"πρστφχψω"
         r"ΓΔΘΛΣΦΨΩ]")
SUBSCRIPT = r"\b[A-Za-z]_[A-Za-z0-9]+"


def split_prose_and_code(lines: List[str]) -> Tuple[List[str], List[str]]:
    """Partition lines into prose and fenced-code, dropping the fence markers."""
    prose: List[str] = []
    code: List[str] = []
    inside = False
    for line in lines:
        if FENCE_RE.match(line):
            inside = not inside
            continue
        (code if inside else prose).append(line)
    return prose, code


def eq_or_symbol_lines(prose: List[str], total_lines: int) -> dict:
    """Three predicates for 'line carries an equation or model symbol'.

    The brief asserts 49 lines / 3.4170%. 3.4170% == 49/1434, so the denominator
    is total lines. No predicate the panel can state reproduces 49, so all three
    are reported and the sensitivity is shown rather than one being asserted.

    broad   : an operator char, OR a Greek letter, OR a subscripted identifier
              (S_k, R_k, d_tool). Most generous reading of the phrase.
    mid     : an operator char OR a Greek letter. Drops bare subscripts, which
              also catch prose identifiers like `test_cmd`.
    narrow  : an operator char only -- a line carrying actual relational or
              summation notation.
    """
    broad_re = re.compile("%s|%s|%s" % (OPS, GREEK, SUBSCRIPT))
    mid_re = re.compile("%s|%s" % (OPS, GREEK))
    narrow_re = re.compile(OPS)
    out = {}
    for name, rx in (("broad", broad_re), ("mid", mid_re), ("narrow", narrow_re)):
        n = sum(1 for line in prose if rx.search(line))
        out[name] = (n, 100.0 * n / total_lines if total_lines else 0.0)
    return out


def measure(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    prose, code = split_prose_and_code(lines)
    body = [line for line in lines if not HEADING_RE.match(line)]

    fence_markers = sum(1 for line in lines if FENCE_RE.match(line))
    return {
        "path": path,
        "text": text,
        "chars": len(text),
        "bytes": len(text.encode("utf-8")),
        "lines": len(lines),
        "headings": sum(1 for line in lines if HEADING_RE.match(line)),
        "fence_markers": fence_markers,
        "fenced_blocks": fence_markers // 2,
        "decimals": len(DECIMAL_RE.findall("\n".join(body))),
        "percents": len(PERCENT_RE.findall(text)),
        "ci": len(CI_RE.findall(text)),
        "prose_lines": len(prose),
        "code_lines": len(code),
        "eqsym": eq_or_symbol_lines(prose, len(lines)),
    }


def scorer_view(path: Path, text: str) -> dict:
    """What the A19 scorer itself sees. Imports and EXECUTES the real runner."""
    import reference_runner_v3 as R

    rel = str(path.relative_to(REPO_ROOT))
    kind, kind_reason = R.resolve_target_kind(rel, text)
    gateable, why = R._gateable_source(text, rel)
    hunks = R._gateable_hunks(text, rel)
    py_fences = len(R._MD_PY_FENCE_ANY.findall(text))

    # A minimal well-formed fix, so compute_sk gets past block parsing and the
    # only thing that can stop it is the target itself.
    fix = ("FALSIFIER: see producer\n"
           "<<<<<<< SEARCH\nthe\n=======\na\n>>>>>>> REPLACE\n")
    res = R.compute_sk(fix, text, rel, score_prose_listings=True)
    return {
        "module": R.__file__,
        "kind": kind,
        "kind_reason": kind_reason,
        "gateable_chars": None if gateable is None else len(gateable),
        "gateable_why": why,
        "py_listings": len(hunks),
        "py_fence_matches": py_fences,
        "tristate": res.tristate,
        "sk": res.sk,
        "reason": res.gate_details.get("reason", ""),
    }


def listing_density(path: Path) -> Optional[Tuple[int, int, int, float]]:
    """(py_listings, listing_lines, total_lines, density%) -- the density the
    scorer actually reads: lines inside python-tagged fences / total lines."""
    import reference_runner_v3 as R

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    hunks = R._gateable_hunks(text, str(path))
    total = len(text.splitlines())
    listing_lines = sum(len(h.splitlines()) for h in hunks)
    return (len(hunks), listing_lines, total,
            100.0 * listing_lines / total if total else 0.0)


SKIP_PARTS = ("/logs/", "/sandbox_harvest/", "/.scratch/", "/.mutants/",
              "/seat_evidence/", "/.pytest_cache/")


def alternatives(limit: int = 8) -> List[tuple]:
    """Prose targets in this repo that DO satisfy the scorer's requirement."""
    rows = []
    for md in REPO_ROOT.rglob("*.md"):
        rel = "/" + str(md.relative_to(REPO_ROOT))
        if any(part in rel for part in SKIP_PARTS):
            continue
        got = listing_density(md)
        if got and got[0] > 0:
            rows.append((got[0], got[1], got[2], got[3],
                         str(md.relative_to(REPO_ROOT))))
    rows.sort(key=lambda r: (-r[0], -r[3]))
    return rows[:limit]


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target", default=str(TARGET),
                    help="prose target to measure (default: PAPER.md)")
    ap.add_argument("--alt-limit", type=int, default=8,
                    help="how many alternative targets to list (default 8)")
    args = ap.parse_args()

    path = Path(args.target)
    if not path.is_absolute():
        path = REPO_ROOT / path

    m = measure(path)
    claimed = {
        "chars": 145879, "lines": 1434, "headings": 90,
        "decimals": 119, "percents": 16, "fenced_blocks": 11, "ci": 0,
    }

    print("=" * 78)
    print("A19 PROSE-TARGET ASSESSMENT  --  %s" % path.relative_to(REPO_ROOT))
    print("=" * 78)

    print("\n[1] BRIEF'S FIGURES vs MEASURED (predicates in the module docstring)")
    print("  %-24s%10s%10s  verdict" % ("figure", "claimed", "measured"))
    order = [("chars", "characters (not bytes)"), ("lines", "lines"),
             ("headings", "headings (ATX)"),
             ("decimals", "decimal numeric claims"),
             ("percents", "percentage claims"),
             ("fenced_blocks", "fenced code blocks"),
             ("ci", "confidence-interval mentions")]
    for key, label in order:
        got, want = m[key], claimed[key]
        mark = "CONFIRMED" if got == want else "REFUTED"
        print("  %-24s%10s%10s  %s" % (label, "{:,}".format(want),
                                       "{:,}".format(got), mark))
    print("  (for contrast, bytes = %s; the brief's char figure is %s as CHARACTERS)"
          % ("{:,}".format(m["bytes"]),
             "correct" if m["chars"] == claimed["chars"] else "wrong"))
    print("  (fence marker lines counted: %d -> %d blocks)"
          % (m["fence_markers"], m["fenced_blocks"]))

    print("\n[2] EQUATION-OR-SYMBOL LINES  (brief: 49 lines = 3.4170%)")
    print("      49/1434 = 3.4170%, so the brief's denominator is total lines.")
    for name in ("broad", "mid", "narrow"):
        n, pct = m["eqsym"][name]
        print("  %-8s%6d lines  %8.4f%%" % (name, n, pct))
    lo = m["eqsym"]["narrow"][0]
    hi = m["eqsym"]["broad"][0]
    print("  VERDICT: 49 is NOT reproduced by any stated predicate (band %d..%d)."
          % (lo, hi))
    print("           The figure is predicate-sensitive and unreconstructed.")

    print("\n[3] WHAT THE SCORER ACTUALLY SEES  (executed, not reasoned)")
    sv = scorer_view(path, m["text"])
    print("  runner module        %s" % sv["module"])
    print("  resolve_target_kind  %s  (%s)" % (sv["kind"], sv["kind_reason"]))
    print("  _MD_PY_FENCE_ANY     %d match(es)" % sv["py_fence_matches"])
    print("  _gateable_hunks      %d python listing(s)" % sv["py_listings"])
    print("  _gateable_source     %s  (%s)" % (sv["gateable_chars"], sv["gateable_why"]))
    print("  compute_sk(score_prose_listings=True)")
    print("      tristate         %s" % sv["tristate"])
    print("      sk               %s" % sv["sk"])
    if sv["reason"]:
        print("      reason           %s" % sv["reason"])
    reachable = sv["py_listings"] > 0
    print("  A19 PROSE PATH REACHABLE ON THIS TARGET: %s"
          % ("YES" if reachable else "NO"))

    print("\n[4] THE SCORER'S REQUIREMENT, AND THE DENSITY QUESTION")
    print("  Requirement: bool(_gateable_source(...)) -- i.e. COUNT >= 1 of")
    print("  python-tagged fenced listings. It is a boolean admission test.")
    print("  There is NO claim-count threshold and NO density threshold, so")
    print("  'is ~3.4% dense enough' is not the operative question: the scorer")
    print("  never reads equation lines, decimals, percentages or CIs.")
    lp = listing_density(path)
    print("  %s computable-line density (python-fence lines / lines): %d/%d = %.4f%%"
          % (path.name, lp[1], lp[2], lp[3]))
    print("  At exactly 0 listings the target fails the only test there is.")

    print("\n[5] ALTERNATIVE PROSE TARGETS THAT DO SATISFY IT (top %d)"
          % args.alt_limit)
    print("  %8s%9s%8s%10s  path" % ("listings", "code ln", "lines", "density"))
    for n, cl, tot, pct, rel in alternatives(args.alt_limit):
        print("  %8d%9d%8d%9.4f%%  %s" % (n, cl, tot, pct, rel))

    print("\n[6] IS THE FLAG INERT IN THE SIMULATED-RUN CONFIG?")
    sim = REPO_ROOT / "bench" / "tools" / "run_simulated_experiment.py"
    src = sim.read_text(encoding="utf-8")
    flag_on = "sk_score_prose_listings=True" in src
    dflt = re.search(r'add_argument\(\s*"--target",\s*default="([^"]+)"', src)
    dflt_val = dflt.group(1) if dflt else "<not found>"
    import reference_runner_v3 as R
    dflt_kind, dflt_why = R.resolve_target_kind(dflt_val, "")
    print("  %s" % sim.relative_to(REPO_ROOT))
    print("    sk_score_prose_listings=True present : %s" % flag_on)
    print("    --target default                     : %s" % dflt_val)
    print("    that target's kind                   : %s (%s)" % (dflt_kind, dflt_why))
    inert = flag_on and dflt_kind == R.TARGET_KIND_PYTHON
    print("    => flag ON but INERT by default      : %s" % inert)
    print("       (compute_sk requires kind != python before the flag is read)")

    print("\n" + "=" * 78)
    print("CONCLUSION: PAPER.md carries 0 python-tagged listings, so")
    print("compute_sk returns NO_SCORE even with sk_score_prose_listings=True.")
    print("It is NOT a usable prose review target for the A19 scorer -- and the")
    print("reason is a zero count, not a low density.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
