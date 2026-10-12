#!/usr/bin/env python3
"""Is restoring at the first task boundary sooner than waiting for the founder?

HIS DESIGN CORRECTION, 2026-10-12: the restore *"would need to fire at a safe point
immediately after the first task in any given task list completes after a compaction"*,
because *"it's probably not heathy to interrupt a task that was running immediately
before compaction and that continues after compaction completes."*

This script produces every figure quoted in `~/.claude/hooks/compaction_task_boundary.py`
and in the commit that wired it, under `measured-rate-travels-with-its-script`.

THE THREE CANDIDATE TRIGGERS
  * message  — what shipped before: `UserPromptSubmit`, so it waits for him.
  * turn-end — the proposal he corrected: fires mid-task.
  * commit   — the task boundary: the tree is consistent and no task is half-applied.

AND THE HONEST RESULT. A commit trigger ALONE is not reliably better than waiting:
sooner in only 27 of 43 compactions, Wilcoxon p = 0.2164, with a WORSE maximum. The
gain comes from COMPOSING the two, because they fire on whichever comes first. That
composed figure is the one the hook claims, and it is significant at p = 2.803e-06.

A --help COSTS NOTHING: reads the transcript and `git log`, no dispatch, no network.
"""
from __future__ import annotations

import json
import pathlib
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

import numpy as np
from scipy import stats
from statsmodels.stats.proportion import proportion_confint

REPO = pathlib.Path(__file__).resolve().parent.parent
TRANSCRIPT = pathlib.Path(
    "/Users/georgejackson/.claude/projects/"
    "-Users-georgejackson-Developer-Projects/"
    "a07b3790-0a2a-4978-aedb-bd842c0493d3.jsonl")

#: Prefixes that mark a user-role entry as harness-injected rather than typed by him.
NOT_HIS = ("Stop hook feedback:", "This session is being continued",
           "<system-reminder>", "Caveat: The messages below")


def compactions_and_messages(path: pathlib.Path):
    """Structural compaction markers, and the founder's own messages."""
    comps, msgs = [], []
    with path.open("rb") as fh:
        for raw in fh:
            try:
                e = json.loads(raw)
            except Exception:
                continue
            ts = e.get("timestamp")
            if not ts:
                continue
            try:
                t = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except Exception:
                continue
            if e.get("isCompactSummary"):
                comps.append(t)
                continue
            msg = e.get("message") or {}
            if (e.get("type") or msg.get("role")) != "user":
                continue
            c = msg.get("content")
            txt = None
            if isinstance(c, str):
                txt = c
            elif isinstance(c, list):
                parts = [b.get("text", "") for b in c
                         if isinstance(b, dict) and b.get("type") == "text"]
                if parts:
                    txt = " ".join(parts)
            if not txt or not txt.strip():
                continue
            if any(txt.lstrip().startswith(p) for p in NOT_HIS):
                continue
            msgs.append(t)
    return sorted(set(comps)), sorted(set(msgs))


def commit_times() -> list[datetime]:
    r = subprocess.run(["git", "log", "--all", "--pretty=%cI"],
                       cwd=str(REPO), capture_output=True, text=True)
    return sorted(datetime.fromisoformat(l.strip()).astimezone(timezone.utc)
                  for l in (r.stdout or "").splitlines() if l.strip())


def _lags(events: list[datetime], after: list[datetime]) -> np.ndarray:
    out = []
    for c in events:
        nxt = next((x for x in after if x > c), None)
        out.append((nxt - c).total_seconds() / 60.0 if nxt else float("nan"))
    return np.array([v for v in out if v == v])


def _ci(k: int, n: int) -> str:
    wlo, whi = proportion_confint(k, n, method="wilson")
    clo = stats.beta.ppf(0.025, k, n - k + 1) if k else 0.0
    chi = stats.beta.ppf(0.975, k + 1, n - k) if k < n else 1.0
    return f"Wilson [{wlo:.4f}, {whi:.4f}]  CP [{clo:.4f}, {chi:.4f}]"



