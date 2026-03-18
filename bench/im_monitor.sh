#!/bin/bash
# CE Confer Monitor — shows last 5 confer exchanges, formatted
cd /Users/georgejackson/Developer_Projects/Project_Genesis
python3 << 'PYEOF'
import json
from pathlib import Path

state = json.loads(Path("cw_handoff/im_state.json").read_text())

msgs = []
for stream in ["cc", "cx"]:
    for m in state.get(stream, []):
        if "CE confer" in m.get("msg", "") or "confer" in m.get("msg", "").lower():
            msgs.append({"ts": m["ts"], "who": stream.upper(), "msg": m["msg"]})

msgs.sort(key=lambda m: m["ts"], reverse=True)

if not msgs:
    print("No confer messages yet.")
else:
    print("=== CE CONFER LOG (last 5) ===")
    print()
    for m in msgs[:5]:
        # Extract verdict from message
        text = m["msg"]
        verdict = ""
        for v in ["STOP", "CONTINUE", "AGREE", "DISAGREE"]:
            if f"Verdict: {v}" in text or f"verdict: {v}" in text or f"VERDICT: {v}" in text:
                verdict = v
                break
        # Extract task ID
        task = ""
        if "task " in text:
            idx = text.index("task ") + 5
            task = text[idx:idx+6].strip().rstrip(",")

        print(f"  {m['ts']}  {m['who']}  task={task}  verdict={verdict}")

    print()
    print(f"  Total confer messages: {len(msgs)}")
PYEOF
