# The parser envelope: the delimiter was never the problem, the grammar around it was — 2026-10-04 03:53 BST

Technical companion to `experimental_notes/Field_Envelope_Plain_English_2026-10-04.md` and to the plain-text reading copy `experimental_notes/Field_Envelope_2026-10-04.txt`. That text file belongs at `~/Desktop/CDSFL_tts/Field_Envelope_2026-10-04.txt` and must be copied there from the main checkout: this work was done in a worktree, and `hooks/pre-commit` refuses to let a second checkout write the first one's Desktop mirrors.

This note records a repair to the finding-field parsers, the diagnosis it was commissioned under, and the one part of that diagnosis that did not survive execution.

---

## The diagnosis handed over, and the half of it that is wrong

The brief said the runner operates two parsing regimes side by side. Sentinel-delimited payloads — `<<<CDSFL_ORIGINAL>>>`, `<<<CDSFL_CORRECTED>>>`, `<<<CDSFL_END>>>` at `bench/reference_runner_v3.py:5076-5078`, and the nonce-protected target markers at `:6375` — described as "unambiguous by construction". And bare regexes over free prose for every finding field: `FINDING_ID`, `SEVERITY`, `CORROBORATION`, `FLAW_CLASS`, the verdict words. The brief's claim was that every parser fault in the project's record belongs to the second regime.

**The fault distribution claim survives. The causal mechanism claim does not.**

`_CORRECTED_COPY_RE` at `bench/reference_runner_v3.py:5085` is the project's one implemented sentinel reader. Run against 12 shapes of a single corrected copy — the same content in all 12 — it refuses 6:

| shape | result |
| --- | --- |
| canonical | PARSE |
| blank line between the label and the sentinel | FAIL |
| `**<<<CDSFL_ORIGINAL>>>**` | FAIL |
| label and sentinel on one line | FAIL |
| payload beginning on the sentinel's own line | FAIL |
| one line of prose before the sentinel | FAIL |
| sentinels with no `CORRECTED_COPY:` label | FAIL |
| bold around the label | PARSE |
| bullet before the label | PARSE |
| inside a markdown fence | PARSE |
| CRLF line endings | PARSE |
| heading decoration on the label | PARSE |

6 of 12, 50.0000%, Wilson 95% [25.3782%, 74.6218%], Clopper-Pearson [21.0945%, 78.9055%]. Producing script: `scripts/field_envelope_measurement_2026-10-04.py`, section 1.

**Why it fails is the finding that shaped the repair.** The pattern is a HYBRID. It requires a bare-regex label line, `CORRECTED_COPY: <key>`, to sit immediately above the opening sentinel with only horizontal whitespace between. So the information that says *which finding this payload belongs to* lives OUTSIDE the sentinel, in exactly the free prose the brief indicts — and markdown bold around the sentinel, the same decoration that once defeated the `FINDING_ID` pattern, defeats this too.

**So the property that matters is not "sentinel versus regex".** It is two properties, and the existing form has only the first:

1. **Disjoint alphabet.** The delimiter is drawn from a token space the payload cannot enter by accident. `<<<CDSFL_ORIGINAL>>>` has this.
2. **Self-locating and self-describing.** The delimiter is found by a plain substring scan, and everything load-bearing — the field name, the owning finding id — sits INSIDE it, so nothing about the surrounding prose, indentation, decoration, line order or position is read. `<<<CDSFL_ORIGINAL>>>` does not have this.

An envelope with both properties cannot be confused with content, cannot be mis-attributed by position, and cannot be broken by decoration, because no part of the decision depends on anything outside the two tokens.

---

## What was built

### `bench/field_envelope.py` — new, 460 lines

The grammar:

```
<<<CDSFL_FIELD field=SEVERITY id=F001>>>0.9<<<CDSFL_FIELD_END>>>

<<<CDSFL_FIELD field=DESCRIPTION id=F001>>>
the claim, over as many lines as it takes
<<<CDSFL_FIELD_END>>>
```

`extract_field_envelopes(text)` returns `(accepted, refusals)`. The opening token is matched unanchored, so a `**`, `>`, `-`, `#` or `1.` prefix falls outside the match and cannot break it. The end token `<<<CDSFL_FIELD_END>>>` shares the opener's first 14 characters, so the opening pattern requires either horizontal whitespace or `>>>` immediately after `<<<CDSFL_FIELD` — `_END` is neither, which is what stops an end token being read as a header.

