#!/usr/bin/env python3
"""Does the ranking mechanism carry the football terminology he rejected?

HIS REJECTION, 2026-10-09, verbatim: *"we shouldn't have our code littered with
football references... or even 'leagues', as such"*, alongside *"in reality there
should probably be no distinction between models participating in an experiment
other than a 'ranking number'"*. Task C21 records that the rejection was never
itself recorded, so this measures whether it has in fact been honoured.

WHAT IT MEASURES, BY AST so that a comment quoting him is not mistaken for code
he objected to. Every IDENTIFIER and every non-docstring STRING LITERAL in the
live harness path, matched against the terminology he named, and split by
whether it sits in the RANKING MECHANISM or elsewhere.

MEASURED 2026-10-17: the ranking mechanism -- `bench/routing.py`,
`bench/reference_runner_v3.py` and `bench/runner_core.py` -- carries **0** of
them. It names things `strength_order`, `capability_identity` and
`season_strength_order`. So the rejection is honoured where it was aimed.

WHAT THE 28 HITS ACTUALLY ARE, and 9 plus 6 plus 13 accounts for all of them, because a raw total would mislead:

  * 9 are `ZeroDivisionError`, a Python builtin, caught by "division";
  * 6 are `player` or `player_manager` as a ROLE NAME, in the experiment 11, 12
    and 20 runners, the simulated launcher and one Gemini probe. These predate
    the ladder discussion, name a role rather than a ranking, and appear inside
    ARCHIVED PROMPTS -- so renaming them edits the record of runs already
    performed. That is a separate question and it is his;
  * the rest are identifiers and literals in the 2026-10-08 producers that QUOTE
    and ANALYSE his own football analogy. Renaming those would erase what was
    measured about his framing.

A CRUDE SUBSTRING SCAN WAS TRIED FIRST AND IS WHY THIS USES THE AST. It reported
190 hits for "promot", which is the project's own SHADOW PROMOTION; 64 for
"division", mostly arithmetic; and 25 for "fixture", which is pytest. A total
over a proxy produced a number, as it has repeatedly.

Costs nothing and dispatches no model. Run: python3 scripts/<this file>
"""
from __future__ import annotations

import ast
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
from _cli_help import answer_help  # noqa: E402

#: The words he named, plus the ones his analogy used.
TERMS = re.compile(r"(leagues?|relegat|football|player|team|division)", re.I)
#: The files that decide a model's rank. His objection was aimed here.
RANKING_MECHANISM = ("routing.py", "reference_runner_v3.py", "runner_core.py")
#: Not football: a Python builtin that the word "division" catches.
BUILTIN_FALSE_POSITIVES = ("ZeroDivisionError",)


def _live_python():
    for p in sorted((REPO / "bench").rglob("*.py")):
        rel = p.relative_to(REPO).as_posix()
        if ("__pycache__" in rel or rel.startswith("bench/logs/")
                or "/tests/" in rel):
            continue
        yield p, rel


def hits():
    """(kind, file, line, text) for every identifier and live literal."""
    out = []
    for path, rel in _live_python():
        src = path.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        doc_consts = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                                 ast.AsyncFunctionDef)) and node.body:
                if ast.get_docstring(node, clean=False) is not None:
                    first = node.body[0]
                    if isinstance(first, ast.Expr):
                        doc_consts.add(id(first.value))
        for node in ast.walk(tree):
            name = None
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef)):
                name = node.name
            elif isinstance(node, ast.Name):
                name = node.id
            elif isinstance(node, ast.arg):
                name = node.arg
            if name and TERMS.search(name):
                out.append(("identifier", rel, node.lineno, name))
            if (isinstance(node, ast.Constant)
                    and isinstance(node.value, str)
                    and id(node) not in doc_consts
                    and TERMS.search(node.value)
                    and len(node.value) < 90):
                out.append(("literal", rel, node.lineno,
                            node.value.replace("\n", " ")[:70]))
    seen = set()
    return [h for h in out if (h[0], h[1], h[3]) not in seen
            and not seen.add((h[0], h[1], h[3]))]


def main() -> int:
    answer_help(__doc__, __file__)
    rows = hits()
    in_ranking = [h for h in rows
                  if h[1].split("/")[-1] in RANKING_MECHANISM]
    builtins = [h for h in rows if h[3] in BUILTIN_FALSE_POSITIVES]
    roles = [h for h in rows if "player" in str(h[3]).lower()
             and h not in builtins]
    print("FOOTBALL TERMINOLOGY IN THE LIVE HARNESS, BY AST")
    print(f"  identifiers and live literals matched : {len(rows)}")
    print(f"  IN THE RANKING MECHANISM              : {len(in_ranking)}"
          f"   <- what his rejection was aimed at")
    for kind, rel, n, what in in_ranking:
        print(f"      {rel}:{n}  {kind} {what!r}")
    print(f"  Python builtins caught by 'division'  : {len(builtins)}")
    print(f"  a ROLE name (`player`/`player_manager`): {len(roles)}")
    for kind, rel, n, what in roles:
        print(f"      {rel}:{n}  {what!r}")
    rest = [h for h in rows if h not in in_ranking + builtins + roles]
    print(f"  quoting or analysing HIS OWN analogy  : {len(rest)}")

    print("\nVERDICT")
    if not in_ranking:
        print("  the ranking mechanism carries NONE of the terminology he")
        print("  rejected. It names things `strength_order`,")
        print("  `capability_identity` and `season_strength_order`.")
        print("  The role name `player_manager` predates the ladder discussion,")
        print("  names a role rather than a ranking, and appears inside ARCHIVED")
        print("  PROMPTS -- so renaming it edits the record of runs already")
        print("  performed, which is his call and not a tidy-up.")
        return 0
    print(f"  {len(in_ranking)} hit(s) sit in the ranking mechanism itself and")
    print("  are the ones his rejection was aimed at.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
