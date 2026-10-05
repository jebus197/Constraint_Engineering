# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'fingerprint_ladder_review_2026-10-05', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: c9d3edc214e39fc53950ea14ac2574095f582084ed2e74e390558d9ce4f9381e
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The ladder's selection effect ATTENUATES the measured spread. It does not invert it.

WHAT THIS DECIDES. `experimental_notes/Proposal_Fingerprint_Falsification_Dimension_
2026-10-05.md` names as its "strongest objection" that ladder assignment could
"demote exactly the models it should promote", and recommends measuring on
FIRST-PASS falsifiers only on the ground that those are "a common population by
construction". This script tests both halves under an explicit latent-difficulty
model and finds the proposal has them the wrong way round.

THE MODEL, stated so it can be attacked. Finding j has latent difficulty d_j.
Model i has ability a_i. P(i resolves j) = sigmoid(a_i - d_j). This is the
one-parameter logistic (Rasch) form -- the standard model for "an agent of some
ability faces an item of some difficulty" -- chosen because it is the simplest
form in which the question is even well-posed, not because it is fitted to this
project's data. IT IS NOT FITTED. See REFUTED BY, below.

RESULT A. Ladder assignment (strongest first, only unresolved findings pass down)
does NOT invert a correct order. Each later rung inherits a population the earlier
rungs could not resolve, i.e. a harder one -- and later rungs are by construction
the WEAKER models. So the bias pushes weak models further down. It is monotone in
the direction that preserves a correct ranking. Kendall tau vs truth = +1.000.

RESULT B. With the TRUE-strongest model moved to the LAST rung, its measured rate
still ranks 1 of 5 at an ability gap of 2.6 logits -- so the feedback loop does not
even reliably lock in a wrong order at this separation. What it DOES do is compress
the measured spread by a factor of about 0.36 (0.265 vs 0.731), which costs
statistical power to order models, not the order itself.

RESULT C. First-pass-only -- the proposal's recommendation -- is NOT a common
population. Each model generates its own first-pass findings, so the population is
SELF-SELECTED. Parameterising that as an "ambition" coefficient (how much a
stronger model raises the difficulty of what it bothers to report):

    ambition 0.0 -> tau +1.000, spread 0.466   (no self-selection)
    ambition 0.5 -> tau +1.000, spread 0.258
    ambition 1.0 -> tau +0.600, spread 0.004   SIGNAL GONE
    ambition 1.5 -> tau -1.000, spread 0.260   ORDER INVERTED
    ambition 2.0 -> tau -1.000, spread 0.468   ORDER INVERTED
    eps-random   -> tau +1.000, spread 0.489   (unaffected, by construction)

So the failure the proposal fears -- inversion -- is produced by the mitigation it
recommends, and not by the assignment it blames. Ambition is UNOBSERVED and is
under the measured model's own control: a model raises its first-pass confirm rate
by reporting only defects it can already demonstrate. That is a metric the measured
agent can move, which is the property this project's own reward-hacking notes treat
as disqualifying.

THE MITIGATION THAT SURVIVES. Randomise the rung on a fraction eps of routable
findings and estimate on that subsample only. Assignment is then independent of
difficulty by construction rather than by assumption, so no difficulty measure,
no covariate and no stratification is needed. eps = 0 reproduces today's behaviour
exactly, so it is additive and reversible. Cost is bounded by eps x max_rungs extra
dispatches.

REFUTED BY, concretely:
  * Fitting a_i and d_j to the archived routing outcomes in
    `bench/logs/*/runner_state.json` (`routing_history` carries the rung tried and
    the verdict) and finding the measured spread is NOT compressed relative to a
    randomised baseline -- that would refute RESULT A/B.
  * Measuring the real ambition coefficient from archived first-pass findings --
    regress each finding's realised difficulty on its source model's rung position
    -- and finding it below about 0.5 for every seat. That would make first-pass-only
    adequate and refute RESULT C.
  * Either result holding under a 2-parameter (discrimination + difficulty) model
    where it fails under the Rasch form.

