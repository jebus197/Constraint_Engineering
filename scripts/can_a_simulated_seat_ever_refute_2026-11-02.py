#!/usr/bin/env python3
"""Can the severity specification's ANNIHILATION branch ever fire, and does MONEY decide it?

HIS QUESTION, 2026-11-02, verbatim: *"What is it about it that requires a
'different seat', and by different seat, what do you mean? A seat from another
vendor that is not Anthropic? That would by definition require a paid run. So
again, why is a paid run any different to a simulated one for this measurement?"*

HE IS RIGHT THAT THE EARLIER ANSWER WAS INCOHERENT. "A seat that refutes" was
offered as though it were a property of a seat. It is not. `REFUTED` is written
by `reverify_falsifier(code)` at reference_runner_v3.py:16486 and 9439 -- code
EXECUTED on this machine. No vote, no vendor, no charge. So the branch is
reachable with 0 money IF a falsifier runs and fails to demonstrate its defect.

THIS SCRIPT ASKS THE 3 SEPARABLE QUESTIONS THE EARLIER ANSWER RAN TOGETHER:
  Q1  How many falsifiers have EVER executed, and how many returned REFUTED?
  Q2  Does the split differ between runs with SIMULATED seats (-SIM labels) and
      runs with PAID seats? That is the only form in which "money" could be the
      variable, and it is checkable against the archive rather than argued.
  Q3  Of falsifiers that ran, how many were flagged INDETERMINATE_NOT_INTERCEPTED
      by the discrimination control -- i.e. behaved identically when the target
      was replaced wholesale, so could not have returned REFUTED whatever the seat?

Every proportion carries a Wilson interval, computed twice (closed form and
statsmodels) per the project's 2-tool rule.
"""
from __future__ import annotations
import json, pathlib, re, collections, math, sys

# `_cli_help` lives in scripts/. Locate it rather than assume a depth: the
# project has already had a helper import break when a script moved.
import sys as _sys, pathlib as _pl
for _cand in (_pl.Path(__file__).resolve().parent, *_pl.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        if str(_cand) not in _sys.path:
            _sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"
SIM = re.compile(r"-SIM\b")
GATE = re.compile(r"falsifier gate \(tools decide\):\s*(\d+) CONFIRMED,\s*(\d+) REFUTED,\s*(\d+) -> HIL")
CTRL = re.compile(r"discrimination control (\w+)")


def wilson(k: int, n: int) -> tuple[float, float, float]:
    if n == 0:
        return (float("nan"),) * 3
    p = k / n
    z = 1.959963984540054
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, c - h), min(1.0, c + h)


