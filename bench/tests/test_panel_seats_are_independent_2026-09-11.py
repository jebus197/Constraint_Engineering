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
so a 2-seat round pays 13 s against a 15-to-25-minute panel. No script produced
that figure when it was written. `scripts/sandbox_build_cost_2026-09-17.py` now
does, run by `bench/tests/test_sandbox_build_cost_2026-09-17.py`; its output
depends on what the checkout holds, because `build` copies untracked files too.
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

    def test_the_seat_map_is_read_on_the_path_dispatch_takes(self):
        """Reachability, not a name lookup in one function's body.

        REWRITTEN 2026-09-11, hours after it was written. The first version
        asserted `_SEAT_SANDBOXES` appeared as a Name inside `dispatch`. Hours
        later the confinement was extracted into `confine_this_thread` -- so
        another source-text guard could EXECUTE it rather than read it -- and
        this one went red while the behaviour was correct and better tested. The
        fourth source-text guard broken by a correct refactor in a single day,
        and the second of them written by me the same day.

        The property is that the map is read SOMEWHERE ON THE PATH DISPATCH
        TAKES, so the chain is followed instead of one frame being inspected.
        """
        src = PANEL.read_text(encoding="utf-8")
        tree = ast.parse(src)
        funcs = {n.name: n for n in ast.walk(tree)
                 if isinstance(n, ast.FunctionDef)}
        assert "dispatch" in funcs, "confer_maths_panel has no dispatch()"

        seen, queue, found = set(), ["dispatch"], False
        while queue:
            name = queue.pop()
            if name in seen or name not in funcs:
                continue
            seen.add(name)
            node = funcs[name]
            if any(isinstance(n, ast.Name) and n.id == "_SEAT_SANDBOXES"
                   for n in ast.walk(node)):
                found = True
                break
            queue.extend(getattr(c.func, "id", "") for c in ast.walk(node)
                         if isinstance(c, ast.Call))
        assert found, (
            f"nothing dispatch reaches consults the per-seat sandbox map "
            f"(followed: {sorted(seen)}), so seats share whatever the "
            f"module-level path says")

    def test_every_sandbox_is_harvested_and_none_is_deleted_behind_the_operator(self):
        """AMENDED 2026-09-17 ON FOUNDER RULING (j), AND THE AMENDMENT REVERSES
        WHAT THIS TEST USED TO DEMAND.

        It required that `main` tear every sandbox down, on the grounds that N-1
        copies left behind cost 606 MB each and leave a seat's proposals on disk
        after they were supposed to be harvested. The founder ruled the other
        way, because the harvest was the part that failed: *"Take care when a
        panel review or an experiment completes however that the sandbox does not
        simply get automatically deleted and that the results do not end up
        simply being discarded, as has happened in the recent past."*

        So the property is now: `main` hands EVERY attempt's tree to the
        retention step, and the retention step keeps the copies unless the
        operator asks for them to go. The disk cost the old test protected
        against is answered by the manifest and the exact removal command the
        step prints, not by deleting a seat's work unasked.

        The behaviour itself is EXECUTED in
        `bench/tests/test_fresh_sandbox_per_attempt_2026-09-17.py`; this holds
        the wiring inside `main`, which no test can call without paying for a
        panel round.
        """
        main = _main_body()
        calls = [n for n in ast.walk(main) if isinstance(n, ast.Call)
                 and getattr(n.func, "id", None) == "harvest_and_retain"]
        assert calls, "main does not harvest the seats' trees on the way out"
        passed = {getattr(a, "id", None) for c in calls for a in c.args}
        assert "_SEAT_ATTEMPTS" in passed, (
            "the retention step is not given every attempt's tree, so a retry's "
            "work can still be discarded -- the round-17 defect")
        bare = [n for n in ast.walk(main) if isinstance(n, ast.Call)
                and getattr(n.func, "attr", None) == "teardown"]
        assert not bare, (
            "main destroys a sandbox directly again; removal belongs in "
            "panel_sandbox.release, which refuses to delete an unharvested copy")


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


