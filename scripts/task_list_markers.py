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
#: WHY `ruled` WAS ADDED (2026-10-16), and it closes a defect the founder
#: predicted from the symptom. He asked: *"Of the 13 decisions, are you certain
#: none of these are items I have previously ruled on? This seems an unusually
#: large HIL queue, which traditionally has been a strong indicator of
#: mechanical, and/or implementation/process failure."* It was.
#:
#: THE GAP. `state` is lifecycle (OPEN/DONE/BLOCKED/WITHDRAWN) and `status` is
#: build state (PROPOSED/BUILT/TESTED/COMMITTED/ENABLED). BOTH describe the
#: WORK. Nothing recorded whether the FOUNDER HAD RULED. So a ruling he gave
#: that was not immediately executed left its entry indistinguishable from one
#: he had never seen, and the morning report re-presented it as a decision.
#:
#: MEASURED 2026-10-16: of the 13 decisions put to him, 5 should not have been,
#: 38.4615%, 95% Wilson [17.7097%, 64.4771%]. R1 is the clearest: he ruled
#: "Restart it" on 2026-08-07 and again on 2026-09-06, and 70 days later the
#: marker still read BLOCKED/PROPOSED and the item still presented as a decision.
#: Separately, rulings live in 29 dated documents in `experimental_notes/`
#: created at 1.1469 per week over 177 days, and the one named
#: `CDSFL_Founder_Decision_Register_2026-07-06.md` has 3 commits and was last
#: touched 2026-08-15 -- so no canonical register exists to consult either.
#:
#: THE FIELD IS OPTIONAL, exactly as `evidence` is and for the same stated
#: reason: adding it cannot break an entry that predates it. Verified before the
#: change rather than after -- 0 of 107 existing markers parse differently under
#: the new pattern, and 0 evidence values contain a pipe, which is what makes
#: bounding the evidence group at `|` safe.
MARKER = re.compile(
    r"^<!--\s*task:\s*(\S+)\s*\|\s*state:\s*(\w+)\s*\|\s*status:\s*(\w+)"
    r"(?:\s*\|\s*evidence:\s*([^>|]*?))?"
    r"(?:\s*\|\s*ruled:\s*([^>|]*?))?\s*-->")

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
    #: The date the FOUNDER RULED on this entry, or None if he has not. A
    #: DEFAULT is given deliberately: `parse_entries` and every other caller
    #: constructs `Entry` positionally with 6 arguments, so a 7th field without
    #: a default would break ~20 importers at once.
    ruled: str | None = None


def _is_entry(line: str) -> bool:
    if not ENTRY.match(line):
        return False
    body = line.lstrip("*")
    return not any(body.startswith(p) for p in NOT_ENTRIES)


SUPPLEMENTARY = "# SUPPLEMENTARY LIST"


def end_of_entries(lines: list[str]) -> int:
    """Index of the first line past the last task entry.

    THE LAST ENTRY ABSORBS EVERYTHING AFTER IT. Every consumer slices a body as
    "this entry's heading to the next heading, or to end of file for the last
    one", which was harmless while the file held nothing but entries. On
    2026-09-11 a SUPPLEMENTARY LIST of 59 items was appended, and the last entry
    silently grew by 7,612 characters of table.

    It stopped being latent on 2026-09-17: `blocker_triage` read the term
    "verdict-tuple" out of that table, found it inside what it believed was
    entry W1, and reported W1 as declaring a dependency on it. W1 contains 0
    occurrences of the term.

    ONE DEFINITION, 6 CALLERS, because repairing 1 of 6 copies is precisely how
    this class of defect survives being found.
    """
    return next((i for i, l in enumerate(lines) if l.startswith(SUPPLEMENTARY)),
                len(lines))


