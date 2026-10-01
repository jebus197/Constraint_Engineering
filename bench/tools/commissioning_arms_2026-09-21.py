#!/usr/bin/env python3
"""The commissioning study's arms, as data, with a caller and a test.

WHY THIS FILE EXISTS, IN THE PROGRAMME'S OWN WORDS.
`CDSFL_Programme_of_Study_2026-09-17.txt` observes that the simulated harness
"accepts no configuration file", that it "builds its own run", and concludes:
"The run this programme describes, 3 arms on the registry engine for 8 rounds,
has no launcher." Its proposed remedy ends: "It needs a caller and a test that
asserts the settings the runner actually received."

This is that caller. The arms are DATA here, so a test can assert on the same
object the launcher uses rather than on a copy of it -- the 2-copies-drift-apart
failure that `execute-do-not-grep` names, and which this project has already
found 4 separate times by running 2 forms against each other.

WHAT IT DOES NOT DO. It does not launch anything by itself and it spends no
money: every seat is a `-SIM` stand-in with `api="sim"`. `--print` emits the
command lines for review; `--run` executes them one at a time through
`run_simulated_experiment_sandboxed.sh`, which is the founder's 2026-09-01
ruling that "a simulation runs in its own sandbox with a copy of the
current/most recent repo to work on, not the live repo itself".

TARGETS. Arms 1, 2, 3 and 5 take the registry engine,
`bench/cdsfl_registry/engine.py`, as the 17 September programme specifies.
Arm 4 takes `bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md`, the candidate that
programme names -- 3,498 bytes with 2 fenced Python listings -- because A19
cannot be commissioned on a Python target: `_gateable_source` returns Python
unchanged, so `sk_score_prose_listings` reports "enabled" while proving nothing.
Verified 2026-09-21 by executing `compute_sk` against that file: 2 listings
extracted, ruff baseline 4, which reproduces the figure A19 records.

THE DOMAIN STAYS `statistics` AND THAT IS DELIBERATE. `software` is the better
description of a Python target, and `--domain` now exists to say so. It is NOT
used here because arm 5 compares this bundle against a pre-window run that used
`statistics`, and changing the briefing would confound the one arm whose whole
purpose is that comparison.

WHAT THIS RUN CANNOT CONCLUDE, STATED UP FRONT. No canary catalogue is
available, so no ground-truth defects are seeded. A CRITICAL_QUIESCENCE
convergence therefore cannot distinguish "the target is genuinely clean" from
"the panel is dead" -- the sandboxed launcher's own note records exactly that
happening on 2026-09-01 with a vacuous curve, zero critical findings across a
whole run. The catalogue is answer-key material and is the founder's in person,
and generating one alone is refused by design, because `Canary.generator` is
load-bearing and `detection_rate` will not report on a single-generator
held-out set.
"""

from __future__ import annotations

import argparse
import json
import dataclasses
import datetime as _dt
import shlex
import subprocess
import sys
from pathlib import Path


def _utc_date() -> str:
    """UTC date stamp for the default log directory.

    UTC and not local time, so a run launched either side of midnight BST cannot
    land in 2 different directories within one session.
    """
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d")

REPO = Path(__file__).resolve().parents[2]
SANDBOXED = "bench/tools/run_simulated_experiment_sandboxed.sh"

#: The registry engine, as the 17 September programme names it.
ENGINE = "bench/cdsfl_registry/engine.py"

#: The prose target for arm 4. Named by that programme as the candidate, and
#: confirmed by execution to carry 2 fenced Python listings.
PROSE = "bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md"

#: e2_regression runs this. Chosen to EXERCISE THE TARGET: 40 tests over the
#: registry engine, 0.19 s. The runner's default test command is the immune
#: memory suite, which is tied to `bench/dm/_memory.py` and would have measured
#: regressions in a module these arms never touch.
ENGINE_TESTS = "python3 -m pytest bench/tests/test_policy_engine.py -q"


