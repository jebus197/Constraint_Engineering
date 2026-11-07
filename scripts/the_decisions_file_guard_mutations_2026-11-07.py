#!/usr/bin/env python3
"""MUTATION HARNESS for test_the_decisions_file_is_generated_2026-11-07.

A guard that cannot fail is not a guard. Each mutation reverses one part of the
2026-11-07 decisions-file work and must turn the guard red.

★ ANCHORS DERIVED FROM THE FILE, NEVER SPELLED OUT, and each mutation asserts it
matched exactly 1 site. A mutation that applies to nothing is a HARNESS failure
and is reported as one rather than counted as red -- 2 of 5 missed mutations on
2026-11-04 were the probe and not the subject.

★ RESTORE WHAT WAS FOUND. The bytes read at the start are written back verbatim
in a `finally`, never `git checkout --`, which ate uncommitted work once here.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
GEN = REPO / "scripts" / "build_decisions_file_2026-11-07.py"
GUARD = (REPO / "bench" / "tests"
         / "test_the_decisions_file_is_generated_2026-11-07.py")


def _one(src: str, pattern: str, label: str) -> re.Match:
    ms = list(re.finditer(pattern, src))
    if len(ms) != 1:
        raise SystemExit(
            f"HARNESS FAILURE for {label}: matched {len(ms)} sites, expected 1. "
            f"The anchor has drifted; fix the harness, do not count this as red.")
    return ms[0]


def _drop_the_markdown_tag(src: str) -> str:
    """B132 in reverse: the written surface stops carrying the ticket identity."""
    m = _one(src, r'(?m)^        tag = f" `\[\{r\[\'tid\'\]\}\]`" if r\.get\("tid"\) else ""\n'
                  r'        A\(hd if spoken else f"## \{hd\}\{tag\}"\)\n',
             "the heading tag")
    return src[:m.start()] + '        A(hd if spoken else f"## {hd}")\n' + src[m.end():]


def _leak_the_tag_into_the_spoken_file(src: str) -> str:
    """THE HARMFUL FIX: a 12-hex value read aloud, which is B104's open question."""
    m = _one(src, r'(?m)^        A\(hd if spoken else f"## \{hd\}\{tag\}"\)\n',
             "the heading render")
    return (src[:m.start()]
            + '        A((hd + tag) if spoken else f"## {hd}{tag}")\n'
            + src[m.end():])


def _count_a_negation_as_a_claim(src: str) -> str:
    """THE HISTORICAL OVER-MATCH, reintroduced: the BARE WORD as an alternative.

    ★ A FIRST VERSION OF THIS MUTATION MERELY DROPPED THE PATTERN'S NEGATIVE
    LOOKBEHINDS AND THE GUARD STAYED GREEN -- correctly, because those
    lookbehinds can only fire on "not is the recommendation", which is not
    English and appears nowhere in the corpus. The ad-hoc regex that actually
    flagged 9 of 31 entries included `|recommended` as an alternative, and THAT
    is what reads "NOT recommended" as a claim. The mutation now reverses the
    live property instead of a decoration.
    """
    m = _one(src, r'(?m)^_CLAIMS = re\.compile\(.*\n', "the claim pattern")
    return (src[:m.start()]
            + '_CLAIMS = re.compile(r"\\bis (?:my |the )?recommendation\\b'
              '|recommended", re.I)\n'
            + src[m.end():])


def _truncate_the_index(src: str) -> str:
    """An index that samples reads as complete, which is worse than none."""
    m = _one(src, r'(?m)^    for i, r in enumerate\(rows, 1\):\n'
                  r'        k, _how = recommended_index', "the index loop")
    return (src[:m.start()]
            + "    for i, r in enumerate(rows[:5], 1):\n"
              "        k, _how = recommended_index"
            + src[m.end():])


MUTATIONS = [
    (_drop_the_markdown_tag, "written surface stops carrying the ticket identity"),
    (_leak_the_tag_into_the_spoken_file, "ticket identity leaks into the spoken file"),
    (_count_a_negation_as_a_claim, "the detector counts NOT recommended as a claim"),
    (_truncate_the_index, "the index silently samples 5 of the decisions"),
]


def main() -> int:
    red = 0
    for mutate, label in MUTATIONS:
        found = GEN.read_bytes()
        try:
            GEN.write_text(mutate(found.decode("utf-8")), encoding="utf-8")
            r = subprocess.run([sys.executable, "-m", "pytest", str(GUARD), "-q"],
                               capture_output=True, text=True, cwd=REPO)
            failed = r.returncode != 0
            red += bool(failed)
            print(f"  {'RED  ' if failed else 'GREEN'}  {label}")
            if not failed:
                print("         *** THE GUARD DID NOT NOTICE. ***")
        finally:
            GEN.write_bytes(found)
    print(f"\n{red} of {len(MUTATIONS)} mutations turn the guard red.")
    r = subprocess.run([sys.executable, "-m", "pytest", str(GUARD), "-q"],
                       capture_output=True, text=True, cwd=REPO)
    print(f"guard on the restored tree: "
          f"{'GREEN' if r.returncode == 0 else 'RED -- RESTORE FAILED'}")
    return 0 if (red == len(MUTATIONS) and r.returncode == 0) else 1


if __name__ == "__main__":
    import pathlib as _pl
    sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
    from _cli_help import answer_help as _answer_help
    _answer_help(__doc__, __file__)
    raise SystemExit(main())
