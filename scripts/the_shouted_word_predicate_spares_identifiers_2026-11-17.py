#!/usr/bin/env python3
"""The shouted-word check refused the entry codes Rule 32 requires.

`bench/tests/test_a_response_is_not_a_ruling_2026-11-09.py` holds that a
derived "still owed" sentence must read as English, and treats any token that
`str.isupper()` as shouting. Two classes of correct prose were caught by it:

  * a capitalised article -- "A real board has now proven it" -- where the
    predicate already spares "I", so sparing legitimate single-letter words is
    its own intent and "A" was simply missed;
  * a BARE ENTRY CODE such as `B202`, which `an-identifier-never-travels-alone`
    (note standard Rule 32) positively REQUIRES to be written beside its
    descriptor. The predicate already spares tokens holding a backtick,
    underscore, slash, hyphen or paren, so sparing identifiers is also its
    intent; the plain `B202` shape fell through.

So this is a guard accusing correct prose, which this project has measured
before: of 36 failures in one full-suite baseline, 9 were guards accusing
correct code, and fixing the subject in any of them would have made the code
worse to satisfy a broken check.

THE LIMIT IS STATED BECAUSE IT IS SMALL. Only 15 entries derive an owed
sentence, and the old predicate flagged 2 tokens in them. 2 of 2 were false
positives -- Wilson [0.342380, 1.000000], Clopper-Pearson [0.158114,
1.000000], the second bound reproduced from the exact binomial tail -- which
bounds the share very loosely. The positive controls below are HAND-WRITTEN
rather than drawn from the corpus, so they establish that detection power is
retained on obvious cases, not that it is retained in general.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent

ENTRY_CODE = re.compile(r"[A-Z]\d{1,4}")
SINGLE_CAP = re.compile(r"[A-Z]")
STRIP = ".,;:!?)"
SKIP_CHARS = ("`", "_", "/", "-", "(")


def shouted_old(s: str) -> list[str]:
    """The predicate as it stood before 2026-11-17."""
    return [w for w in s.split()
            if w.strip(STRIP).isupper()
            and w.strip(STRIP) != "I"
            and not any(c in w for c in SKIP_CHARS)]


def shouted_new(s: str) -> list[str]:
    """The predicate in force: identifiers and single-letter words spared."""
    out = []
    for w in s.split():
        t = w.strip(STRIP)
        if not t.isupper():
            continue
        if t in ("I", "A"):
            continue
        if ENTRY_CODE.fullmatch(t):
            continue
        if any(c in w for c in SKIP_CHARS):
            continue
        out.append(w)
    return out


#: Sentences that MUST still be caught, and sentences that must now pass.
CONTROLS = [
    ("This is STILL OWED and URGENT.", True),
    ("Nothing is owed. OPEN until proven.", True),
    ("The entry is BLOCKED pending his ruling.", True),
    ("A real board proved it, tracked as B202, the silent board.", False),
    ("I kept A note on B195, the unwatchable board.", False),
    ("Nothing is owed on part 2.", False),
]


def owed_sentences() -> list[tuple[str, str]]:
    """Every derived 'still owed' sentence, via the producer that builds them."""
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location(
        "bdf_shout", REPO / "scripts" / "build_decisions_file_2026-11-07.py")
    bdf = importlib.util.module_from_spec(spec)
    sys.modules["bdf_shout"] = bdf
    spec.loader.exec_module(bdf)
    import task_list_markers as tlm           # noqa: PLC0415

    out = []
    for e in tlm.parse_entries():
        v = bdf.derive_still_owed(e.text)
        if v:
            out.append((e.ident, bdf._owed_sentence(v)))
    return out


def _cli(doc: str) -> None:
    """Answer --help WITHOUT running the measurement.

    `a --help must never cost money`: 15 of 17 runners in this project once
    billed for the flag. This parser takes no options and exists so the flag
    prints usage and exits before anything is measured.
    """
    import argparse                                        # noqa: PLC0415
    argparse.ArgumentParser(
        description=doc.strip().split("\n")[0],
        epilog="Takes no options. Running it performs the measurement.",
    ).parse_args()


def main() -> int:
    _cli(__doc__)
    print(__doc__.strip().split("\n")[0])
    print()

    rows = owed_sentences()
    print(f"== the live corpus: {len(rows)} derived owed sentence(s) ==")
    old_hits = [(i, w) for i, s in rows for w in shouted_old(s)]
    new_hits = [(i, w) for i, s in rows for w in shouted_new(s)]
    print(f"   old predicate flags : {len(old_hits)} {[w for _, w in old_hits]}")
    print(f"   new predicate flags : {len(new_hits)} {[w for _, w in new_hits]}")

    codes = [(i, w) for i, w in old_hits if ENTRY_CODE.fullmatch(w.strip(STRIP))]
    arts = [(i, w) for i, w in old_hits if SINGLE_CAP.fullmatch(w.strip(STRIP))]
    real = [(i, w) for i, w in old_hits if (i, w) not in codes and (i, w) not in arts]
    print(f"     of the old flags, entry codes      : {len(codes)}")
    print(f"     of the old flags, single capitals   : {len(arts)}")
    print(f"     of the old flags, genuine shouting  : {len(real)}")
    print()

    print("== detection power retained? positive and negative controls ==")
    ok = True
    for text, should_flag in CONTROLS:
        hits = shouted_new(text)
        good = bool(hits) == should_flag
        ok &= good
        verdict = "OK " if good else "BAD"
        print(f"   {verdict} expect_flag={str(should_flag):5s} got={str(hits):30s} "
              f"{text[:46]}")
    print()

    print("== intervals on the false-positive share of the OLD predicate ==")
    if old_hits:
        from statsmodels.stats.proportion import proportion_confint  # noqa: PLC0415
        k, n = len(codes) + len(arts), len(old_hits)
        w = proportion_confint(k, n, method="wilson")
        c = proportion_confint(k, n, method="beta")
        print(f"   {k} of {n} = {k / n:.6f}")
        print(f"   Wilson [{w[0]:.6f}, {w[1]:.6f}]  "
              f"Clopper-Pearson [{c[0]:.6f}, {c[1]:.6f}]")
        print("   n is small; this bounds the share loosely and is reported as such.")
    else:
        print("   the old predicate flags nothing on the current corpus, so the")
        print("   share is not estimable today. The repair stands on the controls.")
    print()

    clean = not new_hits and ok and not real
    print("== VERDICT ==")
    print(f"   old flags that were genuine shouting : {len(real)} (expected 0)")
    print(f"   new predicate flags on the corpus    : {len(new_hits)} (expected 0)")
    print(f"   all controls behave                  : {ok}")
    print(f"   repair justified: {clean}")
    return 0 if clean else 1


if __name__ == "__main__":
    sys.exit(main())