Run:  python3 scripts/ladder_selection_effect_attenuates_not_inverts_2026-10-05.py
"""
from __future__ import annotations

import argparse
import sys

import numpy as np
from scipy.stats import kendalltau

TRUE = np.array([2.0, 1.4, 0.8, 0.2, -0.6])      # ability, strongest first
NAMES = ["M0", "M1", "M2", "M3", "M4"]


def _parse_args(argv=None):
    p = argparse.ArgumentParser(
        prog="ladder_selection_effect_attenuates_not_inverts_2026-10-05.py",
        description=__doc__.split("\n\n")[0])
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--n", type=int, default=200_000, help="findings per ladder pass")
    return p.parse_args(argv)


def _sig(x):
    return 1.0 / (1.0 + np.exp(-x))


def ladder_rates(rng, order, n):
    d = rng.normal(0, 1, n)
    alive = np.ones(n, bool)
    num = np.zeros(5)
    den = np.zeros(5)
    for i in order:
        idx = np.flatnonzero(alive)
        if idx.size == 0:
            break
        ok = rng.random(idx.size) < _sig(TRUE[i] - d[idx])
        den[i] += idx.size
        num[i] += ok.sum()
        alive[idx[ok]] = False
    return num / np.maximum(den, 1)


def eps_random_rates(rng, n=120_000):
    d = rng.normal(0.4, 1, n)                    # a routed-like harder population
    who = rng.integers(0, 5, n)
    out = np.zeros(5)
    for i in range(5):
        s = who == i
        out[i] = (rng.random(int(s.sum())) < _sig(TRUE[i] - d[s])).mean()
    return out


def first_pass_rates(rng, ambition, n=40_000):
    out = np.zeros(5)
    for i in range(5):
        own = rng.normal(TRUE[i] * ambition, 1, n)
        out[i] = (rng.random(n) < _sig(TRUE[i] - own)).mean()
    return out


def _tau(r):
    return kendalltau(np.arange(5), -r)[0]


def main(argv=None) -> int:
    args = _parse_args(argv)
    rng = np.random.default_rng(args.seed)
    print("=" * 78)
    print("A. DOES LADDER ASSIGNMENT INVERT A CORRECT ORDER?")
    print("=" * 78)
    r = ladder_rates(rng, [0, 1, 2, 3, 4], args.n)
    print(f"  rates {np.round(r, 4)}  tau vs truth {_tau(r):+.3f}  "
          f"spread {r.max() - r.min():.3f}")
    print("  NO. Later rungs inherit a harder population AND are the weaker models,")
    print("  so the bias is monotone in the order-preserving direction.")

    print()
    print("=" * 78)
    print("B. A MIS-ORDERED LADDER: TRUE-STRONGEST TRIED LAST")
    print("=" * 78)
    r2 = ladder_rates(rng, [4, 3, 2, 1, 0], args.n)
    rank = int(np.argsort(-r2).tolist().index(0)) + 1
    print(f"  rates {np.round(r2, 4)}  spread {r2.max() - r2.min():.3f}")
    print(f"  the true-best model ranks {rank} of 5 by measured rate")
    print(f"  spread ratio vs the correctly-ordered ladder: "
          f"{(r2.max() - r2.min()) / (r.max() - r.min()):.3f}")
    print("  -> the cost is COMPRESSION (lost power to order), not inversion.")

    print()
    print("=" * 78)
    print("C. IS FIRST-PASS-ONLY A COMMON POPULATION?  (the proposal says yes)")
    print("=" * 78)
    print(f"  {'ambition':>10s} {'rates':>42s} {'tau':>7s} {'spread':>7s}")
    for amb in (0.0, 0.5, 1.0, 1.5, 2.0):
        fp = first_pass_rates(rng, amb)
        print(f"  {amb:10.1f} {str(np.round(fp, 3)):>42s} {_tau(fp):+7.3f} "
              f"{fp.max() - fp.min():7.3f}")
    er = eps_random_rates(rng)
    print(f"  {'eps-random':>10s} {str(np.round(er, 3)):>42s} {_tau(er):+7.3f} "
          f"{er.max() - er.min():7.3f}")
    print("  -> NO. The population is self-selected, the signal vanishes at")
    print("     ambition 1.0 and the order INVERTS above it. Ambition is")
    print("     unobserved and is under the measured model's own control.")
    print()
    print("THE MITIGATION THAT SURVIVES: randomise the rung on a fraction eps of")
    print("routable findings; estimate on that subsample only. eps = 0 reproduces")
    print("today exactly. See this file's docstring for what would refute all of it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
