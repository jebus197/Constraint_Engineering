#!/usr/bin/env python3
"""Task A6, half I11: which tests assert on the SOURCE TEXT of a Python module?

`execute-do-not-grep` names one direction of this: a test that reads source can
miss a producer and a consumer that disagree, because each describes itself
correctly. I11 names the CONVERSE, and it is the one nobody had measured: such a
test BREAKS ON AN EDIT THAT CHANGES NOTHING IT ASSERTS, inventing a defect where
there is none.

THE CONVERSE IS NOT HYPOTHETICAL. On 2026-09-10 and 2026-09-11 it fired 4 times
in one day, every time on a CORRECT change:

  1. `test_panel_cwd_reaches_worker_threads` searched a 400-CHARACTER WINDOW of
     the runner for an assignment 8 lines away. A comment grew; the window
     stopped reaching; red while the wiring was right.
  2. `test_the_dispatcher_sets_the_cwd_per_worker_not_on_main` required the
     literal `set_panel_cwd(_PANEL_SANDBOX_CWD)`. Per-seat sandboxes renamed the
     argument; red while the behaviour improved.
  3. `test_the_seat_map_exists_and_is_read_by_dispatch` inspected one function's
     body. The confinement was extracted into a helper hours later; red.
  4. `test_branch_supplies_versions` required a paragraph the script prints only
     on 1 of its 2 paths.

Numbers 2 and 3 were written by the assistant the same day they broke.

WHAT THIS MEASURES. Per TEST FUNCTION, not per file: does it assert that a
string literal appears in the text of a `.py` file it read? That is the fragile
form. Reading a NOTE and asserting on it is not the same thing -- a note IS text,
and there is nothing else to execute.

WHAT IT DELIBERATELY DOES NOT DO. It does not call them defects. Some are the
only available check: a shell hook has no importable surface, and a ratchet on a
list that must not shrink is legitimately about the text. The census names them
so the class can be reasoned about; the companion script mutates a sample to find
out which ones actually break on an irrelevant edit.
"""
from __future__ import annotations

import ast
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
TESTS = REPO / "bench" / "tests"

#: A path expression that names Python SOURCE rather than a note or a fixture.
_SOURCE_HINT = (".py", "reference_runner", "pre-commit", "hooks")


def _mentions_source(node: ast.AST) -> bool:
    for n in ast.walk(node):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            if any(h in n.value for h in _SOURCE_HINT):
                return True
    return False


def _source_text_names(fn: ast.FunctionDef, module: ast.Module) -> set[str]:
    """Local names bound to the text of a Python source file.

    Module-level bindings count too: the common shape is
    `SRC = (REPO / "bench/x.py").read_text()` at the top and the assertion inside
    a test, which is 2 statements and one fact.
    """
    names: set[str] = set()
    assigns = []
    for scope in (module, fn):
        for node in ast.walk(scope):
            if not isinstance(node, ast.Assign):
                continue
            assigns.append(node)
            val = node.value
            if (isinstance(val, ast.Call)
                    and getattr(val.func, "attr", None) in ("read_text", "read_bytes")
                    and _mentions_source(val)):
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        names.add(t.id)

    # PROPAGATE THROUGH INTERMEDIATES, and this was not optional. The first
    # version tracked only names bound DIRECTLY to `read_text()`, and a positive
    # control built from 3 KNOWN instances -- the 4 that broke in this project on
    # 2026-09-10 and 09-11 -- detected 1 of 3. The 2 it missed are the commonest
    # shapes there are:
    #     window = src[i:i + 400];        assert "lit" in window
    #     body   = src[src.index("x"):];  assert "lit" in body
    # A census whose detector cannot see its own worked examples is a fact about
    # the detector. `51 of 5026` was that number before this loop existed.
    changed = True
    while changed:
        changed = False
        for node in assigns:
            used = {n.id for n in ast.walk(node.value) if isinstance(n, ast.Name)}
            if not (used & names):
                continue
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id not in names:
                    names.add(t.id)
                    changed = True
    return names


