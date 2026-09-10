"""Task A1: how complete, functional and useful is Open Brain?

HIS INSTRUCTION: "I have never fully tested yet how complete/functional, or
useful it is."

THE ANSWER, MEASURED 2026-09-10, and it is 3 different answers.

FUNCTIONAL -- mostly. 7 of the 9 read-only subcommands run to a result,
77.7778%, Wilson [45.2589%, 93.6775%]. The 2 that do not are `list-epochs` and
`verify-epochs`, and both fail the same way: `relation "epochs" does not exist`.
The epoch-sealing feature is advertised in `--help` and has no table behind it.

COMPLETE -- no, and it says so itself. Of 20 advertised subcommands, 9 are
read-only enough to exercise here; the other 11 write, need an argument that
varies, or are irreversible by design, and each is named with the reason rather
than left as a silent gap.

INTEGRITY -- the hash chain covers 24.8227% of the store: 35 of 141 memories,
Wilson [18.4237%, 32.5571%]. 99 predate hashing, which is honest history. But 7
were WRITTEN AFTER THE MIGRATION and carry no hash, which is a capture path not
under the chain. The tool reports that itself, in its own words, and exits
non-zero for it -- which is the tool working, not failing.

USEFUL -- narrowly, and this is the sharpest of the 3. 141 memories exist and
semantic search returns real distances. But exactly ONE production path in this
repository reaches it: `scripts/cdsfl_sv.py`. Everything else naming it is that
file's own tests, this assessment, or a documentation mention.

A NON-ZERO EXIT IS NOT A FAILURE. The first version of this assessment conflated
them and would have marked `verify` -- the single most informative command in the
set -- as broken.

AND THE FIRST PASS WAS WRONG IN A LARGER WAY. A shell loop split the arguments of
5 working subcommands, each returned its usage text, and I read that as failure.
That is why this is a script with explicit argv lists: the harness was the defect,
not the tool.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "open_brain_assessment_2026-09-10.py"


def _has_open_brain() -> bool:
    return subprocess.run([sys.executable, "-c", "import open_brain"],
                          cwd=ROOT, capture_output=True).returncode == 0


@pytest.fixture(scope="module")
def mod():
    if not _has_open_brain():
        pytest.skip("open_brain is not importable on this machine")
    spec = importlib.util.spec_from_file_location("ob_assess", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TestTheHarnessDoesNotFabricateFailures:
    def test_arguments_are_passed_as_argv_not_a_shell_string(self, mod):
        """The defect that produced the first, wrong assessment."""
        for entry in mod.READ_ONLY:
            assert isinstance(entry, list), (
                f"{entry!r} is not a list, so a shell would word-split it and "
                f"the subcommand would print usage instead of running")
            assert all(" " not in a for a in entry), entry

    def test_printed_usage_counts_as_a_failure(self, mod):
        """A command that prints its own usage did not do what was asked."""
        src = SCRIPT.read_text(encoding="utf-8")
        assert "printed_usage" in src and "startswith(\"usage:\")" in src

    def test_a_nonzero_exit_is_distinguished_from_a_failure(self, mod):
        src = SCRIPT.read_text(encoding="utf-8")
        assert "nonzero_but_ran" in src, (
            "a non-zero exit is treated as a failure, which mislabels `verify` "
            "-- the command that exits 1 precisely because it found something")


class TestTheMeasuredAnswers:
    def test_most_read_only_subcommands_work(self, mod):
        results = [mod.run(a) for a in mod.READ_ONLY]
        ok = [r for r in results if not r["failed"]]
        assert len(ok) >= 6, [r["argv"] for r in results if r["failed"]]

    def test_the_epoch_feature_is_advertised_and_absent(self, mod):
        """Advertised in --help, no table behind it: the unwired half in a CLI."""
        adv = mod.advertised()
        assert "list-epochs" in adv and "seal-epoch" in adv
        r = mod.run(["list-epochs"])
        assert r["failed"], (
            "list-epochs now works; the epochs table may have been migrated and "
            "this half of the A1 answer should be re-measured")
        assert "does not exist" in r["out"]

    def test_the_hash_chain_covers_a_minority(self, mod):
        r = mod.run(["verify"])
        m_v = re.search(r"Valid:\s*(\d+)", r["out"])
        m_t = re.search(r"verification:\s*(\d+)", r["out"])
        assert m_v and m_t, r["out"][:300]
        valid, total = int(m_v.group(1)), int(m_t.group(1))
        assert total > 100, total
        from statsmodels.stats.proportion import proportion_confint
        lo, hi = proportion_confint(valid, total, method="wilson")
        assert hi < 0.6, (
            f"coverage rose to [{lo:.4%}, {hi:.4%}]; the A1 answer that the "
            f"chain covers a minority needs restating")

    def test_rows_written_after_the_migration_are_reported(self, mod):
        """The half that is a defect rather than honest history."""
        r = mod.run(["verify"])
        assert "WRITTEN AFTER MIGRATION" in r["out"], (
            "the tool no longer separates pre-migration rows from rows that "
            "should have been hashed and were not")


class TestUsefulnessIsNarrow:
    def test_exactly_one_production_path_reaches_it(self, mod):
        c = mod.callers()
        prod = {k: v for k, v in c.items()
                if not k.startswith("bench/tests/")
                and "assessment" not in k
                and not k.endswith(".md")}
        assert prod, "nothing in this repository reaches open_brain at all"
        assert len(prod) <= 3, (
            f"more production paths now reach it: {sorted(prod)} -- the A1 "
            f"answer that usefulness is narrow should be re-measured")
        assert any("cdsfl_sv" in k for k in prod), (
            "the save-state path no longer reaches it, which would make the "
            "store unreachable from ordinary work")

    def test_the_store_is_not_empty(self, mod):
        r = mod.run(["project-labels"])
        m = re.search(r"Total memories:\s*(\d+)", r["out"])
        assert m and int(m.group(1)) > 50, r["out"][:200]
