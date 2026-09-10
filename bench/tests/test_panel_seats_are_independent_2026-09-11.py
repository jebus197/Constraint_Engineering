"""Each panel seat must get its OWN sandbox, or its verdict is not independent.

THE FINDING, measured in panel round 10 on 2026-09-11. `confer_maths_panel`
built ONE sandbox and ran every seat in it CONCURRENTLY, through a
`ThreadPoolExecutor`. The seats are told to write their fixes into that tree at
real paths, so a seat could read -- and did read -- another seat's edits.

IT IS NOT A THEORETICAL RISK. In round 10 the fable seat's reply describes the
`.zenodo.json` identity tier that the cc2 seat had just invented, and its own
figures section records "my first (background) run reported 33/640 from a stale
`.pyc` (old `repo_paths.py` with no declared tier)". Fable reviewed cc2's edited
tree rather than the tree under review.

WHY THAT MATTERS MORE THAN IT SOUNDS. The founder's `pr` protocol says the panel
runs "WITHOUT compelled convergence so each model returns an independent verdict
and its strongest falsification, and disagreement is preserved as information
rather than smoothed to consensus". Agreement between seats sharing a writable
directory is not evidence of anything -- the second seat may simply be reading
the first's answer. The project already has a memory titled "no model voting"
for the weaker version of this problem.

AND THE PROPOSALS WERE UNATTRIBUTABLE. `seat_proposals.diff` was the union of
every seat's edits with no name against any of them: round 10 produced 29 files
and no way to tell who wrote which. The project's own "no fake model labels" rule
exists because provenance that cannot be established is provenance that gets
invented.

WHAT WAS NOT WRONG, so the fix is not oversold. Sharing did not let a seat reach
the canonical tree; confinement worked. The failure is in INDEPENDENCE and
ATTRIBUTION, not containment.

COST, MEASURED BEFORE THE CHANGE: 6.53 s and 606 MB per sandbox on this machine,
so a 2-seat round pays 13 s against a 15-to-25-minute panel.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "bench" / "confer_maths_panel_2026-09-05.py"


def _main_body() -> ast.FunctionDef:
    tree = ast.parse(PANEL.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            return node
    raise AssertionError("confer_maths_panel has no main()")


class TestOneSandboxPerSeat:
    def test_build_is_called_once_per_seat_not_once_per_run(self):
        """The defect, stated as code rather than as prose: `build` must sit
        inside a loop over MODELS, not at top level of main()."""
        main = _main_body()
        builds = [n for n in ast.walk(main)
                  if isinstance(n, ast.Call)
                  and getattr(n.func, "attr", None) == "build"]
        assert builds, "the panel no longer builds a sandbox at all"
        in_loop = []
        for node in ast.walk(main):
            if isinstance(node, (ast.For, ast.AsyncFor, ast.comprehension)):
                for sub in ast.walk(node if not isinstance(node, ast.comprehension)
                                    else ast.Module(body=[], type_ignores=[])):
                    if isinstance(sub, ast.Call) and \
                            getattr(sub.func, "attr", None) == "build":
                        in_loop.append(sub)
        assert in_loop, (
            "panel_sandbox.build is not inside a loop, so every seat shares 1 "
            "writable copy and their verdicts are not independent")

    def test_the_seat_map_exists_and_is_read_by_dispatch(self):
        src = PANEL.read_text(encoding="utf-8")
        assert "_SEAT_SANDBOXES" in src
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "dispatch":
                names = {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}
                assert "_SEAT_SANDBOXES" in names, (
                    "dispatch does not consult the per-seat map, so seats still "
                    "share whatever the module-level path says")
                return
        raise AssertionError("confer_maths_panel has no dispatch()")

    def test_every_sandbox_is_torn_down(self):
        """N-1 sandboxes left behind is 606 MB each AND a seat's proposals still
        on disk after they were supposed to be harvested."""
        main = _main_body()
        teardowns = [n for n in ast.walk(main)
                     if isinstance(n, ast.Call)
                     and getattr(n.func, "attr", None) == "teardown"]
        assert teardowns, "nothing is torn down"
        for node in ast.walk(main):
            if isinstance(node, ast.For):
                if any(isinstance(sub, ast.Call)
                       and getattr(sub.func, "attr", None) == "teardown"
                       for sub in ast.walk(node)):
                    return
        raise AssertionError(
            "teardown is not inside a loop, so only 1 of N sandboxes is removed")


class TestProposalsCarryTheirAuthor:
    def test_the_diff_key_is_prefixed_with_the_seat(self):
        """Provenance that cannot be established is provenance that gets
        invented -- the reason this project forbids fake model labels."""
        # READ AS CODE. The proposals dict must be keyed by an f-string that
        # joins the SEAT NAME to the path. A text search over a source window
        # would pass on a comment saying so, which is the substring-versus-token
        # defect this project has hit 7 times.
        main = _main_body()
        joined = []
        for node in ast.walk(main):
            if isinstance(node, ast.JoinedStr):
                names = {getattr(v.value, "id", None)
                         for v in node.values if isinstance(v, ast.FormattedValue)}
                if "_n" in names and "rel" in names:
                    joined.append(node)
        assert joined, (
            "no proposals key joins the seat name to the path, so the diff is "
            "the union of every seat's edits with nothing to attribute them")


class TestTheSandboxesAreActuallyDistinct:
    """The execution half. The AST checks above prove the SHAPE; this proves 2
    builds give 2 directories that cannot see each other."""

    def test_two_builds_are_separate_trees(self, tmp_path):
        sys.path.insert(0, str(ROOT / "bench"))
        import panel_sandbox

        src = tmp_path / "src"
        (src / "bench").mkdir(parents=True)
        (src / "bench" / "x.py").write_text("original\n", encoding="utf-8")
        a = panel_sandbox.build(src)
        b = panel_sandbox.build(src)
        try:
            assert a != b, "2 builds returned the same directory"
            (a / "bench" / "x.py").write_text("seat A wrote this\n", encoding="utf-8")
            assert (b / "bench" / "x.py").read_text() == "original\n", (
                "seat B can see seat A's edit; the sandboxes are not independent")
            changed_a = panel_sandbox.changes(a, src)
            changed_b = panel_sandbox.changes(b, src)
            assert "bench/x.py" in changed_a
            assert "bench/x.py" not in changed_b, (
                "seat B is credited with seat A's change")
        finally:
            panel_sandbox.teardown(a)
            panel_sandbox.teardown(b)
