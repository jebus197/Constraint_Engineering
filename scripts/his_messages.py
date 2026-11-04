#!/usr/bin/env python3
"""The ONE reader for what the founder typed. Both records, one list.

WHY THIS EXISTS, AND IT IS A DEFECT FOUND BY ITS OWN VICTIM. The harness stores
a message the founder types while a turn is already running DIFFERENTLY from one
typed at the prompt:

  * at the prompt  -> an entry with `type: "user"` and the text in
                      `message.content`;
  * mid-turn       -> an entry with `type: "queue-operation"`,
                      `operation: "enqueue"`, and the text in a TOP-LEVEL
                      `content` key, with no `message` dict at all and no
                      `promptSource` field.

Every instrument in this repository read the first shape only. Measured
2026-11-03 over the whole transcript corpus: of 1,421 distinct messages of his,
1,120 are recorded both ways, 95 only as `type: "user"`, and **206 ONLY as a
`queue-operation` -- 0.144968, Wilson 95% [0.127620, 0.164231]**.

THE LOSS WAS REALISED, NOT HYPOTHETICAL, AND IT COST A FALSE CLAIM ABOUT HIM.
`scripts/a_compaction_summary_can_invent_his_question_2026-11-03.py` was written
the same day to check whether a compaction summary had INVENTED a question of
his about `v_bar`. Its denominator is every entry whose `promptSource == "sdk"`,
which a `queue-operation` entry does not carry. It reported the token appearing
**0 times in 1,719 of his typed messages** and concluded the summary made it up.
He asked it directly at 2026-11-03T03:56:55 -- *"What is v-bar? I have never
heard of it before? Is it part of the mathematical model?"* -- typed mid-turn.
So the instrument built to catch exactly this class of miss was itself blind to
14.5% of his words, and told me he had never asked something he asked 19 hours
earlier. That claim is withdrawn.

WHAT THIS DELIBERATELY DOES NOT DO. It does not touch delivery. The harness
hands a mid-turn message to the model inside a `<system-reminder>` with
`renderedRole: "system"`, and that is a property of the tool rather than of this
repository. It is reported in task entry B102 and not repaired here.

THE EXCLUSIONS ARE NAMED, ONE PREDICATE EACH, so a count built on this reader
can be argued with rather than trusted. Several harness shapes arrive in the
same roles and are not his words at all: task notifications the harness queues
to itself, the `cy` heartbeat prompt this project generates, compaction
summaries, interrupt markers, local slash-command output and Stop-hook echoes.
Measured over the corpus, those account for 3,230 entries.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
from typing import Iterator, NamedTuple

TRANSCRIPTS = (pathlib.Path.home()
               / ".claude/projects/-Users-georgejackson-Developer-Projects")

#: Each entry is (reason, predicate over the decoded text). A shape excluded
#: here is NOT his writing; the reason travels with the rule so a drop can be
#: audited instead of taken on faith.
NOT_HIS_WRITING = (
    ("task notification", lambda t: "<task-notification>" in t),
    ("cy heartbeat", lambda t: t.startswith("cy HEARTBEAT")),
    ("compaction summary",
     lambda t: t.startswith("This session is being continued")),
    ("interrupt marker", lambda t: t.startswith("[Request interrupted")),
    ("caveat block", lambda t: t.startswith("Caveat:")),
    ("local command",
     lambda t: "<command-name>" in t or "<local-command-stdout>" in t),
    ("stop hook echo", lambda t: t.startswith("Stop hook feedback:")),
)


class Message(NamedTuple):
    """One thing he typed, with where it was found."""
    ts: str
    text: str
    record: str          # "prompt" or "queued"
    file: str


def why_not_his(text: str) -> str | None:
    """The NAMED reason this text is not his writing, or None."""
    for reason, pred in NOT_HIS_WRITING:
        if pred(text):
            return reason
    return None


def _text_of_user_entry(entry: dict) -> str:
    msg = entry.get("message") or {}
    content = msg.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(b.get("text", "") for b in content
                        if isinstance(b, dict) and b.get("type") == "text")
    return ""


def iter_messages(transcripts: pathlib.Path | None = None
                  ) -> Iterator[Message]:
    """Every message of his, from BOTH records, in file order.

    A message typed mid-turn is usually recorded twice -- once when queued and
    once when absorbed -- so callers wanting DISTINCT messages should use
    `distinct()` rather than deduplicating by hand.
    """
    root = transcripts or TRANSCRIPTS
    if not root.is_dir():
        return
    for path in sorted(root.glob("*.jsonl")):
        with path.open(errors="ignore") as fh:
            for raw in fh:
                queued = '"queue-operation"' in raw
                prompt = '"type":"user"' in raw or '"type": "user"' in raw
                if not (queued or prompt):
                    continue
                try:
                    entry = json.loads(raw)
                except Exception:                            # noqa: BLE001
                    continue
                kind = entry.get("type")
                if kind == "queue-operation":
                    # ONLY `enqueue` carries his text. `dequeue` and `remove`
                    # are the harness bookkeeping the same message in and out,
                    # and counting them would triple him.
                    if entry.get("operation") != "enqueue":
                        continue
                    text, record = entry.get("content") or "", "queued"
                elif (kind == "user" and entry.get("toolUseResult") is None
                      and not entry.get("isMeta")):
                    text, record = _text_of_user_entry(entry), "prompt"
                else:
                    continue
                if not isinstance(text, str) or not text.strip():
                    continue
                if why_not_his(text):
                    continue
                yield Message(str(entry.get("timestamp") or ""), text,
                              record, path.name)


def distinct(transcripts: pathlib.Path | None = None) -> list[Message]:
    """One row per distinct message, preferring the `prompt` record.

    THE PREFERENCE MATTERS. A mid-turn message that was later absorbed appears
    in both records; the `prompt` copy is the canonical one and carries the
    fields other instruments expect, so it wins. The `queued` copy is kept only
    where no `prompt` copy exists -- which is the 206.
    """
    best: dict[str, Message] = {}
    for m in iter_messages(transcripts):
        key = " ".join(m.text.split())[:300]
        prior = best.get(key)
        if prior is None or (prior.record == "queued" and m.record == "prompt"):
            best[key] = m
    return sorted(best.values(), key=lambda m: m.ts)


def mentions(pattern, transcripts: pathlib.Path | None = None) -> list[Message]:
    """Every distinct message of his matching a compiled regex.

    This is the call an instrument should make before reporting that he never
    said something. `pattern` may be a compiled regex or a plain string.
    """
    if hasattr(pattern, "search"):
        hit = pattern.search
    else:
        needle = str(pattern)
        def hit(s):                                          # noqa: E306
            return needle in s
    return [m for m in distinct(transcripts) if hit(m.text)]


def census(transcripts: pathlib.Path | None = None) -> dict:
    """Counts, for a report or a guard, with the excluded reasons named."""
    rows = list(iter_messages(transcripts))
    by_record = collections.Counter(m.record for m in rows)
    uniq = distinct(transcripts)
    only_queued = sum(1 for m in uniq if m.record == "queued")
    return {"rows": len(rows), "by_record": dict(by_record),
            "distinct": len(uniq), "only_in_queue_record": only_queued}


def main() -> int:
    ap = argparse.ArgumentParser(
        description=("Read what the founder typed, from BOTH transcript "
                     "records. Reads only; writes nothing."))
    ap.add_argument("--grep", help="print only messages matching this substring")
    ap.add_argument("--since", default="", help="ISO prefix, e.g. 2026-11-02")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    c = census()
    print("=" * 74)
    print("WHAT HE TYPED, FROM BOTH RECORDS")
    print("=" * 74)
    print(f"  rows read (a mid-turn message appears twice) : {c['rows']}")
    print(f"  by record                                    : {c['by_record']}")
    print(f"  distinct messages                            : {c['distinct']}")
    print(f"  distinct messages found ONLY in the queue    : "
          f"{c['only_in_queue_record']}")
    print("  THOSE ARE THE ONES NO `type: user` SCAN CAN SEE.")

    rows = distinct()
    if a.since:
        rows = [m for m in rows if m.ts >= a.since]
    if a.grep:
        rows = [m for m in rows if a.grep in m.text]
    if a.limit:
        rows = rows[-a.limit:]
    if a.since or a.grep or a.limit:
        print()
        print(f"  {len(rows)} matching message(s):")
        for m in rows:
            print(f"    [{m.record:6s}] {m.ts}  "
                  f"{' '.join(m.text.split())[:120]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
