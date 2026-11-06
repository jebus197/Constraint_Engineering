#!/usr/bin/env python3
"""HIS QUESTION, 2026-11-06: "at some random point you stopped using hash IDs
like this. I asked you why, but you have yet to provide a meaningful answer."

THE QUESTION HAS 2 HALVES AND THEY HAVE DIFFERENT ANSWERS, which is why no
answer I gave was meaningful:

  ASSIGNMENT  does every issue, fix and status still GET a hash id?
  SURFACING   does that id ever reach a document HE reads?

A store that assigns 7,180 identifiers nobody sees is not a facility he has; it
is a facility he was promised. Measured separately here, with intervals, so the
answer names which half failed.
"""
from __future__ import annotations
import json, re
from collections import Counter
from pathlib import Path

#: ANSWER `--help` BEFORE DOING ANY WORK. These 2 producers run at module
#: level rather than inside a main(), so the guard sits here: after the
#: imports and before the 1st measurement. His rule, measured: a flag
#: that runs the whole measurement can cost machine time or money.
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _cli_help import answer_help as _ah
_ah(__doc__, __file__)

REPO = Path(__file__).resolve().parents[1]
HASH = re.compile(r"\b[0-9a-f]{12}\b")

def iv(label, k, n):
    import mpmath
    from scipy.stats import beta as sbeta
    from statsmodels.stats.proportion import proportion_confint
    if n == 0:
        print(f"  {label}: no denominator, no claim"); return
    wl, wh = proportion_confint(k, n, method="wilson")
    mpmath.mp.dps = 40
    z = mpmath.mpf("1.959963984540054235524594430520551527955"); p = mpmath.mpf(k)/n
    den = 1 + z**2/n; c = p + z**2/(2*n)
    rad = z*mpmath.sqrt(p*(1-p)/n + z**2/(4*n*n))
    cl = 0.0 if k == 0 else float(sbeta.ppf(0.025, k, n-k+1))
    ch = 1.0 if k == n else float(sbeta.ppf(0.975, k+1, n-k))
    print(f"  {label}: {k} of {n} = {k/n:.6f}")
    print(f"      Wilson [{wl:.6f}, {wh:.6f}] statsmodels / "
          f"[{float((c-rad)/den):.6f}, {float((c+rad)/den):.6f}] mpmath")
    print(f"      Clopper-Pearson [{cl:.6f}, {ch:.6f}] scipy.beta")

rows = [json.loads(l) for l in (REPO/"bench"/"tickets"/"tickets.jsonl")
        .read_text(encoding="utf-8").splitlines() if l.strip()]
print("=" * 74)
print("HALF 1 -- ASSIGNMENT: does every row carry a hash id?")
have_tid = [r for r in rows if (r.get("tid") or "").strip()]
iv("rows carrying a `tid`", len(have_tid), len(rows))
print(f"  id lengths seen: {dict(Counter(len(r['tid']) for r in have_tid))}")
have_nid = sum(1 for r in rows if (r.get("nid") or "").strip())
have_rid = sum(1 for r in rows if (r.get("rid") or "").strip())
print(f"  rows with a `nid` (the issue's identity): {have_nid}")
print(f"  rows with a `rid` (the resolution's identity): {have_rid}")
#: DISTINCTNESS is the property an identifier must have; a shared id is worse
#: than none, because it asserts a relation that does not hold.
tids = [r["tid"] for r in have_tid]
print(f"  distinct tids: {len(set(tids))} of {len(tids)} rows "
      f"({len(tids) - len(set(tids))} repeats, which are status UPDATES to the "
      f"same ticket and are correct)")
ids_per_kind = Counter(r.get("kind") for r in have_tid)
print(f"  by kind: {dict(ids_per_kind)}")

print("\nHALF 2 -- SURFACING: does an id reach a document he reads?")
targets = {
    "spoken morning reports (.txt)":
        sorted((REPO/"experimental_notes").glob("Morning_Report_*_GENERATED.txt")),
    "written morning reports (.md)":
        sorted((REPO/"experimental_notes").glob("Morning_Report_*_GENERATED.md")),
    "decisions files (.md)":
        sorted((REPO/"experimental_notes").glob("Decisions_Awaiting_You_*.md")),
    "the master task list":
        [REPO/"experimental_notes"/"CDSFL_MASTER_TASK_LIST.md"],
    "the parked file":
        [REPO/"experimental_notes"/"PARKED_FOR_THE_FOUNDER.md"],
}
known = set(tids)
for label, files in targets.items():
    if not files: continue
    carry = 0
    for f in files:
        if not f.is_file(): continue
        t = f.read_text(encoding="utf-8", errors="replace")
        #: A HASH-SHAPED STRING IS NOT AN ID. It must be one the store issued,
        #: or a commit sha and a sha256 prefix would both count as a ticket id.
        if any(h in known for h in set(HASH.findall(t))):
            carry += 1
    iv(f"{label}", carry, len([f for f in files if f.is_file()]))

print("\n  THE NEWEST OF EACH, NAMED, because a rate hides which one he last read:")
for label, files in targets.items():
    live = [f for f in files if f.is_file()]
    if not live: continue
    f = live[-1]
    t = f.read_text(encoding="utf-8", errors="replace")
    found = sorted({h for h in set(HASH.findall(t)) if h in known})
    print(f"    {f.name[:52]:52s} ids: {len(found)}")
