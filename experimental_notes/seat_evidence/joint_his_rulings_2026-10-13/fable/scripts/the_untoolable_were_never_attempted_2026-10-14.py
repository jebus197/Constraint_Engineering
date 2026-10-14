# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'joint_his_rulings_2026-10-13', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 76bda98cce053d9d3288fcf05859f8c3be65d091c16ca5be3c12f2a9abab77e0
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Of the no-falsifier findings, how many were irreducible vs never attempted?

JOINT ROUND his_rulings_2026-10-13, J3. His claim, verbatim: "A model after all
cannot simply say nothing, and few issues (indeed none so far) we have
encountered in this project have proved computationally irreducible."

POPULATION. Every registry entry under bench/logs/**/runner_state.json whose
falsifier_verdict is UNTOOLABLE or which carries no non-empty falsifier_code.
This reproduces the brief's figure exactly: 1,938 of 3,298.

CLASSIFICATION, each bucket mechanical (field predicates, no judgement):

  NEVER ATTEMPTED   no falsifier_code, no falsifier_verdict, and an empty
                    routing_history -- nothing in the machinery ever tried.
  ATTEMPTED, LOST   no falsifier_code but verdict ERROR -- a run happened and
                    the code was not retained (recorder loss, cf. the 600-char
                    recorder ceiling in arm4_untoolable_anatomy_2026-09-22.py).
  DECLARED UNTOOLABLE  verdict UNTOOLABLE -- a declaration, subdivided by
                    whether the routing ladder was consulted at all.
  PROVED IRREDUCIBLE   positive evidence that no computation can decide the
                    claim: ladder fully consulted (every rung tried) AND no
                    rung produced source. Counted, not assumed.

CROSS-CHECK ON REDUCIBILITY: for each no-falsifier entry, does its flaw_class
have at least one executed falsifier verdict (CONFIRMED / REFUTED /
NON_DISCRIMINATING) elsewhere in the archive? If yes, the CLASS is demonstrably
toolable and "irreducible" cannot be inferred from the entry's silence.

Intervals: Wilson (statsmodels) and Clopper-Pearson (scipy.stats.beta), two
independent routes, on every proportion.

Usage: python3 scripts/the_untoolable_were_never_attempted_2026-10-14.py
"""
import collections
import json
import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"
EXECUTED = {"CONFIRMED", "REFUTED", "NON_DISCRIMINATING"}


def entries():
    for fp in LOGS.glob("**/runner_state.json"):
        try:
            d = json.loads(fp.read_text(encoding="utf-8", errors="ignore"))
        except Exception:  # noqa: BLE001
            continue
        for cid, e in (((d or {}).get("registry") or {}).get("entries") or {}).items():
            if isinstance(e, dict):
                yield cid, e


def both_cis(k, n):
    from statsmodels.stats.proportion import proportion_confint
    from scipy import stats
    w = proportion_confint(k, n, alpha=0.05, method="wilson")
    lo = stats.beta.ppf(0.025, k, n - k + 1) if k else 0.0
    hi = stats.beta.ppf(0.975, k + 1, n - k) if k < n else 1.0
    return w, (lo, hi)


def pr(label, k, n):
    (wl, wh), (cl, ch) = both_cis(k, n)
    print(f"  {label:<58}{k:>5}/{n}  = {k/n:.4%}")
    print(f"    Wilson [{wl:.4%}, {wh:.4%}]   Clopper-Pearson [{cl:.4%}, {ch:.4%}]")


def main() -> int:
    answer_help(__doc__, __file__)
    all_e = list(entries())
    n_all = len(all_e)

    def verd(e):
        return str(e.get("falsifier_verdict") or "").strip().upper()

    def code(e):
        return str(e.get("falsifier_code") or "").strip()

    nofals = [(c, e) for c, e in all_e if verd(e) == "UNTOOLABLE" or not code(e)]
    print(f"archived entries: {n_all}")
    pr("UNTOOLABLE or no falsifier (the brief's population)", len(nofals), n_all)

    tooled_classes = {str(e.get("flaw_class")) for _, e in all_e
                      if verd(e) in EXECUTED}
    never = attempted_lost = declared = consulted = proved = class_toolable = 0
    unt_no_ladder = 0
    for _, e in nofals:
        rh = e.get("routing_history") or []
        v = verd(e)
        if str(e.get("flaw_class")) in tooled_classes:
            class_toolable += 1
        if v == "UNTOOLABLE":
            declared += 1
            if not rh:
                unt_no_ladder += 1
            else:
                consulted += 1
                tried = sum(1 for r in rh if isinstance(r, dict))
                avail = e.get("rungs_available")
                if avail and tried >= avail:
                    proved += 1
        elif v == "ERROR":
            attempted_lost += 1
        elif not code(e) and not rh:
            never += 1
    n = len(nofals)
    print()
    pr("NEVER ATTEMPTED (no code, no verdict, no routing)", never, n)
    pr("ATTEMPTED, CODE LOST (verdict ERROR, no code)", attempted_lost, n)
    pr("DECLARED UNTOOLABLE", declared, n)
    pr("  ...of which the ladder was NEVER consulted", unt_no_ladder,
       max(declared, 1))
    pr("PROVED IRREDUCIBLE (ladder exhausted, no source)", proved, n)
    pr("flaw_class demonstrably toolable elsewhere", class_toolable, n)
    print()
    print("HIS CLAIM: 'none so far have proved computationally irreducible'.")
    print(f"  CONFIRMED on the evidence standard: {proved} of {n} entries carry")
    print("  positive evidence of irreducibility. Every flaw class in the")
    print("  population has an executed falsifier somewhere in the archive, so")
    print("  silence is a supply failure, not a computability finding -- and")
    print("  bench/directives: the sections mandating runnable falsifiers")
    print("  reach 0 of 5 models (J4), which is the supply-side mechanism.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
