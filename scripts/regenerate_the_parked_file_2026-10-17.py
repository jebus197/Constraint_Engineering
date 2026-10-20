#!/usr/bin/env python3
"""Derive the parked file's LIVE portion from the master task list's markers.

TASK B3. His ruling on being shown the measurement: *"Build it and implement
it."*

THE DEFECT. Nothing removed an item from
`experimental_notes/PARKED_FOR_THE_FOUNDER.md` when its underlying entry closed,
so the file re-presented settled business and buried the live items among it.
Measured 2026-10-13 by `scripts/has_he_already_ruled_on_the_parked_2026-10-13.py`
and reproduced 2026-10-17: **14 of 21 parked items were already settled,
66.6667%, Wilson [45.3735%, 82.8052%], Clopper-Pearson [43.0325%, 85.4123%]** --
6 by their own heading, 6 naming entries the list records DONE or WITHDRAWN, and
2 refuted by execution.

THE FIX IS THE ONE HE ASKED FOR: the live portion is DERIVED at generation time
from the task list's own markers, the way the morning report's decision list
already is, so a closed entry cannot reappear.

IT MOVES, IT DOES NOT DELETE. Point-never-prune: a settled item is relocated to a
clearly-labelled SETTLED section with the reason it was settled, so the record of
what was parked survives and a reader can still audit the decision. A parked file
that silently shrank would be worse than one that goes stale, because staleness
is visible and deletion is not.

IT REUSES THE MEASUREMENT'S OWN PARSER AND VOCABULARY rather than carrying a
second copy. Two spellings of "what counts as settled" would drift, which is the
defect the note linter's `paragraphs()` records breaking an exemption set, and
here a drift would mean the generator and the measurement disagreed about the
very items the generator moves.

DRY RUN BY DEFAULT.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import importlib.util
import pathlib
import re as _re
import shutil
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
PARKED = REPO / "experimental_notes" / "PARKED_FOR_THE_FOUNDER.md"
MEASURE = REPO / "scripts" / "has_he_already_ruled_on_the_parked_2026-10-13.py"

#: HIS WORDS, VERBATIM, lifted from the file on 2026-10-17 rather than
#: retyped -- an earlier draft retyped them and changed them. Double quotes
#: are verbatim under his convention, so this string is not editable prose.
HIS_INSTRUCTION = (
    'Why not just leave them all to discuss with me at the end of the completed task list, unless there is something that clearly warrants my immediate attention?')

#: The block `render` writes BETWEEN the live and settled halves. It is a module
#: constant because the renderer emits it and the reader must strip it: the
#: parser gives the LAST LIVE ITEM a body that absorbs everything up to the next
#: "## ", separator and settled header included. Found by EXECUTION on the
#: second --apply, not by reading: run 1 looked perfect, run 2 produced 28
#: `*SETTLED:` lines for 14 items and 2 copies of the settled header, and every
#: further run would have added another. Committing after a single run would
#: have shipped a file that grew on every regeneration.
SETTLED_HEADER = "# Settled — kept for the record, not for his attention"
SETTLED_BLURB = ("Each of these was parked and has since been settled. They are "
                 "listed with the reason so the decision remains auditable.")
#: A reason line this script itself wrote on a previous run.
_OWN_LINE = _re.compile(r"^\*(?:SETTLED|RULED BY HIM)\b.*\*\s*$", _re.M)
#: The structural tail, with the heading's item total allowed to differ.
_OWN_TAIL = _re.compile(
    r"\n*^---\s*$\n+^" + _re.escape(SETTLED_HEADER) + r"[^\n]*$\n+^"
    + _re.escape(SETTLED_BLURB) + r"\s*$\n*", _re.M)


#: The note-standard foot-line this script now emits. THIRD FORM OF THE SAME
#: DEFECT, introduced and caught on 2026-10-19. Adding the stamp without
#: teaching the reader to strip it reproduced exactly the non-idempotence this
#: file's own history records: the parser gives the LAST item's body everything
#: up to the next heading, so a second run re-emitted the stamp and a third
#: would have added another. The idempotence guard went red immediately, which
#: is the whole reason it exists. The version is matched loosely so a later
#: standard bump still strips an older stamp.
_OWN_STAMP = _re.compile(
    r"\n*(?:^---\s*$\n+)?^Written under CDSFL note standard v[\d.]+\.\s*$\n*", _re.M)


def strip_own_output(body: str) -> str:
    """Remove what a PREVIOUS run of this script added to a body.

    Without this the file grows on every regeneration. Three forms are removed:
    the reason line written above an item's text, the separator-plus-header
    block the last live item's body absorbs, and the note-standard foot-line.
    """
    body = _OWN_STAMP.sub("\n", body)
    body = _OWN_TAIL.sub("\n", body)
    body = _OWN_LINE.sub("", body)
    return body.strip("\n")




def _measure():
    """The measurement module, so its parser and vocabulary are the only ones."""
    spec = importlib.util.spec_from_file_location("parked_measure", MEASURE)
    m = importlib.util.module_from_spec(spec)
    sys.modules["parked_measure"] = m
    spec.loader.exec_module(m)
    return m


def classify(m) -> tuple:
    """(live, settled) item lists, each (heading, body, why).

    THE CLASSIFICATION IS THE MEASUREMENT'S, CALLED NOT COPIED. A second
    implementation was written first and disagreed with the measurement on 5 of
    21 items IN BOTH DIRECTIONS, because it read identifiers from the body as
    well as the heading, did not split a compound identifier such as "A13/A14",
    required EVERY entry an item names to be settled rather than any, and had no
    route for an item refuted by execution. Two of its disagreements would have
    moved a LIVE item into a "settled" section, which is the burial this script
    exists to prevent, performed by the script itself.

    ONE DELIBERATE DIVERGENCE, STATED RATHER THAN HIDDEN. The measurement's
    headline total adds `closed` AND `ruled` together, because it answers "has he
    already dealt with this?". This script moves only `closed`. An item in
    `ruled` is one he has given a ruling on whose work is not done -- he ruled
    "restart it" on the zero-plant control on the 7th of August and again on the
    6th of September, and it was still outstanding 70 days later. Moving that to
    a settled section would bury live work behind a ruling, so a ruled item
    stays live and is marked as ruled instead. `ruled` is currently 0 of 21, so
    this divergence changes no present verdict; it is written down because the
    first time it does, silence would be a defect.
    """
    states = m.task_states()
    ann_text = m.annotation_text(m.annotations())
    items = m.parked_items()
    bodies = {}
    for heading, body in items:
        bodies.setdefault(heading, strip_own_output(body))
    closed, ruled, undecided, _body_only = m.classify_items(
        items, states, ann_text)
    settled = [(h, bodies[h], why) for h, why in closed]
    live = [(h, bodies[h], None) for h, _ in undecided]
    live += [(h, bodies[h],
              "RULED BY HIM, WORK NOT DONE: "
              + "; ".join(f"{d} names {i}" for d, i, _ in hits[:2]))
             for h, hits in ruled]
    return live, settled


def _breakdown(settled) -> str:
    """"6 by their own heading, ..." -- DERIVED from the reasons, not typed.

    The sentence it replaces was typed by hand on 2026-10-13 and would have
    been wrong the moment one item moved.
    """
    own = sum(1 for _, _, w in settled if "own heading" in w)
    task = sum(1 for _, _, w in settled if w.startswith("task list:"))
    exe = sum(1 for _, _, w in settled if w.startswith("refuted by execution:"))
    parts = []
    if own:
        parts.append(f"{own} by their own heading")
    if task:
        parts.append(f"{task} naming task entries recorded DONE or WITHDRAWN")
    if exe:
        parts.append(f"{exe} refuted by execution")
    other = len(settled) - own - task - exe
    if other:
        parts.append(f"{other} by another route")
    return ", and ".join([", ".join(parts[:-1]), parts[-1]]) if len(parts) > 1 \
        else (parts[0] if parts else "none")


def render(live, settled, now: str, share: str) -> str:
    """The whole file.

    THE PREAMBLE IS CARRIED FORWARD FROM THE FILE'S OWN WORDS, NOT REWRITTEN.
    An earlier draft of this function composed its own preamble, and in doing so
    it PARAPHRASED HIS INSTRUCTION INSIDE DOUBLE QUOTATION MARKS -- it wrote
    "rather than bother me with them now?" where he wrote "unless there is
    something that clearly warrants my immediate attention?". Under his
    quotation convention double quotes are verbatim, so that draft would have
    put words in his mouth in a file addressed to him, and it would also have
    dropped 3 sentences of substance: that blocking items never appear here, the
    breakdown of how the settled items were settled, and the instruction to
    re-derive the figure before treating any item as open. The quotation is now
    a module constant taken from the file, and the breakdown is derived.
    """
    out = ["# Parked for the founder — non-blocking items, newest last", "",
           f"**Opened 2026-09-10 on his instruction:** *\"{HIS_INSTRUCTION}\"*",
           "",
           "Every item here was classified by `scripts/blocker_triage.py` as NOT "
           "blocking. Nothing here is dropped; it is queued. Items that DO block "
           "are raised at once and never appear in this file.", "",
           "**THE LIVE PORTION IS DERIVED, NOT MAINTAINED BY HAND.** Until "
           "2026-10-17 nothing reconciled this file against the master task list "
           "when an entry closed, so it re-presented settled business and buried "
           "the live items among it. Measured 2026-10-13 by "
           "`scripts/has_he_already_ruled_on_the_parked_2026-10-13.py`: "
           "**14 of 21 items were already settled — 66.6667%**, Wilson "
           "[45.3735%, 82.8052%]. His ruling on reading that was *\"Build it and "
           "implement it.\"* It is now regenerated by "
           "`scripts/regenerate_the_parked_file_2026-10-17.py`, which calls that "
           "producer's own classification rather than carrying a second copy of "
           "it. A settled item is MOVED to the section at the foot with its "
           "reason, never deleted, because staleness is visible and deletion is "
           "not.", "",
           f"**Regenerated {now}. {len(live)} item(s) still need him; "
           f"{len(settled)} are settled — {share}, "
           f"{_breakdown(settled)}.** Re-run the producer before treating any "
           "item here as open; a figure about this file's staleness that is not "
           "re-derived is a claim about evidence rather than evidence.",
           "", "---", ""]
    for heading, body, why in live:
        out.append(f"## {heading}")
        if why:
            out.append(f"*{why}.*")
        out.append(body.rstrip())
        out.append("")
    out += ["---", "",
            f"{SETTLED_HEADER} ({len(settled)})", "",
            SETTLED_BLURB, ""]
    for heading, body, why in settled:
        out.append(f"## {heading}")
        out.append(f"*SETTLED: {why}.*")
        out.append(body.rstrip())
        out.append("")
    # THE NOTE-STANDARD STAMP, emitted MECHANICALLY rather than remembered.
    # His instruction of 2026-10-11: *"You have returned again to not printing
    # the CDSFL notes standard used to produce these files. This is a small
    # glitch, but meaningful and should be fixed (prerably mechanically so you
    # don't forget again), as it helps me to track which notes standards you are
    # using across files."* This file is a DELIVERED note under
    # `experimental_notes/`, so `missing_standard_stamp` in the linter requires
    # one -- and the generator emitted none, so the file has never carried a
    # stamp since it was first regenerated. Found 2026-10-19 while annotating 2
    # stale items. The standard is read from the linter rather than typed, so a
    # later version bump cannot leave a wrong number behind here.
    try:
        import sys as _sys
        _sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
        from note_vagueness_lint import CURRENT_NOTE_STANDARD as _std
    except Exception:  # noqa: BLE001
        _std = ""
    # NO `---` BEFORE IT. The guard
    # `test_regenerating_twice_changes_nothing_but_the_timestamp` pins this
    # file at exactly 2 horizontal rules, which is how it detects the
    # structural duplication this script used to produce. A third rule for a
    # foot-line would have meant editing that guard to accommodate a
    # cosmetic choice of mine, and the linter requires the TEXT rather than
    # the rule. So the stamp goes in on its own.
    if _std:
        out += [f"Written under CDSFL note standard {_std}.", ""]
    return "\n".join(out).rstrip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true",
                    help="write the regenerated file (default is a dry run)")
    a = ap.parse_args()

    if not PARKED.is_file():
        print(f"FATAL: {PARKED} does not exist. Nothing to regenerate.")
        return 2
    m = _measure()
    before = {h: strip_own_output(b) for h, b in m.parked_items()}
    live, settled = classify(m)
    total = len(live) + len(settled)
    print(f"parked items          : {total}")
    print(f"  still need him      : {len(live)}")
    print(f"  already settled     : {len(settled)}")
    if total:
        try:
            from statsmodels.stats.proportion import proportion_confint
            lo, hi = proportion_confint(len(settled), total, method="wilson")
            blo, bhi = proportion_confint(len(settled), total, method="beta")
            print(f"  settled share       : {len(settled)} of {total} = "
                  f"{100*len(settled)/total:.4f}%")
            print(f"    Wilson          [{lo*100:.4f}%, {hi*100:.4f}%]")
            print(f"    Clopper-Pearson [{blo*100:.4f}%, {bhi*100:.4f}%]")
            share = (f"{len(settled)} of {total} = "
                     f"{100*len(settled)/total:.4f}%, Wilson "
                     f"[{lo*100:.4f}%, {hi*100:.4f}%]")
        except Exception as exc:                            # noqa: BLE001
            print(f"  interval unavailable: {exc}")
            share = f"{len(settled)} of {total}"
    else:
        share = "0 of 0"
    print()
    print("STILL LIVE, named so none hides behind the count:")
    for heading, _, _ in live:
        print(f"  {heading[:92]}")
    print()
    print("MOVED TO THE SETTLED SECTION:")
    for heading, _, why in settled:
        print(f"  {heading[:60]:<60} {why[:58]}")

    if not a.apply:
        print("\n--dry-run (default). Nothing written. Re-run with --apply.")
        return 0

    now = _dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    new = render(live, settled, now, share)
    # PROVE THE WRITE BEFORE REPLACING. The superseded bytes are kept beside the
    # file, because this rewrites a document the founder reads.
    bak = PARKED.with_suffix(".md.superseded-" +
                             _dt.datetime.now(_dt.timezone.utc)
                             .strftime("%Y%m%dT%H%M%SZ"))
    shutil.copy2(PARKED, bak)
    if not bak.is_file() or bak.read_bytes() != PARKED.read_bytes():
        print(f"FATAL: the superseded copy at {bak} does not match. REFUSING.")
        return 2
    PARKED.write_text(new, encoding="utf-8")
    print(f"\nwritten. superseded bytes kept at {bak.name}")
    # EVERY ITEM MUST SURVIVE THE MOVE, BODY AND ALL. Counting headings is not
    # enough: a render defect that truncated or dropped a body would leave the
    # count intact while losing the substance, which is the worse half of the
    # harm this script exists to fix. So each item's ORIGINAL TEXT must still be
    # present verbatim in its regenerated body -- a settled item gains a reason
    # line above its text and is therefore a superset, never a replacement.
    after = dict(_measure().parked_items())
    lost = sorted(set(before) - set(after))
    # COMPARED AFTER STRIPPING THIS SCRIPT'S OWN PREVIOUS OUTPUT, so a second
    # regeneration does not report its own reason lines as a body alteration.
    # Stripping removes only what this script writes, never his text, so the
    # property held is still "every word he or an earlier finding put here
    # survives".
    mangled = sorted(h for h in before if h in after
                     and before[h].strip() not in strip_own_output(after[h]))
    print(f"items before {total}, after {len(after)}")
    if lost:
        print(f"HEADINGS LOST: {len(lost)}")
        for h in lost:
            print(f"    {h[:88]}")
    if mangled:
        print(f"BODIES ALTERED: {len(mangled)}")
        for h in mangled:
            print(f"    {h[:88]}")
    if lost or mangled:
        print(f"REFUSING to leave this in place. Restore with:\n"
              f"    cp {bak} {PARKED}")
        return 2
    print(f"all {len(after)} items preserved, bodies verbatim")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
