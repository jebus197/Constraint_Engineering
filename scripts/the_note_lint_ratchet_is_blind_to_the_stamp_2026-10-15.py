#!/usr/bin/env python3
"""The note-lint ratchet cannot see the note-standard stamp rule. Measured.

HOW THIS WAS FOUND, and it was found by being wrong twice. CC1 added a paragraph
to the operational tracker, compared the file's lint count against a `/tmp` copy
of its HEAD version, read +1, concluded its own prose had created a finding, and
DELETED GOOD PROSE to fix a finding it had not created. The pre-commit then
reported the ratchet HELD, which contradicted the shell check. Chasing that
contradiction is what produced this measurement.

THE CAUSE. `scripts/note_vagueness_lint.py` is PATH-SENSITIVE: `NOTE_STANDARD_STAMP`
fires only for a file under a directory named `experimental_notes`. On identical
bytes the same file lints 15 at its real path, 15 under
`/tmp/<x>/experimental_notes/`, and 14 under `/tmp/<x>/` or a different basename.

AND THE PRE-COMMIT SHARES THE BLIND SPOT, BY CONSTRUCTION.
`hooks/pre-commit:375-392` does:

    STAGED_COPY=$(mktemp -d -t cdsfl_note_lint)
    git show ":$f"     > "$STAGED_COPY/after_$base"
    git show "HEAD:$f" > "$STAGED_COPY/before_$base"

so BOTH sides are materialised into a FLAT temp directory with an `after_`/
`before_` prefix. The `experimental_notes` parent is gone from both, so the stamp
rule fires on neither.

WHY THAT MAKES IT A SOUND RATCHET AND AN INCOMPLETE DETECTOR. Being blind on BOTH
sides means the comparison never reports a change that is not there, so it cannot
produce the false +1 that CC1's mixed-path check produced. Its job is "this commit
must not make it worse", and it does that faithfully for every rule it can see.
What it cannot do is notice a note delivered with a STALE STANDARD STAMP, which is
the one thing the foot-line convention exists to catch.

CC1's OWN CHECK WAS WORSE, AND THE DIFFERENCE MATTERS. The hook is consistently
blind. CC1 compared a `/tmp` baseline against a REAL path, so one side saw the rule
and the other did not -- an inconsistent comparison, which is how a 0 delta read
as +1. An earlier run of the same check also used a STALE baseline captured before
an intervening commit.

THE REMEDY FOR A HUMAN OR AGENT COMPARING COUNTS BY HAND: reproduce the parent
directory name in the baseline. `mkdir -p /tmp/b/experimental_notes && git show
HEAD:experimental_notes/<f> > /tmp/b/experimental_notes/<f>` compares like with
like. That is what this script asserts.
"""
from __future__ import annotations

import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

# `_cli_help` lives in scripts/. Locate it rather than assume a depth.
for _cand in (pathlib.Path(__file__).resolve().parent,
              *pathlib.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
LINT = REPO / "scripts/note_vagueness_lint.py"
COUNT = re.compile(r"^\s*(\d+) finding", re.M)


def count(path: pathlib.Path) -> int:
    out = subprocess.run([sys.executable, str(LINT), str(path)],
                         capture_output=True, text=True, cwd=REPO).stdout
    hits = COUNT.findall(out)
    return int(hits[-1]) if hits else -1


def findings(path: pathlib.Path) -> set[str]:
    out = subprocess.run([sys.executable, str(LINT), str(path)],
                         capture_output=True, text=True, cwd=REPO).stdout
    return {re.sub(r"para \d+", "para N", m).strip()
            for m in re.findall(r"^    para \d+.*$", out, re.M)}


def main() -> int:
    targets = [p for p in sorted((REPO / "experimental_notes").glob("*.md"))
               if p.stat().st_size > 2000][:6]
    if not targets:
        print("no targets", file=sys.stderr)
        return 2

    rows = []
    print("=" * 78)
    print("1. THE SAME BYTES, 4 PATHS, PER FILE")
    print("=" * 78)
    print(f"  {'file':<46}{'real':>6}{'same dir':>10}{'flat':>6}{'after_':>8}")
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        (d / "experimental_notes").mkdir()
        for t in targets:
            same = d / "experimental_notes" / t.name
            flat = d / t.name
            pref = d / f"after_{t.name}"
            for dst in (same, flat, pref):
                shutil.copyfile(t, dst)
            r = (count(t), count(same), count(flat), count(pref))
            rows.append((t.name, *r))
            print(f"  {t.name[:44]:<46}{r[0]:>6}{r[1]:>10}{r[2]:>6}{r[3]:>8}")
            for dst in (same, flat, pref):
                dst.unlink()

    print()
    print("=" * 78)
    print("2. WHAT THE FLAT PATH LOSES")
    print("=" * 78)
    lost_any = 0
    lost_kinds: dict[str, int] = {}
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        for t in targets:
            flat = d / t.name
            shutil.copyfile(t, flat)
            lost = findings(t) - findings(flat)
            flat.unlink()
            if lost:
                lost_any += 1
                for l in lost:
                    kind = l.split("  ")[1] if "  " in l else l
                    lost_kinds[kind] = lost_kinds.get(kind, 0) + 1
    print(f"  files where the flat path loses at least 1 finding: {lost_any} of {len(targets)}")
    for k, v in sorted(lost_kinds.items(), key=lambda kv: -kv[1]):
        print(f"    {v:>3}  {k[:66]}")

    print()
    print("=" * 78)
    print("3. THE HOOK USES THE FLAT FORM ON BOTH SIDES")
    print("=" * 78)
    hook = (REPO / "hooks/pre-commit").read_text(encoding="utf-8")
    uses_mktemp = 'STAGED_COPY=$(mktemp -d' in hook
    after_flat = '> "$STAGED_COPY/after_$base"' in hook
    before_flat = '> "$STAGED_COPY/before_$base"' in hook
    print(f"  materialises into a flat mktemp dir : {uses_mktemp}")
    print(f"  writes the STAGED side as after_*   : {after_flat}")
    print(f"  writes the HEAD side as before_*    : {before_flat}")
    blind_both_sides = uses_mktemp and after_flat and before_flat
    print(f"  so it is blind on BOTH sides        : {blind_both_sides}")
    print("  -> a SOUND ratchet (no false +1) and an INCOMPLETE detector")
    print("     (a stale standard stamp passes unseen)")

    verdict = lost_any > 0 and blind_both_sides
    print()
    print("=" * 78)
    print("VERDICT")
    print("=" * 78)
    print(f"  the lint is path-sensitive and the hook's comparison is blind to it: {verdict}")
    print("  REMEDY for a hand comparison: reproduce the parent directory in the")
    print("  baseline, which the 'same dir' column above shows agrees with the real path.")

    out = {
        "rows": [{"file": r[0], "real": r[1], "same_dir": r[2],
                  "flat": r[3], "after_prefixed": r[4]} for r in rows],
        "files_losing_a_finding_on_the_flat_path": [lost_any, len(targets)],
        "kinds_lost": lost_kinds,
        "hook_blind_on_both_sides": blind_both_sides,
        "hook_site": "hooks/pre-commit:375-392",
        "verdict": verdict,
    }
    dest = REPO / "experimental_notes/evidence/note_lint_is_path_sensitive_2026-10-15.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(f"  evidence -> {dest.relative_to(REPO)}")
    return 0 if verdict else 1


if __name__ == "__main__":
    answer_help(__doc__, __file__)
    sys.exit(main())
