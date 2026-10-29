#!/usr/bin/env python3
"""Derive the orchestrator's specification from what CC1's role ACTUALLY is.

HIS INSTRUCTION, 2026-10-19, recorded as `fr:047a5b656a64`: *"Primarily the
orchestrator should perform all of the functions you currently perform. But in
order to build a specification, perhaps you should consider deeply what your
current role is and then define it as a specification?"*

WHY THIS IS A SCRIPT AND NOT AN ESSAY. *Considering deeply* what my role is would
produce an account of what I BELIEVE I do, and this project's record is that such
accounts are wrong in a particular direction: they describe the intended design
rather than the live behaviour. 11 confirmed defects since 2026-08-01 were
additions that did nothing, and in every case a description existed saying
otherwise. So the role is DERIVED from 3 things that cannot flatter it:

  1. THE GATES THAT CAN REFUSE ME. A hook that exits non-zero is a hard bound on
     the role, whatever any document says. These are enumerated by reading the
     registrations, not by listing the files, because a file present and
     unregistered binds nothing -- which is exactly how
     `work_not_narrate.py` sat parked and fired on nothing for 47 days.
  2. THE DECISIONS RESERVED TO HIM. Every `NEEDS_PERMISSION` category in
     `scripts/blocker_triage.py` is a decision the role may NOT take, and it is
     a committed list rather than a recollection.
  3. THE INSTRUMENTS THE ROLE IS REQUIRED TO RUN. Taken from the MC command
     definitions the hook injects, which are the same text every turn receives.

WHAT IT DELIBERATELY DOES NOT DO. It does not propose the orchestrator's design,
and it does not assert that CC1's present role is the right one. It reports what
the role IS so that a specification can be written against evidence, and so that
anything the specification adds is visibly an addition rather than a description.

READ-ONLY.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
USER_HOOKS = pathlib.Path.home() / ".claude" / "hooks"
SETTINGS = pathlib.Path.home() / ".claude" / "settings.json"


def registered_hooks() -> dict:
    """Which hooks are REGISTERED, which is what binds, versus merely present.

    A file on disk binds nothing. `work_not_narrate.py` was renamed in its
    registration to `_PARKED_Stop_2026-09-11` and fired on nothing for 47 days
    while its own guard passed a parked entry by design.
    """
    out = {"registered": [], "present_not_registered": [], "error": ""}
    present = set()
    for d in (USER_HOOKS, REPO / "hooks"):
        if d.is_dir():
            present |= {p.name for p in d.glob("*.py")}
    try:
        cfg = json.loads(SETTINGS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        out["error"] = f"{type(exc).__name__}: {exc}"
        out["present_not_registered"] = sorted(present)
        return out
    blob = json.dumps(cfg.get("hooks", {}))
    events = {}
    for event, entries in (cfg.get("hooks") or {}).items():
        for entry in entries if isinstance(entries, list) else []:
            for h in (entry.get("hooks") or []):
                cmd = str(h.get("command", ""))
                for name in present:
                    if name in cmd:
                        events.setdefault(name, []).append(event)
    out["registered"] = sorted((n, sorted(set(ev))) for n, ev in events.items())
    out["present_not_registered"] = sorted(present - set(events))
    #: A PARKED REGISTRATION IS NOT A REGISTRATION. The key is renamed rather
    #: than removed, so it survives a search for the file name.
    out["parked_keys"] = sorted(re.findall(r'"(_PARKED_[^"]+)"', blob))
    return out


def reserved_decisions() -> list[tuple[str, str]]:
    """Decisions the role may NOT take, read from the triage's committed list."""
    src = (REPO / "scripts" / "blocker_triage.py").read_text(encoding="utf-8")
    block = src[src.index("NEEDS_PERMISSION"):]
    block = block[:block.index("\n]")]
    out = []
    for m in re.finditer(r'\(\s*"([A-Z_]+)",\s*re\.compile\(', block):
        label = m.group(1)
        tail = block[m.end():]
        why = re.search(r'\n\s*"([^"]{10,})"\s*\)', tail)
        out.append((label, (why.group(1) if why else "").strip()))
    return out


def required_instruments() -> dict:
    """What every turn is told it must run, from the MC hook's own text."""
    hook = USER_HOOKS / "mc_commands.py"
    if not hook.is_file():
        return {"error": f"absent: {hook}"}
    t = hook.read_text(encoding="utf-8")
    tools = sorted(set(re.findall(
        r"\b(SymPy|z3|SciPy|NumPy|statsmodels|mpmath|pint|Wolfram)\b", t)))
    steps = sorted(set(re.findall(r"\b(FIND|FOLLOW|ANALYSE|FIX|P-PASS)\b", t)))
    return {"stem_tools_named": tools, "ffafp_steps_named": steps,
            "two_tool_rule": "cross-verified" in t or "TWO tools" in t}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    report = {
        "hooks": registered_hooks(),
        "reserved_decisions": reserved_decisions(),
        "required_instruments": required_instruments(),
    }
    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    h = report["hooks"]
    print("== the orchestrator's role, derived ==")
    print()
    print("1. GATES THAT CAN REFUSE THE ROLE (registered, therefore binding)")
    if h["error"]:
        print(f"   settings unreadable: {h['error']}")
    for name, events in h["registered"]:
        print(f"   {name:<34} {', '.join(events)}")
    print(f"   present but NOT registered, so binding nothing: "
          f"{len(h['present_not_registered'])}")
    for n in h["present_not_registered"]:
        print(f"     {n}")
    if h.get("parked_keys"):
        print(f"   PARKED registration key(s) found: {h['parked_keys']}")
        print("     a parked key survives a search for the file name and binds nothing")
    print()
    print("2. DECISIONS RESERVED TO HIM (the role may not take these)")
    for label, why in report["reserved_decisions"]:
        print(f"   {label:<14} {why[:88]}")
    print()
    print("3. INSTRUMENTS THE ROLE IS REQUIRED TO RUN")
    ri = report["required_instruments"]
    if "error" in ri:
        print(f"   {ri['error']}")
    else:
        print(f"   STEM tools named : {', '.join(ri['stem_tools_named'])}")
        print(f"   FFAFP steps named: {', '.join(ri['ffafp_steps_named'])}")
        print(f"   2-tool cross-verification rule present: {ri['two_tool_rule']}")
    print()
    print("WHAT THIS IS NOT. It reports what the role IS. It proposes no design,")
    print("and it does not claim the present role is the right one -- so anything")
    print("a specification adds is visibly an addition rather than a description.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
