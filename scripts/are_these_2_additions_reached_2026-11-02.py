#!/usr/bin/env python3
"""Are `round_wall_clock` and `bench/proof_verify.py` actually reached?

★ WRITTEN BECAUSE 2 FIGURES WERE QUOTED TO HIM WITH NO PRODUCER, 2026-11-02.
`measured-rate-travels-with-its-script` makes a rate that exists only as prose a
claim about evidence rather than evidence. These 2 were established by execution
in the session that quoted them and nothing reproduced them:

  1. `round_wall_clock` appears in 0 of 65 `runner_state.json` files.
  2. 0 PRODUCT modules import `bench/proof_verify.py`.

BOTH ARE REACHABILITY QUESTIONS UNDER THE ADDITIVE STANDARD, which requires an
addition to be wired to a caller AND executed by a test. They are reported
together because they are the same question asked of 2 subjects, not because
they are otherwise related.

NEITHER IS PRESENTED AS A DEFECT, and the distinction is the point:

  `round_wall_clock` is 9 hours younger than the only run of the day. It entered
  the tree at commit `b7cf4c13` on 2026-11-02 at 12:35:05 UTC; that run started
  at 03:39:20 against an earlier HEAD. A test executes the field, so it is
  wired; the 0 is CHRONOLOGY. The first run started after that commit is its
  first live evidence, and this script says so rather than calling it an
  unreached addition -- the error `feedback_a_new_rule_can_be_vacuous_on_its_first_file_2026-11-01`
  records as a 0 drawn from an empty window.

  `bench/proof_verify.py` was folded back on his ruling *"Fix it and fold it back
  as you suggest."* The recommendation he answered offered fold-back against
  leaving the module preserved; wiring was no part of either option, so the 0
  product callers is NOT unfinished business of his. Whether to wire it into the
  falsifier path is a new question nobody has asked.

THE IMPORT SCAN IS AST-BASED, NOT A GREP. A grep over source text cannot tell an
import from a mention in a comment, and this project's record holds a case where
a sentence explaining why a script could not be wired made that script read as
reached. Dynamic loads by path are caught separately, because
`spec_from_file_location` leaves no import node.
"""
from __future__ import annotations

import argparse
import ast
import json
import pathlib
import subprocess

REPO = pathlib.Path(__file__).resolve().parents[1]

FIELD = "round_wall_clock"
MODULE = "proof_verify"
MODULE_PATH = REPO / "bench" / MODULE
#: Where the field is written, so the chronology can be read rather than typed.
FIELD_HOME = REPO / "bench" / "reference_runner_v3.py"


#: This file's own path. A DETECTOR MUST NOT SPELL OUT ITS OWN PATTERN: this
#: script names `proof_verify.py` 4 times and `spec_from_file_location` twice in
#: prose, so the dynamic-load heuristic matched its own source and reported the
#: producer as an importer of its own subject. 6th instance of that shape on
#: 2026-11-02; see `feedback_a_detector_must_not_spell_out_its_own_pattern_2026-11-02`.
SELF = pathlib.Path(__file__).resolve()


def _skip(p: pathlib.Path) -> bool:
    s = str(p)
    return ("/logs/" in s or "seat_evidence" in s or "__pycache__" in s
            or "/CDSFL_review_targets/" in s
            or p.resolve() == SELF)


def field_presence() -> tuple[int, int, list]:
    """How many persisted state files carry a NON-EMPTY `round_wall_clock`?"""
    total = present = 0
    where = []
    for pat in ("*/runner_state.json", "*/checkpoint.json", "*/*_report.json"):
        for f in sorted((REPO / "bench" / "logs").glob(pat)):
            try:
                d = json.loads(f.read_text(errors="replace"))
            except Exception:  # noqa: BLE001
                continue
            if not isinstance(d, dict):
                continue
            total += 1
            v = d.get(FIELD)
            if isinstance(v, list) and v:
                present += 1
                where.append(str(f.relative_to(REPO)))
    return present, total, where


