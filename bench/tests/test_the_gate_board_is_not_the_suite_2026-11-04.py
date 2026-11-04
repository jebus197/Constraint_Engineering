"""The gate must state its own scope, and the share must be DERIVED.

THE DEFECT THIS GUARDS, and it was mine. On 2026-11-04 a board of "2502 passed,
11 skipped, 0 failed" was reported to the founder as a fully green board, in
answer to his explicit instruction to give him a fully green, honest board and
not to cut corners to make it green. That figure is the commit gate's static
`GUARDS` list, not `bench/tests/`. Measured: the gate collects 2,540 tests from
127 guard files against 15,431 from 811 files, a share of 0.164604, so 12,891
tests are never run by the gate and calling its board the suite overstates
coverage by a factor of 6.0752.

IT IS THE SECOND OCCURRENCE OF ONE SHAPE. The record already holds a report of
"2,333 passed" that was 120 files of 759 rather than the suite. In both cases
the sentence was true of what it measured and wrong about what it claimed to
measure.

AND THE FILE SHARE WAS ALREADY BEING MEASURED, which is the harder half to
admit. `scripts/precommit_gate_cost_2026-09-10.py` has printed "NOT reached by
the gate: 684 (0.8434 of the suite)" since commit 859dc04a on 2026-10-30, 5
days before the error. So an instrument existed, reported the adjacent figure,
and was not consulted -- the `use the instrument that exists` shape, not an
absence of measurement. What `scripts/the_gate_board_is_not_the_suite_2026-11-04.py`
adds is the TEST-COUNT share, which is a different quantity from the file share
and the one that carries the 6.0752 factor.

WHY THE ADDITION NEEDED THIS FILE AT ALL. The repair put a scope line on the
gate's success path and a producer in `scripts/`, and NOTHING EXECUTED EITHER.
`additive-standard` in its symmetric form forbids exactly that: every new flag,
gate or entry point must be wired to a caller and executed by a test, because
11 confirmed defects in this project were additions that did nothing. The first
version of the entry claiming this fix named no test file in its evidence
field, and `test_done_markers_carry_evidence_2026-09-10.py` caught it.

HOW IT IS TESTED, AND WHY NOT BY READING. Asserting that the gate's source
contains an `echo` would prove only that the gate describes itself
consistently. So the gate's scope arithmetic is EXTRACTED FROM THE GATE and run
in a real shell against a planted guard list and a planted test directory, and
the printed numbers must equal the plant. A hardcoded `echo` cannot pass that.
The producer's own functions are likewise called against a planted tree, so a
constant share cannot pass either.

NO FULL COLLECTION HAPPENS HERE. A full collection of both targets costs about
17 seconds and the figure already has a producer the operator can run; these
tests collect 2 tiny planted files instead, which exercises the same code path
at a cost the board can carry.
"""
import importlib.util
import io
import contextlib
import pathlib
import re
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PRODUCER = REPO / "scripts" / "the_gate_board_is_not_the_suite_2026-11-04.py"
GATE = REPO / "hooks" / "pre-commit"


