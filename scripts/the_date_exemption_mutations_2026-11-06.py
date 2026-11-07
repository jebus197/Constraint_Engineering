#!/usr/bin/env python3
"""Mutation harness for the date-bounded exemption, 2026-11-06.
import sys

An exemption added to a comparator is the most dangerous kind of change,
because the failure mode is SILENT: an exemption that forgives too much turns
a working check into one that always passes, and nothing about the output
says so. So each mutation here widens or inerts the exemption and the NAMED
test must go red.

Anchors are DERIVED by searching the source; the subject is restored from the
bytes this script read.
"""
from __future__ import annotations
import pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SUBJ = ROOT / "scripts" / "do_the_two_decision_surfaces_agree_2026-11-01.py"
TEST = ROOT / "bench" / "tests" / "test_a_ruling_after_the_file_is_not_a_divergence_2026-11-06.py"


def _anchor(src: str, pattern: str) -> str:
    m = re.search(pattern, src, re.M)
    if not m:
        raise SystemExit(f"ANCHOR NOT FOUND -- harness is stale, not the guard: {pattern}")
    return m.group(0)


def mutations(src: str):
    out = []

    a = _anchor(src, r"^                return _dt\.date\.fromisoformat\(str\(r\)\[:10\]\) > cutoff, k, r$")
    out.append(("M1 same-day rulings become exempt (> relaxed to >=)",
                src.replace(a, "                return _dt.date.fromisoformat(str(r)[:10]) >= cutoff, k, r"),
                "test_a_ruling_on_the_files_own_date_is_still_caught"))

    a = _anchor(src, r"^    return False, None, None$")
    out.append(("M2 an untracked heading is forgiven",
                src.replace(a, "    return True, None, None"),
                "test_a_heading_the_record_never_tracked_is_still_caught"))

    a = _anchor(src, r"^                return False, k, None$")
    out.append(("M3 a decision with NO ruling is forgiven",
                src.replace(a, "                return True, k, None"),
                "test_an_unruled_decision_is_still_caught"))

    a = _anchor(src, r"^                return False, k, r$")
    out.append(("M4 a malformed ruling date is forgiven",
                src.replace(a, "                return True, k, r"),
                "test_a_malformed_date_is_still_caught_rather_than_crashing"))

    a = _anchor(src, r"^            sset\.discard\(head\)$")
    out.append(("M5 the exemption is computed and never applied (inert)",
                src.replace(a, "            pass"),
                "test_it_exits_zero_on_the_live_tree"))

    a = _anchor(src, r'^        print\(f"\\nexempted, ruled AFTER \{cutoff\} so the file could not know "$')
    out.append(("M6 the exemption is applied SILENTLY",
                src.replace(a, '        print(f"" if True else f"'),
                "test_the_exemption_is_reported_rather_than_silent"))

    a = _anchor(src, r"^    return _dt\.date\.fromisoformat\(m\.group\(1\)\) if m else None$")
    out.append(("M7 the file date is read as today rather than from its name",
                src.replace(a, "    return __import__('datetime').date.today()"),
                "test_the_file_date_comes_from_the_name_he_was_handed"))
    return out


def main() -> int:
    found = SUBJ.read_bytes()
    src = found.decode()
    muts = mutations(src)
    print(f"subject: {SUBJ.relative_to(ROOT)}")
    print(f"guard:   {TEST.relative_to(ROOT)}")
    print(f"\n{len(muts)} mutations, each must turn its NAMED test red\n")
    red = 0
    try:
        for label, mutated, node in muts:
            if mutated == src:
                print(f"  INERT  {label}  <- changed nothing; harness is stale")
                continue
            SUBJ.write_text(mutated)
            r = subprocess.run([sys.executable, "-m", "pytest", f"{TEST}::{node}"
                                if "::" in node else str(TEST), "-q", "--no-header",
                                "-k", node.replace("test_", "")[:40]],
                               cwd=ROOT, capture_output=True, text=True, timeout=900)
            if r.returncode != 0:
                red += 1
                print(f"  RED    {label}\n           -> {node}")
            else:
                print(f"  GREEN  {label}  <- THE GUARD DID NOT CATCH THIS")
    finally:
        SUBJ.write_bytes(found)
        assert SUBJ.read_bytes() == found, "RESTORE FAILED -- the subject is damaged"
        print(f"\nsubject restored byte-identical ({len(found)} bytes)")
    print(f"\n{red} of {len(muts)} mutations red")
    return 0 if red == len(muts) else 1


if __name__ == "__main__":
    import pathlib as _pl
    sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
    from _cli_help import answer_help as _answer_help
    _answer_help(__doc__, __file__)
    raise SystemExit(main())
