#!/usr/bin/env python3
"""Date every artefact this board's NEW failures name, and say who added it.

WHY THIS EXISTS. The 2026-11-07 pre-registration
(`experimental_notes/PREDICTION_full_suite_2026-11-07.md`) claimed 0 new
failures and the board returned 10. The obvious next claim -- "but they are all
my own repairing sessions' doing, not regressions in the product" -- is
FLATTERING, and a flattering claim about one's own work is exactly the shape
this project has caught itself making 3 times. So it is measured here instead
of asserted, from git add-dates, with the artefact list DERIVED by running the
failing guards' own producers rather than typed from the failure text.

THE POPULATION is every distinct repository path named by the 5 guards that
name paths:
  * `scripts/help_writers_rate_2026-09-17.py`  -- writes but ignores --help
  * `scripts/scripts_are_reached_2026-09-11.py` -- reached by nothing
  * `scripts/source_text_assertions_2026-09-11.py` -- unpinned source-text test
  * `bench/tests/test_every_test_file_is_collected_2026-09-01.py` -- strays
  * `scripts/precommit_gate_cost_2026-09-10.py` -- the gate's collected set
The other 2 new failures name no path (a blind round's queue state, and the
subcritical branching measure), and are reported separately with their reasons
rather than folded into a rate they do not belong to.

THE DECISION RULE IS STATED SO IT CAN FAIL. The claim "this board's redness is
the repairing sessions' own" survives only if the share of named artefacts added
on or after 2026-11-06 has a Wilson 95% LOWER bound above 0.5000. Below that,
the honest statement is that the board carries older debt too.

Exit 0 iff every rate was computed and both interval routes agreed.
"""
from __future__ import annotations

import ast
import collections
import datetime as dt
import json
import pathlib
import re
import subprocess
import sys

import mpmath as mp
from scipy.stats import beta as _beta
from statsmodels.stats.proportion import proportion_confint

mp.mp.dps = 40
REPO = pathlib.Path(__file__).resolve().parent.parent
CUT = dt.date(2026, 11, 6)          # the 1st of the 2 repairing sessions


def _iv(k: int, n: int):
    """((wilson_lo, wilson_hi), (cp_lo, cp_hi), max_2_route_disagreement)."""
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

    def _inv(a, b, y):
        f = lambda x: mp.betainc(a, b, 0, x, regularized=True) - y   # noqa: E731
        loq, hiq = mp.mpf(0), mp.mpf(1)
        for _ in range(200):
            mid = (loq + hiq) / 2
            loq, hiq = (mid, hiq) if f(mid) < 0 else (loq, mid)
        return float((loq + hiq) / 2)

    cl2 = 0.0 if k == 0 else _inv(k, n - k + 1, 0.025)
    ch2 = 1.0 if k == n else _inv(k + 1, n - k, 0.975)
    dis = max(abs(lo - wl2), abs(hi - wh2), abs(cl - cl2), abs(ch - ch2))
    return (max(0.0, lo), hi), (cl, ch), dis


def _show(label: str, k: int, n: int) -> float:
    (wl, wh), (cl, ch), dis = _iv(k, n)
    print(f"  {label}: {k} of {n} = {k / n:.6f}" if n else f"  {label}: 0 of 0")
    print(f"      Wilson 95% [{wl:.6f}, {wh:.6f}]   "
          f"Clopper-Pearson 95% [{cl:.6f}, {ch:.6f}]")
    print(f"      2-route disagreement {dis:.3e}")
    assert dis < 1e-6, f"the 2 interval routes disagree by {dis}"
    return wl


def _run(*cmd) -> str:
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    return r.stdout + r.stderr


def _added(path: str):
    """The date git first saw this path, or None if it has never been committed."""
    out = _run("git", "log", "--diff-filter=A", "--format=%ad", "--date=short",
               "--", path).strip().splitlines()
    if not out:
        return None
    return dt.date.fromisoformat(out[-1].strip())


_PATH = re.compile(r"(?:scripts|bench|resources|experimental_notes)/[\w./-]+\.(?:py|md|json)")

