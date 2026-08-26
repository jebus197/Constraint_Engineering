"""No test may rewrite canonical project state in the real repository.

MEASURED 2026-08-26. test_sv_memory_unreadable_2026-08-26.py ran sv's main()
with cwd=REPO -- the actual repository -- and no --dry-run. sv did what sv does:
it regenerated docs/CURRENT_STATE.md, resources/ONBOARDING.md and
resources/RECOVERY.md in the working tree. On EVERY suite run.

That is why those three files sat perpetually modified in git status, and it is
how unrelated content kept being swept into commits by sv's auto-staging -- the
same route that put a literal "BROKEN-STAMP" into resources/MEMORY_EXCLUSIONS.md
and shipped it in commit 80faf11.

Verified both ways before fixing: sv --dry-run dirties 0 files and still prints
every string the test asserts on; the live run dirties 3.

This file is the guard, not the fix. It reads the test corpus and fails if any
test invokes sv's main against the real repository without --dry-run.

WHY STATIC RATHER THAN RUNTIME. A runtime check ("are these files clean?")
depends on test ordering and on what the developer happened to leave dirty
before running pytest. Reading the corpus does not.
"""
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
TESTS = REPO / "bench" / "tests"

# Files sv regenerates. Rewriting any of these from a test dirties the tree.
CANONICAL = [
    "docs/CURRENT_STATE.md",
    "resources/ONBOARDING.md",
    "resources/RECOVERY.md",
    "resources/MEMORY_EXCLUSIONS.md",
]

# An invocation of sv's CLI entry point from inside a test.
SV_MAIN = re.compile(r"sv\.main\(\)|cdsfl_sv\.py['\"]")
DRY = re.compile(r"--dry-run")
# cwd pointing at the real repository rather than a tmp_path
REAL_CWD = re.compile(r"cwd\s*=\s*(REPO|REPO_ROOT|str\(REPO\)|str\(REPO_ROOT\))\b")


def _test_files():
    return sorted(p for p in TESTS.glob("test_*.py"))


def test_the_corpus_is_actually_being_read():
    """A scan that silently matches nothing passes forever."""
    files = _test_files()
    assert len(files) > 50, f"only {len(files)} test files found; the glob is wrong"
    assert any(SV_MAIN.search(p.read_text(encoding="utf-8", errors="replace"))
               for p in files), (
        "no test invokes sv.main() anywhere, so this guard is inert. If the sv "
        "end-to-end test was deleted, delete this guard with it."
    )


@pytest.mark.parametrize("path", _test_files(), ids=lambda p: p.name)
def test_no_test_runs_sv_against_the_real_repo_without_dry_run(path):
    src = path.read_text(encoding="utf-8", errors="replace")
    if not SV_MAIN.search(src):
        return
    if not REAL_CWD.search(src):
        return  # runs somewhere else entirely; nothing to police
    assert DRY.search(src), (
        f"{path.name} invokes sv's main with cwd set to the REAL repository and "
        "no --dry-run. sv regenerates "
        + ", ".join(CANONICAL[:3])
        + " when it runs, so every suite run would dirty the working tree. Pass "
          "--dry-run: it exercises the same path and writes nothing (measured "
          "2026-08-26 -- dry run dirties 0 files, live run dirties 3)."
    )


def test_the_guard_would_catch_the_original_defect():
    """Commissioning. Feed it the code as it was on 2026-08-26 and it must fail;
    feed it the fix and it must pass. Otherwise the guard is decoration."""
    before = ("import cdsfl_sv as sv\n"
              "subprocess.run([sys.executable, '-c', \"sys.argv = ['cdsfl_sv.py']; "
              "sys.exit(sv.main())\"], cwd=REPO)\n")
    after = ("import cdsfl_sv as sv\n"
             "subprocess.run([sys.executable, '-c', \"sys.argv = ['cdsfl_sv.py', "
             "'--dry-run']; sys.exit(sv.main())\"], cwd=REPO)\n")
    elsewhere = ("import cdsfl_sv as sv\n"
                 "subprocess.run([...], cwd=tmp_path)\n")

    def offends(src):
        return bool(SV_MAIN.search(src)) and bool(REAL_CWD.search(src)) and not DRY.search(src)

    assert offends(before), "the guard does not catch the defect it was written for"
    assert not offends(after), "the guard rejects the accepted fix"
    assert not offends(elsewhere), "the guard fires on a test that uses a tmp cwd"
