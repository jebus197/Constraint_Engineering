#!/usr/bin/env python3
"""Does the B173 client-resolution guard go RED? 5 mutations, 1 per contract.

★ P3 IS THE ONE THAT MATTERS. It makes `resolve()` prefer the newest installed
client -- which looks like an improvement and is an ALTERED EXPERIMENTAL
CONDITION, because which client serves a dispatch decides which model answers.
If P3 ever fails to redden, the harness can start answering from a different
model with nothing recording that it changed.
"""
from __future__ import annotations

import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
GUARD = "bench/tests/test_the_client_is_resolved_and_recorded_2026-11-13.py"
RESOLVER = REPO / "bench" / "claude_cli_resolution.py"
CC2 = REPO / "bench" / "cc2_manager.py"

MUTATIONS = [
    (RESOLVER, "P1 the bundle glob loses the build-hash level",
     "test_c1_the_bundle_glob_reaches_the_installed_clients",
     '    ("claude-code", "*", "*", "claude.app", "Contents", "MacOS", "claude"),\n',
     "",
     "the original fault: the pattern matches 0 installed clients"),

    (RESOLVER, "P2 ordering reverts to lexicographic",
     "test_c2_ordering_is_by_version_tuple_not_lexicographic",
     "    out.sort(key=lambda c: (c.version is not None, c.version or (0, 0, 0)),\n"
     "             reverse=True)",
     "    out.sort(key=lambda c: c.path, reverse=True)",
     "2.1.90 sorts above 2.1.317 again"),

    (RESOLVER, "P3 resolve() starts preferring the NEWEST client",
     "test_c3_selection_is_unchanged_and_path_still_wins",
     "    on_path = shutil.which(\"claude\")\n    if on_path:\n        return on_path\n"
     "    for c in candidates(probe_path_version=probe_path_version):\n"
     "        if c.source == \"bundle\":\n            return c.path\n    return None",
     "    cs = candidates(probe_path_version=probe_path_version)\n"
     "    return cs[0].path if cs else None",
     "★ an altered experimental condition wearing the clothes of a tidy-up: a "
     "different client, and therefore possibly a different model, serves every "
     "dispatch with nothing recording the change"),

    (CC2, "P4 the resolver is re-inlined, restoring the duplication",
     "test_c4_one_declaration_two_readers",
     "        from claude_cli_resolution import resolve as _resolve",
     "        _resolve = lambda: __import__('glob').glob(str(__import__('pathlib')"
     ".Path.home() / 'Library/Application Support/Claude/claude-code/*/claude.app"
     "/Contents/MacOS/claude'))",
     "2 declarations of 1 fact again, which is the shape this project keeps finding"),

    (RESOLVER, "P5 the report stops naming a newer client",
     "test_c5_a_newer_client_is_reported_rather_than_silently_used",
     '        "newer_available": newer,',
     '        "newer_available": [],',
     "the gap becomes invisible again, which is the half that was missing entirely"),
]


def run(selector: str) -> tuple[int, str]:
    r = subprocess.run([sys.executable, "-m", "pytest", GUARD, "-k", selector,
                        "-q", "--no-header", "-p", "no:cacheprovider"],
                       cwd=REPO, capture_output=True, text=True, timeout=600)
    return r.returncode, (r.stdout + r.stderr)[-300:]


def main() -> int:
    originals = {p: p.read_bytes() for p in {m[0] for m in MUTATIONS}}
    digests = {p: hashlib.sha256(b).hexdigest() for p, b in originals.items()}
    for p, d in digests.items():
        print(f"subject: {p.relative_to(REPO)}  sha256 {d[:16]}")
    print()
    rc, tail = run(" or ".join(m[2] for m in MUTATIONS))
    if rc != 0:
        print(f"REFUSED: baseline is already red (rc={rc}).\n{tail}")
        return 2
    print("BASELINE GREEN\n")

    red, results = 0, []
    try:
        for subject, name, selector, old, new, why in MUTATIONS:
            src = originals[subject].decode()
            if old not in src:
                print(f"  {name}: ANCHOR NOT FOUND -- proves nothing")
                results.append((name, "ANCHOR MISSING"))
                continue
            subject.write_text(src.replace(old, new, 1))
            rc, tail = run(selector)
            ok = rc != 0
            red += ok
            results.append((name, "RED" if ok else "STILL GREEN"))
            print(f"  {name}\n    target  : {selector}\n    why     : {why}")
            print(f"    verdict : {'RED (caught)' if ok else 'STILL GREEN -- BLIND'}")
            if not ok:
                print(f"    tail    : {tail.strip()[:200]}")
            subject.write_bytes(originals[subject])
    finally:
        for p, b in originals.items():
            p.write_bytes(b)
        ok_all = all(hashlib.sha256(p.read_bytes()).hexdigest() == digests[p]
                     for p in originals)
        print(f"\nrestore verified for {len(originals)} file(s): {ok_all}")
        assert ok_all, "THE RESTORE FAILED -- a subject is left mutated"

    print(f"\nmutations_red = {red} of {len(MUTATIONS)}")
    for n, v in results:
        print(f"    {v:<14} {n}")
    rc, tail = run(" or ".join(m[2] for m in MUTATIONS))
    print(f"\npost-restore baseline: {'GREEN' if rc == 0 else f'RED (rc={rc})'}")
    if rc != 0:
        print(tail)
        return 3
    return 0 if red == len(MUTATIONS) else 1


if __name__ == "__main__":
    # A `--help` MUST NOT run: this script WRITES, mutating a tracked file
    # in place and restoring it from the bytes it read first.
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
