#!/usr/bin/env python3
"""Stop gate: his words may not sit unread while a turn ends.

HIS RULING, 2026-10-25: *"we should implement a rule mechanically that compels
you to read from the record, rather than to just make assumptions."*

THE INCIDENT IT EXISTS FOR. On 2026-10-23 he annotated 2 of my own notes -- 8
annotations across `Progress_Report_And_Whether_The_List_Terminates_2026-10-19`
and `Why_sv_Was_Blocked_And_Twelve_Lost_Annotations_2026-10-19` -- and I told him
"0 decisions await you" without ever opening them. The statement was TRUE; the
register did hold zero. The basis was incomplete, which is the whole failure: I
read the index instead of the record.

WHY THIS CHECK AND NOT A NEW ONE. The instrument that eventually caught it already
existed -- `test_every_annotation_verdict_names_its_evidence_2026-10-17` refuses a
commit while any annotation of his in the window has no verdict row. It worked. It
fired only at COMMIT time, and a whole day passed with no commit. So the fix is
not a new detector; it is the existing one moved to the event that happens every
turn. Simplest sufficient, and it reuses a predicate already under test.

WHAT CLEARS IT. Giving the annotation a verdict row, which requires reading it.
Refreshing the manifest does NOT clear it, deliberately: a manifest refresh is an
acknowledgement that files changed, not that his words were read.

HOW IT CANNOT TRAP A SESSION. It refuses at most `MAX_REFUSALS` times per turn,
counted in its own state file, and `sys.exit(0)` on any exception. A gate that
fells the session is worse than the gap it guards.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
#: Overridable for the same reason as the FFAFP gate's counter: a test must not
#: write into his live ~/.claude, and a counter shared between runs makes a test
#: flaky. Found by FOLLOW on 2026-10-25 rather than by waiting for it to bite.
STATE = pathlib.Path(
    os.environ.get("CDSFL_RESPONSES_GATE_STATE")
    or pathlib.Path.home() / ".claude" / ".responses_freshness")
RECORD = REPO / "experimental_notes" / "data" / "annotation_verdicts_2026-10-17.json"
READER = REPO / "scripts" / "read_founder_responses_2026-10-11.py"

#: Same ceiling and the same reason as the FFAFP gate: give the owed read a few
#: chances, then yield loudly rather than risk a trapped session.
MAX_REFUSALS = 3


def _reader():
    import importlib.util
    spec = importlib.util.spec_from_file_location("_rfr_fresh", READER)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_rfr_fresh"] = m
    spec.loader.exec_module(m)
    return m


def unread() -> list[dict]:
    """His annotations in the window that carry no verdict row.

    A row marked `anchor_lost` does NOT count as coverage for a live annotation:
    that mark says his words vanished from the file, which is a different fact.
    """
    rec = json.loads(RECORD.read_text(encoding="utf-8"))
    have = {r["anchor"] for r in rec.get("rows", []) if not r.get("anchor_lost")}
    window = rec.get("window_from", "2026-10-01")
    r = _reader()
    out = []
    for a in r.annotations():
        if str(a.get("date", "")) < window:
            continue
        name = pathlib.Path(str(a["file"])).name
        anchor = f"{name}#{a['line_index']}"
        if anchor not in have:
            out.append({"anchor": anchor, "text": a["text"], "file": name})
    return out


def _shortest(p: pathlib.Path) -> str:
    """A display path that CANNOT raise.

    `relative_to` throws when `p` is not under `REPO`, which happens in any test
    fixture and would happen for a relocated record. The throw lands inside the
    refusal-message construction, where the module's top-level `except` converts
    it to `sys.exit(0)` -- so a path quirk would silently DISABLE the gate rather
    than report anything. Found by `test_the_ceiling_is_reachable...` on the very
    first run, which is the argument for driving a hook rather than reading it.
    """
    try:
        return str(p.relative_to(REPO))
    except ValueError:
        return str(p)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:                                  # noqa: BLE001
        return 0
    if not RECORD.is_file() or not READER.is_file():
        return 0                                       # not built here; say nothing

    counter = None
    refusals = 0
    try:
        STATE.mkdir(parents=True, exist_ok=True)
        counter = STATE / f"{payload.get('session_id') or 'session'}.refusals"
        if payload.get("stop_hook_active") and counter.is_file():
            refusals = int(counter.read_text(encoding="utf-8").strip() or "0")
        if refusals >= MAX_REFUSALS:
            print(f"[responses-gate] {refusals} refusal(s) issued for this turn, "
                  f"which is the ceiling. ALLOWING the stop so the session cannot "
                  f"be trapped -- but his words are still unread, and that is a "
                  f"real gap, not a pass.", file=sys.stderr)
            counter.write_text("0", encoding="utf-8")
            return 0
    except Exception as e:                             # noqa: BLE001
        print(f"[responses-gate SELF-CHECK] counter unusable "
              f"({type(e).__name__}: {e}); falling back to a single refusal.",
              file=sys.stderr)
        if payload.get("stop_hook_active"):
            return 0

    try:
        miss = unread()
    except Exception as e:                             # noqa: BLE001
        print(f"[responses-gate SELF-CHECK] could not read his folder "
              f"({type(e).__name__}: {e}); failing OPEN and allowing the stop. "
              f"The gate is broken, not the work.", file=sys.stderr)
        return 0

    if not miss:
        if counter is not None:
            try:
                counter.write_text("0", encoding="utf-8")
            except Exception:                          # noqa: BLE001
                pass
        return 0

    shown = miss[:6]
    print(
        f"[responses-gate] {len(miss)} ANNOTATION(S) OF HIS HAVE NO VERDICT ROW, "
        f"so they have not been read.\n"
        + "".join(f"    {a['anchor']}\n      \"{' '.join(a['text'].split())[:150]}\"\n"
                  for a in shown)
        + (f"    ... and {len(miss)-len(shown)} more\n" if len(miss) > len(shown) else "")
        + "  HIS RULING, 2026-10-25: a rule that compels reading from the record "
          "rather than assuming.\n"
          "  On 2026-10-23 he annotated 2 of my own notes and I answered \"0 "
          "decisions await you\" without opening them. True statement, incomplete "
          "basis.\n"
          "  READ THEM WITH THE READER, NEVER WITH grep:\n"
          "    python3 scripts/read_founder_responses_2026-10-11.py --json\n"
          "  then record a verdict row for each in\n"
          f"    {_shortest(RECORD)}\n"
          "  Refreshing the manifest does NOT clear this: that acknowledges a file "
          "changed, not that his words were read.\n"
          f"  This gate refuses up to {MAX_REFUSALS} times per turn, then yields "
          f"loudly.",
        file=sys.stderr)
    if counter is not None:
        try:
            counter.write_text(str(refusals + 1), encoding="utf-8")
        except Exception:                              # noqa: BLE001
            pass
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:                                  # noqa: BLE001
        sys.exit(0)
