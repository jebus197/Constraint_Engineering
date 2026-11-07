#!/usr/bin/env python3
"""Does the --help repair need BOTH halves? Measured, because composability is.

HIS 2026-10-02 STANDARD, which this project has applied in the weak sense 10
times out of 10: a composed fix may be recommended ONLY with a committed
measurement showing it dominates either part alone on a NAMED property. Where a
single fix does as well, the single fix is preferred. So the claim "both halves
are needed" is tested here rather than asserted.

THE NAMED PROPERTY is the offender count of
`bench/tests/test_help_never_acts_2026-09-11.py::test_every_script_that_writes_answers_help`
-- scripts that match `WRITES` and fail `answers_help`. Lower is better; 0 is
green.

THE 2 HALVES.
  A  ADD the helper to the 10 scripts that genuinely have none.
  B  TEACH the matcher to resolve `from _cli_help import answer_help as X`.
     15 of the 205 scripts that call it bind it under an alias, so the matcher
     is blind to all 15; in 13 that blindness is latent and in 2 it is red.

Both are simulated IN MEMORY against the committed matcher logic. Nothing is
written and no script is edited by this file.

Exit 0 iff all 4 conditions were computed.
"""
from __future__ import annotations

import ast
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
MATCHERS = REPO / "bench" / "tests" / "test_help_never_acts_2026-09-11.py"

HELPER_BLOCK = '''

if __name__ == "__main__":
    import pathlib as _pl
    sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
    from _cli_help import answer_help as _answer_help
    _answer_help(__doc__, __file__)
'''


def _load():
    import importlib.util as iu
    spec = iu.spec_from_file_location("hna", MATCHERS)
    m = iu.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _alias_names(tree) -> set:
    out = {"answer_help"}
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom) and n.module == "_cli_help":
            for a in n.names:
                if a.name == "answer_help" and a.asname:
                    out.add(a.asname)
    return out


def _answers(src: str, *, alias_aware: bool) -> bool:
    """`answers_help`, with the alias resolution switchable."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return False
    helpers = _alias_names(tree) if alias_aware else {"answer_help"}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
        if name == "ArgumentParser":
            return True
        if name in helpers:
            return True
    return False


def main(argv) -> int:
    m = _load()
    scripts = sorted((REPO / "scripts").glob("*.py"))
    src = {p: p.read_text(encoding="utf-8", errors="replace") for p in scripts}

    #: the 10 that have NO helper call under ANY name -- half A's subjects
    no_helper = [p for p in scripts
                 if m.WRITES.search(src[p]) and not _answers(src[p], alias_aware=True)]
    #: the ones the matcher misses ONLY because of the alias -- half B's subjects
    alias_only = [p for p in scripts
                  if m.WRITES.search(src[p])
                  and _answers(src[p], alias_aware=True)
                  and not _answers(src[p], alias_aware=False)]

    print("=" * 78)
    print("DOES THE --help REPAIR NEED BOTH HALVES?")
    print("=" * 78)
    print(f"half A's subjects (no helper at all, and they WRITE): {len(no_helper)}")
    for p in no_helper:
        print(f"    scripts/{p.name}")
    print(f"half B's subjects (helper present but ALIASED, and they WRITE): "
          f"{len(alias_only)}")
    for p in alias_only:
        print(f"    scripts/{p.name}")

    def offenders(*, add_helper: bool, alias_aware: bool) -> list:
        out = []
        for p in scripts:
            s = src[p]
            if add_helper and p in no_helper:
                s = s + HELPER_BLOCK
            if _answers(s, alias_aware=alias_aware):
                continue
            if m.WRITES.search(s):
                out.append(f"scripts/{p.name}")
        return out

    rows = [
        ("neither half (today)", offenders(add_helper=False, alias_aware=False)),
        ("A only: add the helper to the 10",
         offenders(add_helper=True, alias_aware=False)),
        ("B only: teach the matcher the alias",
         offenders(add_helper=False, alias_aware=True)),
        ("A and B composed", offenders(add_helper=True, alias_aware=True)),
    ]
    print("\nOFFENDER COUNT under each condition (lower is better; 0 is green):")
    w = max(len(r[0]) for r in rows)
    for label, offs in rows:
        print(f"  {label:<{w}} : {len(offs):>3}"
              + ("   GREEN" if not offs else "   still red: " + ", ".join(
                  o.split('/')[-1] for o in offs[:4])))

    a_only, b_only, both = len(rows[1][1]), len(rows[2][1]), len(rows[3][1])
    print("\n" + "=" * 78)
    if both < min(a_only, b_only):
        print("VERDICT: THE COMPOSED FIX DOMINATES on the named property.")
        print(f"  A alone leaves {a_only}; B alone leaves {b_only}; together {both}.")
        print("  Neither half reaches 0, so neither is sufficient and the")
        print("  composition is NECESSARY rather than merely possible -- which")
        print("  is the strong sense his 2026-10-02 rule asks for.")
    elif both == min(a_only, b_only):
        print("VERDICT: THE COMPOSITION DOES NOT DOMINATE. A single half does as")
        print(f"  well ({min(a_only, b_only)}), so by his rule the SINGLE fix is")
        print("  PREFERRED and the composed one must not be recommended.")
    else:
        print("VERDICT: the composition is WORSE than a half. Do not ship it.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    import pathlib as _pl
    sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
    from _cli_help import answer_help as _answer_help
    _answer_help(__doc__, __file__, takes_no_arguments=True)
    raise SystemExit(main(sys.argv[1:]))
