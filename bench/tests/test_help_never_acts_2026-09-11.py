"""`--help` destroyed 54,480 bytes of a verbatim panel record and exited 0.

MEASURED 2026-09-11 in a throwaway clone. `python3
scripts/assemble_panel_record_0819.py --help` rewrote
`experimental_notes/Panel_Enforcement_Prose_FULL_RECORD_2026-08-19.md` from
55,814 bytes to 1,334 and returned success. The script regenerates a panel record
from `bench/logs/`, which `.gitignore:41` excludes, so in any clone the source is
empty and every seat is written back as "NO RESPONSE FILE" -- the complete,
verbatim record of a 5-model review replaced by a stub, by a flag whose entire
job is to print a sentence.

IT HAD BEEN HAPPENING IN EVERY CLONE RUN, and the symptom reached this suite as
`test_each_record_reproduces_a_seat_verbatim` failing on 2 August notes. That
looked like a defect in the records and was a defect in a flag.

THE MORNING'S `--help` SWEEP REPORTED 0 OF 54 AND WAS HONEST. Its population is
MEASUREMENT scripts, and both offenders are ACTION scripts. 122 scripts are
tracked. The 68 the sweep does not reach are exactly the ones where a `--help`
that acts is destructive rather than merely rude -- a false zero in the
POPULATION rather than in the matcher, which is the same defect class one level
out.

WHY THIS CHECK IS STATIC, stated because `execute-do-not-grep` would otherwise
require running them. Running every tracked script with `--help` is precisely
what must not be done: the founder's standing note records that 15 of 17 runners
once BILLED A LIVE DISPATCH on an unrecognised argument, and spending money is
one of the 3 categories reserved to him. The executing proof is done ONCE, by
hand, in a throwaway clone -- all 9 repaired scripts print usage, exit 0 and
leave the tree clean -- and the ratchet below keeps it that way without repeating
the risk on every suite run.

THAT HAND RUN COVERED DIRECT INVOCATION ONLY (panel round 16, 2026-09-17). Under
`python3 -m scripts.<name> --help`, 5 of the 9 still swallowed the ImportError of
their guard and ran their ordinary work; `answers_help` now reads that form (see
its docstring) and the 5 carry the own-directory insert. 4 of the 9, the ones
that write records and the topology diagram, are EXECUTED under both forms by
`bench/tests/test_help_is_inert_under_dash_m_2026-09-17.py`. The rate this entry
quoted is printed by `scripts/help_writers_rate_2026-09-17.py`.
"""
from __future__ import annotations

import ast
import pathlib
import re
import subprocess

REPO = pathlib.Path(__file__).resolve().parents[2]

#: Anything that changes a file. Deliberately broad: the cost of a false positive
#: here is one `answer_help` line, and the cost of a false negative was 54,480
#: bytes of a record the founder's own directive requires preserved verbatim.
WRITES = re.compile(
    r"write_text\s*\(|write_bytes\s*\(|open\([^)]*['\"][wa]|"
    r"shutil\.(copy|copy2|move|rmtree)|os\.(remove|unlink|rename)|\.unlink\(")


def tracked_scripts() -> list[pathlib.Path]:
    r = subprocess.run(["git", "ls-files", "scripts/*.py"], cwd=REPO,
                       capture_output=True, text=True)
    assert r.returncode == 0, (
        "git ls-files failed; refusing to report 0 offenders from an empty list, "
        "which is how a scan reports a clean result for a population it could "
        "not read")
    return [REPO / f for f in r.stdout.split() if f.endswith(".py")]


def answers_help(src: str, under_dash_m: bool = True) -> bool:
    """Does this script actually CALL a help handler, or build a parser?

    A SUBSTRING TEST WAS NOT ENOUGH, and the mutation caught it within a minute.
    The first version asked `"answer_help" in src`, and removing the real call
    from `scripts/apply_v3.py` left the ratchet green -- because the explanatory
    COMMENT beside the call still contains the word. A guard that reads its own
    documentation as evidence of the thing documented is this session's recurring
    defect, now inside the guard written to end one instance of it.

    So the question is asked of the parsed module: is `answer_help` CALLED at
    module level, or is an `ArgumentParser` constructed anywhere?

    A CALL THAT `python3 -m` CANNOT REACH DOES NOT COUNT (panel round 16,
    2026-09-17), unless `under_dash_m=False` asks the direct-invocation question.
    The repaired guards read `try: from _cli_help import answer_help` with an
    `except ImportError: pass` arm. Run directly, scripts/ is `sys.path[0]` and
    the import resolves; under `-m` the repository root is, the import fails, the
    arm swallows it, and the script's ordinary work runs with `--help` on its
    command line. 5 of the 9 repaired scripts had exactly that guard. A swallowing
    guard now counts only when a `sys.path.insert` built from `__file__` precedes
    the import in the same `try`, which is the form `assemble_panel_record.py`
    carries. It is a static proxy: it does not prove the inserted path is the
    script's own directory.
    """
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return False
    leaky = _help_calls_unreachable_under_dash_m(tree) if under_dash_m else set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = getattr(fn, "id", None) or getattr(fn, "attr", None)
        if name == "ArgumentParser":
            return True
        if name == "answer_help" and id(node) not in leaky:
            return True
    return False


