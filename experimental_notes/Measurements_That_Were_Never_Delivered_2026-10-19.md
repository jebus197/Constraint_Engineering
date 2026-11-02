# Measurements that answer his questions and were never delivered to him

**The title carried the count "Six" until 2026-11-02T19:19:19+00:00 and the count is removed rather than incremented.** A 7th measurement was added on 2026-11-02 by the same ratchet that found the first 6, and a number in a title goes stale the next time the set grows — the lesson this project has recorded against stale counts in the pre-commit header, the task list and a seat roster. The 6 found on 2026-10-19 remain 6 and are described as such below.

**Written 2026-10-19T10:46:55+01:00.** Found by the project's own orphan ratchet rather than by looking: `bench/tests/test_scripts_are_reached_2026-09-11.py` reported 8 scripts reached by nothing — no caller, no note citing them as a figure's producer, no document naming them as a command. 6 of the 8 are MEASUREMENTS that answer questions he asked, and their answers sat unquoted. 2 are one-off migrations and are recorded as deliberately unreached.

**WHY THIS MATTERS MORE THAN A TIDY RATCHET.** The standing rule of 2026-09-04 is that a measured rate may be cited only if the script that produced it is committed alongside it. The inverse failure is the one here: the script is committed and the figure it produced was never quoted anywhere, so the measurement exists and the answer never reached him. An unread answer and an unmeasured question are the same thing from where he sits.

## 1. Do the 3 shakedown legs repeat? His question of 2026-10-16

**HIS WORDS:** *"there is a question of whether the fixes derived over the last 3 simulated runs show any tendency towards repeatability, which is a foundational pillar of scientific enquiry, and if the fixed derived from these simulated runs on that specific target should be carried forward into live runs?"*

**THE ANSWER, and it separates 2 things his question joins.** Producer: `scripts/do_the_three_legs_repeat_2026-10-16.py`, every figure cross-verified 3 ways in statsmodels, scipy and mpmath.

At the RUN level the harness is reproducible. At the FINDING level the overlap is modest and, importantly, **asymmetric**: leg 1 against leg 2 is **11 of 22, 50.0000%**; leg 1 against leg 3 **10 of 22, 45.4545%**; leg 2 against leg 1 **13 of 19, 68.4211%**; leg 2 against leg 3 **10 of 19, 52.6316%**; leg 3 against leg 1 **12 of 38, 31.5789%**; and leg 3 against leg 2 **11 of 38, 28.9474%**.

**The asymmetry is the finding.** The later leg's findings are the least likely to have a partner in an earlier one, which is what a system that is still being repaired between legs should look like. **The 3 legs were not run under identical conditions**, so this is consistency across changing conditions and not replication. On the second half of his question — whether fixes from these runs carry forward to live runs — the overlap above does not license it on repeatability grounds alone; it licenses carrying forward a fix whose own falsifier is re-run live.

## 2. What is safe to merge to main? His question of 2026-10-16

Producer: `scripts/what_is_safe_to_merge_to_main_2026-10-16.py`. Its conclusion is a decision of his that is still open: the immune memory now holds priors learned from both live and simulated runs, so carrying that file to main means the live runner begins its next real experiment with priors that no paid model produced. He ruled on 2026-10-16 that the memory be reset for the upcoming live experiments, which settles it — and the script was never cited where that ruling was recorded.

## 3. Had he already ruled on the 13 decisions? His question of 2026-10-16

Producer: `scripts/has_he_already_ruled_on_the_13_decisions_2026-10-16.py`. Its own caveat is the useful part and it is a general one: **a quoted ruling cannot be distinguished from a settled one by pattern alone**, because the ruling that CREATES an item and the ruling that SETTLES it read identically to a regular expression. It prints the sentences so the classification is made against his text rather than from recollection. That is the same defect class as the `ruled` field disagreeing with its own prose, recorded against 11 of 45 entries.

## 4. Does any directive carry unfenced code? Raised 2026-10-17

Producer: `scripts/does_any_directive_carry_unfenced_code_2026-10-17.py`, which reports **2 of 36 = 5.5556%**. Its conclusion names the cause as the length cap rather than the concise rendering — and **that conclusion is now stale**, because the cap it blames was split into a work bound and a specification bound on his ruling of 2026-10-14, and the specification is delivered whole to 5 of 5 models. The script's measurement stands; its attribution does not.

