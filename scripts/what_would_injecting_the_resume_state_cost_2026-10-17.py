#!/usr/bin/env python3
"""What would injecting the post-compaction resume state cost, in characters?

WHY THIS EXISTS. Task B17 carries the founder's question, verbatim: *"If you can
detect compaction mechanically, why can't you also make rs run mechanically too
after compaction?"* Two thirds of that is already built -- a UserPromptSubmit
hook runs `scripts/cdsfl_recover.py --record-restore` and a Stop hook refuses to
end the turn until the context lands. The third that is not built is that a hook
can run a script and inject text, but cannot make the assistant READ the
documents the script names. The proposed repair is to inject CONTENT rather than
paths, and the entry records that it **needs his ruling on how many characters
may be injected, because it trades context against reliability and the ceiling
is his machine's, not a preference**.

This script does not implement the injection. The founder marked B17 for
discussion. It attaches numbers to that discussion, so the decision is made
against measured sizes rather than against a guess.

MEASURED 2026-10-17, with 151 entries of which 21 are open:

  * the master task list in full                   654,237 chars
  * open entries, heading capped at 90               2,009 chars, ~502 tokens
  * open entries, heading capped at 120              2,639 chars, ~659 tokens
  * open entries with their ruled state, cap 110     2,828 chars, ~707 tokens
  * identifiers only                                    97 chars,  ~24 tokens

THE FIGURE THAT MATTERS IS THE COMPARISON, NOT THE SIZE. The notice already
injects a FIRST READ list of roughly 2,600 characters of file PATHS on each
post-compaction turn. Injecting the open entries with their ruled state costs
2,828 characters, 1.09x that. So the choice is not how much context to
spend; it is whether the same characters carry paths to documents or the state
itself, and the second does not depend on a file being opened.

Token figures use 4 characters per token, which is an approximation and is
labelled as one.

Costs nothing and dispatches no model. Run: python3 scripts/<this file>
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
TASKLIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
#: Observed this session. Counted from the notice as it arrived, not derived.
PATHS_ALREADY_INJECTED = 2600
CHARS_PER_TOKEN = 4


def main() -> int:
    answer_help(__doc__, __file__)
    sys.path.insert(0, str(REPO / "scripts"))
    from task_list_markers import parse_entries

    if not TASKLIST.is_file():
        print(f"FATAL: {TASKLIST} does not exist.")
        return 2
    full = TASKLIST.read_text(encoding="utf-8")
    lines = full.splitlines()
    entries = parse_entries(TASKLIST)
    openish = [e for e in entries if e.state in ("OPEN", "REOPENED")]

    def heading(ident: str) -> str:
        for line in lines:
            if line.startswith(f"**{ident}. "):
                return line[len(ident) + 5:]
        return ""

    print(f"THE DOCUMENT, AND WHAT IS OPEN IN IT")
    print(f"  master task list in full : {len(full):>9,} chars, "
          f"{len(lines):>5} lines")
    print(f"  entries                  : {len(entries):>9}")
    print(f"  open or reopened         : {len(openish):>9}")

    variants: dict[str, str] = {}
    for cap in (90, 120, 160):
        variants[f"open entries, heading capped at {cap}"] = "\n".join(
            f"{e.ident}: {heading(e.ident)[:cap]}" for e in openish)
    variants["open entries with their ruled state, capped at 110"] = "\n".join(
        f"{e.ident} [{'ruled ' + e.ruled if e.ruled else 'NEEDS HIS RULING'}]: "
        f"{heading(e.ident)[:110]}" for e in openish)
    variants["identifiers only"] = ", ".join(e.ident for e in openish)

    print("\nWHAT EACH SHAPE WOULD COST")
    for name, body in variants.items():
        print(f"  {name}")
        print(f"      {len(body):>7,} chars, {len(body.splitlines()):>3} lines,"
              f" ~{len(body)//CHARS_PER_TOKEN:>5,} tokens"
              f"  ({CHARS_PER_TOKEN} chars/token, an approximation)")

    print("\nTHE COMPARISON THAT MATTERS")
    chosen = variants["open entries with their ruled state, capped at 110"]
    ratio = len(chosen) / PATHS_ALREADY_INJECTED
    print(f"  the notice already injects ~{PATHS_ALREADY_INJECTED:,} chars of "
          f"file PATHS each post-compaction turn.")
    print(f"  the open entries with their ruled state cost {len(chosen):,} "
          f"chars, {ratio:.2f}x that.")
    print("  so the question is not how much context to spend. It is whether")
    print("  those characters carry paths to documents or the state itself,")
    print("  and the second does not depend on a file being opened.")
    print("\n  THE RULING IS HIS, and he marked B17 for discussion. Nothing")
    print("  here is implemented.")

    print("\nTHE CONTENT ITSELF, so he can read what would be injected:")
    for line in chosen.splitlines():
        print(f"    {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