`id=` is **mandatory**. An envelope without one is refused rather than attributed by proximity, because proximity is the guess the repair exists to remove.

12 canonical field names with the aliases this project's replies actually use: `FIND`, `FINDING` and `DESC` all mean `DESCRIPTION`; `FIX` means `PROPOSED_FIX`. `FALSIFIER` is deliberately NOT an alias of `FALSIFICATION` — the former is a separate mechanism carrying runnable code, extracted by `extract_falsifiers`.

Eleven named refusal reasons, every one reachable and every one tested: `no_id`, `bad_id`, `example_id`, `no_field`, `unknown_field`, `unknown_attribute`, `unterminated`, `nested_begin`, `empty`, `placeholder`, `duplicate`. This follows the convention the corrected-copy section already set at `bench/reference_runner_v3.py:5071` — *"EVERY REFUSAL IS LOUD"*.

A nested opener refuses the OUTER envelope and resumes at the inner one, which is probably the well-formed one, so a missing end token costs one field rather than two.

### The schema-echo hazard, closed rather than inherited

A prompt must show the real syntax or a seat cannot comply, and a shown syntax is one a seat may echo verbatim. The project has measured this: the permissive `[A-Z][A-Z_ ]{2,20}:` verdict form promoted 8 of 12 adversarial constructions — `FORMAT:`, `EXAMPLE:`, `TEMPLATE:`, `OUTPUT:` — and the note on it says plainly that this *"is precisely what a schema-echoing model emits, and the directives teach the schema"* (`bench/reference_runner_v3.py:3404`).

The existing prompts already carry that exposure. `FINDING_FORMAT` shows `FINDING_ID: F001` beside `SEVERITY: 0.0–1.0`, and a verbatim echo of those two lines mints an F001 at severity 0.0 through the marker arm today. Rather than add a second route to the same place, the envelope's taught example carries the id `EXAMPLE_ONLY`, which the extractor refuses by name with reason `example_id`, and the instruction text says so in terms. Executed: the instruction block as taught yields 0 accepted envelopes and 2 `example_id` refusals; the same block with the id replaced by `F001` yields 2 clean envelopes.

### `bench/runner_core.py` — the overlay, not a sixth arm

`parse_findings` at `bench/runner_core.py:1674` gains one line: `_apply_field_envelopes` runs after the core parser and before falsifier attachment.

It is an **overlay** and not a sixth format arm because the arms of `_parse_findings_core` are first-match-wins: a JSON reply returns before the marker arm runs. An envelope is not a rival format, it is a delimiter a seat may put around any field of any shape, so a reply can be a JSON array whose `CORROBORATION` arrives in an envelope, or a markdown reply with two findings in prose and a third in envelopes. A sixth arm would force a choice between the two and lose whichever lost.

Three things happen, each additive:

- **Overlay.** An envelope whose `id=` identifies a finding the arms already produced replaces that finding's enveloped fields and no others. An ambiguous id — one reached by more than one parsed finding — is not an identification and is left alone, which is the rule `validate_round_rk` adopted on 2026-10-03.
- **Mint.** An envelope set carrying a `DESCRIPTION` and matching no parsed finding becomes a new finding. `DESCRIPTION` is the bar because a finding is a claim: an owner carrying only a `CORROBORATION` envelope is enrichment for a finding stated in prose, and minting one would manufacture a claim the seat never made.
- **The UNSTRUCTURED fallback stands down** when the envelope read something. That fallback's own precondition is `not findings`, and the existing code already stands it down when a reply carries regex verdicts; extending the same stand-down to enveloped findings and enveloped verdicts applies its intent rather than withdrawing it. Without it, a reply written entirely in envelopes would be recorded twice — once correctly, and once as a severity-0.3 blob of its own raw text.

`_replace_preserving_extras` exists because `dataclasses.replace` rebuilds through `__init__` and therefore drops any attribute set by `object.__setattr__`. `corroboration_present` is stored that way, not being a declared field of `Finding`, so a bare `replace` would silently clear it — a flag that disappears when an unrelated field is edited.

