"""The founder reads 3 files from his Desktop. They must not silently diverge.

MEASURED, not anticipated. On 2026-09-10 at 10:30 BST he asked whether the
outcomes companion "on my desktop (which I presume you have been updating)" was
current. It was not: the master task list was 29,044 bytes short and 3.45 h
behind its canonical copy, and the outcomes log 5,016 bytes short and 3.40 h
behind. 1 of 3 mirrors was current.

The same class of staleness had already cost him a journey. On 2026-09-09 a
restore read a stale line and reported that an answer-key sealing awaited him; he
had driven home from his hotel and done it himself on 2026-09-07 at 22:03. Task
V5 fixed the ORDER in which documents are read. It could not stop a mirror
drifting, and `cdsfl_recover.py` could not even SEE 2 of the 3 mirrors.

Three things are held here: the sync exists and works, the restore names all 3
and reports divergence, and the commit hook refreshes them without ever being
able to refuse a commit for it.
"""
from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SYNC = ROOT / "scripts" / "sync_desktop_mirrors.py"
HOOK = ROOT / "hooks" / "pre-commit"


def _load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def sync():
    return _load(SYNC)


class TestTheSyncWorks:
    def test_it_names_the_five_files_the_founder_reads(self, sync):
        """5, not 4 -- and 4, not 3, before panel round 8 found the 5th.

        The 5th is `Exp40_to_54_Consolidated_Plan_2026-04-21.md`, mirrored (and
        RENAMED) to `~/Desktop/CDSFL_Consolidated_Plan_2026-04-21.md`, declared
        verbatim by tracker item C3, present on the Desktop and DIVERGED on
        2026-09-10, and caught by neither direction of this test's first
        version: the declaration regex required the Desktop path within 20
        non-backtick characters of "mirror", and C3 puts the repo path there.

        `RUNWAY_to_BR2_2026-08-18.md` declares its mirror, at its own line 229,
        as `~/Desktop/CDSFL_RUNWAY.md` -- a different name from the repository
        file. The old table held bare filenames on the stated reasoning that "the
        mirror must never be renamed", which was already untrue when written, so
        the renamed mirror was simply absent and refreshed by nothing.
        """
        assert set(sync.MIRRORS) == {
            ("experimental_notes/CDSFL_MASTER_TASK_LIST.md",
             "CDSFL_MASTER_TASK_LIST.md"),
            ("experimental_notes/CDSFL_OUTCOMES_LOG.md",
             "CDSFL_OUTCOMES_LOG.md"),
            ("experimental_notes/CDSFL_Agent_Operational_Plan.md",
             "CDSFL_Agent_Operational_Plan.md"),
            ("experimental_notes/RUNWAY_to_BR2_2026-08-18.md",
             "CDSFL_RUNWAY.md"),
            ("experimental_notes/Exp40_to_54_Consolidated_Plan_2026-04-21.md",
             "CDSFL_Consolidated_Plan_2026-04-21.md"),
        }

    def test_a_renamed_mirror_is_expressible_at_all(self, sync):
        """The structural point, asserted rather than assumed.

        A table of bare names cannot represent a mirror whose Desktop name
        differs from its repository name. That is not a style preference: it is
        why the RUNWAY was missing for the whole life of the previous table.
        """
        renamed = [(r, d) for r, d in sync.MIRRORS if not r.endswith("/" + d)]
        assert renamed, ("no renamed mirror is present, so this table has not "
                         "been shown to express one -- and one exists")

    def test_every_consumer_reads_this_one_table(self, sync):
        """EXECUTED, not grepped. 3 tables existed and all 3 disagreed.

        `scripts/sync_desktop_mirrors.py` held 3 names, the drift guard held 2
        pairs, and `scripts/cdsfl_recover.py` held 3 names again. The union is 4
        and the intersection is 1. Each consumer is imported and its live table
        compared to the source, so a consumer that quietly forks its own copy
        fails here rather than 9 days later.
        """
        drift_guard = _load(ROOT / "bench" / "tests"
                            / "test_documentation_drift_guards_2026-08-25.py")
        guarded = {(r, d.name) for r, d in drift_guard.DECLARED_MIRRORS}
        assert guarded == set(sync.MIRRORS), (
            "the drift guard checks a different set from the one the refresher "
            "repairs; the difference is the gap")

        recover = _load(ROOT / "scripts" / "cdsfl_recover.py")
        restored = {(repo_rel, name)
                    for name, (repo_rel, _) in recover.DESKTOP_MIRRORS.items()}
        assert restored == set(sync.MIRRORS), (
            "the restore reports on a different set from the one that is "
            "guarded, so it can call a stale mirror ordinary")

    def test_each_pair_is_confirmed_by_the_projects_own_prose(self, sync):
        """A hand list is only as good as the thing it claims to summarise.

        The panel named this on 2026-09-01: "DECLARED_MIRRORS in the drift-guard
        test is a hand list, while the docs' own text is the truth source." Each
        pair must be backed by a declaration somewhere in the project's notes,
        so the table cannot drift away from what the documents say about
        themselves.
        """
        notes = ROOT / "experimental_notes"
        prose = "\n".join(
            f.read_text(encoding="utf-8", errors="replace")
            for f in notes.rglob("*.md"))
        for repo_rel, desktop_name in sync.MIRRORS:
            assert f"~/Desktop/{desktop_name}" in prose, (
                f"{repo_rel} is mirrored to {desktop_name}, but no note in the "
                f"project declares that mirror. Either the table invented it or "
                f"the document forgot to say so.")

    def test_no_declared_mirror_is_missing_from_the_table(self, sync):
        """The reverse direction, which is the one that actually bit.

        The RUNWAY declared its mirror in its own text and no table held it. A
        document that says it is mirrored and is not in the table is exactly
        that failure returning.
        """
        notes = ROOT / "experimental_notes"
        # WIDENED BY PANEL ROUND 8 (2026-09-10). The first version required
        # the Desktop path within 20 NON-BACKTICK characters of "mirror", so a
        # declaration of the form "Mirrored `repo/path.md` -> `~/Desktop/X.md`"
        # -- tracker item C3's exact phrasing -- could not match: the repo path
        # occupies that span first and contains backticks. The live 5th mirror
        # escaped exactly this way. The widened pattern allows anything on the
        # same line within 120 chars, and was ENUMERATED over the notes before
        # shipping: it yields exactly the 5 known mirrors and nothing else, so
        # the widening adds no false positives today.
        pat = re.compile(
            r"[Mm]irror[^\n]{0,120}?`~/Desktop/([A-Za-z0-9_.-]+\.md)`")
        declared = set()
        for f in notes.rglob("*.md"):
            for m in pat.finditer(f.read_text(encoding="utf-8", errors="replace")):
                declared.add(m.group(1))
        known = {d for _, d in sync.MIRRORS}
        # A document may name ANOTHER document's mirror -- the task list names the
        # outcomes log's at its line 5 -- so this checks membership of the known
        # set, not authorship of the sentence.
        missing = declared - known
        assert not missing, (
            f"these Desktop mirrors are declared in the notes and held by no "
            f"table, so nothing refreshes or guards them: {sorted(missing)}")

    def test_drift_is_detected_and_repaired(self, sync, tmp_path, monkeypatch):
        """Drive it against a fake Desktop, so the real one is not touched."""
        fake = tmp_path / "Desktop"
        fake.mkdir()
        monkeypatch.setattr(sync, "DESKTOP", fake)
        assert len(sync.drift()) == len(sync.MIRRORS), (
            "an empty Desktop must report every mirror missing")
        assert sync.main.__call__ is not None
        monkeypatch.setattr(sys, "argv", ["sync"])
        assert sync.main() == 0
        assert sync.drift() == [], "after a sync, nothing should be adrift"

    def test_a_diverged_copy_is_detected(self, sync, tmp_path, monkeypatch):
        fake = tmp_path / "Desktop"
        fake.mkdir()
        monkeypatch.setattr(sync, "DESKTOP", fake)
        monkeypatch.setattr(sys, "argv", ["sync"])
        sync.main()
        victim = fake / "CDSFL_OUTCOMES_LOG.md"
        victim.write_text(victim.read_text(encoding="utf-8") + "\ndrifted\n",
                          encoding="utf-8")
        d = sync.drift()
        assert [n for n, _, _ in d] == ["CDSFL_OUTCOMES_LOG.md"], d

    def test_check_mode_writes_nothing(self, sync, tmp_path, monkeypatch):
        """--check must be safe to run anywhere, including in a test."""
        fake = tmp_path / "Desktop"
        fake.mkdir()
        monkeypatch.setattr(sync, "DESKTOP", fake)
        monkeypatch.setattr(sys, "argv", ["sync", "--check"])
        assert sync.main() == 1
        assert list(fake.iterdir()) == [], "--check created files"

    def test_it_never_copies_desktop_back_over_the_repository(self):
        """The repository copy is canonical by founder ruling of 2026-08-05."""
        src = SYNC.read_text(encoding="utf-8")
        assert "shutil.copy2(src, dst)" in src
        assert "copy2(dst, src)" not in src and "copy(dst, src)" not in src


