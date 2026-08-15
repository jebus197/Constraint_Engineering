#!/usr/bin/env python3
"""PROOF that the Ouroboros brief reaches a dispatched prompt, c_ext and gamma.

RECOVERY.md has recorded the Ouroboros cell as "strictly shadow — never reaches
a prompt/c_ext/gamma" since 12 July 2026. The retrieval half was real and was
demonstrated live on arXiv 1706.03762 (24,000 characters parsed and hashed).
The half after it did not exist. A parse count is not proof that a brief reached
a prompt, so this script does not report that the wiring works — it prints the
artefacts that decide the question:

  1. the ACTUAL prompt string handed to the dispatch boundary, with the retrieved
     brief inside it;
  2. c_ext taking a non-zero value derived from that same retrieval, and the
     R_k arithmetic it changes;
  3. the OFF path, byte-diffed against today's prompt;
  4. a REAL retrieval performed during this run — network, live, now.

WHAT IS REAL AND WHAT IS STUBBED (stated up front so nothing is hidden):

  REAL  the full ``run_experiment`` loop in reference_runner_v2 — round loop,
        registry, prompt assembly, ``_run_shadow_cells``, the OuroborosCell
        (live arXiv/OpenAlex/Unpaywall network calls, live PDF download, live
        pypdf parse), the Stage 6 calibrator, ``_evaluate_sk_for_findings``,
        the S_k gates (ruff/bandit), ``compute_rk_with_eta_channel``.
  STUB  ``_dispatch_single_model`` — replaced by a recorder that captures the
        prompt and returns findings parsed by the runner's own
        ``parse_findings`` from a canned response. NO PAID MODEL IS CALLED.
  STUB  ``InsectBrain.run_immune_pipeline`` — returns an offline ImmuneResponse.
        The live pipeline dispatches LLM classifiers and specialist B-Cells,
        which costs money. Its only role here is supplying verdicts; the
        Ouroboros reads UNCERTAIN verdicts to pick research targets, and the
        stub supplies those.
  STUB  the librarian reader backend is set to "none", so the relevance score
        comes from the deterministic extractive fallback rather than a Haiku
        read. The paper text it distils is genuinely downloaded and parsed.
        Because that fallback over-rates, the shipped default refuses to inject
        its briefs at all; the proof config sets require_model_reader=False to
        override that, and the rendered block says "judged by
        extractive_fallback" so the weaker provenance stays visible.

Run:
    python3 bench/tools/prove_ouroboros_loop_close.py
    python3 bench/tools/prove_ouroboros_loop_close.py --skip-standalone-retrieval
"""

from __future__ import annotations

import argparse
import difflib
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bench import reference_runner_v2 as rr  # noqa: E402
from bench.experiment_11_orchestrator import (  # noqa: E402
    ExperimentConfig,
    ModelConfig,
)

BAR = "=" * 78
SUB = "-" * 78


# ─────────────────────────────────────────────────────────────────────────────
# The artefact under review, and the canned panel response about it
# ─────────────────────────────────────────────────────────────────────────────

TARGET_SRC = '''"""Toy target for the Ouroboros loop-close proof."""


def streaming_variance(values):
    """Return the variance of a stream in one pass."""
    n = 0
    total = 0.0
    total_sq = 0.0
    for v in values:
        n += 1
        total += v
        total_sq += v * v
    if n < 2:
        return 0.0
    return (total_sq - total * total / n) / (n - 1)
'''

