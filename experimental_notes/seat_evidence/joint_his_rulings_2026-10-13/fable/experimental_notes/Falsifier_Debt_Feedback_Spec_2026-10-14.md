<!-- PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'joint_his_rulings_2026-10-13', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 8728c8d46fafa7f4015cc72f05b4b96f917c7eb05f9c019a74765cbabdb15984
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited. -->
# Falsifier-Debt Feedback — Build Specification (J3, joint round 2026-10-14)

**Status: SUGGESTED, not applied.** Specified to the founder's ruling of
2026-10-13: *"if we feed these issues back into the harness for resolution, as
we have already discussed — and have existing mechanics for... If so you should
build it and apply it."* The archive measurement licensing the build is
`scripts/the_untoolable_were_never_attempted_2026-10-14.py`:

- Population: 1,938 / 3,298 entries UNTOOLABLE or carrying no falsifier
  (58.7629%, Wilson [57.0736%, 60.4318%]).
- NEVER ATTEMPTED (no code, no verdict, no routing): 1,884 / 1,938 = 97.2136%,
  Wilson [96.3823%, 97.8582%].
- PROVED IRREDUCIBLE (ladder exhausted, no source): **0 / 1,938**, Wilson
  upper bound 0.1978%.
- Every flaw class in the population has an executed falsifier elsewhere:
  1,938 / 1,938, Wilson lower bound 99.8022%.

His claim is CONFIRMED, so the mechanism below is owed. It reuses the existing
feedback channel (`bench/dm/_feedback.py`, `cdsfl_operational.md` §17) rather
than adding a new one.

## 1. Record type

Add one record kind to `FindingFeedback`: `FALSIFIER_DEBT`.

Emitted at round close, per source model, for each registry entry where ALL of:

- `status` ∈ LIVE = {OPEN, UNCONFIRMED, CORROBORATED, CONTESTED}, OR
  `status == CONFIRMED` with `status_adjudicator != "tool"` (the archive holds
  530 such entries confirmed by no tool — they re-enter until a tool rules);
- no non-empty `falsifier_code`;
- `falsifier_verdict` not in {CONFIRMED, REFUTED, NON_DISCRIMINATING}.

Explicitly EXCLUDED: entries terminal by other adjudication
({REFUTED, MERGED, CLOSED, WITHHELD} — 612 of the archived never-attempted),
and entries currently queued in the routing ladder (`routing_history`
non-empty and unexhausted — the ladder is already resolving them).

## 2. Payload (fields exist today; no schema addition)

`canonical_id`, `description` (existing truncation cap), `open_since_round`,
and the imperative, worded on the §17 precedent ("agree with tool output OR
show it wrong"):

> This finding carries no executed falsifier. Either (a) attach a runnable
> falsifier per the routing ladder, or (b) return a scoped UNTOOLABLE
> justification naming the specific claim element no computation can decide
> and why. An unscoped UNTOOLABLE is rejected and the debt re-served.

## 3. UNTOOLABLE acceptance rule

An UNTOOLABLE declaration retires the debt ONLY when the routing ladder has
been fully consulted (`rungs_tried == rungs_available`). Measured basis: 30 of
41 archived UNTOOLABLE declarations carry an EMPTY `routing_history` (73.1707%,
Wilson [58.0665%, 84.3050%]) — declarations, not demonstrations. An UNTOOLABLE
with an unexhausted ladder re-enters the ladder (`_routing_ladder` machinery,
the "never served" door of 2026-10-12) instead of retiring.

## 4. Priority, caps, and convergence authority

- Priority: below refutations and admissibility failures, above R_k
  discrepancies, in `FindingFeedback.priority_score()` — refuted claims stay
  the loudest signal.
- Existing `top_k` (10) and aggregate-summary overflow behaviour unchanged.
- **Gates untouched.** The debt record is prompt plumbing; whether a finding
  blocks convergence remains the harness's ruling (`unverified_critical_count`
  and the A4 fail-safe as today). No model decides convergence; discharge of a
  debt is recorded only when a tool-executed verdict lands.

## 5. Flag and wiring (additive standard)

`falsifier_debt_feedback = false` default in `bench/cdsfl_registry/universal.toml`
beside `feedback_channel_enabled`; read in `build_feedback_records`; exercised
by a committed test (debt emitted for a live no-falsifier entry; not emitted
for terminal; UNTOOLABLE-with-unexhausted-ladder re-routes; flag off ⇒
byte-identical sections). Commissioned in the next simulated run; the
promotion measurement is the per-run discharge rate (debts served vs executed
verdicts landed), which the round telemetry already has the fields to count.

## 6. What this does NOT do

It does not manufacture falsifier supply on its own: J4 established that the
directive sections mandating runnable falsifiers reach 0 of 5 models (producer:
`scripts/what_the_minimal_rendering_delivers_2026-10-14.py`). The debt record
puts the obligation in the one channel measured to reach every seat — the
per-round prompt — which is also why the feedback route is the correct carrier
rather than a directive-file edit gated on the lean-vs-full ablation.
