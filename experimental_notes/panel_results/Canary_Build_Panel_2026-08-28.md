# Canary seeding — independent build panel, 2026-08-28

Founder ruling 2026-08-27: "Build it, test it, implement it in its own independent 3 model panel
review ... give it its own panel/build process." This is that review.

Three positions: **cc2**, **fable**, and **CC1's own**, which was written and committed BEFORE
either reviewer returned (`Canary_Panel_CC1_Position_2026-08-28.md`) so that it is a position
rather than a summary of the other two.

**Where the reviewers disagree, the disagreement is preserved.** On the case-mangled path attack
fable reported REFUSED and cc2 reported the answer key READ. CC1 tested both: mangling a component
BELOW the repository root is refused, mangling a component OF the root reads the key. Both reported
accurately; they ran different things, and only running both settled it.

---

## fable — 15,711 chars, 469 s

# Canary seeding — independent build review

Verdict up front: the module is worth having and the core discipline (guarded load, blinding check, held-out-only p_hat, verifier-injected scoring that scores nothing without evidence) is genuinely present, not decorative. But I broke four of the guards with cases the commissioned tests never construct, and I found one structural defect in the estimator that inverts the instrument's purpose: **the dead model — the thing this exists to detect — is the one model that never appears in the p_hat report.** All 21 shipped tests pass (`21 passed in 0.17s`); every finding below is something I executed, with the probe result quoted.

---

## Q1. Is the safety guard real? Mostly — two demonstrated holes, one scope error.

**Held:** symlink outside→inside repo (REFUSED — `resolve()` follows the link), relative path with CWD inside the repo (REFUSED), case-mangled path `/BENCH/` on this case-insensitive APFS volume (REFUSED — `resolve()` case-normalises here), `~` expansion (covered, `expanduser` runs before the check), dict-as-catalogue (TypeError, loud not silent).

**F6 — MEDIUM — the guard protects the wrong tree.** `REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]` (canary_seeding.py:49) means the guard protects *the tree containing this copy of the module*, not "the repository". I am running in a throwaway worktree, and ran:

```
D2 _is_inside_repo('/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/whatever.json') → False
```

A harness copy running in a worktree — which is exactly how panels are dispatched, including this one — will happily read a catalogue sitting inside the **canonical tracked tree**. That is the exp48 shape recurring through the front door. Fix: refuse if the catalogue path lies inside *any* git work tree — walk `p.resolve().parents` looking for a `.git` entry (file or dir), or `git -C p.parent rev-parse --show-toplevel`. The invariant the docstring states ("keys live OUTSIDE the repository") is about the key's location, not the module's.

**F7 — LOW — hardlink bypass, confirmed.** `os.link(<in-repo file>, /tmp/hardlink.json)` then `load_catalogue(/tmp/hardlink.json)`:
```
A2 hardlink out->in: NO-REFUSAL -> ['K1']
```
Tracked-tree bytes were read through the guard. This requires a deliberate act, so it is outside the accident threat model the guard was built for — I rank it low, but `st_nlink > 1 → refuse` is a two-line mitigation. Related, accepted-by-design and I agree: an in-repo *symlink pointing outside* is accepted (A6). Content stays out of the tree; the committed symlink leaks only the key store's path. Note it in the docstring.

**Not a hole but a contradiction to resolve before wiring (Q4):** `vault_keys.sh`'s design is that keys are *unreadable while the panel runs*. `load_catalogue` needs the catalogue readable at seeding time and at scoring time. The module is silent on run-state; nothing stops a mid-run `load_catalogue` on an unsealed store — which is precisely the window exp48 exploited.

## Q2. Are the Goodhart guards load-bearing? Two of three have confirmed holes.

**(a) Held-out-only p_hat — defeated via cross-split duplicate id (F3, HIGH).** No layer checks id uniqueness catalogue-wide: `seed()` checks duplicates only within one call (canary_seeding.py:139), `load_catalogue` not at all, `detection_rate` not at all. Catalogue with `X1` in calibration AND `X1` in held-out; model kills only the *calibration* one:
```
B1 dup id across splits: NO-REFUSAL -> {'alpha': 0.5}
```
A calibration kill scored as held-out detection — the exact Goodhart failure the split exists to prevent. Fix: `load_catalogue` refuses duplicate ids; `detection_rate` refuses any id present in both splits.

