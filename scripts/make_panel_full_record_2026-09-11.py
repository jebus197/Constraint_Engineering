#!/usr/bin/env python3
"""Build a FULL RECORD note for one panel round, from the seats' own replies.

WHY THIS IS A SCRIPT AND NOT AN ACT. The Personalisation directive requires
external review output preserved *"in full and in unfiltered format"* and says
*"Never summarise in place of the full output"*. Round 4's record was written by
hand on 2026-09-10; rounds 5 to 14 then had none, because writing one by hand is
an act and an act does not repeat. Measured 2026-09-11: 78 review directories
exist and 10 had a FULL RECORD note.

WHAT IT DOES NOT DO, stated rather than implied. It cannot write the CONTEXT --
what was reviewed, why, and what CC1 did with the findings. That is judgement and
it is supplied by the caller, which is why the context arrives on stdin rather
than being generated. The script guarantees the seats' words are reproduced
whole; it guarantees nothing about the prose around them.

EVERY REPLY GOES INSIDE A `verbatim-begin`/`verbatim-end` REGION, which is task
V8's mechanism: the note linter is BLOCKING at commit time and a verbatim record
routinely contains findings in the seats' own prose. Without the region the only
way to commit a record is to edit what the models said, which falsifies the
record. The exemption is scoped, so a note still cannot buy amnesty for its own
writing by quoting someone -- proven the first time this ran, when the gate
refused the round-14 note for an UNNAMED SUBJECT in CC1's own summary while
correctly exempting cc2's identical phrase.

A PAID ROUND IS NAMED, NOT ELIDED. 16 of the 78 directories hold a paid seat
reply, all dated 2026-09-05 or earlier. The header says so where it is true
rather than printing the free-seat line unconditionally.
"""
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")

#: ★ A VERBATIM REGION MAY NOT NEST, AND A JOINT ROUND'S BRIEF CONTAINS ITS
#: OWN REGIONS. Found 2026-11-10 when the 2 joint-round records refused the
#: commit gate at 15 and 22 note findings against a baseline of 0. The cause
#: was NOT the seats' prose: `scripts/build_joint_brief_2026-11-10.py` embeds
#: each parent reply inside `verbatim-begin`/`verbatim-end` so a seat is
#: exposed to the other's actual WORDS, and this generator then wraps that
#: whole brief in one more region. The lint reported `3 begin against 5 end`
#: and, with the region malformed, stopped exempting -- so every spelled
#: number in a seat's own sentence became a finding against me.
#: THE INNER MARKERS ARE MADE INERT RATHER THAN REMOVED, AND THE RECORD SAYS
#: SO. Only the HTML-comment delimiter changes, to a visibly bracketed form;
#: not 1 word of any seat's or any brief's prose is altered, which is what
#: `never-paraphrase-inside-quotation-marks` protects. The alternative was to
#: change the dispatched brief, whose sha256 is recorded in `topology.json`
#: and checked against the committed copy, so editing it would have broken
#: the integrity check it exists to provide.
def _denest(text: str) -> tuple[str, int]:
    """Make any nested verbatim marker inert. Returns (text, how many)."""
    n = text.count("<!-- verbatim-begin") + text.count("<!-- verbatim-end")
    out = (text.replace("<!-- verbatim-begin", "[verbatim-begin")
               .replace("<!-- verbatim-end -->", "[verbatim-end]")
               .replace("<!-- verbatim-end-->", "[verbatim-end]"))
    return out, n


