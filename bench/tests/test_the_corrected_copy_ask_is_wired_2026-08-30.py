"""Pin the corrected-copy ask, which survived unwired from 21 Aug to 30 Aug.

CC2, third-pass review 2026-08-30: "`_ASK_CORRECTED_COPY` appears in zero test
files... Line :9657 could be deleted and the suite stays green — which is
precisely how this flag survived from 21 Aug to today."

`discrimination_control_ask` had 1 write and 0 reads. This project's own record
diagnosed it on 2026-08-21 and specified the one-line wire, and nobody applied
it, because nothing failed when it was missing. That is what this file changes.
"""
import ast
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import reference_runner_v3 as R

SRC = pathlib.Path(R.__file__).read_text(encoding="utf-8")


class TestTheFlagIsRead:
    def test_the_module_mirror_exists(self):
        assert isinstance(R._ASK_CORRECTED_COPY, dict)

    def test_run_experiment_sets_it_from_the_config(self):
        fn = next(n for n in ast.walk(ast.parse(SRC))
                  if isinstance(n, ast.FunctionDef) and n.name == "run_experiment")
        body = ast.unparse(fn)
        assert "_ASK_CORRECTED_COPY['on']" in body or '_ASK_CORRECTED_COPY["on"]' in body, (
            "run_experiment no longer arms the ask — deleting that line used to "
            "leave the suite green, which is how the flag stayed dead for 9 days"
        )
        assert "discrimination_control_ask" in body

    def test_the_dispatch_path_reads_it(self):
        fn = next(n for n in ast.walk(ast.parse(SRC))
                  if isinstance(n, ast.FunctionDef) and n.name == "_dispatch_single_model")
        assert "_ASK_CORRECTED_COPY" in ast.unparse(fn)


class TestTheAskChangesThePrompt:
    def test_asking_adds_text_to_the_directive(self):
        base = R._OPERATIONAL_DIRECTIVE_TEXT or ""
        if not base.strip():
            import pytest
            pytest.skip("operational directive text unavailable in this tree")
        off = R._gate_falsifier_directive(base, False)
        on = R._gate_falsifier_directive(base, True)
        assert len(on) > len(off), (
            "ask_corrected_copy=True produced an identical prompt — the ask is "
            "a placebo again"
        )

    def test_the_directive_mentions_a_corrected_copy_when_asking(self):
        base = R._OPERATIONAL_DIRECTIVE_TEXT or ""
        if not base.strip():
            import pytest
            pytest.skip("operational directive text unavailable in this tree")
        on = R._gate_falsifier_directive(base, True).lower()
        assert "corrected" in on


class TestTheStaleWarningIsGone:
    def test_the_runner_no_longer_says_the_flag_is_unwired(self):
        """It printed 'IS NOT WIRED' 23 lines before arming the flag."""
        assert "IS NOT WIRED" not in SRC

    def test_the_ask_without_the_gate_is_announced(self):
        """ask=True with falsifier_gate_enabled=False emits no ask at all; that
        combination must not be silent."""
        fn = next(n for n in ast.walk(ast.parse(SRC))
                  if isinstance(n, ast.FunctionDef) and n.name == "_dispatch_single_model")
        body = ast.unparse(fn)
        assert "NO ask" in body or "no ask" in body.lower()
