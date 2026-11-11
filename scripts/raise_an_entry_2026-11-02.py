#!/usr/bin/env python3
"""Check a NEW task-list entry across every surface it must reach, or name what is missing.

★ WHY THIS EXISTS, AND THE COST IS MEASURED RATHER THAN ASSERTED. On 2026-11-02,
**8 of 13 completed commit attempts were REFUSED -- 0.615385, Wilson 95%
[0.355229, 0.822903], Clopper-Pearson [0.315778, 0.861421]** -- and 3 of those
refusals were the same fault: an entry raised on the task list without the other
surfaces an entry must reach. Attempt 19 and attempt 20 died because 4 entries
had no authored detail, so the morning report could not report them to him.
Attempt 21 died because 6 entries had no register ticket. A 4th was caught only
because a guard was run by hand before committing.

`scripts/close_an_entry_2026-11-02.py` already exists for the INVERSE operation
and records the same history on the closing side: *"3 COMMIT REFUSALS IN ONE DAY,
ALL THE SAME GUARD, ALL MINE ... I touched 1 or 2 of the 3 on every attempt."*
**This is its symmetric half**, and the asymmetry is what cost the refusals:
closing was mechanised and raising was not.

WHAT AN ENTRY MUST REACH, derived from what actually refused rather than from a
design. Each check names the guard that enforces it, so this tool cannot drift
from the gate:

  1. THE MARKER PARSES                `test_task_list_markers_2026-09-09.py`
  2. THE HARVESTER DERIVES A ROW      `test_ticket_harvest_2026-10-17.py`
  3. THE REGISTER TICKET EXISTS,      `test_a_ticket_identity_survives_a_reword
     with terminality matching         _2026-10-17.py`
     the marker
  4. AUTHORED DETAIL, for a live      `test_a_settled_item_is_not_a_decision
     entry the generator derives       _2026-11-01.py`
  5. THE 2 DECISION SURFACES AGREE    `test_the_two_decision_surfaces_cannot
                                       _diverge_2026-11-01.py`
  6. THE SPOKEN MIRRORS ARE           measured on the 2026-10-30 and 2026-11-01
     BYTE-IDENTICAL                    pairs, which are identical; today's
                                       diverged at char 52,550 within the hour
  7. THE ENTRY-TEXT PRODUCER           `test_a_settled_item_is_not_a_decision
     AGREES IT IS A DECISION,          _2026-11-01.py`
     where the generator renders it

IT CHECKS AND REFUSES; IT DOES NOT WRITE. Raising an entry means writing prose
only he should read, and a tool that generates that prose would be writing his
decision aid for him. What this removes is the step held in my memory -- which
surface did I forget -- and the project's standing rule is that a step held in
the author's memory is not a mechanism.

EVERY CHECK CALLS THE AUTHORITATIVE INSTRUMENT RATHER THAN COPYING ITS RULE, by
`execute-do-not-grep`: checks 4 and 5 run the generator and the agreement
producer as subprocesses and read their exit codes, so neither can drift from
what the gate runs.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import importlib.util
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
DETAIL = REPO / "experimental_notes" / "data" / "morning_report_decisions.json"
TERMINAL = {"CLOSED", "WITHDRAWN", "REJECTED", "DEPRECATED", "INVALID"}


def _load(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _spoken_pair() -> tuple[pathlib.Path | None, pathlib.Path | None]:
    repo = sorted((REPO / "experimental_notes").glob("Decisions_Awaiting_You_*.txt"))
    desk = sorted((pathlib.Path.home() / "Desktop" / "CDSFL_tts")
                  .glob("Decisions_Awaiting_You_*.txt"))
    return (repo[-1] if repo else None), (desk[-1] if desk else None)


def check(ident: str) -> list[tuple[str, bool, str]]:
    out: list[tuple[str, bool, str]] = []
    sys.path.insert(0, str(REPO / "scripts"))
    sys.path.insert(0, str(REPO / "bench"))

    # 1 -- the marker parses
    T = _load(REPO / "scripts" / "task_list_markers.py", "_tlm")
    ents = {e.ident: e for e in T.parse_entries(LIST)}
    e = ents.get(ident)
    out.append(("1. the marker parses", e is not None,
                f"state={getattr(e, 'state', None)} status={getattr(e, 'status', None)}"
                if e else f"no entry {ident} on the list"))
    if e is None:
        return out

    # 2 -- the harvester derives a row, which is what gives the ticket its identity
    H = _load(REPO / "scripts" / "harvest_tickets_2026-10-17.py", "_hrv")
    rows = {r["task_ref"]: r for r in H.from_task_list() if r.get("task_ref")}
    r = rows.get(ident)
    out.append(("2. the harvester derives a row", r is not None,
                f"kind={r['kind']} verbatim={r['verbatim'][:48]!r}" if r
                else "the entry's text yields no harvestable row"))

    # 3 -- the register ticket, at the DERIVED identity, with matching terminality
    if r is not None:
        from ticket_store import TicketStore, tid_of          # noqa: E402
        t = TicketStore().get(tid_of(r["kind"], r["verbatim"], ident))
        done = e.state in ("DONE", "WITHDRAWN")
        if t is None:
            out.append(("3. the register ticket exists", False,
                        "no ticket at the derived identity; run "
                        "scripts/harvest_tickets_2026-10-17.py --sources task_list"))
        else:
            agree = (t.status in TERMINAL) == done
            out.append(("3. the register ticket exists", agree,
                        f"tid={t.tid} status={t.status} vs marker {e.state}"
                        + ("" if agree else "  <-- they disagree")))

    # 4 -- authored detail, via the GENERATOR'S OWN check rather than a copy of it
    rc = subprocess.run([sys.executable,
                         str(REPO / "scripts" / "morning_report_build_2026-10-12.py"),
                         "--check"], capture_output=True, text=True, cwd=str(REPO))
    out.append(("4. every derived item has authored detail", rc.returncode == 0,
                (rc.stdout or rc.stderr).strip().splitlines()[-1][:110]
                if (rc.stdout or rc.stderr).strip() else f"exit {rc.returncode}"))

    # 5 -- the 2 decision surfaces agree, by the producer the gate runs
    rc = subprocess.run([sys.executable, str(REPO / "scripts" /
                         "do_the_two_decision_surfaces_agree_2026-11-01.py")],
                        capture_output=True, text=True, cwd=str(REPO))
    tail = [l.strip() for l in (rc.stdout or "").splitlines() if l.strip()]
    out.append(("5. the 2 decision surfaces agree", rc.returncode == 0,
                tail[-1][:110] if tail else f"exit {rc.returncode}"))

    # 6 -- the spoken mirrors
    repo_txt, desk_txt = _spoken_pair()
    if repo_txt is None or desk_txt is None:
        out.append(("6. the spoken mirrors are byte-identical", False,
                    f"repo={repo_txt} desktop={desk_txt}"))
    else:
        # ★ SAME DECISIONS, NOT SAME BYTES. Corrected 2026-11-09, because
        # byte-identity became the WRONG invariant on his own ruling. He
        # objected on 2026-11-08 that the file he was handed ran to over 22,000
        # words -- "an almost impossible workload" -- so the copy he reads is
        # now the INDEX and the repo copy keeps the full render. Measured at
        # the time: 8,031 characters against 130,243. A sha256 comparison
        # therefore reported a divergence that his instruction created, and
        # repairing the files to satisfy it would have undone what he asked
        # for -- a guard accusing correct work.
        #
        # WHAT STILL MUST HOLD, and it is the property that was always the
        # point: the 2 copies must name the SAME DECISIONS. He must never be
        # handed a shorter file that also asks him about a DIFFERENT set. The
        # detail may differ; the question set may not.
        import re as _re
        #: ★ THE ENTRY CODE IS THE MARKER, not the numbering. A first version
        #: matched any `N. text` line and found 58 in the repo render against
        #: 13 in his copy -- because the full render NUMBERS THE OPTIONS inside
        #: each decision, so the pattern counted options as headings. The index
        #: lines themselves were byte-identical for all 13. Matching the
        #: explicit code is the recorded lesson that a marker and a fixed shape
        #: beat an inferred one.
        _H = _re.compile(r"^\s*(\d+)\.\s+((?:B|C|R)\d+\b.*?)\s*$", _re.M)

        #: ★ COMPARE THE CODE AND THE HEADING, NOT THE RECOMMENDATION PROSE --
        #: 2026-11-11. The whole index line was compared until today, and that
        #: worked only while BOTH renders truncated the recommendation at the
        #: same 150 characters. On 2026-11-11 he reported that his copy was cut
        #: mid-sentence 3 times in one file -- "I cannot give verdicts if I
        #: don't know what you are asking" -- so his copy is now rendered UNCUT
        #: while the repo index stays capped. The 2 renders then differ in the
        #: recommendation text by design, and this check reported a divergence
        #: that his own instruction created: a guard accusing correct work, the
        #: same fault the comment above this one already records once.
        #:
        #: THE PROPERTY IS UNCHANGED AND IS WHAT THE CHECK IS NAMED FOR: the 2
        #: copies must NAME THE SAME DECISIONS. A decision is named by its entry
        #: code and its heading, both of which are rendered identically in both
        #: files; what follows "RECOMMENDED OPTION" is the detail the check's
        #: own comment says "may differ". Cutting at that LITERAL MARKER rather
        #: than at an inferred sentence boundary is the recorded lesson that an
        #: explicit marker beats a shape.
        #:
        #: THIS DOES NOT WEAKEN THE CHECK. A decision present in one file and
        #: absent from the other still diverges, because the code is part of the
        #: key; so does a heading that differs by a single word.
        def _key(h: str) -> str:
            return h.upper().split("RECOMMENDED OPTION")[0].strip().rstrip(".").strip()

        _ra = {_key(h) for _n, h in
               _H.findall(repo_txt.read_text(encoding="utf-8", errors="replace"))}
        _db = {_key(h) for _n, h in
               _H.findall(desk_txt.read_text(encoding="utf-8", errors="replace"))}
        _only_repo = sorted(_ra - _db)
        _only_desk = sorted(_db - _ra)
        _same = not _only_repo and not _only_desk
        out.append(("6. the spoken mirrors name the same decisions", _same,
                    f"{repo_txt.name}: {len(_ra)} in the repo render, "
                    f"{len(_db)} in his copy"
                    + ("" if _same else
                       f"  <-- only in repo: {_only_repo[:2]}; "
                       f"only in his copy: {_only_desk[:2]}")))

    # ★ CHECK 7 WAS ADDED AFTER THIS TOOL PASSED AN ENTRY THE GATE THEN REFUSED
    # TWICE, 2026-11-02. Checks 4 and 5 cover the GENERATOR (authored detail
    # plus markers) and the SPOKEN surface. A 3RD decision instrument exists:
    # `how_many_decisions_actually_need_him_2026-11-01.py` derives the set from
    # each entry's OWN TEXT, and `test_a_settled_item_is_not_a_decision_2026-11-01.py`
    # asserts it names exactly what the generator renders. B88 reached all 6
    # surfaces above and was still refused, because its text described the
    # decision in prose instead of the project's `**NEEDS HIS RULING:**` form,
    # so the producer returned `kind=MINE` with no live ask.
    #
    # THIS IS THE SAME FAULT THE TOOL EXISTS TO CATCH, ONE LEVEL UP: a surface
    # COUNT chosen by me rather than enumerated from the record. See
    # `feedback_pin_a_set_not_a_count_2026-10-16`, 5th instance.
    #
    # IT IS CONDITIONAL, because only a DECISION must be classified OWED. An
    # entry carrying no authored detail is not a decision and is skipped with
    # the reason stated, rather than failed.
    try:
        import importlib.util
        prod_path = REPO / "scripts" / "how_many_decisions_actually_need_him_2026-11-01.py"
        spec = importlib.util.spec_from_file_location("_rae_decide", prod_path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["_rae_decide"] = mod
        spec.loader.exec_module(mod)
        rows = {r["ident"]: r for r in mod.classify()}
        # THE AUTHORITY ON "THIS IS A LIVE DECISION" IS THE GENERATOR'S RENDERED
        # SET, NOT THE PRESENCE OF AUTHORED DETAIL. A first version keyed on
        # authored detail and FAILED B20, which carries detail but no
        # `spoken_heading` and is rendered by nothing -- so it is not a decision
        # and must not be required to read as one. Found by running this check
        # on a 2nd entry rather than trusting it after 1 pass, which is the
        # discrimination control applied to my own tool.
        agree = REPO / "scripts" / "do_the_two_decision_surfaces_agree_2026-11-01.py"
        rendered: set = set()
        g = subprocess.run([sys.executable, str(agree)], capture_output=True,
                           text=True, cwd=str(REPO), timeout=600)
        blob = (g.stdout + g.stderr).split("generated report")[-1].split(
            "spoken file")[0]
        rendered = set(re.findall(r"^\s+([A-Z0-9]+)\s+->", blob, re.M))
        r = rows.get(ident)
        if ident not in rendered:
            out.append((
                "7. the entry-text producer agrees it is a decision", True,
                f"SKIPPED: the generator does not render {ident} as a decision, "
                f"so no agreement is owed"))
        elif r is None:
            out.append((
                "7. the entry-text producer agrees it is a decision", False,
                "the producer does not classify this entry at all"))
        else:
            ok = r.get("kind") == "OWED"
            asks = r.get("live_asks") or []
            out.append((
                "7. the entry-text producer agrees it is a decision", ok,
                f"kind={r.get('kind')} live_asks={len(asks)}"
                + ("" if ok else "  <-- its text carries no `**NEEDS HIS "
                                 "RULING:**` sentence, so the 3rd instrument "
                                 "and the generator will disagree")))
    except Exception as e:  # noqa: BLE001
        # A CHECK THAT CANNOT RUN IS A FAILURE, NOT A PASS. Swallowing this
        # would reproduce `feedback_a_swallowed_exception_is_not_a_record`.
        out.append(("7. the entry-text producer agrees it is a decision", False,
                    f"the check could not run: {type(e).__name__}: {e}"))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="raise_an_entry_2026-11-02.py",
        description="Check a new task-list entry across every surface it must "
                    "reach. Reads only and writes nothing.")
    ap.add_argument("--entry", required=True, help="the entry identifier, e.g. B87")
    a = ap.parse_args()

    rows = check(a.entry)
    print("=" * 74)
    print(f"DOES {a.entry} REACH EVERY SURFACE AN ENTRY MUST REACH?")
    print("=" * 74)
    for name, ok, detail in rows:
        print(f"  [{'OK  ' if ok else 'FAIL'}] {name}")
        print(f"         {detail}")
    bad = [n for n, ok, _ in rows if not ok]
    print()
    if bad:
        print(f"  REFUSED: {len(bad)} of {len(rows)} surface(s) not reached:")
        for n in bad:
            print(f"    {n}")
        print("  Each is a commit the gate would refuse. Fix them together: a")
        print("  commit that satisfies 1 surface and not another is the fault this")
        print("  tool exists to prevent, and it cost 3 refusals on 2026-11-02.")
        return 1
    print(f"  ALL {len(rows)} SURFACES REACHED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
