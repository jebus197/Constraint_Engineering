"""The seat confinement must be applied on the thread that dispatches the seat.

THE DEFECT, measured 2026-09-08 and demonstrated by execution rather than argued.

`set_panel_cwd` stores into a `threading.local`. `run_experiment` called it ONCE, on
the MAIN thread, at `reference_runner_v3.py:11395`. Every seat is dispatched from a
`ThreadPoolExecutor` (`:8244` and `:8337`), and a fresh worker thread has no value at
all, so the lookup returned None and each seat subprocess launched with `cwd=None`,
inheriting the repository. Main thread sees the sandbox; 3 workers see [None, None,
None].

So `panel_cwd` was inert for every threaded panel dispatch, including the withheld-exam
runs it exists to confine. Not dormant: a seat reviewing `bench/dm/_memory.py` wrote its
proposed fix into the live working tree twice inside 1 minute -- 22,682 bytes at
03:39:50 and 23,831 at 03:40:30 against a committed 20,605 -- while 5 other seats were
reviewing that same file. 3 of the 6 reported the target changing under them, unprompted.

THE FIX IS THE ONE THIS PROJECT ALREADY CHOSE, not a new one. On 2026-09-07 the same
defect was found in the confer panel and repaired by setting the cwd PER WORKER, inside
`dispatch()`, on the worker's own thread; `test_panel_sandbox_2026-09-07.py` pins it and
explicitly warns "nobody sets the panel cwd from main again and believes the log line".
`reference_runner_v3` was simply never given the same treatment.

A FIRST ATTEMPT HERE WAS WRONG AND IS RECORDED SO IT IS NOT RETRIED: a module-level
fallback inside `_get_panel_cwd_raw`, so a main-thread set would reach workers. That
made the 2026-09-07 guard fail, which is exactly what the guard exists to do -- the
thread-local is deliberate, because concurrent reviewers must each own their value so
one dispatch's cleanup cannot unsandbox another. The value is now carried to the worker
by `_PANEL_CWD_FOR_WORKERS` instead of weakening the store.
"""
import pathlib
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import reference_runner_v3 as R  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _reset():
    yield
    R._PANEL_CWD_FOR_WORKERS["path"] = None
    R.set_panel_cwd(None)


def test_the_seat_dispatcher_confines_itself_on_its_own_thread(tmp_path, monkeypatch):
    """THE REGRESSION, executed.

    Calls the real `_dispatch_single_model` from a real pool worker with an
    unroutable api, so the confinement prologue runs and the dispatch then fails
    without contacting anything. Asserts the cwd was set ON THE WORKER, with the
    configured value. Before the fix nothing was set at all.
    """
    calls = []
    real = R.set_panel_cwd

    def spy(path, *a, **k):
        calls.append((threading.current_thread().name, path))
        return real(path, *a, **k)

    monkeypatch.setattr(R, "set_panel_cwd", spy)
    R._PANEL_CWD_FOR_WORKERS["path"] = str(tmp_path)

    mc = R.ModelConfig(label="PROBE", model_id="none", api="__no_such_route__",
                       role="player", system_prompt_path="")

    def run(_):
        try:
            return R._dispatch_single_model(mc, None, "p", "", "", 0, "pat", "dom", tmp_path)
        except Exception as exc:            # unroutable api: expected, and free
            return type(exc).__name__

    with ThreadPoolExecutor(max_workers=1) as pool:
        list(pool.map(run, range(1)))

    on_worker = [(t, p) for t, p in calls if t != threading.main_thread().name]
    assert on_worker, (
        "the seat dispatcher never set a panel cwd on its own thread, so every seat "
        f"would launch in the repository. calls seen: {calls}"
    )
    assert any(p == str(tmp_path) for _, p in on_worker), (
        f"the worker set a cwd, but not the configured one: {on_worker}"
    )


