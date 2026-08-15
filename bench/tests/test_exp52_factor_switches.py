"""Tests for the Exp 52 factorial's two experimental factor switches.

The capstone crosses the §17 feedback channel (off/on) with the §18
divergence directive (off/on) on one frozen target. That design is only a
measurement if "off" actually removes something, on BOTH halves of each
mechanism (directive text AND runner pass) and on BOTH config-ingestion
paths (``RunnerConfig.from_dict`` and
``launcher_core.build_runner_config_from_dict``).

Coverage:

* section omission against the REAL directive file — target section gone,
  every other section intact, no dangling headers or doubled separators;
* the divergence switch actually prevents the divergence pass;
* both switches default ON, so configs that predate them are unaffected;
* both ingestion paths honour all four new keys (the silent-drop class that
  has now bitten this project three times — see feedback_launcher_config_drop);
* no already-queued config in bench/exp4*_configs or bench/exp5*_configs
  sets either switch, so Exp 47 (running) and Exp 48-51 are untouched;
* the four generated cell configs differ in exactly the two factors plus the
  experiment name, on both ingestion paths.

Run:
    python3 -m pytest bench/tests/test_exp52_factor_switches.py -v
"""

from __future__ import annotations

import dataclasses
import json
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bench import launcher_core  # noqa: E402
from bench.dm._directive_sections import (  # noqa: E402
    FACTOR_SPECS,
    DirectiveSectionError,
    omit_directive_sections,
)
from bench.reference_runner_v2 import (  # noqa: E402
    DIRECTIVE_FACTOR_FIELDS,
    RunnerConfig,
    _apply_directive_omission,
    _DIRECTIVE_OMISSION,
    _directive_factor_state,
    _suppressed_directive_factors,
    arm_directive_omission,
)

OPERATIONAL_PATH = (
    REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_operational.md"
)
EXP52_CONFIGS = REPO_ROOT / "bench" / "exp52_configs"
CELL_LETTERS = ("A", "B", "C", "D")
# (feedback_on, divergence_on) per cell — the factorial's design matrix.
CELL_MATRIX = {
    "A": (False, False),
    "B": (True, False),
    "C": (False, True),
    "D": (True, True),
}


@pytest.fixture(scope="module")
def operational_text() -> str:
    return OPERATIONAL_PATH.read_text(encoding="utf-8")


def _h2_headings(text: str) -> list[str]:
    return [ln.strip() for ln in text.splitlines() if re.match(r"^##\s(?!#)", ln)]


class _StubArgs:
    resume = False


# ─────────────────────────────────────────────────────────────────────────────
# 1. Section omission against the real directive file
# ─────────────────────────────────────────────────────────────────────────────


