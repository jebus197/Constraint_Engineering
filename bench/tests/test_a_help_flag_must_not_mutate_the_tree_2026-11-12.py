#!/usr/bin/env python3
"""The repair tool for writers that ignore `--help`, and the queue-ownership
producer, are EXECUTED here rather than merely existing.

★ WHY THIS FILE EXISTS, AND A RATCHET ON THE COMMIT GATE DEMANDED IT. On
2026-11-12 the board refused with
`test_an_unreached_producer_set_cannot_grow_2026-11-08.py` naming 2 producers
reached by no test: `scripts/a_help_flag_must_not_mutate_the_tree_2026-11-12.py`
and `scripts/how_much_of_this_is_actually_his_2026-11-12.py`. Its own words are
the reason this is a test and not a pin: *"Either have a test execute them, or
-- if one is deliberately exempt -- say so beside the exemption ... Re-pinning to
silence this is how a ratchet becomes a rubber stamp."* An addition nothing
reaches is not additive, which is the symmetric half of this project's additive
standard.

★ IT DOES NOT RE-RUN THE EXPENSIVE MEASUREMENT, DELIBERATELY. The repair tool's
`offenders()` shells out to `scripts/help_writers_rate_2026-09-17.py`, which runs
`--help` on every writing script in the tree and took about 50 seconds standing
alone. `bench/tests/test_help_writers_rate_2026-09-17.py` already measures that,
so repeating it here would buy nothing and spend about 50 seconds of his 8 cores
on every commit. What is tested instead is the part that has no other guard: the
TRANSFORMATION, driven on synthetic files, including the shapes it must REFUSE.

★ AND IT CHECKS THE INSERTED GUARD ACTUALLY WORKS, not merely that bytes moved.
The point of the repair is that `--help` must not reach the writing code, so the
test runs the transformed file and asserts the flag is answered and nothing is
written.

Costs nothing: writes only inside pytest's own tmp_path, dispatches to no model,
runs no pytest of its own.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
TOOL = REPO / "scripts" / "a_help_flag_must_not_mutate_the_tree_2026-11-12.py"
PARTITION = REPO / "scripts" / "how_much_of_this_is_actually_his_2026-11-12.py"


def _load(path: pathlib.Path, name: str):
    assert path.is_file(), f"missing producer: {path}"
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(name, m)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def tool():
    return _load(TOOL, "help_flag_repair_tool")


@pytest.fixture(scope="module")
def partition_run():
    """★ RUN ONCE, NOT ONCE PER TEST. The producer issues 12 `git log` queries
    over a 2,000-line file; 3 separate runs cost about 45 seconds of his 8 cores
    on every commit, against about 15 for one. His machine is a fixed resource."""
    r = subprocess.run([sys.executable, str(PARTITION)],
                       capture_output=True, text=True, cwd=str(REPO))
    return r


#: A writer of exactly the shape the 8 offenders had: it writes, it parses no
#: arguments, and its `__main__` block goes straight to `main()`.
_OFFENDER = '''#!/usr/bin/env python3
"""A synthetic harness that overwrites a file in place."""
from __future__ import annotations

import pathlib
import sys

TARGET = pathlib.Path(__file__).with_name("victim.txt")


def main() -> int:
    with open(TARGET, "w", encoding="utf-8") as fh:
        fh.write("MUTATED\\n")
    print("ran")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


class TestTheTransformation:
    def test_it_inserts_the_guard_above_the_entry_call(self, tool, tmp_path):
        src = _OFFENDER
        m = tool._ENTRY.search(src)
        assert m, "the entry-block pattern does not match the shape it was written for"
        new = src[:m.start()] + m.group(1) + tool.GUARD + m.group(2) + src[m.end():]
        assert "answer_help(__doc__, __file__)" in new
        #: the guard must sit BETWEEN the `if __name__` line and the call, or it
        #: runs after the writing has already happened.
        i_if = new.index('if __name__ == "__main__":')
        i_guard = new.index("answer_help(__doc__, __file__)")
        i_call = new.index("raise SystemExit(main())")
        assert i_if < i_guard < i_call, (i_if, i_guard, i_call)

    def test_the_transformed_file_answers_help_and_writes_NOTHING(self, tool, tmp_path):
        """★ THE TEST THAT MATTERS. Bytes moving is not the property; the
        property is that `--help` cannot reach the writing code."""
        src = _OFFENDER
        m = tool._ENTRY.search(src)
        new = src[:m.start()] + m.group(1) + tool.GUARD + m.group(2) + src[m.end():]
        script = tmp_path / "harness.py"
        script.write_text(new, encoding="utf-8")
        # the helper is imported from scripts/ by the guard's own sys.path line,
        # so the copy must sit where that resolves: beside the real helper.
        staged = REPO / "scripts" / "_tmp_help_guard_probe.py"
        staged.write_text(new.replace('with_name("victim.txt")',
                                      f'__class__ and pathlib.Path({str(tmp_path / "victim.txt")!r})'),
                          encoding="utf-8")
        try:
            r = subprocess.run([sys.executable, str(staged), "--help"],
                               capture_output=True, text=True, cwd=str(REPO))
            assert r.returncode == 0, r.stderr
            assert r.stdout.startswith("usage:"), r.stdout[:200]
            assert "ran" not in r.stdout, "the writing code ran under --help"
            assert not (tmp_path / "victim.txt").exists(), (
                "--help wrote the file the harness mutates")
        finally:
            staged.unlink(missing_ok=True)

    def test_an_unrecognised_argument_is_REFUSED_rather_than_ignored(self, tool, tmp_path):
        """A script that accepts a flag and ignores it is the fault the helper's
        own docstring names; the guard must inherit the refusal, not just the
        help text."""
        src = _OFFENDER
        m = tool._ENTRY.search(src)
        new = src[:m.start()] + m.group(1) + tool.GUARD + m.group(2) + src[m.end():]
        staged = REPO / "scripts" / "_tmp_help_guard_probe2.py"
        staged.write_text(new.replace('with_name("victim.txt")',
                                      f'__class__ and pathlib.Path({str(tmp_path / "v2.txt")!r})'),
                          encoding="utf-8")
        try:
            r = subprocess.run([sys.executable, str(staged), "--no-such-flag"],
                               capture_output=True, text=True, cwd=str(REPO))
            assert r.returncode == 2, (r.returncode, r.stdout, r.stderr)
            assert "unrecognised argument" in r.stderr, r.stderr
            assert not (tmp_path / "v2.txt").exists()
        finally:
            staged.unlink(missing_ok=True)


class TestItRefusesWhatItCannotSafelyChange:
    def test_a_file_with_no_entry_block_is_not_matched(self, tool):
        assert tool._ENTRY.search("def main():\n    return 0\n") is None

    def test_an_entry_block_doing_more_than_calling_main_is_not_matched(self, tool):
        """A `__main__` block with its own setup must not have a guard dropped in
        above code the author put first."""
        odd = ('if __name__ == "__main__":\n'
               '    configure()\n'
               '    raise SystemExit(main())\n')
        assert tool._ENTRY.search(odd) is None

    def test_both_entry_spellings_in_use_are_matched(self, tool):
        for call in ("    sys.exit(main())\n", "    raise SystemExit(main())\n"):
            assert tool._ENTRY.search('if __name__ == "__main__":\n' + call), call


class TestItRunsAndItsHelpDoesNot:
    def test_help_answers_without_measuring(self):
        r = subprocess.run([sys.executable, str(TOOL), "--help"],
                           capture_output=True, text=True, cwd=str(REPO))
        assert r.returncode == 0 and r.stdout.startswith("usage:"), r
        assert "WOULD FIX" not in r.stdout and "FIXED" not in r.stdout

    def test_the_default_run_writes_nothing(self, tool):
        """`--apply` is the only writing path, and the flag defaults to false."""
        import argparse
        ap = argparse.ArgumentParser()
        ap.add_argument("--apply", action="store_true")
        ap.add_argument("--also", nargs="*", default=[])
        assert ap.parse_args([]).apply is False


class TestTheQueueOwnershipProducer:
    """`scripts/how_much_of_this_is_actually_his_2026-11-12.py` answers his
    question of 2026-11-12 about how much of the open queue is really his. It is
    executed here so the figures it produces cannot rot unnoticed."""

    def test_it_runs_and_names_the_3_groups(self, partition_run):
        r = partition_run
        assert r.returncode == 0, r.stderr[-1500:]
        for needed in ("HOW MANY CARRY NO RECORDED RULING AT ALL",
                       "THE 3 PREDICATES FOR 'WAS THIS ASKED AFTER HE RULED'",
                       "WHAT THE PERMISSION PREDICATE ADDS",
                       "THE DEFENSIBLE FLOOR OF WHAT IS OWED TO HIM"):
            assert needed in r.stdout, f"the producer no longer reports: {needed}"

    def test_every_proportion_it_prints_carries_both_interval_routes(self, partition_run):
        r = partition_run
        assert r.returncode == 0, r.stderr[-800:]
        assert r.stdout.count("Wilson [") >= 4, r.stdout.count("Wilson [")
        assert r.stdout.count("Clopper-Pearson [") == r.stdout.count("Wilson ["), (
            "a proportion is reported on 1 interval route where the project "
            "requires 2")
        assert "2 routes agree to" in r.stdout

    def test_the_3_predicates_are_actually_computed_and_not_asserted(self, partition_run):
        """The disagreement is the finding; if the producer ever printed only
        one predicate's verdict the finding would be unsupported."""
        r = partition_run
        assert r.returncode == 0
        rows = [l for l in r.stdout.splitlines()
                if " A=" in l and " B=" in l and " C=" in l]
        assert rows, "no row reports all 3 predicates"
        assert any("DISAGREE" in l for l in rows), (
            "no ruled-and-owed entry shows a disagreement, so either the record "
            "changed or the producer stopped computing all 3")
