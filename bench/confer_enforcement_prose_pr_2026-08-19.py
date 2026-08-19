#!/usr/bin/env python3
"""Panel review: audit the assistant's Stage 1 findings, then rule on the way forward.

Five-model dispatch under the full CDSFL directive. Independent verdicts, NO compelled
convergence.

WHY THIS BRIEF IS BUILT DIFFERENTLY FROM THE 2026-08-18 DEDUP PANEL
-------------------------------------------------------------------
That panel was briefed with the assistant's DESCRIPTION of the defects. Hours later
one of those descriptions was refuted by re-derivation from source. A panel reasoning
from a description inherits the description's errors, and this project has already
recorded the consequence: on 2026-08-12 the single model that accepted a false premise
returned the worst answer, which is why compelled convergence was retired.

So this brief carries PRIMARY SOURCE — raw code with line numbers, and raw measurement
tables re-derived at dispatch time — and quarantines every assistant claim into a
labelled ledger. The panel is asked to adjudicate the claims AGAINST the source, not to
review the prose.

NEUTRAL FRAMING. Where a claim was made and later replaced, BOTH are presented as
competing claims with equal standing. The brief does not say which the assistant
currently believes. Anchoring a panel toward the reviewer's present position is a known
confound in this project's record.
"""
from __future__ import annotations
import concurrent.futures
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from experiment_11_orchestrator import (  # noqa: E402
    call_claude_cli, call_deepseek, call_openrouter,
)

LOGS = Path(__file__).resolve().parent / "logs" / "confer_enforcement_prose_2026-08-19"
LOGS.mkdir(parents=True, exist_ok=True)

MODELS = [
    ("cx",   "openai/gpt-5.5",                  "openrouter"),
    ("ge",   "google/gemini-3.1-pro-preview",   "openrouter"),
    ("cgpt", "openai/gpt-5.5",                  "openrouter"),
    ("ds",   "deepseek-v4-pro",                 "deepseek"),
    ("cc2",  "opus",                            "claude_cli"),
]

SYSTEM = (
    "You are on a five-model review panel for CDSFL, a research framework that uses "
    "structured Popperian falsification and a multi-model panel to find defects in STEM "
    "artefacts. Biological component names (B-Cell, immune pipeline, NK cell, macrophage, "
    "ouroboros) are ANALOGY ONLY -- module names, not biology.\n\n"
    "CDSFL's founding principle is TOOLS DECIDE, NOT VOTES: a finding is confirmed when "
    "the runner independently re-executes a model-supplied falsifier and observes the "
    "designed failure, never by model agreement. Apply that standard to yourself here: "
    "prefer a claim you can check against the source pack over one that merely sounds "
    "right.\n\n"
    "YOUR JOB IS ADJUDICATION, NOT REVIEW. An assistant (referred to as CC1) spent three "
    "days auditing this harness. Six of its fifteen commits in that window were "
    "corrections of its own prior claims. The founder has therefore asked you to check "
    "CC1's assumptions and findings against primary source, and to recommend the way "
    "forward.\n\n"
    "You are asked for an INDEPENDENT verdict. There is no requirement to agree with the "
    "other panellists and no synthesis step will force convergence -- disagreement is "
    "kept as information. State your strongest falsification of your OWN answer. If you "
    "think a question is malformed, say so and say why.\n\n"
    "If you have file-reading tools, USE THEM: the repository is at "
    "/Users/georgejackson/Developer_Projects/Constraint_Engineering and the primary "
    "source pack below is an extract, not a substitute. Verify rather than accept.\n\n"
    "Do not pad. The founder is dyslexic and reads every word."
)

_REPO = Path(__file__).resolve().parent.parent
_SOURCES = [
    ("THE RUNWAY TRACKER -- the current plan and remaining budget (for Q5)",
     "experimental_notes/RUNWAY_to_BR2_2026-08-18.md"),
]


def _load_sources() -> str:
    out = ["\n\n" + "=" * 78,
           "APPENDED SOURCES. Packs 1 and 2 are EVIDENCE -- raw code and raw",
           "measurements, generated at dispatch time. The note and the tracker are",
           "CC1's PROSE and carry no more authority than the claims above.",
           "=" * 78]
    for label, rel in _SOURCES:
        f = _REPO / rel
        if not f.is_file():
            out.append(f"\n\n### {label}\n[NOT PRESENT ON DISK: {rel}]")
            continue
        out.append(f"\n\n{'=' * 78}\n### {label}\n### source: {rel}\n{'=' * 78}\n")
        out.append(f.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(out)


PROMPT = (_REPO / "bench/logs/confer_enforcement_prose_2026-08-19/BRIEF.md"
          ).read_text(encoding="utf-8") + _load_sources()


def dispatch(name, model_id, route):
    t0 = time.time()
    try:
        if route == "claude_cli":
            resp = call_claude_cli(model_id, SYSTEM, PROMPT, timeout=900, max_retries=2)
        elif route == "deepseek":
            resp = call_deepseek(model_id, SYSTEM, PROMPT)
        else:
            resp = call_openrouter(model_id, SYSTEM, PROMPT)
        ok = bool(resp and resp.strip())
        out = {"model": name, "ok": ok, "chars": len(resp or ""),
               "elapsed_s": round(time.time() - t0, 1), "response": resp or ""}
    except Exception as e:  # noqa: BLE001
        out = {"model": name, "ok": False, "error": f"{type(e).__name__}: {e}",
               "elapsed_s": round(time.time() - t0, 1), "response": ""}
    (LOGS / f"{name}.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"  [{name}] ok={out['ok']} chars={out.get('chars', 0)} {out['elapsed_s']}s"
          + (f" ERR={out.get('error')}" if not out["ok"] else ""))
    return out


def main() -> int:
    print(f"=== enforcement + prose-target panel review (pr) — {len(MODELS)} models ===")
    print(f"  prompt {len(PROMPT):,} chars, system {len(SYSTEM):,} chars")
    print(f"  approx {len(PROMPT) // 4:,} input tokens per model, "
          f"{len(MODELS) * len(PROMPT) // 4:,} total")
    if os.environ.get("CDSFL_DRY_RUN"):
        print("  DRY RUN — nothing dispatched, nothing billed.")
        return 0
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(MODELS)) as pool:
        futs = {pool.submit(dispatch, n, m, r): n for n, m, r in MODELS}
        for f in concurrent.futures.as_completed(futs):
            res = f.result()
            results[res["model"]] = res
    ok = sum(1 for r in results.values() if r["ok"])
    (LOGS / "summary.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\n  {ok}/{len(MODELS)} responded. Logs: {LOGS}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