class TestSectionOmissionOnRealDirective:

    def test_directive_file_has_both_sections(self, operational_text):
        """Guard: if the real file loses §17/§18 the rest of this suite is moot."""
        heads = _h2_headings(operational_text)
        assert any(h.startswith("## 17") for h in heads), heads[-5:]
        assert any(h.startswith("## §18") for h in heads), heads[-5:]

    @pytest.mark.parametrize("factor,gone_prefix,kept_prefix", [
        ("feedback", "## 17", "## §18"),
        ("divergence", "## §18", "## 17"),
    ])
    def test_target_section_gone_other_retained(
        self, operational_text, factor, gone_prefix, kept_prefix,
    ):
        out = omit_directive_sections(operational_text, [factor])
        heads = _h2_headings(out)
        assert not any(h.startswith(gone_prefix) for h in heads)
        assert any(h.startswith(kept_prefix) for h in heads)

    @pytest.mark.parametrize("factor", ["feedback", "divergence"])
    def test_all_other_sections_intact_verbatim(self, operational_text, factor):
        """Every heading except the target survives, in the same order."""
        before = _h2_headings(operational_text)
        after = _h2_headings(omit_directive_sections(operational_text, [factor]))
        spec = FACTOR_SPECS[factor]
        expected = [h for h in before if not spec.section_heading_re.match(h)]
        assert after == expected

    @pytest.mark.parametrize("factor", ["feedback", "divergence"])
    def test_section_body_gone_not_just_heading(self, operational_text, factor):
        """A distinctive sentence from inside the section must disappear too."""
        marker = {
            "feedback": "Do not resubmit a flagged finding unchanged",
            "divergence": "Cosmetic rewordings are rejected",
        }[factor]
        assert marker in operational_text
        assert marker not in omit_directive_sections(operational_text, [factor])

    def test_omitting_feedback_removes_the_dependent_paragraph_in_18(
        self, operational_text,
    ):
        """§18's 'Interaction with §17 feedback' paragraph would otherwise
        point the model at a section it cannot see."""
        assert "**Interaction with §17 feedback.**" in operational_text
        out = omit_directive_sections(operational_text, ["feedback"])
        assert "Interaction with §17 feedback" not in out
        # and the paragraph AFTER it in §18 survives
        assert "Divergence directive added 15 April 2026" in out

    @pytest.mark.parametrize("factors", [
        ["feedback"], ["divergence"], ["feedback", "divergence"],
    ])
    def test_no_dangling_headers_or_doubled_rules(
        self, operational_text, factors,
    ):
        out = omit_directive_sections(operational_text, factors)
        assert "---\n\n---" not in out
        assert "---\n---" not in out
        assert "\n\n\n\n" not in out
        # No heading is left with an empty body.
        lines = out.splitlines()
        for i, ln in enumerate(lines):
            if re.match(r"^##\s(?!#)", ln):
                rest = [x for x in lines[i + 1:i + 6] if x.strip()]
                assert rest, f"heading with empty body: {ln!r}"

    @pytest.mark.parametrize("factors", [
        ["feedback"], ["divergence"], ["feedback", "divergence"],
    ])
    def test_every_surviving_heading_keeps_its_separator(
        self, operational_text, factors,
    ):
        """Regression: the first implementation absorbed the rule BEFORE the
        removed heading as well as the one inside its span, which deleted two
        separators for one section and left the surviving neighbour's prose
        running straight into the next `## ` heading with no blank line and no
        rule. Every h2 (except the first after the h1) must still be preceded
        by a blank line and a horizontal rule."""
        out = omit_directive_sections(operational_text, factors)
        lines = out.splitlines()
        h2s = [i for i, ln in enumerate(lines) if re.match(r"^##\s(?!#)", ln)]
        for i in h2s[1:]:
            prev = [x for x in lines[max(0, i - 4):i] if x.strip()]
            assert prev and prev[-1].strip().startswith("---"), (
                f"heading {lines[i]!r} lost its separator; preceding lines: "
                f"{lines[max(0, i - 4):i]!r}"
            )
            assert not lines[i - 1].strip(), (
                f"heading {lines[i]!r} has no blank line before it"
            )

    @pytest.mark.parametrize("factors", [
        ["feedback"], ["divergence"], ["feedback", "divergence"],
    ])
    def test_no_stranded_rule_at_end_of_document(
        self, operational_text, factors,
    ):
        """Removing the LAST section must take the rule that preceded it,
        or the document ends on a separator with nothing after it."""
        out = omit_directive_sections(operational_text, factors)
        tail = [ln for ln in out.splitlines() if ln.strip()][-1]
        assert not tail.strip().startswith("---"), f"stranded rule: {tail!r}"

    def test_separator_count_drops_by_exactly_one_per_section(
        self, operational_text,
    ):
        rules_before = sum(
            1 for ln in operational_text.splitlines()
            if ln.strip() and set(ln.strip()) == {"-"} and len(ln.strip()) >= 3
        )

        def rules(text):
            return sum(
                1 for ln in text.splitlines()
                if ln.strip() and set(ln.strip()) == {"-"} and len(ln.strip()) >= 3
            )

        assert rules(omit_directive_sections(
            operational_text, ["feedback"])) == rules_before - 1
        assert rules(omit_directive_sections(
            operational_text, ["divergence"])) == rules_before - 1
        assert rules(omit_directive_sections(
            operational_text, ["feedback", "divergence"])) == rules_before - 2

    @pytest.mark.parametrize("factors", [
        ["feedback"], ["divergence"], ["feedback", "divergence"],
    ])
    def test_omission_actually_shrinks_the_text(self, operational_text, factors):
        out = omit_directive_sections(operational_text, factors)
        assert len(out) < len(operational_text)

    def test_both_omitted_removes_both(self, operational_text):
        out = omit_directive_sections(operational_text, ["feedback", "divergence"])
        heads = _h2_headings(out)
        assert not any(h.startswith("## 17") for h in heads)
        assert not any(h.startswith("## §18") for h in heads)
        # §16, the last surviving numbered section, is intact with its body.
        assert any(h.startswith("## 16") for h in heads)
        assert "Stage 6 derived 14 April 2026" in out

    def test_numbering_is_not_rewritten(self, operational_text):
        """Sections are NOT renumbered on omission: the directive
        cross-references sections by number throughout, and renumbering would
        silently redirect every one of those references."""
        out = omit_directive_sections(operational_text, ["feedback"])
        heads = _h2_headings(out)
        assert any(h.startswith("## 16") for h in heads)
        assert any(h.startswith("## §18") for h in heads)
        assert not any(h.startswith("## 17") for h in heads)

    def test_policy_dump_lines_are_dropped(self):
        prompt = (
            "policy.divergence.enabled=true\n"
            "policy.divergence.min_alternatives=1\n"
            "policy.feedback_channel.enabled=true\n"
            "policy.convergence.hard_veto=true\n"
            "\n"
            + OPERATIONAL_PATH.read_text(encoding="utf-8")
        )
        out = omit_directive_sections(prompt, ["divergence"])
        assert "policy.divergence." not in out
        assert "policy.feedback_channel.enabled=true" in out
        assert "policy.convergence.hard_veto=true" in out

    def test_missing_section_is_fatal_not_a_silent_no_op(self):
        """A no-op omission produces a cell identical to its control — a
        guaranteed null result dressed as a measurement."""
        with pytest.raises(DirectiveSectionError):
            omit_directive_sections("# Some other document\n\nnothing here\n",
                                    ["divergence"])

    def test_unknown_factor_key_is_fatal(self, operational_text):
        with pytest.raises(DirectiveSectionError):
            omit_directive_sections(operational_text, ["divergance"])  # typo

    def test_renumbered_heading_is_fatal(self):
        """Number matches but the title does not: refuse to guess."""
        text = "# Doc\n\n## 18 Something Entirely Different\n\nbody\n"
        with pytest.raises(DirectiveSectionError, match="keyword"):
            omit_directive_sections(text, ["divergence"])

    def test_empty_factor_list_is_byte_identical(self, operational_text):
        assert omit_directive_sections(operational_text, []) == operational_text

    def test_subsections_are_not_treated_as_boundaries(self, operational_text):
        """### 8.1 belongs to §8; omission must not slice a section short."""
        out = omit_directive_sections(operational_text, ["divergence"])
        assert "### 8.1 Semantic Novelty" in out
        assert "### 8.2 Suspicious Fast Convergence" in out
        assert "### 7.1. Finding Lifecycle" in out


