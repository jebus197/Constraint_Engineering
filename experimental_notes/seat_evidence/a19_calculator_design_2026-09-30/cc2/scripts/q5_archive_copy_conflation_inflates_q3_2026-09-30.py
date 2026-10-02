# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'a19_calculator_design_2026-09-30', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: ece69aea16fb645f019e3df4829e91d67402e5e29b39c5cacebe1f60231aad3d
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Q5 + Q3 - the archive-copy conflation, measured ON A LIVE MEASUREMENT.

Run from the repository root:

    python3 scripts/q5_archive_copy_conflation_inflates_q3_2026-09-30.py

Fact 8 of the brief says copies of archive artefacts live INSIDE the archive
namespace, and that 3 mechanisms were bitten by it. This script shows a FOURTH:
the e1_efficacy false-admission count that Q3 turns on. It computes the same
proportion four ways -- raw, path-filtered, content-deduplicated, and both --
and reports the inflation.

It then states the remedy candidates and the cost of each, measured.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

FIX_INEFFECTIVE = "FIX_DOES_NOT_CURE_ITS_OWN_FALSIFIER"
FIX_CURES = "FIX_CURES_ITS_OWN_FALSIFIER"

#: The single shared predicate this script proposes. One definition, and every
#: consumer imports it rather than re-deriving a glob.
COPY_MARKERS = ("sandbox_harvest", "attempt-", "/files/", "unextracted_sandbox")


def is_archive_copy(path: Path, root: Path) -> bool:
    """True iff `path` is a COPY of an artefact, not the artefact itself.

    The one predicate. A copy is anything reached through a harvest namespace:
    `<run>/sandbox_harvest/<seat>/attempt-N/files/...`. Nesting means a plain
    depth rule cannot decide it and a glob cannot either -- the copy's tail is
    byte-identical to the original's tail.
    """
    rel = str(path.relative_to(root)) if path.is_absolute() else str(path)
    return any(m in rel for m in COPY_MARKERS)


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    z = 1.959963984540054
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def harvest(logs: Path):
    """Yield (path, content_sha, outcome, tristate) for every e1-bearing entry."""
    for p in sorted(logs.rglob("*.json")):
        try:
            raw = p.read_bytes()
            d = json.loads(raw.decode("utf-8", "replace"))
        except Exception:
            continue
        sha = hashlib.sha256(raw).hexdigest()
        stack = [d]
        idx = 0
        while stack:
            x = stack.pop()
            if isinstance(x, dict):
                if "fix_efficacy" in x and "sk_result" in x:
                    out = (x.get("fix_efficacy") or {}).get("outcome")
                    tri = (x.get("sk_result") or {}).get("tristate")
                    cid = (x.get("canonical_id") or x.get("id")
                           or x.get("finding_id") or f"#{idx}")
                    idx += 1
                    yield p, sha, cid, out, tri
                stack.extend(x.values())
            elif isinstance(x, list):
                stack.extend(x)


