#!/usr/bin/env python3
"""Does the B194 draft-block guard actually fail when the repair is reverted?

A guard that passes on broken code guards nothing. This harness reverts the
repair 9 distinct ways and requires `bench/tests/
test_a_draft_block_binds_nothing_2026-11-14.py` to go RED each time.

★ IT MUTATES 2 SUBJECTS, because the repair has 2 halves that fail differently:
the composer, which must strip a marked block, and the canonical directive,
which must tell an author the mechanism exists without spelling the sentinel.
A harness covering only the code half would have passed the state in which the
mechanism works and nobody can discover it -- which is the fault `cc2` named
when it refused the keyword-dodging workaround.

★ EVERY MUTATION IS VERIFIED TO HAVE CHANGED ITS FILE. An edit whose anchor has
moved leaves the subject intact, the guard passes, and the harness would report
that as a MISS -- a false alarm about the guard when the fault is the probe.
This project has recorded 2 of 5 misses being the probe rather than the guard.

★ EACH SUBJECT IS RESTORED FROM BYTES CAPTURED BEFORE THE FIRST MUTATION, never
with `git checkout --`, which in this project once ate the file under test. The
restore is itself verified by comparing bytes, because a restore is a mutation.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
COMPOSER = REPO / "bench" / "cdsfl_registry" / "composer.py"
CORE = REPO / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
GUARD = (REPO / "bench" / "tests"
         / "test_a_draft_block_binds_nothing_2026-11-14.py")

#: (label, subject, old, new). Each must change its file.
MUTATIONS = [
    ("minimal render stops stripping", COMPOSER,
     "    universal_text = strip_not_in_force(universal_text)",
     "    universal_text = universal_text"),
    ("full path stops stripping", COMPOSER,
     "    full_text = strip_not_in_force(full_text)",
     "    full_text = full_text"),
    ("predicate never fires", COMPOSER,
     "    return _NOT_IN_FORCE_MARKER in block.upper()",
     "    return False"),
    ("predicate always fires", COMPOSER,
     "    return _NOT_IN_FORCE_MARKER in block.upper()",
     "    return True"),
    ("predicate matches the PHRASE, not the sentinel", COMPOSER,
     "    return _NOT_IN_FORCE_MARKER in block.upper()",
     '    return "NOT IN FORCE" in block.upper()'),
    ("strip returns its input", COMPOSER,
     '''    out: list[str] = []
    pos = 0''',
     '''    return text
    out: list[str] = []
    pos = 0'''),
    ("strip drops the gap text, reshaping whitespace", COMPOSER,
     "            out.append(m.group(0))",
     '            out.append("\\n\\n")'),
    #: ★ THIS PAIR REPLACED A PROBE THAT RENAMED THE HEADING AND MISSED.
    #: Renaming `## Drafted But Not In Force` to anything else left the guard
    #: GREEN, and correctly so: the body still named the mechanism, so the file
    #: still told an author it exists. The probe was mutating something the
    #: guard does not claim to protect. Each discoverability assertion now gets
    #: its own revert, targeting the exact phrase that assertion reads.
    ("the directive stops naming the mechanism at all", CORE,
     "carrying the CDSFL not-in-force sentinel",
     "carrying the CDSFL draft sentinel"),
    ("the directive stops saying where the sentinel lives", CORE,
     "`bench/cdsfl_registry/composer.py` removes it",
     "the composer removes it"),
    ("the directive spells the sentinel", CORE,
     "as `_NOT_IN_FORCE_MARKER` and is deliberately",
     "as `[CDSFL:NOT-IN-FORCE]` and is deliberately"),
]


def _run_guard() -> bool:
    """True when the guard is GREEN."""
    r = subprocess.run(
        [sys.executable, "-m", "pytest", str(GUARD), "-q", "--no-header"],
        cwd=REPO, capture_output=True, text=True)
    return r.returncode == 0


def main() -> int:
    originals = {p: p.read_bytes() for p in (COMPOSER, CORE)}

    if not _run_guard():
        print("REFUSED: the guard is RED before any mutation. Fix that first; a "
              "harness cannot tell a mutation from a pre-existing failure.")
        return 2

    red = misses = probe_failures = 0
    try:
        for label, subject, old, new in MUTATIONS:
            text = originals[subject].decode("utf-8")
            if old not in text:
                probe_failures += 1
                print(f"  [PROBE FAILED] {label}: anchor absent from "
                      f"{subject.name}, so nothing was mutated. The probe is "
                      f"stale, not the guard.")
                continue
            subject.write_text(text.replace(old, new, 1), encoding="utf-8")
            if subject.read_bytes() == originals[subject]:
                probe_failures += 1
                print(f"  [PROBE FAILED] {label}: bytes unchanged after edit.")
                subject.write_bytes(originals[subject])
                continue
            if _run_guard():
                misses += 1
                print(f"  [MISS]  {label}: guard stayed GREEN with the repair "
                      f"reverted.")
            else:
                red += 1
                print(f"  [RED]   {label}")
            subject.write_bytes(originals[subject])
    finally:
        for p, b in originals.items():
            p.write_bytes(b)

    restored = all(p.read_bytes() == b for p, b in originals.items())
    print(f"\n  subjects restored byte-for-byte: {restored}")
    n = len(MUTATIONS)
    print(f"  {red} of {n} mutations turned the guard RED; "
          f"{misses} MISS; {probe_failures} probe failure(s)")
    if not restored:
        print("  RESTORE FAILED — a subject is not what it was. Fix before "
              "committing.")
        return 2
    if not _run_guard():
        print("  THE GUARD IS RED AFTER RESTORE — the restore did not restore.")
        return 2
    print("  guard GREEN again after restore")
    return 0 if (misses == 0 and probe_failures == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