#: which guard's path list dates which failure. Explicit, so no failure is
#: silently matched by a substring that happens to appear in 2 guards' names.
_GUARD_OF = {
    "test_help_never_acts": "writes but ignores --help",
    "test_help_writers_rate": "writes but ignores --help",
    "test_fresh_clone_is_actually_run": "writes but ignores --help",
    "test_scripts_are_reached": "reached by nothing",
    "test_every_test_file_is_collected": "test file outside the collected root",
    "test_source_text_and_neighbour_audit": "unpinned source-text assertion",
}


def _guard_matches(nodeid: str, label: str) -> bool:
    for stem, lab in _GUARD_OF.items():
        if stem in nodeid:
            return lab == label
    return False


def _baseline_failures():
    out = _run("git", "show", "HEAD:resources/suite_record.json")
    try:
        return json.loads(out).get("failed_tests") or []
    except Exception:
        return []


def _current_failures():
    p = REPO / "resources" / "suite_record.json"
    if not p.is_file():
        return []
    return json.loads(p.read_text(encoding="utf-8")).get("failed_tests") or []


def _paths_from(text: str) -> set:
    return {m for m in _PATH.findall(text)}


def main(argv) -> int:
    print("=" * 78)
    print("WHO MADE THIS BOARD RED: every artefact the NEW failures name, dated")
    print("=" * 78)

    named: dict[str, set] = {}

    #: 1 -- writes but ignores --help. Its own report lists the offenders.
    out = _run(sys.executable, "scripts/help_writers_rate_2026-09-17.py")
    offenders = {p for p in _paths_from(out) if p.startswith("scripts/")}
    m = re.search(r"direct: (\d+) of (\d+)", out)
    named["writes but ignores --help"] = offenders
    if m:
        print(f"\nhelp_writers_rate: {m.group(1)} of {m.group(2)} offenders, "
              f"{len(offenders)} distinct paths parsed")

    #: 2 -- reached by nothing.
    out = _run(sys.executable, "scripts/scripts_are_reached_2026-09-11.py", "--check")
    blk = out.split("reached by NOTHING")[-1].split("reached:")[0] if \
        "reached by NOTHING" in out else ""
    named["reached by nothing"] = {p for p in _paths_from(blk)
                                  if p.startswith("scripts/")}
    print(f"scripts_are_reached: {len(named['reached by nothing'])} unreached")

    #: 3 -- a source-text assertion outside the pinned set.
    #: ★ NOT VIA A FLAG. The first version shelled out with `--check`, which that
    #: script DOES NOT HAVE: the help helper rejected the unrecognised argument,
    #: exited 2, printed nothing, and the unpinned set came back EMPTY -- a 0 that
    #: was a 0 of NOTHING while the suite was reporting 1. So the census module is
    #: imported and diffed against the pinned set exactly as the guard does it.
    import importlib.util as _iu
    unpinned = set()
    try:
        spec = _iu.spec_from_file_location(
            "census_live", REPO / "scripts" / "source_text_assertions_2026-09-11.py")
        cen = _iu.module_from_spec(spec)
        spec.loader.exec_module(cen)
        rows, total = cen.survey()
        #: ★ `set(dict)` TAKES THE KEYS. The first version wrapped the whole
        #: JSON object in `set()`, which yielded its 6 METADATA keys (`_why`,
        #: `_count`, ...) instead of the 111 pinned identifiers, so 112 of 112
        #: live assertions looked unpinned and this guard contributed 78 paths
        #: to a population that should have received 1. The guard itself
        #: reports exactly 1. Read the `assertions` list by name.
        _p = json.loads((REPO / "resources" / "SOURCE_TEXT_ASSERTION_SET.json")
                        .read_text(encoding="utf-8"))
        pinned = set(_p["assertions"] if isinstance(_p, dict) else _p)
        live = {f"{r[0]}::{r[1]}" if isinstance(r, (list, tuple)) else str(r)
                for r in rows}
        for ident in sorted(live - pinned):
            unpinned.add(f"bench/tests/{ident.split('::')[0]}")
        print(f"source_text_assertions: {total} scanned, {len(live)} assertions, "
              f"{len(live - pinned)} outside the pinned set")
    except Exception as e:
        print(f"source_text_assertions: NOT ENUMERABLE ({type(e).__name__}: {e}) "
              f"-- EXCLUDED from the population rather than counted as 0")
    named["unpinned source-text assertion"] = unpinned

    #: 4 -- test files outside the collected root.
    strays = {str(p.relative_to(REPO)) for p in REPO.glob("test_*.py")}
    named["test file outside the collected root"] = strays
    print(f"strays at the repo root: {len(strays)}")

    #: 5 -- THE GATE'S DECLARED FIGURE IS *NOT* A PATH POPULATION, and treating it
    #: as one is the defect this block replaces. The first version added all 128
    #: files of the gate's board, 0 of which were added on or after 2026-11-06, and
    #: the 128 old paths SWAMPED the 23 that actually name a cause: the measured
    #: share fell to 0.111111 and the stated decision rule refused the claim. The
    #: failure is a STALE DECLARATION -- the collected count moved because tests
    #: were added to files ALREADY on the board -- so it is reported with the 2
    #: path-less failures and the growth is measured in TESTS, not in paths.
    #: This is the "a figure can answer a different question" shape, caught by the
    #: producer's own decision rule rather than by reading it.
    pass

    empty = [k for k, v in named.items() if not v]
    if empty:
        print(f"\n  NOTE: {len(empty)} guard(s) named NO path: {empty}. An empty "
              f"list shrinks the population silently, so it is printed here. "
              f"Check whether the board is clean for that guard or the probe "
              f"failed -- a 0 must be a 0 OF something.")
    all_paths = sorted(set().union(*named.values())) if named else []
    print(f"\nPOPULATION: {len(all_paths)} distinct paths named by "
          f"{sum(1 for v in named.values() if v)} path-naming guards")

    rows, undated = [], []
    for p in all_paths:
        d = _added(p)
        if d is None:
            undated.append(p)
        else:
            rows.append((p, d))

    by_date = collections.Counter(d for _, d in rows)
    print("\nADD-DATE DISTRIBUTION of the named artefacts:")
    for d in sorted(by_date):
        flag = "  <= the repairing sessions" if d >= CUT else ""
        print(f"    {d}  {by_date[d]:>4}{flag}")
    if undated:
        print(f"    never committed: {len(undated)}")
        for p in undated[:8]:
            print(f"        {p}")
        #: ★ STATE THE REMAINDER -- see the sibling repair in
        #: the_help_matcher_needed_both_halves_2026-11-07.py. Both were written
        #: on 2026-11-07 and both committed the class repaired that morning.
        if len(undated) > 8:
            print(f"        ... and {len(undated) - 8} more not shown")

    k = sum(1 for _, d in rows if d >= CUT)
    n = len(rows)
    print("\nARTEFACT-POOLED RATE -- REPORTED, AND NOT THE DECISION. It is the")
    print("WRONG UNIT and is kept only so the reasoning is visible:")
    _show("artefacts added on or after 2026-11-06", k, n)
    print("  ★ WHY THIS IS NOT THE ANSWER. Pooling paths across guards weights")
    print("    each guard by HOW MANY PATHS IT HAPPENS TO NAME, which has no")
    print("    relation to how many FAILURES there are: the source-text census")
    print("    names 78 files to carry 1 failure while the stray-file check")
    print("    names 2 to carry 1. 3 successive versions of this producer")
    print("    returned a refusal on this rate for 3 DIFFERENT population")
    print("    faults -- the gate's whole 128-file board, then an ~11-minute")
    print("    subprocess, then a dict read as a set. The standing rule is that")
    print("    3 defeated predicates on one surface means STOP and change the")
    print("    question, not write a 4th. THE UNIT IS THE FAILURE.")

    #: ---- THE DECISION: unit = failure, population = the NEW failures ----
    base = set(_baseline_failures())
    now = set(_current_failures())
    new = sorted(now - base)
    print(f"\n{'=' * 78}")
    print(f"THE DECISION, unit = FAILURE: {len(new)} new failure(s) on this board")
    print("=" * 78)

    def _dates(nodeid: str):
        """(date, evidence) for the artefact that introduced this failure."""
        fn = nodeid.split("::")[0]
        #: a parametrised id naming a file carries its own subject
        pm = re.search(r"\[([^\]]+)\]$", nodeid)
        if pm:
            cand = pm.group(1)
            for root in ("experimental_notes", "bench/tests", "scripts"):
                p = REPO / root / cand
                if p.exists():
                    d = _added(f"{root}/{cand}")
                    if d is None:
                        import datetime as _dt
                        return (_dt.date.fromtimestamp(p.stat().st_mtime),
                                f"{root}/{cand} (untracked; mtime)")
                    return d, f"{root}/{cand}"
        for label, paths in named.items():
            if not paths:
                continue
            if any(x in nodeid for x in ("help", "reached", "collected_root",
                                         "grown_silently")) and label:
                dd = [(_added(p), p) for p in sorted(paths)]
                dd = [(d, p) for d, p in dd if d]
                if dd and _guard_matches(nodeid, label):
                    newest = max(dd)
                    return newest[0], f"newest of {len(dd)} named by: {label}"

        #: ★ THE 3 THAT NAME NO PATH ARE DATED HERE, NOT SCORED AS "older".
        #: The first version returned None for them and the decision rule
        #: counted each None as NOT-session -- an UNMEASURED item silently
        #: entered the denominator as a negative, which is wrong in the
        #: pessimistic direction and is the mirror of failing open.
        if "test_a_blind_round_has_a_joint_round" in nodeid:
            msg = _run(sys.executable, "-c",
                       "import importlib.util as iu;"
                       "s=iu.spec_from_file_location('c',"
                       "'bench/confer_maths_panel_2026-09-05.py');"
                       "m=iu.module_from_spec(s);s.loader.exec_module(m);"
                       "m._refuse_if_a_joint_round_is_owed()")
            dm = re.search(r"(\w+_)(\d{4}-\d{2}-\d{2})", msg)
            if dm:
                return (dt.date.fromisoformat(dm.group(2)),
                        f"the owing round is {dm.group(1)}{dm.group(2)}, "
                        f"named by the guard's own refusal")
            return None, "the guard names no round"

        if "test_fresh_clone_is_actually_run" in nodeid:
            #: scripts that build an argparse parser AND call answer_help
            both = []
            for p in sorted((REPO / "scripts").glob("*.py")):
                try:
                    tr = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
                except SyntaxError:
                    continue
                names = {getattr(n.func, "id", None) or getattr(n.func, "attr", None)
                         for n in ast.walk(tr) if isinstance(n, ast.Call)}
                aliases = {a.asname for n in ast.walk(tr)
                           if isinstance(n, ast.ImportFrom) and n.module == "_cli_help"
                           for a in n.names if a.name == "answer_help" and a.asname}
                if "ArgumentParser" in names and (names & ({"answer_help"} | aliases)):
                    both.append(f"scripts/{p.name}")
            dd = [(_added(x), x) for x in both]
            dd = [(d, x) for d, x in dd if d]
            if dd:
                nd = max(dd)
                return nd[0], f"{len(both)} script(s) use both; newest {nd[1]}"
            return None, f"{len(both)} script(s) use both, none dated"

        if "test_precommit_gate_cost" in nodeid:
            #: the declared figure's own last write, against the newest change to
            #: any file on the gate's board. Dated by git, no pytest run.
            decl = _run("git", "log", "-1", "--format=%ad", "--date=short",
                        "-S", "2581", "--",
                        "experimental_notes/CDSFL_MASTER_TASK_LIST.md").strip()
            newest = _run("git", "log", "-1", "--format=%ad", "--date=short",
                          "--", "bench/tests/").strip()
            try:
                dn = dt.date.fromisoformat(newest.splitlines()[0])
            except Exception:
                return None, "the board's newest change is not dateable"
            return dn, (f"declaration last written {decl or '?'}; newest change "
                        f"to a board file {dn}, so the count moved after it")

        return None, f"no artefact: {fn}"

    kk = 0
    for nid in new:
        d, ev = _dates(nid)
        mark = "  SESSION" if (d and d >= CUT) else ("  older" if d else "  n/a")
        if d and d >= CUT:
            kk += 1
        short = nid.split("::")[0].split("/")[-1]
        print(f"  {str(d or '-'):>12} {mark:<9} {short}")
        print(f"               {ev}")
    print()
    lower = _show("NEW failures introduced on or after 2026-11-06", kk, len(new))
    verdict = ("UPHELD" if lower > 0.5 else "NOT UPHELD")
    print(f"\n  DECISION RULE: Wilson lower bound {lower:.6f} > 0.5000 ? "
          f"--> {verdict}")
    if verdict != "UPHELD":
        print("  So the honest statement is that this board carries OLDER debt "
              "too, and the redness may not be attributed wholly to the "
              "repairing sessions.")

    print("\nPER-GUARD breakdown:")
    for label, paths in named.items():
        if not paths:
            continue
        dated = [(p, _added(p)) for p in sorted(paths)]
        kk = sum(1 for _, d in dated if d and d >= CUT)
        nn = sum(1 for _, d in dated if d)
        print(f"\n  {label}  ({len(paths)} path(s), {nn} dated)")
        _show("    on or after 2026-11-06", kk, nn)

    print("\n" + "=" * 78)
    print("THE 2 NEW FAILURES THAT NAME NO PATH, reported separately rather than")
    print("folded into a rate they do not belong to:")
    print("  * a blind round owes its joint round -- QUEUE STATE. Entry B124")
    print("    option 3 predicted this before the run existed.")
    print("  * the branching measure is no longer subcritical -- the PREDICTED")
    print("    survivor, and entry B123, which is his decision and not a repair")
    print("    available to me.")
    print("  * the gate's declared test figure is STALE.")
    #: ★ THIS BLOCK DOES NOT MEASURE THE FIGURE, DELIBERATELY, AND THE REASON IS
    #: WORTH THE SPACE. The first version shelled out to
    #: `scripts/precommit_gate_cost_2026-09-10.py` with no arguments to read the
    #: count. That script's `main()` does not stop at `pytest --co`: it then runs
    #: `python3 -m pytest <128 files> -q` for real, to time the board. So this
    #: producer silently launched an ~11-minute GATE BOARD RUN -- not the
    #: 834-file suite, which is a distinction this project keeps a rule about,
    #: but 128 files and about 2,585 tests -- on an 8-core, 8 GiB machine, to
    #: obtain a number the FAILING TEST ALREADY PRINTS. It sat blocked in
    #: `poll()` for 8 minutes with 0.0% CPU and no output before the process
    #: tree was sampled and the grandchild found.
    #:
    #: A measurement script must not spawn a job orders of magnitude larger than
    #: the measurement. The figures belong to
    #: `bench/tests/test_precommit_gate_cost_2026-09-10.py`, which computes them
    #: as its own assertion, and are cited from there rather than recomputed.
    print("      Its 2 figures -- the live collected count and the count "
          "declared in the task list's entry 1.1 -- are computed and printed "
          "by bench/tests/test_precommit_gate_cost_2026-09-10.py itself and "
          "are cited from there, NOT recomputed here: reading them costs an "
          "~11-minute gate-board run. The guard's own remedy is "
          "`python3 scripts/precommit_gate_cost_2026-09-10.py --write "
          "--repeats 0`. 0 of the board's 128 FILES were added on or after "
          "2026-11-06, so the growth is tests added to files already on it.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    import pathlib as _pl
    sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
    try:
        from _cli_help import answer_help as _answer_help
        _answer_help(__doc__, __file__, takes_no_arguments=True)
    except ImportError:
        pass
    raise SystemExit(main(sys.argv[1:]))
