# Full-suite logs, 2026-10-28

`bench/logs/**` is gitignored, so a figure cited from a suite log is unreachable
to any reader without a mirror. These are byte-identical copies, kept so the
baseline figures in `resources/RECOVERY.md` can be checked rather than taken on
trust. `bench/tests/test_cited_evidence_is_recoverable_2026-09-11.py` enforces
that, and it refused the citation that had no copy here.

- `full_suite_baseline_2026-10-28.log` — the FIRST full suite since 2026-09-29.
  36 failed, 12,954 passed, 24 skipped in 5123.39 s (1:25:23), at `a39d8da6`.
- `full_suite_2026-10-28_second_run.log` — the re-run after all 36 were
  addressed. 4 failed, 13,001 passed, 25 skipped in 5319.78 s (1:28:39).
- `rss_during_suite_2026-10-28.csv` — resident memory sampled every 15 s across
  the WHOLE python process tree during the second run, because his question was
  whether the suite consumes his 8.00 GiB machine. Columns: epoch, process
  count, total resident MB, largest single process MB.

Written under CDSFL note standard v1.8
