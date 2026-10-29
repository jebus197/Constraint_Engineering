# B21 — the single registration point: a design for his yes or no

**2026-10-29.** Entry B21 of the master task list, ruled 2026-10-17. This exists so the decision is a yes or no on something concrete rather than an open question.

**His question, verbatim:** *"can you build this and implement it in such a way that it d..."* — the entry records it, and its open half is stated there as *"WHAT STILL NEEDS HIS RULING: the single registration point. That changes how every seat is configured, which is why it is not done here."*

## 1. The problem, measured rather than described

Adding a model touches **12 sites across 6 live-harness files**. Of the 10 steps a new seat passes on its way into a run, by `scripts/how_many_places_must_change_to_add_a_model_2026-10-16.py` executing `'Kimi'` through the real chain:

| outcome | steps | what it means |
|---|---|---|
| **SILENT DEFAULT** | 4 | the seat runs and the capability is simply absent |
| **SILENT DEGRADE** | 1 | `compose()` raises and the dispatcher's handler swallows it, so the run continues on a degraded prompt |
| **ANNOUNCED DEFAULT** | 4 | the default is taken and **recorded** in the live miss ledger — entry C18's contribution |
| **MISSING FILE** | 1 | `models/<Name>.toml` is absent, and this is the only step that is **loud** |

**The worst of the 5 silent steps, named because a tally of 5 understates it:** the context-budget ceiling. An unregistered model gets `L -> inf` where a registered model gets `168000.0`. An infinite ceiling means no truncation bound, so a prompt can be assembled with nothing stopping it. The second worst is `INITIAL_FINGERPRINTS -> None`, which leaves the routing ladder with nothing to route on.

## 1a. The class is not hypothetical — it is already realised for a live seat

**Found while writing this design, and it changes the premise.** The producer demonstrates the silent-default class with a hypothetical `'Kimi'`. It is already true of a **registered, live** seat.

Measured by execution: `runner_core.MODEL_SPECS` has an entry for `Fable` and `runner_core.INITIAL_FINGERPRINTS` does not. The call site at `bench/runner_core.py:342` reads `INITIAL_FINGERPRINTS.get(label, CapabilityFingerprint(0.2, 0.7, 0.7, 0.5))` — a hardcoded substitute, taken silently, with nothing recording that it was taken.

**The substitute is worse than every measured seat on all 3 capability axes**, cross-verified in NumPy and mpmath:

| axis | Fable's silent substitute | lowest measured | gap |
|---|---|---|---|
| `v_bar` | 0.7 | 0.75 | **0.05** |
| `A` | 0.7 | 0.75 | **0.05** |
| `C` | 0.5 | 0.65 | **0.15** |
| `D_decay` | 0.2 | 0.1 to 0.25 | inside the range |

So Fable — 1 of only 2 free seats actually in use — is presented to anything routing on capability as less capable than every seat that has been measured, and by a default rather than by a measurement.

**The asymmetry is the finding, and it shows the lesson was already learnt once.** `MODEL_SPECS['Fable']` carries `_provenance = 'inherited from CC2 2026-08-30; not measured'`, so for the spec table the borrowed origin is recorded. For the fingerprint table the same model gets a borrowed value with nothing recorded at all. The discipline reached 1 of the 2 tables.

**What is NOT claimed.** That this caused any particular past result. The routing ladder was measured **inert** in simulation on 2026-10-05, so a mis-ranked seat may have changed nothing there, and whether it has affected a live run is not established here. Raised as `pf:5c099c217f11`.

**And a second, smaller finding that bears directly on section 2:** the per-model TOML naming is **mixed**. 5 files are named by composer key (`chatgpt_5_4`, `codex_5_3`, `deepseek_v3`, `gemini_3_1_pro`, `opus_4_6`) and 1 by roster label (`Fable`). A loader keyed on either convention alone would miss files, so the convention must be settled before the TOML can be the single source.

## 2. The design: extend what already fails loudly

**The single registration point already exists.** It is the per-model file `bench/cdsfl_registry/models/<key>.toml`, and it is the **single step of the 10 that is already loud** when absent. It carries `[model]` identity and timing and `[protocol]` behaviour today; it does **not** carry the 4 things that default silently.

