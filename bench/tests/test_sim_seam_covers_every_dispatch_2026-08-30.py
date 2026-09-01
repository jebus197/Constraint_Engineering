"""A simulated run must intercept EVERY dispatch, not one of nine.

THE DEFECT, MEASURED 2026-08-30
-------------------------------
The simulation shim patched ``_dispatch_single_model``. Nine functions in
``reference_runner_v3`` dispatch to a model, and the other eight went to real,
unconfigured models for the whole v3.1 run. The most costly was ``resolve_fn``,
the routing ladder's FALSIFIER WRITER: its call raised, a bare ``except``
returned "", and the run logged "routing: 0 resolved by strong writer" in every
round.

Downstream, measured against the real exp45 on the same target:
  falsifier_code   0/19 vs 23/39   (scipy Fisher p = 6.0e-06)
  verified         0/19 vs 24/39   (p = 2.2e-06)
  fix_efficacy     0/19            (depends on falsifier_code)

One missed seam silenced the falsification core for an entire run. The repair is
to patch the PRIMITIVE ``dispatch_to_model``, so coverage holds by construction
rather than by keeping a list of call sites in sync.

WHAT THIS TEST PINS
-------------------
1. ``install()`` patches the primitive, and ``restore()`` puts it back.
2. No function in the runner reaches the network by any route OTHER than
   ``dispatch_to_model`` -- so a tenth dispatch path cannot be added that
   silently bypasses the seam.
"""
import ast, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import reference_runner_v3 as R

RUNNER = pathlib.Path(R.__file__)
#: primitives that actually leave the process to reach a model
_NETWORK_PRIMITIVES = {"requests", "httpx", "urllib", "openai", "anthropic"}
#: functions allowed to hold that primitive
_ALLOWED = {"dispatch_to_model"}


class TestTheSeamIsThePrimitive:
    def test_install_patches_dispatch_to_model_and_restore_undoes_it(self):
        from bench.tools import sim_dispatch_shim as S
        before = R.dispatch_to_model
        original = S.install(timeout=5)
        try:
            assert R.dispatch_to_model is not before
            assert R.dispatch_to_model.__module__ == S.__name__
        finally:
            S.restore(original)
        assert R.dispatch_to_model is before

    def test_the_shim_signature_matches_the_primitive(self):
        """A mismatched shim would raise inside a bare `except` and read as a
        model that simply returned nothing -- which is how this hid."""
        import inspect
        from bench.tools import sim_dispatch_shim as S
        real = inspect.signature(R.dispatch_to_model)
        shim = inspect.signature(S.make_shim())
        assert list(real.parameters) == list(shim.parameters), (
            f"real={list(real.parameters)} shim={list(shim.parameters)}")


class TestNothingBypassesTheSeam:
    def test_no_function_reaches_a_model_except_through_dispatch_to_model(self):
        tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
        offenders = []
        for fn in [n for n in ast.walk(tree)
                   if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
            if fn.name in _ALLOWED:
                continue
            for node in ast.walk(fn):
                if not isinstance(node, ast.Call):
                    continue
                root = node.func
                while isinstance(root, ast.Attribute):
                    root = root.value
                if isinstance(root, ast.Name) and root.id in _NETWORK_PRIMITIVES:
                    offenders.append(f"{fn.name}() line {node.lineno}: {root.id}")
        assert offenders == [], (
            "these reach a model without going through dispatch_to_model, so a "
            "simulated run would send them to a REAL model:\n  "
            + "\n  ".join(offenders))

    def test_the_known_dispatchers_all_use_the_primitive(self):
        """Records the nine, so a tenth appearing is a visible diff."""
        tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
        users = set()
        for fn in [n for n in ast.walk(tree)
                   if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
            for c in ast.walk(fn):
                if (isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
                        and c.func.id == "dispatch_to_model"):
                    users.add(fn.name)
        expected = {"_apply_routing", "_post_convergence_sweep", "_inround_reask",
                    "_dispatch_single_model", "_verification_step",
                    "run_preflight", "run_experiment", "resolve_fn",
                    "_arb_dispatch"}
        assert expected <= users, f"a known dispatcher stopped using the primitive: {expected - users}"


class TestTheNinthPath:
    """`decomposed_dispatch` bypasses the primitive entirely.

    Found by Fable in panel review, 2026-08-30, and confirmed:
    `_multiturn_fallback` calls `decomposed_dispatch(api, model_id, ...)`, which
    reaches a model with its own `subprocess.run` and never touches
    `dispatch_to_model`. It is dormant at exp45 scale -- the trigger is
    `DECOMPOSE_HARD_FLOOR_CHARS = 80_000` and 0 of 29 real exp45 dispatches
    decomposed -- but it is ARMED for Bench Run 2's larger targets.

    In simulation it fails on `api="sim"` and degrades to monolithic, so it costs
    no money; what it costs is FIDELITY, silently. This test does not pretend the
    path is covered. It records that it is NOT, so the gap is a visible fact
    rather than an assumption that the primitive catches everything.
    """

    def test_decomposed_dispatch_is_a_known_uncovered_path(self):
        src = RUNNER.read_text(encoding="utf-8")
        assert "decomposed_dispatch" in src
        tree = ast.parse(src)
        users = {fn.name for fn in ast.walk(tree)
                 if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef))
                 for c in ast.walk(fn)
                 if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
                 and c.func.id == "decomposed_dispatch"}
        assert users == {"_multiturn_fallback"}, (
            f"decomposed_dispatch is now called from {users}. Every caller "
            f"bypasses the simulation seam, so a simulated run silently loses "
            f"fidelity there. Extend the shim or narrow the callers."
        )

    def test_the_trigger_threshold_is_recorded(self):
        """If the floor drops, the dormant path becomes live and this must be seen."""
        assert R.DECOMPOSE_HARD_FLOOR_CHARS == 80_000