def _load():
    spec = importlib.util.spec_from_file_location("_gate_share", PRODUCER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def mod():
    return _load()


def _plant_tests(d: pathlib.Path, spec: dict) -> None:
    """spec maps filename -> number of test functions to write into it."""
    d.mkdir(parents=True, exist_ok=True)
    for name, n in spec.items():
        body = "\n".join(f"def test_n{i}():\n    assert True\n" for i in range(n))
        (d / name).write_text(body, encoding="utf-8")


# ------------------------------------------------- the subjects actually exist

def test_the_producer_and_the_gate_both_exist():
    """ANTI-VACUITY for everything below."""
    assert PRODUCER.is_file(), "the producer this guard exists for is missing"
    assert GATE.is_file(), "the commit gate is missing"


# --------------------------------------- the guard list is READ, not duplicated

def test_the_guard_list_is_read_out_of_the_gate(mod, tmp_path, monkeypatch):
    """A planted gate naming 3 files must yield exactly those 3.

    A hardcoded copy of the real list cannot pass this, which is the property:
    the whole reason the figure was wrong before is that the gate's list and a
    reader's idea of it were 2 representations with no comparator.
    """
    fake = tmp_path / "pre-commit"
    fake.write_text(
        '#!/bin/sh\nGUARDS="bench/tests/test_alpha.py\n'
        'bench/tests/test_beta.py\nbench/tests/test_gamma.py"\n',
        encoding="utf-8")
    monkeypatch.setattr(mod, "GATE", fake)
    assert mod.guard_list() == ["bench/tests/test_alpha.py",
                                "bench/tests/test_beta.py",
                                "bench/tests/test_gamma.py"]


def test_an_unreadable_guard_list_voids_the_measurement(mod, tmp_path, monkeypatch):
    """A measurement that cannot be taken must say so, not return a number."""
    fake = tmp_path / "pre-commit"
    fake.write_text("#!/bin/sh\necho no guards here\n", encoding="utf-8")
    monkeypatch.setattr(mod, "GATE", fake)
    assert mod.guard_list() == []


def test_the_live_gate_list_matches_an_independent_parse(mod):
    """2 routes to one number, which is the project's cross-check rule.

    The producer's regex is compared against a line-oriented parse written
    differently here. If they disagree, one of them is wrong and the figure
    quoted to the founder cannot be trusted either way.
    """
    src = GATE.read_text(encoding="utf-8")
    lines = src.splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith('GUARDS="'))
    independent = [lines[start].split('"', 1)[1].strip()]
    for l in lines[start + 1:]:
        if l.rstrip().endswith('"'):
            independent.append(l.rstrip()[:-1].strip())
            break
        independent.append(l.strip())
    independent = [x for x in independent if x]
    assert mod.guard_list() == independent, (
        "the producer's regex and an independent parse disagree on the gate's "
        "own guard list")


# ------------------------------------------- the collection is real collection

def test_collect_returns_the_planted_test_count(mod, tmp_path, monkeypatch):
    """THE LOAD-BEARING TEST for the numerator. A constant cannot pass it."""
    sand = tmp_path / "repo"
    _plant_tests(sand / "bench" / "tests",
                 {"test_one.py": 3, "test_two.py": 4})
    monkeypatch.setattr(mod, "REPO", sand)
    assert mod.collect([sand / "bench" / "tests"]) == 7


def test_collect_reports_a_failure_rather_than_a_number(mod, tmp_path, monkeypatch):
    """A collection that cannot run must return the sentinel, not 0.

    0 would read as "the gate runs no tests", which is a measurement; -1 is an
    admission. The difference is the one this project calls a fail-safe that
    must not be recorded as a fact.
    """
    sand = tmp_path / "repo"
    (sand / "bench" / "tests").mkdir(parents=True)
    (sand / "bench" / "tests" / "test_broken.py").write_text(
        "def test_x(:\n", encoding="utf-8")        # a syntax error
    monkeypatch.setattr(mod, "REPO", sand)
    got = mod.collect([sand / "bench" / "tests"])
    # STRICTLY NEGATIVE. The first version asserted `got <= 0`, which is true of
    # 0 as well as of -1 -- so it could not tell the sentinel from a count,
    # which was the entire property. The mutation harness caught it: reverting
    # `return -1` to `return 0` left all 13 tests green.
    assert got < 0, (
        f"a failed collection reported {got}; only a strictly negative "
        f"sentinel is an admission, and 0 reads as 'the gate runs no tests'")


