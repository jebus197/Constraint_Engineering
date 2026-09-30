"""A declared reusable pattern must be reachable from the LIVE PATH, not only from tests.

WHY THIS EXISTS, and it is the second control both free panel seats converged on
independently in the design review of 2026-09-30.

cc2 put it as the narrow buildable form: *"a reachability test -- for every
declared artefact, assert a live-path caller and an executing test."* It named the
defect it catches in the same breath: *"F1 and F4 are the same defect shape: an
intention recorded in prose with nothing mechanical carrying it. The project's own
record (11/13 were additions that did nothing) says this dominates."*

THE MOTIVATING CASE, MEASURED. `bench/tests/fixtures/stem/` holds 5 ground-truth
STEM documents, 29 tagged claims and a runnable `falsifier_template` each, and all
5 discriminate BIDIRECTIONALLY through the runner's own `reverify_falsifier`:
CONFIRMED on the planted claim, REFUTED once corrected. It is a proven prose
falsifier pattern. And `reference_runner_v3.py`, `routing.py`,
`falsifier_verify.py`, `immune_agents.py` and `runner_core.py` mention it **0 times
each**, so nothing on the live review or falsifier-supply path can reach it. Driving
the live `resolve_via_routing` with the pattern removed resolves 0 of 5; with it,
5 of 5, Fisher p = 7.936508e-03. cc2's formulation: *"Routing is a multiplier on
supply -- and here, a multiplier on zero."*

WHY THE EXISTING RATCHET DOES NOT COVER IT, which is why this is an extension and
not a duplicate. `test_additive_standard_2026-09-07.py::test_unreached_config_fields_do_not_grow`
ratchets CONFIG FIELDS whose NAME appears in no test file. The corpus is not a
config field, and its name DOES appear in tests -- 2 test files import it. It is
reached by tests and unreached by the thing that would use it, and a
name-in-tests check scores that as reached. The property this file adds is the
second leg: a LIVE-PATH caller.

IT IS A RATCHET, DELIBERATELY, AND NOT A PASS/FAIL REQUIREMENT. Wiring the corpus
to the live path is a design change the founder has not ruled on, and
`feedback_fixes_hil_only` says a fix is suggested to the human and never applied by
the assistant. So the backlog is PINNED at what it is today: it may shrink, and it
may not grow. A new declared pattern that nothing reaches fails immediately, which
is the direction that bites.
"""
from __future__ import annotations

import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]

#: The modules a REAL review passes through. A pattern unreachable from all of
#: these is unreachable in production however many tests import it.
LIVE_PATH = (
    "bench/reference_runner_v3.py",
    "bench/routing.py",
    "bench/falsifier_verify.py",
    "bench/immune_agents.py",
    "bench/runner_core.py",
)

#: What marks a module as DECLARING a reusable falsifier pattern rather than
#: merely containing test data. Keyed on the artefact's own field name, so the
#: enumeration follows the corpus if it is renamed or moved.
PATTERN_MARKER = "falsifier_template"

#: PINNED 2026-09-30 at the measured value. 1 declared pattern module is reached
#: by tests and by NO live-path module: bench/tests/fixtures/stem/stem_fixtures.py.
#: Lower this when a pattern is wired; never raise it.
UNREACHED_BY_LIVE_PATH_BASELINE = 1

_SKIP_DIRS = ("bench/logs", ".claude/worktrees", "__pycache__", ".git", "node_modules")


def _py_files():
    for p in REPO.rglob("*.py"):
        rel = p.relative_to(REPO).as_posix()
        if any(rel.startswith(d) or f"/{d}/" in f"/{rel}" for d in _SKIP_DIRS):
            continue
        yield p, rel


def _declared_pattern_modules() -> list[str]:
    """Modules that DEFINE a reusable falsifier pattern (they assign the marker)."""
    out = []
    for p, rel in _py_files():
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        # A definition assigns or declares the field; a consumer merely reads it.
        if f"{PATTERN_MARKER}:" in text or f"{PATTERN_MARKER} =" in text:
            out.append(rel)
    return sorted(out)


