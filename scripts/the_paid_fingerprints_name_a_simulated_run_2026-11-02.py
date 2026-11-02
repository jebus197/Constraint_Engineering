#!/usr/bin/env python3
"""The 5 paid-seat fingerprints record a SIMULATED run as their last experiment.

THE RUNWAY'S FIRST ACTION, from `experimental_notes/Runway_Status_And_Is_It_Safe_To_Merge_2026-10-16.md`:
*"Correct the 5 fingerprints. Take your ruling on the memory. Merge to main.
Then run the Stage 1 replay there."* And on the fingerprints themselves:
*"Five real paid-seat fingerprints differ from main [...] they now record that
the seat was last seen in a simulated run on the 3rd of October. No measured
value moved at all [...] So this is a provenance smear and not a corruption of
capability, and it must be corrected before the merge or main will carry 5 paid
seats whose records name a run that never dispatched them."*

★ THAT DESCRIPTION IS 16 DAYS OLD AND HALF OF IT NO LONGER HOLDS. Measured here
rather than assumed, which matters because the sentence above is the stated
blocker on a merge:

  1. THE BRANCH DIFFERENCE IS GONE. All 5 paid fingerprints are byte-identical
     to main -- 1267 and 1272 bytes on both sides for the 2 checked by hand, and
     0 differing fields across all 5. So "differ from main" is no longer true and
     the merge cannot carry a difference that does not exist.

  2. THE PROVENANCE PROBLEM IS REAL AND PRESENT ON BOTH BRANCHES. All 5 record
     `experiment = sim45_memory` at 2026-09-08, which is a SIMULATED run, while
     the latest run in the archive whose seats are all non-simulated is
     `exp55_v3_control_20260823T153955Z` -- 16 days EARLIER. So a simulated run
     overwrote the label, and main carries the same smear. The runway's concern
     stands; its diagnosis of WHERE does not.

  3. IT IS A SMEAR AND NOT A CORRUPTION, AND THAT IS NOW EVIDENCED RATHER THAN
     ASSERTED. For each seat, 11 of 15 observed fields differ from its own
     simulated twin, so the paid record kept its own measurements. Had they been
     identical, a simulated run would have overwritten the capability figures and
     this would be a corruption.

  4. AND THE MECHANISM IS ALREADY FIXED. The `-SIM` records carry today's run
     while the paid records sit untouched at 2026-09-08, so the separation
     between a seat and its stand-in now holds. The smear is HISTORICAL.

★ THIS SCRIPT DOES NOT CORRECT ANYTHING, AND THE REFUSAL IS THE POINT. A
fingerprint is a PRIOR a future run reads, so rewriting one changes what a model
is told about itself. The correct value is derivable -- the last genuinely paid
run and its stamp -- but deriving a value and being authorised to write it into
an experimental record are different things, and the runway places this
correction before a merge that is his to authorise. So the figures are reported
and the 1-line correction is put to him.
"""
from __future__ import annotations
import json, math, pathlib, re, subprocess, sys

import sys as _sys, pathlib as _pl  # noqa: E402
for _cand in (_pl.Path(__file__).resolve().parent, *_pl.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        if str(_cand) not in _sys.path:
            _sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
FP = REPO / "bench" / "fingerprints"
LOGS = REPO / "bench" / "logs"
PAID = ("CC2", "ChatGPT", "Codex", "DeepSeek", "Gemini")
SIMRUN = re.compile(r"sim\d|free_run|commissioning|shakedown|study_run|"
                    r"severity_bounds|_sim\b", re.I)


def wilson(k: int, n: int):
    if n == 0:
        return (float("nan"),) * 3
    p = k / n; z = 1.959963984540054
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, c - h), min(1.0, c + h)


