#!/usr/bin/env python3
"""CDSFL POST: pass or fail against each check, and halt the boot at the first fail.

THE FOUNDER'S ASK, 2026-10-06: *"We should probably have some kind of integrity check
anyway, before an experiment runs to report if all prerequisite modes are live and the
system overall is green - before an experiment can proceed. I believe some time ago I
gave an analogy of a computer bios health check."*

AND THE SEMANTICS, same day, which overrule the first version of this file: *"on a
bios screen when 'booting up' it prints a simple message against each check, which is
just 'pass or fail'. If a test passes then the next check fails, the system is halted,
giving the user an opportunity to investigate. This fits an early paradigm as CDSFL as
an 'operating system', that can operate over many models and many systems
independently of the underlying system itself."*

So: PASS or FAIL, nothing in between, and the first FAIL halts. The first version
reported 3 states and returned without blocking, on the reasoning that "a health check
that silently blocks is worse than none". The ruling answers that: a HALT is not
silent. It names the failing check, stops, and hands the operator the machine.

THE 3-STATE SCHEME WAS HIDING A DEFECT, and dropping it exposes it. AMBER never set
the exit code, and a check whose own code raised was mapped to AMBER -- so a BROKEN
CHECK BOOTED. Measured by `scripts/post_semantics_2026-10-06.py` part 1: injecting a
check that raises returned exit 0 from the previous version. A guard that cannot fail
is not a guard. Here, a check that raises is a FAIL.

WHY EACH ROW EXECUTES SOMETHING, which is the whole point. A facility can be ARMED IN
CONFIGURATION AND INERT IN FACT. The capability ladder was armed throughout and
climbed nothing, because every simulated seat resolved to one model -- 0 of 6 source
seats got a climb between 2 different models, and no configuration comparison could
ever have seen it.

THE ORDER IS LOAD-BEARING UNDER HALT-ON-FIRST, in a way it was not when every row ran.
A check that runs before its own precondition is reporting on an unestablished
premise, and the halt then stops at the wrong row. `post_semantics_2026-10-06.py`
part 2 holds the order against the declared dependencies with z3 and an independent
index scan.

`--all` RUNS EVERY CHECK INSTEAD OF HALTING, and it is not a weakening of the ruling.
Halt-on-first costs 1 boot cycle per failure: SymPy gives k runs to clear k failures
against 1 for a diagnostic listing, agreeing with a NumPy simulation on 2000 of 2000
trials. The halting screen is the default and the gate; `--all` is the service manual.

Run:  python3 scripts/preflight_health_check_2026-10-06.py
      python3 scripts/preflight_health_check_2026-10-06.py --all
      python3 scripts/preflight_health_check_2026-10-06.py --seats CC2-SIM,Fable-SIM
Exit: 0 every check passed, 1 a check FAILED (boot halted).
"""
from __future__ import annotations

import argparse
import pathlib
import sys
import traceback

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

PASS, FAIL = "PASS", "FAIL"
#: Printed in the rows a halt never reached. Not a verdict -- an absence of one.
NOT_RUN = "not run"

DEFAULT_SEATS = ["CC2-SIM", "ChatGPT-SIM", "Codex-SIM", "DeepSeek-SIM",
                 "Gemini-SIM", "Fable-SIM"]

_WIDTH = 72


def _parse_args(argv=None):
    p = argparse.ArgumentParser(
        prog="preflight_health_check_2026-10-06.py",
        description="CDSFL POST — pass/fail per check, halting at the first fail.")
    p.add_argument("--seats", default=",".join(DEFAULT_SEATS),
                   help="comma-separated seat labels the run will dispatch")
    p.add_argument("--seat-models", default=None, dest="seat_models",
                   help="the seat-model mode the run RESOLVED to (uniform|ladder). "
                        "A caller that knows its own resolved value must pass it; "
                        "omitted, the launcher's declared default is read instead, "
                        "which is only correct when nothing overrode it.")
    p.add_argument("--expect-uniform-ladder", action="store_true",
                   dest="expect_uniform",
                   help="the run deliberately uses --seat-models uniform as a "
                        "control arm, so a non-climbing ladder is expected and is "
                        "reported as PASS rather than halting the boot")
    p.add_argument("--all", action="store_true", dest="run_all",
                   help="run every check instead of halting at the first failure; "
                        "lists all failures in 1 pass for diagnosis")
    return p.parse_args(argv)


# ───────────────────────── the checks ─────────────────────────
# Each returns (status, headline, notes). Each must EXECUTE something.
# A check declares whether it needs the seat roster; nothing is inferred from its
# position in CHECKS, because keying that on `fn is CHECKS[0][1]` meant replacing
# the list silently changed which check received the roster.

