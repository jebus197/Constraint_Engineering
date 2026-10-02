<!-- PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'rho_repair_review_2026-09-29', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 830ee0b406ce910d7ce19497ac2679c11006fd1bdc7af7a2370c01d37bc6e808
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited. -->
# Seat `fable` — between-rounds review of the rho repair, 2026-09-29

All figures below were re-measured in this sandbox. Where I rely on a number
from the implementing session's notes I say so; otherwise the number is mine and
the command that produced it is named.

**Headline.** The repair's *direction* is right and its *mechanism claim is
wrong in two places*. Counting novelty from `occasions` is sound. But (1) the
discount rule is pairwise with no conservation guard, so it can erase a defect
from the novelty count entirely — measured on the archive, and on one run it
erases **all 39 canonicals**; and (2) the commentary at 3 sites says rho reaches
convergence through "blocking condition (d)" of the gamma-alt gate, which has
been false since the founder's 2026-08-29 ruling. It reaches a gate — a
different one, in the opposite direction.

---

## Q1 — Should the CRITICAL novelty series be corroboration-aware?

**Recommendation: NOT YET. Promote only after the conservation guard lands, and
re-measure. Meanwhile the half-promotion is itself a defect that must be closed
one way or the other, because it breaks an arithmetic invariant.**

`novel_this_round` now comes from `_corroborated_novelty_series` while
`novel_critical_history[-1]` still comes from `_settled_novelty_series`. Critical
findings are a subset of all findings, so `crit <= all` must hold. It does not.

Measured (`/tmp/probe7.py`, archive replay): 5 runs produce rounds where
`settled_crit[r] > corroborated_all[r]` — `exp55_v3_control`,
`sim45_canary`, `sim45_canary_v2`, `sim45_postfix` (round 0 each) and
`sim45_memory_20260901T040540Z` (rounds 0 and 3). In that last run the gate
would simultaneously read "1 new critical this round" and "0 new findings of
any severity this round".

Against promotion, *today*: on `sim45_memory_20260901T040540Z` the corroborated
critical series is `[0,0,0,0,0,0,0]` against a settled `[1,0,0,1,0,0,0]`. The
round-3 critical is erased by the annihilation defect below. Unlike rho's churn
flag, the zero-critical streak **is** a genuine convergence trigger — condition
(a) of the two-sided gate. Promoting the critical series before the guard lands
would route the annihilation defect straight into it.

For promotion, *after* the guard: leaving the two series on different
definitions is not a neutral hold. It is a live arithmetic contradiction, and
the cheapest way out is to make both corroborated, since the corroborated series
is the one that answers "how many distinct defects".

---

## Q2 — Should rho's history be retroactively resettled?

**Recommendation: YES, resettle the whole series each round — the same
whole-series correction already applied to `novel_critical_history` on
2026-08-19. Under option 3 the argument that was merely tidy before is now
load-bearing.**

A round's rho is not a statement about what was known then, because it was never
computed that way: `_compute_rho` reads `novelty_counts`, and `rho_avg` averages
the STORED values across the rolling window. A stale index does not sit
harmlessly in a log; it enters the quantity the churn flag tests.

`_backfill_occasion` writes `"round": int(round_idx)` — the round corroboration
*arrived* — while `_corroborated_novelty_series` buckets the discount by the
discounted entry's `open_since_round`. Those are different rounds, so a
corroboration in round K rewrites round r < K, which `novelty_counts[-1] = ...`
cannot reach. This is not exotic: it is the resume-backfill path added in the
same commit.

Executed — `python3 scripts/measure_rho_retroactive_drift_2026-09-29.py`:

```
  raw_counts                          : [2, 2, 1, 2]
  novelty BEFORE the round-3 occasion : [1, 1, 0, 0]   rho [0.5, 0.5, 0.0, 0.0]
  novelty AFTER  the round-3 occasion : [1, 0, 0, 0]   rho [0.5, 0.0, 0.0, 0.0]
  rounds whose novelty MOVED          : [1]
  the runner overwrites only index [-1]=3, so round(s) [1] keep
  a value the registry no longer supports.
  rho_avg over rounds 1-3, as stored    : 0.1667
  rho_avg over rounds 1-3, resettled    : 0.0000
  difference                            : +0.1667  (threshold 0.25)
```

**The archive cannot settle this and I will not pretend it can.** A whole-archive
replay returns 0 of 318 rounds stale, and that zero is an artefact: archived
`codiscovery` records carry model / finding_id / similarity and **no round**, so
any replay must stamp each reconstructed occasion with its target's own
`open_since_round`, which makes a late corroboration inexpressible. Recorded as
UNMEASURABLE-FROM-ARCHIVE, not as measured-clean. The script says so in its own
output rather than printing the reassuring zero.

**Secondary, and cheap:** `codiscovery` records should carry the round. Without
it no future audit can answer this question from the archive either.

---

## Q3 — The 2 unchosen repairs, and whether they compose