# ─────────────────────────────────────────────────────────────────────────────
# 2. Defaults — existing configs must be unaffected
# ─────────────────────────────────────────────────────────────────────────────


class TestDefaultsAreOn:

    def test_both_switches_default_on(self):
        cfg = RunnerConfig(test_article="x.py")
        assert cfg.feedback_channel_enabled is True
        assert cfg.divergence_channel_enabled is True

    def test_off_modes_default_to_absent(self):
        cfg = RunnerConfig(test_article="x.py")
        assert cfg.feedback_off_mode == "absent"
        assert cfg.divergence_off_mode == "absent"

    def test_default_config_suppresses_nothing(self):
        cfg = RunnerConfig(test_article="x.py")
        assert _suppressed_directive_factors(cfg) == ()

    def test_default_config_leaves_prompt_byte_identical(self):
        cfg = RunnerConfig(test_article="x.py")
        _DIRECTIVE_OMISSION["factors"] = _suppressed_directive_factors(cfg)
        try:
            text = OPERATIONAL_PATH.read_text(encoding="utf-8")
            assert _apply_directive_omission(text) == text
        finally:
            _DIRECTIVE_OMISSION["factors"] = ()

    def test_invalid_off_mode_rejected(self):
        with pytest.raises(ValueError, match="off-mode"):
            RunnerConfig(test_article="x.py", feedback_off_mode="sometimes")
        with pytest.raises(ValueError, match="off-mode"):
            RunnerConfig(test_article="x.py", divergence_off_mode="maybe")

    def test_config_without_the_attributes_reads_as_on(self):
        """Back-compat: a config object predating these fields behaves as ON."""
        class _Legacy:
            pass
        legacy = _Legacy()
        assert _directive_factor_state(legacy, "feedback") == (True, True)
        assert _directive_factor_state(legacy, "divergence") == (True, True)


