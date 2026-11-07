#!/usr/bin/env python3
"""MUTATION HARNESS for test_a_store_key_is_not_an_identifier_2026-11-07.

A guard that cannot fail is not a guard. Each mutation below reverses one part
of the 2026-11-07 repair and must turn the guard red.

★ ANCHORS ARE DERIVED FROM THE FILES, NEVER SPELLED OUT. The project's own
lesson from 2026-11-04: 2 of 5 missed mutations were the probe, not the
subject, because the harness wrote the anchor from memory of the shape. Each
mutation here locates its target by reading the file and asserts it found
exactly 1 site, so a mutation that applies to nothing is a FAILURE of the
harness and is reported as one rather than counted as red.

★ RESTORE WHAT WAS FOUND, NOT WHAT GIT HAS. The bytes read at the start are
written back verbatim in a `finally`. `git checkout --` was used once here and
ate uncommitted work.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
BUILD = REPO / "scripts" / "morning_report_build_2026-10-12.py"
YESTERDAY = REPO / "scripts" / "how_many_verdicts_really_await_him_2026-11-06.py"
GUARD = REPO / "bench" / "tests" / "test_a_store_key_is_not_an_identifier_2026-11-07.py"


def _one(src: str, pattern: str, label: str) -> re.Match:
    ms = list(re.finditer(pattern, src))
    if len(ms) != 1:
        raise SystemExit(
            f"HARNESS FAILURE for {label}: pattern matched {len(ms)} sites, "
            f"expected exactly 1. The anchor has drifted; fix the harness, do "
            f"not count this as red.")
    return ms[0]


def _drop_call_in(fn_name: str):
    """Remove the single `_reject_store_key(ident)` inside one function."""
    def apply(src: str) -> str:
        m = _one(src, rf"(?m)^def {re.escape(fn_name)}\(", f"def {fn_name}")
        # the function body runs to the next top-level def
        tail = src[m.end():]
        nxt = re.search(r"(?m)^def ", tail)
        end = m.end() + (nxt.start() if nxt else len(tail))
        body = src[m.start():end]
        call = _one(body, r"(?m)^\s*_reject_store_key\(ident\)\n",
                    f"call inside {fn_name}")
        return src[:m.start()] + body[:call.start()] + body[call.end():] + src[end:]
    return apply


def _neuter_predicate(src: str) -> str:
    m = _one(src, r'(?m)^    if ":" in \(ident or ""\):\n        raise ValueError\(_KEY_NOT_IDENT\.format\(ident\)\)\n',
             "the predicate body")
    return src[:m.start()] + "    if False:\n        pass\n" + src[m.end():]


def _fail_open_on_missing_body(src: str) -> str:
    """The design that was TRIED AND REJECTED: it readmits 7 ruled entries."""
    m = _one(src, r'(?m)^        body = mod\.bodies\(\)\.get\(ident, ""\)\n',
             "the body lookup")
    return (src[:m.start()]
            + "        _b = mod.bodies()\n"
            + "        if ident not in _b:\n"
            + "            return True\n"
            + "        body = _b[ident]\n"
            + src[m.end():])


def _restore_the_prefixed_caller(src: str) -> str:
    m = _one(src, r'(?m)^        spent = mr\.ruling_is_spent\(it\["ident"\], ruled, '
                  r'it\.get\("state"\) or ""\)\n',
             "the corrected caller")
    return (src[:m.start()]
            + '        spent = mr.ruling_is_spent(f"task:{it[\'ident\']}", ruled, '
              'it.get("state") or "")\n'
            + src[m.end():])


MUTATIONS = [
    (BUILD, _drop_call_in("asks_newer_than_the_ruling"),
     "drop the refusal from asks_newer_than_the_ruling"),
    (BUILD, _drop_call_in("still_asks"),
     "drop the refusal from still_asks"),
    (BUILD, _drop_call_in("ruling_is_spent"),
     "drop the refusal from ruling_is_spent"),
    (BUILD, _neuter_predicate,
     "neuter the colon predicate itself"),
    (BUILD, _fail_open_on_missing_body,
     "adopt the REJECTED fail-open-on-missing-body design"),
    (YESTERDAY, _restore_the_prefixed_caller,
     "put the prefixed key back in yesterday's producer"),
]


def main() -> int:
    red = 0
    for path, mutate, label in MUTATIONS:
        found = path.read_bytes()                     # what we FOUND
        try:
            path.write_text(mutate(found.decode("utf-8")), encoding="utf-8")
            r = subprocess.run([sys.executable, "-m", "pytest", str(GUARD), "-q"],
                               capture_output=True, text=True, cwd=REPO)
            failed = r.returncode != 0
            red += bool(failed)
            tag = "RED  " if failed else "GREEN"
            print(f"  {tag}  {label}")
            if not failed:
                print(f"         *** THE GUARD DID NOT NOTICE. "
                      f"{path.name} mutated and 0 tests failed. ***")
        finally:
            path.write_bytes(found)                   # restore what we FOUND
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
