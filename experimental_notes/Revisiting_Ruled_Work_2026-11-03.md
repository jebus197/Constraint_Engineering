# Revisiting Work Already Ruled Or Already Closed: The Measured Cause

3 November 2026, 11:00 GMT

## Summary

The founder asked whether this session had revisited fixes he had already ruled on, or that were already marked complete in the project's issue register. **It had, twice, and a third was a near-miss on a ruling of his.** The cause is not only a lapse of discipline: the register's de-duplication screen is tight enough that re-describing a known mechanism in different words mints a new identity. Both halves are measured below, and the discipline half is the larger one.

## What was revisited

**Ticket `148ebf10bbaa`, status CLOSED, verified by commit `529dada432099793f815f42d87c534a4eacbfc37`.** Its text already states the mechanism that was presented to the founder that night as a discovery: that `scripts/blocker_triage.py` returns a PARK verdict with no permission flag for items that are the founder's decision, and that `~/.claude/hooks/work_not_narrate.py` then reads PARK as permission to carry on, so the Stop gate pushes work he reserved to himself. The ticket closes with the words *"Recorded, not fixed"*, so the behaviour persists by design pending him.

**Ticket `c15b3dbe595a`, status OPEN.** It states that the Stop gate reads "nothing is blocking" from a fact about the turn rather than from the open items' own text. That was re-derived by running the whose-move instrument and reporting that 20 of 22 live entries await the founder.

**Ticket `e41e1fdbc223`, ruled 2026-10-30 — a near-miss, not a repeat.** It records his ruling that a free panel or simulated experiment needs no additional permission beyond the instruction to run it. A rule contradicting that was nearly added. What prevented it was prose in the code recording that the question was his to settle, and that prose was itself 4 days stale, because he had already settled it.

## The discipline half, which is the larger half

The search that was run was `register.py --subject blocker_triage`, which returned 0 matches, and that 0 was read as *nothing is registered*. **3,045 of 3,383 tickets carry no subject at all** — 0.900089, Wilson 95% [0.889525, 0.909745], Clopper-Pearson [0.889487, 0.909993]. The subject index therefore covers roughly a tenth of the register, and a 0 from it is uninformative rather than negative. The closed ticket carries an empty subject list while its own text names the module, so no subject query could have reached it. **505 tickets are in that same position**, naming a module in their text yet carrying no subject, 0.149276, Wilson 95% [0.137665, 0.161682]. **The population is 3,383 as measured, and this same commit's own ticket raise then made it 3,384**, so re-running the producer at HEAD returns the larger denominator. The shift is in the 4th decimal (0.900089 to 0.899823; 0.149276 to 0.149232) and changes no conclusion, but the figure as written does not reproduce from the committed state, which is the defect `measured-rate-travels-with-its-script` exists to prevent: a commit that measures the register and adds to it cannot have both be true at once.

**But a usable query existed.** Searching the filename as a word, `--word "blocker_triage.py"`, returns 8 matches and the closed ticket is among them. Every word query finds it; only the filename query returns a set small enough to read. The queries a reader would reach for instead return 491, 211 and 616 matches and cannot answer a novelty question at all.

## The mechanical half

`TicketStore.propose` advertises itself as the step that stops a rediscovery: a caller receiving any outcome other than `created` must not treat the item as new work. **Tested against a copy of the register, it returned `created`** for a re-wording of the closed ticket's own mechanism, so it would not have stopped this one.

The reason is vocabulary sensitivity. The re-wording shares 15 of its 16 distinctive tokens with the closed ticket, **0.937500 of its own vocabulary, against a screening threshold of 0.95** — a miss by one token. Lowering the screen to 0.80 returns **exactly 1 match, and it is the correct ticket**. At 0.60 it returns 2, at 0.50 it returns 7, and at 0.30 it returns 154 and is useless.

**That is a single instance and must not be read as a calibration.** Whether 0.80 is the right threshold in general requires an operating characteristic: how often a given screen catches a genuine re-wording against how often it wrongly absorbs a distinct item.

## The recommendation, under the project's formal standards

Run `scripts/does_the_register_beat_word_search_2026-10-17.py`. It was built on the founder's own 2026-10-17 requirement that the register demonstrate rather than assert, in his words so that it does not *"risk simply becoming decoration that does nothing useful"*, and the decision it tests is the exact one that failed here: before proposing work, is this already known. Its ground truth comes from the task list's version history rather than from a model.

This is the **simplest sufficient** step, because it is a measurement over an instrument that already exists and changes no behaviour. It is **additive** in the symmetric sense, because the instrument is already wired and executed by a test, so running it adds evidence rather than surface. **No composability claim is made** between it and a threshold change: nothing here measures the pair as better than the measurement alone, and the threshold governs how every ticket in the register is deduplicated, which makes it the founder's ruling rather than a repair.

## What this does not claim

It does not claim the subject index is wrong to be sparse, nor propose populating it, because that would change how every ticket is indexed. It does not claim 0.80 is correct. And it does not claim the register is decoration: the register held both prior findings correctly, with the right statuses and a verification commit on the closed one. What failed was the route taken into it.

Producers: `scripts/the_subject_index_cannot_answer_a_novelty_question_2026-11-03.py`, and for the truncation finding referenced above, `scripts/a_truncated_ruling_reads_as_complete_2026-11-03.py`.

Written under CDSFL note standard v1.9 (1 November 2026).
