#!/usr/bin/env python3
"""HIS UNTESTED HYPOTHESIS, MEASURED FOR THE FIRST TIME, AND HIS PARTITION IS INCOMPLETE.

`reasoning-depth-before-breadth` in the global instruction file carries 2 failure
analyses. One is measured. The other is marked [SPECULATIVE] in his own words --
that too much DEPTH becomes blinkered -- and the directive states a decision rule
so the test can fail:

    "he is right, and depth alone goes blind, if the second-context share of all
     defects so classified has a Wilson 95% lower bound above 0.5000"

and names what would test it: "2 defects first surfaced by a SECOND independent
context against defects first surfaced by further reasoning inside the first,
both drawn from the same bounded pass budget." It also names the candidate
evidence as the panel's 3 corrections on 2026-10-16, "not been analysed this way".

THIS SCRIPT MEASURES IT OVER 2026-11-04, which is the first bounded pass budget
in the record that produced BOTH a panel round and a long single-context repair
arc, so both arms are populated from the same budget as the rule requires.

**THE HEADLINE IS NOT THE SHARE. IT IS THAT THE PARTITION HAS 3 PARTS, NOT 2.**
The rule is binary -- second context against first context. The observed
surfacers are 3: a SECOND CONTEXT (a panel seat), the FIRST CONTEXT (further
reasoning in the same context), and an INSTRUMENT (a gate, a guard, a linter or
a mutation harness, which decides mechanically and belongs to neither). Forcing
a 3-way split into a binary produces a flattering measure in whichever direction
the third category is assigned, so BOTH assignments are reported and the rule's
verdict is given under each.

PROVENANCE, AND THE HONEST LIMIT. Every row carries how it was attributed:
  * COMMITTED -- the commit message or entry text names the surfacer in words
    that are quoted here, so the attribution is auditable without trusting me.
  * DECLARED  -- no artefact names a surfacer, so the attribution is MY
    judgement. That is the flattering-measure exposure and the share of
    DECLARED rows is reported as the limitation it is.
A second independent classifier is what would remove that exposure, and this
script does not pretend to be one.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

SECOND, FIRST, INSTRUMENT = "SECOND_CONTEXT", "FIRST_CONTEXT", "INSTRUMENT"

# (defect, surfacer, provenance, the quoted words or the reason)
DEFECTS = [
    ("the 44-failure distribution summed to 31 of 44", SECOND, "COMMITTED",
     "summed to 31 of 44"),
    ("'18 root causes' was 12 among the 44", SECOND, "COMMITTED",
     "both panel seats raised it independently as their strongest disagreement"),
    ("a joint brief reads live files while seats hold a snapshot", SECOND,
     "COMMITTED", "A JOINT ROUND ASKED 2 SEATS ABOUT A FILE THAT HAD CHANGED"),
    ("R_n is not a probability and 3 surfaces said it was", SECOND, "COMMITTED",
     "A panel seat found the weighted risk is not a probability"),
    ("the seat's own [0, pi_k] clause is wrong for this directive", FIRST,
     "COMMITTED", "its proposed wording also carried [0, pi_k], which is WRONG "
     "for this directive's own form"),
    ("the appendix attributes a per-class range to the weighted sum", FIRST,
     "COMMITTED", "following its citation found 2 more surfaces"),
    ("the April audit records R_n in [0,1] as PROVED", FIRST, "COMMITTED",
     "its quantifier list names pi and m and never names w_k"),
    ("the detector matched its own remedy, 3 times", FIRST, "COMMITTED",
     "THE DETECTOR MATCHED ITS OWN REMEDY 3 TIMES, ALL CAUGHT BY EXECUTION"),
    ("2 of 4 declared citations had drifted", FIRST, "COMMITTED",
     "2 HAD DRIFTED"),
    ("A3 named a function that exists nowhere", FIRST, "COMMITTED",
     "A SYMBOL THAT DOES NOT EXIST"),
    ("the invented symbol propagated into a closing report", FIRST, "COMMITTED",
     "the 2nd is the consequence"),
    ("my citation extractor was incomplete, 1 of 3 became 2 of 4", FIRST,
     "COMMITTED", "My first extraction reported 1 of 3 drifted. It was incomplete"),
    ("the existing citation test was too weak, 3 ways", FIRST, "COMMITTED",
     "IT VERIFIED 1, WEAKLY"),
    ("rglob resolved 1 of 75 matches by traversal order", FIRST, "COMMITTED",
     "correct today by traversal order and not by construction"),
    ("B20's build was already ruled 3 times", FIRST, "COMMITTED",
     "THE BUILD IS ALREADY RULED, 3 TIMES"),
    ("B20's component count was stale, 3 of 4 became 4 of 4", FIRST, "COMMITTED",
     "4 OF 4 BUILT, 0 PARTLY, 0 ABSENT"),
    ("enablement is 2 switches and neither is passed", FIRST, "COMMITTED",
     "ENABLEMENT IS GATED TWICE"),
    ("my '6 of 34 empty headings' inference was wrong", FIRST, "COMMITTED",
     "0 of the 6 were decisions he was owed and not being asked"),
    ("a compound command's exit code masked a refusal", FIRST, "COMMITTED",
     "the wrapping shell reported 0, because the shell's last stage was a git log"),
    ("the fan-out figures moved again and the trend claim was wrong", FIRST,
     "COMMITTED", "DIRECTION CLAIM THIS SENTENCE USED TO MAKE IS WITHDRAWN"),
    ("the memory index stood 2 characters over its refuse line", INSTRUMENT,
     "COMMITTED", "MEMORY INDEX 2 CHARACTERS OVER"),
    ("the joint panel round was unmirrored", INSTRUMENT, "COMMITTED",
     "THE JOINT PANEL ROUND WAS UNMIRRORED"),
    ("a --help answered by running the whole measurement", INSTRUMENT,
     "COMMITTED", "answered --help by running the whole measurement"),
    ("the archiver moves 0 entries at its 30-day default", FIRST, "DECLARED",
     "found by dry-running the archiver across windows after the gate refused; "
     "no artefact names the surfacer"),
    ("B20's authored detail was stale and had no spoken heading", FIRST,
     "DECLARED", "found while re-running the surface check; not attributed "
     "in any commit message"),
]


def _interval(k: int, n: int) -> dict:
    """Wilson on statsmodels and an mpmath closed form, plus Clopper-Pearson."""
    from statsmodels.stats.proportion import proportion_confint
    from scipy.stats import beta as sbeta
    import mpmath as mp
    mp.mp.dps = 40
    lo_raw, hi_sm = proportion_confint(k, n, method="wilson")
    z = mp.mpf("1.959963984540054235524594430520551527955")
    p = mp.mpf(k) / n
    d = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / d
    h = (z / d) * mp.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return {
        "k": k, "n": n, "p": k / n,
        "wilson": (max(0.0, lo_raw), hi_sm),
        "wilson_mp": (max(0.0, float(c - h)), float(c + h)),
        "agree": abs(float(c + h) - hi_sm),
        "cp": (float(sbeta.ppf(0.025, k, n - k + 1)) if k else 0.0,
               float(sbeta.ppf(0.975, k + 1, n - k)) if k < n else 1.0),
        "neg_artefact": -lo_raw if lo_raw < 0 else 0.0,
    }


def _show(label: str, iv: dict, rule_threshold: float = 0.5) -> bool:
    print(f"\n  {label}")
    print(f"    {iv['k']} of {iv['n']} = {iv['p']:.6f}")
    print(f"    Wilson 95%          [{iv['wilson'][0]:.6f}, {iv['wilson'][1]:.6f}]"
          f"   statsmodels")
    print(f"    Wilson 95%          [{iv['wilson_mp'][0]:.6f}, "
          f"{iv['wilson_mp'][1]:.6f}]   mpmath, upper bounds agree to "
          f"{iv['agree']:.1e}")
    print(f"    Clopper-Pearson 95% [{iv['cp'][0]:.6f}, {iv['cp'][1]:.6f}]")
    if iv["neg_artefact"]:
        print(f"    NOTE: statsmodels returned a lower bound of "
              f"-{iv['neg_artefact']:.2e}, a floating-point artefact, clamped "
              f"to 0; a probability cannot be negative.")
    met = iv["wilson"][0] > rule_threshold
    print(f"    HIS RULE: Wilson lower bound {iv['wilson'][0]:.6f} > "
          f"{rule_threshold} ? {met}")
    return met, iv


def _flat(s: str) -> str:
    """Lower-case with every run of whitespace collapsed to 1 space."""
    return re.sub(r"\s+", " ", s).strip().lower()


def _verify_quotes() -> dict:
    """Every COMMITTED row must have its words findable in the git log.

    Otherwise the word COMMITTED is doing no work. A row whose quote cannot be
    located is DOWNGRADED to DECLARED here rather than left looking auditable.
    """
    log = subprocess.run(["git", "log", "--since=2026-11-01", "--format=%B"],
                         capture_output=True, text=True, cwd=str(REPO)).stdout
    parts = [log]
    for rel in ("experimental_notes/CDSFL_MASTER_TASK_LIST.md",
                "experimental_notes/Decisions_Awaiting_You_2026-11-04.md",
                ".claude/CLAUDE.md"):
        f = REPO / rel
        if f.is_file():
            parts.append(f.read_text(encoding="utf-8"))
    # WHITESPACE IS COLLAPSED ON BOTH SIDES. A commit message is hard-wrapped,
    # so a quoted phrase that spans a line break is absent under a literal
    # search and present to a reader. The first version of this check reported
    # 15 of 23 COMMITTED rows as unfindable, and the wrapping was the cause of
    # several of them -- a verifier defeated by formatting, not by provenance.
    hay = _flat(" ".join(parts))
    found, lost = [], []
    for name, _, prov, quote in DEFECTS:
        if prov != "COMMITTED":
            continue
        needle = _flat(quote)[:70]
        (found if needle in hay else lost).append((name, quote))
    return {"found": found, "lost": lost}


def main() -> int:
    print("=" * 78)
    print("1. EVERY COMMITTED ATTRIBUTION, CHECKED AGAINST THE RECORD")
    print("=" * 78)
    v = _verify_quotes()
    tot_committed = len(v["found"]) + len(v["lost"])
    print(f"\n  rows claiming COMMITTED provenance: {tot_committed}")
    print(f"  whose quoted words are findable in the git log or the task list: "
          f"{len(v['found'])}")
    if v["lost"]:
        print(f"  NOT findable, so DOWNGRADED to DECLARED: {len(v['lost'])}")
        for name, q in v["lost"]:
            print(f"    - {name}\n        sought: {q[:70]!r}")

    lost_names = {n for n, _ in v["lost"]}
    rows = [(n, s, ("DECLARED" if n in lost_names else p), q)
            for n, s, p, q in DEFECTS]

    print()
    print("=" * 78)
    print("2. THE PARTITION, WHICH HAS 3 PARTS AND NOT 2")
    print("=" * 78)
    for bucket in (SECOND, FIRST, INSTRUMENT):
        sel = [r for r in rows if r[1] == bucket]
        print(f"\n  {bucket}: {len(sel)}")
        for n, _, p, _q in sel:
            print(f"    [{p[:9]:<9}] {n[:66]}")

    n_second = sum(1 for r in rows if r[1] == SECOND)
    n_first = sum(1 for r in rows if r[1] == FIRST)
    n_inst = sum(1 for r in rows if r[1] == INSTRUMENT)
    n_decl = sum(1 for r in rows if r[2] == "DECLARED")
    total = len(rows)

    print()
    print("=" * 78)
    print("3. HIS RULE, UNDER BOTH ASSIGNMENTS OF THE THIRD CATEGORY")
    print("=" * 78)
    a, a_iv = _show("A. instruments EXCLUDED -- only the binary he specified "
              f"({n_second} second of {n_second + n_first}):",
              _interval(n_second, n_second + n_first))
    b, b_iv = _show("B. instruments counted as FIRST CONTEXT, since an instrument I "
              f"wrote and ran is inside my own context ({n_second} of {total}):",
              _interval(n_second, total))

    # READING C IS THE ONE MOST FAVOURABLE TO HIS HYPOTHESIS, AND IT IS
    # REPORTED FOR THAT REASON. `factual-synthesis-over-agreement` cuts both
    # ways: a measurement must not understate his case either. 3 defects were
    # found by FOLLOWING a seat's citation into the appendix and the audit, and
    # would not have been looked for without the seat. Crediting the second
    # context with what it CAUSED, not only what it stated, is the strongest
    # honest version of his position.
    CAUSED_BY_SEAT = 3
    c, c_iv = _show("C. the second context credited with what it CAUSED as well as "
              f"what it stated ({n_second} + {CAUSED_BY_SEAT} of {total}), "
              "which is the reading most favourable to his hypothesis:",
              _interval(n_second + CAUSED_BY_SEAT, total))

    print()
    print("=" * 78)
    print("4. THE LIMITATION, STATED AS A FIGURE RATHER THAN A CAVEAT")
    print("=" * 78)
    iv = _interval(n_decl, total)
    print(f"\n  rows attributed by MY judgement rather than by a quotable artefact:")
    print(f"    {n_decl} of {total} = {n_decl/total:.6f}")
    print(f"    Wilson 95% [{iv['wilson'][0]:.6f}, {iv['wilson'][1]:.6f}]")
    print(f"  A second independent classifier is what would remove this, and")
    print(f"  this script is not one. The 2 arms it compares were classified by")
    print(f"  the same context that produced one of them.")

    print()
    print("=" * 78)
    print("VERDICT")
    print("=" * 78)
    print(f"""
  HIS HYPOTHESIS IS NOT SUPPORTED ON THIS BUDGET, UNDER EITHER ASSIGNMENT.
  The rule requires the second-context share's Wilson lower bound to exceed
  0.5000. Measured: {a} excluding instruments, {b} counting them as first
  context, {c} even crediting the second context with the 3 defects it CAUSED.
  The lower bounds are below 0.5000 in all 3 readings, so on 2026-11-04 depth
  did not go blind -- the first context surfaced most of its own defects.

  THE SCOPE IS 1 BUDGET AND THE INTERVALS ARE WIDE. n = {total}, and the upper
  bounds reach {a_iv['wilson'][1]:.6f}, {b_iv['wilson'][1]:.6f} and
  {c_iv['wilson'][1]:.6f} -- read from the intervals computed above rather than
  typed here, because a figure typed twice drifts. So this does NOT establish that
  the second-context share is SMALL; it establishes only that it is not above
  0.5000 at 95% confidence on this budget. `failure-scope-discipline` forbids
  generalising past the 1 day measured, and 1 day with 1 panel round is the
  thinnest evidence that can address the question at all.

  BUT THE RESULT THAT MATTERS IS THE PARTITION, NOT THE SHARE.
  {n_inst} of {total} defects were surfaced by an INSTRUMENT, which his binary
  rule has no slot for. Those are not a second opinion and not further
  reasoning; they are a mechanism firing. A rule that cannot name them will
  mis-assign them whichever way it is read.

  AND THE SECOND CONTEXT'S VALUE IS UNDERSTATED BY A COUNT.
  {n_second} of the {total} came from a panel seat, but 3 further defects were
  found by FOLLOWING a seat's citation and would not have been looked for
  otherwise. A count of what each arm surfaced does not capture what one arm
  caused the other to find, and his rule counts only the former.

  WHAT WOULD MAKE THIS DECISIVE. A `surfaced` field on the task-list marker,
  which is decision 23 and his to rule, so the classification stops being
  retrospective prose and starts being recorded when the defect is raised.
""")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
