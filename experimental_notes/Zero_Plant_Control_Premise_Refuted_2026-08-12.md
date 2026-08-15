# The zero-plant control does not measure what it was said to measure

2026-08-12, overnight. Offline measurement, no paid dispatch.

## Summary

The alarm was wrong, and the correction matters more than the alarm did.

It was reported to the founder that a five-model panel produced a large number of
critical findings against a control document containing no defects, and that every
such finding was therefore false by construction. That inference does not hold. The
control's confirmed critical findings were checked against the document's own source
and **they are true**. The panel found real defects. The falsification machinery
re-executed the demonstrations and confirmed them correctly.

There was no false-positive epidemic. There was an invalid premise.

## What "zero-plant" actually guarantees

It guarantees that **no defect was deliberately seeded**, and — per the claim audit —
that **every one of the 44 claims is true**. It was then treated as though it
guaranteed that **the document contains no defects**. Those are different properties,
and the gap between them is where the error lived.

The control is a ~24 KB technical document containing real code listings. Code that
nobody deliberately broke can still be wrong, and it can be wrong in ways no claim
speaks to.

### The precise diagnosis: the ground truth is claim-scoped, the review is not

This is a scope mismatch, not negligence, and the distinction is worth stating
carefully because the claim audit was rigorous — every claim was executed rather than
read, using symbolic algebra, a constraint solver, dimensional analysis and Monte
Carlo sampling.

Take claim ZC-17, which covers `HashRing.locate`. What it asserts is that the INDEX
IS ALWAYS IN RANGE: `bisect_right` returns a value in `[0, len(points)]`, reaching
`len(points)` exactly when the hash exceeds every published point, and the subsequent
`idx % len(self.points)` maps that case back to 0 so the subscript is always valid.

**That claim is true.** It was verified correctly.

The panel's finding is that an exact hash match ROUTES TO THE WRONG POINT, because
`bisect_right` returns the position after an equal element. **That is also true.**

The two are not in contradiction. They are different properties of the same three
lines. The audit established claim-level truth; the panel reviewed the artefact and
found a defect in behaviour no claim asserts anything about.

The same holds for the token bucket: a claim about refill rate and capacity can be
entirely true while `allow()` still admits a negative cost, because no claim says
anything about negative costs.

So the instrument is MIS-SPECIFIED. A control whose ground truth is claim-scoped
cannot score findings that range over the whole artefact. Every such finding is
unscoreable by construction — it can be neither confirmed nor refuted against a
record that does not cover it. That is a design fault in the control, and it is
independent of how carefully the audit was performed.

## The evidence

Two confirmed criticals were checked directly against the document.

**`TokenBucket.allow` admits negative cost.** The listing reads:

```python
def allow(self, cost=1.0):
    now = time.monotonic()
    self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)
    self.last = now
    if self.tokens >= cost:
        self.tokens -= cost
        return True
    return False
```

With `capacity = 1` and the single token already spent, `tokens = 0`. Calling
`allow(-10)` evaluates `0 >= -10` as true, then executes `tokens -= -10`, leaving
`tokens = 10`. The capacity clamp guards only the refill term, not the subtraction,
so the bucket ends above capacity and subsequent requests bypass the limiter. The
finding is correct.

**`HashRing.locate` mis-routes an exact hash match.** The listing reads:

```python
def locate(self, key):
    idx = bisect.bisect_right(self.keys, ring_hash(key))
    return self.points[idx % len(self.points)][1]
```

`bisect_right` returns the insertion point *after* an equal element, so a key whose
hash falls exactly on a ring point is routed to the following point rather than to
the one it matches. The finding is correct.

Both were raised independently in both control runs, seven weeks apart, by different
models.

## Measured verdicts on the control

Extracted from each run's `runner_state.json` registry. Critical is severity ≥ 0.7.

| Run | Registry entries | Critical | Falsifier present | CONFIRMED |
|---|---|---|---|---|
| 2026-07-29 | 23 | 7 | 3 | 2 |
| 2026-08-01 | 40 | 22 | 15 | 8 |

Verdict distribution, 2026-08-01: 8 CONFIRMED, 7 ERROR, 7 UNTOOLABLE.
Verdict distribution, 2026-07-29: 2 CONFIRMED, 1 REFUTED, 4 UNTOOLABLE.

The confirmed findings are the ones checked above. They are true positives.

## Consequences

**One.** The false-positive rate of this system has never been measured. Not
"measured badly" — never measured. The instrument built to measure it cannot, because
its ground truth establishes only that nobody tampered with the document, which is
not the property required.

**Two.** Measuring it needs a target whose correctness is *established* rather than
merely undisturbed. That is a substantially harder artefact to produce than an
un-seeded one, and the difficulty is the finding, not an implementation detail.

**Three.** Both defects are present in the document as it stands, at the content hash
the manifest publishes. The seven claim repairs of 1 August did not touch them, and
correctly so — those repairs addressed claim wording and ambiguity, which is what the
claim audit was scoped to. The defects sit outside every claim.

This leaves a decision the founder should take rather than the record absorb
silently. Three options, and they are genuinely different instruments:

  (a) Repair the two defects, bringing the artefact closer to the property the
      control was believed to have. Cheapest, and it preserves the original intent.
  (b) Keep them and DOCUMENT them as known-true findings. This converts a broken
      control into a small genuine answer key — two defects a competent panel should
      find — which is a more useful instrument than a clean document, because it can
      score both false positives and false negatives.
  (c) Retire the control and build a target whose ground truth is artefact-scoped
      rather than claim-scoped.

