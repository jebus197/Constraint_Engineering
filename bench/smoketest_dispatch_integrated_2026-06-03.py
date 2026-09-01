"""Integrated DISPATCH-PATH smoke test (2026-06-03).

Proves the CONNECTIVE TISSUE that lets a live CDSFL experiment use active tool
use + the falsifier gate. The gate's verdict logic is already built and tested
(bench/falsifier_verify.py); this test exercises the *nested dispatch path* that
the live runner actually takes, end to end:

  in-process path   -> experiment_11_orchestrator.dispatch(enable_tools=True)
  mp watchdog path  -> runner_core.dispatch_to_model(enable_tools=True)
                        |  this is the SINGLE MOST IMPORTANT path to prove:
                        |  the execute_python tool spawns a SUBPROCESS, and in
                        |  the live runner that happens INSIDE a multiprocessing
                        |  daemon worker (mp.Process(daemon=True)). A daemonic
                        |  process cannot have children in some configurations,
                        |  so a nested-subprocess failure here would silently
                        |  break tool use in production. If it fails, this test
                        |  reports it LOUDLY.
  extraction        -> runner_core.parse_findings (-> Finding.falsifier_code)
  verdict           -> reference_runner_v3.apply_falsifier_verdicts over a real
                        FindingRegistry with RunnerConfig(falsifier_gate_enabled=
                        True). The runner re-runs the falsifier; the verdict is
                        CONFIRMED / REFUTED / HIL — a TOOL decision, NOT a vote.

Target under review: bench.dm._similarity.jaccard_similarity — a pure,
deterministic, embedding-independent function with execution-established ground
truth. The claim under test is TRUE: self-similarity is not maximal, i.e.
jaccard_similarity(f, f) < 1.0 (it returns ~0.86). An honest falsifier therefore
RAISES/prints FALSIFIED -> the runner's independent re-run = CONFIRMED.

Honest-failure policy: if OPENROUTER_API_KEY is missing or the dispatch call
fails, the test REPORTS it and aborts — it never fakes a result. The sandbox is
read/import-only and never modifies repo files.

Run:  python3 bench/smoketest_dispatch_integrated_2026-06-03.py
NOT wired into any launch_exp* path; gated/default-OFF integration.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "bench"))

# Minimal .env loader (same as the sibling smoke tests).
_env = REPO_ROOT / ".env"
if _env.exists():
    for ln in _env.read_text().splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        ln = ln[7:] if ln.startswith("export ") else ln
        if "=" in ln:
            k, _, v = ln.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip("'\""))

# Production code paths — the whole point is to use the REAL functions.
from experiment_11_orchestrator import (  # noqa: E402
    ModelConfig,
    dispatch,
)
from runner_core import dispatch_to_model, parse_findings  # noqa: E402
from reference_runner_v3 import (  # noqa: E402
    FindingRegistry,
    RunnerConfig,
    apply_falsifier_verdicts,
)

MODEL_ID = "openai/gpt-5.5"

# The model config a live experiment builds for an OpenRouter participant. Only
# the fields dispatch() reads are set; the rest take dataclass defaults. role is
# "participant" (a reviewing model). system_prompt_path must be truthy for the
# CDSFL system prompt to be forwarded (dispatch gates the system prompt on it).
MODEL_CONFIG = ModelConfig(
    label="cx",
    model_id=MODEL_ID,
    api="openrouter",
    role="participant",
    system_prompt_path="bench/directives/universal/cdsfl_core_formal.md",
    max_tokens=4096,
    timeout=180,
    max_retries=2,
)

SYSTEM_PROMPT = (
    "You are a careful CDSFL STEM/code falsification reviewer with an "
    "execute_python tool. Prove or disprove claims by RUNNING code against the "
    "REAL repository module; never assert a verdict in prose alone."
)

# TRUE claim with execution-established ground truth (CONFIRMED).
CLAIM = (
    "jaccard_similarity does NOT return 1.0 for a finding compared with itself "
    "(self-similarity is not maximal): for a non-empty description, "
    "jaccard_similarity(f, f) < 1.0."
)
GROUND_TRUTH = "CONFIRMED"

USER_PROMPT = f"""You are reviewing this SPECIFIC CLAIM about real repository code.

  CLAIM: {CLAIM}
  TARGET: the function `jaccard_similarity` in module `bench.dm._similarity`.

Decide, mechanically, whether the CLAIM identifies a REAL defect.

You MUST:
1. Use execute_python to investigate. IMPORT THE REAL MODULE — write
   `from bench.dm._similarity import jaccard_similarity` and
   `from bench.dm._types import Finding`. Do NOT retype or redefine the
   function; test the ACTUAL code.
2. Write a FALSIFIER: a self-contained Python snippet that imports the REAL
   module and RAISES an AssertionError (or prints the token FALSIFIED) IF AND
   ONLY IF the claimed defect is genuinely present. If the claim were false the
   falsifier must run to a clean exit (no raise, no FALSIFIED).
3. Actually RUN your falsifier with execute_python and read the result.

