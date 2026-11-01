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
        A(f"- {_subj}{ref}{seen}")
        if it.get("ruled"):
            A(f"  You ruled on this on {it['ruled']}; what is left is work.")
    A("")
    A(_VE)
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
    A(f"Written under CDSFL note standard {CURRENT_NOTE_STANDARD}.")
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
