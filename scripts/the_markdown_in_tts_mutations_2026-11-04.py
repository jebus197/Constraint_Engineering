#!/usr/bin/env python3
"""MUTATION HARNESS for the markdown-in-a-TTS-file rule, 2026-11-04.

A guard that cannot fail is not a guard. This reverts the rule 5 ways and
requires `bench/tests/test_markdown_in_a_tts_file_2026-11-04.py` to go RED on
every one of them. It restores the file it found in a `finally` with a byte
check, because a harness that does not restore what it found is itself a defect
this project has recorded.

Usage: python3 scripts/the_markdown_in_tts_mutations_2026-11-04.py
Exit 0 iff every mutation is caught.
"""
import os
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
SUBJECT = REPO / "scripts" / "note_vagueness_lint.py"
GUARD = REPO / "bench" / "tests" / "test_markdown_in_a_tts_file_2026-11-04.py"

#: Mutations are DERIVED FROM THE SUBJECT, not hardcoded.
#:
#: ★ WHY. The first version of this harness hardcoded the source lines, and 2 of
#: its 5 mutations were faults in the harness rather than in the guard. (1) The
#: em-dash anchor was written with the literal character where the subject holds
#: the escape `\u2014`, because the escape was decoded in transit on the way to
#: disk, so the anchor could never match and the mutation was reported as SKIP.
#: (2) The table was emptied with `{} or {...}`, which in Python evaluates to the
#: SECOND dict because an empty dict is falsy -- so that mutation changed nothing
#: and the guard was blamed for not noticing. Deriving each anchor from the file
#: being mutated removes both classes at once: there is no second spelling of the
#: subject to drift from, and the harness asserts each substitution actually
#: changed the bytes.
#:
#: Each entry is (name, key_or_None, replacement_regex_source). A key names an
#: entry of `MARKDOWN_IN_TTS` whose compiled pattern is swapped; None means the
#: whole table is emptied.
MUTATIONS = [
    ("the whole table is emptied", None, None),
    ("the bold-span pattern never matches",
     "a bold span, spoken as asterisks", r"(?!x)x"),
    ("the bullet pattern never matches",
     "a bullet marker, spoken as an asterisk", r"(?!x)x"),
    ("the em-dash pattern never matches",
     "an em-dash, which the rule replaces with a comma or a full stop",
     r"(?!x)x"),
    # THE FALSE-POSITIVE DIRECTION, and it is the one that matters most: a rule
    # that would accuse multiplication, or his own annotation marker, must turn
    # this guard red just as surely as a rule that catches nothing.
    ("a bare asterisk is reinstated, which accuses multiplication",
     "a bold span, spoken as asterisks", r"\*"),
]

#: Matches `"<key>":` followed by its `re.compile(<pattern>)` call, however the
#: pattern is spelled -- raw string, escape, or literal character.
def _swap(text: str, key: str, pattern: str) -> str:
    """Return `text` with `key`'s compiled pattern replaced. Raises if absent."""
    rx = re.compile(
        r'("' + re.escape(key) + r'":\s*\n\s*re\.compile\()([^\n]*?)(\),)')
    m = rx.search(text)
    if not m:
        raise LookupError(f"key not found in the subject: {key!r}")
    return text[:m.start(2)] + 'r"' + pattern + '"' + text[m.end(2):]


def _empty_table(text: str) -> str:
    """Genuinely empty the table, rather than relying on a falsy-dict trick."""
    anchor = "MARKDOWN_IN_TTS = {"
    if anchor not in text:
        raise LookupError("the table declaration is not where it was")
    return text.replace(anchor, "MARKDOWN_IN_TTS = {}\n_RETIRED_MD_TABLE = {", 1)


def run_guard() -> int:
    r = subprocess.run([sys.executable, "-m", "pytest", str(GUARD), "-q",
                        "--no-header", "-p", "no:cacheprovider"],
                       capture_output=True, text=True, cwd=str(REPO))
    return r.returncode


def main() -> int:
    answer_help(__doc__, __file__)
    found = SUBJECT.read_bytes()
    text = found.decode("utf-8")
    caught, missed = 0, []
    try:
        base = run_guard()
        if base != 0:
            print("the guard is RED before any mutation; measurement void.")
            return 3
        print(f"baseline: guard green on the tree as found "
              f"({len(found)} bytes)\n")
        for name, key, pattern in MUTATIONS:
            try:
                mutated = (_empty_table(text) if key is None
                           else _swap(text, key, pattern))
            except LookupError as exc:
                missed.append((name, f"anchor absent: {exc}"))
                print(f"  [SKIP] {name}: {exc}")
                continue
            # A MUTATION THAT CHANGES NOTHING PROVES NOTHING, which is exactly
            # how the falsy-dict version of this harness blamed the guard.
            if mutated == text:
                missed.append((name, "the substitution changed no bytes"))
                print(f"  [VOID] {name} -- substitution was a no-op")
                continue
            SUBJECT.write_text(mutated, encoding="utf-8")
            rc = run_guard()
            if rc != 0:
                caught += 1
                print(f"  [RED ] {name}")
            else:
                missed.append((name, "guard stayed green"))
                print(f"  [MISS] {name} -- the guard did not notice")
            SUBJECT.write_bytes(found)
    finally:
        SUBJECT.write_bytes(found)
        assert SUBJECT.read_bytes() == found, "RESTORE FAILED"
    n = len(MUTATIONS)
    print(f"\n{caught} of {n} mutation(s) caught")
    print(f"the subject is byte-identical to what was found: "
          f"{SUBJECT.read_bytes() == found}")
    if missed:
        for name, why in missed:
            print(f"  UNCAUGHT: {name} ({why})")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
