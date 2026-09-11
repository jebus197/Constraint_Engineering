#!/usr/bin/env python3
"""How stale are the "NEEDS FOUNDER" labels the work inventory was built from?

The founder objected, with justification, to being handed 17 decisions after
10 days of answering questions. The hypothesis under test is that the LABELS are
stale rather than the decisions outstanding: a document that said "NEEDS FOUNDER"
in August was never updated when he answered in September.

This measures the gap directly: for each source the inventory read, how long
since it was last written, and how many founder messages have arrived since.
A source that predates a founder message cannot know what he said in it.

The rate travels with this script per `measured-rate-travels-with-its-script`.
Two tools per proportion: statsmodels for the intervals, mpmath for a
closed-form Wilson sharing none of statsmodels' code.
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import sys
import subprocess

import mpmath as mp
from scipy import stats as sps
from statsmodels.stats.proportion import proportion_confint

REPO = pathlib.Path(__file__).resolve().parents[1]
TRANSCRIPT = pathlib.Path.home() / ".claude/projects/-Users-georgejackson-Developer-Projects/a07b3790-0a2a-4978-aedb-bd842c0493d3.jsonl"

SOURCES = [
    "experimental_notes/CDSFL_Agent_Operational_Plan.md",
    "experimental_notes/OUTSTANDING_QUEUE_to_BR2.md",
    "experimental_notes/RUNWAY_to_BR2_2026-08-18.md",
    "resources/RECOVERY.md",
    "docs/CURRENT_STATE.md",
]


def last_commit_time(rel: str) -> dt.datetime | None:
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cI", "--", rel],
                             cwd=REPO, capture_output=True, text=True, timeout=20)
        s = out.stdout.strip()
        return dt.datetime.fromisoformat(s) if s else None
    except Exception:
        return None


def founder_message_times() -> list[dt.datetime]:
    """Timestamps of the founder's OWN TYPED messages in this session.

    CORRECTED 2026-09-09 before this figure was ever quoted. The first version
    counted every transcript entry whose type is "user" and reported 6557. That
    is wrong by a factor of 21: 6072 of those entries are TOOL RESULTS, which the
    harness also files under the user role, and a further 175 are hook payloads
    that begin with a tag rather than prose. The founder typed 311 of them.

    Counting the wrong denominator is the exact class of error this script exists
    to explain, so it is filtered here and the filter is stated rather than
    buried: an entry is a typed message only if it carries no toolUseResult, and
    its text is non-empty and does not begin with "<".
    """
    out: list[dt.datetime] = []
    unparsed: list[str] = []
    if not TRANSCRIPT.exists():
        return out
    with TRANSCRIPT.open(errors="replace") as fh:
        for line in fh:
            if '"type":"user"' not in line:
                continue
            try:
                o = json.loads(line)
            except Exception:
                continue
            if o.get("type") != "user" or o.get("toolUseResult") is not None:
                continue
            content = (o.get("message") or {}).get("content")
            if isinstance(content, str):
                text = content
            elif isinstance(content, list):
                if all(b.get("type") == "tool_result"
                       for b in content if isinstance(b, dict)):
                    continue
                text = "".join(b.get("text", "") for b in content
                               if isinstance(b, dict) and b.get("type") == "text")
            else:
                continue
            if not text.strip() or text.lstrip().startswith("<"):
                continue
            ts = o.get("timestamp")
            if not ts:
                unparsed.append("(no timestamp field)")
                continue
            try:
                out.append(dt.datetime.fromisoformat(ts.replace("Z", "+00:00")))
            except (ValueError, TypeError) as exc:
                # NOT SWALLOWED. A dropped message understates the very count this
                # script reports, and `except Exception: pass` is the shape that hid
                # 3 successive faults in _record_recovery_ran on 2026-09-08 -- each
                # failure concealing the next. Caught by the suite on 2026-09-09,
                # which is the mechanism working.
                unparsed.append(f"{ts!r}: {type(exc).__name__}: {exc}")
    if unparsed:
        print(f"  WARNING: {len(unparsed)} message timestamp(s) could not be parsed "
              f"and are MISSING from the count below:", file=sys.stderr)
        for u in unparsed[:5]:
            print(f"    {u}", file=sys.stderr)
        if len(unparsed) > 5:
            print(f"    ... and {len(unparsed) - 5} more not listed here",
                  file=sys.stderr)
    return sorted(out)


def wilson_mp(k: int, n: int, conf: float = 0.95) -> tuple[float, float]:
    mp.mp.dps = 30
    z = mp.mpf(str(sps.norm.ppf(1 - (1 - conf) / 2)))
    p, N = mp.mpf(k) / n, mp.mpf(n)
    c = (p + z**2 / (2 * N)) / (1 + z**2 / N)
    h = (z / (1 + z**2 / N)) * mp.sqrt(p * (1 - p) / N + z**2 / (4 * N**2))
    return float(c - h), float(c + h)


def main() -> int:
    # AN ABSENT TRANSCRIPT IS NOT ZERO STALENESS. Found 2026-09-11, after the
    # fable panel seat pointed at this file's machine-specific input path.
    #
    # `founder_message_times()` returns [] when the transcript is missing, and
    # every "founder msgs since" count is then 0, so the script printed
    #
    #     Sources written BEFORE at least 1 later founder message: 0 of 5 = 0.0%
    #         Wilson 95% [statsmodels] : [0.0%, 43.4%]
    #
    # with its conclusion, and exited 0. A clean authoritative no-staleness
    # result manufactured from no data at all -- which is worse than a
    # traceback, because it reads as a measurement. This project's own record
    # names the shape: "a roster filter that returns EMPTY is indistinguishable,
    # downstream, from the feature working".
    #
    # The transcript lives under the agent session directory, OUTSIDE the
    # repository, so it is absent in every clone and on every other machine.
    # The 3 sibling scripts that read it already decline by name; this one now
    # does too. Held by bench/tests/test_outside_inputs_decline_2026-09-11.py.
    if not TRANSCRIPT.exists():
        print(f"no transcript at {TRANSCRIPT}", file=sys.stderr)
        print("This script counts the founder's messages from a session "
              "transcript under the agent session directory, which is outside "
              "the repository and absent in a clone or on another machine. "
              "Without it every count is 0 and the staleness rate would read "
              "as 0 of 5 rather than as unmeasured.", file=sys.stderr)
        return 2

    msgs = founder_message_times()
    now = dt.datetime.now(dt.timezone.utc)
    print(f"Founder messages found in this session's transcript: {len(msgs)}")
    if msgs:
        print(f"  first {msgs[0].astimezone():%Y-%m-%d %H:%M}, last {msgs[-1].astimezone():%Y-%m-%d %H:%M}\n")

    print(f"{'source':<52}{'last written':<22}{'age':>8}{'founder msgs since':>20}")
    stale = 0
    for rel in SOURCES:
        t = last_commit_time(rel)
        if t is None:
            print(f"{rel:<52}{'(not in git log)':<22}")
            continue
        age = now - t.astimezone(dt.timezone.utc)
        since = sum(1 for m in msgs if m > t.astimezone(dt.timezone.utc))
        if since > 0:
            stale += 1
        print(f"{rel:<52}{t.astimezone():%Y-%m-%d %H:%M:%S}   {age.days:>3d}d{'':>3}{since:>20d}")

    n = len(SOURCES)
    lo_w, hi_w = proportion_confint(stale, n, alpha=0.05, method="wilson")
    lo_c, hi_c = proportion_confint(stale, n, alpha=0.05, method="beta")
    lo_m, hi_m = wilson_mp(stale, n)
    print(f"\nSources written BEFORE at least 1 later founder message: {stale} of {n} = {stale/n:.1%}")
    print(f"    Wilson 95%          [statsmodels] : [{lo_w:.1%}, {hi_w:.1%}]")
    print(f"    Wilson 95%          [mpmath     ] : [{lo_m:.1%}, {hi_m:.1%}]   agree={abs(lo_w-lo_m)<1e-12}")
    print(f"    Clopper-Pearson 95% [statsmodels] : [{lo_c:.1%}, {hi_c:.1%}]")
    print("\n  A source written before a founder message cannot record what he said in it.")
    print("  That is the mechanism by which a decision he HAS made keeps reappearing")
    print("  as one he has not. The defect is in the write-back, not in his answering.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
