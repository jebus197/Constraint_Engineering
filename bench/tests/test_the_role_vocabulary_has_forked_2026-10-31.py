"""GUARD: the structural role vocabulary, and the type checker's blindness.

FOUND 2026-10-31 by doing what the founder's ruling requires before a
seat-written fix is folded back: *"Any fixes emerging from these briefs should
be tested with a, f, sy, before folding back into the runners and to the
project at large."*

Testing the 4 seat-written tests from the B21 round surfaced 3 things: the live
tree constructs role values outside its own declared `Literal`; the 2 seats'
scanners disagree because only one handles a conditional expression; and the
`mypy_check` tool offered to every panel seat reports success on files whose
project types it never resolved.

WHAT THESE TESTS PIN, AND WHAT THEY DELIBERATELY DO NOT. They pin
RELATIONSHIPS, not counts. Pinning "4 undeclared sites" would turn red the
moment someone correctly fixes one, which is the guard-accuses-correct-code
class measured at 9 of 36 on 2026-10-28. And they take NO position on B21's
open question -- whether the structural enum and the founder's functional
vocabulary are 1 dimension or 2 is his to decide, and these tests hold
whichever way he rules.
"""
from __future__ import annotations

import ast
import pathlib
import subprocess
import sys
import typing

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.experiment_11_orchestrator import (  # noqa: E402
    ExperimentConfig, ModelConfig, Role,
)


def _live_files():
    return [p for p in sorted((REPO / "bench").rglob("*.py"))
            if "logs" not in p.parts and "tests" not in p.parts]


def _scan(paths, handle_ifexp: bool):
    hits = []
    for p in paths:
        try:
            tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        except (SyntaxError, OSError):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fn = node.func
            name = fn.id if isinstance(fn, ast.Name) else (
                fn.attr if isinstance(fn, ast.Attribute) else "")
            if name != "ModelConfig":
                continue
            for kw in node.keywords:
                if kw.arg != "role":
                    continue
                vals = []
                if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                    vals = [kw.value.value]
                elif handle_ifexp and isinstance(kw.value, ast.IfExp):
                    for arm in (kw.value.body, kw.value.orelse):
                        if isinstance(arm, ast.Constant) and isinstance(arm.value, str):
                            vals.append(arm.value)
                for v in vals:
                    # A PLANTED PROBE FILE LIVES OUTSIDE THE REPO, so
                    # relative_to raises. cc2's scanner handled this and the
                    # first version of mine did not, which failed its own
                    # anti-vacuity controls.
                    try:
                        shown = p.relative_to(REPO).as_posix()
                    except ValueError:
                        shown = p.name
                    hits.append((shown, node.lineno, v))
    return hits


DECLARED = set(typing.get_args(Role))


class TestTheScannerIsNotBlind:
    def test_the_scan_finds_real_construction_sites(self):
        """ANTI-VACUITY. Both seats wrote this control and BOTH appeared to
        fail until the files were run at the depth they were written for --
        their `parents[2]` resolved to the seat's own folder, so the scan was
        looking at a directory holding only tests. The control was right and
        the harness running it was wrong."""
        hits = _scan(_live_files(), handle_ifexp=True)
        assert len(hits) >= 3, (
            f"only {len(hits)} ModelConfig role site(s) found; the scan has "
            f"gone blind and every assertion below would pass vacuously")

    def test_a_planted_stray_is_seen(self, tmp_path):
        planted = tmp_path / "planted.py"
        planted.write_text(
            'mc = ModelConfig(label="x", role="striker")\n', encoding="utf-8")
        hits = _scan([planted], handle_ifexp=True)
        assert any(v == "striker" for _, _, v in hits)

    def test_a_conditional_arm_is_seen_only_when_handled(self, tmp_path):
        """THE MEASURED DIFFERENCE BETWEEN THE 2 SEATS' SCANNERS.

        cc2 accepted only `ast.Constant`; fable also walked both arms of an
        `ast.IfExp` and said so in its docstring. The site that distinguishes
        them is in the SIMULATED RUNNER, so a fold-back that took cc2's
        scanner alone would be blind to the one site that matters most.
        """
        planted = tmp_path / "cond.py"
        planted.write_text(
            'mc = ModelConfig(label="x",\n'
            '                 role="player_manager" if i == 0 else "player")\n',
            encoding="utf-8")
        assert any(v == "player" for _, _, v in _scan([planted], handle_ifexp=True))
        assert not _scan([planted], handle_ifexp=False), (
            "the constant-only scanner saw a conditional, so this test no "
            "longer distinguishes the 2 designs")


