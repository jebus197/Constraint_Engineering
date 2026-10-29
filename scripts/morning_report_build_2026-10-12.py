#!/usr/bin/env python3
"""Generate the morning report's three sections from the project's own records.

HIS ORDER, 2026-10-12: *"Build the generator, whole session, narrative moves to the
notes. But leave enough detail for me to make sane and sensible choices. Don't leave me
guessing what you are talking about."*

WHY A GENERATOR RATHER THAN PROSE, AND IT IS NOT A STYLE PREFERENCE. The 2026-10-12
report was hand-written and measurably wrong in 2 ways a derived list cannot be:

  * **A19 was listed as "approved by you, not built".** Its own entry says *"BUILT AND
    TESTED 2026-09-11, NOT DONE -- Section P applies, and the last step is HIS"*, its
    marker reads `state: OPEN | status: TESTED`, and its evidence passes 20 tests. The
    marker was right and the prose was wrong.
  * **3 open defects that explicitly say "needs: a founder ruling" were missing entirely.**
    They sit in `experimental_notes/STUDY_IN_FLIGHT.json` under `open_defects`, each
    marked *"FOUND, NOT FIXED (founder issued 'd' - discuss before proceeding)"*. Nothing
    in the hand-written report mentioned them.

And it was 6,659 words of which only 1,089 -- 0.1695, Wilson [0.1605, 0.1788] -- sat in
decision sections, so 5 words in 6 were narrative about finished work. The markdown ran
to 435 lines against the note standard's 40-300 limit, over by 135.

THE SEPARATION THAT MAKES BOTH HALVES POSSIBLE. A pure generator would print "A19
OPEN/TESTED" and leave him guessing what to decide. Hand-writing produced the errors
above. So: **this script derives the LIST and the FACTS; a committed data file carries
the authored DETAIL** -- what the thing is, why it needs him, what the options are --
keyed by the derived item's own id. Neither half can drift from the other, because the
script REFUSES (exit 3) when a derived item has no authored detail, and when authored
detail names an item that is no longer derived. A new decision therefore cannot appear
undocumented, and stale text cannot survive the item it describes.

SOURCES, each read through its OWN producer rather than re-parsed here:
  * `scripts/task_list_markers.py::parse_entries` -- every entry's state, status and
    evidence, from `experimental_notes/CDSFL_MASTER_TASK_LIST.md`
  * `experimental_notes/STUDY_IN_FLIGHT.json` -- the 9 programme measurements and the
    open defects, the same file `hooks/study_pulse.py` reads
  * `experimental_notes/PARKED_FOR_THE_FOUNDER.md` -- the parked items
  * `scripts/his_older_instructions_triage_2026-10-11.py::triage` -- explanations owed
  * `git log` -- what was done, for the one-line-per-item ledger

A --help COSTS NOTHING: reads committed files and `git log`, no dispatch, no network.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
DETAIL = REPO / "experimental_notes" / "data" / "morning_report_decisions.json"
TASKLIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
STUDY = REPO / "experimental_notes" / "STUDY_IN_FLIGHT.json"
PARKED = REPO / "experimental_notes" / "PARKED_FOR_THE_FOUNDER.md"


def _load(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# ───────────────────────── derive the list ─────────────────────────

#: A marker status that means the work EXISTS, as Rule 20 of the note standard
#: names them. COMMITTED and ENABLED are strictly beyond TESTED, so an item at
#: either is certainly already built. NAMED so the guard can read this tuple
#: instead of restating it: until 2026-10-29 the test asserted ("BUILT",
#: "TESTED") against this set of 4, a disagreement that stayed invisible while
#: no live entry carried COMMITTED or ENABLED.
BUILT_STATUSES = ("BUILT", "TESTED", "COMMITTED", "ENABLED")


def task_items() -> list[dict]:
    """Every task-list entry not DONE or WITHDRAWN, with its MARKER state."""
    tlm = _load(REPO / "scripts" / "task_list_markers.py", "tlm_report")
    out = []
    for r in tlm.parse_entries(TASKLIST):
        if (r.state or "").upper() in ("DONE", "WITHDRAWN"):
            continue
        built = (r.status or "").upper() in BUILT_STATUSES
        out.append({
            "key": f"task:{r.ident}",
            "ident": r.ident,
            "source": "master task list",
            "where": f"experimental_notes/CDSFL_MASTER_TASK_LIST.md:{r.line_no}",
            "state": r.state,
            "status": r.status,
            # THE DISTINCTION THE HAND-WRITTEN REPORT LOST on A19.
            "already_built": built,
            "evidence": list(r.evidence),
            # ★ CARRIED SO A RULING CANNOT BE RE-ASKED (2026-10-16). See the
            # routing at the assembly below.
            "ruled": r.ruled,
            "headline": _first_sentence(r.text),
        })
    return out


def study_items() -> list[dict]:
    """Programme measurements with no result, and defects that name a ruling."""
    if not STUDY.is_file():
        return []
    d = json.loads(STUDY.read_text(encoding="utf-8"))
    # ★ THE STATUS GATE BELONGS ON THE MEASUREMENTS AND NOT ON THE WHOLE
    # FUNCTION. Corrected 2026-10-29, and the defect was MINE, introduced hours
    # earlier the same night.
    #
    # This read `if status != "OPEN": return []`. Retiring the 13th and last
    # measurement under task B34 took the register to CLOSED -- correctly, since
    # every measurement is now settled -- and that one line then silently
    # stopped the morning report carrying the register's `open_defects`, which
    # are the entries that SAY THEY NEED HIS RULING. The measurements being
    # finished has nothing to do with whether an open defect still awaits him.
    #
    # CAUGHT BY `test_no_ruling_seeking_defect_is_missed`, whose whole subject is
    # this class of false zero and which named the 2 that vanished:
    # `defect:A4-counter-valve-severity-mismatch` and
    # `defect:integrity-gate-interpreter-carve-out`. It is a shrink-only ratchet
    # naming its members individually, so a regression in the extractor shows up
    # as a named member going missing rather than as a number moving -- which is
    # exactly how it surfaced.
    #
    # AND 2 INSTRUMENTS CONTRADICTED EACH OTHER WHILE THIS HELD, which is worth
    # recording: `--check` reported both defects as authored detail for an item
    # "no longer live" and told me to delete them, because the derived list was
    # empty; the guard refused their absence. Agreeing with one instrument is not
    # licence to remove what another needs.
    _programme_open = str(d.get("status", "")).upper() == "OPEN"
    out = []
    for mrec in (d.get("measurements", []) if _programme_open else []):
        if mrec.get("result") is None or mrec.get("headline") is None:
            out.append({
                "key": f"study:{mrec.get('id')}",
                "ident": str(mrec.get("id")),
                "source": "programme of study",
                "where": "experimental_notes/STUDY_IN_FLIGHT.json",
                "state": "OUTSTANDING",
                "status": "MEASUREMENT",
                "already_built": False,
                "evidence": [],
                "headline": str(mrec.get("what", ""))[:240],
                "founder_ruling": str(mrec.get("founder_ruling", "")),
            })
    for drec in d.get("open_defects", []):
        needs = str(drec.get("needs", ""))
        # ONLY the ones that SAY they need him. A defect being open is not a decision.
        #
        # THE WHOLE RECORD IS SEARCHED, NOT JUST THE `needs` FIELD, and the first
        # version of this filter missed a defect because of that. 2 of the 3 open
        # defects carry `needs: "a founder ruling: ..."`; the third records the same
        # thing under `provenance_question_for_the_founder` ending "AWAITING FOUNDER
        # RULING; no code changed." Keying on one field name is how a false zero gets
        # reported -- the exact failure class this generator exists to remove.
        # ★ A RULED DEFECT STAYS DERIVED AND IS ROUTED, NOT SKIPPED (2026-10-16).
        #
        # A first version skipped it here. That made its authored detail an
        # ORPHAN, the generator refused at exit 3 as it is designed to, and the
        # report silently stayed 2 hours stale while appearing to regenerate --
        # so the strike he asked for did not happen and the queue still read 11.
        # Archiving the detail instead would have been worse: it carries his
        # VERBATIM WORDS, and those are the record of the ruling.
        #
        # So the escape lives in `decisions()`, which marks the item
        # `no_ruling_needed` and sends it to section 3 with his ruling attached.
        # That satisfies "strike this permanently from your list of outstanding
        # decisions" -- it leaves the DECISION list -- while keeping the ruling
        # visible rather than vanishing.
        blob = json.dumps(drec).lower()
        if not any(k in blob for k in ("founder ruling", "awaiting founder",
                                       "needs a founder", "ruling that awaits")):
            continue
        out.append({
            # Carried for the same reason `task_items()` carries it: without
            # this the date never reaches the renderer and a ruled defect
            # appears in section 3 with no indication he had settled it.
            "ruled": drec.get("ruled"),
            "struck_permanently": bool(drec.get("struck_permanently")),
            "key": f"defect:{drec.get('id') or drec.get('name','')[:40]}",
            "ident": str(drec.get("id") or drec.get("name", ""))[:48],
            "source": "programme of study, open defect",
            "where": "experimental_notes/STUDY_IN_FLIGHT.json",
            "state": "NEEDS RULING",
            "status": str(drec.get("status", ""))[:60],
            "already_built": False,
            "evidence": [],
            "headline": str(drec.get("what", ""))[:240],
            "needs": needs,
            "severity": str(drec.get("severity", "")),
        })
    return out


def parked_items() -> list[str]:
    """The parked file's LIVE portion, derived from the task list's markers.

    ★ TASK B3, BUILT 2026-10-15 ON HIS RULING: *"Build it and implement it."*
    Nothing removed an item from the parked file when its underlying entry
    closed, so it re-presented settled business and buried the live items among
    it. Measured 2026-10-13 by
    `scripts/has_he_already_ruled_on_the_parked_2026-10-13.py`: **14 of 21
    parked items were already settled, 66.6667%, Wilson [45.3735%, 82.8052%],
    Clopper-Pearson [43.0325%, 85.4123%]**.

    The filter is the one B3 names: a parked heading that NAMES a task-list
    entry now recorded DONE or WITHDRAWN is dropped, because its question has
    been answered. A heading naming no entry is KEPT, since absence of a marker
    is not evidence of closure -- the measurement's own caveat is that
    identifier matching under-reports, so the residue is an UPPER BOUND on what
    still needs him and this filter must not make it a lower one.
    """
    if not PARKED.is_file():
        return []
    headings = [l[3:].strip() for l in PARKED.read_text(encoding="utf-8").splitlines()
                if l.startswith("## ")]
    # THE WHOLE TASK LIST, not this report's live subset. `task_items()` returns
    # only the LIVE items, so deriving closure from it gave 0 closed and dropped
    # nothing -- an instrument that cannot see the thing it is filtering on.
    # `has_he_already_ruled_on_the_parked_2026-10-13.py` is the committed
    # producer for exactly this question and parses every entry.
    try:
        triage = _load(REPO / "scripts" /
                       "has_he_already_ruled_on_the_parked_2026-10-13.py",
                       "parked_triage")
        states = triage.task_states()
        closed = {k for k, (st, _status) in states.items()
                  if str(st).upper() in {"DONE", "WITHDRAWN"}}
        known = set(states)
    except Exception:                                    # pragma: no cover
        return headings                                  # fail OPEN, never hide
    if not closed:
        return headings
    live = []
    for h in headings:
        named = set(re.findall(r"\b([A-Z]{1,2}\d{1,4}[a-z]?)\b", h)) & known
        if named and named <= closed:
            continue
        live.append(h)
    return live


SUPERSEDED = REPO / "experimental_notes" / "data" / "explanations_superseded.json"


def explanations_owed() -> tuple[list[dict], list[dict]]:
    """(still owed, superseded).

    HIS QUESTION, 2026-10-12: *"Are these questions still relevant? If not you can
    discount those that are not."* An explanation is SUPERSEDED when the record shows
    he answered it himself, or ruled on its subject, AFTER asking -- so the discount is
    a DERIVATION against `data/explanations_superseded.json`, which carries the evidence
    for each, rather than a judgement made in prose. A superseded entry is reported, not
    deleted: the question was really asked and being overtaken is part of the answer.
    """
    t = _load(REPO / "scripts" / "his_older_instructions_triage_2026-10-11.py",
              "triage_report")
    owed = [{"date": i["date"], "text": i["text"]}
            for i in t.triage() if i["cls"] == "QUESTION_OWED"]
    recs = []
    if SUPERSEDED.is_file():
        recs = json.loads(SUPERSEDED.read_text(encoding="utf-8")).get("superseded", [])
    live, dead = [], []
    for q in owed:
        hit = next((r for r in recs
                    if r["date"] == q["date"] and r["match"] in q["text"]), None)
        if hit:
            dead.append({**q, **hit})
        else:
            live.append(q)
    return live, dead


def head_sha() -> str:
    r = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                       cwd=str(REPO), capture_output=True, text=True)
    return (r.stdout or "").strip() or "unknown"


#: The hard-coded session start this replaced, kept so the change is legible.
_FALLBACK_SINCE = "2026-10-11T12:00:00+01:00"


def _session_start() -> str:
    """When did THIS session begin? Derived from the last `sv:` commit.

    ★ IT WAS A HARD-CODED DATE AND IT WENT STALE (2026-10-15). The default was
    2026-10-11T12:00, so "Work done this session" listed **67 commits spanning 4
    days** -- 72 of the report's 376 lines -- and pushed the whole report past
    the note standard's 300-line ceiling (Rule 10). A session boundary that is
    typed once is a session boundary that is wrong from the next session on.

    `sv` IS THIS PROJECT'S OWN SESSION MARKER, so the last `sv:` commit is the
    boundary rather than a guess. Falls back to the old constant if no `sv:`
    commit is reachable, so a shallow clone degrades to the previous behaviour
    rather than to nothing.
    """
    r = subprocess.run(["git", "log", "--grep", "^sv:", "-1", "--pretty=%cI"],
                       capture_output=True, text=True, cwd=str(REPO))
    stamp = (r.stdout or "").strip()
    return stamp if r.returncode == 0 and stamp else _FALLBACK_SINCE


def work_done(since: str) -> list[tuple[str, str, str]]:
    r = subprocess.run(["git", "log", "--since", since, "--pretty=%h|%cI|%s",
                        "--reverse"], cwd=str(REPO), capture_output=True, text=True)
    out = []
    for line in (r.stdout or "").splitlines():
        if line.count("|") >= 2:
            h, ci, subj = line.split("|", 2)
            out.append((h, ci[:16].replace("T", " "), subj))
    return out


def _first_sentence(text: str) -> str:
    t = re.sub(r"\s+", " ", (text or "").replace("**", "")).strip()
    m = re.search(r"^(.{20,200}?[.!?])(\s|$)", t)
    return (m.group(1) if m else t[:200]).strip()


# ───────────────────────── the authored half ─────────────────────────

def decisions(items: list[dict]) -> tuple[list[dict], list[str], list[str]]:
    """Attach authored detail. Returns (attached, missing_detail, orphan_detail)."""
    detail = json.loads(DETAIL.read_text(encoding="utf-8")) if DETAIL.is_file() else {}
    detail = {k: v for k, v in detail.items() if not k.startswith("_")}
    attached, missing = [], []
    for it in items:
        d = detail.get(it["key"])
        if d is None:
            missing.append(it["key"])
            continue
        # The same escape for an item whose AUTHORED DETAIL records his ruling,
        # since not every decision originates from a task marker.
        #
        # ★ THE PREDICATE MUST READ BOTH HALVES (2026-10-19). It read only `d`,
        # the authored detail, while a task entry's ruling arrives on `it` from
        # the marker's `ruled:` field. `{**it, **d}` then carried the date into
        # the OUTPUT, so a reader of the merged record saw the ruling and the
        # routing predicate did not -- a producer and a consumer that disagree,
        # each individually correct, which is the shape `execute-do-not-grep`
        # names. The cost was his: he ruled on B31 on 2026-10-18 ("Your fix is
        # approved", Review_Stop_And_Declared_Modes_2026-10-18.txt) and the
        # report of 2026-10-19 asked him again, which he answered with "Then if
        # I already ruled. Why are you presenting it as a decision required
        # from me again?". 6 of the 7 live decisions that day were in this
        # state. Measured safe: 0 of 29 authored-detail entries set `ruled` to
        # a falsy value, so reading `d` first cannot mask a marker's date.
        ruled = d.get("ruled") or it.get("ruled")
        if d.get("struck_permanently") or ruled:
            attached.append({**it, **d, "ruled": ruled,
                             "no_ruling_needed": ruled or "struck permanently"})
            continue
        attached.append({**it, **d})
    orphan = sorted(set(detail) - {i["key"] for i in items})
    return attached, sorted(missing), orphan


# ───────────────────────── render ─────────────────────────

#: The note standard's verbatim-region markers, as `note_vagueness_lint.region_state`
#: reads them. Quoted material goes inside; this generator's OWN prose never does.
#:
#: WHY, MEASURED 2026-10-29. `test_v17_notes_obey_rules_27_and_28` failed on
#: `Morning_Report_2026-10-29_GENERATED.md` with 4 blocking findings, and all 4 sat
#: in text this generator did not write: "one" inside a git commit subject, "the
#: system" inside a task-list headline, "two" inside a quotation of the founder,
#: and "ONE" inside a line lifted from the parked file. Rule 27 governs what this
#: project WRITES, and the lint already says so -- its own comment reads "Rule 27
#: governs what this project WRITES, not a record of what someone else wrote, and
#: the verbatim [regions exist for that]". The guard calls `blocking()` rather than
#: `lint()` for exactly this reason, after it once failed the suite on a sentence a
#: panel seat wrote inside a region. The generator simply never opened one.
#:
#: SECTION 1 IS DELIBERATELY NOT WRAPPED. Its text comes from
#: `data/morning_report_decisions.json`, which this project authors, so it is this
#: project's own voice and Rule 27 binds it. A region opened around authored prose
#: would be the amnesty-for-its-own-violations shape the lint's `partition`
#: docstring records from panel round 15.
_VB = "<!-- verbatim-begin: {} -->"
_VE = "<!-- verbatim-end -->"


def render_md(decs, outstanding, done, owed, parked, since, superseded=()) -> str:
    L = []
    A = L.append
    A(f"# Morning report — {dt.date.today().isoformat()}")
    A("")
    A(f"Generated by `scripts/morning_report_build_2026-10-12.py` at HEAD `{head_sha()}` "
      f"from the project's own records. Every item's state is read from its marker, never "
      f"retyped. Narrative lives in the notes and commits this points at.")
    A("")
    A(f"**NOT COMMITTED, DELIBERATELY, AND IT IS NOT LOST.** This file is DERIVED: its "
      f"sources — the task-list markers, `STUDY_IN_FLIGHT.json`, the parked file, the "
      f"triage producer and `data/morning_report_decisions.json` — are all versioned, so "
      f"`python3 scripts/morning_report_build_2026-10-12.py --write` at HEAD "
      f"`{head_sha()}` reproduces it byte for byte. Committing it would churn on every "
      f"commit, because its own section 2 ledger would then list the commit that carries "
      f"it — the self-reference `docs/CURRENT_STATE.md` carries and documents.")
    A("")
    A(f"**{len(decs)} decisions need you · {len(outstanding)} outstanding · "
      f"{len(done)} commits this session · {len(owed)} explanations owed · "
      f"{len(parked)} parked**")
    A("")
    A("## 1. Decisions that need you")
    A("")
    for i, d in enumerate(decs, 1):
        A(f"### {i}. {d.get('title') or d['ident']}")
        A("")
        A(f"**What it is.** {d.get('what', d.get('headline',''))}")
        A("")
        A(f"**Why it needs you.** {d.get('why','')}")
        A("")
        if d.get("options"):
            A("**Your options.**")
            A("")
            for o in d["options"]:
                A(f"- {o}")
            A("")
        if d.get("evidence_line"):
            A(f"**Evidence.** {d['evidence_line']}")
            A("")
        built = " · **already BUILT and TESTED**" if d.get("already_built") else ""
        A(f"**State.** `{d['state']}` / `{d['status']}`{built} · {d['where']}")
        if d.get("evidence"):
            A(f"  Evidence files: {', '.join(f'`{e}`' for e in d['evidence'])}")
        A("")
    A("## 2. Work done this session")
    A("")
    A(f"One line per commit since {since}. Detail is in the commit and the notes it names.")
    A("")
    A(_VB.format("git commit subjects, as committed"))
    A("")
    for h, when, subj in done:
        A(f"- `{h}` {when} — {subj}")
    A("")
    A(_VE)
    A("")
    A("## 3. Work outstanding, needing no decision")
    A("")
    A(_VB.format("task-list headlines, as the markers carry them"))
    A("")
    for o in outstanding:
        extra = f" — ruling on record: {o['founder_ruling']}" if o.get("founder_ruling") else ""
        # The marker's own `ruled:` date, shown so a ruled-but-unexecuted item
        # reads as "you ruled this, the work is outstanding" rather than as a
        # mystery that quietly left the decision list.
        if o.get("struck_permanently"):
            extra += (" — **STRUCK PERMANENTLY ON YOUR INSTRUCTION, 2026-10-16. "
                      "It may not re-enter the decision list by any route.**")
        elif o.get("ruled"):
            extra += f" — **YOU RULED THIS ON {o['ruled']}; the work is outstanding**"
        # ★ THE BUILT STATE TRAVELS WITH THE ITEM INTO SECTION 3 (2026-10-16).
        # The mislabel that caused this generator to exist was calling A19
        # unbuilt when its marker read TESTED. Routing a ruled item out of the
        # decision list would have reproduced exactly that mislabel one section
        # further down, because only section 1 rendered the state.
        if o.get("already_built"):
            extra += f" — already BUILT and TESTED (`{o.get('status')}`)"
        A(f"- **{o['ident']}** ({o['source']}){extra}")
        A(f"  {o['headline']}")
    A("")
    A(_VE)
    A("")
    A(f"## 4. Explanations owed — {len(owed)}")
    A("")
    A("You asked for each of these before you would rule; the explanation was never "
      "delivered. Answers owed, not work owed. Producer: "
      "`scripts/his_older_instructions_triage_2026-10-11.py`.")
    A("")
    A(_VB.format("the founder's own words"))
    A("")
    for q in owed:
        A(f"- **{q['date']}** — {_first_sentence(q['text'])}")
    A("")
    A(_VE)
    A("")
    if superseded:
        A(f"**And {len(superseded)} discounted as no longer relevant**, on his question "
          f"*\"Are these questions still relevant? If not you can discount those that are "
          f"not.\"* Each is discounted against the record, not by judgement:")
        A("")
        A(_VB.format("the discounting record, quoted"))
        A("")
        for r in superseded:
            A(f"- **{r['date']} — {r['subject']}**")
            A(f"  {r['why']}")
            A(f"  *What remains:* {r['what_remains']}")
        A("")
        A(_VE)
        A("")
    A(f"## 5. Parked — {len(parked)}")
    A("")
    A("Judged non-blocking and appended rather than raised at the time. Queued, not "
      "dropped. Full list: `experimental_notes/PARKED_FOR_THE_FOUNDER.md`.")
    A("")
    A(_VB.format("PARKED_FOR_THE_FOUNDER.md, verbatim"))
    A("")
    for p in parked:
        A(f"- {p}")
    A("")
    A(_VE)
    A("")
    A("---")
    A("")
    A("*Written under CDSFL note standard v1.7.*")
    return "\n".join(L) + "\n"


def _spoken(text: str) -> str:
    """Markup out, prose intact. NOT a mechanical strip of a markdown document.

    The authored detail in `morning_report_decisions.json` is written as PROSE with
    light emphasis, so removing the emphasis leaves readable English rather than
    wreckage -- which is the condition `feedback_no_mechanical_tts` sets. Two
    deliberate omissions rather than transformations: FILE PATHS and the state/location
    line are dropped entirely, because note standard Rule 6 forbids spelling paths
    phonetically and the markdown companion already carries every locator. A listener
    gets what they need to DECIDE; a reader gets what they need to ACT.
    """
    t = text.replace("**", "").replace("*", "")
    t = re.sub(r"`([^`]*)`", lambda m: m.group(1), t)

    # ★ THE PATH STRIP WAS DESCRIBED AND NEVER IMPLEMENTED (found 2026-10-16).
    #
    # The docstring above has always promised that "FILE PATHS ... are dropped
    # entirely, because note standard Rule 6 forbids spelling paths
    # phonetically". The body did no such thing: it removed emphasis, unwrapped
    # backticks and replaced em-dashes, and every path in the authored detail
    # passed straight through into the spoken file.
    #
    # MEASURED on the file actually delivered to the founder on 2026-10-16: 12
    # path-like tokens, among them `scripts/the_coherence_recalibration_is_inert_
    # three_ways_2026-10-15.py` and `experimental_notes/evidence/coherence_
    # recalibration_inert_2026-10-15.json`, which a text-to-speech reader
    # pronounces character by character.
    #
    # THE GUARD DID NOT CATCH IT EITHER, because it asserted on ONE literal
    # prefix, `bench/tests/`. 11 of the 12 leaked tokens do not start with that
    # prefix, so the test passed while the defect shipped. Same shape as a module
    # that describes itself consistently: the description and the code agreed
    # with each other and both were wrong.
    #
    # A LABELLED CLAUSE IS DROPPED WHOLE, because deleting only the path leaves
    # "guard: , 13 tests" -- wreckage, which is what
    # `feedback_no_mechanical_tts` forbids. A bare path is dropped and the
    # punctuation around it tidied.
    t = re.sub(
        r"(?:[;.]\s*)?\b(?:Producer|Producers|Guard|Guards|Evidence|Script|"
        r"Scripts|Rule|Pinned by a test|Held by)\b\s*:?\s*[^.;]*?"
        r"[\w./-]*/[\w.-]+\.(?:py|json|md|txt|toml)[^.;]*", "", t)
    t = re.sub(r"[\w./-]*/[\w.-]+\.(?:py|json|md|txt|toml)", "", t)
    t = re.sub(r"\(\s*\)", "", t)
    t = re.sub(r"\s*,\s*,", ",", t)
    t = re.sub(r"\s+([,.;])", r"\1", t)
    t = re.sub(r"([,;])\s*\.", ".", t)

    t = t.replace(" — ", ", ").replace("—", ", ").replace(" – ", ", ")
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def render_tts(decs, outstanding, done, owed, parked, since, superseded=()) -> str:
    L = []
    A = L.append
    A(f"MORNING REPORT, {dt.date.today().strftime('%d %B %Y')}")
    A("")
    A(f"This report is generated from the project's own records rather than written by "
      f"hand, at commit {head_sha()}. Every item's state is read from its own marker, so "
      f"an item cannot be described as unbuilt when the record says it is built. The "
      f"narrative of what was done lives in the notes and the commit messages this "
      f"points at. The file itself is not kept in version control, because everything it "
      f"is built from is, and running the generator again at the same commit rebuilds it "
      f"exactly.")
    A("")
    A(f"There are {len(decs)} decisions needing an answer, {len(outstanding)} pieces of "
      f"outstanding work already ruled on, {len(done)} commits this session, "
      f"{len(owed)} explanations owed, and {len(parked)} parked items.")
    A("")
    A("SECTION 1. DECISIONS THAT NEED AN ANSWER")
    A("")
    for i, d in enumerate(decs, 1):
        A(f"DECISION {i}. {_spoken(d.get('title') or d['ident'])}")
        A("")
        A("What it is. " + _spoken(d.get("what", d.get("headline", ""))))
        A("")
        A("Why it needs a decision. " + _spoken(d.get("why", "")))
        A("")
        if d.get("options"):
            A("The options.")
            A("")
            for n, o in enumerate(d["options"], 1):
                A(f"{n}. {_spoken(o)}")
            A("")
        if d.get("evidence_line"):
            A("The evidence. " + _spoken(d["evidence_line"]))
            A("")
    A("SECTION 2. WORK DONE THIS SESSION")
    A("")
    A(f"{len(done)} commits. Each is one line here; the detail is in the commit message "
      f"and the notes it names.")
    A("")
    for _h, when, subj in done:
        A(f"{when}. {_spoken(subj)}")
    A("")
    A("SECTION 3. OUTSTANDING WORK THAT NEEDS NO DECISION")
    A("")
    A("Each of these already carries a ruling on the record, so it is queued work rather "
      "than a question.")
    A("")
    for o in outstanding:
        A(_spoken(o.get("title") or o["ident"]) + ".")
        A("")
        # Spoken aloud, so he hears that he already settled it and on what date.
        if o.get("ruled"):
            A(f"You ruled on this on {o['ruled']}. The work is outstanding, "
              f"not the decision.")
            A("")
        A(_spoken(o.get("what", o.get("headline", ""))))
        if o.get("why"):
            A("")
            A(_spoken(o["why"]))
        A("")
    A(f"SECTION 4. EXPLANATIONS OWED, {len(owed)} OF THEM")
    A("")
    A("Each of these is a place where an explanation was asked for before a ruling would "
      "be given, and the explanation was never delivered. These are answers owed rather "
      "than work owed.")
    A("")
    for q in owed:
        A(f"{q['date']}. {_spoken(_first_sentence(q['text']))}")
    A("")
    if superseded:
        A(f"And {len(superseded)} of them are discounted as no longer relevant, on his "
          f"question of whether these are still relevant. Each is discounted against the "
          f"record rather than by judgement.")
        A("")
        for r in superseded:
            A(f"{r['date']}. {_spoken(r['subject'])}.")
            A("")
            A(_spoken(r["why"]))
            A("")
            A("What remains. " + _spoken(r["what_remains"]))
            A("")
    A(f"SECTION 5. PARKED, {len(parked)} ITEMS")
    A("")
    A("These were judged not to block progress and appended rather than raised at the "
      "time. They are queued, not dropped.")
    A("")
    for pk in parked:
        A(_spoken(pk) + ".")
    A("")
    A("")
    A("Written under CDSFL note standard v1.7.")
    return "\n".join(L) + "\n"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--since", default=None,
                    help="session start for the work-done ledger; derived from "
                         "the most recent `sv:` commit when omitted")
    ap.add_argument("--write", action="store_true", help="write the report files")
    ap.add_argument("--check", action="store_true",
                    help="verify every derived item has authored detail, and exit")
    args = ap.parse_args(argv[1:])
    if args.since is None:
        args.since = _session_start()

    items = task_items() + study_items()
    decs, missing, orphan = decisions(items)

    if missing or orphan:
        print("REFUSED — the derived list and the authored detail disagree.")
        for k in missing:
            print(f"  NO AUTHORED DETAIL for a live item: {k}")
            print(f"    add it to {DETAIL.relative_to(REPO)} or it cannot be reported")
        for k in orphan:
            print(f"  AUTHORED DETAIL for an item no longer live: {k}")
            print(f"    remove it from {DETAIL.relative_to(REPO)}; it is stale")
        return 3
    if args.check:
        print(f"OK — {len(decs)} derived item(s), every one with authored detail.")
        return 0

    outstanding = [i for i in items if i["key"] not in {d["key"] for d in decs}]
    # anything whose authored detail marks it as needing no ruling moves to section 3
    outstanding += [d for d in decs if d.get("no_ruling_needed")]
    decs = [d for d in decs if not d.get("no_ruling_needed")]

    # ★ AN ENTRY HE HAS ALREADY RULED ON IS NOT A DECISION (2026-10-16).
    #
    # HIS QUESTION: *"are you certain none of these are items I have previously
    # ruled on? This seems an unusually large HIL queue, which traditionally has
    # been a strong indicator of mechanical, and/or implementation/process
    # failure."* It was. 5 of the 13 put to him should not have been, 38.4615%,
    # 95% Wilson [17.7097%, 64.4771%].
    #
    # `state` is lifecycle and `status` is build state; BOTH describe the work.
    # Until the `ruled` marker field existed there was nothing to read, so a
    # ruling he had given and that was not yet executed was indistinguishable
    # from one he had never seen. R1: ruled 2026-08-07 and again 2026-09-06, and
    # 70 days later it still appeared under "decisions that need you".
    #
    # IT MOVES, IT DOES NOT VANISH. A ruled item goes to section 3 carrying the
    # DATE he ruled, so he reads "you ruled this on X, the work is outstanding"
    # rather than losing sight of it. Silently dropping it would replace a queue
    # that over-asks with a queue that under-reports, which is worse.
    ruled_now = [d for d in decs if d.get("ruled")]
    outstanding += ruled_now
    decs = [d for d in decs if not d.get("ruled")]

    owed, superseded = explanations_owed()
    parked = parked_items()
    done = work_done(args.since)
    md = render_md(decs, outstanding, done, owed, parked, args.since, superseded)

    tts = render_tts(decs, outstanding, done, owed, parked, args.since, superseded)
    if args.write:
        out = (REPO / "experimental_notes"
               / f"Morning_Report_{dt.date.today().isoformat()}_GENERATED.md")
        out.write_text(md, encoding="utf-8")
        print(f"  wrote {out.relative_to(REPO)}  ({len(md.splitlines())} lines)")
        desk = (pathlib.Path.home() / "Desktop" / "CDSFL_tts"
                / f"Morning_Report_{dt.date.today().isoformat()}_GENERATED.txt")
        desk.parent.mkdir(parents=True, exist_ok=True)
        desk.write_text(tts, encoding="utf-8")
        print(f"  wrote {desk}  ({len(tts.splitlines())} lines)")
        # STAMP THEM HERE, because regenerating WIPES a stamp applied afterwards and a
        # step you must remember is a step that gets forgotten. His order of 2026-10-12:
        # give each output its own hash value, to track them exactly.
        try:
            sys.path.insert(0, str(REPO / "scripts"))
            from stamp_output_hash_2026_10_12 import main as _stamp  # noqa: F401
        except ImportError:
            import importlib.util as _ilu
            _spec = _ilu.spec_from_file_location(
                "stamper", str(REPO / "scripts" / "stamp_output_hash_2026-10-12.py"))
            _m = _ilu.module_from_spec(_spec)
            sys.modules["stamper"] = _m
            _spec.loader.exec_module(_m)
            _stamp = _m.main
        _stamp(["stamp_output_hash", str(out), str(desk)])
    else:
        print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