# ─────────────────────────────────────────────────────────────────────────────
# 3. "Off" semantics — one knob, both halves
# ─────────────────────────────────────────────────────────────────────────────


class TestOffSemantics:

    @pytest.mark.parametrize("factor", ["feedback", "divergence"])
    def test_absent_mode_kills_text_and_pass(self, factor):
        enabled_field, mode_field = DIRECTIVE_FACTOR_FIELDS[factor]
        cfg = RunnerConfig(test_article="x.py", **{enabled_field: False})
        assert getattr(cfg, mode_field) == "absent"
        assert _directive_factor_state(cfg, factor) == (False, False)
        assert factor in _suppressed_directive_factors(cfg)

    @pytest.mark.parametrize("factor", ["feedback", "divergence"])
    def test_text_only_mode_keeps_the_pass(self, factor):
        enabled_field, mode_field = DIRECTIVE_FACTOR_FIELDS[factor]
        cfg = RunnerConfig(test_article="x.py",
                           **{enabled_field: False, mode_field: "text_only"})
        text_present, pass_active = _directive_factor_state(cfg, factor)
        assert (text_present, pass_active) == (False, True)
        assert factor in _suppressed_directive_factors(cfg)

    @pytest.mark.parametrize("factor", ["feedback", "divergence"])
    def test_pass_only_mode_keeps_the_text(self, factor):
        enabled_field, mode_field = DIRECTIVE_FACTOR_FIELDS[factor]
        cfg = RunnerConfig(test_article="x.py",
                           **{enabled_field: False, mode_field: "pass_only"})
        text_present, pass_active = _directive_factor_state(cfg, factor)
        assert (text_present, pass_active) == (True, False)
        assert factor not in _suppressed_directive_factors(cfg)

    @pytest.mark.parametrize("mode", ["absent", "text_only", "pass_only"])
    def test_off_mode_is_inert_while_enabled(self, mode):
        cfg = RunnerConfig(test_article="x.py", feedback_off_mode=mode,
                           divergence_off_mode=mode)
        assert _directive_factor_state(cfg, "feedback") == (True, True)
        assert _directive_factor_state(cfg, "divergence") == (True, True)

    def test_factors_are_independent(self):
        cfg = RunnerConfig(test_article="x.py",
                           feedback_channel_enabled=False,
                           divergence_channel_enabled=True)
        assert _directive_factor_state(cfg, "feedback") == (False, False)
        assert _directive_factor_state(cfg, "divergence") == (True, True)
        assert _suppressed_directive_factors(cfg) == ("feedback",)


# ─────────────────────────────────────────────────────────────────────────────
# 4. The divergence switch prevents the divergence pass
# ─────────────────────────────────────────────────────────────────────────────


