"""Task 9.3, panel round 16: the intake-parser figures get a committed producer.

`scripts/intake_parser_recovery_2026-09-17.py` sums the runner's own
`falsifier_intake_telemetry` over the archived replies. This file executes it:
on a constructed archive whose every count is known, on the live archive under
the 2026-09-10 test's own stop rule, and with `--help`, which must answer without
reading any reply.

WHY A CONSTRUCTED ARCHIVE. The live counts move whenever a run is archived, so
they cannot be pinned. What can be pinned is that the producer counts correctly,
that its invariants hold, that a file reached through a tracked symlinked
directory is counted once, and that the live archive still shows the band the 2026-09-10 test
asserts: fenced-label recovery with a Wilson lower bound above 0.85 and the
raw-label interval wholly below it.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "intake_parser_recovery_2026-09-17.py"


@pytest.fixture(scope="module")
def ipr():
    spec = importlib.util.spec_from_file_location("intake_parser_recovery_2026_09_17", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


STRICT = "FALSIFIER:\n```python\nassert False\n```\n"
BARE = "FALSIFIER: none, nothing to demonstrate."
COMPANION = "FALSIFIER: C0001 shows the drop\n```python\nassert 1 == 2\n```\n"


def _archive(tmp_path):
    run = tmp_path / "bench" / "logs" / "exp99_fixture_20260917T000000Z"
    run.mkdir(parents=True)
    replies = {
        "r1_a_1.json": {"response": STRICT + "\n\n" + BARE},
        "r1_b_1.json": {"response": COMPANION},
        "r2_a_1.json": {"response": "no label here"},
        "r2_b_1.json": {"response": STRICT},
    }
    for name, body in replies.items():
        (run / name).write_text(json.dumps(body), encoding="utf-8")
    (run / "r3_a_1.json").write_text("{not json", encoding="utf-8")
    (tmp_path / "bench" / "logs" / "exp99_fixture_latest").symlink_to(run.name)
    return tmp_path


class TestItCountsAConstructedArchiveExactly:
    def test_the_telemetry_sees_the_companion_case_as_companion_only(self):
        sys.path.insert(0, str(ROOT / "bench"))
        from runner_core import falsifier_intake_telemetry as telem
        t = telem(COMPANION)
        assert (t["labels_seen"], t["blocks_recovered"],
                t["recovered_only_by_the_companion"]) == (1, 1, 1), t

    def test_the_symlinked_alias_is_counted_once(self, ipr, tmp_path):
        repo = _archive(tmp_path)
        files, aliases = ipr.population(repo=repo)
        assert len(files) == 5 and aliases == 5, (len(files), aliases)
        assert len({f.resolve() for f in files}) == 5

    def test_every_count(self, ipr, tmp_path):
        files, _ = ipr.population(repo=_archive(tmp_path))
        s = ipr.scan(files)
        assert s == {"files_read": 5, "replies_examined": 3, "labels_seen": 4,
                     "labels_with_a_fence_within_3_lines": 3, "blocks_recovered": 3,
                     "recovered_only_by_the_companion": 1, "unreadable": 1,
                     "labels_without_a_fence": 1}, s
        r = ipr.rates(s)
        assert (r["over_fenced_labels"]["k"], r["over_fenced_labels"]["n"]) == (3, 3)
        assert (r["over_raw_labels"]["k"], r["over_raw_labels"]["n"]) == (3, 4)

    def test_the_stop_rule_stops(self, ipr, tmp_path):
        files, _ = ipr.population(repo=_archive(tmp_path))
        s = ipr.scan(files, stop_at_fenced=1)
        assert s["labels_with_a_fence_within_3_lines"] == 1
        assert s["replies_examined"] == 1

    def test_the_2_wilson_implementations_agree(self, ipr):
        for k, n in ((3, 4), (117, 120), (1610, 3945), (0, 7), (7, 7)):
            r = ipr.rates({"blocks_recovered": k, "labels_seen": n,
                           "labels_with_a_fence_within_3_lines": n})
            assert r["over_raw_labels"]["agree_to"] < 1e-9, (k, n, r)


class TestTheLiveArchive:
    def test_the_invariants_and_the_band_under_the_2026_09_10_stop_rule(self, ipr):
        files, _ = ipr.population()
        if not files:
            pytest.skip("no archived replies in this clone")
        s = ipr.scan(files, stop_at_fenced=120)
        assert s["labels_with_a_fence_within_3_lines"] > 50, s
        assert s["blocks_recovered"] <= s["labels_seen"]
        assert s["labels_with_a_fence_within_3_lines"] <= s["labels_seen"]
        assert s["labels_without_a_fence"] == (
            s["labels_seen"] - s["labels_with_a_fence_within_3_lines"])
        assert s["recovered_only_by_the_companion"] <= s["blocks_recovered"]
        r = ipr.rates(s)
        lo_f = r["over_fenced_labels"]["wilson"][0]
        hi_r = r["over_raw_labels"]["wilson"][1]
        assert lo_f > 0.85, r["over_fenced_labels"]
        assert hi_r < lo_f, (r["over_raw_labels"], r["over_fenced_labels"])


class TestHelpIsInert:
    def test_help_answers_without_reading_the_archive(self):
        p = subprocess.run([sys.executable, str(SCRIPT), "--help"], cwd=ROOT,
                           capture_output=True, text=True, timeout=60)
        assert p.returncode == 0, p.stderr
        assert p.stdout.startswith("usage:"), p.stdout[:200]
        assert "replies carrying FALSIFIER" not in p.stdout
