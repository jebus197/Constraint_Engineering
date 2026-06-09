"""Regression tests for the Exp 40 continuation fix 1a — structural
finding-ID validation in parse_findings.

Bug class: model output writes arbitrary code fragments or multi-token
descriptions into the FINDING_ID field. The Exp 39 leakage guards
(`_CODE_LEAK_VARNAMES`, parens, f-string markers) caught Python
variable-name leaks but missed dict-comprehension fragments, single
backtick literals, multi-token descriptions, and similar.

Live evidence from the 15 May 2026 continuation run includes mangled
finding IDs:
  - CC2_f for f in findings}
  - Gemini_f for f in findings}
  - DeepSeek_`
  - ChatGPT_f for f in findings}` collapsing non-globally-unique IDs.
    F013 concerns ignoring the `model_id` namespace already present in
    `rk_validation`.

Captured in `experimental_notes/Exp40_Continuation_Postmortem_2026-05-15.md`
Anomaly 2. The panel that produced these IDs ALSO surfaced the
underlying bug — that `{f.finding_id: f for f in findings}` silently
overwrites when finding IDs are not globally unique — making the
panel's own diagnostic the design reference for this regression.

Fix surface: bench/runner_core.py, marker-format parser branch (around
line 728+ post-fix). After the existing leakage guards, an additional
structural rule rejects any finding_id that fails the validation
`^[A-Za-z0-9_]+$`. Single token, alphanumeric + underscore only.

These tests confirm:
  1. Legitimate IDs (F001, CC2_F001, C0144_VERDICT_CONFIRM, IM_F001,
     UNSTRUCTURED) pass.
  2. Code-fragment IDs are rejected (dict-comp, backtick, multi-token
     text, operators, braces).
  3. Whitespace-containing IDs are rejected.
  4. The legitimate findings in a mixed-quality response still parse;
     only the mangled ones are dropped.
  5. AST-level + source-truth pins ensure the validation regex stays
     in the parser branch and matches the expected character class.
"""

from __future__ import annotations

import ast
import inspect
import re
from pathlib import Path

import pytest

from bench import runner_core
from bench.runner_core import parse_findings, _structurally_valid_fid


# ── Behavioural pins ────────────────────────────────────────────────


class TestLegitimateIDsPass:
    """All canonical-shape IDs from the project's registry survive
    the structural validation."""

    def _make_marker_response(self, fid: str) -> str:
        return (
            f"FINDING_ID: {fid}\n"
            f"SEVERITY: 0.8\n"
            f"FLAW_CLASS: 3\n"
            f"ABSTRACTION_INDEX: 0.5\n"
            f"DESCRIPTION: test finding\n"
            f"PROPOSED_FIX: test fix\n"
            f"VERIFIED: false\n"
        )

    def test_bare_F_ID_passes(self):
        resp = self._make_marker_response("F001")
        findings = parse_findings(
            model_id="TestModel", round_idx=1, response=resp,
        )
        assert len(findings) == 1
        assert findings[0].finding_id == "TestModel_F001"

    def test_model_prefixed_F_ID_passes(self):
        resp = self._make_marker_response("CC2_F001")
        findings = parse_findings(
            model_id="CC2", round_idx=1, response=resp,
        )
        assert len(findings) == 1
        # Already prefixed — no double-prefix
        assert findings[0].finding_id == "CC2_F001"

    def test_verdict_style_ID_passes(self):
        resp = self._make_marker_response("C0144_VERDICT_CONFIRM")
        findings = parse_findings(
            model_id="ChatGPT", round_idx=12, response=resp,
        )
        assert len(findings) == 1
        assert findings[0].finding_id.endswith("C0144_VERDICT_CONFIRM")

    def test_unstructured_label_passes(self):
        resp = self._make_marker_response("UNSTRUCTURED")
        findings = parse_findings(
            model_id="Gemini", round_idx=3, response=resp,
        )
        assert len(findings) == 1
        assert findings[0].finding_id.endswith("UNSTRUCTURED")

    def test_relay_branded_ID_passes(self):
        # LB_R2_F001 = canonical relay-topology branded ID seen in
        # Exp 38/39 logs.
        resp = self._make_marker_response("LB_R2_F001")
        findings = parse_findings(
            model_id="Codex", round_idx=4, response=resp,
        )
        assert len(findings) == 1


