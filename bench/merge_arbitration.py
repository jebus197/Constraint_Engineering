"""G7 merge-deadlock arbitration (Exp 40 continuation, 15 May 2026).

Implements the compelled-convergence merge-decision rule designed in
`experimental_notes/G7_Merge_Deadlock_Resolution_Design_2026-05-15.md`
and validated against the continuation's six observed D4 MERGE
DEADLOCK escalations (C0008 20-way, C0023 14-round, C0032, C0035,
C0044, C0147).

Problem. When the runner's auto-merge cannot uniquely place a new
finding among several plausible canonical entries it defers. Deferral
recurs round after round; the continuation produced one 14-round
deadlock and one 20-way ambiguity. §6b of the consolidated plan
deliberately specified NO arbitration rule until post-mortem evidence
existed (Popperian discipline). That evidence now exists.

Rule. On the SECOND consecutive defer of a finding (not the first —
transient deferrals resolve naturally), dispatch a short focused query
to all five panel models, independent, single-answer-each. Aggregate:

  - ≥3 of 5 agree on the same target  → merge into that target
  - ≥3 of 5 say KEEP_DISTINCT         → register as own canonical
  - otherwise (plurality, no majority)→ stay deferred (panel will
    re-encounter next round and may converge then)

Cost discipline. ~$0.50 per dispatch (5 short model calls). Capped at
`max_per_round` arbitrations per round (default 3 ⇒ ≤ ~$1.50/round).
Findings beyond the cap stay deferred.

This module is dispatch-injectable: `dispatch_merge_arbitration`
takes a `dispatch_fn` so the runner passes the real model dispatch
and tests pass a stub. No network in this file.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

# Vote token grammar. A model must answer with exactly one of:
#   MERGE_INTO_C0001   (or any C\d{4,} canonical id — the project's
#   canonical-ID grammar; aligned with the runner's merged_into regex
#   in _update_finding_statuses for cross-surface schema coherence,
#   architectural P-pass 3, 15 May 2026)
#   KEEP_DISTINCT
_MERGE_VOTE_RE = re.compile(r"MERGE_INTO_(C\d{4,})", re.IGNORECASE)
_KEEP_DISTINCT_RE = re.compile(r"KEEP[_\s-]?DISTINCT", re.IGNORECASE)

KEEP_DISTINCT = "KEEP_DISTINCT"


@dataclass
class MergeArbitrationVote:
    """One panel member's single arbitration answer."""

    model: str
    vote: str            # "C0001" (a target id) or KEEP_DISTINCT or ""
    raw_response: str
    elapsed_s: float = 0.0
    parse_ok: bool = True


@dataclass
class MergeArbitrationResult:
    """Aggregated arbitration outcome for one deferred finding."""

    finding_id: str
    decision: str         # "MERGE", "KEEP_DISTINCT", or "DEFER"
    target: Optional[str]  # canonical id when decision == "MERGE"
    votes: List[MergeArbitrationVote] = field(default_factory=list)
    tally: Dict[str, int] = field(default_factory=dict)
    rationale: str = ""

    def to_dict(self) -> dict:
        return {
            "finding_id": self.finding_id,
            "decision": self.decision,
            "target": self.target,
            "tally": self.tally,
            "rationale": self.rationale,
            "votes": [
                {
                    "model": v.model,
                    "vote": v.vote,
                    "parse_ok": v.parse_ok,
                    "elapsed_s": round(v.elapsed_s, 2),
                }
                for v in self.votes
            ],
        }


