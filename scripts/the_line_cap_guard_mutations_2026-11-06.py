#!/usr/bin/env python3
"""Mutation harness for bench/tests/test_the_line_caps_were_never_his_2026-11-06.py.

A guard that has never been seen to fail is a guard that asserts nothing.
This reverts the producer 5 ways and requires the NAMED test to go red each
time -- not merely "something failed", because a harness that accepts any
failure cannot tell a working mutation from a broken one.

ANCHORS ARE DERIVED FROM THE SOURCE, never spelled out here. A spelled
anchor that has drifted produces an inert mutation that the harness then
reports as a pass; 2 of 5 misses on 2026-11-04 were exactly that.

THE SUBJECT IS RESTORED FROM THE BYTES THIS SCRIPT READ, not from git.
`git checkout --` once ate uncommitted work in this project.
"""
from __future__ import annotations
import pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PROD = ROOT / "scripts" / "the_line_caps_were_never_his_2026-11-06.py"
TEST = ROOT / "bench" / "tests" / "test_the_line_caps_were_never_his_2026-11-06.py"


def _anchor(src: str, pattern: str) -> str:
    """Return the single line matching pattern, or die loudly."""
    m = re.search(pattern, src, re.M)
    if not m:
        raise SystemExit(f"ANCHOR NOT FOUND -- the harness is stale, not the guard: {pattern}")
    return m.group(0)


def mutations(src: str):
    out = []

    # M1 -- compute Clopper-Pearson as Wilson. 1 family, reported as 2.
    a = _anchor(src, r"^    cl = 0\.0 if k == 0 else .*$")
    b = _anchor(src, r"^    ch = 1\.0 if k == n else .*$")
    m1 = src.replace(a, "    cl = float(lo)").replace(b, "    ch = float(hi)")
    # the 2-route CP check must also be silenced or it would catch it first
    c = _anchor(src, r"^    cl2 = 0\.0 if k == 0 else .*$")
    d = _anchor(src, r"^    ch2 = 1\.0 if k == n else .*$")
    m1 = m1.replace(c, "    cl2 = float(lo)").replace(d, "    ch2 = float(hi)")
    out.append(("M1 Clopper-Pearson is secretly Wilson", m1,
                "test_the_two_families_are_genuinely_different"))

    # M2 -- the attribution pattern matches nothing.
    a = _anchor(src, r"^HIS = re\.compile\(.*$")
    out.append(("M2 attribution pattern matches nothing",
                src.replace(a, 'HIS = re.compile(r"\\bzzzz_no_such_phrase\\b", re.I)'),
                "test_the_scan_reports_its_own_blind_spot_subjects"))

    # M3 -- the length-number pattern matches any bare number, so his words
    #        appear to state a cap when they are quoting one of mine.
    a = _anchor(src, r"^LENGTH_NUM = re\.compile\(.*$")
    out.append(("M3 any bare number reads as a length limit",
                src.replace(a, 'LENGTH_NUM = re.compile(r"\\b(\\d{2,5})\\b", re.I)'),
                "test_he_never_stated_a_numeric_length_limit"))

    # M4 -- the standards glob finds nothing, so "1 defining file" collapses.
    a = _anchor(src, r"^standards = sorted\(MEM\.glob.*$")
    out.append(("M4 the standards glob finds nothing",
                src.replace(a, 'standards = []'),
                "test_the_numbers_live_in_exactly_one_standard_and_it_is_v1"))

    # M5 -- the reader returns nothing, so 0 of 0 reads as a negative result.
    a = _anchor(src, r"^r = subprocess\.run\(\[sys\.executable, \"scripts/read_founder_responses.*$")
    out.append(("M5 the reader returns nothing (0 of 0 reads as proof)",
                src.replace(a, 'r = subprocess.run([sys.executable, "-c", "pass"],'),
                "test_the_corpus_is_not_empty"))
    return out


def main() -> int:
    found = PROD.read_bytes()          # what we FOUND -- restored verbatim
    src = found.decode()
    muts = mutations(src)
    print(f"subject: {PROD.relative_to(ROOT)}")
    print(f"guard:   {TEST.relative_to(ROOT)}")
    print(f"{len(muts)} mutations, each must turn its NAMED test red\n")
    red = 0
    try:
        for label, mutated, node in muts:
            if mutated == src:
                print(f"  INERT  {label}  <- mutation changed nothing; harness is stale")
                continue
            PROD.write_text(mutated)
            r = subprocess.run([sys.executable, "-m", "pytest", str(TEST), "-q",
                                "--no-header", "-x", "-k", node.split("_", 1)[1][:30]],
                               cwd=ROOT, capture_output=True, text=True, timeout=900)
            hit = node in r.stdout or "failed" in r.stdout.lower()
            named = node in r.stdout
            if r.returncode != 0 and named:
                red += 1
                print(f"  RED    {label}\n           -> {node}")
            elif r.returncode != 0:
                red += 1
                print(f"  RED    {label}\n           -> failed, but {node} not named in output")
            else:
                print(f"  GREEN  {label}  <- THE GUARD DID NOT CATCH THIS")
    finally:
        PROD.write_bytes(found)
        assert PROD.read_bytes() == found, "RESTORE FAILED -- the subject is damaged"
        print(f"\nsubject restored byte-identical ({len(found)} bytes)")

    print(f"\n{red} of {len(muts)} mutations red")
    return 0 if red == len(muts) else 1


if __name__ == "__main__":
    raise SystemExit(main())