def test_an_unset_panel_cwd_leaves_dispatch_untouched(tmp_path, monkeypatch):
    """A code run must behave exactly as before. No mirror value, no call."""
    calls = []
    monkeypatch.setattr(R, "set_panel_cwd", lambda p, *a, **k: calls.append(p))
    R._PANEL_CWD_FOR_WORKERS["path"] = None
    mc = R.ModelConfig(label="PROBE", model_id="none", api="__no_such_route__",
                       role="player", system_prompt_path="")
    with ThreadPoolExecutor(max_workers=1) as pool:
        list(pool.map(lambda _: _safe(R, mc, tmp_path), range(1)))
    assert calls == [], f"an unconfigured run touched the panel cwd: {calls}"


def _safe(mod, mc, tmp):
    try:
        return mod._dispatch_single_model(mc, None, "p", "", "", 0, "pat", "dom", tmp)
    except Exception as exc:
        return type(exc).__name__


def test_the_main_thread_set_still_does_not_propagate(tmp_path):
    """The 2026-09-07 guard must survive this fix.

    The thread-local is deliberate. A fix that made a main-thread set reach workers
    would silently let one dispatch's cleanup unsandbox another, and it broke that
    guard when tried. Kept here so the withdrawal is not quietly re-done.
    """
    R.set_panel_cwd(str(tmp_path))
    with ThreadPoolExecutor(max_workers=2) as pool:
        seen = list(pool.map(lambda _: R.get_panel_cwd(), range(2)))
    assert seen == [None, None], (
        f"thread-locals now propagate to pool workers ({seen}); the per-worker set "
        "may be redundant, but verify against test_panel_sandbox_2026-09-07.py first"
    )


def test_run_experiment_populates_the_mirror(tmp_path):
    """Both halves of the panel-cwd wiring, proven BY CALLING IT.

    REWRITTEN 2026-09-10, task A2. This asserted on SOURCE TEXT: it found
    `set_panel_cwd(` in the runner and searched the next 400 characters for the
    worker-mirror assignment. The 2 statements sat 8 lines apart with a comment
    between them; the comment grew, the window stopped reaching the assignment,
    and the test failed in the maintainer's tree AND in a fresh clone while the
    wiring was entirely correct. `execute-do-not-grep`: a source-text test proves
    only that the source describes itself consistently, and here it did not even
    manage that.

    `run_experiment` now calls `apply_panel_cwd`, which sets both halves, so the
    mechanism can be EXECUTED with no dispatch and no cost. The ratchet is
    stronger than before, not weaker: it now fails if either half stops being
    set, whatever the source happens to look like.
    """
    R.apply_panel_cwd(None)                        # a known starting state
    assert R.get_panel_cwd() is None
    assert R._PANEL_CWD_FOR_WORKERS["path"] is None

    R.apply_panel_cwd(str(tmp_path))
    assert R.get_panel_cwd() == str(tmp_path), (
        "the main-thread thread-local was not set")
    assert R._PANEL_CWD_FOR_WORKERS["path"] == str(tmp_path), (
        "the main thread is confined and the pool workers are not, which is the "
        "inert configuration measured on 2026-09-08")

    # AND THE WORKERS ACTUALLY READ IT. The mirror existing is not the claim;
    # the claim is that a pool worker ends up confined.
    with ThreadPoolExecutor(max_workers=2) as pool:
        seen = list(pool.map(lambda _: R._PANEL_CWD_FOR_WORKERS.get("path"), range(2)))
    assert seen == [str(tmp_path), str(tmp_path)], seen

    R.apply_panel_cwd(None)                        # leave no state behind


def test_run_experiment_still_calls_the_wiring():
    """The execution test above proves the MECHANISM; this proves it is REACHED.

    An addition nothing reaches is not additive. `apply_panel_cwd` could be
    perfect and never called, and every assertion above would still pass.
    """
    import ast

    src = (REPO / "bench" / "reference_runner_v3.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "run_experiment":
            called = {n.func.id for n in ast.walk(node)
                      if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
            assert "apply_panel_cwd" in called, (
                "run_experiment no longer calls apply_panel_cwd, so no run "
                "confines its panel at all")
            return
    raise AssertionError("run_experiment is gone from the runner")
