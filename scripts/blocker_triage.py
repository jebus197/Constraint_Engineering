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
NEEDS_PERMISSION: list[tuple[str, re.Pattern, str]] = [
    ("IRREVERSIBLE", re.compile(
        r"delete\s+(a\s+)?(git\s+)?(ref|branch|tag)|git\s+(branch\s+-D|push\s+--force|reflog\s+expire)"
        r"|\bpaid\s+(seat|dispatch|model|run)\b|spend(ing)?\s+money"
        r"|answer[- ]key|sealed\s+(store|archive)|passphrase|vault", re.I),
     "one of his 3 standing categories: a git ref, money, or the sealed key store"),
    ("HIS_MACHINE", re.compile(
        r"password|credential|api\s*key|token\s+rotat|log\s*in\b|sign\s*in\b"
        r"|desktop\s+app\s+config|claude_desktop_config|system\s+settings"
        r"|purchase|licence\s+renew|license\s+renew", re.I),
     "an account or machine setting that is his to change"),
]


def blocks_progress(text: str, tasks: pathlib.Path | None = None) -> tuple[bool, str]:
    """Does an OPEN entry on the task list depend on this item?

    Measured against the list rather than guessed from a category. The subject
    is matched against each OPEN entry's text; a hit means that entry cannot
    proceed until this is settled, which is exactly his criterion.
    """
    tasks = tasks or (REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md")
    try:
        sys.path.insert(0, str(REPO / "scripts"))
        from task_list_markers import parse_entries, ENTRY, _is_entry   # type: ignore
    except Exception as exc:
        return False, f"cannot read the task list ({exc}); parking rather than guessing"
    lines = tasks.read_text(encoding="utf-8").splitlines()
    starts = [i for i, l in enumerate(lines) if _is_entry(l)]
    states = {e.ident: e.state for e in parse_entries(tasks)}

    # IDENTIFIERS AND PATHS ONLY. A capitalised ordinary word is not a subject.
    # An earlier filter kept any 6+ character token that was not all-lowercase, so
    # "Repair the experimental notes" matched entry 7.1 on the word "Repair".
    terms = {t for t in re.findall(r"[A-Za-z_][A-Za-z0-9_]*_[A-Za-z0-9_]+"
                                   r"|[A-Za-z][A-Za-z0-9]*-[A-Za-z0-9-]+"
                                   r"|[\w./-]+\.(?:py|json|md|sh|txt)"
                                   r"|[\w-]+/[\w./-]+", text)
             if len(t) >= 6}
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
        end = starts[n + 1] if n + 1 < len(starts) else len(lines)
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
        end = starts[n + 1] if n + 1 < len(starts) else len(lines)
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
    with PARKED.open("a", encoding="utf-8") as f:
        f.write(f"\n## {title}\n\n*Parked {stamp}.*\n\n{detail.strip()}\n")
    return PARKED


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--title", help="short name for the item")
    ap.add_argument("--detail", default="", help="what it is, in full")
    ap.add_argument("--check-only", action="store_true",
                    help="classify and print; write nothing")
    a = ap.parse_args()
    if not a.title:
        ap.error("--title is required")

    verdict, why, perm = classify(f"{a.title}\n{a.detail}")
    print(f"  {verdict}: {why}")
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
    if perm:
        detail += f"\n\n**Needs your decision — {perm}.** Not blocking; nothing on the list waits on it."
    p = park(a.title, detail)
    print(f"  -> appended to {p.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
