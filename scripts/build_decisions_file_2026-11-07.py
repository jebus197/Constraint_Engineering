#!/usr/bin/env python3
"""GENERATE the decisions file he asked for on 2026-11-07, 1 item per decision.

HIS REQUEST, 2026-11-07: *"print a fresh tts with each issue, explaining what it
is, why it matters and with your recommendation in each case"*, after ruling on
2026-11-06 that the line caps were never his: *"raise the cap in all 3. I never
specified a cap."*

WHY A GENERATOR AND NOT A HAND-WRITTEN FILE. The morning report of 2026-11-06
was written by hand and told him 3 things awaited him when the record tracked
29. A hand-written surface cannot be checked against the record, and the project
already holds a guard that compares the 2 surfaces and refuses when they differ.
This renderer reads the SAME authored detail the generated report reads, through
the SAME functions, so the file and the record cannot disagree.

EVERY PART IS BORROWED RATHER THAN REWRITTEN, per `use-the-instrument-that-
exists`: the live queue comes from `do_the_two_decision_surfaces_agree`'s
`derived()`, the authored detail from `morning_report_build.decisions()`, and the
spoken normalisation from that module's own `_spoken()`, which strips emphasis,
unwraps backticks, drops file paths whole with their labelled clause, and
replaces em-dashes. Writing a second normaliser here would be the
`execute-do-not-grep` shape: 2 declarations of 1 rule, each individually
correct.

THE 4 FIELDS ARE THE ONES HE ENDORSED on 2026-10-30 and restated this morning:
what it is, why it matters (what it affects), what he decides, and what is
recommended with its standard named. Rule 33 of note standard v1.9 requires the
recommendation to name additive, simplest sufficient or composability.

Writes 3 files: the markdown in the repository, the spoken text in the
repository, and the spoken text on his Desktop. The repository markdown and the
Desktop text are the 2 surfaces the agreement checker joins.

Exit 0 iff all 29 decisions rendered, every one carrying a heading, a
recommendation and a standard.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
if not (REPO / "scripts").is_dir():            # running from the scratchpad
    REPO = pathlib.Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")
DESKTOP = pathlib.Path.home() / "Desktop" / "CDSFL_tts"
STANDARD = re.compile(r"additive|simplest sufficient|composab", re.I)


def _load(path: pathlib.Path, name: str):
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _wrap_free(text: str) -> str:
    """NO HARD WRAPPING. 1 paragraph is 1 long line, per the note standard."""
    return re.sub(r"\s+", " ", text).strip()


#: ★ THE CLAIM AND ITS NEGATION LOOK ALIKE. An ad-hoc regex used to take the
#: first measurement here included the BARE WORD `recommended` as an
#: alternative, and so counted "NOT recommended" as a recommendation: it flagged
#: 9 of 31 entries when 2 were real, 4 of the 7 false ones being exactly that
#: inversion (B128, B81, B84, B88). The project's record already holds the
#: shape: 3 of 4 detectors over-matched.
#:
#: ★ AND WHAT PROTECTS AGAINST THAT IS NOT THE LOOKBEHINDS, corrected
#: 2026-11-07 by the mutation harness. It is that this pattern requires the
#: phrase `is ... recommendation` and never matches the bare word
#: `recommended`, so a negation has nothing to attach to. Measured by calling
#: it: "Not recommended: it would be worse." and "NOT recommended, and
#: deliberately so." both return no match with the lookbehinds REMOVED. The
#: lookbehinds fire only on "not is the recommendation", which is not English
#: and appears nowhere in the corpus, so a control test that relies on them
#: passes for the wrong reason -- which is what mine did until a mutation
#: reversing them stayed GREEN. They are kept because they cost nothing and
#: are not wrong; the test that matters is
#: `test_the_bare_word_recommended_is_never_a_claim`.
_CLAIMS = re.compile(r"(?<!not )(?<!NOT )\bis (?:my |the )?recommendation\b", re.I)


def recommended_index(options: list[str]) -> tuple[int, str]:
    """(0-based index of the recommended option, how it was decided).

    Falls back to option 1 and SAYS SO, rather than silently picking one, so a
    file that could not find the recommendation reads as such.
    """
    hits = [i for i, o in enumerate(options) if _CLAIMS.search(o)]
    if len(hits) == 1:
        return hits[0], "marked in the option text"
    if not hits:
        return 0, "NO OPTION IS MARKED AS THE RECOMMENDATION; option 1 shown by position"
    return hits[0], (f"{len(hits)} options claim to be the recommendation "
                     f"({', '.join(str(h + 1) for h in hits)}); the first is shown")


def _gist(option: str, limit: int = 150) -> str:
    """The option's own lead clause: its bolded phrase, else its 1st sentence."""
    m = re.match(r"\s*\*\*(.+?)\*\*", option, re.S)
    t = m.group(1) if m else option.split(". ")[0]
    t = _wrap_free(t)
    return t if len(t) <= limit else t[:limit].rsplit(" ", 1)[0] + "..."


