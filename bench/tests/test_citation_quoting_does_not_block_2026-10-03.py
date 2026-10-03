#!/usr/bin/env python3
"""A finding may not be discarded for how it QUOTED a path.

THE DEFECT, OBSERVED LIVE AND MEASURED. The skin barrier verifies a finding's
`file:line` citation before the finding is allowed through. Its pattern captures
`(\\S+\\.\\w+)`, and `\\S` is any non-whitespace character -- so a model writing a
path the way models write paths, in backticks, has the backtick captured INTO
the path. All 3 resolution steps then fail: the exact match misses, the basename
match misses because `os.path.basename` cannot strip a backtick, and the suffix
match misses because no source path ENDS WITH a backtick-prefixed name.

Measured in study run 1 of 2026-10-03 over its first 2 rounds: 16 findings
blocked, every one for "Cited file not found", and 12 of the 16 cited THE RUN'S
OWN TARGET by its bare basename in backticks. The run was stopped on that
evidence, because a barrier discarding findings for their quoting starves the
finding supply -- the very thing the programme of study exists to measure.

THE ASYMMETRY THAT HID IT. With a directory present, `os.path.basename` strips
the backtick along with the directory, so `` `bench/evaluate.py `` resolved
while `` `evaluate.py `` did not. The pattern therefore looked harmless on every
citation that happened to carry a directory.

WHAT THESE TESTS HOLD. The 6 citation shapes the run actually produced must all
resolve; a path outside the declared source set must STILL be refused, so the
check does not become the file-existence oracle E31-16 forbids; and the
ambiguous-basename guard must keep refusing an ambiguous name.
"""
from __future__ import annotations

import os
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
BARRIER = REPO / "bench" / "immune_agents.py"

#: The barrier's own capture pattern, read from the module so a change there
#: cannot leave this test asserting about a pattern that no longer exists.
_SRC = BARRIER.read_text(encoding="utf-8")


def _strip_set() -> str:
    """The characters the barrier strips, taken from the barrier itself."""
    mt = re.search(r'cited_file_raw = \(cited_file_raw or ""\)\.strip\((.+?)\)\n',
                   _SRC)
    assert mt, "the quoting strip is gone from the barrier"
    return eval(mt.group(1))            # noqa: S307 - a literal from our own file


def _resolve(raw: str, source_set: set[str], ambiguous=frozenset()):
    """The barrier's 3-step resolution, with its own strip applied first."""
    raw = (raw or "").strip(_strip_set())
    basenames: dict[str, str] = {}
    for p in source_set:
        basenames.setdefault(os.path.basename(p), p)
    if raw in source_set:
        return raw
    b = os.path.basename(raw)
    if b in basenames and b not in ambiguous:
        return basenames[b]
    # The suffix fallback is refused for a BARE name whose basename is
    # ambiguous -- otherwise it overrides the guard above, which is the defect
    # `test_an_ambiguous_basename_is_still_refused` found on 2026-10-03.
    if "/" in raw or os.sep in raw or b not in ambiguous:
        for p in source_set:
            if p.endswith(raw):
                return p
    return ""


SOURCES = {"bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md", "bench/evaluate.py",
           "bench/run_round_robin.py", "bench/run_benchmark.py",
           "bench/report.py"}

CITE = re.compile(r'(\S+\.\w+)(?::|\s+line\s+)(\d+)')


def test_the_barrier_still_strips_quoting():
    assert "`" in _strip_set(), (
        "the barrier no longer strips the backtick, so a path written in "
        "markdown is captured with its quoting and cannot resolve")


@pytest.mark.parametrize("text,expect", [
    ("`BUILD_BOT_TEST_BENCH_FIX_SPEC.md:42`", "bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md"),
    ("(`BUILD_BOT_TEST_BENCH_FIX_SPEC.md:42)", "bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md"),
    ("`run_benchmark.py:17`", "bench/run_benchmark.py"),
    ("`report.py:3`", "bench/report.py"),
    ("`evaluate.py:88`", "bench/evaluate.py"),
    ("`bench/run_round_robin.py:17`", "bench/run_round_robin.py"),
    ("see bench/evaluate.py line 9", "bench/evaluate.py"),
    ("plain BUILD_BOT_TEST_BENCH_FIX_SPEC.md:1 here",
     "bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md"),
])
def test_every_shape_the_run_produced_now_resolves(text, expect):
    found = CITE.findall(text)
    assert found, f"no citation was captured at all from {text!r}"
    raw, _line = found[0]
    assert _resolve(raw, SOURCES) == expect, (
        f"{text!r} still fails to resolve; a finding would be discarded for "
        f"how it quoted its path")


@pytest.mark.parametrize("text,why", [
    ("`no_such_file_anywhere.py:9`", "the file is in no source set"),
    ("`/tmp/elsewhere.py:1`", "outside the declared sources"),
])
def test_a_path_outside_the_source_set_is_still_refused(text, why):
    """ANTI-VACUITY: stripping quoting must not reopen the file-existence oracle."""
    raw, _line = CITE.findall(text)[0]
    assert _resolve(raw, SOURCES) == "", (
        f"{text!r} resolved although {why}; the citation check has become a "
        f"file-existence oracle, which E31-16 forbids")


def test_an_ambiguous_basename_is_still_refused():
    """The Bug#69 guard must survive the strip."""
    sources = {"bench/a/engine.py", "bench/b/engine.py"}
    raw, _line = CITE.findall("`engine.py:4`")[0]
    assert _resolve(raw, sources, ambiguous={"engine.py"}) == "", (
        "an ambiguous basename resolved, so a citation could be credited to "
        "the wrong file")
