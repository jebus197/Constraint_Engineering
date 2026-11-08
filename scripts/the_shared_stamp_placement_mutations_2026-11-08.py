"""Does the shared stamp placement actually REFUSE? 5 reversions, each made red.

B125's prerequisite was wiring a stamper that had reached 0 of 148 briefs into
the builder that was missing it, and extracting the placement rule so both
builders share 1 definition. This reverses 5 properties of that and requires
the guard to go RED for each, restoring exact bytes and verifying by sha256.

MUTATION 4 IS THE ONE WORTH READING. It reinstates the HISTORICAL bug: the
first version of the placement inserted after the first `# ` line and split a
2-line title in half. That bug is the entire reason the rule was extracted
rather than copied into a second builder, so a harness that did not reinstate
it would be testing everything except the thing the design was for.

RESTORATION IS BY SAVED BYTES, not by `git checkout --`, which has destroyed
uncommitted work in this project's record. 3 of these subjects are uncommitted
while this harness first runs.
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")
if not REPO.is_dir():
    REPO = pathlib.Path(__file__).resolve().parents[1]

ST = REPO / "scripts/stamp_the_brief_artefacts_2026-11-06.py"
PER = REPO / "scripts/build_period_joint_brief_2026-11-04.py"
SEV = REPO / "scripts/build_severity_joint_brief_2026-10-31.py"
GUARD = REPO / "bench/tests/test_both_brief_builders_stamp_2026-11-08.py"


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _run(node: str) -> tuple[int, str]:
    sel = f"{GUARD}::{node}" if node else str(GUARD)
    r = subprocess.run(
        [sys.executable, "-m", "pytest", sel, "-q", "-p", "no:randomly",
         "--no-header", "-x"],
        capture_output=True, text=True, timeout=600, cwd=str(REPO))
    return r.returncode, (r.stdout + r.stderr)[-400:]


MUTATIONS = (
    ("1 the severity builder stops loading the stamper", SEV,
     '"stamp_the_brief_artefacts_2026-11-06.py")',
     '"stamp_the_brief_artefacts_THAT_DOES_NOT_EXIST.py")',
     "test_every_joint_brief_builder_is_wired[build_severity_joint_brief_2026-10-31.py]"),
    ("2 the period builder stops applying it", PER,
     "    text = _insert_stamp(text)\n",
     "    pass  # text = _insert_stamp(text)\n",
     "test_every_joint_brief_builder_is_wired[build_period_joint_brief_2026-11-04.py]"),
    ("3 insert_stamp returns the text unchanged", ST,
     "    block = stamp_block(text, repo)\n    if not block:\n        return text\n",
     "    block = stamp_block(text, repo)\n    if True:\n        return text\n",
     "test_the_stamp_actually_lands_in_a_brief"),
    #: ★ THE FIRST VERSION OF THIS MUTATION DID NOT REPRODUCE THE BUG, and it
    #: reported STILL GREEN while the fix was sound. Changing `"## "` to `"# "`
    #: makes `next` match line 0, so the stamp lands BEFORE the title and the
    #: 2 title lines stay adjacent -- no split. The historical bug inserted
    #: AFTER the first `# ` line, so the mutation has to add 1.
    ("4 the HISTORICAL title-splitting bug is reinstated", ST,
     '    at = next((i for i, l in enumerate(lines) if l.startswith("## ")), None)',
     '    at = next((i + 1 for i, l in enumerate(lines)\n'
     '               if l.startswith("# ")), None)',
     "test_a_two_line_title_is_not_split"),
    ("5 the block is appended unconditionally", ST,
     "    block = stamp_block(text, repo)\n    if not block:\n        return text\n",
     "    block = stamp_block(text, repo) or '## ARTEFACT STAMPS AT DISPATCH'\n",
     "test_a_brief_naming_nothing_is_left_alone"),
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--only", type=int, default=None)
    args = ap.parse_args()

    for p in (ST, PER, SEV, GUARD):
        if not p.is_file():
            print(f"REFUSED: {p} is not in this checkout")
            return 1

    print("NODE PATHS VERIFIED FIRST, because a node that does not exist makes")
    print("pytest exit non-zero and a reversion then reads as RED for the wrong")
    print("reason -- a fault this project made earlier the same day.")
    for label, _s, _f, _r, node in MUTATIONS:
        chk = subprocess.run(
            [sys.executable, "-m", "pytest", f"{GUARD}::{node}",
             "--collect-only", "-q", "-p", "no:randomly"],
            capture_output=True, text=True, timeout=300, cwd=str(REPO))
        if chk.returncode != 0 or "no tests ran" in (chk.stdout + chk.stderr):
            print(f"  REFUSED: {node} does not collect")
            return 1
    print("  all node paths collect\n")

    rc, tail = _run("")
    print(f"BASELINE: {GUARD.name} exit {rc}")
    if rc != 0:
        print(f"REFUSED: baseline is red.\n{tail}")
        return 1

    red = ran = 0
    for label, subject, find, repl, node in MUTATIONS:
        if args.only is not None and not label.startswith(str(args.only)):
            continue
        ran += 1
        original = subject.read_bytes()
        before = _sha(original)
        text = original.decode()
        if text.count(find) != 1:
            print(f"  {label}: REFUSED -- anchor appears {text.count(find)} "
                  f"time(s) in {subject.name}")
            continue
        try:
            subject.write_text(text.replace(find, repl, 1))
            rc, tail = _run(node)
            ok = rc != 0
            red += int(ok)
            print(f"  {label}: {'RED (good)' if ok else 'STILL GREEN -- NOT GUARDED'}")
            if not ok:
                print(f"      tail: {tail.strip()[-200:]}")
        finally:
            subject.write_bytes(original)
            if _sha(subject.read_bytes()) != before:
                print(f"  REFUSED: {subject.name} did NOT restore. FIX BY HAND.")
                return 2

    print(f"\n  {red} of {ran} reversions turn the guard red")
    if red == ran:
        print("  every reversed property is guarded")
        return 0
    print("  AT LEAST 1 PROPERTY IS UNGUARDED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