def test_the_reported_share_follows_the_planted_tree(mod, tmp_path, monkeypatch):
    """main() against a planted tree must print the PLANTED share.

    The live share is 2540/15431 = 0.164604. Here the gate lists 1 of 2 planted
    files holding 2 and 6 tests, so the share must be 2/8 = 0.250000. A printed
    constant, or a figure read from the real repository, fails.
    """
    sand = tmp_path / "repo"
    _plant_tests(sand / "bench" / "tests",
                 {"test_listed.py": 2, "test_unlisted.py": 6})
    (sand / "hooks").mkdir(parents=True)
    (sand / "hooks" / "pre-commit").write_text(
        '#!/bin/sh\nGUARDS="bench/tests/test_listed.py"\n', encoding="utf-8")
    monkeypatch.setattr(mod, "REPO", sand)
    monkeypatch.setattr(mod, "GATE", sand / "hooks" / "pre-commit")
    monkeypatch.setattr(mod, "SUITE", sand / "bench" / "tests")

    buf = io.StringIO()
    saved = sys.argv
    try:
        sys.argv = [str(PRODUCER)]
        with contextlib.redirect_stdout(buf):
            rc = mod.main()
    finally:
        sys.argv = saved
    out = buf.getvalue()
    assert rc == 0, f"main() returned {rc} on a sound planted tree:\n{out}"
    assert "2/8 = 0.250000" in out, (
        f"the share is not derived from the planted tree; got:\n{out}")
    assert "0.164604" not in out, (
        "the live share leaked into a planted measurement, so the figure is "
        "not being derived from the tree under test")
    assert "NEVER RUNS : 6" in out


def test_a_missing_guard_file_is_named_not_silently_dropped(mod, tmp_path, monkeypatch):
    """A guard the gate lists but that is absent must be REPORTED.

    Silently dropping it would inflate the share: the numerator would be
    collected from fewer files while the denominator stayed whole.
    """
    sand = tmp_path / "repo"
    _plant_tests(sand / "bench" / "tests", {"test_listed.py": 2})
    (sand / "hooks").mkdir(parents=True)
    (sand / "hooks" / "pre-commit").write_text(
        '#!/bin/sh\nGUARDS="bench/tests/test_listed.py\n'
        'bench/tests/test_vanished.py"\n', encoding="utf-8")
    monkeypatch.setattr(mod, "REPO", sand)
    monkeypatch.setattr(mod, "GATE", sand / "hooks" / "pre-commit")
    monkeypatch.setattr(mod, "SUITE", sand / "bench" / "tests")
    buf = io.StringIO()
    saved = sys.argv
    try:
        sys.argv = [str(PRODUCER)]
        with contextlib.redirect_stdout(buf):
            mod.main()
    finally:
        sys.argv = saved
    out = buf.getvalue()
    assert "absent from disk      : 1" in out
    assert "test_vanished.py" in out, (
        "the absent guard file is counted but not named, so a reader cannot "
        "tell WHICH guard the gate lists and does not have")


# ------------------------------- the gate's scope line EXECUTES and counts right

def _scope_fragment() -> str:
    """The gate's own scope arithmetic, lifted from the gate.

    DERIVED FROM THE SUBJECT rather than copied into this file. If the gate's
    lines move or are reworded, this raises instead of silently testing a stale
    copy of them -- the failure mode where a harness keeps passing against text
    the subject no longer contains.
    """
    src = GATE.read_text(encoding="utf-8").splitlines()
    first = next((i for i, l in enumerate(src)
                  if l.startswith("_GUARD_FILES=")), None)
    assert first is not None, (
        "the gate no longer computes _GUARD_FILES; the scope line this guard "
        "exists for has been removed or renamed")
    frag = src[first:first + 4]
    assert any("NOT the suite" in l for l in frag), (
        f"the scope echo is not within 4 lines of its arithmetic; got:\n"
        + "\n".join(frag))
    return "\n".join(frag)


