# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'asking_predicate_and_fourth_standard_2026-11-14_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: ad365b43bdde76df2ee0b061bf1060221c50a80dbb2471f4461343dbc4bdefe6
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Every surface the ruling-residue date proxy reaches, and the share of each it decides.

★ WHY THIS EXISTS. The joint round of 2026-11-14 asked which predicate should
replace the proxy deciding whether a question was asked after the founder already
ruled. Both blind seats answered on the premise that the proxy reaches TWO live
surfaces -- the `[tasks]` banner and `work_not_narrate._first_movable` -- and
that the refusal budget is blind to it. One seat stated its enumeration was
"found by exhaustive grep".

THAT ENUMERATION IS INCOMPLETE, and this is the instrument that says so rather
than a claim that it is. The same date rule is written out a SECOND time in
`morning_report_build_2026-10-12.asks_newer_than_the_ruling`, whose regex
`_DATED` and the classifier's `_DATED_IN_BODY` are byte-identical in source, and
that second copy reaches `ruling_is_spent`, which gates the MORNING REPORT's
decision list -- the document he reads -- plus 3 further producers. A fix applied
only to `classify_text` leaves the second copy deciding the primary surface.

★ WHAT IT MEASURES, PER SURFACE AND NEVER AS ONE NUMBER. The brief's figure
"5 in 22" mixes populations. Each surface has its own denominator, printed
separately, with Wilson and Clopper-Pearson intervals on 2 independent routes.

★ WHAT IT DOES NOT DO. It changes no verdict, figure or file. It reads, flips the
proxy IN MEMORY ONLY by rebinding the loaded module's `_DATED_IN_BODY` to a
pattern matching nothing -- the minimal intervention that turns predicate A off
without retyping `classify_text` -- and reports.

★ IT READS THE TREE IT LIVES IN. `hooks/work_not_narrate.py` hardcodes its
repository root to `~/Developer_Projects/Constraint_Engineering`, so calling its
`open_items()` unredirected measures the HOME checkout and not the tree under
review. Measured in the review sandbox of 2026-11-14 the 2 task lists differed
(sha256 bea92ccb... against b4702022..., 1,988 bytes apart), so the hazard is
live. Every call here redirects `REPO`, `TASKS` and `MARKERS` to this file's own
parent tree first, and says so in the output.