def _asserts_literal_in(fn: ast.FunctionDef, names: set[str]) -> list[str]:
    """Assertions of the form `"literal" in <source text>`."""
    hits = []
    for node in ast.walk(fn):
        if not isinstance(node, ast.Assert):
            continue
        for cmp_ in ast.walk(node):
            if not isinstance(cmp_, ast.Compare):
                continue
            if not any(isinstance(o, (ast.In, ast.NotIn)) for o in cmp_.ops):
                continue
            left = cmp_.left
            right = cmp_.comparators[0] if cmp_.comparators else None
            lit = (isinstance(left, ast.Constant)
                   and isinstance(left.value, str) and left.value)
            tgt = getattr(right, "id", None) or getattr(
                getattr(right, "func", None), "attr", None)
            if lit and tgt in names:
                hits.append(left.value[:60])
            # `<source>.index("literal")` and `"lit" in <src>[a:b]` shapes
            elif lit and isinstance(right, ast.Subscript) \
                    and getattr(right.value, "id", None) in names:
                hits.append(left.value[:60])
    return hits


def survey():
    out = []
    total_fns = 0
    for path in sorted(TESTS.glob("test_*.py")):
        try:
            module = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for fn in ast.walk(module):
            if not isinstance(fn, ast.FunctionDef) or not fn.name.startswith("test"):
                continue
            total_fns += 1
            names = _source_text_names(fn, module)
            if not names:
                continue
            hits = _asserts_literal_in(fn, names)
            if hits:
                out.append((path.name, fn.name, fn.lineno, hits))
    return out, total_fns


def main() -> int:
    rows, total = survey()
    print(f"test functions scanned                 : {total}")
    print(f"asserting a literal is in Python SOURCE: {len(rows)}")
    by_file: dict[str, int] = {}
    for name, _fn, _ln, _h in rows:
        by_file[name] = by_file.get(name, 0) + 1
    ranked = sorted(by_file.items(), key=lambda kv: -kv[1])
    shown = ranked[:12]
    print(f"across {len(by_file)} file(s); the heaviest {len(shown)}:")
    for name, n in shown:
        print(f"    {n:3d}  {name}")
    if len(ranked) > len(shown):
        # A LIST CUT TO N UNDER A HEADING THAT READS AS COMPLETE IS A SILENT
        # FALSEHOOD. The project's own guard says so and caught this one.
        rest = sum(n for _f, n in ranked[len(shown):])
        print(f"    ... and {len(ranked) - len(shown)} more file(s) carrying "
              f"{rest} further assertion(s), not shown")

    if not total:
        return 0
    from statsmodels.stats.proportion import proportion_confint
    k = len(rows)
    lo, hi = proportion_confint(k, total, method="wilson")
    lo_c, hi_c = proportion_confint(k, total, method="beta")
    from scipy.stats import beta as sbeta
    hi_s = 1.0 if k == total else sbeta.ppf(0.975, k + 1, total - k)
    print(f"\n  {k}/{total} = {k / total:.4%}")
    print(f"  Wilson 95%          : [{lo:.4%}, {hi:.4%}]  (statsmodels)")
    print(f"  Clopper-Pearson 95% : [{lo_c:.4%}, {hi_c:.4%}]  (statsmodels/beta)")
    print(f"  Clopper-Pearson 95% : [{lo_c:.4%}, {hi_s:.4%}]  (scipy cross-check, "
          f"upper agrees to {abs(hi_s - hi_c):.1e})")
    print("\nTHIS IS A CENSUS, NOT A VERDICT. Some of these are the only check "
          "available -- a\nshell hook has no importable surface. Which of them "
          "break on an IRRELEVANT edit is\nthe question, and it is answered by "
          "mutation, not by counting.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
