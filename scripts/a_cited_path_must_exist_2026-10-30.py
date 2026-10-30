#!/usr/bin/env python3
"""A BARE path citation in the master task list must name a real file.

THE GAP THIS CLOSES, AND IT IS A GAP RATHER THAN A DEFECT. Entry B41 cited
`bench/tests/test_ladder_transport_2026-10-11.py`, which has 0 commits in this
history, and no guard caught it. `bench/tests/test_line_citations_resolve_2026-09-01.py`
checks typed `file.py:NNNN` citations and says so in its own docstring, so a
citation carrying NO line number is outside its scope. It does what it says.

WHY THIS IS SCOPED TO ONE DOCUMENT, MEASURED BEFORE BUILDING. Scanning every
tracked `.md` finds HUNDREDS of dead path citations, and the largest
concentrations are `FULL_RECORD` panel transcripts -- 27, 24, 23 and 21 in the
top 4 -- which are VERBATIM SEAT OUTPUT. A seat citing a path that does not
exist is a record of what that seat said and must not be edited. `seat_evidence/`
directories are the same. A blanket check would therefore accuse correct
material, which is the 9-of-36 failure class measured on 2026-10-28, so the
blanket check is deliberately NOT built.

WHAT IS LEFT IS SMALL AND REAL. In the master task list there are **5** distinct
dead citations: **3 are deliberate illustrative placeholders** (`scripts/thing.py`,
`bench/logs/x/y.json`, `bench/logs/there-is-no-such-round/nothing.json`), and
**2 are genuine stale references**:

  * `bench/capability_identity.py` -- NEVER added to `bench/`. It exists only
    inside seat sandboxes under `experimental_notes/seat_evidence/` and
    `bench/logs/`, because it is the filename 2 seats used on 2026-10-14. The
    WORK did land, in `bench/routing.py`, which is what
    `test_capability_is_keyed_on_an_identity_not_a_name_2026-10-17.py` imports.
    So this is a stale path, NOT lost work -- checked rather than assumed,
    because the sandbox-isolation failure of 2026-10-15 is on the record.
  * `bench/tests/test_ladder_transport_2026-10-11.py` -- never existed under any
    path; the prose beside it names the guard that does.

VERBATIM REGIONS ARE EXEMPT, THROUGH THE EXISTING MACHINERY. `inside_verbatim`
from `scripts/note_vagueness_lint.py` is reused rather than reimplemented: his
words and seat output reach this list unedited, and a citation inside such a
region is a record, not a claim this project is making.

PLACEHOLDERS ARE ALLOWLISTED BY NAME, NOT BY PATTERN. A pattern matching `x.json`
or `thing.py` would quietly exempt a real file that happened to be named that
way. The allowlist is 3 entries long and each is listed with its reason.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import note_vagueness_lint as NVL  # noqa: E402

TASKLIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"

_CITED = re.compile(
    r"`((?:bench|scripts|hooks|experimental_notes|resources|docs|tools)"
    r"/[A-Za-z0-9_./-]+\.(?:py|md|json|toml|txt|sh))`")

#: DELIBERATE ILLUSTRATIVE PLACEHOLDERS, each with its reason. Named exactly,
#: never matched by pattern, so a real file of the same name is still checked.
PLACEHOLDERS = {
    "scripts/thing.py":
        "illustrative: the example of a path a citation might name",
    "bench/logs/x/y.json":
        "illustrative: a stand-in run path in an example",
    "bench/logs/there-is-no-such-round/nothing.json":
        "illustrative: names its own non-existence",
    "bench/capability_identity.py":
        "DELIBERATELY ABSENT. The citation sits inside a recorded lesson whose "
        "words are 'here I searched for a MODULE PATH I GUESSED ... found it "
        "absent and concluded nothing existed'. The work landed in "
        "bench/routing.py, which the 2026-10-17 capability guard imports, so "
        "this is not lost work -- but correcting the path would destroy the "
        "lesson, which is the whole point of the sentence. Allowlisted rather "
        "than repaired, on that reasoning and not for convenience.",
    "bench/tests/test_ladder_transport_2026-10-11.py":
        "DELIBERATELY ABSENT after 2026-10-30. B41's failure list named this "
        "path in error and is now annotated in place, naming the real guard "
        "beside it; the correction paragraph also names the path in order to "
        "say it never existed. Both remaining mentions are records of an "
        "absence, not claims that the file is there.",
}

#: THE COST OF ALLOWLISTING, STATED. An allowlisted path is no longer checked,
#: so if one of these is ever cited again AS LIVE code the check will not catch
#: it. That is accepted here because the alternative is editing away a recorded
#: lesson and a correction. It is the reason the allowlist is keyed by exact
#: name with a written reason per entry, and never by pattern: a pattern would
#: exempt files nobody decided to exempt.


def ever_existed(cited: str) -> bool:
    r = subprocess.run(["git", "log", "--all", "--oneline", "--diff-filter=A",
                        "--", cited],
                       capture_output=True, text=True, cwd=str(REPO))
    return bool(r.stdout.strip())


def dead_citations(path: Path = TASKLIST) -> list[dict]:
    """Cited paths that do not exist, excluding verbatim regions and
    allowlisted placeholders."""
    text = path.read_text(errors="ignore")
    out: list[dict] = []
    seen: set[str] = set()
    for m in _CITED.finditer(text):
        cited = m.group(1)
        if (REPO / cited).exists() or cited in seen:
            continue
        if cited in PLACEHOLDERS:
            continue
        if NVL.inside_verbatim(text, cited):
            continue
        seen.add(cited)
        out.append({"cited": cited,
                    "ever_existed": ever_existed(cited),
                    "occurrences": text.count(f"`{cited}`")})
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    dead = dead_citations()
    if args.json:
        print(json.dumps({"dead": dead, "placeholders": PLACEHOLDERS}, indent=2))
        return 0
    print(__doc__)
    print("=" * 78)
    print(f"allowlisted placeholders: {len(PLACEHOLDERS)}")
    for k, why in sorted(PLACEHOLDERS.items()):
        print(f"    {k}  -- {why}")
    print()
    print(f"DEAD CITATIONS outside verbatim regions: {len(dead)}")
    for d in dead:
        tag = "existed once" if d["ever_existed"] else "never existed"
        print(f"    {d['cited']}  ({tag}, {d['occurrences']} occurrence(s))")
    if not dead:
        print("    NONE. Every bare path citation in the task list resolves.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
