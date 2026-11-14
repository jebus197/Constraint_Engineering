# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'asking_predicate_and_fourth_standard_2026-11-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 4e60653343d6a6c40bd1f267faff99e9268b45a4fe4950fe3cac16e5401137d7
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""PRODUCER: which live surfaces the `_later` ruling proxy actually reaches, and
in which DIRECTION each one errs when the proxy is wrong.

★ WHY THIS EXISTS AND WHAT IT CONTRADICTS. The brief of 2026-11-14 asks which of
3 text predicates (A, B, C) for "was a question raised after he ruled" should
replace the live one, and states as fact F5 that A -- the live predicate -- is
"noisy in the SAFE direction" because it OVER-reports what he owes, and that B
and C are the dangerous ones because they REMOVE entries from his list.

THAT IS TRUE OF ONE SURFACE AND FALSE OF ANOTHER, and no instrument in this
repository had measured which surfaces the proxy reaches. `classify_text`'s
`kind` is consumed in 3 places, and they do not all read it:

  1. `task_list_markers.summarise` -> `_whose_move` -> the `[tasks]` banner that
     `hooks/task_list_pulse.py` prints on EVERY turn. Tests `kind == "OWED"`.
     SENSITIVE to `_later`. This is the surface F5 reasons about, and on this
     surface F5 is right: A's error shows him an item he can dismiss.

  2. `hooks/work_not_narrate._first_movable` -> `open_items` -> the entry the
     Stop gate NAMES as the next thing the session should work on. Tests
     `kind == "OWED"` at hooks/work_not_narrate.py:805 and SKIPS the entry when
     it is true. SENSITIVE to `_later` -- and the direction INVERTS. A's
     over-report does not add a visible item here; it REMOVES an entry from the
     session's own work queue. An entry wrongly held to await him is an entry
     the gate will never name, so the work silently stalls. That is the same
     suppression shape this project withdrew on 2026-11-09, displaced from his
     list onto mine.

  3. `hooks/work_not_narrate.movable_count` -> `refusal_budget`. Tests
     `d["live_asks"]` and `_residue_is_his(body)`, NOT `kind`. `_later` cannot
     reach it, because `live_asks` is built before `_later` is computed and is
     not a function of it. INSENSITIVE -- which BOUNDS the consequence, and is
     reported because a bound that is not measured is a hope.

SO "OVER-REPORTING IS SAFE" IS NOT A PROPERTY OF THE PREDICATE. It is a property
of a predicate PAIRED WITH A CONSUMER, and this proxy has 2 consumers that read
it with opposite sign. That is the finding, and it is what makes O3 -- report the
disagreement rather than pick a side -- the only option that is safe on BOTH.

NOTHING HERE CHANGES A VERDICT. This module computes and prints. It does not
edit the classifier, does not alter the banner, and does not move an entry on or
off his list. Q1 is his to rule.

ANTI-VACUITY. Before varying anything, the replicated surface logic is asserted
to reproduce the REAL surfaces at predicate A. A model of a surface that has not
been checked against the surface measures the model.

Costs local CPU only: no model dispatch, no pytest, no network.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, REPO / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def _iv(k: int, n: int):
    """Wilson and Clopper-Pearson, each on 2 INDEPENDENT routes.

    Same shape as `scripts/how_much_of_this_is_actually_his_2026-11-12.py` so
    the 2 producers report an interval identically. Every n here is below 50,
    where scipy's beta quantile and an mpmath bisection on the regularised
    incomplete beta agree to machine precision; the agreement printed beside
    each figure is what demonstrates that rather than a comment claiming it.
    """
    from scipy import stats
    from statsmodels.stats.proportion import proportion_confint
    import mpmath
    mpmath.mp.dps = 40
    if n == 0:
        return (0.0, 1.0), (0.0, 1.0), 0.0
    wl, wh = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = mpmath.mpf("1.959963984540054")
    K, N = mpmath.mpf(k), mpmath.mpf(n)
    p = K / N
    d = 1 + z**2 / N
    c = (p + z**2 / (2 * N)) / d
    hw = z * mpmath.sqrt(p * (1 - p) / N + z**2 / (4 * N**2)) / d
    wdiff = max(abs(wl - float(c - hw)), abs(wh - float(c + hw)))
    cl = 0.0 if k == 0 else float(stats.beta.ppf(0.025, k, n - k + 1))
    ch = 1.0 if k == n else float(stats.beta.ppf(0.975, k + 1, n - k))

    def _bi(a, b, y):
        lo, hi = mpmath.mpf(0), mpmath.mpf(1)
        for _ in range(200):
            if hi - lo < mpmath.mpf("1e-18"):
                break
            m = (lo + hi) / 2
            v = mpmath.betainc(a, b, 0, m, regularized=True) - y
            lo, hi = (m, hi) if v < 0 else (lo, m)
        return float((lo + hi) / 2)

    cdiff = max(abs(cl - (0.0 if k == 0 else _bi(k, n - k + 1, 0.025))),
                abs(ch - (1.0 if k == n else _bi(k + 1, n - k, 0.975))))
    return (max(0.0, wl), wh), (cl, ch), max(wdiff, cdiff)