class TestDivergencePassIsPrevented:
    """The runner half. The pass builds DivergenceRecords, pools alternatives
    into a cross-model diversity signal and flags recidivism; switching the
    factor off must stop all of it."""

    RAW_WITH_ALT = (
        "Alternative 1 (dimension: mechanism)\n"
        "Resolve the contention with a hash join over the shard table "
        "instead of walking the nested loop.\n"
        "Differs from primary: the primary walks a nested loop per key; this "
        "builds one hash table and probes it once.\n"
    )

    def test_divergence_config_construction_honours_the_switch(self):
        """The site that used to read DivergenceConfig(enabled=True)."""
        from bench.dm._divergence import DivergenceConfig, build_divergence_record
        cfg_off = RunnerConfig(test_article="x.py",
                               divergence_channel_enabled=False)
        pass_active = _directive_factor_state(cfg_off, "divergence")[1]
        assert pass_active is False
        rec = build_divergence_record(
            "f1", "primary text here", self.RAW_WITH_ALT,
            config=DivergenceConfig(enabled=pass_active),
        )
        assert rec.alternatives == []
        assert rec.compliant is True  # disabled directive cannot be violated

    def test_divergence_config_enabled_when_switch_on(self):
        from bench.dm._divergence import DivergenceConfig, build_divergence_record
        cfg_on = RunnerConfig(test_article="x.py")
        pass_active = _directive_factor_state(cfg_on, "divergence")[1]
        assert pass_active is True
        rec = build_divergence_record(
            "f1", "primary text here", self.RAW_WITH_ALT,
            config=DivergenceConfig(enabled=pass_active),
        )
        assert rec.alternatives, "enabled pass must extract the alternative"

    def test_runner_source_no_longer_hardcodes_enabled_true(self):
        """Structural guard: the hard-coded construction was the blocker."""
        src = (REPO_ROOT / "bench" / "reference_runner_v2.py").read_text(
            encoding="utf-8")
        assert "_DivergenceConfig(enabled=True)" not in src
        assert "_DivergenceConfig(enabled=divergence_pass_enabled)" in src
        assert "if not divergence_pass_enabled:" in src

    def test_omission_precedes_every_use_of_the_prompt(self):
        """One wiring point must cover ALL dispatch branches — direct,
        decomposed/multi-turn, in-round re-ask and secondary route. Assert the
        omission assignment comes before every downstream use of the variable
        inside _dispatch_single_model."""
        import ast
        src = (REPO_ROOT / "bench" / "reference_runner_v2.py").read_text(
            encoding="utf-8")
        tree = ast.parse(src)
        fn = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef)
                  and n.name == "_dispatch_single_model")
        omit_line = None
        for node in ast.walk(fn):
            if (isinstance(node, ast.Assign)
                    and isinstance(node.value, ast.Call)
                    and getattr(node.value.func, "id", "")
                    == "_apply_directive_omission"):
                omit_line = node.lineno
        assert omit_line is not None, "omission not wired into dispatch"
        loads = [n.lineno for n in ast.walk(fn)
                 if isinstance(n, ast.Name) and n.id == "model_cdsfl"
                 and isinstance(n.ctx, ast.Load) and n.lineno > omit_line]
        assert loads, "model_cdsfl is never used after the omission — check wiring"
        earlier = [n.lineno for n in ast.walk(fn)
                   if isinstance(n, ast.Name) and n.id == "model_cdsfl"
                   and isinstance(n.ctx, ast.Load) and n.lineno < omit_line]
        # The only pre-omission loads are the assembly steps that BUILD the
        # prompt (operational append, falsifier-gate rewrite), never a dispatch.
        assembly_lines = set()
        for node in ast.walk(fn):
            if (isinstance(node, ast.Assign)
                    and any(getattr(t, "id", "") == "model_cdsfl"
                            for t in node.targets)):
                assembly_lines.add(node.lineno)
            if (isinstance(node, ast.AugAssign)
                    and getattr(node.target, "id", "") == "model_cdsfl"):
                assembly_lines.add(node.lineno)
        assert set(earlier) <= assembly_lines, (
            f"model_cdsfl is consumed before omission at lines "
            f"{sorted(set(earlier) - assembly_lines)}"
        )

    def test_feedback_pass_gate_reads_the_factor_state(self):
        src = (REPO_ROOT / "bench" / "reference_runner_v2.py").read_text(
            encoding="utf-8")
        assert 'feedback_enabled = _directive_factor_state(cfg, "feedback")[1]' in src
        assert ('divergence_pass_enabled = _directive_factor_state('
                'cfg, "divergence")[1]') in src


# ─────────────────────────────────────────────────────────────────────────────
# 4b. The experiment-start arming + fail-fast probe
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _reset_omission_mirror():
    """The mirror is module-level process state; never leak it between tests."""
    yield
    _DIRECTIVE_OMISSION["factors"] = ()