def main() -> int:
    logs = REPO / "bench" / "logs"
    rows = list(harvest(logs))
    print("=" * 78)
    print("Q5/Q3  THE ARCHIVE-COPY CONFLATION, MEASURED ON A LIVE MEASUREMENT")
    print("=" * 78)
    print()
    print(f"e1-bearing archive entries found under bench/logs : {len(rows)}")

    def tally(subset, label):
        ineff = [r for r in subset if r[3] == FIX_INEFFECTIVE]
        adm = [r for r in ineff if r[4] == "ADMISSIBLE"]
        lo, hi = wilson(len(adm), len(ineff)) if ineff else (0.0, 1.0)
        print(f"  {label:<34} measured-ineffective = {len(ineff):>5}   "
              f"of which ADMISSIBLE = {len(adm):>5}   "
              f"Wilson [{lo*100:.4f}%, {hi*100:.4f}%]")
        return len(ineff), len(adm)

    print()
    print("THE SAME PROPORTION, FOUR WAYS")
    raw_n, raw_k = tally(rows, "raw (every path, every entry)")

    path_rows = [r for r in rows if not is_archive_copy(r[0], REPO)]
    path_n, path_k = tally(path_rows, "path-filtered (shared predicate)")

    seen: set = set()
    dedup_rows = []
    for r in rows:
        key = (r[1], r[2], r[3], r[4])       # file sha + finding id + verdicts
        if key in seen:
            continue
        seen.add(key)
        dedup_rows.append(r)
    ded_n, ded_k = tally(dedup_rows, "content-deduplicated (sha+id)")

    both = [r for r in dedup_rows if not is_archive_copy(r[0], REPO)]
    both_n, both_k = tally(both, "both")

    print()
    infl = (raw_n / path_n - 1) * 100 if path_n else float("nan")
    infl2 = (raw_n / both_n - 1) * 100 if both_n else float("nan")
    print(f"INFLATION of the denominator by archive copies:")
    print(f"  raw vs path-filtered : {raw_n} vs {path_n}  = {infl:.4f}% inflated")
    print(f"  raw vs both          : {raw_n} vs {both_n}  = {infl2:.4f}% inflated")
    print()
    print("WHAT SURVIVES THE FILTER — this is the number Q3 turns on:")
    print(f"  fixes MEASURED not to cure their own falsifier, ADMITTED anyway:")
    print(f"     {both_k} of {both_n}")
    lo, hi = wilson(both_k, both_n) if both_n else (0.0, 1.0)
    print(f"     Wilson 95% [{lo*100:.4f}%, {hi*100:.4f}%]")
    try:
        from statsmodels.stats.proportion import proportion_confint
        s = proportion_confint(both_k, both_n, method="wilson")
        print(f"     statsmodels (2nd tool) [{s[0]*100:.4f}%, {s[1]*100:.4f}%]")
    except Exception as e:
        print(f"     statsmodels unavailable: {e}")

    # Control: the conflation must NOT change the PROPORTION if the copies are
    # faithful duplicates. If it does, the copies are not duplicates and the
    # remedy has to be stronger than dedup.
    print()
    print("CONTROL — does filtering change the PROPORTION as well as the count?")
    pr_raw = raw_k / raw_n if raw_n else float("nan")
    pr_both = both_k / both_n if both_n else float("nan")
    print(f"  raw proportion  = {pr_raw:.6f}")
    print(f"  both proportion = {pr_both:.6f}")
    print(f"  |difference|    = {abs(pr_raw - pr_both):.6f}")
    print()

    print("REMEDY CANDIDATES AND THEIR MEASURED COST")
    py = sorted(REPO.glob("scripts/*.py")) + sorted((REPO / "bench").rglob("*.py"))
    scanners = []
    for p in py:
        try:
            t = p.read_text(errors="replace")
        except Exception:
            continue
        if ("bench/logs" in t or 'rglob("*.json")' in t or "rglob('*.json')" in t):
            if "sandbox_harvest" not in t:
                scanners.append(p.relative_to(REPO))
    print(f"  (1) shared `is_archive_copy` predicate + a guard test:")
    print(f"      call sites that scan the archive WITHOUT any copy filter today"
          f" = {len(scanners)}")
    for s in scanners[:12]:
        print(f"        {s}")
    if len(scanners) > 12:
        print(f"        ... and {len(scanners) - 12} more")
    harvest_dirs = [d for d in logs.rglob("sandbox_harvest") if d.is_dir()]
    hb = sum(f.stat().st_size for d in harvest_dirs for f in d.rglob("*")
             if f.is_file())
    print(f"  (2) move harvest OUT of the archive namespace:")
    print(f"      directories to relocate = {len(harvest_dirs)}, "
          f"bytes = {hb:,}")
    print(f"      cost: every committed path into those trees breaks at once.")
    print(f"  (3) guard test refusing a new scan with no shared predicate:")
    print(f"      cost: one AST test; it is the ONLY candidate that prevents "
          f"the NEXT instance rather than repairing the last one.")

    print()
    print("=" * 78)
    assert raw_n != both_n, (
        "REFUTED: filtering archive copies changes nothing, so the conflation "
        "is not reaching this measurement and no remedy is warranted here.")
    print("SURVIVES: the conflation inflates a measurement Q3 depends on.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
