#!/usr/bin/env python3
"""THE LINE CAPS WERE NEVER HIS -- producer, 2026-11-06.

FIND. The morning report of 2026-11-06 put 3 items to the founder for a
verdict. Items 1 and 2 were document line limits and the report called the
first one "your cap of 300". The decisions data says "Your note standard,
rule 10, says a markdown note runs 40 to 300 lines and a spoken file 60 to
400", and scripts/morning_report_build_2026-10-12.py names "the note
standard's 300-line ceiling (Rule 10)". He replied: "I never specified a
cap." This script tests that reply against the record.

3 measurements:
  1. DEFINITION. Does any note-standard file DEFINE a Rule 10, or the
     40-300 / 60-400 numbers? Counted separately from files that CITE them.
  2. ATTRIBUTION. Of the live artefacts that cite the limits, how many
     attribute them to HIM ("your note standard", "your cap", ...)?
  3. HIS OWN WORDS. How many of his recorded annotations state a numeric
     length limit for a note or a spoken file?

Every proportion carries 2 interval families (Wilson, Clopper-Pearson),
each computed by 2 independent routes, per the project's sy rule.
"""
from __future__ import annotations
import pathlib, re, subprocess, sys

from statsmodels.stats.proportion import proportion_confint
from scipy.stats import beta as _beta
import mpmath as mp

mp.mp.dps = 40
REPO = pathlib.Path(__file__).resolve().parent.parent
MEM = pathlib.Path.home() / ".claude/projects/-Users-georgejackson-Developer-Projects/memory"


def _iv(k: int, n: int):
    """((wilson_lo, wilson_hi), (cp_lo, cp_hi), disagreement_magnitude)."""
    if n == 0:
        return (0.0, 1.0), (0.0, 1.0), 0.0
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = mp.mpf("1.959963984540054235524594430520551527955")
    ph = mp.mpf(k) / n
    den = 1 + z**2 / n
    cen = (ph + z**2 / (2 * n)) / den
    half = (z / den) * mp.sqrt(ph * (1 - ph) / n + z**2 / (4 * n * n))
    wl2, wh2 = float(cen - half), float(cen + half)

    cl = 0.0 if k == 0 else float(_beta.ppf(0.025, k, n - k + 1))
    ch = 1.0 if k == n else float(_beta.ppf(0.975, k + 1, n - k))

    def _invert(a, b, y):
        f = lambda x: mp.betainc(a, b, 0, x, regularized=True) - y
        loq, hiq = mp.mpf(0), mp.mpf(1)
        for _ in range(200):
            mid = (loq + hiq) / 2
            loq, hiq = (mid, hiq) if f(mid) < 0 else (loq, mid)
        return float((loq + hiq) / 2)

    cl2 = 0.0 if k == 0 else _invert(k, n - k + 1, 0.025)
    ch2 = 1.0 if k == n else _invert(k + 1, n - k, 0.975)
    dis = max(abs(lo - wl2), abs(hi - wh2), abs(cl - cl2), abs(ch - ch2))
    return (max(0.0, lo), hi), (cl, ch), dis


def _show(label, k, n):
    (wl, wh), (cl, ch), dis = _iv(k, n)
    r = k / n if n else float("nan")
    print(f"  {label}: {k} of {n} = {r:.6f}")
    print(f"      Wilson 95% [{wl:.6f}, {wh:.6f}]  Clopper-Pearson 95% [{cl:.6f}, {ch:.6f}]")
    print(f"      2-route disagreement {dis:.3e}")
    assert dis < 1e-6, f"routes disagree by {dis}"


# ---------------------------------------------------------------- 1. DEFINITION
NUMBERS = re.compile(r"\b(40\s*(?:to|-|–)\s*300|60\s*(?:to|-|–)\s*400|300[- ]line|400[- ]line)\b", re.I)
RULE10_DEF = re.compile(r"^#+\s*Rule\s*10\b", re.M)
RULE10_CITE = re.compile(r"\bRule\s*10\b", re.I)

standards = sorted(MEM.glob("cdsfl_note_standard*.md")) + sorted(REPO.glob("**/*note_standard*.md"))
standards = [p for p in standards if "logs/" not in str(p)]
print("1. DEFINITION -- does a Rule 10 exist?")
print(f"  note-standard files found: {len(standards)}")
definers, citers = [], []
for p in standards:
    t = p.read_text(errors="replace")
    if RULE10_DEF.search(t) or NUMBERS.search(t):
        definers.append(p)
    if RULE10_CITE.search(t):
        citers.append(p)
for p in standards:
    print(f"    {p.name}")
print(f"  files DEFINING a Rule 10 or the numbers: {len(definers)} {[p.name for p in definers]}")
print(f"  files even MENTIONING Rule 10:           {len(citers)} {[p.name for p in citers]}")

# ---------------------------------------------------------------- 2. ATTRIBUTION
SKIP = ("/bench/logs/", "/.git/", "/sandbox_harvest/", "/work/")
HIS = re.compile(r"\byour (?:own )?(?:note standard|cap|line limit|limit|standard|ceiling)\b", re.I)
cands = []
for p in list(REPO.glob("**/*.py")) + list(REPO.glob("**/*.md")) + list(REPO.glob("**/*.json")):
    s = str(p)
    if any(k in s for k in SKIP):
        continue
    try:
        t = p.read_text(errors="replace")
    except Exception:
        continue
    if NUMBERS.search(t) or (RULE10_CITE.search(t) and re.search(r"\b(300|400)\b", t)):
        cands.append((p, t))
print("\n2. ATTRIBUTION -- of the live artefacts citing the limits, how many call them HIS?")
attributing = [p for p, t in cands if HIS.search(t)]
for p, t in cands:
    m = HIS.search(t)
    print(f"    {'HIS ' if m else '    '} {p.relative_to(REPO)}" + (f"   <- \"{m.group(0)}\"" if m else ""))
_show("attributed to him", len(attributing), len(cands))

# ---------------------------------------------------------------- 3. HIS WORDS
print("\n3. HIS OWN WORDS -- does he ever state a numeric length limit?")
r = subprocess.run([sys.executable, "scripts/read_founder_responses_2026-10-11.py"],
                   cwd=REPO, capture_output=True, text=True, timeout=600)
print(f"  reader exit {r.returncode}, {len(r.stdout.splitlines())} lines of output")
his = []
for line in r.stdout.splitlines():
    s = line.strip()
    if s.startswith("HIS WORDS:"):
        his.append(s[len("HIS WORDS:"):].strip())
    elif s.startswith(">>"):
        his.append(re.sub(r"^>>\s*\d*\s*#?\s*", "", s))
his = [h for h in his if h]
LENGTH_NUM = re.compile(r"\b(\d{2,5})\s*(?:lines?|characters?|words?)\b", re.I)
CAPWORD = re.compile(r"\b(cap|limit|ceiling|max|maximum|no more than|no longer than|at most|under)\b", re.I)
stating = [h for h in his if LENGTH_NUM.search(h) and CAPWORD.search(h)]
print(f"  his recorded annotation blocks scanned: {len(his)}")
for h in stating:
    print(f"    STATES A NUMERIC LENGTH LIMIT: {h[:220]}")
_show("his blocks stating a numeric length limit", len(stating), len(his))

NARR = [h for h in his if re.search(r"over.?narrat", h, re.I)]
print(f"\n  his blocks saying 'over narration': {len(NARR)}")
for h in NARR:
    print(f"    {h[:300]}")
print("\nDONE")
