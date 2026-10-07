"""Routing — capability-aware falsifier resolution for falsification.

When the falsifier gate leaves a CRITICAL finding un-confirmed (a weak model wrote
a broken or missing falsifier), the system should NOT immediately escalate to a
human, and should NOT endlessly re-ask the weak model to do work it has
demonstrably failed. Instead, route the falsification to progressively STRONGER
models (ordered by capability fingerprint) with the execute_python tool loop —
the stronger models take over the falsification — and only escalate to HIL if even
the strongest writer cannot resolve it (a genuinely-hard, e.g. nondeterministic,
defect). This restores the capability-aware routing that the flat parallel
dispatch had collapsed into identical treatment: weak models find, strong models
adjudicate.

Empirical basis (2026-06-07, the 7 hardest Exp-42 residuals; weak SOURCE models
resolved 0/7):
  * strong model (gpt-5.5) + execute_python tool loop  -> 6/7 CONFIRMED
  * the remaining one (C0063, a markdown-code-block embedding trap) is resolved by
    the next, stronger rung (opus-class) -> the 2-rung ladder reaches 7/7.
  * teaching the weak model with worked examples lifted it only 0/5 -> 1/3 — a
    marginal booster, not a cure: hence routing, not re-asking.

This module is deliberately runner-agnostic and side-effect-free: the caller
injects how to dispatch a model (`resolve_fn`), how the runner decides a verdict
(`reverify_fn`), and how to measure finding similarity (`similarity_fn`). That
keeps it unit-testable in isolation and lets the runner wire it at the single
call site after ``apply_falsifier_verdicts``.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Sequence


# Capability ordering for the FALSIFICATION task, strongest first. Ordered by the
# Exp-42 EMPIRICAL falsifier-confirm rates, not generic capability: Codex 90% / 0
# residuals (and fast — OpenRouter) leads, then CC2 75% / 0 residuals (strong but
# claude_cli-slow), ChatGPT 67%, Gemini 80%-but-format-fragile, DeepSeek 28% /
# 10-of-15-residuals last. Validated ladder: gpt-5.5 (Codex) resolved 6/7 of the
# hardest residuals; CC2 picks up the 7th (the markdown-embedding trap). The
# primary offender (DeepSeek) is last and is never asked to take over routing.
# ★ DO NOT RE-DERIVE THIS ORDER FROM A RUN WITHOUT CHECKING FALSIFIER PROVENANCE
# (founder observation, 2026-08-23, raised by neither external reviewer). This order
# is not a report — it decides which model is asked to resolve the hardest findings,
# so a contaminated confirm rate contaminates the MECHANICS, not just the write-up.
#
# THE ORDER ABOVE IS SOUND: Exp 42's target was `composer.py`, and a code falsifier
# reaches its target by `import`, which PYTHONPATH carries regardless of working
# directory. The gate's empty-working-directory defect (H08) could not touch it.
#
# THE HAZARD IS FORWARD-LOOKING AND WAS MEASURED. On Exp 55, a prose target, while
# that defect was live: Gemini 2 of 2 CONFIRMED with both falsifiers DETACHED (they
# open nothing and restate the document's numbers from memory); DeepSeek 0 of 2 with
# both falsifiers genuine readers that ERRORed on the missing file. Re-deriving from
# that run promotes Gemini to FIRST and demotes DeepSeek to LAST — ranking the models
# by their willingness to ignore the evidence, which is the precise inversion the
# discrimination control exists to detect.
#
# Run `python3 scripts/competence_provenance.py <report.json>` first. It exits 2 and
# prints UNSAFE TO RANK ON when a model's confirmations rest on falsifiers that never
# read the target.
# FABLE ADDED 2026-10-07 ON THE FOUNDER'S RULING: *"Then why not name the model?
# Is it Fable? Then yes we should add it."* It is a FREE seat on `claude_cli` and
# was the only seat in the panel roster absent from this ladder.
#
# ITS POSITION IS DERIVED FROM EVIDENCE, NOT CHOSEN BY NAME, which is the whole
# point of his standing rule that *"the only thing that should impact on
# capability is measured capability"*. Fable has 0 attributed falsifiers in the
# archive, so its lower confidence bound on resolve-rate is 0.0000 and it sorts
# LAST. It climbs as it earns attempts -- a seat needs 12 consecutive successes
# before its Wilson lower bound can pass a seat sitting at 60 of 70, which is the
# arithmetic form of his guard that *"simply counting when a model is successful"*
# is not an improvement in capability.
#
# PLACING IT LAST IS ALSO THE SAFE PLACEMENT, and that is measured rather than
# assumed. `resolve_fn` returns "" for any label absent from the config's own
# `models` roster, and the rung is still CONSUMED -- `route` slices
# `list(rungs)[:_budget]`. No config declares Fable today (46 CC2, 46 Codex,
# 46 ChatGPT, 45 Gemini, 45 DeepSeek, 0 Fable across the 47 files), so an early
# placement would burn one of the 2 capped rungs on a seat that cannot answer.
# Last, it costs nothing under the cap and is reached under exhaustion.
#
# THE OTHER HALF IS NOT DONE AND IS THE FOUNDER'S TO RULE ON: until a config
# lists Fable in `models`, this rung is reachable only where a roster declares
# it. Changing 23 routed configs alters what real experiments dispatch.
DEFAULT_FALSIFIER_STRENGTH = ("Codex", "CC2", "ChatGPT", "Gemini", "DeepSeek", "Fable")


@dataclass
class RoutingResult:
    """Outcome of a routing attempt on one un-confirmed critical."""
    finding_id: str
    verdict: str                      # CONFIRMED / REFUTED / ERROR / UNTOOLABLE / DUPLICATE
    resolved: bool                    # True iff a strong writer CONFIRMED it
    model_used: Optional[str]         # which rung resolved/last-tried it
    falsifier_code: str               # the resolving (or last) falsifier
    duplicate_of: Optional[str] = None  # set iff resolved as a duplicate
    rungs_tried: int = 0
    #: True iff `rank_falsifier_writers` returned NOTHING -- the roster carries no
    #: writer other than this finding's own source model.
    #:
    #: ADDED 2026-10-06 BECAUSE THE SELF-RUNG BROKE ITS PROXY. The runner used
    #: `rungs_tried == 0` to mean "the ladder was empty by construction", which was
    #: exact while every rung came from the ranked list. The self-rung dispatches
    #: when that list is empty, so `rungs_tried` becomes 1 and the discriminator
    #: silently stopped firing -- the finding then missed `routing_deferred`, never
    #: entered `irreducible_queue_count`, and HALTED_IRREDUCIBLE_QUEUE_ALARM could
    #: not fire. That alarm is the pre-registered reportable outcome of the exp56
    #: 1-seat arm. A proxy that was exact under the old mechanics is the first
    #: thing a new mechanic breaks, so the fact is recorded directly instead.
    ladder_was_empty: bool = False


def rank_falsifier_writers(
    labels: Sequence[str],
    strength_order: Sequence[str] = DEFAULT_FALSIFIER_STRENGTH,
    exclude: Sequence[str] = (),
) -> list[str]:
    """Return the available model labels ordered strongest-first for falsification.

    Models not in ``strength_order`` are appended (in input order) after the ranked
    ones — unknown models are tried, but only after the known-strong ones. ``exclude``
    drops models (e.g. the finding's own source model, which already failed)."""
    # A ``-SIM`` label RANKS AS ITS VENDOR (Fable, second-pass review
    # 2026-08-30). `strength_order` holds bare vendor names, and this matched
    # labels exactly, so with a simulated panel `ranked` came out EMPTY and all
    # six members fell into `extras` in panel order. Routing still ran, but it
    # exercised the unknown-model fallback instead of the ranked ladder Bench
    # Run 2 will run -- so ladder ORDER was unrehearsed by every simulation.
    #
    # Normalised locally rather than importing `base_model_label`, which lives
    # in reference_runner_v3 and would make this module import its own caller.
    def _base(m: str) -> str:
        m = str(m or "")
        return m[:-4] if m.endswith("-SIM") else m

    excl = set(exclude)
    by_base = {}
    for m in labels:
        by_base.setdefault(_base(m), []).append(m)
    ranked = [m for name in strength_order
              for m in by_base.get(name, []) if m not in excl]
    ranked_set = set(ranked)
    extras = [m for m in labels if m not in ranked_set and m not in excl]
    return ranked + extras


def confirmed_duplicate(
    finding: dict,
    confirmed_findings: Sequence[dict],
    similarity_fn: Callable[[dict, dict], float],
    threshold: float = 0.85,
) -> Optional[str]:
    """If an already-CONFIRMED finding describes the same defect, return its id.

    This catches the C0028<->C0003 / C0015<->C0001 case from Exp 42, where the same
    real defect was independently CONFIRMED under another id by a competent writer,
    while the weak model's restatement escalated only because ITS falsifier was
    broken. A duplicate of a confirmed defect must never reach HIL."""
    best_id, best_sim = None, threshold
    fid = finding.get("finding_id") or finding.get("id")
    for other in confirmed_findings:
        oid = other.get("finding_id") or other.get("id")
        if oid == fid:
            continue
        sim = similarity_fn(finding, other)
        if sim >= best_sim:
            best_id, best_sim = oid, sim
    return best_id


def resolve_via_routing(
    finding: dict,
    rungs: Sequence[str],
    resolve_fn: Callable[[str, dict], str],
    reverify_fn: Callable[[str], str],
    max_rungs: int = 2,   # 0 = exhaust the ladder
    self_rung: str | None = None,
) -> RoutingResult:
    """Climb the capability ladder until a strong writer CONFIRMS the finding.

    ``rungs``       — model labels, strongest first (from ``rank_falsifier_writers``).
    ``resolve_fn``  — (model_label, finding) -> falsifier_code. The caller dispatches
                      that model WITH the execute_python tool loop and extracts the
                      final falsifier. Empty string means the model produced none.
    ``reverify_fn`` — falsifier_code -> verdict. The runner's real decider
                      (falsifier_verify.reverify_falsifier). It, never the model,
                      decides the verdict — "tools decide".

    Returns a RoutingResult. ``resolved`` is True only on a CONFIRMED from the
    decider; otherwise the caller escalates to HIL with the diagnosis intact.
    A REFUTED here is NOT trusted to drop the critical (CONFIRM-only still holds):
    it just means this rung did not demonstrate it; we try the next rung, then HIL.
    """
    fid = finding.get("finding_id") or finding.get("id") or "?"
    last_verdict, last_code, last_model, tried = "UNTOOLABLE", "", None, 0
    # `max_rungs=0` MEANS EXHAUST THE LADDER. Founder ruling 2026-10-06: *"I don't
    # think there should be a cap at all. If it's a measured statistic, along with
    # capability fingerprinting then the problem should run until it is either
    # resolved, or the ladder is exhausted. (No more models to try.)"*
    #
    # The budget is NOT free, and the honest accounting is that it is nearly free
    # HERE: `resolve_via_routing` stops at the first CONFIRMED, so a deeper budget
    # costs a dispatch only on findings every earlier rung already failed. Measured
    # on the Exp 42 residual set the ladder was validated against, rung 1 resolved
    # 6 of 7 and rung 2 the last, so rungs 3+ are reached on a small minority.
    # A cap is therefore spend-insurance against a pathological run rather than a
    # routine saving, which is why exhaustion is now expressible.
    _ladder_empty = not list(rungs)
    _budget = len(list(rungs)) if not max_rungs else max_rungs
    for model in list(rungs)[:_budget]:
        tried += 1
        last_model = model
        code = (resolve_fn(model, finding) or "").strip()
        last_code = code
        if not code:
            last_verdict = "ERROR"
            continue
        verdict = reverify_fn(code)
        last_verdict = verdict
        if verdict == "CONFIRMED":
            return RoutingResult(fid, "CONFIRMED", True, model, code, rungs_tried=tried,
                                 ladder_was_empty=_ladder_empty)
    # ───────────── THE LAST RUNG POINTS BACK AT THE SOURCE ─────────────
    # FOUNDER'S RULING, 2026-10-06: *"even with all our models being the same ... at
    # least one rung on the ladder should point back to the original model and say,
    # 'your solution didn't work' or 'your falsifier is broken' please fix"*.
    #
    # WHY IT IS NOT A BLIND RETRY, which is the obvious objection. The source model
    # already failed on this finding, so asking it the same question again would be
    # the definition of expecting a different answer. It is not asked the same
    # question: it is handed the VERDICT its own attempt earned and the code that
    # earned it, which is information it did not have the first time. That is the
    # same thing the ladder gives a stronger rung, applied to the only rung left.
    #
    # IT FIRES ONLY WHEN THE LADDER IS OTHERWISE EXHAUSTED, so it costs 1 dispatch on
    # findings that would otherwise reach a human unresolved -- which is the more
    # expensive outcome. On a 1-model roster, where `rank_falsifier_writers` returns
    # an empty list by construction, this is the ONLY rung there has ever been.
    #
    # The existing empty-ladder path is NOT removed: if this rung also fails, the
    # finding still defers and still reaches the irreducible queue, which is what
    # `test_empty_ladder_is_not_a_dead_transport_2026-09-09.py` holds.
    if self_rung and self_rung != last_model:
        tried += 1
        last_model = self_rung
        code = (resolve_fn(self_rung, _with_routing_feedback(
            finding, last_verdict, last_code)) or "").strip()
        if code:
            last_code = code
            verdict = reverify_fn(code)
            last_verdict = verdict
            if verdict == "CONFIRMED":
                return RoutingResult(fid, "CONFIRMED", True, self_rung, code,
                                     rungs_tried=tried,
                                     ladder_was_empty=_ladder_empty)
        else:
            last_verdict = "ERROR"

    # No rung confirmed -> caller escalates to HIL (genuinely-hard until proven otherwise)
    return RoutingResult(fid, last_verdict, False, last_model, last_code,
                         rungs_tried=tried, ladder_was_empty=_ladder_empty)


def _with_routing_feedback(finding: dict, verdict: str, code: str) -> dict:
    """A copy of the finding carrying what the previous attempt earned.

    THE FEEDBACK IS THE WHOLE POINT OF THE SELF-RUNG. Without it the source model is
    asked an identical question it has already failed. `routing_feedback` is the
    field a caller's `resolve_fn` puts in front of the model; a caller that ignores
    it turns the self-rung into the blind retry this is explicitly not.
    """
    out = dict(finding)
    out["routing_feedback"] = {
        "previous_verdict": verdict,
        "previous_falsifier": code,
        "instruction": (
            "An earlier attempt on THIS finding did not resolve it. The verdict it "
            "earned and the falsifier that earned it are above. Either the fix did "
            "not cure the defect or the falsifier did not demonstrate it. Identify "
            "which, and correct that specific failure rather than restating the "
            "original answer."),
    }
    return out


def route(
    finding: dict,
    available_models: Sequence[str],
    confirmed_findings: Sequence[dict],
    resolve_fn: Callable[[str, dict], str],
    reverify_fn: Callable[[str], str],
    similarity_fn: Callable[[dict, dict], float],
    *,
    strength_order: Sequence[str] = DEFAULT_FALSIFIER_STRENGTH,
    max_rungs: int = 2,   # 0 = exhaust the ladder
    dup_threshold: float = 0.85,
    self_rung_enabled: bool = True,
) -> RoutingResult:
    """Full routing pass for ONE un-confirmed critical finding.

    Order of operations:
      1. Dedup — if the defect is already CONFIRMED under another id, resolve as a
         duplicate (never escalate a confirmed defect to HIL).
      2. Ladder — route to progressively stronger writers (excluding the finding's
         own source model, which already failed) with the tool loop; CONFIRMED wins.
      3. Self-rung — when every other rung is exhausted, hand the finding back to
         its OWN source model together with the verdict its earlier attempt earned,
         so it is asked a different question rather than the same one.
      4. Caller escalates to HIL only if none of these resolves it.

    ``self_rung_enabled`` defaults True on the founder's ruling of 2026-10-06:
    *"Nor is there any harm in turning it on and leaving it on."* Set it False for a
    pre-registered arm whose declared outcome depends on the empty-ladder deferral --
    `bench/exp56_configs/d9_single_model_with_agents.json` is the one such arm, and
    it has not yet run.
    """
    fid = finding.get("finding_id") or finding.get("id") or "?"

    dup = confirmed_duplicate(finding, confirmed_findings, similarity_fn, dup_threshold)
    if dup is not None:
        return RoutingResult(fid, "DUPLICATE", True, None, "", duplicate_of=dup, rungs_tried=0)

    source = finding.get("source_model")
    rungs = rank_falsifier_writers(
        available_models, strength_order=strength_order,
        exclude=(source,) if source else (),
    )
    return resolve_via_routing(
        finding, rungs, resolve_fn, reverify_fn, max_rungs=max_rungs,
        self_rung=source if (self_rung_enabled and source) else None)
