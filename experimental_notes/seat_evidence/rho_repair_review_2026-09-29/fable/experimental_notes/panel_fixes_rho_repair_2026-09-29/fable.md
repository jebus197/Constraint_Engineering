<!-- PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'rho_repair_review_2026-09-29', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: cfbc88a2ef4b4b4635d8665a4662ff76ccef1fcc2c29e49bfc8cceec66a9de59
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited. -->
# Seat: fable — between-rounds review of the rho repair and archive-ageing repair

**2026-09-29. All figures below re-measured in this sandbox; where I rely on a
number I could not re-measure, I say so at the point of use.**

Passes run: 3 (instrument probe; edge falsification + fix verification;
regression sweep). Pass 3 produced no new finding above threshold.

---

## Verdict on the 2 landed repairs

**The rho repair (35117b2, 80f0a0c) is SOUND in mechanism and INCOMPLETE in
one measured respect, now patched in this sandbox.** The corroborated series
does what the ruling asked: on a 4-round, 6-defects/round registry with k
re-sightings per round, `rho_corr` falls monotonically with k (1.000 at k=0
to 0.500 at k=6) while `rho_settled` stays pinned at 1.000
(`scripts/panel_probe_rho_novelty_2026-09-29.py`, SWEEP). Both committed
producing scripts re-run and reproduce their recorded figures exactly:
25/406 rounds overstate rho (6.1576%, Wilson [4.2053%, 8.9318%]), 25/25
overstatements, and arm1_harvest option-3 rho = [0.5909, 0.75, 0.5714,
0.875, 0.875] — byte-for-byte the docstring's claim.

**The incompleteness:** the pre-existing retroactive γ-input loop
(reference_runner_v3.py:~14967, added 2026-08-18) recomputes the WHOLE
`novelty_counts` series every round with the settled-only criterion, so the
corroborated value the settle pass writes into `novelty_counts[-1]` was
wiped back to the settled value exactly one round later. `rho_avg` therefore
read a window whose older elements had their discount stripped (measured
overstatement +0.1667 on a [6,3,3]-vs-[6,6,3] window, probe EDGE-6), and
gamma's input kept known re-sightings. Patched: the loop now reads
`_corroborated_novelty_series`. 108 targeted tests pass.

**The archive-ageing repair is SOUND.** Verified live: `_simulated_run_dirs`
returns 22 directories including `shakedown_2026-09-29/arm1_harvest`;
`arm1_harvest/runner_state.json` is caught by the per-file `-SIM`-key rule
(per_dir=False — the directory rule alone would MISS it); the admitted-report
baseline is back at 2026-08-23; `_provenance_time` parses all 4 dating shapes
and returns None (not a guess) on undated paths; 0 admitted reports lack
provenance.

## Two defects found and fixed (bench/reference_runner_v3.py)

1. **`_corroborated_discounts` resolved per pair, not per defect.** Two
   executed falsifiers: (EDGE-1) mutual occasions — A naming B and B naming
   A, same round — discounted BOTH, so one real defect with 2 registrations
   counted 0; (EDGE-3) a discount whose kept entry is REFUTED removed the
   OPEN re-sighting too, so an OPEN critical contributed 0 novelty for the
   whole run. Fixed with a per-component representative (earliest countable
   member, ties by registration order). Archive replay is unchanged under the
   fix (the degenerate shapes do not occur in recorded corroboration — the
   shakedown note's "complementary, not overlapping" claim re-measured TRUE
   for arm 1). 4 new guard tests appended to
   `bench/tests/test_rho_counts_distinct_defects_2026-09-29.py`.

2. **Stale docstring in `_check_gamma_alt_convergence`.** The requires-list
   still said "(d) not churning" 31 days after the founder's 2026-08-29
   ruling removed the early return. Executed: identical inputs with
   rho_churn False/True both return converged=True. Docstring corrected.

---

## The 5 decisions

### Q1 — promote the corroborated CRITICAL series? NOT YET; conditions now stated.

Before this evening the promotion would have been UNSAFE: probe EDGE-3
showed the pairwise discount could make an OPEN critical invisible to the
count-side gate — the exact silent-vanishing the A4 fail-safe exists to
block (A4 covers UNCONFIRMED only, not OPEN). That hole is closed and the
invariant is now a test
(`test_an_open_critical_is_never_invisible_to_the_critical_series`).
Remaining reason to wait: there is no measured run where the settled and
corroborated critical series disagree — the shadow line has never fired on
real data. Promotion loosens a convergence trigger; the evidence standard
this project applies to gate changes is a committed measurement, not a
consistency argument. **Recommend: keep the shadow line through the resumed
shakedown and the first paid run; promote only if it fires and every
divergent round is explained by a genuine critical re-sighting.**