def parse_entries(path: Path = LIST) -> list[Entry]:
    lines = path.read_text().splitlines()
    out: list[Entry] = []
    for i, line in enumerate(lines):
        if not _is_entry(line):
            continue
        ident = ENTRY.match(line).group(1)
        state = status = None
        evidence: tuple = ()
        ruled: str | None = None
        if i + 1 < len(lines):
            m = MARKER.match(lines[i + 1])
            if m:
                state, status = m.group(2), m.group(3)
                raw = (m.group(4) or "").strip()
                evidence = tuple(x.strip() for x in raw.split(",") if x.strip())
                ruled = (m.group(5) or "").strip() or None
        out.append(Entry(ident, i + 1, line, state, status, evidence, ruled))
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
            # MERGE, NEVER OVERWRITE. Found 2026-09-11 by the fable seat in panel
            # round 11 and reproduced before accepting. With 2 entries sharing an
            # identifier -- which happened the same day this guard shipped, when
            # 4 new entries reused Section P's own P1 to P4 -- the second
            # assignment DELETED the first entry's failing evidence from the
            # report. A guard keyed on identifiers, silently losing a finding to
            # a duplicate identifier, is the "a model can delete a finding by
            # repeating itself" shape in a new place.
            #
            # The duplicate ids are separately forbidden by
            # bench/tests/test_no_orphan_task_markers_2026-09-11.py, but a
            # reporter that loses data when its input is malformed is a second
            # defect and is fixed on its own terms.
            out[e.ident] = sorted(set(out.get(e.ident, ())) | set(hit))
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


def register_deferrals(store=None) -> dict[str, tuple[str, str]]:
    """Deferral as the REGISTER records it: {task_ref: (when, reason)}.

    HIS RULING, 2026-10-29, annotation 11 of
    `Responses/Decisions_Awaiting_You_2026-10-29.txt`: *"I accept your
    recommendation. fr"*, against the recommendation to *"Make the register the
    single source and have the marker derived from it, rather than the reverse"*.

    WHY THE REGISTER AND NOT THE MARKER. The register is the stricter of the 2:
    `defer` REFUSES without a stated reason and without a caller-supplied
    timestamp, and `close` refuses a terminal status without a verification. A
    marker is a hand-written word in a markdown comment and can say DEFERRED with
    no reason at all. A derived marker cannot drift from the register; the reverse
    arrangement lets it.

    IMPORTED LAZILY so this module stays usable where the register is not
    importable -- a `git archive` export, or a consumer that only wants to count
    entries. A missing register yields an EMPTY mapping, which makes
    `effective_state` fall back to the marker exactly as before this existed.
    """
    if store is None:
        try:
            if str(REPO) not in sys.path:
                sys.path.insert(0, str(REPO))
            from bench.ticket_store import TicketStore
            store = TicketStore()
            store.load()
        except Exception:                                    # pragma: no cover
            return {}
    out: dict[str, tuple[str, str]] = {}
    try:
        tickets = store.deferred_tickets()
    except Exception:                                        # pragma: no cover
        return {}
    for t in tickets:
        if getattr(t, "task_ref", ""):
            out[t.task_ref] = (t.deferred, t.deferred_reason)
    return out


def effective_state(entry: "Entry", deferrals: dict[str, tuple[str, str]]) -> str | None:
    """The entry's state WITH THE REGISTER AUTHORITATIVE over the marker.

    A TERMINAL MARKER WINS OVER A DEFERRAL, and that is not an exception to his
    ruling -- it is what the ruling means. DONE and WITHDRAWN are outcomes; a
    deferral is a statement about WHEN live work will happen. An entry that is
    finished is not "deferred to the end of the list", and reporting it so would
    put closed work back in front of him. Only a live state is overridden.
    """
    if entry.state in ("DONE", "WITHDRAWN"):
        return entry.state
    if entry.ident in deferrals:
        return "DEFERRED"
    return entry.state


def deferral_disagreements(path: Path = LIST, store=None) -> dict[str, list[str]]:
    """Where the marker and the register disagree about deferral, in both directions."""
    deferrals = register_deferrals(store)
    entries = parse_entries(path)
    marker_says = {e.ident for e in entries if e.state == "DEFERRED"}
    live = {e.ident for e in entries if e.state not in ("DONE", "WITHDRAWN")}
    known = {e.ident for e in entries}
    return {
        "marker_only": sorted(marker_says - set(deferrals)),
        "register_only": sorted((set(deferrals) & live) - marker_says),
        "register_defers_a_closed_entry": sorted(set(deferrals) & (known - live)),
        "register_defers_an_unknown_entry": sorted(set(deferrals) - known),
    }


