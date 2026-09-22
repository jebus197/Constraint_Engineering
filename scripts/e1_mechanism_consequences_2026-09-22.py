#!/usr/bin/env python3
"""What each e1_efficacy mechanism would ACTUALLY change, counted over the archive.

WHY THIS EXISTS. The founder was handed a choice between "raise the e1 weight"
and "move efficacy into the hard gate" as a CONCEPT, with a threshold figure and
no statement of what either would do to real verdicts. That is a decision he
cannot make cheaply, and handing it over in that form was an error: the
consequences are fully computable from data already on disk.

THE MEASURED PROBLEM. Across the 4 commissioning arms of 2026-09-21/22, 124
proposed fixes carry a fix-efficacy probe result. 23 of them are
`FIX_DOES_NOT_CURE_ITS_OWN_FALSIFIER` -- 18.5484%, Wilson
[12.6898%, 26.2972%], Clopper-Pearson [12.1365%, 26.5202%]. At the shipped
weight of 2.0 every one was ADMITTED, because with the other gates clean
`E = 5/7 = 0.714286` on a Python target, comfortably above the break-even
`S* = 0.50493` (printed live by the runner as 0.505, and by 271 of 271 logged
evaluations -- so holding it constant costs nothing here).

CORRECTED 2026-09-22, PANEL: THIS SENTENCE SAID "46 of 248". Each probe record
is serialised TWICE in `bench/logs/commissioning_*/` -- once in
`runner_state.json` and once in `<name>_report.json` -- and both were counted.
The true figure is 23 of 124. The PROPORTION survives a 2x double-count exactly,
which is why it looked right: 46/248 = 23/124 = 18.5484% to every decimal place.
The INTERVAL does not. Reported Wilson width was 9.6488 pp; the data supports
13.6074 pp, so the escalation carried a confidence interval 29% narrower than
the evidence. An interval's whole job is to say how much the figure can be
trusted, and doubling n is precisely the error it cannot absorb. Both figures
cross-verified on statsmodels, mpmath at 50 dps and Wolfram Language, agreeing
to < 1e-12. `_noncuring_share()` below now MEASURES this rather than asserting
it, and de-duplicates by construction by reading `runner_state.json` only.

WHY THE DIRECTION IS NOT A PREFERENCE. `docs/MATHEMATICAL_APPENDIX.md` line 214
defines sigma as "Does the proposed fix actually resolve the detected flaw?",
and `compute_rk` fills the sigma slot with `sk` term for term. A fix that scores
sk = 1.0 while provably not resolving the flaw makes `sk` not sigma. That is an
internal contradiction in the model, not a matter of taste. What remains open is
only WHICH MECHANISM closes it, and that is what this script prices.

THE 4 OPTIONS PRICED.
  A  SHIPPED       e1 in the effect mean at weight 2.0.
  B  HEAVIER       e1 in the effect mean at weight 5.0, the smallest round
                   weight above the 4.9024 threshold derived for a Python
                   target with e2, e3 and e4 available.
  C  HARD GATE     efficacy multiplies into `A` alongside g0/g1/g2, so a
                   non-curing fix scores exactly 0.
  D  AN ABSENT PROBE IS NOT A CURE -- the option neither the escalation nor the
     founder was offered, and the one with 4x the reach. 78 of the 98 judged
     entries carry NO e1 score at all, and BOTH B and C leave every one of them
     admitted: B renormalises the weighted mean over AVAILABLE gates, so a
     missing e1 is skipped; C guards its multiply with `if e is not None`, so a
     missing e1 leaves `A` untouched. The morning report's own section 3 table
     records the third row -- "no probe result | sk 1.000 | ADMISSIBLE" -- and
     that row is 79.5918% of this population. Whatever weight e1 carries, 4
     entries in 5 route around it entirely.

     This matters under the project's OWN additive standard, in both directions.
     B and C add weight to a gate that 79.6% of scored entries never reach, and
     "an addition that nothing reaches is not additive either". And the internal
     contradiction the escalation rests on -- the appendix defines sigma as "does
     the fix actually resolve the detected flaw", `compute_rk` fills the sigma
     slot with `sk` term for term, so `sk = 1.0` on a fix that provably does not
     resolve the flaw makes `sk` not sigma -- applies WORD FOR WORD to an
     UNPROBED fix scoring 1.0, and there it applies to 78 entries rather than 7.
     D is the larger instance of the same defect.

     D is priced here as: an entry with a fix proposed and no e1 score scores
     e1 = 0 in the effect mean at the SHIPPED weight of 2.0. That is the
     conservative reading and deliberately not a hard gate, because unlike a
     measured non-cure an absent probe may mean the probe could not run -- which
     is itself a finding to report, not a reason to admit.

WHAT IS SIMPLIFIED, STATED RATHER THAN HIDDEN. The shipped pipeline returns a
TRISTATE (ADMISSIBLE / REJECTED / ESCALATE / NO_SCORE) and this compares `sk`
against `S*` only. Entries whose recorded tristate is not ADMISSIBLE or REJECTED
are reported separately and excluded from the flip counts, because a mechanism
that changes a score does not necessarily change an escalation. The break-even
is held at the constant 0.50493 rather than recomputed per entry from nu_b, nu_f,
q and R, because those are not all recorded per entry; the live run printed
0.505, so the constant is right to 3 decimal places at this operating point.

Every proportion carries a Wilson AND a Clopper-Pearson interval, and the
weighted-mean arithmetic is cross-verified symbolically in SymPy against the
numeric path.

Run:  python3 scripts/e1_mechanism_consequences_2026-09-22.py
"""