# One finding, with a SEARCH/REPLACE block the S_k pipeline can actually apply.
# Severity is critical so the finding survives triage into the registry.
#
# The defect is real and has a real literature behind it: the textbook
# sum-of-squares ("naive") variance formula loses catastrophically to
# cancellation when the mean is large relative to the spread, and Welford's
# online update is the standard remedy. That matters here because the query the
# Ouroboros issues is derived by the runner's own _target_to_query FROM THIS
# TEXT — nothing in the harness hands the cell a search term. A defect with a
# real literature therefore produces a topically real retrieval; a defect
# without one produces a topically empty retrieval, which is what the first
# proof run showed and what the query-quality caveat below records.
CANNED_RESPONSE = """FINDING_ID: F001
SEVERITY: 0.9
FLAW_CLASS: 5
ABSTRACTION_INDEX: 0.3
FIND: streaming_variance uses the naive sum-of-squares formula, which suffers
catastrophic cancellation in floating point numerical stability when the mean is
large relative to the standard deviation. Welford online algorithm avoids it.
FOLLOW: every caller receives a variance that can be negative or zero for
well-conditioned data; downstream standard deviations then raise on sqrt.
ANALYSE: HARD constraint (mathematics: floating-point cancellation is not a
style preference). Premise: total_sq and total*total/n become nearly equal.
Premise: their difference loses most significant digits. Conclusion: CONFIRMED.
FIX: replace the two-accumulator form with Welford's online update.
<<<< SEARCH toy_target.py
    if n < 2:
        return 0.0
    return (total_sq - total * total / n) / (n - 1)
====
    if n < 2:
        return 0.0
    mean = total / n
    m2 = 0.0
    prev_mean = 0.0
    count = 0
    for v in values:
        count += 1
        prev_mean = mean
        mean = prev_mean + (v - prev_mean) / count
        m2 += (v - prev_mean) * (v - mean)
    return m2 / (count - 1)
>>>> REPLACE
FALSIFICATION: FALSIFIER — if streaming_variance([1e9, 1e9 + 1, 1e9 + 2])
returned 1.0 the cancellation claim would be disproved. ATTEMPT — evaluated the
naive expression in double precision. RESULT — it returns 0.0, so the falsifier
is not satisfied and the finding stands.
CORROBORATION: R_old=0.50, eta=0.80, d=0.70, p=0.60, S_k=0.75, nu_eff=0.15
R_k = 0.50 * (1 - 0.80*0.70*0.60) * 0.75 + 0.15 = 0.32
ADMISSIBILITY: S_min: PASS (location=toy_target.py:14, mechanism=catastrophic
cancellation, evidence=direct evaluation)
G-completeness: PASS
d_tool: PASS (python evaluated both forms)
sigma_measured: PASS (pre-fix: returns 0.0; post-fix: returns 1.0)
q_retest: PASS
NOVELTY: nu_k: 0.15 - Welford 1962 is textbook
c_ext: 0.0 - no external search performed by me
H/H_max: 0.40
VERIFIED: TRUE
"""


# ─────────────────────────────────────────────────────────────────────────────
# Offline stubs (see module docstring)
# ─────────────────────────────────────────────────────────────────────────────


def _offline_immune_response(findings: List[Any], domain: str) -> Any:
    """Build a real ImmuneResponse without dispatching any model.

    Every finding is marked UNCERTAIN. That is the Ouroboros's documented
    research trigger (``_select_targets``), so this is the state in which the
    cell is supposed to go and read the literature.
    """
    from bench.immune_agents import ImmuneResponse

    fids = [f.finding_id for f in findings]
    return ImmuneResponse(
        triaged=[],
        cell_verdicts={},
        final_verdicts={fid: "UNCERTAIN" for fid in fids},
        final_confidences={fid: 0.5 for fid in fids},
        filtered_findings=list(findings),
        rejected_findings=[],
        rejection_rate=0.0,
        autoimmune_flag=False,
        stage_timings={},
        tool_usage={},
        observation_only=False,
        domain=domain,
    )


