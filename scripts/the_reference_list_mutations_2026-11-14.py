#!/usr/bin/env python3
"""Does the reference-list guard fail when the 2026-11-14 build is reverted?

7 reversions, each of which must turn
`bench/tests/test_the_reference_list_is_mechanised_2026-11-14.py` RED.

★ THE WIRING IS MUTATED TOO, NOT JUST THE PRODUCER. The whole reason this exists
is that the layer-3 encoding had 0 callers, so a harness that only broke the
producer would leave the defect it was built for unverified. 2 of the 7 mutate
the generator that consumes it.

★ EVERY SUBJECT IS RESTORED FROM BYTES CAPTURED BEFORE THE FIRST MUTATION, never
with `git checkout --`, and the restore is verified by SHA-256.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PROD = REPO / "scripts" / "researcher_reference_list_2026-11-14.py"
GEN = REPO / "scripts" / "build_decisions_file_2026-11-07.py"
GUARD = (REPO / "bench" / "tests"
         / "test_the_reference_list_is_mechanised_2026-11-14.py")

MUTATIONS = [
    (PROD, "M1 an absent encoding is silently omitted instead of reported MISSING",
     '            missing.append({"domain": name, "path": rel,\n'
     '                            "why": "named in standards.toml and absent from disk"})\n'
     '            continue',
     "            continue"),
    (PROD, "M2 the backstop is typed here instead of read from the policy",
     '    backstop = int(((conf.get("policy") or {}).get("backstop_days")) or 0)',
     "    backstop = 14"),
    (PROD, "M3 needs_confirmation is ignored, so a scale-less domain goes overdue",
     '        needs = rec.get("needs_confirmation", True)',
     "        needs = True"),
    (PROD, "M4 a standard with no date is treated as current",
     '            overdue.append({**row, "age_days": None,\n'
     '                            "why": "needs confirmation and carries no date"})\n'
     "            continue",
     "            continue"),
    (PROD, "M5 the digest is taken of the path instead of the bytes",
     '            "sha256": hashlib.sha256(p.read_bytes()).hexdigest()[:16],',
     '            "sha256": hashlib.sha256(rel.encode()).hexdigest()[:16],'),
    (PROD, "M6 an unknown researcher returns empty instead of raising",
     '        raise FileNotFoundError(f"no layer-3 encoding for {researcher!r}")',
     '        return {"researcher": researcher, "encodings": [], "standards": [],\n'
     '                "missing": [], "overdue": [], "backstop_days": 0,\n'
     '                "as_of": str(today)}'),
    (GEN, "M7 the generator stops appending the list, so layer 3 has no caller again",
     "    if detail:\n        try:\n            import importlib.util as _ilu",
     "    if False:\n        try:\n            import importlib.util as _ilu"),
]


def _run_guard() -> bool:
    r = subprocess.run([sys.executable, "-m", "pytest", str(GUARD), "-q", "--no-header"],
                       cwd=REPO, capture_output=True, text=True)
    return r.returncode == 0


def main() -> int:
    originals = {p: p.read_bytes() for p in {PROD, GEN}}
    shas = {p: hashlib.sha256(b).hexdigest() for p, b in originals.items()}
    texts = {p: b.decode("utf-8") for p, b in originals.items()}

    if not _run_guard():
        print("REFUSED: the guard is RED before any mutation.")
        return 2

    red = misses = probe = 0
    try:
        for path, label, old, new in MUTATIONS:
            if old not in texts[path]:
                probe += 1
                print(f"  [PROBE FAILED] {label}: anchor absent in {path.name}.")
                continue
            path.write_text(texts[path].replace(old, new, 1), encoding="utf-8")
            if path.read_bytes() == originals[path]:
                probe += 1
                print(f"  [PROBE FAILED] {label}: bytes unchanged.")
                path.write_bytes(originals[path])
                continue
            if _run_guard():
                misses += 1
                print(f"  [MISS]  {label}")
            else:
                red += 1
                print(f"  [RED]   {label}")
            path.write_bytes(originals[path])
    finally:
        for p, b in originals.items():
            p.write_bytes(b)

    ok = all(hashlib.sha256(p.read_bytes()).hexdigest() == s for p, s in shas.items())
    print(f"\n  {len(originals)} subject(s) restored, SHA-256 verified: {ok}")
    print(f"  {red} of {len(MUTATIONS)} mutations turned the guard RED; "
          f"{misses} MISS; {probe} probe failure(s)")
    if not ok:
        print("  RESTORE FAILED.")
        return 2
    if not _run_guard():
        print("  THE GUARD IS RED AFTER RESTORE — the restore did not restore.")
        return 2
    print("  guard GREEN again after restore")
    return 0 if (misses == 0 and probe == 0) else 1


if __name__ == "__main__":
    # A `--help` MUST NOT run: this script WRITES, mutating a tracked file
    # in place and restoring it from the bytes it read first.
    # The imports are LOCAL to this guard so it needs nothing of the host
    # file: a subject using `from pathlib import Path` binds `Path`, not
    # `pathlib`, and used to be declined for it.
    import pathlib as _hp_pathlib
    import sys as _hp_sys
    _hp_sys.path.insert(
        0, str(_hp_pathlib.Path(__file__).resolve().parent))
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