def derive_deferred_markers(path: Path = LIST, apply: bool = False,
                            store=None) -> tuple[int, list[str]]:
    """Rewrite each disagreeing marker to the state the register implies.

    Returns (number changed or changeable, lines describing each). With
    ``apply=False`` nothing is written, which is how it is reported inside
    `--check`.

    ONLY `register_only` IS REWRITTEN. A marker saying DEFERRED where the
    register is silent is NOT quietly cleared, because the register being silent
    may mean the item has no ticket at all rather than that it is due -- and
    erasing a deferral the founder wrote by hand would be destroying a statement
    of his, not deriving from a source. Those are REPORTED for a decision.
    """
    dis = deferral_disagreements(path, store)
    changes: list[str] = []
    for ident in dis["register_only"]:
        changes.append(f"{ident}: marker -> state: DEFERRED (the register defers it)")
        if apply:
            set_marker(ident, state="DEFERRED", path=path)
    for ident in dis["marker_only"]:
        changes.append(
            f"{ident}: marker says DEFERRED and the register does not — "
            f"REPORTED, never auto-cleared, because the register may simply "
            f"hold no ticket for it")
    return len(dis["register_only"]), changes


def check(path: Path = LIST) -> tuple[int, list[str]]:
    """Return (exit code, problems). 0 problems means the list is coherent."""
    entries = parse_entries(path)
    problems: list[str] = []
    if not entries:
        return 1, [f"{path}: no entries parsed at all, which cannot be right"]

    # ★ DEFERRAL IS THE REGISTER'S TO STATE, on his ruling of 2026-10-29. The 2
    # representations were independent and disagreed in both directions on the
    # day the ruling was given: the register deferred 5 live entries the markers
    # called OPEN. Reported here rather than silently reconciled, because a
    # checker that repairs without reporting hides the drift it exists to find.
    #: ★ ONLY FOR THE CANONICAL LIST, and the first version omitted this guard.
    #: `deferral_disagreements` reads the LIVE register, whose `task_ref` values
    #: name entries of the canonical list and nothing else. Run against a
    #: temporary LIST.md -- which 20 tests do -- every real deferral became
    #: "the register defers B13, which is not an entry this parser recognises",
    #: so a path-parameterised check was mixing in a global data source. The
    #: pre-commit board caught it and refused the commit, which is the gate
    #: doing exactly its job.
    _dis = (deferral_disagreements(path)
            if Path(path).resolve() == LIST.resolve()
            else {"marker_only": [], "register_only": [],
                  "register_defers_a_closed_entry": [],
                  "register_defers_an_unknown_entry": []})
    for _ident in _dis["register_only"]:
        problems.append(
            f"{path.name}: {_ident} is deferred in the register and its marker "
            f"does not say so. The register is the single source; run "
            f"`python3 scripts/task_list_markers.py --derive-deferrals --apply` "
            f"to derive the marker from it.")
    for _ident in _dis["marker_only"]:
        problems.append(
            f"{path.name}: {_ident} has marker state DEFERRED and the register "
            f"does not defer it. Either the register is missing a ticket for it "
            f"or the deferral is discharged — decide, do not auto-clear.")
    for _ident in _dis["register_defers_an_unknown_entry"]:
        problems.append(
            f"{path.name}: the register defers {_ident}, which is not an entry "
            f"this parser recognises, so the deferral is invisible on the list.")

    # AN ORPHANED MARKER IS AN INVISIBLE ENTRY, and this reported nothing.
    #
    # FOUND 2026-10-17 BY A CONTROLLED TEST, after C24 was written with a
    # heading opening `★ **C24.` rather than `**C24.`. `ENTRY` requires the
    # line to start with the bold span, so the heading was not recognised, the
    # entry did not exist for any consumer -- the ticket register, the
    # DONE-evidence guard, the counts, the resume pointer -- and this checker
    # still answered "coherent, 0 problems". Injecting a deliberately orphaned
    # marker reproduced it exactly.
    #
    # THE EXISTING GUARD DOES NOT COVER THIS. `test_no_entry_is_swallowed_by_an_edit`
    # compares the identifier SET against HEAD, so it catches an entry that
    # DISAPPEARS. An entry that never appeared is absent from both sides and
    # passes. The 2 checks are complementary, which is why this is a separate
    # one rather than a widening of that.
    #
    # `ENTRY` is deliberately NOT widened to admit a leading star: the star
    # marks an ADDENDUM in this file, and an addendum's first line routinely
    # names an identifier -- `★ **C19 IS BUILT ...` -- so admitting it would
    # mint a phantom entry for every addendum written. Naming the orphan is
    # exact; loosening the pattern would guess.
    parsed = {e.ident for e in entries}
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        m = MARKER.match(line.strip())
        if m and m.group(1) not in parsed:
            problems.append(
                f"{path.name}:{n}: marker for {m.group(1)} has no entry heading "
                f"the parser recognises, so the entry is invisible to every "
                f"consumer. An entry heading must begin with its bold "
                f"identifier, as in **{m.group(1)}. ...**")

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


