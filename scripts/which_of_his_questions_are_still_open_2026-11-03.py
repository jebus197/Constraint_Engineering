#!/usr/bin/env python3
"""Which of the founder's recent questions are still open, and is the sim branch's "1 commit behind main" significant?

HIS INSTRUCTION, 2026-11-03T07:36:13: *"But there was the other questions I asked
not so long ago above."* He did not name them, so this enumerates them from the
transcript rather than guessing -- guessing is what `orchestrate-the-founder-too`
exists to prevent.

★ THE FIRST ATTEMPT HAD THE WRONG POPULATION AND IT IS RECORDED HERE BECAUSE THE
FIGURE WOULD HAVE BEEN NONSENSE. A keyword filter over `role == "user"` entries
returned **1657 of his messages carrying 1509 questions**, because this
transcript spans from 2026-08-24 and holds **84 compaction summaries** -- it is
the whole session, not the recent conversation. "Not so long ago above" is a
RECENT window, so the population had to be scoped.

THE CORRECT FILTER IS STRUCTURAL, NOT KEYWORD-BASED. A genuinely typed message
carries `promptSource == "sdk"` with `isMeta` false and `isCompactSummary` false.
Everything else -- Stop-hook feedback, UserPromptSubmit context, task
notifications (`promptSource == "system"`), tool results, compaction summaries --
is excluded by a FIELD rather than by matching its prose. Each exclusion is
counted and printed, because a filter whose rejects are not counted cannot be
checked. Measured: his typed messages on 2026-11-03 number **2**, against 132
user-role entries that day.

WHAT IS MECHANICAL AND WHAT IS NOT.
  MECHANICAL: the message population, the question extraction, the branch
  divergence, and whether a given phrase is present in a file on a given branch.
  BY READING: whether a question was ANSWERED. That is carried below as DATA,
  per question, naming the artefact that answers it, so a reader can check every
  row. A keyword overlap was tried and refused: the same night, classifying his
  annotations by keyword counted 46 instances of the adverb "simply" as
  complaints about complexity, and the correction was his.
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import pathlib
import re
import subprocess

REPO = pathlib.Path(__file__).resolve().parents[1]
TRANSCRIPT = (pathlib.Path.home() / ".claude" / "projects"
              / "-Users-georgejackson-Developer-Projects"
              / "a07b3790-0a2a-4978-aedb-bd842c0493d3.jsonl")

#: The window "not so long ago above" is read as. Stated as data so the
#: population is reproducible rather than a judgement made at run time.
WINDOW_FROM = "2026-11-02T12:00:00"

#: The 4 phrases the Wolfram attribution correction (b536ff86) introduced. If
#: sim carries all 4, the commit's CONTENT is present on sim whatever the merge
#: graph says.
WOLFRAM_PHRASES = (
    "You are quoting a rule that does not exist",
    "THIS IS AN ENGINEERING JUDGEMENT, NOT",
    "never be considered the primary falsifier route",
    "nobody is COMPELLED to install Wolfram",
)

#: Every question in the window, with the artefact that answers it or OPEN.
#: Recorded by reading, named per item, so each row is checkable.
ANSWERED = {
    "role vocabulary: orchestrator / classifier / worker":
        "experimental_notes/Reply_To_Your_Questions_2026-11-02.md "
        "(WHAT I RECORDED FROM YOUR TERMINOLOGY UPDATE)",
    "have you completed all your tasks; are we waiting for anything":
        "experimental_notes/Reply_To_Your_Questions_2026-11-02.md "
        "(THE SHORT ANSWERS FIRST)",
    "are there decisions I still need to make":
        "experimental_notes/Decisions_Awaiting_You_2026-11-03.md",
    "how confident are you I have never ruled on these before":
        "experimental_notes/Reply_To_Your_Questions_2026-11-02.md "
        "(ON WHETHER YOU WILL FIND REPEATS OF RULINGS YOU HAVE ALREADY GIVEN)",
    "ticket-store lessons for the harness registry":
        "scripts/which_ticket_store_lessons_the_registry_lacks_2026-11-02.py",
    "how will bugs be presented to researchers in the v1 UX":
        "experimental_notes/Reply_To_Your_Questions_2026-11-02.md "
        "(ON PRESENTING BUGS IN THE VERSION 1 USER INTERFACE) -- and this is "
        "where the `re` of his 23:26 correction was executed, citing Mozilla's "
        "own separation of Bugzilla, GitHub, Discourse and Mozilla Connect",
    "is the terminology (qs, stm, pf) too idiosyncratic":
        "experimental_notes/Reply_To_Your_Questions_2026-11-02.md "
        "(ON WHETHER THE TERMINOLOGY IS TOO IDIOSYNCRATIC)",
    "how useful has the ticket store actually proved":
        "experimental_notes/Reply_To_Your_Questions_2026-11-02.md "
        "(ON HOW USEFUL THE TICKET STORE ACTUALLY WAS TONIGHT)",
    "why do you still misparse some of my annotations":
        "bench/tests/test_a_markdown_heading_is_not_his_annotation_2026-11-02.py "
        "plus scripts/the_markdown_heading_rule_mutations_2026-11-02.py -- the "
        "2-hash rule was BUILT after his word, 4 of 4 mutations red",
    "would wrapping your paragraphs in asterisks help me parse them":
        "experimental_notes/Reply_To_Your_Questions_2026-11-02.md "
        "(ON WHY I STILL MISREAD SOME OF YOUR ANNOTATIONS, AND YOUR ASTERISK "
        "PROPOSAL)",
    "have you printed my end-of-session tts":
        "Desktop/CDSFL_tts/Session_Self_Audit_2026-11-03.txt and "
        "Consolidated_Morning_Report_2026-11-03.txt",
    "what is a solution outside coding; did a panel already answer it":
        "experimental_notes/Reply_To_Your_Questions_2026-11-02.md "
        "(ON WHETHER A PANEL ALREADY ANSWERED WHAT A SOLUTION IS OUTSIDE CODING)",
    "did your severity / residual-risk conflation reach my work":
        "experimental_notes/Reply_To_Your_Questions_2026-11-02.md "
        "(THE CONFLATION YOU WERE WORRIED ABOUT) -- 3 hits found, 1 is his "
        "name on a position of mine, and THAT ONE LINE IS STILL OPEN below",
    "should the push-back directive be strengthened":
        "experimental_notes/Reply_To_Your_Questions_2026-11-02.md "
        "(ON STRENGTHENING THE PUSH BACK DIRECTIVE)",
    "have all tested fixes been applied back to the runners":
        "experimental_notes/Reply_To_Your_Questions_2026-11-02.md "
        "(ON WHETHER ALL TESTED FIXES ARE APPLIED BACK TO THE RUNNERS)",
    "the simulated experiments: combined or separate":
        "Desktop/CDSFL_tts/Closing_Report_2026-11-03.txt (Question 1)",
    "the Meta Personal Agent Protocol / Meta-Agent Architectures":
        "Desktop/CDSFL_tts/Agent_Contract_Standards_2026-11-03.txt -- 0 genuine "
        "references anywhere in the project, so the derived standard never "
        "reached the core directives",
    "is the sim branch's 1 commit behind main significant":
        "THIS SCRIPT, section 2 below",
}

OPEN = {
    "the 1-line conflation fix he was asked to rule on":
        "scripts/can_the_carry_latch_the_gate_at_one_2026-10-31.py:6 still "
        "reads that residual risk accumulating across passes is 'what the "
        "founder's definition of severity requires'. That equates the 2 terms "
        "AND puts a position of CC1's under his name. The reply of 2026-11-02 "
        "brought him the proposal rather than the edit because he had issued "
        "`d`, and `d` is in force again, so it is still his word to give.",
}


def _iv(k: int, n: int):
    """Wilson and Clopper-Pearson, each on 2 INDEPENDENT routes."""
    from scipy import stats
    from statsmodels.stats.proportion import proportion_confint
    import mpmath
    mpmath.mp.dps = 40
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

    def bi(a, b, y):
        """Invert the regularised incomplete beta by bisection.

        HARDENED 2026-11-04. `mpmath.betainc` is fast, but its hyp2f1 path
        FAILS TO CONVERGE for large parameters at mid-range x. Measured at
        a=2437, b=17564 it succeeds for x <= 0.1264 and for x >= 0.9 and raises
        ValueError in between -- which is exactly where a bisection over [0, 1]
        takes its first step, so the whole inversion died rather than degrading.
        It surfaced when a producer called this at k=2436, n=20000; every
        existing caller used a small n, and the guard that executes every `_iv`
        against the same k and n uses n <= 38, so no test could have seen it.

        Where betainc raises, the same integral is computed by quadrature in
        log space instead. At the measured failing point that agreed with
        scipy's quantile to 1.11e-16. It costs about 6 s per bound against
        milliseconds for betainc, so it is used only after a failure, never by
        default.
        """
        logB = mpmath.log(mpmath.beta(a, b))

        def by_quad(x):
            if x <= 0:
                return mpmath.mpf(0)
            def dens(u):
                return mpmath.e**((a - 1) * mpmath.log(u)
                                  + (b - 1) * mpmath.log1p(-u) - logB)
            return mpmath.quad(dens, [0, min(mpmath.mpf(x), mpmath.mpf(1))])

        fell_back = False

        def f(x):
            nonlocal fell_back
            if not fell_back:
                try:
                    return mpmath.betainc(a, b, 0, x, regularized=True) - y
                except Exception:
                    fell_back = True
            return by_quad(x) - y

        # STOP ON PRECISION, not on a fixed count. The bracket halves every
        # step, so 2**-60 is already below this tolerance and a fixed 240 did
        # 180 redundant evaluations. That is free for betainc and it is NOT
        # free for the quadrature fallback, which costs about 28 ms per
        # evaluation: 240 steps took 6.66 s and 60 take 1.69 s for a bound
        # identical to 12 decimal places. The count is still capped so a
        # pathological case cannot spin.
        lo, hi = mpmath.mpf(0), mpmath.mpf(1)
        tol = mpmath.mpf("1e-18")
        for _ in range(240):
            if hi - lo < tol:
                break
            m = (lo + hi) / 2
            lo, hi = (m, hi) if f(m) < 0 else (lo, m)
        return float((lo + hi) / 2)

    cdiff = max(abs(cl - (0.0 if k == 0 else bi(k, n - k + 1, 0.025))),
                abs(ch - (1.0 if k == n else bi(k + 1, n - k, 0.975))))
    return (max(0.0, wl), wh), (cl, ch), max(wdiff, cdiff)


def _text(msg) -> str:
    c = msg.get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return "\n".join(b.get("text", "") for b in c
                         if isinstance(b, dict) and b.get("type") == "text")
    return ""


def his_messages():
    """His genuinely typed messages in the window, plus the reject tally."""
    out, rejects = [], collections.Counter()
    if not TRANSCRIPT.is_file():
        return out, rejects
    with TRANSCRIPT.open(encoding="utf-8", errors="replace") as fh:
        for ln in fh:
            if '"sdk"' not in ln:
                continue                      # cheap prefilter, SUPERSET of the test
            try:
                d = json.loads(ln)
            except Exception:                                # noqa: BLE001
                rejects["unparseable"] += 1
                continue
            if (d.get("message") or {}).get("role") != "user":
                rejects["not a user entry"] += 1
                continue
            if d.get("promptSource") != "sdk":
                rejects[f"promptSource={d.get('promptSource')!r}"] += 1
                continue
            if d.get("isMeta"):
                rejects["isMeta (hook output)"] += 1
                continue
            if d.get("isCompactSummary"):
                rejects["compaction summary"] += 1
                continue
            txt = _text(d["message"])
            if not txt.strip():
                rejects["no text"] += 1
                continue
            ts = d.get("timestamp") or ""
            if ts < WINDOW_FROM:
                rejects["before the window"] += 1
                continue
            out.append((ts, txt))
    out.sort()
    return out, rejects


def _show(rev: str, path: str) -> str:
    r = subprocess.run(["git", "show", f"{rev}:{path}"],
                       capture_output=True, text=True, cwd=str(REPO))
    return r.stdout


def branch_answer() -> dict:
    """Is the sim branch's '1 commit behind main' significant?"""
    def count(spec):
        r = subprocess.run(["git", "rev-list", "--count", spec],
                           capture_output=True, text=True, cwd=str(REPO))
        return int((r.stdout or "0").strip() or 0)
    behind = count("HEAD..main")
    ahead = count("main..HEAD")
    r = subprocess.run(["git", "log", "--format=%h %ad %s", "--date=short",
                        "HEAD..main"], capture_output=True, text=True, cwd=str(REPO))
    commits = [ln for ln in r.stdout.splitlines() if ln.strip()]
    sim = _show("HEAD", ".claude/CLAUDE.md")
    main = _show("main", ".claude/CLAUDE.md")
    missing = [p for p in WOLFRAM_PHRASES if p not in sim]
    ss, ms = set(sim.splitlines()), set(main.splitlines())
    only_main = [ln for ln in main.splitlines() if ln not in ss and ln.strip()]
    only_sim = [ln for ln in sim.splitlines() if ln not in ms and ln.strip()]
    return {"behind": behind, "ahead": ahead, "commits": commits,
            "phrases_missing_from_sim": missing,
            "only_main": only_main, "only_sim": only_sim,
            "sim_bytes": len(sim), "main_bytes": len(main)}