def _help_calls_unreachable_under_dash_m(tree: ast.AST) -> set[int]:
    """ids of `answer_help` calls inside a `try` that imports `_cli_help`, swallows
    ImportError with `pass`, and puts nothing built from `__file__` on sys.path
    before the import."""
    def catches_import_error(h: ast.ExceptHandler) -> bool:
        types = h.type.elts if isinstance(h.type, ast.Tuple) else [h.type]
        return any(getattr(t, "id", None) in ("ImportError", "ModuleNotFoundError")
                   for t in types)

    leaky: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue
        at = next((i for i, s in enumerate(node.body)
                   if isinstance(s, ast.ImportFrom) and s.module == "_cli_help"), None)
        if at is None:
            continue
        if not any(catches_import_error(h) and all(isinstance(s, ast.Pass) for s in h.body)
                   for h in node.handlers):
            continue
        before = [n for s in node.body[:at] for n in ast.walk(s)]
        inserts = any(isinstance(n, ast.Call) and getattr(n.func, "attr", None) == "insert"
                      and getattr(getattr(n.func, "value", None), "attr", None) == "path"
                      for n in before)
        uses_file = any(isinstance(n, ast.Name) and n.id == "__file__" for n in before)
        if inserts and uses_file:
            continue
        for part in (node.body, node.orelse):
            for s in part:
                for n in ast.walk(s):
                    if isinstance(n, ast.Call) and (getattr(n.func, "id", None)
                                                    or getattr(n.func, "attr", None)) == "answer_help":
                        leaky.add(id(n))
    return leaky


class TestNoWriterIgnoresTheFlag:
    def test_the_population_is_not_empty(self):
        n = len(tracked_scripts())
        assert n >= 100, f"only {n} scripts found; the ratchet guards nothing"

    def test_every_script_that_writes_answers_help(self):
        offenders = []
        for p in tracked_scripts():
            src = p.read_text(encoding="utf-8", errors="replace")
            if answers_help(src):
                continue
            if WRITES.search(src):
                offenders.append(str(p.relative_to(REPO)))
        assert not offenders, (
            f"{len(offenders)} tracked script(s) WRITE something and ignore "
            f"`--help`, so the flag runs their ordinary work: {offenders}\n"
            f"Add `answer_help(__doc__, __file__, sys.argv[1:])` above the first "
            f"statement that does anything, or give the script a parser.")

    def test_the_two_that_caused_this_are_repaired(self):
        """POSITIVE CONTROL naming the actual offenders, so a change to the
        matcher above cannot quietly stop covering them."""
        for name in ("assemble_panel_record.py", "assemble_panel_record_0819.py"):
            src = (REPO / "scripts" / name).read_text(encoding="utf-8")
            # PARSED, not a substring (2026-09-17): `"answer_help" in src` was the
            # comment-satisfiable test this file's own `answers_help` docstring
            # records failing a mutation.
            assert answers_help(src), name
            assert WRITES.search(src), (
                f"{name} no longer looks like a writer, so this control has "
                f"stopped testing what it was written for")

    def test_the_matcher_recognises_a_writer(self):
        """ANTI-VACUITY. A `WRITES` pattern that matched nothing would make the
        ratchet pass over any tree at all."""
        assert WRITES.search("p.write_text('x')")
        assert WRITES.search("shutil.copy2(a, b)")
        assert WRITES.search("open(f, 'w')")
        assert not WRITES.search("p.read_text()")
        assert not WRITES.search("open(f) as fh")

    def test_a_guard_that_swallows_the_import_under_dash_m_does_not_count(self):
        """ANTI-VACUITY AND POSITIVE CONTROL for the `-m` rule, on the 3 guard
        shapes that exist in scripts/ today."""
        leaky = ('if __name__ == "__main__":\n'
                 '    try:\n'
                 '        from _cli_help import answer_help\n'
                 '    except ImportError:\n'
                 '        pass\n'
                 '    else:\n'
                 '        answer_help(__doc__, __file__)\n')
        repaired = ('if __name__ == "__main__":\n'
                    '    try:\n'
                    '        import sys as _sys\n'
                    '        import pathlib as _pl\n'
                    '        _here = str(_pl.Path(__file__).resolve().parent)\n'
                    '        if _here not in _sys.path:\n'
                    '            _sys.path.insert(0, _here)\n'
                    '        from _cli_help import answer_help\n'
                    '    except ImportError:\n'
                    '        pass\n'
                    '    else:\n'
                    '        answer_help(__doc__, __file__)\n')
        bare = ('if __name__ == "__main__":\n'
                '    from _cli_help import answer_help\n'
                '    answer_help(__doc__, __file__)\n')
        assert not answers_help(leaky), "a swallowed import under -m was counted"
        assert answers_help(leaky, under_dash_m=False), (
            "the direct-invocation question must still accept the leaky guard")
        assert answers_help(repaired), "the repaired guard was not accepted"
        assert answers_help(bare), "a bare import fails closed under -m and must count"
        assert answers_help("import argparse\nargparse.ArgumentParser()\n")

    def test_every_repaired_guard_survives_dash_m(self):
        """The 9 scripts A26 repaired, read with the `-m` rule. 5 of them failed
        it until 2026-09-17."""
        nine = ("apply_v3.py", "assemble_panel_record.py", "assemble_panel_record_0819.py",
                "branch_supplies_adjudication_versions_2026-09-10.py",
                "compose_all_2026-08-23.py", "dump_panel_findings_2026-09-05.py",
                "ffafp_cycle_gamma_2026-09-10.py", "generate_topology.py",
                "task_list_entry_count_2026-09-10.py")
        failing = [n for n in nine
                   if not answers_help((REPO / "scripts" / n).read_text(encoding="utf-8"))]
        assert not failing, (
            f"{failing} answer --help only when run directly; under `python3 -m` "
            f"their ImportError is swallowed and their ordinary work runs")


