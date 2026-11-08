"""B20's missing seam: an invocation that is BOTH simulated and resumable.

THE DEFECT, measured 2026-11-04 and built 2026-11-08. The actuator resumes by
re-invoking its launch command with `--resume`, so the launch command must accept
it. `bench/reference_runner_v3.py` declares it on `run` and `bench/launch_exp39.py`
forwards it, but `bench/tools/run_simulated_experiment.py` declared it 0 times and
could not: the protection that stops a simulated run billing anything was a
`getaddrinfo` patch installed inside that file's `main()`, and an in-process
network block cannot survive the subprocess boundary a resume requires. So no
invocation was both simulated and resumable -- the resumable path dispatched for
real and cost money, which he has refused, and the free path could not be
resumed. 0 of 352 archived runs declare the arm, and that was a missing seam
rather than his deferral.

WHAT THESE TESTS HOLD, and they are the 2 the entry names: the wrapper REFUSES a
paid host, and it PROPAGATES exit 42 -- the HIL review pause the actuator
classifies on. Swallowing or remapping 42 would make the actuator blind to the
very state it exists to act on.

THE RUNNER IS STUBBED AND THAT IS DELIBERATE. Importing the real
`reference_runner_v3` costs the founder's machine, which has 8 GiB and is a fixed
resource. What the wrapper OWNS is the plumbing -- the tripwire, the argv, the
exit code -- and a stub exercises all 3. The integration claim it rests on is
asserted SEPARATELY and statically: the real runner's `main` takes no arguments
and its `run` subcommand declares both flags, read from the source by AST rather
than by importing it.
"""
from __future__ import annotations

import ast
import importlib.util
import pathlib
import socket
import sys
import types

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
WRAPPER = REPO / "bench/tools/run_simulated_resumable_2026-11-08.py"
RSE = REPO / "bench/tools/run_simulated_experiment.py"
RUNNER = REPO / "bench/reference_runner_v3.py"


@pytest.fixture(autouse=True)
def _no_resolver_leak():
    """Snapshot and restore the resolver around EVERY test in this module.

    ★ ADDED AFTER THE MUTATION HARNESS FOUND A TEST-ORDER DEPENDENCY. Reversing
    the wrapper's restoration left the guard GREEN, because that reversal
    poisons every call in the class, so by the time the restoration test ran the
    resolver was ALREADY the patch and a comparison against the prior value
    could not tell. Isolation plus an absolute assertion, not one or the other.
    """
    before = socket.getaddrinfo
    try:
        yield
    finally:
        socket.getaddrinfo = before


