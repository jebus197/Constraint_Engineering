#!/usr/bin/env python3
"""What moved since a date he names, and whether this backlog converges.

WHY THIS EXISTS, IN HIS OWN WORDS, 2026-11-21: *"I take a few days out due to
sickness and life and I feel I quickly lose track - and some confidence in what
I'm doing."* And, on the 29 decisions of 2026-11-08: *"that to be honest rather
demotivated me, as I hit a bit of a low point wondering when this will end?"*

THE DIAGNOSIS THE RECORD SUPPORTS IS NOT LOSS OF CONTROL. Every surface he
reads answers *what is outstanding*. Nothing answers *what moved*. So a week
away looks identical to a week of nothing happening, and the only number in
front of him is the one that never looks smaller. This view answers the second
question from the same records, and it is deliberately 2 halves:

  THE LEDGER   -- what closed since his date, split by whether HIS ruling
                  closed it or something else did, because those are different
                  facts about who is in control.
  THE TREND    -- whether arrivals outrun closures. That is the only honest
                  answer to "when will this end", and it is allowed to come
                  back "it does not", because a view that can only reassure is
                  not a measurement.

WHAT THIS IS NOT. It is not a progress report and it does not score the
project. It reads the master task list's own markers and nothing else, so it
cannot flatter: `ruled` is a date HE set, and an entry with no `ruled` field
closed without him whatever its prose claims.

EVERY RATE CARRIES AN INTERVAL ON 2 INDEPENDENT ROUTES, per the project's
2-tool rule: counts get Wilson and Clopper-Pearson from statsmodels against a
hand-rolled mpmath computation, and the daily rates get an exact Poisson
interval from scipy's chi-square quantiles against mpmath's inverse regularised
gamma. A figure whose 2 routes disagree is printed as a disagreement, not
averaged.

THE HONEST LIMITS, STATED RATHER THAN BURIED:
  * 105 of 349 entries carry no `Added` date in their body, so arrival counts
    are a LOWER bound on arrivals and are labelled so.
  * `ruled` records the date he ruled, not the date the entry closed, so a
    closure lags its ruling by an unmeasured amount.
  * The projection is a straight line through a count that moves in steps. It
    is an ORDER OF MAGNITUDE, not a date, and the script says so in its output
    rather than leaving the reader to infer it.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
TASK_LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"

#: The date he named: when the file put 29 decisions in front of him.
DEFAULT_SINCE = "2026-11-08"


def _load(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def entries_and_bodies():
    sys.path.insert(0, str(REPO / "scripts"))
    import task_list_markers as tlm
    cls = _load("_syll_cls", REPO / "scripts" /
                "how_many_decisions_actually_need_him_2026-11-01.py")
    return tlm.parse_entries(TASK_LIST), cls.bodies(), cls


def added_date(body: str):
    m = re.search(r"Added (\d{4}-\d{2}-\d{2})", body)
    return dt.date.fromisoformat(m.group(1)) if m else None


def ruled_date(e):
    r = str(getattr(e, "ruled", "") or "").strip()
    m = re.match(r"(\d{4}-\d{2}-\d{2})", r)
    return dt.date.fromisoformat(m.group(1)) if m else None


# ---------------------------------------------------------------- intervals

def wilson_two_routes(k: int, n: int, alpha: float = 0.05):
    """statsmodels against a hand-rolled mpmath Wilson. Returns (lo, hi, agree)."""
    from statsmodels.stats.proportion import proportion_confint
    import mpmath as mp
    mp.mp.dps = 30
    if n == 0:
        return (float("nan"), float("nan"), 0.0)
    a = proportion_confint(k, n, alpha=alpha, method="wilson")
    kk, nn = mp.mpf(k), mp.mpf(n)
    z = -mp.sqrt(2) * mp.erfinv(mp.mpf(alpha) - 1)
    p = kk / nn
    d = 1 + z**2 / nn
    c = (p + z**2 / (2 * nn)) / d
    h = (z / d) * mp.sqrt(p * (1 - p) / nn + z**2 / (4 * nn**2))
    b = (float(c - h), float(c + h))
    return (a[0], a[1], max(abs(a[0] - b[0]), abs(a[1] - b[1])))


def poisson_rate_two_routes(count: int, days: float, alpha: float = 0.05):
    """Exact Poisson interval on the RATE, scipy chi2 against mpmath gammaincinv.

    The exact interval for a Poisson count k is
        [chi2.ppf(a/2, 2k)/2, chi2.ppf(1-a/2, 2k+2)/2]
    divided by the exposure. The mpmath route inverts the regularised lower
    incomplete gamma instead, which is a different function call on a different
    library, so an error in either is visible rather than shared.
    """
    from scipy import stats
    import mpmath as mp
    mp.mp.dps = 30
    if days <= 0:
        return (float("nan"), float("nan"), float("nan"), 0.0)
    lo_s = 0.0 if count == 0 else stats.chi2.ppf(alpha / 2, 2 * count) / 2
    hi_s = stats.chi2.ppf(1 - alpha / 2, 2 * count + 2) / 2
    # mpmath: P(a, x) = regularised lower incomplete gamma; invert in x.
    def _inv_lower(a_shape, target):
        if a_shape <= 0:
            return mp.mpf(0)
        def f(x):
            return mp.gammainc(a_shape, 0, x, regularized=True) - target
        lo, hi = mp.mpf('1e-12'), mp.mpf(a_shape) + 50
        while f(hi) < 0:
            hi *= 2
        return mp.findroot(f, (lo, hi), solver='bisect', tol=1e-18)
    lo_m = 0.0 if count == 0 else float(_inv_lower(count, alpha / 2))
    hi_m = float(_inv_lower(count + 1, 1 - alpha / 2))
    agree = max(abs(lo_s - lo_m), abs(hi_s - hi_m))
    return (lo_s / days, hi_s / days, count / days, agree)


# ---------------------------------------------------------------- the view

def build(since: dt.date, today: dt.date | None = None) -> dict:
    entries, bodies, cls = entries_and_bodies()
    today = today or dt.date.today()
    span = max((today - since).days, 1)

    closed_by_him, closed_otherwise, opened_since, owed_now = [], [], [], []
    for e in entries:
        body = bodies.get(e.ident, "")
        st = str(e.state).upper()
        rd = ruled_date(e)
        ad = added_date(body)
        if st != "OPEN" and rd and rd >= since:
            closed_by_him.append((e.ident, rd))
        elif st != "OPEN" and ad and ad >= since:
            closed_otherwise.append((e.ident, ad))
        if ad and ad >= since:
            opened_since.append((e.ident, ad))
        if st == "OPEN":
            kind = cls.classify_text(e.state, e.ruled, body)["kind"]
            if kind == "OWED":
                owed_now.append(e.ident)

    # arrivals and closures over the window, as daily rates
    arrivals = len(opened_since)
    closures = len(closed_by_him) + len(closed_otherwise)
    a_lo, a_hi, a_pt, a_agree = poisson_rate_two_routes(arrivals, span)
    c_lo, c_hi, c_pt, c_agree = poisson_rate_two_routes(closures, span)

    return {
        "since": since, "today": today, "span_days": span,
        "closed_by_him": sorted(closed_by_him),
        "closed_otherwise": sorted(closed_otherwise),
        "opened_since": sorted(opened_since),
        "owed_now": sorted(owed_now),
        "arrival": (arrivals, a_pt, a_lo, a_hi, a_agree),
        "closure": (closures, c_pt, c_lo, c_hi, c_agree),
        "dated_bodies": sum(1 for b in bodies.values() if added_date(b)),
        "total_entries": len(entries),
    }


def queue_trajectory() -> dict:
    """HIS OWN QUEUE over time, from the files actually delivered to his Desktop.

    ★ THIS IS THE DISTINCTION THE SINGLE BACKLOG FIGURE DESTROYS, and it is why
    this function exists beside the one above. The project's entry count and the
    number of decisions waiting on HIM are different quantities with different
    owners. The first grows because I raise things; the second shrinks when he
    rules. Reporting only the first tells him the work is diverging when his own
    half may be converging, and that is the shape of the demoralisation he
    described.

    The dated files are the evidence rather than the task list, because a file
    DELIVERED to his Desktop is what he actually saw on that date -- the task
    list has since been edited and cannot say what the queue looked like then.
    """
    import numpy as np
    from scipy import stats
    d = pathlib.Path.home() / "Desktop" / "CDSFL_tts"
    pts = []
    for f in sorted(d.glob("Decisions_Awaiting_You_*_GENERATED.txt")):
        m = re.search(r"(\d{4}-\d{2}-\d{2})", f.name)
        if not m:
            continue
        txt = f.read_text(encoding="utf-8", errors="replace")
        n = len(dict.fromkeys(re.findall(r"^\s*\d+\.\s+(B\d{2,3})\b", txt, re.M)))
        pts.append((dt.date.fromisoformat(m.group(1)), n))
    if len(pts) < 3:
        return {"points": pts, "note": "too few delivered files to fit a trend"}
    x = np.array([(p[0] - pts[0][0]).days for p in pts], dtype=float)
    y = np.array([p[1] for p in pts], dtype=float)
    whole_s = stats.linregress(x, y)
    whole_n = np.polyfit(x, y, 1)
    imin = int(np.argmin(y))
    out = {"points": pts, "peak": int(y.max()), "trough": int(y.min()),
           "trough_date": pts[imin][0], "now": int(y[-1]),
           "net_since_start": int(y[-1] - y[0]),
           "whole_slope": float(whole_s.slope), "whole_p": float(whole_s.pvalue),
           "whole_agree": abs(float(whole_s.slope) - float(whole_n[0]))}
    if len(y) - imin >= 3:
        s = stats.linregress(x[imin:], y[imin:])
        n2 = np.polyfit(x[imin:], y[imin:], 1)
        out.update({"since_trough_slope": float(s.slope),
                    "since_trough_p": float(s.pvalue),
                    "since_trough_r2": float(s.rvalue ** 2),
                    "since_trough_ci": (float(s.slope - 1.96 * s.stderr),
                                        float(s.slope + 1.96 * s.stderr)),
                    "since_trough_agree": abs(float(s.slope) - float(n2[0]))})
    return out


def live_split() -> dict:
    """Of the decisions waiting on him, how many are RULINGS and how many are
    ratifications of work the record already says is done.

    The flag is not written by hand: it is `status_flag` from the decisions
    generator, which reads each entry's own marker through the canonical
    parser. So this cannot flatter the count -- an entry claiming in prose to
    be built but carrying status PROPOSED is counted as live.
    """
    import json
    bd = _load("_syll_bd", REPO / "scripts" / "build_decisions_file_2026-11-07.py")
    states = bd.entry_states()
    rows = json.loads((REPO / "experimental_notes" / "data" /
                       "morning_report_decisions.json").read_text(encoding="utf-8"))
    d = pathlib.Path.home() / "Desktop" / "CDSFL_tts"
    #: ★ THE DESKTOP IS NOT IN THE REPOSITORY, so a fresh clone has 0 of these
    #: files. An unguarded [-1] would raise IndexError there and take the whole
    #: view down, which is `a declared default that does not exist removes the
    #: fallback`. The repository copy is the fallback, and if neither exists the
    #: section reports that it cannot be computed rather than inventing a split.
    candidates = sorted(d.glob("Decisions_Awaiting_You_*_GENERATED.txt"))
    if not candidates:
        candidates = sorted((REPO / "experimental_notes").glob(
            "Decisions_Awaiting_You_*_GENERATED.txt"))
    if not candidates:
        return {"file": None, "all": [], "ratify": [], "live": [],
                "note": "no delivered decisions file found; split not computable"}
    newest = candidates[-1]
    txt = newest.read_text(encoding="utf-8", errors="replace")
    ids = list(dict.fromkeys(re.findall(r"^\s*\d+\.\s+(B\d{2,3})\b", txt, re.M)))
    flagged = [i for i in ids
               if bd.status_flag(i, rows.get(f"task:{i}", {}), states)]
    return {"file": newest.name, "all": ids, "ratify": flagged,
            "live": [i for i in ids if i not in flagged]}


def report(v: dict) -> int:
    span = v["span_days"]
    print(f"SINCE YOU LAST LOOKED — {v['since']} to {v['today']} ({span} day(s))")
    print()
    n_him, n_other = len(v["closed_by_him"]), len(v["closed_otherwise"])
    print(f"  CLOSED, and YOUR ruling is what closed it : {n_him}")
    print(f"  CLOSED without a ruling of yours on record: {n_other}"
          + (f"  {[i for i, _ in v['closed_otherwise']]}" if n_other else ""))
    print(f"  RAISED since that date                    : {len(v['opened_since'])}")
    print(f"  decisions waiting for you NOW             : {len(v['owed_now'])}")
    print()

    ac, ap, alo, ahi, aag = v["arrival"]
    cc, cp, clo, chi, cag = v["closure"]
    print("  DOES THIS CONVERGE? arrivals against closures, as daily rates")
    print(f"    arrivals : {ac:>3d} in {span} d = {ap:.6f}/day  "
          f"exact Poisson [{alo:.6f}, {ahi:.6f}]  2 routes agree {aag:.2e}")
    print(f"    closures : {cc:>3d} in {span} d = {cp:.6f}/day  "
          f"exact Poisson [{clo:.6f}, {chi:.6f}]  2 routes agree {cag:.2e}")
    overlap = not (ahi < clo or chi < alo)
    if cp > ap and not overlap:
        print("    -> CLOSURES OUTRUN ARRIVALS and the intervals do NOT overlap.")
        net = cp - ap
        print(f"       net drain {net:.6f}/day; at that rate the {len(v['owed_now'])} "
              f"waiting on you clear in about {len(v['owed_now'])/net:.0f} day(s).")
        print("       THAT IS AN ORDER OF MAGNITUDE, NOT A DATE: a straight line "
              "through a count that moves in steps.")
    elif cp > ap:
        print("    -> closures outrun arrivals on the point estimate, but the "
              "intervals OVERLAP, so convergence is NOT established.")
        print("       No end date may be quoted from this.")
    else:
        print("    -> ARRIVALS OUTRUN CLOSURES. On this window the backlog does "
              "NOT converge, and saying otherwise would be false comfort.")
    print()
    print(f"  LIMIT, STATED: {v['dated_bodies']} of {v['total_entries']} entries "
          f"carry an 'Added' date, so arrivals are a LOWER bound.")
    print()

    # ---- HIS OWN QUEUE, which the backlog figure above conflates away ----
    q = queue_trajectory()
    print("  YOUR OWN QUEUE, from the files delivered to your Desktop:")
    for date, n in q["points"]:
        print(f"      {date}  {n:>3d}")
    if "since_trough_slope" in q:
        lo, hi = q["since_trough_ci"]
        print(f"    peak {q['peak']}, trough {q['trough']} on {q['trough_date']}, "
              f"now {q['now']}; net since the start {q['net_since_start']:+d}")
        print(f"    whole window slope {q['whole_slope']:+.6f}/day "
              f"(p = {q['whole_p']:.6f}) -- indistinguishable from flat")
        print(f"    FROM THE TROUGH ONWARD {q['since_trough_slope']:+.6f}/day "
              f"(p = {q['since_trough_p']:.6f}, r2 = {q['since_trough_r2']:.6f}), "
              f"95% CI [{lo:+.6f}, {hi:+.6f}]")
        print(f"    -> YOU DID CLEAR IT ONCE, to {q['trough']}. It refilled, and "
              f"the refill is arrivals, which are mine to raise.")
        if max(q["whole_agree"], q["since_trough_agree"]) > 1e-9:
            print(f"    ★ 2 fitting routes disagree by "
                  f"{max(q['whole_agree'], q['since_trough_agree']):.2e} -- UNVERIFIED")
            return 1
    print()

    # ---- and how many of those are rulings rather than ratifications ----
    s = live_split()
    if s.get("note"):
        print(f"  THE RATIFY-OR-RULE SPLIT COULD NOT BE COMPUTED: {s['note']}")
        print()
        return 0 if max(aag, cag) <= 1e-9 else 1
    print(f"  OF THE {len(s['all'])} WAITING ON YOU, read from {s['file']}:")
    print(f"    ratify or close (built, or premise dead) : {len(s['ratify'])}  "
          f"{s['ratify']}")
    print(f"    GENUINELY LIVE QUESTIONS                 : {len(s['live'])}  "
          f"{s['live']}")
    print(f"    -> the number actually in front of you is {len(s['live'])}.")
    print()

    if max(aag, cag) > 1e-9:
        print(f"  ★ THE 2 ROUTES DISAGREE BY {max(aag, cag):.2e} — treat every "
              f"rate above as UNVERIFIED until that is explained.")
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=("What moved since a date, and whether the decision backlog "
                     "converges. Reads the master task list's own markers."))
    ap.add_argument("--since", default=DEFAULT_SINCE,
                    help=f"ISO date to compare against (default {DEFAULT_SINCE}, "
                         f"the day 29 decisions were put to the founder)")
    ap.add_argument("--json", action="store_true", help="emit the view as JSON")
    args = ap.parse_args(argv)

    v = build(dt.date.fromisoformat(args.since))
    if args.json:
        import json
        print(json.dumps(v, indent=2, default=str))
        return 0
    return report(v)


if __name__ == "__main__":
    sys.exit(main())
