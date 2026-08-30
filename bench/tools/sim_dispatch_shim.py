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
LABEL_MAP = {v: f"{v}-SIM" for v in
             ("CC2", "DeepSeek", "ChatGPT", "Gemini", "Codex", "Fable")}

_LOCK = threading.Lock()
_CALLS: list = []


def _sim_label(mc_label: str) -> str:
    return LABEL_MAP.get(mc_label, mc_label if mc_label.endswith("-SIM")
                         else f"{mc_label}-SIM")


def make_shim(model: str = "sonnet", timeout: int = 300):
    """Return a drop-in replacement for `_dispatch_single_model`."""

    def _dispatch(mc, mgr, prompt, cdsfl_text, full_code, round_idx,
                  pattern_name, domain, logs_dir, enable_tools):
        label = _sim_label(getattr(mc, "label", "?"))
        t0 = time.monotonic()
        # The agent gets the SAME prompt the paid model would get, plus the
        # directive text, so the parse path and the briefing are both real.
        full = f"{cdsfl_text}\n\n{prompt}" if cdsfl_text else prompt
        try:
            r = subprocess.run(
                ["claude", "-p", full, "--model", model, "--output-format", "text",
                 "--no-session-persistence",
                 "--allowedTools", "Bash", "Read", "Grep", "Glob"],
                capture_output=True, text=True, timeout=timeout,
                cwd=str(REPO), stdin=subprocess.DEVNULL,
            )
            text = (r.stdout or "").strip()
            if r.returncode != 0 and not text:
                text = f"__DISPATCH_FAILED__:rc={r.returncode}"
        except subprocess.TimeoutExpired:
            text = "__DISPATCH_FAILED__:TimeoutExpired"
        except Exception as e:                              # noqa: BLE001
            return [], f"__DISPATCH_FAILED__:{type(e).__name__}: {e}"

        el = time.monotonic() - t0
        # THE RUNNER'S OWN PARSER. Fabricating Finding objects here would mean the
        # parse path — the thing that has broken most often in this project — was
        # the one path a simulated run never exercised.
        # The SIM label, never ``mc.label``: this is the single call that stamps
# model_id and finding_id into every persisted artefact. Measured
# 2026-08-30: passing mc.label here put 123 bare vendor names into the
# record while the terminal showed the SIM name -- cosmetic in the log,
# absent from the artefact, which is the 2026-08-04 provenance failure.
        findings = R.parse_findings(label, round_idx, text)
        with _LOCK:
            _CALLS.append({"round": round_idx, "model": mc.label, "sim": label,
                           "seconds": round(el, 1), "chars": len(text),
                           "findings": len(findings)})
        print(f"    [r{round_idx} {label} as {mc.label}] {len(findings)} finding(s), "
              f"{len(text)} chars, {el:.0f}s", flush=True)
        return findings, text

    return _dispatch


def install(model: str = "sonnet", timeout: int = 300):
    """Patch the seam. Returns the original so a caller can restore it."""
    original = R._dispatch_single_model
    R._dispatch_single_model = make_shim(model, timeout)
    return original


def restore(original) -> None:
    R._dispatch_single_model = original


def calls() -> list:
    with _LOCK:
        return list(_CALLS)
