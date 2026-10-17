#!/usr/bin/env python3
"""Harvest tickets from his replies, from chat, and from the master task list.

HIS INSTRUCTION, 2026-10-17: "you will need to adapt it in such a way, that it
can also extract/harvest, track and store any pending fixes and changes you or I
propose in chat too, rather than just directly from my tts responses. I propose a
small extension to our MC command list where I (or you) will either mark/label
new proposals with either `fr` (feature request) or `pr` (proposed fix). Then
perhaps your extractor can look for these signals in our exchanges and extract
them and place them within the Bugzilla framework with two distinct sections?"

THE MEASUREMENT THAT MAKES THE CHAT HALF NECESSARY RATHER THAN NICE. Of his 579
recorded annotations, 0 mention the bounded-orchestrator question he has asked 3
times. It exists only in chat. A harvester reading only his written replies is
blind to it by construction, so the chat source is not an enhancement; without it
the store would reproduce the exact gap it exists to close.

THREE SOURCES, and each is read with the instrument that can actually read it.
  responses   his annotated replies, via scripts/read_founder_responses_2026-10-11.py,
              because 319 of his 579 verdicts sit in files a plain text scan
              treats as binary and cannot see.
  chat        the session transcripts under the Claude projects directory, read
              as JSON lines. His message of 2026-10-15T03:40:13 and the reply 103
              seconds later were both recovered this way, so this is demonstrated
              rather than assumed.
  task_list   experimental_notes/CDSFL_MASTER_TASK_LIST.md, to seed the store with
              work already recorded, which he asked for explicitly: "you can begin
              by populating it with work already done, work proposed, work
              completed etc".

MARKERS. A line or sentence carrying `fr` or `pf` as a standalone token, or the
forms `fr:`, `pf:`, `[fr]`, `[pf]`, is an explicit proposal and is harvested as
that kind. HE PROPOSED `pr` FOR THE SECOND MARKER AND IT IS ALREADY TAKEN: his
own list defines `pr` as a full panel review, and 4 of 4 of his real panel-review
usages were mis-harvested as proposed fixes before this was changed to `pf`. Without a marker, a task-list entry is harvested by its recorded
state, and a founder annotation is harvested as `pr` when it reads as an
instruction about an existing defect and as `fr` when it proposes something new.
That last split is a judgement, so every unmarked ticket records
`source=...-unmarked` and keeps his verbatim words, which is what makes a human
read decisive.

`--help` runs no harvest and costs nothing. `--dry-run` reports and writes
nothing.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys
from collections import Counter

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from bench.ticket_store import TicketStore, KINDS  # noqa: E402

READER = REPO / "scripts" / "read_founder_responses_2026-10-11.py"
TASKLIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
TRANSCRIPTS = (pathlib.Path.home() /
               ".claude/projects/-Users-georgejackson-Developer-Projects")

#: `fr` or `pr` as a standalone marker. Deliberately strict: `pr` appears inside
#: ordinary words and inside "panel review", so a bare substring match would
#: harvest noise. Requires a boundary and one of the marker punctuations, or the
#: token alone on its own line.
MARKER = re.compile(r"(?:(?<=^)|(?<=[\s(\[]))(fr|pf)(?:[:\]\)]|\s*[-—]\s|$)",
                    re.IGNORECASE | re.MULTILINE)

#: WHAT MAY BE A BLOCKING SUBJECT, and the measurement that narrowed it.
#:
#: A first version harvested every identifier in an entry, including file paths.
#: Measured over the 104 task-list candidates on 2026-10-17: 424 subject mentions
#: across 343 distinct subjects, of which 49 were test files or globs, 14.2857%,
#: Wilson [10.9774%, 18.3851%]. Worse, `CDSFL_MASTER_TASK_LIST.md` appeared on 20
#: tickets, so closing any 1 of them would have made the other 19 unraisable.
#: That is OVER-BLOCKING, which is strictly worse than no store at all, and it is
#: the failure his word "decoration" points at from the other side.
#:
#: A subject must therefore be SPECIFIC ENOUGH TO BE WRONG ABOUT. A file is not:
#: `reference_runner_v3.py` is 21,000 lines and a dozen unrelated mechanisms. A
#: CALLABLE is: `_load_fingerprints`, `routing.rank_falsifier_writers`,
#: `apply_fixes_back_enabled`. So only callable-level and config-key-level names
#: qualify, files and documents are recorded as context rather than as subjects,
#: and the count is capped at 3 so a single entry cannot blanket the store.
_BACKTICKED = re.compile(r"`([^`\n]{3,70})`")
_DOTTED = re.compile(r"^[a-z_][a-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*$")
_SNAKE = re.compile(r"^_?[a-z][a-z0-9]*(?:_[a-z0-9]+)+$")
_CONST = re.compile(r"^[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+$")
_NOT_A_SUBJECT = re.compile(r"\.(py|md|json|toml|txt|sh|jsonl)$|[*/\\]|^\.|\s")


def _is_blocking_subject(tok: str) -> bool:
    """True only for a name specific enough that a settled ticket on it means
    the SAME mechanism, not merely the same file."""
    tok = tok.strip().strip("`()")
    if not tok or _NOT_A_SUBJECT.search(tok):
        return False
    if tok.startswith("bench/tests/"):
        return False
    return bool(_DOTTED.match(tok) or _SNAKE.match(tok) or _CONST.match(tok))


def subjects_in(text: str) -> list[str]:
    """Exact callable-level identifiers named in the text. Empty is honest.

    Capped at 3. An entry naming more than 3 mechanisms is usually a summary
    rather than a proposal, and a summary should not blanket the subject index.
    """
    out: list[str] = []
    seen: set[str] = set()
    for m in _BACKTICKED.finditer(str(text)):
        tok = m.group(1).strip().strip("`()")
        # a backticked `module.py:123` or `a, b` is context, not a subject
        tok = tok.split(":")[0].strip()
        if _is_blocking_subject(tok) and tok not in seen:
            seen.add(tok); out.append(tok)
    if len(out) < 3:
        for m in re.finditer(r"\b([a-z_][a-z0-9_]*\.[a-z_][a-z0-9_]+)\b", str(text)):
            tok = m.group(1)
            if _is_blocking_subject(tok) and tok not in seen:
                seen.add(tok); out.append(tok)
    return sorted(out)[:3]


def marked_kind(text: str) -> str | None:
    m = MARKER.search(str(text))
    return m.group(1).lower() if m else None


# --------------------------------------------------------------------- sources

def from_responses(since: str) -> list[dict]:
    r = subprocess.run([sys.executable, str(READER), "--json"],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        print(f"  reader failed rc={r.returncode}", file=sys.stderr)
        return []
    rows = json.loads(r.stdout)["annotations"]
    out = []
    for v in rows:
        if v.get("date", "") < since:
            continue
        txt = " ".join(str(v.get("text", "")).split())
        if len(txt) < 25:
            continue
        out.append({"verbatim": txt,
                    "kind": marked_kind(txt) or "pf",
                    "marked": marked_kind(txt) is not None,
                    "source": "responses",
                    "source_ref": f"{pathlib.Path(v['file']).name}:{v['line_index']}",
                    "ruled": v.get("date", ""),
                    "subjects": subjects_in(txt)})
    return out


def from_chat(since: str, limit_per_file: int = 400) -> list[dict]:
    """Marker-bearing messages from the transcripts. Markers only, by design.

    Harvesting every chat message would flood the store, and the store's value is
    that an entry means something. So chat contributes only where a marker makes
    the intent explicit, which is exactly the mechanism he proposed.
    """
    out = []
    if not TRANSCRIPTS.is_dir():
        return out
    for f in sorted(TRANSCRIPTS.glob("*.jsonl")):
        taken = 0
        for line in f.open(errors="ignore"):
            if taken >= limit_per_file:
                break
            if not re.search(r'"(fr|pf)[:\]]', line, re.IGNORECASE):
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = str(d.get("timestamp", ""))[:19]
            if ts[:10] < since:
                continue
            msg = d.get("message") or {}
            role = msg.get("role") or "?"
            c = msg.get("content")
            text = c if isinstance(c, str) else " ".join(
                x.get("text", "") for x in (c or [])
                if isinstance(x, dict) and x.get("type") == "text")
            text = " ".join(str(text).split())
            k = marked_kind(text)
            if not k or len(text) < 25:
                continue
            out.append({"verbatim": text[:1200], "kind": k, "marked": True,
                        "source": f"chat:{role}", "source_ref": ts,
                        "ruled": ts[:10] if role == "user" else "",
                        "subjects": subjects_in(text)})
            taken += 1
    return out


def from_task_list() -> list[dict]:
    """Seed from the recorded task list, carrying its state across.

    MARKER-DRIVEN, NOT HEADING-DRIVEN, and the reason is measured. A first
    version matched a bold heading at the start of each blank-line-separated
    block and missed 47 of 141 entries, 33.3333%, Wilson [26.0856%, 41.4651%].
    Two causes, both invisible from one example: numerically-identified entries
    are written `**1.2 The gap ...**` with no dot after the number while
    letter-prefixed ones are written `**B18. His ruling ...**`, and some entries
    bold the identifier ALONE as `**10.1** Build a script ...` with the title
    outside the bold span. Fixing those left 18 still missing, because several
    entries SHARE one paragraph block, so no paragraph-level rule can separate
    them at all.

    `task_list_markers.parse_entries` already handles every one of those forms --
    it is what reports 141 entries -- and every entry carries an HTML comment
    marker on its own line. So the markers are the index: for each parsed entry,
    the text between the previous marker and this one is its body. That is exact
    and needs no heading pattern.
    """
    if not TASKLIST.exists():
        return []
    sys.path.insert(0, str(REPO / "scripts"))
    import task_list_markers as t

    entries = t.parse_entries(TASKLIST)
    lines = TASKLIST.read_text(encoding="utf-8").splitlines()
    marker_line = {}
    for e in entries:
        # `line` on an Entry is the 1-indexed marker line; fall back to a scan
        ln = getattr(e, "line", None) or getattr(e, "marker_line", None)
        if not ln:
            ln = next((i + 1 for i, l in enumerate(lines)
                       if l.lstrip().startswith(f"<!-- task: {e.ident} ")), None)
        if ln:
            marker_line[e.ident] = ln

    ordered = sorted((ln, ident) for ident, ln in marker_line.items())
    out = []
    prev = 0
    for ln, ident in ordered:
        e = next(x for x in entries if x.ident == ident)
        body = "\n".join(lines[prev:ln - 1])
        prev = ln
        quoted = re.search(
            r"\*\*HIS (?:WORDS|QUESTION|RULING)[^:]*:\*\*\s*(.{40,700}?)(?:\*\*|$)",
            body, re.DOTALL)
        if quoted:
            verbatim = " ".join(quoted.group(1).split())
        else:
            # the entry's own first sentence, which is its headline
            first = re.sub(r"\*+", "", body.strip().split(". ")[0])
            verbatim = " ".join(first.split())[:400]
        if len(verbatim) < 20:
            verbatim = f"task {ident}: " + " ".join(
                re.sub(r"\*+", "", body).split())[:300]
        title = " ".join(re.sub(r"\*+", "", body.strip()).split())[:160]
        out.append({"verbatim": verbatim, "title": title or f"task {ident}",
                    "kind": "fr" if ("orchestrator" in title.lower()
                                     or "selection" in title.lower()) else "pf",
                    "marked": False, "source": "task_list",
                    "source_ref": f"{ident} state={e.state} status={e.status}",
                    "ruled": e.ruled or "", "task_ref": ident,
                    "state": e.state, "status": e.status,
                    "subjects": subjects_in(body)})
    return out


# ----------------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--since", default="2026-10-01")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--store", default=None)
    ap.add_argument("--sources", default="task_list,responses,chat")
    a = ap.parse_args()

    want = {s.strip() for s in a.sources.split(",") if s.strip()}
    rows: list[dict] = []
    if "task_list" in want:
        rows += from_task_list()
    if "responses" in want:
        rows += from_responses(a.since)
    if "chat" in want:
        rows += from_chat(a.since)

    print("=" * 74)
    print("TICKET HARVEST")
    print("=" * 74)
    print(f"\ncandidates by source: "
          f"{dict(Counter(r['source'].split(':')[0] for r in rows))}")
    print(f"explicitly marked with fr or pr: {sum(1 for r in rows if r['marked'])}")
    print(f"carrying at least 1 exact subject: {sum(1 for r in rows if r['subjects'])}")

    if a.dry_run:
        print("\n--dry-run: nothing written. First 6 candidates:")
        for r in rows[:6]:
            print(f"  [{r['kind']}] {r['source']} {r['source_ref']}")
            print(f"      subjects={r['subjects']}")
            print(f"      {r['verbatim'][:110]}")
        return 0

    store = TicketStore(pathlib.Path(a.store) if a.store else None)
    outcomes = Counter()
    for r in rows:
        title = r.get("title") or r["verbatim"][:120]
        # A task-list entry carries a RECORDED state, so it starts OPEN and is
        # then closed below where the record says DONE or WITHDRAWN. An
        # annotation of his is a record of an INSTRUCTION whose state is not
        # established, so it starts UNCONFIRMED: it needs triage, not work. A
        # first version made all of them OPEN and the store reported 306 open
        # items when most were long handled.
        # A BLOCKED task is live work that cannot proceed, and the status
        # vocabulary already has a word for that: WITHHELD. Mapping it to OPEN
        # overstated open work by 1, which is small but is exactly the kind of
        # drift that makes a count untrustworthy.
        if r["source"] == "task_list":
            initial = "WITHHELD" if r.get("state") == "BLOCKED" else "OPEN"
        else:
            initial = "UNCONFIRMED"
        t, o = store.propose(r["kind"], title, r["verbatim"], r["source"],
                             source_ref=r.get("source_ref", ""),
                             ruled=r.get("ruled", ""),
                             task_ref=r.get("task_ref", ""),
                             subjects=r.get("subjects", ()),
                             status=initial)
        outcomes[o] += 1
        # carry a recorded DONE state across as a verified close
        if o == "created" and r.get("state") == "DONE":
            store.close(t.tid, f"recorded DONE in the master task list as {r['task_ref']}",
                        f"task-list marker state=DONE status={r.get('status','')}")
            outcomes["closed-from-task-list"] += 1
        elif o == "created" and r.get("state") == "WITHDRAWN":
            store.close(t.tid, f"withdrawn in the master task list as {r['task_ref']}",
                        f"task-list marker state=WITHDRAWN status={r.get('status','')}")
            outcomes["closed-withdrawn"] += 1

    print(f"\noutcomes: {dict(outcomes)}")
    print(f"\nstore summary: {json.dumps(store.summary(), indent=2)}")
    print(f"\nOPEN work (task-list derived, state recorded): {len(store.open_tickets())}")
    print(f"UNCONFIRMED (harvested, needs triage not work)  : {len(store.unconfirmed())}")
    print(f"SETTLED (closed, withdrawn or rejected)         : {len(store.settled())}")
    print("\n" + "=" * 74)
    print("An outcome other than `created` means the item was ALREADY KNOWN.")
    print("That is the whole point: it is the step that stops a rediscovery.")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
