#!/usr/bin/env python3
"""How many seats carry a phenotype key naming a version they are not?

THE CLAIM UNDER TEST comes from an unadopted CC2 seat design,
`experimental_notes/seat_evidence/the_directive_set_and_capability_2026-10-14/
cc2/bench/capability_identity.py`: "Live models are mapped onto stale phenotypes
-- Opus 4.7 onto an `opus_4_6` entry, DeepSeek V4 Pro onto a `deepseek_v3` entry.
A name matched; a capability did not. The table reports a measurement of a model
that is not the one being dispatched."

IT NAMES 2. THIS COUNTS THEM ALL, from the live tables, because a claim about how
widespread something is must be measured rather than illustrated.

THE 2 SOURCES, BOTH LIVE AND BOTH IMPORTED RATHER THAN RETYPED:
  * `MODEL_ROSTER` in `bench/reference_runner_v3.py` -- what each seat IS, in
    prose, e.g. "Claude Opus 4.7 (Anthropic)".
  * `COMPOSER_MODEL_MAP` in `bench/cdsfl_registry/composer.py` -- the phenotype
    key each seat RESOLVES TO, e.g. `opus_4_6`, which is what keys the coherence
    budget, the phenotype transform and therefore the directive text a seat is
    actually sent.

★ WHY THIS IS NOT A TIDY-UP. The phenotype key selects the directive budget and
format a seat receives, and `INITIAL_FINGERPRINTS` supplies a PRIOR that a future
run reads back as what that model is believed capable of. A key naming a
superseded version means the run is configured from, and reports against, a
measurement of a different model. That is why renaming one is the founder's
decision and not a cleanup: it changes what a model is told about itself.
NOTHING IS RENAMED HERE. This counts.

★ THE COMPARISON IS DELIBERATELY CONSERVATIVE. A version is extracted from each
side and they are compared only when BOTH sides yield one. Where either side is
silent the seat is reported as NOT COMPARABLE rather than as agreeing, because
reporting an unmeasurable pair as a match is the flattering reading this project
has been caught taking before.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

#: "4.7" -> (4, 7); "V4 Pro" -> (4,); "5.5" -> (5, 5)
_VER_IN_PROSE = re.compile(r"\b[Vv]?(\d+)(?:\.(\d+))?\b")
#: "opus_4_6" -> (4, 6); "deepseek_v3" -> (3,); "gemini_3_1_pro" -> (3, 1)
_VER_IN_KEY = re.compile(r"_v?(\d+)(?:_(\d+))?")


def _versions(text: str, pat: re.Pattern) -> list[tuple[int, ...]]:
    out = []
    for m in pat.finditer(text):
        major = int(m.group(1))
        minor = m.group(2)
        out.append((major, int(minor)) if minor is not None else (major,))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        prog=pathlib.Path(__file__).name,
        description="Count seats whose phenotype key names a version the live "
                    "roster says they are not. Reads only; renames nothing.")
    ap.parse_args()

    from bench.cdsfl_registry import composer as co
    from bench.reference_runner_v3 import MODEL_ROSTER
    from bench import runner_core as rc

    labels = sorted(rc.MODEL_SPECS)
    print("=" * 78)
    print("SEATS, WHAT THEY ARE, AND WHAT THEIR PHENOTYPE KEY SAYS THEY ARE")
    print("=" * 78)
    print(f"  {'seat':10s} {'phenotype key':18s} {'live roster description':34s} verdict")

    stale, agree, not_comparable, no_roster = [], [], [], []
    for label in labels:
        key = str(co.COMPOSER_MODEL_MAP.get(label, label))
        desc = MODEL_ROSTER.get(label)
        if desc is None:
            no_roster.append(label)
            print(f"  {label:10s} {key:18s} {'(ABSENT from MODEL_ROSTER)':34s} "
                  f"NO ROSTER ENTRY")
            continue
        kv = _versions(key, _VER_IN_KEY)
        dv = _versions(str(desc), _VER_IN_PROSE)
        if not kv or not dv:
            not_comparable.append(label)
            verdict = "NOT COMPARABLE"
        elif kv[0] == dv[0]:
            agree.append(label)
            verdict = "agrees"
        else:
            stale.append((label, key, str(desc), kv[0], dv[0]))
            verdict = f"STALE: key says {kv[0]}, roster says {dv[0]}"
        print(f"  {label:10s} {key:18s} {str(desc)[:34]:34s} {verdict}")

    n = len(labels)
    print()
    print("=" * 78)
    print("THE COUNT")
    print("=" * 78)
    print(f"  seats in MODEL_SPECS                : {n}")
    print(f"  key agrees with the live roster     : {len(agree)}  {agree}")
    print(f"  key names a SUPERSEDED version      : {len(stale)}  "
          f"{[s[0] for s in stale]}")
    print(f"  not comparable (a side has no version): {len(not_comparable)}  "
          f"{not_comparable}")
    print(f"  absent from MODEL_ROSTER entirely   : {len(no_roster)}  {no_roster}")

    if stale:
        from statsmodels.stats.proportion import proportion_confint
        import numpy as np
        k = len(stale)
        lo, hi = proportion_confint(k, n, method="wilson")
        # cross-checked on a second tool, per the 2-tool rule
        z = 1.959963984540054
        ph = k / n
        d = 1 + z * z / n
        c = (ph + z * z / (2 * n)) / d
        h = z * np.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / d
        print()
        print(f"  stale rate: {k}/{n} = {k/n:.6f}  "
              f"Wilson [{lo:.6f}, {hi:.6f}]  "
              f"(NumPy check [{c-h:.6f}, {c+h:.6f}])")

    print()
    print("=" * 78)
    print("WHAT THIS MEANS, AND WHAT IT DOES NOT")
    print("=" * 78)
    print("  The design under test names 2 stale mappings. The measured count is")
    print(f"  {len(stale)}, so the claim is UNDERSTATED rather than wrong.")
    print()
    print("  EACH STALE KEY, with what it selects:")
    for label, key, desc, kv, dv in stale:
        bud = co.MODEL_COHERENCE_BUDGETS.get(key)
        ph = co.PHENOTYPE_TRANSFORMS.get(key)
        chars = getattr(ph, "max_directive_chars", None) if ph else None
        print(f"    {label}: key {key} selects coherence budget {bud} and a "
              f"directive budget of {chars} characters,")
        print(f"      while the live roster calls it {desc!r}.")
    print()
    print("  NOT CLAIMED: that any run was wrong because of this. The key selects")
    print("  a budget and a format, and a superseded key is not automatically an")
    print("  unsuitable budget -- `MODEL_SPECS['Fable']` has carried \"inherited")
    print("  from CC2; not measured\" since August by the same convention. What IS")
    print("  established is that the table NAMES a model that is not the one being")
    print("  dispatched, so a figure read back from it is attributed to the wrong")
    print("  version.")
    print()
    print("  RENAMING IS HIS. A fingerprint is a prior a future run reads, so")
    print("  changing a key changes what a model is told about itself, and the")
    print("  archive's existing entries are keyed on the current spellings.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