class TestTheForkIsRecordedAsARelationship:
    def test_every_constructed_role_is_declared_or_knowingly_undeclared(self):
        """THE RELATIONSHIP, NOT THE COUNT.

        This does not assert "0 strays" -- that would be a claim the tree
        currently fails, and turning the board red is the founder's call. It
        asserts that the set of undeclared spellings is EXACTLY the set
        recorded here, so a NEW fork is caught while the known ones do not
        keep failing. Fixing a site shrinks the set and this test then names
        what changed, which a bare count cannot do.
        """
        # ★ NARROWED TO EMPTY 2026-11-01, WHICH IS THIS PIN WORKING. It
        # recorded {"player", "reviewer"} -- 9 and 4 occurrences found by the
        # round-1 AST scan. Both are now normalised at their 4 live sites in
        # `bench/tools/`, on his acceptance of the panel's recommendation, so
        # the undeclared set is EMPTY and the fork is closed in the live tree.
        #
        # AN EMPTY PIN IS THE STRONGEST FORM: any new member is a regression,
        # with nothing to argue about. The same shape as the empty
        # `STILL_ASKING` pin in the ruled-entry guard.
        #
        # THE RESOLVER DOES NOT MAKE THIS REDUNDANT, which is why both halves
        # were folded back. `canonical_role` normalises at CONSTRUCTION, so a
        # stray literal still RUNS correctly -- and this scan is what notices
        # the source said something nobody declared. The second seat measured
        # exactly that: with the resolver alone an in-tree stray is silently
        # missed, and with this scan alone a runtime spelling survives
        # undeclared. Neither part does both.
        KNOWN_UNDECLARED: set[str] = set()
        constructed = {v for _, _, v in _scan(_live_files(), handle_ifexp=True)}
        undeclared = constructed - DECLARED
        assert undeclared == KNOWN_UNDECLARED, (
            f"the undeclared role set CHANGED.\n"
            f"  recorded: {sorted(KNOWN_UNDECLARED)}\n"
            f"  now:      {sorted(undeclared)}\n"
            f"  appeared: {sorted(undeclared - KNOWN_UNDECLARED)}\n"
            f"  resolved: {sorted(KNOWN_UNDECLARED - undeclared)}\n"
            f"If a site was fixed, narrow KNOWN_UNDECLARED. If a new spelling "
            f"appeared, the vocabulary has forked again.")

    def test_the_literal_IS_NOW_ENFORCED_at_runtime(self):
        """★ THE PREMISE CHANGED ON 2026-11-01, EXACTLY AS THIS TEST WARNED.

        It used to assert that an out-of-vocabulary role SURVIVED, with the
        message "so the premise of this whole finding has changed" -- and it
        has: he accepted the panel's recommendation on role assignment and the
        composed repair was folded back, so `ModelConfig.__post_init__` now
        resolves every spelling through `canonical_role`.

        A Literal is still only a static annotation. What changed is that the
        constructor checks it, which is the whole of the repair.
        """
        import pytest as _pt
        with _pt.raises(ValueError, match="unknown ModelConfig role"):
            ModelConfig(label="x", model_id="s", api="sim",
                        role="striker", system_prompt_path=None)

    def test_an_aliased_spelling_normalises_rather_than_raising(self):
        """ANTI-VACUITY FOR THE TEST ABOVE: a constructor that refused every
        spelling would pass it and break every live run. The 2 measured
        undeclared spellings resolve instead."""
        for spelling in ("player", "reviewer"):
            mc = ModelConfig(label="x", model_id="s", api="sim",
                             role=spelling, system_prompt_path=None)
            assert mc.role == "participant", (spelling, mc.role)

    def test_the_declared_selector_silently_excludes_a_forked_spelling(self):
        """THE CONCRETE FAILURE PATH, which is why the fork is not cosmetic.

        `run_simulated_experiment.py` builds its non-first models as
        `role="player"`, intending participants. `get_by_role("participant")`
        compares for EQUALITY, so those seats are invisible to it. Latent
        today only because `get_by_role` has 0 callers; a future caller
        inherits a silent exclusion.
        """
        cfg = ExperimentConfig(models=[
            ModelConfig(label="as_the_runner_builds_it", model_id="s",
                        api="sim", role="player", system_prompt_path=None),
            ModelConfig(label="spelled_as_declared", model_id="s", api="sim",
                        role="participant", system_prompt_path=None),
        ])
        got = [m.label for m in cfg.get_by_role("participant")]
        # ★ THE SILENT EXCLUSION IS GONE, 2026-11-01. This asserted that the
        # runner-spelled seat was INVISIBLE to the declared selector, which was
        # the concrete failure path and the reason the fork was not cosmetic.
        # The folded-back resolver normalises the spelling at construction, so
        # both seats are now found. The failure path is closed rather than
        # documented, which is what his acceptance of the panel's
        # recommendation was for.
        assert got == ["as_the_runner_builds_it", "spelled_as_declared"], got
        assert "as_the_runner_builds_it" in got, (
            "the runner-spelled seat is invisible to the declared selector "
            "again, so the fork has returned")