def _importers(module_stem: str) -> list[str]:
    """Every file naming this module. Simplified 2026-09-30: the first draft
    carried `A and B or A` guarded by a nested `if A`, which reduces to `if A`
    and only obscured what was being asked."""
    out = []
    for p, rel in _py_files():
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if module_stem in text:
            out.append(rel)
    return sorted(set(out))


def _reach(rel: str) -> tuple[list[str], list[str]]:
    """(executing tests that reach it, live-path modules that reach it)."""
    stem = pathlib.Path(rel).stem
    imp = [r for r in _importers(stem) if r != rel]
    tests = [r for r in imp
             if r.startswith("bench/tests/") and pathlib.Path(r).name.startswith("test_")]
    live = [r for r in imp if r in LIVE_PATH]
    return tests, live


def _unreached_by_live_path() -> list[str]:
    return [rel for rel in _declared_pattern_modules() if not _reach(rel)[1]]


class TestTheEnumerationIsReal:
    """A ratchet over an empty set passes forever. Checked first, on purpose."""

    def test_at_least_one_declared_pattern_module_is_found(self):
        mods = _declared_pattern_modules()
        assert mods, (
            f"no module declares a {PATTERN_MARKER!r}, so this file is measuring "
            f"nothing. Either the marker was renamed -- update PATTERN_MARKER -- "
            f"or the corpus was deleted, which is a removal needing a measurement.")

    def test_every_live_path_module_exists(self):
        missing = [m for m in LIVE_PATH if not (REPO / m).is_file()]
        assert not missing, (
            f"LIVE_PATH names {missing}, which are not in the tree. A path list "
            f"that points at nothing cannot find an unreached artefact.")


class TestDeclaredPatternsAreReachable:
    def test_the_unreached_backlog_does_not_grow(self):
        unreached = _unreached_by_live_path()
        assert len(unreached) <= UNREACHED_BY_LIVE_PATH_BASELINE, (
            f"{len(unreached)} declared pattern module(s) are reachable from NO "
            f"live-path module, up from the pinned "
            f"{UNREACHED_BY_LIVE_PATH_BASELINE}: {unreached}. A proven pattern "
            f"nothing on the live path can reach is an addition that does nothing "
            f"-- wire it to a live-path caller, or lower the pin if you wired one.")

    def test_the_pin_is_honest(self):
        """A pin above the real count silently licences growth."""
        measured = len(_unreached_by_live_path())
        assert UNREACHED_BY_LIVE_PATH_BASELINE == measured, (
            f"the pin says {UNREACHED_BY_LIVE_PATH_BASELINE} and the measurement "
            f"says {measured}. If the backlog shrank, lower the pin so the ratchet "
            f"keeps biting; if it grew, the test above has already said so.")

    def test_every_declared_pattern_is_at_least_exercised_by_a_test(self):
        """The first leg of cc2's control, and this one is a hard requirement.

        A pattern with no live-path caller is a wiring gap awaiting a ruling. A
        pattern with no EXECUTING TEST is unverified machinery, which needs no
        ruling to be wrong.
        """
        naked = [rel for rel in _declared_pattern_modules() if not _reach(rel)[0]]
        assert not naked, (
            f"{naked} declare a reusable falsifier pattern that NO test file "
            f"exercises. Nothing establishes that the pattern works, so nothing "
            f"would notice if it stopped.")


class TestTheMotivatingCaseIsStillTheMotivatingCase:
    """If the corpus ever becomes live-reachable this class says so out loud.

    Recorded rather than asserted as a permanent truth: the point of the ratchet
    is that this changes.
    """

    def test_the_stem_corpus_state_is_recorded(self):
        target = "bench/tests/fixtures/stem/stem_fixtures.py"
        if target not in _declared_pattern_modules():
            return  # moved or renamed; the enumeration tests above cover that
        tests, live = _reach(target)
        assert tests, f"{target} is exercised by no test"
        if live:
            raise AssertionError(
                f"GOOD NEWS, AND THIS TEST IS NOW STALE: {target} is reached by "
                f"live-path module(s) {live}. Lower "
                f"UNREACHED_BY_LIVE_PATH_BASELINE to "
                f"{len(_unreached_by_live_path())} and delete this class.")
