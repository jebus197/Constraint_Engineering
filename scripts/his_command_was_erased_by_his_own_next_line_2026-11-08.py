#!/usr/bin/env python3
"""His `d` of 2026-11-08 13:54:09 was erased by his own `rs` 11 seconds later.

WHY THIS EXISTS, AND IT CORRECTS MY OWN TICKET. `pf:8fd722f07900` recorded the
cause as the Stop gate reading its OWN feedback as a founder message. That is
REFUTED: `is_founder_message` has rejected `isMeta` entries since 2026-09-11 and
`bench/tests/test_hook_never_reads_its_own_words_2026-09-11.py` holds it. The
real cause was found by EXECUTING `turn_signals` against the live transcript
rather than reading the hook, and it is 2 faults, not 1.

FAULT 1 -- LAST-WINS. `turn_signals` recomputes `had_d` on every accepted
founder entry, so only the LAST one counts. On 2026-11-08 he sent his
instruction at 13:54:09 carrying `a` and `d`, then `rs` on its own at 13:54:20.
`founder_commands('rs')` is `['rs']`, which contains no `d`, so `had_d` became
False and the gate refused 8 times against a standing `d`. His ruling of
2026-09-11 is that his commands are law; a command cancelled by his own next
line is not law.

FAULT 2 -- A HARNESS NOTIFICATION COUNTS AS HIM. A `<task-notification>` user
entry carries `isMeta: None`, so it passes the predicate. 3 of them sit in this
turn's own window, each with no commands, so each ALSO resets `had_d` -- and
`_turn_key` takes its budget key from the same walk, so a background task
completing mid-turn MOVES the turn key and hands the gate a fresh budget of
`MAX_REFUSALS_PER_TURN`. That is the mechanism behind 8 refusals in 1 turn.

THE DISCRIMINATOR IS STRUCTURAL, NOT TEXTUAL, which is the lesson of
`feedback_an_explicit_marker_and_fixed_widths_beat_a_shape_2026-11-04`. Matching
the literal `<task-notification>` would be a shape; the harness states the
provenance in 3 independent fields, measured below. The predicate rejects only
on POSITIVE evidence of non-human origin, so an entry of his that lacks the
fields is still accepted -- failing toward obeying him, per his ruling.

Exit 0 when every cross-check agrees; 1 otherwise.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
HOOK = REPO / "hooks" / "work_not_narrate.py"
SESSIONS = pathlib.Path.home() / ".claude/projects/-Users-georgejackson-Developer-Projects"

#: Scanned window. The transcript is ~900 MB; the hook itself reads at most
#: TAIL_BYTES (48 MiB), so a wider window measures the harness's own habit
#: rather than what the hook sees. Both are reported.
WINDOW = 200 * 1024 * 1024


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


def load_hook():
    spec = importlib.util.spec_from_file_location("wnn_probe", HOOK)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["wnn_probe"] = mod
    spec.loader.exec_module(mod)
    return mod


def non_human(d: dict) -> list[str]:
    """Which of the 3 structural markers POSITIVELY say this is not him."""
    out = []
    if d.get("promptSource") == "system":
        out.append("promptSource=system")
    to = d.get("turnOrigin")
    if isinstance(to, str) and to and to != "human":
        out.append(f"turnOrigin={to}")
    og = d.get("origin")
    if isinstance(og, dict):
        k = og.get("kind")
        if isinstance(k, str) and k and k != "human":
            out.append(f"origin.kind={k}")
    return out


def accepted_before_the_repair(d: dict) -> bool:
    """The predicate as it stood BEFORE 2026-11-08, so the figure survives.

    ★ WHY THIS IS NOT `hook.is_founder_message`. A first version of this script
    called the live predicate, so the moment the repair landed the count fell
    from 75 of 104 to 0 of 29 and the script could no longer reproduce the
    number it exists to record -- `feedback_a_producer_outlives_its_defect_2026-10-15`
    and `feedback_a_grep_verdict_cannot_see_its_subject_removed_2026-11-02`.
    The pre-repair acceptance test is 4 structural clauses and is reproduced
    here verbatim so the measurement is re-runnable against any transcript.
    """
    if d.get("type") != "user":
        return False
    if d.get("isCompactSummary") or d.get("isMeta"):
        return False
    c = d.get("message", {}).get("content")
    if isinstance(c, list) and any(
            isinstance(x, dict) and x.get("type") == "tool_result" for x in c):
        return False
    return True


def scan(path: pathlib.Path, window: int, hook):
    size = path.stat().st_size
    start = max(0, size - window)
    with path.open("rb") as fh:
        fh.seek(start)
        if start:
            fh.readline()
        raw = fh.read()
    accepted = injected = marked = text_bearing = 0
    unmarked_injected = []
    for line in raw.split(b"\n"):
        if b'"type":"user"' not in line and b'"type": "user"' not in line:
            continue
        try:
            d = json.loads(line)
        except Exception:                                      # noqa: BLE001
            continue
        if not accepted_before_the_repair(d):
            continue
        accepted += 1
        c = d.get("message", {}).get("content")
        if isinstance(c, list):
            c = " ".join(x.get("text", "") for x in c if isinstance(x, dict))
        if not isinstance(c, str):
            continue
        text_bearing += 1
        is_inj = any(t in c for t in ("<task-notification>", "<ci-monitor-event>",
                                      "<local-command-stdout>"))
        if is_inj:
            injected += 1
            if non_human(d):
                marked += 1
            else:
                unmarked_injected.append(c[:70].replace("\n", " "))
    return accepted, text_bearing, injected, marked, unmarked_injected


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--window", type=int, default=WINDOW,
                    help="bytes of transcript tail to scan")
    args = ap.parse_args()
    hook = load_hook()
    fails: list[str] = []

    print("=" * 78)
    print("1. THE LIVE READING, against the real transcript")
    print("=" * 78)
    ts = sorted(SESSIONS.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
    if not ts:
        print("  no transcript found; nothing to measure")
        return 0
    T = ts[-1]
    print(f"  transcript: {T.name}  {T.stat().st_size / 1e6:.1f} MB")
    calls, prose, commit, had_d = hook.turn_signals(T)
    print(f"  turn_signals -> calls={calls} prose={prose} commit={commit} had_d={had_d}")
    print(f"  _turn_key    -> {hook._turn_key(T)!r}")

    print("\n" + "=" * 78)
    print("2. HOW RELIABLE IS THE STRUCTURAL DISCRIMINATOR?")
    print("=" * 78)
    acc, txt, inj, marked, unmarked = scan(T, args.window, hook)
    print(f"  window scanned              : {args.window / 1024 / 1024:.0f} MiB")
    print("  predicate                   : the PRE-REPAIR one, "
          "so this stays re-runnable after the fix")
    print(f"  user entries it accepts as his: {acc}")
    print(f"  of those, text-bearing      : {txt}")
    print(f"  of those, harness-injected  : {inj}")
    if inj:
        (wl, wh), (cl, ch), dis = _iv(marked, inj)
        print(f"  injected entries CARRYING a non-human marker: {marked} of {inj} "
              f"= {marked / inj:.6f}")
        print(f"    Wilson [{wl:.6f}, {wh:.6f}]  Clopper-Pearson [{cl:.6f}, {ch:.6f}]")
        print(f"    the helper's own 2 routes disagree by {dis:.3e}")
        if dis > 1e-9:
            fails.append(f"interval routes disagree by {dis}")
        if unmarked:
            print("  ★ UNMARKED INJECTED ENTRIES -- the discriminator would miss these:")
            for u in unmarked[:5]:
                print(f"      {u!r}")
            if len(unmarked) > 5:
                print(f"      ... and {len(unmarked) - 5} more withheld, of "
                      f"{len(unmarked)} unmarked injected entries")
    else:
        print("  0 injected entries in this window, so the rate is not estimable here")

    print("\n" + "=" * 78)
    print("3. THE LAST-WINS FAULT, shown rather than asserted")
    print("=" * 78)
    lines = hook._tail_lines(T)
    seen = []
    for line in lines:
        if '"type":"user"' not in line and '"type": "user"' not in line:
            continue
        try:
            d = json.loads(line)
        except Exception:                                      # noqa: BLE001
            continue
        if not hook.is_founder_message(d):
            continue
        c = d.get("message", {}).get("content")
        if isinstance(c, list):
            c = " ".join(x.get("text", "") for x in c if isinstance(x, dict))
        if not isinstance(c, str) or "<system-reminder>" in c:
            continue
        seen.append((d.get("timestamp", "")[:19], hook.founder_commands(c),
                     non_human(d), c[:46].replace("\n", " ")))
    print(f"  entries the scan walks, in order ({len(seen)}):")
    for t, cmds, nh, head in seen:
        flag = "  <-- NOT HIM" if nh else ""
        print(f"    {t}  cmds={cmds}  {head!r}{flag}")
    if seen:
        union = sorted({c for _, cmds, nh, _ in seen if not nh for c in cmds})
        print(f"\n  LAST-WINS gives : {seen[-1][1]}")
        print(f"  THE UNION gives : {union}")
        print(f"  'd' lost by last-wins: "
              f"{'d' in union and 'd' not in seen[-1][1]}")

    print("\n" + "=" * 78)
    if fails:
        for f in fails:
            print("FAILURE:", f)
        return 1
    print("all cross-checks agree")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