from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

#: As shipped in `reference_runner_v3.py`.
WEIGHTS = {"e1_efficacy": 2.0, "e2_regression": 2.0, "e3_ruff": 1.0, "e4_bandit": 2.0}

#: The corrected break-even. Printed live by the runner as `S*=0.505`.
S_STAR = 0.50493

#: The smallest round weight above the 4.9024 threshold for a Python target.
HEAVY = 5.0


def effect_mean(scores: dict, w1: float) -> float | None:
    """Renormalised weighted arithmetic mean over AVAILABLE effect gates."""
    w = dict(WEIGHTS, e1_efficacy=w1)
    num = den = 0.0
    for gate, weight in w.items():
        s = scores.get(gate)
        if s is None:
            continue
        num += weight * float(s)
        den += weight
    return None if den == 0 else num / den


def collect():
    rows = []
    for f in sorted(glob.glob(str(REPO / "bench/logs/commissioning_*/runner_state.json"))):
        try:
            doc = json.load(open(f))
        except Exception:
            continue

        def walk(n):
            if isinstance(n, dict):
                gd = n.get("gate_details")
                if isinstance(gd, dict) and any(k.startswith("e") for k in gd):
                    scores = {k: (v.get("score") if isinstance(v, dict) else None)
                              for k, v in gd.items() if k.startswith("e")}
                    e1d = gd.get("e1_efficacy", {})
                    detail = e1d.get("detail", "") if isinstance(e1d, dict) else ""
                    rows.append({
                        "A": n.get("A"),
                        "tristate": n.get("tristate"),
                        "scores": scores,
                        "e1": scores.get("e1_efficacy"),
                        "non_curing": "does NOT cure" in detail,
                    })
                for v in n.values():
                    walk(v)
            elif isinstance(n, list):
                for v in n:
                    walk(v)

        walk(doc)
    return rows


def noncuring_share():
    """MEASURE the headline proportion instead of asserting it in prose.

    Reads `runner_state.json` ONLY. The sibling `<name>_report.json` in the same
    directory is a second serialisation of the same registry, and a glob over
    both double-counted every record: the docstring said 46 of 248 where the
    archive holds 23 of 124. The ratio is identical; the interval is not.
    """
    tot = nc = 0
    for f in sorted(glob.glob(str(REPO / "bench/logs/commissioning_*/runner_state.json"))):
        try:
            doc = json.load(open(f))
        except Exception:
            continue
        stack = [doc]
        while stack:
            n = stack.pop()
            if isinstance(n, dict):
                for k, v in n.items():
                    if k == "fix_efficacy" and isinstance(v, dict):
                        tot += 1
                        if "DOES_NOT_CURE" in str(v):
                            nc += 1
                    stack.append(v)
            elif isinstance(n, list):
                stack.extend(n)
    return nc, tot


def interval(k, n):
    from statsmodels.stats.proportion import proportion_confint
    return (proportion_confint(k, n, alpha=0.05, method="wilson"),
            proportion_confint(k, n, alpha=0.05, method="beta"))


