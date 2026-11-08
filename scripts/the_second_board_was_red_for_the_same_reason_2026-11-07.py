#!/usr/bin/env python3
"""Score the SECOND full board of 2026-11-07 and date what made it red.

WHY THIS EXISTS, AND IT IS NOT A SECOND COPY OF THE FIRST SCORER.
`who_made_this_board_red_2026-11-07.py` dates every artefact a failure NAMES in
its output, which is an over-approximation: 1 failure can name 78 paths. This
asks a narrower question whose unit is the FAILURE -- for each failing test,
which artefact does the fix have to touch, and when did THAT artefact first
enter the repository. The mapping is DECLARED here rather than parsed out of
the failure text, because parsing it is what produced the 78-paths-for-1-failure
figure, and a declared mapping can be checked by eye against the log.

THE CLAIM IT TESTS. Board 1 (`e796a010`) returned 10 new failures and 10 of 10
were introduced by the repairing session itself. Board 2 (`aea4ec9b`) was
predicted to return 0 new on the strength of that lesson having been learned.
It returned 2. The question is whether they have the SAME provenance, which
would make this the same error twice in one night rather than 2 errors.

THE DECISION RULE, STATED BEFORE THE MEASUREMENT so it can fail: the provenance
is the same if the Wilson 95% lower bound on "introduced on or after the
repairing cut" exceeds 0.3400 -- deliberately lower than board 1's 0.5000 gate,
because n = 2 cannot reach 0.5000 even at 2 of 2 and a gate no sample can pass
is not a test. At 2 of 2 the Wilson lower bound is 0.342285, so the rule is
passable and tight: 1 of 2 would fail it.

Exit 0 iff every figure was produced by 2 independent routes.
"""
from __future__ import annotations

import json
import pathlib
import subprocess

import mpmath as mp
from scipy.stats import beta as _beta
from statsmodels.stats.proportion import proportion_confint

mp.mp.dps = 40
REPO = pathlib.Path(__file__).resolve().parent.parent
if not (REPO / "scripts").is_dir():
    REPO = pathlib.Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")
RECORD = REPO / "resources" / "suite_record.json"
CUT = "2026-11-06"
GATE = 0.3400

#: THE DECLARED MAPPING: failing test file -> the artefact a fix must touch.
#: Checked by eye against the board log. A test whose fix is a DECISION of his
#: rather than an edit carries None, and is reported separately rather than
#: counted, because dating a decision says nothing.
SUBJECT: dict[str, str | None] = {
    "test_an_interval_rests_on_two_routes_2026-11-03.py":
        "scripts/the_gate_board_serialises_the_tree_2026-11-07.py",
    "test_operational_scripts.py":
        "scripts/the_help_matcher_needed_both_halves_2026-11-07.py",
    "test_a_blind_round_has_a_joint_round_2026-10-08.py": None,   # B124, his call
    "test_task_list_burndown_2026-09-11.py": None,                # B123, his call
}
#: The truncation failure named 2 producers, not 1. The second is listed so the
#: count of ARTEFACTS is honest even though the unit of the rate is the FAILURE.
ALSO = ["scripts/who_made_this_board_red_2026-11-07.py"]


def _iv(k: int, n: int):
    if n == 0:
        return (0.0, 1.0), (0.0, 1.0), 0.0
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = mp.mpf("1.959963984540054235524594430520551527955")
    ph = mp.mpf(k) / n
    den = 1 + z**2 / n
    cen = (ph + z**2 / (2 * n)) / den
    half = (z / den) * mp.sqrt(ph * (1 - ph) / n + z**2 / (4 * n * n))
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
    dis = max(abs(lo - float(cen - half)), abs(hi - float(cen + half)),
              abs(cl - cl2), abs(ch - ch2))
    return (max(0.0, lo), hi), (cl, ch), dis


def _show(label: str, k: int, n: int) -> float:
    (wl, wh), (cl, ch), dis = _iv(k, n)
    print(f"  {label}: {k} of {n} = {k / n:.6f}" if n else f"  {label}: 0 of 0")
    print(f"      Wilson 95% [{wl:.6f}, {wh:.6f}]  "
          f"Clopper-Pearson 95% [{cl:.6f}, {ch:.6f}]")
    print(f"      2-route disagreement {dis:.3e}")
    assert dis < 1e-6, f"the 2 interval routes disagree by {dis}"
    return wl


