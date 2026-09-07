# One defect shape, found 12 times in a night, and 2 things that would have made a PoC release misleading

**2026-09-07 23:40 to 2026-09-08 00:31 BST**, timestamps read from the machine clock rather than estimated. Panel `panel_poc_readiness_20260907T234500Z`, seats cc2 (Opus, 237 tool calls, 955 s) and fable (41 tool calls, 414 s), the first dispatch ever to carry the formal CDSFL schema in its system prompt. Suite after every change: **5400 passed, 4 skipped, 0 failed** in 544 s under `--netguard-strict`, pytest exit code 0. A parallel defect sweep ran 14 agents over 406 tool calls. Every figure below was measured; the commands are named where they matter.

## The shape: a bounded traversal standing in for a complete one

The evening began with a sealing procedure that failed 3 times in the founder's hands and cost a 60-mile round trip. The cause was 1 line: `chmod 600 "$STORE"/*` in `unvault()`. That glob matches **directories**, and mode 600 strips a directory's execute bit, so `targets/` and `clearances/` became untraversable and the next `tar` died with `Cannot stat: Permission denied`. Under `set -o pipefail` the script then aborted before sealing anything. It would have recurred on **every** unseal-reseal cycle, because `unvault` always restores those directories and always chmodded them shut.

That was the 5th instance of one shape in a single file. The other 4, all corrected on 2026-09-07: a manifest built with `shasum -a 256 *` that omitted 27 of 31 keys while `verify` passed against the truncated result; a store count of `ls -1 | wc -l` reporting "4 key(s)" for 29; the same construct in `verify` printing "opened: 18 file(s)" seconds after "sealed: 53 keys"; and a register that enumerated only `$STORE` while every file lived in legacy stores folded in later.

Five instances of one bug in one file is a pattern, not an accident, so a sweep was run against the whole repository for that class specifically. **8 findings raised, 7 confirmed by adversarial verification that reproduced each by execution, 1 refuted.** The refutation matters: it shows the verifiers were testing rather than agreeing.

## The severe one: a safety gate that could not see the repository

`bench/vault_keys.sh` scanned for stray plaintext keys with `find "$HOME" -maxdepth 5`. The repository sits 2 levels below `$HOME`, so a **file** inside `bench/cdsfl_registry/targets/` is at depth 6 — and that directory is exactly where the Experiment 48 leak came from, and where the 7 answer keys for experiments 48 to 53 were tracked.

Measured on the live machine: that predicate returns **0** matches; an unbounded pruned walk returns **6**. `bench/arc_sequencer.sh:50` gates an entire experiment arc on `status | grep -q '^VAULTED'`. So the gate standing between a review panel and live answer keys could not see the directory those keys had actually lived in. Restore any of them — a `git checkout` of a pre-move commit, a worktree, a repair session — and the arc launches regardless.

A committed measurement was invalidated by the same ceiling. The file recorded "the corrected patterns match 0 files inside the repository, so the exclusion suppressed only true positives". That 0 came from the truncated walk; the true count is 6.

**Cost of the repair, measured rather than assumed:** the bounded scan finds 0 in 0.37 s, the pruned unbounded scan finds 6 in 8.56 s, taking `status` from 2.15 s to about 11.5 s. It runs once per arc.

Removing the ceiling then exposed a second defect it had been masking: the pattern `*canary*.json` matched 6 run-output files whose **directory** is named `sim45_canary_*`. Measured before narrowing: 6 matches, **0 answer-bearing** — no `canary_id`, no `defect_id`, no `planted_location`, no `seeded_defects`, no catalogue array, only a `finding_catalogue` metadata block holding a record count of 22 and a path to a deleted temp directory. Narrowed to `canary_catalogue_*.json`, which is what the 2 real catalogues are named. The residual is stated rather than assumed away: a catalogue named otherwise would be missed by that clause, though `*planted*.json` would likely still catch it.

## A third defect, found only because the test was written with an empty value

Writing a hermetic fixture with `CDSFL_LEGACY_STORES=""` surfaced something the live configuration hides. `printf '%s\n' "$STORE" ""` emits a blank line, `paste -sd'|'` turns it into a **trailing pipe**, and `grep -Ev "^(\/some\/store|)/"` then contains an empty alternation branch that matches the empty string. The filter matches every absolute path and suppresses **every** stray file. BSD grep warns `empty (sub)expression` and proceeds; the scan prints VAULTED with plaintext keys on disk. A total false all-clear from one empty configuration value, latent only because the live config happens to name 3 legacy stores.

## Two findings that would have made a formal release misleading