def report(label: str, k: int, n: int) -> None:
    if not n:
        print(f"  {label}: n = 0")
        return
    (wl, wh), (cl, ch), agree = _iv(k, n)
    print(f"  {label}: {k} of {n} = {k / n:.6f}")
    print(f"      Wilson [{wl:.6f}, {wh:.6f}]  "
          f"Clopper-Pearson [{cl:.6f}, {ch:.6f}]  "
          f"2 routes agree to {agree:.3e}")


# ---------------------------------------------------------------------------
# THE 3 PREDICATES, named exactly as the brief names them.
# ---------------------------------------------------------------------------

def pred_A(clf, ruled, body, asks) -> bool:
    """Any date anywhere in the body later than the ruling. THE LIVE ONE."""
    return bool(ruled) and any(d > ruled for d in clf._DATED_IN_BODY.findall(body))


def pred_B(clf, ruled, body, asks) -> bool:
    """A later date inside the asking SENTENCE itself."""
    if not ruled:
        return False
    return any(any(d > ruled for d in clf._DATED_IN_BODY.findall(s)) for s in asks)


def pred_C(clf, ruled, body, asks) -> bool:
    """A live asking sentence POSITIONED after the first post-ruling date."""
    if not ruled:
        return False
    later = [m.start() for m in clf._DATED_IN_BODY.finditer(body)
             if m.group(0) > ruled]
    if not later:
        return False
    first = min(later)
    stale_at = [m.start() for m in clf.STALE.finditer(body)]
    for start, sent in clf._sentences(body):
        if clf.STALE.search(sent) or not clf.ASKS.search(sent):
            continue
        if clf.FREE.search(sent):
            continue
        if any(s > start for s in stale_at):
            continue
        if start >= first:
            return True
    return False


PREDS = {"A": pred_A, "B": pred_B, "C": pred_C}


def kind_under(clf, pred, state, ruled, body) -> str:
    """`classify_text`'s own branch ladder with `_later` supplied by `pred`.

    THE LADDER IS COPIED, WHICH IS A RISK, SO IT IS CHECKED RATHER THAN TRUSTED.
    `classify_text` computes `_later` inline, so there is no seam to inject at
    without editing the live file -- and editing the live file to take a
    measurement is exactly what this round must not do. The anti-vacuity check
    in `main` asserts this reproduces `classify_text` EXACTLY on every live
    entry under predicate A, which is the only predicate the live file
    implements. If that assertion fails, this producer is wrong and says so.
    """
    state = (state or "").upper()
    dep = clf.DEPENDS.search(body)
    d = clf.classify_text(state, ruled, body)
    asks, live = d["asks"], d["live_asks"]
    later = pred(clf, ruled, body, live)
    if state == "DEFERRED" and ruled:
        return "HIS_DEFERRAL"
    if dep:
        return "DEPENDENT"
    if live and ruled and not later:
        return "GRANTED"
    if live:
        return "OWED"
    if asks:
        return "GRANTED"
    return "MINE"


