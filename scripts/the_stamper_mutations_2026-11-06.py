#!/usr/bin/env python3
"""Does the stamper's guard discriminate? Mutate the stamper, require red.

ANCHORS ARE DERIVED by searching the stamper's own source for the construct each
mutation must break, and a mutation whose anchor is absent REFUSES rather than
scoring green -- the fault that made 2 of 5 mutations vacuous earlier tonight.
The stamper is copied before mutation; the original is never written.
"""
from __future__ import annotations
import os, re, subprocess, sys, tempfile
from pathlib import Path

SP = Path(__file__).resolve().parent
REPO = SP.parent
TARGET = SP / "stamp_the_brief_artefacts_2026-11-06.py"
#: THE GUARD LIVES IN `bench/tests/`, NOT BESIDE THIS HARNESS. The first version
#: resolved it as `SP / name`, true while both sat in a scratchpad and false the
#: moment they were installed. The harness reported BASELINE RED and refused
#: rather than scoring the mutations green, which is the only reason the mistake
#: was visible at all.
GUARD = REPO / "bench" / "tests" / "test_the_brief_stamps_its_artefacts_2026-11-06.py"
#: THE MUTANT IS WRITTEN TO A TEMPORARY DIRECTORY, never into `scripts/`, so a
#: harness that dies mid-run cannot leave a mutated module in the tree.
WORK = Path(tempfile.gettempdir()) / "_mut_stamper_2026-11-06.py"


def m_ambiguity(s: str) -> str:
    """Take the first hit instead of refusing an ambiguous basename."""
    a = "    if len(hits) == 1:\n        return str(hits[0].relative_to(repo))\n    return None"
    if a not in s:
        raise SystemExit("ANCHOR ABSENT: the uniqueness check is gone")
    return s.replace(a, "    if hits:\n        return str(hits[0].relative_to(repo))\n    return None")


def m_harvest(s: str) -> str:
    """Stop excluding harvested sandbox copies."""
    m = re.search(r'_IGNORE = \([^)]*\)', s)
    if not m:
        raise SystemExit("ANCHOR ABSENT: _IGNORE is gone")
    return s[:m.start()] + '_IGNORE = ()' + s[m.end():]


def m_digest(s: str) -> str:
    """Hash something other than the file's bytes."""
    a = 'hashlib.sha256(b).hexdigest()'
    if a not in s:
        raise SystemExit("ANCHOR ABSENT: the sha256 call is gone")
    return s.replace(a, 'hashlib.sha256(rel.encode()).hexdigest()')


def m_empty(s: str) -> str:
    """Emit a header even when nothing resolves."""
    a = '    if not arts:\n        return ""'
    if a not in s:
        raise SystemExit("ANCHOR ABSENT: the empty-block guard is gone")
    return s.replace(a, '    if not arts:\n        pass')


def m_dedup(s: str) -> str:
    """Stop de-duplicating a path named twice.

    ★ THE FIRST VERSION OF THIS MUTATION WAS VACUOUS and the harness said so:
    it removed the `seen` set only, and `named_artefacts` de-duplicates a SECOND
    time through `got not in out`, so behaviour was unchanged and the guard
    stayed green. A mutation that changes nothing tests nothing. BOTH mechanisms
    are removed here, and each anchor is required, so a future refactor that
    drops one cannot leave this mutation silently inert again.
    """
    a = "        if not raw or raw in seen:\n            continue\n        seen.add(raw)"
    b = "        if got and got not in out:"
    if a not in s:
        raise SystemExit("ANCHOR ABSENT: the `seen` de-duplication is gone")
    if b not in s:
        raise SystemExit("ANCHOR ABSENT: the `not in out` de-duplication is gone")
    s = s.replace(a, "        if not raw:\n            continue", 1)
    return s.replace(b, "        if got:", 1)


MUT = [
    ("ambiguous basename resolved to the first hit", m_ambiguity,
     "test_an_ambiguous_basename_does_NOT_resolve"),
    ("harvested sandbox copies no longer excluded", m_harvest,
     "test_log_harvests_are_excluded_from_basename_resolution"),
    ("digest taken over the path, not the bytes", m_digest,
     "test_the_digest_matches_the_file"),
    ("a header emitted when nothing resolves", m_empty,
     "test_it_is_empty_when_nothing_resolves"),
    ("a path named twice stamped twice", m_dedup,
     "test_a_path_named_twice_is_stamped_once"),
]


def run() -> tuple[int, str]:
    env = {**os.environ, "STAMPER_OVERRIDE": str(WORK)}
    p = subprocess.run([sys.executable, "-m", "pytest", str(GUARD), "-q"],
                       cwd=SP, capture_output=True, text=True, env=env, timeout=600)
    return p.returncode, p.stdout + p.stderr


def main() -> int:
    base = TARGET.read_text(encoding="utf-8")
    WORK.write_text(base, encoding="utf-8")
    rc, out = run()
    print(f"0. BASELINE: exit {rc}  ({out.strip().splitlines()[-1]})")
    if rc != 0:
        print("   baseline red; stop."); return 1
    red, bad = 0, []
    for name, fn, expect in MUT:
        try:
            WORK.write_text(fn(base), encoding="utf-8")
        except SystemExit as e:
            print(f"\n{name}\n   {e}"); bad.append((name, "anchor absent")); continue
        rc, out = run()
        named = expect in out
        ok = rc != 0 and named
        print(f"\n{name}\n   exit {rc}   named test failed: {named}   -> "
              f"{'RED as required' if ok else 'DID NOT DISCRIMINATE'}")
        if ok: red += 1
        else: bad.append((name, f"exit {rc}, named={named}"))
    WORK.write_text(base, encoding="utf-8")
    print(f"\n{red} of {len(MUT)} mutations turned the guard red.")
    if bad:
        print("NOT DISCRIMINATING:", bad); return 1
    print("the guard discriminates on every property it pins.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
