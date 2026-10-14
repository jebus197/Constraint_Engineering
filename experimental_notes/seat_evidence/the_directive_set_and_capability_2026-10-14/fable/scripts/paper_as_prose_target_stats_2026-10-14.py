# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'the_directive_set_and_capability_2026-10-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: cdbcd88e5424d926b54a1f9192413748dd075b57bd0c3293d2fd68e23bdd50ce
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Is PAPER.md a workable prose target for A19? The mechanical facts, committed.

Run: python3 scripts/paper_as_prose_target_stats_2026-10-14.py  (--help is free)
"""
from __future__ import annotations
import argparse, math, pathlib, re

REPO = pathlib.Path(__file__).resolve().parents[1]
Z = 1.959963984540054

def wilson(k, n):
    if n == 0: return (0.0, 0.0)
    p = k / n; d = 1 + Z*Z/n; c = (p + Z*Z/(2*n))/d
    h = (Z/d)*math.sqrt(p*(1-p)/n + Z*Z/(4*n*n))
    return (max(0.0, c-h), min(1.0, c+h))

def main() -> int:
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()
    t = (REPO / "PAPER.md").read_text(encoding="utf-8")
    lines = t.splitlines()
    n = len(lines)
    comp = [l for l in lines if re.search(r"[=≈≤≥]\s*[\d(]|\b(R_k|R_n|C\(n\)|F_n|S_k|η|ν|π)\b", l)]
    lo, hi = wilson(len(comp), n)
    print(f"chars {len(t)}, lines {n}, headings "
          f"{sum(1 for l in lines if re.match(r'^#{1,6} ', l))}, "
          f"fenced blocks {t.count('```')//2}")
    print(f"computable lines: {len(comp)} of {n} = {100*len(comp)/n:.4f}% "
          f"(Wilson [{100*lo:.4f}%, {100*hi:.4f}%])")
    print(f"decimal numerics: {len(re.findall(r'\b\d+\.\d+\b', t))}; "
          f"percentages: {len(re.findall(r'\b\d+(?:\.\d+)?%', t))}; "
          f"confidence-interval mentions: "
          f"{len(re.findall(r'confidence interval|Wilson|Clopper', t, re.I))}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
