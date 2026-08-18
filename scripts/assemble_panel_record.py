#!/usr/bin/env python3
"""Assemble the FULL, UNFILTERED panel record. No summarising in place of output.

Standing founder directive: external reviews are presented in full, verbatim,
with file/line references intact. A summary may accompany the full text; it may
never replace it. This script writes every response exactly as returned.
"""
import json, pathlib, sys

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
dest.write_text("\n".join(out), encoding="utf-8")
print(f"{dest}  —  {len('\n'.join(out)):,} chars, {present}/{len(ORDER)} panellists")
