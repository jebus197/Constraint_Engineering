#!/usr/bin/env python3
"""Decide MECHANICALLY whether an item blocks, and park it if it does not.

WHY THIS EXISTS, in the founder's words, 2026-09-10: *"Why do you keep stopping
for non-blocking items? ... Why not just leave them all to discuss with me at the
end of the completed task list, unless there is something that clearly warrants
my immediate attention? ... Can you not write some kind of mechanical 'is
blocker' / 'is not blocker' 'append to end of task list/final report' script?"*

THE ANSWER TO WHY A SCRIPT AND NOT A RESOLUTION. This project's own record:
*"The failure was never the absence of a rule or a checker; it was never running
the checker."* A resolution to stop interrupting is a claim about future
behaviour, and claims are the category this project measures worst. A predicate
is checkable, and a parking file is a place the item goes instead of into a
sentence addressed to him.

HIS CRITERION, VERBATIM, 2026-09-10: *"My criteria is very simple. Does it
prevent further progress on the task list? If so, then yes, it's a blocker. If
not, then append to the closing/final report."*

THE FIRST VERSION OF THIS SCRIPT GOT IT WRONG, and the way it was wrong is worth
keeping. It used 4 rules -- IRREVERSIBLE, NEEDS_HIS_HANDS, FROZEN_ARTEFACT,
WOULD_WASTE_WORK -- and 3 of those are not about progress at all. It classified
editing his desktop config as BLOCK when that edit blocked nothing, and it
reported `sk_enabled` to him as a blocker when no open entry waited on it. It had
conflated 2 orthogonal questions:

    DOES IT STOP PROGRESS?          -> blocker      -> raise it now
    IS IT HIS TO AUTHORISE?         -> permission   -> park it, and do not do it

An item can be either, both, or neither. Treating the second as if it implied the
first is what produced the interruptions he was objecting to.

SO THE PREDICATE NOW TESTS THE ACTUAL QUESTION. An item BLOCKS only if some OPEN
entry on the task list cannot proceed without it -- established by looking for
the item's subject in the open entries, not by matching a category. Permission is
a SEPARATE flag: it suppresses the action, never the work, and it travels with
the parked item so he sees it at the end.
"""
from __future__ import annotations

import argparse
import datetime
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
PARKED = REPO / "experimental_notes" / "PARKED_FOR_THE_FOUNDER.md"

#: Actions the assistant must NOT take unilaterally. This is a PERMISSION gate,
#: not a blocker: it stops the action, never the work, and it is reported at the
#: end rather than as an interruption -- unless the item ALSO blocks progress.
#: ★ `panel`, `review`, `arm` AND `experiment` WERE ADDED TO THE PAID NOUN SET
#: ON 2026-10-30, BECAUSE THE GATE DID NOT CATCH THE MOST NATURAL PHRASING OF
#: THE THING IT EXISTS TO STOP. Measured by calling `classify`: his ruling is
#: *"This is declined. No paid dispatch can happen without my express
#: authorisation."*, and `classify("Dispatch the paid panel to 4 seats for this
#: round.")` returned NO permission flag, because the pattern required `paid` to
#: be followed by one of exactly 4 nouns and `panel` was not among them. The
#: same text with "paid dispatch" was caught. So the gate's coverage depended on
#: which noun the sentence happened to use for the same act.
#:
#: THIS IS NOT A NEW CATEGORY. It is the existing IRREVERSIBLE category matching
#: the words it already intends; a paid panel IS a paid dispatch. Whether a FREE
#: dispatch or a simulated run should also require permission -- both spend his
#: token allowance and occupy his 8 cores, which his 2026-10-11 ruling makes a
#: fixed resource -- is a 4th category and therefore his to rule on, so it is
#: raised as a ticket rather than added here in his name.
NEEDS_PERMISSION: list[tuple[str, re.Pattern, str]] = [
    ("IRREVERSIBLE", re.compile(
        r"delete\s+(a\s+)?(git\s+)?(ref|branch|tag)|git\s+(branch\s+-D|push\s+--force|reflog\s+expire)"
        r"|\bpaid\s+(seat|dispatch|model|run|panel|review|arm|experiment)\b"
        r"|spend(ing)?\s+money"
        r"|answer[- ]key|sealed\s+(store|archive)|passphrase|vault", re.I),
     "one of his 3 standing categories: a git ref, money, or the sealed key store"),
    ("HIS_MACHINE", re.compile(
        r"password|credential|api\s*key|token\s+rotat|log\s*in\b|sign\s*in\b"
        r"|desktop\s+app\s+config|claude_desktop_config|system\s+settings"
        r"|purchase|licence\s+renew|license\s+renew", re.I),
     "an account or machine setting that is his to change"),
]


