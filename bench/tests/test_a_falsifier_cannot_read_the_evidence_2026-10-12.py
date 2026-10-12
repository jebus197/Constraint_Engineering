"""A falsifier may not read this project's own run or panel evidence.

THE HOLE, FOUND INDEPENDENTLY BY BOTH FREE SEATS ON 2026-10-12 AND CONFIRMED ON
A CLEAN TREE. The repository root is in the observer's rendered allow set, so a
sandboxed falsifier could read `experimental_notes/evidence/` and `bench/logs/`
-- prior rounds of the very exam it is part of, including other seats' replies.
`tempfile.gettempdir()` is allowed too, and 472 sibling panel sandboxes sat
directly beneath it. The sealed scoring key store was never reachable, being
digest-matched by `_protected`.

Both seats specified the same repair and BOTH DECLINED TO WRITE IT, for the same
stated reason: the observer is the harness's most safety-critical component, the
change reorders its gate precedence, and narrowing an allowlist can refuse
HONEST falsifiers. cc2 named the missing piece exactly -- "a scratch-path
inventory across archived falsifiers ... One line of code, one measurement I did
not have time to take."

THE FOUNDER RULED ON THAT, 2026-10-12: *"Then what is the fix? If the models
didn't suggest any, and you didn't devise any, then that is not an ideal
outcome. ... A better outcome would be to derive the optimal fix, then test it
in the upcoming simulated run and program of study. ... You appear to be
implying here that no resolution can exist? Is that accurate?"* It was not
accurate, and this file is the resolution.

THE MEASUREMENT THAT MADE IT BUILDABLE, and it also DREW THE BOUNDARY. Across
1,360 archived falsifier sources, 0 name a run or panel evidence region: Wilson
95% [0.0000%, 0.2817%], Clopper-Pearson [0.0000%, 0.2709%]. But denying ALL of
`experimental_notes/` would have refused 1 honest falsifier -- C0061 in
commissioning_arm1_panel_20260929T214647Z reads `CDSFL_MASTER_TASK_LIST.md` to
demonstrate that a test file parses the task list at import time. So the
canonical task list stays READABLE and the evidence subtrees do not. Producer:
scripts/does_any_falsifier_read_the_evidence_2026-10-12.py.

WHY THE TIER IS CHECKED BEFORE THE ALLOWLIST rather than carved out of it:
narrowing the temp allowance alone would NOT close this, because the clone root
grants the same reads independently. fable established that. One tier placed
beside `_protected` closes every route at once.

THESE TESTS EXECUTE THE REAL OBSERVER TEMPLATE. The source is rendered exactly
as a verification renders it and run with only the audit-hook installation
stubbed, so what is asserted is the code that actually guards a falsifier, not a
reconstruction of it.
"""
import pathlib
import sys
import types

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import pytest  # noqa: E402

import bench.falsifier_verify as fv  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[2]
SIBLING = "/var/folders/cc/T/cdsfl_panel_abc/repo"


@pytest.fixture(scope="module")
def denied():
    """The REAL `_denied` out of the rendered observer, hook install stubbed."""
    src = fv._observer_source(trace_path="/tmp/cdsfl_trace_probe",
                              repo_root=str(REPO))
    fake_sys = types.ModuleType("sys")
    for attr in ("argv", "executable", "prefix", "base_prefix", "exec_prefix",
                 "base_exec_prefix", "path", "version", "version_info",
                 "modules"):
        setattr(fake_sys, attr, getattr(sys, attr))
    fake_sys.addaudithook = lambda fn: None
    ns = {"sys": fake_sys}
    exec(compile(src.replace("sys.addaudithook(_hook)", "pass"),
                 "<observer>", "exec"), ns)
    return ns["_denied"]


@pytest.mark.parametrize("rel", [
    "bench/logs/clear_the_outstanding_2026-10-12/cc2.json",
    "bench/logs/study_run1b_2026-10-03_20261003T100439Z/runner_state.json",
    "experimental_notes/evidence/panel_records_2026-10-12/x.json",
    "experimental_notes/seat_evidence/round/seat/file.py",
])
def test_this_exams_own_evidence_is_refused(denied, rel):
    assert denied(f"{REPO}/{rel}") is True, (
        f"{rel} is readable from inside a falsifier; that is prior-round "
        f"material from the exam the falsifier is part of")


@pytest.mark.parametrize("rel", [
    "bench/logs/round/cc2.json",
    "experimental_notes/seat_evidence/round/seat/file.py",
])
def test_a_SIBLING_sandboxs_evidence_is_refused(denied, rel):
    """cc2 measured 472 sibling sandboxes under an allowed temp root."""
    assert denied(f"{SIBLING}/{rel}") is True, (
        "another seat's sandbox is readable; this is the Exp 48 shape with no "
        "key involved")


@pytest.mark.parametrize("rel", [
    "experimental_notes/CDSFL_MASTER_TASK_LIST.md",
    "bench/reference_runner_v3.py",
    "docs/MATHEMATICAL_APPENDIX.md",
    "bench/falsifier_verify.py",
])
def test_the_honest_reads_still_work(denied, rel):
    """THE BOUNDARY, AND IT IS WHERE THE MEASUREMENT PUT IT.

    The task list is the measured carve-out: 1 archived falsifier reads it to
    demonstrate a real defect. Source and the maths model were never in
    question and must not become collateral.
    """
    assert denied(f"{REPO}/{rel}") is False, (
        f"{rel} is now refused, so an honest falsifier that reads it is "
        f"reported as an integrity violation")


def test_the_key_store_is_still_refused_and_by_the_PROTECTED_set(denied):
    """The tier must not have displaced the thing that actually matters."""
    import os
    key = os.path.expanduser("~/.config/cdsfl/scoring.env")
    assert denied(key) is True, "the sealed key store became readable"


def test_no_evidence_segment_carries_a_date():
    """A DATED segment covers one day and rots on the next.

    The first draft of this tier listed `panel_records_2026-10-12`. It was
    removed: the mirrored panel records already sit under
    `experimental_notes/evidence/`, which the predicate covers by its own
    branch.
    """
    import re
    bad = [s for s in fv.EVIDENCE_SEGMENTS if re.search(r"20\d\d", s)]
    assert not bad, f"dated segment(s) in the evidence set: {bad}"


def test_the_tier_precedes_the_allowlist(denied):
    """Placement is the whole design: inside an ALLOWED root, still refused.

    The repository root IS an allowed root -- that is the hole. So a path that
    the allowlist would admit, and which the tier refuses, proves the ordering
    by execution rather than by reading it off the page.
    """
    allowed_roots = [r for r in fv._interpreter_roots()]
    inside = f"{REPO}/bench/logs/round/report.json"
    assert denied(inside) is True
    assert denied(f"{REPO}/bench/runner_core.py") is False, (
        "the allowlist no longer admits ordinary repository source, so the "
        "tier is too wide")
    assert isinstance(allowed_roots, list)
