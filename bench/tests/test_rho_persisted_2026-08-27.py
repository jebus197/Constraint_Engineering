"""rho_history reaches the report, and the record's "permanently unavailable" claim is refuted.

FOUNDER RULING 2026-08-27, decision 8: "Persist it."

WHAT THE RECORD SAID. resources/RECOVERY.md:159 read: "One third of 1.7 is
permanently unavailable: no archived report carries a rho series in any form."

WHAT IS TRUE. Measured across all 31 archived reports: 22 carry per-round `rho`
AND `rho_avg` for EVERY round, exp42 through exp55, complete series. What was
absent is only the TOP-LEVEL `rho_history` array -- 0 of 31 -- the same hoisting
that gamma_history, gamma_all_history and gamma_critical_history all get.

So the rho third of Runway 1.7 was never lost. It is retroactively available on
22 runs. exp44 recovers as 13 rounds, mean 0.7536, sd 0.2233, Spearman
rs = -0.477 (p = 0.099, n = 13) against round index.

The runner already tracked rho_history -- declared at :9340, appended at :10030,
checkpoint-restored at :9433 -- and simply never wrote it out.
"""
import json
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
RUNNER = REPO / "bench" / "reference_runner_v2.py"
LOGS = REPO / "bench" / "logs"


class TestTheRunnerWritesIt:
    def test_rho_history_reaches_the_report(self):
        """Pins the one-line fix. If it is removed, future runs silently lose
        the series again -- which is how it went unnoticed for the whole arc."""
        src = RUNNER.read_text(encoding="utf-8")
        assert 'result["rho_history"]' in src, (
            "rho_history no longer reaches the report; the founder ruled "
            "2026-08-27 that it must persist"
        )

    def test_it_sits_with_the_other_histories(self):
        """Hoisted alongside gamma, not bolted somewhere a reader will not
        look."""
        src = RUNNER.read_text(encoding="utf-8")
        i_rho = src.index('result["rho_history"]')
        i_gam = src.index('result["gamma_history"]')
        i_all = src.index('result["gamma_all_history"]')
        assert i_gam < i_rho < i_all + 200, (
            "rho_history has drifted away from the gamma histories it mirrors"
        )

    def test_the_runner_still_tracks_the_series_it_writes(self):
        """Writing an undefined name would be a NameError at run end -- after
        the expensive part. Cheap to pin here."""
        src = RUNNER.read_text(encoding="utf-8")
        assert re.search(r"^\s*rho_history: List\[float\] = \[\]", src, re.M), \
            "rho_history is no longer declared"
        assert "rho_history.append(" in src, "rho_history is no longer appended to"


class TestTheArchiveRefutesThePermanentlyLostClaim:
    # Only exp* run directories, matching the population the 2026-08-27
    # measurement covered. Widening it past that pulls in older report
    # generations whose `rounds` is an INTEGER COUNT rather than a list of
    # round records -- a schema difference between runner generations, found
    # by this test crashing with "'int' object is not iterable" on the first
    # run. The guard below tolerates it rather than assuming one schema.
    EXP_DIR = re.compile(r"^exp\d+[_-]")

    def _reports(self):
        out = []
        for d in sorted(LOGS.iterdir()) if LOGS.is_dir() else []:
            if not (d.is_dir() and self.EXP_DIR.match(d.name)):
                continue
            reps = sorted(d.glob("*_report.json"))
            if reps:
                try:
                    out.append(json.loads(reps[0].read_text(encoding="utf-8")))
                except (OSError, ValueError):
                    pass
        return out

    @staticmethod
    def _rounds(r):
        """Round records, or [] when this generation stored a bare count."""
        v = r.get("rounds", [])
        return v if isinstance(v, list) else []

    def test_the_rho_series_IS_recoverable_from_the_archive(self):
        reps = self._reports()
        if not reps:
            pytest.skip("no archived reports on this machine")
        with_rho = [r for r in reps
                    if any(isinstance(x, dict) and x.get("rho") is not None
                           for x in self._rounds(r))]
        assert len(with_rho) >= 20, (
            f"only {len(with_rho)} of {len(reps)} archived reports carry per-round "
            "rho. The claim that the series was permanently unavailable would "
            "then be closer to true than measured, and RECOVERY.md's correction "
            "needs revisiting."
        )

    def test_a_recovered_series_is_complete_not_sparse(self):
        """A series present in one round of thirteen is not a series."""
        reps = self._reports()
        if not reps:
            pytest.skip("no archived reports")
        worst = None
        for r in reps:
            rounds = [x for x in self._rounds(r) if isinstance(x, dict)]
            if not rounds:
                continue
            have = sum(1 for x in rounds if x.get("rho") is not None)
            if have and (worst is None or have / len(rounds) < worst):
                worst = have / len(rounds)
        assert worst is None or worst >= 0.99, (
            f"the least complete recovered rho series covers only {worst:.0%} of "
            "its rounds; 'recoverable' would be overstating it"
        )

    def test_the_record_no_longer_asserts_permanent_loss(self):
        text = (REPO / "resources" / "RECOVERY.md").read_text(encoding="utf-8")
        assert "no archived report carries a rho series in any form. Decide" not in text, (
            "RECOVERY.md still carries the refuted claim"
        )
        assert "RETROACTIVELY available on 22 runs" in text
