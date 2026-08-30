# LATENT — the discrimination control will mint false mechanical faults on Bench Run 2

**Severity: high, and latent rather than historic. It has never fired. It is wired, and BR2 is its first
real exposure.**

Found by the fable reviewer on the repair-loop panel, 2026-08-30, and independently verified here including
one qualifier the review does not carry.

## The assumption, in the code, in its own words

`reference_runner_v2.py:3340`, justifying why the ownership rule is waived for a fix-derived corrected copy:

> *"The ownership rule does not apply. It exists because a passage correcting a DIFFERENT claim mints a
> mechanical fault against a sound instrument; **a finding's own proposed fix corrects THIS claim by
> construction**, whoever wrote the falsifier now attached to it."*

**That assumption is false about half the time.** Measured the same day, commit `adb566b`: of 246 archived
findings that produced a verdict, **126 fixes do not silence their own falsifier**.

The comment names the exact harm it is waiving — *"mints a mechanical fault against a sound instrument"* —
and then rules it out on a premise that measurement refutes.

## What happens when the fix is the broken half

`_apply_discrimination_control`, the `DISC_FAILED` branch (`:3728`):

```python
entry["falsifier_verdict"] = "NON_DISCRIMINATING"
entry["verified"] = False
entry["escalated"] = True
entry["mechanical_fault"] = True
if entry.get("status") == "CONFIRMED":
    registry.resolve(cid, "UNCONFIRMED", round_idx)
```

A sound falsifier attached to a real defect is stamped non-discriminating, **un-confirmed**, and escalated
as an instrument fault. Three false statements about a working instrument.

**The un-confirm is not gated.** `discrimination_control_blocks` defaults `False`, but it guards a
*different* site (`:3871`). The `registry.resolve(..., "UNCONFIRMED", ...)` above runs unconditionally on
`DISC_FAILED`.

The apparatus does verify itself — tripwire for overlay interception, a repeat probe for determinism, a
baseline check for reproduction. **None of those checks the corrected copy is actually corrected**, which is
the one assumption that fails.

## The qualifier the panel did not carry: it has never fired

Measured across **every archived run**:

```
mechanical_fault stamped        0
NON_DISCRIMINATING              0
```

**Zero.** Not once, in any experiment.

The reason is timing, not safety. `_derive_corrected_copy_from_fix` was wired on **2026-08-23** (`b312b84`).
The only runs since are the two `exp55_v3_control` round-0 halts. **No full experiment has executed against
this path.**

So: no past result is contaminated, no finding was wrongly un-confirmed, and nothing in the archive needs
re-scoring. **Bench Run 2 is the first exposure**, and at a measured ~51% base rate for the triggering
condition it would not be a rare event.

## Disposition

The fable reviewer built a repair in its worktree — a `DISC_FIX_UNPROVEN` outcome that separates *"the fix
did not cure it"* from *"the instrument is broken"*, holds `verified` False without un-confirming, and asks
the model for a `CORRECTED_COPY` so the ambiguity can be resolved by an ask-path copy. The reviewer's own
worktree is discarded by design, so the code does not survive; the design does, and it is recorded here.

**Not ported tonight.** It supersedes a founder-era assumption from 2026-08-22, it changes what a verdict
means, and the reviewer itself lists three items needing founder ratification — including that the residual
ambiguity now fails in the opposite direction. That is a ruling, not a repair.

**But it should be settled before BR2 runs, because BR2 is when it stops being latent.**