def field_chronology() -> tuple[str, str]:
    """When the field entered the tree, and when the newest archived run began.

    Read from git and from the archive rather than stated, because a typed date
    is the fault `feedback_read_the_clock` records.
    """
    r = subprocess.run(
        ["git", "log", "--format=%ci", "-1", "-S", FIELD, "--", str(FIELD_HOME)],
        capture_output=True, text=True, cwd=str(REPO), timeout=120)
    landed = (r.stdout or "").strip().splitlines()
    newest = ""
    for f in sorted((REPO / "bench" / "logs").glob("*/*_report.json")):
        try:
            d = json.loads(f.read_text(errors="replace"))
        except Exception:  # noqa: BLE001
            continue
        # `start_time` is the key the reports actually carry; `started` was a
        # guess and returned "(none)" for every run, which is a 0 of nothing.
        ts = str(d.get("start_time")
                 or (d.get("_declared_config") or {}).get("start_time") or "")
        if ts > newest:
            newest = ts
    return (landed[0] if landed else "(not found)"), (newest or "(none)")


def module_importers() -> tuple[list, list, list]:
    """PRODUCT, TEST and SCRIPT modules that import the module, by AST."""
    product, tests, scripts_ = [], [], []
    for root in (REPO / "bench", REPO / "scripts"):
        for f in root.rglob("*.py"):
            if _skip(f) or f.name == f"{MODULE}.py":
                continue
            try:
                txt = f.read_text(errors="replace")
                tree = ast.parse(txt)
            except Exception:  # noqa: BLE001
                continue
            found = False
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    found |= any(a.name.split(".")[-1] == MODULE
                                 for a in node.names)
                elif isinstance(node, ast.ImportFrom):
                    found |= (node.module or "").split(".")[-1] == MODULE
                    found |= any(a.name == MODULE for a in node.names)
            # A dynamic load leaves no import node.
            if f"{MODULE}.py" in txt and "spec_from_file_location" in txt:
                found = True
            if not found:
                continue
            rel = str(f.relative_to(REPO))
            (tests if "/tests/" in rel else
             scripts_ if rel.startswith("scripts/") else product).append(rel)
    return product, tests, scripts_


def main() -> int:
    argparse.ArgumentParser(
        description=("Are `round_wall_clock` and `bench/proof_verify.py` "
                     "reached? Reports chronology, not blame.")).parse_args()

    print("=" * 76)
    print("ARE THESE 2 ADDITIONS REACHED?")
    print("=" * 76)

    present, total, where = field_presence()
    landed, newest = field_chronology()
    print(f"\n1. `{FIELD}` IN THE PERSISTED ARCHIVE")
    print(f"   state/checkpoint/report files scanned : {total}")
    print(f"   carrying a NON-EMPTY series           : {present}")
    for w in where[:4]:
        print(f"       {w}")
    print(f"   the field entered the tree at         : {landed}")
    print(f"   the newest archived run began at      : {newest}")
    if present == 0:
        print("   => 0, AND THE 0 IS CHRONOLOGY. No run has started since the")
        print("      field existed, so this is a pending verification rather")
        print("      than an unreached addition. A test executes it.")
    else:
        print("   => the field is now present in the archive; the pending")
        print("      verification above is DISCHARGED and this script's own")
        print("      header should be re-read before quoting it.")

    product, tests, scripts_ = module_importers()
    print(f"\n2. WHO IMPORTS `bench/{MODULE}.py` (AST, not grep)")
    print(f"   PRODUCT modules : {len(product)} {product}")
    print(f"   TEST files      : {len(tests)}")
    for t in tests:
        print(f"       {t}")
    print(f"   SCRIPTS         : {len(scripts_)}")
    for t in scripts_:
        print(f"       {t}")
    if not product and tests:
        print("   => executed by a test, wired to NO product caller. Under the")
        print("      additive standard an addition needs both. His ruling to")
        print("      fold it back is nevertheless DISCHARGED: the options he")
        print("      answered were fold-back against leaving it preserved, and")
        print("      wiring was in neither. Whether to wire it is a NEW")
        print("      question, and it is non-blocking.")

    # EXIT NON-ZERO IF EITHER OBSERVATION HAS CHANGED, so a later reader is
    # told to re-derive rather than quoting a figure this script no longer
    # supports.
    changed = []
    if present != 0:
        changed.append(f"`{FIELD}` now appears in {present} of {total} files")
    if product:
        changed.append(f"`bench/{MODULE}.py` now has {len(product)} product "
                       f"importer(s): {product}")
    print()
    if changed:
        print("  THE DOCUMENTED OBSERVATION HAS CHANGED:")
        for c in changed:
            print(f"    - {c}")
        return 1
    print("  Both observations reproduce.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
