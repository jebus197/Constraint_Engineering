#!/usr/bin/env python3
"""How often does `sv` need a repair afterwards, and what shape are the repairs?

Produces the figures quoted by `scripts/sv_postconditions.py`, so that the
justification for a gate is reproducible rather than remembered. Read-only:
every call is a `git log`, and nothing is written unless `--json` is given.

THE QUESTION. The founder's, 2026-09-20: *"sv should be an entirely mechanical
operation. Yet for several weeks now you keep uncovering issues with it?"* The
answerable form of that is a rate -- saves performed against repairs to the
saving script over the same window -- and a classification of the repairs, since
a rate alone does not say whether 1 mechanism would have caught them.

THE CLASSIFICATION IS KEYWORD-BASED AND THEREFORE FALLIBLE, which is why it
prints every subject beside its assigned class: the reader can overrule it by
looking. The class that matters, MEASURED-THEN-IGNORED, is assigned on evidence
in the subject line that sv had the reading and did not act on it.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SV_SCRIPT = "scripts/cdsfl_sv.py"
SINCE = "2026-08-01"

#: Above this many files, a commit is a merge or a milestone that carries the sv
#: script along, not a repair of it. 40 separates the 26-file v3 patch set from
#: the 867-file milestone merge; nothing in the window sits between 27 and 866.
BULK_FILE_CUT = 40

#: Each class carries the words that assign it, most specific first.
CLASSES = (
    ("MEASURED-THEN-IGNORED", (
        "measures", "before committing", "remote", "printed", "recorded in five",
        "timestamps", "cannot be maintained", "refuse a save", "branch drift")),
    ("ASKED-THE-WRONG-QUESTION", ("blind to", "measured it wrongly", "audit")),
    ("ENVIRONMENT", ("python 3.12", "parse only")),
)


def _log(*args: str) -> list:
    out = subprocess.run(["git", "log", *args], cwd=REPO,
                         capture_output=True, text=True, timeout=120)
    if out.returncode != 0:
        raise SystemExit(f"git log failed: {out.stderr.strip()}")
    return [ln for ln in out.stdout.splitlines() if ln.strip()]


def _files_changed(sha: str) -> int:
    out = subprocess.run(["git", "show", "--name-only", "--format=", sha],
                         cwd=REPO, capture_output=True, text=True, timeout=120)
    return len([ln for ln in out.stdout.splitlines() if ln.strip()])


def classify(subject: str) -> str:
    low = subject.lower()
    for name, words in CLASSES:
        if any(w in low for w in words):
            return name
    return "UNCLASSIFIED"


def measure() -> dict:
    saves = [ln for ln in _log(f"--since={SINCE}", "--pretty=format:%h %s")
             if ln.split(" ", 1)[-1].startswith("sv:")]
    repairs = _log(f"--since={SINCE}", "--pretty=format:%h|%ad|%s",
                   "--date=short", "--", SV_SCRIPT)
    rows = []
    for line in repairs:
        h, date, subject = line.split("|", 2)
        # A commit that is itself a save is not a repair of the saving script.
        if subject.startswith("sv:") and "guard" not in subject.lower():
            continue
        rows.append({"commit": h, "date": date, "subject": subject,
                     "class": classify(subject), "files": _files_changed(h)})
    # A commit touching hundreds of files is a merge that happens to carry the
    # sv script along, not a repair of it. Both figures are reported, because
    # the cut is a judgement and a reader is entitled to overrule it: the widest
    # count includes an 867-file milestone merge, and calling that an sv repair
    # would inflate the very rate this script exists to establish.
    focused = [r for r in rows if r["files"] <= BULK_FILE_CUT]
    counts = collections.Counter(r["class"] for r in focused)
    return {
        "window_since": SINCE,
        "saves": len(saves),
        "commits_touching_the_sv_script": len(rows),
        "repairs_to_the_sv_script": len(focused),
        "bulk_file_cut": BULK_FILE_CUT,
        "repairs_per_save": round(len(focused) / len(saves), 4) if saves else None,
        "classes": dict(counts),
        "largest_class": counts.most_common(1)[0] if counts else None,
        "rows": rows,
    }


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", type=pathlib.Path)
    a = ap.parse_args(argv)
    m = measure()
    print(f"window: since {m['window_since']}")
    print(f"saves (commits whose subject starts 'sv:'): {m['saves']}")
    print(f"commits touching {SV_SCRIPT}: {m['commits_touching_the_sv_script']}")
    print(f"of those, repairs (<= {m['bulk_file_cut']} files): {m['repairs_to_the_sv_script']}")
    print(f"repairs per save: {m['repairs_per_save']}")
    print()
    for row in m["rows"]:
        tag = row["class"] if row["files"] <= m["bulk_file_cut"] else "BULK-EXCLUDED"
        print(f"  {row['date']}  {row['commit']}  {row['files']:>3}f  "
              f"[{tag}]  {row['subject'][:74]}")
    print()
    for name, n in sorted(m["classes"].items(), key=lambda kv: -kv[1]):
        print(f"  {n:>2}  {name}")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(m, indent=2) + "\n", encoding="utf-8")
        print(f"\nwritten: {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
