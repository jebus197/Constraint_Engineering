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
to 435 lines against a 40-300 limit, over by 135. ★ THAT LIMIT WAS NEVER THE NOTE
STANDARD'S AND NEVER HIS (corrected 2026-11-06). It is item 10 of note standard v1,
the archival first version; the current v1.9 carries no length rule. 0 of 1,678 of his
recorded annotation blocks state a numeric length limit. The live check is now a
DERIVED per-item budget, not a total. See `scripts/the_line_caps_were_never_his_2026-11-06.py`.

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
#: READ, NOT RESTATED. These reports carried "v1.7" in both foot-lines while the
#: standard had been v1.8 since 2026-10-17, so every report this generator wrote
#: stamped itself with an ARCHIVAL standard. The version now comes from the
#: linter's own named constant, which is the thing that decides what is current,
#: so the next bump cannot leave the generator behind.
sys.path.insert(0, str(REPO / "scripts"))
from note_vagueness_lint import CURRENT_NOTE_STANDARD  # noqa: E402

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
            # ★ N1, 2026-11-09. THE DATE HE REPLIED, which is not the date
            # he settled it. `ruled` routes an entry to `no_ruling_needed`;
            # `responded` must never do that, so it is carried for RENDERING
            # only and no predicate below reads it.
            "responded": r.responded,
            "headline": _first_sentence(r.text),
        })
    return out


#: A parked heading that says, IN ITS OWN WORDS, that it is finished. His `pf`
#: of 2026-11-01: *"The vast majority of these have already been discussed and
#: ruled on."* Measured the same night by
#: `scripts/the_parked_file_represents_settled_business_2026-11-01.py`: **5 of
#: 26 live headings declare their own closure**, Wilson 95% [0.085071,
#: 0.378763], and reached him anyway, because `parked_items()` drops a heading
#: only when it NAMES a task-list entry recorded DONE or WITHDRAWN and has no
#: rule for a heading whose own text says RESOLVED.
#: ★ CASE-SENSITIVE ON PURPOSE, AND THE FIRST VERSION WAS NOT.
#: With `re.I` this matched the LIVE heading "A superseded copy from
#: August is sitting visible on your Desktop", which is a warning that a
#: stale file is on his Desktop -- not a declaration that anything is
#: closed. The fix therefore SUPPRESSED a live item, which is strictly
#: worse than the noise it was built to remove: his `pf` asked for less
#: repetition, not for live work to be hidden. Caught 2026-11-01 by
#: `bench/tests/test_the_parked_presentation_is_described_not_coded_2026-11-01.py`.
#: Every genuine declaration in this corpus is written in CAPITALS --
#: "RESOLVED --", "SUPERSEDED, THE QUESTION GOT SMALLER", "0.1 IS CLOSED",
#: "NOT A BLOCKER" -- so case is the discriminator the corpus already
#: supplies, and it needs no new vocabulary. A mention is lowercase; a
#: declaration shouts.
_PARKED_SELF_CLOSED = re.compile(
    r"\b(RESOLVED|SUPERSEDED|IS CLOSED|NOTHING LEFT TO RULE ON|"
    r"NOT A BLOCKER|ALREADY (?:DONE|BUILT|FIXED))\b")

_PARKED_CODE = re.compile(r"\b([A-Z]{1,2}\d{1,4}[a-z]?)\b")

#: A heading that declares itself a DUPLICATE of another, in its own words.
#: Found 2026-11-01 in the live set: `Enable Tailscale SSH on the private
#: network -- SAME DECISION AS 10.2 ABOVE, NOT A SECOND ONE`. The closure
#: pattern above does not catch it because it is not closed, it is the SAME
#: question written twice -- which is the repetition he objected to, in the
#: clearest possible form, since the note says so itself.
#: Case-sensitive for the same reason as above: "the reason is the same as
#: C0040" is prose about a reason, not a declaration that this item
#: restates another.
_PARKED_SAME_AS = re.compile(
    r"\bSAME (?:DECISION|QUESTION|ITEM) AS\b|\bNOT A SECOND ONE\b")

#: `CODE: the actual description` -- the shape his complaint names. The code is
#: pulled OUT so the description leads and the code becomes a reference, which
#: is Rule 19 of the note standard (name the subject) applied to this report.
_PARKED_LEADING_CODE = re.compile(
    r"^\s*((?:[A-Z]{1,2}\d{1,4}[a-z]?)(?:\s*(?:and|/|,)\s*"
    r"[A-Z]{1,2}\d{1,4}[a-z]?)*)\s*[:\u2014-]\s*(.+)$")


def parked_presentation(parked, items) -> dict:
    """Turn live parked HEADINGS into described, de-duplicated items.

    HIS `pf`, 2026-11-01, verbatim: *"But you are again presenting me just with
    ticket labels like B21, C0037, C0036, without giving any meaningful
    indication what these are? This does not match the recently agreed tts
    presentation standard for issues of this type. Please fix."*

    3 FAULTS, 3 TREATMENTS, each measured before it was written:

      * SETTLED BUSINESS. 5 of 26 live headings declared their own closure and
        still reached him. Those are moved to a `settled` list which the report
        COUNTS and does not enumerate -- nothing is hidden and nothing is
        deleted from `PARKED_FOR_THE_FOUNDER.md`, which keeps every heading.
      * REPETITION. `B21` alone owned **7** of the 26 live headings, so 1
        subject was presented 7 times; collapsing to 1 per subject removes 6 of
        26, Wilson 95% [0.110338, 0.420516]. The collapsed item carries the
        count, so the fact that 7 notes accumulated is still visible.
      * BARE CODES. The description comes from the task list's OWN first
        sentence for that entry, which `task_items()` already returns as
        `headline`. No new data source and no new parser: the generator was
        holding the description all along and rendering the code instead.

    `parked_items()` IS NOT TOUCHED. Its return type is consumed by 4 other
    scripts and 2 guards, and a SECOND function of the same name in
    `has_he_already_ruled_on_the_parked_2026-10-13.py` returns pairs rather
    than strings -- so changing the contract would have reached further than the
    fault. This takes its output as given.

    Returns `{"live": [...], "settled_count": int, "settled_words": [...]}`
    where each live item is a dict with `subject`, `detail`, `codes` and
    `seen_in`.
    """
    by_code = {}
    for it in items or []:
        by_code[it.get("ident")] = it

    settled, dupes, keep = [], [], []
    for h in parked:
        if _PARKED_SELF_CLOSED.search(h):
            settled.append(_PARKED_SELF_CLOSED.search(h).group(0).upper())
        elif _PARKED_SAME_AS.search(h):
            # Its own text says it is another item restated. Counted, not
            # enumerated, for the same reason as a closed one.
            dupes.append(h)
        else:
            keep.append(h)

    grouped, loose = {}, []
    for h in keep:
        codes = sorted(set(_PARKED_CODE.findall(h)) & set(by_code))
        if codes:
            grouped.setdefault(codes[0], []).append(h)
        else:
            loose.append(h)

    live = []
    for code, heads in sorted(grouped.items()):
        entry = by_code.get(code) or {}
        # The LONGEST heading is the most informative one, and it is kept as
        # the live question rather than the first or last arbitrarily.
        longest = max(heads, key=len)
        live.append({
            "subject": entry.get("headline") or longest,
            "detail": longest,
            "codes": [code],
            "seen_in": len(heads),
            "ruled": entry.get("ruled"),
            "state": entry.get("state"),
        })
    for h in loose:
        m2 = _PARKED_LEADING_CODE.match(h)
        if m2:
            # DESCRIPTION FIRST, CODE SECOND. This is the whole of his
            # complaint: the heading already held a description and the report
            # was leading with the identifier instead.
            codes = _PARKED_CODE.findall(m2.group(1))
            live.append({"subject": m2.group(2).strip(), "detail": h,
                         "codes": codes, "seen_in": 1,
                         "ruled": None, "state": None})
        else:
            live.append({"subject": h, "detail": "", "codes": [],
                         "seen_in": 1, "ruled": None, "state": None})

    return {"live": live, "settled_count": len(settled),
            "settled_words": sorted(set(settled)),
            "duplicate_count": len(dupes)}


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
            #: ★ THE FULL STATUS IS CARRIED, 2026-11-08. It was cut at 60
            #: characters and never rendered, so the record could say a defect
            #: was FIXED while the report said its work was outstanding. These
            #: statuses now run to about 1,000 characters, and the renderer --
            #: not the extractor -- decides what to show and says what it cut.
            "status": str(drec.get("status", "")),
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
    # ★ RETIRED IS HIS RULING; SUPERSEDED IS A DERIVATION. Added 2026-11-01 on
    # his ruling "Retire them. stm". They are kept as separate lists because
    # they are different claims: superseded says the record answered the
    # question after he asked it, retired says he struck it. Reporting a
    # retirement as a supersession would tell a reader the record overtook a
    # question when in fact he decided it needed no answer.
    retired = []
    if SUPERSEDED.is_file():
        retired = json.loads(SUPERSEDED.read_text(encoding="utf-8")).get("retired", [])
    live, dead = [], []
    for q in owed:
        hit = next((r for r in recs
                    if r["date"] == q["date"] and r["match"] in q["text"]), None)
        if hit is None:
            hit = next((r for r in retired
                        if r["date"] == q["date"] and r["match"] in q["text"]), None)
            if hit is not None:
                hit = {**hit, "retired_by_his_ruling": True}
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
    a 300-line ceiling then attributed to "Rule 10" -- a label defined in 0 of the
    10 note-standard files, corrected 2026-11-06. A session boundary that is typed
    once is a session boundary that is wrong from the next session on, and so is a
    length ceiling: the live check derives a per-item budget instead.

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


