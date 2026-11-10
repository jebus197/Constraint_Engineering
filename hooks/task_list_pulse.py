#!/usr/bin/env python3
"""UserPromptSubmit hook: put the master task list's state in context, every turn.

Written 2026-09-09 for the CDSFL founder, who asked for the referring-back to be
mechanical: "I will keep referring back to it, as you should do (preferably
mechanically), until you can confirm all outstanding tasks are complete."

THE FAILURE THIS PREVENTS. The task list is 59 entries built from 121 recorded
items, and the assistant's record on remembering things unprompted is the reason
the file exists at all. A compaction discards the conversation; it does not
discard this line, because the line is injected fresh on every prompt.

WHY IT REPORTS TWO VOCABULARIES AND THEIR DISAGREEMENT. The founder asked, of two
proposed designs, "Can you not use them both to cross check the list?" -- and he
was right that they compose. `state` is the state of the TASK; `status` is note
standard Rule 20, the maturity of the WORK PRODUCT. Neither determines the other,
so a disagreement between them is a detectable fault rather than redundancy: an
entry marked DONE whose work is still PROPOSED is a task closed before it was
built. On its first run the cross-check found exactly that, and it was right.

MUST ALWAYS EXIT 0. A hook that blocks a prompt is far worse than a missing line.
Every failure path here is swallowed DELIBERATELY and for that reason alone; the
cost of silence is one absent context line, and the cost of noise is a session
that cannot accept input.
"""
import json
import sys
import pathlib
import importlib.util

CANDIDATES = [
    pathlib.Path.home() / "Developer_Projects" / "Constraint_Engineering",
]


def find_repo(payload):
    """Prefer the session's own cwd, fall back to the known checkout."""
    cwd = payload.get("cwd") or ""
    if cwd:
        p = pathlib.Path(cwd)
        for cand in [p, *p.parents]:
            if (cand / "scripts" / "task_list_markers.py").is_file():
                return cand
    for c in CANDIDATES:
        if (c / "scripts" / "task_list_markers.py").is_file():
            return c
    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    repo = find_repo(payload)
    if repo is None:
        return

    spec = importlib.util.spec_from_file_location(
        "tlm_pulse", repo / "scripts" / "task_list_markers.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["tlm_pulse"] = mod          # the dataclass needs this registered
    spec.loader.exec_module(mod)

    lst = repo / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
    line = mod.summarise(lst)
    ctx = f"[tasks] {line}"

    # ★ EVERY OPEN ENTRY WITH A SHORT DESCRIPTOR, 2026-11-10, HIS INSTRUCTION
    # TWICE OVER: "I already asked you when you print these labels, to include
    # a short descriptor, so I can know what you are talking about."
    #
    # WHY IT IS INJECTED RATHER THAN LOOKED UP. Note standard Rule 32 already
    # states the rule and `scripts/note_vagueness_lint.py` already implements
    # the predicate -- but Rule 32 is scoped to delivered DOCUMENTS, so it has
    # never been applied to chat, which is the surface he reads. Measured over
    # every assistant text block in the session transcripts: 8288 of 10496
    # entry codes printed with NO descriptor, 0.789634, Wilson
    # [0.781732, 0.797325]. The descriptor was missing because fetching it
    # cost a tool call; putting it in the turn's context makes printing one
    # free. Producer: scripts/a_bare_entry_code_in_chat_2026-11-10.py
    #
    # THE PREFIX `[tasks] ` IS PRESERVED EXACTLY, because
    # bench/tests/test_task_list_markers_2026-09-09.py asserts
    # `ctx.startswith("[tasks] ")`. The roster is a SECOND line, so that
    # assertion is untouched -- checked before editing, not after.
    try:
        roster = mod.open_roster(lst)
    except Exception:                      # noqa: BLE001 -- see MUST ALWAYS EXIT 0
        roster = ""
    if roster:
        ctx += ("\n[entries] print a code only WITH its descriptor — "
                + roster)

    print(json.dumps({
        "suppressOutput": True,
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": ctx,
        },
    }))


try:
    main()
except Exception:
    pass
sys.exit(0)
