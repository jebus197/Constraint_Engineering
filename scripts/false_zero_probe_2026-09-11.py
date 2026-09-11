#!/usr/bin/env python3
"""Catch FALSE ZEROS as a CLASS: a scanner that resolves 1 form and misses the other.

WHY A CLASS CHECK AND NOT A 16TH INDIVIDUAL FIX. This defect has now landed 15
times in 1 session, and on 2026-09-11 it landed 4 times in 1 morning -- 3 of
those inside instruments built to detect it. The 4:

  * an ANCHOR: `^FAILED` over archived suite logs indented by 2 spaces. 2 real
    failures read as 0, inside the audit re-counting the I38 flake rate.
  * a SUBSTRING: `"the decay curve measure" in low` firing on "measureS", a verb.
  * a NAME-versus-CONTENT selector: a file classified by what its NAME contains
    rather than by what is IN it.
  * a ROLL-CALL line matcher that accepted `scripts/x.py` and `"scripts/x.py",`
    and silently rejected `- scripts/x.py`, which its own docstring said it took.

Fixing each one individually has a 15-for-15 record of not preventing the 16th.
What they share is not a regex -- it is an ASSUMPTION ABOUT FORM that nothing
ever tested. So test the assumption directly.

THE METHOD IS METAMORPHIC, AND IT IS MECHANICAL. Take a scanner and an input it
answers YES about. Apply a transformation that changes the FORM and not the
CONTENT. The answer must not change. If it flips YES -> NO, that is a false zero,
and no reading of the regex was required to find it:

    verdict(f, x) == verdict(f, t(x))   for every form-preserving t

TOOLS DECIDE, NOT VOTES: every entry below IMPORTS THE REAL MODULE and calls the
real scanner. Nothing here retypes a pattern, because a retyped pattern proves
nothing about the repository's code.

WHAT IT FOUND WHEN IT WAS FIRST RUN, 2026-09-11: 1 live flip --
`scripts_are_reached_2026-09-11.py::_ROLL_CALL` dropped every markdown list form.
The 2 fixes made this morning (the unanchored `_failed_the_test`, the
whitespace-tolerant paragraph splitter) are PINNED here as regression entries:
they pass, and this is what makes them stay passing.

EXPECTED FLIPS ARE DECLARED, NOT HIDDEN. `ACCEPTED` records a flip that is a
known, reasoned limitation with the reason beside it, so a real new flip is never
buried in noise. An entry may only be added with a reason; it is not a mute.
"""
from __future__ import annotations

import argparse
import importlib.util
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[1]