class TestArmDirectiveOmission:

    def test_default_config_arms_nothing_and_probes_nothing(self):
        cfg = RunnerConfig(test_article="x.py")
        assert arm_directive_omission(cfg) == (0, 0)
        assert _DIRECTIVE_OMISSION["factors"] == ()

    @pytest.mark.parametrize("factor", ["feedback", "divergence"])
    def test_off_factor_is_armed_and_probe_shrinks(self, factor):
        enabled_field, _ = DIRECTIVE_FACTOR_FIELDS[factor]
        cfg = RunnerConfig(test_article="x.py", **{enabled_field: False})
        before, after = arm_directive_omission(cfg)
        assert _DIRECTIVE_OMISSION["factors"] == (factor,)
        assert 0 < after < before

    def test_probe_raises_when_omission_would_be_a_no_op(self, monkeypatch):
        """The fail-fast that exists so a null result cannot masquerade as a
        measurement: if the omission removes nothing, refuse to run."""
        monkeypatch.setattr(
            "bench.reference_runner_v2._apply_directive_omission",
            lambda text: text)
        cfg = RunnerConfig(test_article="x.py",
                           divergence_channel_enabled=False)
        with pytest.raises(RuntimeError, match="removed nothing"):
            arm_directive_omission(cfg)

    def test_pass_only_mode_arms_nothing_text_side(self):
        """pass_only keeps the text, so nothing is suppressed from the prompt
        and the probe is skipped."""
        cfg = RunnerConfig(test_article="x.py",
                           divergence_channel_enabled=False,
                           divergence_off_mode="pass_only")
        assert arm_directive_omission(cfg) == (0, 0)
        assert _DIRECTIVE_OMISSION["factors"] == ()

    def test_arming_is_idempotent_and_resettable(self):
        off = RunnerConfig(test_article="x.py", feedback_channel_enabled=False)
        arm_directive_omission(off)
        assert _DIRECTIVE_OMISSION["factors"] == ("feedback",)
        arm_directive_omission(RunnerConfig(test_article="x.py"))
        assert _DIRECTIVE_OMISSION["factors"] == ()


# ─────────────────────────────────────────────────────────────────────────────
# 5. Both ingestion paths honour both keys (the three-times-bitten class)
# ─────────────────────────────────────────────────────────────────────────────


NEW_KEYS = (
    "feedback_channel_enabled",
    "feedback_off_mode",
    "divergence_channel_enabled",
    "divergence_off_mode",
)


class TestBothIngestionPaths:

    BASE = {
        "experiment_name": "ingest_probe",
        "models": ["CC2"],
        "test_article": "bench/launcher_core.py",
    }

    @pytest.mark.parametrize("key,value", [
        ("feedback_channel_enabled", False),
        ("divergence_channel_enabled", False),
        ("feedback_off_mode", "text_only"),
        ("divergence_off_mode", "pass_only"),
    ])
    def test_runner_config_path(self, key, value):
        cfg = RunnerConfig.from_dict({**self.BASE, key: value})
        assert getattr(cfg, key) == value

    @pytest.mark.parametrize("key,value", [
        ("feedback_channel_enabled", False),
        ("divergence_channel_enabled", False),
        ("feedback_off_mode", "text_only"),
        ("divergence_off_mode", "pass_only"),
    ])
    def test_launcher_path(self, key, value):
        cfg = launcher_core.build_runner_config_from_dict(
            {**self.BASE, key: value}, _StubArgs())
        assert getattr(cfg, key) == value, (
            f"launcher dropped {key} — the silent-divergence class that has "
            f"already collapsed three CDSFL config keys"
        )

    @pytest.mark.parametrize("key,value", [
        ("feedback_channel_enabled", False),
        ("divergence_channel_enabled", False),
        ("feedback_off_mode", "text_only"),
        ("divergence_off_mode", "pass_only"),
    ])
    def test_both_paths_agree(self, key, value):
        d = {**self.BASE, key: value}
        a = RunnerConfig.from_dict(d)
        b = launcher_core.build_runner_config_from_dict(d, _StubArgs())
        assert getattr(a, key) == getattr(b, key) == value

    def test_absent_keys_default_on_via_launcher(self):
        cfg = launcher_core.build_runner_config_from_dict(dict(self.BASE),
                                                          _StubArgs())
        assert cfg.feedback_channel_enabled is True
        assert cfg.divergence_channel_enabled is True
        assert cfg.feedback_off_mode == "absent"
        assert cfg.divergence_off_mode == "absent"


# ─────────────────────────────────────────────────────────────────────────────
# 6. Queued experiments are untouched
# ─────────────────────────────────────────────────────────────────────────────


