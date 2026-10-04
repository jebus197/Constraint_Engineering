#!/usr/bin/env python3
"""How far does identity-pairing of worked proofs reach on a real run?

`validate_round_rk` used to pair CORROBORATION sections to findings by POSITION.
This measures, over every archived seat response in a run, how many sections carry
a recoverable FINDING_ID -- i.e. how often the identity path can engage at all --
and how badly the section count diverges from the registered finding count, which
is what makes positional pairing wrong rather than merely fragile.

A number here is only meaningful with its denominator, so unreadable files are
counted and reported separately rather than folded into either arm.
"""
import argparse, collections, glob, json, pathlib, re, sys
sys.path.insert(0, "bench")
import numpy as np
from statsmodels.stats.proportion import proportion_confint
import mpmath as mp
import reference_runner_v3 as R

ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
ap.add_argument("--run", default=None)
a = ap.parse_args()
if getattr(a, "run", None) is None:
    ap.error("--run is required")

run = pathlib.Path(a.run)

def wilson(k, n):
    lo, hi = proportion_confint(k, n, method="wilson")
    mp.mp.dps = 30
    z = mp.mpf("1.959963984540054235309065817"); ph = mp.mpf(k)/n; nn = mp.mpf(n)
    c = (ph + z**2/(2*nn))/(1 + z**2/nn)
    hw = (z/(1+z**2/nn))*mp.sqrt(ph*(1-ph)/nn + z**2/(4*nn**2))
    assert abs(float(c-hw)-lo) < 1e-9 and abs(float(c+hw)-hi) < 1e-9, \
        f"statsmodels and mpmath disagree on Wilson for {k}/{n}"
    return round(100*lo, 4), round(100*hi, 4)

def response_text(d):
    for k in ("response", "raw", "text", "content", "output"):
        if isinstance(d.get(k), str) and len(d[k]) > 200:
            return d[k]
    for v in d.values():
        if isinstance(v, str) and len(v) > 500:
            return v
    return None

files = sorted(glob.glob(str(run / "r*_*.json")))
unreadable = 0
tot_sections = tot_identified = tot_phantom = 0
per_round = collections.defaultdict(lambda: [0, 0])   # round -> [sections, identified]
rows = []
for f in files:
    p = pathlib.Path(f)
    m = re.match(r"r(\d+)_", p.name)
    if not m:
        continue
    rnd = int(m.group(1))
    try:
        d = json.loads(p.read_text(errors="replace"))
    except Exception:
        unreadable += 1; continue
    txt = response_text(d)
    if txt is None:
        unreadable += 1; continue
    owned = R._extract_corroboration_sections_with_ids(txt)
    plain = R._extract_corroboration_sections(txt)
    # THE COUNTS ARE SUPPOSED TO DIVERGE. A first version of this script asserted
    # they must agree, which was my own premise and it was wrong: the original
    # extractor splits case-insensitively on the bare word, so it manufactures
    # sections from the JSON key `corroboration_fit` and from prose like
    # "independent corroboration". The divergence IS the phantom count.
    phantom = len(plain) - len(owned)
    ident = sum(1 for o, _ in owned if o)
    tot_sections += len(owned); tot_identified += ident
    tot_phantom += max(0, phantom)
    per_round[rnd][0] += len(owned); per_round[rnd][1] += ident
    rows.append((p.name, len(owned), ident, len(plain)))

print(f"run: {run.name}")
print(f"seat response files read: {len(rows)}   unreadable/no-text: {unreadable}")
print()
print("per seat response: sections / of those, carrying a FINDING_ID")
for name, n, k, orig in rows:
    print(f"  {name:44} real={n:4d}  owned={k:4d}  "
          f"original_said={orig:4d}  phantom={orig-n:4d}")
print()
if tot_sections:
    lo, hi = wilson(tot_identified, tot_sections)
    print(f"SECTIONS WITH A RECOVERABLE OWNER: {tot_identified}/{tot_sections} = "
          f"{100.0*tot_identified/tot_sections:.4f}%  Wilson [{lo}%, {hi}%]  "
          f"(statsmodels == mpmath)")
    print("  -> this is the fraction where identity pairing can engage. The rest")
    print("     still fall back to position, exactly as before the fix.")
    print()
    print(f"PHANTOM SECTIONS the ORIGINAL extractor manufactures from prose: "
          f"{tot_phantom} on top of {tot_sections} real "
          f"({100.0*tot_phantom/max(1,tot_sections+tot_phantom):.4f}% of what it reports)")
    print("  -> these are what made positional pairing select the wrong block.")
print()
counts = np.array([n for _, n, _, _ in rows])
if counts.size:
    print(f"sections per response (NumPy): min={counts.min()} median={np.median(counts):.1f} "
          f"max={counts.max()} mean={counts.mean():.4f}")

# the registered-finding counts, for the divergence that makes position WRONG
rep = next(iter(sorted(run.glob("*_report.json"))), None)
if rep:
    d = json.loads(rep.read_text(errors="replace"))
    prc = d.get("per_round_counts") or []
    if prc:
        print()
        print("registered findings per round vs sections emitted that round:")
        for rnd in sorted(per_round):
            secs, ident = per_round[rnd]
            reg = prc[rnd] if rnd < len(prc) else None
            print(f"  round {rnd}: sections={secs:4d}  identified={ident:4d}  "
                  f"registered findings={reg}")
        print()
        print("  Where sections FAR exceed registered findings, positional pairing")
        print("  hands a survivor whichever block came first in the raw text.")