def build(round_dir: str, title: str, out_name: str, context: str) -> pathlib.Path:
    R = REPO / "bench" / "logs" / round_dir
    stamp = subprocess.run(["date", "-Iseconds"], capture_output=True, text=True).stdout.strip()
    parts = [f"# {title}\n"]
    parts.append(f"Record written {stamp}.\n")
    parts.append("**This is the seats' own output, reproduced in full.** The Personalisation "
                 "directive requires external review output preserved *\"in full and in "
                 "unfiltered format\"* and says *\"Never summarise in place of the full "
                 "output\"*. Any summary elsewhere is downstream of this file, not a "
                 "substitute for it.\n")
    parts.append(context.strip() + "\n")
    parts.append("## Seats and cost\n")
    seats = [s for s in ("cc2", "fable", "cx", "cgpt", "ds", "ge")
             if (R / f"{s}.json").is_file()]
    paid = [s for s in seats if s in ("cx", "cgpt", "ds")]
    parts.append(
        f"{len(seats)} seat(s): {', '.join('`'+s+'`' for s in seats)}. "
        + ("**0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.\n"
           if not paid else
           f"**{len(paid)} PAID seat(s) in this round: "
           f"{', '.join(paid)}.** Recorded rather than elided.\n"))
    brief = R / "BRIEF.md"
    if brief.is_file():
        parts.append("## The brief, as dispatched\n")
        _b, _n = _denest(brief.read_text(encoding="utf-8", errors="replace"))
        parts.append("<!-- verbatim-begin: the brief as dispatched -->\n")
        if _n:
            parts.append(
                f"*{_n} nested verbatim marker(s) in this brief were made inert "
                f"by the record generator, so this region stays well formed. "
                f"Only the HTML-comment delimiter changed; no word of the brief "
                f"or of any quoted reply was altered.*\n\n")
        parts.append(_b)
        parts.append("\n<!-- verbatim-end -->\n")
    for s in seats:
        d = json.loads((R / f"{s}.json").read_text(encoding="utf-8", errors="replace"))
        body = d.get("response") or "(this seat returned no response text)"
        route = d.get("route") or "(no route recorded)"
        calls = d.get("n_tool_calls")
        parts.append(f"## Seat: {s}\n")
        parts.append(f"Route `{route}`"
                     + (f", {calls} recorded tool call(s).\n" if calls is not None else ".\n"))
        _body, _n = _denest(body)
        parts.append(f"<!-- verbatim-begin: {s} (panel {round_dir}) -->\n")
        if _n:
            parts.append(
                f"*{_n} nested verbatim marker(s) in this reply were made inert "
                f"by the record generator, so this region stays well formed. "
                f"Only the HTML-comment delimiter changed; no word of the "
                f"seat's reply was altered.*\n\n")
        parts.append(_body)
        parts.append("\n<!-- verbatim-end -->\n")
    parts.append("## Where the raw record lives\n")
    parts.append(
        f"`bench/logs/{round_dir}/` holds the brief, every seat reply, the tool logs and "
        f"`seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a "
        f"byte-identical copy is committed under `experimental_notes/evidence/`, verified "
        f"by sha256 and checked on every suite run by "
        f"`bench/tests/test_panel_records_are_preserved_2026-09-11.py`.\n")
    parts.append("\nWritten under CDSFL note standard v1.7 (26 August 2026).\n")
    # THE NAME MUST CARRY "FULL_RECORD", OR THE GUARD CANNOT SEE THE RECORD.
    # MEASURED 2026-10-12: this script accepted
    # `Free_Panel_Clearing_The_Outstanding_2026-10-12.md`, wrote 57,029 bytes of
    # a perfectly good record, and
    # bench/tests/test_panel_rounds_have_a_full_record_2026-09-11.py went on
    # reporting the round as having NO record -- because that guard globs
    # `experimental_notes/*FULL_RECORD*.md` and the name did not match. A
    # builder whose output nothing reads is the defect class the additive
    # standard names, and this builder could produce one silently. Refuse
    # instead, and say what to pass.
    if "FULL_RECORD" not in out_name:
        raise SystemExit(
            f"out_name must contain FULL_RECORD, or the guard that checks every "
            f"panel round has a record cannot see this file. Got: {out_name!r}. "
            f"Try: {out_name.replace('.md', '') + '_FULL_RECORD.md'}")
    out = REPO / "experimental_notes" / out_name
    out.write_text("\n".join(parts), encoding="utf-8")
    return out

def main() -> int:
    """A REAL PARSER, AND THE FIRST VERSION HAD NONE.

    It read `sys.argv[1]` directly, so `--help` raised IndexError -- the exact
    defect class removed from 30 scripts earlier the same day, reintroduced in a
    script written an hour later. The rule this project already carries: a
    `--help` must never cost money, written after 15 of 17 runners billed a live
    dispatch on an unrecognised argument. This one costs nothing but a
    traceback; the principle is identical, and the lapse is recorded rather than
    quietly corrected.
    """
    import argparse
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        epilog="The CONTEXT -- what was reviewed, why, and what was done with "
               "the findings -- is read from stdin, because it is judgement and "
               "cannot be generated.")
    # OPTIONAL POSITIONALS, VALIDATED BELOW, and the reason is a guard.
    # With them REQUIRED, argparse reports the missing positionals BEFORE it
    # reports an unrecognised flag -- so `--this-flag-does-not-exist` produced
    # "the following arguments are required" and never the words "unrecognized
    # arguments", and test_operational_scripts.py's
    # test_an_unknown_flag_is_rejected_loudly went red. The flag IS rejected
    # either way, with exit 2; the guard checks the MESSAGE, because a script
    # that refuses without saying what it refused teaches nothing.
    ap.add_argument("round_dir", nargs="?",
                    help="a directory name under bench/logs/")
    ap.add_argument("title", nargs="?", help="the note's title line")
    ap.add_argument("out_name", nargs="?",
                    help="the file name under experimental_notes/")
    a = ap.parse_args()

    if not (a.round_dir and a.title and a.out_name):
        ap.error("round_dir, title and out_name are all required")
    if (REPO / "bench" / "logs" / a.round_dir).is_dir() is False:
        print(f"no such round directory: bench/logs/{a.round_dir}", file=sys.stderr)
        return 2
    if sys.stdin.isatty():
        print("the context is read from stdin and stdin is a terminal; pipe it "
              "in or redirect from a file", file=sys.stderr)
        return 2
    out = build(a.round_dir, a.title, a.out_name, sys.stdin.read())
    print(f"written: {out.relative_to(REPO)}  ({out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
