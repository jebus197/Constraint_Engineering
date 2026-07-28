# Claude Code Provider Fix (13 April 2026)

## Problem

Running `--provider anthropic` in `run_benchmark.py` fails with:

```
API Error: 401 {"type":"error","error":{"type":"authentication_error","message":"Invalid authentication credentials"}}
```

## Root Cause

`--provider anthropic` routes to `call_anthropic()`, which uses the Anthropic Python SDK directly. The SDK requires `ANTHROPIC_API_KEY` in the environment. This key was intentionally removed from `.env` because the project uses Claude Code Max subscription auth, not pay-per-token API credits.

Max subscription auth only works through `claude -p` (the CLI), not the Python SDK.

Other scripts already handled this correctly:
- `run_round_robin.py` strips `ANTHROPIC_API_KEY` from env and uses `claude -p`
- `interactive_smoke.py` does the same
- `run_benchmark.py` was the outlier — it still used the SDK path

## Fix Applied

Two new providers added to `run_benchmark.py`:

- `claude-code` — uses `claude -p` with Max subscription auth (300s timeout)
- `claude-code-thinking` — same, 600s timeout for thinking models

Both follow the same subprocess pattern as the existing `codex` provider. No API key required.

## Usage

Replace `--provider anthropic` with `--provider claude-code`:

```bash
# Before (broken — needs API key):
python3 bench/run_benchmark.py --provider anthropic --model claude-opus-4-6 ...

# After (uses Max subscription):
python3 bench/run_benchmark.py --provider claude-code --model claude-opus-4-6 ...

# Thinking variant:
python3 bench/run_benchmark.py --provider claude-code-thinking --model claude-opus-4-6 ...
```

## What NOT to Do

- Do not re-add `ANTHROPIC_API_KEY` to `.env` — that burns API credits instead of using the Max subscription.
- Do not use `--provider anthropic` unless you have a valid API key and intentionally want to use pay-per-token billing.
- The old `anthropic` / `anthropic-thinking` SDK providers are preserved but should not be the default path.

## Files Changed

- `bench/run_benchmark.py`: added `call_claude_code()`, `call_claude_code_thinking()`, updated `PROVIDERS` dict and `env_requirements` comment.

## Verification

793/793 tests pass after the change.