class TestMangledIDsRejected:
    """Live evidence from Round 12-14 of the continuation: mangled
    finding IDs drawn from code fragments. The structural rule rejects
    the mangled block; the parser may then either (a) return zero
    findings, or (b) fall through to the runner-generated
    `<model>_UNSTRUCTURED` sentinel which is structurally clean and
    semantically a valid catch-all for "model produced text but no
    parseable finding". The key property: NO finding has the mangled
    string in its `finding_id` field."""

    MANGLED_FRAGMENTS = (
        "f for f in findings",  # dict-comp leak
        "`",                    # bare backtick
        " ",                    # space
        "}",                    # brace
        "F001 with description",  # whitespace inside
        "{F001}",               # brace-wrapped
        "X-Y-Z",                # hyphenated
        "expr or x",            # operator
        "F001`",                # trailing backtick
    )

    def _wrap(self, fid: str) -> str:
        return (
            f"FINDING_ID: {fid}\n"
            f"SEVERITY: 0.8\n"
            f"FLAW_CLASS: 3\n"
            f"DESCRIPTION: real defect being reported\n"
            f"PROPOSED_FIX: a fix\n"
        )

    def _assert_no_mangled_id(self, findings, mangled_str):
        for f in findings:
            assert mangled_str not in f.finding_id, (
                f"Mangled fragment {mangled_str!r} leaked into "
                f"finding_id {f.finding_id!r}"
            )
            # And the ID itself must conform to the structural rule.
            assert re.match(r'^[A-Za-z0-9_]+$', f.finding_id), (
                f"finding_id {f.finding_id!r} fails structural "
                f"validation post-fix."
            )

    def test_dict_comprehension_fragment_rejected(self):
        resp = self._wrap("f for f in findings}")
        findings = parse_findings(
            model_id="CC2", round_idx=12, response=resp,
        )
        self._assert_no_mangled_id(findings, "f for f in findings")

    def test_single_backtick_rejected(self):
        resp = self._wrap("`")
        findings = parse_findings(
            model_id="DeepSeek", round_idx=13, response=resp,
        )
        self._assert_no_mangled_id(findings, "`")

    def test_multi_token_descriptive_text_rejected(self):
        resp = self._wrap(
            "f for f in findings}` collapsing non-globally-unique IDs"
        )
        findings = parse_findings(
            model_id="ChatGPT", round_idx=14, response=resp,
        )
        self._assert_no_mangled_id(findings, "collapsing")

    def test_brace_in_id_rejected(self):
        resp = self._wrap("{F001}")
        findings = parse_findings(
            model_id="X", round_idx=1, response=resp,
        )
        self._assert_no_mangled_id(findings, "{")
        self._assert_no_mangled_id(findings, "}")

    def test_hyphenated_id_rejected(self):
        resp = self._wrap("X-Y-Z-fragment")
        findings = parse_findings(
            model_id="X", round_idx=1, response=resp,
        )
        self._assert_no_mangled_id(findings, "-")

    def test_all_mangled_fragments_caught(self):
        # Sweep across every observed mangled-pattern class.
        for mangled in self.MANGLED_FRAGMENTS:
            resp = self._wrap(mangled)
            findings = parse_findings(
                model_id="SweepModel", round_idx=99, response=resp,
            )
            for f in findings:
                # The structural rule must pass on every emitted ID.
                assert re.match(r'^[A-Za-z0-9_]+$', f.finding_id), (
                    f"Mangled input {mangled!r} produced "
                    f"structurally-invalid id {f.finding_id!r}"
                )
                # And the mangled fragment must not be IN the id —
                # skip when the stripped fragment is empty (the empty
                # string is trivially "in" every string).
                stripped = mangled.strip()
                if stripped:
                    assert stripped not in f.finding_id, (
                        f"Mangled fragment {mangled!r} leaked into "
                        f"id {f.finding_id!r}"
                    )


