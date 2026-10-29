"""Option 3 of entry B29 runs BEFORE the commit, and its margin is real.

HIS RULING, 2026-10-19, on entry B29: *"Verdict: Option 3. Dut do Options 3 and
1 compose, if an event occurs where a save operation does not complete cleanly?"*
(*Dut* is *But*.) Option 3 as he was given it: *"Run the staleness check BEFORE
invoking the save rather than after it refuses. Costs under a third of a second
and turns 2 saves into 1."*

WHAT THIS FILE HOLDS, AND WHY EACH PART IS EXECUTED RATHER THAN READ.

  1. THE CHECK IS REACHED. `additive-standard` forbids an addition nothing
     calls, and this project's record carries 11 confirmed defects of exactly
     that shape against 0 of the opposite. So the wiring is proved by CALLING
     `_preflight_completeness` and finding the check among the verdicts it
     prints, not by searching the source for its name.

  2. THE MARGIN EXISTS. This is the only part that distinguishes Option 3 from
     the postcondition moved earlier. Pre-commit, HEAD is 1 commit behind where
     it will be when the postcondition runs, so a block at exactly the ceiling
     PASSES before and FAILS after -- B29's defect displaced by 1 commit rather
     than repaired. The boundary is tested on BOTH sides against the guard's own
     real ceiling: `ceiling - 1` behind must pass, `ceiling` behind must fail.
     Delete the margin and the second of those goes green, which is the mutation.

  3. IT DOES NOT REFUSE WHERE IT CANNOT ANSWER. A `git archive` export carries
     no `bench/tests`, so the borrowed parser is absent; a block naming no
     resolvable sha cannot be measured. Both report NOT PERFORMED and pass,
     which is how `_check_memory_updated` already treats the same situation, and
     is not the same as asserting the condition holds.

THE FIXTURES ARE BUILT FROM THE LIVE HISTORY ON PURPOSE. `HEAD~59` and `HEAD~60`
are real commits in this repository, so the distance the check measures is the
distance git actually reports rather than a number a mock was told to return.
That is why these tests skip rather than fail outside a checkout with enough
depth: the instrument is git, and without git there is nothing to measure.

Written under CDSFL note standard v1.8.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
GUARD = ROOT / "bench" / "tests" / "test_recovery_session_state_is_current_2026-09-11.py"


@pytest.fixture(scope="module")
def sv():
    spec = importlib.util.spec_from_file_location(
        "cdsfl_sv_under_test", ROOT / "scripts" / "cdsfl_sv.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["cdsfl_sv_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def ceiling():
    spec = importlib.util.spec_from_file_location("_a23", GUARD)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return int(mod.MAX_COMMITS_BEHIND)


def _sha(rev: str) -> str | None:
    r = subprocess.run(["git", "rev-parse", "--short", rev], cwd=ROOT,
                       capture_output=True, text=True, timeout=30)
    return r.stdout.strip() or None


def _block(tmp_path, sha: str) -> pathlib.Path:
    """A minimal RECOVERY.md the borrowed parser accepts, naming one commit."""
    p = tmp_path / "RECOVERY.md"
    p.write_text(
        f"## SESSION STATE — 2026-10-29 02:00 BST (READ THIS FIRST)\n\n"
        f"Branch at `{sha}` before this save.\n",
        encoding="utf-8")
    return p


class TestTheCheckIsReached:
    def test_the_preflight_lists_it(self, sv, capsys):
        """CALLS the pre-flight and reads its verdicts. A source search would
        pass just as well on a check that is defined and never invoked."""
        sv._preflight_completeness(ROOT, apply=False, checking=True)
        printed = capsys.readouterr().out
        assert "recovery-currency" in printed, (
            "the pre-flight ran and never mentioned recovery-currency, so the "
            "check is defined and not wired -- the shape additive-standard names")


class TestTheMargin:
    """The boundary, on both sides, against the guard's own real ceiling."""

    def test_one_inside_the_ceiling_passes(self, sv, ceiling, tmp_path):
        sha = _sha(f"HEAD~{ceiling - 1}")
        if not sha:
            pytest.skip(f"history shallower than {ceiling} commits here")
        got = sv._check_recovery_currency(ROOT, recovery=_block(tmp_path, sha))
        assert got.passed, (
            f"{ceiling - 1} behind plus this save's 1 is exactly the ceiling of "
            f"{ceiling}, which is current: {got.observed}")

    def test_exactly_at_the_ceiling_fails_because_this_save_adds_one(
            self, sv, ceiling, tmp_path):
        """THE MUTATION POINT. Without the margin this goes green, and the
        follow-up save B29 is about returns."""
        sha = _sha(f"HEAD~{ceiling}")
        if not sha:
            pytest.skip(f"history shallower than {ceiling + 1} commits here")
        got = sv._check_recovery_currency(ROOT, recovery=_block(tmp_path, sha))
        assert not got.passed, (
            f"a block exactly {ceiling} commits behind passed the PRE-flight, so "
            f"sv will commit and then fail its own post-condition at "
            f"{ceiling + 1} behind -- which is the defect, moved by 1 commit")
        assert str(ceiling) in got.expected, (
            "the refusal does not name the ceiling it applied")

    def test_the_margin_is_a_parameter_and_zero_restores_the_old_behaviour(
            self, sv, ceiling, tmp_path):
        """Proves the margin is what decides, not some other difference."""
        sha = _sha(f"HEAD~{ceiling}")
        if not sha:
            pytest.skip(f"history shallower than {ceiling + 1} commits here")
        rec = _block(tmp_path, sha)
        assert sv._check_recovery_currency(
            ROOT, recovery=rec, commits_this_save_will_add=0).passed
        assert not sv._check_recovery_currency(
            ROOT, recovery=rec, commits_this_save_will_add=1).passed


class TestItDoesNotRefuseWhereItCannotAnswer:
    def test_a_block_naming_no_sha_is_not_performed(self, sv, tmp_path):
        p = tmp_path / "RECOVERY.md"
        p.write_text("## SESSION STATE — 2026-10-29 02:00 BST (READ THIS FIRST)\n\n"
                     "No commit is named here at all.\n", encoding="utf-8")
        got = sv._check_recovery_currency(ROOT, recovery=p)
        assert got.passed and "not performed" in got.observed.lower(), (
            f"an unmeasurable block was treated as a refusal: {got.observed}")

    def test_a_tree_without_the_guard_is_not_performed(self, sv, tmp_path):
        got = sv._check_recovery_currency(tmp_path)
        assert got.passed and "not performed" in got.observed.lower(), (
            f"a clone with no bench/tests was refused a save: {got.observed}")

    def test_a_current_block_passes(self, sv, tmp_path):
        sha = _sha("HEAD")
        if not sha:
            pytest.skip("not a git checkout")
        got = sv._check_recovery_currency(ROOT, recovery=_block(tmp_path, sha))
        assert got.passed, f"a block naming HEAD was refused: {got.observed}"
