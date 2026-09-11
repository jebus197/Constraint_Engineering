#!/usr/bin/env python3
"""How often does I38's artefact-classifier test fail in a full-size suite run?

THE ANSWER IS "ALWAYS, IN SOME HARNESSES, NEVER IN OTHERS", AND THIS SCRIPT WAS
ASKING THE WRONG QUESTION. I38 was RESOLVED on 2026-09-11 and it was never a
flake: the classifier could not recognise a checkout whose directory is named
`clone`, which is exactly what `fresh_clone_suite_2026-09-11.py` names it. Every
run through that harness failed and every run through another passed. The rate
below, with its confidence intervals, was therefore measuring which harness made
each clone -- a property of the census, not of the software.

IT IS KEPT, NOT DELETED, AND THE CENSUS IS STILL WORTH HAVING. The per-run rows
record which harness produced each full-size run and whether the test failed in
it, and that is the evidence that identified the harness as the variable. What
must not be quoted is the PROPORTION as a failure rate. A rate over a
deterministic phenomenon is a description of the sample.

The anchoring lesson below stands unchanged and is the reason this file exists.


WHY A SCRIPT AND A COMMITTED CENSUS, RATHER THAN A FIGURE IN THE ISSUES LOG.
`measured-rate-travels-with-its-script` requires the producer beside the number,
and the raw suite logs live in a session scratchpad on 1 machine -- the same
"evidence on one machine only" problem task A8 is about. So the census is
DISTILLED and COMMITTED, and this script recomputes the rate from the committed
file. Anyone can reproduce the figure; only the maintainer can rebuild the census
from raw logs, and `--from-logs` is how that is done.

THE FIGURE THIS REPLACES WAS WRONG, AND THE AUDIT HAD THE DEFECT IT WAS AUDITING.
The issues log said "1 failure in 4 full-size runs". The first re-count grepped
`^FAILED` over the archived logs and returned 0 failures -- the lines are
indented by 2 spaces, so the anchor could not match, and 2 real failures read as
none. A scanner that resolves one form of a thing and reports a false zero for
the other is this session's recurring defect, and here it was inside the
instrument built to count that defect. `_failed_the_test` is deliberately
unanchored and is tested against both the indented and the bare form.

WHAT A ROW IS. One full-size run: at least 6,500 tests collected, which excludes
the many partial and subset runs in the same directory. A run is recorded with
its environment, because both observed failures were in clones -- a description
of the 6 runs so far, not a demonstrated cause. With 1 working-tree run the
Fisher exact test returns p = 1.0000 and settles nothing.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
CENSUS = REPO / "experimental_notes" / "evidence" / "suite_runs_2026-09-11.json"

#: The test I38 is about.
TEST = ("bench/tests/test_falsifier_cannot_read_the_key.py::"
        "test_the_artefact_classifier_cannot_excuse_a_real_escape")

#: A full-size run. Subset runs in the same directory are not evidence about a
#: test that only ever failed in a whole-suite run.
FULL_SIZE = 6500

_TOTAL = re.compile(r"(?:(\d+) failed, )?(\d+) passed")


def _failed_the_test(blob: str) -> bool:
    """Did this log record TEST as failed?

    UNANCHORED ON PURPOSE. pytest writes `FAILED <id>` at the start of a line,
    but an archived log may have been piped through `sed 's/^/  /'` first, and
    the anchored form returned a false zero over exactly such files.
    """
    return re.search(r"FAILED\s+\S*" + re.escape(TEST.split("::")[0])
                     + r"::" + re.escape(TEST.split("::")[1]), blob) is not None


def _shown(path: pathlib.Path) -> str:
    """Repo-relative where possible, absolute otherwise.

    `Path.relative_to` RAISES for a path outside the repository, so the refusal
    message crashed instead of refusing -- found by the test that calls the
    refusal branch. A failure path that fails is worse than no failure path,
    because it turns a clear "no census" into a traceback.
    """
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


def census_from_logs(log_dir: pathlib.Path) -> list[dict]:
    """Distil every full-size run in `log_dir` into one row each."""
    rows = []
    for f in sorted(log_dir.glob("*.log")):
        try:
            blob = f.read_text(errors="replace")
        except OSError:
            continue
        hits = list(_TOTAL.finditer(blob))
        if not hits:
            continue
        last = hits[-1]
        failed, passed = int(last.group(1) or 0), int(last.group(2))
        if passed + failed < FULL_SIZE:
            continue
        rows.append({"log": f.name, "passed": passed, "failed": failed,
                     "environment": "clone" if "clone" in f.name or "flake" in f.name
                                    else "working tree",
                     "i38_failed": _failed_the_test(blob)})
    return rows


def rate(rows: list[dict]) -> dict:
    """The figure, with both intervals, each cross-checked by a second tool."""
    from statsmodels.stats.proportion import proportion_confint
    from scipy.stats import beta, fisher_exact
    import mpmath as mp

    n = len(rows)
    k = sum(1 for r in rows if r["i38_failed"])
    if n == 0:
        raise SystemExit("census is empty; nothing to measure")
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    cl = float(beta.ppf(0.025, k, n - k + 1)) if k else 0.0
    ch = float(beta.isf(0.025, k + 1, n - k)) if k < n else 1.0

    mp.mp.dps = 50
    z = mp.mpf("1.959963984540054235524594430520551527955550995213")
    p, N = mp.mpf(k) / n, mp.mpf(n)
    c = p + z**2 / (2 * N)
    h = z * mp.sqrt(p * (1 - p) / N + z**2 / (4 * N**2))
    d = 1 + z**2 / N
    mp_lo, mp_hi = float((c - h) / d), float((c + h) / d)

    clones = [r for r in rows if r["environment"] == "clone"]
    trees = [r for r in rows if r["environment"] != "clone"]
    kc = sum(1 for r in clones if r["i38_failed"])
    kt = sum(1 for r in trees if r["i38_failed"])
    _, pv = fisher_exact([[kc, len(clones) - kc], [kt, len(trees) - kt]])
    return {"n": n, "k": k, "wilson": (lo, hi), "cp": (cl, ch),
            "wilson_mpmath": (mp_lo, mp_hi),
            "clone": (kc, len(clones)), "tree": (kt, len(trees)), "fisher_p": pv}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--from-logs", metavar="DIR",
                    help="rebuild the census from raw suite logs and write it")
    a = ap.parse_args()

    if a.from_logs:
        rows = census_from_logs(pathlib.Path(a.from_logs))
        CENSUS.parent.mkdir(parents=True, exist_ok=True)
        CENSUS.write_text(json.dumps(rows, indent=1) + "\n", encoding="utf-8")
        print(f"  wrote {len(rows)} full-size run(s) to {_shown(CENSUS)}")
    if not CENSUS.is_file():
        # REFUSE rather than report 0 of 0. A missing census is an unmeasured
        # state, and printing a rate over it would be a fabricated figure.
        print(f"  REFUSED: no census at {_shown(CENSUS)}; "
              f"rebuild it with --from-logs", file=sys.stderr)
        return 4

    rows = json.loads(CENSUS.read_text(encoding="utf-8"))
    r = rate(rows)
    print(f"full-size suite runs (>= {FULL_SIZE} tests): {r['n']}")
    for row in rows:
        print(f"    {row['log']:28} {row['passed']:>5} passed, {row['failed']:>2} failed"
              f"  [{row['environment']}]  I38 failed: {row['i38_failed']}")
    print(f"\n  I38 failures: {r['k']} of {r['n']} = {100 * r['k'] / r['n']:.4f}%")
    print(f"    Wilson          [{100 * r['wilson'][0]:.4f}%, {100 * r['wilson'][1]:.4f}%]")
    print(f"    Wilson (mpmath) [{100 * r['wilson_mpmath'][0]:.4f}%, "
          f"{100 * r['wilson_mpmath'][1]:.4f}%]")
    print(f"    Clopper-Pearson [{100 * r['cp'][0]:.4f}%, {100 * r['cp'][1]:.4f}%]")
    print(f"  clone {r['clone'][0]} of {r['clone'][1]}, "
          f"working tree {r['tree'][0]} of {r['tree'][1]}, "
          f"Fisher exact p = {r['fisher_p']:.4f}")
    if r["fisher_p"] > 0.05:
        print("    NOT significant. The clone/working-tree split describes the runs "
              "so far; it does not establish a cause.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
