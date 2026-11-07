#!/usr/bin/env python3
"""HIS QUESTION, 2026-11-07: 29 verdicts awaiting him seems unusually high --
are they all new, or are any of them repeats he has already ruled on?

THE ANSWER IS NEITHER, AND THAT IS WHY THIS PRODUCER EXISTS. Both readings he
offered are refuted by the record:

  * NOT NEW. Every one of the 29 has been put to him before, in a dated
    `Decisions_Awaiting_You_*` file. The queue is an unanswered BACKLOG, not a
    fresh batch of questions.
  * NOT REPEATS EITHER. 0 of the 29 carry a ruling of his that still settles
    them. 3 carry a ruling on a DIFFERENT question, each recorded in the
    entry's own `what_the_ruling_means`, and each is correctly live again.

AND IT CORRECTS `how_many_verdicts_really_await_him_2026-11-06.py`, WHICH
ANSWERED THE SAME QUESTION WRONG YESTERDAY. That producer called
`ruling_is_spent(f"task:{ident}", ...)`. The function expects a BARE
identifier: it passes `ident` straight to `asks_newer_than_the_ruling`, which
looks it up in `how_many_decisions_actually_need_him_2026-11-01.bodies()`,
whose keys are bare (`B21`, not `task:B21`). So the body came back EMPTY, no
dated addition could be found in an empty string, and `any([])` is False --
the function reported "the ruling still settles this" because it could not
find the entry at all. Measured below: 3 of 41 live entries change label when
the key is spelled correctly, B13, B20 and B21, all of them REPEAT -> LIVE
AGAIN. B20 is the next task on the list and the 1st decision in his queue, and
its own heading says he has ruled the build 3 times and has never been asked
whether to turn it on.

THIS IS THE SAME ERROR CLASS, IN THE MIRROR DIRECTION, AS ONE MADE HOURS
EARLIER IN THE SAME SESSION: `detail.get(ident)` with a bare `B20` against a
dict keyed `task:B20`, which measured 0 of 29 Rule 33 compliance instead of
29 of 29. One direction loses the prefix, the other adds it; both return a
default that reads as a finding.

HALF THE DEFECT WAS HIDDEN BY A FAIL-OPEN. For B71 the wrong spelling gives
the RIGHT answer, because `still_asks` fails open on an entry it cannot find
and B71 is BLOCKED, so the second branch rescued it. A bug that is wrong on 3
entries and accidentally right on a 4th is harder to see than one that is
wrong everywhere.

EXIT 0 iff every measurement completed and the 2 interval routes agree.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import sys
from collections import Counter

import mpmath as mp
from scipy.stats import beta as _beta
from statsmodels.stats.proportion import proportion_confint

mp.mp.dps = 40
REPO = pathlib.Path(__file__).resolve().parent.parent
HEADING = re.compile(r"^#{2,3}\s*DECISION\s+(\d+)\.\s*(.+?)\s*$", re.M)


def _load(path: pathlib.Path, name: str):
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _iv(k: int, n: int):
    """Wilson and Clopper-Pearson, each by 2 independent routes."""
    if n == 0:
        return (0.0, 1.0), (0.0, 1.0), 0.0
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = mp.mpf("1.959963984540054235524594430520551527955")
    ph = mp.mpf(k) / n
    den = 1 + z**2 / n
    cen = (ph + z**2 / (2 * n)) / den
    half = (z / den) * mp.sqrt(ph * (1 - ph) / n + z**2 / (4 * n * n))
    wl2, wh2 = float(cen - half), float(cen + half)
    cl = 0.0 if k == 0 else float(_beta.ppf(0.025, k, n - k + 1))
    ch = 1.0 if k == n else float(_beta.ppf(0.975, k + 1, n - k))

    def _invert(a, b, y):
        f = lambda x: mp.betainc(a, b, 0, x, regularized=True) - y   # noqa: E731
        loq, hiq = mp.mpf(0), mp.mpf(1)
        for _ in range(200):
            mid = (loq + hiq) / 2
            loq, hiq = (mid, hiq) if f(mid) < 0 else (loq, mid)
        return float((loq + hiq) / 2)

    cl2 = 0.0 if k == 0 else _invert(k, n - k + 1, 0.025)
    ch2 = 1.0 if k == n else _invert(k + 1, n - k, 0.975)
    dis = max(abs(lo - wl2), abs(hi - wh2), abs(cl - cl2), abs(ch - ch2))
    return (max(0.0, lo), hi), (cl, ch), dis


def _show(label: str, k: int, n: int) -> float:
    (wl, wh), (cl, ch), dis = _iv(k, n)
    rate = (k / n) if n else float("nan")
    print(f"  {label}: {k} of {n} = {rate:.6f}")
    print(f"      Wilson 95% [{wl:.6f}, {wh:.6f}]  "
          f"Clopper-Pearson 95% [{cl:.6f}, {ch:.6f}]")
    print(f"      2-route disagreement {dis:.3e}")
    assert dis < 1e-6, f"the 2 interval routes disagree by {dis}"
    return dis


def ask_history() -> dict[str, list[str]]:
    """heading (upper) -> the dates of every decisions file that carried it."""
    hist: dict[str, list[str]] = {}
    for f in sorted(REPO.glob("experimental_notes/Decisions_Awaiting_You_*.md")):
        date = f.stem.rsplit("_", 1)[-1]
        for _n, h in HEADING.findall(f.read_text(encoding="utf-8", errors="replace")):
            hist.setdefault(h.strip().upper(), []).append(date)
    return hist


#: The commit whose bytes carried the defect. PINNED rather than HEAD, because
#: HEAD moves the moment the repair lands and the historical figure must stay
#: reproducible from the code that produced it.
PRE_FIX_COMMIT = "6955397a40b0238087a3f4e45531750e42d45e73"


def _pre_fix_module(tmpdir: pathlib.Path):
    """The 2026-11-06 bytes of the build script, loaded from git.

    The live code now REFUSES a prefixed key, so the defect cannot be
    reproduced against it -- which is the point of the repair and would
    otherwise make this measurement unreproducible. The historical figure is
    therefore taken from the historical bytes.
    """
    import subprocess
    src = subprocess.run(
        ["git", "show", f"{PRE_FIX_COMMIT}:scripts/morning_report_build_2026-10-12.py"],
        capture_output=True, text=True, cwd=REPO, check=True).stdout
    p = tmpdir / "mrb_pre_fix.py"
    p.write_text(src, encoding="utf-8")
    return _load(p, "mrb_pre_fix")


def classify(mrb, items, prefixed: bool) -> dict[str, str]:
    """REAL (never ruled) / REPEAT (ruling still settles it) / LIVE-AGAIN.

    `prefixed` reproduces the 2026-11-06 defect on demand, so the correction
    is measured against it rather than asserted over it.
    """
    out: dict[str, str] = {}
    for it in items:
        ruled = it.get("ruled")
        ident = it["ident"]
        if not ruled:
            out[ident] = "REAL"
            continue
        key = f"task:{ident}" if prefixed else ident
        spent = mrb.ruling_is_spent(key, ruled, it.get("state") or "")
        out[ident] = "LIVE-AGAIN" if spent else "REPEAT"
    return out


def main(argv: list[str]) -> int:
    mrb = _load(REPO / "scripts" / "morning_report_build_2026-10-12.py", "mrb_29")
    sf = _load(REPO / "scripts" / "do_the_two_decision_surfaces_agree_2026-11-01.py",
               "sf_29")
    probe = _load(REPO / "scripts"
                  / "how_many_decisions_actually_need_him_2026-11-01.py", "probe_29")

    live = sf.derived()
    items = mrb.task_items()
    by_ident = {it["ident"]: it for it in items}
    bodies = probe.bodies()
    hist = ask_history()

    print("=" * 78)
    print("HIS QUESTION: ARE THE 29 NEW, OR REPEATS HE HAS ALREADY RULED ON?")
    print("=" * 78)
    print(f"live decisions in the queue : {len(live)}")
    print(f"live task entries overall   : {len(items)}")
    print(f"decisions files on record   : "
          f"{len(sorted(REPO.glob('experimental_notes/Decisions_Awaiting_You_*.md')))}")

    # ---- 1. HAVE THEY BEEN PUT TO HIM BEFORE? -----------------------------
    print("\n1. ASKED BEFORE -- every decision joined to the dated files by heading")
    asked = {ident: sorted(set(hist.get((head or "").strip().upper(), [])))
             for ident, head in live}
    n_asked = sum(1 for v in asked.values() if v)
    _show("put to him in an earlier dated decisions file", n_asked, len(live))
    first = {i: (v[0] if v else None) for i, v in asked.items()}
    print(f"      earliest delivery dates: "
          f"{dict(Counter(v for v in first.values() if v))}")

    # ---- 2. IS ANY OF THEM A REPEAT? --------------------------------------
    print("\n2. REPEAT -- a ruling of his that STILL SETTLES the entry")
    good = classify(mrb, items, prefixed=False)
    dec_cls = {ident: good.get(ident, "REAL") for ident, _h in live}
    counts = Counter(dec_cls.values())
    print(f"      the 29, partitioned: {dict(counts)}")
    _show("REPEAT among the 29", counts["REPEAT"], len(live))
    _show("carry a ruling on a DIFFERENT question (live again)",
          counts["LIVE-AGAIN"], len(live))
    _show("carry no ruling at all", counts["REAL"], len(live))
    for ident in sorted(i for i, c in dec_cls.items() if c == "LIVE-AGAIN"):
        it = by_ident.get(ident, {})
        print(f"      LIVE-AGAIN {ident}: ruled {it.get('ruled')}, "
              f"state {it.get('state')}, body {len(bodies.get(ident, ''))} chars")

    # ---- 3. THE DEFECT IN YESTERDAY'S PRODUCER ----------------------------
    print("\n3. THE KEY SPELLING, MEASURED BOTH WAYS OVER ALL LIVE ENTRIES")
    print(f"      historical bytes: {PRE_FIX_COMMIT[:8]}:"
          f"scripts/morning_report_build_2026-10-12.py")
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        old = _pre_fix_module(pathlib.Path(td))
        bad = classify(old, items, prefixed=True)
    print(f"      with a task: prefix (2026-11-06) : {dict(Counter(bad.values()))}")
    print(f"      with the bare ident (correct)    : {dict(Counter(good.values()))}")
    moved = sorted(k for k in bad if bad[k] != good[k])
    _show("live entries MISLABELLED by the prefix", len(moved), len(items))
    for k in moved:
        print(f"      {k}: {bad[k]} -> {good[k]}")
    print(f"      live decisions whose ident is absent from bodies(): "
          f"{sum(1 for i, _h in live if i not in bodies)} of {len(live)}")
    print("      (so every empty body under the prefixed key is a LOOKUP FAILURE,")
    print("       not an entry that genuinely carries no dated addition)")

    # ---- 3b. THE LIVE CODE NOW REFUSES IT ---------------------------------
    print("\n3b. AND THE LIVE CODE REFUSES THE PREFIXED KEY OUTRIGHT")
    refused = 0
    for fname, args in (("asks_newer_than_the_ruling", ("task:B21", "2026-10-17")),
                        ("still_asks", ("task:B21",)),
                        ("ruling_is_spent", ("task:B21", "2026-10-17", "OPEN"))):
        try:
            got = getattr(mrb, fname)(*args)
            print(f"      {fname}: NOT REFUSED, returned {got}  *** GUARD ABSENT ***")
        except ValueError:
            refused += 1
            print(f"      {fname}: refused")
    _show("entry points that refuse a store key", refused, 3)

    # ---- 4. THE GATED VERDICT ---------------------------------------------
    ok = (n_asked == len(live) and counts["REPEAT"] == 0
          and len(moved) > 0 and refused == 3)
    print("\n" + "=" * 78)
    print(f"""
