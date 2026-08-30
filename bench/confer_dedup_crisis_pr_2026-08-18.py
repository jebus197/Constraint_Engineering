#!/usr/bin/env python3
"""Panel review: duplicate/novelty detection is not measurably working. What now?

Five-model dispatch under the full CDSFL directive. Independent verdicts, NO
compelled convergence — disagreement is preserved as information. Founder
authorised this dispatch explicitly after a week in which the assistant's own
error rate made unilateral conclusions untrustworthy.

The panel is briefed on what has been MEASURED, what has been INFERRED, and what
was CLAIMED AND LATER REFUTED, because the last two times this question went to
models they proposed machinery that had already been built and buried.
"""
from __future__ import annotations
import concurrent.futures, json, os, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from experiment_11_orchestrator import (  # noqa: E402
    call_claude_cli, call_deepseek, call_openrouter,
)

LOGS = Path(__file__).resolve().parent / "logs" / "confer_dedup_crisis_2026-08-18"
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
    "ouroboros) are ANALOGY ONLY — they are module names, not biology.\n\n"
    "CDSFL's founding principle is TOOLS DECIDE, NOT VOTES: a finding is confirmed when the "
    "runner independently re-executes a model-supplied falsifier and observes the designed "
    "failure, never by model agreement.\n\n"
    "You are asked for an INDEPENDENT verdict. There is no requirement to agree with the "
    "other panellists and no synthesis step will force convergence — disagreement is kept as "
    "information. State your strongest falsification of your OWN answer. If you believe the "
    "question is malformed, say so and say why. Do not pad; every word is read and "
    "reads every word."
)