class PromptRecorder:
    """Stands in for ``_dispatch_single_model`` and keeps every prompt."""

    def __init__(self) -> None:
        self.prompts: List[Dict[str, Any]] = []

    def __call__(self, mc, mgr, prompt, cdsfl_text, full_code, round_idx,
                 pattern_text, domain, logs_dir, falsifier_gate=False, **kw):
        self.prompts.append({
            "round": round_idx,
            "model": mc.label,
            "prompt": prompt,
            "cdsfl_chars": len(cdsfl_text or ""),
        })
        findings = rr.parse_findings(mc.label, round_idx, CANNED_RESPONSE)
        return findings, CANNED_RESPONSE

    def get(self, round_idx: int, model: str) -> str:
        for p in self.prompts:
            if p["round"] == round_idx and p["model"] == model:
                return p["prompt"]
        raise KeyError(f"no prompt captured for round {round_idx} / {model}")

    def first_with_brief(self, model: str) -> int:
        """Earliest captured round whose prompt carries the brief block.

        The cell runs BETWEEN rounds and only retrieves once a round has left
        something UNCERTAIN, so which round first carries a brief depends on
        what the panel filed — it is not fixed at round 1. Returns -1 if none.
        """
        from bench.ouroboros_cell import _BRIEF_BEGIN
        for p in sorted(self.prompts, key=lambda x: x["round"]):
            if p["model"] == model and _BRIEF_BEGIN in p["prompt"]:
                return p["round"]
        return -1


# ─────────────────────────────────────────────────────────────────────────────
# Harness
# ─────────────────────────────────────────────────────────────────────────────


def _make_configs(workdir: Path, ouroboros_block: Dict[str, Any] | None,
                  name: str) -> Tuple[ExperimentConfig, str, "rr.RunnerConfig"]:
    target = workdir / "toy_target.py"
    target.write_text(TARGET_SRC, encoding="utf-8")

    raw: Dict[str, Any] = {
        "experiment_name": f"ouroboros_proof_{name}",
        "test_article": str(target),
        "context_files": [],
        "models": ["Gemini", "Codex"],
        "topology": "star",
        "domain": "code",
        "max_rounds": 3,
        "extension_cap": 3,
        "earliest_stop_round": 99,     # never converge early; we want round 1
        "consecutive_rounds_required": 99,
        "sk_enabled": True,
        "test_cmd": None,
        "hil_review": False,
    }
    if ouroboros_block is not None:
        raw["_ouroboros"] = ouroboros_block

    # BOTH config-ingestion boundaries are exercised: this proof uses the
    # runner's own from_dict; test_ouroboros_loop_close.py asserts the
    # launcher_core path carries the same keys (the silent-drop class that has
    # bitten this project three times).
    cfg = rr.RunnerConfig.from_dict(raw)

    models = [
        ModelConfig(label="Gemini", model_id="stub", api="openrouter",
                    role="reviewer", system_prompt_path=None),
        ModelConfig(label="Codex", model_id="stub", api="openrouter",
                    role="reviewer", system_prompt_path=None),
    ]
    exp_config = ExperimentConfig(models=models)
    return exp_config, "CDSFL DIRECTIVE (stub for the proof harness)\n", cfg


class _ProtectFingerprints:
    """Restore bench/fingerprints/*.json after a proof run.

    ``run_experiment`` persists per-model prompt/throughput fingerprints, which
    later runs read to size context budgets. A proof harness driving stub models
    would otherwise write nonsense into real project state — caught when the
    first run left five fingerprint files dirty in git.
    """

    DIR = REPO_ROOT / "bench" / "fingerprints"

    def __enter__(self):
        self._saved = {p: p.read_bytes() for p in self.DIR.glob("*.json")}
        return self

    def __exit__(self, *exc):
        for p, blob in self._saved.items():
            if p.read_bytes() != blob:
                p.write_bytes(blob)
        for p in self.DIR.glob("*.json"):
            if p not in self._saved:
                p.unlink()
        return False