#: A LEDGER LINE IS ONE LINE, AND ITS BUDGET IS DERIVED FROM THE PREFIX.
#:
#: * ADDED 2026-10-30. `test_it_lists_commits_not_narrative` pins a ledger line
#: below 220 characters, and commit `018e1b01` carries a 226-character subject
#: written the same night -- 193 characters of prose where a subject belongs.
#: The guard is right: that subject IS narrative. History is not rewritten here,
#: on his ruling, so the generator must tolerate an over-long subject rather
#: than break on one.
#:
#: THE BUDGET IS MEASURED, NEVER RESERVED. It is the limit minus the length of
#: the ACTUAL rendered prefix minus the marker, because a hardcoded reserve
#: cannot bound a string whose prefix grows -- the 960-against-900 defect of
#: 2026-10-28, where a truncation path reserved 200 characters for a notice
#: whose length grew with the open count.
#:
#: AND THE LABEL CHANGES WITH IT. The surrounding region is declared verbatim as
#: "git commit subjects, as committed". A silent truncation would make that
#: declaration false, so the declaration now names the truncation. 220 stays
#: hardcoded in the guard ON PURPOSE: a pin that imported this constant would
#: follow it upward and stop being a pin.
_LEDGER_LINE_MAX = 200
_LEDGER_TRUNCATION_MARK = " [...]"


def ledger_line(prefix: str, subject: str,
                limit: int = _LEDGER_LINE_MAX) -> str:
    """One ledger line, with the subject cut to the measured remaining budget."""
    line = prefix + subject
    if len(line) <= limit:
        return line
    budget = limit - len(prefix) - len(_LEDGER_TRUNCATION_MARK)
    if budget <= 0:                 # prefix alone already over: nothing to cut
        return line
    return prefix + subject[:budget].rstrip() + _LEDGER_TRUNCATION_MARK


def _first_sentence(text: str) -> str:
    t = re.sub(r"\s+", " ", (text or "").replace("**", "")).strip()
    m = re.search(r"^(.{20,200}?[.!?])(\s|$)", t)
    return (m.group(1) if m else t[:200]).strip()


# ───────────────────────── the authored half ─────────────────────────

#: ★ A SETTLED TICKET IS NOT A DECISION -- HIS INSTRUCTION, 2026-11-01:
#: *"Please fix it so issues that are genuinely closed don't keep being
#: represented."*
#:
#: HOW CLOSED WORK REACHED HIM ANYWAY. This generator carried 2 filters, both
#: keyed on the TASK LIST: `no_ruling_needed` from the authored detail, and the
#: `ruled:` marker date. Neither consults the REGISTER, which is the only record
#: where CLOSED is tool-only and requires a verification. So an item whose ticket
#: was closed with evidence could still be presented as a question, and on
#: 2026-11-01 he asked of 2 such items *"So if it is closed, why did it come up
#: again?"*. The nearest thing to a check was `_PARKED_SELF_CLOSED`, which reads
#: PROSE for a self-declared closure -- a text heuristic, and the same shape as
#: the case-insensitive match that suppressed live work hours earlier.
#:
#: AND THE OPPOSITE FAULT IS DESIGNED OUT RATHER THAN RISKED. Dropping on a
#: settled ticket ALONE would recreate the suppression measured this morning,
#: where a ruling 14 days older than its entry's newest questions silenced 4 of
#: them. So an item leaves the decision list only when its tickets are ALL
#: settled AND the entry carries NO LIVE ASKING SENTENCE, the second half being
#: the predicate already built and mutation-tested in
#: `scripts/how_many_decisions_actually_need_him_2026-11-01.py`. 1 predicate, 2
#: callers -- never 2 implementations asserted to agree.
#:
#: IT FAILS OPEN. An item with no ticket, an unreadable register, or any live
#: ask is KEPT. A filter that hides an item when its own input is missing is the
#: false-zero shape this project has met repeatedly.
_SETTLED_STATUSES = frozenset({"CLOSED", "MERGED", "WITHDRAWN", "REJECTED",
                               "DUPLICATE", "DEPRECATED"})


def settled_in_the_register(ident: str) -> tuple[bool, str]:
    """(is it settled, why) for one task entry, read from the register."""
    try:
        sys.path.insert(0, str(REPO))
        from bench.ticket_store import TicketStore        # noqa: PLC0415
        rows = [t for t in TicketStore().all()
                if getattr(t, "task_ref", None) == ident]
    except Exception as exc:                               # noqa: BLE001
        return False, f"register unreadable ({type(exc).__name__}), kept"
    if not rows:
        return False, "no ticket, kept"
    unsettled = [t for t in rows if str(t.status).upper() not in _SETTLED_STATUSES]
    if unsettled:
        return False, f"{len(unsettled)} of {len(rows)} ticket(s) still open"
    shown = rows[:3]
    tail = (f", + {len(rows) - len(shown)} more" if len(rows) > len(shown) else "")
    return True, (f"all {len(rows)} register ticket(s) settled: "
                  + ", ".join(f"{t.tid[:8]} {t.status}" for t in shown) + tail)