def main() -> int:
    answer_help(__doc__, __file__)
    gate_conf = gate_refu = gate_hil = 0
    ctrl = collections.Counter()
    per_run = []
    # Only TOP-LEVEL run logs. A harvested copy under */files/bench/** is the
    # same run preserved twice; counting it would be the 27-of-27 self-match
    # shape the project already has a memory file about.
    for lg in sorted(LOGS.glob("*.log")):
        txt = lg.read_text(errors="replace")
        gs = GATE.findall(txt)
        if not gs:
            continue
        c = sum(int(a) for a, _, _ in gs)
        r = sum(int(b) for _, b, _ in gs)
        h = sum(int(x) for _, _, x in gs)
        gate_conf += c; gate_refu += r; gate_hil += h
        cs = collections.Counter(CTRL.findall(txt))
        ctrl.update(cs)
        per_run.append({"log": lg.name, "simulated": bool(SIM.search(txt)),
                        "confirmed": c, "refuted": r, "hil": h,
                        "not_intercepted": cs.get("INDETERMINATE_NOT_INTERCEPTED", 0),
                        "ctrl": dict(cs)})

    # Registry-level verdicts, from runner_state.json (the recorded field, not the log).
    reg = collections.Counter(); reg_sim = collections.Counter(); reg_paid = collections.Counter()
    for st_f in sorted(LOGS.glob("*/runner_state.json")):
        try:
            st = json.loads(st_f.read_text())
        except Exception:
            continue
        ents = (st.get("registry") or {}).get("entries") or {}
        ents = list(ents.values()) if isinstance(ents, dict) else list(ents)
        if not ents:
            continue
        simulated = any(SIM.search(str(e.get("model") or e.get("origin_model") or
                                       e.get("canonical_id") or "")) for e in ents)
        for e in ents:
            v = str(e.get("falsifier_verdict") or "<none>")
            reg[v] += 1
            (reg_sim if simulated else reg_paid)[v] += 1

    print("=" * 78)
    print("CAN THE ANNIHILATION BRANCH EVER FIRE? ARCHIVE-WIDE")
    print("=" * 78)
    print(f"  run logs carrying a falsifier gate line : {len(per_run)}")
    tot = gate_conf + gate_refu
    print(f"\n  Q1  FALSIFIER GATE DECISIONS, ALL RUNS")
    print(f"      CONFIRMED {gate_conf} | REFUTED {gate_refu} | -> HIL {gate_hil}")
    if tot:
        p, lo, hi = wilson(gate_refu, tot)
        print(f"      REFUTED share of decided: {gate_refu}/{tot} = {p:.6f}"
              f"  Wilson 95% [{lo:.6f}, {hi:.6f}]")
    print(f"\n      recorded falsifier_verdict census (runner_state.json):")
    for k, v in reg.most_common():
        print(f"        {k:22s} {v}")

    print(f"\n  Q2  DOES MONEY DECIDE IT? simulated vs paid runs")
    n_sim = sum(1 for r in per_run if r["simulated"])
    sim_c = sum(r["confirmed"] for r in per_run if r["simulated"])
    sim_r = sum(r["refuted"] for r in per_run if r["simulated"])
    pd_c = sum(r["confirmed"] for r in per_run if not r["simulated"])
    pd_r = sum(r["refuted"] for r in per_run if not r["simulated"])
    print(f"      SIMULATED runs ({n_sim}): CONFIRMED {sim_c}, REFUTED {sim_r}")
    print(f"      PAID/other runs ({len(per_run)-n_sim}): CONFIRMED {pd_c}, REFUTED {pd_r}")
    if (sim_c + sim_r) and (pd_c + pd_r):
        from scipy import stats as _s
        odds, pv = _s.fisher_exact([[sim_r, sim_c], [pd_r, pd_c]])
        print(f"      Fisher exact p = {pv:.6f}, odds ratio {odds:.6f}")
        print("      -> a p that cannot distinguish them means MONEY IS NOT THE VARIABLE.")
    else:
        print("      ONE SIDE HAS NO DECIDED FALSIFIERS. The comparison is NOT TESTABLE,")
        print("      and reporting it either way would be the flattering reading.")
    print(f"      registry falsifier_verdict, simulated: {dict(reg_sim)}")
    print(f"      registry falsifier_verdict, paid/other: {dict(reg_paid)}")

    print(f"\n  Q3  COULD THOSE FALSIFIERS HAVE REFUTED AT ALL?")
    print(f"      discrimination control census: {dict(ctrl)}")
    ni = ctrl.get("INDETERMINATE_NOT_INTERCEPTED", 0)
    ctot = sum(ctrl.values())
    if ctot:
        p, lo, hi = wilson(ni, ctot)
        print(f"      NOT_INTERCEPTED: {ni}/{ctot} = {p:.6f}  Wilson 95% [{lo:.6f}, {hi:.6f}]")
        print("      A falsifier that behaves identically when its target is replaced")
        print("      wholesale is not reading the target, so it CANNOT return REFUTED.")
    print("\n  PER RUN")
    for r in per_run:
        print(f"      {'SIM ' if r['simulated'] else 'PAID'} {r['log'][:52]:52s} "
              f"C={r['confirmed']:3d} R={r['refuted']:3d} HIL={r['hil']:3d} "
              f"notintercepted={r['not_intercepted']:3d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
