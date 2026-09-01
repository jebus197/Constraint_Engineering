"""Tests for the Ouroboros loop-close: brief -> round prompt, retrieval -> c_ext.

The retrieval half of the Ouroboros cell has been real since 12 July 2026 and
was demonstrated live on arXiv 1706.03762. The half after it did not exist:
RECOVERY.md records the cell as "strictly shadow — never reaches a
prompt/c_ext/gamma". These tests cover the step that was missing, and they cover
it IN THE RUNNER, because every control activated in this project in the last
three days passed its own unit tests and then broke on contact with something it
had to live alongside.

What is asserted:

* the brief renders deterministically, dedupes papers, honours the relevance
  floor and the char budget, and returns "" when there is nothing to say;
* ``_run_shadow_cells`` — the real function, with the network stubbed at the
  cell's own fetch boundary — emits the brief section and the (c_ext, nu_k)
  pair ONLY when the experiment's ``_ouroboros`` block opts in;
* the five archival configs that already carry an ``_ouroboros`` block
  (Exp 45-49) do NOT opt in, so re-running them is byte-identical;
* ``_evaluate_sk_for_findings`` at its default arguments reproduces the exact
  R_k the identity path produced before 31 July, and diverges only when a real
  c_ext arrives;
* BOTH config-ingestion boundaries carry the new keys — the silent-drop class
  that has bitten this project three times (feedback_launcher_config_drop);
* the OFF path through the runner's own star prompt builder is byte-identical.

Run:
    python3 -m pytest bench/tests/test_ouroboros_loop_close.py -v
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bench import launcher_core  # noqa: E402
from bench import reference_runner_v3 as rr  # noqa: E402
from bench.ouroboros_cell import (  # noqa: E402
    _BRIEF_BEGIN,
    _BRIEF_END,
    OuroborosCell,
    build_brief_prompt_section,
)


def _brief(title="A Paper", ref="arXiv:1706.03762", rel="HIGH",
           chars=24000, h="abc123def456", target="a target",
           text="the paper says something specific", reader="haiku"):
    return {
        "target": target, "source_ref": ref, "title": title, "via": "arxiv",
        "fulltext_chars": chars, "source_hash": h, "relevance": rel,
        "brief": text, "reader_model": reader, "raw_reader_response": "",
        "elapsed_s": 1.0, "error": "",
    }


# ─────────────────────────────────────────────────────────────────────────────
# 1. The renderer
# ─────────────────────────────────────────────────────────────────────────────


class TestBriefRenderer:

    def test_empty_inputs_render_nothing(self):
        assert build_brief_prompt_section([], 3) == ""
        assert build_brief_prompt_section(None, 3) == ""

    def test_none_relevance_is_not_injected(self):
        """A librarian verdict of NONE means the paper does not bear on the
        target. Injecting it would spend prompt budget to mislead."""
        assert build_brief_prompt_section([_brief(rel="NONE")], 1) == ""

    def test_relevance_floor_is_honoured(self):
        low = [_brief(rel="LOW")]
        assert build_brief_prompt_section(low, 1, min_relevance="LOW") != ""
        assert build_brief_prompt_section(low, 1, min_relevance="MEDIUM") == ""
        assert build_brief_prompt_section(low, 1, min_relevance="HIGH") == ""

    def test_empty_brief_text_is_not_injected(self):
        assert build_brief_prompt_section([_brief(text="   ")], 1) == ""

    def test_block_carries_citation_provenance_and_the_disjoint_rule(self):
        out = build_brief_prompt_section([_brief()], 4)
        assert out.startswith(_BRIEF_BEGIN)
        assert out.rstrip().endswith(_BRIEF_END)
        assert "arXiv:1706.03762" in out          # the citation
        assert "24,000 chars" in out              # what was actually parsed
        assert "abc123def456" in out              # the content hash
        assert "judged by haiku" in out           # who scored the relevance
        assert "disjoint-evidence" in out         # design decision 2
        assert "round 4" in out

    def test_extractive_fallback_is_dropped_by_default(self):
        """The no-LLM fallback scores MEDIUM on any three-word overlap. In the
        first live proof run it rated "Overcoming Catastrophic Forgetting by
        XAI" MEDIUM against a floating-point-cancellation finding, on the word
        "catastrophic" alone. Default behaviour is therefore to inject nothing
        rather than to inject that."""
        recs = [_brief(reader="extractive_fallback")]
        assert build_brief_prompt_section(recs, 1) == ""

    def test_extractive_fallback_is_named_when_explicitly_allowed(self):
        out = build_brief_prompt_section(
            [_brief(reader="extractive_fallback")], 1,
            require_model_reader=False)
        assert "judged by extractive_fallback" in out

    def test_missing_reader_field_is_also_dropped_by_default(self):
        rec = _brief()
        rec.pop("reader_model")
        assert build_brief_prompt_section([rec], 1) == ""

    def test_same_paper_from_two_models_appears_once(self):
        """Two panel models filing the same defect give the cell two identical
        targets, which resolve to the same paper. The first live proof run
        listed it as both [1] and [2]."""
        dup = [_brief(target="model A said X"), _brief(target="model B said X")]
        out = build_brief_prompt_section(dup, 1)
        assert out.count("source_ref:") == 1
        assert "[2]" not in out

    def test_distinct_papers_are_both_kept(self):
        two = [_brief(h="hash_one", ref="arXiv:1"),
               _brief(h="hash_two", ref="arXiv:2")]
        out = build_brief_prompt_section(two, 1)
        assert out.count("source_ref:") == 2

    def test_highest_relevance_first(self):
        recs = [_brief(title="Lo", rel="LOW", h="1"),
                _brief(title="Hi", rel="HIGH", h="2")]
        out = build_brief_prompt_section(recs, 1)
        assert out.index("Hi") < out.index("Lo")

    def test_char_budget_is_never_exceeded(self):
        recs = [_brief(title=f"P{i}", h=str(i), text="x " * 2000)
                for i in range(6)]
        for budget in (1200, 2000, 4000, 8000):
            out = build_brief_prompt_section(recs, 1, max_chars=budget)
            assert len(out) <= budget, f"budget {budget} exceeded: {len(out)}"

    def test_budget_too_small_for_the_header_renders_nothing(self):
        assert build_brief_prompt_section([_brief()], 1, max_chars=100) == ""

    def test_deterministic(self):
        recs = [_brief(h="1"), _brief(h="2", rel="MEDIUM")]
        a = build_brief_prompt_section(recs, 2)
        b = build_brief_prompt_section(recs, 2)
        assert a == b

    def test_newlines_in_finding_text_do_not_break_field_structure(self):
        """Finding descriptions are multi-line. A raw newline inside the
        relevance field would make the block's own structure unparseable."""
        out = build_brief_prompt_section(
            [_brief(target="line one\nline two\nline three")], 1)
        field_lines = [ln for ln in out.splitlines()
                       if ln.strip().startswith("relevance to")]
        assert len(field_lines) == 1
        assert "line one line two line three" in field_lines[0]

    def test_malformed_records_are_skipped_not_fatal(self):
        assert build_brief_prompt_section(["not a dict", None], 1) == ""
        mixed = ["junk", _brief()]
        assert build_brief_prompt_section(mixed, 1) != ""