#: Where a DONE entry's evidence must live for the suite to run it. The
#: DONE-evidence guard resolves containment rather than matching this as a
#: prefix, because `bench/tests/../../../tmp/test_x.py` matches the prefix and
#: resolves outside the repository -- cc2 defeated the first version that way
#: in panel review on 2026-09-10.
#: RELATIVE, and resolved against the caller's root. Written first as
#: `REPO / "bench" / "tests"`, an absolute path, which made `evidence_objections`
#: ignore its own `root` argument: every check against a temporary tree refused
#: a perfectly sound file as "outside". Its own guard caught it on the first run
#: -- 6 of 13 red -- which is what a parameter that nothing exercises looks like.
EVIDENCE_HOME = Path("bench") / "tests"


def _asserts_something(node, src: str) -> bool:
    """Does this test function assert anything that is not a truthy constant?

    `def test_hollow(): assert True` satisfied the first version of the
    DONE-evidence guard -- found by cc2 in panel review, 2026-09-10.
    """
    import ast
    for inner in ast.walk(node):
        if isinstance(inner, ast.Assert):
            test = inner.test
            if isinstance(test, ast.Constant) and bool(test.value):
                continue
            return True
    return "raises" in (ast.get_source_segment(src, node) or "")


def evidence_objections(ident: str, evidence, root: Path = REPO) -> list[str]:
    """Every reason a DONE entry's named evidence is not evidence. [] if sound.

    ONE DEFINITION, TWO CALLERS, and that is the whole point of extracting it.
    The checks lived inline in `test_done_markers_carry_evidence_2026-09-10.py`
    and nowhere else, so the only thing that could object to a bad evidence
    value was the suite -- AFTER the marker had been written and a commit
    attempted. Three times in one session (tasks C16, B15 and the C2/C9 pair)
    an entry was marked DONE carrying either a prose annotation or a directory
    as its evidence, and each time the refusal arrived as a red suite rather
    than as a refusal to write.

    `set_marker` now calls this BEFORE writing, and the guard calls it instead
    of keeping its own copy, so the two cannot drift apart. Neither form
    asserts on the other's source text: both execute this function.
    """
    import ast

    out: list[str] = []
    if not evidence:
        return [f"task {ident}: DONE with no evidence named"]
    for name in evidence:
        target = (root / name)
        if not target.exists():
            out.append(f"task {ident}: {name} does not exist")
            continue
        if target.is_dir():
            out.append(f"task {ident}: {name} is a directory, not a test file")
            continue
        resolved = target.resolve()
        home = (root / EVIDENCE_HOME).resolve()
        if not (home in resolved.parents or resolved.parent == home):
            out.append(f"task {ident}: {name} resolves to {resolved}, outside "
                       f"{home}, so nothing in the suite runs it")
            continue
        src = resolved.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(src, filename=name)
        except SyntaxError as exc:
            out.append(f"task {ident}: {name} does not parse ({exc})")
            continue
        funcs = [n for n in ast.walk(tree)
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                 and n.name.startswith("test_")]
        if not funcs:
            out.append(f"task {ident}: {name} defines no test function")
            continue
        if not any(_asserts_something(n, src) for n in funcs):
            out.append(f"task {ident}: {name} has {len(funcs)} test "
                       f"function(s) and not one of them asserts anything")
    return out


