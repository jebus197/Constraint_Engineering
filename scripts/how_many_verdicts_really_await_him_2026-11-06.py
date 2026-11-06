#!/usr/bin/env python3
"""HIS QUESTION, 2026-11-06: which of the verdicts required of him are real and
which repeat a ruling he has already given -- and is the count unusually high?

HE WAS GIVEN AT LEAST 5 DIFFERENT NUMBERS BY 5 DIFFERENT SURFACES, which is why
the count was confusing before any of them was wrong. Each is counted here from
its own artefact, and the REPEAT test is the report builder's own
`ruling_is_spent`, so this producer cannot disagree with the surface he reads.

A REPEAT is an item whose ruling is ON RECORD and still settles it. An item that
carries a ruling AND asks something new afterwards is NOT a repeat -- that is the
inverse fault, suppressing a live question behind an old answer, and the record
holds it happening (the role layer, silenced by a ruling 14 days older than its
questions).
"""
from __future__ import annotations
import importlib.util, json, re, sys
from pathlib import Path
from collections import Counter

#: ANSWER `--help` BEFORE DOING ANY WORK. These 2 producers run at module
#: level rather than inside a main(), so the guard sits here: after the
#: imports and before the 1st measurement. His rule, measured: a flag
#: that runs the whole measurement can cost machine time or money.
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _cli_help import answer_help as _ah
_ah(__doc__, __file__)

REPO = Path(__file__).resolve().parents[1]

def iv(k, n):
    import mpmath
    from scipy.stats import beta as sbeta
    from statsmodels.stats.proportion import proportion_confint
    if n == 0: return None
    wl, wh = proportion_confint(k, n, method="wilson")
    mpmath.mp.dps = 40
    z = mpmath.mpf("1.959963984540054235524594430520551527955"); p = mpmath.mpf(k)/n
    den = 1 + z**2/n; c = p + z**2/(2*n)
    rad = z*mpmath.sqrt(p*(1-p)/n + z**2/(4*n*n))
    wl2, wh2 = float((c-rad)/den), float((c+rad)/den)
    cl = 0.0 if k == 0 else float(sbeta.ppf(0.025, k, n-k+1))
    ch = 1.0 if k == n else float(sbeta.ppf(0.975, k+1, n-k))
    return (wl, wh), (wl2, wh2), (cl, ch)

def show(label, k, n):
    r = iv(k, n)
    print(f"  {label}: {k} of {n} = {k/n:.6f}")
    print(f"      Wilson [{r[0][0]:.6f}, {r[0][1]:.6f}] statsmodels / "
          f"[{r[1][0]:.6f}, {r[1][1]:.6f}] mpmath  agree={abs(r[0][0]-r[1][0])<1e-12}")
    print(f"      Clopper-Pearson [{r[2][0]:.6f}, {r[2][1]:.6f}] scipy.beta")

print("=" * 76)
print("SURFACE 1 -- THE REPORT HE READS, section 1 'Decisions that need you'")
rep = sorted(REPO.glob("experimental_notes/Morning_Report_*_GENERATED.md"))[-1]
lines = rep.read_text(encoding="utf-8").splitlines()
a = next(i for i, l in enumerate(lines) if l.startswith("## 1."))
b = next(i for i, l in enumerate(lines) if l.startswith("## 2."))
#: AN ITEM IS A NUMBERED HEADING, not any mention. A mention-based count caught
#: 'B9' out of prose earlier tonight, which is the over-matching fault again.
items = re.findall(r"^#{3,4}\s*\d+\.\s*([A-Z]\d{1,4}|C00\d\d|R\d)\b", "\n".join(lines[a:b]), re.M)
print(f"  file: {rep.name}  (written {rep.stat().st_mtime and ''}{rep.name[15:25]})")
print(f"  decision ITEMS: {len(items)} -> {items}")

print("\nSURFACE 2 -- THE STANDALONE DECISIONS FILE")
dec = REPO/"experimental_notes"/"Decisions_Awaiting_You_2026-11-04.md"
t = dec.read_text(encoding="utf-8")
nums = sorted(int(x) for x in re.findall(r"^#{2,3} DECISION (\d+)\.", t, re.M))
hdr = re.search(r"carries forward all (\d+) decisions.*?adds (\d+) new ones", t, re.S)
print(f"  headings: {len(nums)}, contiguous 1..{len(nums)}: {nums == list(range(1, len(nums)+1))}")
print(f"  the file's OWN header still claims: {int(hdr.group(1)) + int(hdr.group(2))}"
      f"  -> STALE BY {len(nums) - (int(hdr.group(1)) + int(hdr.group(2)))}")

print("\nSURFACE 3 and 4 -- THE TASK LIST, and whose move it is")
spec = importlib.util.spec_from_file_location(
    "mrb", REPO/"scripts"/"morning_report_build_2026-10-12.py")
mr = importlib.util.module_from_spec(spec); sys.modules["mrb"] = mr
spec.loader.exec_module(mr)
live = mr.task_items()
cls = {}
for it in live:
    ruled = it.get("ruled")
    if not ruled: cls[it["ident"]] = "REAL"
    else:
        spent = mr.ruling_is_spent(f"task:{it['ident']}", ruled, it.get("state") or "")
        cls[it["ident"]] = "LIVE-AGAIN" if spent else "REPEAT"
c = Counter(cls.values())
print(f"  live entries: {len(live)}   partition: {dict(c)}")
repeats = sorted(k for k, v in cls.items() if v == "REPEAT")
print(f"  REPEAT entries: {repeats}")
show("REAL, never ruled", c["REAL"], len(live))
show("REPEAT, ruling still settles it", c["REPEAT"], len(live))

print("\n  THE DECIDING LAYER: do those repeats reach section 1?")
leak = [x for x in items if cls.get(x) == "REPEAT"]
print(f"    repeats among the {len(items)} decision items: {len(leak)} -> {leak}")
show("    leak into section 1", len(leak), len(items))

print("\nSURFACE 5 -- THE TICKET STORE / REGISTRY, which he asked me to check")
rows = [json.loads(l) for l in (REPO/"bench"/"tickets"/"tickets.jsonl")
        .read_text(encoding="utf-8").splitlines() if l.strip()]
openr = [r for r in rows if (r.get("status") or "").upper() == "OPEN"]
ruled_open = [r for r in openr if (r.get("ruled") or "").strip()]
print(f"  rows: {len(rows)}   OPEN: {len(openr)}")
print(f"  OPEN by kind: {dict(Counter(r.get('kind') for r in openr))}")
show("OPEN rows carrying a ruling of his", len(ruled_open), len(openr))
print(f"  those rulings by kind: {dict(Counter(r.get('kind') for r in ruled_open))}")
tr = [r for r in ruled_open if (r.get('task_ref') or '').strip()]
print(f"  of them, tied to a task entry: {len(tr)}")
print(f"  distinct task entries they name: {len(set(r['task_ref'] for r in tr))}")