# ─────────────────────────────────────────────────────────────────────────────
# 2. The cell inside _run_shadow_cells (the real runner function)
# ─────────────────────────────────────────────────────────────────────────────


# Three results, because the Stage 6 query-quality term is q_s = min(1, n/3):
# one result would give q_s = 1/3 and a c_ext the test could not pin.
_FAKE_PAPERS = [
    {"title": "Numerically Stable Streaming Moments", "authors": "A. Author",
     "abstract": "Welford's online update avoids catastrophic cancellation.",
     "url": "http://arxiv.org/abs/1234.56789v1", "published": "2020-01-01"},
    {"title": "A Second Paper", "authors": "B. Author", "abstract": "Second.",
     "url": "http://arxiv.org/abs/2234.56789v1", "published": "2021-01-01"},
    {"title": "A Third Paper", "authors": "C. Author", "abstract": "Third.",
     "url": "http://arxiv.org/abs/3234.56789v1", "published": "2022-01-01"},
]


class _FakeFinding:
    def __init__(self, fid, desc, sev=0.9):
        self.finding_id = fid
        self.description = desc
        self.severity = sev
        self.flaw_class = 5
        self.model_id = "Gemini"
        self.origin_type = "model"
        self.novelty = 0.9


class _FakeImmune:
    def __init__(self, fids):
        self.final_verdicts = {f: "UNCERTAIN" for f in fids}
        self.final_confidences = {f: 0.5 for f in fids}
        self.cell_verdicts = {}
        self.triaged = None
        self.stage_timings = None