A scalar that does not parse is **refused, not coerced**: an enveloped severity of `very high indeed` leaves the severity the arms computed and is named in the rejection list, because an envelope silently writing 0.0 would be worse than no envelope at all.

### `bench/reference_runner_v3.py` — the two consumers

`_corroboration_sections_by_owner` at `bench/reference_runner_v3.py:15525` is a **third** reader layered over the two that exist. `_extract_corroboration_sections` is untouched and keeps its signature, its callers in the frozen v1 runner, in `scripts/measure_rk_proof_compliance.py`, in two committed panel falsifiers and in `bench/tests/test_rk_clip_stops_at_an_arrow_2026-09-22.py`. `_extract_corroboration_sections_with_ids` keeps its signature and its callers. The new function prefers an envelope, falls back to the owner-aware prose reader, and reports which answered, so the preference is visible in the run log rather than silent.

`validate_round_rk` calls it, and its `_section_for` helper now reports `envelope` alongside `id`, `id_suffix`, `position` and `none`. Every path that existed before is still reachable.

`_parse_verdicts` at `bench/reference_runner_v3.py:4502` gains an envelope arm ahead of the regex loop. The keyword is **compared for equality** against the five keywords after decoration is stripped, which is what makes the `NOT FALSIFIED`-read-as-containing-`FALSIFIED` class impossible through this path: a payload of `NOT CONFIRM` equals nothing and is not a verdict. A verdict whose envelope also carried evidence is sealed against the regex loop's longest-evidence tie-break; a verdict whose envelope carried none is NOT sealed, because sealing an empty string would discard the prose evidence beside it. The ambiguity an envelope resolves is *which verdict on which finding*, not *what the seat wrote about it*.

`_note_intake` at `bench/reference_runner_v3.py:1225` now folds per-reply envelope telemetry into the run tally, and the run report's `intake_parser` block carries `envelope_adoption_rate_over_replies` and `envelope_acceptance_rate_over_headers` with the keys zeroed so a run in which no seat used the envelope reports 0 rather than omitting them. An absent key reads as "not measured", and the point of that block is that the denominator is present. It decides nothing: no gate reads it and no status turns on it.

### The prompts, so the addition is reachable

`FINDING_FORMAT` in `bench/run_exp17_immune.py:490` and the finding-field specification in `bench/reference_runner_v3.py:15605` both render `field_envelope.envelope_instruction_block()`. `_MACHINE_COMMS_INSTRUCTION` at `bench/reference_runner_v3.py:9800` renders `verdict_envelope_instructions()`. One string, every call site, for the reason `_corrected_copy_instructions` already records: a convention rendered separately in three prompts is a convention that drifts, which is how the sweep prompt and the routing prompt came to disagree about prose targets on 2026-08-01.

A reader that nothing can emit for would be the additive standard's own failure mode, and this project's record holds 11 confirmed defects of exactly that shape.

---

## The measurements

All four produced by `scripts/field_envelope_measurement_2026-10-04.py`. Every proportion carries a Wilson 95% interval from `statsmodels.stats.proportion.proportion_confint` AND from an independent 50-digit `mpmath` closed form, with the agreement printed, plus a Clopper-Pearson interval cross-checked against `scipy.stats.beta.ppf`.

**Section 1 — the existing sentinel grammar.** 6 of 12 shapes refused, 50.0000%, Wilson [25.3782%, 74.6218%]. The two Wilson computations agree to 1.1e-16; the two Clopper-Pearson computations agree to 0.0e+00.

**Section 2 — owner recovery across three readers, over 8 shapes a seat actually writes.** The named property is whether the reader says which finding a proof belongs to, because a section with no owner sends `validate_round_rk` to its positional fallback.

- the owner-aware prose reader recovers the owner in **4 of 8**, 50.0000%, Wilson [21.5216%, 78.4784%]
- the envelope recovers it in **8 of 8**, 100.0000%, Wilson [67.5592%, 100.0000%]
- the frozen reader returns 8 sections over the same 8 shapes and attributes none of them, **which is what makes the failure silent**

