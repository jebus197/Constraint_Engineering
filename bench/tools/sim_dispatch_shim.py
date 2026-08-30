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


def make_shim(model: str = "sonnet", timeout: int = 900):
    """Return a drop-in replacement for ``dispatch_to_model``.

    THE SEAM MOVED DOWN ONE LEVEL, 2026-08-30, AND THIS IS WHY
    ----------------------------------------------------------
    The first version patched ``_dispatch_single_model``. That is ONE of NINE
    functions in ``reference_runner_v2`` that dispatch to a model:

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
        budget = int(wall_clock_limit) if wall_clock_limit and wall_clock_limit > 0 else timeout
        try:
            r = subprocess.run(
                ["claude", "-p", full, "--model", model, "--output-format", "text",
                 "--no-session-persistence",
                 "--allowedTools", "Bash", "Read", "Grep", "Glob"],
                capture_output=True, text=True, timeout=budget,
                cwd=str(REPO), stdin=subprocess.DEVNULL,
            )
            text = (r.stdout or "").strip()
            if r.returncode != 0 and not text:
                text = f"__DISPATCH_FAILED__:rc={r.returncode}"
        except subprocess.TimeoutExpired:
            text = "__DISPATCH_FAILED__:TimeoutExpired"
        except Exception as e:                              # noqa: BLE001
            text = f"__DISPATCH_FAILED__:{type(e).__name__}: {e}"

        el = time.monotonic() - t0
        with _LOCK:
            _CALLS.append({"model": label, "seconds": round(el, 1),
                           "chars": len(text), "budget_s": budget,
                           "failed": text.startswith("__DISPATCH_FAILED__")})
        print(f"    [{label}] {len(text)} chars, {el:.0f}s"
              + (" FAILED" if text.startswith("__DISPATCH_FAILED__") else ""),
              flush=True)
        return text, el

    return _dispatch


def install(model: str = "sonnet", timeout: int = 900):
    """Patch the PRIMITIVE seam. Returns the original so a caller can restore."""
    original = R.dispatch_to_model
    R.dispatch_to_model = make_shim(model, timeout)
    return original


def restore(original) -> None:
    R.dispatch_to_model = original


def calls() -> list:
    with _LOCK:
        return list(_CALLS)
