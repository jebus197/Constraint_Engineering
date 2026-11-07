#!/usr/bin/env python3
"""Mutation harness for the dormant-section archive axis.
import sys

Reverts `cdsfl_sv.archive_stale_memory_entries` 6 ways and requires the
NAMED guard test to go red each time. Anchors are DERIVED from the source;
a spelled anchor that has drifted produces an inert mutation the harness
would then report as a pass. The subject is restored from the bytes this
script read, never from git.
"""
from __future__ import annotations
import pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SUBJ = ROOT / "scripts" / "cdsfl_sv.py"
TEST = ROOT / "bench" / "tests" / "test_a_dormant_memory_section_can_be_archived_2026-11-06.py"


def _anchor(src: str, pattern: str) -> str:
    m = re.search(pattern, src, re.M)
    if not m:
        raise SystemExit(f"ANCHOR NOT FOUND -- harness is stale, not the guard: {pattern}")
    return m.group(0)


def mutations(src: str):
    out = []

    a = _anchor(src, r"^            head_at = len\(keep\) if section in dormant_sections else None$")
    out.append(("M1 the heading is never withdrawn",
                src.replace(a, "            head_at = None"),
                "test_every_bullet_leaves_and_the_heading_is_withdrawn"))

    a = _anchor(src, r"^                if line\.strip\(\):\n                    dormant_kept \+= 1$")
    out.append(("M2 surviving prose is not counted, so the heading goes anyway",
                src.replace(a, "                if False:\n                    dormant_kept += 1"),
                "test_a_section_with_surviving_prose_keeps_its_heading"))

    a = _anchor(src, r"^            if _MEMORY_BULLET_RE\.match\(line\):\n                moved\.append\(\(None, line\)\)$")
    out.append(("M3 a dormant section moves its prose too",
                src.replace(a, "            if True:\n                moved.append((None, line))"),
                "test_a_section_with_surviving_prose_keeps_its_heading"))

    a = _anchor(src, r"^        return \(when is None, when or date\.min, line\)$")
    out.append(("M4 undated rows sort FIRST",
                src.replace(a, "        return (when is not None, when or date.min, line)"),
                "test_undated_entries_sort_after_dated_ones"))

    a = _anchor(src, r"^        \(w\.isoformat\(\) if w is not None else \"undated\",$")
    out.append(("M5 an undated row is asked for its isoformat",
                src.replace(a, '        (w.isoformat(),'),
                "test_an_undated_only_run_still_reports_a_reason"))

    a = _anchor(src, r"^                                 dormant_sections: tuple = \(\)\) -> dict:$")
    out.append(("M6 the default is no longer inert",
                src.replace(a, '                                 dormant_sections: tuple = ("Session Handoffs (historical, read only if relevant)",)) -> dict:'),
                "test_the_default_moves_only_dated_entries"))

    a = _anchor(src, r"^        what \+= f\", and the dormant section\(s\) \{', '\.join\(dormant_sections\)\}\"$")
    out.append(("M7 the record stops naming the route",
                src.replace(a, '        what += ", and some sections"'),
                "test_the_reason_names_the_dormant_sections"))
    return out


def main() -> int:
    found = SUBJ.read_bytes()
    src = found.decode()
    muts = mutations(src)
    print(f"subject: {SUBJ.relative_to(ROOT)}")
    print(f"guard:   {TEST.relative_to(ROOT)}")
    print(f"{len(muts)} mutations, each must turn its NAMED test red\n")
    red = 0
    try:
        for label, mutated, node in muts:
            if mutated == src:
                print(f"  INERT  {label}  <- changed nothing; harness is stale")
                continue
            SUBJ.write_text(mutated)
            r = subprocess.run([sys.executable, "-m", "pytest", str(TEST), "-q",
                                "--no-header", "-k", node.replace("test_", "")[:38]],
                               cwd=ROOT, capture_output=True, text=True, timeout=600)
            if r.returncode != 0 and node in r.stdout:
                red += 1
                print(f"  RED    {label}\n           -> {node}")
            elif r.returncode != 0:
                red += 1
                print(f"  RED    {label}\n           -> failed, but {node} not named")
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