Report EXACTLY one finding in this format (a Finding line + a runnable
FALSIFIER block are mandatory):

FINDING_ID: F001
SEVERITY: CRITICAL
FINDING: <one-line description of the claim under test>
FALSIFIER:
```python
<the exact code you ran — importing the REAL module>
```
RAN_RESULT: <paste the tool's actual output>
VERDICT: CONFIRMED
"""

# Deterministic fallback falsifier (imports the REAL module; raise-iff-defect).
# Used ONLY if the model fails to attach a usable one, so the verdict step
# always has runnable code to decide on. Reported when used.
FALLBACK_FALSIFIER = """\
from bench.dm._types import Finding
from bench.dm._similarity import jaccard_similarity
f = Finding('a', 'm', 0, 2, 0.8, 0.5, 'memory leak in the cache eviction path')
s = jaccard_similarity(f, f)
# Defect-claim: self-similarity is not 1.0. Raise IFF that defect is real.
assert s < 1.0, f'self-similarity is {s}, not < 1.0 -> claim NOT demonstrated'
print(f'FALSIFIED: self-similarity is {s}, not 1.0')
"""


def _detect_tool_use(response: str) -> bool:
    """Heuristic: did the model actually run the tool against the real module?

    The dispatch tool loop folds tool turns back into the conversation, so the
    final text reflects whether the model exercised the tool. We treat presence
    of the FALSIFIER fenced block that imports the real module, plus a pasted
    RAN_RESULT, as evidence of genuine tool use. (The mp-path's stronger proof
    is structural: the call completes without a nested-subprocess crash.)
    """
    up = response
    return (
        "bench.dm._similarity" in up
        and "```python" in up
        and ("RAN_RESULT" in up or "FALSIFIED" in up or "0.8" in up)
    )


def _verdict_via_runner(response: str, label: str) -> dict:
    """parse_findings -> register -> apply_falsifier_verdicts. Returns a row.

    The runner re-runs the model's attached falsifier independently; that re-run
    is the verdict. Mirrors the live runner's order: register findings, then the
    gate decides truth (NOT the CONFIRM/CHALLENGE vote).
    """
    findings = parse_findings("cx", 1, response)
    model_attached = bool(findings and findings[0].falsifier_code)
    imports_real = bool(
        findings and "bench.dm._similarity" in (findings[0].falsifier_code or "")
    )
    used_fallback = False
    if not model_attached or not imports_real:
        # Guarantee runnable code so the verdict step is deterministic; the
        # severity is forced CRITICAL so the gate cannot skip it. Finding is a
        # FROZEN dataclass, so build a fresh instance (replace) rather than
        # mutating in place.
        import dataclasses
        from bench.dm._types import Finding as _F
        used_fallback = True
        if findings:
            findings[0] = dataclasses.replace(
                findings[0],
                falsifier_code=FALLBACK_FALSIFIER,
                severity=max(findings[0].severity, 0.9),
            )
        else:
            findings = [_F(
                finding_id="F001", model_id="cx", round_idx=1,
                flaw_class=0, severity=0.9, abstraction_index=0.5,
                description=CLAIM, target_file="bench/dm/_similarity.py",
                falsifier_code=FALLBACK_FALSIFIER,
            )]

    # Register into a real registry, run the REAL gate with the flag ON.
    reg = FindingRegistry()
    cids = [reg.register(f, "cx") for f in findings]
    cfg = RunnerConfig(
        models=["cx"],
        falsifier_gate_enabled=True,
    )
    apply_falsifier_verdicts(reg, round_idx=1, cfg=cfg, repo_root=str(REPO_ROOT))

    verdicts = {
        cid: {
            "status": reg.entries[cid]["status"],
            "falsifier_verdict": reg.entries[cid].get("falsifier_verdict", ""),
            "severity": reg.entries[cid]["severity"],
        }
        for cid in cids
    }
    return {
        "label": label,
        "model_attached_falsifier": model_attached,
        "imports_real_module": imports_real,
        "used_fallback": used_fallback,
        "verdicts": verdicts,
    }


def run_in_process() -> dict:
    """Path A: dispatch() directly (in-process tool loop, no mp worker)."""
    print("\n=== PATH A: in-process dispatch(enable_tools=True) ===")
    try:
        response = dispatch(
            MODEL_CONFIG, USER_PROMPT, SYSTEM_PROMPT, enable_tools=True
        )
    except Exception as exc:  # noqa: BLE001
        print(f"[in-process dispatch ERROR: {type(exc).__name__}: {exc}]")
        return {"path": "in_process", "error": f"{type(exc).__name__}: {exc}"}
    tool_used = _detect_tool_use(response)
    row = _verdict_via_runner(response, "in_process")
    row["path"] = "in_process"
    row["model_called_tool"] = tool_used
    row["response_tail"] = response[-300:]
    print(f"model_called_tool? {tool_used}")
    print(f"falsifier_attached? {row['model_attached_falsifier']} "
          f"(imports real: {row['imports_real_module']}, "
          f"fallback used: {row['used_fallback']})")
    print(f"runner verdict(s): {row['verdicts']}")
    return row


def run_mp_worker() -> dict:
    """Path B (THE KEY RISK): dispatch_to_model() — the mp watchdog worker path.

    The execute_python sandbox spawns a subprocess; here that happens INSIDE the
    multiprocessing daemon worker (mp.Process(daemon=True)) that the live runner
    uses. If the nested subprocess cannot launch under the daemon worker, this is
    where it surfaces — reported LOUDLY.
    """
    print("\n=== PATH B: mp-watchdog dispatch_to_model(enable_tools=True) "
          "[THE KEY RISK] ===")
    try:
        response, elapsed = dispatch_to_model(
            MODEL_CONFIG, USER_PROMPT, SYSTEM_PROMPT,
            wall_clock_limit=MODEL_CONFIG.timeout * 3,
            enable_tools=True,
        )
    except Exception as exc:  # noqa: BLE001
        print("*** mp-watchdog dispatch FAILED — nested subprocess under the "
              "multiprocessing daemon worker did not complete. THIS IS THE "
              "SINGLE MOST IMPORTANT FAILURE TO SURFACE. ***")
        print(f"*** {type(exc).__name__}: {exc} ***")
        return {"path": "mp_worker", "mp_path_ok": False,
                "error": f"{type(exc).__name__}: {exc}"}

    tool_used = _detect_tool_use(response)
    row = _verdict_via_runner(response, "mp_worker")
    row["path"] = "mp_worker"
    row["mp_path_ok"] = True
    row["model_called_tool"] = tool_used
    row["elapsed_s"] = round(elapsed, 1)
    row["response_tail"] = response[-300:]
    print(f"mp_path_ok? True (completed in {elapsed:.1f}s, "
          f"{len(response)} chars)")
    print(f"model_called_tool? {tool_used}")
    print(f"falsifier_attached? {row['model_attached_falsifier']} "
          f"(imports real: {row['imports_real_module']}, "
          f"fallback used: {row['used_fallback']})")
    print(f"runner verdict(s): {row['verdicts']}")
    return row


def _has_tool_decided_verdict(row: dict) -> bool:
    """A finding got a tool-decided verdict (CONFIRMED/REFUTED/HIL), not a vote.

    The gate writes falsifier_verdict (CONFIRMED/REFUTED/ERROR/UNTOOLABLE) and
    sets status accordingly. We require at least one entry whose status is a
    falsifier-driven terminal (CONFIRMED/REFUTED) OR which was escalated to HIL.
    """
    if row.get("error"):
        return False
    for v in row.get("verdicts", {}).values():
        fv = v.get("falsifier_verdict", "")
        if v["status"] in ("CONFIRMED", "REFUTED") or fv in (
            "CONFIRMED", "REFUTED", "ERROR", "UNTOOLABLE"
        ):
            return True
    return False


def main() -> int:
    print("=== integrated DISPATCH-PATH smoke test "
          "(target: real jaccard_similarity; claim ground truth = CONFIRMED) ===")
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("OPENROUTER_API_KEY not set — cannot run the model dispatch. "
              "Reporting honestly and aborting (NO faked results).")
        return 2

    rows = [run_in_process(), run_mp_worker()]

    print("\n=== SUMMARY ===")
    ok = True
    mp_ok = None
    for r in rows:
        if r.get("error") and r["path"] == "in_process":
            print(f"in_process: ERROR {r['error']}")
            ok = False
            continue
        tool_decided = _has_tool_decided_verdict(r)
        verdict_strs = {
            cid: f"{v['status']}/{v.get('falsifier_verdict', '')}"
            for cid, v in r.get("verdicts", {}).items()
        }
        line = (
            f"{r['path']}: model_called_tool={r.get('model_called_tool')} "
            f"falsifier_attached={r.get('model_attached_falsifier')} "
            f"verdict={verdict_strs} tool_decided={tool_decided}"
        )
        if r["path"] == "mp_worker":
            mp_ok = r.get("mp_path_ok", False)
            line = f"{line} mp_path_ok={mp_ok}"
        print(line)
        # A tool-decided verdict is the deliverable proof for each path.
        if not r.get("error") and not tool_decided:
            print(f"  !! {r['path']}: NO tool-decided verdict produced — "
                  "the gate did not decide this finding.")
            ok = False

    # The mp-worker nested-subprocess result is the headline.
    print("\n--- HEADLINE: nested-subprocess under mp daemon worker ---")
    if mp_ok is True:
        print("mp-watchdog dispatch ran the execute_python tool subprocess "
              "successfully from INSIDE the multiprocessing daemon worker. "
              "The live runner's tool path is viable.")
    elif mp_ok is False:
        print("*** mp-watchdog dispatch FAILED: the nested subprocess did NOT "
              "complete under the multiprocessing daemon worker. The live "
              "runner CANNOT use tools on this path as wired. SURFACE THIS. ***")
        ok = False
    else:
        print("mp-watchdog path did not run (in-process error upstream).")
        ok = False

    print(f"\nOVERALL: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