@pytest.fixture(autouse=True)
def _reset_shadow_singletons():
    """The runner caches shadow cells in module globals across rounds by
    design. Tests must not inherit one another's Ouroboros."""
    rr._shadow_macrophage = None
    rr._shadow_ouroboros = None
    rr._shadow_stage6_calibrator = None
    yield
    rr._shadow_macrophage = None
    rr._shadow_ouroboros = None
    rr._shadow_stage6_calibrator = None


@pytest.fixture
def no_network(monkeypatch):
    """Stub the cell's own network + download boundary, nothing above it.

    Everything the loop-close touches — target selection, query building,
    _read_and_brief, the extractive reader, the Stage 6 calibrator, the
    rendering, the runner's gating — runs for real.
    """
    monkeypatch.setattr(OuroborosCell, "_query_arxiv",
                        staticmethod(lambda q, max_results=3: list(_FAKE_PAPERS)))
    monkeypatch.setattr(
        OuroborosCell, "_query_semantic_scholar",
        staticmethod(lambda q, max_results=3: list(_FAKE_PAPERS)))
    monkeypatch.setattr(OuroborosCell, "_query_openalex",
                        staticmethod(lambda q, max_results=3: list(_FAKE_PAPERS)))
    monkeypatch.setattr(
        OuroborosCell, "_download_and_extract",
        lambda self, url, timeout_s=20.0: {
            "text": ("Welford's online algorithm updates the mean and the sum "
                     "of squared deviations incrementally, avoiding the "
                     "catastrophic cancellation of the naive sum-of-squares "
                     "variance formula in floating point arithmetic. " * 20),
            "chars": 2400, "content_type": "application/pdf", "error": ""})


def _run(config: Dict[str, Any], round_idx: int = 0, tmp_path=None):
    findings = [_FakeFinding(
        "Gemini_F001",
        "streaming_variance uses the naive sum-of-squares formula which "
        "suffers catastrophic cancellation in floating point arithmetic")]
    immune = _FakeImmune([f.finding_id for f in findings])
    return rr._run_shadow_cells(
        round_idx=round_idx, immune_result=immune, findings=findings,
        exp_config=config, logs_dir=tmp_path)