class TestQueuedConfigsUnaffected:
    """Exp 47 is RUNNING and 48-51 are queued. None may change behaviour."""

    @staticmethod
    def _queued_configs() -> list[Path]:
        out: list[Path] = []
        for d in sorted(REPO_ROOT.glob("bench/exp4*_configs")):
            out.extend(sorted(d.glob("*.json")))
        for d in sorted(REPO_ROOT.glob("bench/exp5*_configs")):
            out.extend(p for p in sorted(d.glob("*.json"))
                       if not p.name.startswith("52_factorial_cell_"))
        return out

    def test_found_some_configs(self):
        assert len(self._queued_configs()) > 10

    def test_no_queued_config_sets_a_switch_to_off(self):
        offenders = []
        for path in self._queued_configs():
            data = json.loads(path.read_text(encoding="utf-8"))
            for key in NEW_KEYS:
                if key not in data:
                    continue
                default = getattr(RunnerConfig(test_article="x.py"), key)
                if data[key] != default:
                    offenders.append(f"{path.name}:{key}={data[key]!r}")
        assert not offenders, (
            "queued configs would change behaviour under the new switches: "
            + ", ".join(offenders)
        )

    def test_queued_configs_suppress_nothing(self):
        for path in self._queued_configs():
            data = json.loads(path.read_text(encoding="utf-8"))
            cfg = launcher_core.build_runner_config_from_dict(data, _StubArgs())
            assert _suppressed_directive_factors(cfg) == (), path.name
            assert _directive_factor_state(cfg, "feedback") == (True, True)
            assert _directive_factor_state(cfg, "divergence") == (True, True)


# ─────────────────────────────────────────────────────────────────────────────
# 7. The four factorial cell configs
# ─────────────────────────────────────────────────────────────────────────────


