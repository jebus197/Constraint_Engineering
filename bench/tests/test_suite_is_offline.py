"""Pins the 2026-07-31 offline-suite fix. Each test names the defect it guards.

THE DEFECT
----------
`python3 -m pytest bench/tests/` made real outbound calls from 62 tests, none
of them marked `network`. The worst single case,
`test_exp29_integration.py::TestEndToEnd::test_three_round_flow`, attempted 60
serialised 15 s dispatches to the `claude` CLI and died on the 300 s pytest
timeout — but only on a machine where the CLI is installed. On a machine
without it, the same test passed in seconds, because every dispatch site fails
open when the CLI is absent. The suite's behaviour depended on a binary being
on PATH.

THE FIX, in three parts, each pinned below
------------------------------------------
1. `bench/live_dispatch_policy.live_dispatch_allowed()` — False under pytest
   unless `CDSFL_ALLOW_LIVE_DISPATCH=1` — consulted by
   `bench/immune_agents._get_claude_cli()`.
2. `bench/tests/conftest.py` pins `HF_HUB_OFFLINE=1`, so the sentence
   transformer loads from local cache with no hub call and no loss of
   embedding coverage.
3. `bench/tests/conftest.py` installs a socket/subprocess guard that denies
   any remaining outbound attempt and records it.

FALSIFICATION RECORD (2026-07-31, measured — not asserted)
----------------------------------------------------------
Baseline, all three fixes in place:   19 passed, 0 failed (11.0 s).

Each part was then reverted in turn and this file re-run. A pin that stayed
green against the defect it names would be decoration; none did.

  * revert 1 — `if not live_dispatch_allowed(): return None` deleted from
    `bench/immune_agents._get_claude_cli`:
        2 failed, 17 passed
        FAILED test_get_claude_cli_returns_none_under_pytest
        FAILED test_pipeline_makes_no_model_dispatch
    (the pipeline was observed launching `claude` again; the netguard, still
    installed, denied the spawn, so no quota was spent proving it)

  * revert 2 — the `HF_HUB_OFFLINE` / `TRANSFORMERS_OFFLINE` lines deleted
    from `bench/tests/conftest.py`:
        FAILED test_huggingface_hub_is_pinned_offline (immediate)
        FAILED test_embedding_backend_still_works_from_cache — did not merely
        fail, it HUNG in `huggingface_hub.utils._http.http_backoff` retry-sleep
        and had to be killed by the pytest timeout. Worth recording: the guard
        alone is not sufficient for the huggingface family. Denying the socket
        without pinning offline converts 35 fast tests into slow retry loops.
        The offline pin is load-bearing, not belt-and-braces.

  * revert 3 — `install_netguard()` call deleted from `pytest_configure`:
        7 failed, 12 passed
        FAILED test_netguard_is_installed_by_default
        FAILED test_outbound_tcp_is_denied
        FAILED test_outbound_dns_is_denied
        FAILED test_model_cli_spawn_is_denied
        FAILED test_attempts_are_recorded_even_when_swallowed
        FAILED test_child_pytest_session_is_offline
              — child probe printed PROBE_RESULT=REACHED_NETWORK, confirming
                the probe really does test the wire and not a stub
        FAILED test_strict_mode_fails_a_test_that_attempts_outbound

All three restored: 19 passed. Full-suite numbers are in the task report.
"""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

