"""7.2's "29 of 379" must reproduce, and it must reproduce at its own revision.

`measured-rate-travels-with-its-script`. 7.2 quoted the reach of the only test
that linted real notes -- 29 of 379 files, 7.65%, Wilson [5.4%, 10.8%] -- with no
script behind it. The figure turns out to be correct, which is not the same as
being evidence: it was a claim about evidence until this script existed.

THE TRAP THIS FILE EXISTS TO HOLD OPEN. The notes tree grows. At HEAD the same
measurement reads 30 of 380, so a script that could only see the working tree
would report the entry's figure as wrong. The figure is historical and the script
must be able to reach the revision it was taken at, or it cannot back it.

Every test here CALLS the script or its functions. None asserts on source text.
"""
from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "lint_reach_over_notes_2026-09-10.py"
GUARD = ROOT / "bench" / "tests" / "test_note_standard_v17_enforced_2026-08-26.py"

#: The revision 7.2's figure was taken at.
REV = "b593500"


def _load(path: Path = SCRIPT):
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location("lint_reach", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _load()


@pytest.fixture(scope="module")
def out():
    r = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT,
                       capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"the script backing 7.2's figure does not run: exit {r.returncode}\n"
        f"{r.stdout[-2000:]}\n{r.stderr[-2000:]}")
    return r.stdout


class TestTheFigureReproduces:
    def test_29_of_379_is_produced(self, out):
        assert "29 of 379 = 7.6517%" in out, "7.2's figure did not reproduce"

    def test_the_interval_matches_the_entry(self, out):
        assert "[5.3802%, 10.7731%]" in out, (
            "7.2 quotes Wilson [5.4%, 10.8%]")

    def test_both_interval_tools_agree(self, out):
        agreements = re.findall(r"agree to 1e-9: (True|False)", out)
        assert agreements and set(agreements) == {"True"}, agreements


class TestItReachesTheRevisionNotOnlyTheWorkingTree:
    def test_head_and_the_revision_differ(self, mod):
        """If they were equal this test could not tell the modes apart."""
        guard = _load(GUARD) if False else None  # selector comes from the script
        import importlib.util as iu
        spec = iu.spec_from_file_location("v17_guard", GUARD)
        g = iu.module_from_spec(spec)
        spec.loader.exec_module(g)
        k_rev, n_rev = mod.at_revision(REV, True, g.FOOTLINE)
        k_head, n_head = mod.at_revision("HEAD", True, g.FOOTLINE)
        assert (k_rev, n_rev) == (29, 379)
        assert (k_head, n_head) != (k_rev, n_rev), (
            "the tree has not moved since b593500, so this file cannot "
            "demonstrate that the revision mode does anything")

    def test_the_two_populations_differ(self, mod):
        import importlib.util as iu
        spec = iu.spec_from_file_location("v17_guard", GUARD)
        g = iu.module_from_spec(spec)
        spec.loader.exec_module(g)
        rec = mod.at_revision(REV, True, g.FOOTLINE)
        top = mod.at_revision(REV, False, g.FOOTLINE)
        assert rec != top, (
            "recursive and top-level counts coincide, so the script cannot show "
            "which population the entry meant")
        assert rec == (29, 379) and top == (27, 368)


class TestTheSelectorIsTheLiveOne:
    def test_the_script_imports_the_guard_rather_than_retyping_it(self, mod):
        import importlib.util as iu
        spec = iu.spec_from_file_location("v17_guard", GUARD)
        g = iu.module_from_spec(spec)
        spec.loader.exec_module(g)
        assert mod._selector().FOOTLINE.pattern == g.FOOTLINE.pattern

    def test_the_live_selector_matches_the_working_tree_not_head(self, mod):
        """Compare like with like, and explain any gap rather than tolerating it.

        The live selector walks the WORKING TREE; `at_revision("HEAD", ...)` reads
        the COMMITTED tree. On a dirty tree they differ by exactly the uncommitted
        notes, and the first version of this test asserted they were equal — it
        failed the moment 2 new notes were written, which is correct behaviour
        from a wrong assertion. The gap is now computed and named.
        """
        live = {p.relative_to(ROOT).as_posix()
                for p in mod._selector()._v17_notes()}
        head = mod._revision_declaring("HEAD")
        only_live = sorted(live - set(head))
        only_head = sorted(set(head) - live)

        tracked = subprocess.run(
            ["git", "status", "--porcelain", "--", "experimental_notes/"],
            cwd=ROOT, capture_output=True, text=True, timeout=120).stdout
        dirty = {ln[3:].strip().strip('"') for ln in tracked.splitlines() if ln.strip()}

        unexplained = [p for p in only_live if p not in dirty]
        assert not unexplained, (
            f"the working tree declares v1.7 in {unexplained} but HEAD does not, "
            f"and git reports them as clean — the selector and the revision "
            f"reader disagree for a reason that is not uncommitted work")
        assert not [p for p in only_head if p not in dirty], (
            f"HEAD declares v1.7 in {only_head} and the working tree does not, "
            f"with no pending change to explain it")