So the design is not a new registry. It is:

1. **Add the silently-defaulting fields to the per-model TOML** — the roster description, the model spec (`tau`, `L`, `c`), the initial capability fingerprint, and the roster label the composer key corresponds to.
2. **Derive the 4 tables from the TOMLs at import**, keeping `MODEL_SPECS`, `INITIAL_FINGERPRINTS`, `COMPOSER_MODEL_MAP` and `describe_model` **under their present names and with their present shapes**.
3. **Make absence loud**, as the missing file already is: a seat in the roster with no TOML, or a TOML missing a required field, is named at the POST screen and the run does not silently proceed on a default.

**Why keeping the names and shapes is the whole of the risk control.** Those symbols are read in **36, 37 and 43** places respectively, and the overwhelming majority are historical experiment runners rather than the live harness — the producer separates them as 50 sites in 16 historical files against 12 in 6 live ones. If only the *source* of the values changes, **0 of those readers need editing** and no archived runner changes behaviour. A design that renamed or reshaped them would touch all of them, and that is the version to refuse.

**It also resolves an ordering problem the present arrangement has.** `COMPOSER_MODEL_MAP` maps a roster label such as `CC2` to a composer key such as `opus_4_6`, while the TOMLs are named by composer key. If the TOML is the source, each file declares its own roster label, and the map is derived rather than maintained. A model with no file then has no mapping — which is loud by construction instead of defaulting to its own name.

## 3. What it costs

- **6 TOML files** exist today (`Fable`, `chatgpt_5_4`, `codex_5_3`, `deepseek_v3`, `gemini_3_1_pro`, `opus_4_6`). Each gains roughly 6 values, so about **36 values to migrate**, every one of them already written down in a literal somewhere.
- **1 loader**, plus the POST check already written for exactly this (`every seat is fully registered`, which today names each absent table per seat and returns PASS).
- **1 guard** that executes both paths: a registered seat loads, and an unregistered seat is named rather than defaulted.

**What it does not cost:** edits to the 50 historical sites, because their symbols keep their names and shapes.

## 4. What could break, stated rather than discovered later

1. **A literal and a TOML disagreeing during migration.** The mitigation is mechanical: assert for every current model that the value loaded from TOML equals the literal it replaces, before the literal is removed. That is the `execute-do-not-grep` rule — compare the 2 forms by calling them, not by reading them.
2. **Import-time failure turning a degradation into a dead run.** Entry C18 took this trade deliberately: its resolver *records* a fallback and still returns the default, because raising would stop a run that would otherwise have produced work. The same choice applies here, and the recommendation below keeps it.
3. **The simulated seats.** All 6 `-SIM` labels are currently absent from 4 tables each — 24 absences the POST screen reports inside a PASS. Under this design each would need a TOML or an explicit declaration that a simulated label inherits its base model's registration. **Which of those 2 is right is a genuine question**, and it is the single part of this that is not merely mechanical.

## 5. The panel already rejected 2 of the 3 options

Recorded on 2026-10-16, so they are not re-proposed here:

- **A plain error at each lookup** — needs 15 edit sites and fails at first use, which is mid-run after money has been spent.
- **Refusing to dispatch the seat** — that is benching a model, which this codebase forbids in the rule that a dead seat refuses the whole run.

## 6. One recommendation

**Yes to the design in section 2, with absence LOUD AT THE POST SCREEN and still DEFAULTING at run time.**

That is: the pre-run check names every unregistered field and refuses to report a clean board; the run itself still proceeds on a recorded default rather than dying. It makes the 5 silent steps visible before anything is spent, keeps C18's deliberate choice not to turn a degradation into a dead run, and costs no edit to any archived runner.

**The one thing his ruling must also settle:** whether a `-SIM` label registers in its own right or inherits its base model's registration. Everything else in section 2 follows mechanically from a yes.

## 7. What this authorises

Nothing. It is a design for his decision. B21's measurement half is already built and committed; this is the half that changes how every seat is configured, which is why it waits.

Written under CDSFL note standard v1.8 (17 October 2026).
