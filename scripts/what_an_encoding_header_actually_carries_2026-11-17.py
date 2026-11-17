#!/usr/bin/env python3
"""Which fields an expert encoding's header actually carries, and under which predicate.

B185 quotes a census of the 52 encodings -- 38 carrying `VERSION:` and 1 carrying
a confirmation date -- and cites
`scripts/standards_currency_and_model_staleness_2026-11-13.py` as its evidence.
That script NEVER READS `bench/directives`: the word appears in its prose only.
So those 2 figures were not reproducible from anything committed, which is
`measured-rate-travels-with-its-script` broken at the point it matters, and a
re-derivation under broader patterns gave 45 and 5 instead. This script exists so
the census has a producer and so the DISAGREEMENT IS VISIBLE rather than
arbitrated by whoever measured last.

THE POINT IS THAT A FIELD CENSUS IS PREDICATE-DEPENDENT, so the predicate is
reported beside every count. `VERSION:` anchored to the start of a line is not
the same question as `VERSION` anywhere; a confirmation date spelled `CONFIRMED:`
is not the same question as any of `CONFIRMED`, `LAST-CHECKED`, `CHECKED` or
`CONFIRMATION` followed by a date. Both readings are computed and both are
printed, because reporting 1 of them as "the" census is how 2 instruments come to
hold 2 populations.

WHY IT MATTERS BEYOND TIDINESS. B161's remaining piece persists a researcher's
profile so it reloads on every restart. A reloaded profile points at an encoding,
and an encoding whose currency cannot be established is one that can be reloaded
silently after the standard beneath it has moved -- which is the hazard B185
names. The share of encodings whose staleness is CHECKABLE is therefore a
precondition on that persistence, not a side observation.
"""
from __future__ import annotations

import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
DIRECTIVES = REPO / "bench" / "directives"

#: predicate name -> compiled pattern. Each is a DIFFERENT question.
FIELDS = {
    "VERSION: at line start": re.compile(r"^VERSION:", re.M),
    "VERSION anywhere": re.compile(r"\bVERSION\b", re.I),
    "SEVERITY SCALE:": re.compile(r"^SEVERITY SCALE:", re.M),
    "SOURCES:": re.compile(r"^SOURCES:", re.M),
    "TIER:": re.compile(r"^TIER:", re.M),
    "CONFIRMED: + a date": re.compile(r"^CONFIRMED:[^\n]{0,40}\d{4}-\d{2}-\d{2}", re.M),
    "any confirm-word + a date": re.compile(
        r"(CONFIRMED|LAST[- ]CHECKED|CHECKED|CONFIRMATION)[^\n]{0,40}\d{4}-\d{2}-\d{2}", re.I),
}

#: the currency question: an encoding is CHECKABLE against upstream only if it
#: carries a date to compare. Which predicate counts as "a date" is the whole
#: disagreement, so the narrow and broad readings are both reported.
CURRENCY = ("CONFIRMED: + a date", "any confirm-word + a date")


def _cli(doc: str) -> None:
    """Answer --help WITHOUT reading a single encoding."""
    import argparse                                        # noqa: PLC0415
    argparse.ArgumentParser(
        description=doc.strip().split("\n")[0],
        epilog="Takes no options. Running it performs the census.",
    ).parse_args()


def encodings() -> list[pathlib.Path]:
    """Every expert encoding, which B185 establishes are the .txt files here."""
    return sorted(DIRECTIVES.rglob("*.txt"))


def census(paths: list[pathlib.Path]) -> dict[str, list[pathlib.Path]]:
    out: dict[str, list[pathlib.Path]] = {k: [] for k in FIELDS}
    for p in paths:
        txt = p.read_text(encoding="utf-8", errors="replace")
        for name, rx in FIELDS.items():
            if rx.search(txt):
                out[name].append(p)
    return out


def main(argv: list[str] | None = None) -> int:
    _cli(__doc__)
    print(__doc__.strip().split("\n")[0])
    print()

    if not DIRECTIVES.is_dir():
        print(f"  {DIRECTIVES} is absent; nothing to census")
        return 1

    from statsmodels.stats.proportion import proportion_confint  # noqa: PLC0415
    import mpmath as mp                                          # noqa: PLC0415
    mp.mp.dps = 40

    paths = encodings()
    n = len(paths)
    print(f"== {n} encoding(s) under bench/directives ==")
    hits = census(paths)
    for name in FIELDS:
        k = len(hits[name])
        w = proportion_confint(k, n, method="wilson")
        c = proportion_confint(k, n, method="beta")
        print(f"   {name:28s} {k:3d} of {n} = {k / n:.6f}  "
              f"Wilson [{w[0]:.4f}, {w[1]:.4f}]  CP [{c[0]:.4f}, {c[1]:.4f}]")
    print()

    print("== the currency question, under BOTH readings ==")
    for name in CURRENCY:
        k = len(hits[name])
        print(f"   checkable under {name!r}: {k} of {n}; "
              f"UNCHECKABLE: {n - k}")
    narrow, broad = (len(hits[c]) for c in CURRENCY)
    print(f"   the 2 readings differ by {broad - narrow} encoding(s), which is why "
          f"neither may be quoted as 'the' figure without its predicate")
    print()

    print("== against what B185 records ==")
    print("   B185 states 38 of 52 carrying VERSION: and 1 of 52 carrying a")
    print("   confirmation date, citing a producer that never reads this folder.")
    v_narrow = len(hits["VERSION: at line start"])
    #: REPORTED SEPARATELY, because 1 of the 2 reproduces EXACTLY and the other
    #: does not, and calling that "the pair does not reproduce" would discard a
    #: confirmation. The anchored VERSION reading lands on B185's own figure; the
    #: broad one gives 45, which is the predicate-dependence this script exists
    #: to make visible rather than a contradiction.
    v_ok = v_narrow == 38
    d_ok = narrow == 1 or broad == 1
    print(f"   VERSION: at line start -> {v_narrow} of {n}; "
          f"B185 records 38 -> reproduces EXACTLY: {v_ok}")
    print(f"   a confirmation date    -> {narrow} of {n} narrow, {broad} of {n} "
          f"broad; B185 records 1 -> matched by either reading: {d_ok}")
    if v_ok and not d_ok:
        print("   -> so B185's VERSION census is CONFIRMED, and its date census")
        print("      uses a 3rd predicate that neither reading here recovers.")
        print("      That is not a refutation: what is established is that its")
        print("      cited producer cannot settle it either way, because that")
        print("      producer never reads this folder.")
    print()
    print("== VERDICT ==")
    print("   the census now has a producer: True")
    print(f"   staleness checkable for {narrow} to {broad} of {n} encodings, so a")
    print("   profile that reloads automatically can point at an encoding whose")
    print(f"   currency cannot be established in {n - broad} to {n - narrow} cases.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
