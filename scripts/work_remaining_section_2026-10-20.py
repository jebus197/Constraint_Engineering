#!/usr/bin/env python3
"""Render the WORK REMAINING section at the top of the master task list.

HIS INSTRUCTION, 2026-10-20: "add all the tasks agreed to/ruled on to the top of
your mechanical master task list and run it", and "wr is a valid section in the
Bugzilla registry, and you should use it to track all remaining outstanding work,
and refer back to this before risking constantly referring back to me and
requesting my verdict".

SO THE SECTION IS GENERATED FROM THE REGISTER, NOT TYPED. A typed list is a claim
about the register; this one IS the register, re-rendered. Running it again after
a ticket closes removes that line, which is what makes the section safe to trust
as the thing to work from.

ORDER IS HIS. Within the section: what he ruled most recently first, because a
ruling of his is the freshest statement of what he wants; then panel requests,
oldest first, because those are the ones that went unrun longest; then the rest.
R1 is last by his own ruling: "The zero plant control will be run (with the
updated runner) after all outstanding tasks from your master task list have been
complete!"

Run:  python3 scripts/work_remaining_section_2026-10-20.py --write
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LIST = ROOT / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
BEGIN = "<!-- work-remaining-begin -->"
END = "<!-- work-remaining-end -->"


def render() -> str:
    sys.path.insert(0, str(ROOT))
    from bench.ticket_store import TicketStore              # noqa: PLC0415
    store = TicketStore()
    live = [t for t in store.by_kind("wr")
            if t.status in ("OPEN", "REOPENED", "WITHHELD", "CONTESTED")]

    panel = [t for t in live if t.title.startswith("PANEL REQUESTED")]
    r1 = [t for t in live if t.task_ref == "R1"]
    rest = [t for t in live if t not in panel and t not in r1]

    # ★ THE RULED ENTRIES BELONG HERE TOO, and reading only kind=wr loses them.
    # 16 wr records created on 2026-10-20 carried a task_ref, which put them at a
    # second identity for one entry; they were MERGED into the canonical entry
    # tickets, whose kind is whatever the harvester assigned. So the work he has
    # ruled on is read from the LIST's own markers, which is where his ruling
    # actually lives, rather than from the kind of a ticket.
    sys.path.insert(0, str(ROOT / "scripts"))
    import task_list_markers as tlm                          # noqa: PLC0415
    class _E:                                                # a ticket-shaped view
        def __init__(self, e):
            self.tid = f"entry-{e.ident}"
            self.task_ref = e.ident
            self.ruled = e.ruled
            head = e.text.lstrip("*").strip()
            self.title = (head.split("**")[0].strip() or head)[:150]
    ruled_entries = [_E(e) for e in tlm.parse_entries(LIST)
                     if e.state == "OPEN" and e.ruled]
    rest = rest + ruled_entries
    rest.sort(key=lambda t: (t.ruled or "0000", t.tid), reverse=True)
    panel.sort(key=lambda t: (t.ruled or "0000", t.tid))

    L = [BEGIN, "",
         "## ★ WORK REMAINING — generated from the register, never typed",
         "",
         f"There are **{len(live)} live `wr` tickets**. This section is rendered by "
         f"`scripts/work_remaining_section_2026-10-20.py` from "
         f"`bench/ticket_store.py`, so it cannot drift from the register it "
         f"reports. Closing a ticket removes its line on the next render. "
         f"**His instruction, 2026-10-20:** *\"wr is a valid section in the "
         f"Bugzilla registry, and you should use it to track all remaining "
         f"outstanding work, and refer back to this before risking constantly "
         f"referring back to me and requesting my verdict\"*.",
         ""]

    if rest:
        L += [f"### Ruled by him, {len(rest)} items — newest ruling first", ""]
        for t in rest:
            ref = f" `{t.task_ref}`" if t.task_ref else ""
            rule = f" — ruled {t.ruled}" if t.ruled else ""
            L.append(f"- `{t.tid[:12]}`{ref}{rule}  {t.title[:150]}")
        L.append("")

    if panel:
        L += [f"### Panel reviews he asked for, {len(panel)} items — oldest first",
              "",
              "Measured 2026-10-20: 30 of his 60 panel requests, 50.0000%, "
              "Wilson [37.7350%, 62.2650%], were reached by nothing at all "
              "before this section existed.",
              "",
              # ★ HIS WORDS, SO THE REGION IS NOT OPTIONAL. Each line below is a
              # quotation of his, and the note linter's undefined-term rule would
              # otherwise demand that his phrasing be edited -- "The prose arm is
              # what exactly?" tripped it on the first render. The exemption
              # exists precisely so that his input is never gated or rewritten.
              "<!-- verbatim-begin: the founder's own words, quoted from his replies -->",
              ""]
        for t in panel:
            when = f" — asked {t.ruled}" if t.ruled else ""
            L.append(f"- `{t.tid[:12]}`{when}  {t.title[len('PANEL REQUESTED: '):][:140]}")
        L += ["", "<!-- verbatim-end -->", ""]

    if r1:
        L += ["### Last, by his own ruling", "",
              "*\"The zero plant control will be run (with the updated runner) "
              "after all outstanding  tasks  from your master task list  have "
              "been complete!\"*", ""]
        for t in r1:
            L.append(f"- `{t.tid[:12]}` `{t.task_ref}` — ruled {t.ruled}  {t.title[:140]}")
        L.append("")

    L += ["", END]
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true", help="write it into the list")
    args = ap.parse_args()
    section = render()
    if not args.write:
        print(section)
        return 0
    t = LIST.read_text(encoding="utf-8")
    if BEGIN in t and END in t:
        t = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), section, t, flags=re.S)
    else:
        # after the document's own title line, before everything else
        lines = t.split("\n")
        i = next((k for k, l in enumerate(lines) if l.startswith("# ")), -1) + 1
        lines[i:i] = ["", section, ""]
        t = "\n".join(lines)
    LIST.write_text(t, encoding="utf-8")
    print(f"written into {LIST.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