## 5. Is the author's own audit a rediscovery engine? Raised 2026-10-17

Producer: `scripts/is_my_own_audit_a_rediscovery_engine_2026-10-17.py`, which reports **17 of 20 = 85.0000%** of audit candidates sharing a term with the settled record. Its own caveat is that this is **triage and not a verdict**: a shared term means the subject is discussed in the settled record, not that the item is closed. Each candidate needs the note read before an entry is struck.

## 6. Which open items can the panel resolve? Raised 2026-10-18

Producer: `scripts/which_open_items_can_the_panel_resolve_2026-10-18.py`. It is the triage behind the 4 briefs queued on 2026-10-18, and it was cited in 3 notes only as a bare path in a list, which the ratchet deliberately does not count as a citation — a roll call is not a reference.

## The 2 that are genuinely unreached, with the reason

`scripts/correct_the_brief_tickets_source_2026-10-17.py` corrected 5 tickets that claimed to be his annotations when they were not. `scripts/migrate_ticket_identity_to_the_reference_2026-10-17.py` moved every task-list ticket onto its reference-keyed identity. **Both are one-off migrations.** A migration that runs twice is a defect, so neither should acquire a caller, and both are recorded in the ratchet's own `UNREACHED` list with that reason rather than left to read as orphans.

## 7. For how many declared figures is the historical fallback actually available? Found 2026-11-02

**HOW IT SURFACED, which is the same way as the first 6.** `bench/tests/test_scripts_are_reached_2026-09-11.py`, which refuses to let the count of scripts reached by nothing grow, turned red on 2026-11-02 after a day of work added 45 scripts, and exactly 1 of the 45 was reached by nothing: `scripts/how_many_declared_figures_can_be_checked_2026-11-02.py`. Its figures had never been quoted anywhere. The ratchet's own `UNREACHED` exemption list stood at 0 entries and is left at 0, because the convention recorded above is that an exemption duplicating a citation loosens the bound by its own width, and the reasons belong in a note where a reader will find them.

**WHAT IT ASKED, AND IT CORRECTED ITSELF FIRST.** Its own first version counted producers lacking an `--as-of` flag and called their declared figures *"uncheckable"*. That was false, and the script records the correction in its own docstring rather than quietly rewriting the question: it is the same overstatement that had been criticised in another entry within the hour.

**WHAT THE VALIDATOR ACTUALLY DOES, read from its control flow rather than from its comments.** `scripts/panel_brief_validate.py` runs a declared figure's producer PLAIN first, and if the declared value appears in the output the figure is ACCEPTED with the flag never consulted. Only on a plain miss does it retry with `--as-of` set to the brief's latest date, accepting a match LOUDLY as a historical figure. Only if that also fails does it consult the amendments register for a recorded rule change, which must name both the figure and the brief and whose replacement value the producer must actually print. Otherwise it refuses.

**SO THE MISSING FLAG DOES NOT MEASURE A SHARE OF WRONG FIGURES, and saying it did would have been the flattering reading in the wrong direction — it would have invented a defect.** What the missing flag costs is the SECOND step only: a figure that was true at the brief's date and has since drifted is refused where it could have been accepted as historical, loudly and with its date attached.

**WHAT IS STILL NOT MEASURED, stated rather than left implied.** The number that would matter is how many declared figures fail the PLAIN re-execution today, because only those ever reach step 2. That was not measured, and the reason is a resource bound rather than a judgement: 49 producers would have to run on a machine with 8 GiB and a derived budget of 2 heavy processes. The 1 instance found by hand is 4 figures in 1 brief.

**WHY NOTHING IS FIXED, which is the script's own conclusion and not a deferral.** The remedy follows the scope: a shared helper if many producers lack the flag, a single patch if few do, and the scope is exactly the unmeasured number above. Fixing before measuring would pick one of those two at random.

Producer: `scripts/how_many_declared_figures_can_be_checked_2026-11-02.py`, which reads the validator and the briefs and writes nothing.

Section 7 written under CDSFL note standard v1.9.

Written under CDSFL note standard v1.8.