def run_leg(workdir: Path, ouroboros_block: Dict[str, Any] | None,
            name: str) -> Tuple[PromptRecorder, Dict[str, Any]]:
    """Run the real ``run_experiment`` loop with the dispatch boundary stubbed."""
    import bench.insect_brain as insect_brain

    exp_config, cdsfl_text, cfg = _make_configs(workdir, ouroboros_block, name)

    recorder = PromptRecorder()
    real_dispatch = rr._dispatch_single_model
    real_immune = insect_brain.InsectBrain.run_immune_pipeline

    def _immune_stub(self, findings, observation_only=False):
        return _offline_immune_response(findings, getattr(cfg, "domain", ""))

    # Shadow-cell singletons persist across runs by design; reset so the two
    # legs of this proof do not share an Ouroboros or a calibrator.
    rr._shadow_macrophage = None
    rr._shadow_ouroboros = None
    rr._shadow_stage6_calibrator = None

    rr._dispatch_single_model = recorder
    insect_brain.InsectBrain.run_immune_pipeline = _immune_stub
    try:
        with _ProtectFingerprints():
            result = rr.run_experiment(exp_config, cdsfl_text, cfg)
    finally:
        rr._dispatch_single_model = real_dispatch
        insect_brain.InsectBrain.run_immune_pipeline = real_immune
    return recorder, result


# ─────────────────────────────────────────────────────────────────────────────
# Proof steps
# ─────────────────────────────────────────────────────────────────────────────


def step1_real_retrieval(offline: bool) -> Dict[str, Any] | None:
    """A real paper, fetched now, parsed now — before any prompt is built."""
    print(BAR)
    print("STEP 1 — REAL RETRIEVAL, PERFORMED NOW")
    print(BAR)
    if offline:
        print("skipped by flag (the two run legs below still retrieve "
              "live).\n")
        return None

    from bench.ouroboros_cell import OuroborosCell

    cell = OuroborosCell(
        shadow=True,
        allowed_sources=["arxiv"],
        reader_backend="none",          # no paid read; extractive fallback
        contact_email="cdsfl-ouroboros@constraint-engineering.local",
    )
    queries = cell._build_queries([
        "uncertain_finding:naive sum-of-squares variance suffers catastrophic "
        "cancellation in floating point; Welford online algorithm numerical "
        "stability"])
    metadata = cell._fetch_metadata(queries)
    briefs = cell._read_and_brief(queries, metadata)

    for m in metadata:
        print(f"  query      : {m['query']!r}")
        print(f"  source     : {m['source']}  via={m.get('fetched_via')}  "
              f"status={m['status']}  results={m['results_count']}")
    if not briefs:
        print("  NO BRIEF PRODUCED — network unavailable or no OA full text.\n")
        return None
    for b in briefs:
        print(f"  paper      : {b['title'][:90]}")
        print(f"  source_ref : {b['source_ref']}")
        print(f"  retrieval  : via={b['via']}  fulltext_chars={b['fulltext_chars']:,}")
        print(f"  sha256     : {b['source_hash'][:32]}")
        print(f"  relevance  : {b['relevance']}")
        print(f"  brief      : {' '.join(b['brief'].split())[:400]}")
        print(f"  error      : {b['error'] or '(none)'}")
    print()
    return {"metadata": metadata, "briefs": briefs}


def _locate(prompt: str) -> Tuple[int, int]:
    from bench.ouroboros_cell import _BRIEF_BEGIN, _BRIEF_END
    a = prompt.find(_BRIEF_BEGIN)
    b = prompt.find(_BRIEF_END)
    return a, (b + len(_BRIEF_END) if b >= 0 else -1)


def step2_prompt(recorder: PromptRecorder, round_idx: int) -> str:
    print(BAR)
    print(f"STEP 2 — THE ACTUAL PROMPT AT THE DISPATCH BOUNDARY "
          f"(round {round_idx}, Gemini)")
    print(BAR)
    prompt = recorder.get(round_idx, "Gemini")
    a, b = _locate(prompt)
    print("Captured inside reference_runner_v2._dispatch_single_model — the "
          "last call before the model API.")
    print(f"Prompt length: {len(prompt):,} chars. "
          f"Brief block at offset {a:,}..{b:,}.\n")
    if a < 0:
        print("*** NO BRIEF BLOCK IN THE PROMPT — the wiring did not fire. ***\n")
        return prompt

    # Print the prompt around the brief: enough before and after to show the
    # brief is inside the dispatched text, not appended to a log line.
    head_from = max(0, a - 1200)
    print(SUB)
    print(f"[prompt bytes {head_from:,}..{a:,} — what precedes the brief]")
    print(SUB)
    print(prompt[head_from:a])
    print(SUB)
    print(f"[prompt bytes {a:,}..{b:,} — THE RETRIEVED BRIEF, VERBATIM]")
    print(SUB)
    print(prompt[a:b])
    print(SUB)
    print(f"[prompt bytes {b:,}..{min(len(prompt), b + 1200):,} — what follows]")
    print(SUB)
    print(prompt[b:b + 1200])
    print()
    return prompt