def _looks_like_an_identifier(token: str, text: str) -> bool:
    """Is `token` a code identifier, or ordinary hyphenated English?

    ★ ADDED 2026-10-30, AND IT IS FORCED BY THE WINDOW REPAIR RATHER THAN
    CHOSEN. While `blocks_progress` truncated the entry list at the
    supplementary heading it never reached an OPEN entry, so this defect could
    not fire. With the window corrected it fired immediately: the extractor's
    second alternative, `[A-Za-z][A-Za-z0-9]*-[A-Za-z0-9-]+`, matches ANY
    hyphenated word, and this project's prose is full of them. Measured over
    the 186 entry bodies that day: 1,028 of 2,686 distinct terms were
    hyphenated English with no digit and no underscore -- 0.382725, Wilson 95%
    [0.364524, 0.401262], Clopper-Pearson [0.364294, 0.401413] -- including
    `AI-powered`, `Agresti-Coull`, `BYTE-IDENTICAL` and `cross-verified`. On
    those, every one of the 6 OPEN entries was reported as blocking progress.

    THIS IS THE FUNCTION'S OWN STATED INTENT, NOT A NEW POLICY. The comment
    above the extractor already reads "IDENTIFIERS AND PATHS ONLY. A
    capitalised ordinary word is not a subject." A hyphenated ordinary word is
    the same thing with a hyphen in it.

    WHAT IS DELIBERATELY KEPT. A CLI flag is the one kebab-case form that is a
    real symbol, so `--check-only` and `--record-restore` still count, matched
    by their own `--` in the text rather than by shape. A concept such as
    `B-cell` is dropped, which is correct under the stated intent: it names what
    work is ABOUT, not a symbol an entry can wait on.

    REJECTED ON MEASUREMENT, recorded so it is not proposed again: requiring the
    term and the dependency phrase to sit on the SAME LINE changed nothing, 6 of
    6 before the restriction and 3 of 3 after it, because this project writes one
    paragraph per line and those lines run to about 1,100 characters.
    """
    if "/" in token or token.endswith((".py", ".json", ".md", ".sh", ".txt")):
        return True                       # a path
    if "_" in token:
        return True                       # snake_case
    if any(c.isdigit() for c in token):
        return True                       # exp53_control..., free-run1
    return f"--{token}" in text           # a CLI flag


