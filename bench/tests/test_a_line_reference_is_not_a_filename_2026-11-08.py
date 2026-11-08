"""An `evidence:` citation of the form `file.py:123` names a FILE, not a path.

THE DEFECT THIS GUARDS, proven by execution on 2026-11-08.
`task_list_markers.evidence_objections` did `root / name` with the whole
evidence string, so `bench/run_round_robin.py:2121` was looked up as a filename
and reported as "does not exist" -- while the file existed and the cited line
sat at 2,121 of 4,682. 7 such objections stood across entries B20, B93 and B94.

IT WAS NOT COSMETIC. `set_marker` calls that function to REFUSE a write before
changing a marker, so closing any of those 3 entries would have been refused
for a reason that was not true: a guard accusing correct work, which this
project has recorded at 9 of 36 failures in a single board.

AND THE INCONSISTENCY IS THE REAL LESSON. The guard built for entry B110
already stripped the reference and said why in a comment, while the function
had no such step. 2 checks over the same field disagreed about this project's
own citation convention because each carried its own idea of it -- one of them
by carrying its own regex. The pattern now lives in `task_list_markers`, where
both reach it.
"""
from __future__ import annotations

import ast
import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def M():
    sys.path.insert(0, str(REPO / "scripts"))
    import task_list_markers as m
    return m


@pytest.fixture(scope="module")
def B110():
    p = REPO / "bench" / "tests" / "test_an_entrys_cited_evidence_must_exist_2026-11-04.py"
    spec = importlib.util.spec_from_file_location("b110_probe", p)
    m = importlib.util.module_from_spec(spec)
    sys.modules["b110_probe"] = m
    spec.loader.exec_module(m)
    return m


class TestTheConventionIsDefinedOnce:

    def test_the_pattern_lives_in_the_module_both_callers_reach(self, M):
        assert hasattr(M, "LINE_REF"), (
            "LINE_REF is not in task_list_markers, so the function that needs "
            "it and the guard that needs it must each carry a copy -- which is "
            "how the 2 came to disagree")

    def test_the_guard_uses_that_definition_rather_than_its_own(self, M, B110):
        """★ STRUCTURAL, BECAUSE `is` CANNOT SEE THIS.

        The first version asserted `B110._LINE_REF is M.LINE_REF`. Python
        CACHES compiled patterns, so `re.compile` of an equal pattern returns
        the IDENTICAL object -- `a is b` is True for 2 separate compiles of the
        same source. The reversal harness proved it: putting the guard's own
        copy back left this test green. So the question is not whether the
        objects coincide but whether the guard DEFINES one, and that is a
        property of its source.
        """
        src = (REPO / "bench" / "tests"
               / "test_an_entrys_cited_evidence_must_exist_2026-11-04.py"
               ).read_text(encoding="utf-8")
        tree = ast.parse(src)
        compiles = [n for n in ast.walk(tree)
                    if isinstance(n, ast.Call)
                    and getattr(n.func, "attr", None) == "compile"
                    and getattr(getattr(n.func, "value", None), "id", None) == "re"]
        assert not compiles, (
            f"the guard compiles its own pattern at line(s) "
            f"{[c.lineno for c in compiles]}, so the 2 checks can drift apart "
            f"again about what a citation looks like. It must read "
            f"task_list_markers.LINE_REF.")
        assert "_markers.LINE_REF" in src, (
            "the guard does not read LINE_REF from task_list_markers")
        assert B110._LINE_REF.pattern == M.LINE_REF.pattern

    @pytest.mark.parametrize("cited,bare", [
        ("bench/dm/_types.py:314", "bench/dm/_types.py"),
        ("bench/tests/conftest.py:10-20", "bench/tests/conftest.py"),
        ("bench/run_round_robin.py", "bench/run_round_robin.py"),
        #: ★ THE ANCHOR IS ONLY OBSERVABLE HERE. Without `$` the substitution
        #: strips EVERY colon-digits group, so a directory named with one is
        #: mangled: `run:12` disappears. Measured -- anchored gives
        #: `bench/logs/run:12/test.py`, unanchored `bench/logs/run/test.py`.
        #: The reversal harness caught this case missing.
        ("bench/logs/run:12/test.py:34", "bench/logs/run:12/test.py"),
    ])
    def test_it_strips_a_reference_and_leaves_a_bare_path(self, M, cited, bare):
        assert M.LINE_REF.sub("", cited) == bare


