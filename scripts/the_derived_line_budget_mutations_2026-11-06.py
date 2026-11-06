#!/usr/bin/env python3
"""Mutation harness for the DERIVED line budgets, 2026-11-06.

His ruling raised 2 ceilings that were never his. Raising a cap is the easy
half; the half that matters is that the check still catches what a cap was
there to catch. So this pads and truncates the GENERATOR -- not the test --
and requires the named assertion to go red each time.

ANCHORS COME FROM THE AST, NOT FROM A STRING MATCH. Both render functions
end with the byte-identical line `return "\\n".join(L) + "\\n"`, so a textual
anchor would be ambiguous and a `replace` would hit the wrong function. The
harness parses the module, finds each function by name, and rewrites that
function's own return line by index.

The subject is restored from the bytes this script read, never from git.
"""
from __future__ import annotations
import ast, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SUBJ = ROOT / "scripts" / "morning_report_build_2026-10-12.py"
TEST = ROOT / "bench" / "tests" / "test_the_morning_report_is_generated_2026-10-12.py"
MD_NODE = "TestItStaysInsideTheStandard::test_the_report_is_within_the_line_limit"
TTS_NODE = "TestTheTTSVersionIsSpeakable::test_it_is_within_the_tts_line_limit"


def _return_line(src: str, fname: str) -> int:
    """1-indexed line of the single return in `fname`, derived from the AST."""
    tree = ast.parse(src)
    node = next((n for n in ast.walk(tree)
                 if isinstance(n, ast.FunctionDef) and n.name == fname), None)
    if node is None:
        raise SystemExit(f"ANCHOR NOT FOUND -- no function {fname}; harness is stale")
    rets = [r for r in ast.walk(node) if isinstance(r, ast.Return)]
    if len(rets) != 1:
        raise SystemExit(f"ANCHOR AMBIGUOUS -- {fname} has {len(rets)} returns")
    return rets[0].lineno


def _rewrite(src: str, fname: str, expr: str) -> str:
    n = _return_line(src, fname)
    lines = src.splitlines(keepends=True)
    indent = " " * (len(lines[n - 1]) - len(lines[n - 1].lstrip()))
    lines[n - 1] = f"{indent}return {expr}\n"
    return "".join(lines)


def mutations(src: str):
    return [
        ("M1 render_md pads 400 lines of nothing",
         _rewrite(src, "render_md", '"\\n".join(L) + "\\n" + "\\n" * 400'),
         MD_NODE, "the ceiling"),
        ("M2 render_md truncates to 20 lines",
         _rewrite(src, "render_md", '"\\n".join(L[:20]) + "\\n"'),
         MD_NODE, "the floor"),
        ("M3 render_md emits no item headings (derivation would be vacuous)",
         _rewrite(src, "render_md",
                  '"\\n".join(l for l in L if not l.startswith("### ")) + "\\n"'),
         MD_NODE, "anti-vacuity"),
        ("M4 render_tts pads 800 lines of nothing",
         _rewrite(src, "render_tts", '"\\n".join(L) + "\\n" + "\\n" * 800'),
         TTS_NODE, "the spoken ceiling"),
        ("M5 render_tts truncates to 20 lines",
         _rewrite(src, "render_tts", '"\\n".join(L[:20]) + "\\n"'),
         TTS_NODE, "the spoken floor"),
    ]


def main() -> int:
    found = SUBJ.read_bytes()
    src = found.decode()
    muts = mutations(src)
    print(f"subject: {SUBJ.relative_to(ROOT)}")
    print(f"guard:   {TEST.relative_to(ROOT)}")
    print(f"render_md return at L{_return_line(src, 'render_md')}, "
          f"render_tts at L{_return_line(src, 'render_tts')}  (AST-derived)")
    print(f"\n{len(muts)} mutations, each must turn its NAMED test red\n")
    red = 0
    try:
        for label, mutated, node, what in muts:
            if mutated == src:
                print(f"  INERT  {label}  <- changed nothing; harness is stale")
                continue
            SUBJ.write_text(mutated)
            r = subprocess.run([sys.executable, "-m", "pytest",
                                f"{TEST}::{node.replace('::', '::')}",
                                "-q", "--no-header"],
                               cwd=ROOT, capture_output=True, text=True, timeout=900)
            if r.returncode != 0:
                red += 1
                print(f"  RED    {label}\n           -> {what} caught it")
            else:
                print(f"  GREEN  {label}  <- {what} DID NOT CATCH THIS")
    finally:
        SUBJ.write_bytes(found)
        assert SUBJ.read_bytes() == found, "RESTORE FAILED -- the subject is damaged"
        print(f"\nsubject restored byte-identical ({len(found)} bytes)")
    print(f"\n{red} of {len(muts)} mutations red")
    return 0 if red == len(muts) else 1


if __name__ == "__main__":
    raise SystemExit(main())