@dataclasses.dataclass(frozen=True)
class Arm:
    key: str
    name: str
    seats: str
    target: str
    purpose: str
    #: `None` means the gate is unavailable by construction. It is EMITTED as an
    #: empty `--test-cmd`, never omitted -- see `argv`.
    test_cmd: str | None = ENGINE_TESTS
    #: RAISED 8 -> 10 on the founder's ruling of 2026-09-30, and it is a BUDGET
    #: CAP rather than a derived optimum. Both free panel seats recommended 10;
    #: both then established that `n*` cannot justify it, because the coefficient
    #: pair (4.89, 0.709) reproduces from no archived fit (0 of 421 curves swept
    #: by one seat, 379 by the other) and 2 incompatible quantities in this
    #: codebase are both named `gamma`. His ruling: "Go with 10 -- with a
    #: recommendation to the reviewer to set a higher cap if convergence appears
    #: within direct reach." That recommendation is `cap_recommendation` below.
    rounds: int = 10

    def argv(self) -> list[str]:
        """Always emit `--test-cmd`; an empty value means EXPLICITLY DISABLED.

        THE DEFECT THIS REPLACES, measured 2026-09-30. This read
        `if self.test_cmd:`, a TRUTHINESS test, so `None` emitted no flag at all
        and `run_simulated_experiment`'s argparse substituted its own default --
        the immune-memory suite for `bench/dm/_memory.py`, unrelated to a prose
        target. The gate then ran against the wrong artefact and returned the
        constant 52/55 = 0.9454545454545454 for every scored fix, identical on a
        document whose bytes had been destroyed. A falsy guard cannot express 3
        states: `None` (disabled), `''` and *unset* were indistinguishable, so the
        most explicit signal was the one discarded.

        VERIFIED BY EXECUTION before adopting: `_run_effect_regression` returns
        `(None, "no test command configured")` for BOTH `None` and `''`, and the
        launcher's argparse preserves `''` as distinct from its default. So an
        empty value reaches the runner as a genuine absence rather than as a
        command. Both free panel seats reached this fix independently; this is the
        fable seat's version, which the founder chose, because it makes the intent
        explicit where the setting is declared.
        """
        a = ["--target", self.target, "--seats", self.seats,
             "--rounds", str(self.rounds), "--name", self.name]
        a += ["--test-cmd", self.test_cmd if self.test_cmd is not None else ""]
        return a


#: Arm 5 is NOT here. It requires running the harness as it stood at `a2a0197`
#: (2026-09-06, pre-window) against the same target and seed, which is a
#: checkout of a different commit rather than a flag on this one. Listing it
#: with the others would imply this launcher can produce it, and it cannot.
ARMS = [
    Arm("arm1", "commissioning_arm1_panel",
        "CC2,Codex,Gemini,DeepSeek,ChatGPT", ENGINE,
        "the repairs in a panel shape; 5 seats, as the 17 September programme lists them"),
    Arm("arm2", "commissioning_arm2_single",
        "CC2", ENGINE,
        "the repairs in a single-seat shape"),
    Arm("arm3", "commissioning_arm3_contrast",
        "Codex,ChatGPT", ENGINE,
        "seat contrast; WEAK BY CONSTRUCTION in simulation, both seats being the "
        "same stand-in model under different labels, and reported as weak"),
    Arm("arm4", "commissioning_arm4_prose",
        "CC2,Codex,Gemini,DeepSeek,ChatGPT", PROSE,
        "commissions A19; e2_regression is UNAVAILABLE on prose by construction, "
        "so an EMPTY test command is passed and the gate is genuinely excluded. "
        "Before 2026-09-30 no flag was passed at all and argparse substituted the "
        "immune-memory suite, which faked the gate rather than excluding it",
        test_cmd=None),
]


#: How close to the gate still counts as "within direct reach", as a fraction of
#: the configured threshold. 0.9 makes a gamma_critical of 0.27 against a 0.30
#: threshold reach-worthy and 0.26 not. It is a REVIEWER PROMPT, never a gate: no
#: verdict, score or convergence decision reads this value.
REACH_FRACTION = 0.9


