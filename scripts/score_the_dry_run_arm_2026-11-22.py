#!/usr/bin/env python3
"""Score the dry-run arm's 5 pre-registered predictions. Written BEFORE the run.

DRAFTED 2026-11-22; destination `scripts/`.

WHY IT IS WRITTEN FIRST. The 2026-09-02 blind audit holds 286 first-pass and 108
second-pass verdicts and names NO SCORER, so a result there is attributed to
nobody. The 2026-11-02 severity run fixed that by committing
`score_the_severity_predictions_2026-11-02.py` before launching. This follows
that precedent rather than inventing one.

★ EVERY PREDICATE IS EXERCISED TODAY, NOT ON ITS FIRST TRIAL. `--survey` runs
the 5 predicates against every archived run directory, so a predicate that
crashes, or that can never fire, is found NOW rather than when it is the only
thing standing between a run and its verdict. That is the same reason the
severity scorer took `--survey`.

WHAT IT CANNOT DO, STATED SO NOBODY LOOKS FOR IT. It cannot say whether a
RESUME verdict was RIGHT. That judgement is the founder's, because it decides
whether the harness may act unattended on its own classification, which is his
4th reserved category. This scorer reports WHAT was decided and on what
evidence; it does not grade the decision.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

REQUIRED_FIELDS = ["exit_code", "pid", "pid_alive", "pid_known",
                   "pulse_present", "pulse_age_s", "pulse_ended",
                   "rounds", "events"]
DECISIONS = "actuator_decisions.jsonl"


def _repo() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    for c in [here.parent, *here.parents]:
        if (c / "bench" / "tests").is_dir() and (c / "hooks").is_dir():
            return c
    return pathlib.Path.home() / "Developer_Projects" / "Constraint_Engineering"


REPO = _repo()


def load_decisions(run_dir: pathlib.Path) -> list[dict]:
    p = run_dir / DECISIONS
    if not p.is_file():
        return []
    out = []
    for line in p.read_text(errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            out.append({"_unparseable": line[:120]})
    return out


def p1(decs: list[dict]) -> tuple[str, str]:
    """At least 1 decision, every one carrying all 9 evidence fields."""
    if not decs:
        return "FALSIFIED", "0 decisions recorded"
    # ★ THE 9 FIELDS ARE NESTED UNDER "evidence", NOT AT THE TOP LEVEL.
    # Verified 2026-11-22 by calling the real `classify()`: it returns
    # {decision, evidence, reason}, and `record()` keeps that shape. The first
    # version of this predicate read the top level and would have FALSELY
    # FALSIFIED P1 on every real run. Found before the arm was ever launched,
    # which is the whole reason the scorer is written first.
    bad = []
    for i, d in enumerate(decs):
        ev = d.get("evidence")
        if not isinstance(ev, dict):
            bad.append(f"row {i}: no `evidence` object")
            continue
        missing = [f for f in REQUIRED_FIELDS if f not in ev]
        if missing:
            bad.append(f"row {i}: missing {','.join(missing)}")
    if bad:
        return "FALSIFIED", "; ".join(bad[:3])
    return "HELD", f"{len(decs)} decision(s), all 9 fields present in each"


def p2(decs: list[dict], invocations: int | None) -> tuple[str, str]:
    """0 resumes driven. THIS IS ALSO THE TEST OF CC1'S AUTONOMY CALL."""
    if not decs:
        # VACUITY GUARD, added 2026-11-22 after --survey reported HELD on all 375
        # archived runs, every one of which recorded 0 decisions. "0 of 0 acted"
        # proves nothing, and a false pass on the predicate that tests CC1's own
        # autonomy call is the worst place in this file to have one.
        return "NOT TESTABLE", ("0 decisions recorded, so there was nothing that "
                                "COULD have acted; this neither holds nor falsifies")
    acted = [d for d in decs if d.get("acted") is True]
    if acted:
        return "FALSIFIED", (f"{len(acted)} action(s) taken with --act withheld. "
                             f"The switch is not a switch, and the judgement that "
                             f"this arm was CC1's to run was WRONG.")
    if invocations is not None and invocations > 1:
        return "FALSIFIED", f"{invocations} invocations; expected exactly 1"
    return "HELD", f"0 of {len(decs)} decision(s) acted; launch invoked once"


def p3(decs: list[dict]) -> tuple[str, str]:
    """In the observable state, the decision is RESUME."""
    def _ev(d):
        return d.get("evidence") if isinstance(d.get("evidence"), dict) else {}
    target = [d for d in decs
              if _ev(d).get("exit_code") == 42
              and _ev(d).get("pid_alive") is False
              and _ev(d).get("pulse_present") is True]
    if not target:
        return "NOT TESTABLE", ("no decision in the state exit=42, process dead, "
                                "pulse present -- the arm observed nothing it "
                                "exists to observe, so it is UNINFORMATIVE rather "
                                "than reassuring")
    wrong = [d for d in target if str(d.get("decision", "")).upper() != "RESUME"]
    if wrong:
        return "FALSIFIED", (f"{len(wrong)} of {len(target)} in that state decided "
                             f"{ {str(d.get('decision')) for d in wrong} }")
    return "HELD", f"{len(target)} decision(s) in that state, all RESUME"