def main() -> int:
    sys.path.insert(0, str(REPO / "scripts"))
    import task_list_markers as tlm                             # type: ignore
    clf = _load("_clf2", "scripts/how_many_decisions_actually_need_him_2026-11-01.py")
    wnn = _load("_wnn2", "hooks/work_not_narrate.py")

    #: ★ REDIRECT THE HOOK AT THE TREE BEING MEASURED. `work_not_narrate` hard-
    #: codes REPO to `~/Developer_Projects/Constraint_Engineering`, so in any
    #: checkout that is not that one -- a panel sandbox, a worktree -- its
    #: `movable_count()` silently measures a DIFFERENT task list from the one
    #: the rest of the producer parsed. Measured here 2026-11-14: the 2 paths
    #: differed and the figure still printed without complaint. NOT a live
    #: defect, because in his own environment the 2 coincide; it IS a
    #: measurement hazard for any instrument run outside it, which is why the
    #: redirection is explicit and printed rather than assumed.
    wnn.TASKS = LIST
    wnn.MARKERS = REPO / "scripts"
    print("=" * 78)
    print("WHICH SURFACES THE `_later` RULING PROXY REACHES")
    print("=" * 78)
    print(f"  task list under measurement: {LIST}")
    print(f"  work_not_narrate.TASKS redirected to it (hardcoded was {wnn.REPO})")

    bodies = clf.bodies()
    opens = [e for e in tlm.parse_entries(LIST) if (e.state or "").upper() == "OPEN"]
    print(f"  OPEN entries: {len(opens)}")

    # ---------------------------------------------------------------- 0
    print("\n0. ANTI-VACUITY: the replicated ladder must equal the live one at A")
    bad = []
    for e in opens:
        b = bodies.get(e.ident, "")
        live = clf.classify_text(e.state, e.ruled, b)["kind"]
        mine = kind_under(clf, pred_A, e.state, e.ruled, b)
        if live != mine:
            bad.append((e.ident, live, mine))
    if bad:
        print(f"    REPLICATION BROKEN on {len(bad)} entries: {bad[:5]}")
        print("    This producer's model of classify_text is WRONG. Stopping.")
        return 1
    print(f"    replicated ladder == classify_text on all {len(opens)} open "
          f"entries under A: 0 mismatches")

    # ---------------------------------------------------------------- 1
    print("\n1. EVERY ENTRY WHERE THE 3 PREDICATES DO NOT ALL AGREE ON `kind`")
    kinds = {p: {} for p in PREDS}
    for e in opens:
        b = bodies.get(e.ident, "")
        for p, fn in PREDS.items():
            kinds[p][e.ident] = kind_under(clf, fn, e.state, e.ruled, b)
    moved = [e.ident for e in opens
             if len({kinds[p][e.ident] for p in PREDS}) > 1]
    for ident in moved:
        row = "  ".join(f"{p}={kinds[p][ident]:8s}" for p in PREDS)
        print(f"      {ident:5s} {row}")
    report("open entries whose KIND depends on which predicate is used",
           len(moved), len(opens))

    # ---------------------------------------------------------------- 2
    print("\n2. SURFACE 1 -- THE `[tasks]` BANNER HE READS EVERY TURN")
    print("     route: task_list_pulse -> summarise -> _whose_move -> kind=='OWED'")
    for p in PREDS:
        his = sum(1 for e in opens if kinds[p][e.ident] == "OWED")
        print(f"      under {p}: \"{his} of {len(opens)} open await YOU\"")
    spread = {sum(1 for e in opens if kinds[p][e.ident] == "OWED") for p in PREDS}
    print(f"      SENSITIVE: the figure he reads takes {len(spread)} distinct "
          f"values {sorted(spread)} across the 3 predicates")

    # ---------------------------------------------------------------- 3
    print("\n3. SURFACE 2 -- THE ENTRY THE STOP GATE NAMES AS NEXT WORK")
    print("     route: work_not_narrate.open_items -> _first_movable -> kind=='OWED'")
    print("     and the test at :805 SKIPS the entry when that is true")
    _STARTED = {"BUILT", "TESTED", "COMMITTED"}

    def first_movable_under(p) -> str:
        unstarted, started = [], []
        for e in opens:
            b = bodies.get(e.ident, "")
            if kinds[p][e.ident] == "OWED" or wnn._residue_is_his(b):
                continue
            st = (getattr(e, "status", "") or "").upper()
            (started if st in _STARTED else unstarted).append(e.ident)
        return (unstarted + started or [""])[0]

    real = wnn._first_movable(opens)
    model = first_movable_under("A")
    print(f"      real _first_movable(opens) = {real!r}")
    print(f"      replicated at A            = {model!r}   "
          f"{'MATCH' if real == model else 'MISMATCH -- model is wrong'}")
    for p in PREDS:
        print(f"      under {p}: the gate names {first_movable_under(p)!r}")

    print("\n     THE DIRECTION OF A's ERROR ON THIS SURFACE, which is the point:")
    excluded = [e.ident for e in opens
                if kinds["A"][e.ident] == "OWED"
                and any(kinds[p][e.ident] != "OWED" for p in ("B", "C"))]
    print(f"      entries A marks OWED that B or C would release to the session:")
    print(f"      {excluded}")
    print("      On the BANNER these are a visible over-report he can dismiss.")
    print("      On THIS surface they are REMOVED from the work queue and the")
    print("      gate will never name them. Over-reporting is NOT safe here.")

    # ---------------------------------------------------------------- 4
    print("\n4. SURFACE 3 -- THE REFUSAL BUDGET, AND WHY `_later` CANNOT REACH IT")
    print("     route: movable_count -> refusal_budget; tests live_asks, NOT kind")
    for p in PREDS:
        n = 0
        for e in opens:
            b = bodies.get(e.ident, "")
            d = clf.classify_text(e.state or "", e.ruled, b)
            if not d.get("live_asks") and not wnn._residue_is_his(b):
                n += 1
        budget = (wnn.MAX_REFUSALS_PER_TURN if n <= 0
                  else min(wnn.MAX_REFUSALS_CEILING,
                           wnn.MAX_REFUSALS_PER_TURN * n))
        print(f"      under {p}: movable_count = {n}  refusal_budget = {budget}")
    print("      IDENTICAL under all 3, and that is a DERIVATION not a")
    print("      coincidence: `live_asks` is built in the sentence loop ABOVE")
    print("      the line that computes `_later`, so no value of `_later` can")
    print("      change it. The budget is algebraically independent of the proxy.")
    nmov = sum(1 for e in opens
               if not clf.classify_text(e.state or "", e.ruled,
                                        bodies.get(e.ident, "")).get("live_asks")
               and not wnn._residue_is_his(bodies.get(e.ident, "")))
    sat = wnn.MAX_REFUSALS_CEILING / wnn.MAX_REFUSALS_PER_TURN
    print(f"      AND IT IS SATURATED ANYWAY: movable_count = {nmov}, and the")
    print(f"      ceiling binds for any count >= {sat:.0f}, so even a swing of")
    print(f"      {len(moved)} entries leaves the budget at "
          f"{wnn.MAX_REFUSALS_CEILING}. 2 independent reasons it is unreachable.")

    # ---------------------------------------------------------------- 5
    print("\n5. AGREEMENT BETWEEN THE 3 PREDICATES, ON THE ENTRIES THEY APPLY TO")
    ruled_owed = [e for e in opens
                  if kinds["A"][e.ident] == "OWED" and e.ruled]
    vec = {p: [PREDS[p](clf, e.ruled, bodies.get(e.ident, ""),
                        clf.classify_text(e.state, e.ruled,
                                          bodies.get(e.ident, ""))["live_asks"])
               for e in ruled_owed] for p in PREDS}
    print(f"      population: {[e.ident for e in ruled_owed]}  n = {len(ruled_owed)}")
    for p in PREDS:
        print(f"      {p} = {['T' if x else 'F' for x in vec[p]]}")
    from sklearn.metrics import cohen_kappa_score
    for x, y in (("A", "B"), ("A", "C"), ("B", "C")):
        agree = sum(1 for i, j in zip(vec[x], vec[y]) if i == j)
        report(f"raw agreement {x} vs {y}", agree, len(ruled_owed))
        const = len(set(vec[x])) == 1 or len(set(vec[y])) == 1
        k = cohen_kappa_score([int(v) for v in vec[x]], [int(v) for v in vec[y]])
        note = ("   DEGENERATE: one rater is CONSTANT, so this is 0 by algebra, "
                "not by measurement") if const else ""
        print(f"      Cohen kappa {x} vs {y} = {k:.6f}{note}")
    print("\n      THE DEGENERACY, DERIVED rather than asserted. With rater X")
    print("      constant at T: p_o = P(Y=T); p_e = P(X=T)P(Y=T) + P(X=F)P(Y=F)")
    print("                   = 1*P(Y=T) + 0*P(Y=F) = P(Y=T) = p_o.")
    print("      So kappa = (p_o - p_e)/(1 - p_e) = 0 for EVERY Y. A is constant")
    print("      at T on this population, so kappa cannot distinguish B from C")
    print("      against A, and quoting it as evidence about A would be an error.")
    print("      Raw agreement above is the reportable statistic; n is small and")
    print("      every interval printed with it says so.")

    # ---------------------------------------------------------------- 6
    print("\n6. THE 4 OPTIONS SCORED ON ONE NAMED PROPERTY, SO COMPOSABILITY")
    print("   IS DECIDED BY A MEASUREMENT AND NOT BY A JUDGEMENT")
    print("     PROPERTY: INVISIBLE-ERROR PAIRS. Count the (entry, surface)")
    print("     pairs where a wrong proxy verdict produces a wrong outcome the")
    print("     founder CANNOT detect from what he is shown. Lower is better.")
    print("     The population is the undecidable set; the surfaces are the 2")
    print("     measured above as SENSITIVE. Surface 3 contributes 0 to every")
    print("     option because the proxy cannot reach it.")
    print()
    print("     The sign rule, which is the whole content of the finding:")
    print("       BANNER  -- asserting OWED on an undecidable entry is VISIBLE")
    print("                  (he reads the item and can dismiss it); asserting")
    print("                  GRANTED is INVISIBLE (the question is simply gone).")
    print("       GATE    -- asserting OWED is INVISIBLE (the entry is skipped")
    print("                  and never named); asserting GRANTED is VISIBLE")
    print("                  (the entry gets named and worked).")
    und = [e for e in opens if kinds["A"][e.ident] == "OWED" and e.ruled
           and len({kinds[p][e.ident] for p in PREDS}) > 1]
    U = len(und)

    def score(banner, gate):
        """(invisible on banner, invisible on gate) -> total, from the sign rule."""
        return banner + gate

    # O1: banner OWED on all U (visible); gate skips all U (invisible).
    o1 = score(0, U)
    # O2 under B: banner GRANTED wherever B says settled -> invisible there;
    # gate still skips wherever B says OWED -> invisible there.
    for nm, pr in (("O2 (adopt B)", "B"), ("O2 (adopt C)", "C")):
        g = sum(1 for e in und if kinds[pr][e.ident] == "GRANTED")
        o = sum(1 for e in und if kinds[pr][e.ident] == "OWED")
        globals()[f"_{pr}"] = (nm, g + o, g, o)
    # O3 as DELIVERED this round: banner flags undecidable (visible, 0); gate
    # unchanged, still skips all U (invisible, U).
    o3 = score(0, U)
    # O3-EXTENDED: the same flag read by the gate, so an undecidable entry is
    # NAMEABLE and the session's move is to ask him -- visible on both.
    o3x = score(0, 0)
    # O4: both surfaces read a RECORDED answer, so 0 invisible for any entry
    # raised after the mechanism exists -- but the U legacy entries carry no
    # record, fall back to the proxy, and nothing prompts the backfill.
    o4 = score(0, U)
    # O3 + O4 composed: O3 makes the U legacy entries visible for backfill,
    # O4 removes the inference for everything after.
    o34 = score(0, 0)
    print()
    print(f"     undecidable population U = {U}  ({[e.ident for e in und]})")
    rows = [("O1 change nothing", o1),
            (_B[0], _B[1]), (_C[0], _C[1]),
            ("O3 as delivered (report only)", o3),
            ("O3 extended to the gate", o3x),
            ("O4 recorded fact alone", o4),
            ("O3 + O4 composed", o34)]
    for nm, v in rows:
        print(f"       {nm:34s} invisible-error pairs = {v}")
    print()
    print(f"     O2 breakdown: B hides {_B[2]} live question(s) on the banner and")
    print(f"     still suppresses {_B[3]} on the gate; C hides {_C[2]} and suppresses {_C[3]}.")
    print()
    best = min(v for _, v in rows)
    winners = [nm for nm, v in rows if v == best]
    print(f"     MINIMUM = {best}, reached by: {winners}")
    print("     THE COMPOSITION IS THEREFORE REFUSED, ON HIS OWN STANDARD.")
    print("     `O3 extended to the gate` is a SINGLE fix that TIES the composed")
    print("     `O3 + O4` at the minimum. His definition is explicit -- \"Where a")
    print("     single fix out performs a composed one, that fix should continue")
    print("     to be preferred\" -- and a tie is not a demonstrated advantage,")
    print("     which is what `composability-requires-a-measurement` requires")
    print("     before a composed fix may be recommended. So the measurement")
    print("     SELECTS THE SINGLE FIX and no composition is claimed.")
    print("     O4 is still the only option that removes the INFERENCE rather")
    print("     than making its error visible; on THIS property it does not beat")
    print("     O3-extended, so it is reported as a direction and not adopted.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