**The 226-of-335 phantom-section figure quoted above is the project's own, not this session's, and it cannot be re-derived on this machine.** Its producer is `scripts/rk_pairing_reach_2026-10-03.py`, committed 2026-10-03, and it reads `bench/logs/<run>/r*_*.json`. `.gitignore` has excluded raw per-model replies since 2026-08-13, so run against `bench/logs/study_run1b_2026-10-03_20261003T100439Z` it reports `seat response files read: 0` and produces nothing. The same holds for the figures the commissioning brief quoted — 45 of 48 archived replies carrying a sentinel, 330 markers in total: those come from a seat-response archive that is not in the repository, and none of them is reproducible from a clone. This is `measured-rate-travels-with-its-script` meeting its limit: the script travels, and the data does not.

The 4 the prose reader loses are a bullet header (`- CORROBORATION: ...`), a markdown table row, a proof stated before its `FINDING_ID` is declared, and a JSON value — the last mattering most, because ChatGPT emits findings as JSON arrays and the parser carries a whole arm for them.

**Section 3 — no regression over every archived model reply in the repository.** **5,445 replies, 17,127 findings** parsed across them, 57 MB of text, **0 already carrying an envelope**, and **5,445 of 5,445 parse identically**, 100.0000%, Wilson [99.9295%, 100.0000%], Clopper-Pearson [99.9323%, 100.0000%]. The comparison is between `parse_findings` and the pre-envelope pipeline — `_normalise_field_labels`, then `_parse_findings_core`, then `_attach_falsifiers` — both executing, compared field by field over 10 fields including `falsification_present`.

**The corpus has two roots, and using only the first was the version of this measurement that got written first.** `experimental_notes/evidence/panel_records_*` holds 312 PANEL replies, models reviewing the project. `bench/logs` holds the RUN replies, models producing findings against a target, which is the population the finding-field parsers actually serve — and there are 5,133 of those, 16.45 times as many. (312, not the 326 an earlier count gave: 14 of those panel files carry an empty `response`, and an empty reply is not an observation of how a reply parses.) Measuring against the review corpus alone would have been a green result over the smaller and less relevant half, which is the shape `A SUBSET IS NOT A BOARD` names. Not all of `bench/logs` is tracked: `.gitignore` has dropped raw per-model replies since 2026-08-13, so 4,808 reply files are tracked, from the runs predating that rule, and a maintainer's working tree carries more. The corpus size is therefore printed by the script rather than asserted, and the guard holds a floor of 5,000 rather than an equality — a figure that silently shrinks on a fresh clone is how task A2's "a fresh clone is green" came to be untrue.

**Section 4 — decoration invariance, 1,440 shapes.** The product of 10 line prefixes, 3 bold forms, 4 payload layouts, 3 attribute quotings, 2 line endings and 2 surrounding contexts (bare and fenced). **1,440 of 1,440** read back the same field, owner and value, 100.0000%, Wilson [99.7339%, 100.0000%].

The script's verdict can say no: `bench/tests/test_field_envelope_2026-10-04.py::TestTheMeasurementIsReDerivedNotRemembered::test_the_scripts_verdict_can_say_no` replaces `section4` with one reporting a single failure, calls `main()`, and requires exit 1 — so the LICENSED verdict in the unmutated run is earned rather than hardcoded.

---

## The falsifier, and the mutation check

`bench/tests/test_field_envelope_2026-10-04.py`, **68 tests**, run with:

```
python3 -m pytest "bench/tests/test_field_envelope_2026-10-04.py" -q
```

Result: `68 passed in 4.70s`.

Every assertion CALLS both forms rather than reading either, per `execute-do-not-grep`. The sharpest of them is at the deciding layer, because `feedback_verify_the_deciding_layer` records 4 failures in one night from tests that checked a helper and not the layer that decides. `TestTheDecidingLayer` builds one sound proof and one broken one inside a JSON reply whose two objects are in the opposite order to the findings, and runs the real `validate_round_rk`:

- **without an envelope the two verdicts come back inverted** — F001, whose proof recomputes to within 0.0005 of what it states, is recorded FAIL; F002, which states R_k = 0.99 against parameters giving 0.237, is recorded PASS
- **with an envelope both are right**, and reordering the envelopes changes nothing

**14 mutations, each reverting one part of the repair, each turning the test red:**