class TestMutationsAreCaught:
    """Each mutation asserted APPLIED, and landing on a line the fixture runs."""

    def _mutate(self, old: str, new: str) -> Path:
        """Write the mutant INSIDE scripts/, and prove it still runs.

        THIS HARNESS WAS BROKEN WHEN FIRST WRITTEN, 2026-09-10, and the way it
        was broken is the exact failure it exists to detect. The mutant was
        written to the system temp directory, so the script's own
        `REPO = Path(__file__).resolve().parents[1]` resolved outside the
        repository and every mutant died at startup with FileNotFoundError. Its
        stdout was empty, and `assert "<figure>" not in ""` passes. **A mutant
        that crashes reads as caught.** 3 of 4 mutations here were vacuous and
        reported green.

        So: the mutant lives beside the original, and `_run` REFUSES a mutant
        that did not execute. A mutation is evidence only if the mutated program
        ran and produced a different answer.
        """
        src = SCRIPT.read_text(encoding="utf-8")
        assert old in src, f"MUTATION ANCHOR ABSENT, never applied: {old!r}"
        mutated = src.replace(old, new, 1)
        assert mutated != src, "the replacement changed nothing"
        # `.mutants/` and NOT `scripts/`: a mutant written into scripts/ is
        # visible to every suite-wide scanner that walks that directory, and
        # one showed up as a full-suite failure the moment this harness was
        # first used. `Path("<repo>/.mutants/x.py").parents[1]` is still the
        # repo root, so the script under test resolves its own paths exactly
        # as it does in place.
        pen = SCRIPT.parent.parent / ".mutants"
        pen.mkdir(exist_ok=True)
        p = pen / f"_mutant_{abs(hash(old)) % 10**8}.py"
        p.write_text(mutated, encoding="utf-8")
        return p

    def _run(self, p: Path):
        r = subprocess.run([sys.executable, str(p)], cwd=ROOT,
                           capture_output=True, text=True, timeout=900)
        assert r.returncode == 0 and r.stdout.strip(), (
            "THE MUTANT DID NOT RUN, so it cannot be 'caught' — a crashing "
            f"mutant produces empty output and every `not in` check passes.\n"
            f"exit {r.returncode}\nstdout: {r.stdout[-800:]}\n"
            f"stderr: {r.stderr[-1500:]}")
        return r

    def test_mutation_revision_mode_pinned_to_head(self):
        """The commonest way to lose a historical figure: ignore the revision."""
        m = self._mutate('["git", "ls-tree", "-r", "--name-only", rev, "experimental_notes/"]',
                         '["git", "ls-tree", "-r", "--name-only", "HEAD", "experimental_notes/"]')
        try:
            assert "29 of 379 = 7.6517%" not in self._run(m).stdout, (
                "pinning the listing to HEAD still produced the historical "
                "figure — the revision argument is not reaching git")
        finally:
            m.unlink(missing_ok=True)

    def test_mutation_recursive_flag_ignored(self):
        m = self._mutate('    if not recursive:\n        md = [n for n in md if n.count("/") == 1]',
                         '    if False:\n        md = [n for n in md if n.count("/") == 1]')
        try:
            out = self._run(m).stdout
            assert "27 of 368" not in out, (
                "ignoring the recursive flag left the top-level figure "
                "unchanged — the flag is doing nothing")
        finally:
            m.unlink(missing_ok=True)

    def test_mutation_version_floor_lowered(self):
        """v1.7-or-later is the selector's rule; accepting v1.0 must change the count."""
        # ANCHOR MOVED 2026-09-10 when the script was rewritten to use one
        # `git grep` per revision instead of one `git show` per file (43x faster,
        # identical figures). The version comparison now lives in
        # `_revision_declaring`. The old anchor's absence made this test fail
        # loudly rather than silently pass, which is the harness working.
        m = self._mutate(">= (1, 7):\n            hits.add(path)",
                         ">= (1, 0):\n            hits.add(path)")
        try:
            assert "29 of 379 = 7.6517%" not in self._run(m).stdout, (
                "lowering the version floor left the count at 29 — the "
                "foot-line version is not being read")
        finally:
            m.unlink(missing_ok=True)

    def test_mutation_footline_pattern_broken(self):
        # ANCHOR MOVED with the same rewrite: the per-file search is now the
        # FALLBACK path taken only by a substituted selector, and the fast path
        # matches the version inside `_revision_declaring`.
        m = self._mutate(
            '        m = re.search(r"CDSFL note standard v(\\d+)\\.(\\d+)", text)',
            '        m = None')
        try:
            out = self._run(m).stdout
            assert "0 of 379" in out, (
                "with the foot-line search disabled the historical count should "
                "be 0 of 379; it was not, so the search is not load-bearing")
        finally:
            m.unlink(missing_ok=True)