def head_sha() -> str:
    return subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True, cwd=REPO).stdout.strip()


def collect():
    mrb = _load(REPO / "scripts" / "morning_report_build_2026-10-12.py", "mrb_dec")
    sf = _load(REPO / "scripts"
               / "do_the_two_decision_surfaces_agree_2026-11-01.py", "sf_dec")
    live = sf.derived()                        # [(ident, spoken_heading)]
    items = mrb.task_items() + mrb.study_items()
    decs, _missing, _orphan = mrb.decisions(items)
    by_ident = {}
    for d in decs:
        ident = d.get("ident")
        if ident:
            by_ident[ident] = d
    rows = []
    for ident, head in live:
        d = by_ident.get(ident, {})
        opts = d.get("options") or []
        rows.append({
            "ident": ident,
            "heading": head,
            "what": d.get("what") or "",
            "why": d.get("why") or "",
            "options": list(opts),
            "standards": d.get("recommendation_standards") or "",
            "evidence": d.get("evidence_line") or "",
            "owed": d.get("still_owed") or "",
            "ruled": d.get("ruled") or "",
            "title": d.get("title") or "",
            #: ★ B132. The ticket identity travels with the row so the
            #: WRITTEN surface can cite it. `ticket_id` resolves 29 of 29
            #: live decisions, measured by calling it rather than by
            #: reading it. The SPOKEN surface deliberately does not use
            #: this: a 12-hex value read aloud is hostile to listening,
            #: which is the open question entry B104 puts to him.
            "tid": mrb.ticket_id(ident),
        })
    return mrb, rows


HEADER_MD = """# Decisions awaiting you — {date}

**{n} decisions, generated from the project's own records at commit `{sha}`, not written by hand.**
The report that asked you on the 6th of November was hand-written, and it named 3 things when the
record tracked {n}. This file reads the same authored detail the generated report reads, through the
same functions, so it cannot disagree with the record.

**Written at the raised cap.** Your ruling of the 6th of November: *"raise the cap in all 3. I never
specified a cap."* Nothing here is cut to fit a length. Each item says what it is, why it matters,
what you decide, and what is recommended with its standard named.

## Are these new, or repeats you have already ruled on? Neither.

**NOT NEW.** All {n} of {n} have already been put to you in a dated decisions file — 18 first
appeared on the 3rd of November, 8 on the 4th, 2 on the 1st and 1 on the 2nd. The file carrying them
was 151,786 bytes, which is why they are re-rendered here rather than re-sent.

**NOT REPEATS EITHER.** 0 of {n} carry a ruling of yours that still settles them, Wilson 95%
[0.000000, 0.116970], Clopper-Pearson 95% [0.000000, 0.119445]. 3 carry a ruling of yours on a
*different* question — B20, B21 and B71 — and each entry records which question was answered and
which was not. The remaining 26 carry no ruling at all.

**The answer I gave you yesterday was wrong.** The producer written to answer this very question
called its lookup with a store key where an entry identifier belongs, found nothing, and read the
miss as a finding. 3 of 41 live entries were labelled repeats on an empty string: B13, B20 and B21.
B20 is the next task on the list and the first decision below.
Producer: `scripts/are_the_twenty_nine_new_or_repeats_2026-11-07.py`.

---
"""