def main() -> int:
    answer_help(__doc__, __file__)
    print("=" * 78)
    print("THE 5 PAID-SEAT FINGERPRINTS AND WHAT THEIR LABELS SAY")
    print("=" * 78)

    # --- 1. the branch difference the runway names ------------------------
    print("\n1. DO THEY DIFFER FROM main, AS THE RUNWAY STATES?")
    differ = 0
    for m in PAID:
        rel = f"bench/fingerprints/{m}.json"
        here = (REPO / rel).read_text()
        out = subprocess.run(["git", "show", f"main:{rel}"], capture_output=True,
                             text=True, cwd=str(REPO))
        if out.returncode != 0 or not out.stdout:
            print(f"   {m:10s} main copy UNREADABLE -- nothing concluded for it")
            continue
        same = json.loads(here) == json.loads(out.stdout)
        differ += 0 if same else 1
        print(f"   {m:10s} identical to main: {same}   "
              f"({len(here)} bytes here, {len(out.stdout)} on main)")
    print(f"   seats differing from main: {differ} of {len(PAID)}")
    print(f"   -> the runway's 'differ from main' no longer holds."
          if differ == 0 else "   -> the difference the runway names is still present.")

    # --- 2. does the label name a simulated run? -------------------------
    print("\n2. DOES THE LABEL NAME A SIMULATED RUN?")
    smeared = 0
    for m in PAID:
        d = json.loads((FP / f"{m}.json").read_text())
        exp = str(d.get("experiment") or "")
        hit = bool(SIMRUN.search(exp))
        smeared += 1 if hit else 0
        print(f"   {m:10s} experiment={exp!r:22s} stamp={str(d.get('timestamp'))[:19]}"
              f"   simulated: {'YES' if hit else 'no'}")
    p, lo, hi = wilson(smeared, len(PAID))
    print(f"   {smeared}/{len(PAID)} = {p:.6f}  Wilson 95% [{lo:.6f}, {hi:.6f}]")
    print("   The uniformity is EXPLAINED rather than suspicious: all 5 carry the")
    print("   same experiment and the same second, so 1 run wrote all 5.")

    # --- 3. smear or corruption? -----------------------------------------
    print("\n3. SMEAR OR CORRUPTION? Compared against each seat's OWN stand-in.")
    for m in PAID:
        sim = FP / f"{m}-SIM.json"
        if not sim.is_file():
            print(f"   {m:10s} no -SIM twin; nothing concluded")
            continue
        po = (json.loads((FP / f"{m}.json").read_text()).get("observed") or {})
        so = (json.loads(sim.read_text()).get("observed") or {})
        keys = set(po) | set(so)
        diff = {k for k in keys if po.get(k) != so.get(k)}
        print(f"   {m:10s} {len(diff)} of {len(keys)} observed field(s) differ "
              f"from its stand-in")
    print("   Differing values mean the paid record kept its own measurements, so")
    print("   only the provenance label is wrong. Identical values would have")
    print("   meant a simulated run overwrote the capability figures.")

    # --- 4. what the label SHOULD name -----------------------------------
    print("\n4. WHAT THE LABEL WOULD NAME IF CORRECTED")
    best = None
    for f in sorted(LOGS.glob("*/runner_state.json")):
        try:
            j = json.loads(f.read_text(errors="ignore"))
        except Exception:                                    # noqa: BLE001
            continue
        e = (j.get("registry") or {}).get("entries") or {}
        e = list(e.values()) if isinstance(e, dict) else list(e)
        seats = {str(x.get("source_model") or "") for x in e if x.get("source_model")}
        if not seats or any(s.endswith("-SIM") for s in seats):
            continue
        mm = re.search(r"(20\d{6}T\d{6}Z)", f.parent.name)
        if mm and (best is None or mm.group(1) > best[1]):
            best = (f.parent.name, mm.group(1))
    print(f"   latest run whose seats are ALL non-simulated: "
          f"{best[0] if best else '(none found)'}")
    if best:
        print(f"   its stamp: {best[1]}, which is EARLIER than the 2026-09-08 the")
        print(f"   fingerprints record -- so the label was overwritten after it.")

    print("\n" + "=" * 78)
    print("NOTHING IS CORRECTED HERE, DELIBERATELY. A fingerprint is a PRIOR a")
    print("future run reads, so rewriting 1 changes what a model is told about")
    print("itself. The value is derivable; the authorisation is his, and the")
    print("runway places this correction before a merge that is his to make.")
    print("THE 1-LINE DECISION: correct the 5 labels to the last genuinely paid")
    print("run and its stamp, or leave them and record the smear in the files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