**(b) Single-generator refusal — string-level only (F5, MEDIUM).**
```
B2 empty generator as 2nd gen:  NO-REFUSAL -> {'alpha': 0.5}   # generators {"", "handwritten"}
B3 'gpt' vs 'gpt ' generators:  NO-REFUSAL -> {'alpha': 0.5}
```
`Canary.__post_init__` (line 79) validates `find`/`replace`/`split` but not `generator`, `domain`, or `defect_class` for emptiness. Fix: require non-empty stripped `generator`; normalise (`strip().lower()`) before the set-count at line 222. Be honest about the ceiling: no code can verify *semantic* generator diversity — beyond typo-hardening this guard is necessarily a process control, and the docstring should say so rather than imply the code enforces it.

**(c) Blinding — three confirmed problems (F4, MEDIUM).**
1. **Docstring lies.** `seed()`'s docstring (line 130) says the seeded text is verified to contain "no split name". `_assert_blind` (line 162) checks id, generator, summary — never the split. Ran it: `# held_out` in the replacement → `NO-REFUSAL`.
2. **Plural evasion.** `\bmutant\b` does not match `mutants`; ran `# mutants, canaries` → `NO-REFUSAL`. A word blacklist is a tripwire, not a proof; fine, but it should not be described as "checked, not hoped for" without that caveat.
3. **Confirmed false refusal — this one will bite the real corpus.** A clean target containing "Results used a *seeded* random number generator" is REFUSED outright (B6). Same for any biology document containing "mutant" — and the corpus has a bio domain (Tranche B, biopython). Root fix for all three: check *introduced* text, not the whole document — flag a token only if its occurrence count in seeded exceeds its count in clean. That also lets you add split names safely ("calibration" is legitimate DSP prose).

## Q3. Is the measurement sound? Two real defects, one structural gap, one statistical honesty problem.

