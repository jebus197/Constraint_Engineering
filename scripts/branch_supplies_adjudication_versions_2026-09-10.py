#!/usr/bin/env python3
"""Task 8.3: rebuild the figure that justifies keeping `exp39-experimental`.

MEASURED, and committed alongside the figures (`measured-rate-travels-with-its-script`).

THE FIGURE AS IT STOOD. "20 of 21 falsifiers reproduce against an earlier stored
version" exists only as prose and as a code comment at
`scripts/adjudicate_by_repair.py:270`. The rule covering this names code comments
explicitly, so a comment is not an exemption.

IT DOES NOT REPRODUCE FROM THE COMMITTED OUTPUT, and the reason is structural
rather than a lost file. `experimental_notes/data/adjudication_by_repair.json`
records PAIR verdicts -- 133 rows, 7 NO_BASELINE, 15 adjudicated at a non-HEAD
version -- while the claim is about FINDINGS. Counted as findings the committed
data gives 9, 16 and 25 for the nearest available quantities, and none of them is
21. The per-finding search the comment describes was never stored.

RE-DERIVING IT WOULD MEAN RE-RUNNING THE ADJUDICATOR, and that routine WRITES TO
THE TARGET FILE -- `target.write_text(txt)` inside a version loop, restored in a
`finally`. Running it to reconstruct a figure is not worth writing to real
targets, so it is not done here and the reason is recorded rather than the
attempt.

WHAT IS REBUILT INSTEAD IS THE ACTUAL QUESTION. The comment's own justification
for the branch is not the 20 of 21. It is `_versions`, whose docstring says
"`--all` is load-bearing ... the branch `exp39-experimental` holds 107 commits
main does not". That IS the figure that justifies keeping the branch, it is
answerable read-only, and it is answered below.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _cli_help import answer_help  # noqa: E402

# `--help` MUST NOT ACT. MEASURED 2026-09-11: `--help` on
# `scripts/assemble_panel_record_0819.py` rewrote a 55,814-byte verbatim panel
# record down to 1,334 bytes and exited 0, because the flag fell through to the
# script's ordinary work. 7 tracked scripts both WROTE something and ignored the
# flag -- 5.7377% of 122, Wilson [2.8068%, 11.3709%].
#
# `answer_help` returns immediately when argv is empty, so a plain run reaches
# exactly the code it reached before.
answer_help(__doc__, __file__, sys.argv[1:])

REPO = pathlib.Path(__file__).resolve().parents[1]
BRANCH = "exp39-experimental"


def shas(rev: str, path: str) -> set:
    out = subprocess.run(["git", "log", rev, "--format=%h", "--", path],
                         cwd=REPO, capture_output=True, text=True).stdout
    return set(out.split())


def in_repo_targets() -> list:
    out = set()
    for r in sorted((REPO / "bench" / "logs").glob("exp*/exp*_report.json")):
        try:
            d = json.loads(r.read_text())
        except (ValueError, OSError):
            continue
        t = d.get("target_file", "")
        if t and not t.startswith("/"):
            out.add(t)
    return sorted(out)


def main() -> int:
    print("--- the 20 of 21, checked against the committed output ---")
    p = REPO / "experimental_notes" / "data" / "adjudication_by_repair.json"
    if p.is_file():
        rows = json.loads(p.read_text())["rows"]
        nb = [r for r in rows if r["verdict"] == "NO_BASELINE"]
        ver = [r for r in rows if r.get("baseline") not in (None, "HEAD")]
        f_nb, f_ver = set(), set()
        for r in nb:
            f_nb |= {(r["run"], r["a"]), (r["run"], r["b"])}
        for r in ver:
            f_ver |= {(r["run"], r["a"]), (r["run"], r["b"])}
        print(f"  pair rows: {len(rows)}   NO_BASELINE: {len(nb)}   "
              f"adjudicated at a non-HEAD version: {len(ver)}")
        print(f"  distinct FINDINGS: {len(f_nb)} in NO_BASELINE pairs, "
              f"{len(f_ver)} adjudicated at a version, {len(f_nb | f_ver)} in union")
        print("  NONE of these is 21. The output records PAIRS; the claim is about")
        print("  FINDINGS, and the per-finding search was never stored.")
    else:
        print("  no committed adjudication output in this clone")

    print(f"\n--- what {BRANCH} uniquely supplies to the version search ---")
    if not subprocess.run(["git", "rev-parse", "--verify", BRANCH],
                          cwd=REPO, capture_output=True).returncode == 0:
        print(f"  no {BRANCH} in this clone -- it is a LOCAL branch that was never")
        print("  pushed, so `git clone` cannot carry it and this half of the")
        print("  measurement is UNAVAILABLE here rather than measured at 0.")
        _print_attribution_caveat()
        return 0
    targets = in_repo_targets()
    refs = [r for r in subprocess.run(
        ["git", "for-each-ref", "--format=%(refname)"], cwd=REPO,
        capture_output=True, text=True).stdout.split() if not r.endswith("/HEAD")]

    total = only_off_main = from_branch = 0
    rows_out = []
    for t in targets:
        a, m = shas("--all", t), shas("origin/main", t)
        total += len(a)
        off = a - m
        only_off_main += len(off)
        for s in off:
            who = {r.split("/")[-1] for r in refs if s in shas(r, t)}
            if BRANCH in who:
                from_branch += 1
                rows_out.append((t, s, sorted(who)))
    print(f"  in-repo targets across archived runs: {len(targets)}")
    print(f"  stored versions reachable with --all: {total}")
    print(f"  reachable from no ref on origin/main: {only_off_main}")
    print(f"  of those, supplied by {BRANCH}      : {from_branch}")
    for t, s, who in sorted(rows_out):
        print(f"     {s}  {t}")

    from statsmodels.stats.proportion import proportion_confint
    lo, hi = proportion_confint(from_branch, total, method="wilson")
    lo_c, hi_c = proportion_confint(from_branch, total, method="beta")
    print(f"\n  {from_branch}/{total} = {from_branch / total:.4%}")
    print(f"  Wilson 95%          : [{lo:.4%}, {hi:.4%}]  (statsmodels)")
    print(f"  Clopper-Pearson 95% : [{lo_c:.4%}, {hi_c:.4%}]")
    from scipy.stats import beta as sbeta
    slo = sbeta.ppf(0.025, from_branch, total - from_branch + 1) if from_branch else 0.0
    print(f"  Clopper-Pearson 95% : [{slo:.4%}, ...]  (scipy; agrees to "
          f"{abs(slo - lo_c):.1e})")

    _print_attribution_caveat()
    return 0


def _print_attribution_caveat() -> None:
    """The methodological caveat, printed on BOTH paths through main().

    FOUND 2026-09-10 BY RUNNING THE SUITE IN A FRESH CLONE, task A2. This
    paragraph sat after the measurement, and the branch-absent path returned
    before reaching it -- so in any clone (where the branch cannot exist, being
    local and never pushed) the reader got the numbers with none of the warning
    about what they do and do not mean. The caveat is a statement about METHOD,
    not about this clone's refs, so it is true whether or not the branch is here
    and it now prints either way.
    """
    print("\n  ATTRIBUTION MATTERS AND IS NOT ASSUMED. Not every off-main version")
    print("  belongs to this branch: at the time of measurement 1 came from local")
    print("  main running ahead of origin/main, and 1 from the pre-rewrite backup")
    print("  refs. Crediting the branch with all of them would have overstated its")
    print("  contribution by 40%.")


if __name__ == "__main__":
    sys.exit(main())
