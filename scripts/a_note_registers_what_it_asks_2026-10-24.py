#!/usr/bin/env python3
"""A note that asks him for a ruling must register that ask before delivery.

HIS RULING, 2026-10-24, approving the rule he was asked about: *"should the same
rule apply to the TTS → list path, so a question in a TTS file must be registered
before the file is delivered?"* -- Approved.

THE CASE THAT PROVED IT, measured 2026-10-23. `Master_Task_Completion_List_
2026-10-19.txt` carried a section headed "WHAT NEEDS HIS RULING, AND NOTHING ELSE
DOES" with 4 numbered items. 3 of them he ruled on. The 4th -- the stagger value
-- was tracked NOWHERE: no task entry, no ticket, 0 live tickets mentioning it.
It existed only as prose in a file he had not re-read, which is exactly how an ask
is lost. He had already asked why things reach him twice and why panel requests
never ran; this is the same hole on the outbound side.

WHY THE DETECTOR IS MARKER-BASED AND NOT QUESTION-MARK-BASED. A bare question
mark is far too loose: these notes are written for a third-party reader and pose
rhetorical questions constantly. The project already has deliberate markers for a
real ask -- "NEEDS YOUR RULING" and "NEEDS HIS RULING" appear in 10 and 9 files
respectively, and "WHAT NEEDS HIS RULING" heads a section in 4. Those are written
on purpose, so they are what this reads.

Run to check:    python3 scripts/a_note_registers_what_it_asks_2026-10-24.py <file>...
Run to register: python3 scripts/a_note_registers_what_it_asks_2026-10-24.py --register <file>...
"""
from __future__ import annotations

import argparse
import difflib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

#: An inline marker. Each is a deliberate statement that he must decide something.
INLINE = re.compile(
    r"(NEEDS (?:YOUR|HIS) RULING|\[NEEDS YOUR RULING\]|RULING OWED"
    r"|awaiting (?:his|your) ruling)", re.I)

#: A section whose whole purpose is to list asks. Its numbered items are the asks.
SECTION = re.compile(r"^.*WHAT NEEDS (?:HIS|YOUR) RULING.*$", re.I | re.M)

#: A numbered item inside such a section.
ITEM = re.compile(r"^\s*(\d+)[.)]\s+(.{20,})$", re.M)


def _norm(s: str) -> str:
    return " ".join((s or "").split())


def asks(path: pathlib.Path) -> list[dict]:
    """Every ask a note makes, each with the sentence that makes it."""
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("cp1252")             # Word rewrites these; see B42
    out: list[dict] = []

    # 1. inline markers: the sentence containing each
    for m in INLINE.finditer(text):
        start = text.rfind("\n", 0, m.start()) + 1
        end = text.find("\n", m.end())
        line = _norm(text[start:end if end > 0 else len(text)])
        # ★ A HEADING IS NOT AN ASK. "WHAT NEEDS HIS RULING, AND NOTHING ELSE
        # DOES" is a section title; the asks are the items beneath it. The first
        # version counted the heading too and reported 5 asks where 4 existed,
        # which is the kind of noise that gets a gate switched off.
        rest = _norm(INLINE.sub("", line))
        if line and len(rest) >= 40:
            out.append({"kind": "inline", "text": line[:400], "file": path.name})

    # 2. a ruling section's numbered items
    sec = SECTION.search(text)
    if sec:
        tail = text[sec.end():]
        # the section ends at the next ALL-CAPS heading line
        stop = re.search(r"\n[A-Z][A-Z0-9 ,'’-]{12,}\n", tail)
        body = tail[:stop.start()] if stop else tail
        for m in ITEM.finditer(body):
            out.append({"kind": "section-item", "n": m.group(1),
                        "text": _norm(m.group(2))[:400], "file": path.name})

    # de-duplicate: an inline marker inside a numbered item is one ask
    seen, uniq = [], []
    for a in out:
        if any(difflib.SequenceMatcher(None, a["text"][:120], s[:120]).ratio() >= 0.80
               for s in seen):
            continue
        seen.append(a["text"])
        uniq.append(a)
    return uniq