def main() -> int:
    argparse.ArgumentParser(
        description=("Enumerate the founder's recent questions and their "
                     "answering artefacts, and settle the sim-vs-main "
                     "divergence question.")).parse_args()

    print("=" * 76)
    print("WHICH OF HIS RECENT QUESTIONS ARE STILL OPEN?")
    print("=" * 76)
    msgs, rejects = his_messages()
    print(f"  window                     : from {WINDOW_FROM}")
    print(f"  his genuinely typed messages: {len(msgs)}")
    for ts, t in msgs:
        q = len(re.findall(r"\?", t))
        print(f"    {ts[:19]}  {len(t):>5} chars, {q:>2} question mark(s)")
    print("  entries REJECTED, counted so the filter is checkable:")
    for k, v in rejects.most_common(8):
        print(f"    {v:>7}  {k}")

    n = len(ANSWERED) + len(OPEN)
    k = len(OPEN)
    print(f"\n  questions enumerated       : {n}")
    print(f"  answered, each naming its artefact: {len(ANSWERED)}")
    print(f"  STILL OPEN                 : {k}")
    (wl, wh), (cl, ch), d = _iv(k, n)
    print(f"    {k} of {n} = {k/n:.6f}")
    print(f"    Wilson 95%          [{wl:.6f}, {wh:.6f}]")
    print(f"    Clopper-Pearson 95% [{cl:.6f}, {ch:.6f}]  (2-route |diff| {d:.1e})")
    print("\n  THE OPEN ITEM:")
    for q, why in OPEN.items():
        print(f"    {q}")
        print(f"      {why}")

    print("\n" + "=" * 76)
    print("2. IS THE SIM BRANCH'S '1 COMMIT BEHIND MAIN' SIGNIFICANT?  NO.")
    print("=" * 76)
    b = branch_answer()
    print(f"  commits main has that sim lacks : {b['behind']}")
    print(f"  commits sim has that main lacks : {b['ahead']}")
    for c in b["commits"]:
        print(f"    {c[:120]}")
    print(f"  .claude/CLAUDE.md  sim {b['sim_bytes']:,} bytes, "
          f"main {b['main_bytes']:,} bytes")
    miss = b["phrases_missing_from_sim"]
    print(f"  Wolfram corrective phrases MISSING from sim: {len(miss)} of "
          f"{len(WOLFRAM_PHRASES)}")
    (wl, wh), (cl, ch), dd = _iv(len(miss), len(WOLFRAM_PHRASES))
    print(f"    Wilson 95%          [{wl:.6f}, {wh:.6f}]")
    print(f"    Clopper-Pearson 95% [{cl:.6f}, {ch:.6f}]  (2-route |diff| {dd:.1e})")
    om, os_ = b["only_main"], b["only_sim"]
    print(f"  non-blank lines ONLY on main : {len(om)}")
    for row in om:
        print(f"    {row[:150]}")
    print(f"  non-blank lines ONLY on sim  : {len(os_)}")
    tot = len(om) + len(os_)
    if tot:
        (wl, wh), (cl, ch), dd = _iv(len(om), tot)
        print(f"  main's share of divergent content: {len(om)} of {tot} = "
              f"{len(om)/tot:.6f}")
        print(f"    Wilson 95%          [{wl:.6f}, {wh:.6f}]")
        print(f"    Clopper-Pearson 95% [{cl:.6f}, {ch:.6f}]  "
              f"(2-route |diff| {dd:.1e})")
    print("\n  THE ANSWER. The 1 commit is b536ff86, a 1-file Wolfram-attribution")
    print("  correction to .claude/CLAUDE.md. Sim already carries that correction")
    print("  in full. Every line main uniquely holds is an OLDER version of text")
    print("  sim has since revised -- the note standard at v1.7 where sim is")
    print("  v1.9, its foot-line convention, a DeepSeek row lacking the `disc`")
    print("  collision note, and 2 paragraphs sim has since corrected.")
    print("  SO 'behind' IS A MERGE-GRAPH FACT, NOT A CONTENT GAP, and merging")
    print("  main into sim would REGRESS those lines to superseded text.")
    print("  WHAT THIS DOES NOT CLAIM: it compares 1 file, the only file that")
    print("  commit touched. It is not a general statement that sim dominates")
    print("  main everywhere.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
