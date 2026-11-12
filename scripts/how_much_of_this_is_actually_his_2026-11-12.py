#!/usr/bin/env python3
"""How much of the open queue is genuinely HIS, and how much of it is new.

★ HIS QUESTION, 2026-11-12, verbatim: *"you appear to have both done substantial
work, and that would have resulted in a substantial amount of work that is
required of me. Is that correct?"* This answers it from the record rather than
from the morning report, because the morning report is one of the things being
checked.

★ WHY IT IS NEEDED AT ALL. The turn hook prints "8 of 12 open await YOU" from
`scripts/how_many_decisions_actually_need_him_2026-11-01.py`, and that figure
has never been audited against the rulings he has ALREADY given. This project
has recorded the failure twice: 5 of 7 entries described as awaiting him already
carried his ruling, and a stored verdict outvoted a live predicate for 9 days.

★ WHAT IT FINDS, AND THE HONEST SHAPE OF IT. The classifier's OWED test for an
entry that carries a ruling is `_later` -- is there any date in the body later
than the ruling date. That is a PROXY for "a question was raised after the
ruling", and 3 predicates for the same idea disagree on 3 of the 4 entries it
applies to. This script computes all 3 and reports the disagreement rather than
picking a winner, because picking one would be the 4th predicate on a surface
that has already defeated 3 -- which this project's own record says is the point
to stop and raise it.

★ EVERY PROPORTION CARRIES WILSON AND CLOPPER-PEARSON INTERVALS ON 2 ROUTES, via
the canonical `_iv` lifted byte-identically by AST from
`scripts/a4_blockers_lock_audit_2026-10-03.py`, never retyped.

Costs nothing but local CPU: reads the task list, 12 `git log` queries, no model
dispatch, no pytest.
"""
from __future__ import annotations

import importlib.util
import math
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
#: His most recent work window opened here: the 3 commits of 2026-11-10 onward.
RECENT_FROM = "2026-11-10"


def _iv(k: int, n: int):
    """Wilson and Clopper-Pearson, each on 2 INDEPENDENT routes."""
    from scipy import stats
    from statsmodels.stats.proportion import proportion_confint
    import mpmath
    mpmath.mp.dps = 40
    if n == 0:
        return (0.0, 1.0), (0.0, 1.0), 0.0
    wl, wh = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = stats.norm.ppf(0.975)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    wdiff = max(abs(wl - (c - hw)), abs(wh - (c + hw)))
    cl = 0.0 if k == 0 else float(stats.beta.ppf(0.025, k, n - k + 1))
    ch = 1.0 if k == n else float(stats.beta.ppf(0.975, k + 1, n - k))

    def bi(a, b, y):
        """Invert the regularised incomplete beta by bisection.

        HARDENED 2026-11-04. `mpmath.betainc` is fast, but its hyp2f1 path
        FAILS TO CONVERGE for large parameters at mid-range x. Measured at
        a=2437, b=17564 it succeeds for x <= 0.1264 and for x >= 0.9 and raises
        ValueError in between -- which is exactly where a bisection over [0, 1]
        takes its first step, so the whole inversion died rather than degrading.
        It surfaced when a producer called this at k=2436, n=20000; every
        existing caller used a small n, and the guard that executes every `_iv`
        against the same k and n uses n <= 38, so no test could have seen it.

        Where betainc raises, the same integral is computed by quadrature in
        log space instead. At the measured failing point that agreed with
        scipy's quantile to 1.11e-16. It costs about 6 s per bound against
        milliseconds for betainc, so it is used only after a failure, never by
        default.
        """
        logB = mpmath.log(mpmath.beta(a, b))

        def by_quad(x):
            if x <= 0:
                return mpmath.mpf(0)
            def dens(u):
                return mpmath.e**((a - 1) * mpmath.log(u)
                                  + (b - 1) * mpmath.log1p(-u) - logB)
            return mpmath.quad(dens, [0, min(mpmath.mpf(x), mpmath.mpf(1))])

        fell_back = False

        def f(x):
            nonlocal fell_back
            if not fell_back:
                try:
                    return mpmath.betainc(a, b, 0, x, regularized=True) - y
                except Exception:
                    fell_back = True
            return by_quad(x) - y

        # STOP ON PRECISION, not on a fixed count. The bracket halves every
        # step, so 2**-60 is already below this tolerance and a fixed 240 did
        # 180 redundant evaluations. That is free for betainc and it is NOT
        # free for the quadrature fallback, which costs about 28 ms per
        # evaluation: 240 steps took 6.66 s and 60 take 1.69 s for a bound
        # identical to 12 decimal places. The count is still capped so a
        # pathological case cannot spin.
        lo, hi = mpmath.mpf(0), mpmath.mpf(1)
        tol = mpmath.mpf("1e-18")
        for _ in range(240):
            if hi - lo < tol:
                break
            m = (lo + hi) / 2
            lo, hi = (m, hi) if f(m) < 0 else (lo, m)
        return float((lo + hi) / 2)

    cdiff = max(abs(cl - (0.0 if k == 0 else bi(k, n - k + 1, 0.025))),
                abs(ch - (1.0 if k == n else bi(k + 1, n - k, 0.975))))
    return (max(0.0, wl), wh), (cl, ch), max(wdiff, cdiff)

