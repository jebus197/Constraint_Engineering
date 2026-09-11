#!/usr/bin/env python3
"""Task A18: are the exp56 config off-switches read by anything, or not?

THE ENTRY SAYS THREE FIELDS ARE READ BY NONE OF THE 210 RUNNER MODULES,
"resolved by AST, not by grep". Two of the three are read. The third is not, and
the arm's intent is achieved anyway by the key beside it.

  merge_arbitration_enabled   READ. `reference_runner_v3.py:12638`,
                              `if getattr(cfg, "merge_arbitration_enabled", False)`.
  immune_memory_enabled       READ. `reference_runner_v3.py:14984`, same form.
  _ouroboros.max_papers_per_round
                              NOT read anywhere in production. Its SIBLING in
                              the same block, `api_access`, IS read at
                              `reference_runner_v3.py:9423` -- so the block
                              reaches the runner and exactly 1 of its 2 keys is
                              consulted.

WHY THE SWEEP MISSED THEM, and it is this project's recurring shape. An AST scan
for attribute access resolves `cfg.merge_arbitration_enabled` and reports zero
for `getattr(cfg, "merge_arbitration_enabled", False)` -- which is an attribute
read WRITTEN AS A STRING. The sweep chose AST over grep for good reasons and
then looked for one of the two forms the language offers.

AND THE ARM IS NOT LYING TO ITS READER. `max_papers_per_round = 0` is redundant
rather than inert: the arm's stated intent is "external literature retrieval
OFF", and `api_access: []` achieves it through the key that IS read. A reader who
believed the capability was disabled for the experiment was RIGHT, for a
different reason than the one they would have guessed.

THIS SCRIPT RESOLVES BOTH FORMS, so the question can be asked again without
re-learning the lesson.
"""
from __future__ import annotations

import argparse
import ast
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]


def production_sources():
    for base in ("bench", "scripts"):
        for p in sorted((REPO / base).rglob("*.py")):
            if "tests" in p.parts:
                continue
            yield p


def readers_of(field: str) -> list[str]:
    """Every production site that READS `field`, in either form.

    BOTH FORMS, because the language offers both and a scanner that resolves one
    reports a false zero for the other:
      * `cfg.field`                      -- an ast.Attribute load
      * `getattr(cfg, "field", default)` -- the same read, written as a string
      * `d["field"]` / `d.get("field")`  -- for config dicts, which is how the
                                            `_ouroboros` block is consulted
    """
    out = []
    for p in production_sources():
        try:
            tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        except (OSError, SyntaxError):
            continue
        rel = str(p.relative_to(REPO))
        for n in ast.walk(tree):
            if isinstance(n, ast.Attribute) and n.attr == field \
                    and isinstance(n.ctx, ast.Load):
                out.append(f"{rel}:{n.lineno} cfg.{field}")
            elif isinstance(n, ast.Call):
                fname = getattr(n.func, "id", None) or getattr(n.func, "attr", None)
                if fname in ("getattr", "get") and n.args:
                    for arg in n.args[:2]:
                        if isinstance(arg, ast.Constant) and arg.value == field:
                            out.append(f"{rel}:{n.lineno} {fname}(..., {field!r})")
            elif isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant) \
                    and n.slice.value == field and isinstance(n.ctx, ast.Load):
                out.append(f"{rel}:{n.lineno} [{field!r}]")
    return sorted(set(out))


def declared_fields(config_glob: str) -> dict:
    """Every leaf key in the named configs, with the file that carries it."""
    out: dict[str, set] = {}

    def walk(o, prefix=""):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, (dict, list)):
                    walk(v, f"{prefix}{k}.")
                else:
                    out.setdefault(k, set()).add(prefix + k)

    for f in sorted(REPO.glob(config_glob)):
        try:
            walk(json.loads(f.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            continue
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--configs", default="bench/exp56_configs/*.json")
    ap.add_argument("--field", action="append",
                    help="check only these fields; default is every leaf key")
    a = ap.parse_args()

    fields = a.field or sorted(declared_fields(a.configs))
    unread, read = [], []
    for f in fields:
        if f.startswith("_"):          # a `_note` key is documentation
            continue
        sites = readers_of(f)
        (read if sites else unread).append((f, sites))

    print(f"config leaf keys examined: {len(read) + len(unread)}")
    print(f"  read by production code : {len(read)}")
    print(f"  read by nothing         : {len(unread)}")
    print("\nREAD BY NOTHING:")
    for f, _s in unread:
        print(f"    {f}")
    if not unread:
        print("    none")

    if a.field:
        print("\nper field:")
        for f, sites in read + unread:
            print(f"  {f}: {len(sites)} reader(s)")
            for s in sites[:4]:
                print(f"      {s}")

    n = len(read) + len(unread)
    if n:
        from statsmodels.stats.proportion import proportion_confint
        from scipy.stats import beta as sbeta
        k = len(unread)
        lo, hi = proportion_confint(k, n, method="wilson")
        lo_c, hi_c = proportion_confint(k, n, method="beta")
        hi_s = 1.0 if k == n else sbeta.ppf(0.975, k + 1, n - k)
        print(f"\nunread rate: {k}/{n} = {k / n:.4%}")
        print(f"  Wilson 95%          : [{lo:.4%}, {hi:.4%}]  (statsmodels)")
        print(f"  Clopper-Pearson 95% : [{lo_c:.4%}, {hi_c:.4%}]  (statsmodels/beta)")
        print(f"  Clopper-Pearson 95% : [{lo_c:.4%}, {hi_s:.4%}]  (scipy, agrees "
              f"to {abs(hi_s - hi_c):.1e})")

    print("\nBOTH ACCESS FORMS ARE RESOLVED. `cfg.field` and "
          "`getattr(cfg, \"field\", ...)` are\nthe same read; a scanner that "
          "resolves only the first reports a false zero for the\nsecond, which "
          "is what put 2 wired fields on the A18 list.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
