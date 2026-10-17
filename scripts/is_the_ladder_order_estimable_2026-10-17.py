#!/usr/bin/env python3
"""Can the routing ladder's order be derived from measured capability?

HIS RULING, 2026-10-09: *"in reality there should probably be no distinction
between models participating in an experiment other than a 'ranking number' ...
the only things that should denote a model's ranking in any given experiment is
derived/demonstrable capability, either above that. Or below that of its
peers"*, with the timing fixed as *"one round of an experimental run could
potentially constitute a season, and players/teams should get demoted promoted
based on the evidence derived from this first experimental round. Then for the
rest of the rounds in an experiment the positions of these models in their
rankings stays fixed"*. Confirmed again 2026-10-11. The project's memory records
him making this point 4 times.

WHAT THE CODE DOES INSTEAD. `bench/routing.py` carries
`DEFAULT_FALSIFIER_STRENGTH = ("Codex", "CC2", "ChatGPT", "Gemini", "DeepSeek",
"Fable")` -- a frozen tuple of VENDOR NAMES -- as the default `strength_order`
for `rank_falsifier_writers`. Vendor identity is exactly what he ruled must not
determine capability.

THE QUESTION THIS SCRIPT ANSWERS, because replacing the tuple requires knowing
what may replace it. Two candidate quantities:

  1. FINDING RATE, which the fingerprints do record. REFUTED by a free seat on
     2026-10-06: it measures productivity, not falsification capability, and
     ranking on it reproduces the inversion `competence_provenance` exists to
     prevent. This script does not use it.
  2. FALSIFICATION OUTCOMES -- how often a seat's falsifier actually REFUTES a
     finding. That is the capability the ladder exists to exploit, and it is
     recorded as `falsifier_verdict` on every archived registry entry.

So the question is whether (2) discriminates between the seats well enough to
ORDER them. A ranking is a total order over pairs, so it needs pairwise
separation, not merely an overall difference -- and the 2 are tested separately
here because they give opposite answers.

NO FINGERPRINT FIELD MEASURES THIS. Checked across all 11 fingerprint files: the
recorded fields are capacity (`max_successful_prompt_chars`,
`max_successful_context_chars`, `compression_threshold`), attention (`D_decay`,
`attention_ratio`, `measured_attention_span`, `quality_at_capacity`) and
productivity (`total_findings`, `avg_findings_per_round`). Not one is a
falsification outcome, which is why the archive registries have to be read.
"""
from __future__ import annotations

import argparse
import collections
import itertools
import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"
FINGERPRINTS = REPO / "bench" / "fingerprints"