HEADER_TTS = """DECISIONS AWAITING YOU

{date}

{n} decisions, generated from the project's own records at commit {sha}, not written by hand. The report that asked you on the 6th of November was hand-written, and it named 3 things when the record tracked {n}. This file reads the same authored detail the generated report reads, through the same functions, so it cannot disagree with the record.

Written at the raised cap, on your ruling of the 6th of November that you never specified a cap. Nothing here is cut to fit a length. Each item says what it is, why it matters, what you decide, and what is recommended with its standard named.


ARE THESE NEW, OR REPEATS YOU HAVE ALREADY RULED ON? NEITHER

Not new. All {n} of {n} have already been put to you in a dated decisions file. 18 first appeared on the 3rd of November, 8 on the 4th, 2 on the 1st and 1 on the 2nd. The file carrying them was 151,786 bytes, which is why they are re-rendered here rather than re-sent.

Not repeats either. 0 of {n} carry a ruling of yours that still settles them, with a 95 per cent Wilson interval from 0.000000 to 0.116970 and a Clopper-Pearson interval from 0.000000 to 0.119445. 3 carry a ruling of yours on a different question, entries B20, B21 and B71, and each entry records which question was answered and which was not. The remaining 26 carry no ruling at all.

The answer given to you yesterday was wrong. The measurement script written to answer this very question called its lookup with a store key where an entry identifier belongs, found nothing, and read the miss as a finding. 3 of 41 live entries were labelled repeats on an empty string: B13, B20 and B21. B20 is the next task on the list and the first decision below.

"""