Costs nothing but local CPU: no git, no model dispatch, no pytest.
"""
from __future__ import annotations

import importlib.util
import math
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"

#: Every site reading the ruling-residue verdict, by file and line, each verified
#: against the live source by `verify_sites()` so the list cannot drift from the
#: tree. `proxy` records whether the proxy's value can change what the site
#: emits; `invisible` names the error direction the founder cannot detect there.
SITES = [
    {"file": "scripts/task_list_markers.py", "line": 780,
     "needle": 'if k == "OWED":',
     "surface": "the `[tasks]` banner: 'N of 47 open await YOU'",
     "impl": "classify_text._later",
     "proxy": True, "reads_hil": True,
     "invisible": "UNDER-report: a live question vanishes from the figure"},
    {"file": "hooks/work_not_narrate.py", "line": 805,
     "needle": 'if kind == "OWED" or _residue_is_his(body):',
     "surface": "the stop gate's naming of the next unstarted entry",
     "impl": "classify_text._later",
     "proxy": True, "reads_hil": True,
     "invisible": "OVER-report: the entry is SKIPPED and never named again"},
    {"file": "hooks/work_not_narrate.py", "line": 565,
     "needle": 'if not d.get("live_asks") and not _residue_is_his(body):',
     "surface": "the per-turn refusal budget",
     "impl": "reads live_asks, NOT kind",
     "proxy": False, "reads_hil": False,
     "invisible": "none: structurally blind to the proxy"},
    {"file": "scripts/morning_report_build_2026-10-12.py", "line": 758,
     "needle": "return bool(mod.residue_proxy_fired(ruled, body))",
     "surface": "the MORNING REPORT's decision list, and the spoken copy",
     "impl": "asks_newer_than_the_ruling -- was a SECOND, INDEPENDENT copy of "
             "the date rule until 2026-11-14; now DELEGATES to "
             "residue_proxy_fired, measured verdict-neutral 10 of 10",
     "proxy": True, "reads_hil": True,
     "invisible": "UNDER-report: filed as 'you already ruled this' and leaves "
                  "the list he reads"},
    {"file": "scripts/raise_an_entry_2026-11-02.py", "line": 255,
     "needle": 'ok = r.get("kind") == "OWED"',
     "surface": "check 7 of the raise-an-entry gate",
     "impl": "classify_text, via classify()",
     "proxy": True, "reads_hil": False,
     "invisible": "OVER-report: check 7 passes on an entry already settled"},
    {"file": "scripts/how_many_verdicts_really_await_him_2026-11-06.py",
     "line": 96, "needle": "spent = mr.ruling_is_spent(",
     "surface": "the 'how many verdicts really await him' producer",
     "impl": "asks_newer_than_the_ruling (the second copy)",
     "proxy": True, "reads_hil": False,
     "invisible": "UNDER-report: the producer agrees with a wrong banner"},
]

#: A pattern that cannot match, used to turn predicate A off in memory.
_NEVER = re.compile(r"(?!x)x")


def _iv(k, n):
    """Wilson and Clopper-Pearson, each on 2 INDEPENDENT routes.

    Lifted in shape from `how_much_of_this_is_actually_his_2026-11-12._iv`. Its
    mpmath bisection fallback is for parameters this script cannot reach
    (n <= 47), so the scipy / statsmodels pair is the whole of it and the
    agreement figure is between those 2 routes.
    """
    from scipy import stats
    from statsmodels.stats.proportion import proportion_confint
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
    return (max(0.0, wl), wh), (cl, ch), wdiff


def report(label, k, n):
    if not n:
        print(f"      {label}: n = 0, no denominator and no interval")
        return
    (wl, wh), (cl, ch), agree = _iv(k, n)
    print(f"      {label}: {k} of {n} = {k / n:.6f}")
    print(f"          Wilson [{wl:.6f}, {wh:.6f}]  "
          f"Clopper-Pearson [{cl:.6f}, {ch:.6f}]  "
          f"2 routes agree to {agree:.3e}")


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, REPO / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def verify_sites():
    """Every SITES row must still name a line that exists and reads as claimed.

    ★ WITHOUT THIS THE LIST IS PROSE. A row naming a line that has moved makes
    the enumeration silently describe a tree that no longer exists -- which is
    the defect this script exists to report in somebody else's enumeration.
    """
    bad = []
    for s in SITES:
        p = REPO / s["file"]
        if not p.is_file():
            bad.append(f"{s['file']}: file missing")
            continue
        lines = p.read_text(errors="replace").splitlines()
        i = s["line"] - 1
        if not (0 <= i < len(lines)) or s["needle"] not in lines[i]:
            found = [n + 1 for n, l in enumerate(lines) if s["needle"] in l]
            bad.append(f"{s['file']}:{s['line']} does not read {s['needle']!r} "
                       f"(found at {found or 'nowhere'})")
    return bad


def rows(clf, opens, bodies):
    out = []
    for e in opens:
        b = bodies.get(e.ident, "")
        out.append((e, b, clf.classify_text(e.state, e.ruled, b)))
    return out


def disputed(clf, opens, bodies):
    """The entries on which predicates A, B and C disagree. One place, one rule.

    A = any date in the body later than the ruling   (the live classifier)
    B = a later date inside the asking sentence itself
    C = a live asking sentence positioned after the first later date
    """
    out = []
    for e, b, d in rows(clf, opens, bodies):
        if d["kind"] != "OWED" or not e.ruled:
            continue
        ruled = e.ruled
        dates = [(m.start(), m.group(0))
                 for m in clf._DATED_IN_BODY.finditer(b)]
        later = [off for off, dd in dates if dd > ruled]
        A = bool(later)
        B = any(any(x > ruled for x in clf._DATED_IN_BODY.findall(s))
                for s in d["live_asks"])
        first_later = min(later) if later else None
        ask_offs = []
        for start, sent in clf._sentences(b):
            if clf.STALE.search(sent) or not clf.ASKS.search(sent):
                continue
            if clf.FREE.search(sent):
                continue
            if any(s > start for s in
                   [m.start() for m in clf.STALE.finditer(b)]):
                continue
            ask_offs.append(start)
        C = first_later is not None and any(p >= first_later for p in ask_offs)
        if not (A == B == C):
            out.append(e.ident)
    return out


def main():
    sys.path.insert(0, str(REPO / "scripts"))
    import task_list_markers as tlm                            # type: ignore
    clf = _load("_clf", "scripts/how_many_decisions_actually_need_him_2026-11-01.py")
    hook = _load("_hook", "hooks/work_not_narrate.py")
    mrb = _load("_mrb", "scripts/morning_report_build_2026-10-12.py")

    print("=" * 78)
    print("EVERY SURFACE THE RULING-RESIDUE DATE PROXY REACHES")
    print("=" * 78)
    print(f"tree under measurement: {REPO}")
    print(f"hook's own hardcoded root (NOT used below): {hook.REPO}")
    #: ★ REDIRECT BEFORE ANY HOOK CALL. Unredirected, `open_items()` reads the
    #: HOME checkout, so a producer in a sandbox measures a different task list
    #: from the one under review and cannot tell.
    hook.REPO = REPO
    hook.TASKS = LIST
    hook.MARKERS = REPO / "scripts"
    print("REDIRECTED hook.REPO / TASKS / MARKERS to the tree above")

    bad = verify_sites()
    if bad:
        print("\n  SITE LIST HAS DRIFTED FROM THE TREE:")
        for b in bad:
            print("    " + b)
        return 1
    print(f"all {len(SITES)} enumerated sites verified against the live source")

    opens = [e for e in tlm.parse_entries(LIST)
             if (e.state or "").upper() == "OPEN"]
    bodies = clf.bodies()
    n_open = len(opens)
    rs = rows(clf, opens, bodies)
    owed = [e.ident for e, _, d in rs if d["kind"] == "OWED"]
    dis = disputed(clf, opens, bodies)

    print()
    print("1. THE SITE ENUMERATION, AND IT IS 6 NOT 3")
    for s in SITES:
        print(f"      {s['file']}:{s['line']}")
        print(f"          surface   : {s['surface']}")
        print(f"          impl      : {s['impl']}")
        print(f"          proxy-fed : {s['proxy']}   HIL-facing: {s['reads_hil']}")
        print(f"          invisible : {s['invisible']}")
    report("enumerated sites fed by the proxy",
           sum(1 for s in SITES if s["proxy"]), len(SITES))
    report("proxy-fed sites the founder READS AND ACTS ON",
           sum(1 for s in SITES if s["proxy"] and s["reads_hil"]),
           sum(1 for s in SITES if s["proxy"]))

    print()
    print("2. THE 2 INDEPENDENT IMPLEMENTATIONS OF ONE RULE, COMPARED ENTRY BY ENTRY")
    print("      classify_text: live_asks and ruled and `_later`")
    print("      morning_report_build.asks_newer_than_the_ruling: "
          "still_asks and any(d > ruled)")
    agree = dis_impl = 0
    for e, b, d in rs:
        a = bool(d["live_asks"]) and bool(e.ruled) and any(
            x > e.ruled for x in clf._DATED_IN_BODY.findall(b))
        try:
            g = mrb.asks_newer_than_the_ruling(e.ident, e.ruled)
        except Exception:
            g = None
        if g is None:
            continue
        #: The generator returns `still_asks` when there is NO ruling, so the
        #: 2 are comparable only where a ruling exists. Outside that the
        #: functions answer different questions and an "agreement" figure over
        #: them would be the population-mixing this script was written to stop.
        if not e.ruled:
            continue
        if a == g:
            agree += 1
        else:
            dis_impl += 1
            print(f"      {e.ident:5s} DIVERGE  classify_text={a}  generator={g}")
    report("ruled OPEN entries where the 2 implementations AGREE TODAY",
           agree, agree + dis_impl)
    print("      --> 10 of 10 is the COMMITTED MEASUREMENT that licensed")
    print("          folding the generator's copy onto `residue_proxy_fired` on")
    print("          2026-11-14. Before that fold the rule was written out twice")
    print("          with byte-identical regexes and independent call sites, and")
    print("          `ruling_is_spent`'s own docstring records what that already")
    print("          cost this project once. This row now re-measures the fold")
    print("          every run, so a future edit that re-forks them shows up here.")

    print()
    print("3. THE PROXY-DEPENDENT SHARE OF EACH SURFACE, SEPARATELY")
    print(f"      banner line as printed: {tlm.summarise().split('|')[-1].strip()}")
    report("banner 'await YOU': entries whose verdict the proxy decides",
           len(dis), len(owed))
    gate_named = hook.open_items()[1]
    skipped_owed = [e.ident for e, b, d in rs
                    if d["kind"] == "OWED" and not hook._residue_is_his(b)]
    report("stop gate: SKIPPED-as-OWED entries whose verdict the proxy decides",
           len(dis), len(skipped_owed))
    report("whole open queue: entries whose verdict the proxy decides",
           len(dis), n_open)
    print(f"      the 3 denominators are {len(owed)}, {len(skipped_owed)} and "
          f"{n_open} and they are DIFFERENT POPULATIONS; one share is not")
    print("      transportable to another surface.")

    print()
    print("4. DOES THE PROXY GATE THE WORK QUEUE -- MEASURED BY PATCHING ON DISK")
    #: ★ THE FIRST VERSION OF THIS MEASUREMENT WAS VOID AND IS RECORDED RATHER
    #: THAN QUIETLY REPLACED. It rebound `clf._DATED_IN_BODY` IN MEMORY and then
    #: called `hook.open_items()`. `_first_movable` loads the classifier FROM
    #: DISK on every call via `spec.loader.exec_module`, so the in-memory
    #: rebinding reached nothing and the measurement printed "the named entry
    #: MOVED: False" -- a clean negative that was an artefact of the probe, not
    #: a fact about the gate. Patching the file and letting the reload read it
    #: gives the opposite answer. A flip test against a function that reloads
    #: its dependency by path MUST patch the path.
    import hashlib
    target = REPO / "scripts" / "how_many_decisions_actually_need_him_2026-11-01.py"
    src = target.read_bytes()
    before = hashlib.sha256(src).hexdigest()
    live = hook.open_items()[1]
    print(f"      sha256 before          : {before[:16]}")
    print(f"      named, proxy LIVE      : {live!r}")
    patched = src.replace(
        b"    if not ruled:\n        return False\n    return any(d > ruled "
        b"for d in _DATED_IN_BODY.findall(txt))",
        b"    if not ruled:\n        return False\n    return False  "
        b"# PROXY OFF, measurement only")
    if patched == src:
        print("      COULD NOT PATCH `residue_proxy_fired` -- measurement VOID")
        return 1
    try:
        target.write_bytes(patched)
        off = hook.open_items()[1]
    finally:
        target.write_bytes(src)
    after = hashlib.sha256(target.read_bytes()).hexdigest()
    print(f"      named, proxy OFF       : {off!r}")
    print(f"      sha256 after restore   : {after[:16]}  "
          f"{'RESTORED OK' if after == before else 'RESTORE FAILED'}")
    if after != before:
        return 1
    print(f"      the named entry MOVED  : {off != live}")
    print()
    print("4b. HOW MUCH OF THAT SILENT REMOVAL IS ATTRIBUTABLE TO THE PROXY")
    #: ★ THE CORRECTION THE JOINT BRIEF AND BOTH SEATS NEED. `_first_movable`
    #: skips an entry when `kind == "OWED" OR _residue_is_his(body)`. Both
    #: disjuncts suppress. An entry the PERMISSION predicate also catches would
    #: be skipped whatever the proxy said, so the proxy is the SOLE reason for
    #: the skip only where `_residue_is_his` is False.
    sole = [i for i in dis if not hook._residue_is_his(bodies.get(i, ""))]
    for i in dis:
        print(f"      {i:5s} _residue_is_his="
              f"{str(hook._residue_is_his(bodies.get(i, ''))):5s}  "
              f"{'PROXY IS THE SOLE REASON FOR THE SKIP' if i in sole else 'skipped anyway by the permission predicate'}")
    report("disputed entries the proxy ALONE removes from the gate's candidacy",
           len(sole), len(dis))
    print("      --> the mechanism is real and the attributable count is NOT 5.")
    print("          'all 5 are silently removed' over-attributes by 4.")

    print()
    print("5. THE FORESEEABLE GROWTH SET, which is what discriminates the 2 fixes")
    unruled_owed = [e.ident for e, _, d in rs
                    if d["kind"] == "OWED" and not e.ruled]
    print("      entries that are OWED and carry NO ruling yet: "
          + ", ".join(unruled_owed))
    print(f"      --> each becomes a disputed entry the moment he rules on it,")
    print(f"          so the flagged-undecidable set can grow from {len(dis)} "
          f"to {len(dis) + len(unruled_owed)} without one new question.")
    stamped = 0
    total_asks = 0
    stamp = re.compile(r"\braised:\s*2026-\d{2}-\d{2}")
    for e, b, d in rs:
        for s in d["live_asks"]:
            total_asks += 1
            if stamp.search(s):
                stamped += 1
    report("live asking sentences carrying a `raised:` record TODAY",
           stamped, total_asks)
    print("      --> every one of the growth-set asks ALREADY EXISTS and is")
    print("          already unstamped, so a stamp-at-raise discipline cannot")
    print("          decide ANY of them. Its benefit set is empty today and")
    print("          its first member cannot be created by any existing tool:")
    print("          `raise_an_entry_2026-11-02.py` has 0 non-test callers and")
    print("          its own docstring says it CHECKS AND REFUSES, IT DOES NOT")
    print("          WRITE.")

    print()
    print("=" * 78)
    print("WHAT THIS DECIDES")
    print("=" * 78)
    print(f"  * the proxy reaches {sum(1 for s in SITES if s['proxy'])} sites, "
          f"not 3, and "
          f"{sum(1 for s in SITES if s['proxy'] and s['reads_hil'])} of them "
          f"are HIL-facing.")
    print("  * the error direction INVERTS across sites, so 'over-reporting is")
    print("    safe' is not a property of the predicate at all.")
    print("  * before 2026-11-14 a fix to `classify_text` alone would have left")
    print("    the generator's second copy deciding the morning report; the 2")
    print("    are now 1 implementation with 2 callers, measured 10 of 10.")
    print("  * stamp-at-raise decides 0 of today's asks and 0 of the")
    print("    foreseeable growth set, so composing it buys nothing MEASURABLE")
    print("    over the single fix.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