class TestJSONPathMangledIDsRejected:
    """The JSON-array parser path also handles FINDING_ID. If the model
    emits JSON with a mangled FINDING_ID value, the structural rule
    must reject it there too — not only in the marker path."""

    def test_json_array_with_mangled_id(self):
        resp = (
            '[{"FINDING_ID": "f for f in findings}", '
            '"SEVERITY": 0.8, "FLAW_CLASS": 3, '
            '"DESCRIPTION": "real defect", '
            '"PROPOSED_FIX": "a fix"}]'
        )
        findings = parse_findings(
            model_id="ChatGPT", round_idx=10, response=resp,
        )
        for f in findings:
            assert "f for f in findings" not in f.finding_id
            assert re.match(r'^[A-Za-z0-9_]+$', f.finding_id)

    def test_json_array_clean_id_passes(self):
        resp = (
            '[{"FINDING_ID": "F001", '
            '"SEVERITY": 0.8, "FLAW_CLASS": 3, '
            '"DESCRIPTION": "real defect", '
            '"PROPOSED_FIX": "a fix"}]'
        )
        findings = parse_findings(
            model_id="ChatGPT", round_idx=10, response=resp,
        )
        assert len(findings) == 1
        assert findings[0].finding_id == "ChatGPT_F001"

    def test_json_array_trailing_space_id_normalised_not_dropped(self):
        # P-pass edge: a legitimate ID with stray trailing whitespace
        # in JSON output must be normalised (parity with the marker
        # path's .strip()), NOT dropped as if it were a code-fragment
        # leak.
        resp = (
            '[{"FINDING_ID": "F001 ", '
            '"SEVERITY": 0.8, "FLAW_CLASS": 3, '
            '"DESCRIPTION": "real defect", '
            '"PROPOSED_FIX": "a fix"}]'
        )
        findings = parse_findings(
            model_id="ChatGPT", round_idx=10, response=resp,
        )
        assert len(findings) == 1
        assert findings[0].finding_id == "ChatGPT_F001"

    def test_json_object_trailing_space_id_normalised(self):
        resp = (
            '{"F001": {"FINDING_ID": "F001 ", '
            '"SEVERITY": 0.8, "FLAW_CLASS": 3, '
            '"DESCRIPTION": "real defect", '
            '"PROPOSED_FIX": "a fix"}}'
        )
        findings = parse_findings(
            model_id="Gemini", round_idx=10, response=resp,
        )
        assert len(findings) == 1
        assert findings[0].finding_id == "Gemini_F001"


class TestMixedResponseStillParses:
    """A response containing both legitimate and mangled findings
    should produce the legitimate ones and drop the mangled."""

    def test_mixed_response_keeps_clean_drops_mangled(self):
        resp = (
            "FINDING_ID: F001\n"
            "SEVERITY: 0.9\n"
            "FLAW_CLASS: 3\n"
            "DESCRIPTION: legitimate finding one\n"
            "PROPOSED_FIX: a fix\n"
            "\n"
            "FINDING_ID: f for f in findings}\n"
            "SEVERITY: 0.7\n"
            "FLAW_CLASS: 2\n"
            "DESCRIPTION: this would be mangled\n"
            "PROPOSED_FIX: another fix\n"
            "\n"
            "FINDING_ID: F002\n"
            "SEVERITY: 0.8\n"
            "FLAW_CLASS: 4\n"
            "DESCRIPTION: legitimate finding two\n"
            "PROPOSED_FIX: third fix\n"
        )
        findings = parse_findings(
            model_id="TestModel", round_idx=12, response=resp,
        )
        # Two legitimate findings survive; the mangled middle one is
        # dropped.
        legitimate_ids = {f.finding_id for f in findings}
        assert "TestModel_F001" in legitimate_ids
        assert "TestModel_F002" in legitimate_ids
        # The mangled one's content "this would be mangled" should not
        # appear in any preserved description.
        for f in findings:
            assert "this would be mangled" not in f.description
        # Phantom IDs must NOT be present.
        for fid in legitimate_ids:
            assert " " not in fid, f"Whitespace in id {fid!r}"
            assert "}" not in fid, f"Brace in id {fid!r}"
            assert "`" not in fid, f"Backtick in id {fid!r}"