#: ★ AN ENTRY WAITING ON ANOTHER ENTRY'S DECISION IS NOT A DECISION OF ITS OWN
#: -- the fault he challenged on 2026-11-01: *"The first seemed like a
#: suspiciously high number, as you have a habit of repeating issues to me to
#: rule on that I have already ruled on, or that have already been settled."*
#:
#: THE 2 FILTERS THIS GENERATOR ALREADY CARRIED ARE BOTH KEYED ON ONE ENTRY'S
#: STATE -- `no_ruling_needed` added 2026-10-16 and the `ruled:` marker added
#: 2026-10-19, each after he asked this same question. Neither can see a
#: DECISION GRAPH, so 4 entries that each say in their own text that they await
#: a 5th were presented to him as 4 decisions. Measured 2026-11-01: of the 10
#: items presented under a heading promising they were his to decide, 3 were
#: genuinely his, 1 he had ruled on 2026-10-30, and 6 were mine.
def depends_on_another_entry(ident: str) -> str | None:
    """The entry whose decision this one waits on, or None."""
    try:
        mod = _load(REPO / "scripts"
                    / "how_many_decisions_actually_need_him_2026-11-01.py",
                    "decide_probe")
        bodies = mod.bodies()
        import task_list_markers as _T                   # noqa: PLC0415
        e = {x.ident: x for x in _T.parse_entries()}.get(ident)
        if e is None:
            return None                                   # unknown: fail open
        d = mod.classify_text((e.state or ""), e.ruled, bodies.get(ident, ""))
        return d["parent"] if d["kind"] == "DEPENDENT" else None
    except Exception:                                     # noqa: BLE001
        return None                                       # cannot tell: fail open


#: ★ THE PREDICATE HAS TO BE DATE-AWARE, AND MY FIRST ATTEMPT WAS NOT.
#: Using "does it still ask" alone took the decision list from 3 to 12 and put
#: back the zero-plant control, which he ruled DEFERRED on 2026-10-30 with the
#: words *"You keep asking me about this and I keep giving you the same
#: answer"*, plus items whose only remaining question was whether the work was
#: done. That is the inflation he challenged, recreated by over-correcting the
#: suppression -- and it is why the ruling filter existed: measured 2026-10-17,
#: 11 of 45 ruled entries still carried an asking sentence their ruling had
#: already answered.
#:
#: SO THE TEST IS NOT "does it ask" BUT "does it ask something NEWER than the
#: ruling". A question raised after a ruling cannot have been answered by it; a
#: question raised before it probably was.
_DATED = re.compile(r"\b(2026-\d{2}-\d{2})")


#: ★ A STORE KEY IS NOT AN IDENTIFIER, AND PASSING ONE HERE USED TO BE SILENT.
#: Both this function and `still_asks` look an identifier up in dicts keyed
#: BARE -- `B21`, never `task:B21`. A caller that passes the store key finds
#: nothing, and the miss then reads as a finding: `bodies().get("task:B21","")`
#: returns "", `_DATED.findall("")` is empty, `any([])` is False, and the
#: function reports "the ruling still settles this entry" -- the one direction
#: that SILENCES him.
#:
#: MEASURED COST, 2026-11-07. `how_many_verdicts_really_await_him_2026-11-06.py`
#: called `ruling_is_spent(f"task:{ident}", ...)`. 3 of 41 live entries were
#: labelled REPEAT on that empty string -- B13, B20 and B21 -- and B20 is the
#: next task on the list and the 1st decision in his queue, its own heading
#: saying he has ruled the build 3 times and has never been asked whether to
#: turn it on. Half the defect was hidden because B71 came out right anyway,
#: rescued by the BLOCKED branch.
#:
#: WHY A COLON AND NOT A MISSING KEY. Failing open on any ident absent from
#: `bodies()` was tried first and is REJECTED BY MEASUREMENT: the 7 `defect:`
#: entries he ruled on 2026-10-16 legitimately have no body, so that version
#: moved the decision queue from 29 to 36 and would have put 7 settled items
#: back in front of him -- the already-ruled fault it was written to prevent.
#: A COLON is the precise signal, because 0 of 274 task-list entries, 0 of 274
#: `bodies()` keys and 0 decision identifiers contain one, so a colon can only
#: mean a caller passed a key where an identifier belongs.
#: Producer: scripts/are_the_twenty_nine_new_or_repeats_2026-11-07.py
_KEY_NOT_IDENT = (
    "asks_newer_than_the_ruling was passed {!r}, which contains a colon and is "
    "therefore a STORE KEY, not an entry identifier. The lookups here are keyed "
    "bare (B21, not task:B21); a prefixed key finds nothing and the miss reads "
    "as 'the ruling still settles this', which silences him. Pass the bare "
    "identifier. See scripts/are_the_twenty_nine_new_or_repeats_2026-11-07.py."
)


def _reject_store_key(ident: str) -> None:
    """1 predicate, 3 callers -- the 3 public entry points that take an ident.

    Written as 1 function rather than 3 copies because this file already holds
    the lesson: `ruling_is_spent` exists precisely because the same date rule
    was written out at 2 call sites and repaired at only 1.
    """
    if ":" in (ident or ""):
        raise ValueError(_KEY_NOT_IDENT.format(ident))


def asks_newer_than_the_ruling(ident: str, ruled: str | None) -> bool:
    """A live ask PLUS a dated addition later than the ruling that silences it."""
    _reject_store_key(ident)
    if not ruled:
        return bool(still_asks(ident))
    if not still_asks(ident):
        return False
    try:
        mod = _load(REPO / "scripts"
                    / "how_many_decisions_actually_need_him_2026-11-01.py",
                    "decide_probe")
        body = mod.bodies().get(ident, "")
    except Exception:                                    # noqa: BLE001
        return False                                     # cannot tell: stay quiet
    return any(d > ruled for d in _DATED.findall(body))


def still_asks(ident: str) -> bool:
    """Does this entry carry a LIVE asking sentence? 1 predicate, 2 callers."""
    _reject_store_key(ident)
    try:
        mod = _load(REPO / "scripts"
                    / "how_many_decisions_actually_need_him_2026-11-01.py",
                    "decide_probe")
        bodies = mod.bodies()
        rows = {e.ident: e for e in __import__("task_list_markers").parse_entries()}
        e = rows.get(ident)
        if e is None:
            return True                     # unknown entry: fail open
        d = mod.classify_text((e.state or ""), e.ruled, bodies.get(ident, ""))
        return bool(d["live_asks"])
    except Exception:                        # noqa: BLE001
        return True                          # cannot tell: fail open


def ruling_is_spent(ident: str, ruled: str | None, state: str | None) -> bool:
    """Has the recorded ruling stopped settling this entry? 1 predicate, 2 callers.

    ★ WRITTEN 2026-11-01 BECAUSE THE RULE WAS DECLARED TWICE AND REPAIRED ONCE.
    `decisions()` and `main()` each decided independently whether a ruling date
    still absolves an entry, by the same date comparison written out twice. Both
    were individually correct, so no test could see them disagree -- the shape
    `execute-do-not-grep` names, and the 5th time this project has met it. The
    BLOCKED carve-out was added to the first site and the second site silently
    undid it, which is how B71 stayed out of the list after the first repair.

    2 ways a ruling stops settling an entry:
      1. the entry carries a DATED addition later than the ruling, so the ask
         postdates the answer;
      2. the entry is BLOCKED and still asking, which no date can detect when
         the ruling and the new question fall on ONE DAY, as B71's did.
    """
    _reject_store_key(ident)
    if not ruled:
        return False
    if asks_newer_than_the_ruling(ident, ruled):
        return True
    return (state or "").upper() == "BLOCKED" and bool(still_asks(ident))


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
        # ★ A RULING DATE IS A POINT EVENT, NOT PERMANENT ABSOLUTION.
        # Corrected 2026-11-01, and this is the INVERSE of the fault above and
        # the worse direction of it. This branch removed an entry from the
        # decision list the moment it carried ANY ruling date. The role-layer
        # entry carries a ruling of 2026-10-17 and has since collected 4 NEW
        # questions, dated 2026-10-30, 2026-10-31 and 2026-11-01 in its own
        # body: whether a role is 1 dimension or 2, the go-ahead to build the
        # single functional layer, the 2 declarations of the structural axis,
        # and the type-checker configuration. A ruling 14 days older than the
        # questions silenced all 4.
        #
        # REPETITION IS VISIBLE; SUPPRESSION IS NOT -- the identical argument
        # that forced the reversal of the parked-file fix 9 hours earlier the
        # same night. A question raised AFTER a ruling cannot have been answered
        # by it, so the ruling only settles the entry when the entry has stopped
        # asking. `still_asks` is the same predicate the 2 filters below use.
        if ruling_is_spent(it.get("ident") or "", ruled, it.get("state")):
            attached.append({**it, **d, "ruled": ruled})
            continue
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


