#!/usr/bin/env python3
"""Read and maintain the machine-readable markers on the CDSFL master task list.

A NOTE ON THE FUNCTION NAMES. `parse_entries` and `parse_events` were both called
`parse` until 2026-09-09, when the suite refused a commit: a repository guard
collects, BY NAME, every function returning a tuple and then objects when such a
name is bound whole and tested for truth. `parse` in
scripts/remote_bridge_recovery_2026-09-09.py returns a tuple, so it poisoned every
other `parse` in the tree. The guard's name-based scope is a deliberate
over-reach -- it cannot resolve which `parse` a call meant -- and the right answer
is not to weaken it but to stop using a name so generic that two unrelated
functions collide under it. Rule 19, name the subject, applied to code.

WHY THIS EXISTS. On 2026-09-09 two different regular expressions over
`experimental_notes/CDSFL_MASTER_TASK_LIST.md` counted 29 entries and 48. A third,
stricter one counted 23. The true figure is 59. A list that cannot be counted
cannot be reported on, and a task-list pulse built on a regex would inherit the
ambiguity it was meant to remove. So every entry carries an explicit marker and
this module is the only thing that reads or writes them.

THE TWO VOCABULARIES, AND WHY BOTH. The founder asked, verbatim: "Can you not use
them both to cross check the list?" They are orthogonal, which is what makes the
cross-check worth having rather than redundant:

  state  -- OPEN / DONE / BLOCKED / DEFERRED. The state of the TASK.
  status -- PROPOSED / BUILT / TESTED / COMMITTED / ENABLED. Note standard Rule 20,
            the maturity of the WORK PRODUCT.

Neither determines the other. A COMMITTED item can still be OPEN, because
committed is not enabled. A DONE item can carry no code at all when it is a
documentation write-back. Enumerating the joint space gives 20 cells of which 17
are reachable and 3 are contradictory:

    state=DONE with status in {PROPOSED, BUILT, TESTED}

which is a task closed before its work was committed. A single vocabulary cannot
express that fault. `--check` reports it.

The marker is an HTML comment so it is invisible in rendered markdown and does not
disturb the prose the founder reads.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"

#: WITHDRAWN added 2026-09-09, on the cross-check's first run. It flagged entry
#: 1.3 as state=DONE status=PROPOSED and was RIGHT to: an item the founder closed
#: by ruling has no work product, so no Rule 20 status describes it and DONE
#: falsely implies work was completed. Neither vocabulary could express "closed
#: because it will not be done", which is a real and common outcome here. The
#: contradiction was genuine; the remedy is a missing word, not a looser rule.
STATES = ("OPEN", "DONE", "BLOCKED", "DEFERRED", "WITHDRAWN")
STATUSES = ("PROPOSED", "BUILT", "TESTED", "COMMITTED", "ENABLED")
CONTRADICTORY = {("DONE", "PROPOSED"), ("DONE", "BUILT"), ("DONE", "TESTED")}

#: An entry opens with a bolded identifier. Both punctuation styles are in use --
#: `**R1. Title**` and `**6.1** Title` -- and both must match, because the reason
#: this module exists is that a pattern matching only one of them undercounted.
#: CORRECTED 2026-09-09, immediately after the first --apply run. The first
#: version required a period after the identifier, so `**R1. Title**` matched and
#: `**0.1 Title` did not: 16 real entries were silently skipped and the tool
#: reported the list "coherent" while ignoring a quarter of it. A parser that
#: silently omits is worse than one that fails, because it reports success.
#: Now: identifier, then a period, or `**`, or whitespace.
ENTRY = re.compile(r"^\*\*((?:[A-Z]{1,2})?\d+(?:\.\d+)?[a-z]?)(?:\.\*\*|\*\*|\.|)\s")
#: The marker, with an OPTIONAL trailing `evidence:` field.
#:
#: WHY EVIDENCE WAS ADDED (2026-09-10). The founder asked whether this engine
#: ensures the work can be completed mechanically. It did not. `CONTRADICTORY`
#: below refuses an entry only when its own 2 labels disagree with each other;
#: nothing ever compared a DONE marker against the repository. So the engine
#: recorded what the assistant CLAIMED. Measured the same night by 18 adversarial
#: agents re-running the tests rather than reading the claims: **11 of 19 DONE
#: entries were overstated, 57.89%, Wilson [36.3%, 76.9%]**, 2 reviewers agreeing
#: on every one, and 1 of the 11 was a live regression shipped to HEAD.
#:
#: The field is optional in the REGEX and required by the suite guard, so adding
#: it cannot break an entry that predates it while a DONE entry without it fails.
MARKER = re.compile(
    r"^<!--\s*task:\s*(\S+)\s*\|\s*state:\s*(\w+)\s*\|\s*status:\s*(\w+)"
    r"(?:\s*\|\s*evidence:\s*([^>]*?))?\s*-->")

#: Lines that LOOK like entries but are prose opening with a number in bold.
#: Listed explicitly rather than filtered by a heuristic, so that adding a real
#: entry beginning with a digit cannot be silently swallowed by a clever rule.
NOT_ENTRIES = ("11 tests", "1158 findings")


@dataclass
class Entry:
    ident: str
    line_no: int          # 1-based line of the entry heading
    text: str
    state: str | None
    status: str | None
    evidence: tuple = ()


def _is_entry(line: str) -> bool:
    if not ENTRY.match(line):
        return False
    body = line.lstrip("*")
    return not any(body.startswith(p) for p in NOT_ENTRIES)


def parse_entries(path: Path = LIST) -> list[Entry]:
    lines = path.read_text().splitlines()
    out: list[Entry] = []
    for i, line in enumerate(lines):
        if not _is_entry(line):
            continue
        ident = ENTRY.match(line).group(1)
        state = status = None
        evidence: tuple = ()
        if i + 1 < len(lines):
            m = MARKER.match(lines[i + 1])
            if m:
                state, status = m.group(2), m.group(3)
                raw = (m.group(4) or "").strip()
                evidence = tuple(x.strip() for x in raw.split(",") if x.strip())
        out.append(Entry(ident, i + 1, line, state, status, evidence))
    return out


def unsupported_done_entries(failed_nodeids, path: Path = LIST) -> dict[str, list[str]]:
    """DONE entries whose named evidence produced a failure this session.

    WHY THIS EXISTS, and it is the gap the guard shipped with. The DONE-evidence
    guard checks that each named file EXISTS, contains a real asserting test, and
    sits where the suite collects it. **It never checks that the test passes.**

    Proven on 2026-09-10 and not hypothetically: task V3 was marked DONE naming
    `bench/tests/test_note_lint_guard_2026-09-09.py`, that file went 10 of 10 RED
    when task V1 added a 6th guard to `hooks/pre-commit` and V3's fixture still
    built its repository with 4, and the DONE-evidence guard stayed green
    throughout. A completion claim was standing on a wholly failing test.

    This maps failures back to the entries that claim them, so a red suite says
    WHICH completion claims it invalidates rather than only how many tests broke.
    It adds no test runs: it reads outcomes the session already produced.

    `failed_nodeids` is any iterable of pytest node ids ("path::test_name").
    """
    failed_files = {str(n).split("::", 1)[0].replace("\\", "/")
                    for n in failed_nodeids}
    out: dict[str, list[str]] = {}
    for e in parse_entries(path):
        if e.state != "DONE":
            continue
        hit = [ev for ev in e.evidence
               if any(f.endswith(ev) or ev.endswith(f) for f in failed_files)]
        if hit:
            out[e.ident] = sorted(hit)
    return out


def infer(text: str) -> tuple[str, str]:
    """Best-effort defaults for an entry with no marker yet.

    Deliberately simple and reviewable. It is applied ONCE, and the result is
    then edited by hand where wrong; it is not a standing classifier.
    """
    up = text.upper()
    status = next((s for s in reversed(STATUSES) if re.search(rf"\b{s}\b", up)), "PROPOSED")
    if "CLOSED BY FOUNDER RULING" in up:
        state = "WITHDRAWN"
    elif "COMMITTED AND ENABLED" in up:
        state = "DONE"
    elif "DEFERRED" in up:
        state = "DEFERRED"
    elif re.search(r"\bBLOCKED ON\b", up):
        state = "BLOCKED"
    else:
        state = "OPEN"
    return state, status


def check(path: Path = LIST) -> tuple[int, list[str]]:
    """Return (exit code, problems). 0 problems means the list is coherent."""
    entries = parse_entries(path)
    problems: list[str] = []
    if not entries:
        return 1, [f"{path}: no entries parsed at all, which cannot be right"]
    seen: dict[str, int] = {}
    for e in entries:
        if e.state is None:
            problems.append(f"{path.name}:{e.line_no}: entry {e.ident} has no marker")
            continue
        if e.state not in STATES:
            problems.append(f"{path.name}:{e.line_no}: {e.ident} state {e.state!r} is not one of {STATES}")
        if e.status not in STATUSES:
            problems.append(f"{path.name}:{e.line_no}: {e.ident} status {e.status!r} is not one of {STATUSES}")
        if (e.state, e.status) in CONTRADICTORY:
            problems.append(
                f"{path.name}:{e.line_no}: {e.ident} is state={e.state} but status={e.status}. "
                f"A task cannot be done before its work was committed.")
        if e.ident in seen:
            problems.append(f"{path.name}:{e.line_no}: identifier {e.ident} already used at line {seen[e.ident]}")
        seen[e.ident] = e.line_no
    return (1 if problems else 0), problems


def apply_markers(path: Path = LIST) -> int:
    """Insert a marker under every entry that lacks one. Returns how many added."""
    lines = path.read_text().splitlines()
    out: list[str] = []
    added = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        if _is_entry(line):
            nxt = lines[i + 1] if i + 1 < len(lines) else ""
            if not MARKER.match(nxt):
                ident = ENTRY.match(line).group(1)
                state, status = infer(line)
                out.append(f"<!-- task: {ident} | state: {state} | status: {status} -->")
                added += 1
        i += 1
    path.write_text("\n".join(out) + "\n")
    return added


def summarise(path: Path = LIST) -> str:
    entries = parse_entries(path)
    counts = {s: sum(1 for e in entries if e.state == s) for s in STATES}
    nxt = next((e for e in entries if e.state == "OPEN"), None)
    # EVERY state is printed, not a chosen 4. The first version listed 4 of the 5
    # and the line read "59 entries, 56 open, 1 done, 1 blocked, 0 deferred" --
    # which sums to 58. A summary that omits a category is a silent falsehood of
    # the same kind the truncated-list guard exists to catch.
    parts = ", ".join(f"{counts[s]} {s.lower()}" for s in STATES if counts[s])
    head = f"{len(entries)} entries: {parts}"
    assert sum(counts.values()) == len(entries), (
        f"state counts {counts} sum to {sum(counts.values())}, not {len(entries)}")
    if nxt:
        title = re.sub(r"\*\*|`", "", nxt.text)[:72]
        head += f" — next: {title}"
    code, problems = check(path)
    if problems:
        head += f" | {len(problems)} MARKER PROBLEM(S): {problems[0]}"
    return head


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="insert missing markers")
    ap.add_argument("--check", action="store_true", help="report incoherence, exit 1 if any")
    ap.add_argument("--summary", action="store_true", help="one line, for the pulse hook")
    ap.add_argument("--path", type=Path, default=LIST)
    a = ap.parse_args()
    if a.apply:
        n = apply_markers(a.path)
        print(f"markers added: {n}")
    if a.summary:
        print(summarise(a.path))
    if a.check or not (a.apply or a.summary):
        code, problems = check(a.path)
        for p in problems:
            print(p, file=sys.stderr)
        if not problems:
            print(f"task list coherent: {len(parse_entries(a.path))} entries, 0 problems")
        return code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
