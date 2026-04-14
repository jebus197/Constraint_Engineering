# Read This First — 500 Error Self-Diagnosis

You hit a 500 Internal Server Error from the Anthropic API. Before doing anything else, read this and self-diagnose. **Do not start editing code.** A 500 is a server-side failure; your code is not the first suspect.

**Constraint:** the model is Opus 4.6 Max. This is non-negotiable. Do not suggest or attempt a model switch. The other Claude session is also Opus 4.6 Max and works fine — this is a runtime issue, not a model-choice issue.

## What This Error Means

`500 {"type":"error","error":{"type":"api_error","message":"Internal server error"}}`

The request reached Anthropic and their server failed to handle it. This is categorically different from the 401 you had earlier (that was auth; it has been fixed — see `CLAUDE_CODE_PROVIDER_FIX.md`). A 500 cannot be fixed by editing the bench script, because the bench script is not what is failing — the server is.

Anthropic's status page at the time of writing said "All Systems Operational", but the status page typically lags real incidents by 10–30 minutes.

## Possible Causes (Most Likely First)

1. **Transient Anthropic hiccup.** Most 500s are one-off. A single retry after a short wait usually succeeds. No code change needed.
2. **Oversized prompt.** CDSFL directives + full task + multi-pass history + accumulated findings can push prompts past internal limits that manifest as 500s rather than clean size-limit errors. If every retry on the same request fails identically, this is the likely cause.
3. **Edge-case content in the request.** Specific token sequences, malformed escape characters in accumulated findings, or certain content patterns can occasionally trigger server-side 500s rather than a clean 4xx.
4. **Temporary endpoint degradation.** Individual API endpoints can degrade without the status page reflecting it.

## Self-Diagnosis Protocol

Work through these in order. Do not skip ahead.

### Step 1: Is it transient?

Wait 30 seconds. Retry the exact same command once. If it succeeds, it was transient. Continue the run. Change nothing.

If it fails again with 500, proceed to Step 2.

### Step 2: Is it the specific request?

Try a smaller, simpler task with the same provider and Opus 4.6. Use `--dry-run` first to confirm the pipeline, then run a single minimal task from the task set with shortened context (fewer passes, trimmed directives if possible).

- If the simpler task succeeds: the failing request itself is the problem. Most likely oversized prompt or edge-case content. Reduce passes, trim accumulated history, or split the task.
- If the simpler task also fails: proceed to Step 3.

### Step 3: Is it endpoint degradation?

Check `https://status.anthropic.com/` directly. If an incident is listed, wait it out. If the page is clean but Step 1 and Step 2 both failed, back off and retry with exponential spacing (30 s → 2 min → 5 min → 15 min). Log the `request_id` from each failure.

If all of that still fails, stop. Do not keep throwing requests.

## Measures to Not Repeat This

- **Do not loop-retry in tight succession.** Back off (30 s → 2 min → 5 min → 15 min). Hammering a failing endpoint does not make it return sooner and may trigger rate-limit penalties on the subscription.
- **Do not assume it is your code.** The 401 fix was a code fix because the script was routing to the wrong auth path. A 500 is not that — your request is reaching the right server. Do not "fix" code that is already correct.
- **Do not switch models.** Opus 4.6 is required. If Opus 4.6 is temporarily unhappy, wait for it rather than substituting another model.
- **Log the `request_id`.** Every 500 includes a `request_id` (e.g. `req_011Ca3vxc967U5UoKmyqBYd7`). Capture every failure ID to the run log before retrying.
- **Check prompt size before dispatching.** For the `claude-code` provider, combined system + user prompt over ~150k tokens is the danger zone. The bench framework has context-budget tooling; use it rather than sending the full accumulated chain blind.

## If None of This Works

Stop. Write what you tried to a log file in `bench/logs/` with timestamps and the `request_id` for each failed attempt, then hand back to the human with a short status summary. Wait for further instruction. Do not improvise.

## What You Should Now Do

1. Re-read the command you were running when the 500 occurred.
2. Go to Step 1 of the Self-Diagnosis Protocol.
3. Work through the steps in order.
4. Do not edit `run_benchmark.py` or any other bench code unless the diagnosis explicitly indicates a code-level issue (it almost certainly will not).
