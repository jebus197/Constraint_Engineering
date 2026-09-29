# The Vault Guard's Timeout Is MARGINAL, Not Impassable — CORRECTED 2026-09-29 15:13

> **CORRECTION, 15:13 BST, and it overturns this note's headline.** When written, this note reported the guard failing **2 of 2** in-run with no in-run success observed, and concluded the shakedown was hard-blocked. **A third attempt PASSED.** A non-invasive `sitecustomize` probe on `PYTHONPATH` — which modifies nothing in the repository — timed the guard's own subprocess inside a live run at **30.77s, rc=0**, against ~11s standalone and a 120s cap. **Arm 1 is now running.**
>
> **What this changes.** The guard is not impassable; its cost inside a run is ELEVATED (roughly 3x) and VARIABLE, and on 2 of 3 attempts that variance carried it past 120s. So this is a **flaky guard with a marginal timeout**, not a false refusal that always fires. In-run record: **1 pass of 3**. Standalone: **9 passes of 9**, 11.0 to 12.4s.
>
> **What this does NOT change.** The keys are vaulted, the guard still fails closed, and the root cause of the 3x in-run elevation is still unidentified. The recommendation below is now better supported, not worse: a marginal timeout on a fail-closed guard is exactly the case a bounded retry exists for. The ruling is less urgent, because the run can sometimes proceed unaided.
>
> **The original text follows unchanged**, because a note that quietly rewrites its own conclusion destroys the record of how the conclusion moved.

# The Shakedown Is Blocked By A False Refusal In The Vault Guard, And The Cause Is Unidentified

**2026-09-29, 14:50 BST.** [BLOCKING] — needs the founder's ruling. Plain-English companion at `~/Desktop/CDSFL_tts/Shakedown_Blocked_Vault_Guard_2026-09-29.txt`.

## What happened

The simulated shakedown was launched under `cy` at 14:38:45 (`bench/tools/commissioning_arms_2026-09-21.py --run`, 4 arms, all `-SIM` stand-ins, 0 spend). Arm 1 failed at round 0:

> `RuntimeError: cannot verify the scoring keys are vaulted (TimeoutExpired); refusing to start an exam run`

The run was paused immediately rather than allowed to burn through arms 2 to 4, which would have hit the same wall. Arm 1 was re-run alone at 14:45:10 and **failed identically**. In-run: **2 failures of 2 attempts.**

## The guard, and why it is right to exist

`bench/reference_runner_v3.py:13338-13369`. When `cfg.panel_cwd` is set — which a sandboxed simulated run always sets, per the founder's 2026-09-01 confinement ruling — the runner shells out to `bash bench/vault_keys.sh status` with `timeout=120` and refuses to start unless the output begins with `VAULTED`.

Its own comment records why it must live there: panel confinement, read-only staging and the vault govern what the *panel* can reach, but **two paths run model-authored code with the operator's own credentials** — `reverify_falsifier` and the `execute_python` tool. The 2026-07-29 adversarial audit found a falsifier that read every answer key by absolute path and wrote the planted sets to `/tmp`. *"Against that, the only defence is that there is no plaintext key to read."*

**The guard fails closed. That is correct and must stay.**

## The keys ARE vaulted — this is a FALSE refusal

Run by hand, the same check succeeds every time:

> `VAULTED — no plaintext key file on disk in any known or scanned location`

**6 successful standalone runs, 0 failures**, in ~11s each. The refusal is not "the keys are exposed"; it is "we could not finish asking".

## Nine hypotheses, all measured, all refuted

| # | hypothesis | measurement | verdict |
|---|---|---|---|
| 1 | I/O starvation from the 20,800-file sandbox copy | 11.8s under a live copy vs 11.2s idle — **1.05x**, 10.2x headroom | REFUTED |
| 2 | the sandbox's copy of the script differs | `cmp` — **byte-identical** to live | REFUTED |
| 3 | it hangs when run from the sandbox path | 10.9s, `VAULTED=True`, from the exact failing directory | REFUTED |
| 4 | the script blocks on a prompt, git, network or keychain | no `git`, `security`, `curl`, `ssh`, `sudo` or interactive `read` in `status()` | REFUTED |
| 5 | the launcher alters the environment | sets **only** `CDSFL_SANDBOX_ROOT` | REFUTED |
| 6 | `cwd` inherited from `apply_panel_cwd` breaks it | 10.6s from an empty temp dir | REFUTED |
| 7 | `HOME` is unset, breaking config resolution | fails in **0.0s** with a clear error, not a hang | REFUTED |
| 8 | importing `reference_runner_v3` slows subprocesses | 10.9s after import (import itself 0.2s) | REFUTED |
| 9 | `apply_panel_cwd` slows subprocesses | 10.9s after applying it, exactly as `run_experiment` does | REFUTED |

**No escape hatch exists**: no `VAULT_TIMEOUT`, `SKIP_VAULT` or equivalent anywhere in `bench/` or `scripts/`.

**The unexplained part is the interesting part.** For the guard to trip, the in-run check must exceed **120s** against a **~11s** standalone cost — an **11x** slowdown reproducible in the run and reproducible in *nothing else tried*. If something in a live run makes spawned subprocesses an order of magnitude slower, that bears on everything else the runner spawns, not only this guard.

## Why this stops here rather than being patched

**It is a blocker by the founder's own definition** — *"anything that required a verdict from me before you could meaningfully move on."*

The obvious repair is to raise the timeout and add a bounded retry. That would **not** weaken the control: the check still requires output beginning with `VAULTED`, so it cannot pass on exposed keys; it would only stop the guard refusing because it ran out of time to ask. But:

1. **The root cause is unidentified.** Patching the symptom of an 11x slowdown would mask a signal rather than explain it, which is what P-pass forbids.
2. **This guard is the last line protecting the answer keys**, and the sealed store at `~/.config/cdsfl/scoring.env` is reserved to the founder in person. Nothing in this investigation touched it — only the script that reads it was read.

## The ruling sought

**Recommended:** raise the guard's timeout (120s → 300s) and add one bounded retry before refusing, keeping the fail-closed `VAULTED` requirement exactly as it is; and record the unexplained 11x subprocess slowdown as a separate open finding rather than letting the patch bury it.

**Alternative:** hold the shakedown until the slowdown is explained.

The difference matters because the first unblocks the run today and leaves the anomaly visible; the second keeps the anomaly in front of us at the cost of the run.

## State

Nothing else is blocked. Everything from today is committed and pushed (`e89a316`). The paused run left 3 kept sandboxes under `/private/var/folders/.../cdsfl_sim.*` for inspection; arm 1's original was already reaped. Arms 2, 3 and 4 have not run.
