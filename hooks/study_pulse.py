#!/usr/bin/env python3
"""UserPromptSubmit hook: keep the programme of study's PURPOSE in context.

WHY THIS EXISTS, and it is not a reminder for its own sake. The simulated runs
were repeatedly described by their success criterion -- 3 clean convergences --
rather than by WHY they are run, which is to measure whether the fixes of the
last 15+ days actually work. The founder had to point this out on 2026-10-03 and
he was substantially right: arms 1 to 4 had each run twice, and arm 5, the only
arm that answers the effectiveness question, had NEVER run. The purpose was lost
across compactions because nothing carried it.

A compaction discards the conversation. It does not discard this line, because
the line is injected fresh on every prompt from a COMMITTED file.

IT EXPIRES. When every measurement in the file carries both a result and a
headline, `status` becomes CLOSED and this hook falls silent for good. A
mechanism that cannot stop is one people learn to ignore, which is this project's
own recorded sentence about 3 different alarms.

MUST ALWAYS EXIT 0. A hook that blocks a prompt is far worse than a missing line;
every failure path below is swallowed deliberately.
"""
import json
import os
import pathlib
import sys

DEFAULT_STUDY = (pathlib.Path.home() / "Developer_Projects"
                 / "Constraint_Engineering" / "experimental_notes"
                 / "STUDY_IN_FLIGHT.json")


def register_path() -> pathlib.Path:
    """The register this hook reads, overridable so it can be TESTED.

    Added 2026-10-03 because the first version hard-coded the path, which made
    the hook impossible to execute against a planted register -- so the only
    available guard would have been a test asserting on this file's source
    text, and `execute-do-not-grep` (2026-09-04) says such a test establishes
    only that the file describes itself consistently. The default is unchanged;
    `CDSFL_STUDY_REGISTER` is read only when set and non-empty.
    """
    override = os.environ.get("CDSFL_STUDY_REGISTER", "").strip()
    return pathlib.Path(override) if override else DEFAULT_STUDY


def main():
    try:
        study = register_path()
        if not study.is_file():
            return
        d = json.loads(study.read_text())
        if str(d.get("status", "")).upper() != "OPEN":
            return                      # expired: say nothing, for good
        ms = d.get("measurements") or []
        outstanding = [m for m in ms
                       if m.get("result") is None or m.get("headline") is None]
        if not outstanding:
            print(json.dumps({"suppressOutput": False, "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext":
                    "[study] every measurement now has a result and a headline. "
                    "Set STUDY_IN_FLIGHT.json status to CLOSED to retire this hook."}}))
            return
        names = ", ".join(m.get("id", "?") for m in outstanding)
        msg = (f"[study] PROGRAMME OF STUDY IS OPEN — {len(outstanding)} of "
               f"{len(ms)} measurements outstanding: {names}.\n"
               f"  WHY THE RUNS EXIST: {d.get('rationale','')}\n"
               f"  Success = {d.get('run_conditions',{}).get('success','?')}; "
               f"fixes fold forward. Full scope: "
               f"experimental_notes/CDSFL_Programme_of_Study_Full_Scope_2026-09-21.md")
        print(json.dumps({"suppressOutput": False, "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit", "additionalContext": msg}}))
    except Exception:
        pass


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
