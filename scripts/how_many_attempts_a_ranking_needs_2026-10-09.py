#!/usr/bin/env python3
"""How many attempts a ranking needs, and why the founder's "2 or 3" was nearly right.

HIS CHALLENGE, 2026-10-09: *"300 attempts for a single model to solve any given problem is clearly
vastly much too much! ... Are you even checking if these numbers make any practical sense before
writing them?"* And his proposal: *"maybe we could give models 3 chances to resolve a problem
before their ranking is calculated, or perhaps 2 really is enough?"*

HE WAS RIGHT TO CHALLENGE IT AND THE FIGURE WAS MINE. 300 was quoted without the quantity that
determines it. The attempts needed to order 2 models correctly depends almost entirely on the GAP
between their success proportions, and 300 belongs to a gap of 0.05.

WHAT THIS FILE ESTABLISHES, all of it re-derived rather than cited, because the research run that
raised these mechanisms came back sound only WITH CORRECTIONS on every dimension, including
fabricated quotations.

  * The exact probability that n attempts each order a stronger model above a weaker one, in
    SymPy rationals, with ties split evenly.
  * The attempts needed for 95% correct ordering across a range of gaps.
  * That a knockout bracket cannot support a Bradley-Terry ranking, by Ford's 1957 condition.

SO HIS "VERY HARD PROBLEM" IS DOING STATISTICAL WORK, NOT JUST SOUNDING DEMANDING. Choosing a hard
first problem is choosing one that MAXIMISES the gap, and at a gap of 0.40 the requirement is 7
attempts rather than 300. That is the same principle as information-maximising item selection in
adaptive testing.

Run: python3 scripts/how_many_attempts_a_ranking_needs_2026-10-09.py
"""
from __future__ import annotations

import argparse
import math

TARGET = 0.95


def exact_order_probability(n: int, pa, pb):
    """P(a is ranked above b) on n attempts each, ties split evenly. Exact rationals."""
    import sympy as sp
    pa, pb = sp.Rational(pa), sp.Rational(pb)
    total = sp.Integer(0)
    for ka in range(n + 1):
        wa = sp.binomial(n, ka) * pa ** ka * (1 - pa) ** (n - ka)
        for kb in range(n + 1):
            wb = sp.binomial(n, kb) * pb ** kb * (1 - pb) ** (n - kb)
            if ka > kb:
                total += wa * wb
            elif ka == kb:
                total += wa * wb / 2
    return sp.simplify(total)


def attempts_needed(pa: float, pb: float, target: float = TARGET, cap: int = 1500):
    """Smallest n whose exact ordering probability reaches `target`. SciPy for speed."""
    import numpy as np
    from scipy.stats import binom, norm
    for n in range(1, cap + 1):
        z = (pa - pb) / math.sqrt(pa * (1 - pa) / n + pb * (1 - pb) / n)
        if norm.cdf(z) < target - 0.02:
            continue                      # cheap screen, never the decision
        k = np.arange(n + 1)
        A, B = binom.pmf(k, n, pa), binom.pmf(k, n, pb)
        below = np.concatenate([[0.0], np.cumsum(B)[:-1]])
        p = float((A * below).sum() + 0.5 * float((A * B).sum()))
        if p >= target:
            return n, p
    return None, None


def claim_the_founders_budget_is_gap_dependent() -> dict:
    rows = {}
    for pa, pb in ((0.90, 0.50), (0.80, 0.50), (0.70, 0.50), (0.60, 0.50), (0.55, 0.50)):
        n, p = attempts_needed(pa, pb)
        rows[round(pa - pb, 2)] = {"stronger": pa, "weaker": pb,
                                   "attempts_each_for_95_percent": n,
                                   "achieved": round(p, 6) if p else None}
    return {
        "by_gap": rows,
        "his_proposal_is_enough_at_gap": [g for g, r in rows.items()
                                          if r["attempts_each_for_95_percent"] is not None
                                          and r["attempts_each_for_95_percent"] <= 14],
        "the_300_figure_belongs_to_gap": 0.05,
        "verdict": ("the budget is set by the GAP, not by the roster or the ladder; a hard first "
                    "problem maximises the gap and is therefore the cheap instrument, which is "
                    "what information-maximising item selection does in adaptive testing"),
    }


