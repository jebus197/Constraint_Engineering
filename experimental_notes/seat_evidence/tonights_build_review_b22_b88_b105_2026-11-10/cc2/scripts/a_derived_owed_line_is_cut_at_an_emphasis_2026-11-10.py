# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'tonights_build_review_b22_b88_b105_2026-11-10', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 7abfacf3a1cb73dffee0df0ae9427c8d35477fdf4c22c234b51f30b62a276183
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Does `derive_still_owed` quote a WHOLE statement, or a fragment of one?

WHY THIS EXISTS. `scripts/build_decisions_file_2026-11-07.py:derive_still_owed`
puts DERIVED prose in front of the founder under the heading "what is still
owed", in a file he reads aloud and decides from. A wrong extraction there
crashes nothing; it misinforms a human decision. The free-seat round of
2026-11-10 was asked to attack the regex, the last-marker-wins rule, the
260-character cut and the no-marker-no-claim rule. This producer is the
measurement behind that attack, so the figures in the reply are reproducible
rather than asserted.

WHAT IT MEASURES, over the LIVE `experimental_notes/CDSFL_MASTER_TASK_LIST.md`
and the LIVE decision queue, by calling the real function in the real module --
nothing is retyped here:

  P1  How many derived statements are not self-contained, where
      NOT SELF-CONTAINED is decided mechanically and not by reading:
      the statement does not end on a sentence terminator (. ! ?), or it
      ends on the ellipsis the length cut appends, or it contains a literal
      double asterisk that leaked out of the source markdown.

  P2  How many derived statements DROP the marker heading's own remainder.
      The capture group begins AFTER the closing bold delimiter of the
      marker's span, so any words the author wrote INSIDE that span --
      between the word OWED and the closing delimiter -- never reach him.
      Where those words are the answer, the sentence he reads states
      something else.

  P3  Whether the {30,1200} minimum capture length can carry the quote
      ACROSS a following bold heading, so that an unrelated heading is read
      to him as the answer. Demonstrated on a constructed input, because the
      live list does not currently contain a short-bodied marker and a
      measurement that depends on today's corpus would go stale silently.

EXIT STATUS. Non-zero, printing the token FALSIFIED, when any of P1/P2/P3
holds -- that is, when the defect is present. Exit 0 when every derived
statement is self-contained, retains its heading remainder, and the
cross-heading capture is impossible. Read-only: it writes nothing.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
TARGET = REPO / "scripts" / "build_decisions_file_2026-11-07.py"

#: The marker, located independently of the target's own capture rule, so P2
#: can see what the target's capture group throws away. This duplicates the
#: ANCHOR only -- never the extraction -- and a drift check below refuses to
#: report if the two stop agreeing about where the markers are.
_MARKER = re.compile(
    r"\*\*\s*(?:★\s*)?(?:AND\s+)?WHAT IS (?:STILL |ACTUALLY )?OWED"
    r"(?P<head>[^*]{0,120}?)\s*\*\*",
    re.I)

_TERMINATED = re.compile(r"[.!?][\"'’)]?\s*$")


def _load():
    spec = importlib.util.spec_from_file_location("bdf_falsify", TARGET)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _entries():
    sys.path.insert(0, str(REPO / "scripts"))
    import task_list_markers as tlm           # noqa: PLC0415
    return {e.ident: e.text for e in tlm.parse_entries()}


def _head_content(head: str) -> str:
    """The author's words inside the marker's bold span, or "" if none.

    Leading punctuation that merely joins the marker to its content is not
    content, so a bare `WHAT IS STILL OWED:` yields "" and nothing is claimed.
    """
    return head.strip().strip(":,;—-").strip()