class TestRunShadowCellsGating:

    def test_no_ouroboros_block_produces_no_wiring(self, no_network, tmp_path):
        out = _run({"_macrophage": {"mode": "patrol"}}, tmp_path=tmp_path)
        assert "_ouroboros_wiring" not in out

    def test_no_shadow_config_at_all_returns_empty(self, no_network, tmp_path):
        assert _run({}, tmp_path=tmp_path) == {}

    def test_ouroboros_block_without_optin_produces_no_wiring(
            self, no_network, tmp_path):
        """This is the archival shape: Exp 45-49 carry an _ouroboros block.
        Their behaviour must not change."""
        out = _run({"_ouroboros": {"api_access": ["arxiv"],
                                   "reader_backend": "none"}},
                   tmp_path=tmp_path)
        assert out["ouroboros"]["queries_issued"] >= 1   # the cell still ran
        assert "_ouroboros_wiring" not in out            # but nothing consumed
        assert "brief_section_chars" not in out["ouroboros"]
        assert "c_ext_consumed" not in out["stage6_calibration"]

    def test_inject_brief_emits_a_section(self, no_network, tmp_path):
        out = _run({"_ouroboros": {"api_access": ["arxiv"],
                                   "reader_backend": "none",
                                   "require_model_reader": False,
                                   "inject_brief": True}},
                   tmp_path=tmp_path)
        section = out["_ouroboros_wiring"]["brief_section"]
        assert _BRIEF_BEGIN in section
        assert "1234.56789" in section          # the paper actually retrieved
        assert out["ouroboros"]["brief_section_chars"] == len(section)

    def test_no_librarian_means_no_injection_by_default(
            self, no_network, tmp_path):
        """Same config, minus the explicit override. reader_backend "none"
        leaves the extractive fallback scoring relevance, and the shipped
        default refuses to put that in front of the panel."""
        out = _run({"_ouroboros": {"api_access": ["arxiv"],
                                   "reader_backend": "none",
                                   "inject_brief": True}},
                   tmp_path=tmp_path)
        assert out["_ouroboros_wiring"]["brief_section"] == ""
        assert out["ouroboros"]["queries_issued"] >= 1   # it did search

    def test_inject_brief_alone_does_not_arm_c_ext(self, no_network, tmp_path):
        """The two halves are independently switchable; turning on the prompt
        must not silently change the maths."""
        out = _run({"_ouroboros": {"api_access": ["arxiv"],
                                   "reader_backend": "none",
                                   "inject_brief": True}},
                   tmp_path=tmp_path)
        assert "c_ext" not in out["_ouroboros_wiring"]

    def test_c_ext_enabled_alone_does_not_arm_the_prompt(
            self, no_network, tmp_path):
        out = _run({"_ouroboros": {"api_access": ["arxiv"],
                                   "reader_backend": "none",
                                   "c_ext_enabled": True}},
                   tmp_path=tmp_path)
        assert "brief_section" not in out["_ouroboros_wiring"]
        assert out["_ouroboros_wiring"]["c_ext"] > 0.0

    def test_c_ext_is_derived_from_the_retrieval_not_invented(
            self, no_network, tmp_path):
        out = _run({"_ouroboros": {"api_access": ["arxiv"],
                                   "reader_backend": "none",
                                   "c_ext_enabled": True}},
                   tmp_path=tmp_path)
        w = out["_ouroboros_wiring"]
        # Stage 6: c_s = r_s * q_s * a_s; arXiv r_s=0.4, 1 source, 3 results
        # -> q_s = 1.0, a_s = 1.0 -> c_ext_raw = 0.4 -> c_ext = 0.7 * 0.4.
        assert w["c_ext"] == pytest.approx(0.28, abs=1e-6)
        assert w["c_ext_uniform"] is True
        assert w["search_status"] == "searched"
        assert "Gemini_F001" in w["nu_k_by_finding"]
        assert 0.0 <= w["nu_k_mean"] <= 1.0

    def test_c_ext_is_in_the_unit_interval(self, no_network, tmp_path):
        """compute_rk_with_eta_channel raises ChannelViolationError outside
        [0,1]; a c_ext that escaped would abort a live run."""
        out = _run({"_ouroboros": {"api_access": ["arxiv", "semantic_scholar",
                                                  "openalex"],
                                   "reader_backend": "none",
                                   "c_ext_enabled": True}},
                   tmp_path=tmp_path)
        c = out["_ouroboros_wiring"]["c_ext"]
        assert 0.0 <= c <= 1.0
        for v in out["_ouroboros_wiring"]["nu_k_by_finding"].values():
            assert 0.0 <= v <= 1.0

    def test_reader_backend_defaults_to_haiku(self, no_network, tmp_path):
        """The new reader_backend key must default to the constructor default
        the cell has always used, or archival configs change behaviour."""
        _run({"_ouroboros": {"api_access": ["arxiv"]}}, tmp_path=tmp_path)
        assert rr._shadow_ouroboros.reader_backend == "haiku"

    def test_a_failing_ouroboros_does_not_arm_half_the_wiring(
            self, monkeypatch, tmp_path):
        """The cell is wrapped in a non-fatal try. If it throws, the runner
        must inject nothing rather than a partly-built section."""
        monkeypatch.setattr(
            OuroborosCell, "run_between_rounds",
            lambda *a, **k: (_ for _ in ()).throw(RuntimeError("network down")))
        out = _run({"_ouroboros": {"api_access": ["arxiv"],
                                   "inject_brief": True,
                                   "c_ext_enabled": True}},
                   tmp_path=tmp_path)
        assert "error" in out["ouroboros"]
        assert not out.get("_ouroboros_wiring", {}).get("brief_section")


# ─────────────────────────────────────────────────────────────────────────────
# 3. c_ext where it enters the maths
# ─────────────────────────────────────────────────────────────────────────────


