# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'asking_predicate_and_fourth_standard_2026-11-14_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 1e0cd7d21d7b1c4e57b92fd34e9d064af384a188c4cc891ef4e40620de644533
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The measurement that separates the gate extension from the composition.

JOINT ROUND `asking_predicate_and_fourth_standard_2026-11-14`. The 2 blind
seats scored the candidate fixes on DIFFERENT named properties and each
measured only its own:

  P1  invisible-error (entry, surface) pairs TODAY -- seat cc2's property.
      On P1, "O3 extended to the gate" and "O3-extended composed with O4"
      TIE at 0, and cc2 refused the composition on that tie.
  P2  arrivals into the set undecidable-by-text, over time -- seat fable's
      property. On P2 the 2 candidates DIFFER, and the difference is
      measurable: every ruling recorded on an entry with unstamped live asks
      adds one entry no text predicate can decide (5 such arrivals sit in
      the live record, 2026-11-08 x4 and 2026-11-12 x1, and 0 of the live
      asking sentences carry any raise record), while a `raised:YYYY-MM-DD`
      stamp inside the asking sentence decides every future case by record.

The founder's composability standard (verbatim, 2026-10-02) prefers a single
fix "where a single fix out performs a composed one". This script measures
whether it does. A composed fix that ties on P1 and strictly wins on P2,
and whose worst case (a future ask left unstamped) degrades exactly to the
single fix and never below it, is not refused by that standard.

READS THE TREE IT SITS IN (`parents[1]`), never the home checkout: a
producer in a sandbox must measure the tree under review.