def blocks_progress(text: str, tasks: pathlib.Path | None = None) -> tuple[bool, str]:
    """Does an OPEN entry on the task list depend on this item?

    Measured against the list rather than guessed from a category. The subject
    is matched against each OPEN entry's text; a hit means that entry cannot
    proceed until this is settled, which is exactly his criterion.
    """
    tasks = tasks or (REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md")
    try:
        sys.path.insert(0, str(REPO / "scripts"))
        from task_list_markers import (parse_entries, ENTRY, _is_entry,  # type: ignore
                                end_of_entries, body_bounds)
    except Exception as exc:
        return False, f"cannot read the task list ({exc}); parking rather than guessing"
    lines = tasks.read_text(encoding="utf-8").splitlines()

    # THE LAST ENTRY'S BODY MUST NOT RUN TO END OF FILE (2026-09-17).
    # Bodies are sliced from one entry start to the next, so the final entry
    # absorbed everything after it. On 2026-09-11 a SUPPLEMENTARY LIST of 59
    # generated entries was appended to this same file, and from that moment
    # W1 -- the last entry, state BLOCKED -- carried all 61 of its table rows:
    # 90 lines and 10,725 characters it does not contain. One of those rows
    # names the verdict-tuple guard, so the predicate reported W1 as blocked by
    # an item appearing nowhere in W1, and a BLOCKED state short-circuits the
    # dependency check that would otherwise have caught it.
    #
    # The boundary is the supplementary heading, because that list is a
    # different document sharing a file: its rows are a table ABOUT entries,
    # not entry bodies. Measured before the fix: W1's body was 10,725 chars;
    # after, it is its own text alone.
    # ★ THE TRUNCATION IS GONE, 2026-10-30. It read
    # `lines = lines[:end_of_entries(lines)]`, which dropped every entry after
    # the supplementary heading -- 72 of 186 on the day it was measured, and ALL
    # 6 that were OPEN. The scan then reported "no entry declares a dependency
    # on it" for items it had never read, which is the triage answering a
    # question it could not see. Bodies are now bounded per entry by
    # `body_bounds`, so the 2026-09-17 property is kept without the amputation.
    starts = [i for i, l in enumerate(lines) if _is_entry(l)]
    states = {e.ident: e.state for e in parse_entries(tasks)}

    # IDENTIFIERS AND PATHS ONLY. A capitalised ordinary word is not a subject.
    # An earlier filter kept any 6+ character token that was not all-lowercase, so
    # "Repair the experimental notes" matched entry 7.1 on the word "Repair".
    terms = {t for t in re.findall(r"[A-Za-z_][A-Za-z0-9_]*_[A-Za-z0-9_]+"
                                   r"|[A-Za-z][A-Za-z0-9]*-[A-Za-z0-9-]+"
                                   r"|[\w./-]+\.(?:py|json|md|sh|txt)"
                                   r"|[\w-]+/[\w./-]+", text)
             if len(t) >= 6 and _looks_like_an_identifier(t, text)}
    if not terms:
        return False, "no distinctive term to match against the entries"

    # A TERM THAT APPEARS EVERYWHERE CARRIES NO INFORMATION. `reference_runner_v3.py`
    # is named by many entries; matching it proves only that the file is central,
    # not that any entry waits on this particular question about it. So a term
    # must be SELECTIVE -- it must distinguish a few entries from the rest -- and
    # the threshold is stated rather than tuned: more than a quarter of the entries
    # is not a dependency, it is a subject everyone shares.
    bodies = []
    for n, i in enumerate(starts):
        _, end = body_bounds(lines, starts, n)
        bodies.append((ENTRY.match(lines[i]).group(1), "\n".join(lines[i:end])))
    cap = max(2, len(bodies) // 4)
    selective = {t for t in terms if sum(1 for _, b in bodies if t in b) <= cap}
    if not selective:
        common = sorted(terms)[:2]
        return False, (f"the only matching terms {common} appear in more than "
                       f"{cap} entries, so they identify a shared subject rather "
                       f"than a dependency")
    terms = selective

    # A STATED PRECONDITION, NOT A MENTION. `reference_runner_v3.py` appears in
    # many open entries; that does not make every question about it a blocker.
    # An entry is blocked BY this item only where the entry says so: it carries
    # state BLOCKED, or its text names the item inside a passage declaring a
    # dependency. Anything looser reports a mention as an obstruction, which is
    # how a triage tool becomes the interruption it was built to prevent.
    DECLARES = re.compile(
        r"BLOCKED ON|blocked on|NEEDS THE FOUNDER|NEEDS YOUR RULING|awaits? (?:his|the founder)"
        r"|cannot proceed|precondition|is the founder's(?: call| to)?|reserved to him", re.I)
    for n, i in enumerate(starts):
        _, end = body_bounds(lines, starts, n)
        ident = ENTRY.match(lines[i]).group(1)
        state = states.get(ident)
        if state not in ("OPEN", "BLOCKED"):
            continue
        body = "\n".join(lines[i:end])
        hit = [t for t in terms if t in body]
        if not hit:
            continue
        # A BARE FILE PATH CANNOT ESTABLISH DEPENDENCE. A file is central to many
        # entries; naming one says what the work is ABOUT, not what it waits on.
        # An OPEN entry therefore needs a non-path identifier to match; a BLOCKED
        # entry does not, because its state already declares the dependency.
        only_paths = all(("/" in t or t.endswith((".py", ".json", ".md", ".sh", ".txt"))
                          ) for t in hit)
        if state == "OPEN" and only_paths:
            continue
        if state == "BLOCKED" or DECLARES.search(body):
            return True, (f"entry {ident} (state {state}) names {sorted(hit)[:2]} "
                          f"inside a declared dependency, so it cannot proceed")
    return False, ("no entry declares a dependency on it; it is mentioned but "
                   "nothing is waiting")


#: Phrases by which an entry DECLARES ITSELF a decision only the founder can
#: make. Matched on the entry's own committed text, so this is a reading of
#: what the record says, never an inference about what the item "feels like".
DECLARES_A_DECISION = re.compile(
    r"NEEDS A POLICY RULING|NEEDS (?:YOUR|HIS|A FOUNDER) RULING"
    r"|NEEDS? (?:THE )?FOUNDER'?S? (?:RULING|DECISION)"
    r"|(?:his|the founder's) (?:call|decision) (?:to make|not ours)"
    r"|(?:his|her|their) to decide|NEEDS HIS DECISION"
    r"|awaiting (?:his|the founder's) ruling",
    re.IGNORECASE)


def decision_required(text: str) -> str:
    """Why this item is the FOUNDER'S DECISION, or "" when it is not.

    THE THIRD QUESTION, AND THE SCRIPT ANSWERED ONLY 2 OF ITS OWN 3 UNTIL
    2026-10-12. This module's header names three: does it block progress, is it
    his to authorise, and is the ITEM ITSELF a decision only he can make. Only
    the first two were implemented. Both free seats of the 2026-10-12 panel
    found the gap independently and neither wrote the fix.

    WHAT IT COST. A8 -- whose own committed text ends "NEEDS A POLICY RULING:
    track them, relocate them, or accept and label them" -- triaged as a bare
    PARK with no flag, and `hooks/work_not_narrate.py` reads PARK as "carry
    on". So the hook pushed the assistant to go and DO a thing the entry itself
    says is the founder's to decide. A19 is the same shape: a flag on/off
    design call.

    IT IS A THIRD FLAG, NOT A THIRD VERDICT, and that is deliberate. The 3
    questions are orthogonal -- an item can be any combination of blocking,
    permission-bearing and decision-bearing -- and FOLDING TWO OF THEM INTO ONE
    IS THE DEFECT THE FIRST VERSION OF THIS SCRIPT SHIPPED (it called editing a
    desktop config a BLOCK when that edit blocked nothing). `classify` keeps
    its 3-tuple so that no caller changes shape.
    """
    m = DECLARES_A_DECISION.search(text or "")
    return m.group(0) if m else ""


def classify(text: str) -> tuple[str, str, str]:
    """(verdict, why, permission). BLOCK only if progress is prevented.

    The permission flag is returned ALONGSIDE the verdict rather than folded
    into it, because the 2 are orthogonal and folding them is the defect the
    first version shipped.
    """
    perm = ""
    for name, rx, why in NEEDS_PERMISSION:
        if rx.search(text):
            perm = f"{name}: {why}"
            break
    blocked, why = blocks_progress(text)
    if blocked:
        return "BLOCK", why, perm
    return "PARK", why, perm


def park(title: str, detail: str, stamp: str | None = None) -> pathlib.Path:
    if stamp is None:
        stamp = subprocess.run(["date", "-Iseconds"], capture_output=True,
                               text=True).stdout.strip()
    if not PARKED.is_file():
        PARKED.write_text(
            "# Parked for the founder — non-blocking items, newest last\n\n"
            "**Opened 2026-09-10 on his instruction:** *\"Why not just leave them all to "
            "discuss with me at the end of the completed task list, unless there is something "
            "that clearly warrants my immediate attention?\"*\n\n"
            "Every item here was classified by `scripts/blocker_triage.py` as NOT blocking. "
            "Nothing here is dropped; it is queued. Items that DO block are raised at once and "
            "never appear in this file.\n\n---\n",
            encoding="utf-8")
    # ALREADY PARKED IS NOT PARKED AGAIN.
    #
    # MEASURED 2026-09-11: running this script on an item already in the file
    # appended a SECOND heading for it, and a third for A8 within an hour of 2
    # earlier duplicates being merged by hand. The founder had just asked whether
    # the workload set out for him was significant; a queue that grows a heading
    # every time it is re-triaged answers that question wrongly, by inflating the
    # count of DECISIONS with copies of one decision.
    #
    # Compared on a normalised title -- case, punctuation and runs of whitespace
    # removed -- because "A8: re-point the 20 note citations" and "A8: re-point
    # 20 note citations" are the same question and differ by a word.
    existing = PARKED.read_text(encoding="utf-8") if PARKED.is_file() else ""
    if _normalise(title) in {_normalise(h) for h in _headings(existing)}:
        return None
    # A NEW ITEM GOES IN FRONT OF THE SETTLED SECTION, NOT AFTER IT.
    #
    # Since 2026-10-17 `scripts/regenerate_the_parked_file_2026-10-17.py` moves
    # every settled item to a section at the FOOT of this file, so the end of the
    # file is no longer the live queue -- it is the archive. A plain append would
    # have put each newly parked item inside that archive, buried on arrival,
    # which is the defect task B3 exists to fix reproduced by a different route.
    # Found by tracing what else writes to this file rather than by a failure.
    #: ★ AN EMPTY BODY IS REFUSED, added 2026-10-29. `detail` is the `--detail`
    #: argument and it DEFAULTS TO EMPTY, so a PARK that matched no permission
    #: rule and named no decision wrote a heading, a timestamp and nothing else.
    #: It happened: the panel-dispatch item parked at 17:53 that day. 2 separate
    #: harms. It tells the founder NOTHING, which defeats the file's own stated
    #: purpose that parked is queued rather than dropped; and the regenerator
    #: cannot round-trip it, so
    #: `test_the_parked_file_regenerates_without_losing_him_2026-10-17` went red
    #: with "body lost" -- the body it extracted ran past the blank lines into
    #: the section divider. `defer()` in the ticket store already refuses a
    #: deferral with no stated reason, for the same reason, so this is the
    #: existing rule applied to the other queue rather than a new one.
    if not detail.strip():
        raise ValueError(
            "park() needs a detail saying WHAT the item is and why it can wait. "
            "An entry with a heading and no body tells him nothing and cannot be "
            "regenerated. Pass --detail, or let main() seed it from the "
            "verdict's own reason.")
    entry = f"\n## {title}\n\n*Parked {stamp}.*\n\n{detail.strip()}\n"
    marker = "\n---\n\n# Settled — kept for the record"
    cut = existing.find(marker)
    if cut == -1:
        with PARKED.open("a", encoding="utf-8") as f:
            f.write(entry)
    else:
        PARKED.write_text(existing[:cut] + entry + existing[cut:],
                          encoding="utf-8")
    return PARKED


def _headings(blob: str) -> list[str]:
    return [ln[3:].strip() for ln in blob.splitlines() if ln.startswith("## ")]


def _normalise(title: str) -> str:
    """A title reduced to the question it asks.

    Drops anything after an em dash or a double hyphen, which is where this
    file's headings carry status notes such as "SUPERSEDED" or "SAME DECISION AS
    10.2" -- a heading that gained a note is still the same item.
    """
    head = re.split(r"—|--", title)[0].lower()
    # Articles dropped as well as punctuation: "re-point 20 note citations" and
    # "re-point THE 20 note citations" are the same question, and the first pair
    # this was tested on differed by exactly that word.
    head = re.sub(r"\b(the|a|an)\b", " ", head)
    return re.sub(r"[^a-z0-9]+", "", head)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--title", help="short name for the item")
    ap.add_argument("--detail", default="", help="what it is, in full")
    ap.add_argument("--check-only", action="store_true",
                    help="classify and print; write nothing")
    a = ap.parse_args()
    if not a.title:
        ap.error("--title is required")

    _text = f"{a.title}\n{a.detail}"
    verdict, why, perm = classify(_text)
    decision = decision_required(_text)
    print(f"  {verdict}: {why}")
    if decision:
        print(f"  HIS DECISION — the entry says so itself: \"{decision}\"")
        print("  -> do NOT act on it; carry it to him as a decision, not as work.")
    if perm:
        print(f"  NEEDS PERMISSION — {perm}")
        print("  -> do NOT do it unilaterally. That is separate from whether it blocks.")
    if verdict == "BLOCK":
        print("  -> raise this with the founder NOW; an open entry is waiting on it")
        return 2
    if a.check_only:
        print("  -> would be appended to " + str(PARKED.relative_to(REPO)))
        return 0
    detail = a.detail
    #: SEED FROM THE VERDICT'S OWN REASON when no --detail was given, so the
    #: entry always says why it was parked. `why` is what `classify` returned
    #: and is the most accurate 1-line account available without the caller.
    if not detail.strip():
        detail = (f"**Parked by `scripts/blocker_triage.py`, which classified it "
                  f"NOT BLOCKING: {why}.** No fuller description was supplied at "
                  f"triage time, so this body is the classifier's own reason. "
                  f"Pass `--detail` to say more.")
    if decision:
        detail += (f"\n\n**This is YOUR DECISION, by the entry's own words — "
                   f"\"{decision}\".** Not blocking, and not work to be done "
                   f"meanwhile.")
    if perm:
        detail += f"\n\n**Needs your decision — {perm}.** Not blocking; nothing on the list waits on it."
    p = park(a.title, detail)
    if p is None:
        # ALREADY PARKED. A queue that grows a heading every time an item
        # is re-triaged inflates the count of DECISIONS with copies of one
        # decision, which is the opposite of what this file is for.
        print("  -> already parked; not appended again")
    else:
        print(f"  -> appended to {p.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