@pytest.fixture
def wrapper(monkeypatch):
    """The wrapper, with the real runner replaced by a stub we can steer."""
    for p in (REPO / "bench", REPO / "bench/tools"):
        monkeypatch.syspath_prepend(str(p))
    spec = importlib.util.spec_from_file_location("_rsr_under_test", WRAPPER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_rsr_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


def _stub_runner(monkeypatch, outcome):
    """Install a fake `reference_runner_v3` whose `main()` yields `outcome`."""
    stub = types.ModuleType("reference_runner_v3")
    seen: dict = {}

    def main():
        seen["argv"] = list(sys.argv)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome

    stub.main = main
    monkeypatch.setitem(sys.modules, "reference_runner_v3", stub)
    return seen


class TestTheTripwireRefusesAPaidHost:
    def test_the_paid_host_list_is_not_empty(self, wrapper):
        """ANTI-VACUITY. An empty list would make every refusal test pass by
        refusing nothing."""
        import live_dispatch_policy as pol
        assert pol.PAID_HOSTS, "the canonical paid-host list is empty"

    def test_a_paid_host_is_refused_once_installed(self, wrapper):
        import live_dispatch_policy as pol
        import run_simulated_experiment as rse
        original = socket.getaddrinfo
        try:
            rse.install_paid_tripwire()
            host = sorted(pol.PAID_HOSTS)[0]
            with pytest.raises(RuntimeError, match="PAID DISPATCH"):
                socket.getaddrinfo(host, 443)
        finally:
            socket.getaddrinfo = original

    def test_a_subdomain_of_a_paid_host_is_refused(self, wrapper):
        import live_dispatch_policy as pol
        import run_simulated_experiment as rse
        original = socket.getaddrinfo
        try:
            rse.install_paid_tripwire()
            host = "sub." + sorted(pol.PAID_HOSTS)[0]
            with pytest.raises(RuntimeError, match="PAID DISPATCH"):
                socket.getaddrinfo(host, 443)
        finally:
            socket.getaddrinfo = original

    def test_an_unpaid_host_is_not_refused(self, wrapper):
        """NEGATIVE CONTROL. Without this the tripwire could refuse everything
        and every test above would still pass."""
        import run_simulated_experiment as rse
        original = socket.getaddrinfo
        try:
            rse.install_paid_tripwire()
            calls: list = []
            # The patch delegates to the ORIGINAL for a host it allows, so
            # intercepting the original proves delegation without a network call.
            socket.getaddrinfo._cdsfl_original = lambda *a, **k: calls.append(a)
            socket.getaddrinfo("localhost", 80)
        except RuntimeError as exc:                            # pragma: no cover
            pytest.fail(f"an unpaid host was refused: {exc}")
        finally:
            socket.getaddrinfo = original

    def test_the_installer_is_idempotent_and_returns_the_original(self, wrapper):
        """A resumable wrapper installs this and then calls the runner, which may
        install it again; chaining 2 patches would make the error name the wrong
        layer and would break restoration."""
        import run_simulated_experiment as rse
        original = socket.getaddrinfo
        try:
            first = rse.install_paid_tripwire()
            second = rse.install_paid_tripwire()
            assert first is original
            assert second is original
        finally:
            socket.getaddrinfo = original

    def test_there_is_ONE_installer(self):
        """The patch must not exist twice: a billing guard that exists twice can
        be repaired once. Asserted on the parsed module, not on its text."""
        tree = ast.parse(RSE.read_text(encoding="utf-8"))
        defs = [n.name for n in ast.walk(tree)
                if isinstance(n, ast.FunctionDef) and n.name == "_no_paid"]
        assert len(defs) == 1, f"`_no_paid` is defined {len(defs)} times"
        top = [n.name for n in tree.body
               if isinstance(n, ast.FunctionDef) and n.name == "install_paid_tripwire"]
        assert top == ["install_paid_tripwire"], (
            "the installer is not a module-level function, so a second caller "
            "cannot reach it")


class TestExitFortyTwoIsPropagated:
    def test_a_returned_42_is_propagated(self, wrapper, monkeypatch):
        _stub_runner(monkeypatch, 42)
        assert wrapper.main(["--config", "cfg.json"]) == 42

    def test_a_raised_42_is_propagated(self, wrapper, monkeypatch):
        """`main()` may return OR raise; 42 must survive both paths."""
        _stub_runner(monkeypatch, SystemExit(42))
        assert wrapper.main(["--config", "cfg.json"]) == 42

    def test_a_zero_stays_zero_and_none_becomes_zero(self, wrapper, monkeypatch):
        _stub_runner(monkeypatch, 0)
        assert wrapper.main(["--config", "cfg.json"]) == 0
        _stub_runner(monkeypatch, None)
        assert wrapper.main(["--config", "cfg.json"]) == 0

    def test_a_failure_is_not_turned_into_a_pause(self, wrapper, monkeypatch):
        """NEGATIVE CONTROL: only 42 means paused. A wrapper that mapped every
        non-zero to 42 would have the actuator resume a genuinely failed run."""
        _stub_runner(monkeypatch, 1)
        assert wrapper.main(["--config", "cfg.json"]) == 1

    def test_the_resolver_is_restored_afterwards(self, wrapper, monkeypatch):
        """ASSERTED ABSOLUTELY, not against the prior value.

        ★ THE RELATIVE FORM WAS VACUOUS and the mutation harness proved it:
        reversing the wrapper's restoration left this GREEN, because the
        reversal poisons every earlier call in the class, so `before` was
        already the patch. Asking whether a tripwire SURVIVES cannot be masked
        that way, whatever ran first.
        """
        _stub_runner(monkeypatch, 0)
        wrapper.main(["--config", "cfg.json"])
        assert not getattr(socket.getaddrinfo, "_cdsfl_paid_tripwire", False), (
            "the wrapper left the patched resolver installed")

    def test_the_tripwire_is_actually_installed_during_the_call(self, wrapper,
                                                                monkeypatch):
        """ANTI-VACUITY FOR THE TEST ABOVE. If the tripwire were never installed
        at all, "no tripwire afterwards" would pass for the wrong reason."""
        seen: dict = {}
        stub = types.ModuleType("reference_runner_v3")

        def main():
            seen["patched"] = getattr(socket.getaddrinfo,
                                      "_cdsfl_paid_tripwire", False)
            return 0

        stub.main = main
        monkeypatch.setitem(sys.modules, "reference_runner_v3", stub)
        wrapper.main(["--config", "cfg.json"])
        assert seen.get("patched") is True, (
            "the tripwire was NOT installed while the runner ran, so a "
            "simulated run could dispatch for real")


class TestTheArgvItHandsTheRunner:
    def test_the_pause_flag_is_on_by_default(self, wrapper):
        """`--hil-review` is what CREATES the pause the actuator waits for, so a
        wrapper omitting it would be resumable with nothing to resume from."""
        assert "--hil-review" in wrapper.build_argv("cfg.json")

    def test_resume_is_appended_only_when_asked(self, wrapper):
        assert "--resume" not in wrapper.build_argv("cfg.json")
        assert "--resume" in wrapper.build_argv("cfg.json", resume=True)

    def test_the_runner_really_receives_it(self, wrapper, monkeypatch):
        seen = _stub_runner(monkeypatch, 42)
        wrapper.main(["--config", "cfg.json", "--resume"])
        assert seen["argv"][1:] == ["run", "--config", "cfg.json",
                                    "--hil-review", "--resume"]

    def test_sys_argv_is_restored(self, wrapper, monkeypatch):
        _stub_runner(monkeypatch, 0)
        before = sys.argv[:]
        wrapper.main(["--config", "cfg.json"])
        assert sys.argv == before


class TestTheIntegrationClaimItRestsOn:
    """Asserted STATICALLY, because importing the real runner costs the
    founder's machine and what is claimed is a signature, not a behaviour."""

    def test_the_runners_main_takes_no_arguments(self):
        tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
        mains = [n for n in tree.body
                 if isinstance(n, ast.FunctionDef) and n.name == "main"]
        assert len(mains) == 1, f"{len(mains)} module-level `main` in the runner"
        args = mains[0].args
        assert not args.args and not args.posonlyargs, (
            "the runner's `main` now takes arguments, so letting argparse read "
            "`sys.argv` is no longer how it is driven")

    def test_the_run_subcommand_declares_both_flags(self):
        src = RUNNER.read_text(encoding="utf-8")
        assert '"--resume"' in src, "the runner no longer declares --resume"
        assert '"--hil-review"' in src, "the runner no longer declares --hil-review"

    def test_the_simulated_runner_still_lacks_resume(self):
        """Recorded, not required: this is the asymmetry the wrapper exists for.
        If `run_simulated_experiment` ever grows `--resume` itself, the wrapper
        may be redundant and that should be a deliberate decision, not a drift."""
        assert '"--resume"' not in RSE.read_text(encoding="utf-8")
