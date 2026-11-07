# The complete board, the prediction it refuted, and the comparator that would have agreed with it

2026-11-07, Europe/London. Written under CDSFL note standard v1.9 (1 November 2026).

## Summary

A complete test board was run against a clean committed tree at `e796a010` and returned 15,858 passed, 11 failed and 37 skipped in 8,247.78 seconds, 2 hours 17 minutes, from `python3 -m pytest bench/tests/ -q --netguard-strict`. A prediction had been committed before the run started. It was right about the hard half and wrong about the easy half, and the instrument built to judge it was briefly capable of confirming it for the wrong reason.

## The partition against the previous board

The previous complete board, recorded at `e0feed27` on 2026-11-06, carried 17 failures. Set against it:

- 16 of the 17 are FIXED, 0.941176, Wilson 95% [0.730180, 0.989540], Clopper-Pearson 95% [0.713111, 0.998512].
- 1 of the 17 is STILL RED, 0.058824, Wilson 95% [0.010460, 0.269820], Clopper-Pearson 95% [0.001488, 0.286889]. It is the branching-ratio check, and it is the exact failure the prediction named as the survivor.
- 10 failures are NEW.

Both interval routes agree to within 1.2e-16 on every figure above. Producer: `scripts/compare_this_board_against_the_record_2026-11-07.py`.

## The prediction, scored

The pre-registration at `experimental_notes/PREDICTION_full_suite_2026-11-07.md` made 2 claims. The first was that exactly 1 of the 17 would still fail and that it would be the branching-ratio check, which is a decision held by the founder rather than a repair available to the assistant. That claim HELD, exactly. The second was that no new failure would arise from the work since. That claim is REFUTED by 10.

The asymmetry is the finding. The clause that required understanding which repairs held was correct; the clause that required the predicting session to account for what it had itself done to the board was not.

## The comparator would have confirmed the refuted clause

The instrument written to produce the partition carried 3 refusals, each aimed at a false result this project had produced before: an unfinished log, a narrower run, and a missing baseline. All 3 passed, and the instrument still reported nothing.

The suite wrapper records the board it has just finished, overwriting `resources/suite_record.json`. That overwrite is correct for the citation function that reads it, and it destroys the only baseline the comparator had. Run after a board, the comparator partitioned the board against ITSELF and reported 0 fixed, 11 of 11 still red and 0 new, with both interval routes agreeing to 1.1e-16.

The number 0 new is precisely the clause the prediction claimed. An instrument in that state agrees with whatever prediction it is pointed at, which is worse than an instrument that fails loudly. A 4th refusal now fires when the record's own commit field equals the current HEAD, and the earlier recorded board must be named explicitly.

## Who made the board red, measured rather than asserted

The attributing claim -- that the new failures are the repairing sessions' own doing and not regressions in the product -- is flattering, and this project has caught itself making flattering claims about its own work 3 times. So it was measured, with the decision rule written before the measurement so that it could fail.

Every one of the 10 new failures was dated by the artefact it names, each row carrying its own evidence line. 10 of 10 were introduced on or after 2026-11-06: 1.000000, Wilson 95% [0.722467, 1.000000], Clopper-Pearson 95% [0.691503, 1.000000]. The decision rule asked for a Wilson lower bound above 0.5000 and got 0.722467, so the claim is UPHELD. Producer: `scripts/who_made_this_board_red_2026-11-07.py`.

That producer needed 4 attempts, and the first 3 were refused by its own decision rule rather than by a reader.

1. The first pooled all 128 files of the commit gate's board into the population. 0 of them were added on or after 2026-11-06, so 128 old paths swamped the 17 that name a cause and the measured share fell to 0.111111.
2. The second read a figure by shelling out to the gate-cost script with no arguments. That script does not stop at a pytest collection: it then runs the 128-file gate board for real, to time it. So a measurement script silently launched an approximately 11-minute board run on an 8-core, 8 GiB machine to obtain a number the failing test already prints. It sat blocked in a poll for 8 minutes at 0.0% processor use, with no output, before `ps` and `sample` were used to walk the descendants and the grandchild was found. The figures are now cited from the guard that computes them.
3. The third wrapped a JSON object in a set constructor, which yields the object's 6 metadata keys rather than its 111 pinned identifiers, so 112 of 112 live assertions looked unpinned and 1 guard contributed 78 paths to a population that should have received 1.