def _answer_help(doc, path, args):
    """Answer `--help` AND refuse an unknown flag, through the shared helper.

    WIRED 2026-10-12 after `test_operational_scripts` caught all of this date's
    new scripts accepting `--this-flag-does-not-exist` with exit 0 -- in the
    guard's own words, *"an unrecognised argument that reads as success is the
    118-day no-op again"*. The hand-rolled block each carried answered `--help`
    and ignored everything else. `scripts/_cli_help.answer_help` enforces both
    in the one place every caller goes through.
    """
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _cli_help import answer_help
    answer_help(doc, path, list(args))


def main(argv: list[str]) -> int:
    _answer_help(__doc__, __file__, argv[1:])
    if not TRANSCRIPT.is_file():
        print(f"  transcript not on this machine: {TRANSCRIPT}")
        return 3

    comps, msgs = compactions_and_messages(TRANSCRIPT)
    commits = commit_times()
    print(f"compactions {len(comps)}   founder messages {len(msgs)}   "
          f"commits on all refs {len(commits)}")

    msg_l = _lags(comps, msgs)
    com_l = _lags(comps, commits)
    m = min(len(msg_l), len(com_l))
    msg_l, com_l = msg_l[:m], com_l[:m]
    both = np.minimum(msg_l, com_l)
    print()
    print(f"{'trigger':<22} {'median':>9} {'mean':>10} {'p90':>10} {'max':>10}")
    for lab, v in (("message (shipped)", msg_l), ("commit alone", com_l),
                   ("BOTH (composed)", both)):
        print(f"{lab:<22} {np.median(v):>9.2f} {v.mean():>10.2f} "
              f"{np.percentile(v, 90):>10.2f} {v.max():>10.2f}")

    print()
    print("COMMIT ALONE IS NOT RELIABLY BETTER — the honest negative result")
    k = int(((msg_l - com_l) > 0).sum())
    w = stats.wilcoxon(msg_l, com_l, alternative="greater")
    print(f"  sooner than waiting on {k} of {m}  {_ci(k, m)}")
    print(f"  Wilcoxon one-sided p = {w.pvalue:.4f}  "
          f"-> {'NOT significant' if w.pvalue > 0.05 else 'significant'}")
    print(f"  and its maximum is WORSE: {com_l.max():.2f} min against {msg_l.max():.2f}")

    print()
    print("COMPOSED IS — because the two fire on whichever comes first")
    d = msg_l - both
    k2 = int((d > 0).sum())
    w2 = stats.wilcoxon(msg_l, both, alternative="greater")
    print(f"  improvement non-negative by construction: {bool(np.all(d >= 0))}")
    print(f"  strictly improved on {k2} of {m}  {_ci(k2, m)}")
    print(f"  median improvement {np.median(d):.2f} min")
    print(f"  Wilcoxon one-sided p = {w2.pvalue:.3e}")

    print()
    print("THE CASE HE DESCRIBED — UNATTENDED work (his next message >30 min away)")
    mask = msg_l > 30
    mu, bu = msg_l[mask], both[mask]
    w3 = stats.wilcoxon(mu, bu, alternative="greater")
    k3 = int(((mu - bu) > 0).sum())
    print(f"  such compactions: {int(mask.sum())} of {m}")
    print(f"  median wait for him    {np.median(mu):8.2f} min")
    print(f"  median with the design {np.median(bu):8.2f} min")
    print(f"  median saving          {np.median(mu - bu):8.2f} min")
    print(f"  improved on {k3} of {len(mu)}  {_ci(k3, len(mu))}")
    print(f"  Wilcoxon one-sided p = {w3.pvalue:.3e}")
    print(f"  total degraded work avoided: {float((mu - bu).sum())/60:.2f} hours")

    print()
    print("THE 2026-10-11 COMPACTION, the one that prompted this")
    C = datetime.fromisoformat("2026-10-11T22:23:01.510+00:00")
    nxt_commit = next((x for x in commits if x > C), None)
    nxt_msg = next((x for x in msgs if x > C), None)
    if nxt_commit:
        print(f"  first commit after it  : +{(nxt_commit-C).total_seconds()/60:7.2f} min"
              f"   <- the task boundary")
    if nxt_msg:
        print(f"  his next message       : +{(nxt_msg-C).total_seconds()/60:7.2f} min"
              f"   <- what actually fired")
    if nxt_commit and nxt_msg:
        print(f"  saving                 : {(nxt_msg-nxt_commit).total_seconds()/60:7.2f} min")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
