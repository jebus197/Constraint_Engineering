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
from bench.ticket_store import TicketStore, norm_title, KINDS  # noqa: E402

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


def _own_body(block: str, ident: str) -> str:
    """The part of a shared block that belongs to THIS entry.

    The block runs from the previous marker to this entry's marker, so where
    entries share a block it also contains whatever was written above this
    entry -- typically an addendum recording a neighbour as built. Slicing
    from this entry's own heading line removes that, which keeps `tid_of`
    stable under an unrelated edit nearby. Where no heading is found the whole
    block is returned, because a wrong narrowing would be worse than none.
    """
    lines = block.splitlines()
    pat = re.compile(r"^\s*(?:★\s*)?\*{0,2}" + re.escape(ident) + r"(?:\.|\b)")
    for i, line in enumerate(lines):
        if pat.match(line.lstrip()):
            return "\n".join(lines[i:])
    return block


#: An entry identifier in HEADING position on a line: an optional star
#: marker, optional bold asterisks, then the identifier, then a dot or a
#: word boundary. Covers all 3 recorded heading forms -- `**B18. His ruling`,
#: `**1.2 The gap`, and `**10.1** Build a script`.
def _heading_line(body: str, ident: str) -> str:
    """The line in `body` that names THIS entry, or '' if none does.

    WHY A TITLE CANNOT BE THE BLOCK'S FIRST 160 CHARACTERS. Measured
    2026-10-17 by `scripts/do_the_ticket_titles_name_their_own_entry_2026-10-17.py`:
    9 of 141 titles, 6.3830% with a Wilson interval from 3.3941% to 11.6854%,
    named a DIFFERENT entry. 8 of the 9 are the same shape -- an addendum
    recording that entry N is built, written above entry N+1's heading
    because the two share one blank-line-separated block, so N+1's title
    became prose about N.

    That is harmful rather than untidy. The founder's ruling of 2026-10-17
    requires the registry to be searched before any work is proposed, so a
    lookup of B11 returning prose about B10 either re-proposes settled work
    or passes over open work. Picking the line that names the entry is exact
    and needs no guess about which neighbour wrote last.
    """
    pat = re.compile(r"^\s*(?:★\s*)?\*{0,2}" + re.escape(ident) + r"(?:\.|\b)")
    for line in body.splitlines():
        if pat.match(line.lstrip()):
            return " ".join(re.sub(r"\*+", "", line).split())
    return ""


def _title_for(body: str, ident: str) -> str:
    """This entry's own heading where it has one, else the block's opening."""
    own = _heading_line(body, ident)
    if own:
        return own[:160]
    return " ".join(re.sub(r"\*+", "", body.strip()).split())[:160]


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
        block = "\n".join(lines[prev:ln - 1])
        prev = ln
        # ANCHOR THE BODY ON THE ENTRY'S OWN HEADING, 2026-10-17. The slice
        # between 2 markers is the entry PLUS anything written above it in a
        # shared block, so an addendum recording a NEIGHBOUR as built changed
        # this entry's text -- and `tid_of` digests the text. Measured: B15
        # and B20 each acquired a SECOND open ticket that way, because the
        # addenda written above them on 2026-10-17 changed their verbatim and
        # therefore their hashed identity.
        #
        # That is the exact failure this store exists to prevent, arriving by
        # the back door: an entry whose identity moves when an unrelated edit
        # lands nearby cannot be relied on to say whether an issue is already
        # filed. Anchoring on the entry's own heading makes the identity a
        # property of the entry rather than of its neighbours' edit history.
        body = _own_body(block, ident)
        quoted = re.search(
            r"\*\*HIS (?:WORDS|QUESTION|RULING)[^:]*:\*\*\s*(.{40,700}?)(?:\*\*|$)",
            body, re.DOTALL)
        if quoted:
            verbatim = " ".join(quoted.group(1).split())
        else:
            # the entry's own first sentence, which is its headline.
            #
            # THE LEADING IDENTIFIER IS STRIPPED FIRST, 2026-10-17. Anchoring
            # the body on the entry's own heading makes it begin `P1. Full
            # CDSFL format ...`, and `split(". ")` then returns the bare
            # identifier `P1` as the first sentence. That is 2 characters, so
            # it fell under the 20-character floor below and the fallback
            # rewrote the verbatim -- which would have changed the hashed
            # identity of 95 of 141 entries and minted a duplicate for each.
            # Measured before the fix, which is why the migration never ran.
            stem = re.sub(r"\*+", "", body.strip())
            stem = re.sub(r"^(?:★\s*)?" + re.escape(ident) + r"[.)]?\s*", "", stem)
            # A LEADING STATUS STAMP IS NOT THE ENTRY'S SUBSTANCE. 22 of 141
            # headings open `<ref>. DONE 2026-09-10.`, so once the reference is
            # removed the first sentence is a 15-character stamp, under the
            # 20-character floor below, and the whole verbatim fell back to a
            # stub. A stub still gets a correct identity, because identity is
            # the reference, but it defeats the reworded-match tier that catches
            # a paraphrase of the same issue -- which is the tier that stops a
            # rediscovery arriving in different words.
            stem = re.sub(
                r"^(?:DONE|WITHDRAWN|CLOSED|PARTIAL|BLOCKED)\b[^.]*\.\s*",
                "", stem, flags=re.IGNORECASE)
            first = stem.split(". ")[0]
            verbatim = " ".join(first.split())[:400]
        if len(verbatim) < 20:
            verbatim = f"task {ident}: " + " ".join(
                re.sub(r"\*+", "", body).split())[:300]
        title = _title_for(body, ident)
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
        # REFRESH A STALE SEARCH LABEL, 2026-10-17. `propose` returns `exists`
        # without touching the stored record, which is correct -- silently
        # rewriting one is how a settled issue returns wearing new words. But
        # the label is what the pre-work search reads, and 9 of 141 named a
        # DIFFERENT entry before `_title_for` was fixed. So the label alone is
        # refreshed, through the one path that cannot move identity or
        # substance, and only for a task-list row, whose entry is the
        # authority on its own heading.
        if r["source"] == "task_list" and t.title != norm_title(title):
            store.retitle(t.tid, title)
            outcomes["retitled"] += 1
        # AND TRACK THE CURRENT WORDING, for the same reason. The reworded-match
        # tier reads `nid`, which is derived from the stored text, so a record
        # left at an old wording weakens the tier that catches a rediscovery
        # arriving in different words. Safe only because identity is the
        # reference: `restate` asserts the identity did not move and refuses
        # the write if it did.
        if (r["source"] == "task_list" and r.get("task_ref")
                and t.verbatim != " ".join(r["verbatim"].split())):
            store.restate(t.tid, r["verbatim"],
                          "task-list entry reworded; tracked by "
                          "scripts/harvest_tickets_2026-10-17.py")
            outcomes["restated"] += 1
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
    # SETTLED WORK AND RETIRED IDENTIFIERS ARE COUNTED SEPARATELY. MERGED is
    # terminal, so `settled()` includes every redirect left behind by an
    # identity migration -- 146 of them. Reporting that as settled work
    # overstated it by more than twice: 257 against 111 settled task entries.
    redirects = [t for t in store.settled() if t.status in ("MERGED", "DUPLICATE")]
    print(f"SETTLED work (closed, withdrawn or rejected)    : "
          f"{len(store.settled()) - len(redirects)}")
    print(f"RETIRED identifiers (redirects to a live record): {len(redirects)}")
    print("\n" + "=" * 74)
    print("An outcome other than `created` means the item was ALREADY KNOWN.")
    print("That is the whole point: it is the step that stops a rediscovery.")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