import conftest as netguard_conftest  # bench/tests/conftest.py
from bench import immune_agents
from bench.dm._types import Finding
from bench.live_dispatch_policy import (
    OPT_IN_ENV,
    live_dispatch_allowed,
    under_pytest,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

# RECOVERY.md, live_dispatch_policy.py and conftest.py all advertise
#     CDSFL_ALLOW_LIVE_DISPATCH=1 python3 -m pytest bench/tests/
# as the deliberate way to exercise the live path. Without this marker that
# command could never be green: twelve tests here assert that the guard DENIES
# outbound calls, which is false by construction once the guard has been stood
# down. A documented command that always fails teaches people to ignore red.
#
# The assertion "the guard denies outbound traffic" is not wrong when the guard
# is off — it is inapplicable. Skip is the honest verdict, and it keeps the
# tests loud in the default configuration where they mean something.
# Found 2026-07-31 by an adversarial pass over this file's own deliverable.
requires_guard = pytest.mark.skipif(
    os.environ.get(OPT_IN_ENV) == "1",
    reason=f"{OPT_IN_ENV}=1 stands the guard down; an assertion that the guard "
           f"blocks outbound traffic is inapplicable, not failing",
)


def _mk(fid: str, desc: str) -> Finding:
    return Finding(
        finding_id=fid,
        model_id="TestModel",
        round_idx=1,
        flaw_class=3,
        severity=0.7,
        abstraction_index=0.5,
        description=desc,
    )


# ---------------------------------------------------------------------------
# Part 1 — the source-level dispatch gate
# ---------------------------------------------------------------------------

class TestLiveDispatchPolicy:
    def test_under_pytest_is_detected(self):
        assert under_pytest() is True

    @requires_guard
    def test_live_dispatch_disallowed_by_default(self):
        assert os.environ.get(OPT_IN_ENV) != "1", (
            "this test is meaningless with the opt-in already set"
        )
        assert live_dispatch_allowed() is False

    def test_opt_in_restores_live_dispatch(self, monkeypatch):
        """The live path must be disabled, never unreachable."""
        monkeypatch.setenv(OPT_IN_ENV, "1")
        assert live_dispatch_allowed() is True

    @requires_guard
    def test_get_claude_cli_returns_none_under_pytest(self):
        """The load-bearing pin.

        Guards the exact regression: `_get_claude_cli()` returning a path
        under pytest is what let `_active_llm_classify` shell out to Haiku.
        Meaningless on a machine with no CLI, hence the skip — which is
        itself the point: this fix exists to make those two machines behave
        the same.
        """
        import shutil
        if not shutil.which("claude"):
            pytest.skip("no claude CLI on this machine — nothing to suppress")
        assert immune_agents._get_claude_cli() is None

    def test_get_claude_cli_finds_cli_when_opted_in(self, monkeypatch):
        import shutil
        if not shutil.which("claude"):
            pytest.skip("no claude CLI on this machine")
        monkeypatch.setenv(OPT_IN_ENV, "1")
        assert immune_agents._get_claude_cli() is not None

    def test_direct_patching_of_get_claude_cli_still_works(self, monkeypatch):
        """Existing deterministic coverage must not be collateral damage.

        `test_llm_classifier_log_honesty.py` exercises the classifier's
        SUCCESS branch by patching `_get_claude_cli` to "/bin/true" and
        faking `sp.run`. The gate lives inside that function, so patching it
        out must still bypass the gate entirely.
        """
        monkeypatch.setattr(
            immune_agents, "_get_claude_cli", lambda: "/bin/true",
        )
        assert immune_agents._get_claude_cli() == "/bin/true"


class TestPipelineIsOffline:
    @requires_guard
    def test_pipeline_makes_no_model_dispatch(self, monkeypatch):
        """End-to-end pin on the measured chain.

        `run_immune_pipeline` -> `_apply_llm_reclassification` ->
        `_active_llm_classify` -> `sp.run([claude, ...])`. Every subprocess
        launched by the pipeline is recorded; none may be a model CLI.
        Local python spawns (B-Cell sympy/z3 verifiers) are expected and are
        deliberately NOT asserted away — blocking those would shrink real
        offline coverage.
        """
        spawned: list[list[str]] = []
        real_run = subprocess.run

        def spy_run(cmd, *a, **kw):
            spawned.append([str(c) for c in cmd] if isinstance(cmd, (list, tuple))
                           else [str(cmd)])
            return real_run(cmd, *a, **kw)

        monkeypatch.setattr(immune_agents.sp, "run", spy_run)

        findings = [
            _mk("f1", "The retry counter is off by one when the queue drains"),
            _mk("f2", "Race condition in dispatcher shutdown"),
            _mk("f3", "asdf qwer zxcv"),  # deliberately unclassifiable residue
        ]
        immune_agents.run_immune_pipeline(
            new_findings=findings,
            prior_findings=[],
            source_paths=[],
            observation_only=True,
        )

        model_cli = [
            argv for argv in spawned
            if os.path.basename(argv[0]) in netguard_conftest._NETWORK_BINARIES
        ]
        assert model_cli == [], (
            f"pipeline dispatched to a model CLI: {model_cli}"
        )


class TestClassifierSuccessBranchStillCovered:
    """Replaces, deterministically, the one thing the fix genuinely took away.

    Before 2026-07-31, 17 tests reached `_active_llm_classify` for real. They
    never *asserted* on the result — but they did execute its success branch
    (parse two lines, map the category, clamp the confidence) and
    `_apply_llm_reclassification`'s reclassify branch, whenever Haiku happened
    to answer above threshold. With the CLI gated off, those branches would
    otherwise have no coverage at all: `test_llm_classifier_log_honesty.py`
    fakes the CLI but exercises `typed_llm_classifier`, a different function.

    So the branches are pinned here with a fake CLI instead — which is a strict
    improvement, because the old coverage was incidental and depended on the
    model's reply, and this asserts the parse and the threshold outright.
    """

    class _FakeCompleted:
        def __init__(self, stdout: str):
            self.stdout, self.stderr, self.returncode = stdout, "", 0

    def _classify(self, monkeypatch, stdout: str):
        monkeypatch.setattr(immune_agents, "_get_claude_cli", lambda: "/bin/true")
        monkeypatch.setattr(
            immune_agents.sp, "run",
            lambda *a, **kw: self._FakeCompleted(stdout),
        )
        return immune_agents._active_llm_classify(_mk("F001", "some description"))

    def test_success_branch_parses_category_and_confidence(self, monkeypatch):
        claim_type, conf = self._classify(monkeypatch, "MATHEMATICAL\n0.91\n")
        assert claim_type is immune_agents.ClaimType.MATHEMATICAL
        assert conf == pytest.approx(0.91)

    def test_confidence_is_clamped_to_unit_interval(self, monkeypatch):
        _, conf = self._classify(monkeypatch, "LOGICAL\n7.4\n")
        assert conf == 1.0
        _, conf = self._classify(monkeypatch, "LOGICAL\n-3\n")
        assert conf == 0.0

    def test_non_numeric_confidence_becomes_moderate(self, monkeypatch):
        claim_type, conf = self._classify(monkeypatch, "STATISTICAL\nquite sure\n")
        assert claim_type is immune_agents.ClaimType.STATISTICAL
        assert conf == 0.5

    def test_empty_reply_fails_open(self, monkeypatch):
        assert self._classify(monkeypatch, "\n") == (None, 0.0)

    def test_reclassification_applies_above_threshold(self, monkeypatch):
        monkeypatch.setattr(immune_agents, "_get_claude_cli", lambda: "/bin/true")
        monkeypatch.setattr(
            immune_agents.sp, "run",
            lambda *a, **kw: self._FakeCompleted("MATHEMATICAL\n0.90\n"),
        )
        triaged = [immune_agents.TriagedFinding(
            finding=_mk("F001", "the bound is not tight"),
            claim_type=immune_agents.ClaimType.UNCATEGORISED,
        )]
        n = immune_agents._apply_llm_reclassification(triaged, domain="")
        assert n == 1
        assert triaged[0].claim_type is immune_agents.ClaimType.MATHEMATICAL

    def test_reclassification_declines_below_threshold(self, monkeypatch):
        monkeypatch.setattr(immune_agents, "_get_claude_cli", lambda: "/bin/true")
        monkeypatch.setattr(
            immune_agents.sp, "run",
            lambda *a, **kw: self._FakeCompleted("MATHEMATICAL\n0.10\n"),
        )
        triaged = [immune_agents.TriagedFinding(
            finding=_mk("F001", "the bound is not tight"),
            claim_type=immune_agents.ClaimType.UNCATEGORISED,
        )]
        n = immune_agents._apply_llm_reclassification(triaged, domain="")
        assert n == 0
        assert triaged[0].claim_type is immune_agents.ClaimType.UNCATEGORISED


# ---------------------------------------------------------------------------
# Part 2 — huggingface pinned offline, WITHOUT losing embedding coverage
# ---------------------------------------------------------------------------

class TestHuggingFaceOffline:
    @requires_guard
    def test_huggingface_hub_is_pinned_offline(self):
        assert os.environ.get("HF_HUB_OFFLINE") == "1"
        assert os.environ.get("TRANSFORMERS_OFFLINE") == "1"

    def test_embedding_backend_still_works_from_cache(self):
        """Coverage-preservation pin.

        The 35 huggingface offenders were reaching the hub for a revision
        check on an already-cached model. Pinning offline must keep the
        embedding backend live rather than silently demoting the whole suite
        to lexical Jaccard — otherwise the "fix" would quietly change what
        every convergence test measures.
        """
        pytest.importorskip("sentence_transformers")
        from bench.dm import _similarity

        model = _similarity._get_embedding_model()
        if model is None:
            pytest.skip(
                "all-MiniLM-L6-v2 is not in the local huggingface cache on "
                "this machine; the documented lexical fallback applies"
            )
        a = _mk("a", "The retry counter is off by one")
        b = _mk("b", "Retry count is incremented one time too many")
        c = _mk("c", "Colourless green ideas sleep furiously")
        assert _similarity.finding_similarity(a, b) > _similarity.finding_similarity(a, c)


# ---------------------------------------------------------------------------
# Part 3 — the containment guard
# ---------------------------------------------------------------------------

class TestNetguard:
    @requires_guard
    def test_netguard_is_installed_by_default(self):
        assert netguard_conftest.netguard_active(), (
            "conftest did not install the outbound guard"
        )

    @pytest.mark.allow_outbound
    @requires_guard
    def test_outbound_tcp_is_denied(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        try:
            with pytest.raises(ConnectionError):
                s.connect(("93.184.216.34", 80))  # literal IP: no DNS first
        finally:
            s.close()

    @pytest.mark.allow_outbound
    @requires_guard
    def test_outbound_dns_is_denied(self):
        with pytest.raises(socket.gaierror):
            socket.getaddrinfo("api.semanticscholar.org", 443)

    @pytest.mark.allow_outbound
    @requires_guard
    def test_model_cli_spawn_is_denied(self):
        # `--version`, not `-p <prompt>`: the guard blocks on argv[0] alone, so
        # this exercises it identically — but if the guard is ever absent (as
        # during falsification) the spawn costs no subscription quota.
        with pytest.raises(FileNotFoundError):
            subprocess.run(["claude", "--version"], capture_output=True)

    def test_local_subprocess_is_permitted(self):
        """The guard must be a scalpel, not a hammer.

        B-Cell verification spawns local python for sympy/z3/statsmodels.
        Blocking all subprocesses would delete that coverage outright.
        """
        r = subprocess.run(
            [sys.executable, "-c", "print('local ok')"],
            capture_output=True, text=True,
        )
        assert r.returncode == 0
        assert "local ok" in r.stdout

    def test_loopback_is_permitted(self):
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.bind(("127.0.0.1", 0))
        srv.listen(1)
        port = srv.getsockname()[1]
        cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cli.settimeout(2)
        try:
            cli.connect(("127.0.0.1", port))  # must NOT raise
        finally:
            cli.close()
            srv.close()

    @pytest.mark.allow_outbound
    @requires_guard
    def test_attempts_are_recorded_even_when_swallowed(self):
        """Pins the reason teardown-failure exists.

        11 of the 62 measured offenders swallowed the guard's exception in a
        broad `except Exception` and would have looked clean to any
        instrumentation that only raised. Recording is what caught them, so
        recording is what must be pinned.
        """
        nodeid = os.environ["PYTEST_CURRENT_TEST"].split(" ")[0]
        before = len(netguard_conftest.netguard_attempts(nodeid))
        try:
            socket.getaddrinfo("export.arxiv.org", 443)
        except Exception:  # noqa: BLE001 — deliberately swallowing, as the code does
            pass
        after = netguard_conftest.netguard_attempts(nodeid)
        assert len(after) == before + 1
        assert after[-1]["target"] == "export.arxiv.org"


class TestChildSession:
    """Proves the guard applies to a REAL pytest run, not just in-process."""

    @requires_guard
    def test_child_pytest_session_is_offline(self, tmp_path):
        probe = Path(REPO_ROOT) / "bench" / "tests" / "_netguard_probe_test.py"
        probe.write_text(textwrap.dedent(
            '''
            import socket

            def test_probe_attempts_outbound():
                try:
                    socket.getaddrinfo("api.openalex.org", 443)
                    print("PROBE_RESULT=REACHED_NETWORK")
                except Exception as exc:
                    print("PROBE_RESULT=DENIED:%s" % type(exc).__name__)
            '''
        ))
        try:
            r = subprocess.run(
                [sys.executable, "-m", "pytest", str(probe), "-q", "-s",
                 "-p", "no:cacheprovider"],
                cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=180,
            )
        finally:
            probe.unlink(missing_ok=True)
        assert "PROBE_RESULT=DENIED" in r.stdout, (
            f"child pytest session reached the network.\n{r.stdout[-3000:]}"
        )

    @requires_guard
    def test_strict_mode_fails_a_test_that_attempts_outbound(self, tmp_path):
        """Pins the regression guard itself."""
        probe = Path(REPO_ROOT) / "bench" / "tests" / "_netguard_strict_probe_test.py"
        probe.write_text(textwrap.dedent(
            '''
            import socket

            def test_probe_swallows_the_denial():
                try:
                    socket.getaddrinfo("api.openalex.org", 443)
                except Exception:
                    pass          # exactly what immune_agents.py does
                assert True       # the test itself "passes"
            '''
        ))
        try:
            r = subprocess.run(
                [sys.executable, "-m", "pytest", str(probe), "-q",
                 "--netguard-strict", "-p", "no:cacheprovider"],
                cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=180,
            )
        finally:
            probe.unlink(missing_ok=True)
        assert r.returncode != 0, (
            "strict mode passed a test that attempted an outbound call\n"
            + r.stdout[-3000:]
        )
        assert "netguard(strict)" in r.stdout


class TestNetworkMarkedTestsAreSkipped:
    """A test that honestly declares `@pytest.mark.network` must be SKIPPED,
    not failed, while the guard is denying the wire — and must still run when
    the opt-in is set. Anything else punishes correct labelling."""

    def _probe(self, extra_env=None, extra_args=()):
        probe = Path(REPO_ROOT) / "bench" / "tests" / "_netguard_marker_probe_test.py"
        probe.write_text(textwrap.dedent(
            '''
            import pytest

            @pytest.mark.network
            def test_wants_the_wire():
                print("MARKER_PROBE=RAN")
            '''
        ))
        env = dict(os.environ)
        env.update(extra_env or {})
        try:
            return subprocess.run(
                [sys.executable, "-m", "pytest", str(probe), "-q", "-rs", "-s",
                 "-p", "no:cacheprovider", *extra_args],
                cwd=str(REPO_ROOT), capture_output=True, text=True,
                timeout=180, env=env,
            )
        finally:
            probe.unlink(missing_ok=True)

    @requires_guard
    def test_network_marked_test_is_skipped_by_default(self):
        r = self._probe()
        assert "1 skipped" in r.stdout, r.stdout[-2000:]
        assert "MARKER_PROBE=RAN" not in r.stdout

    def test_network_marked_test_runs_under_opt_in(self):
        r = self._probe(extra_env={OPT_IN_ENV: "1"})
        assert "MARKER_PROBE=RAN" in r.stdout, r.stdout[-2000:]
        assert "1 passed" in r.stdout


class TestKnownOutboundRegistry:
    """The strict-mode exemption list must stay small and justified."""

    def test_every_exemption_is_ouroboros_and_documented(self):
        for key, reason in netguard_conftest.KNOWN_OUTBOUND.items():
            assert "ouroboros" in key.lower() or "Ouroboros" in key, (
                f"exemption {key!r} is not an ouroboros test. The exemption "
                f"list exists solely because bench/ouroboros_cell.py was "
                f"under concurrent edit on 2026-07-31; anything else needs a "
                f"real fix, not an exemption."
            )
            assert len(reason) > 40, f"exemption {key!r} lacks a written reason"