def step3_c_ext(result: Dict[str, Any], workdir: Path, name: str) -> None:
    print(BAR)
    print("STEP 3 — c_ext ENTERING THE MATHS")
    print(BAR)

    rounds = result.get("rounds", [])
    shown = False
    for rnd in rounds[:1]:
        cal = (rnd.get("shadow_cells") or {}).get("stage6_calibration", {})
        sk = rnd.get("sk_pipeline") or {}
        if "c_ext_consumed" not in cal:
            continue
        shown = True
        c_ext = cal["c_ext_consumed"]
        print(f"round {rnd.get('round')}: Stage 6 calibrator computed "
              f"c_ext = {c_ext:.4f} from the retrieval above")
        print(f"           mean nu_k proxy = {cal.get('mean_nu_k_proxy')}")
        for cid, res in (sk.get("results") or {}).items():
            if "c_ext" not in res:
                continue
            ce, nk = float(res["c_ext"]), float(res["nu_k"])
            print(f"\n  registry entry {cid}:")
            print(f"    S_k        = {res.get('sk')}   (A={res.get('A')}, "
                  f"E={res.get('E')})")
            print("    the channel: eta_combined = eta_int * "
                  "(1 - c_ext*(1 - nu_k))")
            print(f"                 {res.get('eta_combined')} = 0.5 * "
                  f"(1 - {ce}*(1 - {nk}))")
            print(f"                 c_ext={ce} is the ONLY term here that "
                  f"came from the retrieval;")
            print("                 before this change the runner passed the "
                  "literal 0.0.")
            print(f"    R_old      = {res.get('R_old')}  ->  "
                  f"R_new = {res.get('R_new')}")
            _counterfactual(res)
    if not shown:
        print("No c_ext was consumed in this run (no admissible S_k entry, or "
              "the retrieval returned nothing).")
    print()


def _counterfactual(res: Dict[str, Any]) -> None:
    """Same entry, same S_k, c_ext forced to 0 — the pre-31-July path."""
    from bench.reference_runner_v2 import compute_rk_with_eta_channel

    q, R_old, sk = 0.5, 0.5, float(res.get("sk", 0.0))
    c_ext, nu_k = float(res["c_ext"]), float(res["nu_k"])
    off = compute_rk_with_eta_channel(
        R_old=R_old, sk=sk, eta_int=q, m_div=1.0,
        c_ext=0.0, nu_k=0.0, d=1.0, p=1.0)
    on = compute_rk_with_eta_channel(
        R_old=R_old, sk=sk, eta_int=q, m_div=1.0,
        c_ext=c_ext, nu_k=nu_k, d=1.0, p=1.0)
    print(f"    counterfactual on the same numbers "
          f"(R_old={R_old}, q={q}, S_k={sk}):")
    print(f"      c_ext=0 (the path before this change) -> R_k = {off:.6f}")
    print(f"      c_ext={c_ext} nu_k={nu_k} (this run)  -> R_k = {on:.6f}")
    print(f"      delta = {on - off:+.6f}")