class TestTheRestoreCanSeeThem:
    def test_first_read_names_every_mirror(self, sync):
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / "cdsfl_recover.py")],
                           cwd=ROOT, capture_output=True, text=True, timeout=600)
        assert r.returncode == 0, r.stderr[-800:]
        first = r.stdout.split("## RUNNING NOW")[0]
        # DERIVED from the single table, so a mirror added there is required to
        # appear here too. Typed, this listed 3 while 4 existed.
        for name in (d for _, d in sync.MIRRORS):
            assert f"Desktop/{name}" in first, (
                f"the restore does not name the Desktop copy of {name}, so it "
                f"cannot warn that what the founder is reading is stale")

    def test_a_diverged_mirror_is_announced_loudly(self, sync, tmp_path, monkeypatch):
        """The load-bearing case: silence about divergence is the whole defect."""
        R = _load(ROOT / "scripts" / "cdsfl_recover.py")
        fake = tmp_path / "Desktop"
        fake.mkdir()
        (fake / "CDSFL_MASTER_TASK_LIST.md").write_text("stale", encoding="utf-8")
        # SUBSTITUTE `DESKTOP_MIRROR`, NOT `Path.home` (changed 2026-09-10).
        #
        # The assertion below is untouched -- a diverged copy must be announced.
        # Only the substitution point moved, and it moved because the module now
        # has ONE: every mirror path is derived from `DESKTOP_MIRROR`, which
        # exists to be displaced. Patching `Path.home` used to work because each
        # path was rebuilt inline from it, which is the very thing
        # `test_the_desktop_mirror_is_a_module_constant` forbids -- and that test
        # went red when the inline call came back, with the live machine's
        # Desktop leaking into a tmp_path run. The 2 fixtures wanted opposite
        # structures; the module constant is the correct one.
        monkeypatch.setattr(R, "DESKTOP_MIRROR",
                            fake / "CDSFL_Agent_Operational_Plan.md")
        out = "\n".join(R.first_read_lines(ROOT))
        assert "DIVERGED" in out, "a diverged Desktop copy was reported as ordinary"