**(a) Lower the 0.85 routing dedup threshold — NOT redundant, but must NOT land
alone.** Its *novelty-accounting* motivation is now redundant: option 3 captures
corroboration without merging. Its *routing* purpose is not — merge candidacy
changes registry identity, prompt content and the irreducible queue, none of
which a counting change touches. But at the threshold catching all 4 known
duplicates, precision is 13.79% — 4/29, Wilson [5.4974%, 30.5590%]
(statsmodels; the 13.79% is the brief's figure, the interval is mine). That is
~6.25 false candidates per true one pushed at a human queue, which is precisely
the founder's standing signature: *an unusually high human-escalation queue has
always indicated broken machinery*. Landing (a) alone would manufacture that
signature deliberately.

**(b) Let a falsifier firing on both findings' locations BE the tool verdict —
NOT redundant, and it is the on-principle answer, but the predicate as stated is
too weak.** Option 3 explicitly declines to merge (the duplicate keeps its own
canonical, a founder ruling), so (b) addresses something option 3 does not
touch. It is also the only one of the three that is "tools decide, not votes"
rather than an accounting change. The hazard: *firing on both locations* is
evidence of a shared **location**, not of a shared **defect**. Two genuinely
distinct defects in one function both satisfy it. Tighten to: the **same**
falsifier, unmodified, must demonstrate **both findings' claims** — not merely
touch both sites.

**Do they compose? Yes, and only in that order.** (b) supplies the tool verdict
that makes (a)'s widened candidacy safe; (a) supplies the candidates (b) needs
in order to have anything to adjudicate. (a) without (b) is a queue-flood.
(b) without (a) is inert above 0.85 for the 4 known duplicates. Sequence (b)
first, measure, then (a).

---

## Q4 — Is `-SIM` in dict KEYS the right general invariant?

**Recommendation: RETAIN the per-directory rule — its redundancy is not even a
property of this corpus at the level that matters. And add a produced marker, so
the invariant stops being inferred.**

The brief's redundancy figure (30 both / 0 either-alone / 73 neither) is over
103 *keyed* documents. Measured over every JSON document in `bench/logs`
(7,250 docs; `_is_simulated` and `_simulated_run_dirs` called directly):

```
docs=7250 both=426 file_only=0 dir_only=170 neither=6654
first-firing signal: {'directory_name': 310, 'sim_seat_label': 100,
                      '_simulated': 4, 'severity_provenance': 12}
```

The per-directory rule catches **170 documents the per-file rule misses** —
2.3448%, Wilson [2.0209%, 2.7192%]. It is not redundant. Removing it would also
violate the additive standard: no committed measurement shows a replacement
dominating it on any named property.

On the invariant itself: `-SIM` as a seat suffix is a sound **sufficient**
condition and a good one — it is structural, read from named fields rather than
prose, so it cannot resurrect the 9-real-transcript false positive. It is not a
**necessary** condition: it rests on a naming convention, and the convention is
enforced by directive, not by the writer. The better invariant is not a cleverer
reader — it is a **produced fact**: have the runner write
`"_simulated": <bool>` unconditionally into *every* artefact it emits,
`runner_state.json` included. Note the measured signal distribution above: only
4 documents in the whole archive are caught by `_simulated` first, because
almost nothing writes it. That is the gap. Keep all 4 existing signals; add the
fifth at the producer.

---

## Q5 — The grep blind-spot test

**Ruled: same rewrite as `TestAgeControl`. Fixed at
`bench/tests/test_shell_grep_blind_spot_2026-09-28.py`.**

Reproduced here: `397` and `397` (the brief says 403/403; the tree has moved).
The decisive evidence is that the file already contains the honest version of
the same question — `test_the_wrapper_is_a_shell_function_not_a_binary` probes
`type grep`, gets `grep is /usr/bin/grep`, and skips. Two tests, one mechanism,
one circular: the failing one inferred wrapper presence *from the very
inequality it was asserting*.

The invariant is **`seen <= real`** — the wrapper can only subtract. That now
runs unconditionally, and catches the direction that would actually matter (the
remedy under-reporting, which would invalidate every figure in the file header).
The strict `seen < real` is gated on the independent `_wrapper_state()` probe.

**Skipping does not destroy the detection, and I executed the check rather than
asserting it** — `python3 scripts/falsify_grep_gate_not_vacuous_2026-09-29.py`:

```
[1] wrapper loaded, 397 == 397 -> test FAILED as required
[2] wrapper absent -> Skipped (skip, correct)
[3] seen=500 > real=397 -> invariant FAILED as required
REFUTED: the gate preserves the detection
```

---

## Observation, not a finding: the age control fails open without git

`bench/tests/test_latent_control_audit_2026-09-01.py::TestAgeControl` fails 4/4
in this sandbox because the sandbox copy carries no `.git`, so
`first_committed` is `None`. **Not caused by my changes and not the defect the
brief asked about.** What is worth a look: with dates unavailable the audit
prints `Quarantined set: []` — a reassuring empty set — rather than refusing.
That is the shape `shell_grep_blind_spot`'s own header calls "a lie in the
reassuring direction". I could not separate "no git here" from "fails open in
general" without git history, so I report it as unresolved rather than ruling.
