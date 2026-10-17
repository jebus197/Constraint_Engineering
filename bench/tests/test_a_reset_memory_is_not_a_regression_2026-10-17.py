"""A deliberately reset immune memory must not be reported as a defect.

FOUND 2026-10-17 BY RUNNING THE SUITE AFTER CARRYING OUT HIS RULING. His words,
2026-10-16: *"We reset immune memory for the upcoming live experiments, since
simulation can probably only tell us so much about how this facility will
function in real live/paid experiments."* The reset was carried out, archiving 6
experiments' priors and leaving the live store at 0 records.

`bench/tests/test_immune_memory_evaluation.py` then reported 6 failures, and its
own message read: *"NO class carries any refutation weight. Refutations were
observed from leg 3 onward, so this means falsifiers have stopped reaching a
refutation -- the confinement defect of 2026-10-15, or one like it, is back"*.
IT IS NOT BACK. The memory is empty because he ordered it emptied, and a reader
following that message would have gone hunting a defect that does not exist --
a false alarm of the most expensive kind, because it points at a real past
defect by name.

THE RESET IS DETECTABLE, so the confusion had no excuse: the reset writes an
archived copy beside a `.why.json` naming the ruling, the archived sha, how
many experiments it held and their ids. `reset_record()` reads that evidence and
`_require_populated_memory()` skips with the reset's own reason.

IT IS NOT AN EXEMPTION, AND THAT IS THE PROPERTY THIS GUARD EXISTS FOR. The
first version read `getattr(live, "records", None)`, and the attribute is
`_records` -- always None, so the reset record was returned even with records
present and the 6 assertions would have stayed skipped FOR EVER. That is the
permanent exemption the docstring promises it is not, and it was caught only by
the check written to verify the re-arm.

THIS GUARD NEVER TOUCHES THE LIVE STORE. It redirects the module's paths at a
temporary copy. Earlier on 2026-10-17 a test of mine destroyed the live immune
memory by matching a sidecar in an archive glob, and it had to be recovered from
the verified archive; that file is not something to experiment on.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SUITE = REPO / "bench" / "tests" / "test_immune_memory_evaluation.py"
LIVE = REPO / "bench" / "state" / "immune_memory.json"
ARCHIVE = REPO / "bench" / "state" / "immune_memory_archive"


def _fresh_module(name: str):
    sys.path.insert(0, str(REPO))
    sys.path.insert(0, str(REPO / "bench" / "tests"))
    spec = importlib.util.spec_from_file_location(name, SUITE)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def sandboxed(tmp_path, monkeypatch, request):
    """The suite's module with its state paths pointed at a COPY."""
    mod = _fresh_module(f"ime_sandbox_{abs(hash(request.node.name)) % 10**8}")
    state = tmp_path / "immune_memory.json"
    archive = tmp_path / "immune_memory_archive"
    archive.mkdir()
    if LIVE.is_file():
        state.write_bytes(LIVE.read_bytes())
    if ARCHIVE.is_dir():
        for f in ARCHIVE.iterdir():
            (archive / f.name).write_bytes(f.read_bytes())
    monkeypatch.setattr(mod, "_STATE", str(state))
    monkeypatch.setattr(mod, "_ARCHIVE", str(archive))
    return mod, state, archive


def test_the_live_store_is_never_written_by_this_guard():
    """Stated first because it is the precondition for everything below."""
    before = LIVE.read_bytes() if LIVE.is_file() else None
    _fresh_module("ime_readonly_probe")
    after = LIVE.read_bytes() if LIVE.is_file() else None
    assert before == after


def test_a_reset_store_is_recognised_as_reset(sandboxed):
    mod, state, archive = sandboxed
    if not any(archive.glob("*.why.json")):
        pytest.skip("no archived reset record to read")
    record = mod.reset_record()
    assert record is not None, (
        "the reset was not recognised, so the suite will report a confinement "
        "regression that has not happened")
    assert "reset immune memory" in str(record.get("reason", "")).lower()
    held = record.get("state_when_archived") or {}
    assert held.get("experiment_count", 0) >= 1, (
        "the archived record names no experiments, so the skip reason would "
        "tell a reader nothing about what was reset")


def test_the_skip_reason_names_his_ruling_and_what_was_reset(sandboxed):
    mod, _, archive = sandboxed
    if not any(archive.glob("*.why.json")):
        pytest.skip("no archived reset record to read")
    with pytest.raises(BaseException) as caught:
        mod._require_populated_memory()
    message = str(getattr(caught.value, "msg", caught.value))
    assert "DELIBERATELY RESET" in message, message
    assert "his ruling" in message.lower(), message
    assert "re-arms itself" in message, (
        "the skip must say it is temporary, or the next reader takes it for a "
        "permanent exemption")


def test_it_re_arms_the_moment_a_record_exists(sandboxed):
    """THE PROPERTY THE FIRST VERSION FAILED, and the reason this guard exists."""
    mod, state, _ = sandboxed
    data = json.loads(state.read_text())
    data["records"] = {"1": {"flaw_class": 1, "confirmed": 1.0, "rejected": 0.0}}
    data["experiment_count"] = 1
    data["experiment_ids"] = ["probe_run"]
    state.write_text(json.dumps(data))
    assert mod.reset_record() is None, (
        "a populated memory is still being read as reset, so the 6 "
        "populated-memory assertions would stay skipped for ever")
    # AND THE SKIP HELPER THEN LETS THE TEST RUN.
    mod._require_populated_memory()


def test_a_renamed_records_attribute_raises_rather_than_exempting(sandboxed,
                                                                  monkeypatch):
    """Defaulting on a rename would silently restore the exemption."""
    mod, _, archive = sandboxed
    if not any(archive.glob("*.why.json")):
        pytest.skip("no archived reset record to read")

    class _NoRecords:
        @staticmethod
        def load(_path):
            return _NoRecords()

    monkeypatch.setattr(mod, "ImmuneMemory", _NoRecords)
    with pytest.raises(AttributeError, match="_records"):
        mod.reset_record()


def test_the_six_assertions_are_guarded_and_no_others(sandboxed):
    """The guard must be on the populated-memory tests and nowhere else.

    Counted, because adding it to a test that does not need it would hide a
    real failure behind a reset that is irrelevant to it.
    """
    src = SUITE.read_text(encoding="utf-8")
    assert src.count("_require_populated_memory()") == 7, (
        f"expected 6 call sites plus the definition, found "
        f"{src.count('_require_populated_memory()')}")
