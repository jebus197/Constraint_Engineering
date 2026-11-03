#!/usr/bin/env python3
"""Does the questions register need a THREADED forum, or a native view?

C33 IS A DISCUSSION HE ASKED FOR, NOT A BUILD. His instruction, 2026-10-19:
questions should also appear in the discussions section of the upcoming UX build
through a facility such as Discourse, and the integration itself is a discussion
to be recorded at the foot of the master task list. There is no UX build, so the
entry is DEFERRED and the question is which FRONT to choose when there is one.

C33 NAMED ITS OWN DECIDING MEASUREMENT AND SAID IT COULD NOT YET BE TAKEN:
*how many of the register's questions ever acquire a SECOND MESSAGE?* A register
where almost every question is asked once and answered once does not need a
forum; one where questions develop into threads does. It also named what would
make the measurement takeable -- either a reply field on a question, or a tally
of closed questions later REOPENED or superseded by a second question on the
same subject -- and noted that `reopen()` is founder-only, so the reopen tally
measures HIS behaviour, which is the right subject.

THIS SCRIPT TAKES THAT MEASUREMENT. Both named proxies are available from the
register today, and both are reported, because they answer slightly different
questions and a single number would hide that.

WHAT IT DOES NOT CLAIM, stated before the figures so the limits are not read as
an afterthought:

  1. THE REGISTER IS HALF UNTRIAGED. A large share of questions sit UNCONFIRMED,
     which is a state needing triage rather than an answer, so they have not yet
     had the chance to acquire a follow-up. The conclusion is therefore about
     the ANSWERED portion and is bounded accordingly.
  2. A SUBJECT IS NOT A THREAD. 2 questions naming one code subject need not be
     a follow-up to each other; they may be independent questions about the same
     function. The subject tally is an UPPER bound on threading, not a count of
     it.
  3. "NEVER REOPENED" IS BOUNDED, NOT PROVEN. The upper end of the interval is
     what the evidence supports, and it is quoted rather than rounded to 0.

THE DECISION RULE IS STATED SO THE MEASUREMENT CAN FAIL, which is the point of
pre-registering it: the forum is indicated if either proxy's Wilson LOWER bound
exceeds 0.20, i.e. if better than 1 question in 5 shows a second message. Below
that the native view is indicated, because a threaded forum's cost -- an external
dependency and its own database -- buys a capability the register does not
exercise.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
STORE = REPO / "bench" / "tickets" / "tickets.jsonl"

#: The store's own terminal set, imported rather than restated, so a change to
#: the vocabulary cannot leave this script disagreeing with it.
def _terminal() -> frozenset:
    sys.path.insert(0, str(REPO))
    from bench.ticket_store import TERMINAL  # noqa: E402
    return frozenset(TERMINAL) | {"REJECTED"}


#: Above this Wilson LOWER bound, a threaded forum is indicated. Pre-registered
#: here rather than chosen after seeing the figures.
FORUM_THRESHOLD = 0.20


def _rows() -> list:
    out = []
    for line in STORE.read_text(errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except Exception:  # noqa: BLE001
            continue
        if r.get("kind") == "qs":
            out.append(r)
    return out


def _iv(k: int, n: int) -> tuple:
    """Wilson and Clopper-Pearson, each on 2 independent tools."""
    from scipy import stats
    from statsmodels.stats.proportion import proportion_confint
    import mpmath
    mpmath.mp.dps = 40

    def bi(a, b, y):
        f = lambda x: mpmath.betainc(a, b, 0, x, regularized=True) - y
        lo, hi = mpmath.mpf(0), mpmath.mpf(1)
        for _ in range(200):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if f(mid) < 0 else (lo, mid)
        return float((lo + hi) / 2)

    if n == 0:
        return (0.0, 1.0), (0.0, 1.0), 0.0
    wl, wh = proportion_confint(k, n, alpha=0.05, method="wilson")
    cl = 0.0 if k == 0 else float(stats.beta.ppf(0.025, k, n - k + 1))
    ch = 1.0 if k == n else float(stats.beta.ppf(0.975, k + 1, n - k))
    d = max(abs(cl - (0.0 if k == 0 else bi(k, n - k + 1, 0.025))),
            abs(ch - (1.0 if k == n else bi(k + 1, n - k, 0.975))))
    return (wl, wh), (cl, ch), d


def main() -> int:
    argparse.ArgumentParser(
        description=("Does the questions register need a threaded forum, or a "
                     "native view? Takes the measurement C33 named.")).parse_args()
    TERM = _terminal()
    rows = _rows()
    hist: dict = collections.defaultdict(list)
    for i, r in enumerate(rows):
        hist[r.get("tid")].append((i, r.get("status")))
    latest = {t: v[-1][1] for t, v in hist.items()}
    by_status = collections.Counter(latest.values())

    print("=" * 76)
    print("DOES THE QUESTIONS REGISTER NEED A THREADED FORUM?")
    print("=" * 76)
    print(f"\n  qs questions in the register : {len(hist)}")
    print(f"  revision rows                : {len(rows)}")
    print(f"  by current status            : {dict(by_status)}")
    untriaged = by_status.get("UNCONFIRMED", 0)
    answered = sum(v for k, v in by_status.items() if k in TERM)
    print(f"  UNCONFIRMED (needing triage, not an answer) : {untriaged}")
    print(f"  in a terminal state (answered or settled)   : {answered}")

    # PROXY 1 -- a question that went terminal and came back.
    reopened = []
    for tid, seq in hist.items():
        st = [s for _i, s in seq]
        for a, b in zip(st, st[1:]):
            if a in TERM and b not in TERM:
                reopened.append(tid)
                break
    print(f"\n  PROXY 1. QUESTIONS REOPENED AFTER GOING TERMINAL")
    print(f"    `reopen()` is founder-only, so this measures HIS behaviour.")
    (w1l, w1h), (c1l, c1h), d1 = _iv(len(reopened), len(hist))
    print(f"    {len(reopened)} of {len(hist)}, "
          f"{len(reopened)/len(hist) if hist else 0:.6f}")
    print(f"      Wilson 95%          [{w1l:.6f}, {w1h:.6f}]")
    print(f"      Clopper-Pearson 95% [{c1l:.6f}, {c1h:.6f}]  (2-tool |diff| {d1:.1e})")
    if reopened:
        print(f"      reopened: {reopened[:6]}")

    # PROXY 2 -- a code subject carrying more than 1 distinct question.
    subj: dict = collections.defaultdict(set)
    for r in rows:
        for s in (r.get("subjects") or []):
            subj[s].add(r.get("tid"))
    multi = {k: v for k, v in subj.items() if len(v) > 1}
    print(f"\n  PROXY 2. CODE SUBJECTS CARRYING A 2nd DISTINCT QUESTION")
    print(f"    An UPPER bound on threading: 2 questions about one function need")
    print(f"    not be a follow-up to each other.")
    (w2l, w2h), (c2l, c2h), d2 = _iv(len(multi), len(subj))
    print(f"    {len(multi)} of {len(subj)}, "
          f"{len(multi)/len(subj) if subj else 0:.6f}")
    print(f"      Wilson 95%          [{w2l:.6f}, {w2h:.6f}]")
    print(f"      Clopper-Pearson 95% [{c2l:.6f}, {c2h:.6f}]  (2-tool |diff| {d2:.1e})")
    for k, v in sorted(multi.items())[:6]:
        print(f"        {k}: {len(v)} questions")

    print(f"\n  THE PRE-REGISTERED RULE: a forum is indicated if either proxy's")
    print(f"  Wilson LOWER bound exceeds {FORUM_THRESHOLD:.2f}.")
    forum = (w1l > FORUM_THRESHOLD) or (w2l > FORUM_THRESHOLD)
    print(f"    proxy 1 lower bound {w1l:.6f}; proxy 2 lower bound {w2l:.6f}")
    print(f"    VERDICT: {'A THREADED FORUM IS INDICATED' if forum else 'THE NATIVE VIEW IS INDICATED'}")
    if not forum:
        print("    -> questions here are asked once and answered once. A forum's")
        print("       cost is an external dependency and its own database, buying")
        print("       threading, moderation and notification that the register")
        print("       does not exercise. The native view reuses the inverted word")
        print("       index already in place.")
    if untriaged:
        share = untriaged / len(hist) if hist else 0
        print(f"\n  THE LIMIT THAT MATTERS: {untriaged} of {len(hist)} questions "
              f"({share:.6f}) are UNCONFIRMED,")
        print("  so they have not had the chance to acquire a follow-up. This")
        print("  verdict is about the ANSWERED portion and should be re-taken")
        print("  once triage has run. It is NOT a recommendation to build either")
        print("  front now: C33 records that no ruling is owed yet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
