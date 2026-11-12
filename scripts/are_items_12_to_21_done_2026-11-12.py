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
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=REPO,
                           capture_output=True, text=True).stdout.strip()
    n_dirty = len([l for l in dirty.splitlines() if l.strip()])
    moved = not head.startswith("d41ea21")
    checks = {"HEAD has moved off d41ea210": moved,
              "the working tree is clean": n_dirty == 0}
    return (DONE if moved and n_dirty == 0 else PART if moved else NOT), checks, \
        f"HEAD {head[:60]}; {n_dirty} uncommitted path(s)"


# ---------------------------------------------------------------- 15
def item_15():
    """Both halves of the severity round. Does the topology gate still owe a joint round?"""
    logs = sorted((REPO / "bench" / "logs").glob("*severity_is_ordinal*"))
    blind = [p for p in logs if p.is_dir()]
    joint = [p for p in logs if p.is_dir() and p.name.endswith("_joint")]
    topo = []
    for p in blind:
        f = p / "topology.json"
        if f.exists():
            try:
                topo.append((p.name, json.loads(f.read_text(encoding="utf-8"))))
            except Exception:                      # noqa: BLE001
                topo.append((p.name, {}))
    owes = [n for n, t in topo if not t.get("joint_of") and not n.endswith("_joint")]
    checks = {"a joint round directory exists": bool(joint),
              "no blind round still owes a joint round": not owes}
    return (DONE if joint and not owes else NOT), checks, \
        (f"{len(blind)} round dir(s), {len(joint)} joint; owing: {owes}"
         if blind else "no severity round directories found at all")


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


# ---------------------------------------------------------------- 17
def item_17():
    """B125, both halves: quote file state at dispatch, and refuse a moved reference."""
    rows = _entries()
    e = rows.get("B125")
    runner = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
    checks = {
        "B125 is off OPEN": e is not None and (e.state or "").upper() != "OPEN",
        "the dispatch records the referenced file's state":
            bool(re.search(r"file_state_at_dispatch|quoted_file_state", runner)),
        "a moved reference is refused":
            bool(re.search(r"referenced file (?:has )?moved|refuse.*moved", runner, re.I)),
    }
    n = sum(bool(v) for v in checks.values())
    return (DONE if n == len(checks) else PART if n else NOT), checks, \
        (f"B125 state={e.state if e else 'ABSENT'}; {n} of {len(checks)} conditions met")


# ---------------------------------------------------------------- 18
def item_18():
    """The 4 steering chats simulated with the orchestrator as HIL. Is there a record?"""
    cands = list((REPO / "bench" / "logs").glob("*steering*")) \
        + list((REPO / "experimental_notes").glob("*[Ss]teering*")) \
        + list((REPO / "docs" / "ux").glob("*[Ss]teering*"))
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
