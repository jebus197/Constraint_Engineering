"""Task R6: the blast radius of the absolute-path defect, and whether to revert.

EXECUTED, NOT GREPPED. Every assertion CALLS the measuring script.

THE POSITIVE CONTROLS ARE THE LOAD-BEARING TESTS. The sweep's headline result is
"0 archived runs show a mutated target". A detector that could never fire would
print exactly that, so 2 tests feed synthetic reports through the real classifier
and require it to fire. Without them the null is unfalsifiable, which is the
"a guard that cannot fail is not a guard" defect this project has named 3 times.
"""
from __future__ import annotations

import hashlib
import importlib.util
import pathlib
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "target_mutation_blast_radius_2026-09-10.py"


def _git_history_available() -> bool:
    """A clone without `.git` has no history to interrogate.

    Added 2026-09-17: in such a clone `git log` fails, `committed_sizes` and
    `committed_digests` return empty, and the history tests below FAILED in a
    way indistinguishable from "the history contradicts R6" -- while
    `test_no_observed_rewrite_ever_reached_a_commit` PASSED vacuously against
    an empty history, which is worse. Absence of the instrument must read as
    SKIP, never as a verdict either way.
    """
    r = subprocess.run(["git", "rev-parse", "--git-dir"], cwd=ROOT,
                       capture_output=True)
    return r.returncode == 0


needs_git = pytest.mark.skipif(
    not _git_history_available(),
    reason="no .git in this clone: R6's commit-history claims need a real "
           "checkout; skipping is not passing and not failing")


class TestNoGitIsReportedAsAbsenceNotAsAVerdict:
    """Added at intake, 2026-09-17: the script's own no-.git branch, EXECUTED.

    The repair that added `git_history_available()` to the script was reached by
    no test -- the skip marker above uses its own copy of the predicate -- and
    it left 1 false zero behind: ANSWER TO (a) still printed "never committed:
    0" when nothing had been checked. `main()` is called here with the
    predicate forced False and every commit-history reader instrumented, in a
    real checkout, so this runs everywhere.
    """

    def test_main_asserts_nothing_about_commits_without_git(self, br, monkeypatch,
                                                            capsys):
        monkeypatch.setattr(br, "git_history_available", lambda: False)
        consulted = []
        monkeypatch.setattr(br, "committed_digests",
                            lambda rel: consulted.append(rel) or set())
        monkeypatch.setattr(br, "committed_sizes",
                            lambda rel: consulted.append(rel) or [])
        br.main()
        out = capsys.readouterr().out
        assert out.count("GIT HISTORY UNAVAILABLE") == 2, out[-1500:]
        for verdict in ("NEVER COMMITTED", "never reached a commit",
                        "ABSENT in the history", "NOTHING NEEDS REVERTING",
                        "matches a committed revision",
                        "never committed: 0"):
            assert verdict not in out, f"a verdict without git: {verdict!r}"
        assert "never committed: UNKNOWN" in out
        assert not consulted, (
            f"commit history was consulted with git declared absent: {consulted}")


@pytest.fixture(scope="module")
def br():
    spec = importlib.util.spec_from_file_location("blast_radius", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TestTheDetectorCanFire:
    def test_a_target_that_changed_mid_run_is_caught(self, br):
        """POSITIVE CONTROL for instrument 1."""
        c = br.classify({"target_file": "bench/dm/_memory.py",
                         "target_hashes": {"0": "a" * 64, "1": "b" * 64}})
        assert c["mutated"] is True
        assert len(c["distinct"]) == 2

    def test_an_unchanged_target_is_not_called_mutated(self, br):
        c = br.classify({"target_file": "bench/dm/_memory.py",
                         "target_hashes": {"0": "a" * 64, "1": "a" * 64}})
        assert c["mutated"] is False

    def test_a_run_with_no_hashes_is_neither_clean_nor_dirty(self, br):
        c = br.classify({"target_file": "bench/dm/_memory.py"})
        assert c["hashed"] is False and c["mutated"] is False, (
            "a run with no instrument must not be reported as clean")

    @needs_git
    def test_content_never_committed_is_detectable(self, br):
        """POSITIVE CONTROL for instrument 2, both directions."""
        rel = pathlib.Path("bench/dm/_memory.py")
        known = br.committed_digests(rel)
        assert known, "no committed revision found; the instrument reads nothing"
        real = hashlib.sha256(
            (ROOT / rel).read_bytes()).hexdigest()
        assert real in known, (
            "the working copy matches no committed revision, which would itself "
            "be the finding")
        assert "f" * 64 not in known, "a fabricated digest was accepted as known"

    def test_a_target_outside_the_tree_is_reported_as_such(self, br):
        c = br.classify({"target_file": "/Users/georgejackson/CDSFL_review_targets/x.md",
                         "target_hashes": {"0": "a" * 64}})
        assert c["rel"] is None


class TestTheAnswerToA:
    def test_no_archived_run_shows_a_target_changing_mid_run(self, br):
        import json
        bad = []
        for r in br.reports():
            c = br.classify(json.loads(r.read_text()))
            if c["mutated"]:
                bad.append(r.parent.name)
        assert bad == [], f"runs with a mutated target: {bad}"

    def test_the_coverage_is_reported_rather_than_assumed(self, br):
        """35 of 39 runs carry no target hash. That is the honest half of (a)."""
        import json
        reps = br.reports()
        hashed = [r for r in reps if br.classify(json.loads(r.read_text()))["hashed"]]
        assert len(reps) >= 39, len(reps)
        assert len(hashed) < len(reps), (
            "every run now carries the instrument; the R6 answer's stated "
            "coverage limit no longer holds and should be revisited")


class TestTheAnswerToB:
    @needs_git
    def test_no_observed_rewrite_ever_reached_a_commit(self, br):
        """The decidable half. A rewrite never committed cannot need reverting."""
        for rel, size, where in br.OBSERVED_REWRITES:
            sizes = br.committed_sizes(rel)
            assert size not in sizes, (
                f"{rel} at {size:,} bytes ({where}) IS in the committed history; "
                f"it needs reverting after all")

    @needs_git
    def test_the_size_search_finds_a_size_that_IS_there(self, br):
        """POSITIVE CONTROL. Otherwise 'not in sizes' proves nothing."""
        for rel, expected in br.EXPECTED_SIZE.items():
            sizes = br.committed_sizes(rel)
            assert expected in sizes, (
                f"{rel} has never been committed at its stated correct size "
                f"{expected:,}, so the search above cannot be trusted either")

    @needs_git
    def test_the_file_has_only_the_sizes_its_record_accounts_for(self, br):
        sizes = set(br.committed_sizes("bench/dm/_memory.py"))
        assert 20605 in sizes
        assert len(sizes) == 2, (
            f"bench/dm/_memory.py now has {len(sizes)} distinct committed sizes, "
            f"{sorted(sizes)}; the R6 answer accounted for 2")
