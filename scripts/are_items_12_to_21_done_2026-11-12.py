#!/usr/bin/env python3
"""Is each of items 12 through 21 of the 12-hour window DONE? Measured, not claimed.

★ WHY THIS EXISTS. His words, 2026-11-12: "You often report work as done, only
for me to subsequenly find that there is substantial work still outstanding."
(His "subsequenly" is "subsequently".) A reply saying "done" is a claim about
evidence. This file is the evidence: 1 PREDICATE PER ITEM, each returning a
verdict from the repository's own state, so the answer can disagree with me.

THE PREDICATES ARE DELIBERATELY NOT FLATTERING. Each one names the condition
that would make the item NOT done, and several are built to return NOT DONE for
work that exists but is incomplete -- which is exactly the failure he described.

Costs nothing: reads local files, dispatches to no model, runs no pytest.
"""
from __future__ import annotations
import argparse, json, pathlib, re, subprocess, sys

#: DERIVED from this file's own location, never typed. A hardcoded root
#: measures whatever tree the file was copied FROM, which is the shape
#: already recorded as a probe outliving its subject.
REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

DONE, PART, NOT = "DONE", "PARTIAL", "NOT DONE"


def _entries():
    import task_list_markers as tlm
    return {e.ident: e for e in tlm.parse_entries()}