#: Calls that change something on disk.
_WRITE_CALLS = {"write_text", "write_bytes", "copy", "copy2", "move", "rmtree",
                "remove", "unlink", "rename", "mkdir", "makedirs"}


def module_level_writes(src: str) -> list[str]:
    """Writes that happen merely because the module was IMPORTED.

    A `__main__` guard is fine: importing does not enter it.
    """
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    out = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if isinstance(node, ast.If) and isinstance(node.test, ast.Compare) \
                and getattr(node.test.left, "id", "") == "__name__":
            continue
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call):
                name = getattr(sub.func, "attr", None) or getattr(sub.func, "id", None)
                if name in _WRITE_CALLS:
                    out.append(f"{name}() at line {sub.lineno}")
    return out


class TestImportingAScriptChangesNothing:
    """Guarding `--help` was not enough, and the next clone run said so.

    `bench/tests/test_operational_scripts.py` probes every script by IMPORTING it
    (`spec_from_file_location`). A script whose work runs at module scope
    therefore does its work whenever it is inspected -- and in a clone
    `bench/logs/` is empty, so importing `assemble_panel_record_0819.py` rebuilt
    a 55,814-byte verbatim panel record as a 1,334-byte stub. Every clone run.

    THE FLAG WAS NEVER THE ONLY WAY IN. Fixing `--help` fixed one entrance to a
    room with two doors, which is why the same 2 notes were still truncated in
    the run after that fix. A script that acts at import has no safe way to be
    inspected, and inspecting scripts is something this suite does deliberately.

    MEASURED after the repair: 0 of 122 tracked scripts write at module level.
    """

    def test_no_tracked_script_writes_at_import(self):
        offenders = {}
        for p in tracked_scripts():
            w = module_level_writes(p.read_text(encoding="utf-8", errors="replace"))
            if w:
                offenders[str(p.relative_to(REPO))] = w[:3]
        assert not offenders, (
            f"{len(offenders)} tracked script(s) write when merely imported, so "
            f"any tool that inspects them changes the tree: {offenders}\n"
            f"Move the work into a function and call it under "
            f"`if __name__ == \"__main__\":`.")

    def test_the_detector_sees_a_module_level_write(self):
        """ANTI-VACUITY. A detector that found nothing would pass over any tree."""
        assert module_level_writes("import pathlib\npathlib.Path('x').write_text('y')\n")
        assert module_level_writes("import shutil\nshutil.copy2('a','b')\n")

    def test_a_guarded_write_is_not_flagged(self):
        """POSITIVE CONTROL: the `__main__` form must be accepted, or the fix
        this test exists to protect would itself be reported as the defect."""
        assert not module_level_writes(
            'import pathlib\n'
            'def main():\n    pathlib.Path("x").write_text("y")\n'
            'if __name__ == "__main__":\n    main()\n')

    def test_the_two_records_are_importable_without_acting(self):
        """POSITIVE CONTROL naming the scripts that caused this."""
        for name in ("assemble_panel_record.py", "assemble_panel_record_0819.py"):
            src = (REPO / "scripts" / name).read_text(encoding="utf-8")
            assert not module_level_writes(src), name
            assert "def main(" in src, (
                f"{name} no longer has a main(); its work may have drifted back "
                f"to module scope")