#: Statuses at which the WORK is in the tree. `state` says whether the ENTRY
#: is closed; `status` says how far the work got. Section 3 lists items whose
#: STATE is still OPEN, so an item belongs there on its state -- but the prose
#: below used to assert "the work is outstanding" from the ruling date alone,
#: with no reference to status at all. The moment 2 statuses were correctly
#: advanced to COMMITTED on 2026-11-08 that clause became FALSE, and the line
#: he reads said the work was outstanding and COMMITTED in the same breath.
#:
#: Measured before and after: with 3 further advances applied, the old pair of
#: clauses contradicts itself on 5 of 21 ruled items and this pair on 0 of 21.
#: That is why the status advance and this change ship TOGETHER -- the advance
#: alone takes the contradiction from 2 to 5, so composing them dominates
#: either half, which is the only sense in which composing is justified here.
WORK_IS_DONE = ("COMMITTED", "ENABLED")


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
        A(f"### {i}. {d.get('title') or d['ident']}{ticket_tag(d['ident'])}")
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
    A(_VB.format("git commit subjects, as committed, each cut to one line "
              "at " + str(_LEDGER_LINE_MAX) + " characters where over-long"))
    A("")
    for h, when, subj in done:
        A(ledger_line(f"- `{h}` {when} — ", subj))
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
        #: ★ THE RECORDED STATUS IS SHOWN, 2026-11-08, so the record and this
        #: report cannot disagree about whether a defect is still open work.
        #: The cut is ANNOUNCED rather than silent: a listing trimmed under a
        #: heading that reads as complete is the defect class repaired 5 times
        #: in this file's own history.
        _st = str(o.get("status") or "").strip()
        if _st and o.get("source", "").startswith("programme of study"):
            _shown = _st[:200]
            _rest = len(_st) - len(_shown)
            extra += (f" — **RECORDED STATUS:** {_shown}"
                      + (f" … ({_rest} more characters in "
                         f"experimental_notes/STUDY_IN_FLIGHT.json)"
                         if _rest > 0 else ""))
        if o.get("struck_permanently"):
            extra += (" — **STRUCK PERMANENTLY ON YOUR INSTRUCTION, 2026-10-16. "
                      "It may not re-enter the decision list by any route.**")
        elif o.get("ruled"):
            #: ★ CONDITIONED ON STATUS, 2026-11-08. See WORK_IS_DONE above.
            _done = _st.upper() in WORK_IS_DONE
            extra += (
                f" — **YOU RULED THIS ON {o['ruled']}; the work is "
                f"`{_st.upper()}` and the ENTRY is still open**" if _done
                else f" — **YOU RULED THIS ON {o['ruled']}; "
                     f"the work is outstanding**")
        # ★ THE BUILT STATE TRAVELS WITH THE ITEM INTO SECTION 3 (2026-10-16).
        # The mislabel that caused this generator to exist was calling A19
        # unbuilt when its marker read TESTED. Routing a ruled item out of the
        # decision list would have reproduced exactly that mislabel one section
        # further down, because only section 1 rendered the state.
        if o.get("already_built") and _st.upper() not in WORK_IS_DONE:
            #: Suppressed once the work is done, because the clause above
            #: already names the status and printing it twice in one line is
            #: noise. Retained verbatim for every status short of COMMITTED,
            #: so nothing a reader relied on is lost.
            extra += f" — already BUILT and TESTED (`{o.get('status')}`)"
        A(f"- **{o['ident']}**{ticket_tag(o['ident'])} ({o['source']}){extra}")
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
    # ★ THE REGION IS ONLY OPENED WHEN IT HAS SOMETHING IN IT, 2026-11-03. With
    # 0 explanations owed the markers were emitted around nothing, which cost 4
    # lines and left an empty verbatim region in a report already 69 lines over
    # Rule 10's ceiling. An empty exemption region is also meaningless: it
    # exempts no text while still being a region the balance check must account
    # for, and the same night's stray-close defect showed what an unaccounted
    # marker costs.
    if owed:
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
        # ★ HIS `pf` OF 2026-11-01 REACHES THIS SECTION TOO, 2026-11-03. It was
        # applied to the PARKED section and not to this one, its sibling: this
        # enumerated 11 struck questions at 3 lines each, 9 of them repeating an
        # identical retirement sentence and an identical "Nothing", under a
        # heading that already said 0 were owed. That is the re-presenting of
        # settled business his ruling names. The TTS renderer at the equivalent
        # point already states the count and does not enumerate, so the 2
        # renderings disagreed and the MARKDOWN was the wrong one.
        #
        # THE FOLD KEEPS WHAT MATTERS. Collapsing all 11 was the obvious move and
        # would have hidden 2 live items: grouping by `what_remains` gives 3
        # distinct values, and while 9 say "Nothing. He struck the question", the
        # other 2 declare REMAINING WORK. So the nothing-remains group is COUNTED
        # and every other item is ENUMERATED, which is what `parked_presentation`
        # means by folding what is restated rather than dropping it.
        _struck = [r for r in superseded
                   if str(r.get("what_remains", "")).strip().lower()
                   .startswith("nothing")]
        _live_sup = [r for r in superseded if r not in _struck]
        if _struck:
            A(f"**{len(_struck)} of those were struck rather than deferred** — "
              f"his ruling of 2026-11-01, verbatim *\"Retire them. stm\"* — so "
              f"nothing remains on any of them and they are counted here rather "
              f"than listed again. Every one is kept in full in the record this "
              f"section is derived from.")
            A("")
        if _live_sup:
            A(f"**{len(_live_sup)} of them leave something behind**, so each is "
              f"named:")
            A("")
            A(_VB.format("the discounting record, quoted"))
            A("")
            for r in _live_sup:
                A(f"- **{r['date']} — {r['subject']}**")
                A(f"  {r['why']}")
                A(f"  *What remains:* {r['what_remains']}")
            A("")
            A(_VE)
        A("")
    # ★ HIS `pf`, 2026-11-01. The raw headings used to be printed verbatim,
    # which re-presented settled business and led with identifiers. Now routed
    # through `parked_presentation`, which counts what is closed, folds what is
    # restated, collapses 1 subject to 1 line, and puts the DESCRIPTION first.
    _pres = parked_presentation(parked, outstanding)
    _plive = _pres["live"]
    A(f"## 5. Parked — {len(_plive)}")
    A("")
    A("Judged non-blocking and appended rather than raised at the time. Queued, not "
      "dropped. Full list: `experimental_notes/PARKED_FOR_THE_FOUNDER.md`.")
    if _pres["settled_count"] or _pres["duplicate_count"]:
        A("")
        A(f"**{len(parked)} notes reduce to {len(_plive)} items.** "
          f"{_pres['settled_count']} say in their own words that they are "
          f"finished ({', '.join(_pres['settled_words'])}) and "
          f"{_pres['duplicate_count']} say they restate another item, so both "
          f"are counted here rather than listed again. Nothing is removed from "
          f"the parked file itself.")
    A("")
    for it in _plive:
        ref = f" `{', '.join(it['codes'])}`" if it["codes"] else ""
        seen = (f" *(accumulated over {it['seen_in']} notes)*"
                if it["seen_in"] > 1 else "")
        _subj = it["subject"].strip()
        if _subj:
            _subj = _subj[0].upper() + _subj[1:]
        _tids = "".join(ticket_tag(c) for c in it["codes"]) if it.get("codes") else ""
        A(f"- {_subj}{ref}{_tids}{seen}")
        if it.get("ruled"):
            A(f"  You ruled on this on {it['ruled']}; what is left is work.")
    A("")
    # ★ THE ORPHAN `_VE` IS REMOVED, 2026-11-03. This section used to print the
    # parked headings VERBATIM and was wrapped accordingly. His `pf` of
    # 2026-11-01 routed it through `parked_presentation`, which makes the text
    # this project's OWN presentation prose, and the opening `_VB` was dropped
    # -- correctly, since Rule 27 should bind it -- while the closing marker was
    # left behind. The output therefore carried 4 begin markers against 5 ends,
    # which `region_state` reports as 1 stray close and the note standard calls
    # malformed. FOUND 2026-11-03 by the self-lint added to this generator the
    # same hour, on its FIRST run: nothing had ever linted this file, because it
    # is gitignored and the test that would catch it is not on the commit board.
    # A repair that removes an opening marker must remove its close in the same
    # edit; this is the half that was missed.
    A("")
    A("---")
    A("")
    A(f"*Written under CDSFL note standard {CURRENT_NOTE_STANDARD}.*")
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