### Q2 — retroactively resettle rho's history? The question dissolves under measurement.

`novelty_counts` is ALREADY whole-series resettled every round (line ~14967,
2026-08-18) — the brief's premise that "earlier rounds keep the value known
at the time" holds only for `rho_history`, not for rho's input series. The
right split, consistent with the 2026-08-18 and 2026-08-19 precedents:
**rho's INPUT window is a statement about what is known now** (fixed — the
retroactive loop is now corroboration-aware, so a re-sighting identified in
round r+3 stops inflating round r's element of the rolling window);
**`rho_history` entries are a statement about what was known then** — they
are the log of what the instrument read when the run made its decisions, and
rewriting them would falsify the record the archive exists to preserve.
Archived runs stay untouched; `scripts/option3_replay_2026-09-29.py` is the
correction lens. The dead run's round-1 value 7-vs-6 re-measured TRUE
(stored numerator 7; final-registry settle 6).

### Q3 — the two unchosen repairs: both still live; they compose; neither is redundant.

Option 3 counts what the immune pipeline already catches; it does nothing
for duplicates the pipeline never flags. The corroboration coverage is thin
(13 of 49 archived runs carry ANY corroboration records, 26.5306%, Wilson
[16.2113%, 40.2623%] — re-measured), so the counter is repaired while its
supply remains starved. (a) raises candidate RECALL: at the 0.1528 threshold
that catches all 4 known duplicates, precision 13.79% (4/29) — acceptable
for a CANDIDATE stage whose merges stay withheld pending a tool verdict, but
25 false candidates cost tool executions; the note's AUC 0.9900 (a figure I
rely on from the note, not re-measured — 4 positives, low power, as it says
itself) argues for a top-K-per-round candidate list rather than a raw
threshold, bounding the cost. (b) supplies the missing ADJUDICATOR — a
falsifier firing on both locations is a tool verdict in this project's own
sense — and converts the 4 merges arm 1 withheld every round from round 2
into decidable cases. **Recommend: (b) first, then (a) with top-K; neither
is made redundant by the landed repair, because option 3 changed the
counter, not the supply.**

### Q4 — the `-SIM` dict-key invariant: the brief's own figures are wrong, in the direction that matters.

Re-measured over the 103 archive-admissible documents: **both rules 21/103;
per-FILE alone 9/103 = 8.7379%, Wilson [4.6651%, 15.7777%]; per-DIRECTORY
alone 0/103 [0.0000%, 3.5955%]; neither 73/103.** (Local closed form and
statsmodels agree to 5.6e-17; the 9/103 interval confirmed with Wolfram
Language, local kernel.) The brief's "30 caught by both, 0 by either alone"
merges both+file-only into "both": the 9 file-only catches are exactly the
`commissioning_arm*` and `arm1_harvest` runner_states — the leaking files
these repairs exist for. So the per-FILE rule is load-bearing, and the
per-DIRECTORY rule is the redundant one on this corpus. **Keep both** (its
redundancy is corpus-dependent and it covers the converse failure: a future
sim state file carrying no label-map fields in a sim-named directory).
Better invariant: the durable fix is at the PRODUCER — the runner writes
`_simulated`/`severity_provenance` into reports but NOT into
`runner_state.json`, which is why detection is reverse-engineering
provenance from seat labels at all. Recommend the runner stamp `_simulated:
true` into every document it writes in a simulated run, at state-write time;
the label-key rule then becomes defence in depth rather than primary key.
That touches the live runner mid-shakedown, so it is the founder's call.

### Q5 — the grep blind-spot test: the TestAgeControl rewrite applies, and is applied.

