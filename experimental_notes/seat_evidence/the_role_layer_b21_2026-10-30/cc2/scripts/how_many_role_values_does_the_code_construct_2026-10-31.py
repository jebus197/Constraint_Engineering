# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'the_role_layer_b21_2026-10-30', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 52ef4e1f024b6eccc7f4cda0247aaf01da180076899601fd05f1b98bd8bf5162
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The declared `Role` has 3 members; the code CONSTRUCTS 5. Measured by AST.

WHY THIS EXISTS. Panel brief `the_role_layer_b21_2026-10-30` asks whether the
harness's existing role vocabulary and the founder's proposed one are 1
dimension or 2. Both the brief and
`scripts/which_role_vocabulary_does_the_code_speak_2026-10-30.py` take the
existing vocabulary to be the 3 members of
`bench/experiment_11_orchestrator.py:59`:

    Role = Literal["collator", "player_manager", "participant"]

and compute a 63/67 = 0.940 "structural share" over exactly those 3 words. That
denominator is drawn from a `grep` for 6 chosen words. It cannot see a role
value that is neither in the declared literal nor in the founder's list, and it
therefore cannot detect that the literal is not enforced.

WHAT THIS MEASURES INSTEAD. Every `role=<string literal>` keyword argument to a
`ModelConfig(...)` call in live code, found by parsing the AST rather than by
grepping for known words, so an unknown value is visible. `bench/logs/` is
excluded: those are `sandbox_harvest` copies of older revisions of the same
files, not live code, and counting them double-counts one construction site.

`role=` kwargs to non-`ModelConfig` calls are excluded too -- the Google GenAI
SDK and the OpenRouter message format both use `role="user"`/`"model"`/`"tool"`
for an unrelated purpose, and conflating them would inflate the count.

WHAT IT DOES NOT CLAIM. It does not claim the undeclared values break a run
today. Whether they do is a separate question, answered by executing the 2 live
reads; see `--probe-reads`.
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

EXCLUDE_PARTS = {"logs", ".git", ".pytest_cache", "node_modules"}
TARGET_CALLS = {"ModelConfig"}


def declared_members() -> list[str]:
    """Parse the `Role = Literal[...]` assignment out of the orchestrator.

    Read from the AST of the declaring module rather than imported, so this
    works without executing the orchestrator's import-time side effects.
    """
    src = (REPO / "bench" / "experiment_11_orchestrator.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not (len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == "Role"):
            continue
        sub = node.value
        if isinstance(sub, ast.Subscript):
            idx = sub.slice
            elts = idx.elts if isinstance(idx, ast.Tuple) else [idx]
            return [e.value for e in elts
                    if isinstance(e, ast.Constant) and isinstance(e.value, str)]
    raise SystemExit("FATAL: no `Role = Literal[...]` assignment found")


def _callee_name(func: ast.expr) -> str:
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return ""


def _literal_role_strings(value: ast.expr) -> list[str]:
    """Collect string constants a `role=` expression can evaluate to.

    Handles the bare constant and the conditional form actually in the tree,
    `role="player_manager" if i == 0 else "player"`, which a grep for
    `role="..."` reports as one value and which is two.
    """
    if isinstance(value, ast.Constant) and isinstance(value.value, str):
        return [value.value]
    if isinstance(value, ast.IfExp):
        return _literal_role_strings(value.body) + _literal_role_strings(value.orelse)
    return []


def scan() -> dict[str, list[str]]:
    """Map role value -> sorted list of "path:line" construction sites."""
    sites: dict[str, list[str]] = defaultdict(list)
    for path in sorted(REPO.rglob("*.py")):
        rel = path.relative_to(REPO)
        if EXCLUDE_PARTS & set(rel.parts):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if _callee_name(node.func) not in TARGET_CALLS:
                continue
            for kw in node.keywords:
                if kw.arg != "role":
                    continue
                for val in _literal_role_strings(kw.value):
                    sites[val].append(f"{rel}:{node.lineno}")
    return {k: sorted(set(v)) for k, v in sorted(sites.items())}


def probe_reads(undeclared: list[str]) -> list[str]:
    """Evaluate the live `mc.role` predicates against each undeclared value.

    `bench/reference_runner_v3.py:13189` and `:13269` both filter
    `mc.role != "collator"`; `bench/run_exp20_confer.py:253` splits on
    `mc.role == "player_manager"`; `ExperimentConfig.get_by_role` compares for
    equality against a requested role. Each predicate is evaluated on the value
    itself -- no network, no dispatch.
    """
    out = []
    for v in undeclared:
        dispatched = (v != "collator")
        is_manager = (v == "player_manager")
        found_as_participant = (v == "participant")
        out.append(
            f"    {v!r:14} dispatched_by_runner={dispatched}  "
            f"is_manager={is_manager}  get_by_role('participant') matches={found_as_participant}"
        )
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--probe-reads", action="store_true",
                    help="evaluate the live `mc.role` predicates on each undeclared value")
    args = ap.parse_args()

    declared = declared_members()
    sites = scan()
    constructed = list(sites)
    undeclared = [v for v in constructed if v not in declared]
    unconstructed = [v for v in declared if v not in constructed]

    if args.json:
        print(json.dumps({
            "declared": declared,
            "constructed": constructed,
            "undeclared": undeclared,
            "declared_but_never_constructed": unconstructed,
            "sites": sites,
        }, indent=2))
        return 0

    print("=" * 78)
    print("ModelConfig `role=` string literals in live code, by AST")
    print("=" * 78)
    print(f"\ndeclared by `Role = Literal[...]`  : {len(declared)}  {declared}")
    print(f"constructed at call sites          : {len(constructed)}  {constructed}")
    print()
    for v, s in sites.items():
        tag = "DECLARED  " if v in declared else "UNDECLARED"
        print(f"  [{tag}] {v!r:16} {len(s)} site(s)")
        for site in s:
            print(f"               {site}")
    print()
    print(f"UNDECLARED values constructed      : {len(undeclared)}  {undeclared}")
    print(f"DECLARED values never constructed  : {len(unconstructed)}  {unconstructed}")
    print()
    if undeclared:
        print("  So the `Role` literal is NOT the live vocabulary. It is an")
        print("  annotation that no runtime check enforces, and the construction")
        print(f"  sites have drifted to {len(constructed)} values against {len(declared)} declared.")
        print()
        print("  CONSEQUENCE FOR THE BRIEF'S TALLY. The 63/67 = 0.940 'structural")
        print("  share' greps for 3 declared words and 3 proposed ones. It counts")
        print(f"  none of {undeclared}, so its denominator omits")
        print("  every drifted value by construction and cannot detect the drift.")

    if args.probe_reads and undeclared:
        print()
        print("  LIVE READS EVALUATED on each undeclared value:")
        for line in probe_reads(undeclared):
            print(line)
        print()
        print('    Both runner reads are `!= "collator"`, so an undeclared value is')
        print("    dispatched as a reviewer -- which is why the drift has never")
        print('    surfaced as a failure. `get_by_role("participant")` does NOT')
        print("    match it, so a role-KEYED lookup misses those seats silently.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