def main() -> int:
    mod = _load()
    entries = _entries()
    failures: list[str] = []

    print("=" * 76)
    print("DOES THE DERIVED `what is still owed` QUOTE A WHOLE STATEMENT?")
    print("target:", TARGET.relative_to(REPO))
    print("=" * 76)

    derived = {i: mod.derive_still_owed(t) for i, t in entries.items()}
    derived = {i: v for i, v in derived.items() if v}
    marked = {i: list(_MARKER.finditer(re.sub(r"\s+", " ", t)))
              for i, t in entries.items()}
    marked = {i: ms for i, ms in marked.items() if ms}

    #: DRIFT REFUSAL. If this producer's anchor and the target's anchor
    #: disagree about WHICH entries carry a marker, every figure below is
    #: about a different population than the one claimed, so it refuses.
    if set(marked) != set(derived):
        print("REFUSING TO REPORT: anchor drift.")
        print("  this producer sees markers in:", sorted(marked))
        print("  the target derives text for  :", sorted(derived))
        return 2

    print()
    print(f"P1 + P2 over {len(derived)} entries carrying the marker.")
    print()
    p1 = p2 = 0
    for ident in sorted(derived):
        out = derived[ident]
        head = _head_content(marked[ident][-1].group("head"))

        not_terminated = not _TERMINATED.search(out)
        ellipsis = out.endswith("...")
        leaked = "**" in out
        bad = not_terminated or ellipsis or leaked
        dropped = bool(head) and head.lower() not in out.lower()

        if bad:
            p1 += 1
        if dropped:
            p2 += 1
        if not (bad or dropped):
            continue

        print("-" * 76)
        print(ident)
        if bad:
            why = []
            if not_terminated:
                why.append("does not end on a sentence terminator")
            if ellipsis:
                why.append("ends on the length cut's ellipsis")
            if leaked:
                why.append("contains a literal bold delimiter from the source")
            print(f"  P1 NOT SELF-CONTAINED: {'; '.join(why)}")
            print(f"     ...{out[-95:]!r}")
        if dropped:
            print("  P2 HEADING REMAINDER DROPPED -- the author wrote these words")
            print("     inside the marker's own bold span and he never sees them:")
            print(f"       {head!r}")
            print(f"     what he sees instead begins: {out[:95]!r}")

    print("-" * 76)
    print(f"P1 not self-contained : {p1} of {len(derived)}")
    print(f"P2 heading dropped    : {p2} of {len(derived)}")
    if p1:
        failures.append(f"P1: {p1} derived statements are not self-contained")
    if p2:
        failures.append(f"P2: {p2} derived statements drop their heading remainder")

    print()
    print("=" * 76)
    print("THE LIVE QUEUE -- the sentences actually rendered to him")
    print("=" * 76)
    try:
        _mrb, rows = mod.collect()
    except Exception as exc:                        # noqa: BLE001
        print(f"  queue unavailable ({exc!r}); the figures above stand alone.")
        rows = []
    #: ★ READ THE REAL RENDERED SURFACE, NEVER A RETYPED FORMAT STRING.
    #: The first version of this producer rebuilt the sentence from its own
    #: copy of the template, so after the frame was repaired it went on
    #: reporting the OLD frame as broken -- a falsifier measuring its own
    #: paraphrase instead of the artefact. `render(spoken=True)` is the text
    #: that reaches his Desktop, so that is what is inspected.
    live_bad = 0
    spoken_text = mod.render(_mrb, rows, spoken=True) if rows else ""
    owed_lines = [ln.strip() for ln in spoken_text.splitlines()
                  if "still owed" in ln.lower()]
    print(f"  {len(owed_lines)} 'still owed' lines in the rendered spoken file,")
    print(f"  against {sum(1 for r in rows if r['ruled'] or r.get('responded'))}"
          " rows carrying a ruling or a reply.")
    for ln in owed_lines:
        #: MALFORMED, decided mechanically: a doubled full stop, a leaked
        #: bold delimiter, the length cut's ellipsis, or a line that does
        #: not end on a sentence terminator.
        broken = (".." in ln.replace("...", "") or "**" in ln
                  or "..." in ln or not re.search(r"[.!?][\"'’)]?$", ln))
        print("-" * 76)
        print(f"  {'BROKEN' if broken else 'ok'}: {ln[:260]}")
        if broken:
            live_bad += 1
    if live_bad:
        failures.append(f"LIVE: {live_bad} rendered sentences are malformed")

    print()
    print("=" * 76)
    print("P3 -- can the quote run ACROSS a following bold heading?")
    print("=" * 76)
    probe = ("**B99. An entry.** Body. "
             "**WHAT IS STILL OWED:** his ruling. "
             "**UNRELATED HEADING ABOUT SOMETHING ELSE ENTIRELY.** "
             "The suite passed and nothing is owed. **NEXT.** tail")
    got = mod.derive_still_owed(probe)
    print("  marker body is 'his ruling.' -- 11 characters.")
    print("  derived:", repr(got))
    crossed = "UNRELATED" in got
    print(f"  crossed into the next heading: {crossed}")
    if crossed:
        failures.append("P3: a short body carries the quote across a heading")

    print()
    print("=" * 76)
    if failures:
        print("FALSIFIED")
        for f in failures:
            print("  -", f)
        return 1
    print("CLEAN: every derived statement is self-contained, retains its")
    print("heading remainder, and cannot run across a following heading.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