#: ★ B105: HIS RULING OF 2026-11-08, AND IT AMENDS HIS OWN EARLIER PROPOSAL.
#: Verbatim: *"I accept your recommendation. But because a double asterisk
#: *like this* can be misread in some situations, change this so that your
#: messages open with an asterisk *like this but do not close with one. stm"*
#:
#: HIS ORIGINAL PROPOSAL was that his comments always open with a `#` and mine
#: always open AND CLOSE with a `*`. The measurement argued against the pair and
#: he accepted that, then kept the open-only half: Read Aloud speaks every
#: asterisk as the word "asterisk", so 2 per paragraph is twice the noise of 1.
#: A report of 100 paragraphs costs him 100 spoken noises instead of 200.
#:
#: WHAT IS MARKED AND WHAT IS NOT, because marking the wrong line MISATTRIBUTES
#: HIS OWN WORDS TO ME, which is worse than not marking at all:
#:   * MY PROSE PARAGRAPHS        -> marked
#:   * his quoted material        -> NOT marked. The spans are already tracked
#:                                  by line index in `_ex` for the lint, so the
#:                                  same record governs both.
#:   * section titles             -> NOT marked. The note standard's own words
#:                                  are "a blank line and a capitalised section
#:                                  title on its own line", so a lone
#:                                  capitalised line is structure, not prose.
#:   * numbered list items        -> NOT marked. The standard permits
#:                                  "numbered lists with digits and full stops
#:                                  only", and an asterisk before a digit reads
#:                                  as 2 noises in a row.
#:   * a line already marked      -> NOT marked twice.
#:
#: IT RUNS BEFORE THE OFFSET CONVERSION BELOW, deliberately. `exempt_out`
#: converts line indices to CHARACTER offsets from `L` itself, so inserting
#: characters afterwards would slide every offset by the number of asterisks
#: above it and the lint's exempt spans would describe the wrong text.
#: A numbered or bracketed list item, an ISO date, or a clock time.
#: These are structure or ledger lines rather than prose of mine.
_LIST_OR_STAMP = re.compile(
    r"^\s*(?:\d+[.)]\s|\d{4}-\d{2}-\d{2}|\d{1,2}:\d{2})")


def _mark_my_paragraphs(lines: list, exempt_spans: list,
                        heading_idx=()) -> int:
    """Prefix `*` to the first line of each paragraph that is MINE. In place.

    Returns how many paragraphs were marked, so a caller or a test can assert
    the count rather than trust the walk.

    ★ `heading_idx` IS A RECORD, NOT A SHAPE, AND THAT IS THE WHOLE POINT.
    The all-caps test below cannot recognise a heading whose body is prose:
    `DECISION 1. B13, admitting a model is not trivial` is a structural
    heading with a mixed-case headline, so on the first build all 17 of them
    were marked -- 17 spoken instances of the word "asterisk" on the lines
    that give the report its structure, which his ruling of 2026-11-08 did
    not ask for (it governs PARAGRAPHS), and a sibling guard red because
    the guard pattern for a numbered decision heading no longer matched. The FOOT-LINE was marked too, and
    the note standard requires that exact line as the final content.
    B105's own finding was that a SHAPE heuristic misreading headings was 1
    of the 3 measured causes of his lost responses, so inferring a heading
    here would repeat the error it diagnosed. `render_tts` knows which lines
    it emits as headings, so it RECORDS them at the point of emission, the
    way `_ex` already records quoted spans -- 1 record, no second opinion.
    """
    _headings = set(heading_idx or ())
    quoted = set()
    for _a, _b in (exempt_spans or []):
        for _i in range(max(0, _a), min(len(lines), _b)):
            quoted.add(_i)

    def _is_section_title(text: str) -> bool:
        letters = [c for c in text if c.isalpha()]
        if not letters:
            return False
        return all(c.isupper() for c in letters)

    #: THE DOCUMENT TITLE IS NOT A PARAGRAPH OF MINE, and the all-caps rule
    #: below does not catch it: the title reads "MORNING REPORT, 10 November
    #: 2026" and the month name is mixed case, so it failed the section-title
    #: test and was marked on the first run of this function. The first
    #: non-blank line of the file is the title by construction.
    _first_nonblank = next((i for i, ln in enumerate(lines) if ln.strip()), None)

    marked, at_start = 0, True
    for i, ln in enumerate(lines):
        stripped = ln.strip()
        if not stripped:
            at_start = True
            continue
        if not at_start:
            continue
        at_start = False
        if i == _first_nonblank:
            continue
        if i in quoted:
            continue
        #: A RECORDED HEADING, not a guessed one. See the docstring.
        if i in _headings:
            continue
        if stripped[0] in "*#-":
            continue
        #: A LIST MARKER OR A TIMESTAMP, not every numeral. See
        #: `refine_the_digit_rule` in the 2026-11-10 apply script:
        #: `no-word-numbers` requires my sentences to OPEN with a
        #: digit, so skipping every digit-initial line left my own
        #: prose unmarked in the real report.
        if _LIST_OR_STAMP.match(stripped):
            continue
        if _is_section_title(stripped):
            continue
        #: A DIGIT-INITIAL LINE PASSES HERE TOO. Without this the
        #: list-marker refinement above is inert, because this gate
        #: rejected every numeral the other one admitted.
        if not (stripped[0].isalpha() or stripped[0].isdigit()):
            continue
        lines[i] = "*" + ln
        marked += 1
    return marked


