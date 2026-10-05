# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'fingerprint_ladder_review_2026-10-05', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 60b77080b6cd19b9e29b34d6961d808cb3f0d4681f2472216a701521f42911fa
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The writer guard exempts 54 scripts on the strength of a parser. Nothing checked it.

`bench/tests/test_help_never_acts_2026-09-11.py::
test_every_script_that_writes_answers_help` exists because `--help` once rewrote a
55,814-byte verbatim panel record as a 1,334-byte stub and exited 0. Its matcher,
`answers_help`, accepts a script on EITHER of two grounds: it calls the shared
`_cli_help.answer_help`, or it constructs an `argparse.ArgumentParser` anywhere.
Its own failure message offers both -- "or give the script a parser".

THE SECOND GROUND CARRIES AN UNCHECKED IMPLICATION. argparse answers `--help`
inside `parse_args()`, not at construction. So "has a parser" only implies "`--help`
is inert" if nothing that changes a file runs BEFORE `parse_args()` on the path
`python3 script.py --help` takes. Constructing a parser at line 400 and writing a
record at line 100 satisfies the matcher and destroys the record, which is the
original defect exactly.

MEASURED 2026-10-05, and it came back clean: of the scripts that write and are
accepted by the matcher on the parser ground ALONE, 0 reach a write before
`parse_args()`. This file converts that measurement into a ratchet, because the
class has already cost 54,480 bytes of a record the founder's standing directive
requires preserved verbatim, and because nothing else in the suite asks the
question.

WHY THIS IS STATIC, and the reason is the same one the sibling file gives: running
every tracked script with `--help` is what must not be done. 15 of 17 runners once
BILLED A LIVE DISPATCH on an unrecognised argument, and spending money is reserved
to the founder. So the entry path is walked on the syntax tree. The proxy is named
rather than hidden: it follows module-level statements, the `__main__` block, and
calls into module-level functions up to 4 frames deep, and it would miss a write
reached through a class method, a decorator, or a dynamic dispatch.

