#!/usr/bin/env python3
"""The future-stamp rule dated a bare clock from the mtime, and accused 16 notes
of claiming a time none of them claimed.

FOUND 2026-11-03 by the rule blocking a commit. A reply file written at 23:38 on
2 November, and stamped "2 November 2026, 23:40 GMT", was reported as claiming
"2026-11-03 23:40" -- 23 hours in the future -- because the clock had passed
midnight before the check ran.

HOW THE RULE WORKS, AND WHERE IT WENT WRONG. `future_stamp` first looks for an
ISO stamp that `STAMP_LINE` can parse, which needs `YYYY-MM-DD HH:MM ZONE` at
the start of a line. Failing that it falls back to a BARE clock time in the
header and dates it FROM THE FILE'S MTIME. That fallback is correct only while a
note is never touched again. Edit a note on a later day -- or let a commit hook
lint a temporary copy, which is what happened here -- and the rule reports a
claim the note never made.

AND THE FALLBACK IS THE BRANCH THAT ACTUALLY RUNS. Only 145 of 639 notes carry a
stamp `STAMP_LINE` parses; 205 carry a bare clock and 289 carry neither. So the
mtime-dated path is the normal one, not an edge case.

THE FIX IS ADDITIVE AND READS A FIELD THE RULE ALREADY HAD IN FRONT OF IT. The
same header almost always carries a prose date -- "15 April 2026" -- and the
fallback now uses that date with the bare clock, falling back to mtime only when
no prose date is present. The comparison against mtime is unchanged, so a note
that genuinely claims a future time is still accused, and the accusation now
quotes the day the note actually names.

WHAT IT IS NOT. It is not a weakening. Section 3 drives both directions: a
same-day clock 2 hours ahead is still caught, a header dated tomorrow is still
caught, and an honest note 30 days old stays silent.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import pathlib
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
LINT = REPO / "scripts" / "note_vagueness_lint.py"
NOTES = REPO / "experimental_notes"


def _load(path: pathlib.Path):
    spec = importlib.util.spec_from_file_location("_nvl_probe", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _iv(k: int, n: int):
    from scipy import stats
    from statsmodels.stats.proportion import proportion_confint
    if n == 0:
        return (0.0, 1.0), (0.0, 1.0)
    wl, wh = proportion_confint(k, n, alpha=0.05, method="wilson")
    cl = 0.0 if k == 0 else float(stats.beta.ppf(0.025, k, n - k + 1))
    ch = 1.0 if k == n else float(stats.beta.ppf(0.975, k + 1, n - k))
    return (max(0.0, wl), wh), (cl, ch)


def _show(label: str, k: int, n: int) -> None:
    (wl, wh), (cl, ch) = _iv(k, n)
    print(f"   {label}: {k} of {n}, {k / n if n else 0.0:.6f}")
    print(f"     Wilson 95%          [{wl:.6f}, {wh:.6f}]")
    print(f"     Clopper-Pearson 95% [{cl:.6f}, {ch:.6f}]")


def main() -> int:
    argparse.ArgumentParser(
        description=("Measure the future-stamp rule's false accusations and "
                     "show the fix keeps its true ones.")).parse_args()
    nvl = _load(LINT)
    notes = sorted(NOTES.rglob("*.md"))

    print("=" * 78)
    print("A BARE CLOCK WAS DATED FROM THE MTIME, NOT FROM THE HEADER'S OWN DATE")
    print("=" * 78)

    print("\n1. WHICH BRANCH ACTUALLY RUNS.")
    iso = bare = neither = 0
    for f in notes:
        try:
            text = f.read_text(errors="replace")
        except OSError:
            continue
        head = "\n".join(text.splitlines()[:3])
        if nvl.STAMP_LINE.search(text[:800]):
            iso += 1
        elif nvl._BARE_CLOCK_IN_HEADER.search(head):
            bare += 1
        else:
            neither += 1
    print(f"   notes under experimental_notes/        : {len(notes)}")
    print(f"   an ISO stamp STAMP_LINE can parse      : {iso}")
    print(f"   only a BARE clock in the header        : {bare}")
    print(f"   neither                                : {neither}")
    _show("the mtime-dated fallback is the branch that runs", bare, iso + bare)
    print("   => the fallback is the normal path, so its dating rule is not an")
    print("      edge case.")

    print("\n2. HOW MANY ACCUSATIONS A PROSE DATE EXONERATES.")
    fires, exon = [], []
    for f in notes:
        if nvl.future_stamp(f) is None:
            continue
        fires.append(f.name)
    #: Recomputed against the UNFIXED logic, so the figure survives the fix.
    for f in notes:
        try:
            text = f.read_text(errors="replace")
        except OSError:
            continue
        head = "\n".join(text.splitlines()[:3])
        if nvl.STAMP_LINE.search(text[:800]):
            continue
        b = nvl._BARE_CLOCK_IN_HEADER.search(head)
        pd = nvl._PROSE_DATE_IN_HEADER.search(head)
        if not b or not pd:
            continue
        mt = dt.datetime.fromtimestamp(f.stat().st_mtime)
        try:
            prose = dt.datetime.strptime(
                f"{int(pd.group(1))} {pd.group(2)} {pd.group(3)}", "%d %B %Y")
        except ValueError:
            continue
        old_claim = mt.replace(hour=int(b.group(1)), minute=int(b.group(2)),
                               second=0, microsecond=0)
        new_claim = prose.replace(hour=int(b.group(1)), minute=int(b.group(2)),
                                  second=0, microsecond=0)
        slack = mt + dt.timedelta(minutes=2)
        if old_claim > slack and new_claim <= slack:
            exon.append((f.name, old_claim, new_claim, mt))
    print(f"   notes the rule accuses NOW (post-fix)  : {len(fires)}")
    print(f"   accusations the prose date removes     : {len(exon)}")
    _show("false accusations among the pre-fix total", len(exon),
          len(fires) + len(exon))
    for name, oc, nc, mt in exon[:5]:
        print(f"      {name[:44]:44s} rule said {oc:%Y-%m-%d %H:%M}  "
              f"header says {nc:%Y-%m-%d %H:%M}  mtime {mt:%Y-%m-%d %H:%M}")
    print("   => none of these notes ever claimed the day it was accused of.")

    print("\n3. THE RULE STILL CATCHES WHAT IT IS FOR. 3 cases, driven.")
    now = dt.datetime.now()
    cases = []
    with tempfile.TemporaryDirectory() as d:
        dd = pathlib.Path(d)
        fut = now + dt.timedelta(hours=2)
        a = dd / "Same_Day_Clock_Ahead.md"
        a.write_text(f"# A note\n\n{now.day} {now:%B} {now.year}, "
                     f"{fut:%H:%M} GMT\n\nbody\n")
        cases.append(("a same-day clock 2 hours ahead", a, True))
        tom = now + dt.timedelta(days=1)
        b = dd / "Header_Dated_Tomorrow.md"
        b.write_text(f"# A note\n\n{tom.day} {tom:%B} {tom.year}, "
                     f"09:00 GMT\n\nbody\n")
        cases.append(("a header dated tomorrow", b, True))
        old = now - dt.timedelta(days=30)
        c = dd / "Honest_Old_Note.md"
        c.write_text(f"# A note\n\n{old.day} {old:%B} {old.year}, "
                     f"23:50 GMT\n\nbody\n")
        cases.append(("an honest note 30 days old", c, False))
        ok = 0
        for label, path, should_fire in cases:
            got = nvl.future_stamp(path)
            fired = got is not None
            good = fired == should_fire
            ok += good
            print(f"   {label:32s} expected "
                  f"{'ACCUSE' if should_fire else 'SILENT':6s} -> "
                  f"{'ACCUSE' if fired else 'SILENT':6s} "
                  f"{'ok' if good else 'WRONG'}"
                  f"{'  ' + str(got) if got else ''}")
    print(f"   {ok} of {len(cases)} behave correctly")
    print("   => the fix removes false accusations without removing true ones.")
    return 0 if ok == len(cases) else 1


if __name__ == "__main__":
    raise SystemExit(main())