Every proportion carries a confidence interval, computed by 2 independent
routes (closed-form Wilson, statsmodels) that must agree.
"""

from __future__ import annotations

import importlib.util
import math
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"

RAISE_STAMP = re.compile(r"raised:\s*(\d{4}-\d{2}-\d{2})")


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, REPO / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(name, m)
    spec.loader.exec_module(m)
    return m


def wilson(k: int, n: int) -> tuple[float, float]:
    """Closed-form Wilson 95% interval. Route 1 of 2."""
    if n == 0:
        return (0.0, 1.0)
    z = 1.959963984540054
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def wilson_route2(k: int, n: int) -> tuple[float, float]:
    """statsmodels Wilson 95% interval. Route 2 of 2."""
    from statsmodels.stats.proportion import proportion_confint
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    return (float(lo), float(hi))


def report(label: str, k: int, n: int) -> None:
    lo1, hi1 = wilson(k, n)
    lo2, hi2 = wilson_route2(k, n)
    gap = max(abs(lo1 - lo2), abs(hi1 - hi2))
    assert gap < 1e-9, f"interval routes disagree by {gap}"
    print(f"  {label}: {k} of {n} = {k / n:.6f}"
          f"  Wilson [{lo1:.6f}, {hi1:.6f}]  2 routes agree to {gap:.3e}")


# --------------------------------------------------------------------------
# THE O4 COMPONENT, DELIVERED VERDICT-NEUTRAL. `recorded_raise` reads the
# stamp; `verdict_by_record` decides by record where a full set of stamps
# exists and otherwise KEEPS predicate A's verdict, flagged
# `undecided_by_record` -- never silently. It is wired to a test
# (bench/tests/test_the_record_decides_where_text_cannot_2026-11-14.py) and
# to this producer; it is NOT wired into `classify_text`, because changing a
# verdict any surface he reads depends on is his to rule.
# --------------------------------------------------------------------------

def recorded_raise(sentence: str) -> str | None:
    """The date a question was raised, read from its own `raised:` stamp."""
    m = RAISE_STAMP.search(sentence)
    return m.group(1) if m else None


def verdict_by_record(state: str, ruled: str | None, txt: str, clf) -> dict:
    """classify_text's verdict, with the ruled-and-asking branch decided by
    RECORD where every live ask carries a `raised:` stamp.

    Returns the classify_text dict plus:
      decided_by          : "RECORD" | "PROXY_A" | "TEXT"
      undecided_by_record : True where a ruled entry's live asks lack stamps,
                            so predicate A's verdict stands but is REPORTED
                            as undecided rather than silently resolved.
    """
    r = clf.classify_text(state, ruled, txt)
    r = dict(r)
    r["decided_by"] = "TEXT"
    r["undecided_by_record"] = False
    if not ruled or not r["live_asks"]:
        return r
    stamps = [recorded_raise(s) for s in r["live_asks"]]
    if all(stamps):
        r["kind"] = "OWED" if any(s > ruled for s in stamps) else "GRANTED"
        r["decided_by"] = "RECORD"
    else:
        r["decided_by"] = "PROXY_A"
        r["undecided_by_record"] = True
    return r


# --------------------------------------------------------------------------
# Predicates B and C, copied exactly from
# scripts/how_much_of_this_is_actually_his_2026-11-12.py lines 231-243 (the
# producer that defined them), cited rather than re-invented. Predicate D is
# the 4th text predicate seat cc2 named as "not obviously impossible": the
# nearest date stamp PRECEDING the asking sentence, read as its raise date.
# Measured below rather than argued about.
# --------------------------------------------------------------------------

def preds_BCD(e_ruled: str, txt: str, clf):
    r = clf.classify_text("OPEN", e_ruled, txt)
    norm_asks = set(r["live_asks"])
    B = any(any(d > e_ruled for d in clf._DATED_IN_BODY.findall(s))
            for s in r["live_asks"])
    dates = [(m.start(), m.group(1)) for m in clf._DATED_IN_BODY.finditer(txt)]
    later = [p for p, d in dates if d > e_ruled]
    first_later = min(later) if later else None
    ask_offs = [start for start, sent in clf._sentences(txt)
                if re.sub(r"\s+", " ", sent).strip() in norm_asks]
    C = first_later is not None and any(p >= first_later for p in ask_offs)
    d_votes = []
    for start in ask_offs:
        before = [d for p, d in dates if p < start]
        if not before:
            return B, C, None
        d_votes.append(before[-1] > e_ruled)
    D = any(d_votes) if d_votes else None
    return B, C, D


def main() -> int:
    sys.path.insert(0, str(REPO / "scripts"))
    from task_list_markers import parse_entries  # noqa: E402
    clf = _load("_clf_rec",
                "scripts/how_many_decisions_actually_need_him_2026-11-01.py")
    bodies = clf.bodies()
    es = parse_entries(LIST)
    opens = [e for e in es if e.state == "OPEN"]

    disputed, arrivals = [], {}
    live_ask_total, stamped = 0, 0
    owed = []
    for e in opens:
        txt = bodies.get(e.ident, "")
        r = clf.classify_text(e.state, e.ruled, txt)
        if r["kind"] == "OWED":
            owed.append(e.ident)
        live_ask_total += len(r["live_asks"])
        stamped += sum(1 for s in r["live_asks"] if recorded_raise(s))
        if r["kind"] == "OWED" and e.ruled and r["live_asks"]:
            B, C, D = preds_BCD(e.ruled, txt, clf)
            if not (True == B == C):          # A is True on this branch
                disputed.append((e.ident, e.ruled, B, C, D))
                arrivals[e.ruled] = arrivals.get(e.ruled, 0) + 1

    print("1. THE LIVE RECORD")
    print(f"  open {len(opens)}, OWED {len(owed)}, "
          f"disputed by the text predicates: {[d[0] for d in disputed]}")
    report("live asking sentences carrying a raise record",
           stamped, live_ask_total)
    print(f"  arrivals into the undecidable-by-text set, by ruling date: "
          f"{dict(sorted(arrivals.items()))}")
    print("  -- every future ruling recorded on an entry with unstamped live")
    print("     asks adds 1 more; no text predicate retires one.")

    nd = len(disputed)
    print("\n2. P1 -- INVISIBLE-ERROR PAIRS TODAY (cc2's property)")
    for opt, pairs in [("O1 change nothing", nd),
                       ("O2 adopt B or C", nd),
                       ("O3 as delivered (banner only)", nd),
                       ("O4 alone (0 stamps exist)", nd),
                       ("O3 extended to the gate", 0),
                       ("O3-extended composed with O4", 0)]:
        print(f"  {opt:34s} {pairs}")
    print("  -- the 2 survivors TIE on P1. P1 alone cannot choose between them.")

    print("\n3. P2 -- WHAT EACH SURVIVOR DOES WITH THE NEXT RULING")
    settled = ("Progress 2026-11-21: measured, committed, no question. "
               "Whether the gate also skips DEFERRED entries NEEDS YOUR "
               "RULING, raised:2026-11-18.")
    r_text = clf.classify_text("OPEN", "2026-11-20", settled)
    r_rec = verdict_by_record("OPEN", "2026-11-20", settled, clf)
    B, C, D = preds_BCD("2026-11-20", settled, clf)
    print("  record-settled entry (ask raised 11-18, ruled 11-20, progress 11-21):")
    print(f"    text suite: A={r_text['kind'] == 'OWED'} B={B} C={C} D={D}"
          f" -> kind {r_text['kind']} (disagreeing, undecidable by text)")
    print(f"    by record : kind {r_rec['kind']}, decided_by {r_rec['decided_by']}")
    post = ("Progress 2026-11-21: committed. "
            "Which ordering is kept NEEDS YOUR RULING, raised:2026-11-22.")
    r_rec2 = verdict_by_record("OPEN", "2026-11-20", post, clf)
    print(f"  genuinely-post-ruling stamped ask: by record -> {r_rec2['kind']},"
          f" decided_by {r_rec2['decided_by']}")
    legacy = ("The ceiling of 40 NEEDS YOUR RULING. "
              "Progress 2026-11-21: measured.")
    r_leg = verdict_by_record("OPEN", "2026-11-20", legacy, clf)
    print(f"  unstamped legacy ask: kind {r_leg['kind']} (= predicate A), "
          f"decided_by {r_leg['decided_by']}, "
          f"undecided_by_record {r_leg['undecided_by_record']} -- never silent")
    print("  -- under O3-extended ALL 3 cases above join the undecidable set")
    print("     and leave it only through his attention; under the composition")
    print("     the first 2 are decided by record and only the legacy case waits.")

    print("\n4. PREDICATE D (nearest preceding date), ON THE DISPUTED SET")
    truth = {"B94": False, "B142": False}
    # Ground-truthed false positives: B94's latest amendment says the residue
    # is MINE and NOT BUILT; B142's only live ask predates its ruling, the
    # later date records work done ON the ruling.
    for ident, ruled, B, C, D in disputed:
        gt = truth.get(ident)
        verdict = "UNDECIDED" if D is None else str(D)
        note = ""
        if gt is not None:
            note = ("  matches ground truth" if D == gt
                    else "  CONTRADICTS ground truth" if D is not None
                    else "  cannot decide a ground-truthed entry")
        print(f"  {ident:5s} ruled {ruled}  D={verdict}{note}")
    print("  -- n=2 ground-truthed entries cannot validate a predicate; D's")
    print("     error rate is unmeasurable without the record it substitutes for.")

    print("\n5. INTERVALS FOR THE SHARES EACH SURFACE CARRIES")
    report("proxy-dependent share of the banner count (OWED)", nd, len(owed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