class _Registry:
    """Minimal stand-in with the two attributes _evaluate_sk_for_findings uses."""

    def __init__(self, entries):
        self.entries = entries


_TOY = "def f(x):\n    return x + 1\n"
_FIX = ("<<<< SEARCH toy.py\n    return x + 1\n====\n"
        "    return x + 2\n>>>> REPLACE\n")


def _entry(aliases):
    return {"status": "OPEN", "proposed_fix": _FIX, "source_aliases": aliases,
            "model_params": {"q": 0.5, "R": 0.5, "nu_b": 0.05, "nu_f": 0.20}}


@pytest.fixture
def sk_case(tmp_path):
    """A registry whose one entry the REAL S_k gate admits.

    The baseline comes from the runner's own ``_capture_baseline`` (a real ruff
    and bandit run). Without it the effect gates report "baseline unavailable",
    S_k tri-states to ESCALATE and never reaches ``compute_rk_with_eta_channel``
    — which would leave the c_ext assertions passing vacuously.
    """
    src = tmp_path / "toy.py"
    src.write_text(_TOY, encoding="utf-8")
    baseline = rr._capture_baseline(_TOY, source_path=str(src))

    def _run_sk(aliases="Gemini_F001", **kw):
        reg = _Registry({"C0001": _entry([aliases])})
        rr._evaluate_sk_for_findings(
            reg, _TOY, str(src), baseline=baseline, round_idx=0, **kw)
        got = reg.entries["C0001"]["sk_result"]
        assert got["tristate"] == "ADMISSIBLE", (
            f"S_k did not admit the fix, so the channel was never reached: "
            f"{got.get('gate_details')}")
        assert "R_new" in got
        return got

    return _run_sk


class TestCExtInTheChannel:

    def test_defaults_reproduce_the_identity_path(self, sk_case):
        """Before 31 July the S_k path passed the literals c_ext=0.0, nu_k=0.0.
        With no Ouroboros the new signature must land on the same R_k."""
        got = sk_case()
        expected = rr.compute_rk(R_old=0.5, q=0.5, sk=got["sk"],
                                 nu_b=0.05, nu_f=0.20)
        assert got["R_new"] == pytest.approx(expected, abs=1e-12)
        assert "c_ext" not in got     # nothing recorded when nothing was used

    def test_real_c_ext_changes_r_k_and_is_recorded(self, sk_case):
        got = sk_case(c_ext=0.28,
                      nu_k_by_finding={"Gemini_F001": 0.2}, nu_k_default=0.2)
        identity = rr.compute_rk(R_old=0.5, q=0.5, sk=got["sk"],
                                 nu_b=0.05, nu_f=0.20)
        assert got["c_ext"] == 0.28
        assert got["nu_k"] == 0.2
        # eta_combined = q * (1 - c_ext*(1 - nu_k)) = 0.5 * (1 - 0.28*0.8)
        assert got["eta_combined"] == pytest.approx(0.388, abs=1e-9)
        assert got["R_new"] != pytest.approx(identity, abs=1e-9)
        # Direction: external corroboration of a NON-novel finding suppresses
        # eta, so less risk is discharged and R_k lands HIGHER.
        assert got["R_new"] > identity

    def test_nu_k_is_joined_through_the_registry_alias(self, sk_case):
        """The calibrator keys on the model's own finding_id; the registry keys
        on canonical id. A broken join would silently use the round mean."""
        got = sk_case(aliases="Codex_F007", c_ext=0.5,
                      nu_k_by_finding={"Codex_F007": 0.77}, nu_k_default=0.11)
        assert got["nu_k"] == 0.77

    def test_unknown_alias_falls_back_to_the_round_mean(self, sk_case):
        got = sk_case(aliases="filed_in_an_earlier_round", c_ext=0.5,
                      nu_k_by_finding={"Codex_F007": 0.77}, nu_k_default=0.11)
        assert got["nu_k"] == 0.11

    def test_out_of_range_c_ext_is_clamped_not_raised(self, sk_case):
        """A calibration change upstream must degrade, not abort a live run
        through ChannelViolationError."""
        got = sk_case(c_ext=1.9,
                      nu_k_by_finding={"Gemini_F001": -3.0}, nu_k_default=0.0)
        assert got["c_ext"] == 1.0
        assert got["nu_k"] == 0.0

    def test_channel_semantics_hold_at_the_documented_corners(self):
        """MATHEMATICAL_APPENDIX: nu_k=0, c_ext=1 -> eta_combined = 0
        (known externally, fully covered search); c_ext=0 -> Stage 6 reduces
        to Stage 5."""
        base = dict(R_old=0.5, sk=0.8, eta_int=0.5, m_div=1.0, d=1.0, p=1.0)
        reduces = rr.compute_rk_with_eta_channel(c_ext=0.0, nu_k=0.7, **base)
        assert reduces == pytest.approx(
            rr.compute_rk(R_old=0.5, q=0.5, sk=0.8), abs=1e-12)
        suppressed = rr.compute_rk_with_eta_channel(c_ext=1.0, nu_k=0.0, **base)
        assert suppressed == pytest.approx(
            rr.compute_rk(R_old=0.5, q=0.0, sk=0.8), abs=1e-12)
        novel = rr.compute_rk_with_eta_channel(c_ext=1.0, nu_k=1.0, **base)
        assert novel == pytest.approx(
            rr.compute_rk(R_old=0.5, q=0.5, sk=0.8), abs=1e-12)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Both config-ingestion boundaries (feedback_launcher_config_drop)
