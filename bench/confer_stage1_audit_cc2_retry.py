#!/usr/bin/env python3
"""CC2-only retry for the Stage 1 audit panel. The other four already returned.

WHY THIS EXISTS. cc2 timed out three times at exactly 300.0s. Root cause is not
the model: call_claude_cli defaults to timeout=300, and this panel's SYSTEM prompt
explicitly instructs the only tool-capable panellist to read the repository and
verify rather than accept. reference_runner_v3.py is ~9,900 lines. The instruction
and the default were in direct conflict.

Precedent for the fix is in the same module: experiment_11_orchestrator.py:134
already carries "WP4a: 300->900s to prevent CC2 timeout cascade" for a different
call site. This applies the same value here.

No marginal cost: cc2 runs on the Max subscription, not metered credits.
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from experiment_11_orchestrator import call_claude_cli  # noqa: E402

import importlib.util
spec = importlib.util.spec_from_file_location(
    "panel", Path(__file__).resolve().parent / "confer_stage1_audit_pr_2026-08-18.py")
panel = importlib.util.module_from_spec(spec)
spec.loader.exec_module(panel)

LOGS = panel.LOGS
t0 = time.time()
print(f"=== cc2 retry — timeout 900s (was 300s) ===")
print(f"  prompt {len(panel.PROMPT):,} chars")
try:
    resp = call_claude_cli("opus", panel.SYSTEM, panel.PROMPT, timeout=900, max_retries=2)
    ok = bool(resp and resp.strip())
    out = {"model": "cc2", "ok": ok, "chars": len(resp or ""),
           "elapsed_s": round(time.time() - t0, 1), "response": resp or "",
           "note": "retry at timeout=900s after three 300s timeouts"}
except Exception as e:  # noqa: BLE001
    out = {"model": "cc2", "ok": False, "error": f"{type(e).__name__}: {e}",
           "elapsed_s": round(time.time() - t0, 1), "response": ""}
(LOGS / "cc2.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print(f"  [cc2] ok={out['ok']} chars={out.get('chars', 0)} {out['elapsed_s']}s"
      + (f" ERR={out.get('error')}" if not out["ok"] else ""))
