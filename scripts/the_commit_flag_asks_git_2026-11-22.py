#!/usr/bin/env python3
"""Drive `_a_commit_landed_since` over its stated cases, so the figure is real.

RAISED BY THE PANEL 2026-11-22. Seat fable observed that the comment at
`hooks/work_not_narrate.py` declaring *"DRIVEN OVER 5 CASES BEFORE BEING
WRITTEN, correct in 5 of 5"* had no committed producer. Under
`measured-rate-travels-with-its-script` a number that exists only as prose is a
claim about evidence rather than evidence, and the rule binds a code comment
exactly as it binds a note. The finding was verified before this script was
written: the string `5 of 5` appeared in the hook and in no script.

THE DEFECT THE PREDICATE REPLACED. The gate used to set its commit flag from
the literal string `git commit` appearing anywhere in the turn's transcript, and
`hooks/pre-commit` carries `git commit --no-verify` as its own bypass advice --
so merely READING that file made the gate report a commit that never happened.
HEAD was unmoved across 6 such reports.

METHOD. A scratch repository is created with a pinned committer date, the hook
is imported and its `REPO` constant redirected at it, and the predicate is
driven over every case the comment names plus the empty-string case. Nothing in
the real repository is read or written.
"""
from __future__ import annotations

import datetime
import importlib.util
import os
import pathlib
import subprocess
import sys
import tempfile

# `_cli_help` lives in scripts/. Located rather than assumed at a fixed depth,
# so the import works when this file is IMPORTED as well as when it is RUN.
for _cand in (pathlib.Path(__file__).resolve().parent,
              *pathlib.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402


REPO = pathlib.Path(__file__).resolve().parents[1]
HOOK = REPO / "hooks" / "work_not_narrate.py"

PINNED = "2026-06-15T12:00:00+00:00"


def load_hook():
    spec = importlib.util.spec_from_file_location("wnn_producer", HOOK)
    m = importlib.util.module_from_spec(spec)
    sys.modules["wnn_producer"] = m
    try:
        spec.loader.exec_module(m)
    except SystemExit:
        pass                      # the hook is a script; its functions are bound
    return m


def scratch_repo(d: pathlib.Path) -> str:
    env = dict(os.environ)
    env.update({
        "GIT_AUTHOR_DATE": PINNED, "GIT_COMMITTER_DATE": PINNED,
        "GIT_AUTHOR_NAME": "p", "GIT_AUTHOR_EMAIL": "p@e",
        "GIT_COMMITTER_NAME": "p", "GIT_COMMITTER_EMAIL": "p@e",
    })
    subprocess.run(["git", "init", "-q", str(d)], check=True, capture_output=True)
    (d / "f.txt").write_text("x\n")
    subprocess.run(["git", "-C", str(d), "add", "f.txt"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(d), "commit", "-q", "-m", "pinned"],
                   check=True, capture_output=True, env=env)
    out = subprocess.run(["git", "-C", str(d), "log", "-1", "--format=%cI"],
                         capture_output=True, text=True, check=True)
    return out.stdout.strip()


def main() -> int:
    m = load_hook()
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td) / "r"
        d.mkdir()
        head_iso = scratch_repo(d)
        m.REPO = d                      # redirect the predicate at the scratch repo
        head = datetime.datetime.fromisoformat(head_iso)

        cases = [
            ("a turn starting now, long after HEAD",
             datetime.datetime.now(datetime.timezone.utc).isoformat(), False),
            ("a turn predating HEAD",
             (head - datetime.timedelta(hours=1)).isoformat(), True),
            ("HEAD's own timestamp, exactly",
             head.isoformat(), True),
            ("1 second after HEAD",
             (head + datetime.timedelta(seconds=1)).isoformat(), False),
            ("an unparseable timestamp",
             "not-a-timestamp", False),
            ("an empty timestamp",
             "", False),
        ]
        print(f"scratch HEAD committed at {head_iso}\n")
        right = 0
        for label, turn_iso, want in cases:
            got = m._a_commit_landed_since(turn_iso)
            ok = got is want
            right += ok
            print(f"  {'OK ' if ok else 'BAD'}  {label:38s} -> {got!r:6s} "
                  f"(expected {want!r})")
        n = len(cases)
        print(f"\ncorrect in {right} of {n}")

        # The fail-safe direction, stated separately because it is the property
        # that matters most: a broken predicate must never CLAIM a commit.
        claimed_wrongly = sum(
            1 for label, t, want in cases
            if want is False and m._a_commit_landed_since(t) is True)
        print(f"cases where a False expectation was wrongly reported as a commit: "
              f"{claimed_wrongly}")
        return 0 if (right == n and claimed_wrongly == 0) else 1


if __name__ == "__main__":
    answer_help(__doc__, __file__)
    sys.exit(main())