# ─────────────────────────────────────────────────────────────────────────────


_OPTIN = {
    "api_access": ["arxiv"],
    "inject_brief": True,
    "c_ext_enabled": True,
    "brief_max_chars": 2500,
    "brief_min_relevance": "MEDIUM",
    "reader_backend": "none",
}


class _StubArgs:
    resume = False


class TestBothIngestionPaths:

    def test_runner_from_dict_carries_every_key(self):
        cfg = rr.RunnerConfig.from_dict(
            {"experiment_name": "t", "models": ["Gemini"],
             "test_article": "bench/x.py",
             "_ouroboros": dict(_OPTIN)})
        assert cfg.shadow_cell_config["_ouroboros"] == _OPTIN

    def test_launcher_core_carries_every_key(self):
        cfg = launcher_core.build_runner_config_from_dict(
            {"experiment_name": "t", "models": ["Gemini"],
             "test_article": "bench/x.py",
             "_ouroboros": dict(_OPTIN)}, _StubArgs())
        assert cfg.shadow_cell_config["_ouroboros"] == _OPTIN

    def test_the_two_paths_agree(self):
        raw = {"experiment_name": "t", "models": ["Gemini"],
               "test_article": "bench/x.py",
               "_ouroboros": dict(_OPTIN)}
        a = rr.RunnerConfig.from_dict(dict(raw)).shadow_cell_config
        b = launcher_core.build_runner_config_from_dict(
            dict(raw), _StubArgs()).shadow_cell_config
        assert a == b


# ─────────────────────────────────────────────────────────────────────────────
# 5. The archival configs must not have been re-armed
# ─────────────────────────────────────────────────────────────────────────────


def _shipped_configs() -> List[Path]:
    out: List[Path] = []
    for d in sorted(REPO_ROOT.glob("bench/exp*_configs")):
        out.extend(sorted(d.glob("*.json")))
    return out


class TestShippedConfigsUnchanged:

    def test_no_shipped_config_opts_in(self):
        """Exp 44-49 have run and their logs are the project's evidence base.
        A shipped config that opted in would make a re-run non-reproducible."""
        armed = []
        for p in _shipped_configs():
            blk = json.loads(p.read_text(encoding="utf-8")).get("_ouroboros")
            if isinstance(blk, dict) and (
                    blk.get("inject_brief") or blk.get("c_ext_enabled")):
                armed.append(str(p.relative_to(REPO_ROOT)))
        assert armed == [], f"configs armed for the loop-close: {armed}"

    def test_the_five_archival_configs_still_carry_a_plain_block(self):
        """Guards the other direction: if the blocks vanished, this suite would
        pass vacuously while the cell stopped running at all."""
        with_block = [
            p for p in _shipped_configs()
            if isinstance(json.loads(p.read_text(encoding="utf-8"))
                          .get("_ouroboros"), dict)]
        assert len(with_block) >= 5