def step4_off_path(on_prompt: str, off_prompt: str, round_idx: int) -> bool:
    print(BAR)
    print(f"STEP 4 — THE OFF PATH: NO _ouroboros BLOCK (same round {round_idx})")
    print(BAR)
    identical = on_prompt == off_prompt
    print(f"ON  prompt: {len(on_prompt):,} chars")
    print(f"OFF prompt: {len(off_prompt):,} chars")
    print(f"byte-identical: {identical}")
    if identical:
        print("*** The ON prompt carries no brief — the wiring did not fire. ***\n")
        return False

    diff = list(difflib.unified_diff(
        off_prompt.splitlines(keepends=True),
        on_prompt.splitlines(keepends=True),
        fromfile=f"round{round_idx}_prompt_OFF (no _ouroboros block)",
        tofile=f"round{round_idx}_prompt_ON  (_ouroboros.inject_brief=true)",
        n=2))
    added = [ln for ln in diff if ln.startswith("+") and not ln.startswith("+++")]
    removed = [ln for ln in diff if ln.startswith("-") and not ln.startswith("---")]
    print(f"unified diff: {len(added)} line(s) added, "
          f"{len(removed)} line(s) removed\n")
    print(SUB)
    sys.stdout.write("".join(diff))
    print(SUB)
    print()
    return len(removed) == 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-standalone-retrieval", action="store_true",
                    dest="offline",
                    help="skip STEP 1 only; the two run legs still retrieve live")
    ap.add_argument("--keep", action="store_true", help="keep the work dir")
    args = ap.parse_args()

    os.environ.setdefault("CDSFL_QUIET", "1")

    step1_real_retrieval(args.offline)

    workdir = Path(tempfile.mkdtemp(prefix="ouroboros_proof_"))
    try:
        print(BAR)
        print("RUNNING THE REAL run_experiment LOOP — ON leg (live retrieval)")
        print(BAR)
        rec_on, res_on = run_leg(
            workdir, {
                "api_access": ["arxiv"],
                "inject_brief": True,
                "c_ext_enabled": True,
                "brief_max_chars": 3000,
                "brief_min_relevance": "LOW",
                # No paid librarian in a proof harness, so the relevance score
                # comes from the extractive fallback and the shipped default
                # would (correctly) refuse to inject it. Overridden HERE, in
                # the proof only, so the prompt has something to show; the
                # block itself prints "judged by extractive_fallback" so the
                # weaker provenance is visible in the artefact, not hidden.
                "reader_backend": "none",
                "require_model_reader": False,
            }, "ON")
        print()

        print(BAR)
        print("RUNNING THE REAL run_experiment LOOP — OFF leg (no _ouroboros block)")
        print(BAR)
        rec_off, res_off = run_leg(workdir, None, "OFF")
        print()

        r = rec_on.first_with_brief("Gemini")
        if r < 0:
            print("*** NO CAPTURED PROMPT CARRIES A BRIEF — wiring did not "
                  "fire in any round. ***")
            r = max(p["round"] for p in rec_on.prompts)
        on_prompt = step2_prompt(rec_on, r)
        step3_c_ext(res_on, workdir, "ON")
        off_prompt = rec_off.get(r, "Gemini")
        ok = step4_off_path(on_prompt, off_prompt, r)

        print(BAR)
        print("VERDICT")
        print(BAR)
        a, _ = _locate(on_prompt)
        print(f"  brief inside the dispatched prompt : {a >= 0} (round {r})")
        print(f"  OFF prompt differs only by additions: {ok}")
        cons = any("c_ext_consumed" in
                   ((r.get("shadow_cells") or {}).get("stage6_calibration", {}))
                   for r in res_on.get("rounds", []))
        print(f"  c_ext consumed by the R_k channel  : {cons}")
        return 0 if (a >= 0 and ok) else 1
    finally:
        # The runner writes logs under bench/logs/<experiment_name>_<ts>.
        # bench/logs is archival ground; the proof cleans up after itself.
        if not args.keep:
            for d in (REPO_ROOT / "bench" / "logs").glob("ouroboros_proof_*"):
                shutil.rmtree(d, ignore_errors=True)
            shutil.rmtree(workdir, ignore_errors=True)
        else:
            print(f"\nwork dir kept: {workdir}")
            for d in sorted((REPO_ROOT / "bench" / "logs")
                            .glob("ouroboros_proof_*")):
                print(f"run logs kept: {d}")


if __name__ == "__main__":
    raise SystemExit(main())
