#!/usr/bin/env python3
"""A quarter of the project's own STEM claims are invisible to the topic's
claim patterns, because the patterns key on SYMBOLS and real prose states
properties in WORDS.

HOW THIS WAS FOUND. Driving the per-domain tool sets over
`bench/tests/fixtures/stem/` -- 29 tagged claims across 5 documents, reached by
0 live-path modules -- 7 classified as `uncategorised` and routed to 0 tools.
A classification miss is quieter than a wrong verdict: the claim simply never
reaches a tool, and the run records no opinion rather than a bad one.

THE 3 CAUSES, each established by driving the classifier on a pair that differs
only in the suspected feature.

1. GRAPH AND COMBINATORIAL PROSE HAS NO ROUTING VOCABULARY, AND THIS IS THE
   ONE THAT MATTERS. `cs_software` declares `graph_property` as a tool for
   `mathematical` claims, and **0** of that domain's claim patterns mention
   graph, path, edge, node, vertex, topological, acyclic, transitive or
   ordering. So a graph claim reaches the graph tool only if it happens to
   carry an arithmetic operator or the word "complexity":

       longest directed path visits 7 stages across 6 edges  -> uncategorised
       the longest path = 7 edges                            -> mathematical

   The tool is wired to a claim type its own subject matter cannot produce.
   That is `additive-standard`'s symmetric failure: an addition nothing
   reaches. 4 of the 7 misses are graph claims.

2. A PROPERTY STATED IN WORDS MISSES. The `mathematical` pattern requires an
   operator character or one of `formula|equation|calculat`:

       addition is not associative: 0.0 versus 1.0  -> uncategorised
       addition is not associative: 0.0 != 1.0      -> mathematical

3. AND THE SPELLED-OUT PERCENT WAS NOT THE CAUSE, WHICH IS WHY BOTH FORMS WERE
   TESTED. The first reading blamed British "per cent" against a pattern
   expecting `%`. Both miss:

       the 95 per cent level attaches to the procedure -> uncategorised
       the 95% level attaches to the procedure         -> uncategorised

   The statistics pattern is `\\d+%\\s*CI` -- the symbol must be ADJACENT TO
   `CI` -- so a sentence about a confidence level misses either way. A
   plausible cause that a 1-line control refutes is worth more than a
   plausible cause reported.

WHAT IS NOT CLAIMED. No pattern is proposed here. Widening `claim_patterns`
changes which claims the LIVE immune pipeline routes to which tools across 10
domains, and 2 of those tools were measured the same day as non-discriminating,
so widening the intake before fixing the tools would route more claims to
instruments that cannot decide them. The order matters and the decision is his.

Run: python3 scripts/the_claim_patterns_key_on_symbols_not_words_2026-11-10.py
Exit 0 while the gap reproduces, 1 once the patterns recognise graph prose --
so this cannot outlive the defect it reports.
"""
from __future__ import annotations

import pathlib
import sys
import types

GRAPH_VOCAB = ("graph", "path", "edge", "node", "vertex", "topolog",
               "acyclic", "transitive", "ordering")

PAIRS = (
    ("cs_software",
     "longest directed path visits 7 stages across 6 edges",
     "the longest path = 7 edges",
     "graph prose vs the same claim with an operator"),
    ("mathematics",
     "addition is not associative: 0.0 versus 1.0",
     "addition is not associative: 0.0 != 1.0",
     "a property in words vs the same with an operator"),
    ("statistics",
     "the 95 per cent level attaches to the procedure",
     "the 95% level attaches to the procedure",
     "spelled percent vs the symbol -- BOTH expected to miss"),
)


def _find_repo() -> pathlib.Path:
    for start in (pathlib.Path(__file__).resolve().parent,
                  pathlib.Path.cwd().resolve()):
        for cand in (start, *start.parents):
            if (cand / "bench" / "domain_immune.py").is_file():
                return cand
    raise SystemExit("cannot locate the repository")


REPO = _find_repo()


def main(argv=None) -> int:
    #: A `--help` MUST NEVER COST MINUTES -- his standing rule, and the
    #: project enforces it. This producer had no argparse at all, so `--help`
    #: was ignored and the whole measurement ran (0.91s on 2026-11-10).
    #: The description is taken from the module docstring so the usage text
    #: cannot drift from the file.
    import argparse
    _ap = argparse.ArgumentParser(
        description=(__doc__ or "").strip().splitlines()[0] if __doc__ else "")
    _ap.parse_args(argv)
    sys.path.insert(0, str(REPO))
    sys.path.insert(0, str(REPO / "bench"))
    sys.path.insert(0, str(REPO / "bench" / "tests" / "fixtures" / "stem"))
    import domain_immune as di

    def view(t: str):
        return types.SimpleNamespace(description=t, finding_id="F",
                                     title="", evidence="")

    print("=" * 78)
    print("THE CLAIM PATTERNS KEY ON SYMBOLS; REAL STEM PROSE USES WORDS")
    print("=" * 78)

    for dom, plain, symbolic, label in PAIRS:
        cfg = di.load_domain_config(dom)
        a, _ = di.domain_classify_claim(view(plain), cfg)
        b, _ = di.domain_classify_claim(view(symbolic), cfg)
        print(f"\n  {dom} — {label}")
        print(f"    {a:15s} {plain[:62]}")
        print(f"    {b:15s} {symbolic[:62]}")

    cfg = di.load_domain_config("cs_software")
    pats = getattr(cfg, "claim_patterns", {}) or {}
    mentions = sum(1 for plist in pats.values() for p in plist
                   for w in GRAPH_VOCAB if w in str(p).lower())
    declares = [ct for ct in pats
                if "graph_property" in (di.domain_b_cell_tools(ct, cfg) or [])]
    print(f"\n  cs_software patterns mentioning graph vocabulary: {mentions}")
    print(f"  claim types that declare `graph_property`: {declares}")

    # The corpus count, if the fixtures are reachable.
    try:
        import stem_fixtures as sf
        MAP = {"structural / mechanical engineering": "engineering",
               "statistics": "statistics", "chemistry / metrology": "chemistry",
               "algorithms / complexity": "cs_software",
               "numerical analysis": "mathematics"}
        tot = unc = 0
        for f in sf.load_all():
            c2 = di.load_domain_config(MAP.get(getattr(f, "domain", ""),
                                               "cross_domain"))
            for c in (getattr(f, "claims", None) or []):
                tot += 1
                ct, _ = di.domain_classify_claim(
                    view(getattr(c, "summary", "") or ""), c2)
                unc += (ct == "uncategorised")
        from statsmodels.stats.proportion import proportion_confint
        w = proportion_confint(unc, tot, alpha=0.05, method="wilson")
        print(f"\n  corpus claims routed to 0 tools: {unc} of {tot} "
              f"= {unc / tot:.6f}  Wilson [{w[0]:.6f}, {w[1]:.6f}]")
    except Exception as exc:                                  # noqa: BLE001
        print(f"\n  corpus unavailable ({type(exc).__name__}), count omitted "
              f"rather than guessed")

    gap = mentions == 0 and bool(declares)
    print("\n" + "=" * 78)
    if gap:
        print("  GAP REPRODUCES — `graph_property` is declared for a claim")
        print("  type whose patterns recognise no graph vocabulary, so graph")
        print("  prose reaches it only by an incidental operator.")
    else:
        print("  GAP DOES NOT REPRODUCE — the patterns now recognise graph")
        print("  vocabulary. Retire this producer.")
    print("=" * 78)
    return 0 if gap else 1


if __name__ == "__main__":
    raise SystemExit(main())
