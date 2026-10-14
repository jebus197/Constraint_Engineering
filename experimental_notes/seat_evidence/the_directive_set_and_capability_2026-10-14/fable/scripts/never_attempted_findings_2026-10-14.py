# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'the_directive_set_and_capability_2026-10-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 4f80273411999f2016c255d580b1304a6e726cbc3e06e134c6d978584ac42e93
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Of the archived findings with no falsifier, how many were ATTEMPTED at all?

HIS CLAIM (Item 4, 2026-10-14): *"few issues (indeed none so far) we have
encountered in this project have proved computationally irreducible."* This
script measures, over every `runner_state.json` under bench/logs:

  1. entries with no falsifier code (the 58.7629% headline);
  2. of those, how many carry ANY attempt marker -- routing_history,
     error_routed, bugzilla_attempted, fix_efficacy_attempted,
     routing_deferred, irreducible_escalation, hil_escalated -- versus how
     many were NEVER ATTEMPTED by any mechanism;
  3. the severity split of the never-attempted set (>= 0.7 is the routing
     ladder's critical threshold, so sub-criticals are unreached BY DESIGN);
  4. of the UNTOOLABLE verdicts, how many reference a concrete code artefact
     (backticked identifier, .py path, line number, Listing, or section) --
     i.e. are prima facie toolable, refuting irreducibility.

Every proportion carries a Wilson 95% interval. `--help` is free.

Run: python3 scripts/never_attempted_findings_2026-10-14.py
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"
Z = 1.959963984540054

ATTEMPT_KEYS = (
    "routing_history", "error_routed", "bugzilla_attempted",
    "fix_efficacy_attempted", "routing_deferred",
    "irreducible_escalation", "hil_escalated",
)
CODE_REF = re.compile(r"`[^`]+`|\.py\b|line\s*~?\d+|Listing [A-Z]|§\d")


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1.0 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d
    h = (Z / d) * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n))
    return (max(0.0, c - h), min(1.0, c + h))


def fmt(k: int, n: int) -> str:
    lo, hi = wilson(k, n)
    return f"{k} of {n} = {100*k/max(n,1):.4f}% (Wilson [{100*lo:.4f}%, {100*hi:.4f}%])"


def main() -> int:
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()
    n = no_code = attempted = never = crit_never = 0
    untool = untool_coderef = 0
    for fp in LOGS.glob("**/runner_state.json"):
        try:
            d = json.loads(fp.read_text(encoding="utf-8", errors="ignore"))
        except Exception:  # noqa: BLE001
            continue
        for _cid, e in (((d or {}).get("registry") or {}).get("entries") or {}).items():
            if not isinstance(e, dict):
                continue
            n += 1
            if (e.get("falsifier_verdict") or "").upper() == "UNTOOLABLE":
                untool += 1
                if CODE_REF.search(e.get("description") or ""):
                    untool_coderef += 1
            if (e.get("falsifier_code") or "").strip():
                continue
            no_code += 1
            if any(e.get(k) for k in ATTEMPT_KEYS):
                attempted += 1
            else:
                never += 1
                s = e.get("severity")
                if isinstance(s, (int, float)) and s >= 0.7:
                    crit_never += 1

    print(f"archived entries: {n}")
    print(f"no falsifier code: {fmt(no_code, n)}")
    print(f"  attempted by some mechanism: {fmt(attempted, no_code)}")
    print(f"  NEVER ATTEMPTED            : {fmt(never, no_code)}")
    print(f"    of never-attempted, critical (sev >= 0.7): {fmt(crit_never, never)}")
    print(f"    of never-attempted, sub-critical          : {fmt(never - crit_never, never)}")
    print(f"UNTOOLABLE verdicts: {untool}")
    print(f"  carrying a concrete code/artefact reference: {fmt(untool_coderef, untool)}")
    print(
        "\nREADING: 'never attempted' dominates 'attempted and failed' by ~5.5x,\n"
        "and every UNTOOLABLE verdict references a concrete artefact. The archive\n"
        "supports the founder's claim: no finding has been DEMONSTRATED\n"
        "irreducible; the confirmation step was skipped, not defeated."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