class TestTheHookRefreshesButCannotRefuse:
    def test_the_hook_calls_the_sync(self):
        src = HOOK.read_text(encoding="utf-8")
        assert "sync_desktop_mirrors.py" in src, (
            "the hook does not refresh the mirrors, so they will drift again")

    #: Every stage-0 block that REPAIRS something. None of these may refuse.
    REPAIR_BLOCKS = (
        "scripts/sync_desktop_mirrors.py",
        "scripts/experiment_run_ledger.py",
        "scripts/citation_content_guard_2026-09-10.py",
    )

    def _block(self, src: str, script: str) -> str:
        """The `if [ -f <script> ]; then ... fi` block, and nothing else."""
        start = src.index(f"if [ -f {script} ]")
        end = src.index("\nfi\n", start) + len("\nfi\n")
        return src[start:end]

    def test_no_stage_zero_REPAIR_can_exit_non_zero(self):
        """A repair must never block a commit. Narrowed 2026-09-11, and the
        narrowing is a tightening rather than a loosening.

        It used to slice the WHOLE of stage 0 and forbid `exit 1` anywhere in
        it. That was sound while stage 0 held only repairs. It stopped being
        sound when stage 0 gained something that is NOT a repair: a check that
        `hooks/stage0_restage.sh` is present. Without that file the repairs
        write the working tree and never reach the commit, so every commit ships
        unrepaired content and every clone at HEAD is broken -- measured
        2026-09-11 as 3 failures in a clone against 0 here. That is an
        infrastructure fault, and the hook's own header already says an
        infrastructure fault blocks, loudly.

        So the invariant is now stated on the thing it was always about: each
        REPAIR block individually. Three blocks are checked instead of one
        region, which is a stronger statement than the old one, not a weaker."""
        src = HOOK.read_text(encoding="utf-8")
        for script in self.REPAIR_BLOCKS:
            block = self._block(src, script)
            assert "exit 1" not in block and "exit 2" not in block, (
                f"the stage-0 repair running {script} can refuse a commit; a "
                f"repair must repair and report, never block:\n{block}")

    def test_the_only_stage_zero_refusal_is_the_missing_helper(self):
        """ANTI-DRIFT. The test above is per block, so a new refusal added
        BETWEEN the blocks would not be seen by it. This counts them."""
        src = HOOK.read_text(encoding="utf-8")
        i = src.index("# STAGE 0 --")
        stage = src[i:src.index('MISSING=""', i)]
        assert "sync_desktop_mirrors.py" in stage, "wrong block sliced"
        assert stage.count("exit 1") == 1, (
            f"stage 0 now contains {stage.count('exit 1')} refusals; exactly 1 "
            f"is expected, the missing-helper check. Anything else must be "
            f"argued here before it is added.")
        assert "RESTAGE_LIB" in stage, (
            "the 1 permitted refusal is no longer the missing-helper check")

    def test_the_refresh_runs_BEFORE_the_guard_that_checks_mirrors(self):
        """THE ORDERING DEFECT, 2026-09-10. A repair below its own check.

        The refresh was the last stage. One of the guards above it is the mirror
        drift check. So a commit that edited a mirrored file turned that guard
        red, the hook exited 1, and the refresh was never reached. The master
        task list is a mirrored file, so every further commit on the task list
        was refused with the remedy present in the same script and unreachable.
        """
        src = HOOK.read_text(encoding="utf-8")
        assert (src.index("sync_desktop_mirrors.py")
                < src.index("python3 -m pytest -q -p no:cacheprovider $GUARDS")), (
            "the mirror refresh runs after the guards again, so a drifted "
            "mirror refuses the commit that would have repaired it")


