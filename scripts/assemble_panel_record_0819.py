#!/usr/bin/env python3
"""Assemble the FULL, UNFILTERED panel record. No summarising in place of output.

Standing founder directive: external reviews are presented in full, verbatim,
with file/line references intact. A summary may accompany the full text; it may
never replace it. This script writes every response exactly as returned.
"""
import json, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _cli_help import answer_help  # noqa: E402

# `--help` MUST NOT ACT, AND ON THIS SCRIPT IT DESTROYED 54,480 BYTES.
# Measured 2026-09-11 in a throwaway clone: `--help` rewrote
# `experimental_notes/Panel_Enforcement_Prose_FULL_RECORD_2026-08-19.md` from
# 55,814 bytes to 1,334 and exited 0. This script REGENERATES a panel record
# from `bench/logs/`, which `.gitignore:41` excludes, so in any clone the source
# is empty and every seat is written back as "NO RESPONSE FILE" -- a verbatim
# record of a 5-model review replaced by a stub, silently, by a flag that is
# supposed to print a sentence.
#
# THE MORNING'S `--help` SWEEP REPORTED 0 OF 54 AND WAS CLEAN, because its
# population is MEASUREMENT scripts and this is an ACTION script. 122 scripts are
# tracked. The 68 the sweep does not cover are exactly the ones where a `--help`
# that acts is destructive rather than merely rude. A false zero in the
# POPULATION rather than in the matcher.
answer_help(__doc__, __file__, sys.argv[1:])

LOGS = pathlib.Path("bench/logs/confer_enforcement_prose_2026-08-19")
ORDER = [("ge", "Gemini 3.1 Pro Preview", "OpenRouter"),
         ("cgpt", "ChatGPT GPT-5.5", "OpenRouter"),
         ("cx", "Codex GPT-5.5", "OpenRouter"),
         ("ds", "DeepSeek V4 Pro", "DeepSeek direct"),
         ("cc2", "Claude Opus 4.7", "Claude CLI, Max subscription")]

out = ["# Panel Review — Enforcement, Prose Targets, and the Runway to BR2",
       "",
       "**19 August 2026, dispatched 09:19 BST.** Five models, no compelled convergence.",
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

dest = pathlib.Path("experimental_notes/Panel_Enforcement_Prose_FULL_RECORD_2026-08-19.md")
# HOISTED, 2026-09-07. A backslash inside an f-string replacement field is PEP 701
# and parses only on Python 3.12+; before that it is a hard SyntaxError. Joining
# once is also the honest form -- the previous line already built the same string,
# so the report counted characters in a SECOND join rather than in what was written.
_written = "\n".join(out)
dest.write_text(_written, encoding="utf-8")
print(f"{dest}  —  {len(_written):,} chars, {present}/{len(ORDER)} panellists")
