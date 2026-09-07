# The tool-call counter read 0 by construction, and a provenance that was invented to explain a real measurement

**7 September 2026, 15:24 to 16:00 BST.** Panel run `panel_toollog_20260907T152800Z`, seats cc2 (Opus) and fable, both dispatched into a writable sandbox copy. Suite re-run after every change. All figures below are measured, and the scripts that produce them are committed alongside.

## The headline: a panel counter that could only ever say 0

`bench/confer_maths_panel_2026-09-05.py`, in `dispatch()`, initialised `tool_log = []` and reassigned it on exactly 1 of its 3 route branches — the `openrouter` one. The `claude_cli` branch, which carries the cc2 and fable seats, never touched it. So `n_tool_calls` was **0 for every Claude-route seat on every panel this dispatcher has ever run**, whatever work those seats actually did. The function's own docstring, 12 lines above, claimed the opposite: that every seat's tool calls were recorded so the claim "this panel used tools" was "checkable rather than asserted". It was not checkable. It was 0, with no path to any other value.

The evidence that made this legible: `fable.json` of 6 September 23:01 carries `n_tool_calls: 0` beside a reply quoting verbatim `pwd` output and a real sandbox path. That record is unreadable as either proof of tool use or fabrication of it, because the only field that could separate the two was hard-wired.

The sink mechanism `set_tool_log_sink` already existed. `set_tool_log_sink` (`bench/experiment_11_orchestrator.py:331`) is thread-local, which makes it safe under the dispatcher's `ThreadPoolExecutor`, and setting it also switches the CLI from `--output-format text` to `stream-json` — the only format that carries `tool_use` blocks at all. **1 of 37 dispatchers calling `call_claude_cli` wired it**, Wilson 95% interval [0.5%, 13.8%]. The working pattern was copied from that one, `bench/confer_panel_2026-08-28.py:173`, and extended to read the sink back into the seat record rather than leaving it in a side file.

**Built and unwired**, which this same file names 40 lines below, about its sibling mechanism `set_panel_cwd`, as "the project's most repeated failure shape".

Proof by execution rather than by reading, which is what `execute-do-not-grep` requires: the very next dispatch reported `[cc2] ok=True chars=10780 tools=33 368.4s` and `[fable] ok=True chars=7714 tools=26 506.3s`. cc2 confirmed the sink mechanism from the inside by reading its own process ancestry and finding `--output-format stream-json` on the command line of its parent.

## A number I corrected that did not need correcting, and a story I invented for it

`sk_threshold_shadow`'s docstring read "s_star reads 0.0 in 3181 of 3181 archived records, Wilson [99.88%, 100.00%]". A measurement gave 3816, so the sentence was changed to 3816, and an explanation was written into the permanent record: that 3181 was the line count of `dynamic_management.py`, the Experiment 12 artefact, pasted where the gate count belonged.

**That explanation was false, and it was never tested before being written down.** `bench/dynamic_management.py` is 78 lines. The measurement, run by both seats independently and reproduced here:

| encoding of `s_star` | records |
|---|---|
| float `0.0` | 3181 |
| string `"0"` | 635 |
| total | 3816 |

3181 is the exact count of gate records whose `s_star` is the literal float `0.0`. The other 635 carry the string `"0"`, confined to 4 `sim45_*` run families that stringify every numeric field. A strict `x == 0.0` gives 3181; a coercing `float(x) == 0.0` gives 3816. **Neither number was ever an error. They are 2 predicates over 1 corpus.**

The coincidence that should have been found incredible — a stray line count of 3181 landing to the digit on a real statistic of the very field under discussion — was instead used as the evidence for the story.

The sequence is worth keeping because no party was right by holding a position: a strict-float count of 3181 was stated; the cc2 seat flagged it against 3816; that seat was refuted on a bad measurement; the refutation was then reversed and the seat's own transcription theory adopted without test; and the seat finally re-measured, refuted its own theory, and established the encoding split. **Measurement settled what neither position had.**

