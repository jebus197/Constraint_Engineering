"""Signing must actually happen — and be verifiable.

Signing lapsed silently when the arc moved to runner v2 (last sealed chain:
Exp 37, 9 April 2026), while the project documented tamper-evident provenance
as a core property. These tests pin the wiring so it cannot lapse unnoticed
again, and prove the seal detects tampering rather than merely existing.
"""
from __future__ import annotations

import ast
import json
import os
import sys
from pathlib import Path

_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _root not in sys.path:
    sys.path.insert(0, _root)

from bench.verification_chain import VerificationChain  # noqa: E402

_RUNNER = Path(_root) / "bench" / "reference_runner_v2.py"


class TestRunnerWiring:
    def test_runner_imports_and_seals_the_chain(self):
        src = _RUNNER.read_text(encoding="utf-8")
        assert "from bench.verification_chain import VerificationChain" in src
        assert "seal_epoch()" in src
        assert "experiment_chain.json" in src

    def test_seal_runs_before_the_report_is_written(self):
        """The chain must cover the report, so it seals first."""
        src = _RUNNER.read_text(encoding="utf-8")
        assert src.index("seal_epoch()") < src.index(
            'report_path = logs_dir / f"{cfg.experiment_name}_report.json"')

    def test_failure_is_loud_not_silent(self):
        """A run that cannot be signed must say so — silence is how this lapsed."""
        src = _RUNNER.read_text(encoding="utf-8")
        assert "verification chain NOT sealed" in src
        assert '"sealed": False' in src

    def test_runner_still_parses(self):
        ast.parse(_RUNNER.read_text(encoding="utf-8"))


class TestChainDetectsTampering:
    def _chain(self):
        c = VerificationChain()
        c.append_record(artifact_type="experiment_round",
                        payload={"round": 0, "findings": "3"},
                        recorded_by="test", metadata={"experiment": "t"})
        c.append_record(artifact_type="experiment_report",
                        payload={"converged_at": 5},
                        recorded_by="test", metadata={"experiment": "t"})
        return c

    def test_intact_chain_verifies(self, tmp_path):
        c = self._chain(); c.seal_epoch()
        p = tmp_path / "chain.json"; c.save_json(str(p))
        loaded = VerificationChain.load_json(str(p))
        ok, msg = loaded.verify_chain()
        assert ok, f"an untampered chain must verify: {msg}"

    def test_mutated_payload_fails_verification(self, tmp_path):
        c = self._chain(); c.seal_epoch()
        p = tmp_path / "chain.json"; c.save_json(str(p))
        d = json.loads(p.read_text())
        body = d["records"][0]["sealed_body"]
        # flip a recorded value — the exact class of silent edit this exists to catch
        if isinstance(body.get("payload"), dict):
            body["payload"]["findings"] = "999"
        p.write_text(json.dumps(d))
        loaded = VerificationChain.load_json(str(p))
        ok, msg = loaded.verify_chain()
        assert not ok, "a mutated record must fail verification"