def build_arbitration_query(
    new_finding: Dict[str, Any],
    candidates: Sequence[Dict[str, Any]],
    *,
    fix_truncate: int = 1000,
    desc_truncate: int = 600,
) -> str:
    """Construct the focused single-answer arbitration prompt.

    `new_finding` and each candidate are plain dicts with at least
    `finding_id`/`canonical_id` and `description`; the new finding may
    also carry `proposed_fix`, `target_file`, `severity`.
    """
    nf_id = new_finding.get("finding_id", new_finding.get("canonical_id", "?"))
    nf_desc = (new_finding.get("description", "") or "")[:desc_truncate]
    nf_fix = (new_finding.get("proposed_fix", "") or "")[:fix_truncate]
    nf_file = new_finding.get("target_file", "") or ""
    nf_sev = new_finding.get("severity", "")

    lines = [
        "MERGE ARBITRATION — single definitive answer required.",
        "",
        "The auto-merge cannot uniquely place a new finding. Decide, on "
        "ROOT CAUSE, whether it is the SAME underlying defect as one of "
        "the candidate canonical entries, or genuinely distinct.",
        "",
        "NEW FINDING:",
        f"  id: {nf_id}",
        f"  description: {nf_desc}",
    ]
    if nf_fix.strip():
        lines.append(f"  proposed_fix (truncated): {nf_fix}")
    if nf_file:
        lines.append(f"  target_file: {nf_file}")
    if nf_sev != "":
        lines.append(f"  severity: {nf_sev}")
    lines += [
        "",
        "CANDIDATE CANONICAL ENTRIES (the new finding plausibly matched "
        "one or more):",
    ]
    for c in candidates:
        cid = c.get("canonical_id", c.get("finding_id", "?"))
        cdesc = (c.get("description", "") or "")[:desc_truncate]
        lines.append(f"  {cid}: {cdesc}")
    lines += [
        "",
        "QUESTION: Which (if any) canonical entry is the SAME ROOT "
        "CAUSE as the new finding? Respond with EXACTLY ONE token, "
        "nothing else:",
        "  MERGE_INTO_<canonical_id>   (e.g. MERGE_INTO_C0008)",
        "  KEEP_DISTINCT               (none is the same root cause)",
        "",
        "No commentary. No multiple votes. One token. This is a "
        "compelled-convergence decision: you MUST commit to a single "
        "definitive answer.",
    ]
    return "\n".join(lines)


def parse_arbitration_vote(
    response: str,
    candidate_ids: Sequence[str],
    model_label: str = "",
    elapsed_s: float = 0.0,
) -> MergeArbitrationVote:
    """Extract the single vote from a model response.

    Resolution order:
      1. An explicit MERGE_INTO_<id> whose id is among the candidates.
      2. An explicit KEEP_DISTINCT token.
      3. A bare candidate id mentioned exactly once and no other.
      4. Otherwise unparseable (vote="", parse_ok=False).

    A MERGE_INTO pointing at a non-candidate id is treated as
    unparseable — the model must choose among the offered candidates
    or KEEP_DISTINCT.
    """
    text = response or ""
    cand_set = {c.upper() for c in candidate_ids}

    merge_hits = [
        m.group(1).upper() for m in _MERGE_VOTE_RE.finditer(text)
    ]
    keep_hit = bool(_KEEP_DISTINCT_RE.search(text))

    valid_merge = [h for h in merge_hits if h in cand_set]

    # Unambiguous single MERGE_INTO into a real candidate.
    if valid_merge and len(set(valid_merge)) == 1 and not keep_hit:
        return MergeArbitrationVote(
            model=model_label, vote=valid_merge[0],
            raw_response=text, elapsed_s=elapsed_s, parse_ok=True,
        )
    # Unambiguous KEEP_DISTINCT with no competing merge vote.
    if keep_hit and not valid_merge:
        return MergeArbitrationVote(
            model=model_label, vote=KEEP_DISTINCT,
            raw_response=text, elapsed_s=elapsed_s, parse_ok=True,
        )
    # Fallback: a single bare candidate id appears and nothing else
    # ambiguous.
    bare = [
        cid for cid in cand_set
        if re.search(rf"\b{re.escape(cid)}\b", text.upper())
    ]
    if not keep_hit and not merge_hits and len(bare) == 1:
        return MergeArbitrationVote(
            model=model_label, vote=bare[0],
            raw_response=text, elapsed_s=elapsed_s, parse_ok=True,
        )
    # Unparseable / contradictory / multi-vote.
    return MergeArbitrationVote(
        model=model_label, vote="", raw_response=text,
        elapsed_s=elapsed_s, parse_ok=False,
    )