def _launcher_rung_budget() -> int:
    """The rung budget the simulated runner will actually use, read from it.

    0 means exhaust. Falls back to the dataclass default only if the launcher does
    not set it at all, and says so rather than guessing.
    """
    import ast
    from bench.reference_runner_v3 import RunnerConfig
    src = (REPO / "bench" / "tools" / "run_simulated_experiment.py").read_text(
        encoding="utf-8")
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Call) and (
                getattr(node.func, "attr", None)
                or getattr(node.func, "id", None)) == "RunnerConfig":
            for kw in node.keywords:
                if kw.arg != "routing_max_rungs":
                    continue
                v = kw.value
                # `x if cond else 0` — take the fallback, which is the default path
                if isinstance(v, ast.IfExp):
                    v = v.orelse
                if isinstance(v, ast.Constant) and isinstance(v.value, int):
                    return v.value
    return int(getattr(RunnerConfig, "routing_max_rungs", 2) or 2)


def _launcher_seat_models() -> str:
    """What `--seat-models` the simulated runner DEFAULTS to: "uniform" or "ladder".

    THIS IS THE SECOND CAUSE OF THE INERT LADDER, and reading `DEFAULT_LADDER`
    directly cannot see it. `run_simulated_experiment.py:697` consults the ladder
    ONLY when `--seat-models ladder` is passed, and the flag defaults to "uniform",
    which maps every seat to a single model. The project record names this as cause
    2 of 2: "the ORDER was right but every seat was answered by the SAME model, so
    0 of 6 source seats got a climb between 2 different models". The ladder ran,
    logged rungs, could record "ladder exhausted", and rehearsed nothing.

    The first version of this check read the ladder mapping and passed, which is the
    SAME error it caught once already one level up: measuring a configuration other
    than the one about to run.
    """
    import ast
    src = (REPO / "bench" / "tools" / "run_simulated_experiment.py").read_text(
        encoding="utf-8")
    for node in ast.walk(ast.parse(src)):
        if not (isinstance(node, ast.Call)
                and getattr(node.func, "attr", None) == "add_argument"):
            continue
        flags = [a.value for a in node.args
                 if isinstance(a, ast.Constant) and isinstance(a.value, str)]
        if "--seat-models" not in flags:
            continue
        for kw in node.keywords:
            if kw.arg == "default" and isinstance(kw.value, ast.Constant):
                return str(kw.value.value)
    return "unknown"


def check_facilities_armed():
    """Which named facilities the simulated runner actually sets."""
    import ast
    src = (REPO / "bench" / "tools" / "run_simulated_experiment.py").read_text(
        encoding="utf-8")
    want = ("burst_mode", "immune_memory_enabled", "hardened_gate_enabled",
            "apply_fixes_back_enabled", "routing_enabled", "falsifier_gate_enabled",
            "sk_enabled", "routing_max_rungs")
    seen = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Call) and (
                getattr(node.func, "attr", None)
                or getattr(node.func, "id", None)) == "RunnerConfig":
            for kw in node.keywords:
                if kw.arg in want:
                    seen.add(kw.arg)
    missing = [w for w in want if w not in seen]
    if missing:
        return FAIL, (f"{len(missing)} facility/-ies left at default, so the run's "
                      f"configuration is partly unknown: {missing}"), []
    budget = _launcher_rung_budget()
    return PASS, f"all {len(want)} named facilities set explicitly", [
        f"routing_max_rungs = {budget}" + (" (exhaust the ladder)" if budget == 0
                                           else " rung(s)")]


def check_severity_test_is_present():
    """Does a PROVEN sub-critical stop blocking, and an UNPROVEN one keep blocking?"""
    from bench.reference_runner_v3 import FindingRegistry
    base = {"canonical_id": "C1", "status": "UNCONFIRMED", "severity": 0.45,
            "verified": False, "verdicts": [], "description": "p",
            "source_model": "SIM", "proposed_fix": "", "open_since_round": 0,
            "last_status_change_round": 0, "computed_evidence": [],
            "routing_history": [], "falsifier_code": "", "falsifier_verdict": ""}
    r1 = FindingRegistry(); r1.entries = {"C1": dict(base)}
    unproven = r1.unverified_critical_count()
    r2 = FindingRegistry()
    proven_e = dict(base)
    proven_e["severity_proof"] = {"status": "PASS", "model_rk": 0.31,
                                  "recomputed_rk": 0.31}
    r2.entries = {"C1": proven_e}
    proven = r2.unverified_critical_count()
    if unproven == 1 and proven == 0:
        return PASS, "proven sub-critical clears, unproven still blocks", []
    if unproven == 0:
        return FAIL, ("an UNPROVEN sub-critical does NOT block — a model can open "
                      "the gate by asserting a number"), []
    return FAIL, (f"the severity test is absent or inert "
                  f"(unproven={unproven}, proven={proven})"), []


