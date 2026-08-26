"""The compile gate must create NO files, and nothing may anchor a temp file to the CWD.

WHAT WAS MEASURED, 2026-08-26. A stray `tmpjwur6y1n.py` was caught in the
repository root during a full suite run -- present in one `ls`, gone from the
next. Tracing it:

  _run_hard_gate_compile wrote a temp .py into _anchor_dir_for(source_path) and
  unlinked it in a `finally`. That made the .py transient. But py_compile ALSO
  writes bytecode beside it, and NOTHING removed that:

      repo-root __pycache__   17,848 entries, 70 MB, every single one tmp*
      bench/__pycache__          368 tmp* entries of 502, 29 MB

  The root ones come from bare-filename targets like the test fixture's "x.py",
  whose Path(...).parent is "." -- the working directory, which during a suite
  run is the repository root. The bench/ ones come from REAL runs, whose targets
  live in bench/.

So the visible symptom was a transient .py and the actual cost was 99 MB of
permanent bytecode that grew with every gate call.

THE FIX AND WHY IT IS THE SIMPLE ONE. This gate only asks whether the source
compiles, and the builtin compile() answers that from a string with no file I/O
at all. The anchoring was pointless here regardless: it exists so ruff and
bandit walk up to the repository's config, and py_compile walks up to nothing.
The three ruff/bandit sites still write real files, because those tools need
one; they do not write bytecode.
"""
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.reference_runner_v2 import (  # noqa: E402
    _anchor_dir_for, _run_hard_gate_compile,
)

VALID = "def f(x):\n    return x + 1\n"
BROKEN = "def f(x)\n    return x + 1\n"     # missing colon


class TestTheAnchorNeverResolvesToTheWorkingDirectory:
    @pytest.mark.parametrize("bare", ["x.py", "target.py", "mod.py"])
    def test_known_bad_a_bare_filename_no_longer_anchors_to_cwd(self, bare):
        """This returned '.' before 2026-08-26, which is the repository root
        during a suite run."""
        assert _anchor_dir_for(bare) is None, (
            f"{bare!r} still anchors to {_anchor_dir_for(bare)!r}; a temp file "
            "would be written into the working directory"
        )

    def test_known_good_a_real_directory_still_anchors(self):
        """The ruff/bandit context parity must survive the fix."""
        assert _anchor_dir_for("bench/insect_brain.py") == "bench", (
            "a real source directory no longer anchors, so ruff and bandit lose "
            "the repository config they walk up to find"
        )

    def test_a_non_python_target_does_not_anchor(self):
        assert _anchor_dir_for("bench/cdsfl_registry/targets/thing.md") is None

    def test_the_two_answers_differ(self):
        assert (_anchor_dir_for("x.py") is None) != (
            _anchor_dir_for("bench/insect_brain.py") is None), (
            "bare filename and real path get the same answer; the discriminator "
            "is doing no work"
        )


class TestTheCompileGateStillWorks:
    def test_valid_source_scores_one(self):
        score, detail = _run_hard_gate_compile(VALID, "bench/whatever.py")
        assert score == 1, f"valid source failed the compile gate: {detail}"

    def test_known_bad_a_syntax_error_scores_zero(self):
        score, detail = _run_hard_gate_compile(BROKEN, "bench/whatever.py")
        assert score == 0, "a syntax error passed the compile gate"
        assert "CompileError" in detail, (
            f"the detail no longer names the failure class: {detail!r}"
        )

    def test_the_two_answers_differ(self):
        assert (_run_hard_gate_compile(VALID, "bench/w.py")[0]
                != _run_hard_gate_compile(BROKEN, "bench/w.py")[0])


class TestItCreatesNothing:
    """The assertion that matters. Not that the gate cleans up after itself --
    that it writes nothing to clean up."""

    def _snapshot(self):
        roots = [REPO, REPO / "__pycache__", REPO / "bench", REPO / "bench/__pycache__"]
        out = set()
        for r in roots:
            if r.is_dir():
                out |= {p for p in r.iterdir()}
        return out

    @pytest.mark.parametrize("src,path", [
        (VALID, "bench/insect_brain.py"),          # anchors to a real directory
        (VALID, "x.py"),                            # the bare-filename case
        (BROKEN, "bench/insect_brain.py"),          # the failure path
        (BROKEN, "x.py"),
    ], ids=["valid-real", "valid-bare", "broken-real", "broken-bare"])
    def test_no_file_appears_anywhere_it_could(self, src, path):
        before = self._snapshot()
        _run_hard_gate_compile(src, path)
        new = self._snapshot() - before
        assert not new, (
            "the compile gate created "
            + ", ".join(sorted(str(p.relative_to(REPO)) for p in new))
            + ". Before 2026-08-26 this left a tmp*.pyc behind on every call; "
              "17,848 of them accumulated in the repository root."
        )

    def test_repeated_calls_leave_the_tree_identical(self):
        """A single call leaking nothing is weaker than fifty not leaking."""
        before = self._snapshot()
        for i in range(50):
            _run_hard_gate_compile(VALID if i % 2 else BROKEN, "x.py")
        assert self._snapshot() == before, "fifty gate calls changed the tree"


def test_no_stray_temp_python_files_are_committed_or_left_in_the_root():
    """A guard for the symptom as well as the cause. Catches an interrupted run
    that died before its finally, which is how these survive at all."""
    strays = sorted(p.name for p in REPO.glob("tmp*.py"))
    assert not strays, (
        f"stray temp Python file(s) in the repository root: {strays}. "
        "A gate run was interrupted before its cleanup, or a new writer anchors "
        "to the working directory."
    )