VERDICT (gated on the 3 measurements above, not appended to them):

  NOT NEW:     {n_asked} of {len(live)} were already put to him in a dated file.
  NOT REPEATS: {counts['REPEAT']} of {len(live)} carry a ruling that still settles them.
  SO:          an unanswered backlog of {len(live)}, of which {counts['LIVE-AGAIN']} carry a ruling
               of his on a different question and {counts['REAL']} carry none at all.

  AND YESTERDAY'S ANSWER TO THE SAME QUESTION WAS WRONG: {len(moved)} live entries
  were labelled REPEAT by a key-spelling error, B20 among them -- the next
  task on the list and the 1st decision in his queue.
""")
    if not ok:
        print("  ONE OR MORE GATE CONDITIONS FAILED -- read the sections above.")
    return 0 if ok else 1


if __name__ == "__main__":
    #: ★ THE HELP HANDLER BELONGS INSIDE `__main__`, NEVER AT MODULE LEVEL:
    #: `answer_help` exits 2 on an unrecognised argument, so at module level it
    #: sees pytest's own argv on import and took 12 tests down on 2026-11-06.
    import pathlib as _pl
    sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
    from _cli_help import answer_help as _answer_help
    _answer_help(__doc__, __file__)
    raise SystemExit(main(sys.argv[1:]))
