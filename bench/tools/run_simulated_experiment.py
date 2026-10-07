#!/usr/bin/env python3
"""A REAL experimental run — `run_experiment()` itself — with agents for models.

    LABELS CARRY THE MANDATORY `-SIM` SUFFIX (founder ruling 2026-08-08) AT
    SOURCE. `VENDORS` is already CC2-SIM, DeepSeek-SIM and so on, so the
    ModelConfig labels, cfg.models, every finding ID, the log directory and
    the report all carry it by construction -- there is no relabelling step
    left for anything to drop. Nothing here is an experimental result.


WHY: founder, 2026-08-30 — "test all recent fixes as they unfold and not risk
burning real money, only to discover in the actual runs that things aren't
working as specified. The remaining runway remains short."

TARGET: `bench/dm/_memory.py`, the smallest target in the experimental series
(20,605 bytes, 489 lines, 20 archived findings). Its experiment, exp45, is the
shortest on record — 4 rounds, converged at round 3 by CRITICAL_QUIESCENCE via
the two-sided gate — so there is a clean reference outcome to compare against.
"""
from __future__ import annotations

import argparse
import os
import dataclasses
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone

REPO = pathlib.Path(__file__).resolve().parents[2]
for p in (str(REPO), str(REPO / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)

import reference_runner_v3 as R                       # noqa: E402

#: The dataclass defaults this launcher wants to pass EXPLICITLY, captured at import
#: time rather than read off `R.RunnerConfig` at the call.
#:
#: WHY AT IMPORT. `burst_mode` is passed explicitly so the preflight POST can see the
#: facility as deliberately set rather than silently defaulted. Reading it as
#: `R.RunnerConfig.burst_mode` inside `main()` broke
#: `test_the_simulated_launcher_sets_both_lists`, which runs this launcher in a fresh
#: subprocess with BOTH config constructors REPLACED by interceptors in order to
#: compare the 2 model lists they receive -- so by the time `main()` ran,
#: `R.RunnerConfig` was a function and had no attributes at all
#: ("AttributeError: 'function' object has no attribute 'burst_mode'"). Captured here,
#: the value is read before any caller can intercept the class, and the launcher stops
#: depending on the class still being a class when it builds its config.
_RUNNER_DEFAULT_BURST_MODE = R.RunnerConfig.burst_mode
from bench.tools import sim_dispatch_shim as SHIM     # noqa: E402

#: Named with the mandatory ``-SIM`` suffix AT SOURCE (founder ruling
#: 2026-08-08) so every downstream consumer -- ModelConfig labels,
#: cfg.models, parse_findings, finding IDs, the log directory and the report
#: -- carries it by construction. A relabelling map has somewhere to be
#: dropped; a correct name at source does not.
VENDORS = [f"{v}-SIM" for v in
           ("CC2", "DeepSeek", "ChatGPT", "Gemini", "Codex", "Fable")]


class SeatSelectionError(ValueError):
    """A named seat that is not a seat. Raised before any dispatch is built."""


def resolve_seats(seats_arg: str | None, models_count: int) -> list[str]:
    """The seats to dispatch, as labels, in the order given.

    ``seats_arg`` is a comma-separated list of vendor names with or without the
    ``-SIM`` suffix; ``None`` falls back to the historic prefix behaviour,
    ``VENDORS[:models_count]``, so nothing that does not pass ``--seats``
    changes.

    Order is PRESERVED rather than sorted into `VENDORS` order, because seat 0
    is given the ``player_manager`` role at the call site. ``--seats
    Codex,ChatGPT`` therefore makes Codex-SIM the manager, which is what a
    reader of that command line would expect; sorting would silently hand the
    role to ChatGPT-SIM.

    Duplicates are rejected rather than de-duplicated. A repeated seat would
    make ``len(models)`` disagree with the number of distinct labels, and the
    runner builds 2 lists from this selection that must match -- the config
    comment at the call site records that they must, "or the runner counts a
    different panel than it dispatches".
    """
    if seats_arg is None:
        if models_count < 1 or models_count > len(VENDORS):
            raise SeatSelectionError(
                f"--models must be between 1 and {len(VENDORS)}, got {models_count}"
            )
        return list(VENDORS[:models_count])

    raw = [s.strip() for s in seats_arg.split(",") if s.strip()]
    if not raw:
        raise SeatSelectionError("--seats was given but named no seat")

    by_bare = {v[: -len("-SIM")].lower(): v for v in VENDORS}
    by_full = {v.lower(): v for v in VENDORS}

    chosen: list[str] = []
    for name in raw:
        label = by_full.get(name.lower()) or by_bare.get(name.lower())
        if label is None:
            raise SeatSelectionError(
                f"unknown seat {name!r}; the simulated panel is "
                + ", ".join(v[: -len("-SIM")] for v in VENDORS)
            )
        if label in chosen:
            raise SeatSelectionError(
                f"seat {label} named more than once; a repeated seat would make "
                "the dispatched panel and the counted panel disagree"
            )
        chosen.append(label)
    return chosen


def build_parser() -> argparse.ArgumentParser:
    """The argument surface, separated from main() so a test can EXECUTE it.

    While this lived inside ``main()`` the only way to check that a flag existed
    and reached its config field was to read the source, and a test that reads
    source proves only that the file describes itself consistently. Building the
    parser here lets a test parse real argument lists and assert on the resulting
    namespace, which is the `execute-do-not-grep` form.
    """
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target", default="bench/dm/_memory.py")
    # 7, NOT 4 (2026-08-30). `verification_min_round` is 6, so at 4 rounds the
    # verification stage returned {"skipped": True, "reason": "round N < 6"} in
    # EVERY round of the v3.1 run and `verified` was False on all 19 entries.
    # Raising the harness rather than lowering the runner's threshold keeps the
    # simulation faithful to what Bench Run 2 will actually do.
    # 16, matching the real exp45 (which converged at round 3, so this costs
    # nothing in practice and lets convergence rather than the cap decide).
    # NOTE: `verification_min_round` is 6 and rounds are 0-based, so CC2v will
    # NOT fire on a run that converges at 3 -- and that is FAITHFUL: the real
    # exp45 never fired it either, reaching verified 24/39 through the
    # falsifier path. Recorded so the absence is not read as a defect.
    ap.add_argument("--rounds", type=int, default=16)
    ap.add_argument("--models", type=int, default=6)
    # WHICH seats, not HOW MANY. `--models` is a COUNT and the seats were taken
    # as `VENDORS[:count]`, a PREFIX -- so the only 2-seat panel expressible was
    # CC2-SIM + DeepSeek-SIM, positions 0 and 1.
    #
    # The commissioning study's arm 3 is a SEAT CONTRAST between Codex-SIM and
    # ChatGPT-SIM, positions 4 and 2. No value of `--models` selects them, so
    # that arm could not be launched at all -- not a flag left off, but an arm
    # with no way to ask for it. Arm 2 (single seat, CC2-SIM) happens to work
    # only because CC2-SIM is at position 0.
    #
    # Omitted, this keeps the prefix behaviour exactly, so every existing caller
    # and config is unaffected. Names may be given with or without the `-SIM`
    # suffix; they are normalised TO the suffixed form, because the founder's
    # 2026-08-08 ruling is that the name carries `-SIM` at source rather than
    # through a relabelling map applied later.
    ap.add_argument("--seats", default=None,
                    help="comma-separated seats to dispatch, e.g. 'Codex,ChatGPT'. "
                         "Overrides --models. Default: the first --models seats.")
    # 300s timed out 7 of 20 dispatches (35%, Wilson CI [18.1%, 56.7%]) on a
    # 20KB target, and two of those left a model with three consecutive ITC
    # RAISED 900 -> 3600 ON 2026-09-08, FROM MEASUREMENT.
    #
    # 900 was chosen because it "matches the live CC2 timeout in the real panel",
    # which is a per-seat justification for a parameter whose failures compound
    # per RUN: 6 seats x 16 rounds is 96 dispatches, and losing any one damages a
    # round. Run sim45_memory_20260908T011846Z lost 3 of its 6 seats in round 0 --
    # the BLIND BASELINE -- all three killed at exactly 900s having produced 0
    # characters, while the three that returned took 624s, 768s and 845s. The
    # largest success was 94% of the cap: the ceiling sat inside the distribution
    # rather than above it, and the runner accepted the half-empty round.
    #
    # Measured by `scripts/seat_timeout_budget.py` over 2,221 archived dispatches
    # carrying a duration (median 288s, p95 932s, p99 2068s, max 5194s):
    #
    #   cap     per-seat loss    P(a 6-seat x 16-round run loses NO seat)
    #    900s        5.45%                    0.5%
    #   1800s        1.44%                   24.8%
    #   2400s        0.77%                   47.8%
    #   3600s        0.32%                   73.9%
    #
    # So at 900s a full-strength run was a 1-in-200 event. Raising the cap costs
    # nothing on a healthy round, because a round takes as long as its SLOWEST
    # seat either way; it costs wall-clock only when a seat genuinely hangs, and
    # at 3600s that is expected 0.30 times per run.
    #
    # AN EARLIER VERSION OF THIS COMMENT CITED 3.43%, 0.87% AND 43.2%, FROM A
    # SCAN THAT DID NOT DEDUPLICATE. Some runs write each dispatch under both
    # `r5_gemini_<ts>.json` and `round5_gemini_<ts>.json`, so those runs were
    # counted twice and the fast ones dominated. The committed script dedupes on
    # (run, seat, round, duration). The corrected rates are worse, not better.
    #
    # NOT PROVEN SUFFICIENT for this configuration. 3 of 6 lost is inconsistent
    # with even the corrected archive rate (binomial p = 2.9e-3, scipy.stats
    # binomtest, cross-checked against an exact mpmath tail), so 6 concurrent
    # seats on a 20,698-char target are slower
    # than the archive's mixture. If seats still die at the ceiling the answer is
    # retry-on-timeout, not a bigger number: `ModelConfig.max_retries` exists and
    # `reference_runner_v3.py` reads it nowhere.
    ap.add_argument("--timeout", type=int, default=3600)
    ap.add_argument("--test-cmd", dest="test_cmd",
                    default=("python3 -m pytest bench/tests/test_immune_memory_consumption.py "
                             "bench/tests/test_immune_memory_evaluation.py -q"),
                    help="command S_k runs for its e2_regression gate")
    ap.add_argument("--name", default="sim45_memory")
    # THE STAND-IN MODEL IS NOW SELECTABLE. `--models` is a COUNT, not a name, and
    # there was no way to choose the model at all: it was a Python default in two
    # function signatures and a bare literal in a third file.
    ap.add_argument("--model", default="opus",
                    help="stand-in model for the simulated seats (default: opus)")
    # MIXED-CAPABILITY BENCH (founder ruling 2026-10-05). "ladder" selects
    # SHIM.DEFAULT_LADDER; "uniform" (the default) keeps one model for every
    # seat, which is the behaviour every run before this date had.
    ap.add_argument("--routing-max-rungs", type=int, default=None,
                    help="how many ladder rungs routing may try per unresolved "
                         "critical. Default: the RunnerConfig default (parity with "
                         "the real configs, none of which pins it). Raising it is "
                         "a SIMULATION-ONLY divergence and is recorded as an ask: "
                         "rungs beyond the 2nd are dispatched only when every "
                         "earlier rung has failed, so a deeper budget buys a "
                         "cross-model climb on a small fraction of findings.")
    # CDSFL POST, wired 2026-10-06 on the founder's BIOS analogy. Verbatim: *"on a
    # bios screen when 'booting up' it prints a simple message against each check,
    # which is just 'pass or fail'. If a test passes then the next check fails, the
    # system is halted, giving the user an opportunity to investigate."*
    #
    # It runs AFTER the roster resolves -- so it checks the panel actually being
    # dispatched, not a default -- and BEFORE any dispatch, so a halt costs nothing.
    ap.add_argument("--ignore-post", action="store_true",
                    help="proceed even if the preflight POST halts (the BIOS "
                         "F1-to-continue). The failure is still printed and is "
                         "recorded in the run's console log.")
    ap.add_argument("--expect-uniform-ladder", action="store_true",
                    help="this run deliberately uses --seat-models uniform as a "
                         "control arm, so POST reports the non-climbing ladder as "
                         "PASS instead of halting.")
    # DEFAULT CHANGED uniform -> ladder, 2026-10-07, ON THE FOUNDER'S RULING. His
    # words: "The simulated runs can involve a mix of models from Anthropic ... why
    # should the schema, or capability fingerprints, or the ladder care about model
    # names at all?" Under `uniform` every seat was answered by ONE model, which is
    # cause 2 of 2 in the project record for the inert ladder and was never fixed at
    # the launcher. With `ladder` the 6 seats resolve to 4 distinct models, each
    # probed before it was wired. `uniform` remains available as a deliberate
    # control arm and nothing is removed.
    ap.add_argument("--seat-models", choices=("uniform", "ladder"),
                    default="ladder",
                    help="uniform = one model for all seats (default); "
                         "ladder = the per-seat capability ladder in "
                         "sim_dispatch_shim.DEFAULT_LADDER")
    # SEVERITY CALIBRATION, wired 2026-09-07. Measured the same day: the harness
    # built RunnerConfig with 24 keyword arguments and this was not among them, so
    # it took its default of False and `_apply_severity_calibration` returned 0
    # immediately -- meaning a simulated run exercised NONE of the demotion half of
    # the severity-proof enforcement it exists to study. `latent_tagger_enabled`
    # feeds that same path and was equally absent. Both default ON here.
    #
    # WHAT THIS DOES AND DOES NOT DELIVER (panel, cc2 and fable independently).
    # Enabling both makes the SWEEP execute. It does NOT make a demotion happen,
    # because two further conditions gate it and neither is supplied by a flag:
    #   * `latent` -- true for 1 of 467 falsifier-CONFIRMED criticals in the whole
    #     archive, 0.21%, Wilson [0.04%, 1.20%], so the expected demotion count on
    #     a 10-40 finding target is ~0; and
    #   * `severity_is_proven` -- the 2026-09-06 interlock, requiring a stamped R_k
    #     proof that recomputes, or a HIL `latent_source == "external"`.
    # So the rehearsal exercises the tagger and the sweep, not the demotion. That
    # is stated rather than claimed away: the earlier version of this comment said
    # "a rehearsal that skips the mechanism under test is not a rehearsal", which
    # read as though the change delivered the demotion. It does not.
    #
    # Checked across all shipped bench/exp*_configs/*.json: neither key appears in
    # any of them, so there is no paid config to mirror and default-ON is a
    # deliberate simulation-only divergence, not a parity break.
    ap.add_argument("--no-severity-calibration", action="store_true",
                    help="run WITHOUT the severity-calibration sweep (default: on)")
    # MERGE ARBITRATION HAD NO SWITCH, and the pre-registered arm design needs it
    # off. `merge_arbitration_enabled=True` was a bare literal in the config
    # below, while `CDSFL_Programme_of_Study_2026-09-17.txt` specifies the 3 arms
    # run "with routing, the falsifier gate and the admissibility gate on, and
    # the hardened gate, merge arbitration and immune memory off". Every other
    # item in that sentence was already reachable; this one was not, which is why
    # the same document records that the run it describes "has no launcher".
    #
    # DEFAULT UNCHANGED, DELIBERATELY. Turning it off by default would disable a
    # shipped capability with no measurement showing the run is better without
    # it, which the additive standard forbids in that direction. The flag makes
    # the pre-registered configuration REACHABLE; it does not make it the norm,
    # and which arms use it stays the founder's call.
    ap.add_argument("--no-merge-arbitration", action="store_true",
                    help="run WITHOUT merge arbitration (default: on)")
    # The domain was the bare literal "statistics" regardless of target. It
    # selects the composer's per-domain directives, so a registry-engine or
    # markdown target was being briefed as a statistics problem.
    ap.add_argument("--domain", default="statistics",
                    help="task domain passed to the composer (default: statistics)")
    return ap


#: THE WATCH STARTS WITH THE RUN AND DIES WITH IT. Founder, 2026-10-02:
#: *"The cy monitor should run automatically when a run starts and end when the
#: run ends."*
#:
#: WHY IT LIVES HERE AND NOT IN A LAUNCHER. The watchdog needs 3 things and the
#: runner is the only process that knows all 3 at once: its own pid, the
#: TIMESTAMPED outcome directory it names itself, and a console log that grows.
#: Arming it by hand from outside got the outcome directory wrong on
#: 2026-10-02 (commit 058dfae, "the watchdog looked for the run's verdict in the
#: wrong directory") and again in its twin `_round_count` (cd0b5f3), because the
#: artefacts live in the run's own directory and the console log is wherever the
#: operator happened to redirect it. Spawned from here, all 3 are correct by
#: construction and cannot drift.
#:
#: IT ALSO ENDS ITSELF. `cy_watchdog` exits on PROCESS GONE when this pid dies,
#: so nothing has to remember to stop it -- which is the other half of the
#: founder's sentence.
#:
#: FAIL-OPEN, DELIBERATELY. A monitoring process must never be able to stop an
#: experiment. Every failure path here returns quietly and the run proceeds
#: unwatched, which is worse than watched and far better than halted. Set
#: CDSFL_NO_CY_WATCHDOG=1 to suppress it.
def _start_cy_watchdog(outcome_dir, console_log):
    """Spawn the cy watchdog against THIS run. Returns the Popen or None."""
    if os.environ.get("CDSFL_NO_CY_WATCHDOG", "").strip():
        return None
    script = REPO / "scripts" / "cy_watchdog_2026-10-02.py"
    if not script.is_file():
        return None
    try:
        proc = subprocess.Popen(
            [sys.executable, str(script),
             "--log", str(console_log),
             "--pid", str(os.getpid()),
             "--outcome-dir", str(outcome_dir),
             "--interval", "60", "--stall-seconds", "1200",
             "--heartbeat-minutes", "25", "--max-hours", "12"],
            stdout=open(outcome_dir / "cy_watchdog.log", "w"),
            stderr=subprocess.STDOUT,
            start_new_session=True)
    except (OSError, ValueError):
        return None
    print(f"    cy watchdog armed (pid {proc.pid}) -> "
          f"{outcome_dir.name}/cy_watchdog.log", flush=True)
    return proc


class _Tee:
    """Mirror a stream into a file so the watchdog has a log that grows.

    The sandboxed launcher does not redirect anything -- it runs the runner in
    the foreground and leaves stdout to the operator -- so before this there was
    no console log unless someone made one by hand. The watchdog's stall
    detector reads byte growth, so without a log a stall is undetectable.
    Writes are best-effort: a failed mirror must never break the run's own
    output.
    """

    def __init__(self, stream, path):
        self._stream = stream
        try:
            self._fh = open(path, "a", buffering=1, encoding="utf-8",
                            errors="replace")
        except OSError:
            self._fh = None

    def write(self, data):
        n = self._stream.write(data)
        if self._fh is not None:
            try:
                self._fh.write(data)
            except (OSError, ValueError):
                self._fh = None
        return n

    def flush(self):
        self._stream.flush()
        if self._fh is not None:
            try:
                self._fh.flush()
            except (OSError, ValueError):
                self._fh = None

    def __getattr__(self, name):
        return getattr(self._stream, name)


def _run_post(seats, args) -> int:
    """Run the preflight POST against the roster this run will actually dispatch.

    Imported by path rather than as a module, because `scripts/` is not a package
    and the check is deliberately runnable on its own as the operator's BIOS screen.

    A POST that cannot be LOADED is a failure, not a pass. The previous version of
    the check mapped its own exceptions to a 3rd state that did not set the exit
    code, so a broken check booted; the same trap would be re-set here by swallowing
    an ImportError and continuing.
    """
    import importlib.util
    path = REPO / "scripts" / "preflight_health_check_2026-10-06.py"
    try:
        spec = importlib.util.spec_from_file_location("cdsfl_post", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception as exc:  # noqa: BLE001
        print(f"    POST could not be loaded from {path}: "
              f"{type(exc).__name__}: {exc}", flush=True)
        print("    A health check that cannot run has not passed.", flush=True)
        return 2
    # PASS THE RESOLVED VALUE, never let POST re-derive it. POST falls back to
    # reading this file's declared default, which is wrong the moment a caller
    # overrides it on the command line.
    argv = [f"--seats={','.join(seats)}",
            f"--seat-models={args.seat_models}"]
    if getattr(args, "expect_uniform_ladder", False):
        argv.append("--expect-uniform-ladder")
    return mod.main(argv)


def main() -> int:
    args = build_parser().parse_args()

    if os.path.isabs(args.target):
        # `REPO / <absolute>` lets the absolute path WIN, which would then reach
        # _build_discrimination_overlay and be rejected there. The default is
        # safe; the flag was not (Fable, 2026-08-30).
        print(f"    FATAL: --target must be repo-relative, got {args.target!r}",
              flush=True)
        return 2
    target = REPO / args.target
    if not target.is_file():
        print(f"target not found: {target}", file=sys.stderr)
        return 2

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    logs = REPO / "bench" / "logs" / f"{args.name}_{stamp}"
    logs.mkdir(parents=True, exist_ok=True)

    # The console log and the watch, both by construction. See _start_cy_watchdog.
    _console = logs / "console.log"
    sys.stdout = _Tee(sys.stdout, _console)
    sys.stderr = _Tee(sys.stderr, _console)
    _start_cy_watchdog(logs, _console)

    # SEPARATION BY CONSTRUCTION, 2026-08-31.
    #
    # bench/logs/immune_pipeline.log is the ARCHIVAL immune record: 52,162 lines
    # from 2026-04-04 onward, append-only, never edited. Every run resolves that
    # ONE path at immune_agents.py:3393, so before this the simulated panel
    # appended straight into it -- 363 lines across two runs on 2026-08-30. The
    # separation between simulated and real records was then a naming CONVENTION
    # (the -SIM suffix) rather than a property of where the bytes went, and one
    # compliant append was enough to get five months of real history re-labelled
    # simulated by the provenance guard.
    #
    # CDSFL_SHADOW_LOG_DIR is the isolation hook added 2026-07-31 for exactly
    # this shape of problem, when pytest was found dirtying the archive. It
    # existed the whole time; the simulated runner simply never set it.
    os.environ["CDSFL_SHADOW_LOG_DIR"] = str(logs)

    # VERIFY, DO NOT TRUST. immune_agents resolves that variable at IMPORT time,
    # in module-level code guarded by `if not _shadow_log.handlers`, so setting
    # it after the first import of that module is a silent no-op -- the run would
    # look isolated and would not be. Measured 2026-08-31: importing
    # reference_runner_v3 and sim_dispatch_shim leaves immune_agents unloaded, so
    # here is early enough. That is a fact about today's import graph, not a
    # guarantee, and one lazy import promoted to module level would break it
    # without a symptom. So import it HERE, while the variable is set, and read
    # back where the handler actually points.
    import logging as _logging
    import immune_agents as _immune  # noqa: F401  -- imported for its side effect
    handlers = [getattr(h, "baseFilename", "")
                for h in _logging.getLogger("immune.pipeline").handlers]
    if not any(str(logs) in path for path in handlers):
        print("    FATAL: the immune pipeline log is NOT isolated to this run.\n"
              f"      expected under: {logs}\n"
              f"      actually writing to: {handlers or '(no handler configured)'}\n"
              "      Something imported immune_agents before CDSFL_SHADOW_LOG_DIR\n"
              "      was set, so this simulated run would append to the archival\n"
              "      record and mix simulated output into it. Refusing to start.",
              flush=True)
        return 2
    print(f"    immune pipeline log isolated to {logs.name}/", flush=True)

    # Roles mirror the live panel: one player-manager, the rest players. The
    # labels are the VENDOR labels because the runner keys on them; the shim maps
    # each to its SIM- stand-in and the report records both.
    # CORRECTED PATH, 2026-08-30 (found by Fable in panel review). This pointed
    # at bench/cdsfl_core_formal.md, WHICH DOES NOT EXIST -- the real file is
    # bench/directives/universal/cdsfl_core_formal.md. The `if is_file()` guard
    # below then silently passed system_prompt_path=None, the composer raised
    # FileNotFoundError, that was swallowed, and the whole simulated panel ran
    # WITHOUT its core directive for the entire v3.1 run. A guard that turns a
    # wrong path into a quiet None is worse than no guard.
    cdsfl_path = REPO / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
    if not cdsfl_path.is_file():
        print(f"    FATAL: core directive not found at {cdsfl_path}", flush=True)
        print("    A simulated panel briefed without its directive is not a "
              "simulation of this schema.", flush=True)
        return 2
    # Resolved ONCE and reused, so the dispatched panel and the counted panel
    # cannot drift apart. Both were separately written as `VENDORS[:args.models]`
    # before, which is 2 expressions that happened to agree.
    try:
        seats = resolve_seats(args.seats, args.models)
    except SeatSelectionError as exc:
        print(f"    FATAL: {exc}", flush=True)
        return 2


    models = [R.ModelConfig(label=v, model_id="sim", api="sim",
                            role="player_manager" if i == 0 else "player",
                            system_prompt_path=str(cdsfl_path),
                            timeout=args.timeout, max_retries=1)
              for i, v in enumerate(seats)]
    exp_cfg = R.ExperimentConfig(models=models, logs_dir=str(logs),
                                 budget_limit=0.0, cdsfl_system_prompt="")
    cfg = R.RunnerConfig(
        experiment_name=args.name,
        # BOTH lists, or the runner counts a different panel than it dispatches.
        models=list(seats),
        # REPO-RELATIVE, not absolute (CC2, panel review 2026-08-30).
        # `_build_discrimination_overlay` raises
        # "discrimination control: target must be repo-relative" on an absolute
        # path, and `cfg.test_article` reaches it raw. So even with the
        # falsifier supply repaired, the discrimination control could not have
        # fired in ANY simulated run. Verified by forcing both forms:
        # relative -> DISCRIMINATES, absolute -> INDETERMINATE_ERROR.
        test_article=str(args.target),
        # "statistics", matching the REAL exp45 this run is compared against
        # (verified in its report). The composer renders domain-specific
        # directives, so "software" briefed the simulated panel differently
        # from the run it is measured against (Fable, 2026-08-30).
        domain=args.domain,
        max_rounds=args.rounds,
        falsifier_gate_enabled=True,
        routing_enabled=True,
        # THE RUNG BUDGET IS OPT-IN AND DEFAULTS TO PARITY. REVERTED 2026-10-05.
        #
        # This was briefly set to an unconditional 4, to make the simulated
        # capability ladder span more than one model: with the default budget of 2,
        # every source seat's first 2 rungs come from {Codex-SIM, CC2-SIM,
        # ChatGPT-SIM} and a faithful seat map puts all 3 on the same model, so
        # 0 of 6 source seats got a climb between different models.
        #
        # THE cc2 SEAT FALSIFIED THAT REPAIR, and it was right on two counts.
        #
        # 1. PARITY. 0 of 288 config-shaped files pin `routing_max_rungs`; the
        #    dataclass default is 2. Rungs 3 and 4 would be reachable ONLY in
        #    simulation — and the literal sat directly beneath the block headed
        #    "PARITY WITH THE REAL exp45 CONFIG ... Every value below differed, and
        #    each difference let the simulation behave in a way the run it is
        #    compared against structurally could not." It was a new instance of
        #    the class that block exists to remove.
        #
        # 2. THE PROPERTY WAS MEASURED ON A PREFIX THAT IS NOT DISPATCHED.
        #    `resolve_via_routing` stops at the first CONFIRMED. Verified by
        #    execution: a run confirming at rung 1 dispatches ['A'] and nothing
        #    else; only an all-rungs-fail run dispatches 4. So rung 3 executes only
        #    when rungs 1 AND 2 have both failed — the seat priced it at 2.7542%
        #    first-pass and 0.7857% on the residual rates Exp 42 validated.
        #
        #    The seat's own words, and they are fair: CC1 "used exactly this
        #    execution semantics to falsify the fable seat and did not apply it to
        #    its own repair." The 6-of-6 figure counted prefixes, not dispatches.
        #
        # WHAT IS KEPT. The seat derived exhaustively that over all 64 two-model
        # seat maps, 0 reach 6-of-6 mixed at budget 2 and the ceiling is 5 of 6, so
        # a deeper budget IS genuinely required for that property. It is therefore
        # offered rather than imposed: `--routing-max-rungs` records the ask, and
        # the default is the dataclass default, which is parity.
        #
        # The `DeepSeek-SIM -> fable` correction in the seat map STANDS: DeepSeek
        # ranks last in DEFAULT_FALSIFIER_STRENGTH on a measured 28% confirm rate,
        # so the strong model was the unfaithful assignment.
        # EXHAUST THE LADDER IN SIMULATION. Founder ruling 2026-10-06: *"I don't
        # think there should be a cap at all ... the problem should run until it is
        # either resolved, or the ladder is exhausted. (No more models to try.)"*
        #
        # 0 means exhaust. It is set HERE and not in the dataclass default, which
        # stays at 2, because that default governs the 49 real configs — none of
        # which pins the value — and his own methodology is that the simulated runs
        # exist "so that functionality can be exercised cheaply before money is
        # spent on the full paid panel". So the behaviour he ruled is measured here
        # first and promoted on evidence.
        #
        # The cost is bounded by the thing that made the old cap nearly free:
        # `resolve_via_routing` stops at the first CONFIRMED, so a deeper budget
        # spends a dispatch only on a finding every earlier rung already failed.
        # Verified by execution: with 5 rungs and a rung-1 CONFIRMED, exhaustion
        # dispatches exactly 1.
        routing_max_rungs=(args.routing_max_rungs
                           if args.routing_max_rungs is not None
                           else 0),
        sk_enabled=True,
        location_keyed_convergence=True,
        # PARITY WITH THE REAL exp45 CONFIG (bench/exp45_configs/
        # 45_memory_statistics_live.json), measured by CC2 in second-pass
        # review 2026-08-30. Every value below differed, and each difference
        # let the simulation behave in a way the run it is compared against
        # structurally could not:
        #   earliest_stop_round   default 12 > max_rounds, so the STATE GATE
        #                         returned "too early" every round and only ONE
        #                         of the two convergence gates was ever exercised
        #   stall_gamma_*         exp45 pins both at 1.01, ABOVE the gamma
        #                         ceiling, so its stall detector can never fire
        #                         via gamma; the sim left them live at
        #                         0.45/0.30 and could halt on a path the real
        #                         run cannot reach
        #   merge_arbitration     exp45 True, default False -- a second seam
        #                         path (_arb_dispatch) was permanently dark
        pattern="four_layer",
        consecutive_rounds_required=3,
        max_contested_rounds=3,
        # ── FOUNDER RULINGS, 2026-10-06. FOUR FACILITIES TURNED ON. ──────────
        #
        # BURST / ITC. His words: *"It shouldn't be off as far as I am concerned.
        # The ITC machinery is one of the more effective methods of finding and
        # resolving problems we uncovered."* It was set to "off" here against a
        # dataclass default of "auto", under the 2026-08-30 parity work, and the
        # reason was never restated in terms of what it cost. Burst is driven by
        # the capability fingerprints, so switching it off also switched off one of
        # the mixed-capability facilities the simulated runs exist to rehearse.
        # Returned to the default rather than pinned, so parity is the behaviour.
        burst_mode=_RUNNER_DEFAULT_BURST_MODE,
        # IMMUNE MEMORY. *"Then this also should be fixed going forward."* Armed in
        # 13 of 49 real configs and never once in simulation. The RECORDING half is
        # what goes on here. `immune_memory_consume_rk0` stays off for the reason
        # already on the record: the memory is a single persistent file, so
        # consumption couples runs and would destroy the 2x2 factorial's
        # independence. That reasoning never covered recording.
        immune_memory_enabled=True,
        # HARDENED GATE. *"Then this should also be on, by default in all our
        # runners."* Armed in 4 of 49 real configs, absent from this runner, and
        # mentioned nowhere in it.
        hardened_gate_enabled=True,
        # FOLD FIXES FORWARD. *"I already ruled on this in another context in the
        # live runners. Fold fixes forward is a useful facility, so we don't lose
        # fixes suggested by the models, providing it never touches the live tree
        # and we can still review those fixes (and change and revert them as
        # needed) in the subsequent simulated and real experimental runners."*
        #
        # THE LIVE-TREE CONDITION IS SATISFIED BY CONSTRUCTION, NOT BY PROMISE, and
        # that is checked rather than asserted: `apply_fixes_back` writes to the
        # run's own sandbox copy of the target, never to the repository working
        # tree, and `bench/tests/test_fold_fixes_forward_never_touches_the_live_tree_2026-10-06.py`
        # holds it by executing a round and comparing the tracked tree before and
        # after.
        apply_fixes_back_enabled=True,
        gamma_telemetry_only_until=20,
        stall_gamma_terminate=1.01,
        stall_gamma_advisory=1.01,
        earliest_stop_round=3,
        merge_arbitration_enabled=not args.no_merge_arbitration,
        # DELIBERATE SIMULATION-ONLY DIVERGENCES, so that machinery the real
        # exp45 never reaches is still stress-tested. Each is stated rather
        # than silently inherited:
        #
        #  verification_min_round  exp45 uses 6 and rounds are 0-based, so a run
        #                          converging at 3 NEVER fires the verification
        #                          stage -- true of the real exp45 too. Lowered
        #                          here so the stage is exercised at all.
        #  post_convergence_sweep  0 in the earlier sim, which left one of the
        #                          dispatch paths permanently dark.
        #  discrimination_control_ask  wired 2026-08-30 and enabled here: the
        #                          main panel has NEVER been asked for a
        #                          corrected copy, which is why the control has
        #                          0 of 58 entries carrying both its inputs.
        verification_min_round=2,
        post_convergence_sweep_rounds=1,
        # RE-ARMED (founder ruling 2026-08-30, decision 2 option A).
        #
        # It was disarmed for exactly one reason: the DISC_FAILED branch ran
        # registry.resolve(cid, "UNCONFIRMED", ...) UNCONDITIONALLY, so supplying
        # the control its missing input would have let it reverse sound verdicts
        # about half the time it fired (126 of 246 archived fixes do not silence
        # their own falsifier -- 51.2%, Wilson [45.0%, 57.4%]).
        #
        # That reversal is now behind discrimination_control_blocks, which
        # defaults False. The control can therefore RUN and RECORD -- which it
        # has never once done in this project's life, for want of a corrected
        # copy -- without being able to silently un-confirm anything. That is the
        # whole point of the ruling, so the ask goes back on.
        discrimination_control_ask=True,
        extension_cap=args.rounds,
        # Set so S_k's e2_regression is a reading rather than a null. Measured
        # 2026-08-30: e2_regression was None on all 19 entries because no test
        # command was configured, so one of S_k's gates never contributed.
        test_cmd=args.test_cmd,
        # Shadow cells observe and log; they never touch the verdict path.
        # `_run_shadow_cells` returns {} unless these sections exist, so the
        # v3.1 run reported "B Cell v2: 0 claims checked" purely because the
        # harness omitted them. Shape copied from
        # bench/exp47_configs/47_divergence_locationkey_live.json.
        #
        # `_ouroboros` is deliberately NOT enabled: it reaches arXiv and
        # Semantic Scholar, and a simulated run should not depend on an external
        # service being up. Stated rather than silently dropped.
        shadow_cell_config={"_macrophage": {"mode": "patrol"}},
        # The half of the overnight severity work a simulated run could not reach.
        severity_calibration_enabled=not args.no_severity_calibration,
        latent_tagger_enabled=not args.no_severity_calibration,
        # ── COMMISSIONED 2026-09-21 ON THE FOUNDER'S INSTRUCTION ───────────
        # He ruled: "enable it all now and test it in the next simulated run
        # and add them all to the programme of study". These 2 are the only
        # members of that set not already armed here -- `discrimination_
        # control_ask`, `severity_calibration_enabled` and `latent_tagger_
        # enabled` were already on, above.
        #
        # hierarchical_novelty_convergence: promotes a measure that has been
        # RECORDED IN SHADOW on every round at no cost since 2026-08-04 to
        # GATING. This genuinely changes what the convergence gate reads, so
        # it is a STUDY VARIABLE rather than a safe default -- which is the
        # point: the founder's position is that a facility whose benefit is
        # unmeasured is what the programme of study is FOR.
        hierarchical_novelty_convergence=True,
        # sk_score_prose_listings: TASK A19, his design point of 2026-09-10 --
        # "it should simply mark a purely prose input as 'inadmissible', while
        # still solving any computationally reducible elements within that
        # prose! This is STEM."
        #
        # ⚠ SET HERE BUT INERT ON THE DEFAULT TARGET, AND THAT IS STATED
        # RATHER THAN LEFT TO BE DISCOVERED. `--target` defaults to
        # `bench/dm/_memory.py`, a PYTHON file, and `_gateable_source` returns
        # python source unchanged, so the flag cannot bite. Verified by
        # execution: .py -> unchanged, .md with a fenced block -> 1 listing
        # extracted. TO COMMISSION A19 THE STUDY MUST RUN A PROSE TARGET
        # CARRYING FENCED CODE. Setting the flag on a .py target would report
        # "enabled" while proving nothing, which is the precise difference
        # between a flag being set and a capability being exercised.
        sk_score_prose_listings=True,
        # fix_efficacy_mode: ask at closure time whether each fix cures the
        # defect its own finding claims. RECORD ONLY -- it changes no decision
        # here. 126 of 246 conclusively probed fixes in the archive do not cure
        # their own falsifier (51.2195%, Wilson [45.0027%, 57.3989%]) and every
        # one closed regardless, so this run is the measurement that decides
        # whether the veto is safe to turn on.
        fix_efficacy_mode="record",
    )

    print(f"=== SIMULATED EXPERIMENT (runner {R.RUNNER_VERSION}) ===", flush=True)
    print(f"    target  {args.target}  ({target.stat().st_size:,} bytes)", flush=True)
    print(f"    panel   {len(models)} agents as {seats}", flush=True)
    print(f"    map     {SHIM.LABEL_MAP}", flush=True)
    print(f"    rounds  max {args.rounds}", flush=True)
    print(f"    logs    {logs}", flush=True)
    print(f"    started {datetime.now().strftime('%H:%M:%S')}", flush=True)

    # PAID-DISPATCH TRIPWIRE (CC2, panel review 2026-08-30, ranked 7th).
    # If the shim ever fails to install, or a path is added that bypasses the
    # seam, this run would dispatch to REAL models and bill for it. The whole
    # point of a simulated run is that it cannot. So the harness refuses at the
    # transport layer rather than trusting the seam.
    import socket as _sock
    from live_dispatch_policy import PAID_HOSTS as _PAID   # ONE canonical copy
    _orig_gai = _sock.getaddrinfo

    def _no_paid(host, port, *a, **kw):
        h = str(host).lower().rstrip(".")
        if any(h == d or h.endswith("." + d) for d in _PAID):
            raise RuntimeError(
                f"SIMULATED RUN ATTEMPTED A PAID DISPATCH to {h}. The seam has "
                f"a hole. Refusing rather than billing.")
        return _orig_gai(host, port, *a, **kw)

    _sock.getaddrinfo = _no_paid
    _seat_map = SHIM.DEFAULT_LADDER if args.seat_models == "ladder" else None
    if _seat_map:
        print(f"    seats   MIXED LADDER {_seat_map}", flush=True)
    original = SHIM.install(model=args.model, timeout=args.timeout,
                            seat_models=_seat_map)
    t0 = time.monotonic()
    # SEATS GET A DISPOSABLE WORKTREE, NOT THE LIVE REPO (2026-09-08).
    #
    # MEASURED THE NIGHT THIS WAS WRITTEN. The panel banner read
    # `working directory: (inherited -- repo)`, and `RunnerConfig.panel_cwd`
    # defaults to "" so `set_panel_cwd(cfg.panel_cwd or None)` unset it. The
    # Claude CLI route grants Bash, and BASH IS A SUPERSET OF WRITE, so a seat
    # reviewing `bench/dm/_memory.py` wrote its proposed fix straight into the
    # live working tree -- twice inside 1 minute, at 03:39:50 (22,682 bytes) and
    # 03:40:30 (23,831 bytes), against a committed 20,605.
    #
    # THE COST IS NOT TIDINESS, IT IS THE EXPERIMENT. 3 of the 6 seats reported
    # the target changing under them mid-review, unprompted. Gemini-SIM: "a
    # review of the target file cannot be trusted while the target mutates
    # during it." A finding raised against a file that changes underneath the
    # reviewer yields a falsifier that will not reproduce, which cannot be
    # CONFIRMED, which escalates. That round escalated 9 of 11 findings to HIL.
    #
    # THE RIGHT COMPARATOR IS THIS EXPERIMENT, NOT THE ARCHIVE MEAN. A first pass
    # here cited a pooled 39.35% across 72 archived gate events as "the baseline".
    # The founder rejected it from memory and was right: that pool averages a
    # broken era with a working one. Split by the record's OWN account of each
    # run, the documented-compromised runs (exp55's gate running falsifiers in an
    # empty directory; exp48 and exp49's key exposure) escalate at 65.5% and the
    # rest at 30.4% -- z = 6.49, p = 4.3e-11. The like-for-like figure is the
    # archived exp45 on this same target, the run that converged at R3:
    # 2 of 23, 8.7%, Wilson [2.4%, 26.8%]. Tonight: 9 of 11, 81.8%, Wilson
    # [52.3%, 94.9%] -- non-overlapping, Fisher exact p = 4.95e-5, odds ratio
    # 47.2, cross-checked with proportions_ztest at p = 1.0e-5.
    #
    # The runner's own target-integrity guard could not catch it: it compares a
    # hash BETWEEN rounds, and these writes happen WITHIN one.
    #
    # A worktree rather than an empty directory, because the comment at
    # `reference_runner_v3.py:11391` is right that a code run's panel
    # legitimately needs to read this repository, and `build_experiment_run.py:164`
    # already does this after a model edited the runner in the live tree on
    # 2026-08-22.
    #
    # THIS IS NOT SUFFICIENT ON ITS OWN, AND SAYING SO HERE BECAUSE IT WAS TRIED.
    # With the confinement verified working -- 1 main-thread call and 6 per-worker
    # calls in the log -- a seat rewrote the repo target TWICE MORE, at 04:20:52
    # (24,834 bytes) and 04:22:22 (25,650), against a committed 20,605. A cwd
    # confines RELATIVE paths. Seats are handed the ABSOLUTE repo path to their
    # target by `_absolute_target`, under the founder's 2026-08-23 ruling, and that
    # ruling is correct for its own reasons: a repo-relative name cannot be
    # redirected into the discrimination control's overlay and cannot be found from
    # a throwaway working directory, which is what left 6 Exp 55 falsifiers ERRORed.
    # Bash is a superset of write, so an absolute path defeats any cwd.
    #
    # The remaining fix is to resolve that absolute path against the sandbox when
    # one is set -- `_absolute_target` already takes a `repo_root` -- but that
    # changes which paths appear in findings and interacts with
    # `_retarget_falsifier`, which substitutes the absolute repo root. It touches a
    # founder ruling and is NOT taken unilaterally here. What this does buy: the
    # panel gets a real sandbox, relative writes land in it, and the log line stops
    # claiming a confinement that was never applied.
    _wt_parent = pathlib.Path(tempfile.mkdtemp(prefix="cdsfl_sim_panel_"))
    _wt = _wt_parent / "repo"
    _rc = subprocess.run(["git", "worktree", "add", "--detach", str(_wt), "HEAD"],
                         cwd=str(REPO), capture_output=True, text=True)
    if _rc.returncode != 0:
        # THE SANDBOX FALLBACK, ADDED 2026-09-21 AFTER THIS DEADLOCKED A LAUNCH.
        #
        # `run_simulated_experiment_sandboxed.sh` SEVERS git history on purpose,
        # so that `git diff` cannot hand a seat the planted set. The confinement
        # above then cannot build a worktree, because there is no git, and the
        # refusal fires. Both mechanisms are individually correct and together
        # they made every sandboxed simulated run unlaunchable -- measured, not
        # predicted: arm 1 of the commissioning study exited 2 at 22:51:57 BST
        # with "fatal: not a git repository".
        #
        # What the refusal is FOR is running the panel in the LIVE repository,
        # where a seat's relative write reaches the real target. Inside the
        # sandbox that cannot happen, because the whole tree is already a
        # throwaway copy with its history severed. So the protection the
        # worktree provides is already in force, and the right move is to build
        # the same disposable cwd by COPYING rather than to refuse.
        #
        # THE MARKER IS VERIFIED, NOT TRUSTED. The wrapper exports the directory
        # it created, and this compares it against the runner's own resolved
        # root. A stale or hostile value naming some other directory does not
        # unlock the fallback, so the refusal still stands everywhere it should
        # -- including in the live repository, where the variable is unset.
        _declared = os.environ.get("CDSFL_SANDBOX_ROOT", "")
        # THE PREDICATE MUST MATCH THE JUSTIFICATION (2026-09-22, panel seat).
        # The fallback's whole argument is "the history is already severed, so
        # the worktree's protection is already in force". An env var equal to
        # the root verifies that an OPERATOR DECLARED a sandbox -- it does not
        # verify the severance. If `git worktree` fails for any OTHER reason
        # inside a real checkout (corrupt .git, worktree limit, git missing
        # from PATH) while the variable happens to name this root, the
        # justification is false but the fallback would proceed. Requiring
        # `.git` to be ABSENT ties the unlock to the one fact the argument
        # rests on; in the live repository `.git` exists and the refusal
        # stands regardless of any exported variable.
        _in_sandbox = (bool(_declared)
                       and pathlib.Path(_declared).resolve() == REPO.resolve()
                       and not (REPO / ".git").exists())
        if not _in_sandbox:
            print("    FATAL: could not create the panel worktree; refusing to run the\n"
                  "      panel in the live repository, where a seat can rewrite the target.\n"
                  f"      {_rc.stderr.strip()[:300]}", flush=True)
            shutil.rmtree(_wt_parent, ignore_errors=True)
            return 2
        # `secret_ignore`, NOT a bare `shutil.ignore_patterns`. The first
        # version of this used the bare form and was caught by
        # `test_no_repo_copy_in_bench_still_uses_the_secret_blind_exclusion_list`,
        # whose whole reason for existing is that the same leak had already
        # reached 6 separate copy sites. A pattern list built from `.git`,
        # `logs` and `__pycache__` is about SIZE AND NOISE and says nothing
        # about secrets, so it happily materialises `.env` in a directory the
        # panel can read. `secret_ignore` keeps those exclusions and adds the
        # credential patterns, so the rule lives in 1 place instead of 5.
        from panel_sandbox import secret_ignore
        shutil.copytree(REPO, _wt, symlinks=True,
                        ignore=secret_ignore(".git", "logs", "__pycache__"))
        print("    panel confined to a disposable COPY (sandbox has no git history,\n"
              f"      which is deliberate): {_wt}", flush=True)
    else:
        print(f"    panel confined to a disposable worktree: {_wt}", flush=True)
    cfg.panel_cwd = str(_wt)

    # ───────────────── CDSFL POST ─────────────────
    # An addition nothing reaches is not additive, so the check is CALLED rather
    # than left as a script an operator may remember to run.
    #
    # IT GATES THE DISPATCH, NOT THE CONFIG BUILD, and the first placement got that
    # wrong. Called immediately after the roster resolved, it returned before the
    # launcher had built its `RunnerConfig` -- which broke
    # `test_the_simulated_launcher_sets_both_lists`, a guard that drives this
    # launcher precisely to compare the 2 model lists it builds and needs it to get
    # that far. POST's purpose is to stop a RUN from dispatching against a facility
    # that is inert, not to stop the launcher from assembling its own state, and a
    # gate placed earlier than its purpose requires takes legitimate callers with
    # it. Here it is the last thing before `run_experiment`, so nothing is
    # dispatched on a RED board and everything upstream still runs.
    _post_rc = _run_post(seats, args)
    if _post_rc != 0:
        if not args.ignore_post:
            return _post_rc
        print("    POST FAILED and --ignore-post was given: proceeding anyway.",
              flush=True)
        print("    The failure above is part of this run's record.", flush=True)

    try:
        # THE CORE DIRECTIVE, NOT "" (Fable, second-pass review 2026-08-30).
        # `system_prompt_path` is read ZERO times in reference_runner_v3 and
        # runner_core -- the panel's directive arrives only via the composer, or
        # via THIS argument when the composer fails. Passing "" meant the loud
        # composer fallback handed a panellist NOTHING: Fable-SIM has no
        # composer .toml, so it would have run on an empty system prompt while
        # the core directive sat verified-on-disk in this same function.
        result = R.run_experiment(exp_cfg, cdsfl_path.read_text(encoding="utf-8"), cfg)
    finally:
        SHIM.restore(original)
        # HARVEST BEFORE REMOVING (founder ruling (j), 2026-09-17): *"Take care
        # when a panel review or an experiment completes however that the sandbox
        # does not simply get automatically deleted and that the results do not
        # end up simply being discarded, as has happened in the recent past."*
        #
        # This worktree is `cfg.panel_cwd` -- the tree the SEATS work in -- and
        # the 2 lines below removed it unconditionally, so anything a seat wrote
        # that was not already parsed out of its reply went with it. The sweep
        # that found this is scripts/sandbox_deletion_audit_2026-09-17.py, which
        # classified 26 removal sites across bench/ and, on its first run, missed
        # this one: it read `_wt_parent` as scratch because of the name. A
        # classifier that names the failure by its VARIABLE misses the site whose
        # variable is badly named, so it now asks whether the same function hands
        # the path to a model.
        try:
            from bench import panel_sandbox as _PS
            _kept = _PS.harvest(_wt, REPO, logs / "panel_worktree_harvest")
            print(f"    panel worktree harvested: {_kept['changed']} changed file(s), "
                  f"{_kept['bytes']} byte(s) -> {logs / 'panel_worktree_harvest'}",
                  flush=True)
        except Exception as _h:                                  # noqa: BLE001
            print(f"    WARNING: the panel worktree could not be harvested "
                  f"({type(_h).__name__}: {_h}); it is NOT being removed, so "
                  f"nothing is lost: {_wt}", flush=True)
        else:
            subprocess.run(["git", "worktree", "remove", "--force", str(_wt)],
                           cwd=str(REPO), capture_output=True)
            shutil.rmtree(_wt_parent, ignore_errors=True)
    el = time.monotonic() - t0

    # MEASUREMENT 10 HAD NO SCRIPT BECAUSE IT HAD NO DATA (2026-10-03).
    #
    # The programme of study's measurement 10 asks whether what the launcher
    # DECLARES matches what actually FIRES. It had no committed script, and the
    # reason is upstream of the script: nothing recorded the declaration. The
    # report carried the runner's results and not one field of the config that
    # produced them, so "declared" existed only in this file's source and in
    # whatever argv a human happened to keep. The comparison was unanswerable
    # from the archive for every run ever made.
    #
    # Recorded here as a flat dict of the config the runner was ACTUALLY
    # constructed with -- not a restatement of the flags, which is the same
    # mistake one level up. `scripts/declared_vs_observed_2026-10-03.py`
    # consumes it.
    #
    # NOTHING CREDENTIAL-SHAPED IS WRITTEN. Field names are filtered, and the
    # value of any field whose name names a key, token, secret, password or
    # environment file is replaced with a marker rather than omitted, so a
    # reader can tell a withheld field from an absent one.
    try:
        _hide = ("key", "token", "secret", "password", "passwd", "credential",
                 "api", "env_file", "scoring_env")
        _declared_cfg = {}
        for _f in dataclasses.fields(cfg):
            _v = getattr(cfg, _f.name, None)
            if any(h in _f.name.lower() for h in _hide):
                _declared_cfg[_f.name] = "<withheld: name matches a credential pattern>"
            elif isinstance(_v, (str, int, float, bool, type(None))):
                _declared_cfg[_f.name] = _v
            elif isinstance(_v, (list, tuple)):
                _declared_cfg[_f.name] = [x if isinstance(
                    x, (str, int, float, bool, type(None))) else type(x).__name__
                    for x in _v]
            else:
                _declared_cfg[_f.name] = f"<{type(_v).__name__}>"
        result["_declared_config"] = _declared_cfg
        result["_declared_argv"] = list(sys.argv[1:])
    except Exception as _dc:                                   # noqa: BLE001
        result["_declared_config_error"] = f"{type(_dc).__name__}: {_dc}"

    result["_simulated"] = True
    result["_sim_label_map"] = SHIM.LABEL_MAP
    result["_sim_dispatches"] = SHIM.calls()
    result["_wall_seconds"] = round(el, 1)
    out = logs / f"{args.name}_report.json"
    out.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")

    gh = result.get("gamma_critical_history") or result.get("gamma_history") or []
    print(f"\n=== RESULT ===", flush=True)
    print(f"    runner_version : {result.get('runner_version')}", flush=True)
    print(f"    rounds run     : {len(gh)}", flush=True)
    print(f"    converged_at   : {result.get('converged_at')}", flush=True)
    print(f"    reason         : {(result.get('convergence_reason') or '(none)')[:120]}", flush=True)
    print(f"    findings       : {len((result.get('registry') or {}).get('entries', {}))}", flush=True)
    print(f"    wall           : {el/60:.1f} min", flush=True)
    print(f"    report         : {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