**F1 — HIGH — the dead model is invisible.** `catches()` creates a model's entry only on a verified catch (`out.setdefault` at line 204). A model whose findings all fail verification never gets a row; `detection_rate` iterates `caught.items()` (line 229). Ran it:
```
D1 catches: {'alpha': ['H1']}      # beta submitted findings, caught nothing
D1 p_hat report: {'alpha': 0.5}
D1 => dead model 'beta' absent from report: True
```
The instrument exists to expose the model with p_hat = 0, and that is the model the report omits. A gate reading this dict would see only live models and pass. Fix: `detection_rate` takes an explicit model roster (or `catches` seeds `out[model] = []` for every finding's model — one line, though a roster is stronger since a fully silent model submits no findings at all).

**F2 — HIGH — denominator unlinked from what was seeded.** `detection_rate` sets k from held-out canaries *in the catalogue passed*, with no connection to the `seed()` manifest. Pass the full catalogue when only half was seeded:
```
C1 unseeded canaries in k: {'alpha': 0.5}    # panel caught 2 of 2 actually seeded
```
Unseeded canaries are unkillable by construction and silently deflate every model. This is the denominator error Q3 asked about. Fix: `detection_rate` should accept the manifest (or seeded-id set) and refuse held-out canaries not in it. Companion (F8, LOW): ids in `caught` that exist in no canary are silently intersected away (`D3 → 0.5`) — an upstream id-drift bug would be invisible; refuse unknown ids.

**Structural (F9):** (i) *Unkillable canaries* — mutation testing's equivalent-mutant problem — have no exclusion mechanism; one bad canary permanently caps everyone's p_hat below 1.0 and there is no way to mark it. (ii) *No round attribution* — a canary killed in round 1 proves the panel was alive in round 1; the gate's question is whether it is alive at rounds 5–6 when the streak accrues. `catches/k` conflates "alive ever" with "alive now". (iii) Two models finding the same canary is handled correctly for per-model rates, but there is no panel-level p_hat (`|union ∩ ids|/k`), and the gate question is about the panel. (iv) Accidental catches are fine — the counterfactual criterion means detection is detection regardless of intent.

**Statistical honesty.** As an estimator, catches/k is the correct MLE for a per-model detection proportion. But at plausible catalogue sizes it is noise for gate purposes — I computed Wilson intervals (statsmodels):
```
k=4  caught=4  p_hat=1.00  95% CI [0.51, 1.00]
k=6  caught=5  p_hat=0.83  95% CI [0.44, 0.97]
```
A perfect 4/4 is statistically compatible with a coin-flip detector. Any gate wiring must either use k ≥ ~20 held-out canaries per domain or report the interval, not the point.

**No-vote check (constraint 2): clean.** `verifier=None → {}` is honest; the kill criterion is programmatic counterfactual demonstration. One caveat: the counterfactual contract lives only in a docstring — nothing prevents wiring a prose-similarity or model-agreement verifier later. When the real verifier is built, the no-vote property must be tested there, not assumed from here.

## Q4. What must exist before "yes, block"?

Nothing imports `bench/canary_seeding.py` today (grep confirms; only the test does) — genuinely unwired, as claimed. In order:

1. **Fix F1–F5 first.** A gate consuming today's p_hat blocks on a number that omits dead models and divides by the wrong k.
2. **A real verifier** — new `bench/canary_verifier.py` bridging runner findings to the counterfactual criterion, reusing `reference_runner_v2.py`'s falsifier re-execution machinery. Must execute the falsifier on *both* seeded and clean text. This is the hard build; nothing exists.
3. **Findings decontamination — the interaction nobody has named.** Seeded canaries generate *genuine critical findings*. Those enter the settled novelty series feeding `novel_critical_history`, so every killed canary resets the zero-critical streak of `_check_gamma_alt_convergence` (reference_runner_v2.py:4866): the instrument breaks the gate it calibrates. The runner must tag canary-attributable findings (via manifest id after counterfactual match) and strip them from the series before gate evaluation. No such mechanism exists.
4. **Gate condition (e)** in `_check_gamma_alt_convergence`: held-out p_hat ≥ threshold, threshold *derived from the calibration split* — no code computes a threshold from calibration today; the split exists but nothing consumes it. Failure routes to HIL, not auto-verdict (constraint 2).
5. **Vault order-of-operations** (`bench/vault_keys.sh`): catalogue open at seed time → catalogue + manifest sealed before dispatch → opened for scoring after the run. Plus a run-state check in `load_catalogue`, and manifest-aware corpus exclusion so the seeded target is withheld from publication until post-run (constraint 1). Note `seed()` returns the manifest but the module has no guarded writer — the read path is guarded, the write path is trust; add `write_manifest()` with the F6-strengthened refusal.
6. **A canary ledger.** A held-out canary is burned the first time it is scored — it is calibration thereafter. Nothing tracks usage across runs; without rotation, p_hat decays into memorisation exactly as the docstring warns.
7. **Round-stamped scoring** if the founder's question is "alive now" rather than "alive ever" (F9.ii).

## Q5. The case against — and it lands harder than the brief expects.

**Strongest form:** p_hat measures detection of *generator-producible defects from known classes*. The residual risk after a converged run is dominated by defects *outside* known classes — that is why they are residual. High p_hat therefore certifies the panel against yesterday's defect taxonomy while the gate uses it to certify today's document. Mutation testing survives this via the coupling hypothesis (simple mutants couple to real faults), which is empirically supported for *test suites*. For LLM reviewers it is untested, and there is reason to doubt it transfers: a test suite cannot pattern-match "this sentence was edited"; a language model is precisely a detector of local stylistic discontinuity. **Texture learning is the killer, and this design would not detect it.** All generators share the edit signature — an inserted error inside otherwise-coherent prose — so the multi-generator guard is no defence against edit-detection-as-a-skill. And fable's own stated requirement, *held-out defect classes*, is not implemented: the split is per-canary; nothing refuses a held-out set whose defect classes all appear in calibration. Ran the check implicitly — every canary in every test carries `defect_class="reasoning"` and nothing objects. A texture-learning panel yields a p_hat that is high, stable, and false — the "contaminated p_hat = false calibration" fable warned about, produced by fable's own module.

**Cheaper instruments that answer part of the question:** (i) *natural canaries* — prior HIL-confirmed defects deliberately left unfixed in a corpus document; no seeding, no blinding machinery, no edit texture; weakness: no control over type/location/count, and they burn on reuse too. (ii) *Fresh-context probe* — hand the converged document to an ITC-restarted instance; new criticals → panel was exhausted; already project-native and near-free; weakness: not affirmative when it finds nothing, since a fresh instance can share blind spots.

**My position, held against the proposal's:** build it anyway — it is the only *affirmative*, ground-truthed discriminator between clean and exhausted on offer, and the fresh-context probe should run beside it as the cheap cross-check. But the texture-learning detector must exist before p_hat touches the gate: concretely, a matched-control comparison (p_hat on seeded defects vs catch rate on natural canaries of the same classes — divergence over runs = the panel is learning texture, not detection) and a held-out-class refusal in `detection_rate` parallel to the single-generator one. Without those, wiring this to the gate would replace "silence we cannot interpret" with "a number we should not trust", which is worse, because it looks like evidence.

---

## What I could NOT check

- **The verifier contract on real findings.** No verifier implementation exists; `catches()` was exercised (by the shipped tests and by me) only with synthetic lambdas. Whether the counterfactual kill criterion is *implementable* against real runner finding objects and falsifiers is unverified — it is the largest untested surface.
- **Texture learning empirically.** Requires live panels over repeated seeded runs. My Q5 claim that this design would not detect it is an argument from what the code refuses (verified: nothing checks defect-class overlap between splits), not a measured demonstration of a panel doing it. [SPECULATIVE] as to whether real panels actually develop the skill.
- **Guard behaviour on case-sensitive volumes / non-macOS.** A4 (case-mangling) was refused on this APFS volume because `resolve()` case-normalised; I did not verify other filesystems.
- **Full bench suite regression.** I ran the commissioned file (21/21) and confirmed by grep that nothing else imports `canary_seeding`, so regression risk is nil by construction; I did not run the full suite in this worktree for time.
- **Whether git would surface the A2 hardlink** in any tracking sense — irrelevant to the finding (the tracked inode's bytes were read), so I did not pursue it.

One meta-observation on the tests: the accept-AND-refuse-per-guard discipline in the test file is right and real — but every hole above lives in a case the tests never construct (cross-split duplicate, zero-catch model, catalogue-vs-manifest mismatch, split-name token, plural, worktree boundary). The tests verify the guards do what they say on the inputs the author imagined; they do not yet try to defeat them. Adding my attack battery (it is in `/tmp/canary_attack/attack.py` and `attack2.py`, dies with this worktree) as regression tests — against the *fixed* module — would close that gap.

---

## cc2 — 17,525 chars, 394 s

Everything below I ran. 21/21 commissioned tests pass; that is where the good news ends.

---

# Canary seeding — independent review

**Verdict: do not wire this to the gate. The concept is sound and worth building. This build guards the wrong artefact, and its central statistic hides the one signal it exists to produce.**

---

## Q1. The safety guard is real but narrow, and it is watching the wrong door

`_is_inside_repo` (L91–96) → `resolve().relative_to(REPO_ROOT)`. I attacked it five ways:

| Attack | Result |
|---|---|
| honest in-repo path | **refused** ✓ |
| symlink outside → in | **refused** ✓ (`resolve()` follows) |
| relative `../bench/key.json` | **refused** ✓ |
| **case-variant path** (`/REPO/bench/…`) | **★ ANSWER KEY READ** |
| **hardlink outside → tracked file** | **★ ANSWER KEY READ** |

```
A2 case-variant path: *** READ ***  -> THE ANSWER KEY — Nyquist bound weakened at line 3
A3 hardlink outside:  *** READ ***  -> THE ANSWER KEY — Nyquist bound weakened at line 3
```

**F1 (case bypass).** macOS APFS is case-insensitive, but `Path.resolve()` does **not** canonicalise case — I measured both: `UPPER exists: True`, `resolve()` returns `…/REPO/BENCH` unchanged. `relative_to` is pure string comparison, so it raises `ValueError` and the file is declared outside. This is not an exotic attack; it is any config, env var or hand-typed path with different casing. The exp48 lesson was that the dangerous call site *looks innocuous* — this is that shape exactly. Fix: compare `os.path.realpath` + `os.path.normcase`, or `os.path.samefile` against each ancestor.

**F2 (hardlink).** `resolve()` cannot see through a hardlink. Lower priority — it needs deliberate action, not an accident.

### F3 — the module guards the catalogue and leaves the seeded target wide open. This is the finding.

`seed()` returns the seeded text. There is **no write guard anywhere in the module** — I confirmed by AST and string scan that `canary_seeding.py` contains no `write_text`, no `open(`, no `json.dump`. Guarding reads while offering no protected write is half a door.

And the project has *already measured* what that costs. `bench/cdsfl_registry/targets/MANIFEST.md:85–92`:

> "A target kept under version control leaks itself… `git diff` on the target returns the planted set at **precision 1.000**, with no answer key, no similarity measure and nothing for a detector to catch. Measured 2026-07-29: six of eleven for physics, three of nine for biology, **Fisher p = 1.3e-05**."

I reproduced it against `seed()` output in a fresh git repo:

```
seed() returned happily. manifest ids: ['K1', 'K2']
--- git diff on the tracked target ---
-The sampling theorem requires f_s > 2*f_max …
-With N = 1024 points the bin spacing is 1.5625 Hz.
+The sampling theorem requires f_s > f_max …
+With N = 1024 points the bin spacing is 15.625 Hz.
changed lines: 2  canaries: 2  precision: 1.0
```

The catalogue is the lesser artefact. The seeded document *is* the answer key, in a form that needs no key to read, and this module hands it back with nothing objecting.

### F4 — the docstring misattributes exp48, and the real cause indicts the design

Module docstring L30–32: *"the harness read the key… through a path that looked innocuous at the call site."*

`resources/RECOVERY.md:133` and `bench/tests/test_falsifier_cannot_read_the_key.py:1–12` say otherwise: **a model** wrote a falsifier that opened the key, and the runner re-ran it. Its own comment: editing the file *"destroys a seeded fault the panel is scored on"*. The model read the key **because the document had seeded faults in it**. Seeding created the motive. A module whose entire purpose is seeding faults should not summarise that incident as a path-handling slip — it is the closest thing to a base rate this design has, and it points at the design.

### F5 — it reimplements a stronger guard that already exists, and does not extend it

`bench/falsifier_verify.py` has `scan_falsifier_source`, `scan_falsifier_output`, `_protected_values()`, a sandbox observer with deny-tracing — regression-tested against the verbatim exp48 exploit and all 457 archived falsifier sources. `canary_seeding.py` uses none of it and rolls its own weaker check. Two guards for one property, free to drift.

Worse, the existing layer has **no concept of canary material**:

```
protected env vars: ('CDSFL_KEY_DIR','CDSFL_STORE','CDSFL_VAULT','CDSFL_SCORING_CONF',
                     'CDSFL_TARGETS','CDSFL_LEGACY_STORES','CDSFL_PROTECTED_PATHS')
canary-related?   NONE

catalogue inside allowed root    -> *** ALLOWED ***
relative glob '**/*canar*.json'  -> *** ALLOWED ***
env-var indirection              -> *** ALLOWED ***
printed canary record            -> *** ALLOWED THROUGH ***
```

`_KEY_MATERIAL_RULES` (L274–298) covers "answer key", "planted false", "seeded fault", "scoring key", `MANIFEST` — **not "canary"**. A falsifier can read a canary catalogue and print its ground-truth summaries and the output net passes it. This is exp48 re-armed one layer up.

---

## Q2. One guard is real, one is decorative, one is half-built

### (c) Blinding — **decorative against anything but a typo**

`_assert_blind` L171: `re.search(r"\bcanary\b|\bseeded\b|\bmutant\b", low)`. Word-boundary anchors on three singular nouns. Everything I tried walked through:

```
ACCEPTED:  # deliberately mutated for the canaries exercise
ACCEPTED:  # PLANTED DEFECT - do not fix
ACCEPTED:  # injected mutation, seed id below
ACCEPTED:  # CANARIES: this line is the test
ACCEPTED: split name 'held_out' in seeded text
ACCEPTED: defect_class leaked
```

`\bcanary\b` does not match **canaries**. Not `mutated`, `mutation`, `planted`, `injected`, `synthetic`, `seed`. A seeded document can announce itself in block capitals and pass.

**F6.** And `seed()`'s docstring (L129–131) claims the text is checked for *"no canary id, no split name and no generator name"*. Code checks id, generator, **summary** — **not split**. The docstring is wrong in both directions. Under `docs-defect-parity` that is a defect.

### (b) Single-generator refusal — **decorative**

It tests set cardinality ≥ 2 on raw strings. No normalisation, no balance:

```
9x'gpt-5.5' + 1x'gpt-5.5 ' (trailing space): {'m': 0.1}   ← accepted
9x'handwritten' + 1x'Handwritten':          {'m': 0.1}   ← accepted
99:1 imbalance, k=100:                      {'m': 0.01}  ← accepted
```

A whitespace typo satisfies the Goodhart guard. It refuses only the literal degenerate case a careful person would never build, and accepts the 99:1 contamination a careless one would.

### (a) Held-out-only — **real, but half-built**

The held-out filter works (L217, verified: calibration hits do not inflate `p_hat`). But `CALIBRATION` appears at L52, L54, and L221 — a constant, a tuple member, and an error string. **No function in the module ever computes anything from a calibration canary.** The stated purpose, "Calibration canaries set the threshold" (L214), is not implemented. Right now the split is a label that means "excluded".

---

## Q3. The measurement is not sound. `p_hat = catches/k` hides panel death.

### F7 — a model that catches nothing vanishes from the report. This is the worst finding in the build.

`detection_rate` L229: `{m: … for m, hits in caught.items()}`. `catches()` only `setdefault`s a model when the verifier returns True, so a model that caught **nothing** is never a key.

```
catches()        -> {'alpha': [...], 'bravo': ['H1']}
detection_rate() -> {'alpha': 1.0, 'bravo': 0.25}
charlie present? False        ← charlie caught zero of four
mean over reported: 0.625  |  true mean over 3 models: 0.417
```

A blind panel member — the exact condition this instrument exists to detect — does not appear as `0.0`. It disappears. Any aggregate over the returned dict is **biased upward precisely as the panel dies**. `detection_rate` has no roster parameter, so it cannot know charlie exists.

**F8.** Compounding it, three different worlds return the identical `{}` with no exception:

```
no verifier available : {}
all models blind      : {}
```

"I could not measure" and "the panel is dead" are the same value.

### F9 — no exposure model, so the denominator is wrong whenever review is partitioned

`k` is *all* held-out canaries. If the panel splits a document by section, or if models differ in context window, a model is scored on canaries it was never shown. And there is no round dimension at all: `p_hat` is a single-shot binomial applied to a multi-round process, where a canary killed in round 1 is presumably fixed before round 2. The correct denominator is canaries **exposed to that model in that round**.

### F10 — an unkillable canary reads as a dead panel

`find != replace` is textual. Nothing checks the mutation is semantically detectable. One null canary drags every model uniformly:

```
alpha, 4/4 real + 1 unkillable -> 0.8
```

The instrument reports panel degradation when the canary is the broken thing. Calibration canaries are exactly the mechanism that would catch this — and they compute nothing (F-above).

### F11 — no minimum k, no interval

`k=2` is accepted; `p_hat` is quantised to {0, 0.5, 1.0}. Wilson 95% CIs (statsmodels):

```
p_hat=0.50 k= 2   CI [0.09, 0.91]
p_hat=0.75 k= 4   CI [0.30, 0.95]
p_hat=0.80 k=10   CI [0.49, 0.94]
p_hat=0.80 k=20   CI [0.58, 0.92]
```

At realistic catalogue sizes a point estimate cannot be compared to a threshold. `p_hat` should be a Wilson interval, and the gate should read its **lower bound**.

**On "two models find the same canary":** handled correctly — per-model dedup at L201, each model credited independently. That is right for a per-model statistic. **On "accidental catch":** it counts, and I think that is defensible for *is the panel still detecting* — but the docstring's claim that the counterfactual is "the only evidence accepted" implies a rigour about *intent* the method does not have.

### F12 — `seed()` is order-dependent

`n = out.count(c.find)` (L142) counts against the **partially seeded** document, not the clean one. Same canary set, different list order, different outcome:

```
[X,Y]: ValueError -> K2: `find` text occurs 2 times…
[Y,X]: ACCEPTED
```

`seeded_sha256` is therefore order-dependent too, which undermines the manifest as a provenance record. Validate all `find` counts against `target_text` before mutating anything.

---

## Q4. What must exist before the gate can block on a missed canary

Assume the ruling is "yes, block". Concretely required:

1. **`bench/falsifier_verify.py`** — add canary vocabulary to `_KEY_MATERIAL_RULES` (L274) and a `CDSFL_CANARY_DIR` to `_PROTECTED_ENV_VARS` (L335 area). Demonstrated above: three falsifier shapes read a catalogue today and the output net passes ground-truth summaries. Without this, wiring canaries to the gate **manufactures exp48 conditions on every run**.
2. **A real verifier.** `catches(verifier=...)` is injected and every caller must supply one. The only honest implementation is `reverify_falsifier` (`bench/falsifier_verify.py:1064`) run twice — seeded and clean — with the catch defined as CONFIRMED-on-seeded ∧ REFUTED-on-clean. That function does not exist and is the bulk of the remaining work. Note the cost: **2× falsifier re-execution per finding per round**.
3. **A protected write path** for seeded target + manifest, refusing any in-repo destination — mirroring `load_catalogue`, closing F3.
4. **`bench/reference_runner_v2.py:4866` `_check_gamma_alt_convergence`** — a new parameter and a new return reason. It currently returns `Tuple[bool, str]` from conditions (a)–(d); a canary condition (e) is a fifth way to fail, and every caller reading that string needs auditing.
5. **A roster.** F7 makes `detection_rate` unusable as a gate input until it takes the expected model list and reports absent models as `0.0`.
6. **A stopping rule.** If a missed canary blocks convergence and canaries stay seeded, a run with one unkillable canary (F10) **never converges**. There must be a bounded escape, and per the standing directive the cause will be mechanical — but the runner must not hang while you find out.
7. **`bench/tests/test_two_sided_gate.py`** — extend, or the gate change ships untested.
8. **Note under `cdsfl_note_standard_v1.7`** + `docs/ARCHITECTURE.md`, `docs/GLOSSARY.md` (`p_hat`, canary, calibration/held-out).

**On the no-voting constraint (#2 in the brief): this design does not smuggle a vote back in.** `catches()` refuses to score without an injected verifier and returns `{}` rather than guessing — that is the right instinct and it is honoured. The verdict comes from re-execution, not agreement. My objection to the measurement is statistical, not constitutional. Provided requirement 2 above is built from `reverify_falsifier` and not from prose-matching against `summary`, TOOLS DECIDE holds. The docstring at L185–188 explicitly rejects prose matching; keep that.

---

## Q5. The strongest case against — and I find it partly persuasive

**The instrument's failure mode is indistinguishable from success.**

If a panel learns to spot seeded defects by *texture* — edit-shaped phrasing, a mutation's characteristic locality, an unnatural collocation — `p_hat` goes **up**. The design reads rising `p_hat` as a healthy panel. So confidence in the instrument increases exactly as the instrument becomes invalid. Nothing in this build discriminates the two: `_assert_blind` checks substrings, and the only texture guard is generator diversity, which I defeated with a trailing space.

**This is not hypothetical here.** `resources/RECOVERY.md:133`: on exp48/49/50 *"the planted count equalled sections-minus-one, so the design was inferable **without touching a key at all**."* A structural tell already leaked the seeded set in this project's own history. That is texture detection, observed, and `_assert_blind` would not have seen it — it is a property of the *distribution* of edits, not of any token.

**What would fix it, and is absent:** a discriminator control. Give a held-out model the seeded and clean documents and ask which was edited. If it can tell above chance, `p_hat` is not measuring detection. That control is cheap and it is the thing that makes the whole design falsifiable. It should have been in the build.

**Cheaper instrument that answers the same question:** the corpus already contains targets with planted defects and per-target counts under key (`MANIFEST.md:63`, `exp52_factorial_answer_key.json`, 48 claims). Running the panel against an already-scored held-out target measures panel liveness with no new seeding machinery, no new key material, and no new leak channel. It is weaker — the defects are not fresh, so it degrades with reuse — but it costs a config change rather than a module, and it does not create the motive that produced exp48.

**Where I land, disagreeing with the brief's framing:** the two-sided gate's blind spot is real and worth an instrument. But this build has *inverted the risk*. It protects the catalogue, which is a file, and exposes the seeded target, which the project has already measured leaking at precision 1.000. Seeding is the highest-variance possible answer to "is the panel awake", and the historical record shows seeding is what motivated the only real key access this project has had. Build the discriminator control and the cheap held-out-target check first; they will tell you whether canary seeding is worth its blast radius.

---

## What I could not check

- **The verifier.** It does not exist. Everything about `catches()`'s real behaviour — whether counterfactual re-execution actually discriminates a canary kill — is untested by me and untestable from this tree. All my scoring findings assume a perfect verifier; a real one can only be worse.
- **Whether `p_hat` correlates with anything.** No live run, no panel dispatch, no calibration data. That canary detection tracks genuine review quality is the design's core assumption and it is **unvalidated**. I have no evidence for or against.
- **The 26 s Wolfram ceiling / cross-validation.** Not needed; SymPy and statsmodels covered the statistics locally.
- **Case-sensitivity on other filesystems.** F1 is confirmed on this macOS APFS volume. On a case-sensitive Linux volume the bypass does not apply; the hardlink one (F2) does.
- **Sandbox runtime behaviour.** I tested `scan_falsifier_source`/`scan_falsifier_output` statically. I did not execute the observer, so I cannot say whether it would deny a canary read at runtime — only that canary paths are absent from `_protected_values()`.
- **Whether the founder's key store is already covered.** If catalogues happen to live under `CDSFL_KEY_DIR`, F5 is much reduced. I could not check — the env vars are unset in this worktree.
- **exp48 primary source.** I read the incident via `RECOVERY.md`, `ONBOARDING.md` and the test file's docstring. I did not open the run report or errata, so F4 rests on three secondary records that agree with each other.

---

**Ranked:** F7 (blind model vanishes) and F3 (seeded target unguarded, precision 1.000) are blockers. F5 (canary material invisible to the falsifier gate) is a blocker before any live run. F1, F6, F10, F12 are must-fix. F2, F8, F9, F11 are must-fix before gate wiring. The blinding regex (Q2c) and the generator guard (Q2b) need rebuilding, not patching.

Nothing was pushed; this worktree is disposable. One note — it is 04:11 BST. The review is complete and stands on its own, but I would not act on it tonight.

---

## Brief

```
# Canary seeding — independent build review

You are reviewing a NEW module built tonight: `bench/canary_seeding.py`, with tests in
`bench/tests/test_canary_seeding_2026-08-28.py`. Read both in full before answering.

## Where it came from

The fable reviewer proposed this on 2026-08-27 (its Note 5, route B). The founder ruled:
"Build it, test it, implement it in its own independent 3 model panel review." This is that
review. You are reviewing a build, not a proposal.

## What problem it claims to solve

The runner's two-sided convergence gate certifies a run as converged when the critical-severity
novelty slope has flattened AND K consecutive rounds add no new critical findings. Both halves
read the same evidence: what the reviewing models said. Neither can distinguish

    "the panel went quiet because the document is clean"      -> converged
    "the panel went quiet because the panel stopped looking"  -> exhausted

Canary seeding is meant to supply that discriminator: seed defects of known type and location,
and measure whether the panel still kills them. Method is mutation testing (DeMillo, Lipton and
Sayward 1978) pointed at reviewers rather than at a test suite. p_hat = catches / k.

## Hard constraints this project operates under — violating any is a finding

1. **Keys and planted defects live OUTSIDE the repository.** Unencrypted study copies may be
   published only AFTER an experiment has run. exp48 had to be EXCLUDED from the corpus because
   the harness re-ran a falsifier that opened the scoring key.
2. **No model voting.** Findings are confirmed programmatically or by a human, never by models
   agreeing. If any part of this design smuggles a vote back in, say so.
3. **A simulated agent never carries a vendor name.**
4. Goodhart guards must be designed in, not retrofitted. Fable's own words on the proposal:
   "diverse generators, blinding, held-out defect classes -- a contaminated p_hat is false
   calibration."

## The questions

**Q1. Is the safety guard real?** `load_catalogue` refuses any path inside the repository.
Try to defeat it. Symlinks, `..` traversal, a relative path, a path that resolves inside the
repo only after expansion, a catalogue passed as a dict rather than a path. If you can get
answer-key material read from, or written into, the tracked tree, that is the finding.

**Q2. Are the three Goodhart guards actually load-bearing, or decorative?**
   (a) p_hat computed on held-out canaries only;
   (b) a held-out set drawn from a single generator is refused;
   (c) blinding is checked -- the seeded text must not contain the canary id, the generator
       name, the ground-truth summary, or the words canary/seeded/mutant.
   For each: can you construct a case that SHOULD be refused and is not? Run it.

**Q3. Is the measurement sound?** `catches()` takes an injected verifier and scores NOTHING
when none is supplied. `detection_rate` divides by the held-out count. Is p_hat = catches/k the
right estimator here, given the panel has multiple models and multiple rounds? What does it do
when a canary is unkillable, when two models find the same canary, or when a model finds a
canary by accident while looking for something else? Is there a denominator error?

**Q4. What is missing before this could be wired to the gate?** The module deliberately does
NOT decide anything -- whether a missed canary should BLOCK convergence is reserved as a founder
ruling. Assume that ruling comes back "yes, block". What would have to exist first? Be concrete
and name files.

**Q5. Should this be built at all?** Argue the strongest case AGAINST canary seeding. Does it
measure what it claims? Could a panel learn to spot seeded defects by their texture rather than
their content, and would this design detect that happening? Is there a cheaper instrument that
answers the same question?

## Rules

- Run the tests. Break things. Every verdict must be something you ran, not something you read.
- You are in a throwaway git worktree. Nothing you write escapes. Do not try to push.
- Report what you could NOT check, and why. That section is not optional.
- Disagreement is information here. Do not converge toward the other reviewer or toward me.

```