`test_the_session_grep_sees_fewer_files_than_usr_bin_grep` asserted a
transient (this machine's newest shell snapshot defines a grep wrapper) as
an invariant. Measured here: the newest snapshot resolves `grep` to
/usr/bin/grep, ugrep is absent, counts = (398, 398) — the test's own failure
message correctly diagnoses "the wrapper is not loaded", i.e. a skip written
as a failure. Rewritten (same shape as TestAgeControl 2026-09-01): the
invariant is CONDITIONAL — when the session shell resolves grep to a shell
function, it must see strictly fewer files; when it does not, skip, with a
message distinguishing "no snapshot" from "snapshot without wrapper" so a
broken loader cannot read as a clean environment. Skipping does NOT destroy
the detection this test exists for: the detection targets the wrapper's
blind spot, which does not exist without the wrapper, and the measurement's
honesty (the refusal to print a reassuring 0%) is carried by the script's
vacuity guard, which `TestTheScriptRefusesRatherThanReassures` exercises in
EVERY environment. 7 passed, 2 skipped after the rewrite.

---

## Files changed in this sandbox (all suggestions, per standing rule)

- `bench/reference_runner_v3.py` — per-defect `_corroborated_discounts`;
  corroboration-aware retroactive series loop; corrected gamma-alt docstring.
- `bench/tests/test_rho_counts_distinct_defects_2026-09-29.py` — 4 guard tests.
- `bench/tests/test_shell_grep_blind_spot_2026-09-28.py` — conditional-invariant rewrite.
- `scripts/panel_probe_rho_novelty_2026-09-29.py` — the executed falsifiers (EDGE-1..6, SWEEP, GATE).

## What would refute each of my findings

- **Per-pair discount defect:** a demonstration that the runner's triage can
  never produce mutual occasions nor a discount onto a terminal entry — my
  falsifiers construct the registry states directly; I could not exhibit a
  full runner path that produces a 2-cycle. If such states are unreachable,
  the fix is hardening, not repair (the kept-terminal case needs only a
  later REFUTED verdict on the earlier entry, which IS a live path).
- **Retroactive-wipe finding:** evidence that line-14967's loop does not
  execute after the first corroborated overwrite — it is inside the same
  round loop, ~600 lines earlier, and runs unconditionally; a trace from a
  live run showing round r's element retaining its corroborated value at
  round r+2 would refute me.
- **Q4 re-measurement:** a population definition under which per-file-alone
  is 0 of 103. Mine: docs admitted by `_archive`'s key test, per-file =
  provenance keys OR `_has_sim_seat_label`, per-dir = the name test in
  `_is_simulated`. My proportions are properties of THIS corpus (a census,
  not a sample — the operational distribution of future leaking files is
  unknown, and I do not claim the 8.7% transfers to it).
- **Q5 rewrite:** a use of this test in an environment where the wrapper is
  absent but a DIFFERENT mechanism produces the blind spot (the skip would
  then mask it); I know of none — the header attributes the blind spot to
  the wrapper alone.
- **Gamma-alt churn finding:** any call path in which rho_churn flips this
  function's boolean; grep + execution says there is none.

## What I did NOT check

- The full test suite (forbidden here on time; the 5-failure record at
  693b29f is relied on as reported). My regression evidence is 108 targeted
  tests across 8 files.
- The immune pipeline's triage internals (`run_exp17_immune`) — whether
  is_duplicate can produce occasion 2-cycles; TestAgeControl's 4 failures in
  this sandbox (no `.git` here — `_key_first_committed` returns None;
  environmental, not a defect).
- Wolfram beyond one secondary check (serial-gate etiquette; the open-source
  set carried the rest).
- The claim that exp40/exp38 "show the machinery can work" (53 merges, rho
  0.5/0.0) — relied on from the shakedown note.
- Whether the concurrent shakedown's in-flight writes raced my archive
  reads (both producing scripts exited 0 with cross-tool agreement, so any
  race did not surface).

## Where I could not decide

- Whether triage can emit mutual duplicate_of pairs (needed to grade EDGE-1
  live-path vs hardening). The call site takes triage output as given; the
  producing pipeline is a separate module I did not audit.
- The operationally right top-K for Q3(a) — needs the resumed shakedown's
  candidate-volume data.

## Strongest disagreement with the brief's framing

The brief states "rho's churn flag is blocking condition (d) in
`_check_gamma_alt_convergence`" and instructs assessment of "whether the new
numerator can move the gate". Executed: churn has been unable to move that
gate since the founder's 2026-08-29 ruling — both churn states return
converged=True on identical inputs. The brief repeats the same stale
docstring the code carried. Where the new numerator CAN move an outcome is
`_check_stall_convergence` (STALL_CONVERGED requires >= max(stall_window,4)
consecutive churn rounds AND gamma above threshold) and the D1 phase
transition — paths that were UNREACHABLE while rho was pinned at 1.000,
since churn could never accrue. The repair's real behavioural surface is the
stall machinery, not gamma-alt condition (d), and the review should be
scoped there.