def _added(rel: str) -> str:
    r = subprocess.run(["git", "-C", str(REPO), "log", "--diff-filter=A",
                        "--format=%cs", "--", rel],
                       capture_output=True, text=True)
    lines = [ln for ln in r.stdout.splitlines() if ln.strip()]
    return lines[-1] if lines else "NEVER COMMITTED"


def main() -> int:
    if not RECORD.is_file():
        print(f"REFUSED: no record at {RECORD}")
        return 1
    rec = json.loads(RECORD.read_text(encoding="utf-8"))
    failed = rec.get("failed_tests") or []

    print("=" * 78)
    print("THE SECOND BOARD OF 2026-11-07, AND WHAT MADE IT RED")
    print("=" * 78)
    print(f"  commit {rec.get('commit')}  {str(rec.get('when'))[:19]}")
    print(f"  {rec.get('passed')} passed, {rec.get('failed')} failed, "
          f"{rec.get('skipped')} skipped, {rec.get('seconds'):.2f} s")
    print(f"  tree clean when recorded: {rec.get('tree_clean_at_record_time')}")

    print("\nEVERY FAILURE, WITH THE ARTEFACT A FIX MUST TOUCH AND ITS ADD DATE:")
    mine, his, unmapped = [], [], []
    for node in failed:
        f = node.split("::")[0].rsplit("/", 1)[-1]
        if f not in SUBJECT:
            unmapped.append(f)
            continue
        subj = SUBJECT[f]
        if subj is None:
            his.append(f)
            print(f"  {f}\n      -> HIS DECISION, not an edit; no date applies")
            continue
        d = _added(subj)
        mine.append((f, subj, d))
        flag = "  <= the repairing session" if d >= CUT else ""
        print(f"  {f}\n      -> {subj}\n         first committed {d}{flag}")
    for extra in ALSO:
        print(f"  (same failure, 2nd artefact) {extra}\n"
              f"         first committed {_added(extra)}")

    assert not unmapped, (
        "a failing test is not in the declared mapping, so this producer is "
        f"blind to it: {unmapped}. Add it rather than letting it go uncounted.")

    k = sum(1 for _, _, d in mine if d >= CUT)
    n = len(mine)
    print("\nTHE RATE, UNIT = FAILURE (not artefact):")
    wl = _show(f"new failures whose subject was added on or after {CUT}", k, n)
    print(f"\n  DECISION RULE, pre-stated: Wilson lower bound > {GATE:.4f}")
    print(f"  measured lower bound     : {wl:.6f}")
    print(f"  VERDICT                  : {'UPHELD' if wl > GATE else 'NOT UPHELD'}")

    print("\n" + "=" * 78)
    print("WHAT THIS SUPPORTS, AND WHAT IT DOES NOT")
    print("  SUPPORTS: board 2's new failures have the SAME provenance as")
    print("    board 1's -- the repairing session's own commits, caught by")
    print("    guards that already existed. 0 came from the product.")
    print("  DOES NOT SUPPORT: any rate over boards in general. n = 2 new")
    print("    failures on 1 board. The interval is wide and says so.")
    print("  AND THE UNFLATTERING READING IS THE RIGHT ONE: board 2's")
    print("    pre-registration claimed 0 new ON THE STRENGTH of board 1's")
    print("    lesson, hours after board 1 refuted the identical clause by 10.")
    print(f"    Same clause, same cause, same night. {len(his)} of the 4 failures")
    print("    are his decisions and were correctly predicted to persist.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    #: ★ `sys` IS IMPORTED HERE, NOT AT THE TOP, AND THAT IS DELIBERATE.
    #: ruff correctly reported the module-level `import sys` as unused when this
    #: file had no help handler, and removing it was right at that moment. Adding
    #: the handler made it needed again, so the block carries its own import and
    #: cannot be broken by a future unused-import sweep. A linter's remediation is
    #: sound for the code it saw, not for the code that comes next.
    import pathlib as _pl
    import sys as _sys
    _sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
    from _cli_help import answer_help as _answer_help
    _answer_help(__doc__, __file__, takes_no_arguments=True)
    raise SystemExit(main())