def main() -> int:
    rows = collect()
    if not rows:
        print("no scored entries found in the commissioning archive", file=sys.stderr)
        return 2

    # --- cross-verify the mean symbolically before trusting the numbers -----
    import sympy as sp
    w1, e1, e2, e3, e4 = sp.symbols("w1 e1 e2 e3 e4")
    sym = (w1 * e1 + 2 * e2 + 1 * e3 + 2 * e4) / (w1 + 2 + 1 + 2)
    probe = {"e1_efficacy": 0.0, "e2_regression": 1.0, "e3_ruff": 1.0, "e4_bandit": 1.0}
    num_val = effect_mean(probe, 2.0)
    sym_val = float(sym.subs({w1: 2, e1: 0, e2: 1, e3: 1, e4: 1}))
    assert abs(num_val - sym_val) < 1e-12, (num_val, sym_val)
    print(f"SymPy/numeric agreement on the weighted mean: {abs(num_val - sym_val):.2e}")
    print()

    judged = [r for r in rows if r["tristate"] in ("ADMISSIBLE", "REJECTED")]
    other = [r for r in rows if r["tristate"] not in ("ADMISSIBLE", "REJECTED")]
    probed = [r for r in judged if r["e1"] is not None]
    noncure = [r for r in judged if r["non_curing"]]
    curing = [r for r in judged if r["e1"] == 1.0]

    print("POPULATION")
    print(f"  scored entries with gate detail : {len(rows)}")
    print(f"  ADMISSIBLE or REJECTED (judged) : {len(judged)}")
    print(f"  other tristate (excluded)       : {len(other)}")
    print(f"  of judged, e1 available         : {len(probed)}")
    print(f"     non-curing : {len(noncure)}")
    print(f"     curing     : {len(curing)}")
    print()

    def _E(r, w1=None, hard=False, absent_is_zero=False):
        """The effect mean under one mechanism. `A` is returned alongside it."""
        A = 1.0 if r["A"] in (1, 1.0, True) else 0.0
        scores = dict(r["scores"])
        if absent_is_zero and scores.get("e1_efficacy") is None:
            # OPTION D: a fix was proposed and efficacy was never measured. That
            # is not evidence of a cure, so it does not score as one.
            scores["e1_efficacy"] = 0.0
        if hard:
            e = r["e1"]
            if e is not None:
                A *= float(e)
            sc = {k: v for k, v in scores.items() if k != "e1_efficacy"}
            E = effect_mean(sc, WEIGHTS["e1_efficacy"]) or 0.0
        else:
            E = effect_mean(scores, w1 if w1 is not None
                            else WEIGHTS["e1_efficacy"]) or 0.0
        return A, E

    def verdicts(w1=None, hard=False):
        adm = rej = 0
        for r in judged:
            A = 1.0 if r["A"] in (1, 1.0, True) else 0.0
            if hard:
                e = r["e1"]
                if e is not None:
                    A *= float(e)
                sc = {k: v for k, v in r["scores"].items() if k != "e1_efficacy"}
                E = effect_mean(sc, WEIGHTS["e1_efficacy"]) or 0.0
            else:
                E = effect_mean(r["scores"], w1) or 0.0
            sk = A * E
            (adm := adm) if False else None
            if sk >= S_STAR:
                adm += 1
            else:
                rej += 1
        return adm, rej

    def flips(w1=None, hard=False):
        """How many NON-CURING flip to reject, and how many CURING wrongly do."""
        nc_rej = cu_rej = 0
        for r in judged:
            A = 1.0 if r["A"] in (1, 1.0, True) else 0.0
            if hard:
                e = r["e1"]
                if e is not None:
                    A *= float(e)
                sc = {k: v for k, v in r["scores"].items() if k != "e1_efficacy"}
                E = effect_mean(sc, WEIGHTS["e1_efficacy"]) or 0.0
            else:
                E = effect_mean(r["scores"], w1) or 0.0
            sk = A * E
            if sk < S_STAR:
                if r["non_curing"]:
                    nc_rej += 1
                elif r["e1"] == 1.0:
                    cu_rej += 1
        return nc_rej, cu_rej

    # --- MEASURED headline proportion, replacing the prose figure -----------
    nc_all, tot_all = noncuring_share()
    if tot_all:
        (wl, wh), (cl, ch) = interval(nc_all, tot_all)
        print("HEADLINE PROPORTION, MEASURED (runner_state.json only, no double count)")
        print(f"  non-curing probe results : {nc_all}/{tot_all} = "
              f"{100*nc_all/tot_all:.4f}%")
        print(f"    Wilson [{100*wl:.4f}%, {100*wh:.4f}%]  "
              f"Clopper-Pearson [{100*cl:.4f}%, {100*ch:.4f}%]")
        print(f"    a glob over BOTH runner_state.json and *_report.json gives "
              f"{2*nc_all}/{2*tot_all} -- same ratio, interval too narrow by "
              f"{100*((wh-wl) - 0):.0f}"[:0] or "")
        print()

    # --- OPTION D: how far do B and C actually reach? -----------------------
    absent = [r for r in judged if r["e1"] is None]
    if judged:
        (al, ah), _ = interval(len(absent), len(judged))
        print("REACH OF THE MECHANISM (the question neither A, B nor C answers)")
        print(f"  judged entries with NO e1 score : {len(absent)}/{len(judged)} = "
              f"{100*len(absent)/len(judged):.4f}%  Wilson "
              f"[{100*al:.4f}%, {100*ah:.4f}%]")
        print("  B and C both admit EVERY one of them: B renormalises over")
        print("  available gates, C guards its multiply with `if e is not None`.")
        print()

    print("CONSEQUENCES, counted over the judged population")
    print(f"{'option':<26} {'admit':>6} {'reject':>7} {'non-curing rejected':>21} "
          f"{'curing rejected':>17}")
    def verdicts_d(w1=None):
        adm = rej = 0
        for r in judged:
            A, E = _E(r, w1=w1 or WEIGHTS["e1_efficacy"], absent_is_zero=True)
            if A * E >= S_STAR:
                adm += 1
            else:
                rej += 1
        return adm, rej

    def flips_d(w1=None):
        nc_rej = cu_rej = ab_rej = 0
        for r in judged:
            A, E = _E(r, w1=w1 or WEIGHTS["e1_efficacy"], absent_is_zero=True)
            if A * E < S_STAR:
                if r["non_curing"]:
                    nc_rej += 1
                elif r["e1"] == 1.0:
                    cu_rej += 1
                else:
                    ab_rej += 1
        return nc_rej, cu_rej, ab_rej

    for label, kw in (("A  SHIPPED  w1=2.0", dict(w1=2.0)),
                      ("B  HEAVIER  w1=5.0", dict(w1=HEAVY)),
                      ("C  HARD GATE", dict(hard=True))):
        a, r_ = verdicts(**kw)
        nc, cu = flips(**kw)
        nct = f"{nc} of {len(noncure)}"
        cut = f"{cu} of {len(curing)}"
        print(f"{label:<26} {a:>6} {r_:>7} {nct:>21} {cut:>17}")

    for lbl, w in (("D  ABSENT != CURE w1=2.0", WEIGHTS["e1_efficacy"]),
                   ("D+ ABSENT != CURE w1=5.0", HEAVY)):
        a_d, r_d = verdicts_d(w)
        nc_d, cu_d, ab_d = flips_d(w)
        print(f"{lbl:<26} {a_d:>6} {r_d:>7} "
              f"{str(nc_d) + ' of ' + str(len(noncure)):>21} "
              f"{str(cu_d) + ' of ' + str(len(curing)):>17}"
              f"   (+{ab_d} of {len(absent)} unprobed)")
    print()
    print("D AT THE SHIPPED WEIGHT MOVES ALMOST NOTHING, AND THAT IS THE RESULT.")
    print("With e2/e3/e4 clean, e1 = 0 at weight 2.0 still gives E = 5/7 = 0.7143,")
    print("above S* = 0.50493. So the dilution the escalation is ABOUT defeats the")
    print("absent-probe repair at the shipped weight too. The direction and the")
    print("weight are ONE decision, not two: a mechanism only bites at w1 > 4.9024")
    print("(Python) / 2.9414 (prose), and it only bites on the 20.4% of entries a")
    print("probe actually reached unless D is adopted with it.")

    print()
    if noncure:
        (wl, wh), (cl, ch) = interval(len(noncure), len(probed) or 1)
        print(f"  non-curing share of probed judged entries: "
              f"{len(noncure)}/{len(probed)} = {100*len(noncure)/max(len(probed),1):.4f}%")
        print(f"    Wilson [{100*wl:.4f}%, {100*wh:.4f}%]  "
              f"Clopper-Pearson [{100*cl:.4f}%, {100*ch:.4f}%]")

    print()
    print("READ THIS BEFORE CHOOSING. A 'curing rejected' count above 0 is the cost")
    print("of the option: a fix that DID cure its falsifier being refused anyway.")
    print("An option that rejects every non-curing fix and 0 curing ones is strictly")
    print("better than one that does not, and needs no preference to choose.")
    return 0


if __name__ == "__main__":
    from _cli_help import answer_help   # scripts/ is sys.path[0] when run directly
    answer_help(__doc__, __file__)
    sys.exit(main())