PROMPT = r"""
# THE SITUATION

CDSFL must decide, given two findings produced by different models (or the same model in
different rounds) about the same target document, whether they name THE SAME DEFECT or two
different ones. That judgement feeds a convergence gate. Merge wrongly and a run stops while
genuine defects are still arriving; split wrongly and a run never stops.

Five months of machinery exists for this. An audit this week measured it. The results follow.
Everything marked MEASURED was verified directly against the archive, usually by more than one
route. Everything marked INFERRED was produced by an investigating agent and NOT independently
confirmed — treat it as an indication, not a fact.

## 1. MEASURED: no similarity measure discriminates on the hard cases

85 finding-pairs were labelled by COUNTERFACTUAL REPAIR — apply one finding's proposed fix to
the target, re-run BOTH findings' falsifiers, and see whether the repair cured both (same
defect) or only one (different defects). Both directions must agree. This is tool-decided
ground truth: no opinions, no embeddings, no votes. 40 same / 45 different.

Scored against those 85 labels:

    measure                       same median   different median   AUC
    sentence-embedding cosine        0.784           0.778         0.608
    lexical Jaccard                  0.137           0.125         0.586
    stem-signature Jaccard (tier 2)  0.229           0.346         0.433

Tier 2 is BELOW CHANCE — different-defect pairs score higher than same-defect pairs.

No threshold helps. Sweeping the embedding threshold from 0.50 to 0.72 flags all 85 pairs;
precision stays at 47%, which is exactly the base rate.

IMPORTANT CAVEAT, and it bounds the claim: these 85 are by construction the pairs a
sentence-embedding model REFUSED to call (it labelled confidently above 0.90 and below 0.70,
and abstained between). They are the hard cases. On easy cases these measures do separate.

## 2. MEASURED: the previously reported success was an artefact

Tier 2 was reported at AUC 0.9864. That figure was obtained by grading tier 2 against
sentence-embedding labels. Both measure surface similarity, so they agree with each other.
Against repair-decided ground truth the same measure scores 0.433.

## 3. MEASURED: a five-month regression, with a date and a cause

The immune-verification pipeline passed roughly 944 findings across its first six weeks
(e.g. 268 findings in one run, 412 in another). From a run dated 13 April 2026 onward it has
passed 1-3 findings in round 0 of each run and ZERO in every subsequent round. Verified three
ways: the code path, archived per-round rejection rates across six runs, and a separate
verdict log.

Cause: commit dated 12 April 2026, "Phase 2: Embedding similarity shared backend". The
duplicate detector switched from lexical Jaccard to sentence embeddings. Under embeddings,
UNRELATED findings score a minimum of 0.418 and a median of 0.569 on this corpus. The
duplicate threshold is 0.50. Under Jaccard the same 780 pairs had median 0.026 and maximum
0.347 — nothing reached 0.50.

Consequences, all measured: real tool verdicts are computed then discarded (one run recorded
19 CONFIRMED and 8 REJECTED verdicts from symbolic-mathematics, constraint-solving and
chemical-balance tools; the final verdicts were 38 DUPLICATE, 1 CONFIRMED, 1 UNCERTAIN). The
programmatic fix-verification channel reads from the surviving set and has had nothing to
read. The "verified" counts in reports come from the model's OWN self-reported field. The
health monitor has an explicit carve-out that suppresses the alarm when all removals are
duplicates, so a round rejecting 100% reports healthy.

## 4. MEASURED: the formal model requires a term it never defines

The mathematical appendix defines discovery efficiency as novel(t)/raw(t) where novel(t) is
"the count of findings in round t that are not duplicates of any prior finding" — a semantic
definition. The runner computes it by exact identifier match, comparing no content at all.
The appendix also states that total novel verified findings are a "post-dedup" count.

It never defines what makes two findings the same. Roughly 20 named quantities depend on a
deduplicated count. (An agent counted 23; an independent count found 19; the exact figure is
UNVERIFIED, the class of claim is not.)

Consequence, measured: on one archived run, holding estimator, rounds and population fixed and
changing ONLY the sameness rule, the convergence parameter gamma reads 0.6068 (exact-identifier
matching), 0.6866 (code-location keying), or 0.7701 (a combined rule). The value that actually
gated is 0.6068 — the least-deduplicated of the three.

## 5. MEASURED: the merge machinery has never merged anything

Across all 28 archived registries the alias map has exactly the same length as the entry list:
no canonical entry has EVER acquired a second alias. 287 entries carry status MERGED, but that
marks a finding discarded with a pointer; nothing is folded in. Every model is told each round
that "DUPLICATE -> MERGED into the canonical entry". That has never happened. Merge cycles
exist (21 of 86 merged entries in one run sit in a cycle; another run has a finding merged
into itself at severity 0.86).

## 6. MEASURED: what still works

The panel plus falsifiers find real defects. Of 101 findings in the disputed set, 99 are CLOSED
and 100 carry a CONFIRMED falsifier verdict — produced by the runner executing code, not by any
of the broken machinery. Convergence conclusions survive: 6 of 7 runs converge under BOTH the
loose and the strict novelty relation, and every gamma under both clears its 0.30 threshold.

## 7. THE CLOSED-DOORS LIST — do not re-propose these

- MinHash / SimHash / LSH: proposed twice, tested. The corpus is 165 criticals = 13,530 pairs
  computed exactly in 15 ms; the proposal assumed ~50 million comparisons. Signatures have a
  MEDIAN OF 4 TOKENS, so hashing error plateaus. Reopens only past ~2000 findings per set.
- Sentence-embedding cosine as the identity decider: implemented, live since April, and the
  cause of the regression in section 3.
- A mutation-vector equivalence tier (FELM): built to a previous panel's design, measured at
  Fisher exact p = 0.71 — no association — and removed.
- Raising the duplicate threshold: measured. 0.55 gives a 60% duplicate rate, still rejecting
  the majority. No value separates on the hard cases (section 1).
- A model panel VOTING on whether two findings match: refused on principle. CDSFL is a
  tools-decide harness. Your proposals must be mechanically checkable.

## 8. THE CONSTRAINT ON SCALING

Published work ("nine judges, two effective votes") finds correlated errors between models mean
a nine-model panel behaves statistically like a two-model panel. More models answering the same
question does not buy proportional coverage. Dividing a problem into parts that different
models work on separately is a different and untested axis.

## 9. WHAT IS AVAILABLE TO TEST WITH

About 11 remaining experiment opportunities: 6 built and unrun (two prose exams, four factorial
cells) and 5 proposed (a dedup experiment, a load-balancer shakedown, a clean-control build, a
control re-run, a capstone). Re-running past experiments is not proposed — everything above was
re-derived offline from the archive at zero cost.

# THE QUESTIONS

Answer each. Be specific enough to implement or refute.

Q1. Section 1 says no surface measure separates same-defect from different-defect pairs on the
hard cases. Is that a solvable measurement problem, or evidence that "same defect" is not
decidable from finding text at all? If solvable, propose a MECHANICALLY CHECKABLE
discriminator and say what would falsify it. If not solvable, say what should replace the
attempt.

Q2. The immune pipeline regression (section 3) has a known cause and no known fix, because a
threshold cannot be calibrated on measures that do not separate. What is the correct repair?
Consider: reverting the backend, running both backends, gating on something other than
similarity, or removing the duplicate check from that pipeline entirely.

Q3. The formal model (section 4) requires a deduplicated count and never grounds sameness.
Should the model be amended to define an equality relation, or should the requirement be
weakened to something computable? What are the consequences for gamma-based convergence claims
either way?

Q4. Given roughly 11 remaining experiments and a schema still under construction, what is the
best strategy: fix first and test on the remaining runs, run a dedicated experiment on this
question first, or something else? Where would you spend the runway?

Q5. What have we got wrong in the framing above? Name the strongest objection to this brief.
"""