def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, REPO / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def first_seen(ident: str) -> str:
    """The date `ident` first appeared in the task list, from git, not prose."""
    p = subprocess.run(
        ["git", "log", "--reverse", "-S", f"{ident} ", "--format=%ad",
         "--date=short", "--", str(LIST.relative_to(REPO))],
        capture_output=True, text=True, cwd=str(REPO))
    out = (p.stdout or "").strip().splitlines()
    return out[0] if out else ""


def report(label: str, k: int, n: int) -> None:
    (wl, wh), (cl, ch), agree = _iv(k, n)
    print(f"  {label}: {k} of {n} = {k / n:.6f}" if n else f"  {label}: n = 0")
    if n:
        print(f"      Wilson [{wl:.6f}, {wh:.6f}]  "
              f"Clopper-Pearson [{cl:.6f}, {ch:.6f}]  "
              f"2 routes agree to {agree:.3e}")


def main() -> int:
    sys.path.insert(0, str(REPO / "scripts"))
    import task_list_markers as tlm                            # type: ignore
    clf = _load("_clf", "scripts/how_many_decisions_actually_need_him_2026-11-01.py")
    hook = _load("_hook", "hooks/work_not_narrate.py")
    bodies = clf.bodies()

    opens = [e for e in tlm.parse_entries(LIST) if (e.state or "").upper() == "OPEN"]
    n = len(opens)
    print("=" * 78)
    print(f"THE OPEN QUEUE ON {subprocess.run(['date','-u','+%Y-%m-%dT%H:%M:%SZ'], capture_output=True, text=True).stdout.strip()}")
    print("=" * 78)
    print(f"OPEN entries: {n}")

    rows = []
    for e in opens:
        b = bodies.get(e.ident, "")
        d = clf.classify_text(e.state, e.ruled, b)
        rows.append({
            "ident": e.ident,
            "ruled": e.ruled,
            "kind": d["kind"],
            "n_asks": len(d["live_asks"]),
            "asks": d["live_asks"],
            "residue_his": hook._residue_is_his(b),
            "first_seen": first_seen(e.ident),
            "body": b,
        })

    print()
    print("1. HOW MUCH OF THE QUEUE IS NEW FROM THE MOST RECENT WORK")
    recent = [r for r in rows if r["first_seen"] >= RECENT_FROM]
    for r in sorted(rows, key=lambda x: x["first_seen"]):
        flag = "NEW" if r["first_seen"] >= RECENT_FROM else "   "
        print(f"      {flag} {r['ident']:5s} first seen {r['first_seen']}  "
              f"kind={r['kind']:9s} live_asks={r['n_asks']}")
    report(f"raised on or after {RECENT_FROM}", len(recent), n)

    print()
    print("2. HOW MANY CARRY NO RECORDED RULING AT ALL")
    #: ★ CORRECTED 2026-11-12, THE SAME DAY IT WAS WRITTEN, AND THE FAULT IS THE
    #: ONE THIS SCRIPT EXISTS TO CATCH. `not ruled` means NO RULING DATE IS
    #: RECORDED. That is NOT the same as "needs a ruling": an entry that is mine
    #: and asks him nothing has no ruling date either, because none was ever
    #: owed. Section 6 below used this set under the label "needing a RULING he
    #: has never given", which was FALSE for B158 and B159 -- 2 entries raised
    #: hours earlier that carry `no_ruling_needed` in their authored detail. A
    #: figure answering a different question from the one its label asks is
    #: exactly the defect recorded on 2026-10-31, where 6 per cent was 1,705 per
    #: cent. The 2 sets are now reported SEPARATELY and section 6 intersects
    #: with OWED.
    unruled = [r for r in rows if not r["ruled"]]
    print("      " + ", ".join(r["ident"] for r in unruled))
    report("no ruling DATE recorded (which is not the same as needing one)",
           len(unruled), n)
    unruled_owed = [r for r in unruled if r["kind"] == "OWED"]
    print("      of those, classified OWED so a ruling IS owed: "
          + ", ".join(r["ident"] for r in unruled_owed))
    report("no ruling recorded AND a ruling owed", len(unruled_owed), n)

    print()
    print("3. THE CLASSIFIER'S OWN SPLIT, which the turn hook prints")
    owed = [r for r in rows if r["kind"] == "OWED"]
    report("classified OWED (awaits him)", len(owed), n)
    report("total live asking sentences", sum(r["n_asks"] for r in rows),
           sum(r["n_asks"] for r in rows) or 1)
    print(f"      live asking sentences across the queue: "
          f"{sum(r['n_asks'] for r in rows)} across {len(owed)} entries")

    print()
    print("4. THE 3 PREDICATES FOR 'WAS THIS ASKED AFTER HE RULED', AND THEY DISAGREE")
    print("      A = any date in the body later than the ruling   (the live classifier)")
    print("      B = a later date inside the asking sentence itself")
    print("      C = a live asking sentence positioned after the first later date")
    ruled_owed = [r for r in owed if r["ruled"]]
    disagree = 0
    for r in ruled_owed:
        b, ruled = r["body"], r["ruled"]
        dates = [(m.start(), m.group(0)) for m in clf._DATED_IN_BODY.finditer(b)]
        later = [off for off, d in dates if d > ruled]
        A = bool(later)
        B = any(any(d > ruled for d in clf._DATED_IN_BODY.findall(s))
                for s in r["asks"])
        first_later = min(later) if later else None
        ask_offs = []
        for start, sent in clf._sentences(b):
            if clf.STALE.search(sent) or not clf.ASKS.search(sent):
                continue
            if clf.FREE.search(sent):
                continue
            if any(s > start for s in [m.start() for m in clf.STALE.finditer(b)]):
                continue
            ask_offs.append(start)
        C = first_later is not None and any(p >= first_later for p in ask_offs)
        if not (A == B == C):
            disagree += 1
        print(f"      {r['ident']:5s} ruled {ruled}  A={str(A):5s} B={str(B):5s} "
              f"C={str(C):5s} {'DISAGREE' if not (A == B == C) else 'agree'}")
    report("ruled-and-OWED entries where the 3 predicates disagree",
           disagree, len(ruled_owed))

    print()
    print("5. WHAT THE PERMISSION PREDICATE ADDS, installed 2026-11-12 on his `y`")
    mine = [r for r in rows if r["kind"] != "OWED"]
    caught = [r for r in mine if r["residue_his"]]
    print("      entries the classifier calls MINE: "
          + ", ".join(r["ident"] for r in mine))
    print("      of those, needing his permission: "
          + ", ".join(r["ident"] for r in caught))
    report("MINE entries whose own text says the residue is his",
           len(caught), len(mine))
    print(f"      movable_count() = {hook.movable_count()}  "
          f"refusal_budget() = {hook.refusal_budget()}  "
          f"(floor {hook.MAX_REFUSALS_PER_TURN}, ceiling {hook.MAX_REFUSALS_CEILING})")

    print()
    print("6. THE DEFENSIBLE FLOOR OF WHAT IS OWED TO HIM")
    mine_movable = [r for r in mine if not r["residue_his"]]
    groups = {
        "needing a RULING he has never given": unruled_owed,
        "needing only PERMISSION, which is a word not a day": caught,
        "carrying his ruling, residue undecidable by text (3 predicates "
        "disagree)": ruled_owed,
        "MINE and movable without him": mine_movable,
    }
    for label, g in groups.items():
        print(f"      {len(g):2d}  {label}: "
              + (", ".join(r["ident"] for r in g) or "none"))
    #: ★ THE INVARIANT, ASSERTED RATHER THAN HOPED FOR. The 4 groups must
    #: PARTITION the open set: no entry in 2 groups, none in none. Without this
    #: a relabelling can quietly double-count, which is how section 6 came to
    #: describe 2 of my own entries as rulings he owed.
    seen: dict[str, list[str]] = {}
    for label, g in groups.items():
        for r in g:
            seen.setdefault(r["ident"], []).append(label)
    dupes = {k: v for k, v in seen.items() if len(v) > 1}
    missing = [r["ident"] for r in rows if r["ident"] not in seen]
    if dupes or missing:
        print(f"\n  PARTITION BROKEN -- in 2 groups: {dupes}; in none: {missing}")
        return 1
    print(f"      --  the 4 groups partition all {n} open entries exactly: "
          f"0 in 2 groups, 0 in none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
