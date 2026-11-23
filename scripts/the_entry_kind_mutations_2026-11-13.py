#!/usr/bin/env python3
"""Does the B168 entry-kind guard go RED? 4 mutations, 1 per contract.

The repair replaced a 2-keyword title test with a reader of the entry's own
STATUS declaration. These reverts check each contract can actually fail.
"""
from __future__ import annotations

import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
SUBJECT = REPO / "scripts" / "harvest_tickets_2026-10-17.py"
GUARD = "bench/tests/test_an_entrys_kind_is_declared_not_guessed_2026-11-13.py"

MUTATIONS = [
    ("Q1 the 2-keyword title rule restored",
     "test_two_title_keywords_no_longer_decide_anything",
     '    _t = CODE_SPAN.sub(" ", body or "")\n    _t = CITATION.sub(" ", _t)\n    mk = marked_kind(_t)\n    if mk and mk in KINDS:\n        return mk\n',
     '    t = (title or \"\").lower()\n'
     '    if \"orchestrator\" in t or \"selection\" in t:\n'
     '        return \"fr\"\n'
     '    _t = CODE_SPAN.sub(" ", body or "")\n    _t = CITATION.sub(" ", _t)\n    mk = marked_kind(_t)\n    if mk and mk in KINDS:\n        return mk\n',
     "3 entries that never declared a feature request are filed as one again"),

    ("Q2 the declaration loosened to a free-text search",
     "test_merely_mentioning_the_phrase_is_not_declaring_it",
     '_DECLARED_FR = re.compile(r"\\*\\*STATUS:\\s*FEATURE\\s+REQUEST\\b", re.I)',
     '_DECLARED_FR = re.compile(r"FEATURE\\s+REQUEST", re.I)',
     "an entry that merely MENTIONS the phrase -- including the entry describing "
     "this very defect -- is filed as a feature request"),

    ("Q3 the annotation rule applied to entries",
     "test_his_annotation_rule_is_not_applied_to_entries",
     '    if _DECLARED_FR.search(body or ""):\n        return "fr"\n    return "pf"',
     '    if _DECLARED_FR.search(body or ""):\n        return "fr"\n'
     '    return _unmarked_kind(body or "")',
     "his ruling about HIS OWN annotations is applied to task entries, making "
     "every entry a discussion and any entry ending in a question mark a question"),

    ("Q4 the existing declaration mechanism dropped",
     "test_an_explicit_marker_wins_over_the_declaration",
     '    _t = CODE_SPAN.sub(" ", body or "")\n    _t = CITATION.sub(" ", _t)\n    mk = marked_kind(_t)\n    if mk and mk in KINDS:\n        return mk\n',
     '',
     "an explicit marker stops winning, so there are 2 declaration mechanisms "
     "and the older one is ignored"),
]


def run(selector: str) -> tuple[int, str]:
    r = subprocess.run([sys.executable, "-m", "pytest", GUARD, "-k", selector,
                        "-q", "--no-header", "-p", "no:cacheprovider"],
                       cwd=REPO, capture_output=True, text=True, timeout=600)
    return r.returncode, (r.stdout + r.stderr)[-300:]


def main() -> int:
    original = SUBJECT.read_bytes()
    digest = hashlib.sha256(original).hexdigest()
    print(f"subject : {SUBJECT.relative_to(REPO)}  sha256 {digest[:16]}\n")
    rc, tail = run(" or ".join(m[1] for m in MUTATIONS))
    if rc != 0:
        print(f"REFUSED: baseline is already red (rc={rc}).\n{tail}")
        return 2
    print("BASELINE GREEN\n")
    red, results = 0, []
    try:
        for name, selector, old, new, why in MUTATIONS:
            src = original.decode()
            if old not in src:
                print(f"  {name}: ANCHOR NOT FOUND -- proves nothing")
                results.append((name, "ANCHOR MISSING"))
                continue
            SUBJECT.write_text(src.replace(old, new, 1))
            rc, tail = run(selector)
            ok = rc != 0
            red += ok
            results.append((name, "RED" if ok else "STILL GREEN"))
            print(f"  {name}\n    target  : {selector}\n    why     : {why}")
            print(f"    verdict : {'RED (caught)' if ok else 'STILL GREEN -- BLIND'}")
            if not ok:
                print(f"    tail    : {tail.strip()[:200]}")
            SUBJECT.write_bytes(original)
    finally:
        SUBJECT.write_bytes(original)
        back = hashlib.sha256(SUBJECT.read_bytes()).hexdigest()
        print(f"\nrestore verified: {back[:16]} == {digest[:16]} -> {back == digest}")
        assert back == digest, "THE RESTORE FAILED -- the subject is left mutated"
    print(f"\nmutations_red = {red} of {len(MUTATIONS)}")
    for n, v in results:
        print(f"    {v:<14} {n}")
    rc, tail = run(" or ".join(m[1] for m in MUTATIONS))
    print(f"\npost-restore baseline: {'GREEN' if rc == 0 else f'RED (rc={rc})'}")
    return 0 if red == len(MUTATIONS) and rc == 0 else 1


if __name__ == "__main__":
    # A `--help` MUST NOT run: this script WRITES, mutating a tracked file
    # in place and restoring it from the bytes it read first.
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
