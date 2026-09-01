#!/usr/bin/env python3
"""Replay the Exp 53 control's escalated findings through the REPAIRED routing ladder.

THE QUESTION
------------
On 2026-08-01 the routing ladder went 0-for-25 on the zero-plant control: every
escalated finding was locked "irreducible" with the reason "no model produced a
runnable test". That reason was false — the ladder's prompt was code-only and no
model was ever given the target document's path or text. The prompt was repaired
at 1bd7605.

This replays the SAME findings through the REAL repaired code and asks whether
they resolve now. Paired, not a fresh run: a new experiment produces different
findings and can only give an unpaired number against a hard null of 0/25.

WHY IT CALLS THE RUNNER'S OWN FUNCTION RATHER THAN A HAND-WRITTEN COPY
----------------------------------------------------------------------
This project's recurring failure is unit-green-but-not-integration-live: a fix
verified in isolation while the live path silently disagreed (the 2026-06-08
wiring bug; the launcher config-drop class, six instances). So this calls
``_apply_routing`` itself, with ``cfg`` built by
``launcher_core.build_runner_config_from_dict`` on the real shipped config, which
exercises BOTH config-ingestion boundaries and the repaired prompt at once.

SAFETY
------
* Operates on an in-memory COPY of the archived registry. Writes nothing to the
  archive, the store, or any run directory.
* ``--dry-run`` (default) stubs the dispatch boundary: it CAPTURES the prompt
  each rung would have sent and spends nothing. Use it to prove the target path
  and text now reach the model before paying for anything.
* ``--live`` dispatches for real. Bounded: ``--max-findings`` (default 8) times
  the ladder's own rung cap.

Usage:
    python3 bench/tools/replay_routing_on_control.py            # dry run, free
    python3 bench/tools/replay_routing_on_control.py --live     # spends money
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

ARCHIVE = REPO / "bench/logs/exp53_control_zero_live_20260801T005649Z/runner_state.json"
CONFIG = REPO / "bench/exp53_configs/53_control_zero_live.json"


def load_env() -> None:
    """experiment_11_orchestrator sources .env only under __main__."""
    env = REPO / ".env"
    if not env.exists():
        return
    for line in env.read_text().splitlines():
        m = re.match(r"\s*(?:export\s+)?([A-Z0-9_]+)\s*=\s*(.+)", line)
        if m:
            os.environ.setdefault(m.group(1), m.group(2).strip().strip('"').strip("'"))


def build_registry(max_findings: int):
    """A registry holding the CONFIRMED set (needed for the ladder's dedup pass)
    plus the top-N escalated findings by severity."""
    from bench.reference_runner_v3 import FindingRegistry

    raw = json.loads(ARCHIVE.read_text())
    entries = raw.get("registry", {}).get("entries", {}) or raw.get("entries", {})

    confirmed = {k: v for k, v in entries.items()
                 if v.get("falsifier_verdict") == "CONFIRMED"}
    escalated = {k: v for k, v in entries.items()
                 if (v.get("escalated") or v.get("irreducible_escalation"))
                 and v.get("falsifier_verdict") != "CONFIRMED"}
    chosen = dict(sorted(escalated.items(),
                         key=lambda kv: -(kv[1].get("severity") or 0.0))[:max_findings])

    reg = FindingRegistry()
    for cid, e in {**confirmed, **chosen}.items():
        d = dict(e)
        # The ladder selects on `escalated`; the archive may carry only the
        # irreducible stamp from the earlier lock. Restore the selection flag and
        # clear the stale lock so this is a genuine re-attempt, not a replay of
        # the locked state.
        if cid in chosen:
            d["escalated"] = True
            d["irreducible_escalation"] = False
            d["hil_escalated"] = False
            d.pop("hil_reason", None)
            d.pop("error_routed", None)
        reg.entries[cid] = d
    return reg, set(chosen), set(confirmed)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="dispatch for real (spends money)")
    ap.add_argument("--max-findings", type=int, default=8)
    args = ap.parse_args()

    load_env()
    from bench import reference_runner_v3 as R
    from bench import launcher_core

    exp_cfg = json.loads(CONFIG.read_text())

    class _A:
        resume = False
    cfg = launcher_core.build_runner_config_from_dict(exp_cfg, _A())
    exp_config = launcher_core.load_experiment_config()

    print(f"  target      : {getattr(cfg, 'test_article', '?')}", flush=True)
    print(f"  routing_on  : {getattr(cfg, 'routing_enabled', None)}")
    print(f"  panel       : {[m.label for m in exp_config.models]}")

    reg, chosen, confirmed = build_registry(args.max_findings)
    print(f"  replaying   : {len(chosen)} escalated + {len(confirmed)} confirmed (dedup pool)")

    captured: list[dict] = []
    if not args.live:
        real = R.dispatch_to_model

        def _stub(mc, prompt, system, **kw):
            captured.append({"model": mc.label, "prompt": prompt, "system": system})
            return "", {}

        R.dispatch_to_model = _stub
    else:
        n = 0
        real = R.dispatch_to_model

        def _counting(mc, prompt, system, **kw):
            nonlocal n
            n += 1
            print(f"    dispatch {n}: {mc.label} ({len(prompt)} char prompt)", flush=True)
            captured.append({"model": mc.label, "prompt": prompt, "system": system})
            return real(mc, prompt, system, **kw)

        R.dispatch_to_model = _counting

    try:
        R._apply_routing(reg, 0, exp_config, cfg, str(REPO))
    finally:
        R.dispatch_to_model = real

    print("\n  ── PROMPT CHECK (the repair, in the live call path) ──")
    if not captured:
        print("    NO DISPATCH ATTEMPTED — the ladder did not select anything. "
              "Check routing_enabled and the escalated flag.")
    else:
        p = captured[0]["prompt"]
        s = captured[0]["system"]
        doc = Path(getattr(cfg, "test_article", ""))
        name = doc.name
        checks = [
            ("target path in prompt", name in p),
            ("target TEXT in prompt", len(p) > 5000),
            ("told to open by path", "open(" in p),
            ("system says PROSE DOCUMENT", "PROSE DOCUMENT" in s),
            ("NOT told to import the registry", "cdsfl_registry" not in s),
        ]
        for label, ok in checks:
            print(f"    [{'PASS' if ok else 'FAIL'}] {label}")

    resolved = [c for c in chosen if reg.entries[c].get("resolved_by_routing")]
    still = [c for c in chosen if reg.entries[c].get("irreducible_escalation")]
    print(f"\n  ── OUTCOME ──")
    print(f"    resolved by routing : {len(resolved)} / {len(chosen)}   (archive null: 0 / 25)")
    print(f"    still irreducible   : {len(still)} / {len(chosen)}")
    for c in resolved:
        print(f"      RESOLVED {c} by {reg.entries[c].get('resolved_by_routing')}")
    if not args.live:
        print("\n    DRY RUN — no model was called and nothing was spent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
