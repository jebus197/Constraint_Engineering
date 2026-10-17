"""A `getattr` fallback for a scope must be the declared default, not a literal.

FOUND 2026-10-17 BY READING THE TWO SIDES TOGETHER, which is the only way this
class of defect shows: each side is individually correct and they disagree.

`RunnerConfig.fingerprint_scope` declares `"experiment"`, on his ruling that
*"The fingerprints should be recomputed in the first/blind run of any
experiment"*. The runner then read `getattr(cfg, "fingerprint_scope",
"persist")`. So a config object missing the field would silently take `persist`,
and the run would split payloads against a prior experiment's
465,206-character ceiling -- effective 418,686 -- while believing it had
re-measured. Measured through the live routing predicate: under `experiment` the
ceiling is 80,001, which sits inside what the seats have actually handled
recently, 70,045 to 95,045; under `persist` it is 418,686, which is 4.4x to 6.0x
above the top of that range.

THE TEST FOR IT REPEATED THE SAME WRONG LITERAL.
`bench/tests/test_experiment_scoped_state_2026-10-16.py` passed
`getattr(cfg, "fingerprint_scope", "persist")` into the loader, so it mirrored
the defect rather than catching it. Both now call `scope_default`, which reads
the dataclass field, so the 2 cannot disagree by construction.

`immune_memory_scope` was already consistent -- declared `persist`, fallback
`persist`, on his separate ruling that immune memory persists between
experiments by default. It is asserted here anyway, because the property is
"every scope fallback agrees with its declared default", and a guard that checks
only the field already known to be broken cannot catch the next one.
"""
from __future__ import annotations

import dataclasses
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
RUNNER = REPO / "bench" / "reference_runner_v3.py"

#: His rulings, so a changed default is visible as a changed ruling.
EXPECTED = {
    "fingerprint_scope": "experiment",
    "immune_memory_scope": "persist",
}


@pytest.fixture(scope="module")
def runner():
    import bench.reference_runner_v3 as mod
    return mod


def test_the_declared_defaults_are_his_rulings(runner):
    for field, want in EXPECTED.items():
        assert runner.scope_default(field) == want, (
            f"RunnerConfig.{field} declares "
            f"{runner.scope_default(field)!r}, not {want!r}. If his ruling "
            f"changed, change EXPECTED here and say where he said so.")


def test_scope_default_reads_the_dataclass_rather_than_a_table(runner):
    """It must track the dataclass, not carry a third copy of the defaults."""
    declared = {f.name: f.default
                for f in dataclasses.fields(runner.RunnerConfig)}
    for field in EXPECTED:
        assert runner.scope_default(field) == str(declared[field])


def test_an_unknown_field_raises_rather_than_guessing(runner):
    """A silent default is how the defect existed; it may not be reintroduced."""
    with pytest.raises(KeyError):
        runner.scope_default("no_such_scope_field")


def test_no_scope_fallback_is_a_hand_typed_literal():
    """THE RATCHET. Every `getattr(cfg, "<x>_scope", ...)` must derive.

    Scanned across the runner's source because the property is about the whole
    file rather than one call site, and a new call site typed by hand is exactly
    how the 2 defaults came to disagree. The executing assertions above cover
    the behaviour of the 2 that exist today.
    """
    # COMMENTS ARE STRIPPED FIRST, and this is not a convenience. The first
    # version of this scan went red on the repair's OWN COMMENT, which quotes
    # `getattr(cfg, "fingerprint_scope", "persist")` to record what used to be
    # there. A source-text scan that reads its own documentation as code
    # reports a defect that was fixed in the same commit -- so the property is
    # about live code, and the comment explaining the fix must not count as a
    # breach of it.
    bad = []
    for n, line in enumerate(RUNNER.read_text(encoding="utf-8").splitlines(), 1):
        code = line.split("#", 1)[0]
        for m in re.finditer(
                r'getattr\(\s*cfg\s*,\s*"(\w*scope\w*)"\s*,\s*("(?:[^"]*)")\s*\)',
                code):
            bad.append((m.group(1), m.group(2), n))
    assert not bad, (
        "these scope fallbacks are typed literals and can contradict the "
        "declared default; pass scope_default(<field>) instead:\n"
        + "\n".join(f"    line {ln}: {field} falls back to {lit}"
                    for field, lit, ln in bad))


def test_the_experiment_scope_really_lowers_the_routing_ceiling(runner):
    """The ruling must have an effect, or honouring it is decoration.

    Set through the SAME binding the runner uses. An earlier probe set the
    scope on a SECOND copy of the module -- `run_exp17_immune` is reachable
    both as `bench.run_exp17_immune` and bare, with separate globals -- and
    concluded the repair did not work. It does.
    """
    class _Cfg:
        pre_decompose_models = ()

    class _Mgr:
        config = _Cfg()

    def ceiling() -> int:
        lo, hi = 0, 4_000_000
        for _ in range(48):
            mid = (lo + hi) // 2
            if runner._decomposition_is_futile("CC2", _Mgr(), mid):
                hi = mid
            else:
                lo = mid
        return hi

    try:
        runner.set_fingerprint_scope("persist")
        inherited = ceiling()
        runner.set_fingerprint_scope("experiment")
        measured = ceiling()
    finally:
        runner.set_fingerprint_scope("persist")
    assert measured < inherited, (
        f"the experiment scope did not lower the ceiling: {inherited:,} under "
        f"persist, {measured:,} under experiment. His ruling that fingerprints "
        f"are recomputed in the blind round is not reaching the routing "
        f"decision.")
    assert measured <= runner.DECOMPOSE_HARD_FLOOR_CHARS + 1