def check_in_round_clearance_is_monotone():
    """Can the in-round clearance ever RAISE the blocker count?"""
    from bench.reference_runner_v3 import FindingRegistry
    base = {"canonical_id": "C1", "status": "UNCONFIRMED", "severity": 0.95,
            "verified": False, "verdicts": [], "description": "p",
            "source_model": "SIM", "proposed_fix": "", "open_since_round": 0,
            "last_status_change_round": 0, "computed_evidence": [],
            "routing_history": [], "falsifier_code": "", "falsifier_verdict": ""}
    rises = []
    for new_status, new_ver in (("CONFIRMED", True), ("REFUTED", False)):
        r = FindingRegistry(); r.entries = {"C1": dict(base)}
        before = r.unverified_critical_count()
        r.entries["C1"]["status"] = new_status
        r.entries["C1"]["verified"] = new_ver
        if r.unverified_critical_count() > before:
            rises.append(new_status)
    if rises:
        return FAIL, (f"{len(rises)} clearance transition(s) RAISE the blocker "
                      f"count: {rises}"), []
    return PASS, "no clearance transition raises the blocker count", []


def check_blockers_are_not_labelled_settled():
    """Is any status both counted as an A4 blocker and printed under SETTLED?"""
    from bench.reference_runner_v3 import FindingRegistry, FINDING_STATUS_VOCABULARY
    bad = []
    for st in sorted(FINDING_STATUS_VOCABULARY):
        reg = FindingRegistry()
        reg.entries = {"C0001": {
            "canonical_id": "C0001", "status": st, "severity": 0.45,
            "verified": False, "verdicts": [], "description": "probe",
            "source_model": "SIM", "proposed_fix": "", "open_since_round": 0,
            "last_status_change_round": 0, "computed_evidence": [],
            "routing_history": [], "falsifier_code": "", "falsifier_verdict": ""}}
        try:
            n = reg.unverified_critical_count()
            text = reg.build_summary(3)
        except Exception:
            continue
        if n < 1 or "--- SETTLED" not in text:
            continue
        block = text.split("--- SETTLED", 1)[1].split("\n---", 1)[0]
        if "C0001" in block:
            bad.append(st)
    if bad:
        return FAIL, (f"{len(bad)} blocking status(es) printed as SETTLED: {bad} — "
                      f"the panel is told not to challenge what holds the run open"), []
    return PASS, "no blocking status is printed as SETTLED", []


def check_capability_ladder_climbs(seats, expect_uniform=False, seat_models=None):
    """Does climbing the ladder reach more than 1 distinct model, AS THE RUN WILL?"""
    from bench.routing import rank_falsifier_writers
    from bench.tools import sim_dispatch_shim as SHIM
    # THE BUDGET MUST COME FROM WHAT THE RUN WILL USE, NOT THE DATACLASS DEFAULT.
    # The first version of this check read `RunnerConfig.routing_max_rungs` and
    # reported the ladder INERT while the launcher had already been set to exhaust.
    # A preflight check that measures a different configuration from the one about
    # to run is worse than none — it is the "armed in config, inert in fact" error
    # it exists to catch, committed by the catcher.
    budget = _launcher_rung_budget()
    # THE RESOLVED VALUE WINS OVER THE DECLARED DEFAULT. Reading only the default
    # would re-commit, in this check's own wiring, the error it exists to catch:
    # a caller passing `--seat-models ladder` would still be told the ladder is
    # uniform, and the boot would halt on a configuration nobody was going to run.
    seat_models = seat_models or _launcher_seat_models()
    mixed = 0
    notes = [f"launcher --seat-models default: {seat_models}",
             f"launcher routing_max_rungs: {budget}"]
    for src in seats:
        rungs = rank_falsifier_writers(seats, exclude=(src,))
        eff = rungs if not budget else rungs[:budget]
        models = [SHIM.DEFAULT_LADDER.get(r, "opus") for r in eff]
        mixed += len(set(models)) > 1
        notes.append(f"{src} -> {models}")
    if len(seats) < 2:
        # A 1-seat roster legitimately has no rung to climb to. Informational,
        # not a failure: exp56's single-seat arm is a pre-registered condition.
        return PASS, ("1-seat roster: there is no rung above the source, so the "
                      "ladder is empty by construction, not inert"), notes
    if seat_models != "ladder":
        # THE MAPPING BEING MIXED IS NOT THE SAME AS THE RUN USING IT.
        if expect_uniform:
            return PASS, (f"ladder uniform BY REQUEST (--seat-models "
                          f"{seat_models}): a deliberate control arm"), notes
        return FAIL, (f"the ladder cannot climb: the launcher defaults to "
                      f"--seat-models {seat_models}, which answers every seat with "
                      f"1 model, so 0 of {len(seats)} seats get a cross-model "
                      f"climb however many rungs are budgeted"), notes
    if mixed < len(seats):
        return FAIL, (f"only {mixed} of {len(seats)} seats get a climb between 2 "
                      f"different models — the ladder is inert for "
                      f"{len(seats) - mixed} of them"), notes
    return PASS, f"all {mixed} of {len(seats)} seats get a mixed climb", notes


