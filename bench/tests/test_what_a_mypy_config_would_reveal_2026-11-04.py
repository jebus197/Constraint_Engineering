"""Guard for B130: the size of what a mypy config would reveal.

`scripts/does_mypy_check_anything_2026-11-02.py` deliberately stopped short of
a tree-wide run and said why: "a full run over 201 bench files is a heavy
process of unknown cost". B21 asks the founder to rule on a mypy config and
that ask had no size attached to it.
`scripts/what_a_mypy_config_would_reveal_2026-11-04.py` measures it. The cost
turned out to be about 1 second for 1,713 files in a single invocation, so the
deferral's own stated reason has lapsed.

WHAT THIS GUARD HOLDS, each assertion for a reason rather than for form:

  * the producer answers --help without measuring;
  * it uses ONE combined invocation. The first version ran mypy once per scope
    and summed, which MANUFACTURES import errors: checking `scripts/` alone
    makes `bench` unresolvable. A config runs once over the tree, so a
    per-scope sum measures the method and not the tree;
  * both mypy flags are present. `--exclude bench/logs/` alone is NOT enough
    and that was the first wrong diagnosis: `bench/` has no `__init__.py`, so
    `bench/routing.py` resolves as both `bench.routing` and `routing` and mypy
    aborts with "errors prevented further checking" regardless of the
    exclusion. Both flags are required for the run to CHECK rather than ABORT,
    and this test proves that by running mypy both ways;
  * the buckets partition. Every reported code lands in exactly 1 of
    RESOLUTION, ANNOTATION, POTENTIAL DEFECT or OTHER, so no finding is
    double-counted or silently dropped;
  * the headline is not presented as a defect count. The producer must say
    that the remaining figure is an UPPER BOUND, because 12 findings were read
    of more than 1,000.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PROD = REPO / "scripts" / "what_a_mypy_config_would_reveal_2026-11-04.py"


@pytest.fixture(scope="module")
def mod():
    if not PROD.is_file():
        pytest.fail(f"the producer is not at {PROD}")
    spec = importlib.util.spec_from_file_location("_mypyreveal", PROD)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_mypyreveal"] = m
    spec.loader.exec_module(m)
    return m


class TestTheProducerIsHonestAboutItsMethod:
    def test_help_does_not_measure(self):
        r = subprocess.run([sys.executable, str(PROD), "--help"],
                           capture_output=True, text=True, cwd=str(REPO))
        assert r.returncode == 0, r.stderr[-600:]
        assert "usage:" in r.stdout.lower()
        assert "VERDICT" not in r.stdout

    def test_one_invocation_not_one_per_scope(self, mod):
        """A per-scope sum measures the method, not the tree."""
        src = PROD.read_text(encoding="utf-8")
        assert "def _run(scopes: list[str])" in src, (
            "_run no longer takes a LIST of scopes, so it may have gone back "
            "to one invocation per scope, which manufactures import errors")
        assert "*scopes" in src, "the scopes are not splatted into one command"
        assert re.search(r"for scope in SCOPES:\s*\n\s*if not .*is_dir", src) is None, (
            "a per-scope loop around the mypy call has returned")

    def test_both_flags_are_used(self, mod):
        src = PROD.read_text(encoding="utf-8")
        assert '"--exclude", "bench/logs/"' in src
        assert '"--explicit-package-bases"' in src, (
            "the package-bases flag is gone; without it mypy aborts on "
            "bench/routing.py resolving under 2 module names, and the "
            "exclusion alone does NOT fix that")


class TestTheExclusionAloneIsNotEnough:
    """Proved by running mypy both ways rather than asserting it in prose."""

    def _run(self, *flags: str) -> str:
        """The SUMMARY is deliberately NOT suppressed here.

        The first version passed `--no-error-summary` and then asserted on
        "errors prevented further checking", which is part of the summary. A
        predicate that asserts on output its own flags suppress cannot fail
        for the right reason. Both the collision error and the summary line
        are therefore left visible and both are asserted.
        """
        r = subprocess.run(
            [sys.executable, "-m", "mypy", *flags, "bench/cdsfl_registry/"],
            capture_output=True, text=True, cwd=str(REPO))
        return r.stdout + r.stderr

    def test_exclusion_alone_aborts(self):
        out = self._run("--exclude", "bench/logs/")
        assert "Source file found twice under different module names" in out, (
            "the package-layout collision is gone, so the producer's section 1 "
            "needs remeasuring")
        assert "errors prevented further checking" in out, (
            "the exclusion alone no longer aborts, so the package-layout "
            "collision this producer documents has been fixed elsewhere and "
            "the producer's section 1 needs remeasuring")

    def test_both_flags_check(self):
        out = self._run("--exclude", "bench/logs/", "--explicit-package-bases")
        assert "errors prevented further checking" not in out, (
            "mypy still aborts with both flags, so the producer cannot have "
            "measured anything and its figures are void")


class TestTheBucketsPartition:
    def test_every_bucket_name_is_distinct(self, mod):
        names = {mod._bucket(c) for c in
                 (mod.RESOLUTION | mod.ANNOTATION | mod.POTENTIAL)}
        assert names == {"RESOLUTION", "ANNOTATION", "POTENTIAL DEFECT"}

    def test_the_code_sets_do_not_overlap(self, mod):
        pairs = [("RESOLUTION", mod.RESOLUTION), ("ANNOTATION", mod.ANNOTATION),
                 ("POTENTIAL", mod.POTENTIAL)]
        for i, (an, a) in enumerate(pairs):
            for bn, b in pairs[i + 1:]:
                assert not (a & b), (
                    f"{an} and {bn} share {sorted(a & b)}, so a finding would "
                    f"be counted in whichever bucket is tested first")

    def test_an_unknown_code_falls_to_other(self, mod):
        assert mod._bucket("a-code-mypy-has-never-emitted") == "OTHER", (
            "an unrecognised code is silently dropped rather than reported")


class TestTheHeadlineIsNotPresentedAsADefectCount:
    def test_the_upper_bound_caveat_is_in_the_output(self):
        r = subprocess.run([sys.executable, str(PROD)],
                           capture_output=True, text=True, cwd=str(REPO))
        assert r.returncode == 0, r.stdout[-1200:] + r.stderr[-1200:]
        assert "UPPER BOUND" in r.stdout, (
            "the producer no longer states that the remaining figure is a "
            "bound rather than an estimate, and only 12 findings were read")
        assert "does not say" in r.stdout.lower(), (
            "the producer no longer names what it does not establish")
        m = re.search(r"the importlib module-loading idiom: (\d+) of (\d+)",
                      r.stdout)
        assert m, "the countable idiom is no longer reported"
        k, n = int(m.group(1)), int(m.group(2))
        assert 0 < k < n, f"idiom count {k} of {n} is degenerate"