def aggregate_votes(
    finding_id: str,
    votes: Sequence[MergeArbitrationVote],
    *,
    majority: int = 3,
) -> MergeArbitrationResult:
    """Apply the compelled-convergence majority rule.

    `majority` (default 3, i.e. ≥3 of 5) is the agreement threshold.
    Unparseable votes count toward neither side but are retained for
    audit.
    """
    tally: Dict[str, int] = {}
    for v in votes:
        if not v.parse_ok or not v.vote:
            continue
        tally[v.vote] = tally.get(v.vote, 0) + 1

    if not tally:
        return MergeArbitrationResult(
            finding_id=finding_id, decision="DEFER", target=None,
            votes=list(votes), tally=tally,
            rationale="no parseable votes — stay deferred",
        )

    top_vote, top_n = max(tally.items(), key=lambda kv: kv[1])

    if top_n >= majority:
        if top_vote == KEEP_DISTINCT:
            return MergeArbitrationResult(
                finding_id=finding_id, decision="KEEP_DISTINCT",
                target=None, votes=list(votes), tally=tally,
                rationale=(
                    f"{top_n} of {len(votes)} voted KEEP_DISTINCT "
                    f"(≥{majority} majority) — register as own "
                    f"canonical entry"
                ),
            )
        return MergeArbitrationResult(
            finding_id=finding_id, decision="MERGE", target=top_vote,
            votes=list(votes), tally=tally,
            rationale=(
                f"{top_n} of {len(votes)} voted MERGE_INTO_{top_vote} "
                f"(≥{majority} majority)"
            ),
        )

    return MergeArbitrationResult(
        finding_id=finding_id, decision="DEFER", target=None,
        votes=list(votes), tally=tally,
        rationale=(
            f"plurality without majority (top={top_vote}:{top_n}, "
            f"need ≥{majority}) — stay deferred, panel re-encounters "
            f"next round"
        ),
    )


def dispatch_merge_arbitration(
    new_finding: Dict[str, Any],
    candidates: Sequence[Dict[str, Any]],
    panel: Sequence[Any],
    dispatch_fn: Callable[[Any, str], Tuple[str, float]],
    *,
    majority: int = 3,
    log_fn: Optional[Callable[[str], None]] = None,
) -> MergeArbitrationResult:
    """Run one arbitration round across the panel for one finding.

    Args:
        new_finding: dict for the deferred finding.
        candidates: list of candidate canonical-entry dicts.
        panel: sequence of model configs (anything `dispatch_fn`
            accepts as its first arg — a ModelConfig in production).
        dispatch_fn: callable(model_cfg, prompt) -> (response, elapsed).
            The runner passes a thin wrapper over `dispatch_to_model`;
            tests pass a stub. Exceptions per model are caught and that
            model's vote is recorded unparseable (the arbitration
            degrades gracefully rather than aborting the round).
        majority: agreement threshold (default 3 of 5).
        log_fn: optional logger.

    Returns:
        MergeArbitrationResult.
    """
    def _log(msg: str) -> None:
        if log_fn:
            log_fn(msg)

    fid = new_finding.get(
        "finding_id", new_finding.get("canonical_id", "?"),
    )
    candidate_ids = [
        c.get("canonical_id", c.get("finding_id", "?"))
        for c in candidates
    ]
    query = build_arbitration_query(new_finding, candidates)

    votes: List[MergeArbitrationVote] = []
    for mc in panel:
        label = getattr(mc, "label", str(mc))
        try:
            response, elapsed = dispatch_fn(mc, query)
        except Exception as e:  # graceful degradation
            votes.append(MergeArbitrationVote(
                model=label, vote="", raw_response=f"__ERROR__: {e}",
                elapsed_s=0.0, parse_ok=False,
            ))
            _log(f"  G7 arbitration {fid}: {label} dispatch error — {e}")
            continue
        vote = parse_arbitration_vote(
            response, candidate_ids, model_label=label,
            elapsed_s=elapsed,
        )
        votes.append(vote)
        _log(
            f"  G7 arbitration {fid}: {label} → "
            f"{vote.vote or 'UNPARSEABLE'}"
        )

    result = aggregate_votes(fid, votes, majority=majority)
    _log(f"  G7 arbitration {fid}: {result.decision} "
         f"({result.rationale})")
    return result