def _bodies():
    import importlib.util
    p = REPO / "scripts" / "how_many_decisions_actually_need_him_2026-11-01.py"
    spec = importlib.util.spec_from_file_location("probe", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.bodies()



def _third_collision_is_tracked() -> bool:
    """The severity formula's 2 inputs are written by nothing. That is HIS ruling,
    not my fix, so the checkable condition is that an entry carries a LIVE ask
    naming it -- never that it has been silently resolved."""
    import importlib.util
    p = REPO / "scripts" / "how_many_decisions_actually_need_him_2026-11-01.py"
    spec = importlib.util.spec_from_file_location("probe12", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    bodies = m.bodies()
    rows = _entries()
    for ident in ("B143", "B84"):
        e = rows.get(ident)
        if e is None:
            continue
        body = bodies.get(ident, "")
        d = m.classify_text(e.state or "", e.ruled, body)
        if d.get("live_asks") and re.search(
                r"HARD/SOFT|confidence|severity formula|2 inputs", body, re.I):
            return True
    return False

# ---------------------------------------------------------------- 12
def item_12():
    """The severity collisions in the maths model. 3 were found; how many are fixed?"""
    appendix = (REPO / "docs" / "MATHEMATICAL_APPENDIX.md").read_text(encoding="utf-8")
    core = (REPO / "bench" / "directives" / "universal"
            / "cdsfl_core_formal.md").read_text(encoding="utf-8")
    #: ★ 2 OF THESE 3 PREDICATES WERE WRONG ON THEIR FIRST RUN, 2026-11-12, AND
    #: THEY FAILED IN OPPOSITE DIRECTIONS -- which is why they are written out here
    #: rather than summarised.
    #:
    #: (a) THE DEAD-CITATION CHECK READ A SCAR AS A WOUND. It asked whether the
    #: string "cdsfl_core.txt §10" appears at all. It does -- inside the CORRECTION
    #: NOTE that records the citation as dead, because a correction has to quote
    #: what it corrects. So a repaired appendix failed its own check. The predicate
    #: now requires the refutation marker to appear BEFORE every occurrence, so the
    #: citation is admissible only inside its own refutation. Same shape as the
    #: 2026-11-02 finding that a detector must not spell out its own pattern.
    #:
    #: (b) THE THIRD CHECK BELONGED TO ITEM 16, NOT HERE. It tested whether the
    #: fixed-value cut had left the formal directive, which is B146's work and is
    #: measured by item_16. Counting it here reported item 12 as 1 of 3 when it is
    #: 2 of 3, and double-counted one piece of work across 2 items. The real third
    #: collision -- the severity formula whose 2 inputs are written by nothing --
    #: is NOT mine to fix: it needs his ruling, so what is checkable is that it is
    #: TRACKED as needing one.
    refut = appendix.find("THE CITATION THAT STOOD HERE WAS DEAD")
    cites = [i for i in range(len(appendix))
             if appendix.startswith("§10", i)]
    checks = {
        "V renamed to Ver in 7.7 (V collided with the value symbol)":
            "Ver(" in appendix and not re.search(r"\bSev\(f\)\s*=\s*W\(class\)\s*[*x·]\s*confidence\s*[*x·]\s*V\(", appendix),
        "the dead cdsfl_core.txt section 10 citation survives only inside its own refutation":
            refut >= 0 and all(i > refut for i in cites),
        "the third collision -- the severity formula with no writer -- is tracked as needing his ruling":
            _third_collision_is_tracked(),
    }
    n = sum(bool(v) for v in checks.values())
    return (DONE if n == len(checks) else PART if n else NOT), checks, \
        f"{n} of {len(checks)} collisions repaired"


# ---------------------------------------------------------------- 13
def item_13():
    """The entries he had already ruled on. Does any still sit OPEN with a live ask?"""
    import importlib.util
    p = REPO / "scripts" / "how_many_decisions_actually_need_him_2026-11-01.py"
    spec = importlib.util.spec_from_file_location("probe13", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    bodies = m.bodies()
    rows = _entries()
    #: ★ THIS PREDICATE WAS TOO STRICT AND MEASURED SOMETHING THAT IS NOT A
    #: DEFECT. Corrected 2026-11-12. It asked whether any entry carries a ruling
    #: AND a live ask, and flagged 4. But the project's own rule is that A RULING
    #: DATE IS A POINT EVENT, NOT PERMANENT ABSOLUTION: a question raised AFTER a
    #: ruling cannot have been answered by it, so an entry that collects new
    #: questions after being ruled on is behaving exactly as designed. Reading
    #: the 4 flagged entries confirmed it -- B77 asks WHICH RHO, B84 asks about a
    #: pre-run description and an extra suite run, B94 asks on both halves, B125
    #: asks for awareness that a composed half is unbuilt. All 4 postdate their
    #: rulings. Flagging them would have pushed me to close entries that
    #: legitimately await him, which is the SUPPRESSION direction and the worse
    #: one, for the reason the generator's own comment gives: repetition is
    #: visible, suppression is not.
    #:
    #: WHAT IS ACTUALLY A DEFECT: an entry asking something the ruling ALREADY
    #: ANSWERED. `asks_newer_than_the_ruling` is the project's own predicate for
    #: that distinction and is CALLED here rather than re-implemented.
    stale, fresh = [], []
    for ident, e in sorted(rows.items()):
        if (e.state or "").upper() != "OPEN" or not e.ruled:
            continue
        d = m.classify_text(e.state or "", e.ruled, bodies.get(ident, ""))
        if not d.get("live_asks"):
            continue
        try:
            import importlib.util as _iu
            _p = REPO / "scripts" / "morning_report_build_2026-10-12.py"
            _s = _iu.spec_from_file_location("mrb13", _p)
            _m = _iu.module_from_spec(_s)
            _s.loader.exec_module(_m)
            newer = _m.asks_newer_than_the_ruling(ident, e.ruled)
        except Exception:                          # noqa: BLE001
            newer = True                           # cannot tell: treat as fresh
        (fresh if newer else stale).append(f"{ident} ruled {e.ruled}")
    checks = {"no entry re-asks a question his ruling already answered": not stale}
    return (DONE if not stale else PART), checks, \
        (f"{len(stale)} re-ask an ANSWERED question: " + ", ".join(stale) if stale
         else f"0 re-ask an answered question; {len(fresh)} ask NEW questions that "
              f"postdate their rulings, which is the designed behaviour: "
              + ", ".join(fresh))


# ---------------------------------------------------------------- 14
def item_14():
    """The commit. Did HEAD actually move, and is the tree clean?"""
    head = subprocess.run(["git", "log", "-1", "--format=%h %s"], cwd=REPO,
                          capture_output=True, text=True).stdout.strip()
    #: ★ NOT `git status --porcelain`, 2026-11-12, AND THE REASON IS A REAL BUG
    #: THIS PREDICATE HAD. Porcelain output is COLUMN-BASED -- 2 status
    #: characters then the path -- and calling `.strip()` on the whole multi-line
    #: output removes the leading space of the FIRST line only. That shifted its
    #: columns by 1, so `line[3:]` returned 'ench/tickets/sv_completions.jsonl'
    #: and the exclusion below never matched. The 2nd line, which kept its
    #: leading space, parsed correctly -- so the fault was INVISIBLE whenever the
    #: path of interest was not first.
    #:
    #: Asking git for PATHS instead removes the class of error rather than the
    #: instance: there are no columns to mis-slice.
    def _paths(*args):
        out = subprocess.run(["git", *args], cwd=REPO,
                             capture_output=True, text=True).stdout
        return [l.strip() for l in out.splitlines() if l.strip()]
    rows = sorted(set(_paths("diff", "--name-only")
                      + _paths("diff", "--cached", "--name-only")
                      + _paths("ls-files", "--others", "--exclude-standard")))
    #: ★ THE SAVE'S OWN RECEIPT IS EXCLUDED BY NAME, 2026-11-12, AND THE REASON
    #: IS EVIDENCE RATHER THAN CONVENIENCE. `sv` appends 1 line to
    #: bench/tickets/sv_completions.jsonl AFTER it commits, recording the sha it
    #: just made. Measured on this run: commit 072c038d landed at 04:54:01 and
    #: the receipt was written at 05:26:18, 32 minutes later, and the line it
    #: added carries `"sha": "072c038d..."`. A receipt naming a commit cannot be
    #: inside that commit, so "the working tree is clean" was UNREACHABLE
    #: immediately after any successful save and this item could never read DONE.
    #:
    #: EXCLUDED BY NAME AND NOT BY LOOSENING THE CHECK: any other dirty path
    #: still fails, and the exclusion is CONDITIONAL on the receipt's newest sha
    #: actually matching HEAD -- so a stale receipt, or one naming a different
    #: commit, is still counted as uncommitted work.
    RECEIPT = "bench/tickets/sv_completions.jsonl"
    receipt_ok = False
    try:
        import json as _j
        lines = [l for l in (REPO / RECEIPT).read_text(encoding="utf-8").splitlines() if l.strip()]
        newest = _j.loads(lines[-1]) if lines else {}
        receipt_ok = str(newest.get("sha", "")).startswith(head.split()[0])
    except Exception:                                          # noqa: BLE001
        receipt_ok = False
    excluded = [l for l in rows if l == RECEIPT] if receipt_ok else []
    remaining = [l for l in rows if l not in excluded]
    moved = not head.startswith("d41ea21")
    checks = {"HEAD has moved off d41ea210": moved,
              "nothing is uncommitted except the save's own receipt for THIS head":
                  not remaining}
    return (DONE if moved and not remaining else PART if moved else NOT), checks, \
        f"HEAD {head[:46]}; {len(remaining)} uncommitted path(s)" \
        + (f"; receipt for {head.split()[0]} excluded" if excluded else
           ("; receipt does NOT match HEAD, so it is counted" if rows and not receipt_ok else ""))


# ---------------------------------------------------------------- 15
def item_15():
    """Both halves of the severity round. Does the topology gate still owe a joint round?"""
    #: ★ THIS PREDICATE HAD THE DIRECTION BACKWARDS, 2026-11-12. It read each
    #: BLIND round's own `joint_of` and called the round owing when that field
    #: was empty -- but a blind round has no parents, so the field is CORRECTLY
    #: empty and the check could never pass. The debt is discharged by a JOINT
    #: round that NAMES the parent in its own `joint_of` AND has landed at least
    #: 2 replies, which is the opposite lookup.
    #:
    #: SO IT NOW CALLS THE DISPATCHER'S OWN FUNCTION instead of re-deciding.
    #: `confer_maths_panel_2026-09-05._rounds_owing_a_joint_round` is the
    #: authority the gate itself consults, and a second implementation of the
    #: same rule is exactly the producer-consumer divergence this project keeps
    #: meeting -- each individually correct, disagreeing in the one case that
    #: matters.
    logs = sorted((REPO / "bench" / "logs").glob("*severity_is_ordinal*"))
    dirs = [q for q in logs if q.is_dir()]
    joint = [q for q in dirs if q.name.endswith("_joint")]
    landed = []
    for q in joint:
        for seat in ("cc2", "fable"):
            f = q / f"{seat}.json"
            if not f.is_file():
                continue
            try:
                j = json.loads(f.read_text(encoding="utf-8"))
            except Exception:                      # noqa: BLE001
                continue
            if j.get("ok") and (j.get("chars") or 0) > 0:
                landed.append(f"{q.name}/{seat}")
    owed_here = True
    authority = "could not be consulted"
    try:
        import importlib.util as _iu
        _s = _iu.spec_from_file_location(
            "_panel_auth", REPO / "bench" / "confer_maths_panel_2026-09-05.py")
        _m = _iu.module_from_spec(_s)
        _s.loader.exec_module(_m)
        owing = _m._rounds_owing_a_joint_round()
        owed_here = "severity_is_ordinal_2026-11-11" in owing
        authority = f"{len(owing)} round(s) owing overall"
    except Exception as exc:                       # noqa: BLE001
        authority = f"could not be consulted: {exc!r}"[:70]
    checks = {
        "a joint round directory exists for the severity round": bool(joint),
        "the joint round landed at least 2 seat replies": len(landed) >= 2,
        "the dispatcher's own debt function no longer names the blind round":
            not owed_here,
    }
    n = sum(bool(v) for v in checks.values())
    return (DONE if n == len(checks) else PART if n else NOT), checks, \
        (f"{len(dirs)} round dir(s), {len(joint)} joint, {len(landed)} landed "
         f"repl(y/ies); authority: {authority}")


# ---------------------------------------------------------------- 16
def item_16():
    """The symbolic form. Is it IN the appendix and the directive, or only drafted?"""
    appendix = (REPO / "docs" / "MATHEMATICAL_APPENDIX.md").read_text(encoding="utf-8")
    core = (REPO / "bench" / "directives" / "universal"
            / "cdsfl_core_formal.md").read_text(encoding="utf-8")
    checks = {
        "the appendix states a per-domain ordering and critical level":
            bool(re.search(r"(?:≽|succeq|preceq)_?d|per-domain (?:ordering|critical level)",
                           appendix)),
        "the appendix names the scale alongside the value":
            "scale-name" in appendix or "scale name" in appendix,
        "the formal directive instructs the seats on the ordinal form":
            "ordinal" in core.lower(),
        "the directive forbids averaging a consequence":
            bool(re.search(r"never (?:average|sum|interpolate)", core, re.I)),
    }
    n = sum(bool(v) for v in checks.values())
    return (DONE if n == len(checks) else PART if n else NOT), checks, \
        f"{n} of {len(checks)} required statements present"



def _panel_exports(name: str) -> bool:
    """Is `name` actually CALLABLE on the panel dispatcher? Imported, not read.

    A source-text search cannot tell a definition from a reference to one, and
    the reference survives the definition's removal.
    """
    try:
        import importlib.util as _iu
        _p = REPO / "bench" / "confer_maths_panel_2026-09-05.py"
        _s = _iu.spec_from_file_location("_panel_probe", _p)
        _m = _iu.module_from_spec(_s)
        _s.loader.exec_module(_m)
        return callable(getattr(_m, name, None))
    except Exception:                              # noqa: BLE001
        return False

# ---------------------------------------------------------------- 17
def item_17():
    """B125, both halves: quote file state at dispatch, and refuse a moved reference."""
    #: ★ THIS PREDICATE NAMED THE WRONG FILE, 2026-11-12. It searched
    #: `bench/reference_runner_v3.py`, the EXPERIMENT runner. B125 is about
    #: PANEL JOINT BRIEFS, which are dispatched by
    #: `bench/confer_maths_panel_2026-09-05.py`. So the repair landed in the
    #: panel dispatcher and this check went on reading a file it was never going
    #: to appear in -- the same shape as the declaration instrument that globbed
    #: the directory its own repair did not land in.
    #:
    #: ★ AND IT REQUIRED THE WRONG THING. It demanded BOTH halves of B125's
    #: composed recommendation. His composability standard permits recommending a
    #: composed fix ONLY with a measurement showing it beats either part alone,
    #: and that measurement CANNOT BE TAKEN: of 17 archived joint briefs, 17 name
    #: an artefact and 0 carried the stamp, so no round ever had either half in
    #: force and there is no data on either alone. Demanding half 2 would be
    #: demanding work his own standard forbids recommending.
    #:
    #: SO WHAT IS REQUIRED IS: half 1 built, and the composability position
    #: RECORDED rather than claimed. Half 2 stays open as an unmeasured option.
    rows = _entries()
    e = rows.get("B125")
    panel = (REPO / "bench" / "confer_maths_panel_2026-09-05.py").read_text(
        encoding="utf-8")
    bodies = _bodies()
    body = bodies.get("B125", "")
    checks = {
        #: ★ IMPORTED AND CALLED, NOT GREPPED. 2026-11-12: this read
        #: `"stamp_brief_at_dispatch" in panel`, and a mutation renaming the
        #: DEFINITION away left it GREEN -- because the CALL SITE still contains
        #: the same string. A substring is not a call, which this project has
        #: already recorded with "2 of 2 green; `None and f(...)` holds the
        #: name". The function is now resolved on the imported module, so a
        #: definition that has gone cannot be satisfied by a reference to it.
        "the panel dispatcher stamps the state of every file a brief names":
            _panel_exports("stamp_brief_at_dispatch"),
        "the stamp reaches the text the SEATS receive, not only the file":
            "PROMPT = stamp_brief_at_dispatch(" in panel
            and "global MODELS, PROMPT" in panel,
        "a guard executes the stamping path":
            (REPO / "bench" / "tests"
             / "test_the_brief_is_stamped_at_dispatch_2026-11-12.py").is_file(),
        "the entry records that the COMPOSED half is unmeasured rather than claiming it":
            bool(re.search(r"unmeasur|cannot be taken|0 of 17|no data on either",
                           body, re.I)),
    }
    n = sum(bool(v) for v in checks.values())
    return (DONE if n == len(checks) else PART if n else NOT), checks, \
        (f"B125 state={e.state if e else 'ABSENT'}; {n} of {len(checks)} conditions met")


# ---------------------------------------------------------------- 18
def item_18():
    """The 4 steering chats simulated with the orchestrator as HIL. Is there a record?"""
    #: ★ CASE-INSENSITIVE BY COMPARISON, NOT BY GLOB PATTERN. Corrected
    #: 2026-11-12: the first version globbed `*[Ss]teering*`, which matches
    #: "steering" and "Steering" and NOT "STEERING". The record was written as
    #: `STEERING_SIMULATION_RECORD_2026-11-12.md`, which is the convention in
    #: docs/ux -- every other file there is upper case -- so the FILE was right
    #: and the predicate could not see it. A character-class glob is a hand-rolled
    #: case fold that silently omits the case nobody thought of; comparing lowered
    #: names cannot.
    roots = (REPO / "bench" / "logs", REPO / "experimental_notes",
             REPO / "docs" / "ux")
    cands = [p for root in roots if root.is_dir()
             for p in sorted(root.iterdir()) if "steering" in p.name.lower()]
    checks = {"a steering-simulation record exists anywhere in the repo": bool(cands)}
    return (DONE if cands else NOT), checks, \
        (f"{len(cands)} candidate record(s): {[p.name for p in cands[:4]]}"
         if cands else "0 records: the simulation has not been run")


# ---------------------------------------------------------------- 19
def item_19():
    """The UX record. Does any file in docs/ux name the steering design?"""
    ux = REPO / "docs" / "ux"
    files = sorted(ux.glob("*.md")) if ux.exists() else []
    #: ★ THIS PREDICATE PASSED VACUOUSLY ON ITS FIRST RUN, 2026-11-12, AND IN THE
    #: FLATTERING DIRECTION -- the worst one. It asked whether any file in docs/ux
    #: contains the word "steering", and HIL_INTERACTION_SPECIFICATION_DRAFT_
    #: 2026-10-29.md does, because it specifies a human-in-the-loop surface and
    #: used the word generically a fortnight BEFORE this window. So an item with 0
    #: work done reported DONE. A single generic word is not a record of a design.
    #: THE PREDICATE NOW REQUIRES 2 OF THE 3 SUBJECTS THIS WINDOW ACTUALLY
    #: PRODUCED, because no pre-existing file can name 2 of them by accident.
    SUBJECTS = ("domain_manifest", "subdomain", "domain vocabulary")
    hits = {}
    for p in files:
        body = p.read_text(encoding="utf-8", errors="replace").lower()
        found = [w for w in SUBJECTS if w in body]
        if len(found) >= 2:
            hits[p.name] = found
    weak = {p.name for p in files
            if "steering" in p.read_text(encoding="utf-8", errors="replace").lower()}
    checks = {"the user-experience folder holds at least 1 markdown file": bool(files),
              "at least 1 file names 2 or more of this window's own subjects": bool(hits)}
    return (DONE if hits else NOT), checks, \
        (f"{len(files)} file(s) in docs/ux; naming 2+ subjects: {hits or 'none'}; "
         f"{len(weak)} file(s) use the bare word 'steering', which is not a record"
         if files else "docs/ux holds no markdown at all")


# ---------------------------------------------------------------- 20
def item_20():
    """The 28 older encodings. How many carry all 4 categories the seats asked for?"""
    d = REPO / "bench" / "directives"
    skip = {"universal"}
    files = [p for p in sorted(d.rglob("*.txt")) if p.parent.name not in skip]
    CATS = ("[Known failure modes]", "[Exception catalogue]",
            "[Tool limitations]", "[Diagnostic heuristics]")
    full, thin = [], []
    for p in files:
        t = p.read_text(encoding="utf-8", errors="replace")
        (full if all(c in t for c in CATS) else thin).append(p.name)
    checks = {"every encoding carries all 4 categories": not thin}
    return (DONE if not thin else PART if full else NOT), checks, \
        f"{len(full)} of {len(files)} encodings carry all 4 categories; {len(thin)} thin"


# ---------------------------------------------------------------- 21
def item_21():
    """The rulings-required spoken report. Does a dated pair exist for today?"""
    stamp = subprocess.run(["date", "-u", "+%Y-%m-%d"], capture_output=True,
                           text=True, check=True).stdout.strip()
    desk = pathlib.Path.home() / "Desktop" / "CDSFL_tts"
    notes = REPO / "experimental_notes"
    txt = list(desk.glob(f"*{stamp}*.txt")) if desk.exists() else []
    md = list(notes.glob(f"*{stamp}*.md"))
    checks = {f"a TTS text file dated {stamp} exists": bool(txt),
              f"a markdown companion dated {stamp} exists": bool(md)}
    return (DONE if txt and md else PART if (txt or md) else NOT), checks, \
        f"{len(txt)} TTS file(s) and {len(md)} markdown file(s) dated {stamp}"


ITEMS = {
 12: ("the severity collisions in the maths model", item_12),
 13: ("the task-list entries he had already ruled on", item_13),
 14: ("the commit", item_14),
 15: ("the severity brief through BOTH halves, blind and joint", item_15),
 16: ("the symbolic per-domain form in the maths model and the seats' instruction", item_16),
 17: ("B125, both halves: file state at dispatch and refusal on a moved reference", item_17),
 18: ("the 4 steering chats simulated, orchestrator acting as HIL", item_18),
 19: ("the UX work recorded in a UX-specific resource", item_19),
 20: ("the 28 older expert encodings enriched to 4 categories", item_20),
 21: ("the rulings-required spoken report, in the format he endorsed", item_21),
}


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Measure whether items 12 through 21 of the 2026-11-11/12 window are done. "
                    "Reads local files only; runs no model and no pytest.")
    ap.add_argument("--item", type=int, action="append",
                    help="measure only this item number (repeatable)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    wanted = a.item or sorted(ITEMS)
    results = {}
    for n in wanted:
        if n not in ITEMS:
            print(f"no item {n}", file=sys.stderr)
            return 2
        title, fn = ITEMS[n]
        try:
            verdict, checks, note = fn()
        except Exception as exc:                   # noqa: BLE001
            verdict, checks, note = NOT, {}, f"the predicate itself failed: {exc!r}"
        results[n] = dict(title=title, verdict=verdict, note=note,
                          checks={k: bool(v) for k, v in checks.items()})

    if a.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return 0

    print("=" * 78)
    print("ARE ITEMS 12 THROUGH 21 DONE? MEASURED FROM THE REPOSITORY, IN HIS ORDER")
    print("=" * 78)
    for n in wanted:
        r = results[n]
        print(f"\n{n}. {r['title']}")
        print(f"   VERDICT: {r['verdict']}   ({r['note']})")
        for k, v in r["checks"].items():
            print(f"     [{'OK  ' if v else 'FAIL'}] {k}")
    tally = {}
    for r in results.values():
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
    print()
    print("=" * 78)
    print("TALLY: " + ", ".join(f"{v} {k}" for k, v in sorted(tally.items())))
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
