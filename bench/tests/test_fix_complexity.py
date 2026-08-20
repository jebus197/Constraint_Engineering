"""Tests for the fix-complexity measurer (nu's missing input).

The appendix defines nu as a complexity measure - "localised one-line changes
have low nu, changes to shared interfaces have higher nu" - and the runner
supplies it from two constants. These tests pin the ORDERING the appendix
describes. They do not pin a probability, because the measurer deliberately
returns a percentile rank rather than one.
"""
import pathlib


from bench.dm._fix_complexity import (
    complexity_index,
    fix_complexity_features,
    parse_fix_blocks,
    raw_complexity,
)

ONE_LINE = """<<<< SEARCH bench/foo.py
    x = 1
==== REPLACE
    x = 2
>>>>"""

SIGNATURE_CHANGE = """<<<< SEARCH bench/foo.py
def compute(a, b):
    return a + b
==== REPLACE
def compute(a, b, c=None, *, strict=False):
    return a + b + (c or 0)
>>>>"""

TWO_FILES = """<<<< SEARCH bench/foo.py
    x = 1
==== REPLACE
    x = 2
>>>>
<<<< SEARCH bench/bar.py
    y = 3
==== REPLACE
    y = 4
>>>>"""


class TestParsing:
    def test_parses_a_single_block(self):
        b = parse_fix_blocks(ONE_LINE)
        assert len(b) == 1
        assert b[0]["path"] == "bench/foo.py"
        assert "x = 1" in b[0]["old"] and "x = 2" in b[0]["new"]

    def test_parses_multiple_blocks(self):
        assert len(parse_fix_blocks(TWO_FILES)) == 2

    def test_the_OLD_form_without_a_path_is_accepted(self):
        # The same emitter produces `<<<< OLD` when it has no file hint.
        assert len(parse_fix_blocks("<<<< OLD\na\n====\nb\n>>>>")) == 1

    def test_text_with_no_block_yields_nothing(self):
        assert parse_fix_blocks("no fix here at all") == []


class TestFeatures:
    def test_counts_lines_and_paths(self):
        f = fix_complexity_features(TWO_FILES)
        assert f["blocks"] == 2
        assert f["distinct_paths"] == 2
        assert f["lines_changed"] == 4

    def test_detects_a_signature_change(self):
        assert fix_complexity_features(SIGNATURE_CHANGE)["signatures_touched"] >= 2

    def test_a_localised_edit_touches_no_signature(self):
        assert fix_complexity_features(ONE_LINE)["signatures_touched"] == 0


class TestOrdering:
    """The appendix's own ordering, pinned."""

    def test_a_signature_change_outranks_a_one_line_edit(self):
        assert raw_complexity(SIGNATURE_CHANGE) > raw_complexity(ONE_LINE)

    def test_two_files_outrank_one(self):
        assert raw_complexity(TWO_FILES) > raw_complexity(ONE_LINE)

    def test_no_parseable_fix_scores_zero(self):
        assert raw_complexity("nothing here") == 0.0


class TestIndexHonesty:
    def test_index_is_None_without_a_population(self):
        # An honest absence. Returning 0.0 would read as 'maximally simple'.
        assert complexity_index(ONE_LINE, None) is None
        assert complexity_index(ONE_LINE, []) is None

    def test_index_is_a_percentile_in_range(self):
        pop = [5.0, 10.0, 20.0, 40.0, 80.0]
        v = complexity_index(SIGNATURE_CHANGE, pop)
        assert v is not None and 0.0 <= v <= 1.0

    def test_a_simpler_fix_ranks_below_a_more_complex_one(self):
        pop = [raw_complexity(ONE_LINE), raw_complexity(SIGNATURE_CHANGE),
               raw_complexity(TWO_FILES)]
        assert complexity_index(ONE_LINE, pop) < complexity_index(SIGNATURE_CHANGE, pop)


class TestItDoesNotReachRk:
    """The shadow guarantee, asserted rather than trusted."""

    def test_module_does_not_import_or_call_the_risk_machinery(self):
        # Checked with AST, not string matching: the module docstring explains
        # WHY it stays out of R_k and names compute_rk and check_sk_threshold in
        # doing so. A substring test would fail on its own explanation.
        import ast
        import bench.dm._fix_complexity as m

        tree = ast.parse(pathlib.Path(m.__file__).read_text())

        imported = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                imported |= {a.name for a in n.names}
            elif isinstance(n, ast.ImportFrom) and n.module:
                imported.add(n.module)
        assert not any("reference_runner" in i for i in imported), imported
        assert not any("immune_agents" in i for i in imported), imported

        called = {n.func.id for n in ast.walk(tree)
                  if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        called |= {n.func.attr for n in ast.walk(tree)
                   if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
        assert "compute_rk" not in called
        assert "check_sk_threshold" not in called