#: An ask must NAME its ticket inline, as `[qs:abcdef123456]`. 12 hex characters
#: is the register's own short identifier.
TICKET_REF = re.compile(r"\[(?:qs|fr|pf|wr):([0-9a-f]{12})\]")


def unregistered(items: list[dict], store) -> list[dict]:
    """Asks that do not NAME a ticket, or name one that does not exist.

    ★ SIMILARITY WAS TRIED FIRST AND FAILED IN BOTH DIRECTIONS, 2026-10-24, and
    the failures are recorded here because the design follows from them.

      * A text-ratio bar of 0.62 against ticket text reported 5 of 5 asks
        unregistered when 4 were tracked -- 3 as task entries B37, B39 and the
        7 already ruled.
      * Widening it to a 45% keyword overlap against the task list as well then
        CLEARED the stagger value, the one ask that was genuinely tracked
        nowhere, because entry B38 mentions "the stagger ... RUNNERS" and shares
        enough words with "the stagger value". Two different asks about one noun
        are not distinguishable by overlap.

    A false negative on the only true case is worse than noise, so the mechanism
    is wrong rather than the threshold. AN ASK NOW NAMES ITS TICKET, exactly as a
    declared figure names its producer and a verdict names its anchor. The check
    becomes exact: does the ask carry an identifier, and does the register hold
    it? There is no discriminator left to get wrong.
    """
    out = []
    for a in items:
        refs = TICKET_REF.findall(a["text"])
        if not refs:
            out.append({**a, "why": "names no ticket"})
            continue
        missing = [r for r in refs if store.get(r) is None]
        if missing:
            out.append({**a, "why": f"names {missing} which the register does not hold"})
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("files", nargs="*", help="the note or TTS files to check")
    ap.add_argument("--register", action="store_true",
                    help="file every unregistered ask as a qs ticket")
    ap.add_argument("--now", default="", help="timestamp from `date -Iseconds`")
    args = ap.parse_args()
    if not args.files:
        ap.error("name at least one file")

    sys.path.insert(0, str(ROOT))
    from bench.ticket_store import TicketStore          # noqa: PLC0415
    store = TicketStore()

    total = bad = 0
    for name in args.files:
        p = pathlib.Path(name)
        if not p.is_file():
            print(f"  MISSING: {name}", file=sys.stderr)
            return 2
        items = asks(p)
        miss = unregistered(items, store)
        total += len(items)
        bad += len(miss)
        print(f"{p.name}: {len(items)} ask(s), {len(miss)} unregistered")
        for a in miss:
            print(f"    UNREGISTERED [{a['kind']}] ({a.get('why','')}) "
                  f"{a['text'][:110]}")
            if args.register:
                t, outcome = store.propose(
                    kind="qs",
                    title=f"ASK FROM A NOTE: {a['text'][:110]}",
                    verbatim=a["text"],
                    source=f"note {p.name}",
                    source_ref=f"{p.name}:{a.get('n', a['kind'])}",
                    anchor=f"{p.name}#{a.get('n', a['kind'])}",
                    created=args.now)
                print(f"      -> {outcome} {t.tid[:12]}  "
                      f"PASTE INTO THE NOTE: [qs:{t.tid[:12]}]")
    if args.register:
        print(f"\nregistered: {bad} ask(s) now carry a qs ticket")
        return 0
    if bad:
        print(f"\n{bad} of {total} ask(s) do not name a ticket. A note that asks "
              f"him for a ruling must NAME the ticket inline, as [qs:abcdef123456], "
              f"so the ask exists in the register and not only as prose in a file he "
              f"may not re-read -- which is how the stagger value was lost. Run with "
              f"--register --now \"$(date -Iseconds)\" to create the tickets, then "
              f"paste the printed identifiers into the note.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