# ── THE PRIMARY SOURCES ───────────────────────────────────────────────────────
# The founder's instruction, verbatim: the panel needs "the full unvarnished
# technical details of everything that has been uncovered and everything that has
# been discussed regarding this topic. Not simply a summary."
#
# So the framing above is the ORIENTING layer only — what is measured, what is
# inferred, and which doors are closed. Everything below is the primary record,
# unedited: two historical briefs totalling ~1180 lines with file:line citations
# throughout, the adversarial passes that refuted parts of them, and the two
# working notes from this week's repairs. ~219,000 characters, ~61k tokens.
#
# Attaching the sources rather than a digest is deliberate. The last two times
# this question went to models on a summary, the answers re-proposed machinery
# that had already been built and measured dead.
_SOURCES = [
    ("HISTORICAL BRIEF (first sweep, 6 sections, file:line cited)",
     "experimental_notes/Dedup_Historical_Brief_2026-08-17.md"),
    ("ADDENDUM (second sweep: Bugzilla FSM, the mathematical model, spec-vs-implementation, pre-Exp40 history, ouroboros)",
     "experimental_notes/Dedup_Historical_Brief_Addendum_2026-08-18.md"),
    ("ADVERSARIAL PASSES — these REFUTE parts of the sweeps above; where they conflict, the refutation is the later word",
     "experimental_notes/data/dedup_adversarial_checks_2026-08-18.txt"),
    ("WORKING NOTE — the three truncation repairs and the two-defects-masking-each-other result",
     "experimental_notes/Description_Truncation_Three_Fixes_2026-08-17.md"),
    ("WORKING NOTE — the similarity function's operating characteristic, carrying its own dated correction block",
     "experimental_notes/Similarity_Function_Operating_Characteristic_2026-08-16.md"),
]

_REPO = Path(__file__).resolve().parent.parent

def _load_sources() -> str:
    out = ["\n\n" + "=" * 78,
           "PRIMARY SOURCES — the full record, unedited. Read these; the framing",
           "above is orientation, not evidence.",
           "=" * 78]
    for label, rel in _SOURCES:
        f = _REPO / rel
        if not f.is_file():
            out.append(f"\n\n### {label}\n[NOT PRESENT ON DISK: {rel}]")
            continue
        out.append(f"\n\n{'=' * 78}\n### {label}\n### source: {rel}\n{'=' * 78}\n")
        out.append(f.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(out)


PROMPT = PROMPT + _load_sources()

def dispatch(name, model_id, route):
    t0 = time.time()
    try:
        if route == "claude_cli":
            resp = call_claude_cli(model_id, SYSTEM, PROMPT)
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
    print(f"  [{name}] ok={out['ok']} chars={out.get('chars',0)} {out['elapsed_s']}s"
          + (f" ERR={out.get('error')}" if not out["ok"] else ""))
    return out


def main() -> int:
    print(f"=== dedup-crisis panel review (pr) — {len(MODELS)} models ===")
    print(f"  prompt {len(PROMPT):,} chars, system {len(SYSTEM):,} chars")
    if os.environ.get("CDSFL_DRY_RUN"):
        print("  DRY RUN — nothing dispatched.")
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
