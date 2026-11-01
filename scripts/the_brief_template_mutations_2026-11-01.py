#!/usr/bin/env python3
"""Mutate the brief-validator repair 4 ways; every one must turn the guard red.

WHY. On 2026-11-01 a composability check was added to the validator's REQUIRED
set while the template said nothing about composability. The validator then
refused 134 of 139 archived briefs and refused the TEMPLATE itself, so the next
panel dispatch would have been blocked by a brief written exactly as instructed.
The repair has 4 moving parts and this script proves each is load-bearing rather
than asserting it.

★ THE 4TH MUTATION CAUGHT A HOLE IN THE GUARD ON ITS FIRST RUN. Once the check
is advisory, stripping the requirement OUT of the template no longer makes the
template fail the validator, so mutation 4 passed 9 of 9 and the half his ruling
actually asked for was unguarded. A test asserting the template does not trigger
the advisory was added, and mutation 4 then went red.

EVERY FILE IS RESTORED FROM BYTES READ BEFORE THE MUTATION, never from git, and
the restore is verified by comparison. `git checkout --` has eaten a subject in
this project before.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
VALIDATOR = REPO / "scripts" / "panel_brief_validate.py"
TEMPLATE = REPO / "bench" / "directives" / "universal" / "panel_brief_template.md"
#: BOTH guards, because the repair is pinned in 2 places and a mutation that
#: only 1 of them catches is a mutation the other would let through. The 2nd was
#: added 2026-11-01 after the commit gate refused on it: it had asserted the
#: check was in the REQUIRED set, which the demotion removed, so the guard and
#: the repair disagreed. It was found by the gate rather than by this harness,
#: because this harness named only 1 file.
GUARDS = (
    REPO / "bench" / "tests"
    / "test_the_template_passes_its_own_validator_2026-11-01.py",
    REPO / "bench" / "tests"
    / "test_the_brief_template_states_composability_his_way_2026-11-01.py",
)


def _run_guard() -> tuple[bool, str]:
    r = subprocess.run([sys.executable, "-m", "pytest", "-q",
                        "-p", "no:cacheprovider", *[str(g) for g in GUARDS]],
                       capture_output=True, text=True, cwd=REPO)
    tail = (r.stdout or "").strip().splitlines()[-1:] or [""]
    return r.returncode != 0, tail[0]


def m1_required(src: str) -> str:
    """Put the positive check back into the REQUIRED set."""
    anchor = '    ("requires the fix to be TESTED",'
    return src.replace(
        anchor,
        '    ("states composability as a DEMONSTRATED advantage, not mere '
        'coexistence",\n     _DEMONSTRATED_COMPOSABILITY,\n'
        '     "state it his way"),\n' + anchor, 1)


def m2_no_negation(src: str) -> str:
    """Remove the negation guard, so a sentence FORBIDDING the weak form fires."""
    old = "        if _EXCLUDES.search(_sentence):\n            continue\n"
    assert src.count(old) == 1, "negation guard not found"
    return src.replace(old, "")


def m3_unwired(src: str) -> str:
    """Unwire the advisory from main(), making it an addition nothing reaches."""
    old = "    _comp = composability_advisory(text)"
    assert src.count(old) == 1, "advisory call not found"
    return src.replace(old, "    _comp = []  # unwired")


def m4_template(src: str) -> str:
    """Strip the requirement out of the template: his ruling's own half."""
    i = src.index("Where more than one repair is in play")
    j = src.index("\n## REQUIRED SECTION 4", i)
    return src[:i] + src[j:]


MUTATIONS = (
    ("the check back in the REQUIRED set", VALIDATOR, m1_required),
    ("the negation guard removed", VALIDATOR, m2_no_negation),
    ("the advisory unwired from main()", VALIDATOR, m3_unwired),
    ("the requirement stripped from the TEMPLATE", TEMPLATE, m4_template),
)


def main() -> int:
    ok, line = _run_guard()
    print("=" * 74)
    print("BRIEF-VALIDATOR REPAIR: 4 MUTATIONS, EACH MUST TURN THE GUARD RED")
    print("=" * 74)
    print(f"\nbaseline (unmutated): {'RED' if ok else 'green'}  {line}")
    if ok:
        print("  ★ the guard is already red, so nothing below means anything.")
        return 2
    caught = 0
    for name, path, fn in MUTATIONS:
        original = path.read_bytes()
        try:
            path.write_text(fn(original.decode("utf-8")), encoding="utf-8")
        except Exception as exc:                                  # noqa: BLE001
            path.write_bytes(original)
            print(f"  NOT APPLIED  {name}: {type(exc).__name__}: {exc}")
            continue
        try:
            red, line = _run_guard()
        finally:
            path.write_bytes(original)
            assert path.read_bytes() == original, f"restore failed for {path}"
        caught += red
        print(f"  {'RED  ' if red else '★ NOT CAUGHT'}  {name}\n"
              f"             {line}")
    print(f"\ncaught {caught} of {len(MUTATIONS)} mutation(s)")
    ok2, line2 = _run_guard()
    print(f"guard after all restores: {'RED' if ok2 else 'green'}  {line2}")
    if ok2:
        print("  ★ THE TREE DID NOT COME BACK CLEAN.")
        return 3
    return 0 if caught == len(MUTATIONS) else 1


if __name__ == "__main__":
    sys.path.insert(0, str(REPO / "scripts"))
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
