# Reading `immune_pipeline.log`

This archive contains **252 synthetic lines** produced by the test suite,
interleaved with genuine experiment records. They are not experimental data.

## Why they are here

`bench/immune_agents.py` attaches a logging FileHandler to this file at **import**
time. Every `pytest` run imports that module, so every test run appended its
fixture output here — continuously from 2026-05-15T21:52:18 to 2026-07-29T20:22:26.

Fixed 2026-07-31: under pytest the shadow log is redirected to a scratch
directory (`CDSFL_SHADOW_LOG_DIR` overrides). Pinned by
`bench/tests/test_archive_is_not_written_by_tests.py`.

## Why they have not been removed

`bench/logs/` is archival. It is never edited; corrections are filed beside it,
as this file is. Rewriting the log to tidy it is precisely what that rule exists
to prevent, so the lines stay.

## How to filter them

Synthetic lines carry the model id `TestModel`:

```bash
grep -v TestModel bench/logs/immune_pipeline.log
```

That is exact — no genuine panel model is named `TestModel`.

## What was NOT committed

A further ~1,500 lines of test output accumulated in the working tree on
2026-07-31 before the fix landed. Those were never committed and were discarded
rather than added to the record. The 127 genuine lines caught up in the same
delta — from the halted zero-plant control run — were preserved first, at
`bench/logs/exp53_control_zero_live_20260729T222431Z/immune_pipeline_excerpt.log`.
