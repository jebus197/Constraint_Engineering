#!/usr/bin/env python3
"""Measure what his "areas of functionality" partition would actually buy.

HIS INSTRUCTION, 2026-10-17: "The registry can be organised into different
areas of functionality, again just like the Windows registry, so you don't need
to risk wasting time searching through every issue every single time to
find/ID one particular issue."

THE BRIEF HE ATTACHED makes a stronger claim than that, and the two must not be
conflated. Gemini Web's brief (Responses/design_brief.txt) proposes a RocksDB
or LMDB B-tree for path resolution and an SQLite FTS5 inverted index for word
search, justified by "sub-millisecond, highly accurate query lookups". His own
justification is organisational -- not having to look through everything to
find one issue. Those are different claims and only one of them needs a new
storage engine.

So this measures 3 things rather than assuming any of them:

  1. WHAT A LOOKUP COSTS NOW, per tier, over the real store. If the existing
     lookups are already well under a millisecond, the brief's performance
     justification is answered and a new engine would be churn -- a C
     dependency and a second copy of the data that can drift from the log.
  2. WHETHER AN AREA IS DERIVABLE FROM DATA THAT ALREADY EXISTS. `subjects`
     holds the code identifiers a ticket concerns; the module that DEFINES
     each identifier is the functional area. If coverage is high, the partition
     is a VIEW over the existing log and needs no schema change at all.
  3. WHAT THE PARTITION SAVES, as a reduction in the set a search must touch.
     That is the figure his instruction actually asks for.

Every figure carries an interval, and each is computed twice by different
libraries, per the 21 April 2026 two-tool rule.

Usage: python3 scripts/what_would_partitioning_the_register_buy_2026-10-17.py
"""
from __future__ import annotations

import pathlib
import statistics
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

try:
    from answer_help_without_cost import answer_help  # noqa: F401
except Exception:  # pragma: no cover - the helper is optional here
    def answer_help(doc, path):
        if "--help" in sys.argv or "-h" in sys.argv:
            print(doc)
            raise SystemExit(0)

SAMPLE = 200
WARMUP = 20


def _interval(values):
    """Mean with a 95% t-interval, computed twice by different libraries."""
    import numpy as np
    import scipy.stats as st

    arr = np.asarray(values, dtype=float)
    n = arr.size
    mean_np = float(arr.mean())
    mean_stat = statistics.fmean(values)
    sem = float(st.sem(arr))
    lo, hi = st.t.interval(0.95, n - 1, loc=mean_np, scale=sem)
    # Cross-check the half-width by hand against mpmath rather than trusting
    # one library's tail function.
    import mpmath as mp
    tcrit = float(mp.findroot(
        lambda x: mp.quad(
            lambda u: mp.gamma((n) / 2) / (mp.sqrt((n - 1) * mp.pi)
                                           * mp.gamma((n - 1) / 2))
            * (1 + u ** 2 / (n - 1)) ** (-n / 2), [-mp.inf, x]) - 0.975, 2.0))
    hand_hw = tcrit * sem
    return {
        "n": n, "mean": mean_np, "lo": float(lo), "hi": float(hi),
        "median": float(np.median(arr)),
        "p95": float(np.percentile(arr, 95)),
        "mean_agrees": abs(mean_np - mean_stat) < 1e-12,
        "interval_agrees": abs((hi - mean_np) - hand_hw) < 1e-6,
    }


def _proportion(k, n):
    """A proportion with Wilson and Clopper-Pearson, cross-checked."""
    from statsmodels.stats.proportion import proportion_confint
    import scipy.stats as st

    w = proportion_confint(k, n, method="wilson")
    b = proportion_confint(k, n, method="beta")
    cp_hi = 1.0 if k == n else float(st.beta.ppf(0.975, k + 1, n - k))
    return {
        "k": k, "n": n, "pct": 100.0 * k / n,
        "wilson": (w[0] * 100, w[1] * 100),
        "cp": (b[0] * 100, b[1] * 100),
        "cp_agrees": abs(b[1] - cp_hi) < 1e-9,
    }


def _owning_module(identifier: str, index: dict) -> str:
    return index.get(identifier, "")


