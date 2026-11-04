"""B20's status instrument must MEASURE its verdicts, not assert them.

THE DEFECT, found 2026-11-04 while working B20 because the Stop gate named it.
`scripts/has_the_bound_orchestrator_been_built_or_run_2026-11-02.py` had 3
constants where it reported measurements:

1. `verdicts["monitoring_loop"]` was a conditional expression over 2
   file-existence checks — `cy_watchdog_2026-10-02.py` and
   `hooks/cy_monitor_gate.py` — that returned the literal string "PARTLY BUILT:
   ... what is absent is a loop that ACTS on them unattended", with **0
   references to anything that might act**. So it could not change when the
   actuator was built, and it went on reporting the component as PARTLY BUILT
   while `bench/tools/cy_actuator_2026-11-03.py` sat in the tree, imported, and
   exposed `classify` and `main`. The instrument's own output asserted the
   absence of something present.

2. The EVENT VOCABULARY was counted by `re.findall(r'say\\("([A-Z_ ]+)"')` and
   printed as 4 kinds. The watchdog emits its events through `ev()`, a different
   function with 10 distinct literal kinds; `say()` contributes ARMED, CLOSED and
   HEARTBEAT with WATCHDOG shared. The union is **13**, which is the figure B20's
   own entry records — so the instrument contradicted the entry by more than
   threefold and the ENTRY was right.

3. The closing summary printed "WHAT REMAINS ... a loop that ACTS" and "So an
   absent component here is a DEFERRAL he ordered" unconditionally. Repairing (1)
   without these left the output self-contradictory for one run: "4 of 4 built"
   followed by a paragraph saying the acting loop is missing. That is the
   fixed-the-deciding-layer-left-the-reporting-layer shape found in the verdict
   census the same night, repeated within the hour.

A verdict that is a constant measures nothing. The project has confirmed that
shape before in `boundary_band_sensitivity`, which shipped as an unconditional
constant and was vacuous in 41 of 41 archived reports.

WHY THIS GUARD RUNS THE FUNCTION AGAINST A PLANTED TREE. Asserting on the source
text would prove only that the module describes itself consistently, which is
what `execute-do-not-grep` names. So the instrument is executed twice: once
against the real repository, where the actuator exists, and once against a
temporary tree holding the watchdog and the gate but NO actuator. The verdict
must differ. A constant cannot pass that.
"""
import importlib.util
import io
import contextlib
import pathlib
import shutil
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SRC = REPO / "scripts" / "has_the_bound_orchestrator_been_built_or_run_2026-11-02.py"
ACTUATOR = REPO / "bench" / "tools" / "cy_actuator_2026-11-03.py"


def _load():
    spec = importlib.util.spec_from_file_location("_b20_probe", SRC)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _run(module) -> str:
    """Run main() with a CLEAN argv.

    ★ `answer_help(__doc__, __file__)` inspects `sys.argv`, and under pytest that
    holds pytest's own arguments, so the first version of this harness captured
    an EMPTY string and 5 tests failed against the harness rather than against
    the subject. That is the probe-location failure this project already records:
    the fixture manufactured the result.
    """
    buf = io.StringIO()
    saved = sys.argv
    try:
        sys.argv = [str(SRC)]
        with contextlib.redirect_stdout(buf):
            try:
                module.main()
            except SystemExit:
                pass
    finally:
        sys.argv = saved
    out = buf.getvalue()
    assert out.strip(), "the instrument printed nothing; the harness is wrong"
    return out


@pytest.fixture(scope="module")
def real_output():
    return _run(_load())


# ------------------------------------------------- the actuator is real and seen

