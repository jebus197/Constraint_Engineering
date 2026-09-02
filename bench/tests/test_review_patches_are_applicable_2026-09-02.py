"""A file named .patch must be applicable by the tool its name implies.

New files written by a reviewer were appended after the diff under
`=== NEW FILE:` headers. The content was preserved deliberately -- a dropped
file that says nothing reads identically to a review that produced nothing --
but `git apply` returns **exit 0** on such an artefact while silently ignoring
every one of those blocks.

MEASURED 2026-09-02 across every review artefact on record: 8 of 18 unique
patches carry content `git apply` ignores -- 44.4%, Wilson [24.6%, 66.3%] --
totalling 9,914 lines, and `git apply --check` returns 0 on all of them, so
there is no signal at all.

CC2 hit it applying a review: 8 files and 757 lines absent from the resulting
tree, including `bench/metering.py`. In that tree both `record_dispatch` call
sites sit inside `except Exception: pass`, so a DEFAULT-ON metering ruling
becomes a permanent silent no-op -- defeated by a file extension rather than by
a bug. Its summary of the shape: the patch is green if applied incompletely and
red if applied as intended.

`git add -N` stages intent-to-add, so `git diff HEAD` emits proper
`new file mode` hunks. Nothing is committed, and the sandbox is discarded either
way. The `=== NEW FILE` fallback is kept for what add -N cannot cover.
"""

import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
HARNESS = REPO / "bench" / "confer_panel_2026-08-28.py"


class TestTheExtractorStagesIntentToAdd:
    def test_it_calls_git_add_dash_n_before_diffing(self):
        src = HARNESS.read_text(encoding="utf-8")
        i = src.index('subprocess.run(["git", "add", "-N"')
        j = src.index('subprocess.run(["git", "diff", "HEAD"]', i)
        assert i < j, (
            "intent-to-add must be staged BEFORE the diff, or new files are "
            "still emitted outside the patch format")

    def test_it_only_stages_real_readable_files(self):
        src = HARNESS.read_text(encoding="utf-8")
        i = src.index("_to_add = [")
        block = src[i:i + 400]
        assert ".is_file()" in block and "400_000" in block, (
            "staging must skip directories and oversized files, or the cap "
            "that keeps the artefact readable is bypassed")

    def test_the_loud_fallback_survives(self):
        """add -N cannot cover everything; silence must never be the fallback."""
        src = HARNESS.read_text(encoding="utf-8")
        assert "=== NEW FILE NOT EXTRACTED:" in src, (
            "the loud fallback for oversized files has been removed; a dropped "
            "file that says nothing reads exactly like a review that produced "
            "nothing")


class TestItRoundTripsForReal:
    """Behavioural: create a reviewer-shaped change, extract, apply, verify."""

    def _worktree(self, tmp_path, name):
        wt = tmp_path / name
        subprocess.run(["git", "worktree", "add", "--detach", str(wt), "HEAD"],
                       cwd=str(REPO), capture_output=True, timeout=180)
        return wt

    def _cleanup(self, wt):
        subprocess.run(["git", "worktree", "remove", "--force", str(wt)],
                       cwd=str(REPO), capture_output=True, timeout=180)

    def test_a_new_file_survives_git_apply(self, tmp_path):
        src_wt = self._worktree(tmp_path, "src")
        dst_wt = self._worktree(tmp_path, "dst")
        try:
            (src_wt / "README.md").write_text(
                (src_wt / "README.md").read_text() + "\n# reviewer edit\n")
            newf = src_wt / "scripts" / "reviewer_new_tool.py"
            newf.parent.mkdir(parents=True, exist_ok=True)
            newf.write_text("def main():\n    return 42\n")

            unt = subprocess.run(
                ["git", "ls-files", "--others", "--exclude-standard"],
                cwd=str(src_wt), capture_output=True, text=True, timeout=60)
            to_add = [r for r in (unt.stdout or "").split()
                      if (src_wt / r).is_file()
                      and (src_wt / r).stat().st_size < 400_000]
            assert to_add, "the new file was not seen as untracked"
            subprocess.run(["git", "add", "-N", "--", *to_add], cwd=str(src_wt),
                           capture_output=True, timeout=120)
            diff = subprocess.run(["git", "diff", "HEAD"], cwd=str(src_wt),
                                  capture_output=True, text=True, timeout=120)
            patch = tmp_path / "r.patch"
            patch.write_text(diff.stdout)

            assert "new file mode" in diff.stdout, (
                "the new file is not a diff hunk; git apply will ignore it and "
                "still exit 0")

            rc = subprocess.run(["git", "apply", str(patch)], cwd=str(dst_wt),
                                capture_output=True, text=True, timeout=120)
            assert rc.returncode == 0, rc.stderr[-400:]
            assert (dst_wt / "scripts" / "reviewer_new_tool.py").is_file(), (
                "the new file did not survive the apply -- the exact silent "
                "loss this test exists for")
            assert "reviewer edit" in (dst_wt / "README.md").read_text()
        finally:
            self._cleanup(src_wt); self._cleanup(dst_wt)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