def _definition_index() -> dict:
    """Which module DEFINES each identifier. Parsed, not grepped."""
    import ast

    index: dict[str, str] = {}
    for path in sorted((REPO / "bench").glob("*.py")) + \
            sorted((REPO / "scripts").glob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, SyntaxError):
            continue
        rel = str(path.relative_to(REPO))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef)):
                index.setdefault(node.name, rel)
    return index


def _parse(argv=None) -> None:
    """A REAL PARSER, so an unknown flag FAILS instead of being ignored.

    `answer_help` answers `--help` but accepts anything else silently, which is
    this project's "118-day no-op" shape: a script that takes `--fix-whatever`
    and does nothing with it reports success for work it never did. This
    measurement takes no options at all, so saying so explicitly is the whole
    of it.
    """
    import argparse
    parser = argparse.ArgumentParser(
        prog=pathlib.Path(__file__).name,
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__)
    parser.parse_args(argv)


def main() -> int:
    _parse()
    from bench.ticket_store import TicketStore

    t0 = time.perf_counter()
    store = TicketStore()
    store.load()
    load_ms = (time.perf_counter() - t0) * 1000.0
    tickets = store.all()
    print("THE REGISTER AS IT STANDS")
    print(f"  tickets                 : {len(tickets)}")
    print(f"  log lines               : "
          f"{len((REPO / 'bench/tickets/tickets.jsonl').read_text().splitlines())}")
    print(f"  one full load           : {load_ms:.2f} ms")

    if len(tickets) < 50:
        print("  too few tickets to measure; stopping rather than quoting a "
              "figure from a sample this small.")
        return 1

    import random
    rng = random.Random(20261017)
    sample = rng.sample(tickets, min(SAMPLE, len(tickets)))

    print("\n1. WHAT A LOOKUP COSTS NOW, PER TIER")
    timings: dict[str, list[float]] = {
        "get(tid) exact": [], "similar() hash tiers": [],
        "similar_by_words()": [], "candidates() all 4": []}
    for t in sample[:WARMUP]:
        store.get(t.tid)
        store.similar(t.verbatim)
    for t in sample:
        s = time.perf_counter()
        store.get(t.tid)
        timings["get(tid) exact"].append((time.perf_counter() - s) * 1000)

        s = time.perf_counter()
        store.similar(t.verbatim)
        timings["similar() hash tiers"].append((time.perf_counter() - s) * 1000)

        s = time.perf_counter()
        store.similar_by_words(t.verbatim)
        timings["similar_by_words()"].append((time.perf_counter() - s) * 1000)

        s = time.perf_counter()
        store.candidates(t.kind, t.verbatim, task_ref=t.task_ref,
                         anchor=t.anchor)
        timings["candidates() all 4"].append((time.perf_counter() - s) * 1000)

    for name, values in timings.items():
        st_ = _interval(values)
        print(f"  {name:<22}: mean {st_['mean']:.4f} ms "
              f"[{st_['lo']:.4f}, {st_['hi']:.4f}]  "
              f"median {st_['median']:.4f}  p95 {st_['p95']:.4f}")
        print(f"  {'':<22}  numpy and statistics agree: {st_['mean_agrees']}; "
              f"scipy and mpmath agree on the interval: {st_['interval_agrees']}")

    sub_ms = {k: _interval(v)["p95"] < 1.0 for k, v in timings.items()}
    print(f"  tiers already under 1 ms at the 95th percentile: "
          f"{sum(sub_ms.values())} of {len(sub_ms)}")
    slow = [k for k, ok in sub_ms.items() if not ok]
    if slow:
        print(f"  NOT already sub-millisecond: {slow}")

    print("\n2. IS AN AREA DERIVABLE FROM WHAT THE LOG ALREADY HOLDS?")
    index = _definition_index()
    print(f"  identifiers defined across bench/ and scripts/: {len(index)}")
    with_subjects = [t for t in tickets if t.subjects]
    resolved, areas = 0, {}
    for t in tickets:
        mods = {_owning_module(s, index) for s in t.subjects}
        mods.discard("")
        if mods:
            resolved += 1
            for m in mods:
                areas.setdefault(m, 0)
                areas[m] += 1
    p_sub = _proportion(len(with_subjects), len(tickets))
    p_res = _proportion(resolved, len(tickets))
    print(f"  carry any subject       : {p_sub['k']} of {p_sub['n']} = "
          f"{p_sub['pct']:.4f}%  Wilson [{p_sub['wilson'][0]:.4f}%, "
          f"{p_sub['wilson'][1]:.4f}%]")
    print(f"  resolve to a module     : {p_res['k']} of {p_res['n']} = "
          f"{p_res['pct']:.4f}%  Wilson [{p_res['wilson'][0]:.4f}%, "
          f"{p_res['wilson'][1]:.4f}%]")
    print(f"    Clopper-Pearson [{p_res['cp'][0]:.4f}%, {p_res['cp'][1]:.4f}%]"
          f"  scipy agrees: {p_res['cp_agrees']}")
    print(f"  distinct areas found    : {len(areas)}")
    for mod, count in sorted(areas.items(), key=lambda kv: -kv[1])[:8]:
        print(f"    {count:>4}  {mod}")

    print("\n3. WHAT THE PARTITION SAVES")
    if not areas:
        print("  no area resolves, so the partition cannot be measured and "
              "must not be claimed.")
        return 1
    import numpy as np
    sizes = np.asarray(sorted(areas.values()), dtype=float)
    print(f"  searching everything touches  : {len(tickets)} tickets")
    print(f"  searching one area touches    : median {np.median(sizes):.1f}, "
          f"mean {sizes.mean():.1f}, max {int(sizes.max())}")
    saving = 1.0 - float(np.median(sizes)) / len(tickets)
    print(f"  median reduction in the scanned set: {100*saving:.4f}%")
    print("  BUT NOTE THE DENOMINATOR: a reduction in tickets scanned is only")
    print("  a time saving if scanning is what costs. Section 1 above says")
    print("  what scanning costs; read the two together before building.")

    print("\n4. A BETTER AREA KEY THAN SUBJECTS ALONE")
    print("  Subjects resolve for 1 ticket in 9, so an area derived from them")
    print("  alone would put 8 in 9 in an 'unknown' bucket -- which is the")
    print("  whole-store scan it was meant to avoid, wearing a label. So the")
    print("  key is measured as a FALLBACK CHAIN and each rung is reported.")
    rungs = {"module from subjects": 0, "task_ref prefix": 0,
             "source": 0, "nothing": 0}
    assigned = {}
    for t in tickets:
        mods = {_owning_module(s, index) for s in t.subjects}
        mods.discard("")
        if mods:
            rungs["module from subjects"] += 1
            assigned[t.tid] = sorted(mods)[0]
        elif t.task_ref:
            rungs["task_ref prefix"] += 1
            head = "".join(c for c in t.task_ref if c.isalpha()) or "?"
            assigned[t.tid] = f"task:{head}"
        elif t.source:
            rungs["source"] += 1
            assigned[t.tid] = f"source:{t.source}"
        else:
            rungs["nothing"] += 1
    for name, count in rungs.items():
        pr = _proportion(count, len(tickets))
        print(f"  {name:<22}: {pr['k']:>4} of {pr['n']} = {pr['pct']:7.4f}%  "
              f"Wilson [{pr['wilson'][0]:.4f}%, {pr['wilson'][1]:.4f}%]")
    covered = _proportion(len(tickets) - rungs["nothing"], len(tickets))
    print(f"  COVERED BY THE CHAIN   : {covered['k']} of {covered['n']} = "
          f"{covered['pct']:.4f}%  Wilson [{covered['wilson'][0]:.4f}%, "
          f"{covered['wilson'][1]:.4f}%]")
    buckets = {}
    for area in assigned.values():
        buckets[area] = buckets.get(area, 0) + 1
    sizes = sorted(buckets.values())
    print(f"  distinct areas          : {len(buckets)}")
    print(f"  largest area holds      : {sizes[-1] if sizes else 0} tickets "
          f"({100*(sizes[-1] if sizes else 0)/len(tickets):.4f}% of the store)")
    print("  A PARTITION IS ONLY WORTH HAVING IF NO BUCKET IS MOST OF THE")
    print("  STORE. The largest figure above is the one that decides it.")
    for area, count in sorted(buckets.items(), key=lambda kv: -kv[1])[:8]:
        print(f"    {count:>4}  {area}")

    print("\n5. WHAT AN IN-MEMORY POSTINGS INDEX WOULD DO TO THE WORD LAYER")
    print("  The brief proposes SQLite FTS5 or a BM25 tokeniser. The store")
    print("  already loads wholly into memory in "
          f"{load_ms:.0f} ms, so a token->tid")
    print("  dict built at load time gets the same asymptotic win with no new")
    print("  dependency and no second copy on disk that can drift from the")
    print("  log. Prototyped HERE, and timed, before anything is built.")
    # The threshold is a CLASS attribute on the store, not a module global.
    # Importing it as a global raised on the first call, which is why this
    # prototype is executed rather than only written.
    from bench.ticket_store import _norm_tokens
    WORD_OVERLAP_SURFACE = TicketStore.WORD_OVERLAP_SURFACE

    t_build = time.perf_counter()
    postings: dict[str, set[str]] = {}
    sizes_tok: dict[str, int] = {}
    for t in tickets:
        # THE LIVE METHOD FALLS BACK TO THE TITLE when verbatim is empty. The
        # first prototype indexed verbatim only, which was 1 of 3 reasons it
        # agreed with the live answer on 2 of 200 queries.
        toks = set(_norm_tokens(t.verbatim or t.title or ""))
        sizes_tok[t.tid] = len(toks)
        for tok in toks:
            postings.setdefault(tok, set()).add(t.tid)
    build_ms = (time.perf_counter() - t_build) * 1000.0
    print(f"  index build             : {build_ms:.2f} ms, "
          f"{len(postings)} distinct tokens")
    print("  WHY THE POSTINGS SET IS EXACT AND NOT AN APPROXIMATION: a ticket")
    print("  scoring overlap >= 0.95 must share at least 0.95 of the query's")
    print("  tokens, so it appears in the postings list of at least 1 query")
    print("  token. The postings union is therefore a SUPERSET of the answer,")
    print("  and scoring within it reproduces the live ranking exactly.")

    by_tid = {t.tid: t for t in tickets}
    indexed_ms, agree, checked = [], 0, 0
    for t in sample:
        s = time.perf_counter()
        wanted = set(_norm_tokens(t.verbatim))
        hits = []
        if wanted:
            counts: dict[str, int] = {}
            for tok in wanted:
                for tid in postings.get(tok, ()):
                    counts[tid] = counts.get(tid, 0) + 1
            scored = []
            for tid, shared in counts.items():
                if not sizes_tok[tid]:
                    continue
                # DENOMINATOR IS THE QUERY'S TOKEN COUNT, and the live method
                # does NOT exclude the query's own ticket. Both were wrong in
                # the first prototype.
                overlap = shared / len(wanted)
                if overlap >= WORD_OVERLAP_SURFACE:
                    scored.append((overlap, by_tid[tid]))
            scored.sort(key=lambda pair: (-pair[0], pair[1].tid))
            hits = [x for _, x in scored]
        indexed_ms.append((time.perf_counter() - s) * 1000)
        baseline = [x.tid for x in store.similar_by_words(t.verbatim)]
        checked += 1
        if [x.tid for x in hits] == baseline:
            agree += 1
    st_i = _interval(indexed_ms)
    st_b = _interval(timings["similar_by_words()"])
    print(f"  indexed word search     : mean {st_i['mean']:.4f} ms "
          f"[{st_i['lo']:.4f}, {st_i['hi']:.4f}]  p95 {st_i['p95']:.4f}")
    print(f"  current word search     : mean {st_b['mean']:.4f} ms "
          f"[{st_b['lo']:.4f}, {st_b['hi']:.4f}]  p95 {st_b['p95']:.4f}")
    if st_i["mean"] > 0:
        print(f"  speed-up on the mean    : {st_b['mean']/st_i['mean']:.2f}x")
    ag = _proportion(agree, checked)
    print(f"  SAME ORDERED ANSWER AS THE LIVE METHOD: {ag['k']} of {ag['n']} = "
          f"{ag['pct']:.4f}%  Wilson [{ag['wilson'][0]:.4f}%, "
          f"{ag['wilson'][1]:.4f}%]")
    print("  AN INDEX THAT IS FASTER AND WRONG IS NOT AN IMPROVEMENT. The")
    print("  agreement figure above is the one that licenses building it; a")
    print("  speed-up alone does not.")

    print("\nTHE ANSWER")
    print("  His organisational request and the brief's performance claim are")
    print("  separate. The figures above settle which of them is outstanding.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
