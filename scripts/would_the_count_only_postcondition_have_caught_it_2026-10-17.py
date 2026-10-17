#!/usr/bin/env python3
"""How much of his text would the count-only postcondition have let through?

WHY THIS EXISTS. `scripts/regenerate_the_parked_file_2026-10-17.py` rewrites
`experimental_notes/PARKED_FOR_THE_FOUNDER.md`, a file the founder reads. Its
first postcondition compared the NUMBER of headings before and after, which is
the shape of defect this project has found repeatedly: a check that is satisfied
by something weaker than the property it is meant to hold. The guard suite claims
that version would have passed a mutation that truncates each item's text. A
claim about deleted code is a claim about evidence, so this script re-derives it
by EXECUTING both versions.

WHAT IT DOES. It reverts the postcondition to the form that compared only the
NUMBER OF HEADINGS, applies the
same body-truncating mutation the guard uses, runs the result with `--apply`
against a sandbox copy of the real file, and reports the exit code, what the
script said about itself, and how much of his text actually went missing.

MEASURED 2026-10-17: exit 0, reporting "all preserved", having lost the text of
7 of 21 items and 10,929 of 32,817 characters, 33.2996%. The 7 are the live
items, which is the whole point -- it is the items still needing him whose text
the mutation drops, and the count-only check reported success.

Costs nothing and dispatches no model. Run: python3 scripts/<this file>
"""
from __future__ import annotations

import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
GEN = REPO / "scripts" / "regenerate_the_parked_file_2026-10-17.py"
MEASURE = REPO / "scripts" / "has_he_already_ruled_on_the_parked_2026-10-13.py"
PARKED = REPO / "experimental_notes" / "PARKED_FOR_THE_FOUNDER.md"

#: The postcondition as it stood before 2026-10-17, restored verbatim.
COUNT_ONLY = '''    after = _measure()
    n_after = len(after.parked_items())
    print(f"items before {total}, after {n_after} - "
          f"{'all preserved' if n_after == total else 'ITEMS LOST'}")
    return 0 if n_after == total else 2


'''
BODY_APPEND = ('        out.append(body.rstrip())\n'
               '        out.append("")\n'
               '    out += ["---", "",')
BODY_TRUNCATED = ('        out.append(body.rstrip()[:5])\n'
                  '        out.append("")\n'
                  '    out += ["---", "",')


def _sandbox(root: pathlib.Path, gen_src: str) -> pathlib.Path:
    sand = root / "repo"
    sand.mkdir()
    (sand / "scripts").mkdir()
    (sand / "experimental_notes").mkdir()
    for s in (REPO / "scripts").iterdir():
        (sand / "scripts" / s.name).symlink_to(s)
    for nm in (GEN.name, MEASURE.name):
        (sand / "scripts" / nm).unlink()
        shutil.copy2(REPO / "scripts" / nm, sand / "scripts" / nm)
    (sand / "scripts" / GEN.name).write_text(gen_src, encoding="utf-8")
    for s in (REPO / "experimental_notes").iterdir():
        if s.name != PARKED.name:
            (sand / "experimental_notes" / s.name).symlink_to(s)
    shutil.copy2(PARKED, sand / "experimental_notes" / PARKED.name)
    for rel in ("bench", "resources", "docs", "hooks", "logs"):
        if (REPO / rel).exists():
            (sand / rel).symlink_to(REPO / rel)
    return sand


def _run(label: str, gen_src: str) -> int:
    with tempfile.TemporaryDirectory() as d:
        sand = _sandbox(pathlib.Path(d), gen_src)
        r = subprocess.run([sys.executable, str(sand / "scripts" / GEN.name),
                            "--apply"], capture_output=True, text=True,
                           cwd=str(sand))
        out = (sand / "experimental_notes" / PARKED.name).read_text(
            encoding="utf-8")
        before = PARKED.read_text(encoding="utf-8")
        parts = re.split(r"^## ", before, flags=re.M)[1:]
        bodies = ["\n".join(p.splitlines()[1:]).strip() for p in parts]
        lost = [p.splitlines()[0] for p, b in zip(parts, bodies)
                if b and b not in out]
        said = [l for l in r.stdout.splitlines()
                if "items before" in l or "preserved" in l or "ALTERED" in l]
        gone = len(before) - len(out)
        print(f"\n{label}")
        print(f"  exit code                 : {r.returncode}")
        print(f"  what it said about itself : {said or ['(nothing)']}")
        print(f"  items whose text was lost : {len(lost)} of {len(parts)}")
        print(f"  characters lost           : {gone} of {len(before)}"
              f" = {100*gone/len(before):.4f}%" if gone > 0 else
              "  characters lost           : 0")
        for h in lost:
            print(f"      {h[:84]}")
        return r.returncode


def main() -> int:
    answer_help(__doc__, __file__)
    src = GEN.read_text(encoding="utf-8")
    i = src.index("    # EVERY ITEM MUST SURVIVE THE MOVE, BODY AND ALL.")
    j = src.index("if __name__ ==")
    reverted = src[:i] + COUNT_ONLY + src[j:]
    if BODY_APPEND not in reverted:
        print("FATAL: the render body append moved; this probe is stale.")
        return 2
    mutant_old = reverted.replace(BODY_APPEND, BODY_TRUNCATED)
    mutant_new = src.replace(BODY_APPEND, BODY_TRUNCATED)

    rc_old = _run("COUNT-ONLY postcondition, bodies truncated:", mutant_old)
    rc_new = _run("BODY-PRESERVING postcondition, bodies truncated:",
                  mutant_new)

    print("\nVERDICT")
    if rc_old == 0 and rc_new != 0:
        print("  the count-only check ACCEPTED the loss; the replacement "
              "REFUSES it.")
        return 0
    print(f"  UNEXPECTED: old exit {rc_old}, new exit {rc_new}. The claim in "
          f"bench/tests/test_the_parked_file_regenerates_without_losing_him_"
          f"2026-10-17.py must be corrected.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
