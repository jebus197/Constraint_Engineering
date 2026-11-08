#!/usr/bin/env python3
"""Do the recovery documents' RESUME POINTERS still tell the truth about git?

WHY THIS EXISTS, AND WHY THE EXISTING CHECK CANNOT DO IT.

`bench/tests/test_a_stale_source_says_so_2026-09-21.py` asks whether a canonical
source is OLD AND SILENT: it takes the file's git-commit age, and if that age is
over 14 days it requires a supersession banner in the first 40 lines. That guard
is correct for what it guards, and it is blind to the defect found on
2026-09-21 at 22:14 BST during an `rs` restore:

    `experimental_notes/CDSFL_Agent_Operational_Plan.md` was committed 2 days
    earlier -- comfortably inside the 14-day window, so no banner was owed and
    none was missing -- and its RESUME POINTER read:

        HEAD `d17ab01`, main, working tree CLEAN,
        **11 ahead of `origin/main` -- NOT PUSHED**

    At the moment it was read, HEAD was `2b56916`, 23 commits later, and
    `origin/main` was identical to HEAD. Nothing was unpushed.

A document can therefore be RECENT and still assert a FALSE fact about the
current repository. Age does not detect that, because age is not the variable
that went wrong. The claim is about git state, so git state is what has to be
consulted -- which is `execute-do-not-grep` applied to a document rather than to
a module: the banner test asserts on the file's TEXT AGE and is individually
correct in doing so; only executing the claim against the repository can show
that the producer of the text and the repository disagree.

THE CONSEQUENCE IS NOT HYPOTHETICAL. This tracker is, by its own header, the
"First resource to read after any compaction or long break", and the same file
records the harm landing once already: a line claiming the answer-key sealing
was still waiting for the founder survived 2 days after he had done the work
himself, and on 2026-09-09 at 23:00 it was read during an `rs` restore and
repeated back to him as outstanding. The tracker's own note on that incident
states the mechanism exactly -- "The restore protocol reads this tracker FIRST
and with the greater authority, and it was the older document."

WHAT THIS SCRIPT MEASURES. For every canonical recovery source, it extracts the
git claims the document makes about itself -- the commit it names as HEAD, and
whether it says that work is or is not pushed -- and then it RESOLVES each claim
against the live repository. A source scores as TRUTHFUL when every git claim it
makes still holds, and FALSE when any one of them does not. Sources making no
git claim at all are reported separately and excluded from the proportion,
because a document that never claims a HEAD cannot misstate one.

The proportion carries a Wilson score interval, computed twice by independent
routes (statsmodels' `proportion_confint`, and the closed-form Wilson bounds
evaluated at 50 decimal digits in mpmath) so that the interval is not resting on
a single library. Agreement to 1e-12 is asserted, not assumed.

Run:  python3 scripts/resume_pointer_truth_2026-09-21.py
Exit: 0 when every git claim in every source holds, 1 when any is false.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
import math


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

REPO = Path(__file__).resolve().parents[1]

#: The documents a restoring session is told to read. Ordered as the `rs`
#: protocol reads them, tracker first, because that is the order in which a
#: false claim does damage.
SOURCES = [
    "experimental_notes/CDSFL_Agent_Operational_Plan.md",
    "resources/RECOVERY.md",
    "resources/ONBOARDING.md",
    "experimental_notes/CDSFL_MASTER_TASK_LIST.md",
    "experimental_notes/OUTSTANDING_QUEUE_to_BR2.md",
    "docs/CURRENT_STATE.md",
]

#: "HEAD `d17ab01`" / "HEAD d17ab01" / "HEAD is `abc1234`". A short SHA is 7 or
#: more hex characters; requiring 7 avoids matching ordinary words, and
#: requiring the literal word HEAD avoids matching the many commit hashes these
#: documents cite as HISTORY rather than as current state.
HEAD_CLAIM = re.compile(r"HEAD\s+(?:is\s+)?`?([0-9a-f]{7,40})`?", re.I)

#: An explicit assertion that work has NOT reached the remote.
NOT_PUSHED = re.compile(r"NOT PUSHED|not yet pushed|unpushed", re.I)

#: An explicit count of local-only commits, e.g. "11 ahead of `origin/main`".
AHEAD_CLAIM = re.compile(r"(\d+)\s+ahead of\s+`?origin/main`?", re.I)

#: A claim that DISCLAIMS currency is not a false claim about the present; it is
#: a correct record of the past, and flagging it reports history as error.
#:
#: This distinction was missing from the first version of this script and it
#: over-reported immediately: it charged `resources/RECOVERY.md` with naming a
#: HEAD 399 commits behind, when the block carrying that commit opens
#: "[HISTORICAL -- this block describes commit `b6a2032` and is NOT current
#: state]", and charged `docs/CURRENT_STATE.md` likewise, when that file's own
#: header states the git block is the PARENT of the commit containing it and is
#: "NOT CURRENT TRUTH". Both were doing exactly what this check wants documents
#: to do. Only a pointer that ASSERTS currency can be false about it.
DISCLAIMER = re.compile(
    r"HISTORICAL|SUPERSEDED|superseded by|NOT current (?:state|truth)|"
    r"NOT CURRENT TRUTH|kept as (?:a )?record|AT THAT COMMIT|SNAPSHOT",
    re.I,
)

#: How far back of a claim to look for its disclaimer. These documents put the
#: label at the head of the block, ahead of the commit it describes.
DISCLAIMER_LOOKBACK = 600


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO, capture_output=True, text=True
    ).stdout.strip()


def git_rc(*args: str) -> int:
    """A git exit CODE, kept beside `git` so both can be redirected together.

    `merge-base --is-ancestor` answers with its exit status: 0 means ancestor,
    1 means not an ancestor, and ANY OTHER VALUE is an error -- not a git
    repository, an unreadable object, a bad argument. Collapsing "error" into
    "not an ancestor" is what the first version of this did, and it produced a
    confident false statement ("it is on another branch or from a rewritten
    history") about a repository git had simply failed to read.
    """
    return subprocess.run(
        ["git", *args], cwd=REPO, capture_output=True, text=True
    ).returncode


def resume_pointer_region(text: str) -> str:
    """The newest resume pointer, or the document head if it marks none.

    These files are written newest-first, so the FIRST pointer encountered is
    the live one. Reading the whole document would sweep in every superseded
    pointer it has ever carried and report history as error.
    """
    marker = re.search(r"★?\s*RESUME POINTER", text, re.I)
    if marker:
        return text[marker.start(): marker.start() + 4000]
    return "\n".join(text.splitlines()[:80])


def check(rel: str, head_now: str, ahead_now: int) -> dict:
    path = REPO / rel
    if not path.is_file():
        return {"source": rel, "verdict": "ABSENT", "claims": [], "failures": []}

    region = resume_pointer_region(path.read_text(errors="replace"))
    claims: list[str] = []
    failures: list[str] = []
    disclaimed: list[str] = []
    notes: list[str] = []

    def asserts_currency(match: re.Match) -> bool:
        """False when the claim sits under a label denying it is current."""
        start = max(0, match.start() - DISCLAIMER_LOOKBACK)
        line_end = region.find("\n", match.end())
        window = region[start: line_end if line_end != -1 else match.end()]
        return not DISCLAIMER.search(window)

    m = HEAD_CLAIM.search(region)
    if m and not asserts_currency(m):
        disclaimed.append(f"HEAD == {m.group(1)} (labelled historical)")
        m = None
    if m:
        claimed = m.group(1)
        claims.append(f"HEAD == {claimed}")
        # Resolve rather than string-compare: the document may abbreviate to a
        # different width than `git rev-parse --short` happens to emit.
        # NAMING AN OLDER COMMIT IS NOT AN ERROR, AND REQUIRING OTHERWISE WAS A
        # DESIGN FAULT IN THE FIRST VERSION OF THIS SCRIPT (corrected 22:59 BST
        # the same evening, by executing it after 6 further commits).
        #
        # That version failed unless the pointer named the CURRENT HEAD. Since a
        # resume pointer is written once and HEAD moves with every commit, the
        # guard went red on the very next commit and would have gone red on
        # every commit thereafter, including commits with nothing to do with
        # project state. A check that is red by default is one that gets
        # disabled, and a disabled check is worse than none -- this repository's
        # own history has several guards that were worked around rather than
        # satisfied.
        #
        # What a resume pointer legitimately does is record where a session
        # stopped. So the commit it names is required to be REAL and to be an
        # ANCESTOR of HEAD -- which catches a fabricated hash, a commit from a
        # rewritten history, or one from another branch -- and its distance from
        # HEAD is reported as INFORMATION rather than charged as a failure.
        #
        # THE ORIGINAL DEFECT IS STILL CAUGHT, and by the part that always
        # should have carried it: "11 ahead of origin/main -- NOT PUSHED" are
        # claims about the state RIGHT NOW, not about a past moment, and both
        # were false. Those remain hard failures below.
        resolved = git("rev-parse", "--verify", "--quiet", claimed + "^{commit}")
        if not resolved:
            failures.append(f"names HEAD {claimed}, which is not a commit in this repository")
        elif resolved != head_now:
            rc = git_rc("merge-base", "--is-ancestor", resolved, head_now)
            behind = git("rev-list", "--count", f"{resolved}..HEAD")
            if rc == 1:
                failures.append(
                    f"names HEAD {claimed}, which is NOT an ancestor of {head_now[:7]} "
                    "-- it is on another branch or from a rewritten history"
                )
            elif rc != 0:
                failures.append(
                    f"names HEAD {claimed}, and git could not decide whether it is an "
                    f"ancestor of {head_now[:7]} (exit {rc}); the claim is UNCHECKED "
                    "rather than refuted"
                )
            else:
                notes.append(f"names {claimed}, {behind} commit(s) back (an ancestor, so not charged)")

    np_m = NOT_PUSHED.search(region)
    if np_m and not asserts_currency(np_m):
        disclaimed.append("work is NOT pushed (labelled historical)")
        np_m = None
    if np_m:
        claims.append("work is NOT pushed")
        if ahead_now == 0:
            failures.append(
                "says work is NOT PUSHED, but origin/main is identical to HEAD "
                "-- nothing is unpushed"
            )

    a = AHEAD_CLAIM.search(region)
    if a and not asserts_currency(a):
        disclaimed.append(f"{a.group(1)} ahead of origin/main (labelled historical)")
        a = None
    if a:
        claimed_ahead = int(a.group(1))
        claims.append(f"{claimed_ahead} ahead of origin/main")
        if claimed_ahead != ahead_now:
            failures.append(
                f"says {claimed_ahead} ahead of origin/main; the true count is {ahead_now}"
            )

    if not claims:
        verdict = "DISCLAIMED" if disclaimed else "NO_GIT_CLAIM"
    elif failures:
        verdict = "FALSE"
    else:
        verdict = "TRUTHFUL"
    return {
        "source": rel,
        "verdict": verdict,
        "claims": claims,
        "failures": failures,
        "disclaimed": disclaimed,
        "notes": notes,
    }


def wilson_two_ways(successes: int, n: int, alpha: float = 0.05):
    """Wilson score interval by 2 independent routes; they must agree.

    * DELEGATED 2026-11-08 on his ruling for B135 option 1. `alpha` is KEPT and
    CHECKED rather than dropped: the canonical helper fixes 0.05, and silently
    returning a 95 per cent interval for a caller who asked for another level
    would be the kind of quiet wrong answer this project exists to catch. The
    1 call site uses the default, verified before the edit.
    """
    if abs(alpha - 0.05) > 1e-12:
        raise ValueError(
            f"the canonical interval helper is fixed at alpha=0.05; "
            f"{alpha} was asked for, and a silent 95 per cent answer is wrong")
    (lo, hi), _cp, gap = _iv(successes, n)
    assert gap < 1e-12, (
        f"the 2 Wilson routes disagree by {gap}; a cross-verified figure that "
        f"does not cross-verify is not evidence")
    return float(lo), float(hi)


def main() -> int:
    head_now = git("rev-parse", "HEAD")
    ahead_now = int(git("rev-list", "--count", "origin/main..HEAD") or 0)

    print("RESUME-POINTER TRUTH CHECK")
    print(f"repository HEAD : {head_now[:7]}")
    print(f"ahead of origin/main : {ahead_now}")
    print()

    rows = [check(rel, head_now, ahead_now) for rel in SOURCES]

    for r in rows:
        print(f"[{r['verdict']:<12}] {r['source']}")
        for c in r["claims"]:
            print(f"                 claims: {c}")
        for n in r.get("notes", []):
            print(f"                 note  : {n}")
        for d in r.get("disclaimed", []):
            print(f"                 ok    : {d} -- correctly labelled, not judged")
        for f in r["failures"]:
            print(f"                 FALSE : {f}")
    print()

    judged = [r for r in rows if r["verdict"] in ("TRUTHFUL", "FALSE")]
    false_rows = [r for r in judged if r["verdict"] == "FALSE"]
    silent = [r for r in rows if r["verdict"] in ("NO_GIT_CLAIM", "DISCLAIMED")]
    absent = [r for r in rows if r["verdict"] == "ABSENT"]

    if judged:
        n, k = len(judged), len(false_rows)
        lo, hi = wilson_two_ways(k, n)
        print(
            f"FALSE git claims: {k} of {n} sources that make one "
            f"= {100.0 * k / n:.4f}%, Wilson [{100 * lo:.4f}%, {100 * hi:.4f}%]"
        )
        print("  (cross-verified: statsmodels proportion_confint vs mpmath closed form, 50 dps)")
    else:
        print("no source makes a git claim; the proportion is undefined, not 0")

    print(f"sources making no CURRENT git claim (excluded, cannot misstate): {len(silent)}")
    for r in silent:
        print(f"  {r['source']}")
    if absent:
        print(f"sources absent: {len(absent)}")
        for r in absent:
            print(f"  {r['source']}")

    return 1 if false_rows else 0


if __name__ == "__main__":
    # ANSWER `--help` BEFORE DOING THE WORK. Without this the flag is
    # silently ignored, the whole measurement runs -- a git walk, in this
    # family -- and exiting 0 is indistinguishable from having answered.
    # The founder's ruling on this class is that a `--help` must never
    # cost money, and 30 scripts were measured ignoring it on 2026-09-11.
    from _cli_help import answer_help   # scripts/ is sys.path[0] when run directly
    answer_help(__doc__, __file__)
    sys.exit(main())
