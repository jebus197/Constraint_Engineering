#!/usr/bin/env python3
"""Reverse each half of the B96 out-of-band exemption and prove the guard reds.

The exemption spans 2 files -- the lint that applies them and the renderer that
records them -- so the mutations cross both, and each is restored from bytes
held here and verified by sha256
(`feedback_a_harness_must_restore_what_it_found_2026-11-01`). Anchors are
asserted present before any edit
(`feedback_a_mutation_harness_must_derive_its_anchors_2026-11-04`).
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
LINT = REPO / "scripts/note_vagueness_lint.py"
GEN = REPO / "scripts/morning_report_build_2026-10-12.py"
GUARD = (REPO / "bench/tests"
         / "test_quoted_text_is_exempt_in_the_spoken_copy_2026-11-08.py")

MUTATIONS = [
    (LINT, "the lint ignores the out-of-band spans",
     "    exempt = set(state[\"marked\"]) | paragraphs_covering(text, extra_exempt_spans)",
     "    exempt = state[\"marked\"]",
     "the_spans_exempt_them"),
    (LINT, "paragraph offsets come from a DIFFERENT splitter",
     "    for m in PARAGRAPH_BREAK.finditer(text):",
     "    for m in _re.finditer(r\"\\n\\n\", text):",
     "offsets_use_the_modules_only_splitter"),
    (GEN, "the renderer records no spans",
     "            if _b > _a:\n                exempt_out.append((_starts[_a], _starts[_b]))",
     "            if False:\n                exempt_out.append((_starts[_a], _starts[_b]))",
     "every_span_lies_inside_the_text_it_describes"),
]


def main() -> int:
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()
    good = {p: p.read_bytes() for p in (LINT, GEN)}
    shas = {p: hashlib.sha256(b).hexdigest() for p, b in good.items()}
    for p, h in shas.items():
        print(f"subject : {p.relative_to(REPO)}  sha256 {h[:16]}")
    base = subprocess.run([sys.executable, "-m", "pytest", str(GUARD), "-q"],
                          capture_output=True, text=True, cwd=REPO)
    print(f"baseline: {'GREEN' if base.returncode == 0 else 'RED'}")
    if base.returncode != 0:
        print(base.stdout[-1500:])
        return 1

    failures: list[str] = []
    try:
        for subject, name, anchor, repl, expect in MUTATIONS:
            txt = good[subject].decode("utf-8")
            if txt.count(anchor) != 1:
                failures.append(f"{name}: anchor appears {txt.count(anchor)} "
                                f"times, not 1 -- the probe is wrong")
                print(f"\n[{name}] ANCHOR COUNT WRONG; skipped")
                continue
            subject.write_text(txt.replace(anchor, repl, 1), encoding="utf-8")
            r = subprocess.run([sys.executable, "-m", "pytest", str(GUARD), "-q"],
                               capture_output=True, text=True, cwd=REPO)
            red, named = r.returncode != 0, expect in r.stdout
            tail = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
            print(f"\n[{name}]\n  subject: {subject.name}")
            print(f"  guard  : {'RED' if red else 'GREEN'}   {tail}")
            print(f"  the expected test is named: {named}")
            if not red:
                failures.append(f"{name}: guard stayed GREEN")
            elif not named:
                failures.append(f"{name}: red, but {expect!r} is not the failure")
            subject.write_bytes(good[subject])
    finally:
        ok = True
        for p, b in good.items():
            p.write_bytes(b)
            back = hashlib.sha256(p.read_bytes()).hexdigest()
            ok &= back == shas[p]
            print(f"restored: {p.name} sha256 matches = {back == shas[p]}")
        if not ok:
            print("★ A SUBJECT MAY BE MUTATED. Restore it by hand.")
            return 1

    print("\n" + "=" * 70)
    if failures:
        for f in failures:
            print("FAILURE:", f)
        return 1
    print(f"all {len(MUTATIONS)} reversions turn the guard red")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
