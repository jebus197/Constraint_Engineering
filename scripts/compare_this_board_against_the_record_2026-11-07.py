#!/usr/bin/env python3
"""Set a finished full-suite log against the RECORDED board, as a partition.

WHY THIS EXISTS. `scripts/suite_record.py` stores `failed_tests` for the last
recorded board but has no comparator: its functions are `parse`, `record`,
`cite` and `stale`. The 2026-11-04 figures of 36 fixed, 8 still red and 20 new
were produced by something that is not in `scripts/` under any name I can find,
so the comparison had to be redone by hand each time -- which is the shape
`measured-rate-travels-with-its-script` forbids.

IT REFUSES RATHER THAN GUESSES, on 3 conditions, each of which has produced a
false result in this project before:

  1. AN UNFINISHED LOG. A log with no final tally line is a run in progress, and
     partitioning it reports every not-yet-reached test as FIXED. The 2026-11-04
     comparison was caught producing a false "44 of 44 fixed" exactly this way.
  2. A NARROWER RUN. A log whose collected total is materially below the
     recorded board's is a subset -- the commit gate's 128 files of 834, for
     instance -- and comparing a subset against the whole reports the
     unreached as fixed. This is the defect that let a gate board be reported
     to him as a full board for 36 days.
  3. NO RECORDED BASELINE. With nothing to compare against there is no
     partition, and saying so is the only honest output.

PARAMETRISED IDENTIFIERS ARE REPORTED BOTH WAYS, because they answer different
questions: raw node ids, and ids with their `[...]` parameter stripped. 12 raw
failures in 1 parametrised test are 1 defect by the second count and 12 by the
first, and which is wanted depends on whether the question is about defects or
about red marks.

Exit 0 iff a partition was produced.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

import mpmath as mp
from scipy.stats import beta as _beta
from statsmodels.stats.proportion import proportion_confint

mp.mp.dps = 40
REPO = pathlib.Path(__file__).resolve().parent.parent
RECORD = REPO / "resources" / "suite_record.json"
TALLY = re.compile(r"(?m)^=*\s*(?:\d+ \w+,?\s*)*\d+ (?:passed|failed|error)[^\n]*in "
                   r"[\d.]+s")
FAILED = re.compile(r"(?m)^FAILED (\S+)")
COUNTS = re.compile(r"(\d+) (passed|failed|skipped|error|xfailed|xpassed)")


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
    print(f"      Wilson 95% [{wl:.6f}, {wh:.6f}]  "
          f"Clopper-Pearson 95% [{cl:.6f}, {ch:.6f}]")
    print(f"      2-route disagreement {dis:.3e}")
    assert dis < 1e-6, f"the 2 interval routes disagree by {dis}"


def _bare(node: str) -> str:
    return re.sub(r"\[.*\]$", "", node)


def _head() -> str:
    import subprocess
    try:
        return subprocess.run(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return ""


def _load_baseline(spec):
    """(record, source_description) or (None, refusal_text).

    ★ THE 4TH REFUSAL, AND IT IS THE ONE THAT ACTUALLY FIRED. The suite wrapper
    records the board it has just finished, OVERWRITING the live record -- which
    is correct for `cite()` but destroys the only baseline this comparator had.
    Run against the live record after a board, it partitions the board against
    ITSELF and prints `0 fixed, N still red, 0 NEW`, with 2 agreeing interval
    routes, every earlier refusal passed, and nothing whatever measured.

    IT IS WORSE THAN VACUOUS. `0 new` is the exact clause the 2026-11-07
    pre-registration claimed, so a comparator in this state CONFIRMS whatever
    prediction it is pointed at. A measurement that cannot disagree with you is
    not a measurement. Verified by execution 2026-11-07 19:06 GMT: it reported
    `11 of 11 STILL RED, 0 NEW` against a board whose true partition is 1 of 17
    still red and 10 new.
    """
    import subprocess
    if spec:
        p = pathlib.Path(spec)
        if p.is_file():
            return json.loads(p.read_text(encoding="utf-8")), f"file {p}"
        if ":" in spec:                          # a git ref like HEAD:path/to.json
            r = subprocess.run(["git", "-C", str(REPO), "show", spec],
                               capture_output=True, text=True)
            if r.returncode != 0:
                return None, (f"REFUSED: --baseline {spec!r} is neither a readable "
                              f"file nor a resolvable git ref. git said: "
                              f"{r.stderr.strip()[:200]}")
            return json.loads(r.stdout), f"git ref {spec}"
        return None, f"REFUSED: --baseline {spec!r} is not a readable file."

    if not RECORD.is_file():
        return None, (f"REFUSED: no recorded baseline at "
                      f"{RECORD.relative_to(REPO)}, so there is nothing to "
                      f"partition against.")
    rec = json.loads(RECORD.read_text(encoding="utf-8"))
    head = _head()
    if head and rec.get("commit") == head:
        return None, (
            f"REFUSED: the live record was measured AT the current HEAD "
            f"({head}), so it is this very board and not a baseline for it. "
            f"Partitioning a board against itself reports 0 fixed and 0 NEW no "
            f"matter what changed -- and '0 new' is the clause a prediction "
            f"most wants confirmed, so this failure mode AGREES with you. The "
            f"suite wrapper overwrites the record when the run ends, so after "
            f"any board you must name the prior one explicitly, e.g. "
            f"--baseline HEAD:resources/suite_record.json.")
    return rec, f"live record {RECORD.relative_to(REPO)}"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--log", required=True, help="a FINISHED pytest output file")
    ap.add_argument("--baseline", default=None,
                    help="the PRIOR record to partition against: a JSON path, or a "
                         "git ref like HEAD:resources/suite_record.json. Needed "
                         "whenever the run being compared has already overwritten "
                         "the live record, which the suite wrapper always does.")
    a = ap.parse_args(argv)

    log = pathlib.Path(a.log)
    if not log.is_file():
        print(f"REFUSED: no log at {log}")
        return 1
    text = log.read_text(encoding="utf-8", errors="replace")

    if not TALLY.search(text):
        print("REFUSED: that log has no final tally line, so the run is still "
              "going. Partitioning an unfinished log reports every test it has "
              "not reached as FIXED, which is how a false '44 of 44 fixed' was "
              "produced on 2026-11-04.")
        return 1
    rec, src = _load_baseline(a.baseline)
    if rec is None:
        print(src)
        return 1
    base = set(rec.get("failed_tests") or [])
    base_total = int(rec.get("passed") or 0) + int(rec.get("failed") or 0)
    #: ★ PARSE THE TALLY LINE ITSELF, AND FAIL CLOSED WHEN IT CANNOT BE READ.
    #: The first version sliced the last few lines with a nonsense conditional,
    #: read 0 counts, and then short-circuited on `now_total` being 0 -- so the
    #: narrower-run refusal NEVER FIRED and the comparator produced "17 of 17
    #: fixed" from the commit gate's 2,574-test board, which is the precise
    #: false figure this file's own docstring says it exists to prevent. A
    #: guard whose precondition is falsy-tested fails OPEN; that is the shape
    #: this session met in `if res:` on a 3-tuple earlier the same day.
    tally = TALLY.search(text)
    counts = {w: int(n) for n, w in COUNTS.findall(tally.group(0))} if tally else {}
    now_total = counts.get("passed", 0) + counts.get("failed", 0)
    if now_total == 0:
        print("REFUSED: the tally line parsed to 0 collected tests, so the run "
              "size is unknown. A comparator that cannot measure the run's size "
              "cannot tell a subset from the whole, and treating an unknown as "
              "'wide enough' is failing OPEN.")
        return 1
    if base_total and now_total < 0.9 * base_total:
        print(f"REFUSED: this run collected about {now_total} tests against the "
              f"recorded board's {base_total}. A subset compared against the "
              f"whole reports every unreached test as fixed -- the defect that "
              f"let a gate board of 128 files of 834 be reported as a full "
              f"board for 36 days.")
        return 1

    now = set(FAILED.findall(text))
    fixed, still, new = sorted(base - now), sorted(base & now), sorted(now - base)

    print("=" * 78)
    print("THIS BOARD AGAINST THE RECORDED ONE")
    print("=" * 78)
    print(f"baseline : {rec.get('commit')} on {str(rec.get('when'))[:19]}  "
          f"{rec.get('passed')} passed, {rec.get('failed')} failed   [{src}]")
    print(f"this run : {log.name}  {counts.get('passed', '?')} passed, "
          f"{counts.get('failed', 0)} failed, {counts.get('skipped', 0)} skipped")
    print()
    print("RAW NODE IDS -- red MARKS, which is what a board prints:")
    _show("of the recorded failures, now FIXED", len(fixed), len(base))
    _show("of the recorded failures, STILL RED", len(still), len(base))
    print(f"  NEW failures not in the record: {len(new)}")
    for n in new:
        print(f"      {n}")
    print("\n  still red:")
    for n in still:
        print(f"      {n}")

    print("\nPARAMETERS STRIPPED -- DEFECTS, which is a different question:")
    b2, n2 = {_bare(x) for x in base}, {_bare(x) for x in now}
    _show("fixed", len(b2 - n2), len(b2))
    _show("still red", len(b2 & n2), len(b2))
    print(f"  new: {len(n2 - b2)}")

    print("\n" + "=" * 78)
    print("BOTH COUNTS ARE REPORTED BECAUSE THEY ANSWER DIFFERENT QUESTIONS:")
    print("12 red marks in 1 parametrised test are 1 defect stripped and 12 raw.")
    return 0


if __name__ == "__main__":
    #: NO `answer_help` CALL HERE, DELIBERATELY. This script builds an argparse
    #: parser, and `answer_help` answers `--help` FIRST, which would hide
    #: --log and --baseline from the reader. That is the both-forms fault pinned
    #: by bench/tests/test_fresh_clone_is_actually_run_2026-09-11.py, whose own
    #: docstring records walking into it. argparse answers the flag itself.
    raise SystemExit(main(sys.argv[1:]))