def render_tts(decs, outstanding, done, owed, parked, since, superseded=(),
               detail: bool = True, exempt_out=None) -> str:
    """The spoken report. `detail=False` drops the per-decision argument.

    ★ HIS COMPLAINT OF 2026-11-08 HAS 2 HALVES AND THIS IS THE SECOND. He was
    sent 2 files that morning, 22,555 and 22,505 words, and 0.690653 of this
    report's 12-word sequences also appear in the decisions file -- because
    this renderer and `scripts/build_decisions_file_2026-11-07.py` each render
    all 29 decisions in full, from the same authored detail. Shortening 1 file
    alone would have left him the same text under another name. Measured by
    `scripts/what_his_twenty_nine_rulings_actually_say_2026-11-08.py`.

    SO SECTION 1 BECOMES A COUNT AND A POINTER IN THE COPY HE READS. The
    markdown report in the repository is UNCHANGED and still carries every
    section, which matters because the verbatim-region markers pinned by
    `bench/tests/test_the_report_structure_is_pinned_2026-11-03.py` are emitted
    by `render_md` and not by this function -- checked before the edit, because
    that guard exists for a repair which removed an opening marker and left its
    close behind.
    """
    L = []
    A = L.append
    #: ★ QUOTED SPANS, RECORDED FOR THE LINT RATHER THAN MARKED IN THE FILE.
    #: His ruling for B96 is that genuinely quoted material be exempt in the
    #: spoken copy as it already is in the written one, and then that it be done
    #: the way that honours his TTS standard too: `render_md` carries literal
    #: `verbatim-begin` HTML comments, and putting those in a file he LISTENS to
    #: is forbidden by that standard in its own words. This generator already
    #: lints both copies immediately after writing them, so it records the spans
    #: by LINE INDEX here and converts them to character offsets at the end --
    #: exact, rather than matched by text, and 0 bytes of what he hears change.
    _ex: list = []
    #: ★ HEADING LINES, RECORDED WHERE THEY ARE EMITTED (B105). `L` is
    #: append-only in this function, so an index taken before an append
    #: stays correct for the life of the list.
    _hd: list = []
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
    # ★ BOTH NUMBERS, NEVER JUST ONE. The summary said "25 parked items" while
    # section 5 was headed "PARKED, 14 ITEMS", so the report disagreed with
    # itself and the reduction -- which is the whole of his 2026-11-01 `pf` --
    # was never stated. Saying only 14 would hide that 25 headings exist; saying
    # only 25 misdescribes what follows. Both, with the reason.
    _pp = parked_presentation(parked, outstanding)
    _live_n, _settled_n = len(_pp["live"]), _pp["settled_count"]
    _dupe_n = len(parked) - _live_n - _settled_n
    _parked_clause = (
      f"{len(parked)} parked headings, presented below as {_live_n} items")
    if _settled_n or _dupe_n > 0:
        _parts = []
        if _settled_n:
            _parts.append(f"{_settled_n} that say in their own text they are settled")
        if _dupe_n > 0:
            _parts.append(f"{_dupe_n} that restate another heading or share a subject")
        _parked_clause += " after counting rather than listing " + " and ".join(_parts)
    A(f"There are {len(decs)} decisions needing an answer, {len(outstanding)} pieces of "
      f"outstanding work already ruled on, {len(done)} commits this session, "
      f"{len(owed)} explanations owed, and {_parked_clause}.")
    A("")
    A("SECTION 1. DECISIONS THAT NEED AN ANSWER")
    A("")
    if not detail:
        A(_spoken(
            f"{len(decs)} decisions need an answer and each is listed, with its "
            f"recommendation, in the decisions file of the same date. They are not "
            f"repeated here: this report and that file were rendering the same 29 "
            f"arguments in full, which is why 2 files of about 22,500 words each "
            f"reached you on the 8th of November. Section 2 onward is this "
            f"report's own."))
        A("")
    # SKIPPED BY ITS ITERABLE rather than by re-indenting the block under an
    # `if`: simplest sufficient, and a diff a reader can check.
    for i, d in enumerate(decs if detail else [], 1):
        _hd.append(len(L))
        A(f"DECISION {i}. {_spoken(d.get('title') or d['ident'])}")
        A("")
        A("What it is. " + _spoken(d.get("what", d.get("headline", ""))))
        A("")
        A("Why it needs a decision. " + _spoken(d.get("why", "")))
        A("")
        if d.get("options"):
            _hd.append(len(L))
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
    _s = len(L)                      # git commit subjects, as committed
    for _h, when, subj in done:
        A(f"{when}. {_spoken(subj)}")
    _ex.append((_s, len(L)))
    A("")
    A("SECTION 3. OUTSTANDING WORK THAT NEEDS NO DECISION")
    A("")
    A("Each of these already carries a ruling on the record, so it is queued work rather "
      "than a question.")
    A("")
    _s = len(L)                      # task-list headlines, as the markers carry them
    for o in outstanding:
        A(_spoken(o.get("title") or o["ident"]) + ".")
        A("")
        # Spoken aloud, so he hears that he already settled it and on what date.
        if o.get("ruled"):
            A(f"You ruled on this on {o['ruled']}. The work is outstanding, "
              f"not the decision.")
            A("")
        #: ★ THE RECORDED STATUS IS SPOKEN TOO, 2026-11-08. The written copy
        #: gained this earlier the same day and this loop did not, so the
        #: written report carried 7 status lines while the spoken one carried
        #: 0 -- and the spoken file is the one he actually reads. A fix applied
        #: to 1 of 2 renderers is not applied. Normalised rather than copied,
        #: because this file forbids markdown and backticks, and the withheld
        #: amount is SAID rather than shown in parentheses.
        _sst = str(o.get("status") or "").strip()
        if _sst and str(o.get("source", "")).startswith("programme of study"):
            _sshown = _sst[:200]
            _srest = len(_sst) - len(_sshown)
            A("")
            A("Recorded status: " + _spoken(_sshown)
              + (f" A further {_srest} characters are recorded in the study "
                 f"record." if _srest > 0 else ""))
        A("")
        A(_spoken(o.get("what", o.get("headline", ""))))
        if o.get("why"):
            A("")
            A(_spoken(o["why"]))
        A("")
    _ex.append((_s, len(L)))         # closes the task-list headline span
    A(f"SECTION 4. EXPLANATIONS OWED, {len(owed)} OF THEM")
    A("")
    A("Each of these is a place where an explanation was asked for before a ruling would "
      "be given, and the explanation was never delivered. These are answers owed rather "
      "than work owed.")
    A("")
    _s = len(L)                      # the founder's own words
    for q in owed:
        A(f"{q['date']}. {_spoken(_first_sentence(q['text']))}")
    _ex.append((_s, len(L)))
    A("")
    if superseded:
        A(f"And {len(superseded)} of them are discounted as no longer relevant, on his "
          f"question of whether these are still relevant. Each is discounted against the "
          f"record rather than by judgement.")
        A("")
        _s = len(L)                  # the discounting record, quoted
        for r in superseded:
            A(f"{r['date']}. {_spoken(r['subject'])}.")
            A("")
            A(_spoken(r["why"]))
            A("")
            A("What remains. " + _spoken(r["what_remains"]))
            A("")
        _ex.append((_s, len(L)))
    # ★ HIS `pf`, 2026-11-01, same routing as the markdown above so the 2
    # renderings cannot disagree about what is outstanding.
    _pres = parked_presentation(parked, outstanding)
    _plive = _pres["live"]
    A(f"SECTION 5. PARKED, {len(_plive)} ITEMS")
    A("")
    A("These were judged not to block progress and appended rather than raised at the "
      "time. They are queued, not dropped.")
    if _pres["settled_count"] or _pres["duplicate_count"]:
        A("")
        _n_c, _n_d = _pres["settled_count"], _pres["duplicate_count"]
        _say_c = ("1 of them says" if _n_c == 1 else f"{_n_c} of them say")
        _say_d = ("1 says" if _n_d == 1 else f"{_n_d} say")
        A(f"{len(parked)} notes reduce to {len(_plive)} items. "
          f"{_say_c} in their own words that they are finished, and "
          f"{_say_d} they restate another item, so both are counted here rather "
          f"than read out again. Nothing has been removed from the parked file "
          f"itself.")
    A("")
    for it in _plive:
        # SENTENCES, NOT A RUN-ON. He reads these aloud, so the subject gets its
        # own sentence and each qualifier gets another, rather than being
        # comma-spliced onto a heading that is already a full sentence.
        subj = _spoken(it["subject"]).rstrip(".").strip()
        if subj:
            subj = subj[0].upper() + subj[1:]
        A(subj + ".")
        if it["seen_in"] > 1:
            A(f"This has accumulated over {it['seen_in']} separate notes, which is "
              f"why it kept reappearing.")
        if it.get("ruled"):
            A(f"You ruled on this on {it['ruled']}, so what is left is work rather "
              f"than a decision.")
    A("")
    A("")
    _hd.append(len(L))
    A(f"Written under CDSFL note standard {CURRENT_NOTE_STANDARD}.")
    # ★ B105, HIS RULING OF 2026-11-08. Marked BEFORE the offset conversion
    # below, because that conversion measures `L` itself.
    _marked = _mark_my_paragraphs(L, _ex, _hd)
    if exempt_out is not None:
        # Line index -> character offset, using the SAME join this returns, so
        # the offsets cannot drift from the text they describe.
        _starts, _off = [], 0
        for _ln in L:
            _starts.append(_off)
            _off += len(_ln) + 1
        _starts.append(_off)
        for _a, _b in _ex:
            if _b > _a:
                exempt_out.append((_starts[_a], _starts[_b]))
    return "\n".join(L) + "\n"