def test_the_actuator_exists_and_imports():
    """ANTI-VACUITY for everything below: if it were absent, the real run and the
    planted run would agree and every comparison here would be trivially true."""
    assert ACTUATOR.is_file(), "the subject of this guard is missing"
    spec = importlib.util.spec_from_file_location("_cy_act_probe", ACTUATOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert hasattr(mod, "classify") and hasattr(mod, "main")


def test_the_real_run_sees_the_actuator(real_output):
    assert "cy_actuator_2026-11-03.py exists: True" in real_output
    assert "BUILT AND TESTED, NOT ENABLED" in real_output


def test_the_real_run_reports_four_of_four(real_output):
    assert "4 of 4 component(s) built" in real_output
    assert "0 partly built" in real_output


# ----------------------------------------------- the verdict is not a constant

def test_the_verdict_changes_when_the_actuator_is_absent(tmp_path, monkeypatch):
    """THE LOAD-BEARING TEST. A constant cannot pass this.

    A tree is planted with the watchdog and the gate — the 2 files the old
    conditional tested — but no actuator. The old code returned PARTLY BUILT for
    exactly that input and also for the real tree, so it could not tell them
    apart.
    """
    sand = tmp_path / "repo"
    (sand / "scripts").mkdir(parents=True)
    (sand / "hooks").mkdir()
    (sand / "bench" / "tools").mkdir(parents=True)
    (sand / "bench" / "tests").mkdir()
    (sand / "bench" / "logs").mkdir()
    shutil.copy2(REPO / "scripts" / "cy_watchdog_2026-10-02.py",
                 sand / "scripts" / "cy_watchdog_2026-10-02.py")
    shutil.copy2(REPO / "hooks" / "cy_monitor_gate.py",
                 sand / "hooks" / "cy_monitor_gate.py")
    assert not (sand / "bench" / "tools" / "cy_actuator_2026-11-03.py").exists()

    m = _load()
    monkeypatch.setattr(m, "REPO", sand)
    out = _run(m)
    assert "BUILT AND TESTED, NOT ENABLED" not in out, (
        "the monitoring_loop verdict is the same with and without the actuator, "
        "so it is a constant and measures nothing")
    assert "PARTLY BUILT" in out, (
        f"expected the partly-built verdict on a tree with no actuator; got:\n"
        f"{out[-700:]}")


# --------------------------------------------- the vocabulary counts both emitters

def test_the_vocabulary_is_the_union_of_both_emitters(real_output):
    assert "13 kinds, 10 from ev() and 4 from say() with 1 shared" in real_output, (
        "the event vocabulary is not reported as the union of ev() and say(); a "
        "say()-only count gives 4 and understates it by 9")


def test_the_vocabulary_is_not_read_by_a_say_only_regex():
    """The old predicate named the wrong function; it must not come back."""
    src = SRC.read_text(encoding="utf-8")
    assert 'kinds = sorted(set(re.findall(' not in src, (
        "a regex is reading the event vocabulary again; it must come from the "
        "syntax tree over BOTH emitters")
    assert '_nm == "ev"' in src and '_nm == "say"' in src


# ------------------------------------------- the summary agrees with the verdict

def test_the_summary_does_not_contradict_the_verdict(real_output):
    """"4 of 4 built" and "what remains is a loop that ACTS" cannot both stand."""
    if "4 of 4 component(s) built" in real_output:
        assert "WHAT REMAINS, STATED RATHER THAN COUNTED: a loop that ACTS" \
            not in real_output, (
            "the summary still asserts the acting loop is missing while the "
            "verdict says every component is built")
        assert "NEITHER HALF IS A BUILD" in real_output


def test_the_deferral_line_does_not_excuse_absent_components(real_output):
    """It read "So an absent component here is a DEFERRAL he ordered" always."""
    if "0 absent" in real_output or "4 of 4 component(s) built" in real_output:
        assert "So an absent component here is a DEFERRAL" not in real_output
        assert "0 components are absent" in real_output


def test_the_never_run_finding_is_unchanged(real_output):
    """The repair must not have moved the experiment's own status."""
    assert "experiment_run" in real_output
    assert "NEVER RUN" in real_output