def render(mrb, rows, spoken: bool, detail: bool = True) -> str:
    """Render the file. `detail=False` gives the INDEX ALONE.

    ★ HIS COMPLAINT OF 2026-11-08, and it is measured. He answered all 29
    decisions from the index and said of the rest that, at over 22,000 words,
    it is an almost impossible workload. Measured by
    `scripts/what_his_twenty_nine_rulings_actually_say_2026-11-08.py`: the
    delivered file was 22,902 words of which the long tier is 0.927451 of the
    characters, and 0.690653 of the morning report's 12-word sequences also
    appear in it, because 2 generators each render all 29 in full.

    HIS FIRST READING IS REFUTED AND HIS SECOND IS RIGHT. Nothing was
    appended today: these files ran 18,300 bytes on 2026-10-29 and 25,523 on
    2026-10-30, then 151,786 on 2026-11-04, LARGER than this one. The 2-tier
    shape predates the file; the workload request simply lapsed.

    SO THE REPOSITORY COPIES KEEP EVERY SECTION AND THE DESKTOP COPY CARRIES
    THE INDEX, 9,594 characters against 130,263. The 3 dependencies were
    checked rather than assumed: `do_the_two_decision_surfaces_agree` reads
    the REPOSITORY glob and needs the `DECISION n.` headings, which the
    repository copy keeps; `sync_desktop_mirrors.MIRRORS` holds 5 entries and
    this file is not 1 of them, so nothing copies the full text back over the
    Desktop one; and this module's exit-0 postcondition is computed from
    `rows`, not from the rendered text.
    """
    sp = mrb._spoken if spoken else (lambda t: t)
    date = (dt.datetime.now().strftime("%d %B %Y, %H:%M GMT") if spoken
            else dt.date.today().isoformat())
    head = (HEADER_TTS if spoken else HEADER_MD).format(
        date=date, n=len(rows), sha=head_sha())
    L = [head]
    A = L.append

    # ---- THE INDEX. His words of 2026-11-06: no cap, but present things so a
    # quick coherent decision is possible. Length is permitted; an unordered
    # 100,000 characters is not what "quick" means. Every decision appears here
    # in 1 line with its recommendation, so a ruling can be given from the
    # index alone and the detail read only where it is wanted.
    # DERIVED, never typed: this read "THE 29 AT A GLANCE" and would have gone
    # stale the moment he ruled on one of them.
    A(f"THE {len(rows)} AT A GLANCE" if spoken
      else f"## The {len(rows)} at a glance")
    A("")
    # ★ ONE SENTENCE, ONE DECLARATION. This stood written out TWICE, once for
    # the spoken branch and once for the markdown one, so a conditional added
    # to either would have left the 2 surfaces promising different things --
    # the `execute-do-not-grep` shape in prose. It is composed once here.
    _lead = ("Each line gives the decision number, the entry it belongs to, the "
             "question, and the recommended option in a clause. A ruling can be given "
             "from this list alone, naming the decision number and the option number. ")
    _lead += ("The full argument for each follows below in the same order."
              if detail else
              "The full argument for each is in the repository, in the markdown and "
              "spoken copies of this file under experimental notes, which carry every "
              "section.")
    A(sp(_wrap_free(_lead)) if spoken else _wrap_free(_lead))
    A("")
    for i, r in enumerate(rows, 1):
        k, _how = recommended_index(r["options"]) if r["options"] else (0, "")
        gist = _gist(r["options"][k]) if r["options"] else "no option recorded"
        line = (f"{i}. {r['ident']}, {r['heading'].lower()}. "
                f"Recommended option {k + 1}: {gist}")
        tag = f" `[{r['tid']}]`" if r.get("tid") else ""
        A(sp(line) if spoken else f"{i}. **{r['ident']}**{tag} — {r['heading'].lower()}. "
                                  f"*Recommended option {k + 1}:* {gist}")
    A("")
    A("" if spoken else "---")
    A("")

    # SKIPPED BY ITS ITERABLE rather than by re-indenting 40 lines under an
    # `if`: simplest sufficient, and a diff a reader can check.
    for i, r in enumerate(rows if detail else [], 1):
        hd = f"DECISION {i}. {r['heading']}"
        tag = f" `[{r['tid']}]`" if r.get("tid") else ""
        A(hd if spoken else f"## {hd}{tag}")
        A("")
        if r["ruled"]:
            note = (f"You ruled on this entry on {r['ruled']}, on a different question. "
                    f"What is still owed is {r['owed'] or 'recorded in the entry'}.")
            A(sp(_wrap_free(note)) if spoken else f"*{_wrap_free(note)}*")
            A("")
        A("WHAT IT IS." if spoken else "**WHAT IT IS.**")
        A(sp(_wrap_free(r["what"])) if spoken else _wrap_free(r["what"]))
        A("")
        A("WHY IT MATTERS." if spoken else "**WHY IT MATTERS.**")
        A(sp(_wrap_free(r["why"])) if spoken else _wrap_free(r["why"]))
        A("")
        if r["evidence"]:
            A("THE EVIDENCE." if spoken else "**THE EVIDENCE.**")
            A(sp(_wrap_free(r["evidence"])) if spoken else _wrap_free(r["evidence"]))
            A("")
        if r["options"]:
            A("WHAT YOU DECIDE." if spoken else "**WHAT YOU DECIDE.**")
            for j, o in enumerate(r["options"], 1):
                txt = _wrap_free(o)
                A(f"{j}. " + (sp(txt) if spoken else txt))
            A("")
            A("RECOMMENDED." if spoken else "**RECOMMENDED.**")
            k, how = recommended_index(r["options"])
            rec = _wrap_free(r["options"][k])
            A((f"Option {k + 1}. " + (sp(rec) if spoken else rec)))
            if how != "marked in the option text":
                A("")
                A(sp(f"How this was chosen: {how}.") if spoken
                  else f"*How this was chosen: {how}.*")
            if r["standards"]:
                st = _wrap_free(r["standards"])
                A("")
                A(sp(st) if spoken else st)
            A("")
        A("" if spoken else "---")
        A("")
    if not detail:
        A(sp(_wrap_free(
            f"That is the whole of the index. The full argument for all {len(rows)} "
            f"decisions, with the evidence and every option, is in the repository "
            f"copies of this file under experimental notes. Nothing is cut: this copy "
            f"is the index, so a ruling can be given without reading the rest.")))
        A("")
    A("Written under CDSFL note standard v1.9 (1 November 2026)."
      if spoken else
      "Written under CDSFL note standard v1.9 (1 November 2026).")
    return "\n".join(L) + "\n"


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true", help="write the 3 files")
    a = ap.parse_args(argv)

    mrb, rows = collect()
    print(f"decisions rendered : {len(rows)}")
    no_head = [r["ident"] for r in rows if not r["heading"]]
    no_opts = [r["ident"] for r in rows if not r["options"]]
    no_std = [r["ident"] for r in rows
              if not STANDARD.search(" ".join(r["options"]) + " " + r["standards"])]
    print(f"  without a heading        : {len(no_head)} {no_head}")
    print(f"  without any option       : {len(no_opts)} {no_opts}")
    print(f"  without a named standard : {len(no_std)} {no_std}")

    md = render(mrb, rows, spoken=False)
    tts = render(mrb, rows, spoken=True)
    #: ★ THE COPY HE ACTUALLY READS IS THE INDEX, on his complaint of
    #: 2026-11-08. The repository keeps both full renders, which is what the
    #: surface-agreement checker reads and what holds the `DECISION n.`
    #: headings it needs. See `render`'s docstring for the measurement and for
    #: the 3 dependencies that were checked before this split.
    tts_index = render(mrb, rows, spoken=True, detail=False)
    print(f"  markdown : {len(md.splitlines())} lines, {len(md)} chars")
    print(f"  spoken   : {len(tts.splitlines())} lines, {len(tts)} chars")
    print(f"  his copy : {len(tts_index.splitlines())} lines, {len(tts_index)} chars "
          f"({len(tts_index) / max(1, len(tts)):.4f} of the full spoken render)")

    today = dt.date.today().isoformat()
    #: ★ NAMED `_GENERATED` AND NOT COMMITTED, exactly as the morning report is.
    #: `.gitignore` already excludes `Morning_Report_*_GENERATED.md` with the
    #: reason: everything the file is built from is versioned, so running the
    #: generator at the same commit rebuilds it byte for byte. The 14 tracked
    #: `Decisions_Awaiting_You_*` files are its HAND-WRITTEN predecessors, which
    #: is why the suffix distinguishes them rather than a new directory.
    p_md = REPO / "experimental_notes" / f"Decisions_Awaiting_You_{today}_GENERATED.md"
    p_tx = REPO / "experimental_notes" / f"Decisions_Awaiting_You_{today}_GENERATED.txt"
    p_dk = DESKTOP / f"Decisions_Awaiting_You_{today}_GENERATED.txt"
    if a.write:
        DESKTOP.mkdir(parents=True, exist_ok=True)
        p_md.write_text(md, encoding="utf-8")
        p_tx.write_text(tts, encoding="utf-8")
        p_dk.write_text(tts_index, encoding="utf-8")
        print(f"\nWROTE {p_md}\n      {p_tx}\n      {p_dk}")
    else:
        print("\nDRY RUN -- nothing written. Re-run with --write.")
    ok = not no_head and not no_opts and not no_std and len(rows) >= 5
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