#: ★ B132, 2026-11-06. THE IDENTIFIER THE STORE ALREADY ISSUED, PRINTED.
#: His 3 stated purposes for the hash are duplicate detection, tying a verdict of
#: his to the issue it addresses, and giving researchers and agents a surface on
#: which to see emerging issues. None of them is served by an identifier that
#: never leaves the store. This reads the committed store and returns nothing
#: when no ticket exists, so it can never invent one.
#: ANNOTATED WITH THE BUILT-IN, because this module imports no typing
#: names and `Dict` would have raised at import. Caught by the patch
#: refusing on a missing anchor rather than by the module failing.
_TICKET_IDS: dict[str, str] = {}


def ticket_id(ident: str) -> str:
    """The newest ticket identifier for a task-list entry, or the empty string."""
    if not _TICKET_IDS:
        import json as _json
        path = REPO / "bench" / "tickets" / "tickets.jsonl"
        if not path.is_file():
            _TICKET_IDS["__loaded__"] = ""
            return ""
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                row = _json.loads(line)
            except Exception:                                  # noqa: BLE001
                continue
            ref = str(row.get("task_ref") or "").split(":")[-1].strip()
            tid = str(row.get("tid") or "").strip()
            if ref and tid:
                #: LAST WINS, because the store is append-only and the newest
                #: row is the current state of that ticket.
                _TICKET_IDS[ref] = tid
        _TICKET_IDS["__loaded__"] = ""
    return _TICKET_IDS.get(str(ident).strip(), "")


def ticket_tag(ident: str) -> str:
    """` [tid]` for rendering, or the empty string when no ticket exists."""
    t = ticket_id(ident)
    return f" `[{t}]`" if t else ""


def _bare_ident(key: str) -> str:
    """The identifier inside a derived item's STORE KEY.

    ★ WHY THIS EXISTS, 2026-11-08. A derived item's `key` is a store key of the
    form `task:B20` or `defect:<slug>`, and `ticket_id` wants the BARE
    identifier. Measured: `ticket_id("B20")` returns `a7e64483f941` while
    `ticket_id("task:B20")` returns "". Asking with the store key reported 48 of
    48 items as carrying no ticket, and a refusal built on that reading would
    have refused every item and withheld his morning report. This is the defect
    the project recorded as "a store key is not an identifier" the day before,
    where the same confusion mislabelled 3 live entries as repeats.
    """
    return key.split(":", 1)[1] if ":" in key else key


#: The sources whose items the ticket store issues an id FOR. A study defect
#: read from STUDY_IN_FLIGHT.json is not a ticket and never had one, so
#: demanding an id for it would refuse 8 items today for no fault.
_TICKETED_SOURCES = ("task:",)

#: ★ EVERY PREFIX MUST BE KNOWN, so an exemption is a DECISION and never an
#: accident. The scope test below is a `startswith`, which means a key with an
#: unrecognised prefix -- or none at all -- would be skipped silently and its
#: missing ticket id would never be reported. Measured 2026-11-08: the derived
#: population is 40 `task:` and 8 `defect:` with 0 un-prefixed, so this is
#: latent rather than live. It is written anyway because "0 un-prefixed keys"
#: is only reassuring while something is counting them, and a 0 nobody counts
#: is the shape this project records as asking what a 0 is a 0 OF.
_KNOWN_SOURCES = ("task:", "defect:")


def items_missing_a_ticket_id(items: list[dict]) -> list[str]:
    """Derived items that SHOULD carry a ticket id and do not.

    B132's postcondition. `ticket_tag` renders the empty string when no ticket
    exists, so without this an item reaches him with no id and nothing says so
    -- and B132's own words are that "a postcondition cannot be forgotten, and
    a resolution to remember can".
    """
    out, unclassified = [], []
    for i in items:
        key = i.get("key") or ""
        if not key:
            continue
        if not key.startswith(_KNOWN_SOURCES):
            #: NOT silently exempt. An unrecognised source is reported, so a
            #: new item shape cannot slip past the requirement by accident.
            unclassified.append(key)
            continue
        if not key.startswith(_TICKETED_SOURCES):
            continue
        if not ticket_id(_bare_ident(key)):
            out.append(key)
    return out + [f"{k} (UNCLASSIFIED SOURCE: it carries no known prefix, so "
                  f"nothing decided whether it owes a ticket id)"
                  for k in unclassified]


#: Paths an authored evidence line may cite as the producer of its figures.
#: Anchored to the 2 directories this repository keeps executable code in, so
#: a prose mention of a `.py` name in passing is not mistaken for a citation.
_CITED_PRODUCER = re.compile(r"((?:scripts|bench)/[A-Za-z0-9_./-]+\.py)")


