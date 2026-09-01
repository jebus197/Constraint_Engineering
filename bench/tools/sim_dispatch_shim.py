#!/usr/bin/env python3
"""Run a REAL experiment with agents standing in for the paid models.

    PANEL LABELS CARRY THE MANDATORY `-SIM` SUFFIX. They stand in for CC2, DeepSeek, ChatGPT,
    Gemini, Codex and Fable and are NOT those models. Labelling a simulated agent
    with a vendor name on 2026-08-04 put two indistinguishable panels into the
    record and results were reported as though vendors had produced them.

WHAT THIS IS, AND WHY IT IS DIFFERENT FROM `simulated_bench.py`
==============================================================
`bench/tools/simulated_bench.py` calls runner FUNCTIONS in a hand-written order.
Measured 2026-08-30: it invokes 7 of the 53 functions `run_experiment` calls —
13.2%, 95% Wilson CI [6.5%, 24.8%] — has NO round loop, and never touches
`_dispatch_round_star`, `_compute_rho`, `_estimate_gamma`, `_apply_routing`,
`_build_feedback_for_next_round`, or three of the four convergence gates. Its
"converged=True" came from a stage passing hardcoded arguments.

This runs `run_experiment()` ITSELF — all 2,363 lines of it. Real rounds, real
rho and gamma, all four gates, routing, the feedback channel, and a convergence
verdict at a real round number.

THE SEAM
========
`_dispatch_single_model(mc, mgr, prompt, ...) -> (findings, raw_text)` is the only
place a paid model is called. This patches that one function. Everything upstream
and downstream is untouched, and the agent's raw text is parsed by the runner's
OWN `parse_findings` — no fabricated Finding objects, so the parse path under test
is the real one.

COST: none. Claude subagents on the founder's plan.

IS NOT AN EXPERIMENT. A simulated panel differs in character from six frontier
models under the full directive. Nothing here is an experimental result and none
of it belongs in the paper.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import threading
import time

REPO = pathlib.Path(__file__).resolve().parents[2]
for p in (str(REPO), str(REPO / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)

import reference_runner_v2 as R   # noqa: E402

#: Vendor label -> simulated stand-in. Order fixed so a run is reproducible.
#: Founder ruling 2026-08-08 supersedes the earlier ``SIM-A``..``SIM-E`` form:
#: the mandated names are ``CC2-SIM``, ``DeepSeek-SIM`` and so on. The suffix
#: carries the role information the bare letter threw away.
#: Founder ruling 2026-08-08 supersedes the earlier ``SIM-A``..``SIM-E`` form:
#: the mandated names are ``CC2-SIM``, ``DeepSeek-SIM`` and so on. The suffix
#: carries the role information the bare letter threw away.
LABEL_MAP = {v: f"{v}-SIM" for v in
             ("CC2", "DeepSeek", "ChatGPT", "Gemini", "Codex", "Fable")}

_LOCK = threading.Lock()
_CALLS: list = []


def _sim_label(mc_label: str) -> str:
    return LABEL_MAP.get(mc_label, mc_label if str(mc_label).endswith("-SIM")
                         else f"{mc_label}-SIM")


def _record(label: str, elapsed: float, chars: int, budget: int,
            failure: str | None) -> None:
    """Telemetry, recorded BEFORE any raise.

    The shim now raises on transport death rather than returning a sentinel, so
    a failure leaves this function by exception and would take its own telemetry
    with it. The v3.1 timeout rate (7 of 20 dispatches) was only measurable
    because failures were recorded; losing that would make the next run's
    reliability invisible.
    """
    with _LOCK:
        _CALLS.append({"model": label, "seconds": round(elapsed, 1),
                       "chars": chars, "budget_s": budget,
                       "failed": failure is not None, "failure": failure})
    print(f"    [{label}] {chars} chars, {elapsed:.0f}s"
          + (f" FAILED: {failure}" if failure else ""), flush=True)


def make_shim(model: str = "sonnet", timeout: int = 900):
    """Return a drop-in replacement for ``dispatch_to_model``.

    THE SEAM MOVED DOWN ONE LEVEL, 2026-08-30, AND THIS IS WHY
    ----------------------------------------------------------
    The first version patched ``_dispatch_single_model``. That is ONE of EIGHT
    call sites, in SEVEN enclosing functions, that dispatch to a model
    (``_apply_routing`` and ``run_experiment`` reach it only through the nested
    ``resolve_fn`` and ``_arb_dispatch``; the count was stated as nine here and
    CC2 corrected it by AST on 2026-08-30):

        _apply_routing, _post_convergence_sweep, _inround_reask,
        _dispatch_single_model, _verification_step, run_preflight,
        run_experiment, resolve_fn, _arb_dispatch

    Every one of the other eight therefore dispatched to a REAL, unconfigured
    model during the v3.1 simulated run. The consequences were measured, not
    assumed:

      * ``resolve_fn`` is the routing ladder's FALSIFIER WRITER. Its call raised,
        was swallowed by a bare ``except`` that returns "", and the run logged
        "routing: 0 resolved by strong writer" in all 4 rounds. Result: 0 of 19
        entries carried ``falsifier_code``, against 23 of 39 in the real exp45
        on the same target (scipy Fisher p = 6.0e-06). The falsification core --
        the point of the whole schema -- was silent for the entire run.
      * ``_verification_step`` never ran, so ``verified`` was False on all 19
        entries against 24 of 39 in the real run.
      * the fix-efficacy probe depends on ``falsifier_code``, so it reached 0
        of 19 as a downstream consequence of the same single cause.

    Patching the PRIMITIVE fixes all nine by construction. There is no list of
    call sites to keep in sync -- which is the failure this replaces.

    The runner now does ALL of its own parsing, including
    ``parse_findings``, ``_extract_routing_falsifier`` and
    ``_extract_corrected_copies``. Provenance is correct by construction because
    ``mc.label`` is already ``CC2-SIM`` at source; nothing here relabels
    anything, so there is no longer a place where a label can be dropped.
    """

    def _dispatch(model_config, prompt, cdsfl_text,
                  wall_clock_limit: float = 0, enable_tools: bool = False):
        label = _sim_label(getattr(model_config, "label", "?"))
        t0 = time.monotonic()
        # The agent receives the SAME prompt the paid model would, whichever of
        # the nine paths asked for it -- a findings prompt, a routing prompt
        # asking for a runnable falsifier, a sweep prompt, a verification
        # prompt. The prompts already carry their own instructions, so one
        # handler serves every path without the shim second-guessing any of it.
        full = f"{cdsfl_text}\n\n{prompt}" if cdsfl_text else prompt
        # TOOL-NAME BRIDGE (CC2, second-pass review 2026-08-30). The falsifier
        # directive instructs "Run it with the execute_python tool first". A
        # stand-in agent has Bash, not a tool of that name, so an agent taking
        # the instruction literally could decline to write a falsifier at all --
        # which is the exact failure this simulation exists to catch.
        #
        # Appended in the SIMULATION ONLY. The directive text itself is what the
        # real paid models read and is left untouched, so this changes the
        # rehearsal without changing the experiment.
        if "execute_python" in full:
            full += ("\n\n[SIMULATION NOTE: you do not have a tool literally named "
                     "`execute_python`. Where the directive says to run code with it, "
                     "run the code with Bash (`python3 - <<'PY' ... PY`) instead. The "
                     "requirement to actually EXECUTE the falsifier before reporting "
                     "on it is unchanged.]")
        budget = int(wall_clock_limit) if wall_clock_limit and wall_clock_limit > 0 else timeout
        try:
            r = subprocess.run(
                ["claude", "-p", full, "--model", model, "--output-format", "text",
                 "--no-session-persistence",
                 # FOUNDER RULING 2026-08-31: "remove personal directives like
                 # this and any disability directives from the directive set fed
                 # to the models... do it."
                 #
                 # A `claude -p` subagent loads BOTH ~/.claude/CLAUDE.md and the
                 # project .claude/CLAUDE.md before it sees the brief. Measured:
                 # 66,533 of 93,442 briefing characters (71.2%) were inherited
                 # config, 2.5x more than the CDSFL directive it is meant to
                 # apply. Two panellists refused to review at all, citing the
                 # operator's personal working-hours directive; a third objected
                 # using a naming rule superseded on 2026-08-08.
                 #
                 # `--setting-sources ""` suppresses both. Verified by execution:
                 # the same probe answered YES to both files before and "No. No."
                 # after. `--bare` also works but forces API-key auth, which
                 # would break subscription dispatch -- rejected.
                 "--setting-sources", "",
                 "--allowedTools", "Bash", "Read", "Grep", "Glob"],
                capture_output=True, text=True, timeout=budget,
                cwd=str(REPO), stdin=subprocess.DEVNULL,
            )
            text = (r.stdout or "").strip()
            if r.returncode != 0 and not text:
                _record(label, time.monotonic() - t0, 0, budget,
                        f"rc={r.returncode}")
                raise RuntimeError(
                    f"{label} dispatch process exited without result "
                    f"(exit code {r.returncode})")
        except subprocess.TimeoutExpired:
            # RAISE, DO NOT RETURN A SENTINEL (Fable, second-pass review
            # 2026-08-30). THE ERROR CONTRACT IS PART OF THE SEAM.
            #
            # The real `dispatch_to_model` RAISES on transport death
            # (runner_core.py:1271 TimeoutError, :1277 RuntimeError, :1284
            # re-raised payload). `_dispatch_single_model` catches that and
            # converts it to the `__DISPATCH_FAILED__` sentinel ITSELF
            # (reference_runner_v2.py:6947) -- so the sentinel belongs to the
            # findings path alone.
            #
            # Returning the sentinel instead of raising made every OTHER path
            # read a dead subprocess as a successful dispatch. `resolve_fn`
            # detects transport death by EXCEPTION; a normal return reaches
            # `_routing_attempts.append(model_label)  # a model was genuinely
            # reached`. So a `claude -p` timeout burned the sub-critical
            # one-attempt and, with every rung timing out, minted
            # irreducible_escalation=True on a critical -- which
            # unverified_critical_count skips. THE SIMULATED RUN COULD CONVERGE
            # BECAUSE SUBPROCESSES TIMED OUT, and the transport-dead guard
            # hoisted in v3.2 could never fire in simulation, so the sim could
            # not exercise the repair that most needed exercising.
            #
            # Measured: the v3.1 run lost 7 of 20 dispatches to timeout at 300s.
            _record(label, time.monotonic() - t0, 0, budget, "TimeoutExpired")
            raise TimeoutError(
                f"{label} dispatch exceeded wall-clock limit ({budget:.0f}s). "
                f"Process forcibly terminated.")

        el = time.monotonic() - t0
        _record(label, el, len(text), budget, None)
        return text, el

    return _dispatch


def make_multiturn_shim(dispatch):
    """Stand in for ``_multiturn_fallback``, the SECOND dispatch primitive.

    THE SEAM WAS TWO PRIMITIVES, NOT ONE (2026-09-01). Patching
    ``dispatch_to_model`` covers every path that funnels through it -- but
    ``_multiturn_fallback`` does not. It calls ``decomposed_dispatch``, a
    separate function with its own API table listing google, openrouter,
    deepseek and codex_exec. A simulated ModelConfig carries ``api="sim"``, so
    the moment the runner fell back to the multi-turn path every agent died on
    ``ValueError: Unknown API: sim``. Measured on the first launch of the final
    exp45 run: 5 of 6 agents failed in Round 0, before a single finding.

    This is the same shape as the 2026-08-30 defect where the shim patched one
    of nine dispatch sites. The lesson taken then was "patch the primitive";
    the lesson that survives now is "count the primitives".

    The real function delivers the target in chunks across several turns and
    then asks for a synthesis. The stand-in agent has the whole target in one
    context, so the chunking has nothing to model: the same content and the
    same final instruction go over in one turn. Returns ``(text, elapsed)``,
    the real function's contract.
    """
    def _mt(mc, prompt, cdsfl_text, full_code, round_idx, pattern_text,
            logs_dir, enable_tools: bool = True):
        composed = f"{full_code}\n\n{pattern_text}\n\n{prompt}"
        return dispatch(mc, composed, cdsfl_text, enable_tools=enable_tools)
    return _mt


def make_decomposed_shim(dispatch):
    """Backstop for ``decomposed_dispatch`` itself.

    ``make_multiturn_shim`` covers the runner's own fallback, which is the path
    that failed. This covers any OTHER caller reaching the decomposed primitive
    during a simulated run, so a third route cannot rediscover the same crash.
    It cannot recover the agent's label -- every simulated ModelConfig carries
    ``model_id="sim"`` -- so telemetry lands under the api name. That is why the
    multi-turn patch above exists as well rather than relying on this alone.
    """
    class _Stand:
        label = "sim"

    def _dd(api, model_id, system_prompt, chunks, final_instruction,
            max_tokens: int = 32768, timeout: int = 600,
            cdsfl_directives=None, enable_tools: bool = False,
            extra_body=None):
        from decomposed_dispatch import DecomposedResult
        body = "\n\n".join(getattr(c, "content", str(c)) for c in chunks)
        text, elapsed = dispatch(
            _Stand(), f"{body}\n\n{final_instruction}",
            cdsfl_directives or system_prompt or "", enable_tools=enable_tools)
        return DecomposedResult(
            text=text, model_id=model_id or "sim", api=api,
            chunks_delivered=len(chunks), total_chars_delivered=len(body),
            elapsed_s=elapsed)
    return _dd


def install(model: str = "sonnet", timeout: int = 900):
    """Patch BOTH dispatch primitives. Returns the originals for restore()."""
    dispatch = make_shim(model, timeout)
    originals = (R.dispatch_to_model, R._multiturn_fallback,
                 R.decomposed_dispatch)
    R.dispatch_to_model = dispatch
    R._multiturn_fallback = make_multiturn_shim(dispatch)
    R.decomposed_dispatch = make_decomposed_shim(dispatch)
    return originals


def restore(originals) -> None:
    # Tuple since 2026-09-01. A bare callable is still accepted so an older
    # caller restores the primary seam rather than raising here.
    if not isinstance(originals, tuple):
        R.dispatch_to_model = originals
        return
    (R.dispatch_to_model, R._multiturn_fallback,
     R.decomposed_dispatch) = originals


def calls() -> list:
    with _LOCK:
        return list(_CALLS)
