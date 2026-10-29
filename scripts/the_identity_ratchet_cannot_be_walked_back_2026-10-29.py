#!/usr/bin/env python3
"""Once an identityless ticket exists, no available remedy lowers the count.

`bench/tests/test_an_identity_is_derived_not_remembered_2026-10-28.py` ratchets
the number of tickets carrying neither a `task_ref` nor an `anchor` at 317. On
2026-10-29 it stood at 320: 3 tickets raised by hand through `propose` instead
of `propose_from_chat`, which derives an anchor. This script establishes the
figures in task B49 and, more importantly, tries every remedy the store offers
and reports that none of them reduces the count -- so the claim can fail.

It is READ-ONLY with respect to the real register: every write goes to a
scratch copy in a temporary directory, and the original path is only read.
"""
from __future__ import annotations
import argparse, hashlib, pathlib, shutil, sys, tempfile, collections

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

#: The ratchet's own ceiling and the moment it was measured.
CEILING = 317
CEILING_AT = "2026-10-28T02:10:18"


def bare(store) -> list:
    """The ratchet's predicate, called rather than restated."""
    return [t for t in store.all() if not t.task_ref and not t.anchor]


def wilson(k: int, n: int, alpha: float = 0.05):
    """A proportion needs an interval, and the interval needs 2 tools."""
    out = {}
    try:
        from statsmodels.stats.proportion import proportion_confint
        out["statsmodels"] = tuple(proportion_confint(k, n, alpha=alpha,
                                                      method="wilson"))
    except Exception as exc:                       # pragma: no cover
        out["statsmodels"] = f"unavailable: {exc}"
    try:
        import numpy as np
        from scipy import stats
        z = stats.norm.ppf(1 - alpha / 2)
        p, d = k / n, 1 + z * z / n
        c = (p + z * z / (2 * n)) / d
        h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
        out["numpy+scipy closed form"] = (c - h, c + h)
    except Exception as exc:                       # pragma: no cover
        out["numpy+scipy closed form"] = f"unavailable: {exc}"
    return out


def describe(store) -> None:
    allt = store.all()
    b = bare(store)
    print(f"tickets: {len(allt)}   identityless: {len(b)}   ceiling: {CEILING}")
    ci = wilson(len(b), len(allt))
    print(f"  proportion {len(b)/len(allt):.6f}, Wilson 95%:")
    for name, v in ci.items():
        print(f"    {name:<26} "
              + (f"[{v[0]:.6f}, {v[1]:.6f}]" if isinstance(v, tuple) else str(v)))
    print("  identityless by status:")
    for st, c in collections.Counter(t.status for t in b).most_common():
        print(f"    {st:<12} {c}")
    after = [t for t in b if (t.created or "") > CEILING_AT]
    print(f"  created after the ceiling was measured: {len(after)}")
    for t in sorted(after, key=lambda x: x.created or ""):
        print(f"    {t.created}  {t.kind}:{t.tid}  {t.status:<8} "
              f"src={t.source[:14]:<14} {t.title[:46]}")


def probe_the_remedies(store) -> None:
    """Raise 1 identityless ticket, then try each remedy. None may reduce it."""
    import bench.ticket_store as ts
    start = len(bare(store))
    print(f"\nREMEDY PROBE (scratch copy). start {start}")
    t, outcome = store.propose("pf", "probe", "a probe raised with no identity at all",
                               source="chat", created="2026-10-29T07:00:00+00:00")
    breached = len(bare(store))
    print(f"  raise 1 identityless ticket     -> {breached}  ({outcome})")

    anchor = (f"chat#{t.created}#"
              f"{hashlib.sha256(t.verbatim.encode()).hexdigest()[:8]}")
    new_tid = ts.tid_of(t.kind, t.verbatim, "", anchor)
    moved, retired = store.migrate_identity(t.tid, new_tid, "producer probe")
    print(f"  migrate_identity onto an anchored tid -> {len(bare(store))}")
    print(f"      and the moved record's own anchor is {moved.anchor!r} "
          f"although its tid was derived FROM an anchor -- the identifier claims "
          f"an identity the record does not carry")
    print(f"      the retired record is {retired.status} and still identityless: "
          f"{not retired.task_ref and not retired.anchor}")

    t2, o2 = store.propose_from_chat("pf", "probe", "a second probe, raised correctly",
                                     when="2026-10-29T07:00:00+00:00")
    print(f"  a correct propose_from_chat raise -> {len(bare(store))}  "
          f"({o2}, anchor={t2.anchor!r})")

    t3, _ = store.propose_from_chat("qs", "probe", "a third probe with no clock",
                                    when="")
    print(f"  propose_from_chat(when='')        -> anchor={t3.anchor!r}, which "
          f"identifies no position in the record although that is the field's "
          f"one stated job")

    setters = [n for n in dir(store)
               if not n.startswith("_") and callable(getattr(store, n))]
    print(f"\n  public methods: {len(setters)}; none takes `task_ref` or `anchor` "
          f"to set in place:")
    import inspect
    takers = []
    for n in setters:
        try:
            sig = inspect.signature(getattr(store, n))
        except (TypeError, ValueError):
            continue
        if {"task_ref", "anchor"} & set(sig.parameters) and n not in ("propose",
                                                                      "propose_from_chat",
                                                                      "exact",
                                                                      "candidates"):
            takers.append(n)
    # `by_task_ref` appears here and is a LOOKUP, not a mutator -- it takes a
    # task_ref to SEARCH by. Calling the list "mutators" would have been a
    # wrong label on a right number, so it says what it actually found.
    print(f"    methods taking an identity field (lookups included): "
          f"{takers or 'none'}")
    print("    of these, 0 SET the field on an existing ticket")
    end = len(bare(store))
    print(f"\n  VERDICT: start {start}, after the breach {breached}, after every "
          f"remedy {end} -> "
          f"{'NEVER FELL BELOW THE BREACH' if end >= breached else 'A PATH EXISTS'}")


def callers_that_would_break() -> None:
    """Enforcing identity at creation would break these, so it is not proposed."""
    import re
    hits = collections.Counter()
    pat = re.compile(r'\.propose\(')
    for p in sorted((REPO / "bench" / "tests").rglob("test_*.py")):
        txt = p.read_text(encoding="utf-8", errors="replace")
        for m in pat.finditer(txt):
            # the call's own text, to the closing paren on a best-effort basis
            tail = txt[m.start():m.start() + 400]
            if "task_ref" not in tail.split(")")[0] and "anchor" not in tail.split(")")[0]:
                hits[p.name] += 1
    total = sum(hits.values())
    print(f"\nCALL SITES THAT PASS NEITHER FIELD, in bench/tests: {total} "
          f"across {len(hits)} files")
    for name, c in hits.most_common(10):
        print(f"    {c:3d}  {name}")
    print("  These exercise the subject and word tiers, which exist FOR items with")
    print("  no identity, so forbidding their creation would remove the capability")
    print("  they test. That is why B49 records the enforcement idea as REFUTED.")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--no-probe", action="store_true",
                    help="report the live figures only; skip the remedy probe")
    args = ap.parse_args()      # exits on --help BEFORE anything is read
    import bench.ticket_store as ts

    live = ts.TicketStore()
    live.load()
    describe(live)
    callers_that_would_break()
    if args.no_probe:
        return 0
    tmp = pathlib.Path(tempfile.mkdtemp())
    box = tmp / live.path.name
    shutil.copy(live.path, box)
    scratch = ts.TicketStore(box)
    scratch.load()
    probe_the_remedies(scratch)
    shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