def cap_recommendation(report: dict) -> str | None:
    """A prompt to the reviewer to raise the cap when convergence was in reach.

    THE FOUNDER'S RULING, 2026-09-30: *"Go with 10 -- with a recommendation to the
    reviewer to set a higher cap if convergence appears within direct reach."*

    THE CASE IT EXISTS FOR, measured from the run that prompted the ruling.
    `commissioning_arm1_panel_20260929T214647Z` used all 8 of its 8 rounds and
    stopped with `gamma_critical` at **0.29** against a configured
    `gamma_alt_threshold` of **0.30** -- short by 0.01 -- while carrying 3
    unverified criticals, which is the A4 fail-safe refusing to accrue the
    zero-critical streak. Its novelty was also still RISING, at 9 new findings in
    the final round. That run had not converged and had not failed; it ran out of
    budget 1 round from the gate, and nothing in the artefact said so.

    2 SIGNALS, either sufficient, both read from the report rather than inferred:
      * the final `gamma_critical` is at or above `REACH_FRACTION` of the
        configured `gamma_alt_threshold`; or
      * `gamma_critical` has already MET the threshold while `unverified_critical`
        is non-zero -- the gate satisfied and held open by the fail-safe alone.

    Returns None when the cap was not reached, so a run that converged early is
    never told to buy rounds it did not need.

    THIS DECIDES NOTHING. It prints. `feedback_fixes_hil_only` -- the reviewer
    raises the cap or does not.
    """
    rounds = report.get("rounds") or []
    cap = report.get("max_rounds")
    if not rounds or not isinstance(cap, int) or len(rounds) < cap:
        return None
    cfg = report.get("convergence_config") or {}
    threshold = cfg.get("gamma_alt_threshold")
    if not isinstance(threshold, (int, float)) or threshold <= 0:
        return None
    last = rounds[-1]
    gc = last.get("gamma_critical")
    if not isinstance(gc, (int, float)):
        return None
    unverified = last.get("unverified_critical") or 0
    novel = last.get("novel_this_round")

    met_and_held = gc >= threshold and unverified
    near = gc >= threshold * REACH_FRACTION
    if not (met_and_held or near):
        return None

    why = ("the gate was SATISFIED and held open only by the A4 fail-safe over "
           f"{unverified} unverified critical(s)" if met_and_held else
           f"gamma_critical reached {gc} against a threshold of {threshold}, "
           f"short by {round(threshold - gc, 6)}")
    tail = (f" Novelty was still {novel} in the final round, so the run was "
            f"producing when the budget ended." if isinstance(novel, int) and novel else "")
    return (f"RECOMMENDATION TO THE REVIEWER: raise the round cap and re-run. "
            f"This arm used all {cap} of its {cap} rounds and {why}.{tail} "
            f"The cap is a budget backstop, not a convergence verdict, so a run "
            f"that stops here is carrying falsification debt rather than a "
            f"result.\n{suggested_cap_sentence(report)}")


#: The consecutive zero-new-critical window the two-sided gate requires, when a
#: report does not carry its own. Matches `RunnerConfig.gamma_alt_consecutive_zero_crit`.
DEFAULT_ZERO_WINDOW = 3


def suggested_cap(report: dict) -> "tuple[int, int] | None":
    """(suggested cap, extra rounds) -- a FLOOR, not an estimate of n*.

    THE FOUNDER'S RULING, 2026-09-30, is 2 sentences and the first version of
    this module implemented only the first: *"we go with what you previously
    suggested was the statistical average of 10, with the caveat that if an
    experiment looks close to convergence, a recommendation should be printed to
    the researcher to extend the run to a sane suggested number, or to set their
    own user preference in the runner dialogue."* The recommendation fired and
    named NO NUMBER, so the reviewer was told to raise the cap and left to guess
    by how much.

    WHY THE NUMBER IS DERIVED FROM THE GATE AND NOT FITTED. Both free seats, and
    separately an unbounded external model, reached the same conclusion about
    predicting the required round count from target complexity: it is NOT
    estimable on this archive. Measured over the 9 archived reports carrying
    `target_complexity`: 2 distinct targets, 3 distinct complexity values, and
    only 4 of 9 runs using their full budget -- so the recorded round counts are
    configured CAPS rather than measurements of what a target needed. Fitting
    n*(complexity) on that would manufacture a precise-looking rule with no
    predictive content.

    AND THERE IS A SECOND, STRONGER REASON, raised by an external model (Grok)
    reviewing the same question and recorded here because it is structural
    rather than a fact about this archive, so no amount of further data would
    answer it: COMPLEXITY IS NOT STATIONARY. After round 0 the thing that
    determines how many rounds remain is no longer the original document. It is
    the document PLUS the fixes applied, the challenges still open, and the
    examination history -- so a cap fitted to pre-round complexity is predicting
    a quantity from a state that no longer exists by the time it matters. The
    panel's own conclusion (not estimable on this archive) and Grok's (not the
    right variable at all) point the same way, and Grok's survives a larger
    archive while the panel's would not. Its matching recommendation -- "always
    record which reason fired" -- was checked and WAS a real gap, now closed:
    `reference_runner_v3.stop_reason_fields` puts the stop reason in the report.

    SO THIS ANSWERS A DIFFERENT AND ANSWERABLE QUESTION: what is the SMALLEST
    cap that could satisfy the gate from where the run stopped? The two-sided
    gate's second half requires `gamma_alt_consecutive_zero_crit` consecutive
    rounds with no new critical. A run that ended while still producing
    criticals has accrued none of that streak, so it needs AT LEAST that many
    further rounds, whatever the target's complexity. That is a floor derived
    from the gate's own definition, it is honest about being a floor, and it is
    the only number here that does not require a model of the target.

    Returns None where the report does not carry what this needs, so the caller
    says nothing rather than guessing.
    """
    cap = report.get("max_rounds")
    if not isinstance(cap, int) or cap <= 0:
        return None
    cfg = report.get("convergence_config") or {}
    window = cfg.get("gamma_alt_consecutive_zero_crit")
    if not isinstance(window, int) or window <= 0:
        window = DEFAULT_ZERO_WINDOW
    return cap + window, window


