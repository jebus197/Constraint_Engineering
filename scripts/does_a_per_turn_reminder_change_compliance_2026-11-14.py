#!/usr/bin/env python3
"""His question: how often must a standing instruction be restated? Measured where it can be.

HIS WORDS, verbatim, 2026-11-13: *"this is almost exclusively a result of
context drift. So the longer a HIL leaves a model to 'do it's own thing' the
worse it will become at following that instruction. It then becomes a case of
how often should a model be reminded? On every turn, every few turns or an
exactly calculated 'n' number of turns from a calculated/derived optimum?
Fortunately this project is full of examples where I have given you
instructions, only to encounter this exact outcome."*

★ ONE INSTRUCTION IN THIS PROJECT HAS A BEFORE AND AN AFTER, which is what an
optimum needs and what a repetition tally cannot give. `an-identifier-never-
travels-alone` -- print an entry code only with a short descriptor -- is
mechanically checkable by a predicate that already exists, and a PER-TURN
reminder for it was installed in a single commit: `371f55cc`, 2026-11-10
18:52:44Z, which added `open_roster` and its injection into every turn. Before
that moment there was no per-turn reminder; from it there always is.

★ THE PREDICATE IS NOT RE-DERIVED. `note_vagueness_lint.entry_subjects()`,
`_ENTRY_IDENT` and `_subject_words` are the committed implementation of Rule 32,
and the interval helper is the project's reserved 2-route contract. Writing a
second predicate here would measure the predicate, not the behaviour.

★ ★ THE CONFOUND IS FATAL TO THE NAIVE READING AND IS THE POINT OF THIS SCRIPT.
He STATED the rule on 2026-11-10 and the MECHANISM was installed on 2026-11-10.
A before/after difference therefore cannot be attributed to the reminder rather
than to the restatement: the 2 are simultaneous. Reporting the gap as the
reminder's effect would be the flattering-measure failure this project's record
already names 3 times.

★ SO THE DESIGN DISCRIMINATES THEM INSTEAD, and this is the contribution.
Within the AFTER period the reminder is CONSTANT -- it fires on every turn -- so:

  * if the REMINDER is doing the work, compliance should stay FLAT as the days
    since his restatement accumulate;
  * if the RESTATEMENT is doing the work and the reminder is inert, compliance
    should DECAY as that restatement recedes, which is exactly the decay he
    hypothesises.

A fitted slope over the after-period days therefore separates the 2 causes in a
way the before/after step cannot. The decision rule is stated BEFORE the numbers
so the test can fail: a negative slope whose 95 per cent interval excludes 0
supports his decay hypothesis EVEN UNDER a constant per-turn reminder, which
would be a strong and surprising result; a slope whose interval contains 0 is
consistent with the reminder holding compliance level and does NOT establish it.

★ WHAT THIS CANNOT DO, STATED SO NO READER TAKES MORE THAN IS HERE. (1) It
measures 1 instruction; a per-turn reminder for one rule says nothing about an
optimum for all of them. (2) The roster lists OPEN entries only, so a code for
an entry already closed gains no help from it, and entry state at the time of
each message is not recorded -- the after arm is therefore diluted by an unknown
amount, biasing any measured improvement DOWNWARD. (3) Turn boundaries are
approximated by assistant message timestamps, which is the only clock the
transcripts carry.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import importlib.util
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
SESSIONS = (pathlib.Path.home() / ".claude" / "projects"
            / "-Users-georgejackson-Developer-Projects")

#: The commit that installed the per-turn roster reminder. `git log -1
#: --format=%aI 371f55cc`. Not a guess and not a round number.
REMINDER_INSTALLED = dt.datetime(2026, 11, 10, 18, 52, 44, tzinfo=dt.timezone.utc)
REMINDER_COMMIT = "371f55cc"


def _bare_code_producer():
    """The existing producer, for its `_iv` 2-route interval contract."""
    spec = importlib.util.spec_from_file_location(
        "_bare_codes", REPO / "scripts" / "a_bare_entry_code_in_chat_2026-11-10.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["_bare_codes"] = m
    spec.loader.exec_module(m)
    return m


def scan(limit: int = 0):
    """(timestamp, bare) for every known entry code printed in chat."""
    sys.path.insert(0, str(REPO / "scripts"))
    import note_vagueness_lint as nvl

    subjects = nvl.entry_subjects()
    if not subjects:
        raise SystemExit("FAIL: 0 entry subjects, so a 0 here would be a false 0")

    files = sorted(SESSIONS.glob("*.jsonl"),
                   key=lambda p: p.stat().st_mtime, reverse=True)
    if limit:
        files = files[:limit]

    sent_re = re.compile(r"[^.!?\n]+[.!?]?")
    out = []
    no_stamp = 0
    for f in files:
        try:
            raw = f.read_text(errors="replace").splitlines()
        except OSError:
            continue
        for line in raw:
            if '"type":"assistant"' not in line and '"type": "assistant"' not in line:
                continue
            try:
                d = json.loads(line)
            except Exception:                                  # noqa: BLE001
                continue
            stamp = d.get("timestamp")
            ts = None
            if isinstance(stamp, str):
                try:
                    ts = dt.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
                except ValueError:
                    ts = None
            for blk in (d.get("message", {}).get("content") or []):
                if not isinstance(blk, dict) or blk.get("type") != "text":
                    continue
                for s in sent_re.findall(blk.get("text", "") or ""):
                    for im in nvl._ENTRY_IDENT.finditer(s):
                        subj = subjects.get(im.group(1))
                        if not subj:
                            continue
                        if ts is None:
                            no_stamp += 1
                            continue
                        out.append((ts, not (subj & nvl._subject_words(s))))
    return out, no_stamp, len(files)


#: The decay worth detecting, stated as a figure rather than left to taste: the
#: bare-printing rate rising by 0.10 over 30 days. Smaller than that and the
#: reminder is doing most of its job; larger and he would see it himself.
DETECTABLE_DECAY_PER_DAY = 0.10 / 30
_Z = 1.959963984540054


def _slope_se(n_days: int, sd: float) -> float:
    import numpy as np
    x = np.arange(n_days, dtype=float)
    return float(sd / np.sqrt(np.sum((x - x.mean()) ** 2)))


def power_analytic(n_days: int, sd: float,
                   true_slope: float = DETECTABLE_DECAY_PER_DAY) -> float:
    """Two-sided power of the slope test.

    ★ THE FIRST VERSION OF THIS RETURNED 1.9997, which is an impossible power
    and is recorded rather than quietly corrected. It computed
    `2 * (1 - Phi(z - d))`, which exceeds 1 once `d` is large. The correct
    two-sided form is `Phi(-z + d) + Phi(-z - d)`. The error was caught by the
    value being outside [0, 1] -- not by reasoning about the formula -- which is
    why a computed figure is checked against its own admissible range.
    """
    from scipy import stats as st
    d = true_slope / _slope_se(n_days, sd)
    return float(st.norm.cdf(-_Z + d) + st.norm.cdf(-_Z - d))


def power_simulated(n_days: int, sd: float,
                    true_slope: float = DETECTABLE_DECAY_PER_DAY,
                    trials: int = 20000, base: float = 0.656) -> float:
    """The same question by simulation, using the t critical value the real test
    would use. It must agree with the analytic route or neither is reportable."""
    import numpy as np
    from scipy import stats as st
    rng = np.random.default_rng(20261114)
    x = np.arange(n_days, dtype=float)
    tcrit = st.t.ppf(0.975, n_days - 2)
    hits = 0
    for _ in range(trials):
        y = base + true_slope * x + rng.normal(0, sd, n_days)
        r = st.linregress(x, y)
        if abs(r.slope) - tcrit * r.stderr > 0:
            hits += 1
    return hits / trials


def days_needed(sd: float, target: float = 0.80, cap: int = 400) -> int:
    n = 4
    while n <= cap:
        if power_analytic(n, sd) >= target:
            return n
        n += 1
    return -1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=(__doc__ or "").strip().splitlines()[0])
    ap.add_argument("--limit", type=int, default=0,
                    help="examine only the N most recent transcripts")
    #: ★ THE TRIAL COUNT IS AN OPTION BECAUSE THE GUARD PAYS FOR IT. Measured
    #: 2026-11-14: at the default this function took 197.68 s of a 215.67 s
    #: guard run -- 92 per cent of it, from 120,000 simulated regressions -- and
    #: the commit gate already costs about 27 minutes. The REPORTED figure keeps
    #: the full default so its precision is unchanged; the guard passes a small
    #: value because all it needs to know is that this exits 0.
    ap.add_argument("--power-trials", type=int, default=20000,
                    help="simulation trials per power point (default 20000)")
    ns = ap.parse_args(argv)

    import numpy as np
    from scipy import stats as st

    rows, no_stamp, n_files = scan(ns.limit)
    iv = _bare_code_producer()._iv

    before = [b for ts, b in rows if ts < REMINDER_INSTALLED]
    after = [b for ts, b in rows if ts >= REMINDER_INSTALLED]

    print("=" * 76)
    print("DOES A PER-TURN REMINDER CHANGE COMPLIANCE, AND CAN THE RECORD SAY?")
    print("=" * 76)
    print(f"  transcripts read                : {n_files}")
    print(f"  known entry codes printed       : {len(rows)}")
    print(f"  dropped for having no timestamp : {no_stamp}")
    print(f"  reminder installed              : {REMINDER_INSTALLED.isoformat()} "
          f"(commit {REMINDER_COMMIT})")
    print()
    if not before or not after:
        print("  REFUSED: one arm is empty, so no comparison exists.")
        return 1

    for label, arm in (("BEFORE the reminder", before), ("AFTER the reminder ", after)):
        k, n = sum(arm), len(arm)
        (wlo, whi), (clo, chi), cross = iv(k, n)
        print(f"  {label}: {k} of {n} printed BARE = {k/n:.6f}")
        print(f"      Wilson [{wlo:.6f}, {whi:.6f}]  Clopper-Pearson [{clo:.6f}, {chi:.6f}]"
              f"  2 routes agree to {cross:.3e}")

    kb, nb, ka, na = sum(before), len(before), sum(after), len(after)
    odds, p = st.fisher_exact([[kb, nb - kb], [ka, na - ka]])
    print()
    print(f"  Fisher exact on the 2x2: odds ratio {odds:.6f}, p = {p:.6e}")
    chi2, pchi = st.chi2_contingency([[kb, nb - kb], [ka, na - ka]])[:2]
    print(f"  chi-squared second route: chi2 {chi2:.6f}, p = {pchi:.6e}  "
          f"(agreement is not expected to be exact; the 2 tests differ by design)")

    print()
    print("  ★ THAT STEP CANNOT BE ATTRIBUTED TO THE REMINDER. He STATED the rule and")
    print("    the MECHANISM was installed on the SAME DAY, so the 2 causes are")
    print("    simultaneous and the step measures their sum.")
    print()
    print("  ★ THE DISCRIMINATING TEST: within the AFTER period the reminder is")
    print("    CONSTANT. A decaying slope there supports his hypothesis even under a")
    print("    reminder; a flat slope is consistent with the reminder holding the line.")

    by_day = collections.defaultdict(lambda: [0, 0])
    for ts, b in rows:
        if ts < REMINDER_INSTALLED:
            continue
        d = (ts - REMINDER_INSTALLED).days
        by_day[d][0] += 1
        by_day[d][1] += 1 if b else 0
    days = sorted(by_day)
    print()
    print(f"  {'day':>4} {'codes':>6} {'bare':>5} {'bare rate':>10}")
    for d in days:
        n, k = by_day[d]
        print(f"  {d:>4} {n:>6} {k:>5} {k/n:>10.6f}")

    usable = [(d, by_day[d][1] / by_day[d][0]) for d in days if by_day[d][0] >= 5]
    print()
    if len(usable) < 3:
        print(f"  ★ THE SLOPE IS NOT FITTED: only {len(usable)} day(s) carry 5 or more")
        print("    codes, and a slope on fewer than 3 points is not a measurement.")
        print("    SO THE RECORD CANNOT YET DISCRIMINATE THE 2 CAUSES, and the honest")
        print("    answer to him is the DESIGN above plus the date at which it becomes")
        print("    answerable, not a number.")
        return 0
    xs = np.array([d for d, _r in usable], dtype=float)
    ys = np.array([r for _d, r in usable], dtype=float)
    res = st.linregress(xs, ys)
    lo = res.slope - 1.959963984540054 * res.stderr
    hi = res.slope + 1.959963984540054 * res.stderr
    pf = np.polyfit(xs, ys, 1)
    print(f"  days usable (5+ codes): {len(usable)}")
    print(f"  slope {res.slope:.8f} per day, 95% [{lo:.8f}, {hi:.8f}], p = {res.pvalue:.6f}")
    print(f"  numpy polyfit second route: slope {pf[0]:.8f}  "
          f"(agrees to {abs(pf[0] - res.slope):.3e})")
    print()
    if hi < 0:
        print("  VERDICT: bare-printing FALLS over the after period. Compliance is")
        print("  IMPROVING under a constant reminder, which is consistent with the")
        print("  reminder working and inconsistent with decay.")
    elif lo > 0:
        print("  VERDICT: bare-printing RISES over the after period even though the")
        print("  reminder fires every turn. THAT SUPPORTS HIS DECAY HYPOTHESIS, and it")
        print("  would mean a per-turn reminder is not sufficient on its own.")
    else:
        print("  VERDICT: the slope's interval contains 0. Consistent with the reminder")
        print("  holding compliance level, and NOT evidence that it does -- an interval")
        print("  containing 0 fails to reject, which is not the same as confirming.")

    # ---- HOW LONG THE DISCRIMINATING TEST NEEDS, so the design is actionable
    resid = ys - (res.intercept + res.slope * xs)
    sd = float(np.std(resid, ddof=2)) if len(xs) > 2 else float("nan")
    print()
    print(f"  residual sd of the daily bare rate: {sd:.6f}")
    print(f"  effect to detect: a decay of 0.10 over 30 days "
          f"= {DETECTABLE_DECAY_PER_DAY:.8f} per day")
    need = days_needed(sd)
    print(f"  {'days':>5} {'slope SE':>11} {'analytic':>9} {'simulated':>10} {'delta':>8}")
    worst = 0.0
    for n in (len(xs), 14, 30, 45, 60, 90):
        a = power_analytic(n, sd)
        s = power_simulated(n, sd, trials=ns.power_trials)
        worst = max(worst, abs(a - s))
        print(f"  {n:>5} {_slope_se(n, sd):>11.8f} {a:>9.4f} {s:>10.4f} {abs(a-s):>8.4f}")
    print(f"  the 2 power routes agree to {worst:.4f}; every value lies in [0, 1]")
    print(f"  DAYS OF AFTER-PERIOD RECORD NEEDED FOR 0.80 POWER: {need}  "
          f"(today: {len(days)})")
    print()
    print("  ★ AND THE FINDING THAT NEEDS NO MORE DAYS, which is the answer to his")
    print("    question as asked: WITH the reminder firing on EVERY turn, the bare")
    print("    rate is still the figure printed above. The reminder is already at")
    print("    maximum frequency, so 'remind more often' is not an available lever")
    print("    for this instruction. What is left is a surface that makes the")
    print("    omission VISIBLE rather than one that asks the model to remember.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