class TestTheCheckAcceptsACitedLine:
    """The behaviour, by CALLING the real function on real paths."""

    #: A file that exists, is inside the suite's tree, parses and holds tests --
    #: so the ONLY thing that could object is the line reference.
    SOUND = "bench/tests/test_task_list_markers_2026-09-09.py"

    def test_the_bare_path_is_accepted(self, M):
        assert M.evidence_objections("PROBE", (self.SOUND,)) == []

    @pytest.mark.parametrize("suffix", [":1", ":49", ":10-20", ":2121"])
    def test_the_same_path_with_a_line_reference_is_also_accepted(self, M, suffix):
        objs = M.evidence_objections("PROBE", (self.SOUND + suffix,))
        assert objs == [], (
            f"a citation of {self.SOUND}{suffix} was refused although the bare "
            f"path is accepted, so the reference is being read as part of the "
            f"filename:\n  {objs}")

    def test_a_genuinely_missing_file_is_still_refused(self, M):
        """ANTI-VACUITY in the direction that matters: no false pass.

        ★ THE FIXTURE IS `gone.py`, AND THAT IS NOT COSMETIC.
        `test_line_citations_resolve_2026-09-01.py` scans every tracked file
        for a path-plus-line-number reference and asserts the named file
        exists. The name this fixture used before carried such a suffix and
        named nothing, so it made that guard RED -- correctly, on its own
        terms -- and refused the commit carrying this file. `gone` is ALREADY
        in that guard's PLACEHOLDER alternation for illustrative names, so
        renaming exempts this one fixture WITHOUT widening an exemption the
        other 2,573 board tests rely on. Adding a new name to PLACEHOLDER
        would have bought the same green by reducing a working guard's cover.

        The old name is deliberately NOT written out here, with or without a
        suffix: a file that explains a pattern in the pattern's own notation
        is indistinguishable, to the scanner, from a live instance of it. A
        scar reads as a wound.

        The precondition is asserted rather than assumed. If anyone ever
        creates `bench/tests/gone.py` this test stops probing a missing file
        and silently inverts into a vacuous pass, which is the failure mode
        3 of tonight's reversal-harness catches had in common.
        """
        missing = REPO / "bench/tests/gone.py"
        assert not missing.exists(), (
            f"{missing} now EXISTS, so this test no longer probes a missing "
            f"file and has gone VACUOUS. Pick another absent name that the "
            f"PLACEHOLDER pattern in "
            f"test_line_citations_resolve_2026-09-01.py already matches.")
        objs = M.evidence_objections("PROBE", ("bench/tests/gone.py:12",))
        assert objs and "does not exist" in objs[0], objs

    def test_a_directory_is_still_refused(self, M):
        objs = M.evidence_objections("PROBE", ("bench/tests/fixtures",))
        assert objs and "directory" in objs[0], objs

    def test_a_file_outside_the_suite_tree_is_still_refused(self, M):
        objs = M.evidence_objections("PROBE", ("scripts/task_list_markers.py:1",))
        assert objs and "outside" in objs[0], (
            "stripping the reference must not let a non-test file through; "
            f"got {objs}")


class TestTheLiveListImproves:
    """The measured effect, so the fix is not merely plausible."""

    def test_no_live_entry_is_refused_for_a_line_reference(self, M):
        bad = []
        for e in M.parse_entries():
            for o in M.evidence_objections(e.ident, e.evidence or ()):
                if "does not exist" in o and M.LINE_REF.search(
                        o.split(":", 1)[1].strip().split(" does not exist")[0]):
                    bad.append(o)
        assert bad == [], (
            "entries are still refused because a line reference was read as "
            "part of the filename:\n  " + "\n  ".join(bad))

    def test_the_remaining_objections_are_the_genuine_ones(self, M):
        """ANTI-VACUITY: if nothing objected at all, this file guards nothing."""
        kinds = set()
        for e in M.parse_entries():
            for o in M.evidence_objections(e.ident, e.evidence or ()):
                t = o.split(":", 1)[1]
                kinds.add("directory" if "directory" in t
                          else "outside" if "outside" in t
                          else "missing" if "does not exist" in t else "other")
        assert kinds, (
            "no entry objects on any ground, so this check decides nothing and "
            "the test above passes for the wrong reason")
