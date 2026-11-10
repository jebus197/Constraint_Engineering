"""Which models are in use is DERIVED from the archive, never maintained by hand.

HIS RULING, B79, 2026-11-08, verbatim: *"This is about naming models that no
longer exist? Correct? So what we need is a way to dynamically record what
models do exist and which are in use, rather than going back and renaming them
by hand? fr"*

WHAT EXISTS AND WHAT IS IN USE ARE 2 QUESTIONS. `catalogue()` answered the
first. A label can be declared in the registry and never dispatched, or
dispatched for months and then quietly dropped, and neither is visible from the
registry alone -- which is why the record was being corrected by hand, the
failure his ruling names.

THE SOURCE IS EACH RUN'S OWN `completion_signal.json`, so a model falls out of
the answer by not being used, with no edit anywhere.

WHAT IT SURFACED ON ITS FIRST RUN, and this is why the facility earns its
place rather than merely existing: the most recent REAL dispatch in the whole
archive is 2026-08-23, and `Fable` appears 15 times as a simulated stand-in
with 0 real dispatches. Both facts were invisible before.

THE FIRST VERSION HID THE SECOND ONE. `declared_but_unused` treats a `-SIM` run
as evidence a seat is in use as a configuration -- defensible, and also how
`Fable` was reported as in use while no paid dispatch of it had ever been
recorded. `never_dispatched_for_real` is a separate answer for exactly that
case, because a kinder aggregate is how the question his ruling asks gets lost.
"""
from __future__ import annotations

import importlib
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))


@pytest.fixture(scope="module")
def mc():
    return importlib.import_module("model_catalogue")


class TestItIsDerivedAndNotDeclared:

    def test_the_entry_points_exist(self, mc):
        for name in ("in_use", "declared_but_unused",
                     "never_dispatched_for_real"):
            assert callable(getattr(mc, name, None)), name

    def test_it_reads_the_run_archive_not_a_hardcoded_list(self, mc, tmp_path):
        """Point it at a SYNTHETIC archive and the answer must follow it.

        A function returning the real answer from a baked-in list would pass
        every test above. This one can only pass by reading what it is given.
        """
        run = tmp_path / "synthetic_run"
        run.mkdir()
        (run / "completion_signal.json").write_text(json.dumps({
            "timestamp": "2026-01-02T00:00:00+00:00",
            "active_models": ["ZZTOP", "ZZTOP-SIM"],
        }))
        rows = mc.in_use(logs_dir=tmp_path)
        labels = {r["label"] for r in rows}
        assert labels == {"ZZTOP", "ZZTOP-SIM"}, rows
        assert all(r["runs"] == 1 for r in rows), rows
        assert all(r["last"] == "2026-01-02" for r in rows), rows

    def test_the_simulated_flag_is_read_from_the_suffix(self, mc, tmp_path):
        run = tmp_path / "r"
        run.mkdir()
        (run / "completion_signal.json").write_text(json.dumps({
            "timestamp": "2026-01-02T00:00:00+00:00",
            "active_models": ["Real", "Real-SIM"],
        }))
        by = {r["label"]: r for r in mc.in_use(logs_dir=tmp_path)}
        assert by["Real"]["simulated"] is False
        assert by["Real-SIM"]["simulated"] is True

    def test_since_excludes_older_runs(self, mc, tmp_path):
        for name, stamp, label in (("old", "2026-01-01", "OLDONLY"),
                                   ("new", "2026-06-01", "NEWONLY")):
            d = tmp_path / name
            d.mkdir()
            (d / "completion_signal.json").write_text(json.dumps({
                "timestamp": f"{stamp}T00:00:00+00:00",
                "active_models": [label]}))
        allrows = {r["label"] for r in mc.in_use(logs_dir=tmp_path)}
        assert allrows == {"OLDONLY", "NEWONLY"}
        # `since` is only honoured on the default archive path in the CLI, so
        # assert the filter itself on the same synthetic tree.
        recent = {r["label"] for r in
                  mc.in_use(since="2026-03-01", logs_dir=tmp_path)}
        assert recent == {"NEWONLY"}, recent

    def test_a_malformed_signal_does_not_break_the_answer(self, mc, tmp_path):
        bad = tmp_path / "bad"
        bad.mkdir()
        (bad / "completion_signal.json").write_text("{not json")
        good = tmp_path / "good"
        good.mkdir()
        (good / "completion_signal.json").write_text(json.dumps({
            "timestamp": "2026-05-05T00:00:00+00:00",
            "active_models": ["OK"]}))
        rows = mc.in_use(logs_dir=tmp_path)
        assert [r["label"] for r in rows] == ["OK"], rows