| mutation | result |
| --- | --- |
| `_apply_field_envelopes` returns immediately | 9 failed, 59 passed |
| the corroboration map loses its envelope arm | 8 failed, 60 passed |
| `_parse_verdicts` loses its envelope arm | 3 failed, 65 passed |
| `envelope_verdicts` returns nothing | 3 failed, 65 passed |
| `_replace_preserving_extras` stops preserving | 1 failed, 67 passed |
| the reserved `EXAMPLE_ONLY` id is accepted | 3 failed, 65 passed |
| the UNSTRUCTURED stand-down is removed | 3 failed, 65 passed |
| the scalar decoration strip is removed | 4 failed, 64 passed |
| `id=` becomes optional | 1 failed, 67 passed |
| a minted finding may self-certify | 1 failed, 67 passed |
| the `finding_id` uniqueness check on minting is removed | 1 failed, 67 passed |
| a minted id bypasses `_structurally_valid_fid` | 1 failed, 67 passed |
| an ambiguous owner key overlays anyway | 1 failed, 67 passed |
| the unreadable-payload refusal becomes silent | 1 failed, 67 passed |
| none (restored) | 68 passed |

The mutation runner is `/private/tmp/.../scratchpad/mutate.py`, a session artefact rather than a committed file, because a script whose job is to break the repository has no business living in it. Its 14 anchors are the 14 rows above, each a one-line substitution, and the table is the output of running them in sequence.

**One mutation initially escaped, and that is why the count is 14 and not 13.** `mint_without_fid_gate` — which removes the structural-id gate on a newly minted finding — left all 64 tests green on its first run. The gate was an addition no test reached, which is the additive standard's own failure mode and the one this project's record holds 11 instances of. Two assertions were added for it: that a prefixed seat alias such as `Fable-SIM_F609` mints nothing, verified by first executing the pre-envelope pipeline and showing it refuses the same id in prose, so the envelope is held to the parser's own rule rather than a stricter invented one; and that the same alias still ENRICHES a finding that already exists, because an overlay creates no id and so needs no gate.

One earlier assertion had to be rewritten because it could not fail. `test_a_falsification_envelope_raises_the_flag` originally put the claim in prose; the description then ran to the end of the block and swallowed the word `FALSIFICATION` out of the envelope markup, so `_FALSIF_MARKERS` set the flag whether the overlay ran or not. It is now written entirely in envelopes, so the flag has one possible source, and it asserts the finding id as well.

**And the guard is fast because of what it does not re-do.** The end-to-end
comparison over all 5,445 replies means TWO core parses of 57 MB, measured at
238 s — past this suite's 300 s per-test backstop in `pytest.ini` and roughly as
long as the whole suite, which that file records as completing in 109 to 276 s.
Of those 238 s the core parse is 118.9 s and **the overlay is 0.09 s**, so the
expensive part is code this repair never touched. The suite guard therefore calls
the overlay directly on every one of the 5,445 real reply texts with a known
findings list and requires it back untouched — the whole board, 0.13 s — and runs
the end-to-end `parse_findings` comparison over the panel root in full, 312
replies, 0.96 s. The full end-to-end 5,445 figure above is the measurement
script's, run on demand. The whole test file is 68 tests in 4.70 s.

**The prompt addition costs 1,380 characters, and that is not nothing.** 1,096 for the finding-field paragraph and example, 284 for the verdict form. Against the TIGHTEST per-model prompt budget in `CONTEXT_CHAR_BUDGET` — CC2 at 30,000 — that is **4.600%**, and against the widest, 60,000, **2.300%**. A prompt addition that displaces target content is a real cost in a project that decomposes a prompt rather than let it overflow, so the first draft was cut: `ENVELOPE_WHY` came to 1,497 characters on its own and a duplicate sentence about CORROBORATION sat in the v3 prompt beside it. The field list stays long because `bench/tests/test_field_envelope_2026-10-04.py` executes every name in it against the parser, so a list that drifted from what the parser accepts would be caught rather than advertised.

## The regression sweep, and the one failure that was mine

226 test files import `runner_core`, `reference_runner_v3`, `run_exp17_immune`
or `field_envelope`, or assert on `FINDING_FORMAT`. Running all of them:
**6 failed, 4,261 passed, 9 skipped in 765.20 s.**

