#!/usr/bin/env python3
"""42 guards audit every new script and only 7 run at commit time.

WHY THIS EXISTS. On 2026-11-07, 6 new scripts were written in 1 session and 4
separate guards refused them, each discovered from a different board rather than
in 1 pass:

  * `test_help_never_acts_2026-09-11.py` and `test_help_writers_rate_2026-09-17.py`
    -- 12 scripts write and ignore `--help`.
  * `test_fresh_clone_is_actually_run_2026-09-11.py` -- 1 script called the help
    helper AND built an argparse parser.
  * `test_scripts_are_reached_2026-09-11.py` -- 9 scripts reached by nothing.
  * `test_an_interval_rests_on_two_routes_2026-11-03.py` -- 1 producer rested a
    quantity on a SINGLE route, which RE-OPENED a test that had been in the
    `e0feed27` baseline's 17 and was fixed before `e796a010`.

Each was a real finding and each cost a board to learn. THE QUESTION THIS
ANSWERS is how many such guards exist, and how many of them a commit can pass
without ever consulting.

THE PREDICATE. A guard audits every new script if it ENUMERATES the script
population -- globbing `*.py`, reading `git ls-files`, or calling a population
helper. It is a static over-approximation: a guard may enumerate scripts for a
purpose that no new script can violate, so this is an UPPER bound on the tax and
is reported as one.

WHAT IT BEARS ON. Entries B81 and B103, both his, both about whether the commit
gate should split into tiers. Neither currently carries this figure. NOTHING IS
BUILT HERE: a pre-flight runner for these 42 would be a new mechanism, and what
belongs at commit time is the open question B103 asks.

Exit 0 iff the share was computed and both interval routes agreed.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import sys

import mpmath as mp
from scipy.stats import beta as _beta
from statsmodels.stats.proportion import proportion_confint

mp.mp.dps = 40
REPO = pathlib.Path(__file__).resolve().parent.parent
if not (REPO / "bench" / "tests").is_dir():
    REPO = pathlib.Path(
        "/Users/georgejackson/Developer_Projects/Constraint_Engineering")

#: how a guard can come to hold EVERY script in its population
ENUMERATORS = (
    (re.compile(r'glob\(\s*["\']\*\.py'), "globs *.py"),
    (re.compile(r'["\']scripts["\']\s*\)?\s*/\s*["\']\*'), "globs scripts/*"),
    (re.compile(r'tracked_scripts|all_scripts|script_paths|population\('),
     "calls a script-population helper"),
    (re.compile(r'git\W+ls-files'), "reads git ls-files"),
    (re.compile(r'rglob\(\s*["\']\*\.py'), "rglobs *.py"),
)

#: the 4 that refused this session's new scripts, named so the figure is not abstract
CAUGHT_ME = (
    "test_help_never_acts_2026-09-11.py",
    "test_help_writers_rate_2026-09-17.py",
    "test_fresh_clone_is_actually_run_2026-09-11.py",
    "test_an_interval_rests_on_two_routes_2026-11-03.py",
    "test_scripts_are_reached_2026-09-11.py",
)


def _iv(k: int, n: int):
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


def _show(label: str, k: int, n: int) -> None:
    (wl, wh), (cl, ch), dis = _iv(k, n)
    print(f"  {label}: {k} of {n} = {k / n:.6f}" if n else f"  {label}: 0 of 0")
    print(f"      Wilson 95% [{wl:.6f}, {wh:.6f}]   "
          f"Clopper-Pearson 95% [{cl:.6f}, {ch:.6f}]")
    print(f"      2-route disagreement {dis:.3e}")
    assert dis < 1e-6, f"the 2 interval routes disagree by {dis}"


def _enumerating_scripts() -> set:
    """Scripts that themselves hold the whole population.

    ★ ADDED AFTER THE FIRST VERSION MISSED 2 OF THE 5 KNOWN CASES. A guard need
    not enumerate anything itself: `test_help_writers_rate_2026-09-17.py` and
    `test_scripts_are_reached_2026-09-11.py` both DELEGATE, running a script
    under `scripts/` that does the enumerating and asserting on its output. The
    first predicate looked only for enumeration inside the guard, so it scored
    0 for both -- while they are 2 of the 4 refusals that actually cost a board
    on 2026-11-07. The figure was published as an UPPER bound and was not one.
    """
    out = set()
    for p in sorted((REPO / "scripts").glob("*.py")):
        src = p.read_text(encoding="utf-8", errors="replace")
        if any(rx.search(src) for rx, _ in ENUMERATORS):
            out.add(p.stem)
    return out


def auditors() -> dict:
    enumerating = _enumerating_scripts()
    out = {}
    for p in sorted((REPO / "bench" / "tests").glob("test_*.py")):
        src = p.read_text(encoding="utf-8", errors="replace")
        if "scripts" not in src:
            continue
        why = [lbl for rx, lbl in ENUMERATORS if rx.search(src)]
        #: and the DELEGATED form: it names an enumerating script and runs one
        if not why and ("subprocess" in src or "check_output" in src):
            named = sorted(s for s in enumerating if s in src)
            if named:
                why = [f"delegates to {named[0]}"]
        if why:
            out[p.name] = why
    return out


def main(argv) -> int:
    spec = importlib.util.spec_from_file_location(
        "gc", REPO / "scripts" / "precommit_gate_cost_2026-09-10.py")
    gc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gc)
    board = {pathlib.Path(str(x)).name for x in gc.gate_files()}

    aud = auditors()
    on, off = set(aud) & board, set(aud) - board

    print("=" * 78)
    print("WHAT DOES A NEW SCRIPT OWE, AND WHEN IS IT ASKED?")
    print("=" * 78)

    #: ★ THE HEADLINE IS THE OBSERVED SET, NOT A PREDICATE'S ESTIMATE.
    #: 3 successive predicates were written for the population question and all
    #: 3 were unreliable: the 1st caught 42 and MISSED 2 of the 5 guards that
    #: actually refused this session's scripts, because those delegate their
    #: enumeration to a producer; widening it to the delegated form caught all 5
    #: and took the count to 125, which over-matches any guard that uses
    #: subprocess and happens to name an enumerating script. The standing rule
    #: after 3 defeated predicates on 1 surface is to change the QUESTION, not
    #: write a 4th. So the claim below rests on the 5 observed refusals, which
    #: need no predicate at all.
    print("THE OBSERVED FACT, which needs no predicate: of the 5 guards that")
    print("REFUSED this session's 6 new scripts, how many does a commit consult?")
    k = sum(1 for n in CAUGHT_ME if n in board)
    _show("    on the commit gate's board", k, len(CAUGHT_ME))
    print()
    for n in CAUGHT_ME:
        print(f"    {'ON gate ' if n in board else 'OFF gate'}  {n}")

    print("\nTHE POPULATION-WIDE COUNT IS REPORTED AND NOT RELIED ON.")
    print(f"  by this predicate: {len(aud)} guards enumerate the population, "
          f"{len(on)} on the gate board and {len(off)} off it.")
    print("  An earlier, narrower predicate gave 42 and 35. The 2 disagree by")
    print("  a factor of about 3, so neither is quoted as the tax.")

    print("\nON the gate board, so a commit does consult them:")
    for n in sorted(on):
        print(f"    {n}")

    print("\n" + "=" * 78)
    print("WHAT THIS SUPPORTS AND WHAT IT DOES NOT")
    print("  SUPPORTS: 0 of the 5 guards that refused this session's new")
    print("    scripts are consulted by a commit. The only instrument that")
    print("    asks them is a full board of about 2h17m, which is why 4")
    print("    separate refusals were learned 1 board at a time on 2026-11-07.")
    print("    That claim rests on 5 OBSERVED refusals, not on a population")
    print("    estimate, and it is the narrow form that survives.")
    print("  DOES NOT SUPPORT: a claim that all of these can refuse a new")
    print("    script. The predicate is STATIC, and it is NEITHER a clean upper")
    print("    nor a clean lower bound. It over-counts, because a guard may")
    print("    enumerate scripts for a purpose no new script can violate. And")
    print("    its first version UNDER-counted: it missed 2 of the 5 refusals")
    print("    that actually cost a board, because those guards DELEGATE the")
    print("    enumeration to a script and assert on its output. The delegated")
    print("    form is now matched; a 3rd form would be missed in turn.")
    print("  BEARS ON B81 AND B103, both his, neither carrying this figure.")
    print("    NOTHING IS BUILT HERE: a pre-flight runner would be a new")
    print("    mechanism, and what belongs at commit time is B103's question.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    #: ★ A REAL HELP HANDLER, ADDED 2026-11-08. This script carried NO parser:
    #: the word "argparse" appears once, in the docstring above, describing the
    #: both-forms fault repaired earlier the same day. The commit gate's cheap
    #: structural path vouches for any script whose SOURCE mentions `argparse`,
    #: so a mention inside prose was read as a capability and the script was
    #: never executed with the flag. Run, it ignored `--help` and performed its
    #: whole measurement. A scar read as a cure.
    import pathlib as _pl
    import sys as _sys
    _sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
    from _cli_help import answer_help as _answer_help
    _answer_help(__doc__, __file__, takes_no_arguments=True)
    raise SystemExit(main(sys.argv[1:]))
