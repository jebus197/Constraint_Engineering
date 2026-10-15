"""B7: a run must not restamp a seat it never dispatched.

THE DEFECT, measured 2026-10-15 on both free runs. `_load_fingerprints` globs
EVERY file in `bench/fingerprints/` into one dict keyed by `model_id` and
discards the provenance fields. `_save_fingerprints` then wrote EVERY key of
that dict back, stamped with the current run's name. So the last run to save
re-attributed every profile it did not measure: all 11 files were written at
free run 1's convergence moment, restamping 5 of 5 REAL PAID SEATS -- CC2,
ChatGPT, Codex, DeepSeek, Gemini -- none of which is dispatched in a simulated
run. Confirmed again on free run 2. The true last real observation,
`study_run1b_2026-10-03`, was overwritten in the working tree both times.

THE CREDIT IS NOT CC1's. The `fable` seat found this on 2026-10-05 during the
fingerprint ladder review and named the mechanism exactly, under its own heading
"THE FINGERPRINT STORE ERASES RUN PROVENANCE ON EVERY SAVE". Its producer was
harvested into `bench/logs/` and never promoted into `scripts/`, so the defect
survived 10 days.

WHY IT MATTERED EVEN THOUGH NO VALUE MOVED. 0 of 5 real seats had any observed
VALUE altered, because they were never dispatched and so nothing was appended.
What kept the real and simulated records apart is the mandatory `-SIM` suffix
making `CC2-SIM` a different key from `CC2`. That naming rule is therefore the
sole guard on the real seats' accumulated counters, 3 of which feed live routing
and decomposition decisions. Drop the suffix and a mislabelled record becomes
corrupted data.

THESE TESTS EXECUTE both functions against a temporary directory, per
`execute-do-not-grep`. A test asserting on the source text of `_save_fingerprints`
would pass while a producer and a consumer disagreed.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
for _p in (REPO, REPO / "bench"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))


@pytest.fixture
def runner(tmp_path, monkeypatch):
    import reference_runner_v3 as rr
    monkeypatch.setattr(rr, "FINGERPRINT_DIR", tmp_path, raising=True)
    return rr


def _seed(d: pathlib.Path, seat: str, findings: int,
          experiment: str = "prior_run_2026-10-03") -> None:
    (d / f"{seat}.json").write_text(json.dumps({
        "model_id": seat, "experiment": experiment,
        "timestamp": "2026-10-03T00:00:00+00:00",
        "observed": {"total_findings": findings, "rounds_participated": 7},
    }), encoding="utf-8")


def _read(d: pathlib.Path, seat: str) -> dict:
    return json.loads((d / f"{seat}.json").read_text(encoding="utf-8"))


class TestAnUnobservedSeatKeepsItsProvenance:
    def test_the_real_seat_is_not_restamped(self, runner, tmp_path):
        _seed(tmp_path, "CC2", 400)
        _seed(tmp_path, "CC2-SIM", 11)
        loaded = runner._load_fingerprints()
        loaded["CC2-SIM"]["total_findings"] = 19      # only the SIM seat ran
        runner._save_fingerprints(loaded, "free_run_2026-10-15")
        assert _read(tmp_path, "CC2")["experiment"] == "prior_run_2026-10-03"

    def test_the_observed_seat_IS_restamped(self, runner, tmp_path):
        _seed(tmp_path, "CC2", 400)
        _seed(tmp_path, "CC2-SIM", 11)
        loaded = runner._load_fingerprints()
        loaded["CC2-SIM"]["total_findings"] = 19
        runner._save_fingerprints(loaded, "free_run_2026-10-15")
        got = _read(tmp_path, "CC2-SIM")
        assert got["experiment"] == "free_run_2026-10-15"
        assert got["observed"]["total_findings"] == 19

    def test_the_unobserved_seats_values_are_untouched(self, runner, tmp_path):
        _seed(tmp_path, "CC2", 400)
        _seed(tmp_path, "CC2-SIM", 11)
        loaded = runner._load_fingerprints()
        loaded["CC2-SIM"]["total_findings"] = 19
        runner._save_fingerprints(loaded, "free_run_2026-10-15")
        assert _read(tmp_path, "CC2")["observed"]["total_findings"] == 400

    def test_all_5_real_seats_survive_a_simulated_run(self, runner, tmp_path):
        """The exact shape measured on both free runs."""
        real = ["CC2", "ChatGPT", "Codex", "DeepSeek", "Gemini"]
        sims = [f"{s}-SIM" for s in real] + ["Fable-SIM"]
        for s in real:
            _seed(tmp_path, s, 400)
        for s in sims:
            _seed(tmp_path, s, 11)
        loaded = runner._load_fingerprints()
        for s in sims:
            loaded[s]["total_findings"] = 19
        runner._save_fingerprints(loaded, "free_run_2026-10-15")
        restamped = [s for s in real
                     if _read(tmp_path, s)["experiment"] != "prior_run_2026-10-03"]
        assert restamped == [], f"restamped seats it never dispatched: {restamped}"
        assert all(_read(tmp_path, s)["experiment"] == "free_run_2026-10-15"
                   for s in sims)


class TestTheSnapshotIsByValueNotByReference:
    def test_an_in_place_mutation_is_still_detected(self, runner, tmp_path):
        """The runner mutates payloads in place, so a shallow snapshot would
        alias them and every seat would read as unchanged."""
        _seed(tmp_path, "SEAT", 5)
        loaded = runner._load_fingerprints()
        loaded["SEAT"]["total_findings"] = 6          # in place, same dict object
        runner._save_fingerprints(loaded, "new_run")
        assert _read(tmp_path, "SEAT")["experiment"] == "new_run"

    def test_a_nested_in_place_mutation_is_detected(self, runner, tmp_path):
        (tmp_path / "SEAT.json").write_text(json.dumps({
            "model_id": "SEAT", "experiment": "old",
            "timestamp": "2026-10-03T00:00:00+00:00",
            "observed": {"history": [1, 2, 3]}}), encoding="utf-8")
        loaded = runner._load_fingerprints()
        loaded["SEAT"]["history"].append(4)           # mutates a NESTED list
        runner._save_fingerprints(loaded, "new_run")
        assert _read(tmp_path, "SEAT")["experiment"] == "new_run"


class TestANewSeatIsAlwaysWritten:
    def test_a_seat_with_no_prior_file_is_written(self, runner, tmp_path):
        loaded = runner._load_fingerprints()
        loaded["BRAND-NEW-SIM"] = {"total_findings": 3}
        runner._save_fingerprints(loaded, "first_run")
        assert (tmp_path / "BRAND-NEW-SIM.json").is_file()
        assert _read(tmp_path, "BRAND-NEW-SIM")["experiment"] == "first_run"


class TestTheLogSaysWhatItDid:
    def test_the_log_names_the_observed_count_and_the_skipped_seats(
            self, runner, tmp_path, monkeypatch):
        lines: list[str] = []
        monkeypatch.setattr(runner, "_log", lambda m: lines.append(str(m)))
        _seed(tmp_path, "CC2", 400)
        _seed(tmp_path, "CC2-SIM", 11)
        loaded = runner._load_fingerprints()
        loaded["CC2-SIM"]["total_findings"] = 19
        runner._save_fingerprints(loaded, "free_run_2026-10-15")
        joined = "\n".join(lines)
        assert "1 observed" in joined, joined
        assert "CC2" in joined and "untouched" in joined, joined