Three further defects in that same corrected docstring, all found by the seats and all now repaired: the claim that 3 independent routes agreed "every one reading 0.0" was false at the type level; `scripts/measure_sk_threshold_gate_fire_rate.py` was cited as an independent corroborating route when it never reads `s_star` at all and agrees at 3816 only because the 2 fields co-occur exactly, which is agreement by co-occurrence rather than corroboration; and "7351 archived files" matched neither corpus it might have meant. `bench/logs` holds 6663 JSON files carrying 3816 gate records; `bench/logs_quarantine` is excluded and holds 78 more, so a repo-wide count would be 3894.

**The load-bearing claim survives all of it.** `passes_threshold` reads false 0 times under every method and every corpus tried. The admissibility gate has never rejected a fix whether the denominator is 3181, 3816 or 3894. The interval moves; the finding does not.

## Two instruments, and the boundary between them

A stated figure such as 3816 and a stated interval such as [99.90%, 100.00%], placed side by side, are arithmetically linked, so a half-done correction is detectable without touching the archive. A figure that is wrong but internally coherent, as 3181 with [99.88%, 100.00%] was, is not. These need different instruments and neither implies the other.

`scripts/wilson_interval_consistency.py` checks coherence. Its first draft claimed to catch the original defect; run against it, the script printed "every stated interval agrees" and exited 0, because [99.88%, 100.00%] is exactly right for 3181 of 3181. Worse, cc2 proved the blind spot was structural rather than occasional: at k equals n the Wilson lower bound is n/(n + z squared), which is strictly increasing in n, so a stale interval left by any **upward** correction is necessarily wider than the truth, and the script's own "wider is conservative" rule then forgave it. **The single defect class the file was written for was the one class it could never fail on.** Repaired by consulting `_n_that_fits`, which was already computing the band of n implied by a stated bound and was only ever called on the failing path.

cc2 also defeated the attribution rules with 4 constructed cases. The serious one: "3816 of 3816 across 70 files, Wilson 95% CI [...]" was silently skipped, because the bare integer 70 — the real file count from this very archive — was read as another statistic claiming the interval. Competing statistics in this corpus are decimals, such as Cohen's kappa 0.837 and AUC 0.976; bare integers are counts and file tallies. Integers no longer break attribution and decimals still do.

The complementary instrument, `bench/tests/test_stated_gate_count_matches_measurement_2026-09-07.py`, re-measures the archive and compares the measurement to the prose — a producer and a consumer executed against each other, which is the only shape that can catch a wrong-but-coherent count. Falsified by reintroducing each defect in turn: the original 3181 figure fails the measurement test, the half-fix fails the interval test, and neither catches the other's case.

cc2 reported that test as never committed. It was committed, but **after** `panel_sandbox.build` took the seat's copy. A seat's "file not found" is evidence about the copy, not the repository, whenever the tree is edited while a panel is live. It should not have been: the standing rule is not to edit during a live panel, and that rule was broken here.

## The operator control plane was outside every watch

At 15:04:45 a seat running under the panel sandbox wrote to the real `~/.claude/settings.json`. `panel_sandbox.canonical_was_touched` did not fire and could not have: it digests the repository's tracked files, and `$HOME` is not among them. The write was additive and benign, appending a hook entry and removing nothing, which is luck rather than containment.

These are not ordinary files. `settings.json` names hooks, which are commands executed on every turn of every session; `hooks/*.py` is their code; `CLAUDE.md` is the directive set handed to every model. `control_plane_fingerprint` and `control_plane_was_touched` now digest 143 such files before and after a panel.

**Detection, not prevention, deliberately.** The obvious prevention is to rewrite `HOME` for the seat process. This project already ran that experiment from the other end: `--bare` was added to confine the CLI, and because it also skips keychain reads it selected an auth mode this account does not have, so every headless dispatch returned "Not logged in". Moving `HOME` would break OAuth the same way. Reachable pointer, detected use — the layered position taken everywhere else.

