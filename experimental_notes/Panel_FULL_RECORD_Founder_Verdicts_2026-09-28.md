# The founder verdicts round that never ran — the CLI login had expired

Record written 2026-09-28T23:57:01+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

This round was dispatched at 02:23 on 2026-09-28 against an 11-item brief covering the founder's verdicts of that morning. It produced NO SEAT OUTPUT. Both free seats, cc2 and fable, failed at authentication in under 2 seconds each with 0 tool calls, because the `claude` CLI's OAuth session had expired. The founder re-authenticated at 09:40 the same day and the work was re-cut and re-dispatched as `check_my_work_2026-09-28`.

The record is preserved because a round that produced nothing is still a round, and because this one carries 2 findings of its own.

FIRST, the dispatcher reported "seats proposed edits to 8 file(s)" and "harvested 3394 byte(s) of seat-written files" on a round where neither seat ran. Every captured path was a dispatcher or harvest artefact; the only difference in the diff was `elapsed_s` varying by 0.9 between the canonical log and the sandbox's copy of it. That is the provenance defect fixed the same day in `bench/panel_sandbox.py` by `_run_log_dir` and `_is_dispatcher_own_output`, guarded by `bench/tests/test_harvest_excludes_its_own_output_2026-09-28.py`.

SECOND, 0 paid seats were dispatched. `PANEL_ONLY=cc2,fable` held, which matters because the round 6 days earlier had spent on 5 paid seats through the same omission this setting prevents.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# Panel brief — the founder's verdicts of 2026-09-28, 11 items

## SECTION 1 — The question

The founder read the 2026-09-24 report and returned verdicts. **Most of them say: ask the
panel to devise the sane fix rather than bringing me the choice.** Verbatim: *"Isn't much of
this why the other models exist, to help you decide on the most sane fix and to keep my
workload to a minimum?"* So this brief is not a review of finished work; it is 11 pieces of
work he has delegated, and the single question is:

**For each item, what is the simplest sufficient fix that meets this project's formal
standards, and is it built and executed rather than proposed?**

He also ruled on how to treat CC1's own judgement, and it bounds your role here. Verbatim:
*"No you behaved correctly. Your role is not simply to dispatch seats and take them blindly at
their word. You need to check they actually make sense, when ran against the existing code."*
So CC1 will adjudicate what you return, against the code, and will not take it on trust.

## SECTION 2 — Use the harness

Form every answer by RUNNING the machinery, not by describing it.

`S_k` bears on items 1 to 3: the question in each is what may be admitted, rejected, or left
unscored on a target that is not a program. `R_k` bears with it, because the founder's rule is
that an unscoreable fix must not move risk. **`nu_star` and the break-even bear on item 10**,
which is a question about a published tool's mathematics. `gamma` and the two-sided gate bear
on NONE of this; say so if you find otherwise rather than reaching for them.

## SECTION 3 — Produce a fix, and test it

A finding without a fix is half an answer. A fix without a falsifier you have EXECUTED is a
hypothesis. Deliver every fix by WRITING IT INTO THE SANDBOX REPOSITORY TREE AT ITS REAL PATH;
a fix in prose is not delivered and a fix in scratch space dies at teardown.

<!-- figure: harvest loss | scripts/panel_harvest_loss_2026-09-22.py | 73.3333 -->

73.3333% of scripts delivered by seats never reached `scripts/`, 33 of 45, Wilson 95%
[58.9612%, 84.0351%]. Do not let yours join them.

A STORED falsifier may not call Wolfram; anyone reproducing this project must not need it
installed. You SHOULD use Wolfram while reasoning, as the chief secondary falsifier, with the
open-source tools primary.

## SECTION 4 — The 11 items

**1. DOES THE A19 REPAIR GIVE THE WHOLE ANSWER?** His words: *"what I'm not clear about is
whether this fix, together with your proposed additions provides the whole answer we need? And
if it doesn't how do we fix it."* State plainly whether the current behaviour meets his design —
a purely prose target recorded as having nothing to compute, while computable elements inside
prose are still solved — and name what is still missing.