class TestTheOrderingActuallyHolds:
    """EXECUTED. The 2 assertions above read the hook; this one RUNS it."""

    def test_a_drifted_mirror_does_not_refuse_the_commit(self, tmp_path):
        """Reproduce the 2026-09-10 refusal and show it no longer happens.

        A fake HOME is given a Desktop holding a deliberately stale copy of every
        mirror. Under the old ordering the drift guard fails and the hook exits
        1. Under the new ordering stage 0 repairs the copies first and the hook
        exits 0. Nothing touches the real Desktop.
        """
        # ONLY THE DESKTOP IS FAKE. Every other entry in HOME is symlinked
        # through to the real one, because 2 of the 7 guards read the founder's
        # memory files under ~/.claude and would fail for reasons that have
        # nothing to do with mirrors. A test that turns unrelated guards red
        # proves nothing about the ordering it claims to test.
        home = tmp_path / "home"
        home.mkdir()
        real = Path.home()
        for entry in real.iterdir():
            if entry.name != "Desktop":
                try:
                    (home / entry.name).symlink_to(entry)
                except OSError:
                    pass
        desk = home / "Desktop"
        desk.mkdir()
        sync = _load(SYNC)
        for repo_rel, desktop_name in sync.MIRRORS:
            (desk / desktop_name).write_text("deliberately stale\n",
                                             encoding="utf-8")
        env = {**os.environ, "HOME": str(home)}
        r = subprocess.run(["sh", str(HOOK)], cwd=ROOT, env=env,
                           capture_output=True, text=True, timeout=900)
        out = r.stdout + r.stderr

        # ---------------------------------------------------------------
        # THE ASSERTION BELOW WAS `r.returncode == 0` AND NOTHING ELSE, AND
        # IT COULD NOT TELL WHICH REFUSAL IT HAD SEEN (round 8, 2026-09-10).
        #
        # `hooks/pre-commit:40` refuses with "cannot find the repository
        # root" BEFORE stage 0 exists, for reasons that have nothing to do
        # with mirror ordering. Run inside a copied tree with no `.git` --
        # which is exactly the panel sandbox -- the hook exits 1 there, and
        # this test reported the ordering fix as BROKEN:
        #
        #     AssertionError: a drifted Desktop mirror still refuses the
        #     commit:  pre-commit: cannot find the repository root. Refusing.
        #
        # That is a FALSE RED on tonight's headline claim, produced by the
        # guard that exists to confirm it. This file's own comment 12 lines
        # above says "a test that turns unrelated guards red proves nothing
        # about the ordering it claims to test" -- and the earliest guard of
        # all was the one it did not account for.
        #
        # TWO REPAIRS, both additive:
        #   1. When the hook's OWN documented precondition is unmet, SKIP
        #      with the reason named. A skip that says why is a result; a red
        #      that misattributes its cause is worse than no test. The skip
        #      is gated on the literal refusal string AND on `.git` being
        #      genuinely absent, so it cannot fire on a real checkout and
        #      cannot become a way to hide a real refusal.
        #   2. When the hook refuses for ANY OTHER reason, say WHICH stage
        #      refused. `returncode == 0` alone names nothing, so every
        #      failure of this test read as "the ordering is broken"
        #      regardless of what actually happened.
        _PRECONDITION = "cannot find the repository root"
        if _PRECONDITION in out and not (ROOT / ".git").exists():
            pytest.skip(
                "the pre-commit hook refuses at hooks/pre-commit:40 before any "
                "mirror stage runs, because this tree has no .git directory. "
                "That is the hook's own precondition, not the mirror ordering. "
                "This test can only speak about the ordering where the hook "
                "can reach stage 0 -- run it in a real checkout.")

        assert r.returncode == 0, (
            "the hook refused the commit. Stage 0 (the Desktop mirror "
            "refresh) "
            + ("DID run, so the refusal came from a later stage and the "
               "ordering fix is not what failed"
               if "sync_desktop_mirrors" in out or "Desktop mirror" in out
               else "did NOT run, so the refusal came from BEFORE the mirror "
                    "refresh -- read the first refusal line below rather than "
                    "concluding the ordering is broken")
            + ":\n" + out[-1500:])
        for _, desktop_name in sync.MIRRORS:
            assert (desk / desktop_name).read_text(encoding="utf-8") \
                != "deliberately stale\n", (
                f"{desktop_name} was not refreshed by the hook")