The standing rule after 3 defeated predicates on 1 surface is to stop and change the question rather than write a 4th predicate. The question was wrong: pooling artefact paths weights each guard by how many paths it happens to name, which bears no relation to how many failures there are. The unit of analysis is the FAILURE. The 4th version counts failures, and a failure that cannot be dated is dated by a named route rather than scored as older, because an unmeasured item entering a denominator as a negative is the mirror of failing open.

## 2 guards were accusing correct code

**The alias blindness.** The matcher that decides whether a script answers the help flag asked whether a call named exactly `answer_help` appears in the parsed module. 15 of the 205 scripts that call it bind it under an alias, the form this project's own later scripts adopted, so the matcher could see none of them. In 13 the blindness was latent; in 3 it was red on the board, and running those 3 with the help flag prints usage, exits 0 and writes nothing.

**The string literal.** A second guard asked whether a script both answers the flag and builds an argparse parser, by testing for 2 substrings in the source text. 2 scripts written the same day MENTION the parser class as a string literal inside their own detector logic -- they are tools that look for parsers -- and neither constructs a parser. The guard read the mention as evidence of the construction. It now asks the parsed module instead, and carries a discrimination test that fails if a string literal can accuse again.

## The help repair needed both halves, and that is measured too

The founder's 2026-10-02 standard requires a committed measurement showing a composed fix dominates either part alone on a named property, and this project had used the word in the weak sense 10 times out of 10. The named property is how many scripts the guard reports as offenders, which is 12 today and 0 when green. Measured over 4 conditions:

| condition | offenders |
|---|---|
| neither half | 12 |
| add the helper to the 9 that lack it | 12, unchanged |
| teach the matcher the alias | 9 |
| both | 0 |

Adding the helper alone changes nothing, because the idiom being added is the one the matcher cannot see. Neither half reaches 0, so the composition is NECESSARY rather than merely possible, which is the strong sense the standard asks for. Producer: `scripts/the_help_matcher_needed_both_halves_2026-11-07.py`.

## What was repaired and what is owed

9 of the 10 new failures were repaired in this session: both help-flag guards, `test_fresh_clone_is_actually_run_2026-09-11.py`, `test_note_standard_v17_enforced_2026-08-26.py`, `test_every_test_file_is_collected_2026-09-01.py`, the source-text census and both halves of the reachedness check. The gate's declared test figure was refreshed to 128 files and 2,585 tests. The source-text assertion was CONVERTED to a check that executes the precedence it had been matching as text, in both directions, and a mutation that flips that precedence turns it red; the original bytes were restored byte-for-byte rather than by a checkout.

1 of the 10 remains and it is the founder's, alongside the 1 surviving older failure which is also his. The blind panel round owes its joint half, which is queue state that entry B124 predicted in its own words before the run existed, and paying it costs money that requires authorisation. The branching-ratio check reports that the task list may no longer terminate, which is entry B123.

## Scripts cited here as this note's producers

`scripts/compare_this_board_against_the_record_2026-11-07.py`, `scripts/who_made_this_board_red_2026-11-07.py`, `scripts/the_help_matcher_needed_both_halves_2026-11-07.py`, `scripts/close_the_verified_tickets_2026-11-06.py`, `scripts/stamp_the_completed_entries_2026-11-06.py`, `scripts/the_census_guard_mutations_2026-11-06.py`, `scripts/the_derived_line_budget_mutations_2026-11-06.py`, `scripts/the_hash_guard_mutations_2026-11-06.py`, `scripts/the_line_cap_guard_mutations_2026-11-06.py`, `scripts/the_rule33_ratchet_mutations_2026-11-06.py`, `scripts/the_stamper_mutations_2026-11-06.py`, `scripts/the_store_key_guard_mutations_2026-11-07.py`, `scripts/the_operating_point_route_mutations_2026-11-07.py`, `scripts/the_anchor_in_the_identity_check_mutations_2026-11-07.py`, `scripts/the_gate_board_serialises_the_tree_2026-11-07.py`.

A script reached by nothing is the unwired-addition failure the additive standard forbids in its symmetric form, and a citation in a note is 1 of the 3 routes that check recognises. The alternative, raising a separate entry for each, would push the master list's branching ratio up, and that ratio is the subject of the 1 failure on this board that the founder still holds.

## What the record should carry forward

A pre-registration is worth having because it names its own falsifiers, and the half it got wrong is more informative than the half it got right. The blind spot was specific: the prediction verified the repairs and never asked what the predicting session had done to the board. Every one of the 10 new failures came from the sessions doing the repairing, and 0 came from the product.

Written under CDSFL note standard v1.9 (1 November 2026).