def _load(rel: str):
    spec = importlib.util.spec_from_file_location(
        pathlib.Path(rel).stem.replace("-", "_"), REPO / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------- transforms
# Each changes FORM and preserves CONTENT. A scanner that reports on content
# must be blind to all of them.

def indent2(s: str) -> str:   return "".join("  " + ln for ln in s.splitlines(True))
def indent4(s: str) -> str:   return "".join("    " + ln for ln in s.splitlines(True))
def tab_indent(s: str) -> str: return "".join("\t" + ln for ln in s.splitlines(True))
def trailing_ws(s: str) -> str:
    return "".join(ln.rstrip("\n") + "  \n" for ln in s.splitlines(True))
def blank_with_space(s: str) -> str: return s.replace("\n\n", "\n \n")
def blank_with_tab(s: str) -> str:   return s.replace("\n\n", "\n\t\n")
def leading_blank(s: str) -> str:    return "\n" + s

#: Form axes. The NAME is what a report says was assumed.
INDENTATION = [("indent 2", indent2), ("indent 4", indent4), ("tab", tab_indent)]
INVISIBLE = [("trailing spaces", trailing_ws),
             ("blank line with a space", blank_with_space),
             ("blank line with a tab", blank_with_tab),
             ("leading blank line", leading_blank)]

#: A path written the ways a markdown roll call actually gets written.
LIST_FORMS = [("bullet -", lambda s: "- " + s), ("bullet *", lambda s: "* " + s),
              ("bullet +", lambda s: "+ " + s), ("numbered", lambda s: "1. " + s),
              ("backticked", lambda s: f"`{s}`"),
              ("quoted and comma", lambda s: f'"{s}",'),
              ("indented bullet", lambda s: "  - " + s)]

#: An inflection of a phrase that is STILL the noun the rule is about.
INFLECTIONS = [("capitalised", lambda s: s[0].upper() + s[1:]),
               ("plural as a noun", lambda s: s + "s"),
               ("hyphenated", lambda s: s.replace(" ", "-", 1))]


class Probe:
    def __init__(self, name, subject, positive, axes, note=""):
        self.name, self.subject, self.positive = name, subject, positive
        self.axes, self.note = axes, note


#: Declared, reasoned limitations. A flip here is reported and does not gate.
#: The REASON is required: this is a record, not a mute button.
ACCEPTED = {
    ("Rule 28 category noun", "plural as a noun"):
        "`(?![a-z])` cannot tell the noun 'the decay curve measures are stale' "
        "from the verb 'the decay curve measures the latter'. Bounding the "
        "match was still right -- it removed a real false POSITIVE on "
        "Panel_Roster_Round2_FULL_RECORD_2026-09-09.md -- but it buys that by "
        "going blind to the plural NOUN. Recorded rather than fixed because "
        "separating the 2 needs a part-of-speech judgement, and a linter that "
        "guesses at one produces the false positives that get linters ignored.",
    ("Rule 28 category noun", "hyphenated"):
        "'the-decay curve measure' is not English. The hyphenated form that "
        "IS real -- 'the decay-curve measure' -- is missed by the bare "
        "substring test too, so this is not a regression from bounding.",
}


def probes() -> list[Probe]:
    flake = _load("scripts/flake_rate_2026-09-11.py")
    lint = _load("scripts/note_vagueness_lint.py")
    reach = _load("scripts/scripts_are_reached_2026-09-11.py")

    failed_log = (f"FAILED {flake.TEST} - AssertionError: the artefact "
                  f"classifier excused a real escape\n"
                  f"1 failed, 7100 passed in 512.44s\n")

    note_with_region = (
        "Opening paragraph of ordinary prose, long enough to be linted here.\n\n"
        "<!-- verbatim-begin: fable -->\n\n"
        "A seat wrote that the coverage rose and the rate improved sharply.\n\n"
        "<!-- verbatim-end -->\n\n"
        "The note's own voice: the accuracy fell and the precision fell too.\n")

    unclosed_note = (
        "Intro paragraph that is definitely long enough to be linted here.\n\n"
        "<!-- verbatim-end -->\n\n"
        "Middle paragraph of ordinary prose long enough to reach five words.\n\n"
        "<!-- verbatim-begin: fable -->\n\n"
        "The coverage rose and the rate improved and the score moved upward.\n")

    return [
        # THE ANCHOR. Pins the 2026-09-11 fix: `^FAILED` returned 0 over logs
        # piped through `sed 's/^/  /'`, and 2 real failures read as none.
        Probe("I38 failure detector", flake._failed_the_test, failed_log,
              INDENTATION + INVISIBLE,
              "an archived log may have been indented before it was stored"),

        # THE WHITESPACE SPLITTER. Pins the other 2026-09-11 fix: a blank line
        # carrying 1 space made 2 paragraph numberings drift apart, and the
        # exempt set computed by one was applied to findings numbered by the
        # other.
        Probe("paragraph splitter", lambda t: len(lint.paragraphs(t)) >= 5,
              note_with_region, INVISIBLE,
              "a whitespace-only line is a paragraph break to every renderer"),

        # THE REGION EXEMPTION. Its paragraph numbers must not move either.
        Probe("verbatim exemption", lambda t: len(lint.verbatim_paragraphs(t)) == 3,
              note_with_region, INVISIBLE,
              "the exemption must cover the same 3 paragraphs in every form"),

        # ORDER, NOT COUNT. An unclosed region must still be reported when a
        # stray end marker makes the begin/end TALLY balance.
        Probe("unclosed region guard",
              # DICT, NOT ATTRIBUTES. The seat that wrote this probe also
              # wrote its own `region_state` returning a dataclass; the one
              # that landed returns a mapping. An adopted fix is a
              # hypothesis until it has been RUN against the tree it is
              # going into -- this raised AttributeError on the first call.
              lambda t: lint.region_state(t)["unclosed"],
              unclosed_note, INVISIBLE,
              "a tally is order-blind; an unclosed region is a fact about order"),

        # THE ROLL-CALL MATCHER. This is the entry that was RED when the probe
        # was first run: every markdown list form was silently rejected.
        Probe("roll-call line matcher",
              lambda s: bool(reach._ROLL_CALL.fullmatch(s.strip())),
              "scripts/a_specimen_path_that_is_not_a_real_script.py", LIST_FORMS,
              "a roll call gets reformatted as a bullet list by anyone tidying"),

        # THE PHRASE MATCHER. 2 of its axes are declared in ACCEPTED above.
        Probe("Rule 28 category noun",
              lambda s: any(r.search(s.lower())
                            for r in lint.CATEGORY_NOUN_RE.values()),
              "the decay curve measure", INFLECTIONS,
              "bounding the match traded a false positive for a blind spot"),
    ]


def run() -> list[dict]:
    out = []
    for p in probes():
        base = p.subject(p.positive)
        if not base:
            out.append({"probe": p.name, "axis": "POSITIVE CONTROL",
                        "kind": "VACUOUS",
                        "why": "the scanner says NO to its own positive input, "
                               "so every 'no flip' below would be meaningless"})
            continue
        for axis, t in p.axes:
            try:
                got = p.subject(t(p.positive))
            except Exception as e:                      # noqa: BLE001
                got, axis = False, f"{axis} (raised {type(e).__name__})"
            if not got:
                key = (p.name, axis.split(" (")[0])
                out.append({"probe": p.name, "axis": axis,
                            "kind": "ACCEPTED" if key in ACCEPTED else "FALSE ZERO",
                            "why": ACCEPTED.get(key, p.note)})
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="exit non-zero if any undeclared false zero is found")
    a = ap.parse_args()

    findings = run()
    n_probe = len(probes())
    n_axis = sum(len(p.axes) for p in probes())
    real = [f for f in findings if f["kind"] != "ACCEPTED"]
    print(f"form-invariance probes: {n_probe} scanners, {n_axis} form axes")
    for f in findings:
        print(f"\n  [{f['kind']}] {f['probe']}  --  form axis: {f['axis']}")
        print(f"      {f['why']}")
    # `len(findings) == 0`, not `not findings`. The project's own guard
    # `test_no_script_discards_a_verdict_by_testing_the_tuple` flagged the bare
    # truth test: it cannot tell a list from a (bool, message) tuple, which is
    # always truthy and has silently swallowed a failure here before. `run()`
    # does return a list, so the bare form was correct -- and being correct is
    # not the same as being readable, which is the note already standing beside
    # the identical call in `note_vagueness_lint.py`.
    if len(findings) == 0:
        print("\n  no flips: every scanner answered the same under every form.")
    print(f"\n  {len(real)} undeclared false zero(s), "
          f"{len(findings) - len(real)} declared and reasoned.")
    if a.check:
        return 1 if real else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
