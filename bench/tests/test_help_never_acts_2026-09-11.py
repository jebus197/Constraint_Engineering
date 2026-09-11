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


def answers_help(src: str) -> bool:
    """Does this script actually CALL a help handler, or build a parser?

    A SUBSTRING TEST WAS NOT ENOUGH, and the mutation caught it within a minute.
    The first version asked `"answer_help" in src`, and removing the real call
    from `scripts/apply_v3.py` left the ratchet green -- because the explanatory
    COMMENT beside the call still contains the word. A guard that reads its own
    documentation as evidence of the thing documented is this session's recurring
    defect, now inside the guard written to end one instance of it.

    So the question is asked of the parsed module: is `answer_help` CALLED at
    module level, or is an `ArgumentParser` constructed anywhere?
    """
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = getattr(fn, "id", None) or getattr(fn, "attr", None)
        if name in ("answer_help", "ArgumentParser"):
            return True
    return False


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
            assert "answer_help" in src, name
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