def _population_statements(src: str) -> str:
    """main()'s real statements from `sandboxes = {}` through the assignment of
    `_PANEL_SANDBOX_CWD`, i.e. everything between the brief checks and the `try`
    that dispatches. Taken from the dispatcher's own source by AST, so what runs
    here is the code that ships, not a copy of it."""
    main = next(n for n in ast.parse(src).body
                if isinstance(n, ast.FunctionDef) and n.name == "main")
    body = main.body
    loop = next(i for i, n in enumerate(body)
                if isinstance(n, ast.For)
                and any(isinstance(c, ast.Call) and getattr(c.func, "attr", None) == "build"
                        for c in ast.walk(n)))
    start = loop
    if loop and isinstance(body[loop - 1], ast.Assign) and any(
            getattr(t, "id", None) == "sandboxes" for t in body[loop - 1].targets):
        start = loop - 1
    stop = next(i for i in range(loop, len(body)) if isinstance(body[i], ast.Try))
    segment = body[start:stop]
    assigns = {getattr(t, "id", None) for n in segment if isinstance(n, ast.Assign)
               for t in n.targets}
    assert {"sandboxes", "_PANEL_SANDBOX_CWD"} <= assigns, (
        f"main() no longer builds `sandboxes` and sets `_PANEL_SANDBOX_CWD` before "
        f"its dispatch `try`; this test must be re-aimed, not skipped: {assigns}")
    return "\n".join(ast.unparse(n) for n in segment)


class TestThePopulationStepIsExecuted:
    """EXECUTED, because every test above passes with the population line gone.

    FOUND BY PANEL ROUND 16, 2026-09-17. Deleting the single line
    `_SEAT_SANDBOXES[_n] = str(sandboxes[_n])` from a copy of the dispatcher left
    the 5 tests above green: the AST checks see `build` in a loop and the map read
    on the dispatch path, and `test_panel_sandbox_2026-09-07` fills the map
    itself. But with the map empty, `confine_this_thread` falls back to
    `_SEAT_SANDBOXES.get(name) or _PANEL_SANDBOX_CWD`, which main() sets to the
    FIRST seat's sandbox, so every seat would work in 1 shared tree and the
    harvest would file their edits under whichever names it iterates.

    This runs main()'s own population statements, with a stub builder in place
    of the 606 MB copy, then confines each seat in its own worker thread and
    reads back the thread's working directory."""

    SEATS = [("cc2", "opus", "claude_cli"), ("fable", "fable", "claude_cli"),
             ("ds", "deepseek-v4-pro", "deepseek")]

    def test_every_seat_resolves_to_its_own_sandbox(self, tmp_path, monkeypatch):
        import concurrent.futures
        import importlib.util

        spec = importlib.util.spec_from_file_location("panel_population", PANEL)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        from experiment_11_orchestrator import get_panel_cwd, set_panel_cwd

        built = []

        class StubSandbox:
            @staticmethod
            def build(_repo):
                d = tmp_path / f"seat_{len(built)}" / "repo"
                d.mkdir(parents=True)
                built.append(d)
                return d

        g = mod.__dict__
        monkeypatch.setitem(g, "panel_sandbox", StubSandbox)
        monkeypatch.setitem(g, "MODELS", list(self.SEATS))
        monkeypatch.setitem(g, "print", lambda *a, **k: None)
        monkeypatch.setitem(g, "sandboxes", None)
        monkeypatch.setitem(g, "sandbox", None)
        monkeypatch.setitem(g, "_PANEL_SANDBOX_CWD", None)
        mod._SEAT_SANDBOXES.clear()
        try:
            exec(compile(_population_statements(PANEL.read_text(encoding="utf-8")),
                         str(PANEL), "exec"), g)
            names = [n for n, _, _ in self.SEATS]
            assert len(built) == len(names), f"{len(built)} builds for {len(names)} seats"
            assert g["_PANEL_SANDBOX_CWD"], "main()'s fallback directory was not set"
            missing = [n for n in names if n not in mod._SEAT_SANDBOXES]
            assert not missing, (
                f"seats {missing} are absent from the per-seat map after main()'s "
                f"population step, so they fall back to {g['_PANEL_SANDBOX_CWD']}")

            set_panel_cwd(None)

            def worker(name):
                mod.confine_this_thread(name)
                return name, get_panel_cwd()

            with concurrent.futures.ThreadPoolExecutor(max_workers=len(names)) as pool:
                resolved = dict(pool.map(worker, names))
            assert len(set(resolved.values())) == len(names), (
                f"{len(names)} seats resolved to {len(set(resolved.values()))} "
                f"distinct directories: {resolved}")
            own = {n: str(Path(mod._SEAT_SANDBOXES[n]).resolve()) for n in names}
            assert {n: str(Path(v).resolve()) for n, v in resolved.items()} == own, (
                resolved, own)
        finally:
            mod._SEAT_SANDBOXES.clear()
            set_panel_cwd(None)
