# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'joint_severity_spec_is_uncomputable_2026-11-04', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 0fa83c0496d3720e0c52ab12c15519285e2c1623b6a25ab3f0359eb2c5169937
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""PRODUCER: is `falsifier_verdict == "REFUTED"` terminal on one canonical id?

THE DEBT THE `cc2` SEAT NAMED AGAINST ITSELF IN ROUND 1, verbatim: *"My fix
treats REFUTED as permanent annihilation. Named property: count of
REFUTED->CONFIRMED transitions on one canonical id. I did not measure it, and
it is the weakest joint in this answer."* This measures it three ways: what the
archive records, what the live write sites permit, and what happens when the
real reattachment function is actually called on a REFUTED entry.

WHY THE ANSWER DECIDES A FIX. An annihilator-only severity
(`V == 0 -> 0`, every other value passed through) is only safe if it reads the
verdict AT CALL TIME. If a REFUTED verdict can later become CONFIRMED, a fix
that STAMPS zero onto the entry would permanently delete a finding that the
harness later proves real; a fix that RECOMPUTES from the current field each
round restores it. The two are indistinguishable until this is measured.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from bench.reference_runner_v3 import (  # noqa: E402
    CRITICAL_SEVERITY_THRESHOLD, FindingRegistry,
    record_in_round_falsifier_reattachments,
)

TERMINAL = {"MERGED", "CLOSED", "REFUTED", "DUPLICATE"}
FAILURES: list[str] = []


def distinct(root: pathlib.Path):
    seen = set()
    for p in sorted(root.rglob("runner_state.json")):
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        if h in seen:
            continue
        seen.add(h)
        try:
            d = json.loads(p.read_text())
        except Exception:                        # noqa: BLE001
            continue
        yield p, ((d.get("registry") or {}).get("entries") or {})


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--logs", default=str(REPO / "bench" / "logs"))
    args = ap.parse_args(argv)

    # ---- (1) WHAT THE ARCHIVE RECORDS -----------------------------------
    n = refuted = refuted_nonterminal = refuted_crit = refuted_crit_nonterm = 0
    log_from_refuted = 0
    confirmed_after_refuted = 0
    verdict_status_disagree = 0
    for _p, ents in distinct(pathlib.Path(args.logs)):
        for e in ents.values():
            if not isinstance(e, dict):
                continue
            n += 1
            v = str(e.get("falsifier_verdict") or "").strip().upper()
            st = str(e.get("status") or "").strip().upper()
            sev = float(e.get("severity") or 0.0)
            if v == "REFUTED":
                refuted += 1
                if st not in TERMINAL:
                    refuted_nonterminal += 1
                if sev >= CRITICAL_SEVERITY_THRESHOLD:
                    refuted_crit += 1
                    if st not in TERMINAL:
                        refuted_crit_nonterm += 1
                if st == "CONFIRMED":
                    verdict_status_disagree += 1
            hops = [h for h in (e.get("status_log") or [])
                    if isinstance(h, dict)
                    and str(h.get("from") or "").upper() == "REFUTED"]
            if hops:
                log_from_refuted += 1
                if any(str(h.get("to") or "").upper() == "CONFIRMED" for h in hops):
                    confirmed_after_refuted += 1
    print(f"[archive] entries                                    : {n}")
    print(f"[archive] falsifier_verdict == REFUTED               : {refuted}")
    print(f"[archive]   ... with NON-TERMINAL status (re-servable): "
          f"{refuted_nonterminal}")
    print(f"[archive]   ... asserted-critical (>= "
          f"{CRITICAL_SEVERITY_THRESHOLD})            : {refuted_crit}")
    print(f"[archive]   ... asserted-critical AND non-terminal    : "
          f"{refuted_crit_nonterm}")
    print(f"[archive] status_log hop FROM REFUTED (any target)    : "
          f"{log_from_refuted}")
    print(f"[archive] status_log hop REFUTED -> CONFIRMED         : "
          f"{confirmed_after_refuted}")
    print(f"[archive] verdict REFUTED while status CONFIRMED      : "
          f"{verdict_status_disagree}")

    # ---- (2) WHAT THE LIVE WRITE SITES PERMIT, BY EXECUTION ---------------
    # `record_in_round_falsifier_reattachments` skips on `status` in
    # {MERGED, CLOSED, REFUTED, DUPLICATE} -- NOT on `falsifier_verdict`. So an
    # entry already carrying a REFUTED verdict with a live status is re-served.
    # Called for real below; nothing here is a re-implementation.
    def _entry(status: str, sev: float = 0.9) -> FindingRegistry:
        reg = FindingRegistry()
        reg.entries = {"C0001": {
            "canonical_id": "C0001", "source_model": "SEAT",
            "source_aliases": [], "severity": sev,
            "description": "synthetic probe", "proposed_fix": "",
            "status": status, "open_since_round": 0,
            "last_status_change_round": 0, "verdicts": [],
            "verified": False, "escalated": False, "flaw_class": 1,
            "falsifier_verdict": "REFUTED",
            "falsifier_code": "assert True",
        }}
        return reg

    demo = "FALSIFIER: C0001\n```python\nassert False, 'defect present'\n```"
    reg = _entry("OPEN")
    stats = record_in_round_falsifier_reattachments(reg, {"SEAT": demo}, 1)
    after = reg.entries["C0001"]["falsifier_verdict"]
    print(f"\n[executed] REFUTED verdict + OPEN status, demonstrating falsifier")
    print(f"[executed]   verdict before : REFUTED")
    print(f"[executed]   verdict after  : {after}")
    print(f"[executed]   stats          : executed={stats.get('executed')} "
          f"cleared={stats.get('cleared')}")
    if after != "CONFIRMED":
        FAILURES.append("a REFUTED verdict on a live entry did NOT become "
                        f"CONFIRMED (got {after}) -- the transition this "
                        "measurement claims is reachable did not occur")

    reg2 = _entry("REFUTED")
    stats2 = record_in_round_falsifier_reattachments(reg2, {"SEAT": demo}, 1)
    after2 = reg2.entries["C0001"]["falsifier_verdict"]
    print(f"[executed] REFUTED verdict + REFUTED status (terminal)")
    print(f"[executed]   verdict after  : {after2} "
          f"(skipped_terminal={stats2.get('skipped_terminal')})")
    if after2 != "REFUTED":
        FAILURES.append("a terminal-status entry was re-served")

    print("\n[reading] REFUTED is terminal ONLY through `status`, never through "
          "`falsifier_verdict`. A fix that STAMPS zero onto the entry would be "
          "wrong; one that RECOMPUTES from the current field every round is "
          "restored automatically by the transition above.")
    if FAILURES:
        for f in FAILURES:
            print("FAILED:", f)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
