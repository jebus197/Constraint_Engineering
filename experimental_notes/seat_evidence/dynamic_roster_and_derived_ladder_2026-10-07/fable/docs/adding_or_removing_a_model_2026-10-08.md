<!-- PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'dynamic_roster_and_derived_ladder_2026-10-07', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 878624bc079a289210358e99f7f6f7165001f9b8f11010b682ced07472d0bcd9
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited. -->
# Adding or removing a model: what the researcher does

Status: design note accompanying the derived-capability routing review,
2026-10-08. Companion code: `bench/capability_estimator.py`,
`bench/seat_circuit_breaker.py`, `bench/routing.py`.

## Adding a model

One action: add a `ModelConfig` entry (label, api, model_id, per-dispatch money
cost) to the experiment config's `models` list. Everything downstream is
already label-driven or becomes so with the estimator:

1. **Dispatch** — the runner dispatches whatever `models` declares.
2. **Aliveness** — `seat_aliveness_2026-10-06.caller_for` builds the probe from
   the declared `api`; an unknown api fails loud by design.
3. **Ladder position** — nothing to edit. `rank_falsifier_writers` already
   appends labels absent from `DEFAULT_FALSIFIER_STRENGTH` after the ranked
   ones (measured: the tuple is a priority prefix, not an allowlist), and under
   `CapabilityEstimator.order_seats` a seat with no attempt records has a
   Wilson lower bound of 0.0 and sorts last, climbing only on
   provenance-checked CONFIRMED verdicts. No placement decision exists for a
   human to make, which is requirement 3 satisfied by construction.
4. **UX** — this is exactly the behaviour the existing design brief specifies:
   *"The model list is extensible. When a new model becomes available, the
   user adds it. No code change required."*
   (`experimental_notes/CDSFL_UX_Vision_Sketch_2026-03-28.md`, Model
   Selection.) The config edit is the CLI form of that surface.

What the researcher must now ALSO supply, new with the derived key: the seat's
per-dispatch money cost (0 for subscription seats). Latency is measured, not
declared. `latency_weight` is a per-run config value, default 1.0.

## Removing a model

Removal is an edit to the config's `models` list **between runs**. That is a
roster definition, not benching: benching is setting a seat aside permanently
*within the policy while it remains on the roster*, and mid-run exclusion
without readmission. Mid-run, no removal path exists at all — a failing seat
trips its circuit breaker (`bench/seat_circuit_breaker.py`), is re-probed every
round boundary, and is readmitted on a passing probe; the breaker type has no
terminal state, which its falsifier asserts.

## What is still the founder's to rule on

The 47 experiment configs declare 5 display names; none declares Fable and none
declares Kimi. Wiring either into real experiments changes what real runs
dispatch and is a config decision, not a code decision
(`bench/routing.py`, "THE OTHER HALF IS NOT DONE").
