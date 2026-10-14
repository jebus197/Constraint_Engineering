"""Task 2.2, panel round 16: "28 of 28" must come out of the named producer.

THE DEFECT. `scripts/missing_falsifiers_2026-09-10.py` is the instrument task 2.2
names for its population, and it reproduced every population figure (817, 789,
28, 28 of 440) while still ending "ALREADY WRITTEN: 1 / REMAINING: 27". Its
`done` was a typed set holding only exp47 C0053, so after all 28 falsifiers were
written nothing committed printed "28 of 28".

THE FIX. Each falsifier test file declares a module-level `COVERS` set of
(run directory, canonical id) pairs, and the script derives ALREADY WRITTEN and
REMAINING from those declarations. This file executes the script and requires
the declared union to EQUAL the population, in both directions: a finding with
no declaration is a missing falsifier, and a declaration with no finding is a
mistyped run or id.

WHAT THIS DOES NOT PROVE. That the tests in a declaring file actually falsify the
finding they name. That link is the adjudication inside each file; this file
proves the count is derived from the files rather than typed beside them.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "missing_falsifiers_2026-09-10.py"


def _load(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


#: ★ THESE FIGURES WERE REPLACED, NOT RELAXED, 2026-10-14.
#:
#: They used to read `len(population) == 28`, `7` runs and `REMAINING: 0`. All 3
#: were TRUE of the population the script surveyed and FALSE of the project,
#: because both of `scripts/missing_falsifiers_2026-09-10.py`'s glob sites read
#: `exp*/runner_state.json`. 5 run directories were therefore invisible:
#: `commissioning_arm1_panel_*`, `commissioning_arm4_prose_*` (2 runs),
#: `sim45_memory_*` (2 runs) and `study_run1_2026-10-03_*` -- hiding **11 of 39
#: UNTOOLABLE rows, 28.2051%, Wilson [16.5435%, 43.7753%]**, among them a
#: programme-of-study run and the A19 prose commissioning arm.
#:
#: So "REMAINING: 0" was a CONFIDENT ZERO PRODUCED BY A NARROW GLOB -- the same
#: shape as the Exp 48 forensic scan that globbed `r*_*.json` and reported CLEAN.
#: Found by cc2 in the panel of 2026-10-14, reproduced independently, and the
#: glob widened to `**` with harvest copies excluded.
#:
#: WHAT THE HONEST POPULATION IS: **44 findings across 13 runs, 28 covered =
#: 63.6364%, Wilson [48.8664%, 76.2165%]** (statsmodels and mpmath agreeing
#: exactly), **0 stale declarations** -- every COVERS entry is real, so the gap
#: is uncovered findings and not mis-declaration.
#:
#: AND IT IS A RATCHET, NOT AN EQUALITY. The 16 uncovered are named below and the
#: set MAY SHRINK but MUST NOT GROW. An equality assertion on 16 would make
#: writing the 17th falsifier fail the suite; an inequality alone would let the
#: backlog grow unnoticed. Naming them is what stops either.
#:
#: 6 of the 16 are the SAME findings
#: `scripts/falsifier_untoolable_is_stale_error_2026-09-22.py` already documents
#: as carrying stale UNTOOLABLE labels: arm4_prose C0002, C0005, C0006, C0011,
#: C0012, C0015. The 2 findings converge on one run.
EXPECTED_REMAINING = frozenset({
    ("commissioning_arm1_panel_20260929T214647Z", "C0053"),
    ("commissioning_arm4_prose_20260922T053349Z", "C0002"),
    ("commissioning_arm4_prose_20260922T053349Z", "C0005"),
    ("commissioning_arm4_prose_20260922T053349Z", "C0006"),
    ("commissioning_arm4_prose_20260922T053349Z", "C0011"),
    ("commissioning_arm4_prose_20260922T053349Z", "C0012"),
    ("commissioning_arm4_prose_20260922T053349Z", "C0015"),
    ("commissioning_arm4_prose_20260930T064044Z", "C0004"),
    ("commissioning_arm4_prose_20260930T064044Z", "C0005"),
    ("commissioning_arm4_prose_20260930T064044Z", "C0013"),
    ("commissioning_arm4_prose_20260930T064044Z", "C0014"),
    ("sim45_memory_20260830T161215Z", "C0004"),
    ("sim45_memory_20260830T161215Z", "C0006"),
    ("sim45_memory_20260908T033012Z", "C0050"),
    ("study_run1_2026-10-03_20261003T083519Z", "C0002"),
    ("study_run1_2026-10-03_20261003T083519Z", "C0009"),
})

POPULATION_SIZE = 44
POPULATION_RUNS = 13
COVERED = 28

@pytest.fixture(scope="module")
def mf():
    return _load(SCRIPT, "missing_falsifiers_2026_09_17")


@pytest.fixture(scope="module")
def population(mf):
    post = mf.survey()["post"]
    if not post:
        pytest.skip("no post-mechanism run records in this clone")
    return post


class TestTheCountIsDerivedFromTheTests:
    def test_the_population_is_the_one_the_entry_names(self, population):
        """44 findings in 13 runs: EVERY run, not just the `exp*` ones."""
        assert len(population) == POPULATION_SIZE, len(population)
        assert len({r["run"] for r in population}) == POPULATION_RUNS, \
            sorted({r["run"] for r in population})

    def test_every_finding_is_declared_and_every_declaration_is_a_finding(
            self, mf, population):
        covers = mf.declared_covers()
        written, remaining, stale = mf.coverage(population, covers)
        # RATCHET: the uncovered set may shrink, never grow.
        grew = sorted(set(remaining) - EXPECTED_REMAINING)
        assert not grew, (
            f"{len(grew)} finding(s) became uncovered: {grew}. Either a "
            f"falsifier's COVERS declaration was lost, or a new run archived "
            f"findings nothing adjudicates.")
        assert stale == set(), f"declared but not in the population: {sorted(stale)}"
        assert len(written) == COVERED, len(written)
        assert written | set(remaining) == {(r["run"], r["id"]) for r in population}

    def test_the_script_prints_the_honest_written_and_remaining(self, mf, population):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = mf.main()
        out = buf.getvalue()
        assert rc == 0
        assert f"ALREADY WRITTEN: {COVERED} " in out, out[-800:]
        assert f"REMAINING       : {len(EXPECTED_REMAINING)}\n" in out, out[-800:]
        assert "DECLARED BUT NOT IN THE POPULATION" not in out

    def test_each_declaring_file_holds_tests_and_imports_to_the_same_set(self, mf):
        """2 forms of the declaration, compared: the literal the script reads by
        AST, and the object Python builds when the file is imported. A file that
        rebinds COVERS later, or declares it with no test beside it, fails here."""
        covers = mf.declared_covers()
        by_file: dict[str, set] = {}
        for pair, files in covers.items():
            for f in files:
                by_file.setdefault(f, set()).add(pair)
        assert len(by_file) == 9, sorted(by_file)
        for rel, pairs in sorted(by_file.items()):
            mod = _load(ROOT / rel, "covers_" + pathlib.Path(rel).stem.replace("-", "_"))
            assert mod.COVERS == pairs, rel
            n_tests = sum(
                1 for name, obj in vars(mod).items()
                if (name.startswith("test_") and callable(obj))
                or (name.startswith("Test") and isinstance(obj, type)
                    and any(a.startswith("test_") for a in vars(obj))))
            assert n_tests > 0, f"{rel} declares COVERS but holds no test"

    def test_the_exp53_declaration_matches_its_adjudication(self, mf):
        """The exp53 file adjudicates 11 findings; C0001 appears as C0001a and
        C0001b for its 2 runs. The declaration must name the same 11."""
        mod = _load(ROOT / "bench" / "tests" /
                    "test_falsifier_exp53_zero_plant_2026-09-10.py", "covers_exp53_adj")
        assert len(mod.COVERS) == len(mod.ADJUDICATION) == 11
        assert ({fid for _, fid in mod.COVERS}
                == {k.rstrip("ab") for k in mod.ADJUDICATION})


class TestTheCheckCanFail:
    def test_removing_one_declaration_leaves_one_more_remaining(self, mf, population):
        """RE-BASED 2026-10-14 on the honest population, not weakened.

        It asserted `remaining == {dropped}` and `len(written) == 27`, both of
        which held only while the narrow glob made the uncovered set empty. The
        PROPERTY being checked is unchanged and is now stated as a DELTA, which
        is what it always meant: dropping 1 declaration must move exactly that
        finding from covered to uncovered.
        """
        covers = dict(mf.declared_covers())
        dropped = sorted(covers)[0]
        del covers[dropped]
        written, remaining, stale = mf.coverage(population, covers)
        assert dropped in remaining, dropped
        assert set(remaining) == EXPECTED_REMAINING | {dropped}
        assert len(written) == COVERED - 1, len(written)
        assert set(covers) != {(r["run"], r["id"]) for r in population}

    def test_a_mistyped_run_is_reported_stale(self, mf, population):
        """Same re-basing: the typo's own pair becomes uncovered AND stale, on
        top of the known backlog rather than against an empty one."""
        covers = dict(mf.declared_covers())
        run, fid = sorted(covers)[0]
        covers[(run + "_typo", fid)] = covers.pop((run, fid))
        _, remaining, stale = mf.coverage(population, covers)
        assert set(remaining) == EXPECTED_REMAINING | {(run, fid)}
        assert stale == {(run + "_typo", fid)}

    def test_the_reader_finds_a_declaration_and_refuses_a_non_literal(
            self, mf, tmp_path):
        (tmp_path / "test_a.py").write_text(
            'COVERS = {("run_x", "C0001"), ("run_y", "C0001")}\n'
            "def test_it():\n    pass\n", encoding="utf-8")
        (tmp_path / "test_b.py").write_text("X = 1\n", encoding="utf-8")
        got = mf.declared_covers(tmp_path)
        assert set(got) == {("run_x", "C0001"), ("run_y", "C0001")}
        (tmp_path / "test_c.py").write_text(
            "COVERS = set(PAIRS)\n", encoding="utf-8")
        with pytest.raises(ValueError, match="not a literal"):
            mf.declared_covers(tmp_path)