**2. HOW TO WIDEN THE EXTRACTOR, WHICH IS THE LARGER HALF.** His ruling: *"yes the extractor
should be widened beyond code inside a fence because not all targets going forward will be
exclusively code. They may be any computable element that meets a given STEM criteria. The
question however might then become how to widen this extractor so that it can recognise these
targets and respond appropriately."* Measured already: over constructed documents, 9 of 12
prose documents carrying a computable element are invisible, because the extractor sees Python
inside a python-tagged fence. **Design the widening.** What counts as a computable element —
LaTeX, a plain-text equation, a numbered derivation, a units expression, a SMILES string? What
tool adjudicates each, given this project already has SymPy, z3, mpmath, pint, rdkit and
biopython wired? And what must NEVER be claimed as computable, because a false positive here
sends prose to a solver and reports the failure as a finding.

**3. SHOULD A PROSE-TARGET REJECTION REQUIRE A HIGH SEVERITY FINDING?** His words: *"High
severity I assume would allow the gate to remain reasonably permissible? What I don't want is a
condition where no run could ever complete, and where the HIL queue could grow to unmanageable
levels."* Measured: the current rule convicts on a MEDIUM bandit finding or on ANY ruff
diagnostic, and 3 of 3 benign documentation fixes are convicted at the same signal strength as
the harmful ones. **Answer his actual worry with numbers**: under each candidate rule, what
happens to the count reaching a human? A rule that empties the queue by admitting harm is as
bad as one that fills it.

**4. VERIFY CC1'S POST-REVIEW CHANGES, WHICH NO SEAT HAS SEEN.** His standing instruction:
*"If the other models CC2 and Fable have not verified your fix, ask them to do so, or to devise
a fix that meets the projects formal standards."* After your last round CC1 made 3 further
changes to `hooks/ffafp_audit.py` that no seat has reviewed: a `classify_write` adapter, a
`shell_bindings` alias, and an inference that classifies on the LITERAL LEADING PREFIX plus the
LITERAL EXTENSION so that a variable in a file's name no longer hides a write. Attack all 3.

**5. THE 3 SCRIPTS THAT ACT WHEN IMPORTED.** `test_help_never_acts_2026-09-11.py` was red on
them; CC1 reports 0 offenders in 206 now. Confirm it, and confirm nothing else broke in the
process.

**6. EDITING DURING A MEASUREMENT — NO MECHANISM EXISTS.** His question: *"Is this now also
fixed? Because if not, same answer as before."* It is NOT fixed. CC1 invalidated a full-suite
run 5 times in one day by editing the tree while it ran, and once the Stop hook's own refusal
was what pulled it into doing so. There is no guard. **Devise one**, and weigh it honestly: a
mechanism that refuses edits during a run could deadlock a session that needs to fix the thing
the run found.

**7. THE OWED SYNTHETIC FIXTURE.** Two end-to-end tests CC1 wrote for the Stop hook examined
nothing — `fa.scan` handed `fa.audit` no turn — and were deleted rather than shipped as
coverage. A seat previously showed the missing field was `origin: {"kind": "human"}`. Build the
fixture, with the anti-vacuity assertion that a turn OPENED and the verdict NAMES the file
before any exit code is read.

**8. TEST THAT THE HARVEST MECHANISM ACTUALLY WORKS.** His words: *"You can test the harvest
mechanism in the above panel review and make sure it works properly."* You are inside a sandbox
whose files will be harvested, so you are the test. Check the instrument at
`scripts/panel_harvest_loss_2026-09-22.py` reaches all 3 destinations at full depth and is
content-addressed, and say whether anything you deliver could still be lost.

