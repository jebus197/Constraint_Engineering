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


@pytest.fixture
def sandboxed_reset(sandboxed):
    """A sandbox whose store is EMPTY, which is this mechanism's actual subject.

    ★ DECOUPLED FROM THE LIVE STORE, 2026-10-29. `sandboxed` copies the live
    file in, so the 2 tests below could only pass while the live store happened
    to be empty -- and they went RED the moment a legitimate simulated run
    repopulated it. That is a point-in-time state asserted as an invariant, and
    it is in direct tension with the OTHER half of his 2026-10-16 ruling:
    *"probably the best strategy is to leave the default in this case set to
    on, so that it can persist between experiments"*. Persistence is the ruled
    default, so a populated store is correct behaviour and must not fail a
    guard.

    The RESET recognition machinery still has to work, so it is now tested
    against a store that IS reset, constructed here. That is strictly stronger:
    the mechanism is exercised whatever the live store holds.
    """
    mod, state, archive = sandboxed
    import json as _json
    fresh = {"version": 1, "experiment_count": 0, "decay_rate": 0.0,
             "drift_threshold": 0.0, "source_hash": "", "experiment_ids": [],
             "records": {}}
    if state.is_file():
        try:
            held = _json.loads(state.read_text(encoding="utf-8"))
            # keep whatever shape the real file carries, emptied
            for k in ("version", "decay_rate", "drift_threshold", "source_hash"):
                if k in held:
                    fresh[k] = held[k]
        except (OSError, ValueError):
            pass
    state.write_text(_json.dumps(fresh, indent=2), encoding="utf-8")
    return mod, state, archive


def test_the_live_store_is_never_written_by_this_guard():
    """Stated first because it is the precondition for everything below."""
    before = LIVE.read_bytes() if LIVE.is_file() else None
    _fresh_module("ime_readonly_probe")
    after = LIVE.read_bytes() if LIVE.is_file() else None
    assert before == after


def test_a_reset_store_is_recognised_as_reset(sandboxed_reset):
    mod, state, archive = sandboxed_reset
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


def test_the_skip_reason_names_his_ruling_and_what_was_reset(sandboxed_reset):
    mod, _, archive = sandboxed_reset
    if not any(archive.glob("*.why.json")):
        pytest.skip("no archived reset record to read")
    with pytest.raises(BaseException) as caught:
        mod._require_populated_memory()
    message = str(getattr(caught.value, "msg", caught.value))
    # ★ UPDATED 2026-10-30 FOR HIS OPTION 1. The skip no longer says the memory
    # was RESET, because under his ruling it fires whenever the memory does not
    # hold the 3 runs these claims were measured on -- which includes a memory
    # populated by other runs, where "DELIBERATELY RESET" would be false. The
    # 2 properties that matter are unchanged and are asserted below: the reason
    # is HIS, and the skip says it is temporary.
    assert "does not hold the runs these claims were measured on" in message, message
    assert "his ruling" in message.lower(), message
    assert "re-arms itself" in message, (
        "the skip must say it is temporary, or the next reader takes it for a "
        "permanent exemption")
    assert "reset immune memory" in message.lower(), (
        "the archived reset reason must still be carried, or a reader cannot "
        "tell why the memory is in this state")


def test_it_re_arms_the_moment_the_MEASURED_runs_exist(sandboxed):
    """THE PROPERTY THE FIRST VERSION FAILED, and the reason this guard exists.

    ★ NARROWED TO THE MEASURED RUNS 2026-10-30, ON HIS RULING, AND THIS GUARD
    IS WHAT CAUGHT THE CHANGE. It asserted that ANY record re-arms the suite,
    which is the rule his option 1 replaced: the free run of 2026-10-28 wrote 1
    unrelated record and all 6 assertions re-armed against a memory that does
    not hold `exp47_divergence_locationkey_live`,
    `exp48_chemistry_exam_live` or `exp49_engineering_exam_live`, then failed
    as regressions they are not.

    The TEETH ARE KEPT and the property is now the right one: a memory holding
    the 3 measured runs MUST arm, so the suite cannot be exempted while the
    evidence for its claims is present. The converse -- that a memory holding
    OTHER runs skips, and says which runs are missing -- is asserted in the
    test below, so neither half can be dropped silently.
    """
    mod, state, _ = sandboxed
    data = json.loads(state.read_text())
    data["records"] = {"1": {"flaw_class": 1, "confirmed": 1.0, "rejected": 0.0}}
    data["experiment_count"] = len(mod._RECORDING_RUNS)
    data["experiment_ids"] = list(mod._RECORDING_RUNS)
    state.write_text(json.dumps(data))
    assert mod.reset_record() is None, (
        "the memory holds every run these claims were measured on and is "
        "still being read as reset, so the 6 populated-memory assertions "
        "would stay skipped for ever")
    # AND THE SKIP HELPER THEN LETS THE TEST RUN.
    mod._require_populated_memory()


def test_a_memory_of_OTHER_runs_skips_and_names_what_is_missing(sandboxed_reset):
    """The other half of his option 1, so the widening cannot go unnoticed.

    A memory populated by runs these claims were NOT measured from must skip
    rather than fail -- that is the defect B50 recorded -- and the skip must
    name the runs it is missing, or it is indistinguishable from a blanket
    exemption.
    """
    mod, state, archive = sandboxed_reset
    if not any(archive.glob("*.why.json")):
        pytest.skip("no archived reset record to read")
    data = json.loads(state.read_text())
    data["records"] = {"1": {"flaw_class": 1, "confirmed": 1.0, "rejected": 0.0}}
    data["experiment_count"] = 1
    data["experiment_ids"] = ["some_unrelated_run"]
    state.write_text(json.dumps(data))

    record = mod.reset_record()
    assert record is not None, (
        "a memory holding only unrelated runs was read as sufficient, so the "
        "6 assertions will re-arm against evidence that cannot support them "
        "and fail as regressions -- the exact defect B50 recorded")
    reason = str(record.get("reason", ""))
    for run in mod._RECORDING_RUNS:
        assert run in reason, f"the skip reason does not name {run}"
    assert "some_unrelated_run" in reason, (
        "the skip reason does not say what the memory DOES hold, so a reader "
        "cannot tell a reset from a mismatch")
    with pytest.raises(BaseException):
        mod._require_populated_memory()


def test_a_renamed_records_attribute_raises_rather_than_exempting(sandboxed_reset,
                                                                  monkeypatch):
    """Defaulting on a rename would silently restore the exemption."""
    mod, _, archive = sandboxed_reset
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