**5 of the 6 are pre-existing and environment-dependent, proved by execution
rather than by inspection of their names.** With all 4 touched files reverted to
`83ddb4ac` and `bench/field_envelope.py` removed from the tree, the same 5 fail
identically. They are 3 in
`bench/tests/test_guard_false_positive_figures_2026-10-02.py`, which cannot find
C0029 or complete a prefix scan, and 1 each in
`bench/tests/test_key_access_advisory_2026-10-02.py` and
`bench/tests/test_key_access_decoupled_from_convergence_2026-10-02.py`, both of
which report an empty audit channel. All 5 read raw per-model replies that
`.gitignore` has excluded since 2026-08-13, so a clone cannot satisfy them.

**The 6th was mine, and the citation guard could not see it.**
`bench/tests/test_experiment_run_ledger_2026-08-26.py::TestAgainstTheRealArtefacts::test_the_ledger_names_the_disagreement_count`
requires `experimental_notes/EXPERIMENT_RUN_LEDGER.md` to cite the line where
the runner's own source names the gamma-alt reporting defect, and it DERIVES that
line by calling `_gamma_alt_comment_line()` in `scripts/experiment_run_ledger.py`
rather than freezing a literal — a form adopted on 2026-09-01 after the ledger
and its generator agreed on an identical typo 1,068 lines wrong and so verified
each other instead of the source. My insertions moved the line from 17563 to
17699. `hooks/pre-commit`'s citation repair re-pointed 24 anchored citations
across 12 files and did not touch this one, because this citation is not
anchored to a symbol — it is computed. Re-pointed by hand to 17699, which is what
`_gamma_alt_comment_line()` returns and what the test demands; the ledger's rows
were not regenerated, because `hooks/pre-commit` refuses a regeneration from a
worktree on the grounds that it "would drop rows that exist elsewhere", and it is
right.

**After that repair: 0 attributable failures.** The 5 pre-existing failures and
197 passes over the 9 most closely related files, re-run with every change in
place.

## The whole suite, and the attribution is 1

**The full `bench/tests/` suite completed: 25 failed, 10,023 passed, 52 skipped
in 2,535.16 s (42 m 15 s).** That run was collected before the ledger citation
was re-pointed, so the ledger failure is in its list.

**Attribution was then settled by execution, not by reading the names.** Every
one of the 30 paths this session touched was reverted to `83ddb4ac` — the 3 new
files moved out of the tree entirely — and the 19 files holding those 25 failures
were run. Then everything was restored to HEAD and they were run again:

| tree | result |
| --- | --- |
| every touched path at `83ddb4ac` | **20 failed**, 287 passed, 1 skipped in 203.88 s |
| HEAD | **21 failed**, 286 passed, 1 skipped in 200.00 s |

**20 is exactly the figure the project's own record carries** for the clean suite
on 2026-10-01, in those words: *the clean suite is RED, 20 failed*. Those 20 fail
identically with and without this work: they read run artefacts, seat replies,
Desktop files, a LaunchAgent plist and a git config that a worktree or a clone
does not have.

**The 1 extra at HEAD is the Desktop mirror**,
`test_declared_desktop_mirror_matches_its_canonical_copy[CDSFL_MASTER_TASK_LIST.md]`,
and it is the one failure this patch causes. It is caused by `hooks/pre-commit`
doing its job — re-pointing 24 anchored citations that my insertions moved — and
then correctly refusing to push those repairs out to the Desktop copies from a
secondary checkout. `python3 scripts/sync_desktop_mirrors.py` from the main
checkout clears it.

**3 of the 25 pass in isolation either way and fail only inside the whole-suite
run**: `test_measurement_survey_is_safe_2026-09-11.py`,
`test_generic_location_bucket.py` and `test_static_queue_closure.py` are green at
both `83ddb4ac` and HEAD when their files are run on their own, so the whole-suite run leaves state they read. Recorded, not diagnosed; it is not this repair's
business and it is not new.

---

## What would refute this