**9. NO PAID DISPATCH WITHOUT HIS EXPRESS AUTHORISATION — A MECHANISM, NOT A PROMISE.** His
ruling: *"There should be no paid dispatches without my express authorisation. You should make
sure this is the case going forward. If the answers are useful however we should use them."* On
2026-09-22 CC1 dispatched 5 paid seats after he had asked for free panels, by omitting
`PANEL_ONLY=cc2,fable`. The guard `TestNoPaidSeatWasDispatched` catches it AFTER the money is
spent. **Make it impossible beforehand**, defaulting to free seats and requiring an explicit
authorised round name to spend. Note he also said the 2 answers already obtained are useful and
should be used.

**10. DOES THE PUBLISHED EXPLORER NEED REVISING?** New item, and it is public-facing:
`explorer/index.html`, served at `jebus197.github.io/Constraint_Engineering/explorer/`. His
question: do the maths-model revisions change it, since Astra proposed changes and CC1's study
may have superseded them.

CC1 has verified one thing and deliberately NOT concluded from it. The explorer's per-pass
change is `dR = R_old - R_new` over `R_det = R(1-q)/(1-qR)`, and at `sigma=1, nu=0` that is
**identically** the CONDITIONAL quantity Astra's surviving claim A2 identified — SymPy confirms
the expressions are equal, and it differs from the unconditional expectation `R*q` by a factor
of **70.3** at `R=0.99, q=0.3` on SymPy, mpmath and Wolfram Language alike. §5 of
`bench/directives/universal/cdsfl_operational.md` was corrected on that exact ground: the
conditional is the right quantity for "what did this pass buy me", and the WRONG one for
"is another pass worth running".

**What CC1 could not establish, and will not assert:** whether the explorer PRESENTS that
quantity as a worth-it or stopping decision, or merely displays the per-pass change. It tests
`dR >= o.theta` somewhere, but greps for the surrounding user-facing text returned nothing.
**Settle it by reading the file, and say whether a published tool is misinforming a reader.**
Tracking the no-detection branch is CORRECT for a trajectory, so do not report the recursion
itself as wrong without establishing the decision use. Also check `nuStar` on the same grounds.

**11. THE NAMING CHECK.** His verdict: *"Do the work."* Context: of 13 terms examined from
CC1's own reports, 8 were faults — 7 coined outright, and 1 worse, a term already meaning
something else in 7 files of this project. His complaint: *"It can't be the case that I wake up
to a tts report and struggle to know what you are talking about!"* Rule 28 forbids a
description where a name exists and Rule 19 forbids an unnamed subject; **neither forbids
inventing a name where none existed**, and the lint passed every faulty term at 0 findings.
CC1's proposal, for you to attack: compare each candidate term in a note against the repository
as it stood before the note, and flag anything appearing 0 times. **The obvious objection is
that it fires on every legitimate new name**, so measure its false-positive rate over the
existing notes corpus before recommending it.

## SECTION 5 — What would refute you

For each item, state before concluding what evidence would overturn your answer. On item 3
name the harmful case your rule still admits. On item 6 name the session your guard would
deadlock. On item 10 name what would show the explorer is correct as it stands.

## SECTION 6 — Output shape

Per item: `id`, `verdict`, `reasoning` with file and line, `fix_path` or NONE with the reason,
`falsifier_path`, `falsifier_command`, `falsifier_output` verbatim, `additive_check` naming the
caller that reaches your change and the test that executes it, and `refutation_condition`.
Then overall: `strongest_disagreement` with this brief's framing, which must not be empty, and
`passes_run`.

## SECTION 7 — Termination

Stop on diminishing returns: when a further pass adds no finding above the
real-world-consequence threshold. Say how many passes you ran and what the last added. Do not
manufacture findings and do not nitpick style. **If you cannot finish all 11, do fewer
properly and say which you did not reach** — a half-done item reported as done is worse here
than an item left open.

Disagreement with the other seat is information. Do not smooth it away.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 0 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel founder_verdicts_2026-09-28) -->

(this seat returned no response text)

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 0 recorded tool call(s).

<!-- verbatim-begin: fable (panel founder_verdicts_2026-09-28) -->

(this seat returned no response text)

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/founder_verdicts_2026-09-28/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
