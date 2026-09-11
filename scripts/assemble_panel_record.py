#!/usr/bin/env python3
"""Assemble the FULL, UNFILTERED panel record. No summarising in place of output.

Standing founder directive: external reviews are presented in full, verbatim,
with file/line references intact. A summary may accompany the full text; it may
never replace it. This script writes every response exactly as returned.
"""
import json, pathlib

# `--help` MUST NOT ACT, AND ON A SIBLING OF THIS SCRIPT IT DESTROYED 54,480
# BYTES. Measured 2026-09-11: `--help` on `scripts/assemble_panel_record_0819.py`
# rewrote a 55,814-byte verbatim panel record down to 1,334 and exited 0, because
# the flag fell through to the script's ordinary work.
#
# GUARDED BY `__main__`, WHICH THE FIRST VERSION WAS NOT. Calling it at module
# level meant that any test IMPORTING this module handed pytest's own argv to the
# help handler, which refused it and exited 2 -- 12 failures and errors in the
# next clone run. The established form in this directory guards the call, and
# importing the module then reaches exactly the code it reached before.
if __name__ == "__main__":
    try:
        from _cli_help import answer_help   # scripts/ is sys.path[0] when run directly
    except ImportError:
        # A COPY OUTSIDE scripts/, which is how the mutation harness runs
        # this file: it writes the mutant to `.mutants/` where `_cli_help`
        # is not importable. Crashing there would make every mutant
        # "caught" for the wrong reason -- a crashing mutant produces no
        # output and every `not in` check passes. The guard protects real
        # invocations; a mutant copy is not one.
        pass
    else:
        answer_help(__doc__, __file__)


def main() -> None:
    """The assembly, moved out of module scope so IMPORTING this file does nothing.

    IT USED TO RUN AT IMPORT, AND THAT DESTROYED THE RECORD IT BUILDS.
    `bench/tests/test_operational_scripts.py` probes each script by importing it
    (`spec_from_file_location`), and in a clone `bench/logs/` is empty, so the
    import rebuilt this note with every seat as "NO RESPONSE FILE" -- 55,814
    bytes replaced by 1,334, on every clone run.

    Guarding only `--help` was not enough and the next clone run said so: the
    flag was never the only way in. A script whose work runs on import has no
    safe way to be inspected, and inspecting scripts is something this suite does
    deliberately.
    """
    LOGS = pathlib.Path("bench/logs/confer_stage1_audit_2026-08-18")
    ORDER = [("ge", "Gemini 3.1 Pro Preview", "OpenRouter"),
             ("cgpt", "ChatGPT GPT-5.5", "OpenRouter"),
             ("cx", "Codex GPT-5.5", "OpenRouter"),
             ("ds", "DeepSeek V4 Pro", "DeepSeek direct"),
             ("cc2", "Claude Opus 4.7", "Claude CLI, Max subscription")]

    out = ["# Panel Review — Stage 1 Audit and the Path to Bench Run 2",
           "",
           "**18 August 2026, dispatched 14:37 BST.** Five models, no compelled convergence.",
           "Brief: 46,459 characters carrying two primary-source packs (raw code with line",
           "numbers, raw measurement tables) plus a quarantined ledger of CC1's claims.",
           "",
           "**This file is the COMPLETE, VERBATIM record.** Every response appears exactly as",
           "returned, unedited and untrimmed. Analysis and synthesis live in the companion",
           "note; nothing here is summarised.",
           "",
           "---", ""]

    present = 0
    for key, name, route in ORDER:
        f = LOGS / f"{key}.json"
        if not f.is_file():
            out += [f"## {name} (`{key}`) — NO RESPONSE FILE", "",
                    "This model produced no response file. Absence is recorded, not hidden.",
                    "", "---", ""]
            continue
        d = json.loads(f.read_text())
        # COUNT SUCCESS, NOT FILE EXISTENCE. The first version of this script
        # incremented on the file being present and reported "5 of 5 panellists"
        # while one of those files was a FAILURE record (ok=false, three 300s
        # timeouts). A tally that cannot distinguish a response from a failure is
        # the governing failure mode of this project rendered in six characters.
        if d.get("ok") and (d.get("response") or "").strip():
            present += 1
        hdr = (f"## {name} (`{key}`) — {route}", "",
               f"- returned: **{'yes' if d.get('ok') else 'NO — THIS IS A FAILURE RECORD'}**",
               f"- elapsed: {d.get('elapsed_s')}s",
               f"- length: {d.get('chars', 0):,} characters")
        out += list(hdr)
        if d.get("note"):
            out.append(f"- note: {d['note']}")
        if d.get("error"):
            out.append(f"- error: `{d['error']}`")
        out += ["", "### Verbatim response", ""]
        out.append(d.get("response") or "*(empty)*")
        out += ["", "---", ""]

    out += ["", f"*{present} of {len(ORDER)} panellists returned a usable response (counted by ok=true AND non-empty text, not by file presence).*", "",
            "Written under CDSFL note standard v1.4 (13 August 2026, Rule 24 added 16 August)."]

    dest = pathlib.Path("experimental_notes/Panel_Stage1_Audit_FULL_RECORD_2026-08-18.md")
    # HOISTED, 2026-09-07. A backslash inside an f-string replacement field is PEP 701
    # and parses only on Python 3.12+; before that it is a hard SyntaxError. Joining
    # once is also the honest form -- the previous line already built the same string,
    # so the report counted characters in a SECOND join rather than in what was written.
    _written = "\n".join(out)
    dest.write_text(_written, encoding="utf-8")
    print(f"{dest}  —  {len(_written):,} chars, {present}/{len(ORDER)} panellists")


if __name__ == "__main__":
    main()