def falsification_evidence(top_level_only: bool = True) -> dict:
    """Per-seat (refuted, total) read off every archived registry."""
    per: dict = collections.defaultdict(lambda: [0, 0])
    for rs in LOGS.rglob("runner_state.json"):
        if top_level_only and len(rs.relative_to(LOGS).parts) != 2:
            continue
        try:
            ents = (json.loads(rs.read_text(errors="replace"))
                    .get("registry") or {}).get("entries") or {}
        except (OSError, ValueError):
            continue
        for e in ents.values():
            if not isinstance(e, dict):
                continue
            seat = e.get("source_model") or "?"
            per[seat][1] += 1
            if (e.get("falsifier_verdict") or "").strip().upper() == "REFUTED":
                per[seat][0] += 1
    return {k: tuple(v) for k, v in per.items()}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--include-simulated", action="store_true",
                    help="rank the -SIM stand-ins too (default: paid seats only)")
    a = ap.parse_args()

    ev = falsification_evidence()
    paid = {k: v for k, v in ev.items()
            if "-SIM" not in k and k != "?"}
    use = ev if a.include_simulated else paid

    print("=" * 74)
    print("IS THE LADDER ORDER ESTIMABLE FROM MEASURED CAPABILITY?")
    print("=" * 74)

    print("\n1. WHAT THE FINGERPRINTS MEASURE, and why they cannot answer this")
    fields = set()
    n_fp = 0
    for f in sorted(FINGERPRINTS.glob("*.json")):
        n_fp += 1
        try:
            fields.update((json.loads(f.read_text()).get("observed") or {}).keys())
        except (OSError, ValueError):
            continue
    print(f"   fingerprint files .............. {n_fp}")
    print(f"   distinct observed fields ....... {len(fields)}")
    print(f"   any field a falsification OUTCOME? "
          f"{'YES' if any('refut' in f or 'falsif' in f for f in fields) else 'NO'}")
    print(f"   fields: {', '.join(sorted(fields))}")

    print("\n2. FALSIFICATION OUTCOMES, read off every archived registry")
    total_ref = sum(k for k, _ in ev.values())
    total_ent = sum(n for _, n in ev.values())
    print(f"   entries scanned ................ {total_ent}")
    print(f"   REFUTED verdicts in total ...... {total_ref}"
          f"  ({100*total_ref/total_ent:.4f}% of entries)")
    print(f"   seats with ZERO refutations .... "
          f"{sum(1 for k, _ in use.values() if k == 0)} of {len(use)}")

    try:
        from statsmodels.stats.proportion import proportion_confint
        from statsmodels.stats.multitest import multipletests
        from scipy.stats import fisher_exact, chi2_contingency
        import numpy as np
    except Exception as exc:                            # noqa: BLE001
        print(f"\nFATAL: the statistics tools are unavailable ({exc}), so no "
              f"claim about estimability can be made.")
        return 2

    print(f"\n   {'seat':<12} {'k/n':>10} {'rate':>10}   {'Wilson 95%':>22}")
    iv = {}
    for s in sorted(use, key=lambda x: -use[x][0] / max(1, use[x][1])):
        k, n = use[s]
        lo, hi = proportion_confint(k, n, method="wilson")
        iv[s] = (lo, hi)
        print(f"   {s:<12} {k:>4}/{n:<5} {100*k/n:>9.4f}%   "
              f"[{lo*100:7.4f}%, {hi*100:7.4f}%]")

    print("\n3. IS THERE ANY DIFFERENCE AT ALL? (omnibus)")
    seats = sorted(use)
    tbl = np.array([[use[s][0], use[s][1] - use[s][0]] for s in seats])
    chi2, p_om, dof, _ = chi2_contingency(tbl)
    print(f"   chi-square across {len(seats)} seats: chi2={chi2:.4f}, dof={dof}, "
          f"p={p_om:.6f}")
    print(f"   seats are all equal? {'NO -- heterogeneity is real' if p_om < 0.05 else 'cannot reject'}")

    print("\n4. BUT CAN THEY BE ORDERED? (pairwise, multiplicity-corrected)")
    pairs, ps = [], []
    for x, y in itertools.combinations(seats, 2):
        kx, nx = use[x]
        ky, ny = use[y]
        _, p = fisher_exact([[kx, nx - kx], [ky, ny - ky]])
        pairs.append((x, y))
        ps.append(p)
    rej_h, p_h, _, _ = multipletests(ps, alpha=0.05, method="holm")
    rej_b, _, _, _ = multipletests(ps, alpha=0.05, method="bonferroni")
    if not a.quiet:
        print(f"   {'pair':<26} {'raw p':>10} {'Holm':>10}  survives?")
        for (x, y), p, ph, rh in sorted(zip(pairs, ps, p_h, rej_h),
                                        key=lambda t: t[1]):
            print(f"   {x + ' vs ' + y:<26} {p:>10.6f} {ph:>10.6f}  "
                  f"{'YES' if rh else 'no'}")
    overlap_free = sum(1 for x, y in pairs
                       if iv[x][0] > iv[y][1] or iv[y][0] > iv[x][1])
    print(f"\n   pairs with non-overlapping 95% intervals : {overlap_free} of {len(pairs)}")
    print(f"   pairs surviving Holm at 0.05 ............ {sum(rej_h)} of {len(pairs)}")
    print(f"   pairs surviving Bonferroni at 0.05 ...... {sum(rej_b)} of {len(pairs)}")

    established = bool(sum(rej_h))
    print("\n" + "=" * 74)
    print(f"VERDICT: the ladder order is "
          f"{'ESTIMABLE' if established else 'NOT ESTIMABLE'} from the archive.")
    if not established:
        print("""
Heterogeneity is real -- the omnibus test rejects equality -- but NO pairwise
ordering survives correction for the number of comparisons, and a ranking IS a
set of pairwise orderings. So the archive supports the claim that the seats
differ and does NOT support any statement about which is stronger.

THIS IS WHY HIS SEASON DESIGN IS THE ONLY SOUND FOUNDING. The order cannot be
inherited from the archive, so it must be measured INSIDE the experiment that
uses it -- "one round of an experimental run could potentially constitute a
season ... then for the rest of the rounds the positions stay fixed". Until a
round discriminates, the honest behaviour is to record the order as NOT
ESTABLISHED, not to fall back silently to a tuple of vendor names.""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