def test_the_scope_arithmetic_counts_the_planted_guard_list(tmp_path):
    """THE LOAD-BEARING TEST for the gate's half. Run it, do not read it.

    A planted GUARDS of 3 names and a planted bench/tests of 5 files must print
    3 and 5. A hardcoded echo prints whatever it was written with and fails.
    """
    sand = tmp_path / "repo"
    _plant_tests(sand / "bench" / "tests",
                 {f"test_f{i}.py": 1 for i in range(5)})
    (sand / "bench" / "tests" / "conftest.py").write_text("", encoding="utf-8")
    script = ('GUARDS="bench/tests/test_f0.py\n'
              'bench/tests/test_f1.py\n'
              'bench/tests/test_f2.py"\n') + _scope_fragment() + "\n"
    r = subprocess.run(["/bin/sh", "-c", script], capture_output=True,
                       text=True, cwd=str(sand))
    assert r.returncode == 0, f"the fragment failed: {r.stderr}"
    assert "the gate's 3 guard files of 5 in bench/tests/" in r.stdout, (
        f"the scope line does not count the planted list; got:\n{r.stdout}")
    assert "NOT the suite" in r.stdout


def test_the_scope_arithmetic_moves_with_the_plant(tmp_path):
    """A SECOND plant with different sizes, so one fixture cannot be the answer.

    A single plant can be matched by a constant that happens to agree with it.
    Two plants of different sizes cannot.
    """
    sand = tmp_path / "repo"
    _plant_tests(sand / "bench" / "tests",
                 {f"test_g{i}.py": 1 for i in range(2)})
    script = ('GUARDS="bench/tests/test_g0.py"\n') + _scope_fragment() + "\n"
    r = subprocess.run(["/bin/sh", "-c", script], capture_output=True,
                       text=True, cwd=str(sand))
    assert r.returncode == 0, r.stderr
    assert "the gate's 1 guard files of 2 in bench/tests/" in r.stdout, r.stdout


def test_the_scope_line_names_a_producer_that_exists():
    """A citation to a path that does not exist is worse than no citation."""
    src = GATE.read_text(encoding="utf-8")
    # `\S+` swallowed the shell string's own closing quote, so the captured
    # path was `...py"` and never existed. Stop at a quote or whitespace.
    m = re.search(r'For the test-count share: python3 ([^\s"]+)', src)
    assert m, "the gate no longer names the producer for the test-count share"
    cited = m.group(1)
    assert (REPO / cited).is_file(), f"the gate cites {cited}, which does not exist"


def test_the_scope_line_sits_with_the_boards_own_summary():
    """The addition must be REACHED, which means on the success path.

    The gate prints the board's summary line and the scope line must follow it,
    because a scope statement that appears only on a failure path never reaches
    the reader of a green board -- and a green board is exactly when the frame
    error happens.
    """
    src = GATE.read_text(encoding="utf-8").splitlines()
    scope = next(i for i, l in enumerate(src) if l.startswith("_GUARD_FILES="))
    # THE NEAREST PRECEDING *EXECUTABLE* LINE, not a fixed window. 18 comment
    # lines sit between the 2, so a 6-line window saw only comments and this
    # test failed against its own fixture rather than against the gate. Asking
    # for the nearest executable line is also the stronger property: it proves
    # nothing RUNS between the summary and the scope statement.
    prior = [l for l in src[:scope]
             if l.strip() and not l.lstrip().startswith("#")]
    assert prior, "no executable line precedes the scope arithmetic at all"
    assert "tail -1" in prior[-1], (
        "the scope line no longer immediately follows the board's own summary "
        f"print, so it may have been moved off the success path. The nearest "
        f"preceding executable line is:\n    {prior[-1]}")


# ------------------------------------------------------- the flag costs nothing

def test_the_producer_answers_help_without_collecting():
    """A --help that runs 2 full collections costs about 17 seconds."""
    r = subprocess.run([sys.executable, str(PRODUCER), "--help"],
                       capture_output=True, text=True, cwd=str(REPO),
                       timeout=30)
    assert r.returncode == 0, r.stderr
    assert "usage:" in r.stdout.lower()
    # NOT "tests collected": the docstring --help prints says those 2 words
    # itself, describing what the producer measures, so the first version of
    # this assertion accused the help text of being a measurement. Anchor on a
    # string only the MEASUREMENT emits.
    assert "NEVER RUNS" not in r.stdout, (
        "--help performed the measurement; the flag must be inert")
    assert "share the gate's board covers" not in r.stdout