def suggested_cap_sentence(report: dict) -> str:
    """The reviewer-facing sentence naming the number, and its own limits."""
    got = suggested_cap(report)
    if got is None:
        return ("  NO CAP SUGGESTED: this report does not carry `max_rounds`, "
                "so any number would be invented.")
    value, window = got
    cap = report.get("max_rounds")
    return (
        f"  SUGGESTED CAP: {value} rounds, which is this run's {cap} plus the "
        f"{window} consecutive zero-new-critical rounds the two-sided gate "
        f"requires. It is a FLOOR, not a prediction: a run still producing "
        f"criticals has accrued none of that streak, so it cannot satisfy the "
        f"gate in fewer than {window} further rounds whatever the target's "
        f"complexity. Predicting the round count a target actually needs is "
        f"NOT estimable on the current archive -- 2 distinct targets and 3 "
        f"distinct complexity values across 9 reports -- so no larger number "
        f"is offered here.\n"
        f"  OR SET YOUR OWN: pass --rounds N to this tool, or answer the "
        f"runner's cap prompt, and your value is used unchanged."
    )


def command(arm: Arm) -> list[str]:
    return ["bash", SANDBOXED, *arm.argv()]


def detach(child_argv: list[str], log_path: Path) -> int:
    """Start `child_argv` so it OUTLIVES this process, and return its pid.

    WHY THIS EXISTS, AND IT IS THE ROOT CAUSE OF A LOST RUN. The founder's
    standing detached-launch directive (2026-07-29) requires every experiment
    runner to survive the Claude Code host, "logs are the only tether".
    `bench/detached_launch.sh` implements that -- for `bench/launch_exp42.py`
    ONLY, whose config path and flags it hardcodes. The SIMULATED path goes
    through `run_simulated_experiment_sandboxed.sh` instead, and nothing detached
    it: `--run` called `subprocess.call`, which blocks and dies with its parent.

    Measured consequence, 2026-09-29: the shakedown's arm 1 reached round 5 of 8
    and died at 18:53:47 when the launching session ended, losing the run. Its 50
    evidence files were harvested, so the round-0-to-4 data survived, but the run
    did not finish and could not be resumed. The directive was in force the whole
    time and had no wrapper for this path.

    `start_new_session=True` is setsid, which is STRONGER than the nohup+disown
    in `detached_launch.sh`: the child leads a new session and process group, so
    it is immune to SIGHUP and to a signal sent to this process's group, and it
    reparents to init when this process exits. stdout and stderr go to the log,
    which is the tether.

    The pidfile is written at `${LOG%.log}.pid` -- the SAME convention
    `detached_launch.sh` uses at its line 11 -- so `bench/tail_until_done.sh`
    monitors a detached simulated run with no argument and no change.
    """
    log_path.parent.mkdir(parents=True, exist_ok=True)
    fh = open(log_path, "ab", buffering=0)
    try:
        proc = subprocess.Popen(
            child_argv, cwd=REPO, stdout=fh, stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL, start_new_session=True,
        )
    finally:
        fh.close()
    pidfile = log_path.with_suffix(".pid")
    pidfile.write_text(f"{proc.pid}\n", encoding="utf-8")
    return proc.pid


def _is_attended(args) -> bool:
    """Is a human at the keyboard AND waiting on this process?

    A prompt in an unattended run is a HANG, and this tool's whole reason for
    existing is detached runs that outlive the host (founder directive
    2026-07-29, "logs are the only tether"). So the dialogue is offered only
    when the process both has a terminal and is not about to detach or merely
    print.
    """
    if getattr(args, "detach", False) or not getattr(args, "run", False):
        return False
    try:
        return sys.stdin.isatty() and sys.stdout.isatty()
    except (AttributeError, ValueError):            # a closed or fake stream
        return False


