# Shipping inventory: every built-but-not-on component, with a recommendation

2026-08-12, overnight. Measured mechanically, not recalled.

## The principle this implements

The founder's proposed ruling, verbatim: *"rather than ruling on six items now, rule
on one thing: that nothing ships in the ambiguous state. Every component is either on,
retired, or documented as an unused alternative with its evidence."*

The reason it matters is that a reader cannot currently distinguish **built and
deliberately rejected** from **built and forgotten**, and the second reads far worse
to a reviewer than either honest state.

## Method

All 21 boolean gates on `RunnerConfig` were enumerated from the dataclass and matched
against 864 config files, rather than recalled from notes. Shadow components without a
boolean gate were assessed from the artefacts they leave in run directories.

**One correction came out of doing it mechanically.** `routing_enabled` reported as
enabled by zero configs, contradicting the record. It is not disabled: the field was
renamed from `take_up_slack_enabled`, 17 shipped configs still carry the old name, and
both ingestion paths translate it. The inventory was searching the wrong key. This is
recorded because the same trap will catch the next person who audits by grep.

That near-miss exposed a real gap, now closed. `test_launcher_no_silent_drops` ends the
silent-drop class by iterating every dataclass field — correct, and it covers every
real field. But an alias is by definition not a dataclass field, so it was structurally
invisible to that test. Breaking the mapping would have silently disabled routing in 17
configs with a fully green suite. `test_config_aliases_survive_both_paths` now discovers
aliases by scanning both ingestion paths and asserts each survives, so a future rename
is covered without anyone remembering to return here.

## The inventory

| Component | Gate | Measured state | Classification | Recommendation |
|---|---|---|---|---|
| Capability routing | `routing_enabled` | LIVE — 17 configs via legacy alias | **ON** | No action. Record the alias in the glossary so the next audit does not repeat tonight's false alarm. |
| Stall termination on gamma | `stall_gamma_termination_enabled` | Off, no config sets it | **Documented alternative** | **Keep.** Not dead code — a dated design decision (2026-05-29) retained so the legacy behaviour can be re-enabled for a controlled ablation. That ablation is publishable evidence that the two-sided gate beats what preceded it. Deleting it would destroy the ability to demonstrate the current design is better. |
| Combined similarity rule | `hierarchical_novelty_convergence` | Off; recorded in shadow every run at no cost | **Pending — promote** | Founder has ruled: promote before the capstone. In progress. The refuted mutation-vector half is being removed; the measured half is being kept. |
| Latent tagger | `latent_tagger_enabled` | Off, no config sets it | **Pending evidence** | Measurement in progress against the archive: would enabling it have moved any run's convergence outcome? Recommend on that evidence, not on preference. |
| Severity calibration | `severity_calibration_enabled` | Off, no config sets it | **Pending evidence** | Same measurement. Depends on the tagger, so the pair rise or fall together. |
| Cross-experiment memory | `immune_memory_consume_rk0` | **Half on** — recording since Exp 47 via 11 configs, consuming nothing | **Pending evidence** | The most clearly resolvable of the group: it has been accumulating real data across live runs and influencing nothing. Measure what it learned and whether consuming it would have moved any historical verdict. |
| Discrimination control | (no gate) | Built; `corrected_copy` had zero writers | **Pending — wire, do not arm** | Being connected so it records an outcome without changing any verdict. The panel review of 2026-08-12 refuted the proposal to let it block closure: the check is on *access* rather than *dependence* and is defeated by one line, failing green. Ship as telemetry with that limitation stated. |
| Survived-falsification ledger | (no gate) | Built; no connection to the runner | **Withdraw the claim** | Deferred deliberately. It was built on CC1's own initiative from a founder question, without an explicit ruling, and the terminology is not yet agreed. Either wire it or stop describing it as existing; the current state is exactly the ambiguity this sheet exists to end. |
| Load balancer | (no gate) | Present; never invoked; no task set to distribute | **Pending research** | External research in progress on whether the design reflects current practice for decomposition at scale. Recommendation follows that. |
| Ouroboros | (no gate) | Shadow in 10 runs; records `would_have_injected: true` | **Documented alternative** | It is producing decisions, not merely observing. Promotion needs evidence it does not distort the governing pass condition — the same bar every other promotion faces. |
| Macrophage | (no gate) | Shadow in 28 runs; `pipeline_modified: false` | **Documented alternative** | Observes without modifying, across more runs than anything else on this sheet. Cheapest promotion candidate if the evidence supports it. |
| Stage 6 | (no gate) | **No shadow artefacts in any run** | **Retire or state plainly** | The only item here that is not running even in shadow. It should either be wired to produce shadow evidence like the other two, or be documented as not implemented. Describing it as "shadow" is currently inaccurate. |

## What this leaves for a ruling

Nothing on this sheet needs a decision tonight. Four items are pending measurements
that are running; two are pending research; three are recommendations that can be
accepted or rejected on their face.

The single ruling the founder proposed — that nothing ships ambiguous — is the right
one, and this sheet is what it produces. Three items change status under it
immediately:

1. **Stage 6** stops being called shadow, because it is not.
2. **The survived-falsification ledger** stops being described as existing until it is
   either wired or withdrawn.
3. **Stall termination** stops being listed as forgotten dead code and is recorded as
   what it is, a deliberate ablation switch.

## Standing note for future audits

Two components on this sheet were mis-recorded in the project's own notes before
tonight — cross-experiment memory was repeatedly described as dormant when eleven
configs had enabled it since Exp 47, and routing appeared disabled because it is set
under a legacy key. Both errors came from recalling state rather than measuring it.

The enumeration used here takes about a second to run and should precede any future
statement about what is switched on.

Written under CDSFL note standard v1.2 (14 May 2026).