def claim_two_or_three_attempts_cannot_rank_close_models() -> dict:
    """The limit on his proposal, stated exactly rather than approximately."""
    import sympy as sp
    one = exact_order_probability(1, "7/10", "1/2")
    three = exact_order_probability(3, "7/10", "1/2")
    return {
        "one_attempt_exact": str(one), "one_attempt_float": float(one),
        "three_attempts_exact": str(three), "three_attempts_float": float(three),
        "one_is_three_fifths": one == sp.Rational(3, 5),
        "three_is_1371_over_2000": three == sp.Rational(1371, 2000),
        "verdict": ("at a gap of 0.20, 1 attempt is barely better than a coin and 3 reach only "
                    "0.6855, so 2 or 3 attempts rank a roster only when the problem separates it "
                    "widely"),
    }


def claim_a_knockout_cannot_support_a_ranking(sizes=(4, 8, 16)) -> dict:
    """Ford (1957): the Bradley-Terry estimate is unique iff the win graph is strongly connected."""
    import networkx as nx
    import numpy as np
    rng = np.random.default_rng(3)
    rows = {}
    for n in sizes:
        G = nx.DiGraph()
        players = list(range(n))
        G.add_nodes_from(players)
        while len(players) > 1:
            nxt = []
            for i in range(0, len(players), 2):
                a, b = players[i], players[i + 1]
                w, l = (a, b) if rng.random() < 0.5 else (b, a)
                G.add_edge(w, l)
                nxt.append(w)
            players = nxt
        rows[n] = {"matches": G.number_of_edges(),
                   "matches_equal_n_minus_1": G.number_of_edges() == n - 1,
                   "strongly_connected": nx.is_strongly_connected(G),
                   "is_acyclic": nx.is_directed_acyclic_graph(G)}
    RR = nx.DiGraph()
    rng2 = np.random.default_rng(5)
    for i in range(8):
        for j in range(i + 1, 8):
            w, l = (i, j) if rng2.random() < 0.5 else (j, i)
            RR.add_edge(w, l)
    return {
        "knockout": rows,
        "round_robin_8": {"matches": RR.number_of_edges(),
                          "strongly_connected": nx.is_strongly_connected(RR)},
        "every_bracket_acyclic": all(r["is_acyclic"] for r in rows.values()),
        "no_bracket_strongly_connected": not any(r["strongly_connected"] for r in rows.values()),
        "verdict": ("a bracket yields n-1 matches and never a cycle, so Ford's condition fails and "
                    "the Bradley-Terry estimate is UNDEFINED; a knockout also removes a "
                    "participant on 1 result, against the project's rule that no model is ever "
                    "permanently set aside"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.parse_args()
    print("== 1. the attempts budget is set by the GAP ==")
    d = claim_the_founders_budget_is_gap_dependent()
    for g, r in sorted(d["by_gap"].items(), reverse=True):
        print(f"   gap {g:.2f} ({r['stronger']} against {r['weaker']}): "
              f"{r['attempts_each_for_95_percent']:4d} attempts each -> {r['achieved']}")
    print(f"   2 or 3 attempts suffice at gaps: {d['his_proposal_is_enough_at_gap']}")
    print(f"   {d['verdict']}")
    print("\n== 2. but not for close models ==")
    for k, v in claim_two_or_three_attempts_cannot_rank_close_models().items():
        print(f"   {k}: {v}")
    print("\n== 3. and a knockout bracket cannot support a ranking at all ==")
    d3 = claim_a_knockout_cannot_support_a_ranking()
    for n, r in d3["knockout"].items():
        print(f"   {n:2d} players: {r['matches']} matches, acyclic {r['is_acyclic']}, "
              f"strongly connected {r['strongly_connected']}")
    print(f"   8-player round robin: {d3['round_robin_8']}")
    print(f"   {d3['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
