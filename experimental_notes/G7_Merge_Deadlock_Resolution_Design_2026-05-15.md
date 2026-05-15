# G7 Merge-Deadlock Resolution Rule — Design

2026-05-15 03:18 BST

## Summary

The G7 gap (specified in §6b of the consolidated plan, deferred to post-mortem
evidence per the project's Popperian discipline) is: when the runner's
auto-merge cannot decide which canonical entry a new finding should fold into,
what rule should resolve the deadlock? Experiment 40 produced abundant evidence
that the runner's existing auto-merge defers more often than the §6b spec
predicted — at least eight MERGE DEFERRED events surfaced across the original
run, including one with twenty-one target disagreements on a single finding.
The founder explicitly authorised beginning the G7 design work after the
Round 3 panel review and reaffirmed it during the 14 May post-mortem response.

This note records the design that emerges from the panel's own proposal (made
during the 14 May response, point 6) and the founder's direction to apply
compelled-convergence to the question. Implementation is deferred to a separate
commit after the Exp 40 continuation run closes.

## The Problem in Plain Terms

When a new finding arrives at the runner's reconciliation pipeline, the runner
attempts to identify whether the finding is a duplicate of any existing
canonical entry. The auto-merge logic compares descriptions, fix-text, target
files, and severity. When multiple candidate canonical entries match plausibly
— e.g., the new finding could be a duplicate of C0008 OR C0010 OR C0013 —
the algorithm has no principled way to choose. It defers.

Deferral leaves the finding in an unresolved state. It does not enter any
canonical entry. Subsequent rounds re-evaluate the same finding (or
re-discover it from another model), often producing the same deferral.

§6b deliberately specified no arbitration rule. The Popperian discipline
requires that the rule emerge from observed post-mortem evidence rather than
being pre-registered. Experiment 40 produced that evidence.

## The Founder's Proposal (14 May 2026 response, point 6)

Verbatim from the founder's response document:

> "Either an issue is a dupe or it isn't. Either a merge is warranted, or
> it isn't. Where is the scope for 'debate'? Ideally convergence should
> decide this... Perhaps a way forward if this is the case, might be to
> take a leaf from how we do things during our confer rounds with
> compelled convergence? The models *must* agree on a single definitive
> (preferably best case) solution in all cases."

The founder's proposal is to apply the same compelled-convergence discipline
the project uses for confer rounds: dispatch the merge-decision question to
the panel, require a single answer.

## Design Specification

### Trigger

When the runner's auto-merge encounters a deferral condition (multiple
candidate targets with no clear majority among the verdict-voters), instead
of unconditionally marking MERGE DEFERRED, it considers escalating the
decision to the panel.

Escalation triggers on the SECOND consecutive defer (not the first). The
first defer is logged and the finding's `merge_defer_count` increments; only
on the second defer (or higher) does the runner dispatch to the panel. This
prevents arbitration cost on transient deferrals that resolve naturally in
the next round.

### Dispatch payload

The runner constructs a focused query for each panel member:

```
A new finding has been submitted that the auto-merge cannot uniquely place.

NEW FINDING:
  finding_id: <new finding id>
  description: <new finding description>
  proposed_fix: <new finding proposed_fix, truncated to 1000 chars>
  target_file: <new finding target file>
  severity: <new finding severity>

CANDIDATE CANONICAL ENTRIES (the new finding matched one or more of these):
  C001: <description, truncated>
  C002: <description, truncated>
  C003: <description, truncated>
  ...

QUESTION: Which (if any) canonical entry is the SAME ROOT CAUSE as the new
finding? Respond with exactly ONE of:
  MERGE_INTO_<canonical_id>  (e.g. MERGE_INTO_C001)
  KEEP_DISTINCT              (none of the candidates is the same root cause)

No commentary. No multiple votes. Single answer per the compelled-convergence
discipline.
```

The query is dispatched to all five panel members independently (star topology,
no cross-talk). Each model produces one vote.

### Aggregation rule

After collecting five votes:

- **Clear majority** (≥3 of 5 votes for the same target): merge to that target.
- **Plurality, no majority** (e.g., 2-2-1 split): MERGE DEFERRED stays in
  place; the finding remains unmerged and the panel will re-encounter it next
  round.