def set_marker(ident: str, *, state: str | None = None,
               status: str | None = None, evidence=None,
               ruled: str | None = None, path: Path = LIST) -> str:
    """Rewrite one entry's marker, REFUSING unsound DONE evidence.

    Fields not passed are carried over from the existing marker, so advancing
    `state` alone cannot silently drop a `ruled:` date the founder earned.

    THE REFUSAL IS THE POINT. Every previous close was an ad-hoc inline script,
    and three of them wrote an evidence value the suite then rejected. The
    worst shape was the quietest: a script guarded with `if "evidence:" not in
    marker`, which SKIPPED entries that already carried a `Responses annotation
    dated ...` value -- provenance for the question, not verification of the
    answer -- and so left the stale value in place while reporting success.

    Raises KeyError for an unknown identifier, ValueError for an unknown state
    or status, and ValueError listing every objection when the resulting entry
    would be DONE on evidence that is not a test the suite runs.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    idx = None
    for i, line in enumerate(lines):
        if _is_entry(line) and ENTRY.match(line).group(1) == ident:
            idx = i
            break
    if idx is None:
        raise KeyError(f"no task entry {ident!r} in {path}")

    marker_at = idx + 1
    existing = MARKER.match(lines[marker_at]) if marker_at < len(lines) else None
    if existing:
        cur_state, cur_status = existing.group(2), existing.group(3)
        cur_ev = tuple(x.strip() for x in (existing.group(4) or "").split(",")
                       if x.strip())
        cur_ruled = (existing.group(5) or "").strip() or None
    else:
        cur_state = cur_status = None
        cur_ev, cur_ruled = (), None

    new_state = state or cur_state
    new_status = status or cur_status
    new_ev = cur_ev if evidence is None else (
        (evidence,) if isinstance(evidence, str) else tuple(evidence))
    new_ruled = cur_ruled if ruled is None else (ruled or None)

    if new_state not in STATES:
        raise ValueError(f"state {new_state!r} not in {STATES}")
    if new_status not in STATUSES:
        raise ValueError(f"status {new_status!r} not in {STATUSES}")
    if new_state == "DONE":
        objections = evidence_objections(ident, new_ev, root=path.parents[1])
        if objections:
            raise ValueError(
                f"refusing to mark {ident} DONE: " + "; ".join(objections))

    parts = [f"task: {ident}", f"state: {new_state}", f"status: {new_status}"]
    if new_ev:
        parts.append("evidence: " + ", ".join(new_ev))
    if new_ruled:
        parts.append(f"ruled: {new_ruled}")
    line = "<!-- " + " | ".join(parts) + " -->"

    if existing:
        lines[marker_at] = line
    else:
        lines.insert(marker_at, line)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return line


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
    ap.add_argument("--derive-deferrals", action="store_true",
                    help="derive each DEFERRED marker from the register, which is "
                         "the single source for deferral (his ruling 2026-10-29); "
                         "combine with --apply to write them")
    ap.add_argument("--path", type=Path, default=LIST)
    a = ap.parse_args()
    if a.derive_deferrals:
        n, changes = derive_deferred_markers(a.path, apply=a.apply)
        verb = "derived" if a.apply else "would derive"
        print(f"deferral markers {verb}: {n}")
        for line in changes:
            print(f"  {line}")
        return 0
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