# ── Source-truth pins ───────────────────────────────────────────────


class TestSourceTruth:
    """Pin the validation helper + its placement, so a future refactor
    cannot silently weaken the guard."""

    def test_helper_function_exists(self):
        # The helper is the project's single source-of-truth for the
        # validation rule; the four parser paths all call it.
        assert hasattr(runner_core, "_structurally_valid_fid"), (
            "_structurally_valid_fid helper must exist in "
            "runner_core.py"
        )
        assert hasattr(runner_core, "_VALID_FID_STRUCTURE"), (
            "_VALID_FID_STRUCTURE regex must be a module-level "
            "constant in runner_core.py"
        )

    def test_helper_behaviour(self):
        from bench.runner_core import _structurally_valid_fid
        # Legitimate
        assert _structurally_valid_fid("F001")
        assert _structurally_valid_fid("CC2_F001")
        assert _structurally_valid_fid("C0144_VERDICT_CONFIRM")
        assert _structurally_valid_fid("UNSTRUCTURED")
        assert _structurally_valid_fid("LB_R2_F001")
        assert _structurally_valid_fid("IM_F001")
        # Rejected
        assert not _structurally_valid_fid("f for f in findings}")
        assert not _structurally_valid_fid("`")
        assert not _structurally_valid_fid("X-Y-Z")
        assert not _structurally_valid_fid("{F001}")
        assert not _structurally_valid_fid("F001 description")
        assert not _structurally_valid_fid("")
        assert not _structurally_valid_fid("expr or x")

    def test_helper_called_from_all_paths(self):
        # AST source check: the helper must be referenced from the
        # JSON-array, JSON-object, and marker parser branches inside
        # parse_findings. (The tuple parser is pre-validated by its
        # regex `[A-Z0-9_]*F\d{2,4}`.)
        src = Path(runner_core.__file__).read_text()
        # Count helper calls — must appear in at least three places
        # inside parse_findings (JSON array, JSON object, marker).
        count = src.count("_structurally_valid_fid")
        # 1 = definition + body call + at least 3 call-sites = ≥4.
        assert count >= 4, (
            f"Helper appears only {count} times; expected ≥4 "
            f"(definition + helper-body + 3 parser-path call-sites)."
        )


# ── AST-level pin ───────────────────────────────────────────────────


class TestASTPlacement:
    """Confirm the helper is wired into parse_findings."""

    def test_helper_called_inside_parse_findings(self):
        # The validator must be wired into the parse PIPELINE. After the 2026-06
        # refactor, parse_findings became a thin wrapper over _parse_findings_core,
        # where the per-path _structurally_valid_fid calls now live. Assert the call
        # exists somewhere in that pipeline (wrapper or core) rather than inside one
        # fixed function — the earlier text-on-one-function assertion was brittle to
        # this legitimate refactor (behaviour was never lost; see behavioural check
        # below).
        src = Path(runner_core.__file__).read_text()
        tree = ast.parse(src)
        pipeline_fns = {"parse_findings", "_parse_findings_core"}
        src_lines = src.split("\n")
        found_in = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in pipeline_fns:
                fn_src = "\n".join(src_lines[node.lineno - 1:node.end_lineno])
                if "_structurally_valid_fid" in fn_src:
                    found_in.add(node.name)
        assert found_in, (
            "the parse pipeline (parse_findings / _parse_findings_core) must call "
            "_structurally_valid_fid on every candidate finding_id."
        )

        # Behavioural guarantee (the property that actually matters): a structurally
        # invalid model-supplied id must never survive parsing — it is rejected to a
        # runner-generated valid id.
        bad = parse_findings(
            "Codex", 0,
            '```json\n[{"finding_id": "bad id `x` !", "severity": 0.9, '
            '"description": "X breaks Y", "flaw_class": 5}]\n```')
        assert bad, "parser must still return a finding for malformed-id input"
        assert all(_structurally_valid_fid(f.finding_id) for f in bad), (
            "parse_findings must sanitize/reject structurally-invalid finding ids")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