def resolve_round_cap(flag: "int | None", attended: bool) -> "int | None":
    """The cap to use: the flag, else the researcher's answer, else None.

    None means "change nothing", so the arms keep their own default and this
    function cannot silently alter a run that did not ask it to.

    THE FLAG ALWAYS WINS, including over the prompt, so a scripted or detached
    invocation is never asked and never blocked.
    """
    if flag is not None:
        return flag
    if not attended:
        return None
    default = ARMS[0].rounds
    try:
        answer = input(
            f"Round cap per arm [{default}]: "
            f"(Enter to accept; the cap is a BUDGET BACKSTOP, not a "
            f"convergence verdict) ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return None
    if not answer:
        return None
    try:
        value = int(answer)
    except ValueError:
        print(f"  not a number: {answer!r}; keeping {default}", flush=True)
        return None
    if value < 1:
        print(f"  a cap below 1 would run no rounds; keeping {default}",
              flush=True)
        return None
    return value


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--print", action="store_true",
                    help="emit the command lines and exit (default)")
    ap.add_argument("--run", action="store_true",
                    help="execute the arms sequentially through the sandboxed launcher")
    ap.add_argument("--only", default=None,
                    help="restrict to one arm key, e.g. arm1")
    ap.add_argument("--detach", action="store_true",
                    help="run the arms in a DETACHED session that survives this "
                         "one (founder directive 2026-07-29); implies --run")
    ap.add_argument("--log", default=None,
                    help="log path for --detach; defaults to "
                         "bench/logs/shakedown_<UTC date>/arms.log")
    # THE RESEARCHER'S OWN CAP. Founder's ruling 2026-09-30: a reviewer must be
    # able "to extend the run to a sane suggested number, or to set their own
    # user preference in the runner dialogue". Before this there was no way to
    # set it at all -- the cap was a dataclass default, so `cap_recommendation`
    # told the reviewer to raise a number they had no means of raising.
    ap.add_argument("--rounds", type=int, default=None, metavar="N",
                    help=f"round cap per arm (default {ARMS[0].rounds}); a "
                         f"budget backstop, NOT a convergence verdict. Omit it "
                         f"on an attended run and you are asked.")
    args = ap.parse_args()
    if args.rounds is not None and args.rounds < 1:
        print(f"--rounds must be at least 1, got {args.rounds}", file=sys.stderr)
        return 2

    arms = [a for a in ARMS if args.only in (None, a.key)]
    if not arms:
        print(f"no arm matches {args.only!r}; keys are "
              + ", ".join(a.key for a in ARMS), file=sys.stderr)
        return 2

    chosen = resolve_round_cap(args.rounds, attended=_is_attended(args))
    if chosen is not None:
        arms = [dataclasses.replace(a, rounds=chosen) for a in arms]
        print(f"round cap: {chosen} per arm", flush=True)

    if args.detach:
        # RE-INVOKE THIS FILE WITH --run RATHER THAN COPYING THE SEQUENCING.
        # The arms MUST run one at a time: 4 arms detached in parallel would put
        # 17 simulated seats on the founder's plan at once, which is the overload
        # he reported on 2026-09-29 ("burning through my Max plan allowance by
        # launching too many concurrent instances"). Delegating to --run keeps
        # exactly 1 definition of the order and the concurrency.
        log = Path(args.log) if args.log else (
            REPO / "bench" / "logs"
            / f"shakedown_{_utc_date()}" / "arms.log")
        child = [sys.executable, str(Path(__file__).resolve()), "--run"]
        if args.only:
            child += ["--only", args.only]
        pid = detach(child, log)
        print(f"detached PID {pid} -> {log}")
        print(f"pidfile:  {log.with_suffix('.pid')}")
        print(f"monitor:  bash bench/tail_until_done.sh \"{log}\"")
        print(f"arms:     {', '.join(a.key for a in arms)}")
        return 0

    if not args.run:
        for a in arms:
            print(f"# {a.key}: {a.purpose}")
            # shlex.join, NOT " ".join: --test-cmd carries spaces, and an
            # unquoted printed line would split it into 4 arguments if a
            # reader copied it. Execution was always correct (subprocess
            # takes a list); only the printed form was misleading.
            print(shlex.join(command(a)))
            print()
        return 0

    rc_total = 0
    for a in arms:
        print(f"=== {a.key} — {a.purpose}", flush=True)
        rc = subprocess.call(command(a), cwd=REPO)
        print(f"=== {a.key} exit code {rc}", flush=True)
        # THE FOUNDER'S RAISE-THE-CAP PROMPT, wired here because this is where the
        # reviewer is looking. An unwired recommendation is an addition that does
        # nothing, which is the defect class this session spent the day on.
        for _rep in sorted((REPO / "bench" / "logs").glob(f"{a.name}_*/*_report.json")):
            try:
                _note = cap_recommendation(json.loads(_rep.read_text()))
            except Exception:                                    # noqa: BLE001
                continue
            if _note:
                print(f"=== {a.key} {_note}", flush=True)
            break
        rc_total = rc_total or rc
    return rc_total


if __name__ == "__main__":
    sys.exit(main())