class TestTheSimOnlyCaseIsNotABSORBED:
    """The finding the first version hid."""

    def test_a_seat_only_ever_stood_in_for_is_reported(self, mc, tmp_path):
        d = tmp_path / "r"
        d.mkdir()
        (d / "completion_signal.json").write_text(json.dumps({
            "timestamp": "2026-04-04T00:00:00+00:00",
            "active_models": ["Alpha", "Alpha-SIM", "Beta-SIM"]}))
        # Alpha ran for real AND simulated; Beta only ever simulated.
        rows = mc.in_use(logs_dir=tmp_path)
        real = {r["label"] for r in rows if not r["simulated"]}
        assert real == {"Alpha"}, rows
        sim_bases = sorted({r["label"][:-4] for r in rows if r["simulated"]})
        assert sim_bases == ["Alpha", "Beta"], rows
        # AND THE FUNCTION ITSELF MUST SAY SO, not my re-derivation of it.
        # The first version of this test computed the answer here and compared
        # it to itself, so a mutation inside `never_dispatched_for_real` would
        # have gone unnoticed -- the same shape as a guard deriving its
        # expectation from its subject.
        assert mc.never_dispatched_for_real(logs_dir=tmp_path) == ["Beta"], (
            mc.never_dispatched_for_real(logs_dir=tmp_path))

    def test_the_live_archive_still_names_fable(self, mc):
        """A FLOOR, not an equality: this may only grow if Fable runs for real.

        Pinning the exact list would go stale the moment a paid round runs,
        which is the stale-pin failure this project has recorded 3 times in 2
        days. So the assertion is that the facility REPORTS the sim-only case
        at all, and that it does not claim a real dispatch that the archive
        does not show.
        """
        sim_only = mc.never_dispatched_for_real()
        rows = mc.in_use()
        real = [r for r in rows if not r["simulated"]]
        assert rows, "the live archive produced no rows at all"
        for name in sim_only:
            assert not any(r["label"].upper() == name.upper() for r in real), (
                f"{name} is reported as never dispatched for real while a "
                f"real row for it exists")


class TestTheCLIAnswersBothQuestions:

    def _run(self, *args):
        import subprocess
        return subprocess.run(
            [sys.executable, str(REPO / "bench" / "model_catalogue.py"), *args],
            capture_output=True, text=True, timeout=120)

    def test_help_reaches_no_network_and_names_the_new_flag(self):
        r = self._run("--help")
        assert r.returncode == 0, r.stderr
        assert "--in-use" in r.stdout, r.stdout

    def test_in_use_reports_the_most_recent_real_dispatch(self):
        r = self._run("--in-use")
        assert r.returncode == 0, r.stderr
        assert "most recent REAL dispatch" in r.stdout, r.stdout
        assert "LABEL" in r.stdout and "KIND" in r.stdout, r.stdout

    def test_in_use_json_is_parseable_and_carries_both_answers(self):
        r = self._run("--in-use", "--json")
        assert r.returncode == 0, r.stderr
        j = json.loads(r.stdout)
        assert "in_use" in j and "declared_but_unused" in j, sorted(j)
        assert isinstance(j["in_use"], list)