# ─────────────────────────────────────────────────────────────────────────────
# 6. The OFF path through the runner's own star prompt builder
# ─────────────────────────────────────────────────────────────────────────────


class TestStarPromptOffPath:
    """``_dispatch_round_star`` splices the context prefix before the artifact.
    These assert the splice on the real builder, not on a copy of it."""

    BASE = ("PREAMBLE\n\n=== ARTIFACT: target.py (10 chars) ===\n\n"
            "code here\n\n=== END ARTIFACT ===\n\nProduce your findings now.")

    def _make(self, registry_summary: str) -> str:
        # Mirror of _dispatch_round_star._make_prompt for round_idx > 0.
        star = ("REGISTRY\n\nThis is Round 1. Review the registry above. "
                "File new DISCOVERY findings. Issue VERDICT payloads on "
                "existing entries.\n")
        combined = f"{registry_summary}{star}"
        return self.BASE.replace("=== ARTIFACT:", f"{combined}=== ARTIFACT:")

    def test_empty_section_leaves_the_prompt_byte_identical(self):
        assert self._make("") == self._make("")

    def test_section_lands_before_the_artifact(self):
        section = build_brief_prompt_section([_brief()], 0)
        on = self._make(section)
        off = self._make("")
        assert on != off
        assert on.index(_BRIEF_BEGIN) < on.index("=== ARTIFACT:")
        # Removing the block restores the OFF prompt exactly: the injection is
        # purely additive, it rewrites nothing.
        assert on.replace(section, "") == off


# ─────────────────────────────────────────────────────────────────────────────
# 7. The relay topology carries the brief to every hop
# ─────────────────────────────────────────────────────────────────────────────


class _StubMC:
    def __init__(self, label):
        self.label = label
        self.role = "reviewer"
        self.model_id = "stub"
        self.api = "openrouter"
        self.timeout = 300
        self.secondary_api = None
        self.secondary_model_id = None


class _StubExp:
    def __init__(self, labels):
        self.models = [_StubMC(x) for x in labels]


class _StubBrain:
    def __init__(self, tmp_path):
        self.logs_dir = tmp_path

    def relay(self, round_idx):
        return {}

    relay_directed = relay_conversational = relay


class TestRelayCarriesTheBrief:
    """The arc runs star, so relay is the path most likely to be forgotten.

    ``run_experiment`` prepends the section to ``_relay_prompt`` and hands that
    to ``_dispatch_round_relay`` as its base prompt. These drive the REAL
    ``_dispatch_round_relay`` with the dispatch boundary stubbed, so the
    assertion is on what relay would actually send.
    """

    def _capture(self, monkeypatch, tmp_path, base_prompt):
        seen = {}

        def _rec(mc, mgr, prompt, cdsfl_text, full_code, round_idx,
                 pattern_text, domain, logs_dir, falsifier_gate=False, **kw):
            seen[mc.label] = prompt
            return [], ""

        monkeypatch.setattr(rr, "_dispatch_single_model", _rec)
        cfg = rr.RunnerConfig.from_dict({
            "experiment_name": "relay_t", "test_article": "bench/x.py",
            "models": ["Gemini", "Codex"], "topology": "relay"})
        rr._dispatch_round_relay(
            _StubExp(["Gemini", "Codex"]), None, _StubBrain(tmp_path),
            base_prompt, "CDSFL", "CODE", 1, cfg, registry=None)
        return seen

    def test_brief_reaches_every_relay_model(self, monkeypatch, tmp_path):
        section = build_brief_prompt_section([_brief()], 0)
        assert section
        seen = self._capture(monkeypatch, tmp_path, section + "BASE PROMPT")
        assert set(seen) == {"Gemini", "Codex"}
        for label, prompt in seen.items():
            assert _BRIEF_BEGIN in prompt, f"{label} lost the brief"
            assert _BRIEF_END in prompt

    def test_relay_without_a_brief_is_the_bare_base_prompt(
            self, monkeypatch, tmp_path):
        seen = self._capture(monkeypatch, tmp_path, "BASE PROMPT")
        for prompt in seen.values():
            assert prompt == "BASE PROMPT"