class TestTheTypeCheckerReportsOkOnWhatItCannotType:
    """NOT ABOUT ROLES. Generalised from one of the 2 mypy misses.

    `bench/openrouter_tools.py` runs `mypy <path> --no-error-summary
    --ignore-missing-imports` from the repo root. There is no mypy config in
    the tree and no `bench/__init__.py`. A file importing a project module by
    BARE name therefore has that symbol resolved to `Any`, and mypy reports
    `Success: no issues found` on a file whose project types it never checked.
    """

    def _reveal(self, tmp_path, import_line: str) -> str:
        probe = tmp_path / "probe.py"
        probe.write_text(
            f"{import_line}\nreveal_type(ModelConfig)\n", encoding="utf-8")
        r = subprocess.run(
            [sys.executable, "-m", "mypy", str(probe), "--no-error-summary",
             "--ignore-missing-imports", "--no-pretty"],
            cwd=str(REPO), capture_output=True, text=True, timeout=180)
        return (r.stdout or "") + (r.stderr or "")

    def test_a_bare_import_reduces_a_typed_constructor_to_Any(self, tmp_path):
        out = self._reveal(
            tmp_path, "from experiment_11_orchestrator import ModelConfig")
        assert 'Revealed type is "Any"' in out, (
            "the bare import now resolves, so mypy is no longer blind here -- "
            f"which would be good news and makes this test stale.\n{out[-800:]}")

    def test_the_package_import_does_resolve_the_literal(self, tmp_path):
        """ANTI-VACUITY for the test above: it must be the IMPORT STYLE that
        decides, not mypy failing on everything."""
        out = self._reveal(
            tmp_path, "from bench.experiment_11_orchestrator import ModelConfig")
        assert "Literal['collator']" in out or "'collator'" in out, (
            f"the package import did not resolve the Literal either, so the "
            f"bare-import test proves nothing about import style.\n{out[-800:]}")

    def test_most_live_files_use_the_blind_import_style(self):
        """The reach of it, pinned as a relationship rather than a count."""
        project_modules = {q.stem for q in (REPO / "bench").glob("*.py")}
        bare, pkg = set(), set()
        for q in _live_files():
            try:
                tree = ast.parse(q.read_text(encoding="utf-8", errors="replace"))
            except (SyntaxError, OSError):
                continue
            for n in ast.walk(tree):
                if isinstance(n, ast.ImportFrom) and n.module:
                    root = n.module.split(".")[0]
                    if root == "bench":
                        pkg.add(q)
                    elif root in project_modules:
                        bare.add(q)
        assert bare, "no bare-import file found; the finding would be withdrawn"
        assert pkg, "no package-import file found; the comparison is vacuous"
        assert len(bare) > len(pkg - bare), (
            f"the blind style is no longer the majority: {len(bare)} bare "
            f"against {len(pkg - bare)} package-only. Good news, and this "
            f"test should then be re-pinned.")


class TestTheSeatArtefactsAreAdjudicated:
    SEAT_DIR = (REPO / "experimental_notes" / "seat_evidence"
                / "joint_the_role_layer_b21_2026-10-31")

    def test_the_two_seats_wrote_different_files_under_one_name(self):
        """A NAIVE FOLD-BACK WOULD LOSE ONE OF THEM.

        Both seats independently chose the name
        `test_the_structural_role_vocabulary_cannot_fork_silently_2026-10-31.py`
        and their contents differ, so copying both into `bench/tests/` would
        have one silently overwrite the other.
        """
        if not self.SEAT_DIR.is_dir():
            pytest.skip("the preserved seat evidence is not in this checkout")
        name = "test_the_structural_role_vocabulary_cannot_fork_silently_2026-10-31.py"
        a = self.SEAT_DIR / "cc2" / "bench" / "tests" / name
        b = self.SEAT_DIR / "fable" / "bench" / "tests" / name
        if not (a.is_file() and b.is_file()):
            pytest.skip("one of the 2 same-named seat files is absent")
        assert a.read_bytes() != b.read_bytes(), (
            "the 2 files are now identical, so the collision is no longer a "
            "fold-back hazard")

    def test_the_seat_fix_IS_NOW_IN_THE_TREE_so_its_test_is_foldable(self):
        """★ INVERTED 2026-11-01, AND THE OLD VERSION TOLD ME TO DO IT.

        It asserted that `ROLE_ALIASES` did NOT exist, because preservation had
        kept a seat's test and not its implementation, so folding that test back
        would have added a permanently-red guard for absent code. Its own
        message said "ROLE_ALIASES now exists in the tree, so cc2's test is
        foldable and this test is stale".

        It does exist, on his acceptance of the panel's recommendation, so the
        condition the old test was protecting has been satisfied rather than
        bypassed.
        """
        import bench.experiment_11_orchestrator as orch
        assert hasattr(orch, "ROLE_ALIASES"), (
            "ROLE_ALIASES has gone from the tree, so the folded-back repair has "
            "been reverted and the seat test it supports is red for real")
        assert callable(getattr(orch, "canonical_role", None)), (
            "the resolver is gone, so the aliases are data nothing reads")