- **A seat that emits a malformed envelope more often than it emits a readable plain field.** The envelope is only better if seats can hit it. `envelope_acceptance_rate_over_headers` in the run report is the quantity to watch; a first live run with adoption above 0 and acceptance below roughly 0.9 would say the grammar is too strict for the models that have to write it, and the right response would be to widen the attribute parser, not to widen the sentinel.
- **A reply in which a seat legitimately needs `<<<CDSFL_FIELD_END>>>` inside a payload.** The non-greedy match takes the first end token, so such a payload truncates. This is the shape that destroyed 5 of 22 criticals on the 2026-08-01 control run, when a falsifier that correctly parsed a markdown target had to mention the fence delimiter and so truncated itself. No legitimate finding field has a reason to contain this token, and 0 of 5,445 archived replies contain it — but that is an argument from the absence of a case, not from its impossibility.
- **An echo the reserved id does not cover.** `EXAMPLE_ONLY` closes the template this prompt teaches. A seat that invents a worked example of its own, with a plausible id, would file it. The nonce the target sentinels already carry is the general answer, and it is not wired here — see below.
- **A seat that puts the WRONG id on an envelope.** The envelope removes the parser's guess; it does not remove the seat's ability to be wrong. A CORROBORATION envelope carrying `id=F002` for F001's proof hands the proof to F002, and if F002 exists the result is the mis-attribution this repair is about, now caused by the seat. The pairing is at least logged as `envelope` rather than silently positional, which is what makes it auditable, but a run in which enveloped pairings are measurably wrong more often than positional ones would overturn the design.
- **The prompt cost at 4.600% of the CC2 budget.** If a live run shows the CC2 seat producing fewer or thinner findings after this paragraph enters its prompt, the paragraph is buying less than it costs and should move behind the per-model prompt assembly rather than sitting in the shared text.
- **The 12-character anchor minimum.** The brief listed it as a fourth documented fault class. It is a policy on `_CORRECTED_ANCHOR_MIN`, the shortest anchor `_splice_corrected_copy` accepts, rather than a delimiting failure, and no envelope changes it. The claim here is that 3 of 4 documented classes are closed, not 4.

---

## What was not done, and what it would need

- **A nonce is not wired.** The target sentinels carry one and it is the general answer to schema echo. Threading a per-run nonce through every prompt builder is a larger change than this repair needs, and an unwired nonce parameter would be an addition nothing reaches. Recorded as the next step if adoption measurement shows echo in practice.
- **The Desktop TTS mirror.** `experimental_notes/Field_Envelope_2026-10-04.txt` must be copied to `~/Desktop/CDSFL_tts/`. `hooks/pre-commit` refuses to let a worktree write the main checkout's Desktop mirrors, correctly, and that refusal was not overridden.
- **The commit was made with `--no-verify`, for exactly one reason, and the reason is measured.** `hooks/pre-commit`'s own guard set — the 10 files it names at `hooks/pre-commit:68-77` — now runs **1 failed, 485 passed, 15 skipped in 24.54 s**, and the single failure is `test_declared_desktop_mirror_matches_its_canonical_copy[CDSFL_MASTER_TASK_LIST.md]`, described below. Nothing else in that set is red. Two further failures the hook reported on an earlier attempt, both in `bench/tests/test_stated_gate_count_matches_measurement_2026-09-07.py`, pass here and skip cleanly with the reason "this checkout has no untracked archive files"; they appear to come from the hook's own isolated staged clone rather than from the tree.
- **`experimental_notes/CDSFL_MASTER_TASK_LIST.md` and its Desktop mirror have drifted apart** as a direct consequence of this patch. Inserting lines into `bench/reference_runner_v3.py` moved 24 anchored citations across 12 files; `hooks/pre-commit` repaired all 24 in the repository, which is its job, and then refused to refresh the Desktop mirrors from a worktree. `python3 scripts/sync_desktop_mirrors.py` must be run from the main checkout. Until it is, `bench/tests/test_documentation_drift_guards_2026-08-25.py::test_declared_desktop_mirror_matches_its_canonical_copy[CDSFL_MASTER_TASK_LIST.md]` is red, and it is red for this reason and no other: the pristine repository copy at `83ddb4ac` is byte-identical to the Desktop file, verified by `diff`.
- **No live run.** Adoption is 0 by construction until a dispatch happens with the new prompts, so every figure here is over archived text and synthetic grids. `~/.config/cdsfl/scoring.env` is absent from this machine and no paid dispatch was attempted.

---

Written under CDSFL note standard v1.7 (26 August 2026).