THE POPULATION IS GLOBBED, NOT TAKEN FROM `git ls-files`. The sibling file asserts
`git ls-files` succeeds, which is correct there; in a panel sandbox, a ZIP or a
Zenodo archive there is no `.git` and that assertion fires as a failure blaming
the script. This check does not need the index: `scripts/*.py` is the population,
and an untracked file in that directory is a script a reader can still run.
"""
from __future__ import annotations

import ast
import importlib.util
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "scripts"
SIBLING = REPO / "bench" / "tests" / "test_help_never_acts_2026-09-11.py"

#: argparse answers -h/--help from inside these.
_PARSE_CALLS = frozenset({"parse_args", "parse_known_args", "parse_intermixed_args"})


@pytest.fixture(scope="module")
def sibling():
    """The matcher and the write patterns are taken FROM the guard being audited,
    so this check cannot drift away from the thing it is about."""
    spec = importlib.util.spec_from_file_location("help_never_acts_probe", SIBLING)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _shallow_call_names(stmt):
    """Call names in `stmt`, NOT descending into nested function or class bodies:
    defining a function does not run it."""
    out = []

    def walk(node):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            if isinstance(child, ast.Call):
                out.append(getattr(child.func, "attr", None)
                           or getattr(child.func, "id", None))
            walk(child)

    walk(stmt)
    return out


def _entry_statements(body):
    """Module-level statements that RUN on import or under `__main__`, in order."""
    for st in body:
        if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef,
                           ast.Import, ast.ImportFrom)):
            continue
        if isinstance(st, ast.If) and isinstance(st.test, ast.Compare) \
                and getattr(st.test.left, "id", "") == "__name__":
            yield from _entry_statements(st.body)
            continue
        yield st


def writes_before_parse_args(src: str, write_calls) -> list:
    """Write calls reached on the `--help` entry path before argparse can answer.

    Returns [(call name, line)] in the order they would run. An empty list means
    either that no write precedes `parse_args()`, or that `parse_args()` runs
    first -- which are the same thing for this question.
    """
    tree = ast.parse(src)
    funcs = {n.name: n for n in tree.body
             if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    seen, found = set(), []

    def run(body, depth=0):
        if depth > 4:
            return False
        for st in body:
            if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            names = _shallow_call_names(st)
            for nm in names:
                if nm in write_calls:
                    found.append((nm, st.lineno))
            if any(nm in _PARSE_CALLS for nm in names):
                return True
            for nm in names:
                if nm in funcs and nm not in seen:
                    seen.add(nm)
                    if run(funcs[nm].body, depth + 1):
                        return True
        return False

    run(list(_entry_statements(tree.body)))
    return found


def _population(sibling):
    """Scripts that WRITE and are accepted by the matcher on the parser ground
    alone -- the exact set the exemption is load-bearing for."""
    out = []
    for p in sorted(SCRIPTS.glob("*.py")):
        src = p.read_text(encoding="utf-8", errors="replace")
        if not sibling.WRITES.search(src):
            continue
        if "answer_help" in src:          # accepted on the other ground too
            continue
        try:
            if not sibling.answers_help(src):
                continue
        except SyntaxError:               # pragma: no cover - not valid python
            continue
        out.append((p, src))
    return out


class TestTheParserExemptionIsLoadBearingAndHolds:
    def test_the_population_is_not_empty(self, sibling):
        n = len(_population(sibling))
        assert n >= 20, (
            f"only {n} script(s) are exempted from the writer guard by a parser "
            f"alone; either the population moved or this ratchet guards nothing")

    def test_no_exempted_writer_writes_before_argparse_can_answer(self, sibling):
        offenders = {}
        for p, src in _population(sibling):
            try:
                early = writes_before_parse_args(src, sibling._WRITE_CALLS)
            except SyntaxError:           # pragma: no cover
                continue
            if early:
                offenders[p.name] = early[:3]
        assert not offenders, (
            f"{len(offenders)} script(s) are excused from the `--help` writer "
            f"guard because they build an argparse parser, and reach a write "
            f"BEFORE parse_args() can answer the flag: {offenders}\n"
            f"argparse answers --help inside parse_args(), not at construction. "
            f"Move parse_args() above the first statement that changes a file.")

    def test_the_detector_sees_a_write_before_parse_args(self):
        """ANTI-VACUITY. A detector that found nothing would pass over any tree,
        which is how this exemption went unchecked in the first place."""
        bad = ("import argparse, pathlib\n"
               "def main():\n"
               "    pathlib.Path('record.md').write_text('stub')\n"
               "    p = argparse.ArgumentParser()\n"
               "    return p.parse_args()\n"
               "if __name__ == '__main__':\n"
               "    main()\n")
        found = writes_before_parse_args(bad, {"write_text"})
        assert found and found[0][0] == "write_text", found

    def test_a_script_that_parses_first_is_not_flagged(self):
        """POSITIVE CONTROL: the correct shape must be accepted, or the fix this
        ratchet protects would itself be reported as the defect."""
        good = ("import argparse, pathlib\n"
                "def main():\n"
                "    p = argparse.ArgumentParser()\n"
                "    a = p.parse_args()\n"
                "    pathlib.Path('record.md').write_text('real')\n"
                "    return a\n"
                "if __name__ == '__main__':\n"
                "    main()\n")
        assert writes_before_parse_args(good, {"write_text"}) == []

    def test_a_write_in_an_uncalled_function_is_not_counted(self):
        """Defining a writer does not run it. Counting it would make the ratchet
        fire on correct scripts, which is the failure mode of the class this
        whole session is about."""
        src = ("import argparse, pathlib\n"
               "def never_called():\n"
               "    pathlib.Path('x').write_text('y')\n"
               "def main():\n"
               "    return argparse.ArgumentParser().parse_args()\n"
               "if __name__ == '__main__':\n"
               "    main()\n")
        assert writes_before_parse_args(src, {"write_text"}) == []

    def test_parse_known_args_counts_as_answering(self):
        """`parse_known_args` handles -h exactly as `parse_args` does; treating it
        as not answering would flag correct scripts."""
        src = ("import argparse, pathlib\n"
               "def main():\n"
               "    argparse.ArgumentParser().parse_known_args()\n"
               "    pathlib.Path('x').write_text('y')\n"
               "if __name__ == '__main__':\n"
               "    main()\n")
        assert writes_before_parse_args(src, {"write_text"}) == []


class TestTheExemptionIsWhatCoversTheNewScripts:
    """The 8 scripts written on 2026-10-05 had a local `answer_help` renamed to
    `_parse_args` to satisfy
    `test_fresh_clone_is_actually_run_2026-09-11.py::test_no_script_uses_both`.
    The rename is safe, but NOT for the reason recorded: the writer guard never
    examined them either side of it, because the parser ground short-circuits
    before `WRITES` is consulted. Stated here so the next reader is not told the
    coverage is behavioural when it is an exemption.
    """

    def test_they_are_accepted_on_the_parser_ground_and_write_nothing(self, sibling):
        batch = sorted(SCRIPTS.glob("*_2026-10-05.py"))
        if not batch:
            pytest.skip("the 2026-10-05 batch is not in this checkout")
        for p in batch:
            src = p.read_text(encoding="utf-8")
            assert sibling.answers_help(src), p.name
            assert "answer_help" not in src, (
                f"{p.name} calls answer_help again, which is what "
                f"test_no_script_uses_both forbids alongside a parser")
            if sibling.WRITES.search(src):
                # Its exemption has become load-bearing, so the ordering check is
                # what has to hold for it. This arm is live: the review that added
                # this file also added a script in the same batch that writes a
                # synthetic report to a temporary directory.
                assert writes_before_parse_args(src, sibling._WRITE_CALLS) == [], (
                    f"{p.name} writes before parse_args() can answer --help")