#: (name, fn, wants_seats). ORDER IS LOAD-BEARING — see the module docstring and
#: `post_semantics_2026-10-06.py` part 2, which holds it with z3.
CHECKS = [
    ("facilities armed explicitly", check_facilities_armed, False),
    ("severity test present", check_severity_test_is_present, False),
    ("clearance is monotone", check_in_round_clearance_is_monotone, False),
    ("blockers not labelled SETTLED", check_blockers_are_not_labelled_settled, False),
    ("capability ladder climbs", check_capability_ladder_climbs, True),
]


def _print_notes(notes, indent: str, cap: int = 6) -> None:
    """Print at most `cap` note lines AND say how many were withheld.

    A LISTING THAT TRUNCATES IN SILENCE IS A LISTING THAT LIES BY OMISSION, and on
    a POST screen it is worse than elsewhere: the withheld lines are the per-seat
    detail an operator uses to decide whether a FAIL is the one they expected. The
    first version printed `notes[:6]` and said nothing about the rest.
    """
    notes = list(notes or [])
    for n in notes[:cap]:
        print(f"{indent}{n}")
    withheld = len(notes) - cap
    if withheld > 0:
        print(f"{indent}... and {withheld} more line(s) not shown "
              f"(of {len(notes)} total)")


def _row(name: str, status: str) -> str:
    dots = "." * max(3, _WIDTH - len(name) - len(status) - 2)
    return f"  {name} {dots} {status}"


def run_checks(seats, run_all=False, expect_uniform=False, seat_models=None):
    """Execute the checks in order. Returns the list of (name, status, headline, notes).

    Halts after the first FAIL unless `run_all`. Rows never reached are NOT_RUN,
    which is an absence of a verdict rather than a pass.
    """
    rows = []
    halted = False
    for name, fn, wants_seats in CHECKS:
        if halted:
            rows.append((name, NOT_RUN, "", []))
            continue
        try:
            status, headline, notes = (
                fn(seats, expect_uniform=expect_uniform,
                   seat_models=seat_models) if wants_seats else fn())
        except Exception as exc:  # noqa: BLE001
            # A CHECK THAT RAISES IS A FAIL. The previous version mapped this to a
            # 3rd state that did not set the exit code, so a broken check booted.
            status = FAIL
            headline = f"the check itself raised {type(exc).__name__}: {exc}"
            notes = traceback.format_exc().strip().split("\n")[-3:]
        rows.append((name, status, headline, notes))
        if status == FAIL and not run_all:
            halted = True
    return rows


def main(argv=None) -> int:
    args = _parse_args(argv)
    seats = [s.strip() for s in args.seats.split(",") if s.strip()]

    print("CDSFL POST — Constraint Engineering preflight")
    print(f"Rev 2026-10-06    roster: {len(seats)} seat(s)    "
          f"{'diagnostic (--all)' if args.run_all else 'halt at first failure'}")
    print()

    rows = run_checks(seats, run_all=args.run_all,
                      expect_uniform=args.expect_uniform,
                      seat_models=args.seat_models)

    failed = []
    for i, (name, status, headline, notes) in enumerate(rows, start=1):
        print(_row(name, status))
        if status == FAIL:
            failed.append((i, name, headline))
            print(f"      {headline}")
            _print_notes(notes, "        ")
            print()
        elif status == PASS and notes:
            _print_notes(notes, "      ")

    print()
    n_total = len(rows)
    n_pass = sum(1 for r in rows if r[1] == PASS)
    if not failed:
        print(f"POST complete — {n_pass} of {n_total} checks passed. System ready.")
        return 0

    if args.run_all:
        print(f"*** POST FAILED — {len(failed)} of {n_total} checks failed. ***")
        for i, name, _ in failed:
            print(f"    check {i}: {name}")
        print("    Diagnostic mode ran every check. Fix these, then re-run.")
    else:
        i, name, _ = failed[0]
        print(f"*** SYSTEM HALTED — check {i} of {n_total} failed: {name} ***")
        print(f"    {n_pass} check(s) passed before it; "
              f"{sum(1 for r in rows if r[1] == NOT_RUN)} did not run.")
        print("    Investigate the failure above, then re-run.")
        print("    To list every failure in 1 pass instead: --all")
    return 1


if __name__ == "__main__":
    sys.exit(main())
