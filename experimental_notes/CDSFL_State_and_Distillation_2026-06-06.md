# Where the build stands, the panel's verdict, and how to distil the operational directive without gutting it

**2026-06-06 11:19 BST**

## The problem we set out to fix

CDSFL reviews code and STEM work with a panel of five AI models. Its founding rule: whether a reported flaw is real should be settled by **running a tool**, and where no tool can settle it, by a **human** — never by the models taking a vote. A forensic study established the system had drifted from that rule: it had come to decide truth *by discussion* (models issuing CONFIRM/CHALLENGE opinions, with a late "compelled convergence" patch forcing agreement). A six-model panel reviewed that diagnosis: **sound, with caveats.** The single root cause was truth-by-discussion quietly replacing truth-by-tools.

## The fix, and how it works

Two halves, approved together. (a) Models actively use a sandboxed Python execution tool to check and iterate their findings as they work. (b) — the part that decides truth — every critical finding must carry a **falsifier**: a small runnable test that imports the *real* module under review and fails only if the claimed defect is genuinely present. The **runner re-runs that test itself**, independently; its result is the verdict, not the model's prose. No runnable falsifier, or a broken one → the finding goes to a human, never waved through. The safety guarantee: the system never confirms a defect it cannot mechanically demonstrate. Built and committed behind a default-off flag; 300+ tests pass.

## Three real bugs found while building it

1. A **broken** falsifier (bad import / typo) was being read as a *confirmed* defect — the exact rubber-stamp the fix exists to prevent.
2. The launcher **silently dropped** the switch that turns the mechanism on — it would have run the old voting system with no error.
3. A model looping on the tool to budget-exhaustion **returned nothing**, losing its whole round.

All fixed and pinned with tests.

## The first live run, and what it exposed

Run on a real ~60K-char target. Monitoring caught and fixed one issue immediately (large files are chunked before dispatch — a quality protection — and that path wasn't passing the tool through). The first round then scored **zero testable falsifiers of fourteen criticals.** The runner correctly refused to confirm any — the safety net worked, but on broken inputs.

Cause: the chunking path's summary instruction still asks for falsification in the *old prose format* (a section headed "FALSIFIER / ATTEMPT / RESULT", in words). Four models wrote prose; the fifth wrote no falsifier. The runner had nothing to execute. The measurement tool built for this campaign also **corrected an earlier mistake of mine** — I'd reported a model's output was lost to a text-extraction bug; it wasn't. Its 13,000 chars reached the runner intact; it simply wrote no falsifier. One fix serves all five: demand a runnable code block, not prose.

## The deeper routing findings

The per-model **capability record** ("fingerprint") stores the largest input each model has handled. These are high and genuinely per-model: four models ~400K chars, DeepSeek lower at ~110K. By that record, none needed to chunk a 60K file. What forced chunking was a separate **uniform 80K hard floor** that *overrides* the per-model record. True input size (with the large operational instruction set added) was ~113K → over the floor → all five chunked. The floor exists for a real reason (the record measures *returned-something*, not *returned-good*, so it overstates capability, and one past large input collapsed in quality). But the floor sits far below where collapse was actually observed — plausibly too conservative, forcing capable models to chunk work they'd handle whole.

## The operational instruction set, and the distillation question

~44,000 chars, 23 sections, appended **in full to every model on every turn** — a fixed per-turn tax. On inspection, ~half is *not* operational instruction: it's justification, history, worked examples, the philosophical grounding, the empirical-evidence tables, the academic citations. A model acts on none of it per turn. Your instinct — the models don't need the full project history every decision — is correct; a distilled version is achievable.

## The panel's verdict on the instruction set

Five-model panel, two questions: what must it contain to preserve integrity, and is the proposed cutting method sound. **Q1, unanimous with no dissent:** replace the prose falsifier requirement with a strict **runnable code block** requirement. Consensus on ~6 sections to keep, ~6 to cut as narration; two split (test, not judge).

## The blind spot the panel found — and why it matters most

**Q2: the panel divided, and Gemini returned UNSOUND** with the single most valuable objection of the review — an instance of **Goodhart's Law** (once a measure becomes a target it stops being a good measure).

My proposed metric scores a distilled directive on six dimensions: parse, falsifier-present, admissible, R_k-present, alternatives, participation. **Every one measures *form*. None measures whether the models actually find real defects.** So you could distil, score a perfect 100%, and catch *none* of the actual bugs — the models redirecting effort to well-formatted, admissible, mathematically-decorated trivialities. The metric reports success while reasoning is hollowed out.

**Its fix (which I recommend adopting):** add a **seventh dimension measuring function, not form** — take a stable codebase, seed it with known planted defects, and measure **recall**: how many the distilled directive still causes the models to catch. You cannot ablate a reasoning prompt without measuring reasoning degradation against ground truth.

Three further fair points: (1) temperature-0 isn't actually deterministic → ~10 runs, not 2; (2) sections aren't independent → cutting one can break another's coherence, misattributed as load-bearing; (3) don't union per-model needs → it re-bloats; fix a weak model with one worked example instead.

## What this means for the balance you raised

> "We must be as careful about what we throw away as about what we keep."

Gemini's objection **is** the mechanical answer. My metric could see what we *kept working* (form) but was blind to what we *threw away* (reasoning). The recall measure closes that gap exactly: cut aggressively, and if something thrown away mattered for finding defects, recall drops and the section is restored. The balance stops being judgment and becomes **measurement**.

## My recommendation

1. **Adopt the recall gate before any cutting.** Seed a stable target with known defects; recovered recall is the *primary* gate, ranked above format compliance. The guard against throwing away something load-bearing.
2. **Ground keep/cut in the code, not judgment.** For each of the 23 sections, **trace what in the runner or the mathematics actually consumes it.** Consumed (e.g. the R_k equation, the admissibility constraints) → load-bearing, keep. Consumed by nothing (philosophical narration, history tables) → waffle, cut. This *trace-to-consumer* test is mechanical, fast, and *is* the deep project study — done by following dependencies, not re-reading everything. It replaces debate with an objective criterion (the pace answer).
3. **Distil against both gates, then adopt.** Lean directive as a *separate* file (original never deleted); test against the recall gate (did bug-finding survive?) and the format metric (did structured output survive?), across enough runs to see past variance. Adopt only if both hold for *every* model.

## On pace

The detail wasn't wasted — the live run surfaced load-bearing defects (the prose-format defeat, the over-conservative floor, the bloated directive) that would have quietly corrupted every downstream result. But the diagnostic phase is essentially done. What remains is execution against objective criteria. The recall gate is what lets us cut quickly *without* cutting carelessly — the balance you asked for. From here, judgment gives way to measurement, and the pace picks up.

---

Written under CDSFL note standard v1.2 (14 May 2026).