## A rejected attempt's tool calls were erased by the attempt that replaced it

Found by cc2 within an hour of the counter being wired, with an executed reproduction. The sink write sits inside `call_claude_cli`'s retry loop and `write_text` replaces rather than appends, so when `accept` rejected attempt 1 and attempt 2 succeeded, the seat record kept only attempt 2.

The bias runs the wrong way, which is what makes it worth a permanent test. `accept_reply_or_work` rejects a short reply with no work beside it — the holding-note case it exists for. The attempt most likely to be rejected is therefore the one that spent its clock running tools and then ran short. The erased attempt is systematically the busiest, so the loss biases the record toward under-reporting precisely the tool use the counter exists to evidence. Reproduced at 7 calls then 2 calls recorded as 2, losing 7; now 9 with a per-attempt breakdown.

Two smaller defects from the same review, both repaired: the exception path built its record without the counter keys, so a seat that crashed printed `tools=native`, indistinguishable from a route that has no counter; and there was no freshness guard, so a re-dispatch into an existing log directory would read the previous run's sink as this run's.

## Arithmetic in 2 delivered notes

`Final_Report_2026-09-05.md` and `TODAY_2026-09-05.md` both stated "90 escalated + 41 irreducible across 6,929 findings = 1.30%, Wilson [1.06%, 1.59%]". 90 plus 41 is 131, which is 1.89%. The percentage and the interval were 90's alone, carried across a sum that changed the numerator. Corrected additively, with all 3 figures and their own intervals: 90 of 6,929 is 1.30%, Wilson [1.06%, 1.59%]; 41 of 6,929 is 0.59%, Wilson [0.44%, 0.80%]; 131 of 6,929 is 1.89%, Wilson [1.60%, 2.24%].

## A citation checker that manufactured its own findings

`bench/tests/test_line_citations_resolve_2026-09-01.py` matched filenames with the class `[A-Za-z0-9_/]`, which excludes the hyphen. Every citation to a **dated** filename, which is most new files in this repository, was mangled at the last hyphen: `confer_panel_2026-08-28.py:173` parsed as `28.py`, a file that does not exist, and was then reported as a broken citation. Measured across the repository: 913 citations parsed, 2 mangled this way, and 0 hyphenated citations naming a file that is genuinely missing.

## The process that appeared stuck

A `tail -f` running for 5 days was following `.../cdsfl-panel-e8co9jbb-repo/.../bhvsetsk8.output`. That file, and the temp repository root containing it, no longer exist — casualties of the `rmtree(ov.parent)` line that removed 179 TMPDIR entries on 7 September. `tail -f` on a deleted file blocks indefinitely and produces nothing. It is not stuck on work; there is no work behind it.

## Attribution, recorded before the alarm rather than after

The canonical-tree alarm fired at the end of the panel naming 7 files. A snapshot of the tree taken **before** dispatch shows all 7 are edits made from the main session while the panel was live. Alarm minus snapshot is the empty set: no seat touched the canonical tree. This check exists because on 7 September a panel seat was blamed in writing for a sandbox destruction that was caused by a cleanup line in the main session.

## Status

Suite: 5379 passed with 9 failures on the first run, all 9 traced and repaired. 6 were artefacts of the tree being edited while the suite ran. 3 were real and caused by the changes above: the derived experiment ledger went stale because a docstring expansion shifted a cited line number, and the citation checker mangled a hyphenated filename. The clean re-run against the settled tree returned **5392 passed, 0 failed, 0 errors** in 518 seconds under `--netguard-strict`.

Seat replies in full: `bench/logs/panel_toollog_20260907T152800Z/cc2.json` and `fable.json`, with provable tool logs beside them in `cc2.tools.json` (33 calls) and `fable.tools.json` (26 calls), and 11 proposed file edits captured untested in `seat_proposals.diff`.