class TestFactorialCellConfigs:

    @staticmethod
    def _path(cell: str) -> Path:
        return EXP52_CONFIGS / f"52_factorial_cell_{cell}.json"

    def test_all_four_cells_exist(self):
        for cell in CELL_LETTERS:
            assert self._path(cell).exists(), cell

    @pytest.mark.parametrize("cell", CELL_LETTERS)
    @pytest.mark.parametrize("path_name", ["runner", "launcher"])
    def test_cell_factors_land_as_designed(self, cell, path_name):
        data = json.loads(self._path(cell).read_text(encoding="utf-8"))
        cfg = (RunnerConfig.from_dict(data) if path_name == "runner"
               else launcher_core.build_runner_config_from_dict(data, _StubArgs()))
        fb_on, dv_on = CELL_MATRIX[cell]
        assert cfg.feedback_channel_enabled is fb_on
        assert cfg.divergence_channel_enabled is dv_on
        assert _directive_factor_state(cfg, "feedback") == (fb_on, fb_on)
        assert _directive_factor_state(cfg, "divergence") == (dv_on, dv_on)

    @pytest.mark.parametrize("cell", CELL_LETTERS)
    def test_cell_off_mode_is_absent(self, cell):
        data = json.loads(self._path(cell).read_text(encoding="utf-8"))
        assert data["feedback_off_mode"] == "absent"
        assert data["divergence_off_mode"] == "absent"

    @pytest.mark.parametrize("path_name", ["runner", "launcher"])
    def test_only_the_two_factors_and_the_name_differ(self, path_name):
        """Field-by-field RunnerConfig diff across all four cells."""
        cfgs = {}
        for cell in CELL_LETTERS:
            data = json.loads(self._path(cell).read_text(encoding="utf-8"))
            cfgs[cell] = (
                RunnerConfig.from_dict(data) if path_name == "runner"
                else launcher_core.build_runner_config_from_dict(data, _StubArgs())
            )
        allowed = {"experiment_name", "feedback_channel_enabled",
                   "divergence_channel_enabled"}
        differing = set()
        for field in dataclasses.fields(RunnerConfig):
            values = [getattr(cfgs[c], field.name) for c in CELL_LETTERS]
            if all(v == values[0] for v in values):
                continue
            differing.add(field.name)
        assert differing == allowed, (
            f"cells differ on unexpected RunnerConfig fields: "
            f"{sorted(differing - allowed)}; missing: {sorted(allowed - differing)}"
        )

    # PRE-EXISTING launcher-whitelist drops, discovered 2026-07-29 while
    # tracing the cell configs through both paths. These three keys are
    # honoured by RunnerConfig.from_dict (the runner's own --config path) and
    # absent from launcher_core's whitelist, so on the launcher path — the one
    # the arc sequencer uses — every config from Exp 42 onward has silently
    # run at the code default:
    #
    #   stall_gamma_terminate       config 1.01 -> default 0.45  (inert:
    #                               stall_gamma_termination_enabled is False
    #                               everywhere, so the terminate tier cannot fire)
    #   stall_gamma_advisory        config 1.01 -> default 0.30  (advisory tier
    #                               can fire from round 15; logged, non-gating)
    #   gamma_telemetry_only_until  config 20   -> default 14    (from round 15
    #                               the legacy state-convergence path starts
    #                               applying a gamma threshold the config
    #                               intended to suppress)
    #
    # NOT fixed here: adding the passthrough would change Exp 48-51 relative to
    # the already-completed Exp 42-47 legs, which is a founder ruling, not a
    # side effect of building the factorial switches. Pinned as an exact set so
    # a FOURTH drop cannot appear unnoticed.
    # RESOLVED 2026-07-29: all three drops were fixed in launcher_core
    # (founder-directed, before the factorial). This set is now EMPTY and must
    # stay empty — any entry appearing here again means a config key the runner
    # honours is being silently ignored on the launcher path, which is the
    # failure class that would have run the factorial's primary factor ON in
    # every cell. Empty is the correct steady state, not a placeholder.
    KNOWN_LAUNCHER_DROPS = frozenset()

    def test_cells_agree_across_both_ingestion_paths(self):
        """Every cell must produce the same RunnerConfig on both paths, except
        for the pinned set of pre-existing launcher-whitelist drops."""
        for cell in CELL_LETTERS:
            data = json.loads(self._path(cell).read_text(encoding="utf-8"))
            a = RunnerConfig.from_dict(data)
            b = launcher_core.build_runner_config_from_dict(data, _StubArgs())
            differing = set()
            for field in dataclasses.fields(RunnerConfig):
                if field.name == "resume":
                    continue  # launcher takes resume from argv, runner from JSON
                if getattr(a, field.name) != getattr(b, field.name):
                    differing.add(field.name)
            assert differing == self.KNOWN_LAUNCHER_DROPS, (
                f"cell {cell}: ingestion paths diverge on an unexpected set — "
                f"new drops {sorted(differing - self.KNOWN_LAUNCHER_DROPS)}, "
                f"resolved {sorted(self.KNOWN_LAUNCHER_DROPS - differing)}"
            )

    def test_the_four_new_switch_keys_never_drop(self):
        """The keys this change introduces must agree on both paths in every
        cell — the whole point of shipping the passthrough in the same commit."""
        for cell in CELL_LETTERS:
            data = json.loads(self._path(cell).read_text(encoding="utf-8"))
            a = RunnerConfig.from_dict(data)
            b = launcher_core.build_runner_config_from_dict(data, _StubArgs())
            for key in NEW_KEYS:
                assert getattr(a, key) == getattr(b, key) == data[key], (
                    f"cell {cell}: {key} — runner={getattr(a, key)!r}, "
                    f"launcher={getattr(b, key)!r}, json={data[key]!r}"
                )

    def test_cell_names_are_distinct(self):
        names = set()
        for cell in CELL_LETTERS:
            data = json.loads(self._path(cell).read_text(encoding="utf-8"))
            names.add(data["experiment_name"])
        assert len(names) == 4

    def test_target_and_panel_identical_across_cells(self):
        keys = ("test_article", "domain", "models", "max_rounds",
                "gamma_alt_threshold", "gamma_alt_consecutive_zero_crit",
                "falsifier_gate_enabled", "apply_fixes_back_enabled",
                "apply_fixes_back_seed", "immune_memory_path")
        ref = json.loads(self._path("D").read_text(encoding="utf-8"))
        for cell in CELL_LETTERS:
            data = json.loads(self._path(cell).read_text(encoding="utf-8"))
            for k in keys:
                assert data[k] == ref[k], f"cell {cell} differs on {k}"

    @pytest.mark.parametrize("cell", CELL_LETTERS)
    def test_cell_prompt_omission_is_real(self, cell):
        """End-to-end on the assembled directive text: each cell's prompt
        contains exactly the sections its design matrix calls for."""
        data = json.loads(self._path(cell).read_text(encoding="utf-8"))
        cfg = launcher_core.build_runner_config_from_dict(data, _StubArgs())
        _DIRECTIVE_OMISSION["factors"] = _suppressed_directive_factors(cfg)
        try:
            out = _apply_directive_omission(
                OPERATIONAL_PATH.read_text(encoding="utf-8"))
        finally:
            _DIRECTIVE_OMISSION["factors"] = ()
        fb_on, dv_on = CELL_MATRIX[cell]
        heads = _h2_headings(out)
        assert any(h.startswith("## 17") for h in heads) is fb_on
        assert any(h.startswith("## §18") for h in heads) is dv_on