Option (b) is the recommendation. It costs the least new work, it turns tonight's
finding into an asset rather than a write-off, and it is the only one of the three
that yields a control able to measure a miss as well as a false alarm.

**Four.** The remediation this alarm would have justified — reworking the
adjudication machinery to suppress a flood of false criticals — would have been spent
against a problem for which there is no evidence. The machinery behaved correctly at
every step that was actually exercised.

## The loop, measured: Run A found real defects and the claims were narrowed around them

This was suggested by a panel model during the review of 2026-08-12 and then measured
directly. It converts the earlier run from a discard into the true-positive arm the
control never had.

Run A produced seven criticals. Nearly all map onto the seven claims subsequently
repaired on 1 August:

| Finding | Verdict | Maps to |
|---|---|---|
| C0001 | UNTOOLABLE | `TokenBucket.allow` accepts zero, fractional and negative costs |
| C0003 | REFUTED | `TokenBucket.allow` is not thread-safe |
| C0005 | UNTOOLABLE | ZC-20 "schedule never shortens" is incorrect |
| C0014 | UNTOOLABLE | `backoff_delay` invalidates ZC-20's postcondition |
| C0017 | CONFIRMED | `HashRing.locate` off-by-one on an exact match (ZC-17) |
| C0021 | CONFIRMED | Negative costs violate the invariant stated in ZC-14 |
| C0023 | UNTOOLABLE | `topo_order` construction |

Three claims are named explicitly by the findings — ZC-14, ZC-17, ZC-20 — and all
three are among the seven repaired. The remaining two repairs to ZC-12 were the
insertion of the qualifiers "under single-threaded use" and "unit-cost", which
correspond exactly to C0003 and C0001.

**The panel was right nearly every time.** This is a measured true-positive arm on a
run already paid for, and it points the opposite way from the false-positive alarm.

### Why the same defects reappeared in Run B

The repairs narrowed the CLAIMS. The CODE was never changed. ZC-12 did not stop
asserting something false about negative costs by fixing `allow()`; it stopped
asserting anything about them by adding the word "unit-cost".

Against a claim-scoped audit that closes the finding. Against a panel reviewing the
artefact it does nothing at all, because the finding was never about the wording. So
Run B found the negative-cost defect, the hash-ring defect and the thread-safety
defect again — correctly, and for the third time between them.

The control cannot leave this loop by rewording. Every future run will re-find the
same three defects for as long as the listings contain them, and each will be
unscoreable against a ground truth that has been narrowed to exclude them.

The audit record names the cost itself: findings of this kind "accumulate in the
queue that decides whether a review may finish, and they are what halted the first
attempt at this run."

## A second, independent defect found in the same registry

Seven of the 22 criticals carried a verdict of ERROR. Five of them (C0013-C0017)
held a falsifier truncated to exactly 134 characters, each ending mid-literal at
``re.findall(r'`` and failing with "unterminated string literal".

The extractor terminated a falsifier at the first triple-backtick it encountered.
A falsifier that opens a markdown target and parses its fenced code blocks must
mention the fence delimiter, so it truncated itself at that point.

The selection pressure runs the wrong way. A falsifier that correctly opens and
parses the target is destroyed; one that pastes an inline copy of the code
survives. Rigour is penalised.

Measured across every archived registry: 571 falsifiers carrying code, 15 failing
to compile, 12 with the truncation signature. The distribution is the evidence:

| Run | Falsifiers | Broken | Truncated |
|---|---|---|---|
| exp53 control, 2026-08-01 | 26 | 12 | 11 |
| exp42 composer | 53 | 1 | 1 |
| exp47 divergence | 58 | 1 | 0 |
| exp48 chemistry exam | 35 | 1 | 0 |

46% in the control against roughly 2% elsewhere, and the mechanism predicts exactly
that: the control is a markdown document containing code listings, so reaching the
code requires parsing fences. Every other target is Python source that a falsifier
imports directly and never mentions a fence. Targets for the remaining experiments
are markdown, so this would have worsened as the arc continued.

Fixed by requiring the closing fence to stand alone on its line, which separates a
real fence from one quoted mid-line inside a string. Non-greedy matching is retained
so responses carrying several falsifier blocks still split correctly.

**The control runs can be re-scored rather than re-run.** Re-extracting from the raw
model responses already on disk, using the corrected pattern, yields 42 falsifiers
that all compile, against 26 stored of which 12 do not. Sixteen falsifiers the old
pattern never matched at all are recovered. No paid dispatch is required to obtain a
corrected result for this experiment.

## What remains genuinely open

The keyword-based verdict reader is still a real defect and is being repaired
separately: a falsifier that fails in its own setup is recorded as having
demonstrated the defect unless its author happened to use one of three specific words
in the assertion message. Two of three tested phrasings produced a false
confirmation. That is independent of everything above and is not refuted by it.

Whether it contributed to any recorded verdict on the control is unknown, and the
seven ERROR verdicts in the later run are where to look.

## Method note

This was found while verifying a figure before it went into a paid panel prompt. The
figure originally carried ("22 critical findings, all false by construction") was
wrong in both its count and its interpretation. Checking it cost nothing and changed
the conclusion completely.

Written under CDSFL note standard v1.2 (14 May 2026).
