"""The report must name which gamma series actually decided.

THE MISREADING THIS EXISTS TO STOP, measured on exp44. Its final four rounds
report:

    gamma            0.208  0.221  0.237  0.253      <- what a reader sees
    gamma_critical   0.382  0.409  0.432  0.453      <- what the GATE reads

The threshold is 0.30. A reader taking the unqualified "gamma" as the headline
concludes the gamma condition FAILED, when it held comfortably. That misreading
is the entire source of the impression that gamma "does not work", and it is
also what a demotion-era comment in the runner encouraged until 2026-08-27.

WHY A POINTER AND NOT A RENAME. 22 archived reports carry `gamma` and
`gamma_history` under the all-severity meaning. Redefining either would silently
change what every one of those reports says. The project already met this exact
problem with the location-keyed series and solved it by deprecating the name in
place. So both series stay, unchanged, and a new field names which one is
authoritative.

FOUNDER CONTEXT 2026-08-28: they proposed averaging or summing the two series
instead. Measured across 94 paired observations: the mean is strictly more
conservative (8 disagreements, every one blocking a convergence the critical
series would allow, because footnote novelty drags it down) and the sum strictly
more permissive (6 disagreements, and it would have converged exp44 five rounds
early). Neither is safe, because gamma_critical is not a second opinion on
gamma_all -- it is gamma_all with the minor findings filtered out. Combining
them re-adds the noise the filter removed.
"""
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
RUNNER = REPO / "bench" / "reference_runner_v3.py"


class TestTheReportNamesItsOwnAuthority:
    def test_the_round_record_names_the_gate_series(self):
        src = RUNNER.read_text(encoding="utf-8")
        assert '"gamma_gate_series": "gamma_critical"' in src, (
            "round records no longer say which gamma decided; a reader defaults "
            "to the unqualified 'gamma', which is the all-severity series"
        )

    def test_the_top_level_names_the_gate_series(self):
        src = RUNNER.read_text(encoding="utf-8")
        assert 'result["gamma_gate_series"] = "gamma_critical_history"' in src

    def test_the_legacy_series_is_NOT_renamed_or_repurposed(self):
        """The whole point of a pointer is that it breaks nothing."""
        src = RUNNER.read_text(encoding="utf-8")
        assert 'result["gamma_history"] = [round(g, 4) for g in gamma_history]' in src, (
            "gamma_history was renamed or repurposed; 22 archived reports carry "
            "it under the all-severity meaning and would silently change"
        )
        assert '"gamma": round(gamma, 4),' in src, "the legacy per-round field was removed"

    def test_both_series_are_still_reported(self):
        src = RUNNER.read_text(encoding="utf-8")
        for f in ('"gamma_all": round(gamma_all, 4)',
                  '"gamma_critical": round(gamma_critical, 4)'):
            assert f in src, f"{f} is no longer reported"


class TestTheGapItDocumentsIsReal:
    """If the two series ever coincide, this guard is pointless and should be
    deleted rather than left as decoration."""

    def test_the_archive_shows_a_gap_large_enough_to_mislead(self):
        import json
        gaps = []
        for d in sorted((REPO / "bench" / "logs").iterdir()):
            if not (d.is_dir() and re.match(r"exp(4[1-9]|5\d)", d.name)):
                continue
            for f in d.glob("*_report.json"):
                try:
                    r = json.loads(f.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    continue
                ga, gc = r.get("gamma_history"), r.get("gamma_critical_history")
                if ga and gc and len(ga) == len(gc):
                    gaps += [c - a for a, c in zip(ga, gc)]
        if not gaps:
            pytest.skip("no archived run carries both series on this machine")
        assert max(gaps) > 0.10, (
            f"largest gap between the two series is only {max(gaps):.3f}; if they "
            "have converged this pointer is no longer needed"
        )

    def test_a_reader_of_the_legacy_field_would_reach_the_wrong_verdict(self):
        """The concrete exp44 case, asserted rather than described."""
        import json
        runs = sorted((REPO / "bench" / "logs").glob("exp44_*/*_report.json"))
        if not runs:
            pytest.skip("exp44 not archived on this machine")
        r = json.loads(runs[0].read_text(encoding="utf-8"))
        ga, gc = r["gamma_history"], r["gamma_critical_history"]
        T = 0.30
        misleading = [(a, c) for a, c in zip(ga, gc) if a < T <= c]
        assert misleading, (
            "exp44 no longer shows a round where the legacy field reads below "
            "the threshold while the gate series reads above it"
        )