- **Unanimous KEEP_DISTINCT** (5 of 5 say none of the candidates match): the
  new finding registers as its own canonical entry; the auto-merge attempt
  is abandoned.
- **Mixed KEEP_DISTINCT with one MERGE_INTO vote**: treat the lone MERGE_INTO
  as insufficient quorum; finding registers as its own canonical entry.

### Cost discipline

Each arbitration dispatch costs ~$0.50 of OpenRouter credit (five model
responses, each ~1000 token prompt + ~50 token response). Cap arbitration
dispatches at 3 per round to keep cost bounded. Findings beyond the cap
remain MERGE DEFERRED; the cap is a per-round budget, not a per-finding
budget.

### Implementation surface

Two new pieces of code:

1. **`bench/merge_arbitration.py`** — new module containing:
   - `MergeArbitrationVote` dataclass.
   - `dispatch_merge_arbitration(new_finding, candidates, panel_config)` — sends
     the query, collects votes, returns aggregated result.
   - `aggregate_votes(votes)` — applies the majority rule above.

2. **`bench/reference_runner_v2.py`** — modification to `_update_finding_statuses`
   merge-handling branch around line 870-900. Replace the existing
   `MERGE DEFERRED` log with a check: if `merge_defer_count >= 2` and
   arbitration budget remains for this round, invoke
   `dispatch_merge_arbitration`. Apply the result.

3. **`bench/exp40_configs/40_gate.json`** — new config keys:
   - `merge_arbitration_enabled: bool` (default `false` initially)
   - `merge_arbitration_min_defer_count: int` (default 2)
   - `merge_arbitration_max_per_round: int` (default 3)

### Risk and mitigation

- **Risk: Cost runaway.** Mitigation: per-round cap (default 3 dispatches);
  ability to disable entirely via config flag.
- **Risk: Compute waste.** A round with no MERGE DEFERRED events triggers no
  arbitration dispatch. Cost is bounded by arbitration frequency.
- **Risk: Model disagreement on arbitration itself.** Mitigation: the
  aggregation rule explicitly handles plurality-without-majority by keeping
  the deferral in place. The arbitration vote is advisory; the runner falls
  back to MERGE DEFERRED on genuine panel splits.
- **Risk: Wrong arbitration outcome.** Mitigation: the regular CONFIRMED →
  CLOSED loop via verified fix still applies. If the panel arbitrates wrongly
  (e.g., merges into the wrong canonical), the fix-verification step will
  surface the error when the verified fix is applied — wrong-merge fixes
  won't pass verification.

## Path Forward

1. After the Exp 40 continuation run closes, examine how many MERGE DEFERRED
   events occurred and how the deferral pattern evolved with the now-active
   Bugzilla close-the-loop and gamma-input fixes. Some deferrals may resolve
   naturally now that CLOSED transitions drain the active pool.

2. If MERGE DEFERRED still surfaces materially after the continuation run,
   implement the design above in a dedicated commit. Test against the
   continuation run's deferral events first (the same way the Bugzilla loop
   was validated on Exp 40's existing data before runner integration).

3. Enable in a small experiment (Exp 41 bounded mathematics module is the
   natural next target — single specialist, low MERGE expected, low blast
   radius if the arbitration logic has issues).

4. Expand to subsequent experiments based on observed behaviour.

## What this Design Does Not Cover

- It does not cover the related G6 (specialist-to-specialist verdict
  conflict). G6 surfaces when two B-Cell specialists (e.g., mathematics and
  biology) return conflicting verdicts on the same finding. That requires
  multi-specialist co-rule in the dispatch pipeline, which doesn't surface
  until Exp 49 by current §6b expectations.
- It does not cover G8 (burst-mode phase-zero convergence override), which
  is out-of-arc for the current Experiment 40-54 sequence.

## Next Review Trigger

After the Exp 40 continuation run closes and the founder reviews the
continuation's post-mortem. Decision: proceed with implementation (yes/no),
adjust scope, or defer further pending more evidence.

Written under CDSFL note standard v1.2 (14 May 2026).