**The results document did not disclose that its headline run was contaminated.** `docs/EXPERIMENTAL_RESULTS.md` reported Experiment 48 as CONVERGED with `γ_crit 0.8847 — the highest pair in the record`, and disclosed only a reproducibility caveat about an absolute path. The file contained **0** occurrences of `C0012`, `key access`, or `compromis`. Meanwhile the project's own formal directive states at `cdsfl_core_formal.md:539` that "Exp 48's 6/6 detection figure **cannot be reported as a blind measurement**", because a panel member wrote a falsifier that opened the answer key, read a claim's recorded truth value, and printed the entire planted set — with its own verdict CONFIRMED and status CLOSED, so nothing in the run flagged it. The disclosure existed in the overnight notes, in the integrity note, and in the schema handed to every model. It was absent from the one document a reader would consult. Now added.

**The release would have hidden its own best proof.** `bench/tools/simulated_bench.py --scripted` runs **18 of 18 stages with every API credential unset** — verified by execution with `OPENROUTER_API_KEY`, `DEEPSEEK_API_KEY`, `GEMINI_API_KEY`, `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` all removed from the environment. It demonstrates the founding principle directly: a model asserting `VERDICT: CONFIRMED. Two models agree this is a critical defect.` scores **REFUTED**, because its falsifier exits clean. It was mentioned **0** times in `START_HERE.md`, `README.md`, `docs/REPRODUCING.md` and `scripts/cdsfl_onboard.py`. Every documented path led to paid dispatch, so a reader without credentials would reasonably conclude the project was unreproducible without the author's keys. It never was. Now documented in both entry points.

## The panel refuted its own convergence declaration

The cc2 seat declared convergence under section 10 of the schema, then two commissioned checks returned above-threshold findings, and it withdrew the declaration rather than folding the findings in quietly. That is the sufficiency criterion behaving as specified, and it is the first time this panel has run with the formal schema in its system prompt — measured, **0 of 37** dispatchers had ever loaded it, against a hand-written prompt of 3,015 characters.

Its hardest finding concerned the previous night's repair. The tool-call counter fix was **partial and unguarded**: mutating `set_tool_log_sink(str(_sink))` to `set_tool_log_sink(None)` restores the original "0 by construction" defect exactly, and **88 of 88** relevant tests still passed. Worse, a 4th code path had never been enumerated — the exception handler reads `tool_log`, but the sink is only read back **after** `call_claude_cli` returns, so a seat that times out or has every attempt rejected reported `n_tool_calls=0` while the sink on disk held 13. The counter read 0 precisely when a seat failed, which is the case the panel actually hit on 2026-09-06 and again on 2026-09-07. Both are now fixed and both mutations now fail a test.

## Corrections to claims made earlier in the same session

**"7 answer keys are recoverable from the public repository" was wrong.** The blobs are retrievable, but the only ref reaching them is the local branch `exp39-experimental`; no remote carries it, and a history rewrite had already run on 2026-08-27. The real public residual is **1 file of 635 bytes**, Experiment 55's control ground truth, added 2026-08-20 and deleted 2026-08-26. Reachability was measured; which ref reached them was not. `git log --all` traverses local branches too.

**"8 of 37 dispatchers compose the schema, Wilson [11.4%, 37.2%]" was a substring match** on `cdsfl_registry`; those files reference it to load a target module. The true figure is **0 of 37**, Wilson [0.0%, 9.4%].

**A test written during this session could not fail.** `assert "VAULTED" in stdout` passes when the output reads `UNVAULTED`, because the second string contains the first. It was caught within the hour by mutating the scan pattern and watching the test stay green — the assertion could not see the defect it existed to catch. The same class it was written to guard against.

## Still open

The single public 635-byte file is a decision, not a defect: Experiment 55's target is spent regardless, because both its runs began 3 days after the file was published, so purging history recovers no validity. A rewrite would re-hash **353** of the 955 pushed commits and break **174** hash citations across **57** files. Both review seats independently recommended documenting and retiring rather than rewriting.

Six further sweep findings remain unapplied, and **2 of them are containment gates of the same class as the one repaired tonight** — a first draft of this note said none touched a safety gate, which was wrong and was corrected by reading them. `bench/arc_sequencer.sh:74` counts the panel working directory with `find -maxdepth 1 -type f` and then requires exactly 1 file, so exam documents in a subdirectory are not counted and the gate passes while a panel can reach siblings. `bench/arc_sequencer.sh:173` has the same shape on the staging directory. Both decide whether an experiment leg may launch.

The other 4 are lower consequence. `scripts/cdsfl_qc.py:613` uses `doc_dir.glob("*.md")` and therefore sees 13 top-level documents while missing **139** nested ones. `scripts/supersession_check.py:142` has the same construct. Two are in test files, including a note-standard checker whose `glob("*.md")` cannot see the 10 notes held in subdirectories — though **0** of those 10 currently violate the standard, so that gap is latent rather than active.