def decisions_citing_no_resolvable_producer(
        detail: dict, root: pathlib.Path = REPO) -> list[str]:
    """Authored items that cite producers where NOT ONE of them resolves.

    ★ WHAT THIS CATCHES, WITH A LIVE REPRODUCTION. Entry B102's authored
    evidence line was, in full, `Producer:
    scripts/his_words_arrive_where_nothing_looks_2026-11-03.py` -- a file that
    has NEVER existed here, which `git log --all` confirms by returning 0
    commits for the path. So its figure, 206 of his 1,421 distinct messages,
    reached his morning deliverable with no reproducible route. That is
    `measured-rate-travels-with-its-script` violated inside the document the
    rule exists to protect, and it stood from 2026-11-03 to 2026-11-08 because
    NOTHING checked it: of the guards reading this data, the only one touching
    a field named `evidence_line` reads an unrelated tuple of line numbers.

    AT LEAST ONE, NOT ALL, and that is deliberate. A repair should NAME the
    phantom it replaced so the record shows what was wrong -- B102's corrected
    line does exactly that. Under an ALL rule, writing that history down would
    itself fail this check, so the check would punish the honest repair. The
    same ANY-versus-ALL question is open for the task list's `evidence:` field
    as `qs:65a5b902ff02`; here a concrete requirement settles it.

    CONDITIONAL on a path being cited at all. 22 of 48 authored items cite no
    producer and whether they should is a SEPARATE question; a check that
    conflated the 2 would fire 22 times on its first run and be switched off.

    AND IT IS NOT AN OVERLAP CHECK, which was measured and rejected. 5 of 15
    task-keyed items name no artefact in common with their task-list evidence
    field, but 4 of those 5 are citing different KINDS of artefact on purpose
    -- a producer against a defect location, a guard, a panel log. Only 1 cites
    something absent. An overlap rule would have fired 5 times with 4 false
    positives, which is the guard-accuses-correct-code failure this project has
    measured at 9 of 36.
    """
    out: list[str] = []
    for key, v in detail.items():
        if key.startswith("_") or not isinstance(v, dict):
            continue
        cited = _CITED_PRODUCER.findall(str(v.get("evidence_line", "")))
        if not cited:
            continue
        if not any((root / c).is_file() for c in cited):
            out.append(f"{key}: cites {len(cited)} producer(s) and none "
                       f"resolve: {cited}")
    return out


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

    #: ★ B132's POSTCONDITION, 2026-11-08. Scoped to the sources the store
    #: issues ids for, and the exclusion is said aloud rather than assumed.
    _no_tid = items_missing_a_ticket_id(items)
    if _no_tid:
        print("REFUSED — a derived item would be listed with no ticket id.")
        for k in _no_tid:
            print(f"  NO TICKET ID for {k}: raise it through the ticket store, "
                  f"or the reader meets a code with nowhere to look it up")
        print(f"  (study defects are exempt: the store issues no id for them. "
              f"{len([i for i in items if not (i.get('key') or '').startswith(_TICKETED_SOURCES)])} "
              f"of {len(items)} derived items are in that class.)")
        return 3

    #: ★ B102's POSTCONDITION, 2026-11-08. A figure whose producer does not
    #: resolve is a claim about evidence rather than evidence. Refusing is
    #: right here and reporting would not be: unlike a prose finding, which
    #: needs generated speech rewritten and so must never withhold his
    #: deliverable, a phantom citation has an obvious repair -- name the real
    #: producer, or drop the claim. Checked before wiring: nothing automated
    #: calls `--write`, so this surfaces to an author and cannot silently cost
    #: him a report.
    _no_prod = decisions_citing_no_resolvable_producer(
        json.loads(DETAIL.read_text(encoding="utf-8")) if DETAIL.is_file() else {})
    if _no_prod:
        print("REFUSED — an authored figure cites a producer that does not resolve.")
        for line in _no_prod:
            print(f"  {line}")
        print("  Name a producer that exists, or say the figure is unmeasured. "
              "A measured rate may be cited only with the script that made it.")
        return 3
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

    # ★ A SETTLED TICKET IS NOT A DECISION -- his instruction of 2026-11-01.
    # Both halves are required: the register says settled AND the entry asks
    # nothing live. See the long note on `settled_in_the_register` above for why
    # the second half is not optional.
    _closed = []
    for d in list(decs):
        ident = d.get("ident")
        if not ident:
            continue
        is_settled, why = settled_in_the_register(ident)
        if is_settled and not still_asks(ident):
            d["no_ruling_needed"] = f"settled in the register — {why}"
            _closed.append(d)
    if _closed:
        decs = [d for d in decs if d not in _closed]
        outstanding += _closed

    # ★ AND A DEPENDANT IS NOT A DECISION. Answering the parent releases it, so
    # it is WORK WAITING ON AN ANSWER rather than a question of its own.
    _dependent = []
    for d in list(decs):
        parent = depends_on_another_entry(d.get("ident") or "")
        if parent and parent in {x.get("ident") for x in decs}:
            d["no_ruling_needed"] = (
                f"waits on {parent}'s decision by its own text — answering "
                f"{parent} releases it")
            _dependent.append(d)
    if _dependent:
        decs = [d for d in decs if d not in _dependent]
        outstanding += _dependent

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
    # ★ AND ONLY WHILE THE ENTRY HAS STOPPED ASKING. Corrected 2026-11-01.
    # This was the OPERATIVE suppression of the 3 that existed, and it moved an
    # item out on ANY ruling date. The role-layer entry carries a ruling of
    # 2026-10-17 and 4 questions raised on 2026-10-30, 2026-10-31 and
    # 2026-11-01; all 4 left the decision list here. A question raised AFTER a
    # ruling cannot have been answered by it.
    #
    # 3 PLACES SUPPRESSED ON A RULING DATE and 1 of them was DATA: this filter,
    # the `ruled` branch in `decisions()`, and a hardcoded `no_ruling_needed:
    # true` in the authored detail written when the ruling was recorded and
    # never revisited. Fixing 1 would have left the other 2 biting, which is why
    # all 3 are named here.
    # ★ AN ENTRY HE DEFERRED HIMSELF IS NEVER A DECISION. Added 2026-11-01.
    # DEFERRED is the state this list uses for an item HE took off the queue,
    # and the zero-plant control is the case: he deferred it on 2026-10-30 with
    # *"You keep asking me about this and I keep giving you the same answer"*
    # and it is TO STOP SURFACING. The date-aware test alone put it back,
    # because the entry has dated additions from 2026-11-01 — the stage it was
    # finally given on the runway. Work done on a deferred item is not a new
    # question about it.
    _deferred = [d for d in decs if (d.get("state") or "").upper() == "DEFERRED"]
    for d in _deferred:
        d["no_ruling_needed"] = (
            f"you deferred this on {d.get('ruled') or 'an earlier date'}; it is "
            f"off the queue by your own ruling")
    if _deferred:
        outstanding += _deferred
        decs = [d for d in decs if d not in _deferred]

    ruled_now = [d for d in decs
                 if d.get("ruled")
                 and not ruling_is_spent(d.get("ident") or "", d.get("ruled"),
                                         d.get("state"))]
    outstanding += ruled_now
    decs = [d for d in decs if d not in ruled_now]

    owed, superseded = explanations_owed()
    parked = parked_items()
    done = work_done(args.since)
    md = render_md(decs, outstanding, done, owed, parked, args.since, superseded)

    #: ★ THE COPY HE READS DROPS THE DECISION DETAIL, on his complaint of
    #: 2026-11-08. The markdown in the repository keeps every section.
    #: ★ THE SPOKEN COPY'S QUOTED SPANS, carried OUT OF BAND on his ruling for
    #: B96. The written copy marks them with `verbatim-begin` comments; a file
    #: he LISTENS to may not carry markup, so the renderer records the spans and
    #: the self-lint below is given them instead. Same exemption, 0 bytes of
    #: difference in what he hears.
    _tts_exempt: list = []
    tts = render_tts(decs, outstanding, done, owed, parked, args.since,
                     superseded, detail=False, exempt_out=_tts_exempt)
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
        # ★ LINT WHAT WAS JUST WRITTEN, added 2026-11-03. Rule 27 binds section 1
        # because its text comes from `data/morning_report_decisions.json`, which
        # this project authors -- the comment at `_VB` above says so and declines
        # to wrap it in a verbatim region for exactly that reason. Nothing was
        # checking it: the report is gitignored so the pre-commit note ratchet
        # never sees it, and the test that would catch it is not on the board.
        # Putting that test on the board would make its verdict depend on an
        # untracked file existing, so the check belongs HERE, where the file is
        # made. It REPORTS and never refuses: withholding his morning report over
        # a prose finding would cost him the thing he needs.
        try:
            from note_vagueness_lint import blocking as _blocking
            for _f, _sp in ((out, None), (desk, _tts_exempt)):
                # The markdown carries its own markers; the spoken copy's spans
                # arrive here instead, for the reason recorded at `_tts_exempt`.
                _hits = _blocking(_f, _sp)
                if _hits:
                    print(f"  NOTE-STANDARD: {len(_hits)} blocking finding(s) in "
                          f"{_f.name} -- read before delivering")
                    for _h in _hits[:6]:
                        print(f"      para {_h[0]}  {_h[1]}  {_h[2]!r}")
                    if len(_hits) > 6:
                        print(f"      ... and {len(_hits) - 6} more")
                else:
                    print(f"  NOTE-STANDARD: {_f.name} is clean")
        except Exception as _lx:                               # noqa: BLE001
            # A lint failure must never cost him the report, but it must not pass
            # silently either -- a swallowed exception is not a record.
            print(f"  NOTE-STANDARD: the lint could not run "
                  f"({type(_lx).__name__}: {str(_lx)[:120]}). The report IS "
                  f"written; its compliance is UNCHECKED, not clean.")
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
