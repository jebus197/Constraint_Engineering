# Errata — launcher transcripts, mislabelled terminal verdict line

**Raised by the founder, 2026-07-29. No log file has been edited.**

## The defect

`bench/launch_exp42.py` is the shared launcher for the whole Exp 40–54 arc, but
it printed a **hardcoded** experiment number on its closing line:

```
Experiment 42 reached a terminal verdict at round N: <reason>
```

Every run launched through it therefore closed its own transcript claiming to be
Experiment 42. Affected runs: **Exp 44, 45, 46, 47, 48, 49** (Exp 42's own
transcript is correct by coincidence). The identical hardcoding existed in
`launch_exp40.py` and `launch_exp41.py`.

## Scope — what is and is not affected

**Not affected: every canonical run record.** The per-run directories under
`bench/logs/<run>/` — reports, registries, checkpoints, per-round model
responses — carry the correct experiment name throughout. Verified by grep
across all run directories: zero occurrences.

**Affected: the launcher stdout transcripts only** (captured to `/tmp` during
monitoring, archived here). These are convenience captures of terminal output,
not the scientific record.

The mislabel is cosmetic: it never touched a finding, a verdict, a convergence
decision, or any recorded measurement.

## Fix

The label now derives from the config's `experiment_name`
(commit on `exp39-experimental`, 2026-07-29), in all three launchers. Runs from
Exp 50 onward print their own name.

## Why the transcripts were archived rather than corrected

Editing raw captured output — even to fix a cosmetic label — would cost the
project the ability to state without qualification that no log has ever been
altered. Given that the programme's central claim is about trustworthy
verification, that guarantee is worth more than tidy transcripts. The
transcripts are therefore preserved **byte-identical**, each with a separate
`.errata` sidecar naming its true experiment, and this file records the defect,
its scope, and its resolution.

## Related disclosure — unsigned runs

Signing lapsed at the move to runner v2: the last sealed verification chain on
disk is **Exp 37 (9 April 2026)**, so **Exp 40–49 ran unsigned**. Signing was
reinstated 2026-07-29 (per-round, per-response, whole-report records with an
RFC 9162 Merkle epoch seal; failure to seal is now loud and recorded). Runs from
Exp 50 onward are signed and independently verifiable. **Exp 40–49 are not, and
no retroactive signature is possible or will be fabricated** — a signature
applied after the fact would attest to nothing.