def p4(run_dir: pathlib.Path) -> tuple[str, str]:
    """No paid dispatch.

    ★ REWRITTEN 2026-11-22 AFTER --survey SHOWED THE FIRST VERSION WAS A FALSE
    POSITIVE DETECTOR. It flagged 12 of 375 archived runs, and 11 of those were
    `tickets.jsonl` -- a HARVESTED COPY of the repository's ticket store, which
    names `api.anthropic.com` as TEXT in a ticket body and not as a dispatch.
    Among the 12 was `severity_bounds_validation_20261102T004713Z`, the run this
    project explicitly recorded as unpaid. A predicate that condemns the very run
    it exists to clear is worse than no predicate. A substring is not a call.

    THE SOUND EVIDENCE IS THE TRIPWIRE, NOT A HOST NAME. The simulated runner
    replaces name resolution with a version that RAISES on any paid host, so:
      - the raise message present  -> a paid dispatch was ATTEMPTED  -> FALSIFIED
      - no evidence it was installed -> NOT TESTABLE, because "it did not raise"
        proves nothing about a guard that was never there
      - installed and silent        -> HELD
    """
    marker = "SIMULATED RUN ATTEMPTED A PAID DISPATCH"
    text = []
    for log in list(run_dir.glob("*.log")) + list(run_dir.glob("*.txt")):
        try:
            text.append(log.read_text(errors="ignore"))
        except OSError:
            continue
    blob = "\n".join(text)
    if marker in blob:
        return "FALSIFIED", "the paid-dispatch tripwire RAISED: a paid host was reached for"
    # Was the guard even present? A simulated arm declares -SIM seats.
    installed = ("-SIM" in blob) or ("sim_dispatch_shim" in blob) or \
                ("run_simulated" in blob)
    if not installed:
        return "NOT TESTABLE", ("no evidence the paid-dispatch tripwire was installed, "
                                "so its silence proves nothing")
    return "HELD", "tripwire evidenced as installed and it did not raise"


def p5(run_dir: pathlib.Path, before: list[dict] | None) -> tuple[str, str]:
    """Append-only JSONL beside the run."""
    p = run_dir / DECISIONS
    if not p.is_file():
        return "FALSIFIED", f"no {DECISIONS} in the run directory"
    now = load_decisions(run_dir)
    if any("_unparseable" in d for d in now):
        return "FALSIFIED", "a line is not valid JSON"
    if before is not None:
        if len(now) < len(before):
            return "FALSIFIED", f"rows SHRANK, {len(before)} -> {len(now)}"
        if now[:len(before)] != before:
            return "FALSIFIED", "a pre-existing row CHANGED; the log is not append-only"
    return "HELD", f"{len(now)} row(s), parseable, beside the run"


def score(run_dir: pathlib.Path, invocations: int | None = None,
          before: list[dict] | None = None) -> dict:
    decs = load_decisions(run_dir)
    return {
        "run": str(run_dir),
        "decisions": len(decs),
        "P1": p1(decs),
        "P2": p2(decs, invocations),
        "P3": p3(decs),
        "P4": p4(run_dir),
        "P5": p5(run_dir, before),
    }


def survey() -> int:
    """Exercise all 5 predicates against every archived run, TODAY."""
    logs = REPO / "bench" / "logs"
    runs = sorted([d for d in logs.iterdir() if d.is_dir()]) if logs.is_dir() else []
    print(f"SURVEY: {len(runs)} archived run director(ies)")
    print("Each predicate is RUN against each, so one that crashes or can never "
          "fire is found now rather than on its first real trial.\n")
    tally: dict[str, dict[str, int]] = {k: {} for k in ("P1", "P2", "P3", "P4", "P5")}
    crashed = 0
    with_decisions = 0
    for d in runs:
        try:
            r = score(d)
        except Exception as exc:
            print(f"  CRASH on {d.name}: {type(exc).__name__}: {exc}")
            crashed += 1
            continue
        if r["decisions"]:
            with_decisions += 1
        for k in tally:
            verdict = r[k][0]
            tally[k][verdict] = tally[k].get(verdict, 0) + 1
    print(f"  runs carrying a decision log : {with_decisions}")
    print(f"  predicate crashes            : {crashed}")
    for k, counts in tally.items():
        shown = ", ".join(f"{v}={n}" for v, n in sorted(counts.items()))
        print(f"  {k}: {shown}")
    print("\n  A predicate showing only one verdict across every archived run is "
          "NOT thereby broken -- 0 of these runs set the flag -- but a predicate "
          "that CRASHES is, and that is what this mode exists to find.")
    return 1 if crashed else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", help="the run's log directory")
    ap.add_argument("--invocations", type=int, default=None,
                    help="how many times the launch command was invoked")
    ap.add_argument("--survey", action="store_true",
                    help="exercise every predicate against every archived run")
    a = ap.parse_args()
    if a.survey:
        return survey()
    if not a.run:
        ap.error("pass --run <dir> or --survey")
    r = score(pathlib.Path(a.run), a.invocations)
    print(f"RUN: {r['run']}")
    print(f"  decisions recorded: {r['decisions']}\n")
    worst = 0
    for k in ("P1", "P2", "P3", "P4", "P5"):
        verdict, why = r[k]
        print(f"  {k}  {verdict:<13} {why}")
        if verdict == "FALSIFIED":
            worst = 1
    print("\n  WHAT THIS DOES NOT SAY: whether any RESUME verdict was RIGHT. That "
          "is the founder's ruling, not this script's.")
    return worst


if __name__ == "__main__":
    # NO `answer_help` CALL. That helper is for a script with NO parser, and its
    # `takes_no_arguments` defaults to True, so placing it here refuses this
    # script's own --survey and --run before argparse ever sees them. Measured
    # 2026-11-22 by running it: "unrecognised argument(s): --survey".
    # `scripts/score_the_severity_predictions_2026-11-02.py` does the same thing,
    # for the same reason: argparse answers --help by itself.
    raise SystemExit(main())
